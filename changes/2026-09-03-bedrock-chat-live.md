# 2026-09-03 — Amazon Bedrock over the Chat Completions wire (`bedrock-chat`), live-verified

Status: DRAFT, pending ratification.  First cloud door through the
cloud-hosts pathway (`changes/2026-09-03-cloud-hosts.md`, ratified the
same day); dossier at `research/providers/bedrock-chat/README.md`.

## What this proves

The whole AWS path, end to end, against a real endpoint: the `aws-chain`
picked this machine's `~/.aws/credentials` and its profile `region`
fallback; the host rendered `https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1`;
the standard-library SigV4 signer (service `bedrock`) was accepted on
every request — the first `200` was
`openai.gpt-oss-20b-1:0` answering "Say ok."  No key touched the
environment or a file: the capture ran through lm15's own chain.

## Cases (`cases/bedrock-chat/`, bodies verbatim, model `openai.gpt-oss-20b-1:0`, region `us-east-1`)

Every case pins `settings`, a fixed `credential` (the AWS test pair
`AKIDEXAMPLE`) and `now` (the capture instant); its `authorization`
header is the signature a port must reproduce byte for byte — the
harness compares it exactly (request direction: 10/10).

| case | HTTP | what it pins |
|---|---|---|
| `bedrock-chat.basic_text` | 200 | SigV4 headers; gpt-oss emits `<reasoning>…</reasoning>` inline in `content` (passthrough text, not a thinking part) |
| `bedrock-chat.streaming` | 200 | `stream_options.include_usage` honoured: usage on the final chunk |
| `bedrock-chat.reasoning_low` | 200 | `reasoning_effort: low` accepted; usage carries `prompt_tokens_details` (cached 32, audio 0) |
| `bedrock-chat.tools` | 200 | `tool_calls`, `call_…` ids |
| `bedrock-chat.streaming_tool_call` | 200 | streamed `tool_calls` deltas |
| `bedrock-chat.multi_turn_tool_result` | 200 | live turn-1 replayed with a tool result |
| `bedrock-chat.system_prompt` | 200 | `role: system` |
| `bedrock-chat.user_id` | 200 | `Config.user_id` → `user` |
| `bedrock-chat.tool_choice_required` (deepseek.v3.2) | 200 | `tool_choice: required` honoured — a call |
| `bedrock-chat.response_format_json_schema` (deepseek.v3.2) | 200 | `json_schema` honoured — a pure JSON document |
| `bedrock-chat.tool_choice_required_gpt_oss` | — | **per-model refusal** (below) |
| `bedrock-chat.response_format_json_schema_gpt_oss` | — | **per-model refusal** (below) |

Goldens drafted (`goldens/bedrock-chat/`, scribe-draft, 10).  Harness at
HEAD: request 276, response 222, stream 34, error 76 — 0 failures.

## The door forwards the knobs; two model families ignore them (MAP-8, per model)

First pass (gpt-oss-20b): `tool_choice: required` → HTTP 200, plain text,
no call; `response_format` `json_schema` → HTTP 200, reasoning text +
prose + a JSON object.  Pinning those as door-wide refusals would have
been wrong, so the same two requests went to one model from each family
the door serves (`receipts/2026-09-03-bedrock-chat/family-*.json`,
raw bodies, SigV4):

| family (model) | `tool_choice: required` | `json_schema` |
|---|---|---|
| DeepSeek (`deepseek.v3.2`) | honoured (call) | honoured (pure JSON) |
| Mistral (`mistral-large-3-675b-instruct`) | honoured | honoured |
| Qwen (`qwen3-32b-v1:0`) | honoured | honoured |
| Z.AI (`zai.glm-4.7-flash`) | honoured | honoured |
| Gemma (`google.gemma-3-12b-it`) | **ignored** | honoured |
| gpt-oss (`20b`, `120b`) | **ignored** | **ignored** |

Rule, stated: the door is honest — it forwards every knob to the
vendor's model; whether the model honours it is per family.  The unit
of a refusal is therefore the model family, not the door.  New
mechanism in the reference (spec-level, this entry):
**`OpenAIChatCompat.model_overrides`** — `(model-id prefix, {knob:
value})` pairs, first match wins, resolved per request.  The `bedrock`
preset sends both knobs and overrides `openai.gpt-oss` → reject both,
`google.gemma` → reject `tool_choice`.  A direct
`OpenAIChatLM(access=BEDROCK_CHAT)` with no `compat=` now finds the
registry's preset (found missing while testing this).

Cases: `tool_choice_required` and `response_format_json_schema` are
captured on `deepseek.v3.2` (honoured, 2026-09-04);
`tool_choice_required_gpt_oss` and `response_format_json_schema_gpt_oss`
are the pinned per-model refusals (`expect_lm15.raises`).

The door's catalog (`door-catalog-sweep.json`, every text model in
`ListFoundationModels` us-east-1 sent "Say ok."): 34 answer 200
(nvidia, qwen, moonshot, openai gpt-oss, deepseek, minimax, zai,
mistral, google gemma, writer…), 55 answer 404 "doesn't support this
API" (every versioned `…-v1:0` id and every `us.` inference profile —
the legacy namespace), 20 answer 403 `access_denied` (the un-versioned
5-series ids: `anthropic.claude-opus-5`, `openai.gpt-5.6-*`,
`xai.grok-4.6` — gated, below), 10 answer 400 for Amazon Nova:
`#/messages/0/content: expected type: JSONArray, found: String`.  Nova
wants every message's content as a parts array; lm15 sends a string for
plain text.  Loud, so no MAP-8 raise; a `text_content: parts` compat
knob is the fix and is a stated gap.

The rest of the preset from the same receipts: `instruction_role: system`,
`max_tokens_field: max_completion_tokens`, `stream_usage: include`,
`thinking_format: reasoning_effort`, `user_field: user`,
`cache_control: none` (not probed; the safe value).

## Model ids and listing (receipts `probe-model-id-*.json`, `probe-models-list.json`)

| id form | HTTP | meaning |
|---|---|---|
| `openai.gpt-oss-20b-1:0` | 200 | works with no agreement |
| `anthropic.claude-sonnet-5`, `anthropic.claude-opus-4-7` | 403 `access_denied` "not available for this account" | the Claude 5 ids are the door's namespace; the account lacks the model agreement |
| `anthropic.claude-haiku-4-5` | 400 `validation_error` "identifier is invalid" | not an id on this door |
| `us.anthropic.claude-haiku-4-5-20251001-v1:0`, `amazon.nova-micro-v1:0`, `us.amazon.nova-micro-v1:0`, `global.anthropic.claude-opus-4-6-v1` | 404 `model_not_found` "doesn't support this API" | legacy ids and inference profiles are not served here |
| `GET /openai/v1/models` (SigV4) | 404 `<UnknownOperationException/>` | no listing under SigV4; the docs show it with a bearer key only |

`supports.models` is therefore **false** for `bedrock-chat` (support
matrix row flipped).  Closed 2026-09-04: under a short-term key
(`Authorization: Bearer`) the same `GET` answers the same 404
(`receipts/2026-09-04-bedrock-chat/probe-bearer-models.json`), so the
docs' listing claim (bedrock-openai-chat-completions.md:8) does not hold
in `us-east-1` under either scheme; the row stays false.

## Error envelopes (`errors/cases/bedrock-chat.json`)

| id | HTTP | wire code | mapped |
|---|---|---|---|
| `invalid_signature` | 401 | `invalid_api_key` "The security token included in the request is invalid" | `AuthError` |
| `model_not_found` | 400 | `validation_error` "The provided model identifier is invalid" | `InvalidRequestError` |
| `bad_param` | 400 | `validation_error` "'max_completion_tokens' must be non-negative" | `InvalidRequestError` |

Finding, stated: a 400 for an unknown model id maps to
`InvalidRequestError`, not `ModelNotFoundError`, because the envelope
says `validation_error` and the door also answers 404 `model_not_found`
for other id forms; the 404 form is not yet pinned (no case: the probe
bodies are receipts).

## Claude on the new doors is gated by AWS, not by us (blocks `bedrock-anthropic`, `aws-anthropic`)

Sequence, all receipts in the AWS CLI session 2026-09-03/04: the
Anthropic use-case form was submitted from the console (the CLI wants the
JSON base64-encoded inside the blob — recorded in the dossier); after
~15 minutes the legacy door answered — `Converse` with
`us.anthropic.claude-haiku-4-5-20251001-v1:0` → "ok".  Agreements were
created for `anthropic.claude-haiku-4-5-20251001-v1:0` and
`anthropic.claude-sonnet-5` (both `agreementAvailability AVAILABLE`,
pay-per-token, stated).  Still, every mantle-era id on the mantle door
and on this door answers 403 `permission_error` / `access_denied`
"<model> is not available for this account … For additional access
options, contact AWS Sales", and `Converse` with
`global.anthropic.claude-sonnet-5` answers the same.  The mantle door's
documented Haiku id `anthropic.claude-haiku-4-5` has no catalog entry
and no offer.  Conclusion: the 5-series / mantle models are gated per
account by AWS ("Amazon Bedrock sets access criteria for each Claude
model individually", anthropic-on-bedrock.md:15); this account does not
meet the criteria today.  What works: Claude Haiku 4.5 on the legacy
`bedrock-runtime` door (Converse — phase 2's dialect).

## Capture tooling changes (`research/providers/_capture.py`)

- `Capture(settings=…)`: host settings pinned into every case and error
  case; `aws_fixture()`: send with the chain's real credentials, pin the
  case re-signed with the fixed pair at the capture instant
  (`pinned_wire`); raw-body probes are re-signed (a swapped body
  invalidates a SigV4 signature — caught live as a 401 on the first
  run); `probe(headers=…)`; `models_probe()`.
- Harness: `host_fields(case)` forwarded on every op; a SigV4
  `authorization` value is never rewritten to the test key; `api-key`
  joins `AUTH_HEADERS`; `tools/scribe_goldens.py` forwards host fields.
- Shim: parse-only adapters take `settings`/`clock`.

## Reference changes (lm15-python)

- `compat.py`: preset `bedrock` (above).  `registry.py`: `bedrock-chat`
  binds it.  `access.py`: `BEDROCK_CHAT.supports.models = False`.
- `cloud/hosts.py` + `cloud/chains.py`: `resolve_settings(profile=…)`
  and `profile_settings()` — the AWS profile's `region` and the ADC
  file's project are the fallbacks after env, as AUTH-10 says; found
  missing by the doctor on this machine (`ca-central-1` in
  `~/.aws/config`).

## Bearer key (closed 2026-09-04; `changes/2026-09-04-bedrock-bearer.md`)

`cases/bedrock-chat/bearer_basic_text.json` (HTTP 200,
`openai.gpt-oss-20b-1:0`): the aws-chain's env rung
(`AWS_BEARER_TOKEN_BEDROCK` → `BearerToken`) travelling as
`Authorization: Bearer`.  The key was minted from the profile's IAM keys
by `research/providers/_aws_bearer.py` (the algorithm of
`aws-bedrock-token-generator` 1.1.0, pinned against it), never pasted or
printed.  The case pins the credential
(`{"kind":"bearer_token","value":"bedrock-api-key-FIXTURE"}`) and the
harness compares the header verbatim (PROTOCOL.md 2026-09-04).

## What is not yet evidenced

Claude on this door (account gate); `cache_control`; the 404
`model_not_found` envelope as a pinned case; other regions.
