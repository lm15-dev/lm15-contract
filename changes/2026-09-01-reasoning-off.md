# 2026-09-01 — Explicit reasoning-off reaches the wire or fails loudly

Ratification: RATIFIED 2026-09-01 by maintainer delegation — standing instruction from Maxime Rivest in session ("for ones that have one obvious right decision, you can ratify for me without my involvement"); the rule follows already-ratified principles and every wire claim carries a live receipt. Transcribed.

## The finding

A live audit (2026-09-01) of `Config(reasoning=Reasoning(effort="off"))`
found four adapters omitting the disable from the wire and letting
reasoning-by-default models spend billed, hidden reasoning tokens:

- OpenAI Responses (and the Codex subscription adapter): nothing sent;
  gpt-5-mini spent **64 reasoning tokens** on an explicit-off request.
- OpenAI Chat dialect (`reasoning_effort` servers, incl. Groq): nothing
  sent; Groq gpt-oss-20b spent **45 reasoning tokens**; Groq
  qwen3.6-27b reasoned and leaked a raw `<think>` block into content.
- OpenRouter (both dialects): nothing sent, though the server documents
  `reasoning: {"enabled": false}`.
- xAI: the inherited deepseek shape `thinking: {"type": "disabled"}` is
  accepted by api.x.ai and silently ignored — grok-4.6 spent
  **158 reasoning tokens** and returned a thinking part.

Counter-proof that an explicit off switch exists where we now send it:
gpt-5.1 accepted `reasoning: {"effort": "none"}` with
`reasoning_tokens == 0` (pinned body, `openai.reasoning_off`); Groq
qwen3.6-27b accepted `reasoning_effort: "none"` and answered with no
think block (pinned body, `openai_chat.reasoning_off`).

## The rule

New normative rule MAP-5 (lm15-python/docs/mapping-rules.md): explicit
reasoning-off must reach the wire in the provider's native disable
mechanism, or the request must fail loudly. Silent omission is a paid
no-op and is forbidden. Models that cannot disable reasoning surface
their provider's 400 unchanged (gpt-5-mini's floor is "minimal";
gemini-2.5-pro rejects budget 0). xAI raises
`UnsupportedFeatureError` client-side: Grok reasoning models have no
off switch and the server ignores disable-shaped fields.

## Corpus additions

Four wire cases, every body a live capture through the reference
adapter (receipts in each case's provenance):

- `openai.reasoning_off` — gpt-5.1, `reasoning: {"effort": "none"}`,
  reasoning_tokens 0.
- `openai_chat.reasoning_off` — Groq qwen3.6-27b,
  `reasoning_effort: "none"`, bare answer.
- `gemini.reasoning_off` — gemini-2.5-flash, `thinkingBudget: 0`, no
  thoughtsTokenCount.
- `anthropic.reasoning_off` — claude-sonnet-4-5, NO thinking field;
  absence is Anthropic's native off and the exact-body harness pins it.

Goldens for the four cases are scribe drafts (not frozen). The xAI
raise is client-side behavior and is pinned by
`lm15-python/tests/test_xai.py::test_reasoning_off_raises_unsupported`,
not by a wire case.

## Behavior change (stated, not absorbed)

Requests that previously "worked" by silently ignoring off now fail
loudly on models that cannot disable reasoning (OpenAI models below
gpt-5.1, all current xAI Grok reasoning models). This is deliberate:
the silent path billed users for reasoning they explicitly disabled.

Known remaining gap: compat presets that declare no reasoning wire
control at all (`reasoning_format`/`thinking_format` "none":
ollama, LM Studio) still send nothing for every reasoning config,
off included. The preset itself is the declaration of that limit.
