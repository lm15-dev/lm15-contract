# 2026-09-04 — Azure OpenAI v1 over the Chat Completions wire (`azure-chat`), live-verified

Status: DRAFT, pending ratification.  Same resource, same key, same lab
as `changes/2026-09-04-azure-live.md` (read that entry first: the host,
auth and quota findings are stated once, there).  Dossier:
`research/providers/azure-chat/README.md`.

## Cases (`cases/azure-chat/`, bodies verbatim, model = deployment `gpt-4.1-mini`)

| case | HTTP | what it pins |
|---|---|---|
| `azure-chat.basic_text` | 200 | `api-key`, `model` = deployment; Azure adds `prompt_filter_results` and per-choice `content_filter_results` (passthrough) |
| `azure-chat.streaming` | 200 | `stream_options.include_usage` honoured: usage on the final chunk |
| `azure-chat.tools` | 200 | `tool_calls`, `call_…` ids |
| `azure-chat.streaming_tool_call` | 200 | streamed `tool_calls` deltas |
| `azure-chat.multi_turn_tool_result` | 200 | live turn-1 replayed with a `tool` message |
| `azure-chat.tool_choice_required` | 200 | forced call honoured (the model called `get_weather` twice) |
| `azure-chat.response_format_json_schema` | 200 | strict schema honoured: `{"city":"Paris","country":"France"}` |
| `azure-chat.system_prompt` | 200 | `role: system` |
| `azure-chat.user_id` | 200 | `Config.user_id` → `user`, accepted |
| `azure-chat.models` | 200 | the same `GET /openai/v1/models` catalog (207 entries) |
| `azure-chat.reasoning_low` | 200 | `gpt-5-mini`, `reasoning_effort: low` accepted |
| `azure-chat.reasoning_high` | 200 | effort high; nonzero `reasoning_tokens` (hundreds) |
| `azure-chat.prompt_cache_key` | 200 | warm 4K-token prefix: 4,096 cached tokens |
| `azure-chat.content_filter_completion` | 200 | `finish_reason: content_filter`, per-choice self-harm filter metadata |

No refusals.  The two cells Bedrock's gateway ignored (forced
`tool_choice`, `json_schema`) are honoured here, so the door keeps the
`openai` compat preset — Azure's gateway forwards OpenAI semantics
unchanged. Goldens drafted (`goldens/azure-chat/`, scribe-draft, 14).
Sync and async complete/stream both ran live.

## Auth (receipts `probe-entra-*.json`)

Both Entra scopes 200; the service principal through `azure-chain` 200
by secret and 200 by certificate — the same four results as the
Responses door, on the Chat path.

## Error envelopes (`errors/cases/azure-chat.json`)

| id | HTTP | wire | mapped |
|---|---|---|---|
| `unauthenticated` | 401 | gateway shape `{"error": {"code": "401", …}}` | `AuthError` |
| `deployment_not_found` | 404 | `code: DeploymentNotFound` | `UnsupportedModelError` (mapping added; see the `azure` entry) |
| `rate_limited` | 429 | `type: too_many_requests`, `code: rate_limit_exceeded` | `RateLimitError` |
| `content_filter` | 400 | prompt blocked, `code: content_filter` | `InvalidRequestError` |

Stated: the third envelope was meant to be a context-length error
(~400K tokens of input).  On a 200K tokens-per-minute quota the rate
limiter answers before the context check does, so the case pins the
rate-limit envelope and is named for what it is.  A context-length
envelope on this door is still unpinned; it needs more quota or a
smaller-context deployment.

## Not yet evidenced

A context-length envelope (the rate limit answers first on this quota);
Foundry-sold non-OpenAI models on this wire (DeepSeek, Grok — the docs
say the same path serves them); other regions. Account surfaces are
owned by the `azure` Responses adapter: use it for Files, Batch, speech,
images and Realtime rather than `azure-chat`.
