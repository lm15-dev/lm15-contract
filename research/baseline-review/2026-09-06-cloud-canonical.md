# Independent canonical review — 54 cloud goldens

Review for delegation `14084c9b-5030-44ea-a8ad-b296adb1c018`.
**Submitted for parent review; not acceptance, approval, or ratification.**

## Scope and result

Reviewed every JSON golden in `goldens/azure` (18), `azure-chat` (14),
`bedrock-chat` (11), and `bedrock-mantle-chat` (11): 47 response goldens,
including eight ordinary streams, and seven other endpoint goldens.

**28 have no identified canonical discrepancy; 26 are qualified/held for the
specific normative choices below.** The primary content, tool identities and
arguments, finish reasons, and reported usage in all 47 responses agree with
independent raw-body derivation. This is NOT blanket acceptance of their exact
JSON: continuation, inline-reasoning classification, stream metadata, and one
file-readiness fold prevent that conclusion. No request to rewrite fixtures to
match an implementation is made.

### Method and authority

Read `AUTHORITY.md`; the relevant tables in `spec/types.md`, all of
`spec/invariants.md` and `spec/vocabularies.md`; and
`../lm15-python/docs/mapping-rules.md` and `serde-rules.md`. Also consulted
`spec/auth.md` AUTH-10 for dialect/access composition, `spec/SCOPE.md`,
`harness/PROTOCOL.md`, the model-listing normative mapping and model-hydration
schema named there. Draft cloud changes were context, not substitute authority.

Each response was compared with the case's **pinned** body and its own
`canonical_request`, not another capture or another provider's golden. Stdlib
JSON/SSE processing independently projected raw content/usage, parsed complete
JSON tool arguments, concatenated streamed fragments by slot/kind, and compared
all fields. Every byte of encrypted continuation payloads was compared without
decryption. Model lists were checked entry-by-entry, including order; file and
batch substeps were checked against each pinned object; speech was base64-decoded
and compared with the entire binary body; all 16 live server frames were checked.
No implementation code was imported or executed, no shim/tests supplied an
oracle, no live network calls were made, and no repository/provenance files were
modified. Only this assigned report was written intentionally.

Missing wire-receipt request hashes are a separate evidence task and do not
change any mapping verdict here. A syntactically valid canonical request does
not promise the model obeys it: e.g. required-tool calls with `city: "ok"` must
remain exactly that, and structured JSON output remains text.

## Citation key (exact sections)

References below to MAP rules mean `../lm15-python/docs/mapping-rules.md`.
INV references mean `spec/invariants.md`.

- **BASE:** `spec/types.md` §§TextPart, Message, Response;
  INV-015, INV-036, INV-037; MAP-1/MAP-2;
  `spec/vocabularies.md` §§FinishReason, Forward-compatibility policy rules 2–3;
  `../lm15-python/docs/serde-rules.md` §Omission rule 1–3 and
  “Required fields are always emitted”. Response `provider_data` is excluded
  by default by the Response table, so its absence from `canonical_response`
  is not a discrepancy. Empty annotations, absent/null logprobs, and wire
  bookkeeping do not become invented content parts.
- **USAGE:** `spec/types.md` §Usage, especially “Counters are provider-verbatim”;
  INV-029; MAP-3 “Usage counters at the wire boundary”; MAP-7 rule 9;
  serde §Number rule 2,4 and §Omission rule 1. Counters are integers; reported
  zero is retained; missing counters are omitted, not inferred as zero.
- **TOOLS:** `spec/types.md` §§ToolCallPart, ToolCallDelta, ToolChoice;
  MAP-1, MAP-9 assembly rules 1–3,5; INV-001/002, INV-030/031;
  vocabularies §Forward-compatibility policy rule 2 (present tool call wins);
  serde §Omission rule 3 and required-with-shape `input`.
- **STREAM:** MAP-3 (one final merged end; bare terminator says nothing),
  MAP-4 (one start), MAP-9 assembly rules 1–6;
  `spec/types.md` §§Deltas, StreamStartEvent, StreamDeltaEvent, StreamEndEvent;
  INV-006/007; serde §Number rule 2 and §Omission rule 2 (embed typed deltas
  verbatim; their empty strings are not recursively removed).
- **THINK:** MAP-7 rules 1–3,7–9; `spec/types.md` §§Reasoning,
  ThinkingPart, ThinkingDelta, ContinuationState; INV-005/015;
  serde §Omission rule 3 and required-with-shape thinking `text`.
- **FORMAT:** MAP-8 rules 4–6; INV-050; `spec/types.md` §Config
  `response_format`; serde §Omission rule 3. These rules govern the request
  schema, not a conversion of returned JSON text into an untyped message object.
- **CACHE:** MAP-6 rules 1,6; `spec/types.md` §§CacheConfig, Usage;
  INV-029; serde §Number rule 2. A warm cache does not subtract reads from
  input or fabricate cache-write telemetry.
- **USER:** `spec/types.md` §Config `user_id` (Responses safety_identifier,
  Chat user); serde §Omission rule 1. Attribution does not create a response part.
- **HISTORY:** `spec/types.md` §§Message, ToolResultPart; INV-013/014,
  INV-022/023; MAP-7 rule 8; serde §Omission rule 2–3. The new response is
  not a copy of earlier assistant/tool messages.
- **MODELS:** `changes/2026-08-31-list-models-provisional.md`
  §Canonical mapping (normative for this surface), promoted into scope by
  `spec/SCOPE.md` §Model listing; `harness/PROTOCOL.md`
  §parse_models_response; `../lm15-python/docs/model-hydration.md`
  §§Canonical JSON for ModelInfo, ModelInfo, ModelOrigin, Guardrail;
  serde §Omission rule 1–3. Goldens intentionally strip origin.provider_data;
  full endpoint responses must retain each raw entry there. This is the
  protocol's comparison projection, not permission to mutate opaque data.

## Specific unresolved choices / discrepancies

### C — Azure continuation namespace and complete/stream asymmetry (13 files)

Eleven nonstream Responses goldens attach message-level
`{provider:"openai",kind:"response_id",data:{id:<raw response id>}}`.
Both Responses stream goldens omit this state, although the real start and
terminal response expose the id. The raw id values all match, and serde does
not permit changing their opaque contents.

MAP-7 rules 8–9 **explicitly justify** the two reasoning goldens' empty
ThinkingPart and `openai:reasoning_item` with raw id/encrypted_content.
They do not prescribe a general `response_id` continuation, its host versus
dialect namespace, or its omission only on streams. `spec/types.md`
§ContinuationState defines an open nonempty provider/kind pair, not its
production policy. AUTH-10 distinguishes `azure` access from the Responses
codec; its provider-field consultation list names errors/routing/doctor,
not continuation. It therefore does not compel replacing `openai` with
`azure` either.

**Hold the exact response_id oracle, not the content/usage.** Resolve whether
this state is emitted, on which paths, and whether provider denotes the
codec or access route. Preserve `openai:reasoning_item` as MAP-7 spells it
unless amended. Do not mechanically rename it or invent a stream continuation
without a cited rule. `summary: []` is required on *replayed wire reasoning
items* (MAP-7.8), not required inside canonical continuation.data; the two
current reasoning-state payloads need no invented summary field.

### R — Runtime Bedrock inline `<reasoning>` (8 files)

Runtime bodies put `<reasoning>…</reasoning>` inside ordinary `content`;
Mantle bodies instead supply a distinct `message.reasoning` / `delta.reasoning`.
The runtime goldens preserve the complete string as TextPart/TextDelta;
Mantle correctly exposes the separate field as thinking (MAP-1; THINK).

MAP-7.7 discusses Groq's parsed reasoning wire knob; neither it nor the
ThinkingPart table specifies an inline-tag parser for runtime Bedrock. There
is no normative delimiter grammar, whitespace rule, escaped/literal-tag rule,
or cross-fragment behavior. Thus current runtime bytes are preserved and
there is **no justified mandatory replacement** available from existing rules.
But a semantic promise to separate all provider reasoning is not established
by these goldens. Before freezing that promise, explicitly choose literal
content or a provider-specific parser with stream parity. Do not apply a
regex merely because Python currently does or does not parse tags. No exact
reasoning count is reported by either Bedrock door here; keep
`reasoning_tokens` absent even when thinking text exists (USAGE).

### P — Chat stream raw-terminal preservation / exact no-op trace (6 files)

All six Chat stream traces have correct synthesized start, content fragments,
merged finish/usage and materialization, but omit end.provider_data entirely.
The types table allows an optional provider_data; vocabularies
§Forward-compatibility policy rule 3 says the verbatim provider payload stays
in provider_data, including terminal frames. Response's default serializer
suppresses that field, whereas StreamEndEvent's serializer does **not**.
`harness/PROTOCOL.md` §replay_stream calls events the full canonical trace
and specifies canonical stream-event serde, with no provider_data stripping.
MAP-3 specifies finish/usage coalescing, not the exact multi-frame raw-payload
container or whether only an internal materialized Response retains it.

This is an **unresolved preservation/serialization contract**, not evidence
that an unobserved implementation has lost data. Specify the raw terminal
representation and its required emission before asserting these stripped
traces as a complete raw-metadata oracle. Do not copy a guessed terminal
container into goldens. Azure Responses traces, in contrast, include an exact
copy of the terminal response as end.provider_data (verified).

All ordinary stream traces also suppress initial empty-content role markers,
empty deltas, and repeated done snapshots. This loses no text or actionable
call. Deltas allow empty text but the rules do not demand a delta for every
wire no-op; a one-frame/one-event assertion would be unjustified. Named
empty-input **tool** fragments in the Azure traces are retained, as they
carry identity. This distinction should be explicit if exact no-op emission
is intended as an inter-port requirement.

### F — Azure Files `pending` versus inherited fallback (1 file)

Upload raw `status:"pending"` maps to `readiness:"pending"`; this is sensible
under §FileReadiness's meaning (not yet usable). However its explicit OpenAI
fold lists `uploaded → pending`, `error → failed`, and
`processed/absent/unknown → ready`; it does not name `pending`. Applying that
inherited table literally gives **ready**, not the golden's pending.
`spec/types.md` §FileInfo alone does not define an Azure override. Add an
explicit Azure/native-pending fold, or obtain an authoritative interpretation
of the existing semantic rule; **do not “fix” this to ready just to follow
implementation output or an inappropriate fallback**. This is a narrow
normative conflict, not a byte/source uncertainty. Get/list mapping is clear.

### Other observations (not inferred changes)

- No duplicate starts/ends, lost final usage, invented tool names/ids, malformed
  JSON arguments, or wrong finish words were found. No missing-name fallback
  is exercised: every streamed call is named on the wire.
- All tool-bearing terminal reasons here already agree with `tool_call`;
  MAP-9.5 versus the broader vocabulary “tool call always wins” precedence
  does not create a choice in any of these captures.
- The two Azure filter bodies contain ordinary output text, not native refusal
  parts. Keep their text; `content_filter` is a finish reason, not an instruction
  to replace content with a refusal or an empty placeholder.
- The two Azure catalogs each contain 207 raw ids; Mantle contains 55. Listing
  these does not establish that every model is deployed or callable on that
  door (AUTH-10; MODELS advisory guardrail). No invented capability filtering,
  deployment renaming, or provider-prefix insertion is justified.
- Live realtime uses its own LiveServerEvent vocabulary. MAP-3/4 ordinary
  stream start/end events must **not** be inserted into the live trace.

## Per-file review

`NO DISCREPANCY` is a reviewer finding, not acceptance. `QUALIFIED` identifies
specific rule choices above. Every row's BASE/USAGE/etc citations expand to
the exact sections in the citation key. Usage objects below list **all and
only** the expected counters. Unlisted optional counters remain absent.
Raw text and id checks are exact, including Unicode and whitespace.

### azure

#### 01. `goldens/azure/basic_text.json` — QUALIFIED C

**Raw:** `bodies/azure.basic_text/2026-09-04T11-49-01Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=100.

**Expected mapping:** Raw output_text is `Ok.`; completed → stop. Message response_id equals raw response.id (C).

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id `resp_04bf600a5852e0ef006a9ab02dc48481949d375265f4188a89`.

**Expected usage:** `{"input_tokens":10,"output_tokens":3,"total_tokens":13,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 02. `goldens/azure/batch.json` — NO DISCREPANCY

**Raw:** `bodies/azure.batch/azure-batch-submit.json`, `bodies/azure.batch/azure-batch-status.json`, `bodies/azure.batch/azure-batch-cancel.json`, `bodies/azure.batch/azure-batch-list.json`.

**Expected mapping / comparison:** Checked all four pinned substeps. Submit/status validating → queued; cancel cancelling → cancelling (not prematurely cancelled). Job batch_5fb77dc6-c5be-4515-b914-f0d5f0b359d3, label lm15-azure-capture, created_at=2026-09-04T14:12:55Z. List is that cancelling job followed by batch_9bebc685-2a6e-45cb-98fb-ee014f29f09f cancelled, label lm15-azure-proof, created_at=2026-09-04T14:00:53Z. Raw provider_data preserved fully, including empty output_file_id/endpoint strings, null usage, and request_counts. BatchRequest contains one gpt-4.1-mini-batch request with max_tokens=16 and label. Do not substitute receipt time for raw created_at. No results/BatchEntry canonical outcome is pinned here.

**Citations:** spec/types.md §§BatchRequest, BatchJobInfo, BatchEntry; spec/vocabularies.md §BatchStatus and Forward-compatibility policy rule 2; INV-032; serde §Omission rule 1–3.

#### 03. `goldens/azure/content_filter_completion.json` — QUALIFIED C

**Raw:** `bodies/azure.content_filter_completion/2026-09-04T14-27-35Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=30.

**Expected mapping:** Raw output_text is the provider’s apology; status=incomplete with incomplete_details.reason=content_filter → content_filter. Do not manufacture a RefusalPart or erase text (C).

**Checked response:** assistant; parts text; finish `content_filter`; model `gpt-4.1-mini`; id `resp_0161e44b99f13039006a9ad55831308197b6cfdf47b9232c11`.

**Expected usage:** `{"input_tokens":41,"output_tokens":7,"total_tokens":48,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 04. `goldens/azure/files.json` — QUALIFIED F

**Raw:** `bodies/azure.files/azure-upload.json`, `bodies/azure.files/azure-get.json`, `bodies/azure.files/azure-list.json`.

**Expected mapping / comparison:** Upload/get reference file-ab52117486e94ca695c508a51e7a22ac, filename lm15-azure-proof.txt, bytes=40, created_at=2026-09-04T14:10:47Z. Upload pending is the F fold conflict; get processed → ready is clear. List contains exactly file-2eb380c0425a4601a51cfc6ba11a841e, lm15-batch.jsonl, 209 bytes, created 2026-09-04T14:00:48Z, ready. has_more=true, so next_cursor is that raw last_id even though page has one item. All three raw provider_data objects match in full, including null status_details/expires_at. MIME/downloadable/expires are not inferred from the upload request. Download/delete have no canonical outputs in this golden; they are not reviewed as extra output assertions.

**Citations:** spec/types.md §§FileUploadRequest, FileInfo, FilePage; spec/vocabularies.md §FileReadiness; INV-001/002, INV-011; serde §Omission rule 1–3 and §Number rule (declared integer size).

#### 05. `goldens/azure/live_text.json` — NO DISCREPANCY

**Raw:** `bodies/azure.live_text/2026-09-04T14-37-03Z.jsonl`.

**Expected mapping / comparison:** live_config gpt-realtime-mini / system Be terse.; request text asks “azure live hello”. Checked the 16 server frames, not the two client transcript records. Zero-based server frames 8,9,10 yield text `Azure`, ` live`, ` hello`; frame 15 completed response.done yields one turn_end with usage input=14, output=5, total=19, cache_read=0, input_audio=0, output_audio=0. All other server frames yield []. Preserve capital A from the actual response, not the request. Do not duplicate final text snapshots or emit usage separately as well as turn_end; no tool/cancel case occurs. No ordinary stream start/end.

**Citations:** spec/types.md §§LiveConfig, LiveServerTextEvent, LiveServerTurnEndEvent, LiveServerUsageEvent, Usage; spec/vocabularies.md §LiveServerEventType; INV-029; harness/PROTOCOL.md §replay_live; serde §Omission rule and §Number rule 2.

#### 06. `goldens/azure/models.json` — NO DISCREPANCY

**Raw:** `bodies/azure.models/2026-09-04T11-54-39Z.txt`.

**Expected mapping / comparison:** 207 entries, exactly raw data[].id in order; provider=azure, api_family=openai_responses. No capability, lifecycle, or deployment filtering. No canonical_request: GET listing case. MODELS projection explains omitted origin.

**Citations:** MODELS; spec/auth.md AUTH-10 Azure row.

#### 07. `goldens/azure/multi_turn_tool_result.json` — QUALIFIED C

**Raw:** `bodies/azure.multi_turn_tool_result/2026-09-04T11-49-17Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user→assistant→tool; tools get_weather; max_tokens=200.

**Expected mapping:** Current raw weather answer is one TextPart. Earlier get_weather call and Sunny, 22°C tool result are request history only; the outgoing continuation is the new response id (C).

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id `resp_0a20a5aa65821acc006a9ab03dbe64819685672f7d1815c910`.

**Expected usage:** `{"input_tokens":74,"output_tokens":17,"total_tokens":91,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; HISTORY; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 08. `goldens/azure/prompt_cache_key.json` — QUALIFIED C

**Raw:** `bodies/azure.prompt_cache_key/2026-09-04T14-24-41Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; system present; max_tokens=16; cache={"mode":"auto","key":"lm15-azure-cache-proof"}.

**Expected mapping:** Raw `Ok.`; input 4215 already includes 4096 cache-read tokens. Wire explicitly reports write=0 and reasoning=0. No subtraction or inferred write (C).

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id `resp_0a9361b7cd6f7fc8006a9ad4a9b86c8194bcc12be20cf55f6e`.

**Expected usage:** `{"input_tokens":4215,"output_tokens":3,"total_tokens":4218,"cache_read_tokens":4096,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; CACHE; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 09. `goldens/azure/reasoning_high.json` — QUALIFIED C

**Raw:** `bodies/azure.reasoning_high/2026-09-04T14-19-24Z.txt`.

**Request context:** model `gpt-5-mini`; roles user; max_tokens=1000; reasoning={"effort":"high"}.

**Expected mapping:** Raw reasoning.summary=[] → empty ThinkingPart with exact rs_ id and encrypted_content, then the complete mathematical answer. Explicit reasoning=768 is retained inside output=919, not added again. Message response_id policy remains C.

**Checked response:** assistant; parts thinking → text; finish `stop`; model `gpt-5-mini`; id `resp_0a3e8f7b06a515a5006a9ad36d03188194ad25f91efbc2d2ed`.

**Expected usage:** `{"input_tokens":50,"output_tokens":919,"total_tokens":969,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":768}`.

**Citations:** BASE; USAGE; THINK; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 10. `goldens/azure/reasoning_low.json` — QUALIFIED C

**Raw:** `bodies/azure.reasoning_low/2026-09-04T14-19-22Z.txt`.

**Request context:** model `gpt-5-mini`; roles user; max_tokens=500; reasoning={"effort":"low"}.

**Expected mapping:** Raw reasoning.summary=[] → empty ThinkingPart with exact rs_ id and encrypted_content, then text `391`. Explicit reasoning_tokens=0 is correct despite an opaque reasoning item; do not estimate it from output=38. Message response_id policy remains C.

**Checked response:** assistant; parts thinking → text; finish `stop`; model `gpt-5-mini`; id `resp_068aac5543676f1d006a9ad36acb788194b78b42c7bb5f4cf3`.

**Expected usage:** `{"input_tokens":17,"output_tokens":38,"total_tokens":55,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; THINK; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 11. `goldens/azure/response_format_json_schema.json` — QUALIFIED C

**Raw:** `bodies/azure.response_format_json_schema/2026-09-04T11-49-21Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=200; response_format=json_schema (schema/name/strict checked).

**Expected mapping:** Exact raw JSON text is {"city":"Paris","country":"France"}; it remains a TextPart. Request schema name/strict do not become response fields (C).

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id `resp_0758a410b8f8fc95006a9ab041b6088190b00d72b1d17fd26f`.

**Expected usage:** `{"input_tokens":42,"output_tokens":10,"total_tokens":52,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; FORMAT; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 12. `goldens/azure/speech_gen.json` — NO DISCREPANCY

**Raw:** `bodies/azure.speech_gen/azure-speech-2026-09-04T14-08-11Z.bin`.

**Expected mapping / comparison:** generation_request: gpt-4o-mini-tts, prompt Hello from lm15., voice alloy, format wav. Canonical response has only audio={type:audio, media_type:audio/wav, data:<base64 of pinned body>}. All 69,644 decoded bytes equal the raw RIFF/WAVE body; MIME equals the pinned Content-Type audio/wav. No fabricated model/id/usage from the request or format defaults.

**Citations:** spec/types.md §§SpeechGenerationRequest, SpeechGenerationResponse, AudioPart; INV-010/011/012; serde §Omission rule 1–3.

#### 13. `goldens/azure/streaming.json` — QUALIFIED C

**Raw:** `bodies/azure.streaming/2026-09-04T11-49-08Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=100.

**Expected mapping:** Real response.created → start with its id/model; `Ok` + `.` → `Ok.`; response.completed supplies stop and usage. End.provider_data equals the entire terminal response. No duplicated done snapshots; no message continuation currently (C).

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id `resp_0e068f0b5b3b3328006a9ab0351f7c8193b60b4999486b2583`.

**Expected usage:** `{"input_tokens":10,"output_tokens":3,"total_tokens":13,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Trace:** 4 events = one start, 2 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. C applies to continuation.

**Citations:** BASE; USAGE; STREAM; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 14. `goldens/azure/streaming_tool_call.json` — QUALIFIED C

**Raw:** `bodies/azure.streaming_tool_call/2026-09-04T11-49-14Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; tools get_weather; max_tokens=200.

**Expected mapping:** Real start id/model; call_OPd8TLowrxtjxlYwCHMAHUuZ/get_weather is supplied by output_item.added. Empty input fragment plus {", city, ":", Paris, "} concatenate to {"city":"Paris"}. Never append full arguments.done again. Terminal completed with call → tool_call; exact terminal provider_data retained (C).

**Checked response:** assistant; parts tool_call; finish `tool_call`; model `gpt-4.1-mini`; id `resp_053b8db299f4619a006a9ab03a528c81949e2923397744f403`.

**Expected usage:** `{"input_tokens":49,"output_tokens":15,"total_tokens":64,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Trace:** 8 events = one start, 6 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. C applies to continuation.

**Citations:** BASE; USAGE; TOOLS; STREAM; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 15. `goldens/azure/system_prompt.json` — QUALIFIED C

**Raw:** `bodies/azure.system_prompt/2026-09-04T11-49-23Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; system present; max_tokens=100.

**Expected mapping:** System requests two words; raw answer `Ok noted.` is one TextPart, not a transformed version of the instruction (C).

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id `resp_0e4b9371c15c1938006a9ab043a9f0819492f2d95764ddae60`.

**Expected usage:** `{"input_tokens":21,"output_tokens":4,"total_tokens":25,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 16. `goldens/azure/tool_choice_required.json` — QUALIFIED C

**Raw:** `bodies/azure.tool_choice_required/2026-09-04T11-49-19Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; tools get_weather; max_tokens=200; tool_choice={"mode":"required"}.

**Expected mapping:** One raw function call: get_weather({"city":"London"}), id call_LJspgE6a5yXFcZ6qopLmzLEe. Required does not authorize replacing London with a requested/guessed city; completed plus call → tool_call (C).

**Checked response:** assistant; parts tool_call; finish `tool_call`; model `gpt-4.1-mini`; id `resp_0077ed63f844b176006a9ab03fb74c8193a5127c5b40e72c03`.

**Expected usage:** `{"input_tokens":50,"output_tokens":6,"total_tokens":56,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; TOOLS; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 17. `goldens/azure/tools.json` — QUALIFIED C

**Raw:** `bodies/azure.tools/2026-09-04T11-49-11Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; tools get_weather; max_tokens=200.

**Expected mapping:** One raw function call get_weather({"city":"Paris"}), id call_QomUHHAeDrg6R1ffXS93uR5w, not the output-item fc_ id. No empty TextPart is needed next to a real tool call (C).

**Checked response:** assistant; parts tool_call; finish `tool_call`; model `gpt-4.1-mini`; id `resp_0e98a7a203fb9c65006a9ab0379a608197822867321391459d`.

**Expected usage:** `{"input_tokens":49,"output_tokens":15,"total_tokens":64,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; TOOLS; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

#### 18. `goldens/azure/user_id.json` — QUALIFIED C

**Raw:** `bodies/azure.user_id/2026-09-04T11-49-25Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=50; user_id="lm15-case-user".

**Expected mapping:** Raw `Ok.` with stop. safety_identifier attribution adds no canonical content (C).

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id `resp_0950fda22adec4cb006a9ab045c9c48195b989b5874623303f`.

**Expected usage:** `{"input_tokens":10,"output_tokens":3,"total_tokens":13,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0}`.

**Citations:** BASE; USAGE; USER; spec/types.md §ContinuationState; MAP-7.8–9; spec/auth.md AUTH-10.

### azure-chat

#### 19. `goldens/azure-chat/basic_text.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.basic_text/2026-09-04T11-51-40Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=100.

**Expected mapping:** Raw `Ok.`, stop; preserve returned snapshot model gpt-4.1-mini-2025-04-14 rather than replacing it with the deployment requested.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKMkGdLZS2nXF5N7Sg2MiJDWxX8km`.

**Expected usage:** `{"input_tokens":10,"output_tokens":3,"total_tokens":13,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE.

#### 20. `goldens/azure-chat/content_filter_completion.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.content_filter_completion/2026-09-04T14-27-40Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=30.

**Expected mapping:** Preserve exact raw sentence `I will kill myself tonight.` with finish_reason=content_filter. Raw refusal is null: neither invent refusal text nor sanitize the captured content.

**Checked response:** assistant; parts text; finish `content_filter`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKPBFfdqREQWiX4j4JrCvgQh4E1IN`.

**Expected usage:** `{"input_tokens":41,"output_tokens":7,"total_tokens":48,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE.

#### 21. `goldens/azure-chat/models.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.models/2026-09-04T11-54-41Z.txt`.

**Expected mapping / comparison:** 207 entries, exactly raw data[].id in order; provider=azure-chat, api_family=openai_chat. No capability filtering or snapshot-id rewriting. No canonical_request: GET listing case.

**Citations:** MODELS; spec/auth.md AUTH-10 Azure row.

#### 22. `goldens/azure-chat/multi_turn_tool_result.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.multi_turn_tool_result/2026-09-04T11-51-49Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user→assistant→tool; tools get_weather; max_tokens=200.

**Expected mapping:** Single raw weather answer; request assistant call/tool-result linkage is valid. Do not include old call/result in the new response.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKMkPxY3YSf6SKF8Ul6uu8MExSi6O`.

**Expected usage:** `{"input_tokens":82,"output_tokens":17,"total_tokens":99,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; HISTORY.

#### 23. `goldens/azure-chat/prompt_cache_key.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.prompt_cache_key/2026-09-04T14-28-01Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; system present; max_tokens=16; cache={"mode":"auto","key":"lm15-azure-chat-cache-proof"}.

**Expected mapping:** Raw `Ok.`; input=4215, read=4096. cache_write_tokens is unreported and correctly absent, unlike Azure Responses’s explicit 0.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKPBaFkKyX6y7CqnkdesJQZlbwLb5`.

**Expected usage:** `{"input_tokens":4215,"output_tokens":3,"total_tokens":4218,"cache_read_tokens":4096,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; CACHE.

#### 24. `goldens/azure-chat/reasoning_high.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.reasoning_high/2026-09-04T14-19-50Z.txt`.

**Request context:** model `gpt-5-mini`; roles user; max_tokens=1000; reasoning={"effort":"high"}.

**Expected mapping:** Raw answer only, no separate reasoning text/state. reasoning_tokens=640 is telemetry, not grounds to create a ThinkingPart. Preserve model gpt-5-mini-2025-08-07 and exact answer.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-5-mini-2025-08-07`; id `chatcmpl-EKP3frGbmvNzdH64m4ZF15QbSfIDy`.

**Expected usage:** `{"input_tokens":50,"output_tokens":730,"total_tokens":780,"cache_read_tokens":0,"reasoning_tokens":640,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; THINK.

#### 25. `goldens/azure-chat/reasoning_low.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.reasoning_low/2026-09-04T14-19-47Z.txt`.

**Request context:** model `gpt-5-mini`; roles user; max_tokens=500; reasoning={"effort":"low"}.

**Expected mapping:** Raw `391`, no thinking field. Explicit reasoning_tokens=0 stays 0; no invented empty reasoning item as on Responses.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-5-mini-2025-08-07`; id `chatcmpl-EKP3cySTOxXDauRlV1oeukaxBAujL`.

**Expected usage:** `{"input_tokens":17,"output_tokens":11,"total_tokens":28,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; THINK.

#### 26. `goldens/azure-chat/response_format_json_schema.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.response_format_json_schema/2026-09-04T11-51-53Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=200; response_format=json_schema (schema/name/strict checked).

**Expected mapping:** Exact raw JSON text {"city":"Paris","country":"France"} remains text. Canonical schema is top-level schema/name/strict in request response_format, not provider-native nesting.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKMkTBew2ZFPdTlAssugF2wgG13m3`.

**Expected usage:** `{"input_tokens":48,"output_tokens":10,"total_tokens":58,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; FORMAT.

#### 27. `goldens/azure-chat/streaming.json` — QUALIFIED P

**Raw:** `bodies/azure-chat.streaming/2026-09-04T11-51-42Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=100.

**Expected mapping:** Synthesize start(model=gpt-4.1-mini), no id; `Ok` + `.` → `Ok.`. Merge finish chunk then usage-only chunk then DONE into one final stop. No chunk id/snapshot-model promotion (MAP-4, MAP-9.6); P concerns metadata only.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini`; id omitted by MAP-9.6.

**Expected usage:** `{"input_tokens":10,"output_tokens":3,"total_tokens":13,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Trace:** 4 events = one start, 2 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. P applies to raw-terminal representation.

**Citations:** BASE; USAGE; STREAM.

#### 28. `goldens/azure-chat/streaming_tool_call.json` — QUALIFIED P

**Raw:** `bodies/azure-chat.streaming_tool_call/2026-09-04T11-51-46Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; tools get_weather; max_tokens=200.

**Expected mapping:** Synthesize request-model start, no id. Name/id from first fragment: call_6rNEXc9iVd8OX9su8VvAXegq/get_weather; preserve empty input fragment. Remaining pieces parse to {"city":"Paris"}. Merge tool_calls finish, usage, DONE without overwriting with stop (P).

**Checked response:** assistant; parts tool_call; finish `tool_call`; model `gpt-4.1-mini`; id omitted by MAP-9.6.

**Expected usage:** `{"input_tokens":55,"output_tokens":15,"total_tokens":70,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Trace:** 8 events = one start, 6 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. P applies to raw-terminal representation.

**Citations:** BASE; USAGE; TOOLS; STREAM.

#### 29. `goldens/azure-chat/system_prompt.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.system_prompt/2026-09-04T11-51-55Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; system present; max_tokens=100.

**Expected mapping:** Raw `Okay, noted.` exactly, one TextPart. Do not normalize it to another two-word response.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKMkVticCXI7cNRdmU6c0C156wFXB`.

**Expected usage:** `{"input_tokens":21,"output_tokens":5,"total_tokens":26,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE.

#### 30. `goldens/azure-chat/tool_choice_required.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.tool_choice_required/2026-09-04T11-51-51Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; tools get_weather; max_tokens=200; tool_choice={"mode":"required"}.

**Expected mapping:** Two calls, in wire order: call_tb1jW6YxNqFae1lP7X4aKg8q/New York then call_yzdOQTipRadjqvniLT6icPVF/London, both get_weather. parallel is unspecified; do not collapse to a single required call.

**Checked response:** assistant; parts tool_call → tool_call; finish `tool_call`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKMkRCGFbKldFlUG27jDjmvtn75Sz`.

**Expected usage:** `{"input_tokens":47,"output_tokens":46,"total_tokens":93,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; TOOLS.

#### 31. `goldens/azure-chat/tools.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.tools/2026-09-04T11-51-44Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; tools get_weather; max_tokens=200.

**Expected mapping:** Raw call_fZXAZQEvpnlyn9bIgchIj5MR/get_weather with {"city":"Paris"}; content=null produces no extra empty text because call already satisfies nonempty-message invariant.

**Checked response:** assistant; parts tool_call; finish `tool_call`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKMkKdXi0DBfkAL4dbQjZlYRJiZwE`.

**Expected usage:** `{"input_tokens":55,"output_tokens":15,"total_tokens":70,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; TOOLS.

#### 32. `goldens/azure-chat/user_id.json` — NO DISCREPANCY

**Raw:** `bodies/azure-chat.user_id/2026-09-04T11-51-57Z.txt`.

**Request context:** model `gpt-4.1-mini`; roles user; max_tokens=50; user_id="lm15-case-user".

**Expected mapping:** Raw `Ok.`, stop; user attribution does not alter canonical response shape.

**Checked response:** assistant; parts text; finish `stop`; model `gpt-4.1-mini-2025-04-14`; id `chatcmpl-EKMkXRhvrjA9fAq6mmhaExF2Xyfa1`.

**Expected usage:** `{"input_tokens":10,"output_tokens":3,"total_tokens":13,"cache_read_tokens":0,"reasoning_tokens":0,"input_audio_tokens":0,"output_audio_tokens":0}`.

**Citations:** BASE; USAGE; USER.

### bedrock-chat

#### 33. `goldens/bedrock-chat/basic_text.json` — QUALIFIED R

**Raw:** `bodies/bedrock-chat.basic_text/2026-09-03T16-47-36Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; max_tokens=300.

**Expected mapping:** Whole raw content is a <reasoning> block followed by `ok.`. Byte-preserving TextPart matches; tag classification remains R. No secondary usage counters were sent.

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b-1:0`; id `chatcmpl-75eb654e-b5fc-491f-9bf4-7de71cea5b12`.

**Expected usage:** `{"input_tokens":70,"output_tokens":53,"total_tokens":123}`.

**Citations:** BASE; USAGE; THINK.

#### 34. `goldens/bedrock-chat/bearer_basic_text.json` — QUALIFIED R

**Raw:** `bodies/bedrock-chat.bearer_basic_text/2026-09-04T13-15-06Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; max_tokens=50.

**Expected mapping:** Whole raw content is a <reasoning> block followed by `ok`. Auth mechanism does not justify a different canonical representation; tag policy R. No inferred secondary counters.

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b-1:0`; id `chatcmpl-4757433a-a06d-4dd7-ad31-2e00520b2653`.

**Expected usage:** `{"input_tokens":70,"output_tokens":32,"total_tokens":102}`.

**Citations:** BASE; USAGE; THINK.

#### 35. `goldens/bedrock-chat/multi_turn_tool_result.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-chat.multi_turn_tool_result/2026-09-03T16-47-47Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user→assistant→tool; tools get_weather; max_tokens=400.

**Expected mapping:** Raw current text: The current weather in Paris is **Sunny, 22 °C**. Keep U+202F before °C. Caller-authored prior inline reasoning/call remains history; no current thinking/tool part.

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b-1:0`; id `chatcmpl-89566360-5ad8-4a4e-82f1-3ffdbeeedc91`.

**Expected usage:** `{"input_tokens":191,"output_tokens":19,"total_tokens":210}`.

**Citations:** BASE; USAGE; HISTORY.

#### 36. `goldens/bedrock-chat/reasoning_low.json` — QUALIFIED R

**Raw:** `bodies/bedrock-chat.reasoning_low/2026-09-03T16-47-40Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; max_tokens=300; reasoning={"effort":"low"}.

**Expected mapping:** Whole raw string `<reasoning>Just respond "Ok".</reasoning>Ok.` is preserved (R). Unlike most runtime cases this body explicitly reports cache_read=32 and input_audio=0; both retained. No reasoning count reported.

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b-1:0`; id `chatcmpl-a804d5de-6d09-471b-9657-b5fb3cc58e49`.

**Expected usage:** `{"input_tokens":70,"output_tokens":17,"total_tokens":87,"cache_read_tokens":32,"input_audio_tokens":0}`.

**Citations:** BASE; USAGE; THINK.

#### 37. `goldens/bedrock-chat/response_format_json_schema.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-chat.response_format_json_schema/2026-09-04T12-07-08Z.txt`.

**Request context:** model `deepseek.v3.2`; roles user; max_tokens=400; response_format=json_schema (schema/name/strict checked).

**Expected mapping:** deepseek.v3.2 returns exact text `{ "city": "Paris", "country": "France" }`; preserve spaces, no JSON-text reserialization.

**Checked response:** assistant; parts text; finish `stop`; model `deepseek.v3.2`; id `chatcmpl-598472e8-0d09-4184-9804-3bf6127bc434`.

**Expected usage:** `{"input_tokens":12,"output_tokens":15,"total_tokens":27}`.

**Citations:** BASE; USAGE; FORMAT.

#### 38. `goldens/bedrock-chat/streaming.json` — QUALIFIED R,P

**Raw:** `bodies/bedrock-chat.streaming/2026-09-03T16-47-38Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; max_tokens=300.

**Expected mapping:** Synthesized request-model start/no id; raw reasoning-tag string then `ok` concatenate as text (R). Empty role/obfuscation frames are non-content. Late usage survives and final stop appears once (P).

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b-1:0`; id omitted by MAP-9.6.

**Expected usage:** `{"input_tokens":70,"output_tokens":48,"total_tokens":118}`.

**Trace:** 4 events = one start, 2 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. P applies to raw-terminal representation.

**Citations:** BASE; USAGE; STREAM; THINK.

#### 39. `goldens/bedrock-chat/streaming_tool_call.json` — QUALIFIED R,P

**Raw:** `bodies/bedrock-chat.streaming_tool_call/2026-09-03T16-47-45Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; tools get_weather; max_tokens=400.

**Expected mapping:** Slot 0 receives raw tagged text and get_weather call chatcmpl-tool-a34a998178d47c49 with the complete {"city":"Paris"} string. Both survive, text before tool by MAP-9; no slot overwrite. Final tool_call/late usage are correct (R,P).

**Checked response:** assistant; parts text → tool_call; finish `tool_call`; model `openai.gpt-oss-20b-1:0`; id omitted by MAP-9.6.

**Expected usage:** `{"input_tokens":131,"output_tokens":36,"total_tokens":167}`.

**Trace:** 4 events = one start, 2 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. P applies to raw-terminal representation.

**Citations:** BASE; USAGE; TOOLS; STREAM; THINK.

#### 40. `goldens/bedrock-chat/system_prompt.json` — QUALIFIED R

**Raw:** `bodies/bedrock-chat.system_prompt/2026-09-03T16-47-52Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; system present; max_tokens=300.

**Expected mapping:** Whole raw reasoning-tag content plus `Sure, ok` preserved; do not enforce the system’s two-word constraint by deleting wire content. Tag classification R.

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b-1:0`; id `chatcmpl-78b3b8c8-51c5-4dec-bd4e-f112b040de21`.

**Expected usage:** `{"input_tokens":81,"output_tokens":170,"total_tokens":251}`.

**Citations:** BASE; USAGE; THINK.

#### 41. `goldens/bedrock-chat/tool_choice_required.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-chat.tool_choice_required/2026-09-04T12-07-06Z.txt`.

**Request context:** model `deepseek.v3.2`; roles user; tools get_weather; max_tokens=400; tool_choice={"mode":"required"}.

**Expected mapping:** deepseek.v3.2 emits chatcmpl-tool-9f6a4091a18bc72d/get_weather({"city":"ok"}). This odd but valid argument is the model’s output, not Paris; preserve it exactly. tool_calls → tool_call.

**Checked response:** assistant; parts tool_call; finish `tool_call`; model `deepseek.v3.2`; id `chatcmpl-1aa41798-9124-4353-82b9-95c7024cc40c`.

**Expected usage:** `{"input_tokens":307,"output_tokens":21,"total_tokens":328}`.

**Citations:** BASE; USAGE; TOOLS.

#### 42. `goldens/bedrock-chat/tools.json` — QUALIFIED R

**Raw:** `bodies/bedrock-chat.tools/2026-09-03T16-47-43Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; tools get_weather; max_tokens=400.

**Expected mapping:** Tagged content remains text (R), then chatcmpl-tool-9e257385bfed954a/get_weather({"city":"Paris"}). Exact call id/input retained and finish=tool_call.

**Checked response:** assistant; parts text → tool_call; finish `tool_call`; model `openai.gpt-oss-20b-1:0`; id `chatcmpl-dd595615-f710-4068-bca0-1b6310fef5c8`.

**Expected usage:** `{"input_tokens":131,"output_tokens":34,"total_tokens":165}`.

**Citations:** BASE; USAGE; TOOLS; THINK.

#### 43. `goldens/bedrock-chat/user_id.json` — QUALIFIED R

**Raw:** `bodies/bedrock-chat.user_id/2026-09-03T16-47-54Z.txt`.

**Request context:** model `openai.gpt-oss-20b-1:0`; roles user; max_tokens=300; user_id="lm15-case-user".

**Expected mapping:** Whole raw reasoning-tag content plus `ok` preserved (R); user attribution does not create another part.

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b-1:0`; id `chatcmpl-567baa3e-afd1-4d0f-8b70-3dbdc925e820`.

**Expected usage:** `{"input_tokens":70,"output_tokens":33,"total_tokens":103}`.

**Citations:** BASE; USAGE; THINK; USER.

### bedrock-mantle-chat

#### 44. `goldens/bedrock-mantle-chat/basic_text.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.basic_text/2026-09-04T13-55-48Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user; max_tokens=300.

**Expected mapping:** Separate raw message.reasoning → ThinkingPart, then content `ok` → TextPart. Do not use runtime’s inline-tag spelling or invent reasoning_tokens.

**Checked response:** assistant; parts thinking → text; finish `stop`; model `openai.gpt-oss-20b`; id `chatcmpl-31dc02e4-bfbe-489c-b2b3-ac05e37c66a9`.

**Expected usage:** `{"input_tokens":70,"output_tokens":26,"total_tokens":96}`.

**Citations:** BASE; USAGE; THINK.

#### 45. `goldens/bedrock-mantle-chat/models.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.models/2026-09-04T13-56-05Z.txt`.

**Expected mapping / comparison:** 55 entries, exactly raw data[].id in order; provider=bedrock-mantle-chat, api_family=openai_chat. Preserve unversioned ids and entries not callable on this Chat API; listing is advisory. No canonical_request: GET listing case. Door declaration is draft; this is only a canonical mapping finding, not door ratification.

**Citations:** MODELS; spec/auth.md AUTH-10 Mantle row (draft status acknowledged).

#### 46. `goldens/bedrock-mantle-chat/multi_turn_tool_result.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.multi_turn_tool_result/2026-09-04T13-55-55Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user→assistant→tool; tools get_weather; max_tokens=400.

**Expected mapping:** Current weather answer alone; preserve U+202F in 22 °C. Prior ThinkingPart has no continuation, so assistant-text replay is allowed by MAP-7.8; it does not imply a new thinking part in this response.

**Checked response:** assistant; parts text; finish `stop`; model `openai.gpt-oss-20b`; id `chatcmpl-8d344c39-5186-48c1-b43a-4cdfb8a4bef3`.

**Expected usage:** `{"input_tokens":184,"output_tokens":21,"total_tokens":205}`.

**Citations:** BASE; USAGE; HISTORY.

#### 47. `goldens/bedrock-mantle-chat/reasoning_low.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.reasoning_low/2026-09-04T13-55-51Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user; max_tokens=300; reasoning={"effort":"low"}.

**Expected mapping:** Separate reasoning `I just need to respond "ok".` then text `Ok.`. Effort low does not supply a numerical reasoning count.

**Checked response:** assistant; parts thinking → text; finish `stop`; model `openai.gpt-oss-20b`; id `chatcmpl-29bf2605-eff2-4b80-a6af-73df2ab60ee6`.

**Expected usage:** `{"input_tokens":70,"output_tokens":20,"total_tokens":90}`.

**Citations:** BASE; USAGE; THINK.

#### 48. `goldens/bedrock-mantle-chat/response_format_json_schema.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.response_format_json_schema/2026-09-04T13-55-59Z.txt`.

**Request context:** model `deepseek.v3.2`; roles user; max_tokens=400; response_format=json_schema (schema/name/strict checked).

**Expected mapping:** Exact raw JSON text `{"city": "Paris", "country": "France"}` remains TextPart (different whitespace from runtime’s capture).

**Checked response:** assistant; parts text; finish `stop`; model `deepseek.v3.2`; id `chatcmpl-31127608-f6e0-4ab7-8426-f62da1c65d73`.

**Expected usage:** `{"input_tokens":12,"output_tokens":14,"total_tokens":26}`.

**Citations:** BASE; USAGE; FORMAT.

#### 49. `goldens/bedrock-mantle-chat/streaming.json` — QUALIFIED P

**Raw:** `bodies/bedrock-mantle-chat.streaming/2026-09-04T13-55-49Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user; max_tokens=300.

**Expected mapping:** Three distinct raw delta.reasoning fragments concatenate into ThinkingPart, then content `ok.` into TextPart, both slot 0 in fixed kind order. Synthesized request-model start/no id; EOF after usage is sufficient: this capture has no DONE. One final stop (P).

**Checked response:** assistant; parts thinking → text; finish `stop`; model `openai.gpt-oss-20b`; id omitted by MAP-9.6.

**Expected usage:** `{"input_tokens":70,"output_tokens":90,"total_tokens":160}`.

**Trace:** 6 events = one start, 4 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. P applies to raw-terminal representation.

**Citations:** BASE; USAGE; STREAM; THINK.

#### 50. `goldens/bedrock-mantle-chat/streaming_tool_call.json` — QUALIFIED P

**Raw:** `bodies/bedrock-mantle-chat.streaming_tool_call/2026-09-04T13-55-54Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user; tools get_weather; max_tokens=400.

**Expected mapping:** Separate reasoning then named call chatcmpl-tool-aa3a53230bbea273/get_weather, input {"city":"Paris"}, both slot 0. Materialize thinking then tool, no overwrite; no invented id/name. EOF after late usage, one tool_call end (P).

**Checked response:** assistant; parts thinking → tool_call; finish `tool_call`; model `openai.gpt-oss-20b`; id omitted by MAP-9.6.

**Expected usage:** `{"input_tokens":131,"output_tokens":49,"total_tokens":180}`.

**Trace:** 4 events = one start, 2 deltas, one final end. Delta indexes, string fragments, call identity and final counters independently checked against every raw frame; materialization checked under MAP-9. P applies to raw-terminal representation.

**Citations:** BASE; USAGE; TOOLS; STREAM; THINK.

#### 51. `goldens/bedrock-mantle-chat/system_prompt.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.system_prompt/2026-09-04T13-56-01Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user; system present; max_tokens=300.

**Expected mapping:** Separate raw thinking plus final `Sure ok`; thought text does not count as answer text. No inline-tag parsing is involved.

**Checked response:** assistant; parts thinking → text; finish `stop`; model `openai.gpt-oss-20b`; id `chatcmpl-bd3c7033-4bd6-4e18-ab6e-241fc334abe8`.

**Expected usage:** `{"input_tokens":81,"output_tokens":205,"total_tokens":286}`.

**Citations:** BASE; USAGE; THINK.

#### 52. `goldens/bedrock-mantle-chat/tool_choice_required.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.tool_choice_required/2026-09-04T13-55-57Z.txt`.

**Request context:** model `deepseek.v3.2`; roles user; tools get_weather; max_tokens=400; tool_choice={"mode":"required"}.

**Expected mapping:** deepseek.v3.2 emits chatcmpl-tool-874bffd4b609cc36/get_weather({"city":"ok"}); keep exact argument and tool_call finish.

**Checked response:** assistant; parts tool_call; finish `tool_call`; model `deepseek.v3.2`; id `chatcmpl-8cd45061-3ba3-4171-971d-4f8c9198e5ed`.

**Expected usage:** `{"input_tokens":306,"output_tokens":21,"total_tokens":327}`.

**Citations:** BASE; USAGE; TOOLS.

#### 53. `goldens/bedrock-mantle-chat/tools.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.tools/2026-09-04T13-55-52Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user; tools get_weather; max_tokens=400.

**Expected mapping:** Raw separate reasoning, then chatcmpl-tool-9b4b0e4667f4f723/get_weather({"city":"Paris"}). content=null needs no empty TextPart because thinking/call already exist.

**Checked response:** assistant; parts thinking → tool_call; finish `tool_call`; model `openai.gpt-oss-20b`; id `chatcmpl-f538a95f-72eb-40ac-acbf-dbc348bcdefa`.

**Expected usage:** `{"input_tokens":131,"output_tokens":37,"total_tokens":168}`.

**Citations:** BASE; USAGE; TOOLS; THINK.

#### 54. `goldens/bedrock-mantle-chat/user_id.json` — NO DISCREPANCY

**Raw:** `bodies/bedrock-mantle-chat.user_id/2026-09-04T13-56-04Z.txt`.

**Request context:** model `openai.gpt-oss-20b`; roles user; max_tokens=300; user_id="lm15-case-user".

**Expected mapping:** Separate raw reasoning then `ok`; all thinking prose preserved verbatim. No exact secondary counts reported.

**Checked response:** assistant; parts thinking → text; finish `stop`; model `openai.gpt-oss-20b`; id `chatcmpl-8e2d7d70-b55b-48f8-b8ca-fcac889d3691`.

**Expected usage:** `{"input_tokens":70,"output_tokens":70,"total_tokens":140}`.

**Citations:** BASE; USAGE; THINK; USER.

## Parent-review actions

1. Review the C, R, P and F choices separately from the verified primary mappings.
   A rule change needs its own `changes/` evidence under AUTHORITY; this report
   supplies no ratification and changes no provenance.
2. Preserve the exact pinned content, ids, tool input objects and telemetry.
   In particular do not infer hidden reasoning counts, “repair” city values,
   or change stop/filter/tool-call words to reflect the requested behavior.
3. Treat endpoint coverage precisely: file download/delete and completed batch
   results are not canonical outputs of these particular goldens; missing
   receipt hashes and provider-support approval belong to separate reviews.

End of independent review. Completion requests parent review; nothing here
accepts this report or ratifies the scribe-draft fixtures.
