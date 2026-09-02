"""Seven live probes to settle what the independent review could not judge
offline (goldens/REVIEW-2026-09-02-independent.md §5). Receipts under
receipts/<tag>/<ts>.txt with the redacted request beside each; a results
table in 20-results.json. Budget: under $0.10.
"""
from __future__ import annotations

import hashlib, json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lm15-python"))
from lm15.transports import StdlibTransport, TransportRequest  # noqa: E402
from lm15.auth import get_xai_access_token  # noqa: E402

ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT.parents[1]
RECEIPTS = ROOT / "receipts"; RECEIPTS.mkdir(exist_ok=True)
T = StdlibTransport(); E = os.environ
SECRET = {"authorization", "x-api-key", "x-goog-api-key"}
RESULTS: list[dict] = []


def send(tag, url, headers, body, *, method="POST"):
    raw_body = json.dumps(body, separators=(",", ":")).encode()
    t0 = time.monotonic()
    with T.stream(TransportRequest(method, url, headers=list(headers.items()), body=raw_body)) as r:
        raw = r.read()
    ms = int((time.monotonic() - t0) * 1000)
    ts = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    d = RECEIPTS / tag.replace("/", "__"); d.mkdir(exist_ok=True)
    (d / f"{ts}.txt").write_bytes(raw)
    (d / f"{ts}.request.json").write_text(json.dumps({"url": url, "headers": {k: ("$REDACTED" if k.lower() in SECRET else v) for k, v in headers.items()}, "body": body}, indent=1))
    try:
        data = json.loads(raw)
    except Exception:
        data = {"_raw": raw[:400].decode(errors="replace")}
    return {"tag": tag, "ts": ts, "status": r.status, "ms": ms, "sha": hashlib.sha256(raw_body).hexdigest()[:16], "receipt": f"{d.name}/{ts}.txt"}, data, raw


def rec(row, summary):
    RESULTS.append({**row, "summary": summary})
    print(f"  {row['tag']:58s} HTTP {row['status']} {row['ms']:5d}ms  {json.dumps(summary)[:160]}")


def load_case(cid):
    prov, feat = cid.split(".", 1)
    return json.loads((CONTRACT / "cases" / prov / f"{feat}.json").read_text())


def body_of(cid):
    prov, feat = cid.split(".", 1)
    case = load_case(cid)
    return json.loads((CONTRACT / "bodies" / cid / case["pinned_body"]).read_text())


OAI = {"Authorization": f"Bearer {E['OPENAI_API_KEY']}", "Content-Type": "application/json"}
ANT = {"x-api-key": E["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
GEM = {"x-goog-api-key": E["GEMINI_API_KEY"], "content-type": "application/json"}
GROQ = {"Authorization": f"Bearer {E['GROQ_API_KEY']}", "Content-Type": "application/json"}


def probe1_gemini_text_signature():
    """Does the text-part thoughtSignature matter on replay? Same 2-turn
    request without and with it; compare status and thoughts spent."""
    case = load_case("gemini.thinking_level"); body = body_of("gemini.thinking_level")
    parts = body["candidates"][0]["content"]["parts"]
    text_part = [p for p in parts if not p.get("thought")][0]
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent"
    first_user = case["request"]["body"]["contents"][0]
    for variant, model_part in (("without", {"text": text_part["text"]}), ("with", dict(text_part))):
        req = {"contents": [first_user, {"role": "model", "parts": [model_part]}, {"role": "user", "parts": [{"text": "And is 15 one? One sentence."}]}],
               "generationConfig": {"maxOutputTokens": 400, "thinkingConfig": {"includeThoughts": True, "thinkingLevel": "low"}}}
        row, data, _ = send(f"gemini/3.7-flash/replay-text-signature-{variant}", url, GEM, req)
        um = data.get("usageMetadata", {})
        err = data.get("error", {}).get("message") if isinstance(data.get("error"), dict) else None
        rec(row, {"error": err, "thoughts": um.get("thoughtsTokenCount"), "out": um.get("candidatesTokenCount"), "total": um.get("totalTokenCount")})


def probe2_openai_retention():
    """MAP-6 rule 5 says retention='long' raises on gpt-5.6; pinned bodies echo prompt_cache_retention: '24h'."""
    case = load_case("openai.cache_off")
    req = dict(case["request"]["body"]); req.pop("prompt_cache_options", None)
    req["prompt_cache_retention"] = "24h"; req["max_output_tokens"] = 16
    row, data, _ = send("openai/gpt-5.6-sol/prompt_cache_retention-24h", "https://api.openai.com/v1/responses", OAI, req)
    err = data.get("error", {}).get("message") if isinstance(data.get("error"), dict) else None
    rec(row, {"error": err, "echo": data.get("prompt_cache_retention"), "usage": data.get("usage", {}).get("input_tokens_details")})


def probe3_openai_explicit_mode():
    """Does prompt_cache_options.mode=explicit stop the suffix write (cw>0 on warm calls)?"""
    case = load_case("openai.prompt_cache_breakpoint")
    base = dict(case["request"]["body"])
    base["prompt_cache_options"] = {**(base.get("prompt_cache_options") or {}), "mode": "explicit"}
    for i, q in enumerate(("Reply with the single word ALPHA.", "Reply with the single word BRAVO.")):
        req = json.loads(json.dumps(base))
        req["input"][-1]["content"][0]["text"] = q
        row, data, _ = send(f"openai/gpt-5.6-sol/breakpoint+explicit-{i}", "https://api.openai.com/v1/responses", OAI, req)
        err = data.get("error", {}).get("message") if isinstance(data.get("error"), dict) else None
        det = data.get("usage", {}).get("input_tokens_details", {})
        rec(row, {"error": err, "cached": det.get("cached_tokens"), "cache_write": det.get("cache_write_tokens"), "echo": data.get("prompt_cache_options")})
        time.sleep(1.5)


def probe4_groq_parsed():
    """MAP-7 rule 9 (Groq reasoning_format: parsed) has no receipt."""
    for fmt in (None, "parsed"):
        req = {"model": "qwen/qwen3.6-27b", "messages": [{"role": "user", "content": "What is 143 times 27? Answer with the number."}], "max_tokens": 400}
        if fmt: req["reasoning_format"] = fmt
        row, data, _ = send(f"groq/qwen3.6-27b/reasoning_format-{fmt or 'default'}", "https://api.groq.com/openai/v1/chat/completions", GROQ, req)
        err = data.get("error", {}).get("message") if isinstance(data.get("error"), dict) else None
        msg = (data.get("choices") or [{}])[0].get("message", {})
        rec(row, {"error": err, "reasoning_key": "reasoning" in msg, "reasoning_len": len(msg.get("reasoning") or ""), "content_has_think": "<think>" in (msg.get("content") or ""), "content": (msg.get("content") or "")[:60]})


def probe5_xai_allowlist():
    """MAP-8 rule 1 rests on one call; repeat five times with fresh nonces."""
    key = get_xai_access_token()
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    exp = CONTRACT / "research/tool-choice/receipts/xai__grok-4.6__tc:allow-lookup-ask-weather"
    req_file = sorted(exp.glob("*.request.json"))[0]
    base = json.loads(req_file.read_text())["body"]
    calls = []
    for i in range(5):
        req = json.loads(json.dumps(base))
        req["messages"][-1]["content"] += f" (nonce {i}-{int(time.time())})"
        row, data, _ = send(f"xai/grok-4.6/allow-lookup-ask-weather-rep{i}", "https://api.x.ai/v1/chat/completions", h, req)
        msg = (data.get("choices") or [{}])[0].get("message", {})
        named = [c["function"]["name"] for c in (msg.get("tool_calls") or [])]
        calls.append(named)
        rec(row, {"calls": named, "sent_tool_choice": req.get("tool_choice")})
    print(f"  xai allowlist: weather called in {sum('weather' in c for c in calls)}/5")


def probe6_anthropic_minimal():
    """MAP-7 rule 2: Sonnet 5 rejects effort minimal (grading table lacks it)."""
    case = load_case("anthropic.reasoning_adaptive")
    req = dict(case["request"]["body"]); req["output_config"] = {"effort": "minimal"}; req["max_tokens"] = 300
    row, data, _ = send("anthropic/claude-sonnet-5/effort-minimal", "https://api.anthropic.com/v1/messages", ANT, req)
    err = data.get("error", {}).get("message") if isinstance(data.get("error"), dict) else None
    rec(row, {"error": err, "usage": {k: v for k, v in data.get("usage", {}).items() if "tokens" in k}})


def probe7_streaming_tool_calls():
    """MAP-9 premise: every dialect names the call on its first fragment. Pin one SSE per dialect."""
    tool = {"name": "get_weather", "description": "Current weather for a city.", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}
    prompt = "What is the weather in Gatineau? Use the get_weather tool."
    runs = [
        ("openai/gpt-5.4-mini/stream-tool-call", "https://api.openai.com/v1/responses", OAI,
         {"model": "gpt-5.4-mini", "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}], "tools": [{"type": "function", **tool}], "stream": True, "reasoning": {"effort": "none"}}),
        ("openai_chat/gpt-5.4-mini/stream-tool-call", "https://api.openai.com/v1/chat/completions", OAI,
         {"model": "gpt-5.4-mini", "messages": [{"role": "user", "content": prompt}], "tools": [{"type": "function", "function": tool}], "stream": True, "stream_options": {"include_usage": True}}),
        ("anthropic/claude-haiku-4-5/stream-tool-call", "https://api.anthropic.com/v1/messages", ANT,
         {"model": "claude-haiku-4-5", "max_tokens": 300, "messages": [{"role": "user", "content": prompt}], "tools": [{"name": tool["name"], "description": tool["description"], "input_schema": tool["parameters"]}], "stream": True}),
        ("gemini/gemini-2.5-flash/stream-tool-call", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse", GEM,
         {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "tools": [{"functionDeclarations": [tool]}]}),
    ]
    for tag, url, h, req in runs:
        row, _, raw = send(tag, url, h, req)
        text = raw.decode(errors="replace")
        first_name_line = next((i for i, ln in enumerate(text.splitlines()) if "get_weather" in ln), None)
        first_call_line = next((i for i, ln in enumerate(text.splitlines()) if any(k in ln for k in ("tool_calls", "function_call", "tool_use", "functionCall"))), None)
        rec(row, {"bytes": len(raw), "first_call_frame_line": first_call_line, "first_name_line": first_name_line, "named_on_first_call_frame": first_name_line is not None and first_call_line is not None and first_name_line <= first_call_line})


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for fn in (probe1_gemini_text_signature, probe2_openai_retention, probe3_openai_explicit_mode, probe4_groq_parsed, probe5_xai_allowlist, probe6_anthropic_minimal, probe7_streaming_tool_calls):
        if only and fn.__name__ not in only:
            continue
        print(fn.__name__)
        try:
            fn()
        except Exception as exc:  # keep going; a failed probe is a finding too
            print(f"  FAILED: {type(exc).__name__}: {exc}")
            RESULTS.append({"tag": fn.__name__, "status": None, "summary": {"exception": f"{type(exc).__name__}: {exc}"}})
    (ROOT / "20-results.json").write_text(json.dumps({"ran": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "cells": RESULTS}, indent=1))
