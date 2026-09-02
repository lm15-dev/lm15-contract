"""Tool choice + structured output — step 5, one matrix (2026-09-02).

Hand-built wire.  Records status, calls, finish reason, JSON validity, and
the error text for each cell under receipts/ (redacted headers).

Tool-choice cells: auto | required (no tool needed) | none (tool needed) |
force B (prompt asks A) | allowlist {A} (prompt asks B) | parallel=false
(prompt asks two) | forced + structured output.
Structured-output cells: json_object | schema strict (all required,
additionalProperties false) | schema with an optional field | schema with
minimum/format/pattern | schema with $ref | schema with anyOf | schema +
tools | schema + thinking.
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
RESULTS: list[dict] = []

LOOKUP = {"name": "lookup", "description": "Look up a number.", "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}, "required": ["n"]}}
WEATHER = {"name": "weather", "description": "Get the weather for a city.", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}
P_LOOKUP = "Look up n=7 with the lookup tool."
P_WEATHER = "What is the weather in Paris? Use the weather tool."
P_HELLO = "Say hello in one word."
P_TWO = "Look up n=7 and n=8 with the lookup tool, both."
P_EXTRACT = "Extract the person: John is 34 years old, email john@x.io, code ABC."
S_STRICT = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name", "age"], "additionalProperties": False}
S_OPTIONAL = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name"], "additionalProperties": False}
S_KEYWORDS = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0, "maximum": 150}, "email": {"type": "string", "format": "email"}, "code": {"type": "string", "pattern": "^[A-Z]{3}$"}}, "required": ["name", "age", "email", "code"], "additionalProperties": False}
S_REF = {"type": "object", "properties": {"person": {"$ref": "#/$defs/Person"}}, "required": ["person"], "additionalProperties": False, "$defs": {"Person": {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name", "age"], "additionalProperties": False}}}
S_ANYOF = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"anyOf": [{"type": "integer"}, {"type": "null"}]}}, "required": ["name", "age"], "additionalProperties": False}


def send(tag, url, headers, body):
    raw_body = json.dumps(body, separators=(",", ":")).encode(); t0 = time.monotonic()
    with T.stream(TransportRequest("POST", url, headers=list(headers.items()), body=raw_body)) as r:
        raw = r.read()
    ms = int((time.monotonic() - t0) * 1000); ts = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    d = RECEIPTS / tag.replace("/", "__"); d.mkdir(exist_ok=True)
    (d / f"{ts}.txt").write_bytes(raw)
    (d / f"{ts}.request.json").write_text(json.dumps({"url": url, "headers": {k: ("$REDACTED" if k.lower() in SECRET else v) for k, v in headers.items()}, "body": body}, indent=1))
    try: data = json.loads(raw)
    except Exception: data = {"_raw": raw[:300].decode(errors="replace")}
    return {"tag": tag, "ts": ts, "status": r.status, "ms": ms, "sha": hashlib.sha256(raw_body).hexdigest()[:16], "receipt": f"{d.name}/{ts}.txt"}, data


def rec(row, cell, summary):
    row = {**row, "cell": cell, "summary": summary}; RESULTS.append(row)
    print(f"  {cell:26s} HTTP {row['status']} {row['ms']:5d}ms  {summary}")


def json_ok(text):
    if text is None: return None
    try: json.loads(text); return True
    except Exception: return False


# ─── per-provider builders + summarizers ──────────────────────────────

class OpenAIResponses:
    name = "openai-responses"; url = "https://api.openai.com/v1/responses"
    def __init__(self, model): self.model = model; self.h = {"Authorization": f"Bearer {E['OPENAI_API_KEY']}", "Content-Type": "application/json"}
    def tools(self, *t): return [{"type": "function", **x} for x in t]
    def body(self, prompt, *, tools=None, choice=None, parallel=None, schema=None, json_mode=False, strict=True, thinking=None):
        b = {"model": self.model, "input": prompt, "max_output_tokens": 600}
        if tools: b["tools"] = self.tools(*tools)
        if choice is not None: b["tool_choice"] = choice
        if parallel is not None: b["parallel_tool_calls"] = parallel
        if json_mode: b["text"] = {"format": {"type": "json_object"}}
        if schema: b["text"] = {"format": {"type": "json_schema", "name": "person", "schema": schema, "strict": strict}}
        if thinking: b["reasoning"] = {"effort": thinking}
        return b
    def force(self, n): return {"type": "function", "name": n}
    def allow(self, *n): return {"type": "allowed_tools", "mode": "auto", "tools": [{"type": "function", "name": x} for x in n]}
    def summary(self, d):
        if d.get("error"): return {"error": d["error"].get("message", "")[:120]}
        out = d.get("output", []); calls = [i["name"] for i in out if i.get("type") == "function_call"]
        text = next((c.get("text") for i in out if i.get("type") == "message" for c in i.get("content", []) if c.get("type") == "output_text"), None)
        return {"calls": calls, "status": d.get("status"), "incomplete": (d.get("incomplete_details") or {}).get("reason"), "json": json_ok(text), "text": (text or "")[:60]}


class OpenAIChat:
    name = "openai-chat"; url = "https://api.openai.com/v1/chat/completions"
    def __init__(self, model, key=None, url=None, name=None):
        self.model = model; self.h = {"Authorization": f"Bearer {key or E['OPENAI_API_KEY']}", "Content-Type": "application/json"}
        if url: self.url = url
        if name: self.name = name
    def tools(self, *t): return [{"type": "function", "function": x} for x in t]
    def body(self, prompt, *, tools=None, choice=None, parallel=None, schema=None, json_mode=False, strict=True, thinking=None):
        b = {"model": self.model, "messages": [{"role": "user", "content": prompt}], ("max_completion_tokens" if self.name == "openai-chat" else "max_tokens"): 600}
        if tools: b["tools"] = self.tools(*tools)
        if choice is not None: b["tool_choice"] = choice
        if parallel is not None: b["parallel_tool_calls"] = parallel
        if json_mode: b["response_format"] = {"type": "json_object"}
        if schema: b["response_format"] = {"type": "json_schema", "json_schema": {"name": "person", "schema": schema, "strict": strict}}
        if thinking: b["reasoning_effort"] = thinking
        return b
    def force(self, n): return {"type": "function", "function": {"name": n}}
    def allow(self, *n): return {"type": "allowed_tools", "allowed_tools": {"mode": "auto", "tools": [{"type": "function", "function": {"name": x}} for x in n]}}
    def summary(self, d):
        if d.get("error"): err = d["error"]; return {"error": (err.get("message") if isinstance(err, dict) else str(err))[:120]}
        ch = (d.get("choices") or [{}])[0]; msg = ch.get("message", {})
        calls = [c["function"]["name"] for c in msg.get("tool_calls") or []]
        return {"calls": calls, "finish": ch.get("finish_reason"), "json": json_ok(msg.get("content")), "text": (msg.get("content") or "")[:60]}


class Anthropic:
    name = "anthropic"; url = "https://api.anthropic.com/v1/messages"
    def __init__(self, model): self.model = model; self.h = {"x-api-key": E["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    def tools(self, *t): return [{"name": x["name"], "description": x["description"], "input_schema": x["parameters"]} for x in t]
    def body(self, prompt, *, tools=None, choice=None, parallel=None, schema=None, json_mode=False, strict=True, thinking=None):
        b = {"model": self.model, "max_tokens": 600, "messages": [{"role": "user", "content": prompt}]}
        if tools: b["tools"] = self.tools(*tools)
        if choice is not None:
            b["tool_choice"] = dict(choice)
            if parallel is False: b["tool_choice"]["disable_parallel_tool_use"] = True
        elif parallel is False: b["tool_choice"] = {"type": "auto", "disable_parallel_tool_use": True}
        if json_mode: b["output_config"] = {"format": {"type": "json_schema", "schema": {"type": "object"}}}
        if schema: b["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
        if thinking: b["thinking"] = {"type": "adaptive"}; b["output_config"] = {**b.get("output_config", {}), "effort": thinking}
        return b
    def force(self, n): return {"type": "tool", "name": n}
    def allow(self, *n): return None  # no wire form
    def summary(self, d):
        if d.get("type") == "error": return {"error": d["error"].get("message", "")[:120]}
        blocks = d.get("content", []); calls = [b["name"] for b in blocks if b.get("type") == "tool_use"]
        text = next((b.get("text") for b in blocks if b.get("type") == "text"), None)
        return {"calls": calls, "stop": d.get("stop_reason"), "json": json_ok(text), "text": (text or "")[:60]}


class Gemini:
    name = "gemini"
    def __init__(self, model): self.model = model; self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"; self.h = {"x-goog-api-key": E["GEMINI_API_KEY"], "Content-Type": "application/json"}
    def tools(self, *t): return [{"functionDeclarations": [dict(x) for x in t]}]
    def body(self, prompt, *, tools=None, choice=None, parallel=None, schema=None, json_mode=False, strict=True, thinking=None):
        b = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 600}}
        if tools: b["tools"] = self.tools(*tools)
        if choice is not None: b["toolConfig"] = {"functionCallingConfig": choice}
        if json_mode: b["generationConfig"]["responseMimeType"] = "application/json"
        if schema: b["generationConfig"]["responseMimeType"] = "application/json"; b["generationConfig"]["responseJsonSchema"] = schema
        if thinking: b["generationConfig"]["thinkingConfig"] = {"thinkingLevel": thinking} if self.model.startswith("gemini-3") else {"thinkingBudget": 1024}
        return b
    def force(self, n): return {"mode": "ANY", "allowedFunctionNames": [n]}
    def allow(self, *n): return {"mode": "VALIDATED", "allowedFunctionNames": list(n)}
    def summary(self, d):
        if "error" in d: return {"error": d["error"].get("message", "")[:120]}
        cand = (d.get("candidates") or [{}])[0]; parts = (cand.get("content") or {}).get("parts", [])
        calls = [p["functionCall"]["name"] for p in parts if "functionCall" in p]
        text = next((p.get("text") for p in parts if "text" in p and not p.get("thought")), None)
        return {"calls": calls, "finish": cand.get("finishReason"), "json": json_ok(text), "text": (text or "")[:60]}


AUTO = {"openai-responses": "auto", "openai-chat": "auto", "anthropic": {"type": "auto"}, "gemini": {"mode": "AUTO"}}
REQUIRED = {"openai-responses": "required", "openai-chat": "required", "anthropic": {"type": "any"}, "gemini": {"mode": "ANY"}}
NONE = {"openai-responses": "none", "openai-chat": "none", "anthropic": {"type": "none"}, "gemini": {"mode": "NONE"}}


def run(p):
    fam = "openai-chat" if isinstance(p, OpenAIChat) else p.name
    print(f"=== {p.name}/{p.model} ===")
    def go(cell, **kw):
        row, d = send(f"{p.name}/{p.model}/{cell}", p.url, p.h, p.body(**kw)); rec(row, cell, p.summary(d)); return d
    # tool choice
    go("tc:auto", prompt=P_LOOKUP, tools=[LOOKUP, WEATHER], choice=AUTO[fam])
    go("tc:required-no-need", prompt=P_HELLO, tools=[LOOKUP, WEATHER], choice=REQUIRED[fam])
    go("tc:none-needed", prompt=P_LOOKUP, tools=[LOOKUP, WEATHER], choice=NONE[fam])
    go("tc:force-weather", prompt=P_LOOKUP, tools=[LOOKUP, WEATHER], choice=p.force("weather"))
    if p.allow("lookup") is not None:
        go("tc:allow-lookup-ask-weather", prompt=P_WEATHER, tools=[LOOKUP, WEATHER], choice=p.allow("lookup"))
    go("tc:parallel-false", prompt=P_TWO, tools=[LOOKUP, WEATHER], choice=AUTO[fam], parallel=False)
    go("tc:parallel-default", prompt=P_TWO, tools=[LOOKUP, WEATHER], choice=AUTO[fam])
    go("tc:force+schema", prompt=P_LOOKUP, tools=[LOOKUP, WEATHER], choice=p.force("lookup"), schema=S_STRICT)
    # structured output
    go("so:json_object", prompt=P_EXTRACT + " Answer as JSON.", json_mode=True)
    go("so:schema-strict", prompt=P_EXTRACT, schema=S_STRICT)
    go("so:schema-optional", prompt=P_EXTRACT, schema=S_OPTIONAL)
    go("so:schema-keywords", prompt=P_EXTRACT, schema=S_KEYWORDS)
    go("so:schema-ref", prompt=P_EXTRACT, schema=S_REF)
    go("so:schema-anyof", prompt="Extract the person: John, age unknown.", schema=S_ANYOF)
    go("so:schema+tools", prompt=P_EXTRACT + " (tools available but not needed)", tools=[LOOKUP], choice=AUTO[fam], schema=S_STRICT)
    go("so:schema+thinking", prompt=P_EXTRACT, schema=S_STRICT, thinking="low")
    if fam != "anthropic":
        go("so:schema-nonstrict", prompt=P_EXTRACT, schema=S_OPTIONAL, strict=False)


if __name__ == "__main__" and "--rerun-chat" in sys.argv:
    prev = json.loads((ROOT / "20-results.json").read_text())["results"]
    RESULTS.extend(r for r in prev if not r["tag"].startswith("openai-chat/"))
    run(OpenAIChat("gpt-5.6-sol"))
    (ROOT / "20-results.json").write_text(json.dumps({"date": "2026-09-02", "results": RESULTS}, indent=1)); print(f"\n{len(RESULTS)} rows"); sys.exit(0)

if __name__ == "__main__":
    from lm15.auth import get_xai_access_token
    for p in [OpenAIResponses("gpt-5.6-sol"), OpenAIChat("gpt-5.6-sol"), Anthropic("claude-sonnet-5"), Anthropic("claude-sonnet-4-5"),
              Gemini("gemini-2.5-flash"), Gemini("gemini-3.7-flash"),
              OpenAIChat("grok-4.6", key=get_xai_access_token(), url="https://api.x.ai/v1/chat/completions", name="xai"),
              OpenAIChat("openai/gpt-oss-20b", key=E["GROQ_API_KEY"], url="https://api.groq.com/openai/v1/chat/completions", name="groq")]:
        try: run(p)
        except Exception as e: print("  !!", type(e).__name__, str(e)[:200])
    (ROOT / "20-results.json").write_text(json.dumps({"date": "2026-09-02", "results": RESULTS}, indent=1))
    print(f"\n{len(RESULTS)} rows -> 20-results.json")
