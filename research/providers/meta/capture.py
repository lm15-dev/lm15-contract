#!/usr/bin/env python3
"""Meta Model API over the Responses wire (`meta`) — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-meta/``.

    META_API_KEY=… python3 research/providers/meta/capture.py [--dry-run] [--only a,b] [--force]

Model default ``muse-spark-1.3`` (models.md: "recommended for new work";
Standard tier — prompts are never used for training).  Image cases use
``muse-image-1.0``.  Probes target the dossier's open decisions: reasoning
``none`` (docs: HTTP 400), ``logprobs`` (docs: 400), effort words outside
the documented set, the prompt-cache breakpoint field on a non-OpenAI
server, reasoning replay by ``id`` alone under the default ``store: true``,
the ``phase: "commentary"`` rule on replayed assistant text before a
function_call, the ``web_search`` built-in tool, and the error envelope.
"""
from __future__ import annotations

import base64
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402
from lm15 import BuiltinTool, CacheConfig, Config, FileUploadRequest, ImageGenerationRequest, ImagePart, Message, Reasoning, Request, ToolChoice  # noqa: E402
from lm15.types import TextPart, ThinkingPart, ToolCallPart  # noqa: E402

cap = Capture("meta", env_var="META_API_KEY", default_model="muse-spark-1.3", host="api.meta.ai")

IMAGE_MODEL = "muse-image-1.0"
SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
LOW = Reasoning(effort="low")


def _png(width: int = 64, height: int = 64, rgb: tuple[int, int, int] = (220, 30, 30)) -> bytes:
    """A solid-colour PNG, built without a library (the edit case's input)."""
    raw = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    text_ok = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=3000)), stream=False,
            description="Meta Muse Spark basic_text (Responses wire; the model reasons by default — a reasoning item with no visible content precedes the message; "
                        "the first capture with max_output_tokens 600 came back status incomplete with output [] after 597 reasoning tokens)",
            expect_lm15=text_ok,
            evidence_note="output[] shape: reasoning item (summary [], no encrypted_content without include) then message; usage carries output_tokens_details.reasoning_tokens", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=model, messages=SAY, config=Config(max_tokens=3000)), stream=True,
            description="Meta Muse Spark streaming (Responses SSE: response.created … output_text.delta … response.completed, [DONE]; no reasoning_text events)",
            expect_lm15=None, evidence_note="protocols--responses.md § Streaming: raw reasoning is never streamed as text", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark reasoning.effort=low (guide--reasoning.md: none|minimal|low|medium|high|xhigh; none is refused)",
            expect_lm15=text_ok, evidence_note="reasoning_tokens expected lower than basic_text", force=force))
    if want("reasoning_summary"):
        rows.append(cap.write_case(
            "reasoning_summary", Request(model=model, messages=(Message.user("What is 17 times 23? Think briefly, then answer."),),
                                         config=Config(max_tokens=800, reasoning=Reasoning(effort="low", summary="auto"))), stream=False,
            description="Meta Muse Spark reasoning.summary=auto — the only visible form of the chain of thought (guide--reasoning.md § Summaries; not guaranteed)",
            expect_lm15=text_ok, evidence_note="summary[] on the reasoning item may be empty; treat as optional", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark function call (Responses function_call item; is a phase:commentary message emitted before it?)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="call_id shape and any commentary-phase message are the findings", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW)), stream=True,
            description="Meta Muse Spark streamed function call (response.function_call_arguments.delta / .done)",
            expect_lm15=None, evidence_note="MAP-9 premise for this provider", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600, reasoning=LOW))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description="Meta Muse Spark tool result turn: the live turn-1 output (reasoning item + function_call) replayed with function_call_output under the default store:true",
                expect_lm15=text_ok,
                evidence_note=info["note"].replace("as reasoning_content", "as reasoning input items (id + summary [])"), force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case(
            "response_format_json_schema",
            Request(model=model, messages=(Message.user("Where is the Eiffel Tower?"),),
                    config=Config(max_tokens=600, reasoning=LOW,
                                  response_format={"type": "json_schema", "name": "place",
                                                   "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
                                                              "required": ["city", "country"], "additionalProperties": False},
                                                   "strict": True})), stream=False,
            description="Meta Muse Spark structured output (Responses text.format json_schema — guide--structured-output.md)",
            expect_lm15=text_ok, evidence_note="text.format, not response_format, on this wire", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=model, system="You answer in exactly two words.", messages=SAY, config=Config(max_tokens=600, reasoning=LOW)), stream=False,
            description="Meta Muse Spark system prompt as top-level `instructions` (developer-level; protocols--responses.md § Setting instructions)",
            expect_lm15=text_ok, evidence_note="instructions field", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=model, messages=SAY, config=Config(max_tokens=600, reasoning=LOW, user_id="lm15-case-user")), stream=False,
            description="Meta Muse Spark end-user attribution: Config.user_id rides `safety_identifier` (protocols--responses.md § Safety identifiers)",
            expect_lm15=text_ok, evidence_note="safety_identifier ≤ 64 chars", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    if want("image_gen"):
        rows.append(cap.image_case(
            "image_gen", ImageGenerationRequest(model=IMAGE_MODEL, prompt="A simple flat red circle centered on a white background", size="1024x1024"),
            description="Meta Muse Image generation (POST /images/generations; b64_json default; output_format echoes webp when omitted — images--schemas.md)",
            evidence_note="$0.01 per image (pricing-rate-limits.md); usage carries token counts for reference only", force=force))
    if want("image_edit"):
        rows.append(cap.image_case(
            "image_edit", ImageGenerationRequest(model=IMAGE_MODEL, prompt="Add one small solid blue square in the bottom-right corner. Keep everything else exactly the same.",
                                                 images=(ImagePart(media_type="image/png", data=base64.b64encode(_png()).decode("ascii")),)),
            description="Meta Muse Image edit (POST /images/edits multipart image[] — the OpenAI SDK shape; images--edit.md)",
            evidence_note="input image is a 64x64 solid red PNG built by the capture script", force=force))
    if want("files"):
        rows.append(cap.files_case(
            FileUploadRequest(filename="sample.txt", media_type="text/plain",
                              bytes_data=b"The quick brown fox jumps over the lazy dog.\nlm15 files capture 2026-09-03.\n"),
            description="Meta Files lifecycle (POST/GET/LIST/DELETE /files; purpose user_data — files--upload.md; download of user_data is the finding)",
            evidence_note="files--schemas.md: purpose user_data|batch only; status field deprecated", force=force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    low = Config(max_tokens=300, reasoning=LOW)
    if want("reasoning"):
        rows.append(cap.probe("error-reasoning-none", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=Reasoning(effort="off")))))
        rows.append(cap.probe("effort-minimal", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=Reasoning(effort="minimal")))))
        rows.append(cap.probe("effort-xhigh", Request(model=model, messages=SAY, config=Config(max_tokens=2000, reasoning=Reasoning(effort="xhigh")))))
        rows.append(cap.probe("error-bad-effort", raw_body={"model": model, "input": "Say ok.", "max_output_tokens": 100, "reasoning": {"effort": "bogus"}}))
    if want("logprobs"):
        rows.append(cap.probe("error-logprobs", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=LOW, logprobs=2))))
    if want("cache"):
        # cache_control="openai": prompt_cache_key + prompt_cache_retention=24h are documented (guide--prompt-caching.md);
        # a prompt_cache_breakpoint mark on a non-gpt-5.6 model is not — loud or silent?
        rows.append(cap.probe("cache-key-retention", Request(model=model, messages=SAY, config=Config(max_tokens=300, reasoning=LOW, cache=CacheConfig(key="lm15-probe", retention="long")))))
        rows.append(cap.probe("cache-breakpoint", Request(model=model, messages=(Message.user("Stable prefix. " * 40), *SAY),
                                                          config=Config(max_tokens=300, reasoning=LOW, cache=CacheConfig(prefix_until_index=0)))))
        # The undocumented mark itself, by hand (the preset no longer sends it): loud or silent?
        rows.append(cap.probe("cache-breakpoint-mark-raw", raw_body={"model": model, "max_output_tokens": 300, "reasoning": {"effort": "low"},
                                                                     "input": [{"role": "user", "content": [{"type": "input_text", "text": "Stable prefix. " * 40, "prompt_cache_breakpoint": {"mode": "explicit"}}]},
                                                                               {"role": "user", "content": [{"type": "input_text", "text": "Say ok."}]}]}))
    if want("replay"):
        # Two-turn text replay without a tool: turn 1 → turn 2 sends the reasoning item back by id (default store:true).
        first = Request(model=model, messages=(Message.user("Pick a colour and say only its name."),), config=low)
        adapter = cap.lm()
        status, raw, ts, _ = cap.send(adapter.build_request(first, stream=False))
        if not cap.dry_run and status == 200:
            from lm15.providers.base import HttpResponse
            msg = adapter.parse_response(first, HttpResponse(status, "OK", [], raw)).message
            second = Request(model=model, messages=(*first.messages, msg, Message.user("Say the same colour again.")), config=low)
            rows.append(cap.probe("reasoning-id-only-replay", second))
            rows.append(cap.probe("reasoning-id-only-replay-store-false",
                                  Request(model=model, messages=second.messages, config=Config(max_tokens=300, reasoning=LOW, store=False))))
        # Truly stateless: turn 1 store:false WITHOUT include, then the id-only replay (docs: 400 "not found or has expired").
        unstored = Config(max_tokens=300, reasoning=LOW, store=False)
        first_unstored = Request(model=model, messages=first.messages, config=unstored)
        status, raw, ts, _ = cap.send(adapter.build_request(first_unstored, stream=False))
        if not cap.dry_run and status == 200:
            from lm15.providers.base import HttpResponse
            msg = adapter.parse_response(first_unstored, HttpResponse(status, "OK", [], raw)).message
            rows.append(cap.probe("reasoning-id-only-replay-unstored",
                                  Request(model=model, messages=(*first.messages, msg, Message.user("Say the same colour again.")), config=unstored)))
        # Encrypted replay: include via extensions (the OpenAI precedent, cases/openai/reasoning_encrypted.json), store:false.
        enc = Config(max_tokens=300, reasoning=LOW, store=False, extensions={"include": ["reasoning.encrypted_content"]})
        first_enc = Request(model=model, messages=first.messages, config=enc)
        status, raw, ts, _ = cap.send(adapter.build_request(first_enc, stream=False))
        if not cap.dry_run and status == 200:
            from lm15.providers.base import HttpResponse
            msg = adapter.parse_response(first_enc, HttpResponse(status, "OK", [], raw)).message
            has_enc = any(isinstance(p, ThinkingPart) and p.continuation and p.continuation[0].data.get("encrypted_content") for p in msg.parts)
            cap.write_receipt("NOTE-encrypted-replay.md", f"turn 1 with include: encrypted_content present on the reasoning item: {has_enc}\n")
            rows.append(cap.probe("reasoning-encrypted-replay",
                                  Request(model=model, messages=(*first.messages, msg, Message.user("Say the same colour again.")), config=enc)))
    if want("commentary"):
        # protocols--responses.md § Message phase: assistant text before a function_call must carry phase:"commentary" or the request is 400.
        # lm15 replays text + tool call as message + function_call with no phase — is the 400 real for a turn the server itself produced?
        turn1 = Message.assistant((TextPart(text="Let me check the weather first."), ToolCallPart(id="call_probe1", name=WEATHER.name, input={"city": "Paris"})))
        rows.append(cap.probe("commentary-text-before-call",
                              Request(model=model, messages=(*ASK_WEATHER, turn1, Message.tool("call_probe1", "Sunny, 22°C")), tools=(WEATHER,), config=low)))
        raw_ok = {"model": model, "max_output_tokens": 300, "reasoning": {"effort": "low"},
                  "tools": [{"type": "function", "name": WEATHER.name, "description": WEATHER.description, "parameters": WEATHER.parameters}],
                  "input": [{"role": "user", "content": [{"type": "input_text", "text": ASK_WEATHER[0].text}]},
                            {"type": "message", "role": "assistant", "phase": "commentary", "content": [{"type": "output_text", "text": "Let me check the weather first."}]},
                            {"type": "function_call", "call_id": "call_probe1", "name": WEATHER.name, "arguments": "{\"city\":\"Paris\"}"},
                            {"type": "function_call_output", "call_id": "call_probe1", "output": "Sunny, 22°C"}]}
        rows.append(cap.probe("commentary-text-before-call-tagged", raw_body=raw_ok))
    if want("web_search"):
        # Meta's schema enum is `web_search` | `web_search_2025_08_26` (responses--schemas.md); the `meta` preset maps the
        # canonical builtin to `web_search` (compat builtin_tools="verbatim").  The first pass sent OpenAI's `web_search_preview`
        # by accident and it answered 200 (probe-web-search-preview-spelling, raw); kept as the undocumented-spelling receipt.
        ask = (Message.user("In one sentence: what is today's date according to a web search?"),)
        rows.append(cap.probe("web-search-builtin", Request(model=model, messages=ask, tools=(BuiltinTool(name="web_search"),), config=Config(max_tokens=800, reasoning=LOW))))
        rows.append(cap.probe("web-search-preview-spelling", raw_body={"model": model, "max_output_tokens": 800, "reasoning": {"effort": "low"},
                                                                       "tools": [{"type": "web_search_preview"}],
                                                                       "input": [{"role": "user", "content": [{"type": "input_text", "text": ask[0].text}]}]}))
        # A canonical builtin Meta does not have goes out verbatim — loud or silent?
        rows.append(cap.probe("error-builtin-code-execution", Request(model=model, messages=(Message.user("Compute 2+2 with code."),),
                                                                       tools=(BuiltinTool(name="code_execution"),), config=Config(max_tokens=300, reasoning=LOW))))
    if want("tool_choice"):
        # Chat and Messages wires answer 400 for anything but auto (live 2026-09-03); the Responses wire?
        rows.append(cap.probe("tool-choice-required", Request(model=model, messages=SAY, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=LOW, tool_choice=ToolChoice(mode="required")))))
        rows.append(cap.probe("tool-choice-none", Request(model=model, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=LOW, tool_choice=ToolChoice(mode="none")))))
    if want("image_edit_key"):
        # The evidence for compat edit_image_field="indexed": OpenAI's `image[]` multipart key, as the `openai` preset sends it.
        from lm15 import OpenAILM
        from lm15.compat import OpenAIResponsesCompat
        lm = OpenAILM(api_key=cap.key(), compat=OpenAIResponsesCompat.preset("meta"), base_url="https://api.meta.ai/v1")
        array_lm = OpenAILM(api_key=cap.key(), compat=OpenAIResponsesCompat(edit_image_field="array"), base_url="https://api.meta.ai/v1")
        req = ImageGenerationRequest(model=IMAGE_MODEL, prompt="Add a blue square.", images=(ImagePart(media_type="image/png", data=base64.b64encode(_png()).decode("ascii")),))
        treq = array_lm._image_generate_request(req)
        status, raw, ts, _ = cap.send(treq)
        if not cap.dry_run:
            cap.write_receipt("probe-error-image-edit-array-key.json", {"sent": {**cap.wire_block(treq), "body_b64": "<multipart, image[] key>"}, "status": status,
                                                                         "body": raw.decode("utf-8", "replace"), "timestamp": ts})
        rows.append({"probe": "error-image-edit-array-key", "status": status, "summary": raw.decode("utf-8", "replace")[:140]})
    if want("sampling"):
        rows.append(cap.probe("error-top-p-zero", Request(model=model, messages=SAY, config=Config(max_tokens=100, reasoning=LOW, top_p=0.0))))
        rows.append(cap.probe("error-max-tokens-below-16", Request(model=model, messages=SAY, config=Config(max_tokens=8, reasoning=LOW))))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=model, messages=SAY, config=Config(max_tokens=100)), model_key="LLM|000000|invalid"))
        rows.append(cap.probe("error-model-not-found", Request(model="muse-nonexistent", messages=SAY, config=Config(max_tokens=100))))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "model-not-found", "reasoning-none", "logprobs", "bad-effort", "top-p-zero", "max-tokens-below-16"))
