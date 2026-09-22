#!/usr/bin/env python3
"""Validate managed-auth CONTRACT artifacts, not SDK authentication behavior.

Run with the format extra (date-time validation must never silently disappear):
  uv run --no-project --with 'jsonschema[format]>=4.18,<5' \
    python tools/check_managed_auth.py --self-test

No real credentials, network operations or SDK imports. This checks schema
well-formedness, vector verdicts/identity uniqueness, scenario numbering and local
Markdown links. The --self-test mutations prove this checker rejects bad contract
artifacts; they do NOT stand in for the runtime mutation suite in auth/managed/.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path):
    def members(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON member in contract artifact")
            result[key] = value
        return result

    def nonfinite(_value):
        raise ValueError("non-finite JSON number in contract artifact")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=members,
                      parse_constant=nonfinite)


def unique_ids(items, label: str) -> None:
    require(isinstance(items, list) and bool(items), f"{label}: expected nonempty list")
    ids = [item.get("id") for item in items]
    require(all(isinstance(value, str) and value for value in ids), f"{label}: invalid ID")
    require(len(ids) == len(set(ids)), f"{label}: duplicate ID")


def apply_patch(document, patches):
    """Strict fixture-only RFC 6901 navigation; not a product store operation."""
    result = copy.deepcopy(document)
    for patch in patches:
        op = patch["op"]
        require(op in {"add", "replace", "remove"}, "unsupported fixture patch operation")
        pointer = patch["path"]
        require(isinstance(pointer, str) and pointer.startswith("/"), "invalid fixture pointer")
        require(not re.search(r"~(?![01])", pointer), "invalid JSON Pointer escape")
        parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]
        parent = result
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        last = parts[-1]
        if isinstance(parent, list):
            index = len(parent) if last == "-" and op == "add" else int(last)
            require(0 <= index <= len(parent), "fixture array index out of range")
            if op == "add":
                parent.insert(index, copy.deepcopy(patch["value"]))
            else:
                require(index < len(parent), "fixture array member missing")
                if op == "remove":
                    del parent[index]
                else:
                    parent[index] = copy.deepcopy(patch["value"])
        else:
            require(isinstance(parent, dict), "fixture pointer parent is not a container")
            if op != "add":
                require(last in parent, "fixture object member missing")
            if op == "remove":
                del parent[last]
            else:
                parent[last] = copy.deepcopy(patch["value"])
    return result


def validate_store_vectors(data, validator) -> int:
    require(data.get("version") == 1 and data.get("status") == "review-draft", "store vector envelope")
    cases = data["cases"]
    unique_ids(cases, "store cases")
    resolved = {}
    for case in cases:
        direct = "input" in case
        require(direct != ("base" in case), f"{case['id']}: exactly one input or base")
        require((not direct) == ("patch" in case), f"{case['id']}: patch requires base")
        if direct:
            document = copy.deepcopy(case["input"])
        else:
            require(case["base"] in resolved, f"{case['id']}: unknown/forward fixture base")
            document = apply_patch(resolved[case["base"]], case["patch"])
        verdict = case["expect"].get("valid")
        require(type(verdict) is bool, f"{case['id']}: expected verdict must be boolean")
        # Do not print schema errors: their messages can include private input values.
        require(validator.is_valid(document) == verdict, f"{case['id']}: unexpected structural verdict")
        resolved[case["id"]] = document
    return len(cases)


def validate_resolution(data, validator) -> int:
    require(validator.is_valid(data), "resolution vector schema failed (private values suppressed)")
    unique_ids(data["definitions"], "definitions")
    unique_ids(data["cases"], "resolution cases")
    for case in data["cases"]:
        expected = case["expect"]
        if expected.get("source") == "connection":
            candidates = case["given"].get("connections", [])
            require(any(c["id"] == expected["connection_id"] for c in candidates),
                    f"{case['id']}: expected connection reference is not an input")
    return len(data["cases"])


def check_documents(root: Path) -> int:
    text = (root / "auth/managed/scenarios.md").read_text(encoding="utf-8")
    ids = re.findall(r"^### MA-(\d{3})\b", text, re.MULTILINE)
    require(ids == [f"{n:03}" for n in range(1, len(ids) + 1)] and len(ids) >= 64,
            "acceptance scenario IDs must be unique, contiguous, and include MA-001..064")
    spec = (root / "spec/auth-managed.md").read_text(encoding="utf-8")
    rules = re.findall(r"^## AUTH-(\d+) —", spec, re.MULTILINE)
    require(rules == [str(n) for n in range(12, 27)], "core AUTH-12..26 headings missing/repeated")
    reserved = (root / "spec/auth-managed-reserved.md").read_text(encoding="utf-8")
    reserved_rules = re.findall(r"^## AUTH-(\d+) \(reserved\)", reserved, re.MULTILINE)
    require(bool(reserved_rules) and all(12 <= int(n) <= 26 for n in reserved_rules)
            and len(reserved_rules) == len(set(reserved_rules)),
            "reserved headings must be '## AUTH-n (reserved)' with n in 12..26, each at most once")
    require(all("**Promote when:**" in block for block in re.split(r"^## AUTH-", reserved, flags=re.MULTILINE)[1:]),
            "every reserved rule must state its promote-when trigger")
    docs = [
        "spec/auth-managed.md", "spec/auth-managed-reserved.md", "spec/auth.md",
        "docs/auth-examples.md", "auth/managed/README.md", "auth/managed/scenarios.md",
        "changes/2026-09-22-managed-authentication.md",
        "changes/2026-09-22-managed-authentication-ratification.md",
    ]
    for rel in docs:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        require(text.count("```") % 2 == 0, f"{rel}: unbalanced fenced blocks")
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            file_part = target.split("#", 1)[0]
            if not file_part or "://" in file_part or file_part.startswith("mailto:"):
                continue
            require((path.parent / unquote(file_part)).is_file(), f"{rel}: broken local link {file_part}")
    return len(ids)


def self_test(store_data, store_validator, resolution_data, resolution_validator) -> int:
    mutations = []
    bad = copy.deepcopy(store_data); bad["cases"][0]["expect"]["valid"] = False
    mutations.append(lambda: validate_store_vectors(bad, store_validator))
    duplicate = copy.deepcopy(store_data); duplicate["cases"].append(copy.deepcopy(duplicate["cases"][0]))
    mutations.append(lambda: validate_store_vectors(duplicate, store_validator))
    forward = copy.deepcopy(store_data); forward["cases"][2]["base"] = "not-an-earlier-case"
    mutations.append(lambda: validate_store_vectors(forward, store_validator))
    duplicate_resolution = copy.deepcopy(resolution_data)
    duplicate_resolution["cases"].append(copy.deepcopy(duplicate_resolution["cases"][0]))
    mutations.append(lambda: validate_resolution(duplicate_resolution, resolution_validator))
    bad_reason = copy.deepcopy(resolution_data)
    blocked = next(c for c in bad_reason["cases"] if c["expect"].get("code") == "auth_operation")
    blocked["expect"]["reason"] = "invented-reason"
    mutations.append(lambda: validate_resolution(bad_reason, resolution_validator))
    for i, mutation in enumerate(mutations, 1):
        try:
            mutation()
        except (ValueError, KeyError, IndexError):
            continue
        raise ValueError(f"checker mutation {i} was not detected")
    return len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        print("check_managed_auth: requires jsonschema[format]; use the uv command in this tool's docstring", file=sys.stderr)
        return 2
    try:
        checker = FormatChecker()
        require(not checker.conforms("2026-02-30T10:00:00Z", "date-time"),
                "date-time validation unavailable: install jsonschema[format], not only jsonschema")
        validators = []
        for name in ("auth-store.schema.json", "auth-resolution.schema.json"):
            schema = load(args.root / "spec" / name)
            Draft202012Validator.check_schema(schema)
            validators.append(Draft202012Validator(schema, format_checker=checker))
        stores = load(args.root / "auth/managed/store-vectors.json")
        resolutions = load(args.root / "auth/managed/resolution.json")
        ns = validate_store_vectors(stores, validators[0])
        nr = validate_resolution(resolutions, validators[1])
        nd = check_documents(args.root)
        print(f"check_managed_auth: OK ({ns} structural store verdicts, {nr} resolution shapes, {nd} scenario IDs/local links, core+reserved tiers)")
        if args.self_test:
            n = self_test(stores, validators[0], resolutions, validators[1])
            print(f"check_managed_auth: checker self-test OK ({n} bad-artifact mutations detected)")
        print("No SDK flow, identity-resolution algorithm, concurrency, browser or live-provider behavior was tested.")
        return 0
    except Exception as error:
        # This command reads only synthetic contract fixtures. Never dump entire
        # JSON Schema exceptions, which include the offending private instance.
        safe = str(error) if type(error) is ValueError else type(error).__name__
        print(f"check_managed_auth: FAIL {safe}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
