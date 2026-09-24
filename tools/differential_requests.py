"""Differential request building (MAP-13 parity), across implementations.

The corpus pins chosen cells; this checks the whole grid. For every
(provider, model) pair the corpus uses, and every setting a Config can carry
(one at a time: sampling knobs, each effort level, budgets, summaries, both
answer formats, cache hints, tool-choice forms), it asks each shim to
build_request, then compares with the first shim: the outcome (built or
refused, and the error class), the MAP-13 adaptation records (field, action,
asked, applied), the body and the URL.

    python3 tools/differential_requests.py python typescript go rust
    SHIMS=/path/to/shims.json python3 tools/differential_requests.py python r julia

Exit status 1 when any shim differs; the differences are written to
harness/reports/differential-requests.json. First run 2026-09-24
(changes/2026-09-24-adaptation-parity.md): 1,881 requests, identical in six SDKs.
"""
import json, glob, subprocess, sys, itertools, collections, os, pathlib
CONTRACT = str(pathlib.Path(__file__).resolve().parent.parent)
SHIMS = json.load(open(os.environ.get("SHIMS", os.path.join(CONTRACT, "harness/shims.json")), encoding="utf-8"))
SKIP_PROVIDERS = {"typesafe"}
# (provider, model) pairs from the corpus, so model-specific rules are exercised.
pairs, settings_by = set(), {}
for f in glob.glob(f"{CONTRACT}/cases/*/*.json"):
    c = json.load(open(f, encoding="utf-8"))
    req = c.get("canonical_request") or {}
    p = c.get("provider")
    if not p or p in SKIP_PROVIDERS or not req.get("model") or c.get("expect_lm15", {}).get("raises"): continue
    key = (p, req["model"], c.get("base_url"), json.dumps(c.get("settings")) if c.get("settings") else None)
    pairs.add(key)
TOOLS = [{"type": "function", "name": "a", "description": "A.", "parameters": {"type": "object", "properties": {}}},
         {"type": "function", "name": "b", "description": "B.", "parameters": {"type": "object", "properties": {}}}]
SCHEMA = {"type": "json_schema", "name": "place", "schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}, "strict": True}
VARIANTS = {
    "base": {}, "max_tokens": {"max_tokens": 100}, "temperature_hi": {"temperature": 1.5}, "temperature": {"temperature": 0.2},
    "top_p": {"top_p": 0.9}, "top_k": {"top_k": 40}, "seed": {"seed": 42}, "stop": {"stop": ["END"]},
    "frequency_penalty": {"frequency_penalty": 0.5}, "presence_penalty": {"presence_penalty": 0.5},
    "service_tier": {"service_tier": "flex"}, "user_id": {"user_id": "user-123456"}, "store_false": {"store": False}, "store_true": {"store": True},
    "logprobs": {"logprobs": 3},
    **{f"effort_{e}": {"reasoning": {"effort": e}} for e in ("off", "minimal", "low", "medium", "high", "xhigh", "max")},
    "budget": {"reasoning": {"effort": "medium", "thinking_budget": 2048}}, "summary": {"reasoning": {"effort": "medium", "summary": "concise"}},
    "json_schema": {"response_format": SCHEMA}, "json_object": {"response_format": {"type": "json_object"}},
    "cache_key": {"cache": {"mode": "auto", "key": "k1"}}, "cache_long": {"cache": {"mode": "auto", "retention": "long"}},
    # Added 2026-09-24 (changes/2026-09-24-cache-resource-refusal.md): three SDKs dropped a resource silently.
    "cache_resource": {"cache": {"mode": "auto", "resource": "cachedContents/c1"}}, "cache_off": {"cache": {"mode": "off"}},
    "tc_required": {"tool_choice": {"mode": "required"}, "_tools": True},
    "tc_allowed_one": {"tool_choice": {"mode": "required", "allowed": ["a"]}, "_tools": True},
    "tc_allowed_subset_auto": {"tool_choice": {"mode": "auto", "allowed": ["a"]}, "_tools": True},
    "tc_parallel_false": {"tool_choice": {"mode": "auto", "parallel": False}, "_tools": True},
    "tc_none": {"tool_choice": {"mode": "none"}, "_tools": True},
    # Media in each role (MAP-10: natively or raises). Added 2026-09-24
    # (changes/2026-09-24-message-media.md): three SDKs lost such parts silently.
    **{f"{role}_{kind}": {"_media": (role, kind)} for role, kind in [
        ("user", "image"), ("user", "audio"), ("user", "video"), ("user", "document"), ("user", "binary"),
        ("assistant", "image"), ("assistant", "audio"), ("assistant", "document"),
        ("developer", "image"), ("developer", "audio")]},
}
MEDIA = {"image": {"type": "image", "media_type": "image/png", "data": "QUJD"},
         "audio": {"type": "audio", "media_type": "audio/wav", "data": "QUJD"},
         "video": {"type": "video", "media_type": "video/mp4", "url": "https://example.com/a.mp4"},
         "document": {"type": "document", "media_type": "application/pdf", "data": "QUJD"},
         "binary": {"type": "binary", "media_type": "image/svg+xml", "data": "QUJD"}}
def request(model, variant):
    v = dict(VARIANTS[variant]); tools = v.pop("_tools", False); media = v.pop("_media", None)
    r = {"model": model, "messages": [{"role": "user", "parts": [{"type": "text", "text": "Hi"}]}]}
    if media:
        role, kind = media
        if role == "user":
            r["messages"][0]["parts"].append(MEDIA[kind])
        else:
            r["messages"] += [{"role": role, "parts": [{"type": "text", "text": "a"}, MEDIA[kind]]},
                              {"role": "user", "parts": [{"type": "text", "text": "more"}]}]
    if v: r["config"] = v
    if tools: r["tools"] = TOOLS
    return r
ops = []
for (p, model, base_url, settings), variant in itertools.product(sorted(pairs, key=str), VARIANTS):
    op = {"op": "build_request", "id": f"{p}|{model}|{variant}", "provider": p, "canonical_request": request(model, variant), "stream": False, "api_key": "test-key-123"}
    if base_url: op["base_url"] = base_url
    if settings: op["settings"] = json.loads(settings)
    ops.append(op)
def run(name):
    s = SHIMS[name]
    cwd = os.path.normpath(os.path.join(CONTRACT, s["cwd"]))
    out = subprocess.run(s["command"], cwd=cwd, input="\n".join(json.dumps(o) for o in ops) + "\n", capture_output=True, text=True, timeout=3600, encoding="utf-8")
    replies = [json.loads(l) for l in out.stdout.splitlines() if l.strip().startswith("{")]
    return {r["id"]: r for r in replies}
def norm(r):
    if r is None: return ("missing",)
    if not r.get("ok"): return ("error", r["error"].get("type"))
    res = r["result"]
    ad = sorted(((a["field"], a["action"], json.dumps(a.get("asked"), sort_keys=True), json.dumps(a.get("applied"), sort_keys=True)) for a in res.get("adaptations") or []))
    return ("ok", tuple(ad), json.dumps(res.get("body"), sort_keys=True), res.get("url"))
names = sys.argv[1:] or ["python", "r", "julia"]
results = {n: run(n) for n in names}
ref = names[0]
summary = collections.Counter(); rows = []
for o in ops:
    a = norm(results[ref].get(o["id"]))
    for n in names[1:]:
        b = norm(results[n].get(o["id"]))
        if a == b: summary[(n, "same")] += 1; continue
        kind = "outcome" if a[0] != b[0] else "adaptations" if a[1] != b[1] else "wire"
        summary[(n, kind)] += 1
        rows.append({"shim": n, "id": o["id"], "kind": kind, "ref": a[:2] if a[0]=="ok" else a, "got": b[:2] if b[0]=="ok" else b,
                     "ref_body": a[2] if a[0]=="ok" else None, "got_body": b[2] if b[0]=="ok" else None})
json.dump(rows, open(os.path.join(CONTRACT, "harness/reports/differential-requests.json"), "w", encoding="utf-8"), indent=1)
print(len(ops), "requests;", {f"{shim} {kind}": n for (shim, kind), n in sorted(summary.items())})
sys.exit(1 if rows else 0)
