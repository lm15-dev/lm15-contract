#!/usr/bin/env python3
"""DeepSeek over the Anthropic Messages wire — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts:
``receipts/<date>-deepseek-anthropic/`` (the discovery probes that shaped the
compat preset are already there as ``discovery-*.json``).

    DEEPSEEK_API_KEY=… python3 research/providers/deepseek-anthropic/capture.py [--dry-run] [--only a,b] [--force]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request  # noqa: E402

cap = Capture("deepseek-anthropic", env_var="DEEPSEEK_API_KEY", default_model="deepseek-v4-flash", host="api.deepseek.com/anthropic")

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=600)), stream=False,
            description="DeepSeek over the Anthropic wire: basic_text (thinking on by default; thinking block carries a signature)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="Messages-shaped body; usage carries cache_read_input_tokens (implicit caching)", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=600)), stream=True,
            description="DeepSeek over the Anthropic wire: streaming (message_start … content_block_delta thinking_delta/text_delta … message_stop)",
            expect_lm15=None, evidence_note="Anthropic SSE event vocabulary as served by DeepSeek", force=force))
    if want("reasoning_off"):
        rows.append(cap.write_case(
            "reasoning_off", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=Reasoning(effort="off"))), stream=False,
            description="DeepSeek over the Anthropic wire: reasoning off must be SENT (thinking: {type: disabled}) — absence means on here",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="compat thinking_format=deepseek; no thinking block expected", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=Reasoning(effort="low"))), stream=False,
            description="DeepSeek over the Anthropic wire: thinking: {type: enabled} + output_config.effort=low, no budget_tokens, max_tokens as given",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="the plain Anthropic manual-class wire would send budget_tokens (ignored) and drop the effort", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)), stream=False,
            description="DeepSeek over the Anthropic wire: tool_use block after a signed thinking block; stop_reason tool_use",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_use ids of the call_00_… shape", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)), stream=True,
            description="DeepSeek over the Anthropic wire: streamed tool_use (input_json_delta)",
            expect_lm15=None, evidence_note="MAP-9 premise for this endpoint", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="DeepSeek over the Anthropic wire: the live turn-1 message (signed thinking + tool_use) replayed with a tool_result",
                expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
                evidence_note=info["note"] + "; discovery: the same turn WITHOUT the thinking block also answered 200 (not required on this wire)", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY,
                                     config=Config(max_tokens=100, reasoning=Reasoning(effort="off"))), stream=False,
            description="DeepSeek over the Anthropic wire: top-level system string",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="system field fully supported (guide--anthropic-api.md)", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=50, user_id="lm15-case-user", reasoning=Reasoning(effort="off"))), stream=False,
            description="DeepSeek over the Anthropic wire: Config.user_id rides metadata.user_id (the dialect's own spelling; documented supported)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="metadata.user_id supported, other metadata ignored (guide--anthropic-api.md)", force=force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    low = Config(max_tokens=200, reasoning=Reasoning(effort="low"))
    if want("effort"):
        for e in ("minimal", "medium", "xhigh", "max"):
            rows.append(cap.probe(f"effort-{e}", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort=e)))))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=10)), model_key="sk-invalid"))
        rows.append(cap.probe("error-model-not-found", raw_body={"model": "deepseek-nonexistent", "max_tokens": 10, "messages": [{"role": "user", "content": "Say ok."}]}))
        rows.append(cap.probe("error-bad-effort", raw_body={"model": model, "max_tokens": 10, "messages": [{"role": "user", "content": "Say ok."}],
                                                        "thinking": {"type": "enabled"}, "output_config": {"effort": "bogus"}}))
    if want("top_k"):
        rows.append(cap.probe("top-k", Request(model=model, messages=SAY, config=Config(max_tokens=200, top_k=1, reasoning=Reasoning(effort="off")))))
    if want("stop"):
        rows.append(cap.probe("stop-sequence", Request(model=model, messages=(Message.user("Count from 1 to 10, separated by commas."),),
                                                       config=Config(max_tokens=100, stop=("5",), reasoning=Reasoning(effort="off")))))
    if want("cache"):
        req = Request(model=model, system="You are a helpful assistant. " * 60, messages=SAY, config=Config(max_tokens=20, reasoning=Reasoning(effort="off")))
        rows.append(cap.probe("cache-first", req))
        rows.append(cap.probe("cache-second", req))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "bad-effort"))
