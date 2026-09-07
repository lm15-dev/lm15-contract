#!/usr/bin/env python3
"""Amazon Bedrock Chat Completions on bedrock-mantle (`bedrock-mantle-chat`).

A different host from `bedrock-chat` (bedrock-runtime): un-versioned model
ids, GET /v1/models lists, SigV4 service `bedrock-mantle`.  Probed 2026-09-04
(`receipts/2026-09-04-bedrock-chat/probe-mantle-chat-*`).

    AWS_REGION=us-east-1 python3 research/providers/bedrock-mantle-chat/capture.py [--dry-run] [--only a,b] [--force]

Credentials: lm15's aws-chain; cases pinned re-signed with the fixed test pair.
Default model ``openai.gpt-oss-20b`` (the door's un-versioned namespace).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _aws import REGION  # noqa: E402
from _capture import CONTRACT, WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request, ToolChoice, serde  # noqa: E402
from lm15.credentials import AwsCredentials  # noqa: E402

cap = Capture(
    "bedrock-mantle-chat",
    env_var="AWS_BEARER_TOKEN_BEDROCK",
    default_model=os.environ.get("BEDROCK_MANTLE_CHAT_MODEL", "openai.gpt-oss-20b"),
    host=f"bedrock-mantle.{REGION}.api.aws",
    settings={"region": REGION},
)
cap.prepare = cap.aws_fixture

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
CALL_OK = {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}}
HONOURING = os.environ.get("BEDROCK_MANTLE_CHAT_HONOURING_MODEL", "deepseek.v3.2")
FAMILIES = (
    "deepseek.v3.2",
    "openai.gpt-oss-20b",
    "google.gemma-3-12b-it",
    "mistral.mistral-large-3-675b-instruct",
    "qwen.qwen3-32b",
    "zai.glm-4.7-flash",
)
PLACE_SCHEMA = {
    "type": "json_schema",
    "name": "place",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
        "required": ["city", "country"],
        "additionalProperties": False,
    },
}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=300)), stream=False,
            description="Bedrock-mantle Chat Completions: basic_text (SigV4 service bedrock-mantle; un-versioned id). gpt-oss returns message.reasoning, not inline tags.",
            expect_lm15=TEXT_OK, evidence_note="probe-mantle-chat-sigv4-openai-gpt-oss-20b.json", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=300)), stream=True,
            description="Bedrock-mantle Chat Completions: streaming with stream_options.include_usage",
            expect_lm15=None, evidence_note="compat stream_usage cell", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort="low"))), stream=False,
            description="Bedrock-mantle Chat Completions: reasoning_effort=low",
            expect_lm15=TEXT_OK, evidence_note="compat thinking_format cell", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=400)), stream=False,
            description="Bedrock-mantle Chat Completions: tool_calls",
            expect_lm15=CALL_OK, evidence_note="", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=400)), stream=True,
            description="Bedrock-mantle Chat Completions: streamed tool_calls deltas",
            expect_lm15=None, evidence_note="MAP-9 premise", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=400))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        rows.append({"feature": "multi_turn_tool_result", **info} if second is None else cap.write_case(
            "multi_turn_tool_result", second, stream=False,
            description="Bedrock-mantle Chat Completions: tool result replay",
            expect_lm15=TEXT_OK, evidence_note=info["note"], force=force))
    if want("tool_choice"):
        rows.append(cap.write_case(
            "tool_choice_required", Request(model=HONOURING, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=400, tool_choice=ToolChoice(mode="required"))), stream=False,
            description="Bedrock-mantle Chat Completions: tool_choice required (deepseek.v3.2); per-family overrides from family probes",
            expect_lm15=CALL_OK, evidence_note="compat forced_tool_choice=send", force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case(
            "response_format_json_schema",
            Request(model=HONOURING, messages=(Message.user("Where is the Eiffel Tower?"),),
                    config=Config(max_tokens=400, response_format=PLACE_SCHEMA)),
            stream=False,
            description="Bedrock-mantle Chat Completions: json_schema (deepseek.v3.2); per-family overrides from family probes",
            expect_lm15=TEXT_OK, evidence_note="compat json_schema=send", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=300)), stream=False,
            description="Bedrock-mantle Chat Completions: role system",
            expect_lm15=TEXT_OK, evidence_note="compat instruction_role cell", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=300, user_id="lm15-case-user")), stream=False,
            description="Bedrock-mantle Chat Completions: Config.user_id → user",
            expect_lm15=TEXT_OK, evidence_note="compat user_field cell", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    if want("refusals"):
        rows += _write_refusals(force)
    return rows


def _write_refusals(force: bool) -> list[dict]:
    """MAP-8 per-model refusals.  No wire: the canonical outcome is a raise at build."""
    import json
    rows = []
    specs = [
        ("tool_choice_required_gpt_oss",
         Request(model="openai.gpt-oss-20b", messages=SAY, tools=(WEATHER,), config=Config(max_tokens=400, tool_choice=ToolChoice(mode="required"))),
         "MAP-8: tool_choice beyond auto raises FOR gpt-oss on bedrock-mantle-chat (preset bedrock-mantle, openai.gpt-oss → reject). Live 2026-09-04: HTTP 200, finish=stop, content 'ok.', no tool_calls.",
         "receipts/2026-09-04-bedrock-mantle-chat/probe-family-openai-gpt-oss-20b-tool-choice.json; Gemma honours the same knob on this door"),
        ("response_format_json_schema_gpt_oss",
         Request(model="openai.gpt-oss-20b", messages=(Message.user("Where is the Eiffel Tower?"),), config=Config(max_tokens=400, response_format=PLACE_SCHEMA)),
         "MAP-8: json_schema raises FOR gpt-oss on bedrock-mantle-chat. Live 2026-09-04: HTTP 200, prose + a JSON object in content, not a pure document.",
         "receipts/2026-09-04-bedrock-mantle-chat/probe-family-openai-gpt-oss-20b-json-schema.json"),
    ]
    for feature, request, description, evidence in specs:
        if cap.dry_run:
            rows.append({"feature": feature, "status": "refusal (dry run; no case written)"})
            continue
        path = CONTRACT / "cases" / cap.provider / f"{feature}.json"
        if path.exists() and not force:
            rows.append({"feature": feature, "skipped": "case exists (use --force)"})
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "id": f"{cap.provider}.{feature}", "provider": cap.provider, "feature": feature,
            "description": description, "settings": cap.settings,
            "provenance": {"source": "live-capture", "date": cap.date,
                           "evidence": f"{evidence}; changes/{cap.date}-{cap.provider}-live.md"},
            "canonical_request": serde.request_to_dict(request),
            "canonical_request_provenance": {"source": "hand-authored", "date": cap.date,
                                            "evidence": f"authored with the case (research/providers/{cap.provider}/capture.py); live-validated (receipt above)"},
            "expect_lm15": {"raises": {"op": "build_request", "type": "UnsupportedFeatureError", "code": "unsupported_feature"}},
        }, indent=2, ensure_ascii=False) + "\n")
        rows.append({"feature": feature, "status": "refusal"})
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    req = Request(model=model, messages=SAY, config=Config(max_tokens=10))
    if want("model_ids"):
        for mid in ("openai.gpt-oss-20b-1:0", "anthropic.claude-haiku-4-5", "amazon.nova-2-lite-v1:0", "amazon.nova-micro-v1:0"):
            rows.append(cap.probe(f"model-id-{mid.replace(':', '_').replace('.', '-')}", Request(model=mid, messages=SAY, config=Config(max_tokens=10))))
    if want("family"):
        for mid in FAMILIES:
            slug = mid.replace(".", "-")
            rows.append(cap.probe(
                f"family-{slug}-tool-choice",
                # Bypass the already-evidenced per-family refusal for this
                # raw probe, not for the canonical case builder.
                raw_body={"model": mid, "messages": [{"role": "user", "content": "Say ok."}],
                          "max_completion_tokens": 400, "tool_choice": "required",
                          "tools": [{"type": "function", "function": {
                              "name": WEATHER.name, "description": WEATHER.description, "parameters": WEATHER.parameters}}]},
            ))
            rows.append(cap.probe(
                f"family-{slug}-json-schema",
                raw_body={"model": mid, "messages": [{"role": "user", "content": "Where is the Eiffel Tower?"}],
                          "max_completion_tokens": 400, "response_format": {
                              "type": "json_schema", "json_schema": {k: v for k, v in PLACE_SCHEMA.items() if k != "type"}}},
            ))
    if want("errors"):
        rows.append(cap.probe("error-invalid-signature", req, model_key=AwsCredentials("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY")))
        rows.append(cap.probe("error-model-not-found", Request(model="lm15.no-such-model", messages=SAY, config=Config(max_tokens=10))))
        rows.append(cap.probe("error-bad-param", raw_body={"model": model, "messages": [{"role": "user", "content": "Say ok."}], "max_completion_tokens": -1}))
        rows.append(cap.probe("error-claude-wrong-door", Request(model="anthropic.claude-haiku-4-5", messages=SAY, config=Config(max_tokens=10))))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("invalid-signature", "model-not-found", "bad-param", "claude-wrong-door"))
