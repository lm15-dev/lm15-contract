# Azure — fact sheet

Sources: `sources/manifest.json`, frozen 2026-09-03. Every cell cites
`file:line` in `sources/`. A blank cell is a finding. Re-check date:
2026-12-03.

## Doors

| Door | Base URL | Wire | Auth | Streaming | Model id form | Cite |
|---|---|---|---|---|---|---|
| Azure OpenAI v1 — Responses | `https://{resource}.openai.azure.com/openai/v1/` (also `https://{resource}.services.ai.azure.com/openai/v1/`); `POST …/responses` | OpenAI Responses, no `api-version` needed on v1 GA | `api-key: <key>` header **or** `Authorization: Bearer <Entra token>` | SSE | **deployment name**, not model name (`404` when it is not a deployment) | azure-openai-api-lifecycle.md:59, :90-106, :235-250, :256; azure-openai-managed-identity.md:246 |
| Azure OpenAI v1 — Chat Completions | same base, `POST …/chat/completions`; also serves non-OpenAI Foundry models (DeepSeek, Grok, MAI) | OpenAI Chat Completions | same | SSE | deployment name | azure-openai-api-lifecycle.md:74, :255-258; azure-foundry-openai-v1.md:86-88 |
| Claude in Microsoft Foundry | `https://{resource}.services.ai.azure.com/anthropic/v1/messages` | Messages API, first-party body | Docs say `api-key` or `x-api-key`; live on an `AIServices` resource: **only `x-api-key`** reaches deployment lookup; `api-key` is 401. Entra bearer also reaches lookup. | SSE (docs; successful stream quota-blocked) | `claude-opus-5` style deployment / model id | anthropic-on-foundry.md:106, :124-143, :176, :305-318; `receipts/2026-09-04-azure-anthropic/` |
| Control plane — list models in a region | `https://management.azure.com/subscriptions/{sub}/providers/Microsoft.CognitiveServices/locations/{region}/models?api-version=2023-05-01` | ARM | Bearer, scope `https://management.azure.com/.default`; needs a management role | — | — | azure-openai-managed-identity.md:213-236 |

Two hosting options for Claude in Foundry: "Hosted on Azure"
(Anthropic-operated on Azure infra, Global Standard or US Data Zone) and
"Hosted on Anthropic" (anthropic-on-foundry.md:8-17). Not supported
anywhere on Foundry: Admin, Advisor, Managed Agents, Compliance, Models
API, Message Batches, `fallbacks`, computer/browser toolsets
(anthropic-on-foundry.md:637-646). Additionally unsupported when hosted
on Azure — requests return `400` "by design": code execution, web
search/fetch, Agent Skills, programmatic tool calling, Files API
(anthropic-on-foundry.md:648-658).

Preview features on the v1 API opt in by header, not by api-version
(azure-openai-api-lifecycle.md:75-78).

## Token scope

Two scopes appear in the scraped docs:

- `https://ai.azure.com/.default` — v1 lifecycle page, managed-identity
  how-to, and Claude in Foundry (azure-openai-api-lifecycle.md:153, :195;
  azure-openai-managed-identity.md:135, :200; anthropic-on-foundry.md:340).
- `https://cognitiveservices.azure.com/.default` — the v1 OpenAPI
  reference's `OAuth2Auth` security scheme (azure-foundry-openai-v1.md:76, :84).

Both are recorded. Live cell: which one each host accepts today.

## Credential chain — `DefaultAzureCredential` (azure-identity)

Order from the published table (azure-identity-default-credential.md:85-98)
and the constructor (azure-identity-default-py.md:261-303):

| # | Credential | Reads | Needs | Cite |
|---|---|---|---|---|
| 1 | Environment | `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` + (`AZURE_CLIENT_SECRET` \| `AZURE_CLIENT_CERTIFICATE_PATH` [+ `AZURE_CLIENT_CERTIFICATE_PASSWORD`, `AZURE_CLIENT_SEND_CERTIFICATE_CHAIN`] \| `AZURE_USERNAME`+`AZURE_PASSWORD`); `AZURE_AUTHORITY_HOST` | HTTPS POST to `{authority}/{tenant}/oauth2/v2.0/token` | azure-identity-readme.md:182-194; azure-identity-environment-py.md:31-46 |
| 2 | Workload Identity | `AZURE_FEDERATED_TOKEN_FILE` (projected K8s token) + `AZURE_CLIENT_ID` + `AZURE_TENANT_ID` (+ `AZURE_AUTHORITY_HOST`) | HTTPS POST with `client_assertion` = file contents | azure-identity-workload-py.md:84-86; azure-aks-workload-identity.md:286 |
| 3 | Managed Identity | dispatch on env: `IDENTITY_ENDPOINT`+`IDENTITY_HEADER` (+`IDENTITY_SERVER_THUMBPRINT` → Service Fabric; else App Service), `IDENTITY_ENDPOINT`+`IMDS_ENDPOINT` → Azure Arc, `MSI_ENDPOINT`+`MSI_SECRET` → Azure ML, `MSI_ENDPOINT` alone → Cloud Shell, else IMDS `GET http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=…` with `Metadata: true`; user-assigned via `client_id` / `AZURE_CLIENT_ID` | plain HTTP GET | azure-identity-managed-identity-py.md:82-140; azure-msi-vm-token.md:72-95; azure-app-service-msi.md:468-479 |
| 4 | Shared Token Cache | Windows only, Visual Studio login | — | azure-identity-default-credential.md:92 |
| 5 | Visual Studio Code | needs `azure-identity-broker` | — | :93 |
| 6 | Azure CLI | subprocess `az account get-access-token --output json --resource <r> [--tenant <t>]`; JSON `accessToken`, `expires_on`/`expiresOn` | subprocess | azure-identity-azure-cli-py.md:35, :179-187, :209 |
| 7 | Azure PowerShell | subprocess `Connect-AzAccount` session | subprocess | :95 |
| 8 | Azure Developer CLI | subprocess `azd auth token` | subprocess | :96 |
| 9 | Interactive browser | **disabled by default** | — | :97 |
| 10 | Broker | OS account broker, needs extra package | — | :98 |

Continuation policy: developer credentials (4–10) are all tried even after
errors; a deployed credential (1–3) that can attempt and fails **stops
the chain** with an exception (azure-identity-readme.md:48-50).
`AZURE_TOKEN_CREDENTIALS=prod|dev|<CredentialName>` narrows the chain
(azure-identity-default-credential.md:167-200).

## Certificate assertion (client credentials, certificate)

Grant: `POST {authority}/{tenant}/oauth2/v2.0/token` with
`grant_type=client_credentials`, `scope=<resource>/.default`,
`client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`,
`client_assertion=<JWT>` — differs from the secret form only by replacing
`client_secret` (entra-client-credentials.md:151-168). Claims: `aud` =
the token endpoint URL, `iss` = `sub` = client id, `jti` unique, `nbf`,
`exp`, `iat` (entra-certificate-credentials.md:59-84).

Signing algorithm — two sources disagree:

- The Entra doc page: header `alg` "Should be **PS256**", `typ: JWT`,
  `x5t#S256` = base64url SHA-256 of the DER cert
  (entra-certificate-credentials.md:55-57, :73-75).
- The same doc family's grant-flow example assertion decodes to
  `{"alg":"RS256","x5t":"…"}` (entra-client-credentials.md:157).
- azure-identity: "The certificate must have an RSA private key, because
  this credential signs assertions using RS256" and sends the chain in
  `x5c` when asked (azure-identity-certificate-py.md:20, :37).

Decision candidate: RS256 + `x5t` (SHA-1 thumbprint), as the SDK does —
deterministic, hence pinnable. PS256 as a live cell.

Certificate formats: PEM or PKCS#12 with password
(azure-identity-readme.md:192-193). PKCS#12 parsing is not stdlib in
Python; PEM is the supported input (stated deviation candidate).

## Sovereign clouds

Authority hosts: global `https://login.microsoftonline.com`, US Government
`https://login.microsoftonline.us`, China (21Vianet)
`https://login.partner.microsoftonline.cn`; single-tenant replaces
`common` with the tenant id (entra-national-clouds.md:94-103). Set by
`AZURE_AUTHORITY_HOST` (azure-identity-readme.md:121-124).

## Errors the host raises

`401` when the resource has no custom subdomain (Entra tokens rejected);
`403`/`PermissionDenied` when no role on the resource; `404` when `model`
is not a deployment name; `DefaultAzureCredential failed to retrieve a
token` when not signed in (azure-openai-managed-identity.md:240-246).
Foundry: authentication, rate-limit and deployment error sections exist
(anthropic-on-foundry.md:726-750); live capture pins the envelopes.

## Env var names the Anthropic SDK reads on Foundry

`ANTHROPIC_FOUNDRY_API_KEY`, `ANTHROPIC_FOUNDRY_RESOURCE`,
`ANTHROPIC_FOUNDRY_BASE_URL` (mutually exclusive with resource)
(anthropic-on-foundry.md:180-182). For Azure OpenAI the docs use
`AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_AUTH_TOKEN`, and OpenAI's
`OPENAI_BASE_URL` (azure-openai-api-lifecycle.md:106, :237, :247).

## Blank cells (findings) — resolved live 2026-09-04 on the Azure OpenAI doors

Receipts: `receipts/2026-09-04-azure/`, `receipts/2026-09-04-azure-chat/`
(resource `lm15-oai-29d280ed6f8e`, kind `OpenAI`, eastus2, deployment
`gpt-4.1-mini`).  The Foundry (Anthropic) door is still blank: a fresh
subscription has 0 Claude quota in every region (`provision.sh` output).

- `GET /openai/v1/models` **answers 200 with the api-key** on
  `openai.azure.com`, despite the docs calling listing control-plane only.
  It returns the resource's whole catalog (207 entries: dall-e, whisper,
  gpt-35-…, gpt-4.1-…), each with `status`, `capabilities`,
  `lifecycle_status`, `deprecation`, `created_at` — not the deployments.
  Pinned as `cases/azure/models.json`, `cases/azure-chat/models.json`.
- **Both Entra scopes are accepted** on `openai.azure.com`:
  `https://ai.azure.com/.default` and
  `https://cognitiveservices.azure.com/.default` (200 each, Responses and
  Chat; `probe-entra-*.json`).
- **`x-api-key` is refused** on `openai.azure.com` (401 "invalid
  subscription key"; `probe-x-api-key-header.json`).  Only `api-key`.
- An `OpenAI`-kind resource has **no `{resource}.services.ai.azure.com`
  name at all** (DNS NXDOMAIN; `probe-services-host.json`).  That host
  belongs to `AIServices`-kind (Foundry) resources; the docs' "also" is
  true only for those.
- `max_output_tokens` has a **floor of 16** (400 `integer_below_min_value`,
  `probe-error-bad-param.json`); api.openai.com has no such floor.
- Error envelopes: bad key → 401 `{"error": {"code": "401", "message": …}}`
  (the Cognitive Services gateway shape, not OpenAI's); unknown deployment
  → 404 `{"error": {"type": "invalid_request_error", "code":
  "DeploymentNotFound", …}}`; rate limit → 429 `type: too_many_requests`,
  `code: rate_limit_exceeded`.
- Azure-only content-safety fields ride beside the OpenAI ones:
  `content_filters` on Responses; `content_filter_results` per choice and
  `prompt_filter_results` on Chat. A blocked prompt is HTTP 400 code
  `content_filter`; a blocked completion is HTTP 200 and canonical
  `finish_reason: content_filter` on both wires (cases pinned).
- `gpt-5-mini` accepts low/high reasoning on both wires; a hard high case
  reports hundreds of `reasoning_tokens`. A warm 4K-token prompt reports
  4,096 cached tokens on both wires.
- Files (`/files`) are live: Azure upload is 201 + `status: pending`;
  `/content` is 204 until processed, then exact bytes at 200. `user_data`
  files do not appear in Azure's list, though batch files do. Batches
  upload/submit/status/cancel/list work. Speech returns raw WAV.
- Realtime is live at `wss://{resource}.openai.azure.com/openai/v1/realtime`.
  API-key authentication uses `api-key`, not OpenAI's bearer header.
- Claude without quota: `x-api-key`, both Entra scopes, and service-
  principal secret/certificate all reach 404 `DeploymentNotFound`;
  `/models` is 404 `api_not_supported`. The only missing proof is a
  successful deployment's response/stream and model features.
- Certificate token refresh is live-proven without waiting: one router
  got 200, its cached token was forced expired, it exchanged a new RS256
  assertion with Entra, and got 200 again
  (`probe-certificate-forced-refresh.json`). A natural-expiry soak is an
  extra check, not a blocker.
