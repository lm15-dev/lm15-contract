# 2026-06-10 — extensions-passthrough burn-down: canonical_request rewrites

Rewrote the `canonical_request` of 18 cases so the same provider wire body is
produced through canonical Config keys (`reasoning`, `response_format`,
`tool_choice`, `top_p`, `top_k`, `stop`, `max_tokens`, `temperature`) instead
of raw provider syntax in `config.extensions`. The wire fixtures (`request`
side) are untouched: every rewrite was verified wire-identical to the
live-validated fixture by `harness/check.py --shim python --direction request`
(strict typed deep-equality). No live receipt is needed because the receipts
already exist; only the canonical expression changed. Provenance updated to
`canonical-rewrite` / 2026-06-10 on each case.

## Rewritten (18)

- anthropic.output_config — `config.response_format` (json_schema)
- anthropic.stop_sequences — `config.stop`
- anthropic.top_k — `config.top_k`
- anthropic.top_p — `config.top_p`
- gemini.response_mime_type — `config.response_format` (`{"type":"json_object"}`)
- gemini.response_schema — `config.response_format` (response_mime_type + response_schema)
- gemini.temperature — `config.temperature` + `config.top_p`
- gemini.thinking — `config.reasoning` (effort medium, thinking_budget 256)
- gemini.tool_config_any — `config.tool_choice` (mode required → ANY)
- gemini.tool_config_auto — `config.tool_choice` (mode auto → AUTO)
- gemini.tool_config_none — `config.tool_choice` (mode none → NONE)
- gemini.top_k — `config.top_k`
- gemini.top_p — `config.top_p`
- openai.parallel_tool_calls — `config.tool_choice` (mode required, parallel true)
- openai.reasoning — `config.reasoning` (effort low)
- openai.structured_output — `config.response_format` (text format json_schema)
- openai.structured_output_json_object — `config.response_format` (json_object)
- openai.top_p — `config.top_p`

## Kept as extensions passthrough (4) — no canonical key exists

- anthropic.thinking — wire `thinking` carries `"display": "summarized"`; the
  canonical Reasoning type has no display knob and the Anthropic adapter only
  emits `{type, budget_tokens}` from Reasoning, so the byte-identical wire
  body cannot be produced canonically.
- anthropic.thinking_budget — same wire body / same `display` field as above.
- openai.max_tool_calls — top-level Responses `max_tool_calls` cap has no
  canonical Config field (it is not max_tokens and not ToolChoice).
- openai.code_interpreter — top-level Responses `include`
  (`code_interpreter_call.outputs`) has no canonical Config field.

Audit extensions-passthrough count: 22 → 4. Gates after rewrite: harness
request 69 pass / 0 fail; `--direction all` exit 0; check_provenance OK.
