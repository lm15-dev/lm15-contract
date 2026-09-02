# Reasoning — fact sheets (2026-09-02)

Every cell cites a scraped line (`sources/<name>.md:<line>`) or a cell in
`20-results.json` (bodies under `receipts/`). 134 live cells across
OpenAI (2 models), Anthropic (3), Gemini (3), xAI (1), Groq (2).

## OpenAI (Responses API)

- Dial: `reasoning.effort` ∈ none, minimal, low, medium, high, xhigh, max;
  support and default are model-dependent (`openai-reasoning.md:188-201`).
  Measured: gpt-5.6-sol accepts none/low/medium/high/xhigh/max, rejects
  minimal (400 lists the supported set); gpt-5.4-mini accepts none…xhigh,
  rejects max. Both spent 0 reasoning tokens on a trivial question at every
  effort (adaptive behaviour); 5.4-mini spent 9–22 at low…xhigh.
- Budget: none.
- Visibility: `reasoning.summary` auto/concise/detailed (`:939`); without
  it no reasoning text is returned. Measured: summary=auto → a summary on
  the reasoning item.
- Replay: reasoning items carry `encrypted_content` (measured on every
  reasoning item, with or without `store: false`; doc `:689,707`). Replay
  the items to keep continuity (`:709,733`); measured: turn 2 succeeds
  with and without them.
- Usage: `output_tokens_details.reasoning_tokens`, exact.
- Incompatibilities: `temperature` rejected entirely on both models
  ("not supported with this model"), independent of reasoning.
- Off: `effort: "none"` (measured 0 tokens); MAP-5 receipt 2026-09-01.

## Anthropic (Messages API) — two model classes

- **Adaptive class** (Sonnet 5, Opus 5, Sonnet/Opus 4.6+, Fable, Mythos;
  `anthropic-effort.md:9`, `anthropic-extended-thinking.md:354`):
  `thinking: {type: "adaptive"}` + `output_config.effort` ∈ low, medium,
  high (default), xhigh, max (`anthropic-adaptive-thinking.md:46-51`;
  `effort.md:203-227`). `thinking.type: "enabled"` REJECTED ("use
  adaptive and output_config.effort"). Effort applies to all output
  tokens even without thinking (`effort.md:209-215`; measured 200 with
  effort and no thinking). Measured Sonnet 5: 0 thinking tokens on a
  trivial question at every level except max (148); a hard prompt at
  high → 349 thinking tokens, one signed thinking block. Not every model
  supports xhigh (`effort.md:227`).
- **Manual class** (Sonnet 4.5, Haiku 4.5, Opus 4.5 and earlier):
  `thinking: {type: "enabled", budget_tokens: N}`, N ≥ 1,024
  (`extended-thinking.md:264-272`; 128 → 400), `budget_tokens <
  max_tokens` (`:274`). `adaptive` and `output_config.effort` REJECTED
  ("not supported on this model" / "does not support the effort
  parameter"). Measured 4.5 at 1024: 46 thinking tokens, signed block.
- Visibility: thinking blocks are returned whenever thinking runs
  (summarized on newer models, `:84`); no knob to hide them.
- Replay: signed `thinking` blocks; `redacted_thinking` carries `data`.
  Measured Sonnet 5 tool round-trip: turn 2 succeeds with the block
  (66 new thinking tokens) and without it (301 — it re-thinks).
- Usage: `output_tokens_details.thinking_tokens`, exact; `null` on the
  manual class when thinking is off.
- Incompatibilities: `temperature` must be 1 (or absent) with thinking
  in either mode (400, measured). Forced `tool_choice` works with
  adaptive (measured 200).
- Off: omit `thinking` (measured: default → 0 thinking tokens on Sonnet 5).

## Google Gemini (generateContent) — two model classes

- **2.5 class**: `thinkingConfig.thinkingBudget`: 0 disables (Flash;
  Pro min 128, cannot disable), -1 dynamic (default), ranges per model
  (`gemini-thinking-generatecontent.md:493-506`). `thinkingLevel`
  REJECTED. Measured 2.5-flash: 0 → no thoughts; -1 → 443; 128 → 50;
  1024 → 425. Thought signatures present on function calls only; turn 2
  succeeds WITHOUT the signature (measured 200).
- **3.x class**: `thinkingConfig.thinkingLevel` ∈ minimal, low, medium,
  high, support per model (`:372-379`): 3.7 Flash rejects minimal
  (measured 400); 3.5 Flash-Lite defaults to minimal and treats
  minimal/low as no thinking (measured null). **Cannot fully disable
  thinking** on 3.1 Pro, 3 Flash, Flash-Lite (`:476-477`). Measured 3.7
  Flash: `thinkingBudget: 0` accepted, HTTP 200, still 58 thinking
  tokens — a silent paid no-op; 3.5 Flash-Lite: budget 0 → 400.
  `thinkingBudget` "accepted for backwards compatibility" on 3.x
  (`:490`); measured to cap (128 → 34 tokens).
- Visibility: `includeThoughts: true` returns thought summaries (`:101`);
  default returns none. Measured: one thought part with the flag.
- Replay: `thoughtSignature` on parts. **Required on function calls for
  3.x**: turn 2 without it → 400 "Function call is missing a
  thought_signature" (measured on 3.7 Flash and 3.5 Flash-Lite).
- Usage: `usageMetadata.thoughtsTokenCount`, exact; absent when none.
- Incompatibilities: temperature with thinking works (measured 200).

## xAI (Chat Completions dialect)

- Dial: `reasoning_effort` ∈ low, medium, high (default), xhigh on
  grok-4.6/4.5; xhigh → high silently on models without it
  (`xai-reasoning.md:21-38`). "Reasoning cannot be disabled" (`:23`).
  Measured grok-4.6: none → 400 (loud); max → 400; low 116, medium 149,
  high 141, xhigh 244 tokens; `thinking: {type: "disabled"}` → 200 and
  212 tokens (silently ignored, the MAP-5 finding).
- Visibility: `reasoning_content` on the message, always. Encrypted
  reasoning via `include` on xAI's Responses API only (`:9-13`).
- Usage: `completion_tokens_details.reasoning_tokens`, exact.

## Groq (Chat Completions dialect)

- gpt-oss-20b/120b: `reasoning_effort` ∈ low, medium, high; none → 400
  (`groq-reasoning.md:28-29`, measured). Qwen 3.6: none | default only
  (`:22-23`); low/medium/high → 400.
- Visibility: `include_reasoning` (default true → `message.reasoning`)
  or `reasoning_format` parsed/raw/hidden, mutually exclusive
  (`:17-19`). **Measured Qwen default: the answer text begins with a raw
  `<think>` block and no reasoning field**; `include_reasoning: false`
  strips it and reports 320 reasoning tokens.
- Usage: `completion_tokens_details.reasoning_tokens` (gpt-oss); Qwen
  reports it only when reasoning is separated.

## OpenRouter, DeepSeek, Mistral, Z.AI, vLLM (sources only)

- OpenRouter: unified `reasoning: {effort, max_tokens, exclude,
  enabled}`; per-model `supported_efforts`, `mandatory` (cannot disable)
  (`openrouter-reasoning.md:76-112`).
- DeepSeek: `thinking: {type: enabled|disabled}` + `reasoning_effort`;
  thinking mode ignores temperature/top_p; `reasoning_content` must be
  replayed when tools are present (`deepseek-thinking.md:6-15`).
- Mistral: `reasoning_effort` high | none; thinking chunks inside
  `content` (`mistral-reasoning.md:8-12,47-50`).
- Z.AI: `thinking: {type: enabled|disabled}`; GLM-5.3 forced thinking,
  cannot disable; replay `reasoning_content` with tools
  (`zai-thinking.md:3-4,10,22`).
- vLLM: reasoning parsers separate `reasoning_content`; per-server flag.
- Bedrock: source missing (manifest).
