# DeepInfra — provider dossier

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-26 | maintainer request (key added with credit) |
| researched | 2026-09-26 | this dossier; `scrapes/deepinfra/pages/` (16 pages); `sources/` (terms) |
| implemented | 2026-09-26 | `lm15.registry.PROVIDERS["deepinfra"]`, `lm15.access.DEEPINFRA`, compat preset `deepinfra` |
| offline-conformant | 2026-09-26 | auth case `deepinfra-env-selected`; support matrix row; `tests/test_inference_hosts.py` |
| live-verified | 2026-09-26 | 11 live cases, 3 consumer-side pins, 1 tool-result refusal, 3 error envelopes, probes: `changes/2026-09-26-inference-hosts-live.md`, `receipts/2026-09-26-deepinfra/` |
| supported | — | after a reviewer ratifies the change entry |

## Identity

- Service: DeepInfra, open-model inference cloud (`scrapes/deepinfra/pages/index.md`).
- lm15 provider string: `deepinfra` — the OpenAI-compatible Chat Completions wire only.
- Base URL: `https://api.deepinfra.com/v1/openai` (`chat--overview.md`; the `/v1/openai` root, not `/v1`).
- Console: https://deepinfra.com/dash/api_keys.  Env key: `DEEPINFRA_API_KEY` (the name every docs example uses).
- Model ids are `vendor/name` (`meta-llama/Llama-3.3-70B-Instruct-Turbo`, `openai/gpt-oss-120b`).
- Not registered: the Anthropic Messages door, batch, files, image/speech/embedding endpoints, scoped JWT tokens.

## Wire facts, each with its receipt (receipts/2026-09-26-deepinfra/)

| lm15 knob | DeepInfra wire | Live 2026-09-26 | Compat / decision |
|---|---|---|---|
| effort | top-level `reasoning_effort` (none, minimal … max); `reasoning: {effort, enabled}` also documented | gpt-oss low 22 / high longer traces; `bogus` → 422 (validated enum); xhigh/max run as high | `thinking_format="reasoning_effort"` |
| reasoning off | `reasoning_effort: "none"` (docs) | DeepSeek V4.1: honoured (0 reasoning tokens, `reasoning_off` case); **gpt-oss: accepted, run as low** (`probe-off-reasoner`, trace present); Qwen3-30B: honoured | per model: `("openai/gpt-oss", reasoning_off="lowest")` — pin `deepinfra.reasoning_off_gpt_oss` |
| reasoning out | `message.reasoning_content` | every reasoning model | parsed to thinking |
| reasoning replay | — | code word in `reasoning_content` recalled 1 of 3 (gpt-oss), `reasoning` 0 of 3, absent 0 of 3 (`probe-replay-field-*`) | `thinking_replay="native"` |
| max tokens | `max_completion_tokens` accepted | cap 8 → `finish_reason: length`, 8 tokens (`probe-max-tokens-cap`) | `max_tokens_field="max_completion_tokens"` |
| stream usage | `stream_options.include_usage` | usage on the final chunk (`streaming`) | `stream_usage="include"` |
| tool choice | documented | **required / named ignored** on Llama 3.3 and gpt-oss (plain text, no call); `none` on Llama wrote `<function=get_weather>…` INTO the text; DeepSeek V4.1 honours all three (`probe-tool-choice-*`) | `forced_tool_choice="reject"` host-wide, `("deepseek-ai/DeepSeek-V4", "send")`; pins `tool_choice_required`, `tool_choice_required_deepseek` |
| structured output | `response_format` json_schema | honoured on Llama and gpt-oss (exactly the schema's keys) | send |
| images in tool results | — | **422** "Input should be a valid string" at `messages.2.tool.content` (Qwen3-VL-235B; the same model read the image as user content) | `tool_result_media="reject"`; case `tool_result_image_raise` |
| caching | automatic; `prompt_cache_key` + `prompt_cache_options: {mode, ttl: 5m\|1h}` + `prompt_cache_breakpoint` (retention) | not exercised | `cache_control="none"`: key/retention dropped with a record — **open item** below |
| usage | `prompt_tokens_details.cached_tokens`; `estimated_cost` (USD) on usage; gpt-oss reports no `completion_tokens_details` | `basic_text`, `reasoning_low` | reasoning tokens stay unknown (None) where not reported |
| models | `GET /models` → `data[]` | 187 entries (images, speech, embeddings included) | `models: true` |
| errors | `{"error": {message, type, param, code}}` | 401 `invalid_api_key`; 404 `model_not_found`; 422 on a bad effort word | `errors/cases/deepinfra.json` |

## Terms-of-service verdict

Source: `sources/deepinfra-terms.md` (sha256 in header).  § 11(a): no use competitive with
DeepInfra's business, no reselling or sharing credentials, no probing or scanning.  California law.
A documented-API client used by the key holder is authorized use.

**Verdict: allowed, API key only.**  lm15 records wire facts, never performance figures.

## Open items

- Caching: map `CacheConfig(key, retention="long")` onto `prompt_cache_key` + `prompt_cache_options.ttl` ("1h") and the breakpoint mark; needs a design pass (MAP-6) and a receipt.
- `usage.estimated_cost` is dropped by the parser (kept in the verbatim body only).
- Documents in tool results: untested (images already refused).
