#!/usr/bin/env python3
"""Moonshot AI (Kimi API Platform) live capture — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-moonshotai/``.

    MOONSHOTAI_API_KEY=… python3 research/providers/moonshotai/capture.py [--dry-run] [--only a,b] [--force]

Model default ``kimi-k3`` (the flagship; always thinks, effort low|high|max,
default max — guide--reasoning-effort.md).  Cases use effort ``low`` so
bodies stay small; ``basic_text`` leaves the dial alone to pin the
expensive default.  ``kimi-k2.6`` cases pin the other reasoning family
(``thinking: {type}``).  Probes target the dossier's open decisions: which
family rejects which field, the deprecated ``max_tokens``, the fixed
``temperature``, ``tool_choice`` on K2.6, ``user`` vs ``safety_identifier``,
``json_schema``, the cache-usage spelling, tool-loop replay without
``reasoning_content``, and the error envelope.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request, ToolChoice  # noqa: E402

cap = Capture("moonshotai", env_var="MOONSHOTAI_API_KEY", default_model="kimi-k3", host="api.moonshot.ai")

K26 = "kimi-k2.6"
SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
LOW = Reasoning(effort="low")


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=2000)), stream=False,
            description="Moonshot kimi-k3 basic_text (Chat Completions dialect; reasoning always on, default effort max)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="reasoning_content expected alongside content; how many reasoning tokens 'Say ok.' costs at effort max is the finding",
            force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Moonshot kimi-k3 streaming (SSE, data: [DONE]; stream_options.include_usage documented — usage on the final chunk)",
            expect_lm15=None, evidence_note="reasoning_content deltas precede content deltas (guide--thinking-models.md)", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 reasoning effort low (top-level reasoning_effort alone — the 'kimi' wire shape, no thinking object)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="guide--reasoning-effort.md; kimi-k3 rejects a thinking object (probe)", force=force))
    if want("reasoning_off"):
        rows.append(cap.write_case(
            "reasoning_off", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=Reasoning(effort="off"))), stream=False,
            description="Moonshot kimi-k3 reasoning off (thinking: {type: disabled} alone). The docs say K3 always reasons and takes no thinking object; "
                        "live it honours the switch: no reasoning_content, no completion_tokens_details",
            expect_lm15={"parts": {"text": {"min": 1}, "thinking": {"max": 0}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="docs contradicted (guide--thinking-models.md: 'does not support the thinking parameter'); probe-error-k3-thinking-disabled first showed it",
            force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 tool call (function tools; reasoning_content with the call)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_call id shape and reasoning_content presence are the findings", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Moonshot kimi-k3 streaming tool call (does the call arrive whole or as argument deltas?)",
            expect_lm15=None, evidence_note="MAP-9 premise for this provider", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="Moonshot kimi-k3 tool result turn: the assistant turn replayed with its reasoning_content (thinking_replay=native; "
                            "docs: pass the complete assistant message back as-is, required for K3)",
                expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
                evidence_note=info["note"], force=force))
    if want("response_format_json_object"):
        rows.append(cap.write_case(
            "response_format_json_object",
            Request(model=model, messages=(Message.developer("Answer in JSON with keys city and country."), Message.user("Where is the Eiffel Tower? Reply as json.")),
                    config=Config(max_tokens=600, reasoning=LOW, response_format={"type": "json_object"})), stream=False,
            description="Moonshot kimi-k3 JSON mode (response_format: json_object; the prompt must name the fields — guide--json-mode.md)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="guide--json-mode.md", force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case(
            "response_format_json_schema",
            Request(model=model, messages=(Message.user("Where is the Eiffel Tower? Reply as json."),),
                    config=Config(max_tokens=600, reasoning=LOW,
                                  response_format={"type": "json_schema", "name": "place",
                                                   "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                                                              "required": ["city", "country"], "additionalProperties": False},
                                                   "strict": True})), stream=False,
            description="Moonshot kimi-k3 structured output (response_format: json_schema, strict — MFJS; guide--response-format.md)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="whether the schema is honoured (keys city, country only) is the finding", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, messages=(Message.developer("You answer in exactly two words."), *SAY),
                                     config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 system prompt (role: system)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="instruction_role=system", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW, user_id="lm15-case-user")), stream=False,
            description="Moonshot kimi-k3 user identity: Config.user_id rides the documented `safety_identifier` field (compat user_field)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="chat--create.md OpenAPI safety_identifier; no `user` field documented", force=force))
    if want("k26_reasoning_off"):
        rows.append(cap.write_case(
            "k26_reasoning_off", Request(model=K26, messages=SAY, config=Config(max_tokens=600, reasoning=Reasoning(effort="off"))), stream=False,
            description="Moonshot kimi-k2.6 reasoning off (thinking: {type: disabled} alone — the K2.x family's shape; no reasoning_effort)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="api--models-overview.md: kimi-k2.6 accepts enabled|disabled; no reasoning_content expected", force=force))
    if want("k26_basic_text"):
        rows.append(cap.write_case(
            "k26_basic_text", Request(model=K26, messages=SAY, config=Config(max_tokens=2000)), stream=False,
            description="Moonshot kimi-k2.6 basic_text (thinking on by default; reasoning_content expected)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="guide--thinking-models.md: kimi-k2.6 thinks by default", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    raw = {"model": model, "messages": [{"role": "user", "content": "Say ok."}], "max_completion_tokens": 300, "reasoning_effort": "low"}
    raw26 = {"model": K26, "messages": [{"role": "user", "content": "Say ok."}], "max_completion_tokens": 300}
    if want("reasoning_fields"):
        # The two documented families, each sent the other's field.  Loud or silent decides the wire shape.
        rows.append(cap.probe("k3-thinking-enabled-plus-effort", raw_body={**raw, "thinking": {"type": "enabled"}}))  # the deepseek shape
        rows.append(cap.probe("error-k3-thinking-disabled", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort="off")))))
        rows.append(cap.probe("error-k26-reasoning-effort", Request(model=K26, messages=SAY, config=Config(max_tokens=300, reasoning=LOW))))
        rows.append(cap.probe("k26-thinking-keep-all", raw_body={**raw26, "thinking": {"type": "enabled", "keep": "all"}}))
    if want("effort"):
        rows.append(cap.probe("error-k3-effort-medium", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort="medium")))))
        rows.append(cap.probe("error-bad-effort", raw_body={**raw, "reasoning_effort": "bogus"}))
    if want("params"):
        rows.append(cap.probe("max-tokens-deprecated", raw_body={"model": model, "messages": raw["messages"], "max_tokens": 300, "reasoning_effort": "low"}))
        rows.append(cap.probe("error-temperature", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=LOW, temperature=0.5))))
        rows.append(cap.probe("error-max-tokens-below-reasoning", Request(model=model, messages=SAY, config=Config(max_tokens=5, reasoning=LOW))))
    if want("tool_choice"):
        rows.append(cap.probe("k3-tool-choice-required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="required")))))
        rows.append(cap.probe("k3-tool-choice-none", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="none")))))
        rows.append(cap.probe("error-k26-tool-choice-required", Request(model=K26, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=600, tool_choice=ToolChoice(mode="required")))))
    if want("user_field"):
        rows.append(cap.probe("user-field-user", raw_body={**raw, "user": "lm15-probe"}))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=10)), model_key="invalid-key"))
        rows.append(cap.probe("error-model-not-found", Request(model="kimi-nonexistent", messages=SAY, config=Config(max_tokens=10))))
        rows.append(cap.probe("error-missing-reasoning-content-with-tools", raw_body={
            "model": model, "max_completion_tokens": 600, "reasoning_effort": "low",
            "messages": [{"role": "user", "content": "What is the weather in Paris? Use the tool."},
                         {"role": "assistant", "content": None,
                          "tool_calls": [{"id": "call_probe", "type": "function", "function": {"name": "get_weather", "arguments": "{\"city\":\"Paris\"}"}}]},
                         {"role": "tool", "tool_call_id": "call_probe", "content": "Sunny"}],
            "tools": [{"type": "function", "function": {"name": WEATHER.name, "description": WEATHER.description, "parameters": WEATHER.parameters}}],
        }))
    if want("usage_spelling"):
        # Docs: cache hits need >256 prompt tokens on the previous request; usage shows top-level `cached_tokens`.
        req = Request(model=model, messages=(Message.developer("You are a helpful assistant. " * 60), *SAY), config=Config(max_tokens=300, reasoning=LOW))
        rows.append(cap.probe("cache-usage-first", req))
        rows.append(cap.probe("cache-usage-second", req))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "bad-effort", "k3-effort-medium", "k3-thinking-disabled",
                                          "k26-reasoning-effort", "k26-tool-choice-required", "temperature", "max-tokens-below-reasoning",
                                          "missing-reasoning-content-with-tools"))
