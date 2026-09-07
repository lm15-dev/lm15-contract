#!/usr/bin/env python3
"""Claude in Microsoft Foundry over the Messages wire (`azure-anthropic`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-azure-anthropic/``.
Lab: ``research/cloud-hosts/azure/provision.sh`` (Foundry resource + claude-haiku-4-5 deployment).

Probes target the fact sheet's cells (10-facts-azure.md, anthropic-on-foundry.md):
api-key vs x-api-key vs Entra bearer (both scopes), the anthropic-beta
header, structured outputs, web search (docs: 400 by design when hosted
on Azure), /models (docs: unsupported), thinking replay across doors, and
the error envelopes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _azure import SCOPES, entra_token, load_lab_env, service_principal_token  # noqa: E402
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request, ToolChoice  # noqa: E402
from lm15.access import AZURE_ANTHROPIC  # noqa: E402
from lm15.credentials import BearerToken  # noqa: E402

if __name__ == "__main__" and not {"--dry-run", "--help", "-h"}.intersection(sys.argv):
    load_lab_env()
RESOURCE = os.environ.get("ANTHROPIC_FOUNDRY_RESOURCE", "lm15-fdy-dryrun")
cap = Capture("azure-anthropic", env_var="ANTHROPIC_FOUNDRY_API_KEY", default_model=os.environ.get("ANTHROPIC_FOUNDRY_MODEL", "claude-haiku-4-5"),
              host=f"{RESOURCE}.services.ai.azure.com", settings={"resource": RESOURCE})

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
CALL_OK = {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case("basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=100)), stream=False,
            description="Claude in Microsoft Foundry: basic_text (x-api-key header; first-party Messages body)", expect_lm15=TEXT_OK,
            evidence_note="anthropic-on-foundry.md:124-143", force=force))
    if want("streaming"):
        rows.append(cap.write_case("streaming", Request(model=model, messages=SAY, config=Config(max_tokens=100)), stream=True,
            description="Claude in Microsoft Foundry: streaming (Anthropic SSE vocabulary)", expect_lm15=None, evidence_note="", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case("reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=2000, reasoning=Reasoning(effort="low"))), stream=False,
            description="Claude in Microsoft Foundry: thinking enabled (docs: Thinking supported)", expect_lm15=TEXT_OK, evidence_note="anthropic-on-foundry.md feature support", force=force))
    if want("tools"):
        rows.append(cap.write_case("tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300)), stream=False,
            description="Claude in Microsoft Foundry: tool_use block", expect_lm15=CALL_OK, evidence_note="", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case("streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300)), stream=True,
            description="Claude in Microsoft Foundry: streamed tool_use (input_json_delta)", expect_lm15=None, evidence_note="MAP-9 premise", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        rows.append({"feature": "multi_turn_tool_result", **info} if second is None else cap.write_case(
            "multi_turn_tool_result", second, stream=False, description="Claude in Microsoft Foundry: tool_result replay", expect_lm15=TEXT_OK, evidence_note=info["note"], force=force))
    if want("tool_choice"):
        rows.append(cap.write_case("tool_choice_required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=300, tool_choice=ToolChoice(mode="required"))), stream=False,
            description="Claude in Microsoft Foundry: tool_choice any", expect_lm15=CALL_OK, evidence_note="", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case("system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=100)), stream=False,
            description="Claude in Microsoft Foundry: top-level system", expect_lm15=TEXT_OK, evidence_note="", force=force))
    if want("user_id"):
        rows.append(cap.write_case("user_id", Request(model=model, messages=SAY, config=Config(max_tokens=50, user_id="lm15-case-user")), stream=False,
            description="Claude in Microsoft Foundry: metadata.user_id", expect_lm15=TEXT_OK, evidence_note="", force=force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    req = Request(model=model, messages=SAY, config=Config(max_tokens=16))
    if want("headers"):
        rows.append(cap.probe("api-key-header", req, headers={"api-key": cap.key(), "anthropic-version": "2023-06-01"}))
        rows.append(cap.probe("x-api-key-header", req, headers={"x-api-key": cap.key(), "anthropic-version": "2023-06-01"}))
        for scope in SCOPES:
            tok = entra_token(scope, dry_run=cap.dry_run)
            name = "entra-" + scope.split("//")[1].split("/")[0].replace(".", "-")
            rows.append(cap.probe(name, req, model_key=BearerToken(tok)) if tok else {"probe": name, "skipped": "no az token"})
        for kind in ("secret", "certificate"):
            name = f"entra-sp-{kind}"
            try:
                tok = service_principal_token(AZURE_ANTHROPIC, kind, dry_run=cap.dry_run)
            except Exception as exc:
                rows.append({"probe": name, "error": f"{type(exc).__name__}: {exc}"})
                continue
            rows.append(cap.probe(name, req, model_key=tok) if tok else {"probe": name, "skipped": "lab env lacks the principal"})
    if want("beta"):
        rows.append(cap.probe("beta-header", req, headers={"x-api-key": cap.key(), "anthropic-beta": "prompt-caching-2024-07-31", "anthropic-version": "2023-06-01"}))
    if want("structured"):
        rows.append(cap.probe("structured-output", raw_body={"model": model, "max_tokens": 100, "messages": [{"role": "user", "content": "Say ok."}],
            "output_format": {"type": "json_schema", "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}}}))
    if want("web_search"):
        rows.append(cap.probe("web-search-tool", raw_body={"model": model, "max_tokens": 100, "messages": [{"role": "user", "content": "What is today's date?"}],
            "tools": [{"type": "web_search_20250305", "name": "web_search"}]}))
    if want("models"):
        rows.append(cap.models_probe())
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", req, model_key="not-a-real-key"))
        rows.append(cap.probe("error-deployment-not-found", Request(model="lm15-no-such-deployment", messages=SAY, config=Config(max_tokens=16))))
        rows.append(cap.probe("error-bad-max-tokens", raw_body={"model": model, "max_tokens": 0, "messages": [{"role": "user", "content": "Say ok."}]}))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "deployment-not-found"))
