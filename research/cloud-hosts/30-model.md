# Cloud hosts — the abstract model and the mapping

Status: proposal for `changes/2026-09-03-cloud-hosts.md`. Every rule below
points at a fact-sheet cell (`10-facts-*.md`) or names itself as a design
decision with its trade-off.

## 1. One new word: host

A **host** is how a dialect reaches a backend that is not the dialect's
public API. It is the third use of the seam AUTH-10 already has
(`AccessPolicy.backend` + `backend_options`, used by `claude-code` and
`chatgpt-codex`). A host changes four things and nothing else:

1. **Where the request goes** — a URL template with named settings.
2. **How it is signed** — an auth scheme from a closed vocabulary.
3. **Small body/header rewrites** — from a closed vocabulary.
4. **How the stream is framed** — SSE or AWS event-stream.

The dialect (what the body means) does not change. The canonical types do
not change. A user who switches `anthropic:` to `vertex-anthropic:` sends
the same `Request` and reads the same `Response`.

Why not a class per cloud: three fat adapters would each re-implement SSE,
tool mapping, and error mapping for the same body, and every port would
copy that three times. Why not pure data: SigV4 and RS256 are code. So:
schemes are code (one per port, closed list); everything else is data.

## 2. Vocabularies (closed; new values are spec changes)

### 2.1 `auth_scheme` (extends `AuthHeader`)

| Value | Credential kind it consumes | Wire | Cite |
|---|---|---|---|
| `bearer` | `api_key` or `bearer_token` | `Authorization: Bearer …` | existing |
| `x-api-key` | `api_key` | `x-api-key: …` | existing; Claude on AWS / Foundry accept it (aws:216, foundry:176) |
| `api-key` | `api_key` | `api-key: …` | Azure OpenAI, Foundry (azure-openai-reference.md:87; foundry:176) |
| `query-key` | `api_key` | `?key=…` | Vertex express (vertex-express-mode.md:84) |
| `sigv4` | `aws_credentials` | `Authorization: AWS4-HMAC-SHA256 …`, `x-amz-date`, `x-amz-security-token` | aws-sigv4-create-signed-request.md |

A host lists the schemes it accepts, in preference order. The credential
kind picks the scheme: an `api_key` on a host that accepts `x-api-key` and
`sigv4` goes out as `x-api-key`; `aws_credentials` go out as `sigv4`.

### 2.2 `credential_policy` (extends AUTH-1)

| Value | Chain | Source of the order |
|---|---|---|
| `key`, `oauth`, `oauth-unless-explicit` | existing | spec/auth.md |
| `aws-chain` | § 3.1 | botocore `create_credential_resolver` (10-facts-aws.md) |
| `azure-chain` | § 3.2 | `DefaultAzureCredential` (10-facts-azure.md) |
| `gcp-chain` | § 3.3 | `google.auth.default` (10-facts-gcp.md) |

### 2.3 Credential kinds (extends AUTH-2)

A credential is a small closed sum, not a string:

```
ApiKey        { value }
BearerToken   { value, expires_at? }
AwsCredentials{ access_key_id, secret_access_key, session_token?, expires_at? }
```

A `CredentialProvider` returns one of these. An explicit `api_keys` entry
may be a string (→ `ApiKey`), one of these values, or a provider. Ports:
Python/TS/Julia a tagged value, Go/Rust an interface/enum. Serde: `kind`
discriminator, canonical keys as above.

### 2.4 Rung kinds (the code every port carries, once)

| Kind | Mechanism | Used by |
|---|---|---|
| `env` | read named variables | all |
| `ini-profile` | parse `~/.aws/{credentials,config}` with profile selection | AWS |
| `json-file` | read a JSON credential file and dispatch on `type` | GCP |
| `subprocess` | run a CLI, parse stdout JSON/text | AWS `credential_process`; Azure `az`, `azd`, `pwsh`; GCP `gcloud` |
| `http-metadata` | unauthenticated local HTTP with a marker header | AWS IMDSv2 + container, Azure MSI (5 flavours), GCP metadata |
| `http-token-exchange` | HTTPS POST form/JSON → `{access_token, expires}` | Azure secret/cert/workload, GCP `authorized_user` refresh, STS exchange, impersonation, AWS SSO/login |
| `sigv4-sts` | signed STS call → temporary keys | AWS assume-role |
| `unsigned-sts` | STS `AssumeRoleWithWebIdentity` POST | AWS web identity |
| `jwt-rs256` | build and sign a JWT (RSASSA-PKCS1-v1_5/SHA-256) | GCP service account, Azure certificate |
| `file-cache` | read a tool's cached token JSON (AUTH-8 borrowed file) | AWS SSO, AWS login |

Ten kinds. Every rung in the three chains is one of these with parameters.

### 2.5 Host rewrites

| Rewrite | Values | Used by | Cite |
|---|---|---|---|
| `model_in` | `body` (default) \| `path` | Vertex Claude, Bedrock InvokeModel/Converse | anthropic-on-vertex.md:9; bedrock-invoke-model-stream.md:13 |
| `anthropic_version_in` | `header` (default) \| `body:<value>` | Vertex `vertex-2023-10-16`; Bedrock legacy `bedrock-2023-05-31` | anthropic-on-vertex.md:10; bedrock-anthropic-messages.md:60 |
| `stream_framing` | `sse` (default) \| `aws-event-stream` | Bedrock InvokeModel / Converse | aws-eventstream-smithy.md |
| `required_headers` | list of `name: {setting}` | `anthropic-workspace-id: {workspace}` on Claude Platform on AWS | anthropic-platform-on-aws.md:244-262 |

### 2.6 Host settings (constructor options; env fallbacks in order)

| Setting | Env, in order | Required by | Default |
|---|---|---|---|
| `region` | `AWS_REGION`, `AWS_DEFAULT_REGION`, profile `region` | every AWS door | **none — raise** (anthropic-platform-on-aws.md:271) |
| `workspace` | `ANTHROPIC_AWS_WORKSPACE_ID` | `aws-anthropic` | none — raise |
| `project` | `GOOGLE_CLOUD_PROJECT`, `GCLOUD_PROJECT`, ADC file `quota_project_id`/`project_id` | Vertex OAuth doors | none — raise |
| `location` | `GOOGLE_CLOUD_LOCATION` | Vertex | `global` (design decision: the docs recommend it; trade-off: a user who wanted `us-central1` for residency and forgot the var gets global routing. The doctor prints the location.) |
| `resource` / `endpoint` | `AZURE_OPENAI_ENDPOINT` (full URL) or `AZURE_OPENAI_RESOURCE`; `ANTHROPIC_FOUNDRY_RESOURCE`, `ANTHROPIC_FOUNDRY_BASE_URL` | Azure doors | none — raise |
| `authority_host` | `AZURE_AUTHORITY_HOST` | Azure Entra rungs | `https://login.microsoftonline.com` |
| `scope` | — | Azure Entra rungs | `https://ai.azure.com/.default` (live cell may move it) |
| `base_url` | existing | all | the host template |

Settings live in `backend_options` (AUTH-10). They are never in the model
string. `Request.model` stays `provider:model`.

## 3. The chains (order is data; each rung names a kind and its parameters)

Rung 0 for every chain: explicit `api_keys` entry (any credential kind or
provider). Consistent with all three SDKs' "constructor arguments first".

### 3.1 `aws-chain` (botocore order, 10-facts-aws.md)

```
0  api_keys                        (explicit)
1  env:ANTHROPIC_AWS_API_KEY        (aws-anthropic only)            → ApiKey
1  env:AWS_BEARER_TOKEN_BEDROCK     (bedrock* only)                 → BearerToken
2  env:AWS_ACCESS_KEY_ID[+SECRET,+SESSION_TOKEN]                    → AwsCredentials
3  profile:assume-role  (role_arn + source_profile|credential_source) → sigv4-sts
4  web-identity  (AWS_WEB_IDENTITY_TOKEN_FILE+AWS_ROLE_ARN | profile) → unsigned-sts
5  sso  (profile sso_session/sso_start_url; ~/.aws/sso/cache/<sha1>.json; CreateToken; GetRoleCredentials)
6  shared-credentials-file  (~/.aws/credentials [profile])
7  login  (profile login_session; ~/.aws/login/cache)
8  credential_process  (profile)                                     → subprocess
9  config-file  (~/.aws/config [profile] static keys)
10 container  (AWS_CONTAINER_CREDENTIALS_RELATIVE_URI|FULL_URI, AUTHORIZATION_TOKEN[_FILE])
11 imds  (IMDSv2 token PUT, then role creds; AWS_EC2_METADATA_DISABLED)
```

Rung 1 placement follows the Anthropic AWS client (`ANTHROPIC_AWS_API_KEY`
before the default chain, anthropic-platform-on-aws.md:266-271); botocore
has no bearer rung, so `AWS_BEARER_TOKEN_BEDROCK` at the same position is
a design decision (stated). Boto2 legacy files (rung 9 in botocore) are
dropped: stated deviation, they predate 2016 tooling.

### 3.2 `azure-chain` (DefaultAzureCredential order, 10-facts-azure.md)

```
0  api_keys                                              (explicit)
1  env:AZURE_OPENAI_API_KEY | ANTHROPIC_FOUNDRY_API_KEY  (per door)   → ApiKey
2  environment  (AZURE_TENANT_ID+AZURE_CLIENT_ID+ AZURE_CLIENT_SECRET | AZURE_CLIENT_CERTIFICATE_PATH[+PASSWORD,+SEND_CERTIFICATE_CHAIN]; AZURE_AUTHORITY_HOST)
3  workload-identity  (AZURE_FEDERATED_TOKEN_FILE + tenant + client)
4  managed-identity   (IDENTITY_ENDPOINT/IDENTITY_HEADER/IDENTITY_SERVER_THUMBPRINT/IMDS_ENDPOINT/MSI_ENDPOINT/MSI_SECRET dispatch; else IMDS 169.254.169.254)
5  az   (`az account get-access-token --output json --scope <scope> [--tenant]`)
6  pwsh (`Get-AzAccessToken`)
7  azd  (`azd auth token --output json --scope <scope>`)
```

Dropped, stated: Shared Token Cache (Windows/Visual Studio), VS Code
(needs broker package), Interactive browser (off by default), Broker
(extra package). `AZURE_TOKEN_CREDENTIALS` narrowing is honoured.
Continuation policy copied: rungs 2–4 that can attempt and fail **stop**
the chain with `AuthError`; rungs 5–7 are tried through errors
(azure-identity-readme.md:48-50). `AZURE_USERNAME`+`AZURE_PASSWORD`
(ROPC) is dropped: stated, Microsoft discourages it and it is interactive
in MFA tenants.

### 3.3 `gcp-chain` (google.auth.default order, 10-facts-gcp.md)

```
0  api_keys                                   (explicit)
1  env:GOOGLE_API_KEY | VERTEX_API_KEY        (vertex-express only)   → ApiKey
2  GOOGLE_APPLICATION_CREDENTIALS → json-file dispatch on type
3  $CLOUDSDK_CONFIG|~/.config/gcloud/application_default_credentials.json → same dispatch
4  metadata  (metadata.google.internal, Metadata-Flavor: Google; GCE_METADATA_HOST; NO_GCE_CHECK)
5  gcloud   (`gcloud auth print-access-token`)   — lm15 addition, last, stated
```

`type` dispatch: `authorized_user` → refresh; `service_account` →
jwt-rs256 + exchange; `external_account` → subject token (file/url/
executable/aws) → STS exchange → optional impersonation;
`impersonated_service_account` → nested source → generateAccessToken.
`external_account_authorized_user` and `gdch_service_account`: raise
`NotConfiguredError` naming the type (stated gap, first pass).
App Engine legacy runtime rung: dropped, stated.

## 4. Registry entries (one per wire behaviour, `deepseek`/`deepseek-anthropic` rule)

| id | dialect | host template | schemes (pref. order) | policy | stream | notes / refusals |
|---|---|---|---|---|---|---|
| `aws-anthropic` | anthropic | `https://aws-external-anthropic.{region}.api.aws` | `sigv4`(service `aws-external-anthropic`), `x-api-key` | aws-chain | sse | header `anthropic-workspace-id`; betas pass; no OAuth; batches/files: live cell (platform says "full Claude API") |
| `bedrock-anthropic` | anthropic | `https://bedrock-mantle.{region}.api.aws/anthropic` | `sigv4`(`bedrock-mantle`), `x-api-key` | aws-chain | sse | raise: structured outputs, URL/Files sources, server tools, batches, models, `anthropic-beta` |
| `bedrock-chat` | openai-chat | `https://bedrock-runtime.{region}.amazonaws.com/openai/v1` | `sigv4`(`bedrock`), `bearer` | aws-chain | sse | models via `/models`; compat preset `bedrock` (live) |
| `bedrock` | **converse** (new dialect) | `https://bedrock-runtime.{region}.amazonaws.com` | `sigv4`(`bedrock`), `bearer` | aws-chain | aws-event-stream | second phase; `ListFoundationModels` on `bedrock.{region}` |
| `azure` | openai-responses | `https://{resource}.openai.azure.com/openai/v1` | `api-key`, `bearer` | azure-chain | sse | model = deployment name; models: control plane only (raise `UnsupportedFeatureError` with the ARM hint) |
| `azure-chat` | openai-chat | same | same | azure-chain | sse | also non-OpenAI Foundry models |
| `azure-anthropic` | anthropic | `https://{resource}.services.ai.azure.com/anthropic` | `api-key`, `x-api-key`, `bearer` | azure-chain | sse | raise: batches, models, `fallbacks`; hosted-on-Azure extra 400s pass through as the server's own error |
| `vertex` | gemini | `https://{location_host}/v1/projects/{project}/locations/{location}/publishers/google/models/{model}` | `bearer` | gcp-chain | sse (`?alt=sse`) | `location_host` = `aiplatform.googleapis.com` (global), `{location}-aiplatform…` (regional), `aiplatform.{us\|eu}.rep…` (multi-region) |
| `vertex-express` | gemini | `https://aiplatform.googleapis.com/v1/publishers/google/models/{model}` | `query-key` | key (`GOOGLE_API_KEY`) | sse | no project/location |
| `vertex-anthropic` | anthropic | `…/publishers/anthropic/models/{model}:rawPredict` / `:streamRawPredict` | `bearer` | gcp-chain | sse | `model_in: path`, `anthropic_version_in: body:vertex-2023-10-16`; raise: batches, models, Files sources, code exec |
| `vertex-chat` | openai-chat | `…/endpoints/openapi` | `bearer` | gcp-chain | sse | third phase |

Every entry gets a support-matrix row. `models: false` is the honest row
where the door has no listing (Azure OpenAI data plane, mantle Messages,
Vertex Claude).

## 5. Harness protocol additions

1. `credential` object (replaces `api_key` for hosts; `api_key` stays as
   shorthand for `{"kind":"api_key","value":…}`), plus `now` (RFC 3339)
   and `settings` (`region`, `project`, …). Fixed keys: AWS doc example
   pair `AKIAIOSFODNN7EXAMPLE`/`wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
   (aws-sdkref-env-vars.md); a committed 2048-bit **test-only** RSA key for
   GCP/Azure, generated for this corpus, never used anywhere else.
2. `--direction request` compares `Authorization`, `x-amz-date`,
   `x-amz-security-token` exactly — SigV4 is deterministic under a fixed
   clock.
3. New `--direction token`: input `credential` + `now` + host → expected
   token-exchange request (URL, headers, form/JSON body incl. the exact
   JWT). RS256 is deterministic, so the JWT is pinned byte for byte. A
   second op feeds the token response and expects the resulting
   `BearerToken` (value, expiry).
4. `explain_auth` grows: `files: {path: content}` materialized under a
   sandbox HOME (ini profiles, SSO cache, ADC file); a new step state
   **`unprobed`** for network rungs (IMDS, MSI, metadata): AUTH-7 does no
   network, so the doctor reports them as unprobed unless an env var
   proves them absent (`AWS_EC2_METADATA_DISABLED`, `NO_GCE_CHECK`) or
   present (`IDENTITY_ENDPOINT`, container URIs).
5. `--direction stream` fixtures gain `framing: "aws-event-stream"` with a
   base64 body (phase 2, `bedrock`).
6. `tools/check_secrecy.py`: patterns for `AKIA[0-9A-Z]{16}`, 40-char AWS
   secrets, `-----BEGIN (RSA |)PRIVATE KEY-----`, Azure 32/84-char keys,
   `ya29.` Google tokens, `eyJ` JWTs outside the fixed-key fixtures.

## 6. Mapping: every canonical field × every door = native | extension | raise

The body mapping is the dialect's and is already pinned. What a host adds
is a per-door refusal list (MAP-8) carried as compat preset fields:

| Field / feature | aws-anthropic | bedrock-anthropic | azure-anthropic | vertex-anthropic |
|---|---|---|---|---|
| `anthropic-beta` header | native | **raise** | live cell | live cell |
| structured outputs | native | **raise** | live cell | native |
| URL image/document sources | native | **raise** | live cell | **raise** |
| Files API / file sources | native | **raise** | raise when hosted on Azure | **raise** |
| server tools (web search) | native | **raise** | raise when hosted on Azure | web search native, others raise |
| batches surface | live cell | **raise** | **raise** | **raise** |
| models surface | live cell | **raise** | **raise** | **raise** |
| `fallbacks` | live cell | **raise** | **raise** | **raise** |
| `inference_geo` (AWS only) | extension door | — | — | — |
| `model` placement | body | body | body | path |
| `anthropic_version` | header | header | header | body |

For the OpenAI-wire doors (`azure`, `azure-chat`, `bedrock-chat`,
`vertex-chat`) the compat preset mechanism already exists; each gets a
preset populated from live cells.

## 7. Order of work (revised by the facts)

The scrape moved SSE-based Messages doors to the front and pushed the
binary decoder to the end. Nothing in phase 1 needs the event-stream
decoder or a new dialect.

1. Contract: this design → `changes/` entry; vocabularies; protocol;
   secrecy patterns; test RSA key. **You ratify.**
2. Reference: credential sum type, ten rung kinds, three chains, doctor
   states, `auth_scheme`, host rewrites. Harness `token` direction green
   on fixed vectors (no accounts needed for this step).
3. `azure`, `azure-chat`, `azure-anthropic` — live captures.
4. `aws-anthropic`, `bedrock-anthropic`, `bedrock-chat` — live captures
   (SigV4 proven on SSE doors).
5. `vertex`, `vertex-anthropic`, `vertex-express` — live captures.
6. Phase 2: `bedrock` Converse (new dialect + event-stream decoder).
7. Phase 3: `vertex-chat`; Azure `services.ai.azure.com` non-OpenAI
   models; Bedrock FIPS/GovCloud hosts.
8. Then the Go port, which implements ten rung kinds and five schemes
   once.

## 8. Trade-offs, stated

- **Credential becomes a sum type.** AUTH-2's "zero-arg callable returns
  a string" is widened. Every port's `CredentialProvider` signature
  changes before any port ships 1.0. Cheaper now than after.
- **Chains follow each cloud's SDK order, not AUTH-1's generic order.**
  A machine configured for boto3 gets boto3's identity. AUTH-1 gains
  three named chains; the doctor makes the winner visible.
- **Dropped rungs** (boto2 files, Windows shared cache, VS Code, browser,
  broker, ROPC, App Engine legacy): each named in the spec with the
  reason. A user on those paths gets `NotConfiguredError` with the hint.
- **RS256 in pure Python.** ~150 lines of stdlib crypto in the reference:
  DER parse, PKCS#1 v1.5 pad, `pow`. Not constant-time; the key is the
  user's own, signing a one-hour token. Tested against RFC 8017 vectors
  and a Google-issued token. PS256 for Azure is a live cell; the SDK
  itself uses RS256.
- **PKCS#12 certificates are not parsed** (needs a PKCS#12/ASN.1 + RC2/3DES
  stack). PEM only. Stated deviation; the hint names `openssl pkcs12`.
- **`location` defaults to `global` on Vertex.** Availability first;
  residency users set the variable. The doctor prints it.
- **`vertex-express` is its own entry.** One provider string = one wire
  behaviour. The router hint for `vertex:` with only an API key names it.
- **Network rungs are `unprobed` in the doctor.** Honest, and keeps AUTH-7
  offline. Real resolution probes them with the SDKs' timeouts.
- **Region has no default anywhere.** Same as the Anthropic and AWS
  clients; a wrong-region default is a residency bug.
- **Phase 1 leaves out Converse.** Until phase 2, `bedrock:` names
  nothing; `bedrock-anthropic:` and `bedrock-chat:` carry Claude and the
  OpenAI-wire models. Nova/Llama/Mistral via Converse wait.
