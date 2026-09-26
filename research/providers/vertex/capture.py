#!/usr/bin/env python3
"""Gemini on Google Cloud (`vertex`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-vertex/``.
Project: ``lm15-vertex-live`` (created 2026-09-26; changes/2026-09-26-vertex-live.md).

    # the Google chain (gcloud auth application-default login), bearer cases:
    GOOGLE_CLOUD_PROJECT=lm15-vertex-live python3 research/providers/vertex/capture.py [--dry-run] [--only a,b] [--force]
    # a Vertex API key on the project door (x-goog-api-key, AUTH-10 amended 2026-09-26):
    VERTEX_API_KEY=... GOOGLE_CLOUD_PROJECT=lm15-vertex-live python3 research/providers/vertex/capture.py --auth key

Bearer cases pin ``credential: {"kind": "bearer_token", "value": "test-access-token-123"}``
(the real token is sent and never written).  Key cases pin the header as
``$VERTEX_API_KEY`` and the harness injects its own key.  The key never
comes from a file this script reads.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
AUTH = "key" if "--auth" in sys.argv and sys.argv[sys.argv.index("--auth") + 1] == "key" else "adc"
if "--auth" in sys.argv:  # consumed here; Capture.main parses the rest
    i = sys.argv.index("--auth")
    del sys.argv[i:i + 2]

from _capture import WEATHER, Capture  # noqa: E402
from lm15 import Config, Message, Reasoning, Request  # noqa: E402
from lm15.credentials import ApiKey  # noqa: E402

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "lm15-vertex-live")
cap = Capture("vertex", env_var="VERTEX_API_KEY", default_model="gemini-2.5-flash", change_slug="vertex-live",
              host="aiplatform.googleapis.com", settings={"project": PROJECT, "location": "global"})
if AUTH == "adc":
    cap.prepare = cap.bearer_fixture

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
CALL = {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}}
# gemini-2.5-flash thinks by default; the budget below leaves room for text.
BUDGET = Config(max_tokens=400)


def key_cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("api_key_basic_text"):
        rows.append(cap.write_case("api_key_basic_text", Request(model=model, messages=SAY, config=BUDGET), stream=False,
            description="Vertex project door with a Vertex API key: x-goog-api-key on the global host (AUTH-10, amended 2026-09-26)",
            expect_lm15=TEXT_OK, evidence_note="key bound to a service account; project and location stay in the path", force=force))
    if want("api_key_streaming"):
        rows.append(cap.write_case("api_key_streaming", Request(model=model, messages=SAY, config=BUDGET), stream=True,
            description="Vertex project door with a Vertex API key: streamGenerateContent?alt=sse",
            expect_lm15=None, evidence_note="same SSE framing as the bearer case", force=force))
    return rows


def adc_cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case("basic_text", Request(model=model, messages=SAY, config=BUDGET), stream=False,
            description="Vertex generateContent over the Google chain: bearer token, project/location in the path, model in the path",
            expect_lm15=TEXT_OK, evidence_note="token from lm15's gcp-chain (adc-file rung)", force=force))
    if want("streaming"):
        rows.append(cap.write_case("streaming", Request(model=model, messages=SAY, config=BUDGET), stream=True,
            description="Vertex streamGenerateContent?alt=sse", expect_lm15=None, evidence_note="SSE, usage on the last chunk", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case("system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=BUDGET),
            stream=False, description="Vertex: systemInstruction", expect_lm15=TEXT_OK, evidence_note="same field as the Gemini API", force=force))
    if want("tools"):
        rows.append(cap.write_case("tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=BUDGET), stream=False,
            description="Vertex: functionCall part", expect_lm15=CALL, evidence_note="Gemini function calling on Vertex", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case("streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=BUDGET), stream=True,
            description="Vertex: streamed functionCall", expect_lm15=None, evidence_note="whole call in one chunk", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=BUDGET)
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case("multi_turn_tool_result", second, stream=False,
                description="Vertex: live turn-1 functionCall (with its thought signature) replayed with functionResponse",
                expect_lm15=TEXT_OK, evidence_note=info["note"], force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case("response_format_json_schema",
            Request(model=model, messages=(Message.user("Where is the Eiffel Tower?"),),
                    config=Config(max_tokens=400, response_format={"type": "json_schema", "name": "place",
                        "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                                   "required": ["city", "country"]}})), stream=False,
            description="Vertex: structured output (responseMimeType + response schema field by MAP-16)",
            expect_lm15=TEXT_OK, evidence_note="MAP-16 field choice", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case("reasoning_low", Request(model=model, messages=(Message.user("What is 17 times 23? Answer briefly."),),
            config=Config(max_tokens=800, reasoning=Reasoning(effort="low"))), stream=False,
            description="Vertex: thinkingConfig from Reasoning(effort=low)", expect_lm15=TEXT_OK,
            evidence_note="thoughtsTokenCount reported in usageMetadata", force=force))
    if want("access_token_string"):
        # AUTH-2 amended 2026-09-26: on this door the key header comes first,
        # and a plain string with an access token's shape still travels as
        # bearer.  The real token is sent; the case pins a fixed ya29. string.
        saved = cap.fixture_credential
        cap.fixture_credential = ApiKey("ya29.lm15-test-access-token")
        try:
            rows.append(cap.write_case("access_token_string", Request(model=model, messages=SAY, config=BUDGET), stream=False,
                description="Vertex: a plain-string credential with an access token's shape (ya29.) goes as bearer, not x-goog-api-key",
                expect_lm15=TEXT_OK, evidence_note="AUTH-2 token-shape rule", force=force))
        finally:
            cap.fixture_credential = saved
    if want("regional_location"):
        saved = dict(cap.settings)
        cap.settings["location"] = "europe-west4"
        try:
            rows.append(cap.write_case("regional_location", Request(model=model, messages=SAY, config=BUDGET), stream=False,
                description="Vertex: a regional location renders {location}-aiplatform.googleapis.com and names the location in the path",
                expect_lm15=TEXT_OK, evidence_note="europe-west4 (vertex-locations.md:40-63)", force=force))
        finally:
            cap.settings = saved
    return rows


def adc_probes(model: str, want) -> list[dict]:
    rows = []
    if want("error-unauthenticated"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY),
                              headers={"Authorization": "Bearer ya29.not-a-real-token"}))
    if want("error-model-not-found"):
        rows.append(cap.probe("error-model-not-found", Request(model="gemini-0-does-not-exist", messages=SAY)))
    if want("error-permission-denied"):
        saved = dict(cap.settings)
        cap.settings["project"] = "lm15-no-access-000000"
        try:
            rows.append(cap.probe("error-permission-denied", Request(model=model, messages=SAY)))
        finally:
            cap.settings = saved
    return rows


if __name__ == "__main__":
    if AUTH == "key":
        cap.main(key_cases, lambda model, want: [])
    else:
        cap.main(adc_cases, adc_probes,
                 error_probes=("unauthenticated", "model-not-found", "permission-denied"))
