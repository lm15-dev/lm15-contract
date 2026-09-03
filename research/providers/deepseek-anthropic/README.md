# DeepSeek over the Anthropic Messages wire — provider dossier

Same service as `deepseek` (see `research/providers/deepseek/README.md` for
identity, terms verdict, billing); a **different wire**.  A provider string
names wire behavior, so this is its own entry: `deepseek-anthropic`.

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-03 | named in the `deepseek` dossier § Wire endpoints |
| researched | 2026-09-03 | `scrapes/deepseek/pages/guide--anthropic-api.md`; 15 discovery probes (`receipts/2026-09-03-deepseek-anthropic/discovery-*.json`) |
| implemented | 2026-09-03 | `AnthropicCompat` (new), `AnthropicLM(compat=…)`, `lm15.access.DEEPSEEK_ANTHROPIC`, registry entry |
| offline-conformant | 2026-09-03 | 4 pinned refusals; auth case; support matrix; registry tests |
| live-verified | 2026-09-03 | 9 cases, 3 error envelopes, 11 probes: `changes/2026-09-03-deepseek-anthropic-live.md` |
| supported | — | after ratification |

## Why this endpoint was the third provider

It is the first **bound entry on a second dialect**.  Until it, every
registry binding was `OpenAIChatLM`; `AnthropicLM` had no compat layer.  Now
`ProviderDefinition` validates a bound entry against its dialect's preset
and URL tables (`registry._COMPAT_TABLES`), the router picks the dialect
class from the entry, and Kimi / MiniMax / Moonshot are data.

## Wire facts, each with its receipt

Base URL `https://api.deepseek.com/anthropic/v1` (the docs give
`…/anthropic`; both roots answer — `discovery-base-*.json`).  Auth
`x-api-key`; `anthropic-version` ignored.

| lm15 knob | this endpoint | live 2026-09-03 | compat / decision |
|---|---|---|---|
| reasoning default | ON | `basic_text`: signed thinking block for "Say ok." | omitted = provider default |
| reasoning off | `thinking: {type: disabled}` | honoured (`reasoning_off`: text only) | `thinking_format="deepseek"` **sends** off — on the plain Anthropic wire absence is off; here absence is on |
| effort | `thinking: {type: enabled}` + `output_config.effort` ∈ low, medium, high, xhigh, ultra, max (the 400 for `minimal` lists it) | `reasoning_low`; probes medium/xhigh/max 200; `minimal` 400 | verbatim; `max_tokens` is the total (no budget added) |
| `thinking_budget` | `budget_tokens` ignored (docs; `discovery-lm15-manual-class-budget`) | — | **refused** before the wire (`reasoning_thinking_budget`) |
| model names | `claude-opus*` → `deepseek-v4-pro`, `claude-haiku*`/`sonnet*` → `deepseek-v4-flash` silently; unknown → 400 | `discovery-model-claude-opus`: 200, `model: deepseek-v4-pro` | **refused**: `model_prefixes=("deepseek-",)` (`model_claude_substituted`) |
| structured output | `output_config.format` accepted, schema ignored | `discovery-output-config-format`: 200, wrong keys | **refused** (`response_format_json_schema`) |
| `tool_choice.parallel` | `disable_parallel_tool_use` ignored (docs) | not observable with one tool | **refused** (`tool_choice_parallel_false`, documentation-level) |
| thinking replay | thinking blocks carry `signature` (= message id) | `multi_turn_tool_result`: signed replay 200; `discovery-tool-result-without-thinking`: also 200 | dialect default (signed native replay); not required by this wire, unlike the chat wire |
| tools | `tool_use` / `tool_result`, ids `call_00_…` | `tools`, `streaming_tool_call` | dialect default |
| caching | `cache_control` ignored; implicit; `cache_read_input_tokens` reported | `cache-second`: 256 read | `cache_control="none"`: marks not placed, `CacheConfig` not an error (chat-dialect precedent) |
| `user_id` | `metadata.user_id` supported | `user_id` | dialect default |
| `top_k` | ignored | `top-k`: 200 | documented, not raised (sampling knobs: same rule as temperature-in-thinking) |
| `stop` | `stop_sequences` | `stop-sequence`: `stop_reason: stop_sequence` | dialect default |
| models | `GET /models` → 404 | `discovery-models` | `models=False`; list through `deepseek` |
| errors | **OpenAI-shaped** envelope on an Anthropic wire: `{"error": {message, type, param, code}}` | 401 `authentication_error`, 400 `invalid_request_error` | `AnthropicLM` reads `error.type` → `AuthError` / `InvalidRequestError`; works as-is |

## Open items

- Images (`deepseek-v4-flash-vision-exp`, base64/url) not captured.
- The Files API variant (`source.type=file` with `anthropic-beta:
  files-api-2025-04-14`) not researched.
- Effort vocabularies differ between DeepSeek's two wires (`minimal` OK on
  chat, 400 here; `ultra` exists here only).  lm15 passes the word through
  and the server is the judge; no table is kept.
