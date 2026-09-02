"""Caching design pass — step 5, the experiment matrix (2026-09-01).

Same cells on every provider we hold a key for. Fresh random prefixes per
provider so earlier runs cannot pollute. Records usage fields, latency,
HTTP status, and a redacted request per call under receipts/. Secrets never
touch disk: headers are replaced by their env-var name.

Cells (each ~3k-token prefix unless stated):
  cold          first request with the fresh prefix
  warm x3       same prefix, different suffix, immediately after
  delay45       same prefix after 45 s idle
  below_min x2  a ~300-token prefix, twice
  tools         same prefix + one function tool declared
  other_model   same prefix on a sibling model
  process2      same prefix from a separate OS process (fresh transport)

Provider configurations:
  openai-responses/breakpoint   gpt-5.6-sol, prefix_until_index=0 (explicit)
  openai-responses/implicit     gpt-5.6-sol, no breakpoint
  openai-responses/pre56        gpt-5.4-mini, no breakpoint (implicit-only class)
  openai-chat/breakpoint        gpt-5.6-sol via chat/completions
  anthropic/explicit-block      claude-sonnet-4-5, cache_control on the prefix block (lm15 mapping)
  anthropic/automatic-toplevel  claude-sonnet-4-5, top-level cache_control (hand-built)
  gemini/implicit               gemini-2.5-flash, nothing sent
  gemini/explicit-resource      gemini-2.5-flash, cachedContents lifecycle (create, use x2, list, delete)
  xai/automatic                 grok-4.3
  groq/automatic                openai/gpt-oss-20b
  openrouter/automatic          openai/gpt-4.1-mini
"""
from __future__ import annotations

import hashlib, json, os, random, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lm15-python"))
from lm15 import (AnthropicLM, CacheConfig, Config, FunctionTool, GeminiLM, Message, OpenAIChatLM, OpenAILM, Reasoning, Request, XaiLM)
from lm15.providers import HttpResponse
from lm15.transports import StdlibTransport, TransportRequest

ROOT = Path(__file__).resolve().parent
RECEIPTS = ROOT / "receipts"; RECEIPTS.mkdir(exist_ok=True)
SECRET_HEADERS = {"authorization", "x-api-key", "x-goog-api-key"}
T = StdlibTransport()
Q = ["What is 143 times 27? Reply with just the number.", "What is 12 times 12? Reply with just the number.",
     "What is 7 times 8? Reply with just the number.", "What is 9 times 9? Reply with just the number.",
     "What is 3 times 3? Reply with just the number.", "What is 6 times 7? Reply with just the number."]


def prefix(nonce: str, items: int = 180) -> str:
    return f"Reference notes {nonce}. " + " ".join(f"Item {i}: the quick brown fox jumps over the lazy dog number {i}." for i in range(items))


def redact(headers):
    return {k: ("$REDACTED" if k.lower() in SECRET_HEADERS else v) for k, v in headers}


def send(tag: str, tr: TransportRequest, parse=None):
    t0 = time.monotonic()
    with T.stream(tr) as r:
        raw = r.read()
    ms = int((time.monotonic() - t0) * 1000)
    ts = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    sha = hashlib.sha256(tr.body).hexdigest()[:16]
    d = RECEIPTS / tag.replace("/", "__"); d.mkdir(exist_ok=True)
    (d / f"{ts}.txt").write_bytes(raw)
    (d / f"{ts}.request.json").write_text(json.dumps({"method": tr.method, "url": tr.url, "headers": redact(tr.headers), "body": json.loads(tr.body) if tr.body else None}, indent=1))
    usage = None
    if parse is not None and r.status == 200:
        try:
            u = parse(HttpResponse(r.status, "OK", r.headers, raw)).usage
            usage = {"input": u.input_tokens, "output": u.output_tokens, "cache_read": u.cache_read_tokens, "cache_write": u.cache_write_tokens}
        except Exception as exc:  # noqa: BLE001
            usage = {"parse_error": str(exc)[:120]}
    body = None
    try:
        body = json.loads(raw)
    except Exception:  # noqa: BLE001
        pass
    return {"tag": tag, "ts": ts, "status": r.status, "ms": ms, "sha": sha, "usage": usage, "receipt": f"{d.name}/{ts}.txt", "body": body}


RESULTS: list[dict] = []


def record(res: dict, cell: str, note: str = ""):
    row = {k: v for k, v in res.items() if k != "body"}
    row["cell"] = cell
    if note: row["note"] = note
    RESULTS.append(row)
    print(f"  {cell:14s} HTTP {row['status']} {row['ms']:5d}ms  usage={row['usage']}")
    return res


def run_matrix(name: str, make_lm, model: str, other_model: str | None, cache: CacheConfig | None, *, reasoning_off=True, tools_ok=True, process2=True, hand_builder=None):
    print(f"=== {name} ({model}) ===")
    nonce = f"{random.randrange(10**9):09d}"
    pre = prefix(nonce)
    lm = make_lm()
    cfg = lambda **kw: Config(max_tokens=16, reasoning=Reasoning(effort="off") if reasoning_off else None, cache=cache, **kw)  # noqa: E731

    def req(model_, q, p=pre, tools=()):
        return Request(model=model_, messages=(Message.user(p), Message.user(q)), tools=tools, config=cfg())

    def build(rq):
        return hand_builder(lm, rq) if hand_builder else lm.build_request(rq, stream=False)

    parse = lambda resp: lm.parse_response(req(model, Q[0]), resp)  # noqa: E731
    record(send(f"{name}/cold", build(req(model, Q[0])), parse), "cold")
    for i in range(3):
        record(send(f"{name}/warm", build(req(model, Q[1 + i])), parse), f"warm{i+1}")
    time.sleep(45)
    record(send(f"{name}/delay45", build(req(model, Q[4])), parse), "delay45")
    small = prefix(nonce + "s", items=14)
    for i in range(2):
        record(send(f"{name}/below_min", build(req(model, Q[i], p=small)), parse), f"below_min{i+1}")
    if tools_ok:
        tool = FunctionTool(name="lookup", description="Look up a number.", parameters={"type": "object", "properties": {"n": {"type": "integer"}}})
        record(send(f"{name}/tools", build(req(model, Q[5], tools=(tool,))), parse), "tools", "same prefix + one tool declared")
    if other_model:
        record(send(f"{name}/other_model", build(req(other_model, Q[0])), parse), "other_model", other_model)
    if process2:
        code = f"""
import json,sys; sys.path.insert(0,{str(ROOT)!r}); sys.argv=['x']
import importlib.util; spec=importlib.util.spec_from_file_location('exp', {str(__file__)!r}); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
lm=m.PROVIDERS[{name!r}][0]()
rq=m.Request(model={model!r}, messages=(m.Message.user({pre!r}), m.Message.user({Q[2]!r})), config=m.Config(max_tokens=16, reasoning=m.Reasoning(effort='off') if {reasoning_off} else None, cache=m.CACHES[{name!r}]))
tr=(m.PROVIDERS[{name!r}][4](lm, rq) if m.PROVIDERS[{name!r}][4] else lm.build_request(rq, stream=False))
r=m.send({name!r}+'/process2', tr, lambda resp: lm.parse_response(rq, resp)); r.pop('body',None); print(json.dumps(r))
"""
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
        try:
            row = json.loads(out.stdout.strip().splitlines()[-1]); row["cell"] = "process2"; RESULTS.append(row)
            print(f"  {'process2':14s} HTTP {row['status']} {row['ms']:5d}ms  usage={row['usage']}")
        except Exception:
            print("  process2 FAILED:", out.stderr[-400:])


# ─── hand builders for shapes lm15 does not map yet ─────────────────

def anthropic_toplevel(lm, rq):
    tr = lm.build_request(rq, stream=False)
    body = json.loads(tr.body); body.pop("cache_control", None)
    for m in body["messages"]:
        for blk in m["content"]:
            blk.pop("cache_control", None)
    body["cache_control"] = {"type": "ephemeral"}
    tr.body = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode()
    return tr


def openai_no_breakpoint(lm, rq):
    tr = lm.build_request(rq, stream=False)
    body = json.loads(tr.body)
    for item in body["input"]:
        for blk in item.get("content", []) if isinstance(item.get("content"), list) else []:
            blk.pop("prompt_cache_breakpoint", None)
    tr.body = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode()
    return tr


E = os.environ
CACHES = {
    "openai-responses/breakpoint": CacheConfig(prefix_until_index=0),
    "openai-responses/implicit": None,
    "openai-responses/pre56": None,
    "openai-chat/breakpoint": CacheConfig(prefix_until_index=0),
    "anthropic/explicit-block": CacheConfig(prefix_until_index=0),
    "anthropic/automatic-toplevel": None,
    "gemini/implicit": CacheConfig(mode="off"),  # keep lm15's hidden cachedContents POST out of the measurement
    "xai/automatic": None,
    "groq/automatic": None,
    "openrouter/automatic": None,
}
PROVIDERS = {
    "openai-responses/breakpoint": (lambda: OpenAILM(api_key=E["OPENAI_API_KEY"]), "gpt-5.6-sol", "gpt-5.6-luna", True, None),
    "openai-responses/implicit": (lambda: OpenAILM(api_key=E["OPENAI_API_KEY"]), "gpt-5.6-sol", None, True, None),
    "openai-responses/pre56": (lambda: OpenAILM(api_key=E["OPENAI_API_KEY"]), "gpt-5.4-mini", "gpt-5.4-nano", True, None),
    "openai-chat/breakpoint": (lambda: OpenAIChatLM(api_key=E["OPENAI_API_KEY"]), "gpt-5.6-sol", None, True, None),
    "anthropic/explicit-block": (lambda: AnthropicLM(api_key=E["ANTHROPIC_API_KEY"]), "claude-sonnet-4-5", "claude-sonnet-4-6", True, None),
    "anthropic/automatic-toplevel": (lambda: AnthropicLM(api_key=E["ANTHROPIC_API_KEY"]), "claude-sonnet-4-5", None, True, anthropic_toplevel),
    "gemini/implicit": (lambda: GeminiLM(api_key=E["GEMINI_API_KEY"]), "gemini-2.5-flash", "gemini-2.5-flash-lite", True, None),
    "xai/automatic": (lambda: XaiLM(api_key=E.get("XAI_API_KEY") or None), "grok-4.3", None, True, None),
    "groq/automatic": (lambda: OpenAIChatLM(api_key=E["GROQ_API_KEY"], compat="groq"), "openai/gpt-oss-20b", None, True, None),
    "openrouter/automatic": (lambda: OpenAIChatLM(api_key=E["OPENROUTER_API_KEY"], compat="openrouter"), "openai/gpt-4.1-mini", None, True, None),
}


def gemini_explicit_lifecycle():
    print("=== gemini/explicit-resource (cachedContents lifecycle) ===")
    key = E["GEMINI_API_KEY"]; base = "https://generativelanguage.googleapis.com/v1beta"
    h = [("x-goog-api-key", key), ("Content-Type", "application/json")]
    nonce = f"{random.randrange(10**9):09d}"; pre = prefix(nonce)
    body = {"model": "models/gemini-2.5-flash", "contents": [{"role": "user", "parts": [{"text": pre}]}], "ttl": "300s", "displayName": "lm15-design-pass"}
    tr = TransportRequest("POST", f"{base}/cachedContents", headers=h, body=json.dumps(body).encode())
    res = record(send("gemini/explicit-resource/create", tr), "create")
    name = (res["body"] or {}).get("name")
    print("   cache name:", name, "| usage:", (res["body"] or {}).get("usageMetadata"), "| expire:", (res["body"] or {}).get("expireTime"))
    if not name:
        return
    for i in range(2):
        gen = {"contents": [{"role": "user", "parts": [{"text": Q[i]}]}], "cachedContent": name, "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}, "maxOutputTokens": 16}}
        tr = TransportRequest("POST", f"{base}/models/gemini-2.5-flash:generateContent", headers=h, body=json.dumps(gen).encode())
        r = record(send("gemini/explicit-resource/use", tr), f"use{i+1}")
        print("   usageMetadata:", (r["body"] or {}).get("usageMetadata"))
    # constraint probe: cachedContent + tools in the same request
    gen = {"contents": [{"role": "user", "parts": [{"text": Q[5]}]}], "cachedContent": name, "tools": [{"functionDeclarations": [{"name": "lookup", "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}}}]}], "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}, "maxOutputTokens": 16}}
    tr = TransportRequest("POST", f"{base}/models/gemini-2.5-flash:generateContent", headers=h, body=json.dumps(gen).encode())
    r = record(send("gemini/explicit-resource/use_with_tools", tr), "use+tools", "does the request accept tools next to cachedContent?")
    if r["status"] != 200: print("   ->", json.dumps(r["body"])[:200])
    # other model against the cache
    gen = {"contents": [{"role": "user", "parts": [{"text": Q[0]}]}], "cachedContent": name, "generationConfig": {"maxOutputTokens": 16}}
    tr = TransportRequest("POST", f"{base}/models/gemini-2.5-flash-lite:generateContent", headers=h, body=json.dumps(gen).encode())
    r = record(send("gemini/explicit-resource/use_other_model", tr), "use+other_model", "gemini-2.5-flash-lite against a 2.5-flash cache")
    if r["status"] != 200: print("   ->", json.dumps(r["body"])[:200])
    record(send("gemini/explicit-resource/list", TransportRequest("GET", f"{base}/cachedContents?pageSize=50", headers=h[:1])), "list")
    record(send("gemini/explicit-resource/delete", TransportRequest("DELETE", f"{base}/{name}", headers=h[:1])), "delete")


if __name__ == "__main__":
    random.seed()
    for name, (make, model, other, tools_ok, hb) in PROVIDERS.items():
        try:
            run_matrix(name, make, model, other, CACHES[name], tools_ok=tools_ok, hand_builder=hb,
                       reasoning_off=not (name.startswith("xai") or name.startswith("openrouter")))
        except Exception as exc:  # noqa: BLE001
            print(f"  !! {name} aborted: {type(exc).__name__}: {str(exc)[:200]}")
            RESULTS.append({"tag": name, "cell": "aborted", "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
    try:
        gemini_explicit_lifecycle()
    except Exception as exc:  # noqa: BLE001
        print(f"  !! gemini lifecycle aborted: {type(exc).__name__}: {str(exc)[:200]}")
    (ROOT / "20-results.json").write_text(json.dumps({"date": "2026-09-01", "results": RESULTS}, indent=1))
    print(f"\n{len(RESULTS)} rows -> 20-results.json")
