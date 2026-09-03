# 2026-09-03 — DeepSeek live-verified: eleven cases, four error envelopes, six decisions closed

Status: DRAFT, pending ratification.  Completes
`changes/2026-09-03-provider-registry.md` § What is not yet evidenced.
Every wire fact in that entry's `deepseek` rows now has a receipt.

Captured by `research/providers/deepseek/capture.py` against
`api.deepseek.com`, model `deepseek-v4-flash`, all wires built by the
reference adapter (`OpenAIChatLM` with the `deepseek` compat preset and
access policy bound) and sent verbatim.  Total spend: under $0.02.

## Cases (`cases/deepseek/`, bodies verbatim under `bodies/deepseek.*/`)

| case | body | HTTP | what it pins |
|---|---|---|---|
| `deepseek.basic_text` | 2026-09-03T01-11-03Z | 200 | thinking on by default: `reasoning_content` + `content`; `reasoning_tokens: 20` |
| `deepseek.streaming` | 2026-09-03T01-11-05Z | 200 | 12 thinking deltas then 2 text deltas; usage on the final chunk; `data: [DONE]` |
| `deepseek.reasoning_off` | 2026-09-03T01-11-07Z | 200 | `thinking: {type: disabled}` honoured: no `reasoning_content`, no `reasoning_tokens` |
| `deepseek.reasoning_low` | 2026-09-03T01-11-09Z | 200 | `thinking: enabled` + `reasoning_effort: low`; 37 reasoning tokens |
| `deepseek.tools` | 2026-09-03T01-11-11Z | 200 | tool call `call_00_…` with `reasoning_content` in the same message; `finish_reason: tool_calls` |
| `deepseek.streaming_tool_call` | 2026-09-03T01-11-13Z | 200 | the MAP-9 streamed call for this provider |
| `deepseek.multi_turn_tool_result` | 2026-09-03T01-11-16Z | 200 | **the load-bearing case**: the live turn-1 assistant message replayed with its `reasoning_content` (compat `thinking_replay=native`), tool result appended, answer 200 with `cached_tokens: 384` |
| `deepseek.response_format_json_object` | 2026-09-03T01-11-18Z | 200 | the only structured mode DeepSeek offers |
| `deepseek.system_prompt` | 2026-09-03T01-11-19Z | 200 | `role: system` |
| `deepseek.models` | 2026-09-03T01-11-21Z | 200 | 3 ids: `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-v4-flash-vision-exp`; `owned_by` only |
| `deepseek.user_id` | 2026-09-03T01-13-16Z | 200 | `Config.user_id` → DeepSeek's `user_id` field (new compat `user_field`) |

Every non-stream body parses with an empty `_lm15_unmapped` canary.
Goldens drafted by `tools/scribe_goldens.py` under `goldens/deepseek/`
(source `scribe-draft`; the models golden was written by the same
projection, origin stripped, as `goldens/xai/models.json`).  Harness:
request 157, response 137, stream 16, error 22, models 16 — 0 failures.

## Error envelopes (`errors/cases/deepseek.json`)

OpenAI-shaped `{"error": {message, type, param, code}}`.  Four verbatim:

| case | HTTP | `type` | `code` | lm15 class |
|---|---|---|---|---|
| `deepseek.unauthenticated` | 401 | `authentication_error` | `invalid_request_error` | `AuthError` |
| `deepseek.model_not_found` | 400 | `invalid_request_error` | `invalid_request_error` | `InvalidRequestError` |
| `deepseek.bad_effort` | 400 | `invalid_request_error` | `invalid_request_error` | `InvalidRequestError` |
| `deepseek.missing_reasoning_content_with_tools` | 400 | `invalid_request_error` | `invalid_request_error` | `InvalidRequestError` |

Note the 401's `code` is `invalid_request_error` while its `type` is
`authentication_error`; lm15 classifies by HTTP status, so
`provider_code` carries the odd `code` verbatim and the class is right.
The 401 message echoes the last four characters of the key
(`****alid`); the probe used the literal `sk-invalid`, so nothing real
is in the corpus (`check_secrecy` OK).

## The six open decisions (dossier § Open decisions), closed

1. **`user` vs `user_id`.**  Probes: `user` → 200, `user_id` → 200,
   `user_id: "bad id!"` (outside the documented charset) → 200.  The
   wire accepts anything and echoes nothing, so it cannot tell us
   whether `user` does anything.  The docs name `user_id` for
   content-safety, KV-cache and scheduling isolation.  **Decision: send
   the documented name.**  `OpenAIChatCompat.user_field: "user" |
   "user_id"` (default `user`; `deepseek` preset `user_id`).  Pinned by
   `deepseek.user_id`.
2. **Temperature in thinking mode.**  `temperature: 0.0` with thinking
   on → 200, 17 reasoning tokens, no error, no echo — silently accepted
   as the docs say.  **Decision: do not raise; document.**  It costs
   nothing extra (the xAI precedent raised on a *paid* silent no-op),
   and raising would make `Config(temperature=…)` fail on the provider's
   default mode.  Stated trade-off: a user who sets `temperature=0` for
   determinism does not get it while thinking is on; the docs say so.
3. **`minimal` effort.**  Accepted (200, 80 reasoning tokens — more than
   `medium`'s 25; one sample each, not a finding).  The `bad_effort` 400
   is authoritative on the accepted set: `none, minimal, low, medium,
   high, xhigh, max` — the whole lm15 vocabulary, wider than the docs'
   `low|high|max`.  **Decision: verbatim pass-through stays.**
4. **`json_schema`.**  400 `"This response_format type is unavailable
   now"`.  Loud.  **Decision: no knob; the server's refusal is the
   error.**  Receipt `probe-json-schema.json`.
5. **Cache usage spelling.**  DeepSeek sends both
   `prompt_tokens_details.cached_tokens` and `prompt_cache_hit_tokens`,
   equal (128 on the second identical request; 384 on the tool-result
   turn).  The chat dialect's usage parser already reads the first.
   **Decision: no change.**
6. **`insufficient_system_resource`.**  Not observed.  Stays unmapped
   until a sighting (the adapter records it in the canary, never guesses).

## Reference changes (lm15-python, same commit series)

- `OpenAIChatCompat.user_field` (+ resolved default `"user"`); the chat
  serializer writes `Config.user_id` under `compat.user_field`.
- `deepseek` preset: `user_field="user_id"`.
- Docs: providers table notes temperature-in-thinking and the PRC data
  residency.

## Receipts

`receipts/2026-09-03-deepseek/`: `models.json`, `probe-*.json` (sent wire
with `$DEEPSEEK_API_KEY`, status, verbatim body), `SUMMARY.json`.

Ratified-by: (pending)
