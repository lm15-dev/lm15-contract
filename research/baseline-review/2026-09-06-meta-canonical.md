# Independent canonical review — Meta's 34 draft goldens

Delegation: `70df6e9b-00f5-41af-8a56-7b67d8957019`  
Role: canonical contract reviewer  
Disposition: **submitted for parent review; not approval, acceptance, ratification, or authorization to freeze fixtures.**

## Scope and method

Reviewed all 14 files in `goldens/meta`, all 10 in `goldens/meta-chat`, and all 10 in `goldens/meta-anthropic`, against their corresponding case's canonical request (or endpoint-specific request) and **that case's pinned body**, not an arbitrary/latest body in its directory. The numbered findings below cover every file. All 34 currently say `source: scribe-draft`; implementation-derived provenance was not treated as evidence of canonical correctness.

Read `AUTHORITY.md`; `spec/types.md`, `spec/invariants.md`, `spec/vocabularies.md`; `../lm15-python/docs/mapping-rules.md` and `serde-rules.md`. For endpoint-specific comparison conventions and model-listing rules, also read the relevant portions of `harness/PROTOCOL.md`, `spec/SCOPE.md`, `changes/2026-08-31-list-models-provisional.md`, `changes/2026-08-31-list-models-harness.md`, and `../lm15-python/docs/model-hydration.md`. Read the Meta changes entry for context only: it explicitly remains a draft and cannot resolve the normative choices identified here.

Used only local reads and inline Python standard-library analysis (`json`, `pathlib`, `hashlib`, `base64`, `datetime`). No lm15 implementation import, shim, test suite, fixture alteration, credential/environment-file access, or network call. Independently compared text, response/model IDs, tool names/IDs/parsed arguments, reported counters, opaque continuation payloads, SSE frames, endpoint metadata, and image digests. Scripts' successful assertions only establish those explicit comparisons; they do not settle missing rules. Repository files and provenance were not changed. The only assigned output is this report.

**Excluded:** contemporaneous request-hash/wire-evidence sufficiency, live replay validity, provider onboarding/terms approval, and implementation conformance. In particular, this review does not cure the request-hash deficiency reported by the parent worker.

## Executive result

| Verdict | Count | Meaning |
|---|---:|---|
| **S — Supported mapped expectation** | 15 | The inspected canonical projection is supported by the written mapping/type rules and pinned content. Not approval of provenance or of the implementation. |
| **U — Substantively matches, exact oracle unresolved** | 16 | Content and telemetry match, but continuation attribution/emission and/or redaction rendering are not uniquely specified. Do not freeze the entire exact JSON on the strength of this review. |
| **D — Definite mapping discrepancy** | 2 | Both Responses streams drop an actual reasoning item, contrary to MAP-7.9. |
| **D/U — Semantic discrepancy plus specification gap** | 1 | Anthropic tool stream loses the redacted flag; the existing delta/assembly rules do not specify how to restore it. |
| Total | **34** | Every file individually addressed below. |

The important failures are **not usage arithmetic or stream termination**. All six draft traces have exactly one initial start and exactly one final end, all six materialized usage objects match the end usage, and the inspected raw usage maps correctly. The problems are missing/reduced reasoning state and insufficiently specified exact continuation semantics.

## Citation key and common rules

References below are to sections/rule numbers, not implementation functions as authority.

- **A:** `AUTHORITY.md`, “Canonical facts” precedence and “Evidence”: written normative rules outrank fixtures and implementations; canonical fixture changes require a rule citation. A green reference result is not an oracle.
- **P:** `mapping-rules.md` **MAP-1** (user-relevant text/thinking/client tools become parts); **MAP-2** (only an otherwise empty message gets an empty TextPart). `spec/types.md` §§TextPart, ThinkingPart, ToolCallPart, Message, Response; **INV-015**, **INV-023**, **INV-036**. Tool input is an object named `input`, not an `arguments` string.
- **F:** `spec/vocabularies.md`, “Forward-compatibility policy” **2–3** and §FinishReason. Chat `stop` maps to `stop`, `tool_calls` to `tool_call`; Anthropic `end_turn` maps to `stop`, `tool_use` to `tool_call`; a present client call forces `tool_call`. Completed Responses with no error, truncation, or client call naturally map to `stop`. Raw provider words remain provider data, not new canonical finish values.
- **Usg:** `spec/types.md` §Usage, especially “Counters are provider-verbatim”; **INV-029**; **MAP-3**, “Usage counters at the wire boundary”; **MAP-7.9** (exact reasoning count). Absent is not zero. Only missing total with both primaries present is synthesized, as input + output. Cache/reasoning are not added a second time.
- **Ser:** `serde-rules.md`, “Omission rule” **1–3**, paragraph “Required fields are always emitted,” and “Number rule” **1–4**; **INV-001–003**, **INV-007**. Each typed object cleans only itself; opaque state/schema/input/provider data remains unchanged. `0`, `false`, empty required text, and empty required input are not indiscriminately removed.
- **St:** **MAP-3** (one final merged end; bare terminators contribute no finish/usage), **MAP-4** (one initial start; synthesized request model for chat), **MAP-9**, “Assembly algorithm” **1–6** (slots, concatenation, kind order, continuation placement, finish, identity). `spec/types.md` §§Deltas, ToolCallDelta, ContinuationDelta, StreamStartEvent, StreamEndEvent. A message-level ContinuationDelta omits null `part_index`; content deltas emit integer `part_index` and required empty input.
- **R:** **MAP-7.1–3, 7–9**; `spec/types.md` §Reasoning. A request's reasoning intent does not authorize fabricating visible reasoning. Conversely, an actual Responses reasoning item with no summary becomes empty thinking with replay state, not nothing.
- **C:** `spec/types.md` §§ContinuationState, ContinuationDelta, ThinkingPart; **INV-005**; `spec/vocabularies.md`, “Open string namespaces”; **MAP-7.8**. These specify shape, opaque data and replay purpose, but do not completely specify attribution/emission on a provider bound to another provider's dialect. See Q1–Q3 below.
- **Req:** `spec/types.md` §§Request, Config, FunctionTool, ToolResultPart; **INV-013–014**, **INV-022–024**, **INV-030–031**, **INV-033**, **INV-050**; **MAP-8.4–6**. Structured output remains a text part holding the actual JSON string; the request schema is not a license to rewrite the response string.
- **Projection:** `spec/types.md` §Response and `harness/PROTOCOL.md` §§parse_response, replay_stream: canonical responses omit provider_data by default; event traces use event serde. Absence of Response.provider_data in these goldens is not a defect. It also means their raw-data retention cannot be proven from the golden alone.
- **Models:** `spec/SCOPE.md`, FROZEN/model listing; `changes/2026-08-31-list-models-provisional.md`, “Canonical mapping (normative for this surface),” promoted by `changes/2026-08-31-list-models-harness.md`; `model-hydration.md` §§Canonical JSON for ModelInfo, ModelInfo, ModelOrigin. `harness/PROTOCOL.md` §parse_models_response strips raw origin provider_data and then drops a default-only origin for golden comparison. This is a deliberate projection, not serde permission to discard raw metadata in the actual return value.
- **Files:** `spec/types.md` §§FileUploadRequest, FileInfo, FilePage; `spec/vocabularies.md` §FileReadiness. OpenAI-shaped `uploaded` becomes `pending`; epoch time normalizes to UTC; MIME/downloadability cannot be filled from unreported facts; cursor is absent when listing is complete.
- **Images:** `spec/types.md` §§ImageGenerationRequest, ImageGenerationResponse, ImagePart; **INV-010–012**, Usg and Ser; `harness/PROTOCOL.md` §generation_parse. Golden comparison strips provider_data and replaces media payload strings >=512 characters with `sha256:<hex>`; the actual canonical ImagePart must still contain valid base64, not this digest marker.

For all conversational files, required model/message/finish fields are present, message role is assistant, and no tool result is incorrectly inserted into response parts. All inspected canonical counters and delta indexes are JSON integers. No actual response logprob records were present: Responses lists are empty, chat records are null, and Anthropic does not report them. Omitting canonical logprobs is appropriate under §Response (never emit an empty parsed logprob list). No audio/cache-write counters were invented where the wire did not report them.

### Usage notation

Each conversational entry gives **I/O/T; Cr/Cw/R** = input/output/total; cache-read/cache-write/reasoning tokens. `—` means omitted/unreported, not zero. All numbers were compared to the corresponding raw fields, not inferred from text lengths or request budgets.

- Responses: `input_tokens`, `output_tokens`, `total_tokens`, `input_tokens_details.cached_tokens`, `output_tokens_details.reasoning_tokens`.
- Chat: `prompt_tokens`, `completion_tokens`, `total_tokens`, `prompt_tokens_details.cached_tokens`, `completion_tokens_details.reasoning_tokens`.
- Messages: `input_tokens`, `output_tokens`, synthesized total, `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens_details.thinking_tokens`.

The last is an explicit separately reported thinking count, not an estimate. On Messages, totals below intentionally exclude separately reported cache reads/writes. For example 48 + 108 = 156, not 653. Secondary counters do not alter either primary.

## Cross-cutting discrepancies and unresolved normative choices

### D1 — Both Responses streams drop a real reasoning item

Affected: `meta/streaming.json`, `meta/streaming_tool_call.json`.

Both pinned streams contain an `output_index: 0` reasoning item in `response.output_item.added`, `response.output_item.done`, and `response.completed.response.output`. It has a nonempty id and `summary: []`. Neither draft trace emits thinking or continuation for this item; neither materialized response includes it. Hiding it only in terminal provider_data is not canonical mapping.

**MAP-7.9 explicitly says an OpenAI reasoning item with no summary is an empty ThinkingPart carrying replay state, never dropped.** The case is expressly the Responses dialect; the same empty-summary shape correctly survives in the eight non-streaming Meta Responses goldens. MAP-9.4's fallback for a continuation-only slot produces TextPart, not ThinkingPart, so inserting only a continuation delta would not satisfy MAP-7.9 either.

Required semantic repair: retain an empty thinking part at the reasoning slot, carrying its actual id, alongside the existing text/tool parts. A compatible event representation can include an empty ThinkingDelta and a continuation delta for slot 0, without duplicating the item at each snapshot. The precise event emission point (added versus done), continuation attribution, and message-level response-id emission need an explicit cited rule; this review does not select a new exact event trace. Start/end/usage and the existing text/tool fragments should not be changed to conceal the failure.

### D2/Q3 — Messages tool stream loses `redacted: true`; redaction rendering is underspecified

Affected discrepancy: `meta-anthropic/streaming_tool_call.json`.

Raw blocks 0 and 1 are explicitly `redacted_thinking`. Their state blobs are preserved, and the draft emits `thinking` text `[redacted]` for each. But `canonical_response.message.parts[0]` and `[1]` omit `redacted`, hence deserialize to **false** under `spec/types.md` §ThinkingPart and **INV-045**. The seven non-streaming Messages goldens represent the same raw block class with `redacted: true`.

This is a substantive loss of the raw block's meaning, not harmless JSON omission. However, the current §ThinkingDelta has **no redacted field**, and MAP-9.2–4 does not say to infer the flag from `ContinuationState.kind`. Thus the existing event-to-response algorithm can reproduce this draft while losing the semantic flag. Parent review should resolve the assembly rule, not merely add an unsupported field to deltas or alter a fixture to match implementation output. A rule that restores the flag from redacted continuation state is one possible design, not a rule I can ratify here.

Separately, `[redacted]` is not raw provider text in any of these Messages bodies. The written ThinkingPart table permits empty text and has a redacted flag, but neither MAP nor serde selects this exact English placeholder over `text: ""`. Non-streaming use of `[redacted]` is therefore **plausible presentation policy, not independently established exact canonical text**. Preserve the opaque blob; do not decode/reinterpret it or replace the actual output with invented reasoning. This question affects all seven non-streaming Messages files and the tool stream, but not the Messages text-only stream.

### Q1 — Continuation `provider`: actual provider or dialect namespace?

All eight non-streaming Responses goldens use `provider: "openai"` for both `reasoning_item` and `response_id`, although the case provider is `meta`. The seven non-streaming Messages goldens and both Messages streams use `provider: "anthropic"`, although the case provider is `meta-anthropic`.

The continuation schema requires only a nonempty provider string; the kind namespace is open. **MAP-7.8's explicit `openai:reasoning_item` spelling supports the existing dialect-owned namespace as a reasonable interpretation.** It does not expressly say whether that namespace is shared by Meta, nor define equivalent binding behavior for Anthropic state. No cited normative rule mandates blindly renaming these to `meta`/`meta-anthropic`; equally, raw Meta bodies cannot prove that `openai`/`anthropic` is the correct canonical attribution. These are opaque replay tokens issued by Meta, not evidence of calls to OpenAI/Anthropic services.

The exact oracle needs a statement distinguishing dialect replay namespace from issuer/adapter identity, including whether state must be isolated across hosts. ModelInfo's provider rule is different and explicit (adapter provider string); it must not be transplanted to ContinuationState without justification. **Do not mechanically rename continuation providers based on this report.**

### Q2 — Message-level ID continuation policy and stream parity

Non-streaming Responses outputs duplicate the response id into message continuation `openai/response_id`; both Responses streams omit that continuation even though the start id is available. Messages outputs, including both streams, duplicate the message id into `anthropic/message_id`; their streams emit a message-level continuation delta immediately after start.

The type schema allows these states, and their `data.id` values exactly match the raw response/message id. But MAP-4 and MAP-9.6 require the Response/start identity, not this additional continuation attachment; MAP-7.8 describes reasoning replay rather than a universal response-id/message-id attachment policy. The exact kinds, mandatory emission, and stream/non-stream parity for these message-level states are not uniquely established in the listed normative rules. Treat this as an unresolved exact-oracle choice, distinct from D1's explicit missing reasoning requirement.

### Request-side distinctions that must not be disguised as response findings

Every canonical request inspected is structurally coherent, with request model `muse-spark-1.3` for conversation cases. Baseline text/stream requests use max_tokens 3000; the low-effort cases mostly use 600; Responses reasoning_summary uses 800. Tool inputs/results correlate within each history. Each structured-output request has the permitted json_schema form, required city/country, `additionalProperties: false`, name `place`, strict true.

Two provider-specific policies appear in the pinned request wires but are not a reason to declare response mappings wrong: Meta Chat sends user_id as `safety_identifier` rather than the base chat table's `user`, and the Meta Messages preset chooses adaptive thinking for the Muse model rather than the Claude model-name table. The draft Meta changes entry describes these differences. A request-mapping/preset review must establish their authority independently; this report checks response expectations against the supplied canonical intent and pinned body, not whether Python correctly generated every HTTP request field. A successful response also does not prove that a request control such as user attribution was honored.

## Per-file review — `goldens/meta` (14)

All body paths below are under `bodies/meta.<stem>/`. Each entry uses the identically named case under `cases/meta/`.

### 1. `goldens/meta/basic_text.json` — **U**

- Pin: `2026-09-03T11-46-04Z.txt` (not the earlier low-budget body).
- Request: `Say ok.`, max_tokens 3000, reasoning unspecified. Raw completed response id `resp_6a995e028bd1c7d8076b422d`; raw and canonical model agree.
- Correct semantic parts: empty thinking for output[0], then text `ok`; not just `ok`. The empty thinking text is required-with-shape, even though optional empty fields are omitted. Reasoning state data preserves the full raw item id `rs_6a995e028bd1c7d8076b422d:rs_f42c29d2-dd3c-4caf-8153-ef1eb90c8bf4`.
- Finish `stop`; usage **10/314/324; 0/—/303**, exactly raw, including reported cache zero. No tool args or stream events apply.
- Citations: P, R/**MAP-7.1,9**, F, Usg/**INV-029**, Ser required fields and Number rule, C. Substantive mapping matches; **Q1/Q2** prevent unique justification of the entire continuation JSON.

### 2. `goldens/meta/files.json` — **S**

- Pins: `bodies/meta.files/meta-upload.json`, `meta-get.json`, `meta-list.json`.
- This is a file-lifecycle golden, not a Response/Request pair. Checked step-specific upload_request and file ids. Upload bytes decode to 76 bytes; filename is `sample.txt`. Request media_type `text/plain` is not fabricated as response MIME.
- Upload/get/list's sole item each correctly retain id `file-28818861621033772`, filename, size 76, epoch 1788435772 → `2026-09-03T11:42:52Z`, and `readiness: pending` from raw `status: uploaded`. Each embedded provider_data equals the entire raw file object, including `expires_at: null`, purpose and status.
- No raw MIME or downloadable flag: both correctly omitted. Successful download in a separate step does not establish a provider-stated downloadable flag. No cursor despite first_id/last_id: list has `has_more: false`. One list item, in wire order.
- No canonical download/delete result expectation is present; cannot claim their content/result mapping is covered. No usage, finish, tools, continuation, start/end apply.
- Citations: Files; **INV-011**, Ser omission **1–3**, Number rule. No discrepancy in the three mapped objects.

### 3. `goldens/meta/image_edit.json` — **S**

- Pin: `2026-09-03T11-46-21Z.json`. Endpoint request is ImageGenerationRequest, with an inline PNG and the instruction to add a small blue square. Output need not keep input MIME.
- Raw has one b64_json image and `output_format: webp`; golden correctly maps one ImagePart with `media_type: image/webp`. Base64 validates; decoded bytes have RIFF/WEBP signature (28,154 bytes). Exact 37,540-character encoded payload hashes to `a2cdd04565f81f3a257d8fbdd97acd1d05b88a694f14bcacde6901e8b3f7512e`, matching the golden digest.
- Usage **9607/385/9992** matches raw; no secondary counters, text, id or model are reported, so none are invented. Request model is not copied into an unreported response model. Raw `created` is not a canonical id.
- Citations: Images, Usg/**INV-029**, Ser, **INV-010–012**, PROTOCOL §generation_parse. Digest and omitted provider_data are the documented *golden comparison projection*, not literal valid ImagePart serialization. No semantic/pixel-edit success claim is made. No chat finish, tools, continuation or stream events apply.

### 4. `goldens/meta/image_gen.json` — **S**

- Pin: `2026-09-03T11-42-41Z.json`. Request: `muse-image-1.0`, red circle prompt, size `1024x1024`.
- One raw b64_json, explicitly `output_format: webp`; golden MIME is correct. Base64 validates; 41,440 decoded bytes have RIFF/WEBP signature. Exact 55,256-character payload hashes to `e6b9c35d9aec70465000ae1203b53c3a315f262468dca93a4f9074254c46aa43`, matching golden.
- Usage **9407/319/9726** matches raw. No unreported response model/id/text or secondary usage added. No claim that reported usage is a token-based billing tariff.
- Citations: Images, Usg, Ser, **INV-010–012**, PROTOCOL §generation_parse. Same projection qualifications as #3. No chat finish, tools, continuation or stream events apply.

### 5. `goldens/meta/models.json` — **S**

- Pin: `2026-09-03T11-42-41Z.txt`. No canonical_request exists by design; case is GET-models, entries_key `data`.
- All seven nonempty raw ids retained in order: `muse-spark-1.3-contributor`, `muse-voice-transcribe-1.0`, `muse-spark-1.3`, `muse-image-1.0`, `muse-spark-1.2-contributor`, `muse-spark-1.2`, `muse-spark-1.1`.
- Each correctly has adapter provider `meta`, api_family `openai_responses`. Model-family labels describe the adapter door, not a guarantee that every listed model supports Responses; no fabricated modalities/pricing/inference facts. Raw `owned_by` and `created: 0` belong in origin.provider_data, stripped only for comparison.
- Citations: Models; Ser omission **1–3**. No usage, finish, tool args, continuation or streams apply. Actual raw-origin retention is outside this projected golden.

### 6. `goldens/meta/multi_turn_tool_result.json` — **U**

- Pin: `2026-09-03T11-46-16Z.txt` (not the earlier capture).
- Canonical history calls get_weather with `{"city":"Paris"}` and correlates result `Sunny, 22°C` to `call_f45fb514-792d-4058-993d-d8deeef94197`. The request's earlier response/call ids deliberately differ from `meta/tools.json`; these are separate turns/captures, not a mismatch. Wire history retains an empty summary on the reasoning replay item as MAP-7.8 requires.
- Raw completed id `resp_6a995e0bd5579648fabf4fbc`; golden correctly has one empty thinking with its new raw reasoning id, then `The weather in Paris is **Sunny, 22°C**.`. No outgoing tool call or echoed tool_result is manufactured. Finish `stop`, not tool_call based on historical tools.
- Usage **641/105/746; 497/—/82**. All match; cache reads are not added to input. No stream events.
- Citations: Req/**INV-013–014,22–24**, P, **MAP-7.8–9**, F, Usg, Ser, C. **Q1/Q2** unresolved; replay payload/id contents themselves match.

### 7. `goldens/meta/reasoning_low.json` — **U**

- Pin: `2026-09-03T11-42-04Z.txt`. Request low effort, max_tokens 600; raw echoes low effort.
- Raw id `resp_6a995d0edd88c9285ed04464`; empty-summary reasoning item correctly retained as empty thinking with its raw id, followed by `ok`. No inference that low effort means zero/visible thinking.
- Finish `stop`; usage **10/196/206; 0/—/185**. No tools/stream events.
- Citations: P, **MAP-7.2,9**, F, Usg, Ser required-empty text, C. **Q1/Q2** unresolved.

### 8. `goldens/meta/reasoning_summary.json` — **U**

- Pin: `2026-09-03T11-42-07Z.txt`. Request asks 17×23, low effort and summary auto, max_tokens 800.
- Raw id `resp_6a995d142dc62061cef044f3`. Exactly one summary_text maps to thinking `Multiplying two integers and returning the numeric result under abstract output constraints.`; final text is exactly `17 times 23 is **391**.`. No concatenation ambiguity with multiple summaries in this body. Raw reasoning id preserved; no encrypted_content was returned, so none may be invented.
- Finish `stop`; usage **21/380/401; 0/—/345**. No tools/stream events.
- Citations: P, **MAP-7.7–9**, Usg, F, Ser opaque state, C. **Q1/Q2** unresolved.

### 9. `goldens/meta/response_format_json_schema.json` — **U**

- Pin: `2026-09-03T11-42-25Z.txt`. Request json_schema `place`, strict true, required city/country, no additional properties; low effort.
- Raw id `resp_6a995d25b491bb9618674251`. Empty thinking/reasoning id correctly retained; text exactly `{"city":"Paris","country":"France"}`. It stays a TextPart string, not a new structured-object part or pretty-printed JSON. It satisfies the supplied schema without fixture rewriting.
- Finish `stop`; usage **14/244/258; 0/—/225**. No tool args/stream events.
- Citations: Req/**INV-050**, **MAP-8.4–6**, P, **MAP-7.9**, Usg, F, Ser, C. **Q1/Q2** unresolved.

### 10. `goldens/meta/streaming.json` — **D**

- Pin: `2026-09-03T11-46-11Z.txt`. Request `Say ok.`, max_tokens 3000, no explicit reasoning control.
- Raw frame/sequence 0 is response.created: id `resp_6a995e03f8832c117f39455d`, model `muse-spark-1.3`; draft start and Response id/model match. Exactly one initial start and one final end.
- Raw sequence 2/3 carries reasoning item `rs_6a995e03f8832c117f39455d:rs_01a067173d7e74009ebb127a618f9828` at output index 0. **Missing from canonical events and response: D1, MAP-7.9 violation.**
- Sequence 6's `ok` maps correctly to TextDelta at index 1. Terminal sequence 9 contains completed status and usage **10/222/232; 0/—/211**; end/Response usage and `stop` match. Following `[DONE]` must not create a second end or overwrite terminal data. End provider_data exactly equals raw completed response, retaining nested empty summaries, nulls, zeros, booleans and floats.
- No tool args apply. Message-level response-id continuation absent: **Q2**, not independently declared a mandatory attachment by this review. Required repair must retain thinking/state as described in D1; keep the correct text, identity and usage.
- Citations: **MAP-7.9**, **MAP-3–4**, **MAP-9.2–4,6**, P, Usg, Ser, C, Projection.

### 11. `goldens/meta/streaming_tool_call.json` — **D**

- Pin: `2026-09-03T11-42-17Z.txt`. Request offers get_weather, asks Paris weather, low effort/max_tokens 600.
- Correct start/Response id `resp_6a995d1a81a9da7f11864982` from sequence 0; one start and final end. Correct text delta at index 1 from sequence 6: `I'll check the current weather in Paris for you.`
- **D1:** sequence 2/3's empty-summary reasoning item `rs_6a995d1a81a9da7f11864982:rs_01a06713ade378f1977b31d81102b9c6` at index 0 is omitted from events/parts despite MAP-7.9.
- Tool metadata at sequence 10/output index 2 gives id **call_01a06713b25871d3b30b6a8a49c270a9** and name get_weather. Golden correctly uses call_id, not provider item id `fc_...`. Required first ToolCallDelta input is `""`, followed once by raw sequence 11 `{"city":"Paris"}`. The done snapshots must not duplicate arguments. Concatenation parses to exactly `{"city":"Paris"}`, no name/argument guessed from request.
- Finish **tool_call** correctly wins over completed status and survives `[DONE]`. Usage **545/306/851; 497/—/237** matches terminal sequence 14 and materialized response. End provider_data is exactly the terminal raw response. No second end and no terminal `stop` overwrite.
- Citations: **MAP-1**, **MAP-3–4**, **MAP-7.9**, **MAP-9.1–6**, F, Usg, Ser, §ToolCallDelta. **Q1/Q2** remain relevant to repaired state.

### 12. `goldens/meta/system_prompt.json` — **U**

- Pin: `2026-09-03T11-42-31Z.txt`. Canonical system asks exactly two words; raw instructions echo it.
- Raw id `resp_6a995d2bb74ae00512274370`; correct empty thinking with raw reasoning id then exact text `ok done`. Do not insert system text into response parts.
- Finish `stop`; usage **21/286/307; 0/—/274**. No tool args/stream events.
- Citations: Req/§Request.system, **INV-024**, P, **MAP-7.9**, F, Usg, Ser, C. **Q1/Q2** unresolved.

### 13. `goldens/meta/tools.json` — **U**

- Pin: `2026-09-03T11-42-14Z.txt`. Request offers one client function get_weather and asks Paris weather.
- Raw id `resp_6a995d1833aa13d94d464c1a`; ordered parts correctly retain empty thinking, `I'll check the weather in Paris for you.`, and a client tool call.
- Exact call id `call_b016be8c-5d5e-431c-b3b3-20cde90ba197`, name get_weather, parsed input `{"city":"Paris"}`. Not `fc_b016...`; not a provider-executed builtin; not a tool result. Commentary text must not be discarded merely because a tool follows. Raw `phase: commentary` is not a canonical TextPart field under current types.
- Finish `tool_call`; usage **545/138/683; 0/—/70**. No stream events. Raw reasoning and response ids match continuation data.
- Citations: **MAP-1**, **MAP-7.9**, §ToolCallPart, F present-tool precedence, Usg, Ser opaque-input rule, Req/**INV-030,33**, C. **Q1/Q2** unresolved; general commentary replay policy is not ratified here.

### 14. `goldens/meta/user_id.json` — **U**

- Pin: `2026-09-03T11-42-36Z.txt`. Request user_id `lm15-case-user`, low effort/max_tokens 600; raw safety_identifier echoes the id.
- Raw id `resp_6a995d30756a85d540f44c2a`; correct empty thinking with raw reasoning id and `ok`. User attribution is request/provider metadata, not a new response message part or canonical Response field.
- Finish `stop`; usage **10/291/301; 0/—/280**. No tool args/stream events.
- Citations: §Config.user_id, §Response, P, **MAP-7.9**, Usg, F, Ser, C. **Q1/Q2** unresolved.

## Per-file review — `goldens/meta-chat` (10)

Body paths are under `bodies/meta-chat.<stem>/`. No raw chat body in these cases returns reasoning content or replay state: a nonzero reasoning token counter alone must not generate a ThinkingPart. No continuation is warranted merely because other dialects expose it.

### 15. `goldens/meta-chat/basic_text.json` — **S**

- Pin: `2026-09-03T11-48-37Z.txt`; request `Say ok.`, max_tokens 3000, no explicit effort.
- Raw id `chatcmpl-01a06719-8a55-7401-889b-a4c11d3ebafe` and model retained; sole text `ok`, no fabricated refusal from raw null refusal.
- Raw/canonical finish `stop`; usage **10/226/236; 0/—/215**. Hidden reasoning telemetry is not visible content. No tool args, continuation or events.
- Citations: P, F chat mapping, Usg, Ser, §Response/Projection; **MAP-7.1,9** does not prescribe an empty thinking part when there is no reasoning item.

### 16. `goldens/meta-chat/models.json` — **S**

- Pin: `2026-09-03T11-49-13Z.txt`; GET-models surface, no canonical_request.
- Same seven ordered raw ids listed in #5, independently compared against this pin. Each has `provider: meta-chat`, `api_family: openai_chat`. Do not replace provider with raw owned_by `meta` or infer capabilities from model names.
- Omitted origin is correct only for the golden's stripping projection. No counters, finish, tools, continuation or stream events apply.
- Citations: Models, Ser omission **1–3**.

### 17. `goldens/meta-chat/multi_turn_tool_result.json` — **S**

- Pin: `2026-09-03T11-48-58Z.txt`. History correlates get_weather call/result with id `call_c892b991-42f8-4c65-9d48-b29bbd37111b`; input Paris, result `Sunny, 22°C`. This history is not required to be the separately pinned tools golden's call.
- Raw id `chatcmpl-01a06719-d0a6-7c32-b70d-4ef94c5dbd7c`, model and text `The weather in Paris is **Sunny, 22°C**.` retained exactly. No outgoing call/result invented from request history.
- Finish `stop`; usage **637/137/774; 497/—/114**. No new tool args, continuation or stream events.
- Citations: Req/**INV-013–014,22–24**, P, F, Usg, Ser opaque-input rule, Projection.

### 18. `goldens/meta-chat/reasoning_low.json` — **S**

- Pin: `2026-09-03T11-48-47Z.txt`. Request low effort/max_tokens 600.
- Raw id `chatcmpl-01a06719-abd3-79a2-a44d-c6eb190ef1eb`; sole text `ok`. No raw reasoning content/state to map.
- Finish `stop`; usage **10/247/257; 0/—/236**. No tools, continuation or events.
- Citations: **MAP-7.2**, P, F, Usg/**MAP-7.9 exact-count clause**, Ser, Projection. Request effort must not turn hidden telemetry into invented text.

### 19. `goldens/meta-chat/response_format_json_schema.json` — **S**

- Pin: `2026-09-03T11-49-01Z.txt`. Canonical strict schema `place`, city/country, as #9.
- Raw id `chatcmpl-01a06719-dded-72b1-8a79-f06614133ef5`; exact text `{"city": "Paris", "country": "France"}` **includes spaces**. Golden preserves those spaces rather than copying the compact Responses/Anthropic text.
- Finish `stop`; usage **14/240/254; 0/—/218**. JSON parses to the requested fields; it stays text. No tools, continuation or events.
- Citations: **INV-050**, **MAP-8.4–6**, §TextPart, P, F, Usg, Ser.

### 20. `goldens/meta-chat/streaming.json` — **S**

- Pin: `2026-09-03T11-48-43Z.txt`. Request `Say ok.`, max_tokens 3000; wire asks include_usage.
- Raw frames: content/role chunk `ok`; finish `stop` plus usage; `[DONE]`. Draft is exactly synthesized start(model from canonical_request), text delta index 0, one final end. No continuation or reasoning content was returned.
- Raw chunk id `chatcmpl-01a06719-9207-7862-9f4d-59d2e263e7e0` is intentionally **not** lifted into start/Response: **MAP-9.6 explicitly requires this omission**, even though it is an available wire fact. Do not “fix” it.
- End and Response usage **10/239/249; 0/—/228**, finish `stop`. Empty terminal delta creates no empty extra part; `[DONE]` does not create a second end. No tools.
- Citations: **MAP-3–4**, **MAP-9.1–6**, §TextDelta, F, Usg, Ser, Projection. End provider_data is optional in event schema; this golden does not establish internal raw-data retention.

### 21. `goldens/meta-chat/streaming_tool_call.json` — **S**

- Pin: `2026-09-03T11-48-54Z.txt`. Request offers get_weather and asks Paris weather, low effort/max_tokens 600.
- Correct synthesized start with request model, no id. Raw chunk id `chatcmpl-01a06719-bdb7-7792-b172-7fe75cf3d6d9` correctly absent from Response under MAP-9.6.
- Text `I'll fetch the current weather in Paris.` and tool fragments all use **slot 0**. This is not an index collision bug: **MAP-9.1–3** permits independently indexed kinds and emits text before tool in the slot.
- Raw first tool fragment supplies `call_01a06719bef975d3912c2f61c4f598e7`, get_weather, empty input string. Next fragment is `{"city":"Paris"}`. Golden preserves both fragment strings; materialization yields one correctly named call with exact object input, not `{}{"city":"Paris"}`, and no guessed tool metadata.
- Raw finish tool_calls → `tool_call`, preserved through `[DONE]`; one final end. Usage **545/89/634; 497/—/22** in both end and Response. No visible thinking or continuation.
- Citations: **MAP-1**, **MAP-3–4**, **MAP-9.1–6**, F, Usg, §ToolCallDelta, Ser required-empty input and opaque final input. No mapping discrepancy found in projected fields.

### 22. `goldens/meta-chat/system_prompt.json` — **S**

- Pin: `2026-09-03T11-49-04Z.txt`. System intent exactly two words; raw response text exactly `ok understood`.
- Raw id `chatcmpl-01a06719-f10a-7fb0-a63d-4ef81fd5d9c3` and model retained. Finish `stop`; usage **21/391/412; 0/—/379**. No tool args, continuation or stream events.
- Citations: Req/§Request.system, **INV-024**, P, F, Usg, Ser. Do not normalize text to another dialect's two-word answer.

### 23. `goldens/meta-chat/tools.json` — **S**

- Pin: `2026-09-03T11-48-51Z.txt`. Request offers get_weather/Paris.
- Raw id `chatcmpl-01a06719-b6bd-7d93-91b8-945d2a1c485f`. Correct text `I'll fetch the current weather for Paris.` then call `call_fd4de3a1-fbf8-4a49-80af-abf66eb12471`, name get_weather, exact parsed input `{"city":"Paris"}`.
- Finish raw tool_calls → canonical `tool_call`; usage **545/161/706; 497/—/94**. No reasoning part, continuation or stream events invented.
- Citations: **MAP-1**, §ToolCallPart, F, Usg, Ser opaque objects, Req/**INV-030,33**. No discrepancy.

### 24. `goldens/meta-chat/user_id.json` — **S**

- Pin: `2026-09-03T11-49-09Z.txt`. Canonical user_id `lm15-case-user`, low effort/max_tokens 600. See request-side qualification above about Meta Chat's wire field name.
- Raw id `chatcmpl-01a0671a-008a-7481-923d-961e00c15386`; exact text `ok`. The response does not echo user attribution; the golden does not invent it.
- Finish `stop`; usage **10/221/231; 0/—/210**. No tool args, continuation or events.
- Citations: §Config.user_id, §Response, P, F, Usg, Ser, Projection. Supported *response mapping*, not proof of user_id wire semantics.

## Per-file review — `goldens/meta-anthropic` (10)

Body paths are under `bodies/meta-anthropic.<stem>/`. Redacted payloads were compared in full as opaque strings, not merely by their displayed prefix. Their URL-safe/nonstandard base64-like alphabet is **not** a media-part validation issue: ContinuationState.data is opaque JSON, not ImagePart.data. All request/response tool ids are actual provider values, not synthesized ids.

### 25. `goldens/meta-anthropic/basic_text.json` — **U**

- Pin: `2026-09-03T11-49-47Z.txt`; request no effort/max_tokens 3000.
- Raw id `msg_6a995edfe4086ad14600496d`; ordered redacted_thinking then `ok`. Golden preserves one thinking part with redacted true and the exact 5,522-character blob (SHA-256 `dec8712104b438953c0922bfdb689f6156a6d88b6adb777f5eff46aa94e80b00`), then the exact text. Message continuation id equals raw id.
- Finish end_turn → `stop`; usage **10/376/386; 0/0/365**. Total synthesized 10+376; zero cache counters retained. No tool args/stream events.
- Citations: P/§ThinkingPart, **MAP-7.8**, F, Usg/**INV-029**, Ser opaque payloads, C. **Q1/Q2/Q3** prevent freezing exact provider/kind/placeholder policy; blob and telemetry match.

### 26. `goldens/meta-anthropic/models.json` — **S**

- Pin: `2026-09-03T11-52-02Z.txt`; GET-models surface, no canonical_request.
- Raw response happens to be OpenAI-shaped but all seven usable ids are under case entries_key `data`; same ordered list as #5, compared independently.
- Correct provider `meta-anthropic` and family `anthropic_messages` on all seven entries. Neither raw owned_by `meta` nor raw object `model` changes adapter identity. No invented display names, capabilities or timestamps; omitted origin follows comparison stripping.
- Citations: Models, Ser. No usage, finish, tool args, continuation or streams apply.

### 27. `goldens/meta-anthropic/multi_turn_tool_result.json` — **U**

- Pin: `2026-09-03T11-50-08Z.txt`. Request history has two redacted blocks, get_weather/Paris call `call_01a0671adb6f7781b3ad2fb9d7453d9f`, and correctly correlated `Sunny, 22°C` result. Both historical opaque blobs exactly match their replayed wire blocks; they are not replaced by the later response blob. The request's distinct history id is not the separately captured tools golden's id.
- Raw response id `msg_6a995ef25efdfce1a91c4c59`; one new redacted block (1,426 characters; SHA-256 `756172565f8481c8898128d2eca47eb1d2a5eed888b8897c61ecd8dd857e1216`) then `The weather in Paris is **Sunny, 22°C**.`. Golden content/state matches, no outgoing call or tool_result added.
- Finish `stop`; usage **255/72/327; 497/0/49**. **327 is correct**, despite 497 cache reads; input 255 is not rewritten to 752. No stream events.
- Citations: Req/**INV-013–014,22–24**, **MAP-7.8**, P, F, Usg provider-verbatim table/**INV-029**, Ser, C. **Q1/Q2/Q3** unresolved.

### 28. `goldens/meta-anthropic/reasoning_low.json` — **U**

- Pin: `2026-09-03T11-49-58Z.txt`; request low effort/max_tokens 600.
- Raw id `msg_6a995ee9558656ed22694972`; one redacted thinking block with true flag and exact 2,791-character state (SHA-256 `910d21aa199f780e74c2a167582a5e6b24f8eb58e8d738e9928d4f7f04127bd4`), then `ok`.
- Finish `stop`; usage **10/289/299; 0/0/262**. Do not infer 278 reasoning tokens by subtracting visible text: use exact thinking_tokens 262. No tool args/stream events.
- Citations: P, R/**MAP-7.8–9**, F, Usg, Ser, C. **Q1/Q2/Q3** unresolved; adaptive request-policy scope noted above.

### 29. `goldens/meta-anthropic/response_format_json_schema.json` — **U**

- Pin: `2026-09-03T11-50-11Z.txt`; canonical strict place schema, low effort/max_tokens 600. Schema is preserved; Messages wire's lack of a name field does not license schema edits.
- Raw id `msg_6a995ef6baf91ddfe1cd4fe1`; one redacted thinking block with exact 2,791-character state (SHA-256 `75a7eda101ae3b5048a07c8f5f2152f896264051b2c81d11654971e59a4dc7e3`) then exact compact JSON text `{"city":"Paris","country":"France"}`. No conversion into a tool call/object part.
- Finish `stop`; usage **14/241/255; 0/0/222**. No tool args/stream events.
- Citations: **INV-050**, **MAP-8.4–6**, P/§ThinkingPart/§TextPart, F, Usg, Ser, C. **Q1/Q2/Q3** unresolved.

### 30. `goldens/meta-anthropic/streaming.json` — **U**

- Pin: `2026-09-03T11-49-52Z.txt`; request `Say ok.`, max_tokens 3000, effort absent.
- Raw message_start id `msg_6a995ee247f92338f96849fb`, model retained in start/Response. Draft has one initial start, message-level continuation delta (no part_index), text delta `ok` at index 0, one final end. Continuation data.id exactly matches raw id; serialization of null message-level part_index is correct.
- Raw start reports I/O 0/0, but later message_delta reports **10/293**, cache 0/0 and exact thinking 282. Later non-null data supersedes start values: correct final usage **10/293/303; 0/0/282**, **not** 0/0/0 and not doubled totals. End and Response match. Raw end_turn → `stop`; bare message_stop must contribute no new finish or usage.
- Raw has **no redacted or thinking content block** in this stream; nonzero thinking_tokens alone does not require inventing a ThinkingPart. This is unlike the Responses streams' actual reasoning items. No tool args.
- Citations: **MAP-3–4**, **MAP-9.2–6**, P, F, Usg/**INV-029**, §ContinuationDelta, Ser. **Q1/Q2** unresolved; no Q3 placeholder/flag issue in this body.

### 31. `goldens/meta-anthropic/streaming_tool_call.json` — **D/U**

- Pin: `2026-09-03T11-50-05Z.txt`; request get_weather/Paris, low effort/max_tokens 600.
- Correct actual start id/model `msg_6a995eed385cf0056b9044ee`/`muse-spark-1.3`, message-level continuation data.id, one final end. Ten raw SSE data frames: message_start, redacted block 0 start/stop, redacted block 1 start/stop, tool block 2 start/delta/stop, message_delta, message_stop.
- Both 1,426-character redacted blobs retained exactly and attached to their correct slots. SHA-256 values: slot 0 `bd71512aecbe1ff6070697d4fa6ee1c3d2236eab6c50fa017b9ab3ff8a1f61d4`; slot 1 `8edecf7770e19efa9aea04482955d84cbbaa0dee26e51911e64edcef920981b2`. There are two separate thinking parts, not one concatenated part. **D2:** both omit redacted true in the materialized response, so both mean false under current serde defaults.
- Tool block at index 2 has id `call_01a0671ad2cd71e2928aa60e5ca19492`, name get_weather, initial object input `{}`. Correct canonical metadata delta input is an empty fragment `""`, not a literal prefix `"{}"`; next input_json_delta is exactly `{"city":"Paris"}`. Materialized call input matches the parsed fragment; metadata comes from raw, not the request tool list.
- Raw tool_use → `tool_call`. Terminal usage **48/188/236; 497/0/121** supersedes initial 0/0, then message_stop contributes nothing. End and Response agree; do not add cached 497 to total 236. No user-visible text other than the policy placeholder is returned.
- Citations: **MAP-1**, **MAP-3–4**, **MAP-9.1–6**, §ThinkingPart/**INV-045**, §ThinkingDelta, §ToolCallDelta, F, Usg, Ser, C. **Q1/Q2/Q3** remain open; restoring redaction in assembly needs a normative decision, not a self-approved golden edit.

### 32. `goldens/meta-anthropic/system_prompt.json` — **U**

- Pin: `2026-09-03T11-50-15Z.txt`. Request system exactly two words, low effort/max_tokens 600.
- Raw id `msg_6a995efef40f1e82a2fb437e`; redacted true with exact 5,522-character blob (SHA-256 `4641fd694aa613239decab136aa4376f42decac0b86ddb7419e35577013a3ab4`) then exact `ok noted`. No system-part echo.
- Finish `stop`; usage **21/403/424; 0/0/373**. No tool args/stream events.
- Citations: Req/§Request.system/**INV-024**, P, F, Usg, Ser, C. **Q1/Q2/Q3** unresolved.

### 33. `goldens/meta-anthropic/tools.json` — **U**

- Pin: `2026-09-03T11-50-02Z.txt`; request get_weather/Paris, low effort/max_tokens 600.
- Raw id `msg_6a995eeb80710c7bc9074657`; correct order is **two** redacted thinking parts then tool call, with no fabricated introductory text. Both true flags present. Each state is 1,426 characters, preserved independently: SHA-256 `a9cca38b8f22ae1fc6925cbae356cb297f49fa3909346681a3dad3f7380d7357` and `cee671e0b3817bd857ff56f90a9e606210414f624abbebccbe9846403f5c5271`.
- Exact call id `call_01a0671ac8b57a50a45496712549627f`, name get_weather, input object `{"city":"Paris"}` copied verbatim from tool_use. No string parsing needed for this non-streaming wire's object input.
- Finish `tool_call`; usage **48/108/156; 497/0/41**. A TextPart placeholder is not required because the message already has parts (MAP-2). No stream events.
- Citations: **MAP-1–2**, §ToolCallPart, §ThinkingPart, F, Usg/**INV-029**, Ser opaque objects, C. **Q1/Q2/Q3** unresolved.

### 34. `goldens/meta-anthropic/user_id.json` — **U**

- Pin: `2026-09-03T11-50-23Z.txt`. Request user_id `lm15-case-user`, low effort/max_tokens 600; metadata is request intent, not response text.
- Raw id `msg_6a995f018566219825ac45d1`; redacted true with exact 2,791-character blob (SHA-256 `22c21c86df74bd2d3150405b2fe8cb657952ab324cfa85e0c623132c2e893516`) then exact `ok`.
- Finish `stop`; usage **10/220/230; 0/0/193**. No invented response user field, tool args or stream events.
- Citations: §Config.user_id, §Response, P, F, Usg, Ser, C. **Q1/Q2/Q3** unresolved.

## Parent-review checklist / limits of conclusions

1. **Do not freeze the two Responses stream goldens as written.** MAP-7.9 already requires retention of their empty reasoning items and replay state. Resolve exact event timing/state policy before proposing cited changes.
2. **Resolve the Messages redaction/assembly gap.** The tool stream loses true flags; determine a uniform non-stream/stream rendering and replay rule, including whether `[redacted]` is mandated. The existing delta type alone cannot express the flag.
3. **Specify continuation namespace and message-id policy.** Decide issuer versus dialect attribution, mandatory message-level state, and stream parity. Current `openai`/`anthropic` values are plausible dialect namespaces, not proven errors or independently justified issuer labels. Both changing and freezing them require better authority than Python output.
4. **Keep verified telemetry intact.** All reviewed usage values match the pins; unknown cache-write/audio fields remain absent; Messages totals exclude cache counts; chat stream ids remain omitted by MAP-9.6; tool finish words survive terminators.
5. **Preserve projection distinctions.** Image hashes and omitted generation/model provider_data are comparison conventions. This review did not verify an implementation's unprojected return values or unmapped-field recorder. No positive claim about these hidden properties follows from matching projected goldens.
6. The corpus does not exercise malformed/unnamed tool arguments, multiple parallel calls, error-only streams, duplicate starts, arbitrary usage-only chunks, or unknown finish tokens here. Rules exist for several of those, but these 34 bodies do not validate them. Do not broaden this review into such a coverage claim.
7. Request-hash sufficiency and live wire receipts remain the parent contract worker's separate issue. None of the per-file S verdicts supplies human approval, ratification, or wire evidence.

**Completion requests parent review. No repository files or provenance have been changed, and this reviewer has not accepted its own work.**
