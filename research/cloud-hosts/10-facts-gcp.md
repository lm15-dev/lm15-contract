# Google Cloud — fact sheet

Sources: `sources/manifest.json`, frozen 2026-09-03. Every cell cites
`file:line` in `sources/`. A blank cell is a finding. Re-check date:
2026-12-03.

Naming: Google's pages now call the product "Agent Platform"
(anthropic-on-vertex.md:3-9; vertex-express-mode.md:28). The hostnames are
still `aiplatform.googleapis.com`. lm15 keeps the provider id `vertex`
because the wire names say so; the docs name is recorded here.

## Doors

| Door | URL | Wire | Auth | Streaming | Model id form | Cite |
|---|---|---|---|---|---|---|
| Gemini on Vertex, regional | `https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent` (`:streamGenerateContent`) | Gemini API body | `Authorization: Bearer <OAuth token>` | SSE with `?alt=sse` | `gemini-2.5-pro` style | vertex-locations.md:40 |
| Gemini on Vertex, global | `https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:generateContent` | same | same | same | same | vertex-locations.md:49 |
| Gemini on Vertex, multi-region (`us`, `eu`) | `https://aiplatform.{us\|eu}.rep.googleapis.com/v1/projects/{PROJECT}/locations/{us\|eu}/…` | same | same | same | same | vertex-locations.md:60-63, :91 |
| Express mode (API key) | `https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:streamGenerateContent?key={API_KEY}` — no project, no location | Gemini API body | API key in query | SSE | same | vertex-express-mode.md:84, :181 |
| Claude on Vertex | `https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/anthropic/models/{MODEL}:rawPredict` (`:streamRawPredict`); regional `https://{LOCATION}-aiplatform…` (Sonnet 4.6 and earlier only); multi-region `aiplatform.{us\|eu}.rep.googleapis.com` | Messages API body **without `model`**, with `"anthropic_version": "vertex-2023-10-16"` in the body | Bearer OAuth | SSE | `claude-opus-5`, or `claude-sonnet-4-5@20250929` (older ids carry `@date`) | anthropic-on-vertex.md:9-10, :122-126, :329-333, :483-489, :636-640, :118-135 |
| OpenAI-compatible endpoint | `https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/endpoints/openapi` (`/chat/completions`) | OpenAI Chat Completions | Bearer OAuth (`cloud-platform` scope) | SSE | `google/gemini-…`, partner ids | vertex-inference.md:714-718 |
| Publisher model listing | `publishers.models.list` REST resource (page scraped: vertex-list-models.md, 6450 lines, no single URL line extracted) | — | Bearer | — | — | blank: live cell |

Claude on Vertex — unsupported (raise, MAP-8): URL/Files sources,
server-side tools except web search, Agent Skills/MCP/programmatic tool
calling, Message Batches, Models API, `fallbacks`
(anthropic-on-vertex.md:358-365). Supported: prompt caching, thinking,
tool use, web search, citations, structured outputs (:348-356).

Endpoint tiers: global (no premium, pay-as-you-go only), multi-region
`us`/`eu` (10% premium), regional (10% premium, required for provisioned
throughput) (anthropic-on-vertex.md:373-409).

## Credential chain — ADC (google-auth)

`google.auth.default()` tries, in order (gcp-google-auth-default-py.md:706-714):

| # | Checker | Reads | Needs | Cite |
|---|---|---|---|---|
| 1 | explicit environ | `GOOGLE_APPLICATION_CREDENTIALS` → a JSON file whose `type` is one of `authorized_user`, `service_account`, `external_account`, `external_account_authorized_user`, `impersonated_service_account`, `gdch_service_account` | see per-type below | default-py:39-51, :259-287, :327-348; gcp-adc.md:25-45 |
| 2 | gcloud SDK ADC file | `$CLOUDSDK_CONFIG/application_default_credentials.json`, default `~/.config/gcloud/application_default_credentials.json` (`%APPDATA%\gcloud\…` on Windows); same `type` dispatch | file read | default-py:301-308; gcp-adc.md:54-62; environment-vars-py:41 |
| 3 | App Engine (legacy runtime) | `APPENGINE_RUNTIME` | — | default-py:364; environment-vars-py:91 |
| 4 | GCE metadata | `GET http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token` with `Metadata-Flavor: Google` → `{access_token, expires_in}`; host override `GCE_METADATA_HOST` (legacy `GCE_METADATA_ROOT`), IP `169.254.169.254`; skip with `NO_GCE_CHECK` | plain HTTP | default-py:391; compute-engine-py:40-51, :82; gcp-metadata-token.md:132-137; environment-vars-py:47-73 |

Per-type behaviour of the JSON file:

| `type` | Keys | Exchange | Signing | Cite |
|---|---|---|---|---|
| `authorized_user` | `refresh_token`, `client_id`, `client_secret` (+ `token_uri`, `quota_project_id`) | `POST https://oauth2.googleapis.com/token` `grant_type=refresh_token` | none | oauth2-credentials-py:51, :463; gcp-token-refresh.md:666-702 |
| `service_account` | `client_email`, `private_key`, `token_uri` (+ `private_key_id`) | JWT assertion → `POST https://oauth2.googleapis.com/token`, `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`; lifetime 3600 s | **RS256 (RSASSA-PKCS1-v1_5, SHA-256)** — "the only signing algorithm supported"; header `{"alg":"RS256","typ":"JWT"}` (+ `kid`); claims `iss`, `scope`, `aud=https://oauth2.googleapis.com/token`, `exp` ≤ 1 h after `iat` | service-account-py:86, :219-220, :246, :393-403; gcp-service-account-oauth.md:240-251, :263-278, :318-333 |
| `external_account` | `audience`, `subject_token_type`, `token_url` (default `https://sts.googleapis.com/v1/token`), `credential_source` (`file` \| `url` \| `executable` \| AWS `environment_id`/`region_url`/`regional_cred_verification_url` \| certificate), optional `service_account_impersonation_url` | STS token exchange `grantType=urn:ietf:params:oauth:grant-type:token-exchange`, `subjectToken`, `subjectTokenType`, `requestedTokenType=urn:ietf:params:oauth:token-type:access_token`, `scope`; then optional `iamcredentials …:generateAccessToken` | none (AWS source signs a GetCallerIdentity request with SigV4) | external-account-py:57, :160-187, :262, :672-684; identity-pool-py:355-356; gcp-sts-token.md:20-51; gcp-impersonation-generate-token.md:20-49 |
| `impersonated_service_account` | `source_credentials` (nested, any type), `service_account_impersonation_url`, `delegates` | `POST https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{email}:generateAccessToken` `{scope[], lifetime, delegates[]}` | none | default-py:283; impersonated-py; gcp-impersonation-generate-token.md:20-49 |

Scope for Vertex: `https://www.googleapis.com/auth/cloud-platform`
(vertex-inference.md:714).

Project and location: `GOOGLE_CLOUD_PROJECT` (legacy `GCLOUD_PROJECT`),
`GOOGLE_CLOUD_LOCATION` (environment-vars-py:18-25; vertex-locations.md:40).
The ADC file may carry `quota_project_id`; `GOOGLE_CLOUD_QUOTA_PROJECT`
overrides (environment-vars-py:32).

gcloud CLI rung (not in google-auth's chain, used by the Anthropic and
Google SDK helpers): `gcloud auth print-access-token`
(gcp-gcloud-print-access-token.md:11-13). `gcloud auth application-default
login` writes the ADC file (gcp-gcloud-adc-login.md).

## Signing — RS256 for service accounts

RSASSA-PKCS1-v1_5 with SHA-256 is deterministic: the harness can pin the
JWT and the token-exchange body byte for byte under a fixed clock and a
fixed test key. Python's standard library has no RSA; a ~150-line
stdlib signer (PKCS#8 DER parse, PKCS#1 v1.5 padding, `pow(m, d, n)`) is
the reference's plan (design decision, `30-model.md`).

## Errors the host raises

vertex-errors.md (1151 lines) is a general troubleshooting page; no
Vertex-specific inference error envelope was extracted. Live capture
pins: wrong location, model not enabled in Model Garden, expired token,
quota exceeded (`429`), `PERMISSION_DENIED`.

## Blank cells (findings)

- Exact `publishers.models.list` URL and response shape for Vertex: live
  cell (`GET …/publishers/google/models`, `publishers/anthropic/models`).
- Express-mode API key: whether `x-goog-api-key` header works as an
  alternative to `?key=` (only the query form is scraped,
  vertex-express-mode.md:84).
- Whether the Gemini-on-Vertex body accepts `cachedContent`, and the
  Vertex context-cache lifecycle endpoints (vertex-context-cache.md
  scraped, not yet read): a `caches` support cell.
- Batch prediction on Vertex uses a different resource
  (`batchPredictionJobs`, vertex-batch.md scraped, not read): `batches`
  support cell.
- `external_account_authorized_user` and `gdch_service_account` types:
  recorded as existing; not in scope for the first pass (stated).
