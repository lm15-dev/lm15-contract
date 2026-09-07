#!/usr/bin/env python3
"""Meta Model API over the Anthropic Messages wire (`meta-anthropic`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-meta-anthropic/``.

    META_API_KEY=… python3 research/providers/meta-anthropic/capture.py [--dry-run] [--only a,b] [--force]

Probes: reasoning off (docs: thinking disabled → HTTP 400), `minimal`
(docs list low|medium|high|xhigh only), budget_tokens (docs: accepted, not
translated), cache_control marks (undocumented on this wire — loud or
silent?), a named tool_choice (docs: 400), top_k / stop_sequences (docs:
400), the /models root through this adapter, and the error envelope.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import CacheConfig, Config, Message, Reasoning, Request, ToolChoice  # noqa: E402

cap = Capture("meta-anthropic", env_var="META_API_KEY", default_model="muse-spark-1.3", host="api.meta.ai/v1/messages", change_slug="meta-live")

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
LOW = Reasoning(effort="low")
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=3000)), stream=False,
            description="Meta Muse Spark over the Anthropic wire: basic_text (reasons by default; thinking block with display summarized)",
            expect_lm15=TEXT_OK, evidence_note="content blocks and usage.output_tokens_details.thinking_tokens are the findings", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=3000)), stream=True,
            description="Meta Muse Spark over the Anthropic wire: streaming (message_start … content_block_delta … message_stop)",
            expect_lm15=None, evidence_note="Anthropic SSE event vocabulary as served by Meta", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark over the Anthropic wire: thinking {type: adaptive} + output_config.effort=low (compat thinking_format=adaptive)",
            expect_lm15=TEXT_OK, evidence_note="protocols--messages.md § Reasoning", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark over the Anthropic wire: tool_use block; stop_reason tool_use",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_use id shape and any thinking/redacted_thinking block are the findings", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Meta Muse Spark over the Anthropic wire: streamed tool_use (input_json_delta)",
            expect_lm15=None, evidence_note="MAP-9 premise for this endpoint", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="Meta Muse Spark over the Anthropic wire: the live turn-1 message (thinking + tool_use) replayed with a tool_result",
                expect_lm15=TEXT_OK, evidence_note=info["note"].replace("as reasoning_content", "as thinking blocks"), force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case(
            "response_format_json_schema",
            Request(model=model, messages=(Message.user("Where is the Eiffel Tower?"),),
                    config=Config(max_tokens=600, reasoning=LOW,
                                  response_format={"type": "json_schema", "name": "place",
                                                   "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                                                              "required": ["city", "country"], "additionalProperties": False},
                                                   "strict": True})), stream=False,
            description="Meta Muse Spark over the Anthropic wire: output_config.format json_schema (protocols--messages.md § Request fields)",
            expect_lm15=TEXT_OK, evidence_note="whether the schema is honoured is the finding", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark over the Anthropic wire: top-level system string",
            expect_lm15=TEXT_OK, evidence_note="system accepts text only", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW, user_id="lm15-case-user")), stream=False,
            description="Meta Muse Spark over the Anthropic wire: Config.user_id rides metadata.user_id (also sets the safety identifier — protocols--messages.md)",
            expect_lm15=TEXT_OK, evidence_note="metadata.user_id", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    if want("reasoning"):
        rows.append(cap.probe("error-thinking-disabled", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=Reasoning(effort="off")))))
        rows.append(cap.probe("effort-minimal", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort="minimal")))))
        rows.append(cap.probe("effort-xhigh", Request(model=model, messages=SAY, config=Config(max_tokens=2000, reasoning=Reasoning(effort="xhigh")))))
        rows.append(cap.probe("thinking-enabled-budget", raw_body={"model": model, "max_tokens": 2000, "messages": [{"role": "user", "content": "Say ok."}],
                                                                   "thinking": {"type": "enabled", "budget_tokens": 1024}}))
        rows.append(cap.probe("thinking-display-omitted", raw_body={"model": model, "max_tokens": 600, "messages": [{"role": "user", "content": "Say ok."}],
                                                                    "thinking": {"type": "adaptive", "display": "omitted"}, "output_config": {"effort": "low"}}))
    if want("cache"):
        # cache_control="none" in the preset: this probe sends the Anthropic mark by hand to see whether the server rejects or ignores it.
        rows.append(cap.probe("cache-control-mark", raw_body={"model": model, "max_tokens": 300, "output_config": {"effort": "low"}, "thinking": {"type": "adaptive"},
                                                              "system": [{"type": "text", "text": "You are a helpful assistant. " * 60, "cache_control": {"type": "ephemeral"}}],
                                                              "messages": [{"role": "user", "content": "Say ok."}]}))
    if want("tool_choice"):
        rows.append(cap.probe("tool-choice-any", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=LOW, tool_choice=ToolChoice(mode="required")))))
        rows.append(cap.probe("error-tool-choice-named", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=LOW, tool_choice=ToolChoice(mode="required", allowed=("get_weather",))))))
        rows.append(cap.probe("parallel-false", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=LOW, tool_choice=ToolChoice(mode="auto", parallel=False)))))
    if want("sampling"):
        rows.append(cap.probe("error-top-k", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=LOW, top_k=1))))
        rows.append(cap.probe("error-stop-sequence", Request(model=model, messages=(Message.user("Count from 1 to 10, separated by commas."),), config=Config(max_tokens=300, reasoning=LOW, stop=("5",)))))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=100)), model_key="LLM|000000|invalid"))
        rows.append(cap.probe("error-model-not-found", Request(model="muse-nonexistent", messages=SAY, config=Config(max_tokens=100))))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "thinking-disabled", "tool-choice-named", "top-k", "stop-sequence"))
