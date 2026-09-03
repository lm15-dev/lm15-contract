#!/usr/bin/env python3
"""DeepSeek live capture — case and probe declarations.

The machinery (key handling, adapter-built wires, verbatim bodies, case and
receipt shapes, ``--dry-run``) is ``research/providers/_capture.py``.  This
file says only WHAT to send.  Receipts: ``receipts/<date>-deepseek/``.

    DEEPSEEK_API_KEY=… python3 research/providers/deepseek/capture.py [--dry-run] [--only a,b] [--force]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request  # noqa: E402

cap = Capture("deepseek", env_var="DEEPSEEK_API_KEY", default_model="deepseek-v4-flash", host="api.deepseek.com")

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=600)), stream=False,
            description="DeepSeek basic_text (Chat Completions dialect; thinking mode on by default)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="reasoning_content expected alongside content (thinking default enabled, effort high)", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=600)), stream=True,
            description="DeepSeek streaming (SSE; stream_options.include_usage → usage on the final chunk)",
            expect_lm15=None, evidence_note="SSE terminated by data: [DONE]; usage on the last chunk", force=force))
    if want("reasoning_off"):
        rows.append(cap.write_case(
            "reasoning_off", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=Reasoning(effort="off"))), stream=False,
            description="DeepSeek reasoning off (thinking: {type: disabled}); no reasoning_content, no reasoning tokens",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="explicit off must be honoured: expect reasoning_tokens 0/absent and no reasoning_content", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=Reasoning(effort="low"))), stream=False,
            description="DeepSeek reasoning effort low (thinking enabled + reasoning_effort: low)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="effort word passes verbatim (docs: low|high|max)", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)), stream=False,
            description="DeepSeek tool call (function tools; reasoning_content in the same message)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_call ids of the call_00_… shape", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)), stream=True,
            description="DeepSeek streaming tool call (MAP-9 premise: one streamed call per dialect)",
            expect_lm15=None, evidence_note="tool_calls deltas with index/id/arguments fragments", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="DeepSeek tool result turn: the assistant turn is replayed with its reasoning_content "
                            "(thinking_replay=native); DeepSeek requires it whenever tools are present",
                expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
                evidence_note=info["note"], force=force))
    if want("response_format_json_object"):
        rows.append(cap.write_case(
            "response_format_json_object",
            Request(model=model, messages=(Message.developer("Answer in JSON with keys city and country."), Message.user("Where is the Eiffel Tower? Reply as json.")),
                    config=Config(max_tokens=300, response_format={"type": "json_object"})), stream=False,
            description="DeepSeek JSON Output (response_format: json_object; prompt mentions json per docs)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="the only structured mode DeepSeek documents", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, messages=(Message.developer("You answer in exactly two words."), *SAY),
                                     config=Config(max_tokens=100, reasoning=Reasoning(effort="off"))), stream=False,
            description="DeepSeek system prompt (role: system; thinking off to keep the body small)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="instruction_role=system", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=50, user_id="lm15-case-user", reasoning=Reasoning(effort="off"))), stream=False,
            description="DeepSeek user identity: Config.user_id rides DeepSeek's documented `user_id` field (compat user_field), not OpenAI's `user`",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="probe 2026-09-03: `user` and `user_id` both 200 with no echo; the documented name is sent", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    raw = {"model": model, "messages": [{"role": "user", "content": "Say ok."}], "max_tokens": 50, "thinking": {"type": "disabled"}}
    if want("user_field"):
        rows.append(cap.probe("user-field-user", Request(model=model, messages=SAY, config=Config(max_tokens=50, user_id="lm15-probe", reasoning=Reasoning(effort="off")))))
        rows.append(cap.probe("user-field-user_id", raw_body={**raw, "user_id": "lm15-probe"}))
        rows.append(cap.probe("user-field-user_id-bad-chars", raw_body={**raw, "user_id": "bad id!"}))
    if want("minimal"):
        rows.append(cap.probe("effort-minimal", Request(model=model, messages=SAY, config=Config(max_tokens=200, reasoning=Reasoning(effort="minimal")))))
        rows.append(cap.probe("effort-medium", Request(model=model, messages=SAY, config=Config(max_tokens=200, reasoning=Reasoning(effort="medium")))))
    if want("json_schema"):
        rows.append(cap.probe("json-schema", Request(model=model, messages=(Message.user("Where is the Eiffel Tower? Reply as json."),),
                                                     config=Config(max_tokens=200, reasoning=Reasoning(effort="off"),
                                                                   response_format={"type": "json_schema", "name": "place",
                                                                                    "schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
                                                                                    "strict": True}))))
    if want("temperature"):
        rows.append(cap.probe("temperature-thinking", Request(model=model, messages=SAY, config=Config(max_tokens=200, temperature=0.0))))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=10)), model_key="sk-invalid"))
        rows.append(cap.probe("error-model-not-found", Request(model="deepseek-nonexistent", messages=SAY, config=Config(max_tokens=10))))
        rows.append(cap.probe("error-bad-effort", raw_body={"model": model, "messages": [{"role": "user", "content": "Say ok."}], "max_tokens": 10, "reasoning_effort": "bogus"}))
        rows.append(cap.probe("error-missing-reasoning-content-with-tools", raw_body={
            "model": model, "max_tokens": 100,
            "messages": [{"role": "user", "content": "What is the weather in Paris? Use the tool."},
                         {"role": "assistant", "content": None,
                          "tool_calls": [{"id": "call_00_probe", "type": "function", "function": {"name": "get_weather", "arguments": "{\"city\":\"Paris\"}"}}]},
                         {"role": "tool", "tool_call_id": "call_00_probe", "content": "Sunny"}],
            "tools": [{"type": "function", "function": {"name": WEATHER.name, "description": WEATHER.description, "parameters": WEATHER.parameters}}],
        }))
    if want("usage_spelling"):
        req = Request(model=model, messages=(Message.developer("You are a helpful assistant. " * 40), *SAY),
                      config=Config(max_tokens=20, reasoning=Reasoning(effort="off")))
        rows.append(cap.probe("cache-usage-first", req))
        rows.append(cap.probe("cache-usage-second", req))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "bad-effort", "missing-reasoning-content-with-tools"))
