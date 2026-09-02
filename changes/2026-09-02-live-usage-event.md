# 2026-09-02 — Live `usage` event: billed tokens of a response that ends no turn

Ratification: accepted in advance — Maxime Rivest, in session ("i accept
all your recommendations"), for the recommendation in
`2026-09-02-review-followup.md` (review §4 item 6). This adds a
vocabulary value and a type; stamp on reading.

## What changed

- `LiveServerEventType` gains `usage`; `LiveServerUsageEvent {usage}`
  (spec/types.md, serde vector `live_server_event.usage`).
- OpenAI Realtime: a function-call `response.done` emits `usage` (the
  turn stays open, as before); a cancelled `response.done` emits `usage`
  then `interrupted`. No usage reported → no event, never an empty one.
- Gemini Live: a non-`turnComplete` frame carrying `usageMetadata` emits
  `usage`. A rule, not a receipt: every pinned Gemini frame reports usage
  only on `turnComplete`.
- Reference `Turn.usage` is the field-wise sum of every `usage` and
  `turn_end` event the turn saw (a counter absent on either side is
  unknown in the sum, INV-029). A tool-call response's usage arrives
  after the `tool_call` that ended `result()`, so it lands in the
  continuation turn — the semantic turn stayed open, so that is where it
  belongs. An interrupted turn keeps its usage instead of `None`.

Goldens amended: `openai.live_tools` frame 21 (`[]` → `[usage 75]`),
`openai.live_interrupt` frame 27 (`[interrupted]` → `[usage 143,
interrupted]`). Both drafts.

## Why an event and not a `turn_end`

`turn_end` is a boundary every dispatch loop breaks on; emitting it for a
tool-call response would break the shared Gemini/OpenAI loop (the design
decision of 2026-09-01 stands). Dropping the tokens made live billing
unreconstructible from canonical events. A usage-only event is the
smallest thing that is both: never a boundary, always on the bill.

## Evidence

Harness 13/13 (live 21, serde 110); audit, provenance, secrecy,
spec_drift green; lm15-python 978 tests (five new).
