# Independent re-review — 2026-09-06 golden migration and the 88 new goldens

Delegation `10386d0a-7377-418d-bded-2388bdf5d3d7`. Role: canonical contract reviewer.
Disposition: **submitted for parent review. This is not approval.** The maintainer approves.

Repository: `lm15-contract` at HEAD `a4ae21b`. Pre-migration state: commit `cf298d2`.
No repository file was modified (`git status` clean after the review).

## Method

Read first: `changes/2026-09-06-decisions.md` (D5–D10, "Golden migration"),
`changes/2026-09-06-ratification.md`, `changes/2026-09-06-streamed-reasoning-state.md`,
`tools/migrate_goldens_2026_09_06.py`, both prior reviews under
`research/baseline-review/`, `spec/types.md` (ThinkingPart, ContinuationState,
ContinuationDelta, StreamEndEvent), `spec/invariants.md` INV-051,
`../lm15-python/docs/mapping-rules.md` MAP-3, MAP-7 rules 8–12, MAP-9.6.

Tools: three stdlib Python scripts under `/tmp/rereview/` (copied to the delegation
output directory). No lm15 import, no shim, no network, no `.env` access.

- `part1_migration.py` — for each of the 327 goldens, load old (`git show cf298d2:…`)
  and new. Apply my own implementation of transforms (a), (b), (d) to the old golden.
  Diff the result against the new golden leaf by leaf. Classify each remaining leaf
  difference as (c) or (e). Print anything else with its JSON path. The script does not
  reuse code from `tools/migrate_goldens_2026_09_06.py`.
- `part1c_provider_data.py` — for all 28 goldens that gained `end.provider_data`,
  parse the pinned body (SSE), pick the last frame that carries `usage` (else the frame
  that carries the finish reason), and compare it for equality with the golden's
  `provider_data`.
- `part2_rereview.py` — for each of the 88 new goldens, derive the expected canonical
  response (and, for streams, the expected event trace) from the pinned body with an
  independent dialect parser (Responses, Chat, Messages). Compare for full equality with
  the golden. Materialize the golden's events with the MAP-9 algorithm and compare with
  `canonical_response` (INV-051). Walk the golden for D5, D7, D8, D9, D10 violations.
  Endpoint goldens (models, files, batch, image, speech, live): assert byte-identity
  with `cf298d2`, then run targeted checks (model id list and order, D6 fold, epoch→UTC).
- Mutation test: seven deliberate corruptions (usage off by one, tool argument changed,
  placeholder text and `message_id` state re-added, door name as continuation provider,
  `provider_data` dropped, text changed, files readiness flipped). The checker reported
  every one. See the transcript in this session.
- Also ran `tools/check_provenance.py` (stdlib only): `OK (696 file(s) scanned)`.

## Part 1 — migration verification (327 goldens)

Result: **no out-of-scope difference in any golden.** 189 goldens changed, 138 unchanged.
The old→new difference of every golden is a subset of (a)–(e).

### Counts per transform

| Transform | Leaf changes | Files |
|---|---:|---:|
| (a) removed message-level continuation entries | 172 (openai:response_id 73, anthropic:message_id 64, gemini:response_id 35) | 169 |
| (a) removed message-level ContinuationDelta events (no `part_index`) | 10 (anthropic:message_id 8, gemini:response_id 2) | 10 |
| (b) removed `redacted` keys (all were `true`) | 8 | 7 |
| (b) ThinkingPart/ThinkingDelta text `[redacted]` → `""` | 12 (8 deltas/parts flagged + 4 stream-side: 2 deltas, 2 materialized parts in `meta-anthropic/streaming_tool_call`) | 8 |
| (c) added `provider_data` on `end` events | 28 | 28 |
| (d) Gemini tool-call id `fc_<i>` → `tool_call_<i>` | 3 | 3 (`gemini/tools`, `tool_config_auto`, `tool_config_any`) |
| (e) provenance: sentence appended to `reviewed` | 94 | 94 (all frozen) |
| (e) provenance: sentence appended to `evidence` | 95 | 95 (all drafts) |

Where the (a) entries sat in the old goldens: 166 under `canonical_response`, 6 under
`entries` (batch goldens). None sat in `canonical_request` history.

Changed files per directory: anthropic 35, openai 45, gemini 34, azure 11,
moonshotai-anthropic 10, deepseek-anthropic 9, meta-anthropic 9, meta 8,
moonshotai-responses 8, openai_chat 5, azure-chat 2, bedrock-chat 2,
bedrock-mantle-chat 2, deepseek 2, meta-chat 2, moonshotai 2, zai 2, xai 1.

### Consistency checks (all pass)

- Every golden whose content changed carries exactly one appended note; no unchanged
  golden carries a note. Provenance key sets are identical old vs new in all 327 files.
- Note placement: frozen goldens (110 at `cf298d2`) got the note on `reviewed`; drafts on
  `evidence`. Correct in all 189 cases.
- Note text: the numbers in each note ("removed N message-level …", "rewrote N …",
  "end provider_data added") agree with the observed transform in all 189 files.
- Residue: no `response_id`/`message_id` continuation kind, no `redacted` key, and no
  `[redacted]` thinking text remains in any golden's content (provenance text excluded).
- The three Gemini goldens carry two appended sentences on `reviewed` (the migration
  note, then the MAP-9/INV-051 minted-id note from commit `a4ae21b`). Their pinned bodies
  contain `functionCall` blocks without an `id`; `tool_call_0` is the MAP-9 minted id.

### (c) provider_data vs pinned body — all 28, not a sample

28/28 `end.provider_data` objects equal, verbatim, the pinned-body frame that supplied
`usage`. Covered: chat dialect (azure-chat 2, bedrock-chat 2, bedrock-mantle-chat 2,
deepseek 2, meta-chat 2, moonshotai 2, openai_chat 5, zai 2), Anthropic family
(anthropic 2, deepseek-anthropic 2, meta-anthropic 2, moonshotai-anthropic 2), xAI 1.
In every case the frame was the usage frame (the finish fallback was never needed).

Observation, not a finding: `openai_chat/streaming.json` (Groq body) carries a
top-level `usage` on two frames (the finish chunk and the usage-only chunk). The golden
holds the later usage-only chunk. MAP-3's coalescer reading (later non-null fills) makes
that the frame that "supplied" usage. The rule text could name "the last such frame" to
remove the ambiguity.

### Out-of-scope differences

**None.**

## Part 2 — the 88 new goldens

All 88 are `source: scribe-draft`, none has a `reviewed` line. Prior open items and
how the current goldens stand:

- **D1 (Meta Responses streams dropped the reasoning item)** — fixed before `cf298d2`
  by `changes/2026-09-06-streamed-reasoning-state.md`. Both traces now emit
  `ThinkingDelta("")` at `output_item.added` and a `openai:reasoning_item`
  ContinuationDelta at `output_item.done`; materialized response equals the
  `response.completed`-derived response (INV-051, MAP-7.9).
- **D2/Q3 (redacted flag, placeholder text)** — resolved by D5. All seven Meta-Messages
  complete goldens and the tool stream now carry `text: ""` plus
  `anthropic:redacted_thinking {"data": <blob>}`; no `redacted` key, no `[redacted]`.
  Blobs equal the body byte for byte. Stream shape: `ThinkingDelta("")` at
  `content_block_start`, `ContinuationDelta(part_index=i)` at `content_block_stop`
  (MAP-7.11).
- **Q1 / C (continuation namespace)** — resolved by D7. Every continuation in the 88
  goldens names the dialect: `openai` on meta and azure, `anthropic` on meta-anthropic.
  No chat-dialect golden carries continuation state (none is on the wire).
- **Q2 / C (message-level id state)** — resolved by D8. No `response_id`/`message_id`
  state or delta remains; `id` lives on `Response.id` and `start.id`.
- **P (chat stream terminal frame)** — resolved by D9. All 14 streams among the 88
  have one final `end` with `provider_data` as a JSON object equal to the usage frame.
- **F (Azure files `pending`)** — resolved by D6. `azure/files.json`: upload raw
  `pending` → `pending`; get raw `processed` → `ready`; list item `processed` → `ready`.
  `meta/files.json`: raw `uploaded` → `pending` on upload, get, and the list item.
- **R (Bedrock runtime inline `<reasoning>`)** — resolved by D10. All eight
  `bedrock-chat` bodies with inline tags keep the whole string as TextPart/TextDelta;
  no ThinkingPart on the runtime door. `bedrock-mantle-chat` keeps the typed
  `reasoning` field as ThinkingPart (MAP-7.12).

Re-check of text, tool ids/arguments, finish reasons, and usage: the body-derived
response equals the golden's `canonical_response` in all 75 conversational goldens
(61 complete, 14 stream); the 13 endpoint goldens are covered below. Nothing regressed relative to the prior reviews.

### Per-file table

Columns: kind; migration transforms applied to this file (from Part 1); what was
checked; verdict. "unchanged" means byte-identical to `cf298d2`.

| Golden | Kind | Migration | Checked | Verdict |
|---|---|---|---|---|
| `meta/basic_text.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta/files.json` | endpoint | — | D6 fold, epoch→UTC; unchanged | **REVIEWED-OK** |
| `meta/image_edit.json` | endpoint | — | unchanged since cf298d2; targeted check | **REVIEWED-OK** |
| `meta/image_gen.json` | endpoint | — | unchanged since cf298d2; targeted check | **REVIEWED-OK** |
| `meta/models.json` | endpoint | — | id list = body, provider; unchanged | **REVIEWED-OK** |
| `meta/multi_turn_tool_result.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta/reasoning_low.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta/reasoning_summary.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta/response_format_json_schema.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta/streaming.json` | stream | — | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `meta/streaming_tool_call.json` | stream | — | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `meta/system_prompt.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta/tools.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta/user_id.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-chat/basic_text.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-chat/models.json` | endpoint | — | id list = body, provider; unchanged | **REVIEWED-OK** |
| `meta-chat/multi_turn_tool_result.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-chat/reasoning_low.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-chat/response_format_json_schema.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-chat/streaming.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `meta-chat/streaming_tool_call.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `meta-chat/system_prompt.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-chat/tools.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-chat/user_id.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-anthropic/basic_text.json` | complete | a:1 entry, b:1 flag, b:1 text | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-anthropic/models.json` | endpoint | — | id list = body, provider; unchanged | **REVIEWED-OK** |
| `meta-anthropic/multi_turn_tool_result.json` | complete | a:1 entry, b:1 flag, b:1 text | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-anthropic/reasoning_low.json` | complete | a:1 entry, b:1 flag, b:1 text | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-anthropic/response_format_json_schema.json` | complete | a:1 entry, b:1 flag, b:1 text | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-anthropic/streaming.json` | stream | a:1 entry, a:1 event, c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `meta-anthropic/streaming_tool_call.json` | stream | a:1 entry, a:1 event, b:4 text, c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `meta-anthropic/system_prompt.json` | complete | a:1 entry, b:1 flag, b:1 text | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-anthropic/tools.json` | complete | a:1 entry, b:2 flag, b:2 text | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `meta-anthropic/user_id.json` | complete | a:1 entry, b:1 flag, b:1 text | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/basic_text.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/batch.json` | endpoint | — | unchanged since cf298d2; targeted check | **REVIEWED-OK** |
| `azure/content_filter_completion.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/files.json` | endpoint | — | D6 fold, epoch→UTC; unchanged | **REVIEWED-OK** |
| `azure/live_text.json` | endpoint | — | unchanged since cf298d2; targeted check | **REVIEWED-OK** |
| `azure/models.json` | endpoint | — | id list = body, provider; unchanged | **REVIEWED-OK** |
| `azure/multi_turn_tool_result.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/prompt_cache_key.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/reasoning_high.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/reasoning_low.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/response_format_json_schema.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/speech_gen.json` | endpoint | — | unchanged since cf298d2; targeted check | **REVIEWED-OK** |
| `azure/streaming.json` | stream | — | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `azure/streaming_tool_call.json` | stream | — | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `azure/system_prompt.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/tool_choice_required.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/tools.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure/user_id.json` | complete | a:1 entry | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/basic_text.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/content_filter_completion.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/models.json` | endpoint | — | id list = body, provider; unchanged | **REVIEWED-OK** |
| `azure-chat/multi_turn_tool_result.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/prompt_cache_key.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/reasoning_high.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/reasoning_low.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/response_format_json_schema.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/streaming.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `azure-chat/streaming_tool_call.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `azure-chat/system_prompt.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/tool_choice_required.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/tools.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `azure-chat/user_id.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-chat/basic_text.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8; D10 literal | **REVIEWED-OK** |
| `bedrock-chat/bearer_basic_text.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8; D10 literal | **REVIEWED-OK** |
| `bedrock-chat/multi_turn_tool_result.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-chat/reasoning_low.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8; D10 literal | **REVIEWED-OK** |
| `bedrock-chat/response_format_json_schema.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-chat/streaming.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9; D10 literal | **REVIEWED-OK** |
| `bedrock-chat/streaming_tool_call.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9; D10 literal | **REVIEWED-OK** |
| `bedrock-chat/system_prompt.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8; D10 literal | **REVIEWED-OK** |
| `bedrock-chat/tool_choice_required.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-chat/tools.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8; D10 literal | **REVIEWED-OK** |
| `bedrock-chat/user_id.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8; D10 literal | **REVIEWED-OK** |
| `bedrock-mantle-chat/basic_text.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-mantle-chat/models.json` | endpoint | — | id list = body, provider; unchanged | **REVIEWED-OK** |
| `bedrock-mantle-chat/multi_turn_tool_result.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-mantle-chat/reasoning_low.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-mantle-chat/response_format_json_schema.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-mantle-chat/streaming.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `bedrock-mantle-chat/streaming_tool_call.json` | stream | c:end pd | trace vs body; INV-051 materialize; D5 D7 D8 D9 | **REVIEWED-OK** |
| `bedrock-mantle-chat/system_prompt.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-mantle-chat/tool_choice_required.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-mantle-chat/tools.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |
| `bedrock-mantle-chat/user_id.json` | complete | — | text, ids/args, finish, usage vs body; D5 D7 D8 | **REVIEWED-OK** |

Totals: **88 REVIEWED-OK, 0 FINDING.**

### Notes on the endpoint goldens

`meta/image_edit`, `meta/image_gen`, `azure/batch`, `azure/speech_gen`, `azure/live_text`
were not re-derived byte by byte in this pass. They are byte-identical to `cf298d2`, and
the prior reviews derived them from the pinned bodies (digests, decoded WAV bytes, all
16 live frames, four batch substeps). No decision touched their fields. The five model
lists were re-derived (7/7/7/207/207/55 ids, order, provider string).

## Goldens NOT ready for a `reviewed` line

**None among the 88** on canonical-mapping grounds.

Statements the maintainer should keep in view when adding the line:

1. These 88 captures are dated 2026-09-03/04, before D11. They stand as live evidence
   without an exchange hash (grandfathered, stated in AUTHORITY.md). The `reviewed` line
   does not cure that; it records the canonical review.
2. The harness gate (`harness/check.py --shim python …`) runs the implementation and was
   out of my scope. The parent should confirm it is green at HEAD.
3. The MAP-3 `provider_data` wording ("the frame that supplied usage") is ambiguous
   when two frames carry usage (Groq). The goldens follow the coalescer reading. A
   one-clause clarification would remove the ambiguity; no golden changes.

## Files

- Report: `/tmp/lm15-golden-rereview-2026-09-06.md` (this file).
- Scripts and raw output: `/tmp/rereview/part1_migration.py`, `part1_out.txt`,
  `part1_per_file.json`, `part1c_provider_data.py`, `part1c_out.txt`,
  `part2_rereview.py`, `part2_out.txt`, `part2_results.json`.

Completion requests parent review. I did not accept my own work, did not modify the
repository, and do not claim approval.
