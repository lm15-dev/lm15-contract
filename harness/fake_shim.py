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
    "end_provider_data_dropped",  # replay_stream: provider_data removed from the end event (D9 presence rule)
    "bool_as_int",          # build_request: first boolean body leaf becomes 0/1
    "auth_state_flip",      # explain_auth: first step's state flipped
    "auth_sentinel_leak",   # explain_auth: the planted sentinel leaks into report_text
    "models_wrong_id",      # parse_models_response: first model's id rewritten
    "models_param_drop",    # build_models_request: one query parameter dropped
    "live_dropped_event",   # replay_live: last decoded event dropped from its frame group
    "live_frame_key_drop",  # replay_live: one key dropped from the first encoded client frame
    "gen_wrong_media_type",     # generation_parse: first media part's media_type rewritten
    "gen_dropped_narration",    # generation_parse: the narration text field dropped
    "gen_multipart_field_drop", # generation_build: a multipart form field name corrupted
    "file_readiness_flip",      # file_op_parse: readiness "ready" -> "pending"
    "file_param_drop",          # file_op_build: one query parameter dropped
    "batch_entry_order_swap",   # batch_op_parse entries: first two entries swapped
    "batch_status_vocab_drift", # batch_op_parse job: canonical status replaced by the wire word
    "video_status_vocab_drift", # video_op_parse job: canonical status replaced by the wire word
    "video_part_url_drift",     # video_op_parse part: the delivery URL rewritten
    "cache_expiry_drift",       # cache_op_parse info: expires_at rewritten (the billed lifetime)
    "cache_model_drop",         # cache_op_build create: the model field dropped from the body
    "assembly_guesses_name",    # replay_stream: a pinned StreamAssemblyError answered with a Response (a name invented)
    "build_maps_a_refused_cell", "tool_result_image_dropped", "tool_result_ids_swapped", "tool_result_error_stripped", # build_request: a pinned refusal answered with a wire request (a silent cell)
    "pinned_credential_scheme_drift",  # build_request: a pinned bearer_token sent under the door's key header instead of Authorization
    "sigv4_signature_drift",    # sigv4_sign: the Authorization header's signature hex rewritten
    "token_credential_drift",   # token_exchange_parse: the yielded credential's expiry rewritten
    "token_assertion_drift",    # token_exchange_build: corrupt the signed JWT
    "router_class_drift",       # resolve_model: ambiguous_model collapsed to the parent class
    "router_resolves_instead_of_refusing",  # resolve_model: an unknown string routed anyway
    "router_provider_underscore",  # resolve_model: the underscore spelling as an OUTPUT value
    "router_alias_not_resolved",   # resolve_model: a catalog alias sent on the wire unresolved
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
    # A streaming and a non-streaming case may legitimately share one
    # canonical_request (xai.basic_text / xai.streaming); the stream flag
    # is part of the wire identity, so prefer the matching candidate.
    stream = bool(msg.get("stream"))
    for case in candidates:
        if bool(case.get("stream")) == stream:
            return case
    # Remaining duplicates at the same base_url (e.g.
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


class PinnedRaise(Exception):
    """A golden that pins a refusal: the reply must be ok=false with these fields."""

    def __init__(self, error: JsonObject) -> None:
        super().__init__(error.get("type", "?"))
        self.error = error


def op_build_request(msg: JsonObject) -> JsonObject:
    case = find_wire_case(msg)
    raises = check.expected_raise(case, "build_request")
    if raises is not None:
        if MUTATION == "build_maps_a_refused_cell" and targeted(case):
            # The silent cell: a wire request produced where the receipts
            # say the provider ignores or drops the intent.
            return {"method": "POST", "url": "https://invented/", "params": {}, "headers": {}, "body": {}}
        raise PinnedRaise({"type": raises["type"], "code": raises["code"], "message": "pinned refusal"})
    result = check.expected_wire_request(case)
    if MUTATION == "bool_as_int" and targeted(case):
        mutate_first_bool(result["body"])
    if MUTATION == "tool_result_image_dropped" and targeted(case):
        # The pre-MAP-10 behaviour: the image inside a tool result rendered
        # as a type-name placeholder string, HTTP 200, model none the wiser.
        _first_result_item(result["body"], lambda item, key: item.__setitem__(key, '[{"type": "image"}]'))
    if MUTATION == "tool_result_ids_swapped" and targeted(case):
        # Two results, two calls: association lost.
        items = _result_items(result["body"])
        if len(items) >= 2:
            (a, ka), (b, kb) = items[0], items[1]
            a[ka], b[kb] = b[kb], a[ka]
    if MUTATION == "tool_result_error_stripped" and targeted(case):
        # is_error dropped on the way to the wire (MAP-10 rule 5).
        _strip_error_flag(result["body"])
    if MUTATION == "pinned_credential_scheme_drift" and targeted(case):
        # The AUTH-2 scheme-selection drift: the pinned token lands in the
        # key header.  Only a verbatim header compare (PROTOCOL.md
        # 2026-09-04) can see this; a harness that rewrites auth values
        # to its injected key would pass it.
        value = result["headers"].pop("authorization")
        result["headers"]["x-api-key"] = value.removeprefix("Bearer ")
    return result


def _result_items(body: JsonObject) -> list[tuple[JsonObject, str]]:
    """(container, id-key) of every tool-result item on any of the four wires."""
    out: list[tuple[JsonObject, str]] = []
    for item in body.get("input", []):
        if isinstance(item, dict) and item.get("type") == "function_call_output":
            out.append((item, "call_id"))
    for msg in body.get("messages", []):
        if isinstance(msg, dict) and msg.get("role") == "tool":
            out.append((msg, "tool_call_id"))
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    out.append((block, "tool_use_id"))
    for content in body.get("contents", []):
        for part in content.get("parts", []) if isinstance(content, dict) else []:
            if isinstance(part, dict) and "functionResponse" in part:
                out.append((part["functionResponse"], "id"))
    return out


def _first_result_item(body: JsonObject, set_content) -> None:
    for item, id_key in _result_items(body):
        for key in ("output", "content"):
            if isinstance(item.get(key), list):
                set_content(item, key)
                return
        if "parts" in item:  # Gemini: the media rides in functionResponse.parts
            item.pop("parts")
            item["response"] = {"result": '[{"type": "image"}]'}
            return


def _strip_error_flag(body: JsonObject) -> None:
    for item, _ in _result_items(body):
        if item.pop("is_error", None) is not None:
            return
        resp = item.get("response")
        if isinstance(resp, dict) and "error" in resp:
            item["response"] = {"result": resp.pop("error")}
            return


def op_parse_response(msg: JsonObject) -> JsonObject:
    case = find_parse_case(msg)
    golden = json.loads(check.golden_path(case).read_text())
    raises = check.expected_raise(case, "parse_response")
    if raises is not None:
        # A complete-path refusal (MAP-9, 2026-09-07): the golden carries
        # provenance only; the reply is the pinned ok=false.
        raise PinnedRaise({"type": raises["type"], "code": raises["code"], "message": "pinned refusal"})
    resp = golden["canonical_response"]
    if targeted(case):
        mutate_response(resp)
    return {"canonical_response": resp}


def op_resolve_model(msg: JsonObject) -> JsonObject:
    fixture = check.load_router_fixture()
    for case in fixture["cases"]:
        if case["model"] != msg["model"] or case.get("catalog") != msg.get("catalog"):
            continue
        expect = case["expect"]
        if "error" in expect:
            error = dict(expect["error"])
            error["type"] = error.pop("class")
            error["message"] = "pinned refusal"
            if targeted(case):
                if MUTATION == "router_class_drift":
                    # The pre-2026-09-08 port: every routing failure is the
                    # parent class, the distinction lost.
                    error["type"], error["code"] = "ConfigurationError", "not_configured"
                    error.pop("providers", None)
                elif MUTATION == "router_resolves_instead_of_refusing":
                    return {"provider": "openai", "model": msg["model"], "source": "rule"}
            raise PinnedRaise(error)
        result = dict(expect)
        if targeted(case):
            if MUTATION == "router_provider_underscore":
                result["provider"] = result["provider"].replace("-", "_")
            elif MUTATION == "router_alias_not_resolved":
                result["model"] = msg["model"]
        return result
    raise LookupError("no router fixture matches this (model, catalog)")


def op_replay_stream(msg: JsonObject) -> JsonObject:
    case = find_parse_case(msg)
    golden = json.loads(check.golden_path(case).read_text())
    events = golden.get("events", [])
    raises = check.expected_raise(case, "replay_stream")
    if raises is not None:
        if MUTATION == "assembly_guesses_name" and targeted(case):
            # The pre-MAP-9 behaviour: invent a tool name and hand back a
            # Response as if nothing were wrong.
            resp = json.loads(json.dumps(golden.get("partial_response", {})))
            resp.setdefault("message", {}).setdefault("parts", []).append(
                {"type": "tool_call", "id": "tool_call_0", "name": "get_weather", "input": {"city": "Gatineau"}}
            )
            return {"events": events, "canonical_response": resp}
        error = {"type": raises["type"], "code": raises["code"], "message": "pinned refusal"}
        if "partial_response" in golden:
            error["partial_response"] = golden["partial_response"]
        error["events"] = events
        raise PinnedRaise(error)
    resp = golden["canonical_response"]
    if targeted(case):
        mutate_response(resp)
        if MUTATION == "dropped_event":
            events = events[:-1]
        if MUTATION == "end_provider_data_dropped":
            # D9: the end event's provider_data is compared by presence and
            # type only, never by content. Dropping it entirely must still
            # be caught when the golden carries it.
            events = [
                {k: v for k, v in e.items() if k != "provider_data"}
                if isinstance(e, dict) and e.get("type") == "end" else e
                for e in events
            ]
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
    """Classify a harness-materialized credential file (see check.materialize_borrowed_file).

    Handles both AUTH-8 wire formats: the Claude Code store
    (``claudeAiOauth``: accessToken/expiresAt/refreshToken) and the
    lm15-owned store (``xai``: access/expires/refresh).
    """
    if not path.exists():
        return "missing"
    data = json.loads(path.read_text())
    if "claudeAiOauth" in data:
        oauth = data["claudeAiOauth"]
        expiry, refresh = oauth.get("expiresAt", 0), oauth.get("refreshToken")
    else:
        oauth = data["xai"]
        expiry, refresh = oauth.get("expires", 0), oauth.get("refresh")
    import time

    if int(expiry) > int(time.time() * 1000):
        return "fresh"
    return "expired-with-refresh" if refresh else "expired-no-refresh"


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


def _case_env_matches(case: JsonObject, msg: JsonObject) -> bool:
    """Cloud-chain cases (``files`` present) get their env rewritten by the
    harness: ``~/`` becomes the harness-owned home and ``HOME`` is added
    (check.run_auth_direction).  Undo that before comparing."""
    expected = dict(case.get("env", {}))
    actual = dict(msg.get("env", {}))
    if "files" in case:
        home = actual.pop("HOME", None)
        if home is not None:
            expected = {k: v.replace("~/", f"{home}/") if isinstance(v, str) else v for k, v in expected.items()}
    return expected == actual


def op_explain_auth(msg: JsonObject) -> JsonObject:
    fixture = check.load_auth_fixture()
    for case in fixture["cases"]:
        if case["provider"] != msg["provider"]:
            continue
        if not _case_env_matches(case, msg):
            continue
        if case.get("api_keys_providers", []) != msg.get("api_keys_providers", []):
            continue
        if ("files" in case) != ("files" in msg):
            continue
        if case.get("settings") != msg.get("settings"):
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


# ─── Direction: token (SigV4 + token-exchange vectors) ───────────────

def op_sigv4_sign(msg: JsonObject) -> JsonObject:
    """Echo the pinned SigV4 triple for the vector whose request this is."""
    sig = json.loads(check.SIGV4_FILE.read_text(encoding="utf-8"))
    req = msg["request"]
    token = (msg.get("credential") or {}).get("session_token")
    for case in sig["cases"]:
        pinned = case["request"]
        # The session token is part of the identity: get-vanilla and
        # get-vanilla-with-session-token share one request and differ only
        # in the credential.
        if (pinned["method"], pinned["target"], pinned.get("headers", {}), pinned.get("body", ""),
                check.sigv4_session_token(case)) != (
            req["method"], req["url"].removeprefix("https://example.amazonaws.com"), req.get("headers", {}),
            req.get("body", ""), token,
        ):
            continue
        result = dict(case["expect"])
        if MUTATION == "sigv4_signature_drift" and targeted({"id": f"sigv4.{case['id']}"}):
            head, _, signature = result["authorization"].rpartition("Signature=")
            result["authorization"] = head + "Signature=" + "0" * len(signature)
        return result
    raise LookupError("no sigv4 vector matches this request")


def _token_cases(msg: JsonObject, suffix: str) -> list[JsonObject]:
    tok = json.loads(check.TOKEN_FILE.read_text(encoding="utf-8"))
    return [c for c in tok["cases"]
            if c["id"].endswith(suffix) and c["provider"] == msg["provider"] and c["rung"] == msg["rung"]]


def op_token_exchange_build(msg: JsonObject) -> JsonObject:
    """Echo the pinned exchange request.  The harness adds ``private_key_pem``
    to the input it sends (check.run_token_direction); strip it before matching."""
    sent = {k: v for k, v in msg["input"].items() if k != "private_key_pem"}
    for case in _token_cases(msg, ".build"):
        if check.expand_files(case["input"]) == sent:
            result = dict(case["expect"]["request"])
            if MUTATION == "token_assertion_drift" and targeted({"id": f"token.{case['id']}"}):
                result["body"] = {**result["body"], "assertion": result["body"]["assertion"] + "x"}
            return result
    raise LookupError("no token-exchange build vector matches this input")


def op_token_exchange_parse(msg: JsonObject) -> JsonObject:
    for case in _token_cases(msg, ".parse"):
        pinned = check.expand_files(case["input"])
        if (pinned["status"], pinned["body"]) != (msg["status"], msg["body"]):
            continue
        credential = dict(case["expect"]["credential"])
        if MUTATION == "token_credential_drift" and targeted({"id": f"token.{case['id']}"}):
            credential["expires_at"] = "1970-01-01T00:00:00Z"
        return {"ok": True, "credential": credential}
    raise LookupError("no token-exchange parse vector matches this response")


# ─── Endpoint surfaces: files / batch / generation ───────────────────

def _echo_wire(spec: JsonObject) -> JsonObject:
    """Echo a pinned wire block through the harness's own normalizer so the
    unmutated baseline is exactly green (auth rewrite, lowercase, noise)."""
    result = check.expected_wire_request(spec)
    raw = spec.get("request", {}).get("body_b64")
    if isinstance(raw, str):
        result["body_b64"] = raw
    return result


def find_generation_case(msg: JsonObject) -> JsonObject:
    for case in check.load_surface_cases("generation"):
        if (case["provider"] == msg["provider"] and case["kind"] == msg["kind"]
                and case["generation_request"] == msg["generation_request"]):
            return case
    raise LookupError("no generation case matches this (provider, kind, generation_request)")


def op_generation_build(msg: JsonObject) -> JsonObject:
    case = find_generation_case(msg)
    result = _echo_wire(case)
    if MUTATION == "gen_multipart_field_drop" and targeted(case) and result.get("body_b64"):
        raw = base64.b64decode(result["body_b64"])
        result["body_b64"] = base64.b64encode(raw.replace(b'name="model"', b'name="modell"', 1)).decode("ascii")
    return result


def op_generation_parse(msg: JsonObject) -> JsonObject:
    case = find_generation_case(msg)
    result = dict(json.loads(check.golden_path(case).read_text())["response"])
    result["provider_data"] = {"echo": "fixture"}  # presence is asserted, bulk is stripped
    if targeted(case):
        if MUTATION == "gen_wrong_media_type":
            if result.get("images"):
                result["images"] = [dict(result["images"][0], media_type="image/not-the-format"),
                                    *result["images"][1:]]
            elif isinstance(result.get("audio"), dict):
                result["audio"] = dict(result["audio"], media_type="audio/not-the-format")
        elif MUTATION == "gen_dropped_narration":
            result.pop("text", None)
    return result


def find_files_case(msg: JsonObject) -> JsonObject:
    for case in check.load_surface_cases("files"):
        if case["provider"] == msg["provider"]:
            return case
    raise LookupError("no files case for this provider")


def op_file_op_build(msg: JsonObject) -> JsonObject:
    case = find_files_case(msg)
    step = next(s for s in case["steps"] if s["file_op"] == msg["file_op"])
    result = _echo_wire(step)
    if MUTATION == "file_param_drop" and targeted(case) and result["params"]:
        result["params"].pop(sorted(result["params"])[0])
    return result


def op_file_op_parse(msg: JsonObject) -> JsonObject:
    case = find_files_case(msg)
    body = base64.b64decode(msg["body_b64"])
    step = next(s for s in case["steps"]
                if s.get("pinned_body") and (check.BODIES_DIR / case["id"] / s["pinned_body"]).read_bytes() == body)
    golden = json.loads(check.golden_path(case).read_text())
    value = dict(golden[step.get("golden_key", step["file_op"])])
    if MUTATION == "file_readiness_flip" and targeted(case) and value.get("readiness") == "ready":
        value["readiness"] = "pending"
    return {"file" if msg["kind"] == "info" else "page": value}


def find_batch_case(msg: JsonObject) -> JsonObject:
    for case in check.load_surface_cases("batch"):
        if case["provider"] == msg["provider"]:
            return case
    raise LookupError("no batch case for this provider")


def op_batch_op_build(msg: JsonObject) -> JsonObject:
    case = find_batch_case(msg)
    step = next(s for s in case["steps"] if s["action"] == msg["action"])
    return {"requests": [_echo_wire({"request": spec}) for spec in step.get("requests", [])]}


def op_batch_op_parse(msg: JsonObject) -> JsonObject:
    case = find_batch_case(msg)
    golden = json.loads(check.golden_path(case).read_text())
    kind = msg["kind"]
    if kind == "entries":
        entries = [dict(e) for e in golden["entries"]]
        if MUTATION == "batch_entry_order_swap" and targeted(case) and len(entries) >= 2:
            entries[0], entries[1] = entries[1], entries[0]
        return {"entries": entries}
    body = base64.b64decode(msg["body_b64"])
    step = next(s for s in case["steps"]
                if s.get("pinned_body") and s.get("parse") == kind
                and (check.BODIES_DIR / case["id"] / s["pinned_body"]).read_bytes() == body)
    value = golden[step.get("golden_key", step["action"])]
    if kind == "job":
        job = dict(value)
        if MUTATION == "batch_status_vocab_drift" and targeted(case) and job.get("status") == "completed":
            job["status"] = "ended"  # a wire word, not the canonical vocabulary
        return {"job": job}
    return {"jobs": value}


def find_cache_case(msg: JsonObject) -> JsonObject:
    for case in check.load_surface_cases("cache"):
        if case["provider"] == msg["provider"]:
            return case
    raise LookupError("no cache case for this provider")


def op_cache_op_build(msg: JsonObject) -> JsonObject:
    case = find_cache_case(msg)
    step = next(s for s in case["steps"] if s["cache_op"] == msg["cache_op"])
    result = _echo_wire(step)
    if MUTATION == "cache_model_drop" and targeted(case) and isinstance(result.get("body"), dict):
        result["body"] = {k: v for k, v in result["body"].items() if k != "model"}
    return result


def op_cache_op_parse(msg: JsonObject) -> JsonObject:
    case = find_cache_case(msg)
    body = base64.b64decode(msg["body_b64"])
    step = next(s for s in case["steps"]
                if s.get("pinned_body") and (check.BODIES_DIR / case["id"] / s["pinned_body"]).read_bytes() == body)
    golden = json.loads(check.golden_path(case).read_text())
    value = dict(golden[step.get("golden_key", step["cache_op"])])
    if MUTATION == "cache_expiry_drift" and targeted(case) and value.get("expires_at"):
        value["expires_at"] = "2099-01-01T00:00:00Z"
    return {"cache" if msg["kind"] == "info" else "page": value}


def find_video_case(msg: JsonObject) -> JsonObject:
    for case in check.load_surface_cases("video"):
        if case["provider"] == msg["provider"]:
            return case
    raise LookupError("no video case for this provider")


def op_video_op_build(msg: JsonObject) -> JsonObject:
    case = find_video_case(msg)
    step = next(s for s in case["steps"] if s["action"] == msg["action"])
    return {"requests": [_echo_wire({"request": spec}) for spec in step.get("requests", [])]}


def op_video_op_parse(msg: JsonObject) -> JsonObject:
    case = find_video_case(msg)
    golden = json.loads(check.golden_path(case).read_text())
    kind = msg["kind"]
    if kind == "part":
        part = dict(golden["part"])
        if MUTATION == "video_part_url_drift" and targeted(case) and part.get("url"):
            part["url"] = "https://not-the-recorded-host/video.mp4"
        return {"part": part}
    body = base64.b64decode(msg["body_b64"])
    step = next(s for s in case["steps"]
                if s.get("pinned_body") and s.get("parse") == kind
                and (check.BODIES_DIR / case["id"] / s["pinned_body"]).read_bytes() == body)
    value = golden[step.get("golden_key", step["action"])]
    if kind == "job":
        job = dict(value)
        if MUTATION == "video_status_vocab_drift" and targeted(case) and job.get("status") == "completed":
            job["status"] = "done"  # the wire word, not the canonical vocabulary
        return {"job": job}
    return {"jobs": value}


HANDLERS: dict[str, Callable[[JsonObject], JsonObject]] = {
    "capabilities": op_capabilities,
    "build_request": op_build_request,
    "parse_response": op_parse_response,
    "replay_stream": op_replay_stream,
    "normalize_error": op_normalize_error,
    "serde_roundtrip": op_serde_roundtrip,
    "explain_auth": op_explain_auth,
    "resolve_model": op_resolve_model,
    "build_models_request": op_build_models_request,
    "parse_models_response": op_parse_models_response,
    "replay_live": op_replay_live,
    "generation_build": op_generation_build,
    "generation_parse": op_generation_parse,
    "file_op_build": op_file_op_build,
    "file_op_parse": op_file_op_parse,
    "video_op_build": op_video_op_build,
    "video_op_parse": op_video_op_parse,
    "batch_op_build": op_batch_op_build,
    "batch_op_parse": op_batch_op_parse,
    "cache_op_build": op_cache_op_build,
    "cache_op_parse": op_cache_op_parse,
    "sigv4_sign": op_sigv4_sign,
    "token_exchange_build": op_token_exchange_build,
    "token_exchange_parse": op_token_exchange_parse,
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
    except PinnedRaise as exc:
        return {"id": req_id, "ok": False, "error": exc.error}
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
