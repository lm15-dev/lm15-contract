# Reasoning — the abstract model and the mapping (proposal, 2026-09-02)

## The five facts that shape the design

1. **One dial exists everywhere, with one vocabulary and per-model
   subsets.** The words are none/off, minimal, low, medium, high, xhigh,
   max. No provider accepts all seven on all models; every provider
   rejects unsupported words loudly (400) — except xAI, which downgrades
   xhigh silently on older models, and Gemini 3.x, which accepts a
   disable it does not honour.
2. **"Adaptive" is not a level, it is the default.** Every provider now
   lets the model decide when nothing is sent (OpenAI, Anthropic
   adaptive class, Gemini dynamic, xAI). The canonical way to say "let
   the model decide" is to send no `Reasoning` at all.
3. **Budgets are a second-class, model-class-specific control.**
   Anthropic manual class and Gemini 2.5 take a token budget; Anthropic
   adaptive class rejects it; Gemini 3.x half-honours it; OpenAI, xAI,
   Groq have none. Effort and budget are two spellings of "how much" on
   different model classes, never both on one.
4. **Off is not always available.** Anthropic: omit thinking. OpenAI:
   `none`. Gemini 2.5 Flash: budget 0. Gemini 2.5 Pro, Gemini 3.x,
   xAI, Groq gpt-oss, Z.AI GLM-5.3: cannot. Some reject loudly, some
   accept and spend (Gemini 3.7 Flash).
5. **Replay state is provider-owned and sometimes mandatory.** Gemini
   3.x rejects a function-call turn without its signature; Anthropic
   re-thinks without its block; OpenAI carries encrypted items and copes
   without. lm15 already models this as `ContinuationState`; OpenAI's
   item was the one not captured.

## What `Reasoning` means (proposal)

| Field | Meaning | OpenAI | Anthropic adaptive class | Anthropic manual class | Gemini 2.5 | Gemini 3.x | xAI | Groq / compat |
|---|---|---|---|---|---|---|---|---|
| `config.reasoning` absent | the model decides (provider default) | nothing | nothing (thinking off by default — note) | nothing | nothing (dynamic) | nothing (model default level) | nothing (high) | nothing |
| `effort="off"` | no thinking, or fail loudly (MAP-5) | `effort: none` | omit `thinking` | omit `thinking` | `thinkingBudget: 0` (Pro: server 400) | RAISE (accepted-but-spent) | RAISE (server 400 too) | preset disable form or RAISE |
| `effort=<level>` | the dial | verbatim; model-unsupported words → server 400 | `thinking: adaptive` + `output_config.effort`; `minimal` RAISE (no level below low) | budget from the grading table (stated) | budget from the grading table (stated) | `thinkingLevel` for minimal/low/medium/high; xhigh/max RAISE | `reasoning_effort` verbatim; off/minimal/max → server 400 | per compat format |
| `thinking_budget=N` | a token cap | RAISE | RAISE (deprecated on this class) | `budget_tokens` (server floor 1024) | `thinkingBudget` | `thinkingBudget` (accepted; docs warn) | RAISE | RAISE |
| `effort` + `thinking_budget` | conflict on one-spelling classes | RAISE | RAISE | RAISE (budget is the spelling) | RAISE | both sent? no: RAISE | RAISE | RAISE |
| `summary=None` | provider default visibility | no text | blocks returned | blocks returned | no thoughts | no thoughts | `reasoning_content` | provider default |
| `summary="auto"` | show me the thinking | `summary: auto` | nothing to do (already shown) | same | `includeThoughts: true` | same | nothing to do | `include_reasoning: true` where the wire has it |
| `summary="concise"/"detailed"` | a detail level | verbatim | RAISE | RAISE | RAISE | RAISE | RAISE | RAISE |
| `total_budget` | — | **removed** (it was Anthropic's `max_tokens`; `Config.max_tokens` is the ceiling; on the adaptive class it includes thinking, on the manual class the adapter adds the budget — stated per class) | | | | | | |

The grading table (effort → budget) for budget-only classes, one table
for both providers: minimal 1024 · low 2048 · medium 8192 · high 16384 ·
xhigh 24576 · max 32768. Anthropic's floor is 1024, Gemini 2.5 Flash's
ceiling is 24576 (max → server 400 on Flash, stated). This is the one
place the design invents a mapping; it is a documented table, receipted
on both providers, not a silent choice.

Model-class detection is by model name (Anthropic: sonnet-4-6+, opus-4-6+,
sonnet-5, opus-5, fable, mythos, haiku-5 → adaptive; Gemini: `gemini-3`
prefix → 3.x). A table that rots; the server 400s loudly when it is
wrong; `extensions` overrides. Stated.

Vocabulary change: `adaptive` is removed (it meant "absent"); `max` is
added. `Reasoning.effort` becomes required: `Reasoning()` no longer
means OFF (the beginner trap, decision E).

## Output and replay

- `ThinkingPart` is produced from: Anthropic thinking/redacted blocks
  (signed → continuation `anthropic:thinking_signature`); Gemini thought
  parts (signature → `gemini:thought_signature`, also on function
  calls); OpenAI reasoning items (summary text or "", continuation
  `openai:reasoning_item {id, encrypted_content}` — NEW); chat
  `reasoning_content` / `reasoning`; Groq Qwen `<think>` blocks via
  `include_reasoning`/`reasoning_format` so they never leak into text.
- Replay: the native form when the continuation is present (OpenAI
  reasoning item — NEW; Anthropic block; Gemini signature); otherwise as
  assistant text, everywhere, including OpenAI (`output_text`) and the
  chat dialect (`thinking_replay` default becomes `as_text`) — decision G.
- `Usage.reasoning_tokens` from every provider's exact field; `null`
  when not reported.
