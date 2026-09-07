# spec/auth.md — credential resolution, refresh, storage, secrecy

**STATUS: RATIFIED 2026-08-31.** These rules are normative for every lm15
implementation. The reference implementation (lm15-python `auth.py`,
`authkit.py`, `doctor.py`) implements them; `auth/resolution.json` pins the
AUTH-1/AUTH-7 behavior as fixtures; ports are held to them.

Scope: how an lm15 implementation finds, refreshes, stores, and explains
credentials. lm15 does not own interactive login: applications do. These
rules cover everything around that boundary.

## AUTH-1 — Credential policy and resolution order

Every provider declares exactly one credential policy in its manifest
(`credential_policy`). Routers, doctors, and shims derive their behavior
from the declaration — never from a hardcoded provider-name list, which is
a second copy of the same fact and will drift (amended 2026-09-01):

- **`key`** — the ordinary chain below supplies the credential.
- **`oauth`** (`claude-code`, `openai-codex`) — the provider resolves
  **only** its local CLI credential file; the chain below never runs. In
  particular (stored-credential-owns-provider): a failed OAuth load or
  refresh never falls back to an environment variable silently. An `oauth`
  manifest declares no environment keys.
- **`oauth-unless-explicit`** (`xai`) — an explicit `api_keys` entry wins;
  otherwise a **usable** stored local OAuth credential (fresh, or expired
  with a refresh token) wins; the declared environment keys are consulted
  only when no usable credential is stored. Rationale: deliberate
  in-process configuration always wins, but between two kinds of stored
  state — a subscription login and an ambient environment variable — the
  subscription wins because it spends no money per token, and normal
  inference must never unexpectedly spend money. Stated trade-off: with a
  usable login stored, a set environment key is silently ignored; forcing
  that key's account requires passing it explicitly. The doctor (AUTH-7)
  makes the winning and shadowed rungs visible. Implementations expose an
  offline stored-credential probe on the adapter (reads files, never the
  network) so routers can walk this chain without I/O beyond the
  credential file.

For a `key` provider constructed through the router, the credential
resolves in exactly this order; the first hit wins and later rungs are
dead:

1. an explicit `api_keys` entry for the provider (static value or
   credential-provider callable);
2. the provider's declared environment keys, in declared order, first
   non-empty value;
3. for local-server presets only: the preset's placeholder key.

For an `oauth-unless-explicit` provider the order is: the explicit
`api_keys` entry; the stored local OAuth credential (AUTH-8 store paths)
when usable; the declared environment keys; then the typed
not-configured error carrying the login hint.

Cloud chains (amended 2026-09-03, changes/2026-09-03-cloud-hosts.md). Three
further policies exist for providers whose door is a cloud host:
**`aws-chain`**, **`azure-chain`**, **`gcp-chain`**. Each is the cloud SDK's
own default resolution order — botocore `create_credential_resolver`,
azure-identity `DefaultAzureCredential`, google-auth `google.auth.default`
— pinned from the resolver source frozen under
`research/cloud-hosts/sources/`. WHY: a machine configured for the cloud's
SDK must yield the SAME principal under lm15; a different principal is a
security bug (audit logs, permission boundaries), not a convenience gap.
Rung 0 of every cloud chain is the explicit `api_keys` entry (any
credential kind or provider), matching all three SDKs' "constructor
arguments first". The first usable rung wins; later rungs are dead.

`aws-chain`:
0. explicit `api_keys`;
1. the door's bearer variable — `ANTHROPIC_AWS_API_KEY` (`aws-anthropic`),
   `AWS_BEARER_TOKEN_BEDROCK` (`bedrock*`) — → `ApiKey`/`BearerToken`;
2. `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` [+ `AWS_SESSION_TOKEN`];
3. profile assume-role (`role_arn` + `source_profile` | `credential_source`
   ∈ {Environment, Ec2InstanceMetadata, EcsContainer}) via STS `AssumeRole`;
4. web identity (`AWS_WEB_IDENTITY_TOKEN_FILE` + `AWS_ROLE_ARN`
   [+ `AWS_ROLE_SESSION_NAME`], or the profile's `web_identity_token_file`)
   via STS `AssumeRoleWithWebIdentity`;
5. IAM Identity Center (`sso_session` → `sso-session` section, or legacy
   `sso_start_url`/`sso_region`; `sso_account_id`, `sso_role_name`; cached
   token `~/.aws/sso/cache/<sha1>.json`; `sso-oidc CreateToken` refresh;
   `sso GetRoleCredentials`);
6. `~/.aws/credentials` (`AWS_SHARED_CREDENTIALS_FILE`; profile from
   `AWS_PROFILE`, default `default`);
7. login (`login_session` profile setting; cache `~/.aws/login/cache`,
   `AWS_LOGIN_CACHE_DIRECTORY`);
8. `credential_process` (stdout JSON `Version: 1`, `AccessKeyId`,
   `SecretAccessKey`, `SessionToken`, `Expiration` RFC 3339; absent
   `Expiration` means long-term);
9. `~/.aws/config` static keys (`AWS_CONFIG_FILE`);
10. container (`AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` on `169.254.170.2`,
    or `AWS_CONTAINER_CREDENTIALS_FULL_URI`; `AWS_CONTAINER_AUTHORIZATION_TOKEN`
    or `…_TOKEN_FILE` → `Authorization`; a `FULL_URI` is accepted only when
    `https`, loopback, or a host in {`169.254.170.2`, `169.254.170.23`,
    `fd00:ec2::23`, `localhost`} — botocore's allow-list);
11. IMDSv2 (`PUT /latest/api/token` with `X-aws-ec2-metadata-token-ttl-seconds`,
    then `GET /latest/meta-data/iam/security-credentials/<role>` with the
    token; host `169.254.169.254` / `[fd00:ec2::254]` /
    `AWS_EC2_METADATA_SERVICE_ENDPOINT`; skipped when
    `AWS_EC2_METADATA_DISABLED=true`).
Rung 1 is placed where the Anthropic AWS client places it. Dropped, stated:
the boto2 files (`~/.boto`, `/etc/boto.cfg`).

`azure-chain`:
0. explicit `api_keys`;
1. the door's key variable — `AZURE_OPENAI_API_KEY` (`azure`, `azure-chat`),
   `ANTHROPIC_FOUNDRY_API_KEY` (`azure-anthropic`) → `ApiKey`;
2. environment service principal: `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` +
   (`AZURE_CLIENT_SECRET` | `AZURE_CLIENT_CERTIFICATE_PATH`
   [+ `AZURE_CLIENT_CERTIFICATE_PASSWORD`, `AZURE_CLIENT_SEND_CERTIFICATE_CHAIN`]);
   authority `AZURE_AUTHORITY_HOST` (default `https://login.microsoftonline.com`);
3. workload identity: `AZURE_FEDERATED_TOKEN_FILE` + tenant + client
   (`client_assertion` = the file's contents);
4. managed identity, dispatched on the environment exactly as azure-identity
   does: `IDENTITY_ENDPOINT`+`IDENTITY_HEADER`+`IDENTITY_SERVER_THUMBPRINT`
   → Service Fabric; `IDENTITY_ENDPOINT`+`IDENTITY_HEADER` → App Service;
   `IDENTITY_ENDPOINT`+`IMDS_ENDPOINT` → Azure Arc; `MSI_ENDPOINT`+`MSI_SECRET`
   → Azure ML; `MSI_ENDPOINT` → Cloud Shell; else IMDS
   `GET http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=…`
   with `Metadata: true`; user-assigned identity by `AZURE_CLIENT_ID`;
5. `az account get-access-token --output json --scope <scope> [--tenant <t>]`;
6. Azure PowerShell (`Get-AzAccessToken`);
7. `azd auth token --output json --scope <scope>`.
Continuation policy, copied from azure-identity: a rung 2–4 that CAN attempt
and fails stops the chain with `AuthError`; rungs 5–7 are tried through
errors. `AZURE_TOKEN_CREDENTIALS=prod|dev|<CredentialName>` narrows the
chain as in the SDK. Dropped, stated: Shared Token Cache (Windows/Visual
Studio), Visual Studio Code (broker package), Interactive browser (off by
default), Broker (extra package), `AZURE_USERNAME`+`AZURE_PASSWORD` (ROPC).

`gcp-chain`:
0. explicit `api_keys`;
1. (`vertex-express` only) `GOOGLE_API_KEY` → `ApiKey`;
2. `GOOGLE_APPLICATION_CREDENTIALS` → JSON file, dispatched on `type`;
3. `$CLOUDSDK_CONFIG/application_default_credentials.json`, default
   `~/.config/gcloud/application_default_credentials.json`, same dispatch;
4. metadata server `GET http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token`
   with `Metadata-Flavor: Google` (`GCE_METADATA_HOST`, legacy
   `GCE_METADATA_ROOT`; skipped when `NO_GCE_CHECK` is truthy);
5. `gcloud auth print-access-token` — an lm15 addition placed last, stated.
`type` dispatch: `authorized_user` (`refresh_token`, `client_id`,
`client_secret` → `POST https://oauth2.googleapis.com/token`
`grant_type=refresh_token`); `service_account` (`client_email`,
`private_key`, `token_uri` → RS256 JWT assertion, `aud` = `token_uri`,
`scope`, `iat`, `exp` = `iat`+3600 → `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`);
`external_account` (`audience`, `subject_token_type`, `token_url`,
`credential_source` ∈ {`file`, `url`, `executable`, AWS} → STS
`urn:ietf:params:oauth:grant-type:token-exchange` → optional
`service_account_impersonation_url`); `impersonated_service_account`
(`source_credentials` nested, `service_account_impersonation_url`,
`delegates` → `iamcredentials …:generateAccessToken`). Other `type` values
(`external_account_authorized_user`, `gdch_service_account`) raise
`NotConfiguredError` naming the type. Dropped, stated: the App Engine
legacy runtime rung. Scope for every Vertex door:
`https://www.googleapis.com/auth/cloud-platform`.

## AUTH-2 — Credential providers

Every implementation exposes a credential-provider shape native to its
language (zero-arg callable in Python/TS/Julia, single-method interface in
Go/Rust). The adapter invokes it once per request at request-build time and
never caches the returned value; caching belongs to the provider itself.

A credential is a closed sum, not a string (amended 2026-09-03):

| Kind | Canonical JSON | Consumed by `auth_scheme` |
|---|---|---|
| `ApiKey` | `{"kind":"api_key","value"}` | `bearer`, `x-api-key`, `api-key`, `query-key` |
| `BearerToken` | `{"kind":"bearer_token","value","expires_at"?}` | `bearer`; else `x-api-key` (amended 2026-09-04, ratified 2026-09-06) |
| `AwsCredentials` | `{"kind":"aws","access_key_id","secret_access_key","session_token"?,"expires_at"?}` | `sigv4` |

Scheme selection (amended 2026-09-04, ratified 2026-09-06;
changes/2026-09-04-bedrock-bearer.md, changes/2026-09-06-decisions.md D1):

- An `ApiKey` uses the policy's first header-carrying scheme in policy
  order (`bearer`, `x-api-key`, `api-key`, `query-key`).
- A `BearerToken` uses `bearer` if the policy lists it; else `x-api-key`
  if the policy lists it; else the adapter raises `NotConfiguredError`
  naming the accepted schemes.
- `AwsCredentials` uses `sigv4` only; any other scheme raises.

Cost, stated: a token given to a key-header-only door that does not take
tokens (first-party `anthropic`) gets the provider's 401, not a local
error. A harness wire pin lands with the first Bedrock Claude HTTP 200
(account-gated today; stated, not absorbed).

A provider returns one of these. An explicit `api_keys` entry may be a
plain string (read as `ApiKey`), one of these values, or a provider.
Python/TS/Julia: a tagged value; Go/Rust: an interface/enum with the same
kind names. `expires_at` is RFC 3339; absent means non-expiring.

## AUTH-3 — Refresh state machine

For refreshable OAuth credentials:

- an expiry skew of five minutes: a token inside the skew window counts as
  expired for refresh purposes;
- refresh is double-checked: acquire the cross-process lock, re-read the
  stored credential, and skip the network refresh when the re-read
  credential is fresh (another process refreshed while we waited);
- the network refresh executes while holding the lock. Trade-off, stated:
  one slow refresh stalls sibling processes up to the lock timeout; the
  alternative double-spends rotated refresh tokens, which forces re-login;
- an expired credential without a refresh token, or a failed refresh,
  raises the typed auth error carrying the provider id and a re-login hint
  naming the exact command. Never a raw traceback, never a silent fallback.
- (amended 2026-09-03) a token cache is keyed by the provider id AND a hash
  of the settings that select the identity (AWS profile / role; Azure
  tenant + client id + resource; GCP project + credential source path), so
  two identities on one provider never share a cached token.

## AUTH-4 — Storage semantics

- Credential files are written atomically: temp file created private,
  fsynced, renamed over the target. A reader observes a complete old file or
  a complete new file, never a partial one.
- Credential files and their temp files carry mode 0600 where the platform
  supports it.
- Writes are serialized by an advisory cross-process lock scoped to the
  credential file's canonical path.
- Lock files live in an lm15-owned directory, never inside another tool's
  directory (`~/.claude`, `~/.codex` are foreign territory).
- Stated limitation: the lock is cooperative among lm15 processes. Foreign
  writers do not take it; AUTH-3's double-checked re-read is the mitigation.

## AUTH-5 — Secrecy invariant

Token and key material never appears in: reprs, exception messages,
exception reprs, doctor reports, log output produced by lm15, or any fixture
expectation in this corpus. Fixtures plant the sentinel
`SECRET-SENTINEL-DO-NOT-PRINT` as credential values and assert its absence
from every rendered surface. `tools/check_secrecy.py` enforces the corpus
side; each implementation enforces the runtime side in its test suite.
Secret material includes (amended 2026-09-03) signed JWT assertions,
token-exchange request and response bodies, and metadata/IMDS/MSI
credential responses: each is a bearer-equivalent for its lifetime.

## AUTH-6 — Error taxonomy

- Missing/unreadable/malformed credential sources → the implementation's
  `NotConfiguredError` equivalent, carrying `provider` and a
  `credential_hint` that names the fix (`export GROQ_API_KEY=...`,
  ``run `codex login` ``).
- Expired-and-unrefreshable or provider-rejected credentials → `AuthError`
  equivalent, same hint discipline.
- Lock contention → a local timeout error type, deliberately **not** an
  `AuthError`: nothing is wrong with the credential.

## AUTH-7 — Explainability (doctor)

Every implementation ships an `explain_auth` equivalent that:

- walks exactly the AUTH-1 chain (divergence from real construction is a
  bug, testable against `auth/resolution.json`);
- performs no network I/O;
- reports each rung as `selected`, `shadowed` (usable but beaten by an
  earlier rung), `absent`, or (amended 2026-09-03) `unprobed` — a network
  rung (IMDS, container endpoint, Azure managed identity, GCE metadata)
  that the offline doctor did not contact. An environment variable may
  prove such a rung absent (`AWS_EC2_METADATA_DISABLED`, `NO_GCE_CHECK`)
  or present (`IDENTITY_ENDPOINT`, `MSI_ENDPOINT`, the container URIs);
  otherwise it is `unprobed`. Real resolution probes it with the SDK's
  timeouts;
- prints the resolved host settings (region, location, project, resource,
  workspace) by name and value — they are not secrets and they decide
  residency (amended 2026-09-03);
- never includes secret values in its output. Presence checks may read
  values into memory; they must not retain or render them.

## AUTH-8 — Well-known paths

- lm15-owned credential store: `$LM15_CREDENTIALS_PATH`, else
  `$XDG_CONFIG_HOME/lm15/credentials.json`, else
  `~/.config/lm15/credentials.json`.
- Lock directory: `$LM15_LOCK_DIR`, else `$XDG_CACHE_HOME/lm15/locks`, else
  `~/.cache/lm15/locks`.
- Borrowed files: `~/.claude/.credentials.json` (Claude Code),
  `~/.codex/auth.json` (Codex CLI), and `~/.pi/agent/auth.json` (Pi agent
  store, read for xAI when present). These formats are wire-fact-like:
  owned by foreign tools, revalidated against reality, never "cleaned".
- Borrowed cloud files (amended 2026-09-03): `~/.aws/credentials`,
  `~/.aws/config` (`AWS_SHARED_CREDENTIALS_FILE`, `AWS_CONFIG_FILE`),
  `~/.aws/sso/cache/*.json`, `~/.aws/login/cache/*.json`,
  `$CLOUDSDK_CONFIG|~/.config/gcloud/application_default_credentials.json`.
  Same rule: foreign formats, revalidated, never cleaned. lm15 never
  writes to them; refreshed cloud tokens live in memory (AUTH-3 cache),
  never in a foreign file.
- The lm15-owned store's xAI entry is
  `{"xai": {"type": "oauth", "access", "expires" (ms), "refresh"?}}`;
  refreshes write back to whichever file the credential came from, because
  xAI rotates refresh tokens.

## AUTH-9 — Login-flow primitives

Every implementation exposes one uniform login entry point
(`login(provider)` or the language's idiomatic equivalent; added
2026-09-01). It runs the login flow lm15 owns for that provider (today:
xAI's device-code flow) and returns the stored credential. For every other
provider it fails with the implementation's unsupported-feature error
naming the exact fix: the foreign CLI command that owns the flow
(`claude` `/login`, `codex login`) or the console URL where an API key is
created. Console URLs are guidance strings, not wire facts: drift costs a
stale hint, never broken inference. The entry point must not prompt, open
a browser, or spend money except in the one flow explicitly requested.
Provider-named login functions may exist as the concrete flows underneath;
the uniform door dispatches to them.

Implementations that ship login primitives (PKCE, RFC 8628 device polling,
loopback callback listener, credential store) follow:

- PKCE: S256 only; the RFC 7636 Appendix B vector is a required test.
- Device polling: `slow_down` grows the interval by 5 seconds unless the
  server names an interval; expiry is a typed error distinct from denial.
- Loopback listener: binds `127.0.0.1` only; wrong path or wrong state gets
  an error page and the wait continues; a provider `error` parameter ends
  the wait as a typed failure; authorization codes are repr-suppressed.

## AUTH-10 — Access policy: auth by composition

An adapter is three composed things: a **dialect** (the wire codec:
Anthropic Messages, OpenAI Responses, OpenAI Chat Completions, Gemini), for
the chat dialect an optional **compat** value (a server's quirks), and an
**access policy** — a value that says how the dialect reaches a backend.
Subscription access is never a subclass of a dialect: Go and Rust have no
inheritance, and a class per access path makes every port invent its own
shape for the same facts.

`AccessPolicy` (the reference's `ProviderManifest` under its true name) is
pure data. Ports copy the table as data and consult it at the same named
points:

| Field | Meaning | Consulted at |
|---|---|---|
| `provider` | canonical provider string | errors, routing, doctor |
| `supports` | endpoint surfaces this access path carries | every surface driver: a dialect that implements a surface still RAISES when the policy does not carry it |
| `credential_policy`, `auth_modes`, `env_keys`, `enterprise_variants` | AUTH-1; support-matrix pinned | router, doctor, error guidance |
| `auth_scheme` (was `auth_header`; amended 2026-09-03) | the schemes this access path accepts, in preference order, from `AuthScheme`; the credential kind selects one | the auth header / query / signature |
| `headers` | static headers, in order | every request; Anthropic joins `anthropic-beta` with its own betas |
| `login_hint` | re-login guidance | auth errors — always under `oauth`; under `oauth-unless-explicit` only when the stored login was the rung that won |
| `backend` | dialect-consulted variant (`api` is the public API) | a small stated set of branches inside the dialect |
| `backend_options` | string knobs the variant needs | those branches |
| `system_prefix` | text the backend requires first in system/instructions | payload |
| `base_url` | this access path's default base URL | construction, when the caller left the dialect default |
| `host` (amended 2026-09-03) | a host descriptor: URL template over the settings below, `model_in` (`body`\|`path`), `anthropic_version_in` (`header`\|`body:<value>`), `stream_framing` (`sse`\|`aws-event-stream`), `required_headers` (`name: {setting}`), `sigv4_service` | URL build, payload, stream decoder |
| `settings` (amended 2026-09-03; the typed face of `backend_options`) | `region`, `workspace`, `project`, `location`, `resource`, `authority_host`, `scope`; each with its env fallbacks in order | construction; the doctor prints them |

Host settings and their env fallbacks (in order): `region` ←
`AWS_REGION`, `AWS_DEFAULT_REGION`, profile `region` — **no default,
raise**; `workspace` ← `ANTHROPIC_AWS_WORKSPACE_ID` — no default;
`project` ← `GOOGLE_CLOUD_PROJECT`, `GCLOUD_PROJECT`, the ADC file's
`quota_project_id`/`project_id` — no default; `location` ←
`GOOGLE_CLOUD_LOCATION` — default `global` (stated trade-off:
availability first; the doctor prints it); `resource` ←
`AZURE_OPENAI_ENDPOINT` (a full URL) or `AZURE_OPENAI_RESOURCE`;
`ANTHROPIC_FOUNDRY_BASE_URL` or `ANTHROPIC_FOUNDRY_RESOURCE` — no default;
`authority_host` ← `AZURE_AUTHORITY_HOST`, default
`https://login.microsoftonline.com`; `scope` default
`https://ai.azure.com/.default`. Settings are never part of the model
string: `Request.model` stays `provider:model`.

The policies (reference: `lm15/access.py`):

| Policy | Dialect | credential | auth_header | backend | Notable fields |
|---|---|---|---|---|---|
| `anthropic` | Anthropic | key | `x-api-key` | api | files, batches, models |
| `claude-code` | Anthropic | oauth | bearer | claude-code | betas `claude-code-20250219,oauth-2025-04-20`; `x-app: cli`; `user-agent: claude-cli/<v>`; `anthropic-dangerous-direct-browser-access: true`; system prefix "You are Claude Code, Anthropic's official CLI for Claude."; no files/batch/live |
| `openai` | Responses | key | bearer | api | full surface |
| `openai-codex` | Responses | oauth | bearer | chatgpt-codex | base `https://chatgpt.com/backend-api/codex`; `OpenAI-Beta: responses=experimental`; `originator`; `client_version` option; instructions prefix "You are a helpful assistant."; complete/stream/models only |
| `openai_chat` | Chat | key | bearer | api | complete, stream, models |
| `xai` | Chat (+ provider adapter) | oauth-unless-explicit | bearer | api | base `https://api.x.ai/v1`; images, video, models |
| `gemini` | Gemini | key | `x-goog-api-key` | api | full surface incl. caches |
| `azure` / `azure-chat` | Responses / Chat | azure-chain | `api-key`, `bearer` | azure-openai | `https://{resource}.openai.azure.com/openai/v1`; model = deployment name; data-plane `/models` lists the resource catalog (live, contrary to docs); `azure` also carries Files, Batch, speech and Realtime |
| `azure-anthropic` | Anthropic | azure-chain | `x-api-key`, `bearer` | azure-foundry | `https://{resource}.services.ai.azure.com/anthropic/v1`; docs also claim `api-key`, but live it is 401 while `x-api-key` reaches deployment lookup; no batches/models/`fallbacks`; successful inference quota-blocked |
| `aws-anthropic` | Anthropic | aws-chain | `sigv4`(`aws-external-anthropic`), `x-api-key` | aws-external-anthropic | `https://aws-external-anthropic.{region}.api.aws`; header `anthropic-workspace-id: {workspace}`; betas pass |
| `bedrock-anthropic` | Anthropic | aws-chain | `sigv4`(`bedrock-mantle`), `x-api-key` | bedrock-mantle | `https://bedrock-mantle.{region}.api.aws/anthropic`; no structured outputs, URL/Files sources, server tools, batches, models, `anthropic-beta` |
| `bedrock-chat` | Chat | aws-chain | `sigv4`(`bedrock`), `bearer` | bedrock-runtime | `https://bedrock-runtime.{region}.amazonaws.com/openai/v1`; versioned ids; GET `/openai/v1/models` is 404 under SigV4 and bearer (live 2026-09-03/04) |
| `bedrock-mantle-chat` | Chat | aws-chain | `sigv4`(`bedrock-mantle`), `bearer` | bedrock-mantle | `https://bedrock-mantle.{region}.api.aws/v1`; un-versioned ids; GET `/v1/models` lists (55, live 2026-09-04); Claude 400 "does not support this API"; Nova 404 |
| `vertex` | Gemini | gcp-chain | `bearer` | vertex | `https://{location_host}/v1/projects/{project}/locations/{location}/publishers/google/models/{model}`; `location_host` = `aiplatform.googleapis.com` (global) / `{location}-aiplatform.googleapis.com` / `aiplatform.{us\|eu}.rep.googleapis.com`; stream `:streamGenerateContent?alt=sse` |
| `vertex-express` | Gemini | key | `query-key` | vertex-express | `https://aiplatform.googleapis.com/v1/publishers/google/models/{model}`; `GOOGLE_API_KEY` |
| `vertex-anthropic` | Anthropic | gcp-chain | `bearer` | vertex | `…/publishers/anthropic/models/{model}:rawPredict` / `:streamRawPredict`; `model_in: path`; `anthropic_version_in: body:vertex-2023-10-16`; no batches/models/Files sources |
| `bedrock` (phase 2) | Converse | aws-chain | `sigv4`(`bedrock`), `bearer` | bedrock-runtime | `aws-event-stream` framing; `ListFoundationModels` on `bedrock.{region}.amazonaws.com` |
| `vertex-chat` (phase 3) | Chat | gcp-chain | `bearer` | vertex | `…/endpoints/openapi` |

Host policies above are declared from documentation
(changes/2026-09-03-cloud-hosts.md, `research/cloud-hosts/`); each row
becomes wire-evidenced with its own `changes/` entry and receipts.

The `chatgpt-codex` backend branches, exhaustively: (1) payload —
`instructions` defaults to the prefix, `store: false`, `stream: true`,
no max-token knob; (2) `complete` materializes the stream (streaming-first
backend); (3) errors — a `{"detail": "..."}` envelope is classified before
the OpenAI envelope; (4) `/models` takes `client_version` and lists
`models[].slug`. The `claude-code` backend has no branches beyond the
policy fields.

What stays per-language: loading a stored login (keyed by `provider`) and
the offline stored-credential probe. The policy says *that* a login is
used; the loader says *how*. A subscription adapter class, where a
language keeps one for ergonomics, holds the class-level policy and
constructors and nothing that touches the wire.

WHY: the same wire from `AnthropicLM(access=CLAUDE_CODE)` and from a named
`ClaudeCodeLM` is verifiable (lm15-python `tests/test_access_policy.py`);
a port's binding is a table lookup, not a re-derivation of headers from
memory.

## AUTH-11 — Rung kinds: the mechanisms a chain is made of

(Added 2026-09-03, changes/2026-09-03-cloud-hosts.md.) A cloud chain
(AUTH-1) is data: an ordered list of rungs, each naming one kind from the
closed vocabulary `RungKind` and its parameters. The kinds are the only
code a port writes for auth; a new kind is a spec change.

| Kind | Mechanism | Used by |
|---|---|---|
| `env` | read named variables, first non-empty wins | all |
| `ini-profile` | parse the AWS shared files with profile selection, `sso-session` sections, and `source_profile` chaining | AWS |
| `json-file` | read a JSON credential file and dispatch on `type` | GCP |
| `subprocess` | run a CLI with fixed arguments, parse stdout | AWS `credential_process`; Azure `az`, `azd`, PowerShell; GCP `gcloud` |
| `http-metadata` | unauthenticated local HTTP with a marker header (`X-aws-ec2-metadata-token`, `Metadata: true`, `Metadata-Flavor: Google`) and the SDK's timeouts | AWS IMDSv2 and container, Azure managed identity, GCE metadata |
| `http-token-exchange` | HTTPS POST (form or JSON) → `{access_token, expires…}` | Azure secret/certificate/workload, GCP refresh/STS/impersonation, AWS SSO and login refresh |
| `sigv4-sts` | a SigV4-signed STS call returning temporary keys | AWS assume-role |
| `unsigned-sts` | STS `AssumeRoleWithWebIdentity` (no signature) | AWS web identity |
| `jwt-rs256` | build a JWT and sign it RSASSA-PKCS1-v1_5/SHA-256 with a PEM private key (PKCS#8 or PKCS#1); PKCS#12 is not parsed — the hint names `openssl pkcs12 -nodes` | GCP service account; Azure certificate (`x5t` = base64url SHA-1 of the DER cert; `x5c` chain when asked) |
| `file-cache` | read a foreign tool's cached-token JSON (AUTH-8) | AWS SSO, AWS login |

Every rung result is one of the AUTH-2 credential kinds. Every network
rung is `unprobed` in the doctor (AUTH-7). Signing is deterministic under
a fixed clock and fixed keys: the harness pins SigV4 `Authorization`
headers and RS256 assertions byte for byte (`harness/PROTOCOL.md`,
`auth/sigv4-vectors.json`).

Stated: RS256 in the Python reference is ~150 lines of standard-library
arithmetic, not constant-time, about 75 ms per signature (measured
2026-09-03) once per one-hour assertion; the key is the user's own. Ports use their platform RSA where it exists (Go
`crypto/rsa`, Node `crypto`), a crate in Rust.

---

Ratified-by: Maxime Rivest, 2026-08-31 — assented in session ("I ratify");
transcribed.

Amended 2026-09-01 (AUTH-1 credential policy declaration; AUTH-9 uniform
login entry point; xai fixtures) — ratified in session ("implement all
three!"); see changes/2026-09-01-credential-policy.md.

Amended 2026-09-01, same day (AUTH-1: xai policy reordered to
`oauth-unless-explicit` — stored subscription beats environment keys;
supersedes the morning's `key-then-oauth` before any port consumed it) —
ratified in session ("we always want to use subscriptions before
billing"); see changes/2026-09-01-subscription-first.md.

Amended 2026-09-02 (AUTH-10: access policy as a value; subscription
adapters are names for a binding) — ratified in session ("i ratify auth
10"); see changes/2026-09-02-auth-by-composition.md.

Amended 2026-09-03 (AUTH-1 cloud chains `aws-chain`/`azure-chain`/`gcp-chain`;
AUTH-2 credential sum type; AUTH-3 cache key; AUTH-5 assertions are
secret; AUTH-7 `unprobed` and settings; AUTH-8 borrowed cloud files;
AUTH-10 `auth_scheme`, `host`, `settings`, nine host policies; AUTH-11
rung kinds) — ratified in session ("i ratify"); see
changes/2026-09-03-cloud-hosts.md.

Amended 2026-09-04 (AUTH-2: a `BearerToken` may travel under `x-api-key`
when the policy lists it and not `bearer`) — ratified 2026-09-06 in
session ("perfect, implement it all!"; changes/2026-09-06-decisions.md
D1); found offline: `AWS_BEARER_TOKEN_BEDROCK` set on the machine made
`bedrock-anthropic` raise `NotConfiguredError`; see
changes/2026-09-04-bedrock-bearer.md and
changes/2026-09-06-ratification.md.

Amended 2026-09-04 (AUTH-10: tenth host policy `bedrock-mantle-chat`) —
ratified 2026-09-06 in session ("perfect, implement it all!";
changes/2026-09-06-decisions.md D2).  Live evidence that Bedrock's Chat
Completions API is two hosts, not one: different URL, SigV4 service,
model-id namespace, listing, and reasoning shape.  Not a rename of
`bedrock-chat`.  One provider string, one wire.  See
changes/2026-09-04-bedrock-mantle-chat-live.md and
changes/2026-09-06-ratification.md.
