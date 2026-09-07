# 2026-09-03 — Cloud hosts: AWS, Azure, Google Cloud as doors to existing dialects

Status: RATIFIED 2026-09-03 (design; wire rows stay documentation-evidenced until captured).  Design pass per
`playbooks/design-pass.md`; artifacts under `research/cloud-hosts/`
(frame, 148 frozen sources with manifest, three fact sheets, model,
attack pass, experiment matrix).  **No live receipt exists yet**: every
wire row below is declared from provider documentation and library
source (AUTHORITY.md precedence 2) and is marked so.  Step 5 of the pass
(`20-experiments.py`) runs when accounts exist.

## Why

Enterprise users reach models through the cloud their company already
secured.  They expect the identity the cloud's own SDK would pick on the
same machine, the region they configured, and the same model behaviour
as the public API.  Today lm15 has no door to any of the three clouds.

The scrape corrected the plan we had from memory (`research/cloud-hosts/
10-facts-*.md`):

- AWS has **three** Claude doors, not one: Claude Platform on AWS
  (`aws-external-anthropic.{region}.api.aws`, Anthropic-operated, full
  Claude API, SigV4 service `aws-external-anthropic`, `anthropic-workspace-id`
  header), Claude in Amazon Bedrock ("mantle", `bedrock-mantle.{region}.api.aws/anthropic/v1/messages`,
  SigV4 service `bedrock-mantle`, **plain SSE**), and the legacy
  `bedrock-runtime` InvokeModel/Converse doors with binary event-stream
  framing.  Bedrock also serves OpenAI Chat Completions at
  `bedrock-runtime…/openai/v1` with SigV4 or `AWS_BEARER_TOKEN_BEDROCK`.
- Azure's v1 API needs no `api-version`; the token scope in current docs
  is `https://ai.azure.com/.default` (the OpenAPI reference still says
  `cognitiveservices`); Claude is on Foundry at
  `{resource}.services.ai.azure.com/anthropic/v1/messages`.
- Google's certificate/service-account signing is RS256 (deterministic);
  Entra's doc says "should be PS256" while azure-identity itself signs
  RS256.  Google's product is now named "Agent Platform"; hostnames are
  unchanged.
- Vertex Claude puts `model` in the path and `anthropic_version` in the
  body (`vertex-2023-10-16`).

Nothing in phase 1 needs the binary decoder or a new dialect.

## The rule: a host is the third use of the `backend` seam (AUTH-10)

A host changes where the request goes, how it is signed, a closed set of
body/header rewrites, and the stream framing.  The dialect and the
canonical types do not change.  Full model: `research/cloud-hosts/30-model.md`.

### Spec amendments (spec/auth.md), each with its rule text to be written on ratification

- **AUTH-1** gains three credential policies: `aws-chain`, `azure-chain`,
  `gcp-chain`.  Each is the cloud SDK's default order, pinned from the
  resolver source (botocore `create_credential_resolver`,
  `DefaultAzureCredential`, `google.auth.default`), with an explicit
  `api_keys` entry as rung 0.  Dropped rungs are named with reasons
  (boto2 files; Windows shared cache, VS Code, browser, broker, ROPC;
  App Engine legacy).  Azure's continuation policy is copied: a
  deployed-credential rung that can attempt and fails **stops** the chain.
- **AUTH-2**: a credential is a closed sum — `ApiKey`, `BearerToken`,
  `AwsCredentials` — not a string.  Providers return one of these.
- **AUTH-3**: token-cache key = provider id + hash of identity-selecting
  settings (profile / tenant+client / project+source), so two identities
  on one provider never share a cache (attack pass L2).
- **AUTH-5**: JWT assertions, STS/token-exchange bodies, and IMDS/MSI
  responses are secret material.
- **AUTH-7**: new step state `unprobed` for network rungs (IMDS, MSI,
  metadata); the doctor stays offline.  An env var may prove a network
  rung absent (`AWS_EC2_METADATA_DISABLED`, `NO_GCE_CHECK`) or present
  (`IDENTITY_ENDPOINT`, container URIs).
- **AUTH-8**: borrowed files — `~/.aws/credentials`, `~/.aws/config`,
  `~/.aws/sso/cache/*.json`, `~/.aws/login/cache/*.json`,
  `$CLOUDSDK_CONFIG|~/.config/gcloud/application_default_credentials.json`.
  Foreign formats, revalidated, never cleaned.
- **AUTH-10**: `auth_header` becomes `auth_scheme`, vocabulary
  `bearer | x-api-key | api-key | query-key | sigv4`; a policy lists the
  schemes it accepts in preference order; the credential kind selects
  one.  Host rewrites: `model_in`, `anthropic_version_in`,
  `stream_framing`, `required_headers`.  Host settings (`region`,
  `workspace`, `project`, `location`, `resource`, `authority_host`,
  `scope`) live in `backend_options` with their env fallbacks in order.
  `region` and `resource` have **no default**; `location` defaults to
  `global`.
- **AUTH-11 (new) — Rung kinds**: the ten mechanisms every port carries
  once (`env`, `ini-profile`, `json-file`, `subprocess`, `http-metadata`,
  `http-token-exchange`, `sigv4-sts`, `unsigned-sts`, `jwt-rs256`,
  `file-cache`); a chain is data over these.  Container-credential URLs
  are validated against botocore's allow-list (`169.254.170.2`,
  `169.254.170.23`, `fd00:ec2::23`, `localhost`, any loopback, or
  `https`).

### Vocabularies (spec/vocabularies.md)

`AuthScheme`, `CredentialKind`, `CredentialPolicy` (+3), `RungKind`,
`StreamFraming`, `ModelPlacement`.  New values are spec changes.

### Registry entries (phase by phase; every row `evidence: documentation` until captured)

| id | dialect | door | schemes | policy | phase |
|---|---|---|---|---|---|
| `azure` | openai-responses | `https://{resource}.openai.azure.com/openai/v1` | api-key, bearer | azure-chain | 1 |
| `azure-chat` | openai-chat | same | same | azure-chain | 1 |
| `azure-anthropic` | anthropic | `https://{resource}.services.ai.azure.com/anthropic` | api-key, x-api-key, bearer | azure-chain | 1 |
| `aws-anthropic` | anthropic | `https://aws-external-anthropic.{region}.api.aws` | sigv4(`aws-external-anthropic`), x-api-key | aws-chain | 1 |
| `bedrock-anthropic` | anthropic | `https://bedrock-mantle.{region}.api.aws/anthropic` | sigv4(`bedrock-mantle`), x-api-key | aws-chain | 1 |
| `bedrock-chat` | openai-chat | `https://bedrock-runtime.{region}.amazonaws.com/openai/v1` | sigv4(`bedrock`), bearer | aws-chain | 1 |
| `vertex` | gemini | `…/projects/{project}/locations/{location}/publishers/google/models/{model}` | bearer | gcp-chain | 1 |
| `vertex-anthropic` | anthropic | `…/publishers/anthropic/models/{model}:rawPredict` | bearer | gcp-chain | 1 |
| `vertex-express` | gemini | `https://aiplatform.googleapis.com/v1/publishers/google/models/{model}` | query-key | key | 1 |
| `bedrock` | **converse** (new dialect) | `https://bedrock-runtime.{region}.amazonaws.com` | sigv4(`bedrock`), bearer | aws-chain | 2 |
| `vertex-chat` | openai-chat | `…/endpoints/openapi` | bearer | gcp-chain | 3 |

Naming follows the `deepseek`/`deepseek-anthropic` rule: one provider
string, one wire behaviour.  `bedrock` is reserved for the native
Converse wire; until phase 2 it names nothing.

Support-matrix rows: `models: false` where the door has no listing
(Azure OpenAI data plane, mantle Messages, Vertex Claude).  Per-door
refusals (MAP-8) are compat-preset fields on the Anthropic dialect
(`structured_outputs`, `url_sources`, `server_tools`, `beta_header`,
`batches`, `models`, `fallbacks`: `send | reject`), populated from the
fact sheets and confirmed live.

### Harness (harness/PROTOCOL.md)

1. `credential` object (`kind` discriminator) + `now` + `settings`;
   `api_key` remains as shorthand.  Fixed keys: AWS test-suite pair
   `AKIDEXAMPLE` / `wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY`; a
   committed **test-only** 2048-bit RSA key generated for this corpus,
   allow-listed by path in `check_secrecy.py`, header comment naming it
   test-only.
2. `--direction request` compares `Authorization`, `x-amz-date`,
   `x-amz-security-token` byte for byte.  Ten AWS test-suite cases are
   frozen under `research/cloud-hosts/sources/aws-sigv4-suite/` and
   become `auth/sigv4-vectors.json`; the research signer passes
   `get-vanilla` and `post-vanilla-query` today.
3. New `--direction token`: credential + now + host → the exact
   token-exchange request (URL, headers, body incl. the RS256 JWT), then
   the parsed `BearerToken` from a pinned response.
4. `explain_auth` gains `files: {path: content}` materialized under a
   sandbox HOME, and the `unprobed` state.
5. `--direction stream` gains `framing: "aws-event-stream"` (phase 2).
6. `check_secrecy.py`: `AKIA[0-9A-Z]{16}`, 40-char AWS secrets,
   `-----BEGIN … PRIVATE KEY-----`, `ya29.` tokens, `eyJ` JWTs outside
   the fixed-key fixtures, Azure key shapes.

## Landed with ratification (same day)

- `spec/auth.md`: AUTH-1 three chains (rung by rung), AUTH-2 credential
  sum type, AUTH-3 cache key, AUTH-5, AUTH-7 `unprobed` + settings,
  AUTH-8 borrowed cloud files, AUTH-10 `auth_scheme`/`host`/`settings` and
  eleven host policies, AUTH-11 rung kinds; amendment footer.
- `spec/vocabularies.md`: `AuthScheme`, `CredentialKind`,
  `CredentialPolicy`, `RungKind`, `AuthStepState`, `StreamFraming`,
  `ModelPlacement`.
- `harness/PROTOCOL.md`: `credential`/`now`/`settings` on every op;
  `explain_auth` `files` + `unprobed`; new `token_exchange_build` /
  `token_exchange_parse` ops; `replay_stream` `framing`; `{"$file"}`
  expansion.
- `auth/sigv4-vectors.json`: ten AWS test-suite cases (the research
  signer reproduces all ten).
- `auth/test-keys/`: the corpus test key, public key, and a
  self-signed certificate (`x5t` recorded in the vectors).
- `auth/token-vectors.json`: nine cases — GCP service-account JWT +
  exchange, Azure certificate JWT + exchange, Azure secret exchange, and
  parse vectors for MSI, GCE metadata, `credential_process`, IMDS.  Both
  JWTs verify against the public key with `openssl dgst -verify`.
- `tools/check_secrecy.py`: PEM private keys, AWS secrets, `ya29.`
  tokens, signed JWTs; `.pem`/`.py`/`.sh` scanned; one allow-listed key
  path; AWS's documented `…EXAMPLE` ids excluded.  A guessed Azure key
  pattern was removed the same day (it matched base64 payloads): key
  shapes are added at first capture, never from memory.

## Reference landed (lm15-python, same day)

- `lm15/credentials.py`: `ApiKey`, `BearerToken`, `AwsCredentials`,
  canonical serde (`credential` serde kind, five vectors in
  `serde/canonical.json`), redacting reprs, the AUTH-3 skew.
- `lm15/cloud/sigv4.py`: reproduces all ten AWS test-suite vectors at
  every stage.  `lm15/cloud/rs256.py`: PEM/DER (PKCS#8 and PKCS#1),
  PKCS#1 v1.5, the pinned JWT serialization; both assertion vectors
  byte for byte.
- `lm15/cloud/hosts.py`: `resolve_settings`, `render_base_url`
  (`{location_host}` derivation), `finish_request` (the one pure
  function ports implement), `sign_request`.
- `lm15/features.py` / `lm15/access.py`: `auth_scheme` (the two-value
  `auth_header` stays as a property), `HostSpec`, `HostSetting`, the nine
  host policies with their fact-sheet citations.
- Dialects: every wire request — chat, models, files, batches, images,
  video — goes through one `BaseProviderLM._emit`, which applies the
  host rewrites, the auth header (once per request, AUTH-2) and SigV4.
  The Anthropic dialect no longer spells its own auth header; auth is a
  policy concern.  Every adapter takes `settings=` and `clock=`.
- `lm15/cloud/chains.py`: the three chains over the ten rung kinds;
  offline `explain` (with `unprobed`, subprocess rungs `absent` when the
  CLI is not on PATH) and online `resolve`; the AUTH-3 caching provider;
  `token_exchange_build/parse`.  Container-URL allow-list from botocore.
- Router: `RouterConfig.settings`; hosted providers resolve settings
  from config → env → default and credentials from the chain provider.
  Doctor: cloud walk, settings printed, `configured` true when a rung is
  selected or unprobed.
- Shim: `credential`/`now`/`settings` on every op, `files` on
  `explain_auth`, ops `sigv4_sign`, `token_exchange_build`,
  `token_exchange_parse`; enums from `features`/`credentials` reflected
  for `spec_drift`.  Harness: `--direction token`, `$file` expansion,
  sandbox HOME for `files`.
- Fixtures: eleven cloud cases in `auth/resolution.json` (mirrored to
  `conformance/auth_resolution.json`), `auth/sigv4-vectors.json`,
  `auth/token-vectors.json`, nine support-matrix rows.
- Harness at HEAD: 609 pass, 0 fail across thirteen directions;
  `tools/audit.py`, `spec_drift.py`, `check_secrecy.py`,
  `check_provenance.py` green; lm15-python 1087 tests.
- Docs: `docs/cloud-hosts.md`.

Corrections made while implementing, stated: RS256 costs ~75 ms per
signature in pure Python, not "a few ms"; the AWS `login` rung's refresh
needs a DPoP-bound EC key (botocore `LoginCredentialFetcher`) and is a
stated gap — fresh cached credentials are used, else `aws login`; Azure
Service Fabric managed identity (TLS thumbprint pinning) is a stated
gap; the SigV4 signer must NOT add `x-amz-content-sha256` (S3-only) and
must collapse inner whitespace in header values — both caught by the
vectors, which is what they are for.

`CONTRACT_PIN` moves when this contract commit exists; until then the
harness runs with `--no-check-pin`.

## Order of work

1. ~~Ratify this entry; land spec, vocabularies, protocol, vectors.~~ Done.
2. ~~Reference: credential sum type, ten rung kinds, three chains, doctor
   states, `auth_scheme`, host rewrites; `token` and `request` directions
   green on fixed vectors.~~ Done (above).
3. Azure live captures → `cases/azure*/`, goldens, error envelopes,
   support rows flip to `live`.  Per-provider `changes/` entry.
4. AWS live captures (three SSE doors).  Per-provider entry.
5. GCP live captures.  Per-provider entry.
6. Phase 2: `bedrock` Converse dialect + event-stream decoder; own
   design pass (MAP rules for Converse).
7. Phase 3: `vertex-chat`, Foundry non-OpenAI models, FIPS/GovCloud hosts.
8. Then the Go port implements ten rung kinds and five schemes once.

## Trade-offs, stated

- **`CredentialProvider` returns a sum type, not a string.**  Widening
  AUTH-2 before any port ships 1.0 is cheaper than after.
- **Chains follow each cloud's SDK order**, not AUTH-1's generic order.
  Same identity as boto3 / azure-identity / google-auth on the same
  machine; the doctor shows the winner.
- **Dropped rungs** (listed in AUTH-1 amendment) raise
  `NotConfiguredError` with the hint; they are Windows-only,
  interactive, or need extra packages.
- **RS256 in pure Python** (~150 lines: PKCS#8 DER parse, PKCS#1 v1.5
  pad, `pow`).  Not constant-time; ~75 ms per signature (measured, not
  the "few ms" first estimated); the user's own key, one-hour tokens.
  RFC 8017 vectors + a Google-issued token as tests.  PS256 for Azure is
  a live cell; azure-identity signs RS256.
- **PEM only; PKCS#12 certificates not parsed.**  Hint names
  `openssl pkcs12 -nodes`.
- **`location` defaults to `global` on Vertex.**  Docs recommend it; a
  residency user sets the variable; the doctor prints it.
- **`region` and `resource` have no default.**  Same as the cloud
  clients; a wrong-region default is a residency bug.
- **`vertex-express` is a separate entry.**  One string, one wire.  The
  `vertex:` hint names it when only an API key is present.
- **Network rungs are `unprobed` in the doctor.**  AUTH-7 stays offline.
- **A test RSA private key lives in the corpus**, allow-listed at one
  path.  Any other private key anywhere fails secrecy.
- **Phase 1 leaves out Converse.**  Nova/Llama/Mistral on Bedrock wait
  for phase 2; Claude and the OpenAI-wire models do not.
- **Self-reviewed attack pass.**  No second agent was available;
  `40-attack.md` says so.

## What is not yet evidenced (blocks every `cases/` row)

Everything on the wire.  Live cells named in the fact sheets and in
`20-experiments.py` (≈60 cells, < $1): which Azure scope each host
accepts; `x-api-key` on `openai.azure.com`; data-plane model listing on
Azure and Vertex; mantle behaviour for pre-4.7 models, other
`anthropic-version` values, `anthropic-beta`, structured outputs; Bedrock
chat compat knobs; `aws-anthropic` batches/models surfaces and
`inference_geo`; Vertex `x-goog-api-key` header form; thinking-signature
replay across doors; every host error envelope.

Accounts to provision, in parallel with step 2:

- **AWS**: Bedrock model access for Claude Haiku 4.5 + one Nova model;
  an IAM user with `bedrock:InvokeModel*`, `bedrock-mantle:CreateInference`,
  `bedrock:ListFoundationModels`; Claude Platform on AWS sign-up with
  `aws iam enable-outbound-web-identity-federation` and a workspace id.
- **Azure**: an Azure OpenAI resource with one Responses-capable
  deployment; a Foundry resource with a Claude deployment; an app
  registration with a client secret **and** a certificate; `az login`.
- **GCP**: a project with Vertex enabled and Claude enabled in Model
  Garden; `gcloud auth application-default login`; one service-account
  JSON key (for the RS256 path); an express-mode API key.

---

Ratified-by: Maxime Rivest, 2026-09-03 — in session ("i ratify"), after
the dropped-rung list was explained and accepted; transcribed.
