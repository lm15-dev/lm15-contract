#!/usr/bin/env python3
"""A function tool with no description, live on every tool wire
(changes/2026-10-02-tool-description-absent.md, MAP-17).

Two modes, both through ``research/providers/_capture.py``:

``--probe``  The same request twice per wire: once with the tool's
             ``description`` sent as JSON ``null`` (what every SDK sent
             before MAP-17), once with the key left out.  Receipts only;
             nothing under ``cases/`` changes.  The live sessions (OpenAI
             Realtime, Gemini Live) get the same pair on their setup frame.

``--capture`` One case per dialect, ``cases/<provider>/tool_no_description.json``,
             built by the reference adapter (which must already leave the
             key out) and live-validated.

    set -a; source ../.env; set +a
    python3 research/providers/tool_description_absent.py --probe [--only anthropic,gemini]
    python3 research/providers/tool_description_absent.py --capture [--force]

Receipts: ``receipts/2026-10-02-tool-description/<provider>/``.
"""
from __future__ import annotations

import argparse
import base64
import dataclasses
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, Capture, now_ts  # noqa: E402
from lm15 import Config, FunctionTool, LiveConfig, Message, Request, serde  # noqa: E402
from lm15.types import LiveClientTextEvent  # noqa: E402

RECEIPTS = CONTRACT / "receipts" / "2026-10-02-tool-description"
CHANGE = "tool-description-absent"

# A tool with a name and a schema and nothing else: the shape the bug report
# described, and the one a caller gets from FunctionTool(name=..., parameters=...).
TOOL = FunctionTool(
    name="get_weather",
    parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
)
PROMPT = "What is the weather in Montreal? Use the tool."

# provider -> (key variable, model, host, case?)  `case` = this wire gets a
# pinned case in --capture (one per dialect builder); the others are probed
# to learn which servers refuse a null description, nothing more.
WIRES: dict[str, tuple[str, str, str, bool]] = {
    "anthropic": ("ANTHROPIC_API_KEY", "claude-haiku-4-5", "api.anthropic.com", True),
    "openai": ("OPENAI_API_KEY", "gpt-4.1-mini", "api.openai.com", True),
    "openai-chat": ("OPENAI_API_KEY", "gpt-4.1-mini", "api.openai.com", True),
    "gemini": ("GEMINI_API_KEY", "gemini-2.5-flash", "generativelanguage.googleapis.com", True),
    "groq": ("GROQ_API_KEY", "openai/gpt-oss-20b", "api.groq.com", False),
    "deepseek": ("DEEPSEEK_API_KEY", "deepseek-v4-flash", "api.deepseek.com", False),
    "deepseek-anthropic": ("DEEPSEEK_API_KEY", "deepseek-v4-flash", "api.deepseek.com/anthropic", False),
    "moonshotai": ("MOONSHOTAI_API_KEY", "kimi-k2.6", "api.moonshot.ai", False),
    "together": ("TOGETHER_API_KEY", "openai/gpt-oss-120b", "api.together.xyz", False),
    "zai": ("ZAI_API_KEY", "glm-5.3-flash", "api.z.ai", False),
    # Google's reference calls FunctionDeclaration.description "Required";
    # the enterprise door is probed too.  Credential: lm15's own Google
    # chain (ADC), pinned as a fixed bearer like every vertex case.
    "vertex": ("", "gemini-2.5-flash", "aiplatform.googleapis.com", False),
}
VERTEX_SETTINGS = {"project": "lm15-vertex-live", "location": "global"}
LIVE = {
    "openai": ("OPENAI_API_KEY", "gpt-realtime-mini", "api.openai.com"),
    "gemini": ("GEMINI_API_KEY", "gemini-3.1-flash-live-preview", "generativelanguage.googleapis.com"),
}
CASE_OK = {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}}


def request_for(model: str) -> Request:
    return Request(model=model, messages=(Message.user(PROMPT),), tools=(TOOL,), config=Config(max_tokens=512))


def tool_objects(body: object):
    """Every JSON object in the wire that declares our tool (each dialect
    nests it differently: tools[i], tools[i].function, functionDeclarations[j])."""
    if isinstance(body, dict):
        if body.get("name") == TOOL.name and any(k in body for k in ("parameters", "input_schema", "parametersJsonSchema")):
            yield body
        for value in body.values():
            yield from tool_objects(value)
    elif isinstance(body, list):
        for value in body:
            yield from tool_objects(value)


def with_description(body: dict, variant: str) -> dict:
    body = json.loads(json.dumps(body))
    found = list(tool_objects(body))
    if len(found) != 1:
        raise SystemExit(f"expected one tool declaration in the wire, found {len(found)}")
    if variant == "null":
        found[0]["description"] = None
    else:
        found[0].pop("description", None)
    return body


def cap_for(provider: str, env: str, model: str, host: str, *, dry: bool = False) -> Capture:
    cap = Capture(provider, env_var=env or "GOOGLE_ADC", default_model=model, host=host, change_slug=CHANGE)
    cap.receipts = RECEIPTS / provider
    cap.dry_run = dry
    if provider == "vertex":
        cap.settings = dict(VERTEX_SETTINGS)
        cap.bearer_fixture()
    return cap


def probe_http(provider: str, env: str, model: str, host: str, dry: bool) -> list[dict]:
    cap = cap_for(provider, env, model, host, dry=dry)
    rows = []
    for variant in ("null", "omitted"):
        treq = cap.lm().build_request(request_for(model), stream=False)
        body = with_description(json.loads(treq.body), variant)
        treq = dataclasses.replace(treq, body=json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode())
        status, raw, ts, _ = cap.send(treq)
        row = {"provider": provider, "wire": "http", "variant": variant, "model": model, "status": status,
               "timestamp": ts, "exchange": getattr(cap, "last_exchange", None)}
        if not dry:
            text = cap.redact(raw.decode("utf-8", "replace"))
            row["body_head"] = text[:400]
            cap.write_receipt(f"probe-{variant}-{ts}-response.txt", text)
        rows.append(row)
        time.sleep(1.0)
    return rows


# ─── live sessions ───────────────────────────────────────────────────

def live_lm(provider: str, key: str):
    from lm15.providers import GeminiLM, OpenAILM

    return OpenAILM(api_key=key) if provider == "openai" else GeminiLM(api_key=key)


def live_exchange(provider: str, model: str, key: str, setup: list[dict], frames: list[dict],
                  *, finish: bool) -> tuple[list[dict], dict | None]:
    """Open the socket, send setup (+ frames), read until the server
    accepts, refuses, or (``finish``) completes the turn.  Returns the
    verbatim server frames and the last decoded payload."""
    lm = live_lm(provider, key)
    rows: list[dict] = []
    last: dict | None = None
    connect = (lambda: lm._live_connect(lm._live_url(model), lm._live_headers())) if provider == "openai" \
        else (lambda: lm._live_connect(lm._live_url()))
    try:
        with connect() as ws:
            for frame in setup:
                ws.send(json.dumps(frame))
            sent_frames = False
            while True:
                raw = ws.recv(timeout=60)
                rows.append({"dir": "server", "frame_b64": base64.b64encode(raw).decode("ascii")} if isinstance(raw, bytes)
                            else {"dir": "server", "frame": raw})
                try:
                    last = json.loads(raw)
                except ValueError:
                    last = None
                kind = (last or {}).get("type") if provider == "openai" else None
                accepted = (kind == "session.updated") if provider == "openai" else ("setupComplete" in (last or {}))
                refused = (kind == "error") if provider == "openai" else ("error" in (last or {}))
                if refused:
                    return rows, last
                if accepted and not finish:
                    return rows, last
                if accepted and not sent_frames:
                    for frame in frames:
                        ws.send(json.dumps(frame))
                    sent_frames = True
                if provider == "openai" and kind in ("response.done", "response.error"):
                    return rows, last
                if provider == "gemini" and (((last or {}).get("serverContent") or {}).get("turnComplete")
                                             or "toolCall" in (last or {})):
                    return rows, last
    except Exception as exc:  # a server that closes the socket on a bad setup refuses it this way
        rows.append({"dir": "closed", "error": f"{type(exc).__name__}: {exc}"})
        return rows, None


def frame_text(row: dict) -> str:
    """A recorded server row as text (Gemini Live sends its JSON as binary frames)."""
    if "frame_b64" in row:
        return base64.b64decode(row["frame_b64"]).decode("utf-8", "replace")
    return row.get("frame", "")


def live_receipt(cap: Capture, ts: str, setup: list[dict], frames: list[dict], rows: list[dict], status: str, name: str) -> str:
    hashed = json.dumps({"setup": setup, "frames": frames}, separators=(",", ":"), ensure_ascii=False).encode()
    server = "".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n" for r in rows).encode()
    exchange = f"exchange-{ts}-{uuid.uuid4().hex}.json"
    cap.write_receipt(exchange, {
        "timestamp": ts, "provider": cap.provider, "surface": "live", "status": status, "probe": name,
        "sent": {"setup_frames": setup, "client_frames": frames},
        "request_sha256": hashlib.sha256(hashed).hexdigest(),
        "request_hash_format": "sha256 of UTF-8 compact JSON {setup, frames}: the client frames as sent (they carry no credential)",
        "response_sha256": hashlib.sha256(server).hexdigest(), "response_bytes": len(server),
        "response_hash_format": "sha256 of the server rows as JSONL (verbatim frames)",
        "server": rows,
    })
    return exchange


def probe_live(provider: str, dry: bool) -> list[dict]:
    env, model, host = LIVE[provider]
    cap = cap_for(provider, env, model, host)
    cap.dry_run = dry
    rows = []
    for variant in ("null", "omitted"):
        lm = live_lm(provider, "dry-run-key" if dry else cap._key_string())
        setup = [with_description(f, variant) if list(tool_objects(f)) else f
                 for f in lm._live_setup_frames(LiveConfig(model=model, tools=(TOOL,)))]
        if dry:
            print(json.dumps(setup, indent=2))
            continue
        ts = now_ts()
        frames, last = live_exchange(provider, model, cap._key_string(), setup, [], finish=False)
        accepted = any('"session.updated"' in frame_text(r) or "setupComplete" in frame_text(r) for r in frames)
        status = "accepted" if accepted else "refused"
        exchange = live_receipt(cap, ts, setup, [], frames, status, f"live-setup-{variant}")
        rows.append({"provider": provider, "wire": "live", "variant": variant, "model": model, "status": status,
                     "timestamp": ts, "exchange": exchange, "last": cap.redact(frame_text(frames[-1]) if "dir" in frames[-1] and frames[-1]["dir"] == "server" else json.dumps(frames[-1]))[:400] if frames else None})
        time.sleep(1.0)
    return rows


def capture_live(provider: str, force: bool) -> dict:
    """A complete live turn whose setup carries the tool without a description,
    pinned as ``cases/<provider>/live_tool_no_description.json``."""
    env, model, host = LIVE[provider]
    feature = "live_tool_no_description"
    case_path = CONTRACT / "cases" / provider / f"{feature}.json"
    if case_path.exists() and not force:
        return {"feature": feature, "skipped": "case exists (use --force)"}
    cap = cap_for(provider, env, model, host)
    key = cap._key_string()
    lm = live_lm(provider, key)
    config = LiveConfig(model=model, system="Use tools when asked. Be terse.", tools=(TOOL,))
    event = LiveClientTextEvent(text=PROMPT)
    setup = lm._live_setup_frames(config)
    if any("description" in t for f in setup for t in tool_objects(f)):
        raise SystemExit("the reference adapter still sends a description key for a tool without one; fix it first")
    frames = lm._live_encoder(config)(event)
    ts = now_ts()
    rows, last = live_exchange(provider, model, key, setup, frames, finish=True)
    called = any('"function_call"' in frame_text(r) or "toolCall" in frame_text(r) for r in rows)
    exchange = live_receipt(cap, ts, setup, frames, rows, "tool call" if called else "no tool call", feature)
    if not called:
        return {"feature": feature, "skipped": "the session did not end in a tool call; receipt kept, no case written",
                "exchange": exchange}
    transcript = [{"dir": "client", "kind": "setup", "frames": setup},
                  {"dir": "client", "kind": "event", "event": serde.live_client_event_to_dict(event), "frames": frames},
                  *rows]
    body_dir = CONTRACT / "bodies" / f"{provider}.{feature}"
    body_dir.mkdir(parents=True, exist_ok=True)
    body_name = f"{ts}.jsonl"
    (body_dir / body_name).write_text("".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n" for r in transcript),
                                      encoding="utf-8")
    case = {
        "id": f"{provider}.{feature}", "provider": provider, "feature": feature, "surface": "live",
        "description": "MAP-17: a function tool with no description reaches the live setup frame without a description key, "
                       "and the server accepts it and calls the tool",
        "provenance": {
            "source": "live-capture", "date": ts[:10],
            "evidence": f"{host} live session {ts}, {model}; setup built by the reference adapter, sent verbatim, "
                        f"{len(rows)} verbatim server frames ending in a tool call at bodies/{provider}.{feature}/{body_name}; "
                        f"changes/2026-10-02-{CHANGE}.md",
            "exchange": str(cap.receipts.relative_to(CONTRACT) / exchange),
        },
        "live_config": serde.live_config_to_dict(config), "pinned_body": body_name,
    }
    case_path.parent.mkdir(parents=True, exist_ok=True)
    case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"feature": feature, "provider": provider, "frames": len(rows), "exchange": exchange}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", action="store_true")
    mode.add_argument("--capture", action="store_true")
    ap.add_argument("--only", help="comma-separated providers")
    ap.add_argument("--no-live", action="store_true", help="skip the websocket sessions")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    chosen = set(args.only.split(",")) if args.only else None
    rows: list[dict] = []
    for provider, (env, model, host, pinned) in WIRES.items():
        if chosen is not None and provider not in chosen:
            continue
        if args.capture and not pinned:
            continue
        if env and not args.dry_run and not os.environ.get(env):
            rows.append({"provider": provider, "skipped": f"{env} not set"})
            continue
        if args.probe:
            rows.extend(probe_http(provider, env, model, host, args.dry_run))
        else:
            cap = cap_for(provider, env, model, host)
            cap.dry_run = args.dry_run
            rows.append(cap.write_case(
                "tool_no_description", request_for(model), stream=False,
                description="MAP-17: a function tool with no description reaches the wire without a description key "
                            "(never as null), and the model calls it",
                expect_lm15=CASE_OK,
                evidence_note=f"changes/2026-10-02-{CHANGE}.md; spec/types.md FunctionTool.description is omit-empty",
                force=args.force))
    if not args.no_live:
        for provider in LIVE:
            if chosen is not None and provider not in chosen:
                continue
            if not args.dry_run and not os.environ.get(LIVE[provider][0]):
                continue
            rows.extend(probe_live(provider, args.dry_run) if args.probe
                        else [capture_live(provider, args.force)] if not args.dry_run else [])
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
    if not args.dry_run:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        name = f"SUMMARY-{'probe' if args.probe else 'capture'}-{now_ts()}.json"
        text = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
        for env, *_ in [*WIRES.values(), *LIVE.values()]:
            if env and os.environ.get(env):
                text = text.replace(os.environ[env], f"${env}")
        (RECEIPTS / name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
