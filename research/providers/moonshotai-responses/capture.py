#!/usr/bin/env python3
"""Moonshot AI over the Responses wire (`moonshotai-responses`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-moonshotai-responses/``.

    MOONSHOTAI_API_KEY=… python3 research/providers/moonshotai-responses/capture.py [--dry-run] [--only a,b] [--force]

The OpenAPI (responses--create.md) says: kimi-k3 only; stateless (`store`
always false, `previous_response_id` always null); reasoning comes back as
`summary` text with `encrypted_content: null` and is replayed as a
`reasoning` item; `reasoning.effort` low|high|max; `tool_choice` auto only;
`text.format` json_schema only; tools function|custom|namespace|web_search.
Probes decide: reasoning off, effort validation, `reasoning.summary`,
tool_choice beyond auto, json_object, replay without the reasoning item,
`prompt_cache_retention`, temperature, the web_search built-in, errors.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import BuiltinTool, CacheConfig, Config, Message, Reasoning, Request, ToolChoice  # noqa: E402

cap = Capture("moonshotai-responses", env_var="MOONSHOTAI_API_KEY", default_model="kimi-k3", host="api.moonshot.ai/v1/responses")

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
LOW = Reasoning(effort="low")
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
SCHEMA = {"type": "json_schema", "name": "place",
          "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                     "required": ["city", "country"], "additionalProperties": False}, "strict": True}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=2000)), stream=False,
            description="Moonshot kimi-k3 over the Responses wire: basic_text (always reasons, default effort max; reasoning item then message)",
            expect_lm15=TEXT_OK, evidence_note="output order reasoning → message, summary carries the reasoning text, encrypted_content null", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Moonshot kimi-k3 over the Responses wire: streaming (response.created … reasoning_summary_text.delta … output_text.delta … response.completed)",
            expect_lm15=None, evidence_note="Responses SSE vocabulary as served by Moonshot", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 over the Responses wire: reasoning.effort=low",
            expect_lm15=TEXT_OK, evidence_note="responses--create.md reasoning.effort", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 over the Responses wire: function_call item (call_id shape is the finding)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="function_call.call_id, reasoning item beside it", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Moonshot kimi-k3 over the Responses wire: streamed function_call (output_item.added carries the name; function_call_arguments.delta)",
            expect_lm15=None, evidence_note="MAP-9 premise for this endpoint", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="Moonshot kimi-k3 over the Responses wire: the live turn-1 output (reasoning item with its summary text, function_call) replayed "
                            "with a function_call_output — the stateless replay (store is always false)",
                expect_lm15=TEXT_OK, evidence_note=info["note"].replace("as reasoning_content", "as a reasoning item with summary text"), force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case(
            "response_format_json_schema",
            Request(model=model, messages=(Message.user("Where is the Eiffel Tower?"),), config=Config(max_tokens=600, reasoning=LOW, response_format=SCHEMA)), stream=False,
            description="Moonshot kimi-k3 over the Responses wire: text.format json_schema (the only documented format)",
            expect_lm15=TEXT_OK, evidence_note="whether the schema is honoured is the finding", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, messages=(Message.developer("You answer in exactly two words."), *SAY), config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 over the Responses wire: developer role message (handled as a system instruction — responses--create.md)",
            expect_lm15=TEXT_OK, evidence_note="developer_role=developer", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW, user_id="lm15-case-user")), stream=False,
            description="Moonshot kimi-k3 over the Responses wire: Config.user_id rides safety_identifier",
            expect_lm15=TEXT_OK, evidence_note="responses--create.md safety_identifier", force=force))
    if want("web_search"):
        rows.append(cap.write_case(
            "web_search", Request(model=model, messages=(Message.user("What is today's date and one headline from today? Search the web."),),
                                  tools=(BuiltinTool(name="web_search"),), config=Config(max_tokens=2000, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 over the Responses wire: the server-side web_search built-in (canonical web_search → `web_search`; a web_search_call item leads the output)",
            expect_lm15=TEXT_OK, evidence_note="web_search_call item shape; provider-executed, skipped by the parser", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    raw = {"model": model, "input": "Say ok.", "max_output_tokens": 600, "reasoning": {"effort": "low"}}
    if want("reasoning"):
        rows.append(cap.probe("error-reasoning-none", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort="off")))))
        rows.append(cap.probe("error-effort-medium", raw_body={**raw, "reasoning": {"effort": "medium"}}))
        rows.append(cap.probe("error-effort-bogus", raw_body={**raw, "reasoning": {"effort": "bogus"}}))
        rows.append(cap.probe("reasoning-summary-auto", raw_body={**raw, "reasoning": {"effort": "low", "summary": "auto"}}))
        rows.append(cap.probe("error-thinking-object", raw_body={**raw, "thinking": {"type": "disabled"}}))  # the chat wire's off switch, on this wire
    if want("tool_choice"):
        rows.append(cap.probe("error-tool-choice-required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="required")))))
        rows.append(cap.probe("error-tool-choice-none", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="none")))))
    if want("format"):
        rows.append(cap.probe("error-json-object", Request(model=model, messages=(Message.user("Where is the Eiffel Tower? Reply as json with keys city and country."),),
                                                            config=Config(max_tokens=600, reasoning=LOW, response_format={"type": "json_object"}))))
    if want("replay"):
        rows.append(cap.probe("replay-without-reasoning-item", raw_body={
            "model": model, "max_output_tokens": 600, "reasoning": {"effort": "low"},
            "input": [{"type": "message", "role": "user", "content": "What is the weather in Paris? Use the tool."},
                      {"type": "function_call", "call_id": "get_weather_0", "name": "get_weather", "arguments": "{\"city\":\"Paris\"}"},
                      {"type": "function_call_output", "call_id": "get_weather_0", "output": "Sunny, 22°C"}],
            "tools": [{"type": "function", "name": WEATHER.name, "description": WEATHER.description, "parameters": WEATHER.parameters}]}))
    if want("cache"):
        rows.append(cap.probe("prompt-cache-retention", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=LOW, cache=CacheConfig(key="lm15-probe", retention="long")))))
    if want("sampling"):
        rows.append(cap.probe("error-temperature", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=LOW, temperature=0.5))))
        rows.append(cap.probe("error-max-output-tokens-1", Request(model=model, messages=SAY, config=Config(max_tokens=1, reasoning=LOW))))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=100)), model_key="sk-invalid"))
        rows.append(cap.probe("error-model-not-found", Request(model="kimi-nonexistent", messages=SAY, config=Config(max_tokens=100))))
        rows.append(cap.probe("error-model-k26", Request(model="kimi-k2.6", messages=SAY, config=Config(max_tokens=100))))
        rows.append(cap.probe("error-builtin-code-execution", Request(model=model, messages=SAY, tools=(BuiltinTool(name="code_execution"),), config=Config(max_tokens=100, reasoning=LOW))))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "model-k26", "reasoning-none", "effort-medium", "effort-bogus",
                                          "thinking-object", "tool-choice-required", "tool-choice-none", "json-object", "temperature",
                                          "max-output-tokens-1", "builtin-code-execution"))
