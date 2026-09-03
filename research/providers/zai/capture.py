#!/usr/bin/env python3
"""Z.AI (GLM) live capture — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-zai/``.

    ZAI_API_KEY=… python3 research/providers/zai/capture.py [--dry-run] [--only a,b] [--force]

Model default ``glm-5.3-flash`` (the cheapest GLM-5.3; forced thinking,
efforts low|high|max — model--glm-5.3.md).  Probes target the dossier's
open decisions: forced thinking vs an explicit off, tool_choice beyond
``auto``, ``user`` vs ``user_id``, effort words outside the documented
set, ``json_schema``, temperature above 1.0, stream usage without the
``tool_stream`` flag, the error envelope, and cache usage.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request, ToolChoice  # noqa: E402

cap = Capture("zai", env_var="ZAI_API_KEY", default_model="glm-5.3-flash", host="api.z.ai")

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=600)), stream=False,
            description="Z.AI GLM basic_text (Chat Completions dialect; thinking on by default, effort max)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="reasoning_content expected alongside content (forced thinking on GLM-5.3)", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=600)), stream=True,
            description="Z.AI GLM streaming (SSE, data: [DONE]; is usage on the final chunk without tool_stream?)",
            expect_lm15=None, evidence_note="stream_options.include_usage sent; whether usage arrives is the finding", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=Reasoning(effort="low"))), stream=False,
            description="Z.AI GLM reasoning effort low (thinking: enabled + reasoning_effort: low — the deepseek wire shape)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="the shape the earlier `zai` preset got wrong (enable_thinking); docs.z.ai ChatThinking", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)), stream=False,
            description="Z.AI GLM tool call (function tools; interleaved thinking → reasoning_content with the call)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_call id shape and reasoning_content presence are the findings", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)), stream=True,
            description="Z.AI GLM streaming tool call without tool_stream (docs: default false — does the call arrive whole?)",
            expect_lm15=None, evidence_note="MAP-9 premise for this provider", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="Z.AI GLM tool result turn: the assistant turn replayed with its reasoning_content (thinking_replay=native; "
                            "docs: return thinking blocks with tool results)",
                expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
                evidence_note=info["note"], force=force))
    if want("response_format_json_object"):
        rows.append(cap.write_case(
            "response_format_json_object",
            Request(model=model, messages=(Message.developer("Answer in JSON with keys city and country."), Message.user("Where is the Eiffel Tower? Reply as json.")),
                    config=Config(max_tokens=300, response_format={"type": "json_object"})), stream=False,
            description="Z.AI GLM JSON mode (response_format: json_object — the only structured mode documented)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="guide--struct-output.md", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, messages=(Message.developer("You answer in exactly two words."), *SAY),
                                     config=Config(max_tokens=300, reasoning=Reasoning(effort="low"))), stream=False,
            description="Z.AI GLM system prompt (role: system; effort low to keep the body small — thinking cannot be off)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="instruction_role=system", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=300, user_id="lm15-case-user", reasoning=Reasoning(effort="low"))), stream=False,
            description="Z.AI GLM user identity: Config.user_id rides the documented `user_id` field (6–128 chars; compat user_field)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="chat--create.md user_id", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    low = Config(max_tokens=200, reasoning=Reasoning(effort="low"))
    raw = {"model": model, "messages": [{"role": "user", "content": "Say ok."}], "max_tokens": 200, "reasoning_effort": "low"}
    if want("forced_thinking"):
        # GLM-5.3: "disabling reasoning is not supported … the request will fail". Loud or silent?
        rows.append(cap.probe("thinking-disabled-glm-5.3", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=Reasoning(effort="off")))))
        rows.append(cap.probe("thinking-disabled-glm-5.2", Request(model="glm-5.2", messages=SAY, config=Config(max_tokens=100, reasoning=Reasoning(effort="off")))))
    if want("effort"):
        # Documented set for 5.3 is low|high|max; the schema enum is wider. What do medium / minimal / none do?
        rows.append(cap.probe("effort-medium", Request(model=model, messages=SAY, config=Config(max_tokens=200, reasoning=Reasoning(effort="medium")))))
        rows.append(cap.probe("effort-minimal", Request(model=model, messages=SAY, config=Config(max_tokens=200, reasoning=Reasoning(effort="minimal")))))
        rows.append(cap.probe("error-bad-effort", raw_body={**raw, "reasoning_effort": "bogus"}))
    if want("tool_choice"):
        # Docs: only `auto`. required / named: 400 (loud) or ignored (silent)?
        rows.append(cap.probe("tool-choice-required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=Reasoning(effort="low"), tool_choice=ToolChoice(mode="required")))))
        rows.append(cap.probe("tool-choice-none", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=Reasoning(effort="low"), tool_choice=ToolChoice(mode="none")))))
    if want("user_field"):
        rows.append(cap.probe("user-field-user", raw_body={**raw, "user": "lm15-probe"}))
        rows.append(cap.probe("user-field-user_id-short", raw_body={**raw, "user_id": "abc"}))  # below the 6-char minimum
    if want("json_schema"):
        rows.append(cap.probe("json-schema", Request(model=model, messages=(Message.user("Where is the Eiffel Tower? Reply as json."),),
                                                     config=Config(max_tokens=300, reasoning=Reasoning(effort="low"),
                                                                   response_format={"type": "json_schema", "name": "place",
                                                                                    "schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
                                                                                    "strict": True}))))
    if want("temperature"):
        rows.append(cap.probe("temperature-1.3", Request(model=model, messages=SAY, config=Config(max_tokens=200, temperature=1.3, reasoning=Reasoning(effort="low")))))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=10)), model_key="invalid-key"))
        rows.append(cap.probe("error-model-not-found", Request(model="glm-nonexistent", messages=SAY, config=Config(max_tokens=10))))
        rows.append(cap.probe("error-missing-reasoning-content-with-tools", raw_body={
            "model": model, "max_tokens": 300, "reasoning_effort": "low",
            "messages": [{"role": "user", "content": "What is the weather in Paris? Use the tool."},
                         {"role": "assistant", "content": None,
                          "tool_calls": [{"id": "call_probe", "type": "function", "function": {"name": "get_weather", "arguments": "{\"city\":\"Paris\"}"}}]},
                         {"role": "tool", "tool_call_id": "call_probe", "content": "Sunny"}],
            "tools": [{"type": "function", "function": {"name": WEATHER.name, "description": WEATHER.description, "parameters": WEATHER.parameters}}],
        }))
    if want("usage_spelling"):
        req = Request(model=model, messages=(Message.developer("You are a helpful assistant. " * 60), *SAY), config=low)
        rows.append(cap.probe("cache-usage-first", req))
        rows.append(cap.probe("cache-usage-second", req))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "bad-effort", "missing-reasoning-content-with-tools"))
