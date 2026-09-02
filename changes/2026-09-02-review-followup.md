# 2026-09-02 — Independent review follow-up: what was fixed, what waits

Ratification: PENDING for item 1 (two draft goldens re-drafted under an
existing rule); the rest is mechanical. The review itself is
`goldens/REVIEW-2026-09-02-independent.md`, written by an agent that had
not seen any of the corpus before. Do not push before ratification.

## Fixed in this entry

1. **Gemini 3.x text-part `thoughtSignature` was dropped silently**
   (review §2, highest severity). The reference kept signatures only on
   thought and functionCall parts; on 3.x the answer text carries the
   turn's signature. Now: the text part carries
   `gemini:thought_signature` continuation state exactly like the others,
   the stream emits the same `ContinuationDelta` after the text delta, and
   replay puts `thoughtSignature` back on the text part. A thought part is
   classified by its `thought` flag, not by non-empty text, so
   `{thought: true, text: "", thoughtSignature}` keeps its state too.
   Goldens re-drafted: `gemini.thinking_level` (text part gains a 528-char
   signature), `gemini.response_json_schema` (176-char). Both were drafts,
   never reviewed. Rule cited: MAP-7 rule 8. Reference test:
   `test_gemini_text_part_signature_is_kept_and_replayed`.
2. **Provenance never scanned goldens** (review §4 item 9). 29 goldens had
   no block; 4 said `source: "derived"`. `check_provenance.py` now scans
   `goldens/` with the golden vocabulary (`scribe-draft`,
   `hand-authored`); the 29 gained blocks naming the review as the reason;
   the 4 are `scribe-draft` and no longer claim "reviewed" in prose
   without a reviewer. 351 files scanned, was 181.
3. **Spec drift** (item 8): INV-007 and INV-026 no longer name the removed
   `total_budget`; INV-027 states the widened MAP-6 rule the code enforces.
4. **Stream assembly algorithm written down** (item 2): MAP-9 now states
   the slot model (one `part_index` may hold several kinds), the per-kind
   accumulation, the fixed emission order (thinking, text, image, audio,
   citations, tool call), the empty-slot rule, the finish-reason merge,
   and that the chat dialect's per-chunk `id` is not lifted. This is the
   existing behaviour the goldens pin; no golden changed.
5. **Wording** (items 10, 12): MAP-6 says six providers were measured and
   seven read from docs; the caching entry's "3271" is 3275 (the body's
   number); `gemini.files` no longer claims "no download endpoint";
   `spec/types.md` states how `downloadable` is derived on Gemini.

## Not fixed here — decisions for the maintainer (review §4)

- **Item 3, usage semantics.** `input_tokens` includes cached tokens on
  OpenAI and Gemini and excludes them on Anthropic; `output_tokens`
  includes reasoning on OpenAI and Anthropic and excludes it on Gemini and
  xAI. Every golden is verbatim to its provider, which is what a bill
  reconciles against; cross-provider comparison is what is lost.
  Recommendation: keep counters provider-verbatim, add one normative
  sentence to `spec/types.md` Usage saying so, and add the per-provider
  inclusion table there. Normalising in adapters would touch dozens of
  goldens and break bill reconciliation.
- **Item 6, live usage dropped** on a function-call `response.done` (75
  tokens) and a cancelled one (143 tokens). The design chose "no turn
  end"; the tokens are still billed. Recommendation: emit a `usage`-only
  live server event (new vocabulary value) so billing is reconstructible
  without changing turn semantics. Needs a design decision and two golden
  amendments.
- **Item 7, Gemini modality counters** (`candidatesTokensDetails[AUDIO]`)
  never reach `output_audio_tokens` while OpenAI's do. Recommendation: map
  them; three draft goldens change.
- **Items 4, 5, 11 and the seven live calls** (review §5, under $0.10
  total): the Groq `reasoning_format: parsed` rule, the MAP-9 premise
  (no pinned streaming tool-call body on any dialect), the GPT-5.6
  retention raise versus bodies echoing `prompt_cache_retention: "24h"`,
  the single-sample xAI allowlist cell, and the AUTH-10 header values
  the harness never compares (`user-agent` is dropped). Each needs one
  live call; none can be settled offline.
- **Item 12 low:** `xai.video` hard-codes `video/mp4` where the wire
  carries no MIME; the spec says media types come from the wire. Left as
  is; a port cannot be caught wrong by it since it equals the default.

## Evidence

Harness 13/13 green (response 129 after the two re-drafts); provenance
351/351; audit, secrecy, spec_drift green; selftest 25/25; lm15-python
972 tests.
