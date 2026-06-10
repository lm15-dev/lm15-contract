#!/usr/bin/env python3
"""Attach canonical requests and pinned bodies to the contract corpus.

For each logical case in lm15-python2/conformance/cross_sdk/test_cases.json,
build the canonical Request via the reference's own interpretation
(dump_request.request_for_case, imported by path), serialize it with
lm15.serde.request_to_dict, and write it into the matching
cases/<provider>/<feature>.json as "canonical_request". The attached value is
a DRAFT derived from the reference — lm15-python2 holds no oracle authority
(AUTHORITY.md, canonical facts) — so each one carries its own
"canonical_request_provenance" block marking it pending human review. Logical
cases with stream=true are recorded as "stream": true on the case.

For every body directory under bodies/<provider>.<feature>/, the newest body
file BY NAME is pinned into the case as "pinned_body": the harness must use
ONLY the pinned body, never self-select one. Body dirs with no case file are
reported, never invented. Rerunnable: re-running is a no-op on an already
attached corpus.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON2 = ROOT.parent / "lm15-python2"
TEST_CASES = PYTHON2 / "conformance" / "cross_sdk" / "test_cases.json"
DUMP_REQUEST = PYTHON2 / "conformance" / "cross_sdk" / "dump_request.py"

CANONICAL_REQUEST_PROVENANCE = {
    "source": "derived-from-reference",
    "date": "2026-06-10",
    "evidence": "request_for_case @ lm15-python2 HEAD; DRAFT pending human review — see AUTHORITY.md canonical-facts rule",
}


def load_dump_request():
    """Import dump_request.py by path (it puts lm15-python2 on sys.path itself)."""
    spec = importlib.util.spec_from_file_location("dump_request", DUMP_REQUEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def case_path(case_id: str) -> Path:
    provider, feature = case_id.split(".", 1)
    return ROOT / "cases" / provider / f"{feature}.json"


def write_case(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    dump_request = load_dump_request()
    if str(PYTHON2) not in sys.path:
        sys.path.insert(0, str(PYTHON2))
    from lm15.serde import request_to_dict  # noqa: E402  (needs lm15-python2 on sys.path)

    logical_cases = json.loads(TEST_CASES.read_text())["cases"]

    # 1. Canonical requests, from the reference's own interpretation (DRAFT).
    attached = 0
    missing_case_files: list[str] = []
    for case in logical_cases:
        case_id = str(case["id"])
        path = case_path(case_id)
        if not path.is_file():
            missing_case_files.append(case_id)
            continue
        data = json.loads(path.read_text())
        if bool(case.get("stream", False)):
            data["stream"] = True
        data["canonical_request"] = request_to_dict(dump_request.request_for_case(case))
        data["canonical_request_provenance"] = dict(CANONICAL_REQUEST_PROVENANCE)
        write_case(path, data)
        attached += 1

    # 2. Pinned bodies: newest body file by name, one per case directory.
    pinned = 0
    bodies_without_case: list[str] = []
    for body_dir in sorted(p for p in (ROOT / "bodies").iterdir() if p.is_dir()):
        path = case_path(body_dir.name)
        if not path.is_file():
            bodies_without_case.append(body_dir.name)
            continue
        body_files = sorted(f.name for f in body_dir.iterdir() if f.is_file())
        if not body_files:
            bodies_without_case.append(f"{body_dir.name} (empty dir)")
            continue
        data = json.loads(path.read_text())
        data["pinned_body"] = body_files[-1]
        write_case(path, data)
        pinned += 1

    # 3. Honest summary.
    all_case_files = sorted(ROOT.glob("cases/*/*.json"))
    orphans = [
        f"{p.parent.name}.{p.stem}"
        for p in all_case_files
        if "canonical_request" not in json.loads(p.read_text())
    ]
    print(f"canonical_request attached: {attached} / {len(logical_cases)} logical cases")
    print(f"case files without canonical_request (orphans): {len(orphans)}")
    for orphan in orphans:
        print(f"  orphan: {orphan}")
    print(f"pinned bodies: {pinned}")
    if missing_case_files:
        print(f"logical cases with NO case file (not attached): {missing_case_files}")
    if bodies_without_case:
        print("body dirs with NO case file (reported, not invented):")
        for name in bodies_without_case:
            print(f"  {name}")
    return 1 if missing_case_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
