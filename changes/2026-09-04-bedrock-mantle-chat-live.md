# 2026-09-04 — Amazon Bedrock Chat Completions on bedrock-mantle (`bedrock-mantle-chat`), live-verified

Status: RATIFIED 2026-09-06 (verify/DECISIONS-2026-09-06.md D2, changes/2026-09-06-ratification.md).
A tenth cloud door.  The original
design named nine (`changes/2026-09-03-cloud-hosts.md`); this one was
found live, not invented.  Dossier: `research/providers/bedrock-mantle-chat/`.

## Why a new name, not a setting on `bedrock-chat`

`bedrock-chat` is the **runtime** host
(`bedrock-runtime.{region}.amazonaws.com/openai/v1`, SigV4 service
`bedrock`, versioned ids, no listing).  This door is the **mantle** host
(`bedrock-mantle.{region}.api.aws/v1`, SigV4 service `bedrock-mantle`,
un-versioned ids, listing works).

A host setting cannot tell them apart: AUTH-10's settings list is closed
(`region`, `workspace`, `project`, `location`, `resource`,
`authority_host`, `scope`).  The two doors also differ in ways a URL
template cannot hide: model-id namespace, `/models`, reasoning shape,
which families honour `tool_choice`.

WHY not rename `bedrock-chat` to give mantle the short name: `bedrock-chat`
is already live-verified with cases, goldens, and receipts.  Renaming
that door without ratification would churn a proven pin.  AWS's own page
calls runtime "recommended" for new apps and still documents mantle
separately.

Trade-off, stated: a tenth hosted entry.  Users pick the host in the
provider string.

## What this proves

End to end against the real mantle Chat Completions endpoint, us-east-1:
the aws-chain used this machine's `~/.aws` profile; the host rendered
`https://bedrock-mantle.us-east-1.api.aws/v1`; SigV4 service
`bedrock-mantle` was accepted.  First 200: `openai.gpt-oss-20b` answering
"Say ok." with `message.reasoning` (a thinking part), not the runtime
door's inline `<reasoning>` tags.

## Cases (`cases/bedrock-mantle-chat/`, model `openai.gpt-oss-20b` unless noted)

| case | HTTP | what it pins |
|---|---|---|
| `basic_text` | 200 | SigV4; gpt-oss `message.reasoning` → thinking part + text `ok` |
| `streaming` | 200 | SSE, 6 events |
| `reasoning_low` | 200 | `reasoning_effort: low` accepted |
| `tools` | 200 | `tool_calls` |
| `streaming_tool_call` | 200 | streamed tool_calls |
| `multi_turn_tool_result` | 200 | live turn-1 replayed |
| `tool_choice_required` (deepseek.v3.2) | 200 | `tool_choice: required` honoured |
| `response_format_json_schema` (deepseek.v3.2) | 200 | `json_schema` honoured |
| `system_prompt` | 200 | `role: system` |
| `user_id` | 200 | `Config.user_id` → `user` |
| `models` | 200 | GET `/v1/models`, 55 ids, `supports.models` true |
| `tool_choice_required_gpt_oss` | — | **per-model refusal** |
| `response_format_json_schema_gpt_oss` | — | **per-model refusal** |

## Family knobs (receipts `probe-family-*.json`)

The door forwards both knobs.  Whether a family honours them is **not**
the same as on `bedrock-chat`:

| family | `tool_choice: required` | `json_schema` |
|---|---|---|
| DeepSeek, Mistral, Qwen, Z.AI | honoured | honoured |
| Gemma (`google.gemma-3-12b-it`) | **honoured** (ignored on runtime) | honoured |
| gpt-oss | **ignored** | **ignored** (prose + JSON) |

Preset `bedrock-mantle` sends both knobs and overrides only
`openai.gpt-oss` → reject both.  Gemma is **not** overridden here.
Copied runtime overrides would have broken Gemma on this door.

## Model ids and listing

| id form | HTTP | meaning |
|---|---|---|
| `openai.gpt-oss-20b` | 200 | un-versioned id; this door's namespace |
| `openai.gpt-oss-20b-1:0` | 404 `not_found_error` | runtime's versioned id is not served here |
| `anthropic.claude-haiku-4-5` | 400 `validation_error` "does not support `/v1/chat/completions`" | listed as available; Claude is the Messages door |
| `amazon.nova-2-lite-v1:0`, `amazon.nova-micro-v1:0` | 404 | Nova is not on this door (Converse, phase 2) |
| `GET /v1/models` (SigV4 and bearer) | 200, 55 ids | listing works; `supports.models` true |

Claude's 400 is loud, so no MAP-8 raise.  Mapped as `InvalidRequestError`
(`errors/cases/bedrock-mantle-chat.json` `claude_wrong_door`).

## Error envelopes

| id | HTTP | mapped |
|---|---|---|
| `invalid_signature` | 401 `invalid_api_key` | `AuthError` |
| `model_not_found` | 404 `not_found_error` | `UnsupportedModelError` |
| `bad_param` | 400 `validation_error` | `InvalidRequestError` |
| `claude_wrong_door` | 400 `validation_error` | `InvalidRequestError` |

## Reference

`AccessPolicy` `BEDROCK_MANTLE_CHAT`; registry `bedrock-mantle-chat` with
compat preset `bedrock-mantle`; `CLOUD_HOST_POLICIES` is ten.

`Capture.models_case` now pins `credential`/`now` on a SigV4 door so the
harness can reproduce `GET /models` byte for byte (it used `wire_block`
before, which redacts the signature).

## What is not yet evidenced

Other regions; GPT-5 / Grok ids that list as available (may be gated the
way Claude is on the Messages door); `cache_control`; streaming usage on
the final chunk as a dedicated pin (streaming case exists; chunk shape
not separately probed).
