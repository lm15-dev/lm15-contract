# 2026-09-02 — Seven live probes: two MAP-6 amendments, one bug, five receipts (proposed)

Ratification: PENDING — awaiting Maxime Rivest. Two rules change
(MAP-6 rules 4 and 5), four cases are re-captured, four stream cases and
five goldens are new, and one reference bug is fixed. Record under
`research/review-2026-09-02/`. Do not push before ratification.

## Amendments (need the stamp)

1. **MAP-6 rule 5.** `retention="long"` on the gpt-5.6+ class no longer
   raises; it sends `prompt_cache_retention: "24h"` like every other
   OpenAI class. The raise rested on a doc line about
   `prompt_cache_options.ttl` (30m only), a different field. Probe 2:
   gpt-5.6-sol answers 200 and echoes `"24h"`; every pinned 5.6 body
   already echoed 24h as its default. What one live call cannot show is
   the 24-hour lifetime itself; the echo is the strongest offline
   evidence there is. Stated.
2. **MAP-6 rule 4.** On 5.6+, a placed breakpoint (`prefix="stable"` or
   `prefix_until_index`) travels with `prompt_cache_options: {mode:
   "explicit"}`. Probe 3: without the mode the warm call still wrote the
   volatile suffix at 1.25x (the pinned 18 after reading 3066); with it
   the warm call writes 0 and the cold write shrinks to exactly the
   marked prefix (3088 → 3070). No mark, no mode: explicit mode with no
   mark would cache nothing. `mode="off"` is unchanged.
   Re-captured with adapter-built wires: `openai.cache_stable` (write
   3070), `openai.prompt_cache_breakpoint` (read 3066, write 0),
   `openai_chat.cache_stable` (write 3070),
   `openai_chat.prompt_cache_breakpoint` (write 3066, cold). Goldens
   re-drafted (all four were drafts).

## Bug found by the new pins

**Anthropic streamed tool_use input was unparseable.** The block opens
with `input: {}` and the arguments arrive as `input_json_delta`; the
adapter serialised the placeholder and glued `"{}"` in front, so the
assembled input was `{"partial_json": "{}{\"city\": ..."}`. No body in
the corpus had ever streamed an Anthropic tool call. Fixed (a non-empty
start input is still kept verbatim); red-first test
`test_anthropic_streamed_tool_use_input_assembles_from_deltas`. The golden
`anthropic.streaming_tool_call` pins `{"city": "Gatineau"}` and the
fragment trace `"", "", "{\"city\": \"", "Gatineau\"}"`.

## Receipts that confirm existing rules

- MAP-7 rule 7, Groq `reasoning_format: parsed`: default leaks `<think>`
  into content; parsed returns `message.reasoning` (probe 4). Was
  unreceipted.
- MAP-7 rule 2, Sonnet 5 `effort: minimal`: 400 naming
  low/medium/high/xhigh/max (probe 6).
- MAP-8 rule 1, xAI allowlist: 5/5 repeats called the disallowed tool
  (probe 5). Was one sample.
- MAP-9 premise: all four dialects name a streamed call on its first
  frame (probe 7), now pinned as `openai.streaming_tool_call`,
  `openai_chat.streaming_tool_call`, `anthropic.streaming_tool_call`,
  `gemini.streaming_tool_call` — the first streaming tool-call bodies in
  the corpus. Stream direction: 14 cases.
- Probe 1: the Gemini 3.x text-part signature carries thinking forward
  (145 thought tokens with it, none without). The fix in
  `2026-09-02-review-followup.md` is meaningful, not cosmetic.

## Evidence

Harness 13/13 (request 147, stream 14); audit, provenance (359 files),
secrecy, spec_drift green; selftest 25/25; lm15-python 974 tests. Spend
about 8 cents.
