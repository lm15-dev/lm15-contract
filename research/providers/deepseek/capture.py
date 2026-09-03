#!/usr/bin/env python3
"""DeepSeek live capture — the controlled validator for the `deepseek` provider.

Holds the key (``DEEPSEEK_API_KEY``), builds every request through the
reference adapter exactly as the router would (``lm15.vet.adapter_for_provider``
→ ``OpenAIChatLM`` with the ``deepseek`` compat preset and access policy
bound), sends the wire verbatim, and writes evidence in the contract's
shapes.  The key never reaches disk: wire blocks carry ``$DEEPSEEK_API_KEY``.

Writes (relative to lm15-contract):

- ``cases/deepseek/<feature>.json``      — wire case with canonical_request
- ``bodies/deepseek.<feature>/<ts>.txt`` — verbatim response / SSE
- ``errors/cases/deepseek.json``         — captured error envelopes
- ``receipts/<date>-deepseek/``          — probe outputs for the dossier's
                                            open decisions, models listing
- stdout                                 — the receipt table for changes/

Idempotent per feature: an existing case is overwritten only with
``--force``; bodies are append-only (dated) by rule.

Usage:
    DEEPSEEK_API_KEY=… python3 research/providers/deepseek/capture.py [--force]
        [--only basic_text,streaming,…] [--model deepseek-v4-flash]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(CONTRACT.parent / "lm15-python"))

from lm15 import Config, FunctionTool, Message, Reasoning, Request, serde  # noqa: E402
from lm15.errors import LM15Error  # noqa: E402
from lm15.providers.base import HttpResponse  # noqa: E402
from lm15.transports import StdlibTransport, TransportRequest  # noqa: E402
from lm15.types import ThinkingPart, ToolCallPart  # noqa: E402
from lm15.vet import _parse_stream_body, _response_result, adapter_for_provider, normalize_transport_request  # noqa: E402

PROVIDER = "deepseek"
PLACEHOLDER = "$DEEPSEEK_API_KEY"
DATE = time.strftime("%Y-%m-%d", time.gmtime())
RECEIPTS = CONTRACT / "receipts" / f"{DATE}-deepseek"
T = StdlibTransport()


def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())


DRY_RUN = False


def key() -> str:
    value = os.environ.get("DEEPSEEK_API_KEY", "")
    if DRY_RUN:
        return value or "dry-run-key"
    if not value:
        sys.exit("DEEPSEEK_API_KEY is not set; this script never reads a .env file")
    return value


def lm(model_key: str | None = None):
    return adapter_for_provider(PROVIDER, model_key or key())


def wire_block(treq) -> dict:
    norm = normalize_transport_request(treq)
    headers = {}
    for k, v in norm["headers"].items():
        headers[k] = f"Bearer {PLACEHOLDER}" if k.lower() == "authorization" else v
    return {"method": norm["method"], "url": norm["url"], "params": norm["params"], "headers": headers, "body": norm["body"]}


def send(treq) -> tuple[int, bytes, str, dict]:
    ts = now_ts()
    if DRY_RUN:
        print(json.dumps(wire_block(treq), indent=2, ensure_ascii=False))
        return 0, b"", ts, {}
    with T.stream(treq) as r:
        raw = r.read()
        return r.status, raw, ts, dict(r.headers)


def redact(text: str) -> str:
    k = os.environ.get("DEEPSEEK_API_KEY", "")
    return text.replace(k, PLACEHOLDER) if k else text


def write_receipt(name: str, payload: object) -> None:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2, ensure_ascii=False)
    (RECEIPTS / name).write_text(redact(text) + ("\n" if not text.endswith("\n") else ""))


def write_case(feature: str, request: Request, *, stream: bool, description: str, expect_lm15: dict | None,
               evidence_note: str, force: bool) -> dict:
    """Build through the adapter, send, pin body + case. Returns a receipt row."""
    case_path = CONTRACT / "cases" / PROVIDER / f"{feature}.json"
    if case_path.exists() and not force:
        return {"feature": feature, "skipped": "case exists (use --force)"}
    adapter = lm()
    treq = adapter.build_request(request, stream=stream)
    status, raw, ts, _ = send(treq)
    row = {"feature": feature, "status": status, "timestamp": ts, "model": request.model}
    if DRY_RUN:
        return row
    body_dir = CONTRACT / "bodies" / f"{PROVIDER}.{feature}"
    body_dir.mkdir(parents=True, exist_ok=True)
    body_name = f"{ts}.txt"
    (body_dir / body_name).write_bytes(raw)
    parsed_note = ""
    if status == 200:
        try:
            if stream:
                events = _parse_stream_body(adapter, request, raw)
                parsed_note = f"{len(events)} stream events"
            else:
                resp = adapter.parse_response(request, HttpResponse(status, "OK", [], raw))
                result = _response_result(resp)
                parsed_note = (f"finish={resp.finish_reason} usage={serde.usage_to_dict(resp.usage) if resp.usage else None} "
                               f"unmapped={result.get('unmapped')}")
                row["usage"] = serde.usage_to_dict(resp.usage) if resp.usage else None
                row["finish_reason"] = resp.finish_reason
                row["unmapped"] = result.get("unmapped")
        except Exception as exc:  # the capture must still land the body; the parse failure is the finding
            parsed_note = f"PARSE FAILED: {type(exc).__name__}: {exc}"
    row["parse"] = parsed_note
    case = {
        "id": f"{PROVIDER}.{feature}",
        "provider": PROVIDER,
        "feature": feature,
        "description": description,
        "base_url": adapter.base_url,
        "request": wire_block(treq),
        "expect": {"status": status},
        "provenance": {
            "source": "live-capture",
            "date": ts[:10],
            "evidence": f"api.deepseek.com {ts}, {request.model}, HTTP {status}; {evidence_note}; adapter-built wire "
                        f"(OpenAIChatLM, compat+access 'deepseek'); verbatim body at bodies/{PROVIDER}.{feature}/{body_name}; "
                        f"changes/{DATE}-deepseek-live.md",
        },
        "canonical_request": serde.request_to_dict(request),
        "canonical_request_provenance": {
            "source": "hand-authored",
            "date": ts[:10],
            "evidence": "authored with the case (research/providers/deepseek/capture.py); wire side generated by the "
                        "reference adapter and live-validated (receipt above)",
        },
        "pinned_body": body_name,
    }
    if stream:
        case["stream"] = True
    if expect_lm15:
        case["expect_lm15"] = expect_lm15
    case_path.parent.mkdir(parents=True, exist_ok=True)
    case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
    time.sleep(1.0)
    return row


# ─── the case set ────────────────────────────────────────────────────

WEATHER = FunctionTool(
    name="get_weather",
    description="Get current weather for a city",
    parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
)


def cases(model: str, force: bool, only: set[str] | None) -> list[dict]:
    rows = []

    def want(name: str) -> bool:
        return only is None or name in only

    if want("basic_text"):
        rows.append(write_case(
            "basic_text",
            Request(model=model, messages=(Message.user("Say ok."),), config=Config(max_tokens=600)),
            stream=False,
            description="DeepSeek basic_text (Chat Completions dialect; thinking mode on by default)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="reasoning_content expected alongside content (thinking default enabled, effort high)",
            force=force,
        ))
    if want("streaming"):
        rows.append(write_case(
            "streaming",
            Request(model=model, messages=(Message.user("Say ok."),), config=Config(max_tokens=600)),
            stream=True,
            description="DeepSeek streaming (SSE; stream_options.include_usage → usage on the final chunk)",
            expect_lm15=None,
            evidence_note="SSE terminated by data: [DONE]; usage on the last chunk",
            force=force,
        ))
    if want("reasoning_off"):
        rows.append(write_case(
            "reasoning_off",
            Request(model=model, messages=(Message.user("Say ok."),),
                    config=Config(max_tokens=100, reasoning=Reasoning(effort="off"))),
            stream=False,
            description="DeepSeek reasoning off (thinking: {type: disabled}); no reasoning_content, no reasoning tokens",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="explicit off must be honoured: expect reasoning_tokens 0/absent and no reasoning_content",
            force=force,
        ))
    if want("reasoning_low"):
        rows.append(write_case(
            "reasoning_low",
            Request(model=model, messages=(Message.user("Say ok."),),
                    config=Config(max_tokens=600, reasoning=Reasoning(effort="low"))),
            stream=False,
            description="DeepSeek reasoning effort low (thinking enabled + reasoning_effort: low)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="effort word passes verbatim (docs: low|high|max)",
            force=force,
        ))
    if want("tools"):
        rows.append(write_case(
            "tools",
            Request(model=model, messages=(Message.user("What is the weather in Paris? Use the tool."),),
                    tools=(WEATHER,), config=Config(max_tokens=600)),
            stream=False,
            description="DeepSeek tool call (function tools; reasoning_content in the same message)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_call ids of the call_00_… shape",
            force=force,
        ))
    if want("streaming_tool_call"):
        rows.append(write_case(
            "streaming_tool_call",
            Request(model=model, messages=(Message.user("What is the weather in Paris? Use the tool."),),
                    tools=(WEATHER,), config=Config(max_tokens=600)),
            stream=True,
            description="DeepSeek streaming tool call (MAP-9 premise: one streamed call per dialect)",
            expect_lm15=None,
            evidence_note="tool_calls deltas with index/id/arguments fragments",
            force=force,
        ))
    if want("multi_turn_tool_result"):
        # The load-bearing case for thinking_replay=native + include_empty:
        # turn 1 makes a call (captured live here, not scripted), the
        # tool result is sent back WITH the model's own reasoning_content,
        # and DeepSeek must answer 200 (docs: 400 when it is missing).
        first = Request(model=model, messages=(Message.user("What is the weather in Paris? Use the tool."),),
                        tools=(WEATHER,), config=Config(max_tokens=600))
        adapter = lm()
        status, raw, ts, _ = send(adapter.build_request(first, stream=False))
        if DRY_RUN:
            # Show the replay wire with a scripted turn-1 message instead.
            resp_message = Message.assistant((ThinkingPart(text="Need the tool."), ToolCallPart(id="call_00_dry", name="get_weather", input={"city": "Paris"})))
            calls = [p for p in resp_message.parts if isinstance(p, ToolCallPart)]
        else:
            resp = adapter.parse_response(first, HttpResponse(status, "OK", [], raw))
            resp_message = resp.message
            calls = [p for p in resp_message.parts if isinstance(p, ToolCallPart)]
        if not calls:
            rows.append({"feature": "multi_turn_tool_result", "skipped": f"turn 1 made no tool call (status {status})"})
        else:
            thinking = [p for p in resp_message.parts if isinstance(p, ThinkingPart)]
            second = Request(
                model=model,
                messages=(
                    first.messages[0],
                    resp_message,
                    Message.tool(calls[0].id, "Sunny, 22°C"),
                ),
                tools=(WEATHER,),
                config=Config(max_tokens=600),
            )
            rows.append(write_case(
                "multi_turn_tool_result",
                second,
                stream=False,
                description="DeepSeek tool result turn: the assistant turn is replayed with its reasoning_content "
                            "(thinking_replay=native); DeepSeek requires it whenever tools are present",
                expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
                evidence_note=f"turn-1 call {calls[0].name} {calls[0].input}, {len(thinking)} thinking part(s) replayed as reasoning_content",
                force=force,
            ))
    if want("response_format_json_object"):
        rows.append(write_case(
            "response_format_json_object",
            Request(model=model,
                    messages=(Message.developer("Answer in JSON with keys city and country."), Message.user("Where is the Eiffel Tower? Reply as json.")),
                    config=Config(max_tokens=300, response_format={"type": "json_object"})),
            stream=False,
            description="DeepSeek JSON Output (response_format: json_object; prompt mentions json per docs)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="the only structured mode DeepSeek documents",
            force=force,
        ))
    if want("system_prompt"):
        rows.append(write_case(
            "system_prompt",
            Request(model=model, messages=(Message.developer("You answer in exactly two words."), Message.user("Say ok.")),
                    config=Config(max_tokens=100, reasoning=Reasoning(effort="off"))),
            stream=False,
            description="DeepSeek system prompt (role: system; thinking off to keep the body small)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="instruction_role=system",
            force=force,
        ))
    if want("user_id"):
        rows.append(write_case(
            "user_id",
            Request(model=model, messages=(Message.user("Say ok."),),
                    config=Config(max_tokens=50, user_id="lm15-case-user", reasoning=Reasoning(effort="off"))),
            stream=False,
            description="DeepSeek user identity: Config.user_id rides DeepSeek's documented `user_id` field (compat user_field), not OpenAI's `user`",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="probe 2026-09-03: `user` and `user_id` both 200 with no echo; the documented name is sent",
            force=force,
        ))
    if want("models"):
        case_path = CONTRACT / "cases" / PROVIDER / "models.json"
        if case_path.exists() and not force:
            rows.append({"feature": "models", "skipped": "case exists (use --force)"})
        else:
            adapter = lm()
            treq = adapter._models_request()
            status, raw, ts, _ = send(treq)
            if DRY_RUN:
                rows.append({"feature": "models", "status": status})
                return rows
            body_dir = CONTRACT / "bodies" / f"{PROVIDER}.models"
            body_dir.mkdir(parents=True, exist_ok=True)
            (body_dir / f"{ts}.txt").write_bytes(raw)
            ids = [e.get("id") for e in json.loads(raw).get("data", [])] if status == 200 else []
            case_path.write_text(json.dumps({
                "id": f"{PROVIDER}.models", "provider": PROVIDER, "feature": "models", "surface": "models",
                "description": "DeepSeek model catalog listing (GET /models: ids and owned_by only)",
                "request": wire_block(treq),
                "provenance": {"source": "live-capture", "date": ts[:10],
                                "evidence": f"api.deepseek.com/models {ts}, HTTP {status}, {len(ids)} entries {ids}; "
                                            f"verbatim at bodies/{PROVIDER}.models/{ts}.txt; changes/{DATE}-deepseek-live.md"},
                "entries_key": "data", "pinned_body": f"{ts}.txt", "expect": {"status": status},
            }, indent=2, ensure_ascii=False) + "\n")
            write_receipt("models.json", json.loads(raw) if status == 200 else raw.decode("utf-8", "replace"))
            rows.append({"feature": "models", "status": status, "timestamp": ts, "entries": ids})
    return rows


# ─── probes for the dossier's open decisions (receipts only) ─────────

def probe(name: str, request: Request | None = None, *, raw_body: dict | None = None, model_key: str | None = None) -> dict:
    """Send one request; record status + body under receipts/. Never a case.

    ``raw_body`` replaces the adapter-built JSON body verbatim (for wire
    shapes lm15 does not emit, e.g. DeepSeek's own ``user_id``); the
    headers and URL still come from the adapter.
    """
    adapter = lm(model_key)
    base = request if request is not None else Request(model=raw_body["model"], messages=(Message.user("x"),))  # type: ignore[index]
    treq = adapter.build_request(base, stream=False)
    if raw_body is not None:
        treq = TransportRequest(method=treq.method, url=treq.url, headers=treq.headers,
                                body=json.dumps(raw_body).encode(), connect_timeout=treq.connect_timeout,
                                read_timeout=treq.read_timeout, write_timeout=treq.write_timeout)
    try:
        status, raw, ts, headers = send(treq)
    except LM15Error as exc:
        return {"probe": name, "error": f"{type(exc).__name__}: {exc}"}
    if DRY_RUN:
        return {"probe": name, "status": status}
    text = raw.decode("utf-8", "replace")
    try:
        body = json.loads(text)
    except ValueError:
        body = text
    write_receipt(f"probe-{name}.json", {"sent": wire_block(treq), "status": status, "body": body, "timestamp": ts,
                                          "response_headers": {k: v for k, v in headers.items() if k.lower() in ("content-type", "x-request-id")}})
    time.sleep(1.0)
    return {"probe": name, "status": status, "summary": _summary(body)}


def _summary(body) -> str:
    if isinstance(body, dict):
        if "error" in body:
            return json.dumps(body["error"])[:200]
        ch = (body.get("choices") or [{}])[0]
        msg = ch.get("message", {})
        u = body.get("usage", {})
        return (f"finish={ch.get('finish_reason')} content={str(msg.get('content'))[:60]!r} "
                f"reasoning={'yes' if msg.get('reasoning_content') else 'no'} usage_keys={sorted(u)} "
                f"details={u.get('prompt_tokens_details')} hit={u.get('prompt_cache_hit_tokens')}")
    return str(body)[:200]


def probes(model: str, only: set[str] | None) -> list[dict]:
    rows = []

    def want(name: str) -> bool:
        return only is None or name in only

    say = (Message.user("Say ok."),)
    if want("user_field"):
        # 1. lm15 sends `user`; DeepSeek documents `user_id`.
        rows.append(probe("user-field-user", Request(model=model, messages=say, config=Config(max_tokens=50, user_id="lm15-probe", reasoning=Reasoning(effort="off")))))
        rows.append(probe("user-field-user_id", raw_body={"model": model, "messages": [{"role": "user", "content": "Say ok."}],
                                                            "max_tokens": 50, "thinking": {"type": "disabled"}, "user_id": "lm15-probe"}))
        rows.append(probe("user-field-user_id-bad-chars", raw_body={"model": model, "messages": [{"role": "user", "content": "Say ok."}],
                                                                      "max_tokens": 50, "thinking": {"type": "disabled"}, "user_id": "bad id!"}))
    if want("minimal"):
        # 3. `minimal` is not in DeepSeek's list.
        rows.append(probe("effort-minimal", Request(model=model, messages=say, config=Config(max_tokens=200, reasoning=Reasoning(effort="minimal")))))
        rows.append(probe("effort-medium", Request(model=model, messages=say, config=Config(max_tokens=200, reasoning=Reasoning(effort="medium")))))
    if want("json_schema"):
        # 4. json_schema: loud 4xx, or silently treated as json_object?
        rows.append(probe("json-schema", Request(model=model, messages=(Message.user("Where is the Eiffel Tower? Reply as json."),),
                                                 config=Config(max_tokens=200, reasoning=Reasoning(effort="off"),
                                                               response_format={"type": "json_schema", "name": "place",
                                                                                "schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
                                                                                "strict": True}))))
    if want("temperature"):
        # 2. temperature in thinking mode: accepted silently per docs; echoed?
        rows.append(probe("temperature-thinking", Request(model=model, messages=say, config=Config(max_tokens=200, temperature=0.0))))
    if want("errors"):
        # Error envelope shape: 401 with a bad key, 400/404 with a bad model.
        rows.append(probe("error-unauthenticated", Request(model=model, messages=say, config=Config(max_tokens=10)), model_key="sk-invalid"))
        rows.append(probe("error-model-not-found", Request(model="deepseek-nonexistent", messages=say, config=Config(max_tokens=10))))
        rows.append(probe("error-bad-effort", raw_body={"model": model, "messages": [{"role": "user", "content": "Say ok."}],
                                                        "max_tokens": 10, "reasoning_effort": "bogus"}))
        rows.append(probe("error-missing-reasoning-content-with-tools", raw_body={
            "model": model, "max_tokens": 100,
            "messages": [{"role": "user", "content": "What is the weather in Paris? Use the tool."},
                         {"role": "assistant", "content": None,
                          "tool_calls": [{"id": "call_00_probe", "type": "function", "function": {"name": "get_weather", "arguments": "{\"city\":\"Paris\"}"}}]},
                         {"role": "tool", "tool_call_id": "call_00_probe", "content": "Sunny"}],
            "tools": [{"type": "function", "function": {"name": WEATHER.name, "description": WEATHER.description, "parameters": WEATHER.parameters}}],
        }))
    if want("usage_spelling"):
        # 5. Same prompt twice: the second should hit the cache; which usage keys carry it?
        req = Request(model=model, messages=(Message.developer("You are a helpful assistant. " * 40), Message.user("Say ok.")),
                      config=Config(max_tokens=20, reasoning=Reasoning(effort="off")))
        rows.append(probe("cache-usage-first", req))
        rows.append(probe("cache-usage-second", req))
    return rows


def errors_file(rows: list[dict]) -> None:
    """Fold the captured error envelopes into errors/cases/deepseek.json (verbatim bodies)."""
    out = {"provenance": {"source": "live-capture", "date": DATE,
                          "evidence": f"api.deepseek.com error envelopes captured verbatim {DATE} by research/providers/deepseek/capture.py; receipts/{DATE}-deepseek/probe-error-*.json"},
           "cases": []}
    for name, expected_class, expected_code in (
        ("unauthenticated", "AuthError", "auth"),
        ("model-not-found", None, None),
        ("bad-effort", None, None),
        ("missing-reasoning-content-with-tools", None, None),
    ):
        path = RECEIPTS / f"probe-error-{name}.json"
        if not path.exists():
            continue
        rec = json.loads(path.read_text())
        if rec["status"] < 400 or not isinstance(rec["body"], dict):
            continue
        adapter = adapter_for_provider(PROVIDER, "vet-parse-only")
        err = adapter.normalize_error(rec["status"], json.dumps(rec["body"]))
        out["cases"].append({
            "id": f"{PROVIDER}.{name.replace('-', '_')}",
            "provider": PROVIDER,
            "status": rec["status"],
            "body": rec["body"],
            "expected": {"class": type(err).__name__, "code": err.code, "provider": PROVIDER,
                         "provider_code": getattr(err, "provider_code", None), "status": rec["status"]},
            "provenance": {"source": "live-capture", "date": rec["timestamp"][:10],
                           "evidence": f"api.deepseek.com HTTP {rec['status']} verbatim {rec['timestamp']} — receipts/{DATE}-deepseek/probe-error-{name}.json; "
                                       "expected block is the reference's current mapping, DRAFT until reviewed"},
        })
    if out["cases"]:
        path = CONTRACT / "errors" / "cases" / f"{PROVIDER}.json"
        path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="overwrite existing case files")
    ap.add_argument("--only", help="comma-separated feature/probe names")
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--no-probes", action="store_true")
    ap.add_argument("--no-cases", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="build and print every wire; send nothing, write nothing")
    args = ap.parse_args()
    global DRY_RUN
    DRY_RUN = args.dry_run
    key()  # fail early
    only = set(args.only.split(",")) if args.only else None

    rows: list[dict] = []
    if not args.no_cases:
        rows += cases(args.model, args.force, only)
    if not args.no_probes:
        rows += probes(args.model, only)
        if not DRY_RUN:
            errors_file(rows)
    if not DRY_RUN:
        write_receipt("SUMMARY.json", rows)
    print(f"\nreceipts → {RECEIPTS}\n")
    print("| item | status | detail |\n|---|---|---|")
    for r in rows:
        name = r.get("feature") or r.get("probe")
        detail = r.get("skipped") or r.get("parse") or r.get("summary") or r.get("error") or r.get("entries") or ""
        print(f"| {name} | {r.get('status', '-')} | {str(detail)[:140]} |")


if __name__ == "__main__":
    main()
