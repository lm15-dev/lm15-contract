# 2026-09-03 — DeepSeek over the Anthropic wire: the registry's second dialect, live-verified

Status: DRAFT, pending ratification.  Third provider through the registry
pathway; dossier `research/providers/deepseek-anthropic/README.md`.

## Why this one

Every bound registry entry so far was `OpenAIChatLM`.  `AnthropicLM` had
no compat layer, so the Anthropic-compatible services (Kimi, MiniMax,
Moonshot) could not be data.  DeepSeek's Anthropic endpoint uses a key we
already hold, so the design step cost no new account.  It also carries a
hazard worth designing against: it serves `claude-*` names with DeepSeek
models and says so only in `response.model`.

## Reference changes (lm15-python)

- `compat.AnthropicCompat` (new, small): `thinking_format` anthropic |
  deepseek, `cache_control` anthropic | none, `structured_output` and
  `parallel_tool_calls` send | reject, `model_prefixes`.  Presets
  `anthropic` (all defaults) and `deepseek`; `ANTHROPIC_PRESET_BASE_URLS`.
- `AnthropicLM(compat=…)` (and the async mirror) consult it at five stated
  points: the model-prefix guard, cache marks, the thinking wire, the
  `response_format` guard, the `parallel` guard.  Plain Anthropic is
  byte-for-byte unchanged (manual class still sends `budget_tokens`;
  pinned in `tests/test_registry.py`).
- `registry`: a bound entry is validated against its dialect's preset and
  URL tables (`_COMPAT_TABLES`); `_anthropic_bound`.  `router`: bound
  entries take their dialect class from the entry (`_adapter_for`),
  `CHAT_PRESET_ROUTES` keeps its meaning (chat-bound only), routability
  and env keys come from the registry; `doctor` lists the registry.
- `access.DEEPSEEK_ANTHROPIC`: `x-api-key`, `DEEPSEEK_API_KEY`,
  `models=False`.

## Cases (`cases/deepseek-anthropic/`, model `deepseek-v4-flash`)

| case | body | what it pins |
|---|---|---|
| `basic_text` | 2026-09-03T02-17-55Z | thinking on by default; the thinking block carries a `signature` |
| `streaming` | 02-17-57Z | Anthropic SSE vocabulary: 14 thinking deltas, 2 continuation (signature) deltas, 2 text |
| `reasoning_off` | 02-17-59Z | `thinking: {type: disabled}` SENT and honoured — absence means on here |
| `reasoning_low` | 02-18-01Z | `thinking: {type: enabled}` + `output_config.effort: low`, no budget, `max_tokens` as given |
| `tools` | 02-18-03Z | signed thinking + `tool_use` (`call_00_…`), `cache_read_input_tokens: 256` |
| `streaming_tool_call` | 02-18-04Z | `input_json_delta` |
| `multi_turn_tool_result` | 02-18-07Z | the live turn-1 message (signed thinking + tool_use) replayed |
| `system_prompt` | 02-18-09Z | top-level `system` |
| `user_id` | 02-18-11Z | `metadata.user_id` |
| `model_claude_substituted` | raise | `UnsupportedModelError` — `claude-opus-4-1` was served by `deepseek-v4-pro` (`discovery-model-claude-opus.json`, HTTP 200) |
| `response_format_json_schema` | raise | `output_config.format` accepted, schema ignored (`discovery-output-config-format.json`) |
| `reasoning_thinking_budget` | raise | `budget_tokens` ignored (docs; `discovery-lm15-manual-class-budget.json`) |
| `tool_choice_parallel_false` | raise | `disable_parallel_tool_use` ignored (documentation-level, stated) |

Goldens drafted.  `errors/cases/deepseek-anthropic.json`: 401, unknown
model 400, bad effort 400 — an **OpenAI-shaped envelope on the Anthropic
wire**; `AnthropicLM` reads `error.type` and maps correctly as-is.
Harness: request 181, response 151, stream 20, error 29, auth 17, models
18 — 0 failures.

## What the wire decided

| question | wire | decision |
|---|---|---|
| does lm15's Anthropic thinking wire work here? | `budget_tokens` ignored → `effort` silently lost; absence of `thinking` → on | new `thinking_format="deepseek"`; off is sent, effort rides `output_config` |
| effort vocabulary | `low, medium, high, xhigh, ultra, max`; `minimal` 400 (chat wire accepts it) | verbatim; the server judges |
| is thinking replay required with tools? | 200 with and without the block | dialect default (signed native replay) stays |
| caching | marks ignored; implicit, `cache_read_input_tokens` reported | `cache_control="none"`, chat-dialect precedent |
| `top_k` | accepted, ignored | documented, not raised (sampling-knob rule) |
| `/models` | 404 | `models=False`; typed `UnsupportedFeatureError` |

## Also

- `research/providers/_capture.py`: `x-api-key` / `x-goog-api-key` /
  `api-key` are now redacted in wire blocks.  The first capture wrote the
  real key into nine case files; `tools/check_secrecy.py` failed before
  anything was committed and the files were scrubbed (no commit ever held
  the key).  The library's summary and provenance strings are dialect-neutral.
- `spec/support-matrix.json`: `deepseek-anthropic`.  `auth/resolution.json`:
  `deepseek-anthropic-env-selected` — a second provider string on one env
  key.  Ports' tables gain the line.

Ratified-by: (pending)
