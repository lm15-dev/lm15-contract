#!/usr/bin/env python3
"""changes/2026-09-30-claude-code-client-version.md, live.

Claude Code's server reads the release the claude-code door claims
(``user-agent: claude-cli/<version>``) and refuses a model when it is too
old.  This script collects the evidence for the new default, the
``client_version`` setting, the refusal's guidance, and the model's output
ceiling as the default ``max_tokens``:

  floor        claude-opus-5-5 with the old default 2.1.170 → the refusal
               (errors/cases/claude-code.json)
  setting      claude-opus-5-5 with settings client_version=2.1.280, the
               model's floor → 200 (cases/claude-code/client_version_setting.json)
  defaulted    claude-opus-5-5, no max_tokens, the new default release →
               200 with max_tokens 128000 non-streaming
               (cases/claude-code/max_tokens_defaulted.json)
  models       GET /v1/models: each model's max_tokens (receipt only)
  revalidate   the six claude-code tool_result cases re-sent with only the
               user-agent changed; the hidden oracle must still come back.
               The pinned response bodies and goldens stay: the request side
               is what changed (the case's provenance says so).
  anthropic    cases/anthropic/data_part_text.json re-sent with its new
               default max_tokens (claude-haiku-4-5: 64000), same method.

Credentials, never printed: the Claude Code login from
~/.claude/.credentials.json (lm15's own reader) and ANTHROPIC_API_KEY from
the environment (load ../.env explicitly before running):

    set -a; . ../.env; set +a
    ../lm15-python/.venv/bin/python research/providers/claude_code_client_version.py [--dry-run] [--only floor,setting]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, Capture, now_ts  # noqa: E402
from lm15 import Config, Message, Request, serde  # noqa: E402
from lm15.access import DEFAULT_CLAUDE_CODE_VERSION  # noqa: E402
from lm15.adaptation import adaptation_to_dict  # noqa: E402
from lm15.providers.base import HttpResponse  # noqa: E402

CHANGE = "changes/2026-09-30-claude-code-client-version.md"
OLD_VERSION = "2.1.170"
FLOOR = "2.1.280"  # claude-opus-5-5's minimum (the refusal names it)
MODEL = "claude-opus-5-5"
SAY_OK = Request(model=MODEL, messages=(Message.user("Say ok."),), config=Config(max_tokens=16))


def claude_code_capture() -> Capture:
    from lm15.auth import get_claude_code_access_token

    os.environ["LM15_CAPTURE_CREDENTIAL"] = get_claude_code_access_token()
    return Capture("claude-code", env_var="LM15_CAPTURE_CREDENTIAL", default_model=MODEL,
                   host="api.anthropic.com (Claude Code OAuth)", change_slug="claude-code-client-version")


def pin_user_agent(case_path: Path) -> None:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    case["compare_headers"] = ["user-agent"]
    case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def floor(cap: Capture) -> dict:
    cap.settings = {"client_version": OLD_VERSION}
    try:
        row = cap.probe("error-client-version-floor", SAY_OK)
    finally:
        cap.settings = {}
    if cap.dry_run:
        return row
    rec = json.loads((cap.receipts / "probe-error-client-version-floor.json").read_text(encoding="utf-8"))
    if rec["status"] != 400:
        sys.exit(f"floor: expected 400, got {rec['status']}: {row}")
    adapter = cap.lm()
    err = adapter.normalize_error(rec["status"], json.dumps(rec["body"]))
    exchange = str(cap.receipts.relative_to(CONTRACT) / cap.last_exchange)
    out = {
        "provenance": {"source": "live-capture", "date": rec["timestamp"][:10], "exchange": exchange,
                       "evidence": f"api.anthropic.com (Claude Code OAuth) HTTP 400 verbatim {rec['timestamp']}, {MODEL} with "
                                   f"user-agent claude-cli/{OLD_VERSION}; receipts/{cap.date}-claude-code/probe-error-client-version-floor.json; "
                                   f"the same refusal first seen 2026-09-23 (req_011CfKMizsVsBFXTfU7EVVhQ); {CHANGE}"},
        "cases": [{
            "id": "claude-code.client_version_floor",
            "provider": "claude-code",
            "status": rec["status"],
            "body": rec["body"],
            "expected": {"class": type(err).__name__, "code": err.code, "provider": "claude-code",
                         "provider_code": err.provider_code, "status": rec["status"],
                         # AUTH-10 (amended 2026-09-30): the server says "run
                         # claude update", which does not move what lm15 claims;
                         # the guidance names the setting that does.
                         "message": err.message},
            "provenance": {"source": "live-capture", "date": rec["timestamp"][:10], "exchange": exchange,
                           "evidence": f"verbatim body of receipts/{cap.date}-claude-code/probe-error-client-version-floor.json; "
                                       f"expected.message is the refusal plus the AUTH-10 guidance sentence ({CHANGE} D3), "
                                       "reviewed 2026-09-30"},
        }],
    }
    (CONTRACT / "errors" / "cases" / "claude-code.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**row, "message": err.message.splitlines()[0]}


def setting(cap: Capture, force: bool) -> dict:
    cap.settings = {"client_version": FLOOR}
    try:
        row = cap.write_case(
            "client_version_setting", SAY_OK, stream=False,
            description=(f"AUTH-10 backend settings (amended 2026-09-30): settings client_version={FLOOR} sends "
                         f"user-agent claude-cli/{FLOOR}, {MODEL}'s minimum; the header is compared (compare_headers) "
                         "because the server reads it"),
            expect_lm15=None, evidence_note=f"the setting at {MODEL}'s floor is accepted; {OLD_VERSION} is refused (errors/cases/claude-code.json)",
            force=force)
    finally:
        cap.settings = {}
    if not cap.dry_run and "skipped" not in row:
        pin_user_agent(CONTRACT / "cases" / "claude-code" / "client_version_setting.json")
    return row


def defaulted(cap: Capture, force: bool) -> dict:
    request = Request(model=MODEL, messages=(Message.user("Say ok."),))
    row = cap.write_case(
        "max_tokens_defaulted", request, stream=False,
        description=(f"MAP-7 rule 6 (amended 2026-09-30): no Config.max_tokens on {MODEL} sends its output ceiling, "
                     "128000 (thinking and answer together on the adaptive class), recorded as defaulted; the server "
                     f"accepts it non-streaming.  Also the new default release, claude-cli/{DEFAULT_CLAUDE_CODE_VERSION}, "
                     f"at or above {MODEL}'s floor"),
        expect_lm15={"adaptations": [{"field": "config.max_tokens", "action": "defaulted", "applied": 128000}]},
        evidence_note="default max_tokens 128000 accepted on a non-streaming call; default user-agent accepted",
        force=force)
    if not cap.dry_run and "skipped" not in row:
        pin_user_agent(CONTRACT / "cases" / "claude-code" / "max_tokens_defaulted.json")
    return row


def models(cap: Capture) -> dict:
    adapter = cap.lm()
    treq = adapter._models_request()
    status, raw, ts, _ = cap.send(treq)
    if cap.dry_run:
        return {"probe": "models", "status": status}
    data = json.loads(raw)
    ceilings = {e["id"]: e.get("max_tokens") for e in data.get("data", []) if isinstance(e, dict)}
    cap.write_receipt("models-max-tokens.json", {"timestamp": ts, "status": status, "sent": cap.wire_block(treq),
                                                 "exchange": cap.last_exchange, "max_tokens_by_model": ceilings, "body": data})
    return {"probe": "models", "status": status, "summary": json.dumps(ceilings)}


# ─── request-side revalidation of a pinned case ───────────────────────

def _answer(text: str):
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except ValueError:
        return None


def revalidate(cap: Capture, case_path: Path, judge, *, pin_ua: bool) -> dict:
    """Re-send a pinned case's request as the adapter builds it today.  Only
    the fields this change moves may differ from the pinned wire; anything
    else aborts (the change would be hiding a second edit)."""
    case = json.loads(case_path.read_text(encoding="utf-8"))
    request = serde.request_from_dict(case["canonical_request"])
    adapter = cap.lm()
    notes = adapter.plan(request)
    treq = adapter.build_request(request, stream=bool(case.get("stream")))
    wire = cap.wire_block(treq)
    pinned = case["request"]
    moved = []
    for name in {*wire["headers"], *pinned["headers"]}:
        if wire["headers"].get(name) != pinned["headers"].get(name):
            moved.append(f"header {name}: {pinned['headers'].get(name)!r} -> {wire['headers'].get(name)!r}")
    body_old, body_new = pinned["body"], wire["body"]
    for key in {*body_old, *body_new}:
        if body_old.get(key) != body_new.get(key):
            moved.append(f"body {key}: {json.dumps(body_old.get(key))[:60]} -> {json.dumps(body_new.get(key))[:60]}")
    allowed = {"header user-agent", "body max_tokens"}
    stray = [m for m in moved if m.split(":")[0] not in allowed]
    if stray or wire["url"] != pinned["url"] or wire["method"] != pinned["method"]:
        sys.exit(f"{case['id']}: the rebuilt wire differs beyond this change: {stray}")
    status, raw, ts, _ = cap.send(treq)
    if cap.dry_run:
        return {"feature": case["id"], "status": status, "moved": moved}
    cap.write_receipt(f"revalidate-{case['feature']}-{ts}-response.txt", raw.decode("utf-8", "replace"))
    if status != 200:
        sys.exit(f"{case['id']}: HTTP {status}: {cap.redact(raw.decode('utf-8', 'replace'))[:400]}")
    response = adapter.parse_response(request, HttpResponse(200, "OK", [], raw))
    verdict = judge(case, response)
    if not verdict.startswith("ok"):
        sys.exit(f"{case['id']}: the oracle did not come back: {verdict}")
    old = dict(case["provenance"])
    case["request"] = {**pinned, "headers": wire["headers"], "body": wire["body"]}
    if pin_ua:
        case["compare_headers"] = ["user-agent"]
    if notes and "adaptations" in (case.get("expect_lm15") or {}):
        # The pin carries field/action/asked/applied (the harness ignores reason).
        case["expect_lm15"]["adaptations"] = [{k: v for k, v in adaptation_to_dict(a).items() if k != "reason"} for a in notes]
    case["provenance"] = {
        "source": "live-capture",
        "date": ts[:10],
        "exchange": str(cap.receipts.relative_to(CONTRACT) / cap.last_exchange),
        "response_exchange": old.get("exchange"),
        "evidence": (f"request side re-validated {ts}: the wire the reference adapter builds today, which differs from "
                     f"the {old['date']} capture only in {'; '.join(moved)}, HTTP 200, {verdict}; response "
                     f"receipts/{cap.date}-{cap.provider}/revalidate-{case['feature']}-{ts}-response.txt; {CHANGE}.  "
                     f"The pinned body and golden are the {old['date']} capture's (response_exchange): {old['evidence']}"),
    }
    case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"feature": case["id"], "status": status, "verdict": verdict, "moved": moved}


def tool_result_judge(case: dict, response) -> str:
    """The hidden oracle of the 2026-09-07 run (visual-oracle.json beside its
    receipts) must come back — the model still receives the tool result."""
    oracle = json.loads((CONTRACT / Path(case["provenance"]["exchange"]).parent / "visual-oracle.json").read_text(encoding="utf-8"))
    expected = oracle["expected"]
    answer = _answer(response.text)
    cell = case["feature"].removeprefix("tool_result_")
    if cell == "error":
        return "ok: error acknowledged, nothing fabricated" if answer is None or answer.get("A") is None else f"fabricated {answer}"
    labels = ["A", "B"] if cell == "pair" else ["A"]
    got = {label: (answer or {}).get(label) for label in labels}
    want = {label: expected[label] for label in labels}
    return f"ok: oracle received {got}" if got == want else f"got {got}, want {want}"


def data_part_judge(case: dict, response) -> str:
    from lm15.types import DataPart

    parts = [p for p in response.message.parts if isinstance(p, DataPart)]
    return (f"ok: {len(parts)} data part(s), finish {response.finish_reason}" if parts and response.finish_reason == "stop"
            else f"parts {[type(p).__name__ for p in response.message.parts]}, finish {response.finish_reason}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="comma-separated: floor,setting,defaulted,models,revalidate,anthropic")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else {"floor", "setting", "defaulted", "models", "revalidate", "anthropic"}
    rows: list[dict] = []
    cap = claude_code_capture()
    cap.dry_run = args.dry_run
    if "floor" in only:
        rows.append(floor(cap))
    if "setting" in only:
        rows.append(setting(cap, args.force))
    if "defaulted" in only:
        rows.append(defaulted(cap, args.force))
    if "models" in only:
        rows.append(models(cap))
    if "revalidate" in only:
        for path in sorted((CONTRACT / "cases" / "claude-code").glob("tool_result_*.json")):
            rows.append(revalidate(cap, path, tool_result_judge, pin_ua=True))
    if not cap.dry_run:
        cap.write_receipt(f"SUMMARY-{now_ts()}.json", rows)
    if "anthropic" in only:
        api = Capture("anthropic", env_var="ANTHROPIC_API_KEY", default_model="claude-haiku-4-5",
                      host="api.anthropic.com", change_slug="claude-code-client-version")
        api.dry_run = args.dry_run
        row = revalidate(api, CONTRACT / "cases" / "anthropic" / "data_part_text.json", data_part_judge, pin_ua=False)
        rows.append(row)
        if not api.dry_run:
            api.write_receipt(f"SUMMARY-{now_ts()}.json", [row])
    for row in rows:
        print(cap.redact(json.dumps(row, ensure_ascii=False))[:600])


if __name__ == "__main__":
    main()
