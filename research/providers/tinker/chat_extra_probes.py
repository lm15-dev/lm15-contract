#!/usr/bin/env python3
"""Chat-door probes the survey kit does not send: stop sequences, parallel
tool calls, logprobs, n, seed, the context-window error, a missing or
malformed checkpoint path, an image in a user turn, a checkpoint by name.
Receipts: receipts/<date>-tinker-survey/probe-chat-*.json. Wire shapes only.

    TINKER_API_KEY=… python3 research/providers/tinker/chat_extra_probes.py [--only a,b]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tinker import CHECKPOINTS, capture  # noqa: E402
from anthropic_survey import PIXEL  # noqa: E402

M = "thinkingmachines/Inkling-Small"
TOOL = {"type": "function", "function": {"name": "get_weather", "description": "Get current weather for a city",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}
TWO = [{"role": "user", "content": "What is the weather in Paris and in Tokyo? Use the tool for each city."}]


def chat(messages, model=M, cap=400, **extra):
    return {"model": model, "messages": messages, "max_completion_tokens": cap, **extra}


def u(text):
    return [{"role": "user", "content": text}]


PROBES = {
    "chat-stop": chat(u("Count from 1 to 20 separated by spaces."), stop=[" 7"], reasoning_effort="none"),
    "chat-parallel-default": chat(TWO, tools=[TOOL]),
    "chat-parallel-false": chat(TWO, tools=[TOOL], parallel_tool_calls=False),
    "chat-logprobs": chat(u("Say ok."), logprobs=True, top_logprobs=2, reasoning_effort="none", cap=10),
    "chat-n2": chat(u("Say ok."), n=2, reasoning_effort="none", cap=10),
    "chat-seed": chat(u("Say ok."), seed=7, reasoning_effort="none", cap=10),
    "chat-image-user": chat([{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{PIXEL}"}},
        {"type": "text", "text": "What is the dominant color of this image? One word."}]}], reasoning_effort="none"),
    "chat-image-user-qwen": chat([{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{PIXEL}"}},
        {"type": "text", "text": "What is the dominant color of this image? One word."}]}], model="Qwen/Qwen3.5-4B", reasoning_effort=False),
    "chat-checkpoint-qwen-off": chat(u("Say ok."), model=CHECKPOINTS["Qwen/Qwen3.5-4B"], reasoning_effort=False),
    "chat-checkpoint-inkling-off": chat(u("Say ok."), model=CHECKPOINTS["thinkingmachines/Inkling-Small"], reasoning_effort="none"),
    "chat-checkpoint-gpt-oss-low": chat(u("Say ok."), model=CHECKPOINTS["openai/gpt-oss-20b"], reasoning_effort="low"),
    "chat-checkpoint-stream": chat(u("Say ok."), model=CHECKPOINTS["Qwen/Qwen3.5-4B"], reasoning_effort=False, stream=True,
                                   stream_options={"include_usage": True}),
    "error-chat-context": chat(u("word " * 70000), cap=10),
    "error-chat-checkpoint-missing": chat(u("Say ok."), model="tinker://00000000-0000-5000-8000-000000000000:train:0/sampler_weights/none", cap=10),
    "error-chat-checkpoint-malformed": chat(u("Say ok."), model="tinker://not-a-path", cap=10),
    "error-chat-training-weights": chat(u("Say ok."), model=CHECKPOINTS["Qwen/Qwen3.5-4B"].replace("sampler_weights", "weights"), cap=10),
    "error-chat-base-model": chat(u("Say ok."), model="Qwen/Qwen3.5-9B-Base", cap=10),
    "error-chat-tool-required-unmet": chat(u("Say ok."), model="Qwen/Qwen3.5-4B", tools=[TOOL], tool_choice="required", reasoning_effort=False, cap=50),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    cap = capture("tinker")
    cap.receipts = cap.receipts.parent / f"{cap.date}-tinker-survey"
    cap.key()
    for name, raw in PROBES.items():
        if only and name not in only:
            continue
        row = cap.probe(name, raw_body=raw, stream=bool(raw.get("stream")))
        print(f"| {name} | {row.get('status', '-')} | {cap.redact(str(row.get('summary') or row.get('error') or ''))[:170]} |", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
