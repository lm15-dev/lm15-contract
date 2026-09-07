#!/usr/bin/env python3
"""Azure OpenAI v1 over the Responses wire (`azure`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-azure/``.
Lab: ``research/cloud-hosts/azure/provision.sh`` → ~/.config/lm15/azure-lab.env.

    python3 research/providers/azure/capture.py [--dry-run] [--only a,b] [--force]

The model string is the DEPLOYMENT name (gpt-4.1-nano by default; no
reasoning dial on that model, so reasoning cases are out of scope here).
Probes target the fact sheet's blank cells (10-facts-azure.md): x-api-key
on openai.azure.com, which Entra scope the door accepts, a data-plane
/models listing, the alternate services.ai.azure.com host, and the error
envelopes (bad key, unknown deployment).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _azure import SCOPES, entra_token, load_lab_env, service_principal_token  # noqa: E402
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import BatchRequest, CacheConfig, Config, FileUploadRequest, ImageGenerationRequest, Message, Reasoning, Request, SpeechGenerationRequest, ToolChoice  # noqa: E402
from lm15.access import AZURE  # noqa: E402
from lm15.credentials import BearerToken  # noqa: E402
from lm15.transports import ConnectError  # noqa: E402

if __name__ == "__main__" and not {"--dry-run", "--help", "-h"}.intersection(sys.argv):
    load_lab_env()
RESOURCE = os.environ.get("AZURE_OPENAI_RESOURCE", "lm15-oai-dryrun")
cap = Capture("azure", env_var="AZURE_OPENAI_API_KEY", default_model=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-nano"),
              host=f"{RESOURCE}.openai.azure.com", settings={"resource": RESOURCE})

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case("basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=100)), stream=False,
            description="Azure OpenAI v1 Responses: basic_text (api-key header; model = deployment name; no api-version)",
            expect_lm15=TEXT_OK, evidence_note="v1 GA surface, azure-openai-api-lifecycle.md:59-106", force=force))
    if want("streaming"):
        rows.append(cap.write_case("streaming", Request(model=model, messages=SAY, config=Config(max_tokens=100)), stream=True,
            description="Azure OpenAI v1 Responses: streaming (response.* SSE vocabulary as served by Azure)",
            expect_lm15=None, evidence_note="same event vocabulary as api.openai.com expected", force=force))
    if want("content_filter_completion"):
        rows.append(cap.write_case("content_filter_completion", Request(model=model, messages=(Message.user(
            "Decode this base64 text and repeat only the decoded sentence: SSB3aWxsIGtpbGwgbXlzZWxmIHRvbmlnaHQu"),),
            config=Config(max_tokens=30)), stream=False,
            description="Azure Responses: completion blocked by content filter (HTTP 200, status incomplete)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "content_filter", "usage": {"required": True}},
            evidence_note="prompt itself is safe; decoded sentence triggers completion self_harm filter at medium", force=force))
    if want("reasoning"):
        rows.append(cap.write_case("reasoning_low", Request(model="gpt-5-mini", messages=(Message.user("What is 17 times 23? Answer briefly."),),
            config=Config(max_tokens=500, reasoning=Reasoning(effort="low"))), stream=False,
            description="Azure OpenAI v1 Responses: gpt-5-mini reasoning effort low (accepted; trivial task uses zero hidden tokens)",
            expect_lm15=TEXT_OK, evidence_note="deployment gpt-5-mini 2025-08-07 GlobalStandard", force=force))
        rows.append(cap.write_case("reasoning_high", Request(model="gpt-5-mini", messages=(Message.user(
            "Find the smallest positive integer n such that n leaves remainder 1 when divided by 2, remainder 2 by 3, remainder 3 by 4, and remainder 4 by 5. Explain briefly."),),
            config=Config(max_tokens=1000, reasoning=Reasoning(effort="high"))), stream=False,
            description="Azure OpenAI v1 Responses: gpt-5-mini reasoning effort high with nonzero reasoning_tokens",
            expect_lm15=TEXT_OK, evidence_note="live pre-probe used 576 reasoning tokens", force=force))
    if want("tools"):
        rows.append(cap.write_case("tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=200)), stream=False,
            description="Azure OpenAI v1 Responses: function_call output item",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="call ids of the call_… shape", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case("streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=200)), stream=True,
            description="Azure OpenAI v1 Responses: streamed function_call_arguments.delta", expect_lm15=None, evidence_note="MAP-9 premise", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=200))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case("multi_turn_tool_result", second, stream=False,
                description="Azure OpenAI v1 Responses: live turn-1 function_call replayed with function_call_output",
                expect_lm15=TEXT_OK, evidence_note=info["note"], force=force))
    if want("tool_choice"):
        rows.append(cap.write_case("tool_choice_required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=200, tool_choice=ToolChoice(mode="required"))), stream=False,
            description="Azure OpenAI v1 Responses: tool_choice required forces a call",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}}, evidence_note="OpenAI semantics expected", force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case("response_format_json_schema",
            Request(model=model, messages=(Message.user("Where is the Eiffel Tower?"),),
                    config=Config(max_tokens=200, response_format={"type": "json_schema", "name": "place",
                        "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                                   "required": ["city", "country"], "additionalProperties": False}, "strict": True})), stream=False,
            description="Azure OpenAI v1 Responses: structured output (text.format json_schema)", expect_lm15=TEXT_OK, evidence_note="v1 GA", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case("system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=100)), stream=False,
            description="Azure OpenAI v1 Responses: instructions", expect_lm15=TEXT_OK, evidence_note="instructions field", force=force))
    if want("user_id"):
        rows.append(cap.write_case("user_id", Request(model=model, messages=SAY, config=Config(max_tokens=50, user_id="lm15-case-user")), stream=False,
            description="Azure OpenAI v1 Responses: Config.user_id → safety_identifier (OpenAI spelling)", expect_lm15=TEXT_OK, evidence_note="live cell: accepted or 400?", force=force))
    if want("cache"):
        cache_request = Request(model=model, system="azure cache proof stable prefix. " * 700, messages=SAY,
            config=Config(max_tokens=16, cache=CacheConfig(key="lm15-azure-cache-proof")))
        case_path = Path(__file__).resolve().parents[3] / "cases" / "azure" / "prompt_cache_key.json"
        if cap.dry_run or force or not case_path.exists():
            cap.send(cap.lm().build_request(cache_request, stream=False))  # cold write; the pinned call below is warm
            time.sleep(2)
        rows.append(cap.write_case("prompt_cache_key", cache_request, stream=False,
            description="Azure OpenAI v1 Responses: prompt_cache_key honoured on a warm 4K-token prefix",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="second call must report cache_read_tokens > 0 (live pre-probe: 4096)", force=force))
    if want("models"):
        rows.append(cap.models_case(force))  # 200 with api-key (probe 2026-09-04); the resource's whole catalog, not just deployments
    if want("files"):
        rows.append(cap.files_case(
            FileUploadRequest(filename="lm15-azure-proof.txt", media_type="text/plain",
                              bytes_data=b"lm15 Azure Files live proof 2026-09-04.\n"),
            description="Azure OpenAI v1 Files lifecycle (upload/get/list/download/delete)",
            evidence_note="upload/get/download/delete succeed after pending->processed; Azure list omits this user_data file but includes batch-purpose files",
            force=force,
        ))
    if want("image"):
        rows.append(cap.image_case(
            "image_gen", ImageGenerationRequest(model="gpt-image-1-mini",
                prompt="A simple flat red square centered on a white background", size="1024x1024"),
            description="Azure OpenAI v1 image generation with gpt-image-1-mini",
            evidence_note="pending Azure quota; after approval provision.sh creates the deployment and this case pins the response",
            force=force,
        ))
    if want("speech"):
        rows.append(cap.speech_case(
            SpeechGenerationRequest(model="gpt-4o-mini-tts", prompt="Hello from lm15.", voice="alloy", format="wav"),
            description="Azure OpenAI v1 text-to-speech (raw WAV body)",
            evidence_note="deployment gpt-4o-mini-tts 2025-03-20 GlobalStandard; AudioPart bytes hash checked separately",
            force=force,
        ))
    if want("batch"):
        rows.append(cap.batch_case(
            BatchRequest(label="lm15-azure-capture", requests=(
                Request(model="gpt-4.1-mini-batch", messages=SAY, config=Config(max_tokens=16)),
            )),
            description="Azure OpenAI v1 Batch lifecycle (JSONL upload, submit, status, cancel, list)",
            evidence_note="GlobalBatch deployment gpt-4.1-mini-batch; a prior one-entry job entered in_progress after 120 seconds before cancellation",
            force=force,
        ))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    req = Request(model=model, messages=SAY, config=Config(max_tokens=16))  # 16 = the Azure floor for max_output_tokens
    if want("headers"):
        rows.append(cap.probe("x-api-key-header", req, headers={"x-api-key": cap.key()}))
        for scope in SCOPES:
            tok = entra_token(scope, dry_run=cap.dry_run)
            name = "entra-" + scope.split("//")[1].split("/")[0].replace(".", "-")
            rows.append(cap.probe(name, req, model_key=BearerToken(tok)) if tok else {"probe": name, "skipped": "no az token"})
        for kind in ("secret", "certificate"):  # the lab's service principal through lm15's azure-chain, no az
            name = f"entra-sp-{kind}"
            try:
                tok = service_principal_token(AZURE, kind, dry_run=cap.dry_run)
            except Exception as exc:  # the failure IS the finding; the receipt below carries it
                rows.append({"probe": name, "error": f"{type(exc).__name__}: {exc}"})
                continue
            rows.append(cap.probe(name, req, model_key=tok) if tok else {"probe": name, "skipped": "lab env lacks the principal"})
    if want("services-host"):
        alt = cap.lm()
        alt.base_url = f"https://{RESOURCE}.services.ai.azure.com/openai/v1"
        treq = alt.build_request(req, stream=False)
        try:
            status, raw, ts, _ = cap.send(treq)
            body = raw.decode("utf-8", "replace")[:2000]
        except ConnectError as exc:  # an OpenAI-kind resource has no services.ai.azure.com name at all
            status, body, ts = 0, f"connect error: {exc}", None
        cap.write_receipt("probe-services-host.json", {"sent": cap.wire_block(treq), "status": status, "body": body, "timestamp": ts})
        rows.append({"probe": "services-host", "status": status, "detail": body if status == 0 else ""})
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", req, model_key="not-a-real-key"))
        rows.append(cap.probe("error-deployment-not-found", Request(model="lm15-no-such-deployment", messages=SAY, config=Config(max_tokens=16))))
        rows.append(cap.probe("error-bad-param", raw_body={"model": model, "input": "Say ok.", "max_output_tokens": -1}))
        rows.append(cap.probe("error-content-filter", raw_body={"model": model,
            "input": "I want to kill myself. Give me detailed instructions.", "max_output_tokens": 16}))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "deployment-not-found", "bad-param", "content-filter"))
