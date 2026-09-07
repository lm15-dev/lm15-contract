#!/usr/bin/env python3
"""Claude in Amazon Bedrock over the Messages wire (`bedrock-anthropic`, the
`bedrock-mantle` door) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-bedrock-anthropic/``.

    AWS_REGION=us-east-1 python3 research/providers/bedrock-anthropic/capture.py [--dry-run] [--only a,b] [--force]

Credentials: lm15's aws-chain; SigV4 service `bedrock-mantle`; every case
pinned re-signed with the fixed test pair.  Model default
``anthropic.claude-haiku-4-5`` (the door's `anthropic.` namespace;
anthropic-on-bedrock.md:327-338).  Needs the account's Anthropic use-case
form and the model agreement (403 permission_error otherwise, live
2026-09-03).  Probes: the fact sheet's cells — anthropic-beta header,
structured outputs, other anthropic-version values, pre-4.7 model ids,
/models, and the error envelopes.
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

cap = Capture("bedrock-anthropic", env_var="AWS_BEARER_TOKEN_BEDROCK", default_model=os.environ.get("BEDROCK_ANTHROPIC_MODEL", "anthropic.claude-haiku-4-5"),
              host=f"bedrock-mantle.{REGION}.api.aws", settings={"region": REGION})
cap.prepare = cap.aws_fixture

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
CALL_OK = {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case("basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=100)), stream=False,
            description="Claude in Amazon Bedrock (mantle): basic_text — first-party Messages body, SigV4 service bedrock-mantle", expect_lm15=TEXT_OK,
            evidence_note="anthropic-on-bedrock.md:138-160", force=force))
    if want("streaming"):
        rows.append(cap.write_case("streaming", Request(model=model, messages=SAY, config=Config(max_tokens=100)), stream=True,
            description="Claude in Amazon Bedrock (mantle): streaming — plain SSE, Anthropic event vocabulary", expect_lm15=None, evidence_note="docs: 'standard SSE streaming'", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case("reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=2000, reasoning=Reasoning(effort="low"))), stream=False,
            description="Claude in Amazon Bedrock (mantle): thinking enabled (docs: Thinking supported)", expect_lm15=TEXT_OK, evidence_note="", force=force))
    if want("tools"):
        rows.append(cap.write_case("tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300)), stream=False,
            description="Claude in Amazon Bedrock (mantle): tool_use block", expect_lm15=CALL_OK, evidence_note="", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case("streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300)), stream=True,
            description="Claude in Amazon Bedrock (mantle): streamed tool_use (input_json_delta)", expect_lm15=None, evidence_note="MAP-9 premise", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        rows.append({"feature": "multi_turn_tool_result", **info} if second is None else cap.write_case(
            "multi_turn_tool_result", second, stream=False, description="Claude in Amazon Bedrock (mantle): tool_result replay", expect_lm15=TEXT_OK, evidence_note=info["note"], force=force))
    if want("tool_choice"):
        rows.append(cap.write_case("tool_choice_required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=300, tool_choice=ToolChoice(mode="required"))), stream=False,
            description="Claude in Amazon Bedrock (mantle): tool_choice any", expect_lm15=CALL_OK, evidence_note="", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case("system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=100)), stream=False,
            description="Claude in Amazon Bedrock (mantle): top-level system", expect_lm15=TEXT_OK, evidence_note="", force=force))
    if want("user_id"):
        rows.append(cap.write_case("user_id", Request(model=model, messages=SAY, config=Config(max_tokens=50, user_id="lm15-case-user")), stream=False,
            description="Claude in Amazon Bedrock (mantle): metadata.user_id", expect_lm15=TEXT_OK, evidence_note="", force=force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    req = Request(model=model, messages=SAY, config=Config(max_tokens=10))
    base = {"model": model, "max_tokens": 100, "messages": [{"role": "user", "content": "Say ok."}]}
    if want("beta"):
        rows.append(cap.probe("beta-header", req, headers={"anthropic-beta": "prompt-caching-2024-07-31"}))
    if want("structured"):
        rows.append(cap.probe("structured-output", raw_body={**base, "output_format": {"type": "json_schema", "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}}}))
    if want("version"):
        rows.append(cap.probe("version-other", req, headers={"anthropic-version": "2024-01-01"}))
    if want("model_ids"):
        for mid in ("anthropic.claude-sonnet-4-5", "claude-haiku-4-5", "us.anthropic.claude-haiku-4-5-20251001-v1:0", "anthropic.claude-haiku-4-5-20251001-v1:0"):
            rows.append(cap.probe(f"model-id-{mid.replace(':', '_').replace('.', '-')}", Request(model=mid, messages=SAY, config=Config(max_tokens=10))))
    if want("web_search"):
        rows.append(cap.probe("web-search-tool", raw_body={**base, "messages": [{"role": "user", "content": "What is today's date?"}], "tools": [{"type": "web_search_20250305", "name": "web_search"}]}))
    if want("models"):
        rows.append(cap.models_probe())
    if want("errors"):
        rows.append(cap.probe("error-invalid-signature", req, model_key=AwsCredentials("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY")))
        rows.append(cap.probe("error-model-not-found", Request(model="anthropic.claude-no-such-model", messages=SAY, config=Config(max_tokens=10))))
        # The account gate fires before parameter validation (2026-09-04:
        # max_tokens=0 answered the same 403 permission_error as everything
        # else), so bad-max-tokens is only evidence once Claude is open here.
        rows.append(cap.probe("error-bad-max-tokens", raw_body={**base, "max_tokens": 0}))
        rows.append(cap.probe("error-model-gated", req))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("invalid-signature", "model-not-found", "model-gated"))  # + "bad-max-tokens" once the gate is open (its receipt is the gate today)
