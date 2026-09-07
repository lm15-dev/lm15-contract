# 2026-09-04 — Azure OpenAI v1 over the Responses wire (`azure`), live-verified

Status: RATIFIED 2026-09-06 (wire facts: cases, bodies, errors, receipts). Goldens: see changes/2026-09-06-ratification.md.
Second cloud door through the
cloud-hosts pathway (`changes/2026-09-03-cloud-hosts.md`); the sibling
Chat Completions door is `changes/2026-09-04-azure-chat-live.md`.
Dossier: `research/providers/azure/README.md`.

## What this proves

The Azure OpenAI path end to end against a real resource: the lab
(`research/cloud-hosts/azure/provision.sh`) created `lm15-oai-29d280ed6f8e`
(kind `OpenAI`, S0, eastus2) with a `gpt-4.1-mini` GlobalStandard
deployment; the host rendered
`https://lm15-oai-29d280ed6f8e.openai.azure.com/openai/v1`; the `api-key`
header was accepted on every case; an Entra bearer token from `az` was
accepted on **both** documented scopes; and the lab's service principal
was accepted through lm15's own `azure-chain` — the **secret** rung and
the **certificate** rung, the latter signed by the standard-library RS256
signer (`probe-entra-sp-secret.json`, `probe-entra-sp-certificate.json`,
200 each).  That is the first live acceptance of an lm15-built client
assertion by Entra.  Nothing was pasted: the capture
read `~/.config/lm15/azure-lab.env` (mode 600, outside every repo).

Trade-off, stated: the deployment is `gpt-4.1-mini`, not the planned
`gpt-4.1-nano` — a fresh subscription has **0** tokens-per-minute quota
for nano and 200K for mini.  Same API surface, same version date
(`2025-04-14`), about 4× the price per token; the campaign cost cents.

## Cases (`cases/azure/`, bodies verbatim)

Every case pins `settings: {resource}`; the harness renders the URL from
it. Most use deployment `gpt-4.1-mini`; named surfaces use the deployment
shown below.

| case | HTTP | what it pins |
|---|---|---|
| `azure.basic_text` | 200 | `api-key` header, no `api-version`, `model` = deployment name; Azure adds `content_filters` to the envelope (passthrough) |
| `azure.streaming` | 200 | `response.*` SSE vocabulary as served by Azure; usage on `response.completed` |
| `azure.tools` | 200 | `function_call` output item, `call_…` ids |
| `azure.streaming_tool_call` | 200 | streamed `function_call_arguments.delta` |
| `azure.multi_turn_tool_result` | 200 | live turn-1 replayed with `function_call_output` |
| `azure.tool_choice_required` | 200 | forced call honoured (`get_weather`) |
| `azure.response_format_json_schema` | 200 | strict `text.format` honoured: `{"city":"Paris","country":"France"}` |
| `azure.system_prompt` | 200 | `instructions` |
| `azure.user_id` | 200 | `Config.user_id` → `safety_identifier`, accepted |
| `azure.models` | 200 | `GET /openai/v1/models` (below) |
| `azure.reasoning_low` | 200 | `gpt-5-mini`, effort low accepted; a trivial task honestly uses zero hidden tokens |
| `azure.reasoning_high` | 200 | effort high; nonzero `reasoning_tokens` (hundreds) |
| `azure.prompt_cache_key` | 200 | warm 4K-token prefix: `cache_read_tokens: 4096` |
| `azure.content_filter_completion` | 200 | Responses `status: incomplete`; completion blocked; canonical `finish_reason: content_filter` |
| `azure.files` | 201/200 | upload pending → wait → processed; get/download/delete; Azure list omits `user_data` but lists batch files |
| `azure.batch` | 201/200 | GlobalBatch JSONL upload, submit, status, cancel and list; a pre-capture job entered `in_progress` |
| `azure.speech_gen` | 200 | `gpt-4o-mini-tts`; raw WAV parsed to `AudioPart` |
| `azure.live_text` | WebSocket | `gpt-realtime-mini`; `api-key` upgrade, text deltas, `response.done` usage |

No refusals: every OpenAI cell the Responses dialect sends is honoured
on this door. Goldens drafted (`goldens/azure/`, scribe-draft, 18). Sync
and async complete/stream both ran live. The actual `az` rung also ran
through `azure-chain` after API-key and service-principal variables were
removed (200).

## Blank cells resolved (`research/cloud-hosts/10-facts-azure.md`)

- **`/openai/v1/models` answers 200 with the api-key.**  The docs call
  listing control-plane only; the data plane lists the resource's whole
  catalog (207 entries: dall-e, whisper, gpt-35-…, gpt-4.1-…) with
  `status`, `capabilities`, `lifecycle_status`, `deprecation` — not the
  deployments.  `supports.models` flips to **true**; support-matrix row
  and `lm15.access.AZURE` updated.  Stated limit: the listing does not
  tell a caller which strings are valid `model` values on this resource
  (those are deployments); it is a catalog, and `ModelInfo.provider_data`
  carries the Azure fields verbatim.
- **Both Entra scopes accepted**: `https://ai.azure.com/.default` and
  `https://cognitiveservices.azure.com/.default` (200 each,
  `receipts/2026-09-04-azure/probe-entra-*.json`).  The `azure-chain`
  default scope stays `ai.azure.com`.
- **`x-api-key` refused** (401 "invalid subscription key",
  `probe-x-api-key-header.json`).  `auth_scheme` stays `api-key`.
- **No `services.ai.azure.com` name for an `OpenAI`-kind resource**
  (DNS NXDOMAIN, `probe-services-host.json`).  The docs' "also
  `{resource}.services.ai.azure.com/openai/v1`" is true for
  `AIServices`-kind (Foundry) resources only.  The `azure` door keeps
  `openai.azure.com`.
- `max_output_tokens` floor is 16 (400 `integer_below_min_value`);
  api.openai.com has no floor.  Capture probes now send 16.

## Error envelopes (`errors/cases/azure.json`)

| id | HTTP | wire | mapped |
|---|---|---|---|
| `unauthenticated` | 401 | `{"error": {"code": "401", "message": "Access denied due to invalid subscription key…"}}` — the Cognitive Services gateway shape, not OpenAI's | `AuthError` |
| `deployment_not_found` | 404 | `type: invalid_request_error`, `code: DeploymentNotFound` | `UnsupportedModelError` (below) |
| `bad_param` | 400 | `code: integer_below_min_value`, `param: max_output_tokens` | `InvalidRequestError` |
| `content_filter` | 400 | prompt blocked, `code: content_filter`, `param: prompt` | `InvalidRequestError` |

Reference change: `DeploymentNotFound` joins the OpenAI dialects'
model-error codes.  On Azure the model string *is* the deployment, so
an unknown deployment is an unknown model; the message ("The API
deployment for this resource does not exist") lacks the word "model",
so the 404 heuristic missed it and the first draft said
`InvalidRequestError`.

## Lab and tooling

- `provision.sh`: fixed a self-recursion in the `az` wrapper (the
  function shadowed the command and bash died silently); the name
  suffix is now saved before anything is created (the first run left an
  orphan resource, deleted); Claude deployments go through `az rest`
  with the Anthropic `modelProviderData` form (see the
  `azure-anthropic` gap below); Claude quota is checked and named.
- `research/providers/azure/capture.py`: `services-host` probe records
  a connection failure as a finding instead of crashing; `models` is a
  case, not a receipt; `entra-sp-{secret,certificate}` probes resolve
  the principal through `lm15.cloud.chains.resolve` with an env that
  holds only the principal's variables and an empty `PATH` (so no `az`
  rung can win).  In receipts the bearer is shown as the door's key
  placeholder (`Bearer $AZURE_OPENAI_API_KEY`): the redactor has one
  placeholder per door, not per credential kind.
- `_capture.py`: model, file, batch and speech captures carry host
  `settings`; file uploads accept all 2xx statuses and wait for Azure's
  `pending` state before download.
- Harness: host settings now reach files, batch, generation and live
  directions, not only complete/models.
- `OpenAILM._live_headers`: uses the access policy. The old hard-coded
  bearer header made Azure Realtime API-key sessions impossible.

## Exact pending proofs and unblock runbook

1. **Image generation:** `gpt-image-1-mini` GlobalStandard "Requests Per
   Minute - GPT Image 1 Mini Generation" quota is 0 in eastus2; the
   quota request is submitted. After approval, rerun
   `provision.sh` (the deployment row is already present), then run
   `python3 research/providers/azure/capture.py --only image --force`.
   Review the pixel/body case, flip `AZURE.supports.images` and the
   support-matrix cell, and rerun generation + all harness directions.
2. **Azure Claude:** see
   `changes/2026-09-04-azure-anthropic-partial.md`. Microsoft denied the
   eastus2 request because that region had no capacity. No successful
   inference can be proven until Azure grants quota in some region.
Token refresh is not pending: `probe-certificate-forced-refresh.json`
pins the same long-lived router receiving 200, having its cached
certificate token forced expired, exchanging a new Entra token, and
receiving 200 again (expiry moved from 15:52:45Z to 15:52:47Z; token
values were never recorded). A natural one-hour soak is still running as
an extra check, not a release blocker.

Not pending: Sora/video was deliberately excluded by user decision.
Embeddings answered 200 on `/openai/v1`; transcription answered 200 on
Azure's deployment-scoped `?api-version=2025-04-01-preview` route while
the v1 route returned 404 (`probe-out-of-scope-embedding-transcription.json`).
lm15 has no canonical embedding/transcription surfaces; they are outside
this API, not partial Azure implementations.
