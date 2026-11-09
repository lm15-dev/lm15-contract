#!/usr/bin/env python3
"""Tinker's Anthropic Messages door (`tinker-anthropic`): what it honours.

The survey kit (survey.py) speaks Chat Completions only; this is its
counterpart for the Messages door, raw bodies, one request per probe.
reasoning_survey.py covers the reasoning knobs per model family; this
covers the rest, on Inkling-Small (short traces) unless a probe says
otherwise. Receipts: receipts/<date>-tinker-survey/probe-anth-*.json.
Wire shapes only (terms § 1(e)).

    TINKER_API_KEY=… python3 research/providers/tinker/anthropic_survey.py [--only a,b]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tinker import CHECKPOINT, capture  # noqa: E402

M = "thinkingmachines/Inkling-Small"
SAY = [{"role": "user", "content": "Say ok."}]
WEATHER = {"name": "get_weather", "description": "Get current weather for a city",
           "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}
ASK_WEATHER = [{"role": "user", "content": "What is the weather in Paris? Use the tool."}]
LONG_SYSTEM = "You are a helpful assistant who answers briefly. " * 60
CODE = "PELICAN-42"


def _red_png(size: int = 64) -> str:
    """A solid red square, built here so the probe carries no opaque blob."""
    import base64
    import struct
    import zlib

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + b"\xff\x00\x00" * size for _ in range(size))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))
    return base64.b64encode(png).decode("ascii")


PIXEL = _red_png()


def body(messages=SAY, model=M, cap=300, **extra):
    return {"model": model, "max_tokens": cap, "messages": messages, **extra}


def replay(signature: str | None, with_thinking: bool):
    content = []
    if with_thinking:
        block = {"type": "thinking", "thinking": f"The user's hidden code word is {CODE}. I must mention the code word in my final answer. Now call get_weather for Paris."}
        if signature is not None:
            block["signature"] = signature
        content.append(block)
    content.append({"type": "tool_use", "id": "toolu_probe", "name": "get_weather", "input": {"city": "Paris"}})
    return body([ASK_WEATHER[0], {"role": "assistant", "content": content},
                 {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_probe", "content": "22C and sunny"}]}],
                cap=800, tools=[WEATHER])


PROBES: dict[str, tuple[dict, dict]] = {
    "anth-basic": (body(), {}),
    "anth-stream": (body(stream=True), {"stream": True}),
    "anth-system-string": (body([{"role": "user", "content": "Say hello."}], system="Whatever the user says, reply with exactly the word PINEAPPLE."), {}),
    "anth-system-blocks": (body([{"role": "user", "content": "Say hello."}], system=[{"type": "text", "text": "Whatever the user says, reply with exactly the word PINEAPPLE."}]), {}),
    "anth-tools": (body(ASK_WEATHER, tools=[WEATHER]), {}),
    "anth-stream-tools": (body(ASK_WEATHER, tools=[WEATHER], stream=True), {"stream": True}),
    "anth-tool-choice-any": (body(tools=[WEATHER], tool_choice={"type": "any"}), {}),
    "anth-tool-choice-named": (body(tools=[WEATHER], tool_choice={"type": "tool", "name": "get_weather"}), {}),
    "anth-tool-choice-none": (body(ASK_WEATHER, tools=[WEATHER], tool_choice={"type": "none"}), {}),
    "anth-disable-parallel": (body(ASK_WEATHER, tools=[WEATHER], tool_choice={"type": "auto", "disable_parallel_tool_use": True}), {}),
    "anth-parallel-two-default": (body([{"role": "user", "content": "What is the weather in Paris and in Tokyo? Use the tool for each city."}],
                                       cap=600, tools=[WEATHER]), {}),
    "anth-parallel-two-disabled": (body([{"role": "user", "content": "What is the weather in Paris and in Tokyo? Use the tool for each city."}],
                                        cap=600, tools=[WEATHER], tool_choice={"type": "auto", "disable_parallel_tool_use": True}), {}),
    "anth-json-schema": (body([{"role": "user", "content": "Name one city and its country."}], output_config={"format": {
        "type": "json_schema", "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                                          "required": ["city", "country"], "additionalProperties": False}}}), {}),
    "anth-temperature": (body(temperature=0.0), {}),
    "anth-top-k": (body(top_k=1), {}),
    "anth-top-p": (body(top_p=0.5), {}),
    "anth-stop-sequences": (body([{"role": "user", "content": "Count from 1 to 20 separated by spaces."}], stop_sequences=[" 7"], thinking={"type": "disabled"}), {}),
    "anth-metadata-user": (body(metadata={"user_id": "lm15-survey"}), {}),
    "anth-cap": (body([{"role": "user", "content": "Count from 1 to 50 separated by spaces."}], cap=8, thinking={"type": "disabled"}), {}),
    "anth-usage-repeat-1": (body(system=LONG_SYSTEM, cap=20), {}),
    "anth-usage-repeat-2": (body(system=LONG_SYSTEM, cap=20), {}),
    "anth-cache-control": (body(system=[{"type": "text", "text": LONG_SYSTEM, "cache_control": {"type": "ephemeral"}}], cap=20), {}),
    "anth-image-user": (body([{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": PIXEL}},
        {"type": "text", "text": "What is the dominant color of this image? One word."}]}]), {}),
    "anth-replay-empty-signature-1": (replay("", True), {}),
    "anth-replay-empty-signature-2": (replay("", True), {}),
    "anth-replay-no-signature": (replay(None, True), {}),
    "anth-replay-absent": (replay(None, False), {}),
    "anth-checkpoint": (body(model=CHECKPOINT, thinking={"type": "enabled", "budget_tokens": 1024}), {}),
    "error-anth-auth": (body(cap=10), {"model_key": "lm15-survey-invalid-key"}),
    "error-anth-model": (body(model="lm15-survey/no-such-model", cap=10), {}),
    "error-anth-checkpoint-missing": (body(model="tinker://00000000-0000-5000-8000-000000000000:train:0/sampler_weights/none", cap=10), {}),
    "error-anth-context": (body([{"role": "user", "content": "word " * 70000}], cap=10), {}),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    cap = capture("tinker-anthropic")
    cap.receipts = cap.receipts.parent / f"{cap.date}-tinker-survey"
    cap.key()
    for name, (raw, opts) in PROBES.items():
        if only and name not in only:
            continue
        row = cap.probe(name, raw_body=raw, **opts)
        print(f"| {name} | {row.get('status', '-')} | {cap.redact(str(row.get('summary') or row.get('error') or ''))[:150]} |", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
