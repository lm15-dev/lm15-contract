#!/usr/bin/env python3
"""Moonshot AI over the Anthropic Messages wire (`moonshotai-anthropic`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-moonshotai-anthropic/``.

    MOONSHOTAI_API_KEY=… python3 research/providers/moonshotai-anthropic/capture.py [--dry-run] [--only a,b] [--force]

The OpenAPI (messages--create.md) lists no `thinking` request field: kimi-k3
always reasons and `output_config.effort` low|high|max is the whole dial.
Probes decide the compat thinking shape: does the server take, ignore or
refuse `thinking: {type: adaptive}`, `{type: disabled}`, `{type: enabled,
budget_tokens}`; does it validate effort words; does a thinking block come
back signed (an unsigned block is replayed as text by the dialect); is
`x-api-key` accepted beside the documented bearer token; does /models
answer on the /anthropic root; named tool_choice, temperature, cache marks.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request, ToolChoice  # noqa: E402
from lm15.transports import TransportRequest  # noqa: E402

cap = Capture("moonshotai-anthropic", env_var="MOONSHOTAI_API_KEY", default_model="kimi-k3", host="api.moonshot.ai/anthropic/v1/messages")

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
LOW = Reasoning(effort="low")
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=2000)), stream=False,
            description="Moonshot kimi-k3 over the Anthropic wire: basic_text (always reasons, default effort max; thinking block first)",
            expect_lm15=TEXT_OK, evidence_note="content block order thinking → text and usage.output_tokens_details.thinking_tokens are the findings", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Moonshot kimi-k3 over the Anthropic wire: streaming (message_start … content_block_delta thinking_delta / text_delta … message_stop)",
            expect_lm15=None, evidence_note="Anthropic SSE vocabulary as served by Moonshot; whether a signature_delta arrives", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 over the Anthropic wire: output_config.effort=low (the documented dial)",
            expect_lm15=TEXT_OK, evidence_note="messages--create.md output_config.effort", force=force))
    if want("reasoning_off"):
        rows.append(cap.write_case(
            "reasoning_off", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=Reasoning(effort="off"))), stream=False,
            description="Moonshot kimi-k3 over the Anthropic wire: thinking {type: disabled} alone. messages--create.md lists no thinking field; live the switch is honoured "
                        "(no thinking block, no output_tokens_details)",
            expect_lm15={"parts": {"text": {"min": 1}, "thinking": {"max": 0}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="docs contradicted; probe-error-thinking-disabled first showed it", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 over the Anthropic wire: tool_use block; stop_reason tool_use",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_use id shape and whether the thinking block is signed are the findings", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Moonshot kimi-k3 over the Anthropic wire: streamed tool_use (input_json_delta)",
            expect_lm15=None, evidence_note="MAP-9 premise for this endpoint", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="Moonshot kimi-k3 over the Anthropic wire: the live turn-1 message (thinking + tool_use) replayed with a tool_result",
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
            description="Moonshot kimi-k3 over the Anthropic wire: output_config.format json_schema (messages--create.md)",
            expect_lm15=TEXT_OK, evidence_note="whether the schema is honoured is the finding", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Moonshot kimi-k3 over the Anthropic wire: top-level system string",
            expect_lm15=TEXT_OK, evidence_note="system accepts a string or text blocks", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW, user_id="lm15-case-user")), stream=False,
            description="Moonshot kimi-k3 over the Anthropic wire: Config.user_id rides metadata.user_id (documented: cache affinity + abuse detection)",
            expect_lm15=TEXT_OK, evidence_note="metadata.user_id", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def _header_probe(name: str, headers: list[tuple[str, str]], body: dict) -> dict:
    """A probe with hand-built headers (the adapter's auth header replaced)."""
    adapter = cap.lm()
    base = adapter.build_request(Request(model=body["model"], messages=SAY, config=Config(max_tokens=100)), stream=False)
    treq = TransportRequest(method=base.method, url=base.url, headers=headers, body=json.dumps(body).encode(),
                            connect_timeout=base.connect_timeout, read_timeout=base.read_timeout, write_timeout=base.write_timeout)
    status, raw, ts, resp_headers = cap.send(treq)
    if cap.dry_run:
        return {"probe": name, "status": status}
    text = raw.decode("utf-8", "replace")
    try:
        parsed = json.loads(text)
    except ValueError:
        parsed = text
    sent = {"method": treq.method, "url": treq.url, "headers": {k: (cap.placeholder if k.lower() in ("x-api-key", "authorization") else v) for k, v in headers}, "body": body}
    cap.write_receipt(f"probe-{name}.json", {"sent": sent, "status": status, "body": parsed, "timestamp": ts})
    return {"probe": name, "status": status, "summary": str(parsed)[:160]}


def probes(model: str, want) -> list[dict]:
    rows = []
    raw = {"model": model, "max_tokens": 600, "messages": [{"role": "user", "content": "Say ok."}]}
    if want("reasoning"):
        rows.append(cap.probe("effort-only", raw_body={**raw, "output_config": {"effort": "low"}}))  # the documented shape, no thinking object
        rows.append(cap.probe("thinking-adaptive-plus-effort", raw_body={**raw, "thinking": {"type": "adaptive"}, "output_config": {"effort": "low"}}))  # the current preset shape
        rows.append(cap.probe("error-thinking-disabled", raw_body={**raw, "thinking": {"type": "disabled"}}))
        rows.append(cap.probe("thinking-enabled-budget", raw_body={**raw, "max_tokens": 2000, "thinking": {"type": "enabled", "budget_tokens": 1024}}))
        rows.append(cap.probe("error-effort-medium", raw_body={**raw, "output_config": {"effort": "medium"}}))
        rows.append(cap.probe("error-effort-bogus", raw_body={**raw, "output_config": {"effort": "bogus"}}))
    if want("auth"):
        rows.append(_header_probe("x-api-key-header", [("anthropic-version", "2023-06-01"), ("content-type", "application/json"), ("x-api-key", cap.key())],
                                  {**raw, "max_tokens": 100, "output_config": {"effort": "low"}}))
    if want("replay"):
        # A hand-built tool loop that replays the assistant turn WITHOUT its thinking block: does the server demand it (Preserved Thinking)?
        rows.append(cap.probe("replay-without-thinking-block", raw_body={
            "model": model, "max_tokens": 600, "output_config": {"effort": "low"},
            "messages": [{"role": "user", "content": "What is the weather in Paris? Use the tool."},
                         {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_probe", "name": "get_weather", "input": {"city": "Paris"}}]},
                         {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_probe", "content": "Sunny"}]}],
            "tools": [{"name": WEATHER.name, "description": WEATHER.description, "input_schema": WEATHER.parameters}]}))
        # …and one that replays an UNSIGNED thinking block (what the dialect would send if no signature comes back and it kept the block type).
        rows.append(cap.probe("replay-unsigned-thinking-block", raw_body={
            "model": model, "max_tokens": 600, "output_config": {"effort": "low"},
            "messages": [{"role": "user", "content": "What is the weather in Paris? Use the tool."},
                         {"role": "assistant", "content": [{"type": "thinking", "thinking": "I should call the weather tool."},
                                                           {"type": "tool_use", "id": "toolu_probe", "name": "get_weather", "input": {"city": "Paris"}}]},
                         {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_probe", "content": "Sunny"}]}],
            "tools": [{"name": WEATHER.name, "description": WEATHER.description, "input_schema": WEATHER.parameters}]}))
    if want("cache"):
        rows.append(cap.probe("cache-control-mark", raw_body={**raw, "max_tokens": 300, "output_config": {"effort": "low"},
                                                              "system": [{"type": "text", "text": "You are a helpful assistant. " * 60, "cache_control": {"type": "ephemeral"}}]}))
    if want("tool_choice"):
        rows.append(cap.probe("tool-choice-any", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="required")))))
        rows.append(cap.probe("tool-choice-none", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="none")))))
        rows.append(cap.probe("error-tool-choice-named", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="required", allowed=("get_weather",))))))
        rows.append(cap.probe("parallel-false", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW, tool_choice=ToolChoice(mode="auto", parallel=False)))))
    if want("sampling"):
        rows.append(cap.probe("error-temperature", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=LOW, temperature=0.5))))
        rows.append(cap.probe("error-top-k", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=LOW, top_k=1))))
        rows.append(cap.probe("stop-sequence", Request(model=model, messages=(Message.user("Count from 1 to 10, separated by commas."),), config=Config(max_tokens=300, reasoning=LOW, stop=("5",)))))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=100)), model_key="sk-invalid"))
        rows.append(cap.probe("error-model-not-found", Request(model="kimi-nonexistent", messages=SAY, config=Config(max_tokens=100))))
        rows.append(cap.probe("error-model-k26", Request(model="kimi-k2.6", messages=SAY, config=Config(max_tokens=100))))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "model-k26", "thinking-disabled", "effort-medium", "effort-bogus",
                                          "tool-choice-named", "temperature", "top-k"))
