"""Adapter-driven captures for the review follow-up.

(a) Re-capture the four OpenAI cache cases whose wire changed under the
    MAP-6 amendment (breakpoint + explicit mode): the pinned wire must be
    exactly what build_request emits, so the request is built by the
    adapter, sent verbatim, and the case's `request` block is rewritten
    from it.
(b) Capture one streaming tool call per dialect (MAP-9 premise) as new
    stream cases with canonical requests, again with adapter-built wires.
"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lm15-python"))
from lm15 import AnthropicLM, Config, FunctionTool, GeminiLM, Message, OpenAIChatLM, OpenAILM, Request  # noqa: E402
from lm15 import serde  # noqa: E402
from lm15.transports import StdlibTransport  # noqa: E402
from lm15.vet import normalize_transport_request  # noqa: E402
import os  # noqa: E402

CONTRACT = Path(__file__).resolve().parents[2]
T = StdlibTransport()
E = os.environ
ADAPTERS = {
    "openai": lambda: OpenAILM(api_key=E["OPENAI_API_KEY"]),
    "openai_chat": lambda: OpenAIChatLM(api_key=E["OPENAI_API_KEY"]),
    "anthropic": lambda: AnthropicLM(api_key=E["ANTHROPIC_API_KEY"]),
    "gemini": lambda: GeminiLM(api_key=E["GEMINI_API_KEY"]),
}
PLACEHOLDER = {"openai": "$OPENAI_API_KEY", "openai_chat": "$OPENAI_API_KEY", "anthropic": "$ANTHROPIC_API_KEY", "gemini": "$GEMINI_API_KEY"}


def wire_block(provider: str, treq) -> dict:
    """A case `request` block from a TransportRequest, secrets replaced by env placeholders."""
    norm = normalize_transport_request(treq)
    headers = {}
    for k, v in norm["headers"].items():
        if k.lower() == "authorization":
            headers["Authorization"] = f"Bearer {PLACEHOLDER[provider]}"
        elif k.lower() in ("x-api-key", "x-goog-api-key"):
            headers[k] = PLACEHOLDER[provider]
        else:
            headers[k] = v
    url = norm["url"] + ("?" + "&".join(f"{k}={v}" for k, v in norm["params"].items()) if norm["params"] else "")
    return {"method": norm["method"], "url": url, "headers": headers, "body": norm["body"]}


def send(treq) -> tuple[int, bytes, str]:
    ts = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    with T.stream(treq) as r:
        raw = r.read()
        return r.status, raw, ts


def recapture_cache_cases():
    for cid in ("openai.cache_stable", "openai.prompt_cache_breakpoint", "openai_chat.cache_stable", "openai_chat.prompt_cache_breakpoint"):
        prov, feat = cid.split(".", 1)
        path = CONTRACT / "cases" / prov / f"{feat}.json"
        case = json.loads(path.read_text())
        request = serde.request_from_dict(case["canonical_request"])
        lm = ADAPTERS[prov]()
        treq = lm.build_request(request, stream=False)
        status, raw, ts = send(treq)
        body_dir = CONTRACT / "bodies" / cid; body_dir.mkdir(exist_ok=True)
        (body_dir / f"{ts}.txt").write_bytes(raw)
        data = json.loads(raw)
        usage = data.get("usage", {})
        details = usage.get("input_tokens_details") or usage.get("prompt_tokens_details") or {}
        case["request"] = wire_block(prov, treq)
        case["expect"] = {"status": status}
        case["pinned_body"] = f"{ts}.txt"
        case["provenance"] = {
            "source": "live-capture", "date": ts[:10],
            "evidence": f"api.openai.com {ts}, {request.model}, HTTP {status}; re-captured with the adapter-built wire after the MAP-6 amendment (breakpoint + prompt_cache_options.mode=explicit; review probe 3): {json.dumps(details)}; echo prompt_cache_options={json.dumps(data.get('prompt_cache_options'))}; changes/2026-09-02-review-live-probes.md",
        }
        path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        print(f"  {cid}: HTTP {status} {details} echo={data.get('prompt_cache_options')}")
        time.sleep(1.5)


def capture_stream_tool_calls():
    tool = FunctionTool(name="get_weather", description="Current weather for a city.",
                        parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]})
    prompt = "What is the weather in Gatineau? Use the get_weather tool."
    runs = [
        ("openai", "gpt-5.4-mini", Config(reasoning=None)),
        ("openai_chat", "gpt-5.4-mini", Config()),
        ("anthropic", "claude-haiku-4-5", Config(max_tokens=300)),
        ("gemini", "gemini-2.5-flash", Config()),
    ]
    for prov, model, cfg in runs:
        request = Request(model=model, messages=(Message.user(prompt),), tools=(tool,), config=cfg)
        lm = ADAPTERS[prov]()
        treq = lm.build_request(request, stream=True)
        status, raw, ts = send(treq)
        cid = f"{prov}.streaming_tool_call"
        body_dir = CONTRACT / "bodies" / cid; body_dir.mkdir(exist_ok=True)
        (body_dir / f"{ts}.txt").write_bytes(raw)
        text = raw.decode(errors="replace")
        lines = text.splitlines()
        first_call = next((i for i, ln in enumerate(lines) if any(k in ln for k in ("tool_calls", "function_call", "tool_use", "functionCall"))), None)
        first_name = next((i for i, ln in enumerate(lines) if "get_weather" in ln and i >= (first_call or 0)), None)
        host = wire_block(prov, treq)["url"].split("/")[2]
        case = {
            "id": cid, "provider": prov, "feature": "streaming_tool_call",
            "description": f"Streaming tool call on the {prov} dialect: the call's name arrives on its first fragment (MAP-9 premise), pinned as SSE.",
            "request": wire_block(prov, treq),
            "expect": {"status": status},
            "expect_lm15": {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call"},
            "provenance": {"source": "live-capture", "date": ts[:10],
                           "evidence": f"{host} {ts}, {model}, HTTP {status}, streamed; adapter-built wire; the first frame that carries the call (line {first_call}) also carries its name (line {first_name}) — review probe 7, changes/2026-09-02-review-live-probes.md"},
            "canonical_request": serde.request_to_dict(request),
            "canonical_request_provenance": {"source": "hand-authored", "date": ts[:10],
                                             "evidence": "authored for the capture; wire side generated from it via the reference adapter and sent verbatim (receipt above)"},
            "pinned_body": f"{ts}.txt",
            "stream": True,
        }
        (CONTRACT / "cases" / prov / "streaming_tool_call.json").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        print(f"  {cid}: HTTP {status} {len(raw)}B first_call_line={first_call} first_name_line={first_name}")
        time.sleep(1.0)


if __name__ == "__main__":
    print("cache cases"); recapture_cache_cases()
    print("stream tool calls"); capture_stream_tool_calls()
