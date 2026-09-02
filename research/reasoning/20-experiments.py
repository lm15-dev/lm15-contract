"""Reasoning design pass — step 5, the experiment matrix (2026-09-02).

Hand-built wire (the adapters under redesign must not shape the result).
Every call records status, reasoning-token usage, whether thinking text
came back, and a redacted request under receipts/.  Secrets never touch
disk.

Cells per (provider, model):
  default        no reasoning field at all
  effort=<v>     for v in none, minimal, low, medium, high, xhigh, max  (spelled per wire)
  budget         a token budget where the wire has one (floor probe: 1024 / 128 / 0)
  visible        ask for the trace/summary where the wire has a knob
  temperature    thinking on + temperature=0.2 (incompatibility probe)
  tool_replay    one tool call turn, then replay the assistant turn WITH and WITHOUT the
                 provider's reasoning state, to see what the next turn requires
"""
from __future__ import annotations

import hashlib, json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lm15-python"))
from lm15.transports import StdlibTransport, TransportRequest

ROOT = Path(__file__).resolve().parent
RECEIPTS = ROOT / "receipts"; RECEIPTS.mkdir(exist_ok=True)
SECRET = {"authorization", "x-api-key", "x-goog-api-key"}
T = StdlibTransport(); E = os.environ
Q = "What is 17 times 23? Reply with just the number."
RESULTS: list[dict] = []


def send(tag, method, url, headers, body):
    raw_body = json.dumps(body, separators=(",", ":")).encode()
    t0 = time.monotonic()
    with T.stream(TransportRequest(method, url, headers=list(headers.items()), body=raw_body)) as r:
        raw = r.read()
    ms = int((time.monotonic() - t0) * 1000)
    ts = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    d = RECEIPTS / tag.replace("/", "__"); d.mkdir(exist_ok=True)
    (d / f"{ts}.txt").write_bytes(raw)
    (d / f"{ts}.request.json").write_text(json.dumps({"method": method, "url": url, "headers": {k: ("$REDACTED" if k.lower() in SECRET else v) for k, v in headers.items()}, "body": body}, indent=1))
    try:
        data = json.loads(raw)
    except Exception:
        data = {"_raw": raw[:300].decode(errors="replace")}
    return {"tag": tag, "ts": ts, "status": r.status, "ms": ms, "sha": hashlib.sha256(raw_body).hexdigest()[:16], "receipt": f"{d.name}/{ts}.txt"}, data


def rec(row, cell, summary, note=""):
    row = {**row, "cell": cell, "summary": summary}
    if note: row["note"] = note
    RESULTS.append(row)
    print(f"  {cell:22s} HTTP {row['status']} {row['ms']:5d}ms  {summary}")
    return row


# ─── OpenAI Responses ────────────────────────────────────────────────

def openai_summary(d):
    if d.get("error"):
        return {"error": (d["error"].get("message") or "")[:110]}
    out = d.get("output", [])
    reasoning = [i for i in out if i.get("type") == "reasoning"]
    return {"reasoning_tokens": ((d.get("usage") or {}).get("output_tokens_details") or {}).get("reasoning_tokens"),
            "reasoning_items": len(reasoning), "has_summary": any(i.get("summary") for i in reasoning),
            "has_encrypted": any(i.get("encrypted_content") for i in reasoning),
            "text": next((c.get("text") for i in out if i.get("type") == "message" for c in i.get("content", []) if c.get("type") == "output_text"), None)}


def run_openai(model):
    print(f"=== openai/{model} ===")
    h = {"Authorization": f"Bearer {E['OPENAI_API_KEY']}", "Content-Type": "application/json"}
    url = "https://api.openai.com/v1/responses"
    base = lambda **kw: {"model": model, "input": Q, "max_output_tokens": 4000, **kw}  # noqa: E731
    row, d = send(f"openai/{model}/default", "POST", url, h, base()); rec(row, "default", openai_summary(d))
    for eff in ["none", "minimal", "low", "medium", "high", "xhigh", "max"]:
        row, d = send(f"openai/{model}/effort", "POST", url, h, base(reasoning={"effort": eff})); rec(row, f"effort={eff}", openai_summary(d))
    row, d = send(f"openai/{model}/summary", "POST", url, h, base(reasoning={"effort": "low", "summary": "auto"})); rec(row, "summary=auto", openai_summary(d))
    row, d = send(f"openai/{model}/stateless", "POST", url, h, base(reasoning={"effort": "low"}, store=False)); rec(row, "store=false", openai_summary(d), "encrypted_content by default in stateless mode?")
    row, d = send(f"openai/{model}/temperature", "POST", url, h, base(reasoning={"effort": "low"}, temperature=0.2)); rec(row, "temperature", openai_summary(d))
    # tool replay: turn 1 with a tool, then turn 2 replaying with / without the reasoning item
    tools = [{"type": "function", "name": "lookup", "description": "Look up a number.", "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}, "required": ["n"]}}]
    row, d = send(f"openai/{model}/tool_turn1", "POST", url, h, base(input="Use lookup with n=7 and tell me the result.", tools=tools, reasoning={"effort": "low"}, store=False))
    rec(row, "tool_turn1", openai_summary(d))
    out = d.get("output", [])
    call = next((i for i in out if i.get("type") == "function_call"), None)
    if call:
        history_full = [{"role": "user", "content": "Use lookup with n=7 and tell me the result."}, *out, {"type": "function_call_output", "call_id": call["call_id"], "output": "49"}]
        history_stripped = [i for i in history_full if i.get("type") != "reasoning"]
        row, d = send(f"openai/{model}/tool_turn2_with_reasoning", "POST", url, h, base(input=history_full, tools=tools, reasoning={"effort": "low"}, store=False)); rec(row, "turn2+reasoning", openai_summary(d))
        row, d = send(f"openai/{model}/tool_turn2_stripped", "POST", url, h, base(input=history_stripped, tools=tools, reasoning={"effort": "low"}, store=False)); rec(row, "turn2-reasoning", openai_summary(d), "reasoning items removed from history")


# ─── Anthropic ───────────────────────────────────────────────────────

def anth_summary(d):
    if d.get("type") == "error":
        return {"error": d["error"].get("message", "")[:120]}
    blocks = d.get("content", [])
    u = d.get("usage") or {}
    return {"thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens"), "output_tokens": u.get("output_tokens"),
            "thinking_blocks": sum(1 for b in blocks if b.get("type") in ("thinking", "redacted_thinking")),
            "signed": any(b.get("signature") for b in blocks if b.get("type") == "thinking"),
            "text": next((b.get("text") for b in blocks if b.get("type") == "text"), None), "stop": d.get("stop_reason")}


def run_anthropic(model):
    print(f"=== anthropic/{model} ===")
    h = {"x-api-key": E["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    url = "https://api.anthropic.com/v1/messages"
    base = lambda **kw: {"model": model, "max_tokens": 4000, "messages": [{"role": "user", "content": Q}], **kw}  # noqa: E731
    row, d = send(f"anthropic/{model}/default", "POST", url, h, base()); rec(row, "default", anth_summary(d))
    row, d = send(f"anthropic/{model}/adaptive", "POST", url, h, base(thinking={"type": "adaptive"})); rec(row, "adaptive", anth_summary(d))
    for eff in ["low", "medium", "high", "xhigh", "max"]:
        row, d = send(f"anthropic/{model}/effort", "POST", url, h, base(thinking={"type": "adaptive"}, output_config={"effort": eff})); rec(row, f"adaptive+effort={eff}", anth_summary(d))
    row, d = send(f"anthropic/{model}/effort_no_thinking", "POST", url, h, base(output_config={"effort": "low"})); rec(row, "effort, no thinking", anth_summary(d), "effort applies to all tokens even without thinking?")
    for budget in [1024, 128]:
        row, d = send(f"anthropic/{model}/budget", "POST", url, h, base(thinking={"type": "enabled", "budget_tokens": budget})); rec(row, f"enabled budget={budget}", anth_summary(d))
    row, d = send(f"anthropic/{model}/temperature", "POST", url, h, base(thinking={"type": "adaptive"}, temperature=0.2)); rec(row, "adaptive+temperature", anth_summary(d))
    row, d = send(f"anthropic/{model}/forced_tool", "POST", url, h, base(thinking={"type": "adaptive"}, tools=[{"name": "lookup", "input_schema": {"type": "object", "properties": {"n": {"type": "integer"}}}}], tool_choice={"type": "tool", "name": "lookup"})); rec(row, "adaptive+forced tool", anth_summary(d))
    HARD = "Use lookup with n=7, then explain in one sentence whether 7 is a Mersenne prime. Think it through carefully."
    row, d = send(f"anthropic/{model}/hard", "POST", url, h, base(messages=[{"role": "user", "content": HARD}], thinking={"type": "adaptive"}, output_config={"effort": "high"})); rec(row, "hard prompt", anth_summary(d))
    # tool replay with and without the thinking block
    tools = [{"name": "lookup", "description": "Look up a number.", "input_schema": {"type": "object", "properties": {"n": {"type": "integer"}}, "required": ["n"]}}]
    row, d = send(f"anthropic/{model}/tool_turn1", "POST", url, h, base(messages=[{"role": "user", "content": HARD}], tools=tools, thinking={"type": "adaptive"}, output_config={"effort": "high"}))
    rec(row, "tool_turn1", anth_summary(d))
    if d.get("content"):
        call = next((b for b in d["content"] if b.get("type") == "tool_use"), None)
        if call:
            assistant_full = d["content"]; assistant_stripped = [b for b in d["content"] if b.get("type") not in ("thinking", "redacted_thinking")]
            for label, asst in (("turn2+thinking", assistant_full), ("turn2-thinking", assistant_stripped)):
                msgs = [{"role": "user", "content": HARD}, {"role": "assistant", "content": asst},
                        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": call["id"], "content": "49"}]}]
                row, d2 = send(f"anthropic/{model}/{label}", "POST", url, h, base(messages=msgs, tools=tools, thinking={"type": "adaptive"}, output_config={"effort": "high"})); rec(row, label, anth_summary(d2))


# ─── Gemini ──────────────────────────────────────────────────────────

def gem_summary(d):
    if "error" in d:
        return {"error": d["error"].get("message", "")[:120]}
    cand = (d.get("candidates") or [{}])[0]
    parts = (cand.get("content") or {}).get("parts", [])
    u = d.get("usageMetadata", {})
    return {"thoughts_tokens": u.get("thoughtsTokenCount"), "output_tokens": u.get("candidatesTokenCount"),
            "thought_parts": sum(1 for p in parts if p.get("thought")), "signed": any(p.get("thoughtSignature") for p in parts),
            "text": next((p.get("text") for p in parts if not p.get("thought") and "text" in p), None), "finish": cand.get("finishReason")}


def run_gemini(model):
    print(f"=== gemini/{model} ===")
    h = {"x-goog-api-key": E["GEMINI_API_KEY"], "Content-Type": "application/json"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    base = lambda gen=None, **kw: {"contents": [{"role": "user", "parts": [{"text": Q}]}], "generationConfig": {"maxOutputTokens": 4000, **(gen or {})}, **kw}  # noqa: E731
    row, d = send(f"gemini/{model}/default", "POST", url, h, base()); rec(row, "default", gem_summary(d))
    for lvl in ["minimal", "low", "medium", "high"]:
        row, d = send(f"gemini/{model}/level", "POST", url, h, base({"thinkingConfig": {"thinkingLevel": lvl}})); rec(row, f"thinkingLevel={lvl}", gem_summary(d))
    for b in [0, -1, 128, 1024]:
        row, d = send(f"gemini/{model}/budget", "POST", url, h, base({"thinkingConfig": {"thinkingBudget": b}})); rec(row, f"thinkingBudget={b}", gem_summary(d))
    row, d = send(f"gemini/{model}/include", "POST", url, h, base({"thinkingConfig": {"includeThoughts": True}})); rec(row, "includeThoughts", gem_summary(d))
    row, d = send(f"gemini/{model}/temperature", "POST", url, h, base({"thinkingConfig": {"thinkingLevel": "low"}, "temperature": 0.2})); rec(row, "level+temperature", gem_summary(d))
    tools = [{"functionDeclarations": [{"name": "lookup", "description": "Look up a number.", "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}, "required": ["n"]}}]}]
    row, d = send(f"gemini/{model}/tool_turn1", "POST", url, h, base(contents=[{"role": "user", "parts": [{"text": "Use lookup with n=7 and tell me the result."}]}], tools=tools))
    rec(row, "tool_turn1", gem_summary(d))
    cand = (d.get("candidates") or [{}])[0]; parts = (cand.get("content") or {}).get("parts", [])
    call = next((p for p in parts if "functionCall" in p), None)
    if call:
        full = parts; stripped = [{k: v for k, v in p.items() if k != "thoughtSignature"} for p in parts if not p.get("thought")]
        for label, asst in (("turn2+signature", full), ("turn2-signature", stripped)):
            contents = [{"role": "user", "parts": [{"text": "Use lookup with n=7 and tell me the result."}]}, {"role": "model", "parts": asst},
                        {"role": "user", "parts": [{"functionResponse": {"name": "lookup", "response": {"result": "49"}}}]}]
            row, d2 = send(f"gemini/{model}/{label}", "POST", url, h, base(contents=contents, tools=tools)); rec(row, label, gem_summary(d2))


# ─── Chat-dialect providers (xAI, Groq) ──────────────────────────────

def chat_summary(d):
    if "error" in d:
        err = d["error"]; return {"error": (err.get("message") if isinstance(err, dict) else str(err))[:120]}
    ch = (d.get("choices") or [{}])[0]; msg = ch.get("message", {}); u = d.get("usage", {})
    return {"reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
            "has_reasoning_content": bool(msg.get("reasoning_content") or msg.get("reasoning")), "text": (msg.get("content") or "")[:40]}


def run_chat(name, url, key, model, efforts, extra_cells=()):
    print(f"=== {name}/{model} ===")
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    base = lambda **kw: {"model": model, "messages": [{"role": "user", "content": Q}], "max_tokens": 4000, **kw}  # noqa: E731
    row, d = send(f"{name}/{model}/default", "POST", url, h, base()); rec(row, "default", chat_summary(d))
    for eff in efforts:
        row, d = send(f"{name}/{model}/effort", "POST", url, h, base(reasoning_effort=eff)); rec(row, f"reasoning_effort={eff}", chat_summary(d))
    for label, kw in extra_cells:
        row, d = send(f"{name}/{model}/{label}", "POST", url, h, base(**kw)); rec(row, label, chat_summary(d))


if __name__ == "__main__" and "--rerun" in sys.argv:
    prev = json.loads((ROOT / "20-results.json").read_text())["results"]
    RESULTS.extend(r for r in prev if not r["tag"].startswith("openai/"))
    for model in ["gpt-5.6-sol", "gpt-5.4-mini"]:
        try: run_openai(model)
        except Exception as e: print("  !!", e)
    (ROOT / "20-results.json").write_text(json.dumps({"date": "2026-09-02", "results": RESULTS}, indent=1))
    print(f"\n{len(RESULTS)} rows -> 20-results.json"); sys.exit(0)

if __name__ == "__main__":
    from lm15.auth import get_xai_access_token
    for model in ["gpt-5.6-sol", "gpt-5.4-mini"]:
        try: run_openai(model)
        except Exception as e: print("  !!", e)
    for model in ["claude-sonnet-5", "claude-sonnet-4-5", "claude-haiku-4-5-20251001"]:
        try: run_anthropic(model)
        except Exception as e: print("  !!", e)
    for model in ["gemini-2.5-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"]:
        try: run_gemini(model)
        except Exception as e: print("  !!", e)
    try:
        run_chat("xai", "https://api.x.ai/v1/chat/completions", get_xai_access_token(), "grok-4.6", ["none", "low", "medium", "high", "xhigh", "max"],
                 [("thinking_disabled", {"thinking": {"type": "disabled"}}), ("temperature+effort", {"reasoning_effort": "low", "temperature": 0.2})])
    except Exception as e: print("  !!", e)
    for model, efforts in [("openai/gpt-oss-20b", ["none", "low", "medium", "high"]), ("qwen/qwen3.6-27b", ["none", "default", "low", "medium", "high"])]:
        try:
            run_chat("groq", "https://api.groq.com/openai/v1/chat/completions", E["GROQ_API_KEY"], model, efforts,
                     [("include_reasoning=false", {"include_reasoning": False})])
        except Exception as e: print("  !!", e)
    (ROOT / "20-results.json").write_text(json.dumps({"date": "2026-09-02", "results": RESULTS}, indent=1))
    print(f"\n{len(RESULTS)} rows -> 20-results.json")
