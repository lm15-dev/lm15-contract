# 2026-09-03 — Moonshot AI's Responses and Anthropic wires live-verified; four Anthropic-compat knobs from the wire

Status: RATIFIED 2026-09-06 (wire facts: cases, bodies, errors, receipts). Goldens: see changes/2026-09-06-ratification.md.
Follows `changes/2026-09-03-moonshotai-live.md`
(the Chat Completions wire); dossier at `research/providers/moonshotai/README.md`
(one dossier, three strings).  One provider string names one wire
(`changes/2026-09-03-provider-registry.md`), so the two further wires are
`moonshotai-responses` and `moonshotai-anthropic` — the `deepseek` /
`deepseek-anthropic` and `meta*` precedents.  Same key, same two env names.

## `moonshotai-responses` (`cases/moonshotai-responses/`, bodies verbatim, kimi-k3)

| case | body | HTTP | what it pins |
|---|---|---|---|
| `basic_text` | 2026-09-03T13-16-11Z | 200 | `reasoning` item with the reasoning in `summary[].text`, no `encrypted_content`; `store: false`, `previous_response_id: null` |
| `streaming` | 13-16-15Z | 200 | `reasoning_summary_text.delta` then `output_text.delta` |
| `reasoning_low` | 13-16-19Z | 200 | `reasoning.effort: low` |
| `tools` | 13-16-22Z | 200 | `function_call` with `call_id: get_weather_0`, `id: fc_…` |
| `streaming_tool_call` | 13-16-28Z | 200 | name on `output_item.added`, then `function_call_arguments.delta` |
| `multi_turn_tool_result` | 13-16-40Z | 200 | the stateless replay: the reasoning item with its summary text + `function_call` + `function_call_output` |
| `response_format_json_schema` | 13-16-44Z | 200 | strict schema honoured exactly |
| `system_prompt` | 13-16-52Z | 200 | `developer` role item |
| `user_id` | 13-16-58Z | 200 | `safety_identifier` |
| `web_search` | 13-17-03Z | 200 | the server-side built-in: `web_search_call` leads the output; 4,627 input tokens |
| `models` | 13-17-10Z | 200 | 4 ids (the same `GET /v1/models`) |

Nine error envelopes (`errors/cases/moonshotai-responses.json`): this wire
**validates** — `reasoning.effort: none` and `bogus`, `tool_choice`
`required` / `none`, `text.format: json_object`, `temperature`,
`prompt_cache_retention`, an unknown builtin type, an unknown model
(`code: model_not_found` on HTTP 400) are all 400 with a message.  So no
refusal knob is needed here.  One consequence stated plainly: `medium`
answers 200 on this wire (the server names it supported while the docs
list low|high|max), so the word goes out verbatim (MAP-7 rule 2 — the
server decides when it validates), whereas the chat and Anthropic wires,
which accept `bogus` too, get the client-side allowlist.  Different
evidence, different decision.

No new Responses-compat field.  The stateless reasoning replay — a
`reasoning` item carrying `summary: [{summary_text}]` — is what the
dialect already sends for a ThinkingPart with text (Meta pass).  The
`web_search` built-in rides `builtin_tools="verbatim"`: the canonical name
is the wire type on this server as on Meta's.  The value was first
written as `"meta"` and renamed the same day (the Meta entry, still
unratified, is amended in place): a shape is not named after the first
server that needed it.  `CacheConfig(retention="long")` reaches the
wire as `prompt_cache_retention` and is refused loudly by the server; the
docs note says so.

Harness (python shim): request 246, response 200, stream 32, error 64,
auth 37, models 28 — 0 failures.

## `moonshotai-anthropic` (`cases/moonshotai-anthropic/`, bodies verbatim, kimi-k3)

| case | body | HTTP | what it pins |
|---|---|---|---|
| `basic_text` | 13-15-21Z | 200 | thinking block first, **no signature**; disjoint usage (`input_tokens: 0`, `cache_read_input_tokens: 88`), `output_tokens_details.thinking_tokens` |
| `streaming` | 13-15-26Z | 200 | 23 `thinking_delta`, 2 `text_delta`, no `signature_delta` |
| `reasoning_low` | 13-15-30Z | 200 | `output_config.effort: low` alone — the `effort` shape |
| `reasoning_off` | 13-19-09Z | 200 | `thinking: {type: disabled}` alone: no thinking block, no thinking_tokens — the schema lists no thinking field |
| `tools` | 13-15-32Z | 200 | `tool_use` id `get_weather_0`, `stop_reason: tool_use` |
| `streaming_tool_call` | 13-15-39Z | 200 | `input_json_delta` |
| `multi_turn_tool_result` | 13-15-51Z | 200 | the live turn-1 **unsigned** thinking block replayed as a `thinking` block (`thinking_replay="unsigned"`) with the `tool_use` and a `tool_result` |
| `response_format_json_schema` | 13-15-55Z | 200 | `output_config.format` honoured exactly |
| `system_prompt` | 13-16-00Z | 200 | top-level `system` string |
| `user_id` | 13-16-05Z | 200 | `metadata.user_id` |
| `reasoning_effort_medium` | — | raise | **refusal** |
| `temperature` | — | raise | **refusal** |
| `tool_choice_parallel_false` | — | raise | **refusal** |

`GET /anthropic/v1/models` is **404** (`receipts/2026-09-03-moonshotai-anthropic/discovery-models-404.txt`);
`models: false`, as `deepseek-anthropic`.  Three envelopes pinned (401
`invalid_authentication_error`, 404 `resource_not_found_error`, 400 named
tool_choice "incompatible with thinking enabled").

## Four `AnthropicCompat` fields, each from a receipt

1. **`thinking_format="effort"`.**  The schema has no `thinking` request
   field; `output_config.effort` low|high|max is the whole dial.  Live:
   effort alone 200; `thinking: {type: adaptive}` 200 (ignored — not
   sent); `{type: enabled, budget_tokens}` 200 with 240 thinking tokens
   (not translated — `thinking_budget` raises as on the adaptive class);
   **`{type: disabled}` 200 and honoured**.  So: effort word →
   `output_config.effort` alone; off → `thinking.type=disabled`.
2. **`thinking_replay="unsigned"`.**  Every thinking block comes back with
   `signature: ""` or none, and the dialect's rule (decision G) replays an
   unsigned ThinkingPart as a text block — on this server that would put
   the model's reasoning into its spoken turn.  Live: an unsigned
   `thinking` block replayed → 200 (`probe-replay-unsigned-thinking-block`);
   the block omitted → 200 too.  The preset replays it as `thinking`.
   The dialect default stays `"signed"`; api.anthropic.com is untouched.
3. **`sampling_params="reject"`.**  `temperature: 0.5` and `top_k: 1` →
   200 on this wire; the same server's chat wire answers 400 "only 1 is
   allowed for this model".  The model's sampling is fixed and the field
   is swallowed — MAP-8 §2, refuse.  Pinned refusal
   `moonshotai-anthropic.temperature`.
4. **`reasoning_efforts=("low","high","max")`.**  `medium` → 200 (12
   thinking tokens), `bogus` → 200 (70).  The allowlist from the chat
   compat, same rule (MAP-7 rule 2).  Pinned refusal
   `reasoning_effort_medium`.

Plus `parallel_tool_calls="reject"` on documentation evidence:
`MessagesToolChoice` carries only `type`; a hand-sent
`disable_parallel_tool_use` answered 200 with one call, which proves
nothing either way; a field the server does not document is not sent as
a silent no-op (the DeepSeek precedent).  Pinned refusal
`tool_choice_parallel_false`.  Stated trade-off: if the server does honour
it, callers lose a knob until a probe with a two-tool prompt proves it.

Error mapping: the Anthropic dialect learns `resource_not_found_error`
(→ `UnsupportedModelError` when the message names a model, as on the chat
wire; `InvalidRequestError` otherwise) and `invalid_authentication_error`
(→ `AuthError`).

## Reference changes (lm15-python)

- `compat.py`: Responses preset `moonshotai` + base URL; Anthropic preset
  `moonshotai` + base URL (`/anthropic/v1`); `AnthropicThinkingFormat`
  gains `"effort"`; new `AnthropicCompat` fields `thinking_replay`,
  `sampling_params`, `reasoning_efforts`; resolved and auto-default tables.
- `providers/anthropic.py`: the `effort` branch, the unsigned replay, the
  sampling refusal, the allowlist; two error types.
- `access.py`: `MOONSHOTAI_RESPONSES`, `MOONSHOTAI_ANTHROPIC` (bearer).
- `registry.py`: two entries.
- `tests/test_registry.py`: `TestMoonshotai` +4 (9 total).
- Docs: providers table (+2 rows) and note, authentication, router pages,
  CHANGELOG.

## Also in this entry

- `research/providers/moonshotai-responses/capture.py` (16 probes),
  `research/providers/moonshotai-anthropic/capture.py` (20 probes, one
  with hand-built headers for the `x-api-key` question).
- `auth/resolution.json` (+ the reference's conformance copy): 2 cases.
- `spec/support-matrix.json`: 2 rows.
- Goldens drafted (`goldens/moonshotai-responses/`, `goldens/moonshotai-anthropic/`, scribe-draft).

Ratified-by: (pending)
