# Together AI — provider dossier

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-26 | maintainer request (key added with credit) |
| researched | 2026-09-26 | this dossier; `scrapes/together/pages/` (24 pages); `sources/` (terms) |
| implemented | 2026-09-26 | `lm15.registry.PROVIDERS["together"]`, `lm15.access.TOGETHER`, compat preset `together` |
| offline-conformant | 2026-09-26 | auth case `together-env-selected`; support matrix row; `tests/test_inference_hosts.py` |
| live-verified | 2026-09-26 | 11 live cases, 4 consumer-side pins, 2 error envelopes, probes: `changes/2026-09-26-inference-hosts-live.md`, `receipts/2026-09-26-together/` |
| supported | 2026-09-26 | change entry ratified |

## Identity

- Service: Together AI serverless inference (`scrapes/together/pages/serverless--overview.md`).
- lm15 provider string: `together` — Chat Completions wire only. litellm spells it `together_ai/`.
- Base URL: `https://api.together.ai/v1` (`openai-compatibility.md`; `api.together.xyz` also answers — the documented host wins).
- Console: https://api.together.ai/settings/projects/~current/api-keys.  Env key: `TOGETHER_API_KEY`.
- `GET /models` lists dedicated-only models too; calling one answers 400 "Unable to access non-serverless model" (Qwen3-VL-32B, Qwen3-VL-8B, Llama-4-Scout, Gemma-4 on 2026-09-26).
- Not registered: batch, files, images, video, speech, fine-tuning, dedicated endpoints.

## Wire facts, each with its receipt (receipts/2026-09-26-together/)

| lm15 knob | Together wire | Live 2026-09-26 | Compat / decision |
|---|---|---|---|
| effort | `reasoning_effort` low/medium/high (gpt-oss); `reasoning: {enabled}` toggle; `chat_template_kwargs` | **gpt-oss runs xhigh, max and `bogus` at its default (medium)** (`probe-effort-word-*`); DeepSeek V4.1 refuses minimal/medium/bogus with 400 | per model: `("openai/gpt-oss", reasoning_efforts=low\|medium\|high)` — pin `reasoning_effort_max_gpt_oss` |
| reasoning off | `reasoning_effort: "none"` or `reasoning: {enabled: false}` | DeepSeek V4.1: honoured (`reasoning_off` case); **gpt-oss: trace hidden, reasoning tokens still billed**; **GLM-5.3: ignored** (`probe-off-reasoner`, `probe-off-always-on`); both shapes behave the same | `reasoning_off="lowest"` for gpt-oss and `zai-org/GLM-5.3`; pins `reasoning_off_gpt_oss`, `reasoning_off_glm` |
| reasoning out | `reasoning` (gpt-oss, DeepSeek V4 Pro) or `reasoning_content` (Kimi, GLM, DeepSeek V4.1) | both seen | both parsed to thinking |
| reasoning replay | "pass it back under the same key" (`openai-compatibility.md`) | DeepSeek V4.1: `reasoning_content` recalled 2 of 3, `reasoning` 2 of 3, absent 0 of 3 | `thinking_replay="native"` (`reasoning_content`) |
| max tokens | `max_tokens`; `max_completion_tokens` accepted | cap 8 → `finish_reason: length` (`probe-max-tokens-cap`) | `max_completion_tokens` |
| stream usage | `stream_options` | usage on the final chunk | include |
| tool choice | documented | Llama: required and named honoured, `none` answered prose; **gpt-oss: HTTP 500 "Internal server error" every time** on required (`probe-tool-choice-required-reasoner`) | `("openai/gpt-oss", forced_tool_choice="reject")` — a 500 is retryable; pin `tool_choice_required_gpt_oss` |
| gpt-oss tool loops | — | **server bug**: turn 1 content carries the model's reasoning and an invented answer; replaying the turn with `content: null` → 400 "prompt cannot be empty"; with `""` or omitted → the answer starts with the raw harmony channel word (`analysis…`, `final…`) | not worked around; documented for users (docs/providers-and-models.md) |
| structured output | json_schema | honoured on Llama and gpt-oss | send |
| images in tool results | — | **open cell**: credit limit (402) during the pass; the serverless vision model is Kimi-K3 | `tool_result_media="reject"` until a receipt (`tools/check_content_coverage.py` OPEN) |
| usage | nested details on reasoning models; **flat `usage.cached_tokens`** on Llama (docs: "a client configured for only one shape will return 0 … with no error") | `basic_text` | the dialect now reads both (nested first) |
| caching | automatic; `prompt_cache_key` documented | not exercised | `cache_control="none"` |
| models | `GET /models` → **bare JSON array** | 272 entries | dialect parser reads a bare array; case `entries_key: null` |
| errors | `{"error": {message, type, param, code}}`; Together's own type/code values | 401 `invalid_api_key`; 404 `model_not_available`; 402 "Credit limit exceeded" (flapping for minutes after a top-up) | `errors/cases/together.json` |

## Terms-of-service verdict

Source: `sources/together-terms-of-service.md`.  § 4: no competitive products, competitive
analysis or benchmarking; no reselling or offering the Services standalone; no sensitive personal
data (SSNs, card numbers…).  § 6: the account is charged a prepaid balance and the customer
authorizes automatic replenishment.  California law.

**Verdict: allowed, API key only.**  lm15 records wire facts, never performance figures.

## Open items

- Images in tool results (Kimi-K3) once the account has credit.
- Preserved thinking (`chat_template_kwargs.clear_thinking=false`) and per-turn toggles are not mapped.
