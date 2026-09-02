# 2026-09-02 — Reasoning: one dial, two spellings, no silent drops (MAP-7, proposed)

Ratification: PENDING — awaiting Maxime Rivest. Output of the second
design pass (`playbooks/design-pass.md`); the record is under
`research/reasoning/`. Do not push before ratification.

## What the pass established (134 live cells, 17 sources)

- Every provider has one dial with the same words — off/none, minimal,
  low, medium, high, xhigh, max — and each model accepts a subset,
  rejecting the rest with a 400. Two exceptions are silent: xAI downgrades
  xhigh on older models, and Gemini 3.7 Flash accepts `thinkingBudget: 0`
  and still spends thinking tokens.
- "Adaptive" is every provider's default when nothing is sent; it is not
  a level.
- Anthropic split into two model classes: adaptive (Sonnet 5, Opus 5,
  4.6+, Fable, Mythos: `thinking: adaptive` + `output_config.effort`,
  budget rejected) and manual (4.5 and earlier: budget ≥ 1024, effort
  and adaptive rejected). The reference adapter knew only the manual
  class; on Sonnet 5 every `Reasoning` it sent was a 400.
- Gemini split too: 2.5 takes `thinkingBudget`; 3.x takes
  `thinkingLevel`, rejects `minimal` on 3.7 Flash, cannot disable
  thinking, and requires thought signatures on function-call replay.
- OpenAI reasoning items carry `encrypted_content`; the reference
  dropped them on replay.
- Groq Qwen leaks a raw `<think>` block into answer text unless
  reasoning is separated on the wire.
- The reference silently dropped `thinking_budget`, `total_budget`, and
  `summary` on providers without them (four cells of the field table).

## The rule — MAP-7, reasoning

1. **Absent `config.reasoning` sends nothing**: the model decides.
2. **`effort` is the one dial**, vocabulary `off, minimal, low, medium,
   high, xhigh, max` (`adaptive` removed — it meant absent; `max`
   added). `Reasoning.effort` is required. Providers with the dial send
   the word verbatim (OpenAI, Anthropic adaptive class, Gemini 3.x
   levels, xAI, Groq gpt-oss, compat formats); unsupported words fail
   with the server's 400. Words with no native level on a provider
   RAISE client-side rather than downgrade (Anthropic `minimal`; Gemini
   3.x `xhigh`/`max`).
3. **Budget-only model classes express effort as a budget** through one
   documented grading table (minimal 1024, low 2048, medium 8192, high
   16384, xhigh 24576, max 32768): Anthropic manual class, Gemini 2.5.
   This is the design's one invented mapping; stated, receipted.
4. **`effort="off"`** sends the native disable (OpenAI `none`; Anthropic
   omit `thinking`; Gemini 2.5 `thinkingBudget: 0`; compat disable
   forms) and RAISES where the provider cannot disable or accepts the
   disable without honouring it (xAI; Gemini 3.x). MAP-5 unchanged in
   spirit, extended by the Gemini 3.x receipt.
5. **`thinking_budget`** maps only where the wire has a budget
   (Anthropic manual class, Gemini); RAISES elsewhere (OpenAI, Anthropic
   adaptive class, xAI, Groq). Setting both `effort` and
   `thinking_budget` on a budget-only class RAISES (two spellings of one
   thing).
6. **`total_budget` is removed.** `Config.max_tokens` is the ceiling; on
   Anthropic's manual class the adapter adds the thinking budget to it
   (unchanged); on the adaptive class it is the total (provider
   semantics, stated in the spec row).
7. **`summary`** is visibility: `None` = provider default; `"auto"` =
   show the thinking (OpenAI `summary: auto`; Gemini `includeThoughts`;
   Groq `include_reasoning`; Anthropic/xAI already show — satisfied,
   nothing sent); `"concise"`/`"detailed"` verbatim on OpenAI, RAISE
   elsewhere. The Gemini adapter stops sending `includeThoughts` unless
   asked.
8. **Replay**: native form when the continuation state is present —
   Anthropic signed block, Gemini signature (required on 3.x), and NEW:
   OpenAI reasoning items (`ThinkingPart.continuation` kind
   `openai:reasoning_item {id, encrypted_content}`), replayed as
   `{"type": "reasoning", ...}` input items. Without state, a
   `ThinkingPart` is replayed as assistant text on every provider
   (decision G); the chat dialect's `thinking_replay` default becomes
   `as_text`.
9. **Groq Qwen**: the `groq` preset sends `reasoning_format: "parsed"`
   whenever reasoning is not off so `<think>` never leaks into text.
10. **Model-class detection** (Anthropic adaptive vs manual; Gemini 2.5
    vs 3.x) is by model-name table, a table that rots; the server 400s
    loudly when wrong; `extensions` overrides. Stated.

## Behaviour changes (stated)

- `Reasoning()` no longer constructs; `Reasoning(effort="off")` is the
  explicit off. `adaptive` is gone. `total_budget` is gone (surface
  ratchet: removal ratified here).
- Anthropic adaptive-class models start working with `Reasoning`; the
  Gemini 2.5 effort→budget grading is unchanged in numbers but now
  shared and stated; Gemini 3.x uses levels.
- `thinking_budget` / `summary` on providers without them raise instead
  of vanishing.
- `includeThoughts` on Gemini only when `summary` is set: pinned Gemini
  thinking cases are re-captured with the canonical request that asks
  for it (spec citation: MAP-7 rule 7).
- OpenAI replays reasoning items; unsigned thinking becomes assistant
  text on OpenAI and the chat dialect instead of vanishing.

## Spec and code effects (after ratification)

- `spec/vocabularies.md` ReasoningEffort; `spec/types.md` Reasoning
  table (`effort` required, `total_budget` removed, per-provider notes);
  `spec/invariants.md` INV-026 (off forbids budget/summary — unchanged),
  INV-043 (legacy `enabled: false`, `budget` — unchanged; missing effort
  on read → `medium` unchanged).
- Cases: anthropic `reasoning_adaptive` (Sonnet 5), `reasoning_budget`
  (4.5, exists as `thinking`), gemini `thinking_level` (3.7), openai
  `reasoning_replay` (tool round-trip with the reasoning item),
  openai_chat/groq `qwen_reasoning_parsed`; re-captures where
  `includeThoughts` changes.
- Reference: `Reasoning` type, `serde`, four adapters, compat default,
  tests per cell.

## Open questions for the maintainer

1. The grading table's numbers (rule 3): keep the existing Gemini
   numbers for both providers, or pick provider-specific tables.
2. `summary="auto"` on Anthropic/xAI: silently satisfied (proposed) or
   raise because nothing is sent.

## Amendments during implementation (2026-09-02)

- **Rule 5 corrected.** A budget plus an effort on a budget-only class is
  not a conflict: the budget is the spelling on the wire and `effort`
  stays the required universal intent (the existing `gemini.thinking`
  case has both). Raising there would have made `effort` unusable
  exactly where users pass a budget.
- **Rule 8 receipt.** A replayed OpenAI reasoning item MUST carry
  `summary`, even `[]`: HTTP 400 "Missing required parameter:
  input[1].summary" (2026-09-02T12:52Z). The adapter always sends it.
- **Rule 9 (Groq) narrowed.** `reasoning_format: "parsed"` rides
  `summary="auto"` on the `groq` preset (a visibility knob, MAP-7 rule
  7), not every request: the pinned Groq cases run through `base_url`
  without the preset, and a Groq-wide field would have broken ten Llama
  cases. Qwen 3.6's dial accepts only `none|default`, so any effort word
  fails loudly there; the documented door is
  `extensions={"reasoning_format": "parsed"}` with `reasoning` absent.
  A provider limit, stated.

## Implementation landed (2026-09-02, awaiting ratification)

Reference: `Reasoning` (effort required, `adaptive` removed, `max`
added, `total_budget` removed; legacy spellings read leniently);
`EFFORT_THINKING_BUDGETS` shared table; Anthropic two classes
(`anthropic_adaptive_class`), Gemini two classes (`gemini_level_class`),
OpenAI verbatim + reasoning-item round-trip, chat dialect raises +
`thinking_replay` default `as_text`, Groq visibility; MAP-7 in
docs/mapping-rules.md; docs and cookbook prose; 931 tests.

Contract: cases `anthropic.reasoning_adaptive` (Sonnet 5, 108 thinking
tokens, signed block), `anthropic.reasoning_budget` (Sonnet 4.5, table
budget 2048, wire max_tokens 3048), `gemini.thinking_level` (3.7 Flash,
`thinkingLevel: low` + `includeThoughts`), `openai.reasoning_replay`
(two-turn tool round-trip, the item replayed with id, encrypted_content,
empty summary; turn-1 body kept beside); 4 drafted goldens; serde vector
`reasoning.medium` drops `total_budget`; `gemini.thinking` canonical
gains `summary: "auto"` (wire unchanged); spec vocabulary and Reasoning
table. **Two reviewed goldens amended** (`openai.reasoning`,
`openai.reasoning_encrypted`) plus `openai.batch`: the reasoning item is
now an empty ThinkingPart with its replay state (rule 9) — the 2026-06-10
review line is kept and an `amended` line cites this entry; this is the
change that needs the maintainer's eyes most.

Open question 1 (table numbers) and 2 (`summary="auto"` satisfied
silently on Anthropic/xAI) stand.
