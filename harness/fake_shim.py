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
    "auth_state_flip",      # explain_auth: first step's state flipped
    "auth_sentinel_leak",   # explain_auth: the planted sentinel leaks into report_text
    "models_wrong_id",      # parse_models_response: first model's id rewritten
    "models_param_drop",    # build_models_request: one query parameter dropped
    "live_dropped_event",   # replay_live: last decoded event dropped from its frame group
    "live_frame_key_drop",  # replay_live: one key dropped from the first encoded client frame
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


def _borrowed_state(path: Path) -> str:
    """Classify a harness-materialized borrowed file (see check.materialize_borrowed_file)."""
    if not path.exists():
        return "missing"
    oauth = json.loads(path.read_text())["claudeAiOauth"]
    import time

    expired = int(oauth.get("expiresAt", 0)) <= int(time.time() * 1000)
    if not expired:
        return "fresh"
    return "expired-with-refresh" if oauth.get("refreshToken") else "expired-no-refresh"


def find_models_case(msg: JsonObject) -> JsonObject:
    for case in check.load_model_cases():
        if case["provider"] == msg["provider"] and case.get("base_url") == msg.get("base_url"):
            return case
    raise LookupError("no models case matches this (provider, base_url)")


def op_build_models_request(msg: JsonObject) -> JsonObject:
    case = find_models_case(msg)
    result = check.expected_wire_request(case)
    if MUTATION == "models_param_drop" and targeted(case) and result["params"]:
        result["params"].pop(sorted(result["params"])[0])
    return result


def op_parse_models_response(msg: JsonObject) -> JsonObject:
    case = find_models_case(msg)
    golden = json.loads(check.golden_path(case).read_text())
    entries = json.loads(check.pinned_body(case))[case["entries_key"]]
    models = []
    for i, model in enumerate(golden["models"]):
        model = dict(model)
        # Re-attach the verbatim wire entry the golden strips (goldens carry
        # the mapped surface only; the harness checks embedding separately).
        # In-order assignment holds while fixtures skip no entries.
        origin = dict(model.get("origin", {"type": "provider"}))
        origin["provider_data"] = entries[i]
        model["origin"] = origin
        models.append(model)
    if MUTATION == "models_wrong_id" and targeted(case) and models:
        models[0]["id"] = "not-the-recorded-model"
    return {"models": models}


def find_live_case(msg: JsonObject) -> JsonObject:
    for case in check.load_live_cases():
        if case["provider"] == msg["provider"] and case["live_config"] == msg["live_config"]:
            return case
    raise LookupError("no live case matches this (provider, live_config)")


def op_replay_live(msg: JsonObject) -> JsonObject:
    case = find_live_case(msg)
    transcript = check.load_live_transcript(case)
    setup = next((e["frames"] for e in transcript if e["dir"] == "client" and e.get("kind") == "setup"), [])
    client_frames = [e["frames"] for e in transcript if e["dir"] == "client" and e.get("kind") == "event"]
    events = json.loads(check.golden_path(case).read_text())["events"]
    if targeted(case):
        if MUTATION == "live_dropped_event":
            for group in reversed(events):
                if group:
                    group.pop()
                    break
        elif MUTATION == "live_frame_key_drop":
            for frames in client_frames:
                if frames and isinstance(frames[0], dict) and frames[0]:
                    frames[0] = dict(frames[0])
                    frames[0].pop(sorted(frames[0])[0])
                    break
    return {"setup_frames": setup, "client_frames": client_frames, "events": events}


def op_explain_auth(msg: JsonObject) -> JsonObject:
    fixture = check.load_auth_fixture()
    for case in fixture["cases"]:
        if case["provider"] != msg["provider"]:
            continue
        if case.get("env", {}) != msg.get("env", {}):
            continue
        if case.get("api_keys_providers", []) != msg.get("api_keys_providers", []):
            continue
        has_borrowed = "borrowed_file" in case
        if has_borrowed != ("credentials_path" in msg):
            continue
        if has_borrowed:
            actual_state = _borrowed_state(Path(msg["credentials_path"]))
            if case["borrowed_file"]["state"] != actual_state:
                continue
        expect = case["expect"]
        steps = [dict(step) for step in expect["steps"]]
        report_text = "\n".join(f"{s['kind']}: {s['state']}" for s in steps) or "empty chain"
        if targeted(case):
            if MUTATION == "auth_state_flip" and steps:
                steps[0]["state"] = "absent" if steps[0]["state"] == "selected" else "selected"
            elif MUTATION == "auth_sentinel_leak":
                report_text += f"\nkey: {msg['sentinel']}"
        return {"configured": expect["configured"], "steps": steps, "report_text": report_text}
    raise LookupError("no auth fixture matches this (provider, env, api_keys_providers, borrowed state)")


HANDLERS: dict[str, Callable[[JsonObject], JsonObject]] = {
    "capabilities": op_capabilities,
    "build_request": op_build_request,
    "parse_response": op_parse_response,
    "replay_stream": op_replay_stream,
    "normalize_error": op_normalize_error,
    "serde_roundtrip": op_serde_roundtrip,
    "explain_auth": op_explain_auth,
    "build_models_request": op_build_models_request,
    "parse_models_response": op_parse_models_response,
    "replay_live": op_replay_live,
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
