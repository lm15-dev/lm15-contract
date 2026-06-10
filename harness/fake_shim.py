#!/usr/bin/env python3
"""Mutation-injecting fake shim for harness/selftest.py. NOT a real shim.

Speaks the vet protocol (harness/PROTOCOL.md) but never transforms anything:
it echoes the recorded-correct outputs straight from the corpus — wire
fixtures for build_request, goldens/ for parse_response and replay_stream,
the expected blocks for normalize_error, the input value for serde_roundtrip
— EXCEPT for one injected mutation (--mutation, optionally scoped to one
case with --target). With --mutation none the echo must be fully green; with
any other mutation the harness comparator must turn the target case red.
selftest.py enforces both, so a weakened comparator fails CI.

This file is test scaffolding for the harness itself. It must NEVER be
registered in harness/shims.json: an oracle-echo shim is green by
construction and proves nothing about any implementation.

Usage: fake_shim.py --mutation NAME [--target CASE_ID]
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any, Callable

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))

import check  # harness/check.py — corpus loaders, expected_wire_request, golden_path

JsonObject = dict[str, Any]

MUTATIONS = (
    "none",
    "wrong_tool_name",      # parse: first tool_call part's name rewritten
    "garbage_text",         # parse: first text part's text replaced with garbage
    "absent_empty",         # parse: emit provider_data: {} where the golden has it ABSENT
    "usage_off_by_1000",    # parse: first integer usage field += 1000
    "dropped_event",        # replay_stream: last event dropped
    "bool_as_int",          # build_request: first boolean body leaf becomes 0/1
)

MUTATION = "none"
TARGET: str | None = None


# ─── Corpus indexes (recorded-correct outputs) ───────────────────────

def _canon_key(provider: Any, canonical_request: Any, base_url: Any = None) -> str:
    # base_url is part of the identity: cases for different OpenAI-compatible
    # servers (vLLM :8000, SGLang :30000) share canonical_requests but record
    # different wire URLs (see check.case_base_url / PROTOCOL.md).
    return json.dumps(
        [provider, base_url, canonical_request], sort_keys=True, separators=(",", ":")
    )


WIRE_CASES = check.load_wire_cases()
BY_CANON: dict[str, list[JsonObject]] = {}
for _case in WIRE_CASES:
    if "canonical_request" in _case:
        BY_CANON.setdefault(
            _canon_key(_case["provider"], _case["canonical_request"], _case.get("base_url")),
            [],
        ).append(_case)


def _candidates(msg: JsonObject) -> list[JsonObject]:
    return BY_CANON.get(
        _canon_key(msg["provider"], msg["canonical_request"], msg.get("base_url")), []
    )


def find_wire_case(msg: JsonObject) -> JsonObject:
    candidates = _candidates(msg)
    if not candidates:
        raise LookupError("no case fixture matches this canonical_request")
    # Duplicate canonical_requests at the same base_url (e.g.
    # anthropic.thinking/thinking_budget) necessarily record identical wire
    # requests — any candidate echoes right.
    return candidates[0]


def find_parse_case(msg: JsonObject) -> JsonObject:
    candidates = _candidates(msg)
    for case in candidates:
        if "pinned_body" in case:
            pinned = base64.b64encode(check.pinned_body(case)).decode("ascii")
            if pinned == msg.get("body_b64"):
                return case
    if candidates:
        return candidates[0]
    raise LookupError("no case fixture matches this canonical_request")


def targeted(case: JsonObject) -> bool:
    return TARGET is None or case.get("id") == TARGET


# ─── Mutations ───────────────────────────────────────────────────────

def mutate_first(node: Any, predicate: Callable[[JsonObject], bool],
                 action: Callable[[JsonObject], None]) -> bool:
    """Depth-first; applies `action` to the first dict matching `predicate`."""
    if isinstance(node, dict):
        if predicate(node):
            action(node)
            return True
        return any(mutate_first(v, predicate, action) for v in node.values())
    if isinstance(node, list):
        return any(mutate_first(v, predicate, action) for v in node)
    return False


def mutate_first_bool(node: Any, container: Any = None, key: Any = None) -> bool:
    """Replaces the first boolean leaf with int(value) — true becomes 1."""
    if isinstance(node, bool):
        container[key] = int(node)
        return True
    if isinstance(node, dict):
        return any(mutate_first_bool(v, node, k) for k, v in node.items())
    if isinstance(node, list):
        return any(mutate_first_bool(v, node, i) for i, v in enumerate(node))
    return False


def mutate_response(resp: JsonObject) -> None:
    if MUTATION == "wrong_tool_name":
        mutate_first(
            resp,
            lambda n: n.get("type") == "tool_call" and isinstance(n.get("name"), str),
            lambda n: n.update(name="not_the_recorded_tool"),
        )
    elif MUTATION == "garbage_text":
        mutate_first(
            resp,
            lambda n: n.get("type") == "text" and isinstance(n.get("text"), str),
            lambda n: n.update(text="GARBAGE — injected by harness selftest"),
        )
    elif MUTATION == "absent_empty":
        # The flip: goldens never carry provider_data (PROTOCOL.md serializes
        # responses WITHOUT it). Absent and {} are different values; a
        # comparator that drops empties before comparing passes this.
        resp["provider_data"] = {}
    elif MUTATION == "usage_off_by_1000":
        usage = resp.get("usage")
        if isinstance(usage, dict):
            for key, value in usage.items():
                if isinstance(value, int) and not isinstance(value, bool):
                    usage[key] = value + 1000
                    break


# ─── Ops ─────────────────────────────────────────────────────────────

def op_capabilities(msg: JsonObject) -> JsonObject:
    return {
        "language": "fake",
        "ops": sorted(HANDLERS),
        "impl_version": f"selftest mutation={MUTATION} target={TARGET or '*'}",
    }


def op_build_request(msg: JsonObject) -> JsonObject:
    case = find_wire_case(msg)
    result = check.expected_wire_request(case)
    if MUTATION == "bool_as_int" and targeted(case):
        mutate_first_bool(result["body"])
    return result


def op_parse_response(msg: JsonObject) -> JsonObject:
    case = find_parse_case(msg)
    golden = json.loads(check.golden_path(case).read_text())
    resp = golden["canonical_response"]
    if targeted(case):
        mutate_response(resp)
    return {"canonical_response": resp}


def op_replay_stream(msg: JsonObject) -> JsonObject:
    case = find_parse_case(msg)
    golden = json.loads(check.golden_path(case).read_text())
    resp = golden["canonical_response"]
    events = golden.get("events", [])
    if targeted(case):
        mutate_response(resp)
        if MUTATION == "dropped_event":
            events = events[:-1]
    return {"events": events, "canonical_response": resp}


def op_normalize_error(msg: JsonObject) -> JsonObject:
    for case in check.load_error_cases():
        body = case["body"]
        body_text = body if isinstance(body, str) else json.dumps(body)
        if (
            case["provider"] == msg["provider"]
            and int(case["status"]) == int(msg["status"])
            and body_text == msg["body_text"]
        ):
            expected = case["expected"]
            return {
                "class": expected.get("class"),
                "code": expected.get("code"),
                "provider_code": expected.get("provider_code"),
                "message": expected.get("message", ""),
            }
    raise LookupError("no error fixture matches this (provider, status, body_text)")


def op_serde_roundtrip(msg: JsonObject) -> JsonObject:
    return {"value": msg["value"]}


HANDLERS: dict[str, Callable[[JsonObject], JsonObject]] = {
    "capabilities": op_capabilities,
    "build_request": op_build_request,
    "parse_response": op_parse_response,
    "replay_stream": op_replay_stream,
    "normalize_error": op_normalize_error,
    "serde_roundtrip": op_serde_roundtrip,
}


# ─── Framing (as PROTOCOL.md) ────────────────────────────────────────

def handle_line(line: str) -> JsonObject:
    try:
        msg = json.loads(line)
    except Exception as exc:
        return {"id": None, "ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}
    req_id = msg.get("id") if isinstance(msg, dict) else None
    try:
        if not isinstance(msg, dict):
            raise ValueError("request must be a JSON object")
        handler = HANDLERS.get(str(msg.get("op")))
        if handler is None:
            raise ValueError(f"unknown op: {msg.get('op')}")
        result = handler(msg)
    except Exception as exc:
        return {"id": req_id, "ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}
    return {"id": req_id, "ok": True, "result": result}


def main(argv: list[str] | None = None) -> int:
    global MUTATION, TARGET
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mutation", default="none", choices=MUTATIONS)
    parser.add_argument("--target", default=None, help="case id the mutation applies to (default: all)")
    args = parser.parse_args(argv)
    MUTATION, TARGET = args.mutation, args.target

    for line in sys.stdin:
        if not line.strip():
            continue
        sys.stdout.write(json.dumps(handle_line(line), separators=(",", ":")) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
