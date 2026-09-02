# Independent review — 2026-09-02

Reviewer: independent of every author. Method: for each golden, open the
pinned body and the case first, derive the expected canonical value by
hand, then open the golden. For each design-pass entry, attack from five
lenses, then trace each rule to a receipt file.

Everything ran offline. No provider was called. No fixture was edited.

## 1. Baseline

Checkout: `lm15-contract` HEAD `176d903` (working tree clean).

```
harness/check.py --shim python --direction all
  request    pass 143  fail 0  skip 1
  response   pass 129  fail 0  skip 1
  stream     pass  10  fail 0  skip 0
  error      pass  18  fail 0  skip 0
  serde      pass 109  fail 0  skip 0
  auth       pass  14  fail 0  skip 0
  models     pass  14  fail 0  skip 0
  live       pass  21  fail 0  skip 0
  files      pass  23  fail 0  skip 0
  batch      pass  26  fail 0  skip 0
  generation pass  14  fail 0  skip 0
  video      pass  24  fail 0  skip 0
  cache      pass   9  fail 0  skip 0
tools/audit.py            OK (1 allowlisted orphan pending burn-down)
tools/check_provenance.py OK (181 files scanned)
harness/selftest.py       OK (baseline green, 25/25 mutations caught)
```

### The population of "60 drafts"

The brief says 60 goldens have `provenance.source == "scribe-draft"` and no
`reviewed` line. That set has **27** members. Two other sets fill the gap
to 60:

- **29** goldens have **no provenance block at all** (every `models`,
  `files`, `batch`, `video`, `image_gen`, `image_edit`, `speech_gen`,
  `live_*` golden). `tools/check_provenance.py` scans `cases/`, `errors/`,
  `auth/`, `serde/` — it never opens `goldens/`. Its "OK" says nothing
  about goldens.
- **4** goldens carry `source: "derived"` (`xai.basic_text`,
  `xai.streaming`, `xai.tools`, `xai.models`). The word `reviewed` appears
  inside their `evidence` string, not as a key. Nobody's review is named.

I reviewed all 60. The 33 non-scribe goldens get a form flag on top of
their content verdict.

## 2. Golden verdicts

Legend: AGREE = golden says what the body says, every counter, every
state. FLAG = a difference, with path. Notes in parentheses are
observations for humans, not flags against the golden.

### Scribe drafts (27)

| golden | verdict | detail |
|---|---|---|
| anthropic.cache_history | AGREE | Body `usage.input_tokens: 3`, `cache_creation_input_tokens: 3275`. Golden `input_tokens: 3`, `cache_write_tokens: 3275`, `total_tokens: 9`. (Note: canonical `input_tokens` excludes cached tokens on Anthropic but includes them on OpenAI and Gemini — see §3 MAP-6 lens d.) |
| anthropic.reasoning_adaptive | AGREE | Empty `thinking` block with signature → `ThinkingPart("")` + `thinking_signature` continuation. `thinking_tokens: 82` → `reasoning_tokens: 82`. |
| anthropic.reasoning_budget | AGREE | Thinking text, signature, text part, 56/220/276, reasoning 188 — all match. |
| anthropic.reasoning_off | AGREE | No `output_tokens_details` in body → `reasoning_tokens` absent. Correct: absent, not 0. |
| anthropic.tool_choice_builtin | AGREE | `server_tool_use` + `web_search_tool_result` (9 results) dropped per MAP-1, same as reviewed `anthropic.web_search`. Text + 1 citation match `citations[0]`. (Note: `usage.server_tool_use.web_search_requests: 1` is a billed unit with no canonical slot.) |
| gemini.cache | AGREE | All four bodies map field by field. (Notes for ports: `model` `models/gemini-2.5-flash` → `gemini-2.5-flash` and `createTime` `…59.749060Z` → `…59Z` are a prefix strip and a truncation, not a round; neither rule is in spec/types.md.) |
| gemini.cache_history_fallback | AGREE | Body has no `cachedContentTokenCount`; golden has no `cache_read_tokens`. Matches MAP-3 ("secondary Gemini counters stay verbatim"). (Note: the case description says the fallback's outcome "is visible in usageMetadata.cachedContentTokenCount". In this body it is not visible; absent reads as "not reported", not as 0.) |
| gemini.cache_resource | AGREE | `cachedContentTokenCount: 3580` → `cache_read_tokens: 3580`; `promptTokenCount: 3598` includes it. |
| gemini.reasoning_off | AGREE | No `thoughtsTokenCount` → `reasoning_tokens` absent. |
| gemini.response_json_schema | **FLAG** | `bodies/gemini.response_json_schema/2026-09-02T13-20-07Z.txt` `candidates[0].content.parts[0].thoughtSignature` (a 176-char signature on the answer text part) is **dropped**. Golden `$.canonical_response.message.parts[0]` has no `continuation`; no `_lm15_unmapped` record. Expected: `continuation: [{provider: gemini, kind: thought_signature, data: {value: "Em0K…"}}]` on the text part — the corpus already uses that kind on tool-call parts (`gemini.tool_config_any`). Cause: `lm15-python/lm15/providers/gemini.py:793-806` reads `thoughtSignature` only when `thought: true`; the `elif "text" in part` branch at `:802` ignores it. Reference bug and silent drop. |
| gemini.service_tier | AGREE | (Note: `usageMetadata.serviceTier: "flex"` — the served tier changes the price and has no canonical response slot.) |
| gemini.thinking_level | **FLAG** | Same drop. `bodies/gemini.thinking_level/2026-09-02T12-50-16Z.txt` `candidates[0].content.parts[1].thoughtSignature` (528 chars, on the final text part) absent from golden `$.canonical_response.message.parts[1]`. The thought part itself carries no signature in this body, so the golden pins a 3.x reply with **no** replay state at all. MAP-7 rule 8 says Gemini signatures are replay state. Also: `_parse_candidate_parts` requires `part.get("text")` truthy to classify a thought (`gemini.py:793`); a `{thought: true, text: "", thoughtSignature: …}` part would become `TextPart("")` and lose its signature too. |
| openai.cache_off | AGREE | 3091/6/3097, cache read 0, write 0, reasoning 0 — all verbatim. (Note: body echoes `prompt_cache_retention: "24h"` and `prompt_cache_options.ttl: "30m"` on gpt-5.6-sol — see §3 MAP-6 receipt check.) |
| openai.cache_stable | AGREE | `cache_write_tokens: 3088` matches; the system prompt is the 3k-token notes block, so the write size is right. |
| openai.prompt_cache_breakpoint | AGREE | 3087/6/3093, read 3066, write 18. |
| openai.reasoning_off | AGREE | `reasoning_tokens: 0` reported → 0, not absent. |
| openai.reasoning_replay | AGREE | Reasoning item `content: []`, `summary: []`, `encrypted_content` → `ThinkingPart("")` with `reasoning_item {id, encrypted_content}` verbatim. Consistent with the amended reviewed `openai.reasoning`. |
| openai.tool_choice_allowed | AGREE | `call_id` is the part id; the `fc_…` item id is dropped as in reviewed `openai.parallel_tool_calls`. |
| openai.tool_choice_builtin | AGREE | Both `url_citation` slices verified against `start_index`/`end_index` on the text. `web_search_call` dropped per MAP-1. |
| openai_chat.cache_off | AGREE | `audio_tokens` 0/0 → `input_audio_tokens`/`output_audio_tokens` 0. `accepted/rejected_prediction_tokens` have no slot. |
| openai_chat.cache_stable | AGREE | write 3088. |
| openai_chat.logprobs | AGREE | `top_logprobs: []` → `top` omitted (default `[]`); `cache_write_tokens` absent in body → absent. |
| openai_chat.prompt_cache_breakpoint | AGREE | write 3084. |
| openai_chat.reasoning_off | AGREE | Groq body has no token details → only three counters. |
| openai_chat.structured_output | AGREE | |
| openai_chat.tool_call_unnamed | **FLAG (low)** | (1) `$.partial_response.id` absent; every chunk carries `"id": "chatcmpl-hand-authored-map9"`. The reviewed `openai_chat.streaming` golden drops the id the same way, and non-stream `openai_chat` goldens keep it. The precedent is consistent; the drop is still a wire fact that vanishes without a rule naming it. (2) `$.events[1].delta.part_index` (text) and `$.events[2..4].delta.part_index` (tool_call) are both `0`. The trace is what the reference emits, but no spec text says a text part and a tool call may share an index, nor in what order they assemble — see §3 MAP-9 lens c. Raise, partial text, usage 48/11/59 and `finish_reason: tool_call` all match the body. |
| xai.structured_output | AGREE | `prompt 254 + completion 9 + reasoning 111 = total 374` — xAI's `completion_tokens` **excludes** reasoning; golden keeps all four verbatim. (See §3 MAP-7 lens d.) |

### "derived" goldens (4)

| golden | verdict | detail |
|---|---|---|
| xai.basic_text | AGREE; **FLAG (form)** | Content matches (639/1/828, cached 512, reasoning 188, thinking + text). Provenance `source: "derived"` is not a scribe-draft value and carries no `reviewed` key. |
| xai.streaming | AGREE; **FLAG (form)** | Ten deltas and the end usage match the SSE. `canonical_response.id` absent although every chunk carries `e35e6c83-…` (same precedent as above). Thinking and text deltas both at `part_index 0`. |
| xai.tools | AGREE; **FLAG (form)** | `content: ""` next to a tool call yields no empty TextPart — consistent with reviewed openai_chat tool goldens. |
| xai.models | AGREE; **FLAG (form)** | 12 ids in body order. |

### Goldens with no provenance block (29)

Every row below also carries **FLAG (form): no provenance block; not scanned by check_provenance.py**.

| golden | verdict | detail |
|---|---|---|
| anthropic.models | AGREE | 10 ids, in order. Body fields `max_input_tokens`, `max_tokens`, `capabilities` are not mapped; changes/2026-08-31-list-models-provisional.md limits the mapping to id/provider/api_family, so this is a stated drop. |
| claude-code.models | AGREE | (Note: case lives at `cases/claude_code/`, golden at `goldens/claude-code/`; the harness bridges the underscore/hyphen.) |
| gemini.models | AGREE | 53 ids, `models/` stripped. |
| openai.models | AGREE | 132 ids. |
| openai-codex.models | AGREE | 9 slugs. |
| openai_chat.models | AGREE | 14 ids. |
| anthropic.files | AGREE | `downloadable: false` verbatim; `expires_at: null` → absent. |
| gemini.files | AGREE | `downloadable: false` is **derived** from `source: "UPLOADED"`; the rule lives only in changes/2026-08-31-files-lifecycle.md:49, not in spec/types.md ("provider-stated capability or null"). The case description says "no download endpoint"; the same changes entry says that claim "was overturned live". Stale description. |
| openai.files | AGREE | Epochs verified: 1788215944 → 2026-08-31T22:39:04Z, 1790796140 → 2026-09-30T19:22:20Z. `next_cursor` = `last_id` under `has_more: true`. |
| anthropic.batch | AGREE | Results JSONL order 1,0 → entries 0,1. `ended` → `completed`. |
| gemini.batch | AGREE | `BATCH_STATE_PENDING` → `queued`; inline responses in key order. |
| openai.batch | AGREE | `validating` → `queued`; both `encrypted_content` digests recomputed and match (`sha256:f8971e…`, `sha256:b23f20…`). |
| gemini.video | AGREE | `data` digest = sha256 of the base64 text of `gemini-video.mp4` (verified). (Note: a body of `{"name": …}` with no `done` becomes `running` on both submit and status; no text states that rule.) |
| openai.video | AGREE | Digest verified. `in_progress` → `running`. |
| xai.video | **FLAG (low)** | `$.part.media_type: "video/mp4"` is hard-coded (`lm15-python/lm15/providers/xai.py:246`); the terminal body carries no MIME and no content-type was captured. spec/types.md says media types come "from the wire, never assumed". The value equals `VideoPart`'s default, so no port can be caught wrong by it. `video.duration: 8` and `usage.cost_in_usd_ticks` have no slot. |
| gemini.image_gen | AGREE | Digest verified; narration text kept. (Note: `candidatesTokensDetails[IMAGE] 1290` has no slot.) |
| openai.image_gen | AGREE | `output_format: "jpeg"` → `image/jpeg`; JPEG magic bytes verified. |
| xai.image_gen | AGREE | `usage` is ticks only → `usage` omitted entirely. |
| openai.image_edit | AGREE | Digest verified. |
| xai.image_edit | AGREE | Digest verified. |
| gemini.speech_gen | **FLAG (low)** | `usageMetadata.candidatesTokensDetails[0] = {modality: AUDIO, tokenCount: 59}` is reported; golden `$.response.usage` has no `output_audio_tokens`. The canonical slot exists and the OpenAI adapters fill it (`openai.live_audio`: 24). |
| openai.speech_gen | AGREE | `audio/mpeg` from the pinned header; digest verified. |
| gemini.live_text | **FLAG (low)** | `$.events[12][0].usage` lacks `output_audio_tokens`; frame 12 reports `responseTokensDetails: [{modality: AUDIO, tokenCount: 28}]`. `sessionResumptionUpdate` (frame 2) → `[]` with no canonical event; a resumable handle is lost. |
| gemini.live_tools | **FLAG (low)** | Same: `$.events[19][0].usage` lacks `output_audio_tokens` (body: AUDIO 56). Tool call `fc_7930085371853702299` → `tool_call` event matches. |
| gemini.live_interrupt | AGREE | `interrupted: true` → `interrupted`; no `turn_end`. |
| openai.live_text | AGREE | `response.done` usage 13/5/18 with all details → `turn_end`. |
| openai.live_tools | **FLAG** | `$.events[21] = []` for the `response.done` of the function-call response. That frame reports `usage {total 75, input 54, output 21}`. Those 75 billed tokens appear in no canonical event. The case description states "function_call response.done ends NO turn"; the design chose it, the usage is still lost. |
| openai.live_interrupt | **FLAG** | `$.events[27] = [{"type": "interrupted"}]` for `response.done` `status: cancelled` with `usage {total 143, input 127, output 16}`. The description says "(usage dropped)". 143 billed tokens vanish. |
| openai.live_audio | AGREE | `output_token_details.audio_tokens: 24` → `output_audio_tokens: 24`. |

What I tried that did not break anything: every token counter in every
body was compared by hand against the golden, including absent-vs-0 on
every Anthropic `output_tokens_details`, Gemini `thoughtsTokenCount`,
Gemini `cachedContentTokenCount`, and OpenAI `cache_write_tokens`
(absent in `openai_chat.logprobs`, present elsewhere). Every citation
slice, every media digest, every epoch timestamp, every stream delta
sequence, and every batch re-sort was recomputed. I looked for parts in
bodies with no golden counterpart; apart from the flags above, every
absent part is covered by MAP-1 with a reviewed precedent.

## 3. Design-pass entries

### changes/2026-09-01-caching-design.md → MAP-6

**Receipt check.**

- `research/caching/20-results.json` holds 101 cells. HTTP 200 on six
  wires (openai-responses, openai-chat, anthropic, gemini, xai, groq);
  openrouter 9×401. MAP-6 in mapping-rules.md:139 says "measured
  2026-09-01 across 13 providers". Six were measured; the other seven in
  `10-facts.md` (Bedrock, Vertex, Azure, DeepSeek, Fireworks, vLLM,
  SGLang, Mistral, Together) are doc-read. **FLAG: the word "measured"
  overstates the receipt.**
- Rule 3 (trailing marker writes and never reads): receipted —
  `anthropic/automatic-toplevel/warm` ×3 cw=3267 cr=0;
  `openai-responses/implicit/warm` ×3 cw=3088 cr=0.
- Rule 2 (`mode=off` on 5.6+): receipted by `openai.cache_off` body
  (cw=0).
- Rule 5 (`retention="long"` RAISES on OpenAI 5.6+ because "30m is the
  only value"): rests on a doc line (`10-facts.md:55`, `:117`). No live
  cell sends `prompt_cache_retention` to a 5.6 model. The pinned 5.6
  bodies (`openai.cache_off`, `openai.cache_stable`,
  `openai.prompt_cache_breakpoint`) all echo
  `"prompt_cache_retention": "24h"` next to `"ttl": "30m"`. **FLAG: the
  receipt points the other way or is ambiguous; a raise built on it may
  be refusing a knob the server accepts.**
- Rule 10 / item 10 ("`prefix="stable"` is the one-line fix" for
  fan-out): the breakpoint receipts show warm calls still write the
  suffix (`openai-responses/breakpoint/warm` cr=3070 **cw=18**, ×3). The
  adapter leaves `prompt_cache_options.mode` implicit next to the mark.
  No cell measures breakpoint + `mode: explicit`. **FLAG: the fix is
  partial and the rule does not say so.**
- Entry §"Receipts of note" says `anthropic.cache_history` "turn 1
  writes 3271"; the pinned body says 3275. Minor number drift.
- 40-attack.md is labelled self-review. It lists streaming usage, batch,
  and media prefixes as unmeasured. Still unmeasured.

**Lenses.**

- (a) Cold learner. Strongest objection: `mode="auto"` means "stable"
  which on OpenAI 5.6+ **moves the system prompt out of `instructions`
  into the first input item** (trade-off 3 in the entry). A learner who
  adds `cache=CacheConfig()` changes the wire shape of their request in
  a way that has nothing to do with caching. Sustained as a
  documentation gap, not a rule error.
- (b) Library author. Objection: `CachedPrefix.request()` sets
  `prefix_until_index` to the end of the prefix; on OpenAI that index
  must land on a text block or the adapter RAISES. A library that builds
  prefixes ending in tool results cannot use `lm.cache` on OpenAI.
  Sustained; stated in 40-attack scenario 3, not in MAP-6.
- (c) Go/Rust implementer. Objection: rule 4 says "Providers without
  marks … send nothing", but the class test "OpenAI ≥5.6" is a
  `gpt-<major>.<minor>` parse (entry trade-off 1). The spec table gives
  no version rule. A port must copy the reference's regex from code.
  Sustained.
- (d) Cost accountant. Objection: canonical `input_tokens` **excludes**
  cache tokens on Anthropic (`cache_history`: 3 + 3275 written) and
  **includes** them on OpenAI (`prompt_cache_breakpoint`: 3087 with
  3066 read) and Gemini (`cache_resource`: 3598 with 3580 read).
  spec/types.md Usage says only `>= 0`. The MAP-6 promise "the outcome
  is always visible in Usage" is true; a bill cannot be reconciled from
  Usage alone without a per-provider rule the spec does not state.
  **Sustained.** Second: `gemini.cache_history_fallback` shows the
  fallback's "observable" outcome as an absent counter, which INV-029
  says means "not reported".
- (e) Provider switcher. Objection: `retention="long"` and `key` raise on
  the second provider (40-attack scenario 8). Accepted as designed.
  Weaker but real: `prefix="history"` on Anthropic marks the last user
  block; switching to OpenAI 5.6 sends nothing and relies on implicit
  mode — a different cost curve with the same config. Not sustained
  beyond what the entry states.

### changes/2026-09-02-reasoning-design.md → MAP-7

**Receipt check.** `research/reasoning/20-results.json`, 134 cells.

- Rule 2 (Anthropic `minimal` RAISES): no cell sends
  `output_config.effort: minimal` to Sonnet 5; the adaptive `effort`
  cells cover low/medium/high/xhigh/max. Doc-based. Minor.
- Rule 3 (grading table "receipted on both"): Anthropic manual cells
  measure `budget_tokens` 1024 (200) and 128 (400). Gemini 2.5 cells
  measure 0, -1, 128, 1024. **None of 2048, 8192, 16384, 24576, 32768
  was sent to either provider.** The Flash ceiling "24576 (max → server
  400 on Flash)" is doc-based. **FLAG: "receipted on both" is true for
  the floor only.**
- Rule 4 (Gemini 3.x off RAISES): receipted on 3.7 Flash
  (`thinkingBudget=0` → 200, 58 tokens). On 3.5 Flash-Lite,
  `thinkingBudget=0` → **400** (loud, the MAP-5 contract) and
  `thinkingLevel=minimal` → no thinking. The rule generalises one model's
  silent behaviour to the class. Not wrong; over-broad. Noted.
- Rule 7/9 (Groq preset `reasoning_format: "parsed"`): **no receipt.**
  `grep reasoning_format research/reasoning/receipts/` finds nothing.
  40-attack.md item 7 says "Needs a receipt at implementation"; the
  entry's planned case `openai_chat/groq qwen_reasoning_parsed` does not
  exist in `cases/`. **FLAG.**
- Rule 8 (OpenAI item replay needs `summary`): receipted in the entry
  (HTTP 400 text quoted, 2026-09-02T12:52Z) and by
  `openai.reasoning_replay`.
- Rule 9 (`reasoning_tokens` from every provider's exact field): the
  goldens confirm the field; see lens (d).

**Lenses.**

- (a) Cold learner. Objection: `Reasoning()` no longer constructs, and
  `effort` on Sonnet 5 at low/medium/high/xhigh all spent **0** thinking
  tokens on the probe (only `max` spent 148). A learner sets
  `effort="high"` and sees no thinking; the dial looks broken. The
  receipts say this is model behaviour. Not sustained against the rule;
  the cookbook must show it.
- (b) Library author. Objection: rule 8 says a `ThinkingPart` **without**
  state replays as assistant text on every provider. A loop that stores
  `Response.message` and replays it on a different provider (or after
  serde that drops `continuation`) silently converts private reasoning
  into visible assistant text in the transcript. Sustained as a stated
  trade-off (decision G) with a real leakage surface.
- (c) Go/Rust implementer. Objection: `spec/invariants.md` still lists
  `total_budget` in INV-007 (line 50) and INV-026 (line 146), and INV-027
  (line 149) still says `mode="off"` forbids only `retention` and `key`
  while spec/types.md:506 says it also forbids `prefix`,
  `prefix_until_index`, `resource`. A port built from invariants.md
  implements a removed field and a narrower check. **Sustained; FLAG on
  spec drift.** Also: the model-class table (rule 10) is "by name"; the
  names are in the reference's code, not in the spec.
- (d) Cost accountant. Objection: `reasoning_tokens` is a **subset** of
  `output_tokens` on OpenAI (`reasoning_replay`: 199 incl. 147) and
  Anthropic (`reasoning_budget`: 220 incl. 188) but **disjoint** on
  Gemini (`thinking_level`: 19 + 48 + 155 = 222) and xAI
  (`structured_output`: 254 + 9 + 111 = 374). The spec says "exact
  separate count" and nothing about the relation. Billed output is
  `output_tokens` on two providers and `output_tokens + reasoning_tokens`
  on the other two. **Sustained.**
- (e) Provider switcher. Objection: a Gemini 3.x reply's `thoughtSignature`
  on the **text** part is dropped (goldens flagged above). Rule 8 says
  signatures are replay state; the corpus pins their loss on every
  no-tool 3.x turn. Whether the server degrades or 400s on a text-only
  replay without it is unmeasured (`turn2-signature` cells cover function
  calls only). **Sustained.**

### changes/2026-09-02-tool-choice-structured-output.md → MAP-8, INV-050

**Receipt check.** `research/tool-choice/20-results.json`, 141 cells
(structured-output cells live in the same file; `research/structured-output/`
has no 20-results.json of its own).

- Rule 1 (xAI ignores allowlists): `xai/grok-4.6/tc:allow-lookup-ask-weather`
  → called `weather`. **One cell, one model, no repeat.** The playbook
  (step 5) says to repeat noisy cells; tool selection is model behaviour.
  In the same run `tc:required-no-need` on xAI called `weather` where
  every other provider called `lookup`, which suggests the model, not the
  wire, was picking. Receipt exists; it is thin. FLAG (weak receipt).
- Rule 2 (Gemini `parallel=false` → two calls): receipted on 2.5 and
  3.7, one cell each.
- Rule 3 (xAI force + schema → JSON, no call): receipted, one cell
  (`{"name": "lookup", "age": 7}`).
- Rule 6 (Anthropic `json_object` → 400): receipted on Sonnet 5 and 4.5.
- Anthropic `minimum`/`maximum` 400, OpenAI/Groq strict-needs-required
  400, Gemini 2.5 schema+tools 400, Groq JSON+tools 400: all receipted.
- Four raises are pinned as build-request cases
  (`changes/2026-09-02-map8-raises-pinned.md`).

**Lenses.**

- (a) Cold learner. Objection: INV-050 rejects `{"json_schema": {...}}`
  and bare schemas at construction — the two spellings every OpenAI
  tutorial uses. The error names both shapes and the `extensions` door;
  a learner can recover. Not sustained.
- (b) Library author. Objection: `gemini/gemini-2.5-flash/tc:none-needed`
  returned `finishReason: UNEXPECTED_TOOL_CALL` with no call. The Gemini
  finish map folds unknown values to `stop` **without** an
  `_lm15_unmapped` record (only openai_chat records finish values). A
  loop asking "why did the model stop" sees `stop`. Sustained against
  vocabularies.md policy 2, not MAP-8; the cell is a receipt that the
  gap is real.
- (c) Go/Rust implementer. Objection: rule 5's Gemini branch "the
  existing `additionalProperties` rule picks the field" —
  `responseJsonSchema` vs `responseSchema` — is a rule stated nowhere in
  spec/*.md; it lives in the Gemini adapter. Sustained.
- (d) Cost accountant. Objection: none material; a raise costs nothing.
  The strongest is that MAP-8's refusals are client-side and free while
  MAP-6 justified silent fallbacks by "spends nothing and observable" —
  rule 2 explicitly rejects that exception for Gemini `parallel`. The
  two rules use the same test and reach opposite results by reading
  "observable" differently. Noted, not sustained.
- (e) Provider switcher. Objection: `tool_choice.allowed` with two names
  works on OpenAI and Gemini, RAISES on Anthropic (proper subset) and
  xAI. Portable code cannot use allowlists at all. Stated in spec/types.md
  since 2026-09-01. Not sustained beyond what is written.

### changes/2026-09-02-stream-assembly-no-guess.md → MAP-9

**Receipt check.**

- The premise "every shipped dialect names a call on its first fragment
  (OpenAI Chat in the first delta, Responses in `output_item.added`,
  Anthropic in `content_block_start`, Gemini in the whole `functionCall`
  part)" has **no pinned body**. `grep` over `bodies/` finds no
  live-captured streaming tool call for any dialect; the only streaming
  tool-call body in the corpus is the synthetic one
  (`bodies/openai_chat.tool_call_unnamed/2026-09-02-hand-authored.txt`).
  The reviewed stream goldens are text-only. **FLAG: the rule's factual
  premise rests on the reference's unit tests, which AUTHORITY.md ranks
  below fixtures.**
- The pinned case itself is honest about being synthetic. The golden
  matches the reference (§2).
- The entry says the golden shape is `{"error": {type, code}, …}`;
  harness/PROTOCOL.md and the actual golden carry only
  `{partial_response, events}` with the raise declared on the case.
  Minor doc mismatch.

**Lenses.**

- (a) Cold learner. Objection: `ResponseStream` yields text, then raises
  at the end. A learner's `for chunk in stream: print(chunk)` prints a
  page and then crashes with an error about an adapter defect they
  cannot fix. The alternative (a guessed name) is worse. Not sustained.
- (b) Library author. Objection: the **event** trace still yields
  `ToolCallDelta`s with no name (golden events[2..4]); only the
  assembler refuses. A loop that dispatches from deltas (streaming tool
  execution) must implement its own "no name yet" state and never gets
  the refusal. MAP-9 governs `StreamAccumulator.response` only.
  Sustained as a scope statement that should be explicit.
- (c) Go/Rust implementer. Objection: the assembler's real algorithm is
  not in any spec text. From `lm15-python/lm15/result.py:194-244`:
  `part_index` is a **slot** that may hold one thinking, one text, one
  image, one audio, many citations, and one tool call **at the same
  index**; the slot emits them in a **fixed kind order** (thinking, text,
  image, audio, citation, tool_call), not arrival order; an index with
  only a continuation becomes `TextPart("")`. The goldens depend on it
  (`xai.streaming`: thinking and text both at 0; `tool_call_unnamed`:
  text and tool_call both at 0). INV-006 says indexes "address parts
  positionally", which reads as one part per index. A port that builds
  one part per index produces a different `Response` from the same
  events and passes no golden. **Sustained; FLAG.**
- (d) Cost accountant. Objection: `partial.usage` carries the full
  provider usage while the partial holds fewer parts. Stated trade-off
  1. Not sustained.
- (e) Provider switcher. Objection: the minted id `tool_call_<index>`
  (Gemini) is replayed on the next provider as a real call id; OpenAI
  and Anthropic accept any string, so it works, but a second Gemini turn
  gets an `id` it never issued. Stated as lm15-owned. Not sustained.

### changes/2026-09-02-auth-by-composition.md → AUTH-10

**Receipt check.**

- The entry claims "the Claude Code, Codex, and xAI request cases produce
  the same headers and bodies as before". The corpus holds **one** case
  each for `claude_code` and `openai_codex`, both `models` (GET). No chat
  request case exists for either, so `system_prefix` ("You are Claude
  Code…" / "You are a helpful assistant."), the Codex payload branch
  (`store: false`, `stream: true`, no max-token knob), and `complete`
  materialising the stream have **no corpus receipt**. They are pinned
  only by `lm15-python/tests/test_access_policy.py`. **FLAG.**
- The `claude-code` policy lists `user-agent: claude-cli/<v>`. `<v>` is
  `2.1.170` in `lm15/access.py:66` and appears in no spec text.
  `harness/check.py:63` drops `user-agent` from every comparison. The
  oracle cannot see this header. If the backend checks it, ports have no
  pinned value; if it does not, the spec names a header that does not
  matter. Either way it is unreceipted. **FLAG.**
- `originator: lm15` and `client_version: 0.147.0` are pinned by
  `cases/openai_codex/models.json`; a port can copy them.

**Lenses.**

- (a) Cold learner. Objection: `AnthropicLM(access=CLAUDE_CODE)` and
  `ClaudeCodeLM()` are two spellings of one thing; the entry keeps both.
  Ergonomic, stated. Not sustained.
- (b) Library author. Objection: `lm.supports` moved from class to
  instance (behaviour change 2). A library that checked
  `AnthropicLM.supports.files` at import time now gets an attribute
  error or a class default that may differ from the bound policy.
  Stated. Not sustained.
- (c) Go/Rust implementer. Objection: the table is "data ports copy",
  but three of its values are not in the table: the Claude Code CLI
  version, the Codex client version (pinned only in a case), and the
  credential-file formats behind "loading a stored login (keyed by
  provider)". AUTH-8 covers the formats; the versions rot with no
  receipt. **Sustained.**
- (d) Cost accountant. Objection: `xai` policy is
  `oauth-unless-explicit` — a stored subscription beats an environment
  key. A CI box with a developer's cached xAI login bills the
  subscription, not the project key. Ratified 2026-09-01
  (subscription-first). Stated; not sustained here.
- (e) Provider switcher. Objection: `system_prefix` is injected into
  `system`/`instructions`; a conversation captured under Claude Code and
  replayed on plain `anthropic` carries a different system prompt than
  the caller wrote, or loses the prefix. The spec says the prefix is
  policy, so this is by design. Not sustained.

## 4. What a human must decide, by severity

1. **Gemini text-part `thoughtSignature` is dropped silently**
   (`gemini.thinking_level`, `gemini.response_json_schema`;
   `gemini.py:802`). Decide: attach it as `gemini:thought_signature` on
   the text part (a canonical-fixture change with MAP-7 rule 8 as the
   citation) and fix the reference, or write a rule that says text-part
   signatures are discarded and why. Until then every 3.x no-tool turn
   loses replay state the spec calls mandatory-adjacent.
2. **Stream assembly semantics are unwritten** (`part_index` as a
   multi-kind slot, fixed kind order). Ports cannot reproduce
   `xai.streaming` or `tool_call_unnamed` from the spec. Decide: write
   the slot rule into MAP-9 or types.md, or change the reference to one
   part per index and re-draft the two goldens.
3. **Usage semantics differ per provider and the spec is silent**:
   `input_tokens` with vs without cache tokens; `output_tokens` with vs
   without reasoning. Decide: normalise in adapters (a canonical-fixture
   change touching many goldens) or add a normative sentence per counter
   to spec/types.md and accept that Usage is not cross-provider
   comparable.
4. **MAP-7 rule 9 (Groq `reasoning_format: parsed`) has no receipt** and
   MAP-9's "every dialect names the call on its first fragment" has no
   pinned body. Decide: capture, or mark both as unreceipted until then.
5. **MAP-6 rule 5 conflicts with pinned bodies**: 5.6 responses echo
   `prompt_cache_retention: "24h"`. Decide after one live call (§5).
6. **Live usage drops** (`openai.live_tools` frame 21, 75 tokens;
   `openai.live_interrupt` frame 27, 143 tokens). Decide whether a
   function-call `response.done` and a cancelled `response.done` should
   emit a `turn_end` with usage, or accept that live billing is not
   reconstructible from canonical events.
7. **Gemini audio/image modality counters** never reach
   `output_audio_tokens` (`live_text`, `live_tools`, `speech_gen`) while
   OpenAI's do. Decide one rule.
8. **Spec drift**: invariants.md INV-007/INV-026 still name
   `total_budget`; INV-027 not widened. Mechanical, but a port reads it.
9. **Provenance form**: 29 goldens have no provenance block and
   `check_provenance.py` never scans `goldens/`; 4 goldens say
   `source: "derived"`. Decide whether goldens are fixtures under
   AUTHORITY.md (then the checker must scan them) or not.
10. **"Measured across 13 providers"** in MAP-6 should read "six
    measured, seven read from docs".
11. **AUTH-10 unpinned values**: the Claude Code `user-agent` version and
    the Codex payload branch have no corpus receipt; the harness drops
    `user-agent`. Decide whether to pin a chat case for each subscription
    policy.
12. Low: `xai.video` hard-coded `video/mp4`; `gemini.files` stale case
    description; caching entry "3271" vs body 3275.

## 5. What needs one live call

Each request is the smallest that settles the question. Costs are
estimates at list prices.

1. **Gemini 3.x text-part signature.** POST
   `models/gemini-3.7-flash:generateContent`, `thinkingConfig
   {thinkingLevel: low}`, contents = [user "Is 7 a Mersenne prime?",
   model <the text part from `gemini.thinking_level` **without**
   `thoughtSignature`>, user "And 15?"]. Then the same with the signature.
   Compare status and `thoughtsTokenCount`. ~300 tokens each,
   < $0.01 total.
2. **OpenAI 5.6 retention.** POST `/v1/responses`, `model: gpt-5.6-sol`,
   the `openai.cache_off` input, plus `"prompt_cache_retention": "24h"`.
   Expect 200 (rule 5 wrong) or 400 (rule 5 right). ~3.1k input tokens,
   ≈ $0.01.
3. **OpenAI 5.6 breakpoint + explicit mode.** The
   `openai.prompt_cache_breakpoint` request plus
   `"prompt_cache_options": {"mode": "explicit"}`, sent twice with a
   different last question. Expect second call `cache_write_tokens: 0`
   (suffix no longer written) — settles whether `prefix="stable"` should
   also send explicit mode. 2 × ~3.1k tokens, ≈ $0.02.
4. **Groq Qwen parsed reasoning.** POST `api.groq.com/openai/v1/chat/completions`,
   `model: qwen/qwen3.6-27b`, one user message "What is 143 times 27?",
   `"reasoning_format": "parsed"`, no `reasoning_effort`. Expect
   `message.reasoning` populated and `content` free of `<think>`.
   ~100 tokens, < $0.001.
5. **xAI allowlist, repeated.** The
   `xai/grok-4.6/tc:allow-lookup-ask-weather` request from
   `research/tool-choice/receipts/`, five times with fresh nonces. Expect
   `weather` called ≥ 4/5 if rule 1 is systematic. 5 × ~300 tokens,
   ≈ $0.02.
6. **Anthropic Sonnet 5 `effort: minimal`.** POST `/v1/messages`,
   `thinking {type: adaptive}`, `output_config {effort: minimal}`, the
   `reasoning_adaptive` prompt. Expect 400 (rule 2 right) or 200.
   ~50 tokens, < $0.01.
7. **Live streaming tool call on each dialect** (MAP-9 premise). One
   `stream: true` request with one tool and "use the tool" on
   `gpt-4.1-mini` (Responses and Chat), `claude-haiku-4-5`, and
   `gemini-2.5-flash`; pin the SSE bodies. Four calls, ~500 tokens each,
   ≈ $0.02 total.

Total for all seven: under $0.10.
