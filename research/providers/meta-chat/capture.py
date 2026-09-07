#!/usr/bin/env python3
"""Meta Model API over the Chat Completions wire (`meta-chat`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-meta-chat/``.

    META_API_KEY=… python3 research/providers/meta-chat/capture.py [--dry-run] [--only a,b] [--force]

Probes: the documented refusals (reasoning_effort none, logprobs, n > 1,
stop, modalities — protocols--chat-completions.md § OpenAI compatibility),
the deprecated `user` field next to `safety_identifier`, whether
`reasoning_content` is really redacted to empty (guide--reasoning.md), and
the error envelope.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request, ToolChoice  # noqa: E402

cap = Capture("meta-chat", env_var="META_API_KEY", default_model="muse-spark-1.3", host="api.meta.ai", change_slug="meta-live")

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
LOW = Reasoning(effort="low")
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=3000)), stream=False,
            description="Meta Muse Spark basic_text over Chat Completions (reasons by default; reasoning_content redacted to empty for external keys)",
            expect_lm15=TEXT_OK, evidence_note="completion_tokens_details.reasoning_tokens present; message.reasoning_content empty or absent", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=3000)), stream=True,
            description="Meta Muse Spark streaming over Chat Completions (SSE, stream_options.include_usage → usage on a final choices-empty chunk)",
            expect_lm15=None, evidence_note="chat--schemas.md: choices is empty on the final chunk when include_usage is set", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark top-level reasoning_effort=low (guide--reasoning.md)",
            expect_lm15=TEXT_OK, evidence_note="reasoning_effort at the top level on this wire", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark function call over Chat Completions (tool_calls; finish_reason tool_calls)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_call id shape is the finding", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Meta Muse Spark streamed tool call over Chat Completions (arguments streamed in delta.tool_calls)",
            expect_lm15=None, evidence_note="MAP-9 premise for this provider", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="Meta Muse Spark tool result turn over Chat Completions: assistant tool_calls message replayed with its tool message (no reasoning to replay on this wire)",
                expect_lm15=TEXT_OK, evidence_note=info["note"], force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case(
            "response_format_json_schema",
            Request(model=model, messages=(Message.user("Where is the Eiffel Tower?"),),
                    config=Config(max_tokens=600, reasoning=LOW,
                                  response_format={"type": "json_schema", "name": "place",
                                                   "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                                                              "required": ["city", "country"], "additionalProperties": False},
                                                   "strict": True})), stream=False,
            description="Meta Muse Spark structured output over Chat Completions (response_format json_schema — guide--structured-output.md)",
            expect_lm15=TEXT_OK, evidence_note="response_format, not text.format, on this wire", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark instruction message as role developer (the documented instruction role; system is merged at the same level)",
            expect_lm15=TEXT_OK, evidence_note="instruction_role=developer", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW, user_id="lm15-case-user")), stream=False,
            description="Meta Muse Spark end-user attribution over Chat Completions: Config.user_id rides safety_identifier (user is deprecated)",
            expect_lm15=TEXT_OK, evidence_note="compat user_field=safety_identifier", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    raw = {"model": model, "messages": [{"role": "user", "content": "Say ok."}], "max_completion_tokens": 300, "reasoning_effort": "low"}
    if want("reasoning"):
        rows.append(cap.probe("error-reasoning-none", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=Reasoning(effort="off")))))
        rows.append(cap.probe("reasoning-content-redacted", Request(model=model, messages=(Message.user("What is 17 times 23?"),), config=Config(max_tokens=600, reasoning=LOW))))
    if want("compat"):
        rows.append(cap.probe("error-logprobs", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=LOW, logprobs=2))))
        rows.append(cap.probe("error-stop", Request(model=model, messages=(Message.user("Count from 1 to 10, separated by commas."),), config=Config(max_tokens=100, reasoning=LOW, stop=("5",)))))
        rows.append(cap.probe("error-n-2", raw_body={**raw, "n": 2}))
        rows.append(cap.probe("user-deprecated-field", raw_body={**raw, "user": "lm15-probe"}))
        rows.append(cap.probe("max-tokens-alias", raw_body={"model": model, "messages": raw["messages"], "max_tokens": 300, "reasoning_effort": "low"}))
    if want("tool_choice"):
        rows.append(cap.probe("tool-choice-required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=LOW, tool_choice=ToolChoice(mode="required")))))
        rows.append(cap.probe("tool-choice-none", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=LOW, tool_choice=ToolChoice(mode="none")))))
    if want("cache"):
        req = Request(model=model, system="You are a helpful assistant. " * 60, messages=SAY, config=Config(max_tokens=300, reasoning=LOW))
        rows.append(cap.probe("cache-first", req))
        rows.append(cap.probe("cache-second", req))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=100)), model_key="LLM|000000|invalid"))
        rows.append(cap.probe("error-model-not-found", Request(model="muse-nonexistent", messages=SAY, config=Config(max_tokens=100))))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "reasoning-none", "logprobs", "stop", "n-2"))
