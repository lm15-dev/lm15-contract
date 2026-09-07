#!/usr/bin/env python3
"""Amazon Bedrock over the OpenAI Chat Completions wire (`bedrock-chat`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-bedrock-chat/``.

    AWS_REGION=us-east-1 python3 research/providers/bedrock-chat/capture.py [--dry-run] [--only a,b] [--force]

Credentials: lm15's aws-chain (this machine's ~/.aws profile); the wire is
SigV4 (service `bedrock`) and every case is pinned re-signed with the fixed
test pair at the capture instant.  Model default ``openai.gpt-oss-20b-1:0``
— the door's model-id namespace is Bedrock's own and, live 2026-09-03, the
Claude ids need the account's model agreement (403 otherwise); gpt-oss
answered 200 with no agreement.  Probes: model-id forms, /models (404
UnknownOperationException with SigV4, live 2026-09-03), the compat knobs
(stream usage, tool_choice required, json_schema, reasoning_effort), and
the error envelopes (bad signature, unknown model, oversize).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _aws import REGION  # noqa: E402
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request, ToolChoice  # noqa: E402
from lm15.credentials import AwsCredentials  # noqa: E402

cap = Capture("bedrock-chat", env_var="AWS_BEARER_TOKEN_BEDROCK", default_model=os.environ.get("BEDROCK_CHAT_MODEL", "openai.gpt-oss-20b-1:0"),
              host=f"bedrock-runtime.{REGION}.amazonaws.com", settings={"region": REGION})
cap.prepare = cap.aws_fixture

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
CALL_OK = {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case("basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=300)), stream=False,
            description="Bedrock over the Chat Completions wire: basic_text (SigV4 service bedrock; Bedrock model id)", expect_lm15=TEXT_OK,
            evidence_note="gpt-oss emits <reasoning>…</reasoning> inline in content on this door — passthrough text, not a thinking part", force=force))
    if want("streaming"):
        rows.append(cap.write_case("streaming", Request(model=model, messages=SAY, config=Config(max_tokens=300)), stream=True,
            description="Bedrock over the Chat Completions wire: streaming with stream_options.include_usage", expect_lm15=None,
            evidence_note="compat stream_usage cell", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case("reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort="low"))), stream=False,
            description="Bedrock over the Chat Completions wire: reasoning_effort=low (gpt-oss)", expect_lm15=TEXT_OK, evidence_note="compat thinking_format cell", force=force))
    if want("tools"):
        rows.append(cap.write_case("tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=400)), stream=False,
            description="Bedrock over the Chat Completions wire: tool_calls", expect_lm15=CALL_OK, evidence_note="", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case("streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=400)), stream=True,
            description="Bedrock over the Chat Completions wire: streamed tool_calls deltas", expect_lm15=None, evidence_note="MAP-9 premise", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=400))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        rows.append({"feature": "multi_turn_tool_result", **info} if second is None else cap.write_case(
            "multi_turn_tool_result", second, stream=False, description="Bedrock over the Chat Completions wire: tool result replay",
            expect_lm15=TEXT_OK, evidence_note=info["note"], force=force))
    honouring = os.environ.get("BEDROCK_CHAT_HONOURING_MODEL", "deepseek.v3.2")  # a family that honours tool_choice/json_schema (family-*.json)
    if want("tool_choice"):
        rows.append(cap.write_case("tool_choice_required", Request(model=honouring, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=400, tool_choice=ToolChoice(mode="required"))), stream=False,
            description="Bedrock over the Chat Completions wire: tool_choice required honoured (deepseek.v3.2); gpt-oss and gemma ignore it → per-model refusal cases", expect_lm15=CALL_OK, evidence_note="compat forced_tool_choice=send with model_overrides", force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case("response_format_json_schema",
            Request(model=honouring, messages=(Message.user("Where is the Eiffel Tower?"),),
                    config=Config(max_tokens=400, response_format={"type": "json_schema", "name": "place", "strict": True,
                        "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}}, "required": ["city", "country"], "additionalProperties": False}})),
            stream=False, description="Bedrock over the Chat Completions wire: response_format json_schema honoured (deepseek.v3.2); gpt-oss ignores it → per-model refusal case", expect_lm15=TEXT_OK, evidence_note="compat json_schema=send with model_overrides", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case("system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=300)), stream=False,
            description="Bedrock over the Chat Completions wire: role system", expect_lm15=TEXT_OK, evidence_note="compat instruction_role cell", force=force))
    if want("user_id"):
        rows.append(cap.write_case("user_id", Request(model=model, messages=SAY, config=Config(max_tokens=300, user_id="lm15-case-user")), stream=False,
            description="Bedrock over the Chat Completions wire: Config.user_id → user", expect_lm15=TEXT_OK, evidence_note="compat user_field cell", force=force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    req = Request(model=model, messages=SAY, config=Config(max_tokens=10))
    if want("model_ids"):
        for mid in ("anthropic.claude-haiku-4-5", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "anthropic.claude-sonnet-5", "amazon.nova-micro-v1:0", "us.amazon.nova-micro-v1:0"):
            rows.append(cap.probe(f"model-id-{mid.replace(':', '_').replace('.', '-')}", Request(model=mid, messages=SAY, config=Config(max_tokens=10))))
    if want("models"):
        rows.append(cap.models_probe())
    if want("errors"):
        rows.append(cap.probe("error-invalid-signature", req, model_key=AwsCredentials("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY")))
        rows.append(cap.probe("error-model-not-found", Request(model="lm15.no-such-model-v1:0", messages=SAY, config=Config(max_tokens=10))))
        rows.append(cap.probe("error-bad-param", raw_body={"model": model, "messages": [{"role": "user", "content": "Say ok."}], "max_completion_tokens": -1}))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("invalid-signature", "model-not-found", "bad-param"))
