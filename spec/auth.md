# spec/auth.md — credential resolution, refresh, storage, secrecy

**STATUS: existing rules ratified 2026-08-31 with subsequent amendments;
2026-09-22 managed-authentication revision is a REVIEW DRAFT.** The newly
written behavior is a normative candidate for review, not a claim that any
SDK implements it. Unchanged API-key and cloud-identity rules remain in
force. The detailed revision is [AUTH-12–26](auth-managed.md) (core tier;
[reserved rules](auth-managed-reserved.md) bind nobody until promoted),
incorporated as the managed-authentication part of this specification. See
[the change record](../changes/2026-09-22-managed-authentication.md) and
[fixture transition](../auth/managed/README.md).

Scope: LM15 owns credential resolution, provider login protocols, renewal,
storage coordination and safe request binding. Applications own presentation,
authorized user scopes and deliberate login actions. Ordinary inference never
initiates interactive login. The interactive `connect()` helper composes these
operations without changing process-global identity or canonical request types.
No compatibility with the old implicit Claude/Codex/Pi or xAI login behavior is
required; API-key and cloud users are deliberately unaffected when they do not
attach a managed Auth.

## AUTH-1 — Credential policy and resolution order

Every provider declares exactly one credential policy in its manifest
(`credential_policy`). Routers, doctors, and shims derive their behavior
from the declaration — never from a hardcoded provider-name list, which is
a second copy of the same fact and will drift (amended 2026-09-01):

- **`key`** — the ordinary chain below supplies the credential.
- **`connection`** — an account-only route requires an accepted explicit
  credential or an explicitly attached managed Auth. No environment-key,
  foreign CLI-file or implicit managed-store lookup. Without either source,
  fail with login guidance naming LM15's login/connect operation.

The `oauth` and `oauth-unless-explicit` policies are proposed for retirement
by the 2026-09-22 draft (ratification items R1/R2); they remain in force and in
the runtime until that answer. Protocol capabilities now live in discoverable auth-method
and binding declarations (AUTH-13), not implicit source chains. A dual-method
provider such as xAI, Meta or OpenRouter has ordinary `key` resolution without
managed Auth, and the managed rules below when Auth is attached. Account-only
routes use `connection`. OAuth is not a billing guarantee: account access can
consume credits or incur extra usage.

**Mode boundary:** the key/cloud chains in this section apply to callers
without managed Auth. With managed Auth, AUTH-15 is authoritative: explicit
credentials/named identities still win, then the scoped connection; absence
or failure never falls through to ambient identity. The bound client returned
by `connect()` is stricter: it pins the selected Connection ID and model and
rejects identity overrides.

For a `key` provider constructed through the router, the credential
resolves in exactly this order; the first hit wins and later rungs are
dead:

1. an explicit `api_keys` entry for the provider, selected by the shared-key
   rule below (static value or credential-provider callable);
2. the provider's declared environment keys, in declared order, first
   non-empty value;
3. for local-server presets only: the preset's placeholder key.

### Shared explicit keys (ratified 2026-09-09)

Select an exact provider entry first, accepting the standard underscore
alias. Without one, select the single configured provider whose declared
`env_keys` tuple is identical to the target's **non-empty** tuple (including
order). Derive this from provider declarations, never a second family-name
table. Thus `openai` supplies `openai-chat`, but `gemini` does not supply
`vertex-express`: overlapping lists are not identical. Empty lists do not
join local servers, OAuth stores or GCP chains.

An exact entry wins regardless of other shared candidates. Multiple shared
candidates without an exact entry raise `not_configured`; never choose by
map order, compare secrets, or invoke credential providers to test equality.
The diagnostic names only configuration keys and the target. Duplicate
spellings for the same explicit provider are refused, not resolved by order.
An empty explicit credential is a configuration failure, not permission to
fall back to ambient credentials.

The selected shared entry is still the explicit rung, ahead of every later
credential source. AUTH-7 shows the source configuration key when it differs
from the target; it remains kind `api_keys`. This does not claim the key is
valid for the selected host/account: provider authentication still decides.
URLs and host settings remain exact-provider configuration; this rule never
shares endpoints, settings, stored OAuth credentials, or an implicit login.
The `connection` policy has no ambient-store or environment fallback.

See `changes/2026-09-09-python-migration-ux.md`. Implementation rollout is
Python first; other languages are follow-up, not claimed aligned here.

Saved account/key/cloud connections are never inserted into an unmanaged
router's source chain. To use them, attach Auth explicitly or use the
interactive `connect()` helper. AUTH-15 specifies resolution, and AUTH-19/20
specify failure, replacement, logout and renewal.

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

### Named credentials and provenance (amended 2026-09-19)

(changes/2026-09-19-cloud-identity-and-endpoints.md D1, D2.) The three
clouds' own guidance differs on the default chain: Microsoft asks that a
library never build `DefaultAzureCredential` on the developer's behalf in
production and that the developer pick one deterministic credential
(managed identity when hosted on Azure); AWS endorses the chain but says
"specify the provider explicitly in production"; Google recommends ADC
and warns that on a laptop it picks the user. What all three object to
is not a chain existing but a chain being invisible. Hence one rule:
**an implementation never picks an identity silently — it either
receives a credential, or it says which one it picked.**

**Named credentials.** A router configuration may name one identity for
a cloud door instead of walking its chain: `credentials: {provider:
name}` with `name` ∈ {`platform`, `workload`, `environment`, `cli`} —
the same four words on every cloud. A bare adapter takes the same name
(`credential=`). The name selects the rungs below, in chain order, and
**nothing else is tried**: an absent named identity is
`NotConfiguredError` naming the name, what it means on this cloud, and
what was probed — never a fall-through to another rung. A name and an
explicit `api_keys` entry for one provider is refused at construction
(two answers to "who am I"); a name on a non-cloud door is refused; an
unknown name is refused before the first request.

| name | `azure-chain` | `aws-chain` | `gcp-chain` |
|---|---|---|---|
| `platform` | managed-identity | container, then imds | metadata |
| `workload` | workload-identity | web-identity | adc-env with `type: external_account` |
| `environment` | environment | `AWS_ACCESS_KEY_ID` + secret | adc-env with `type: service_account` (or `impersonated_service_account`) |
| `cli` | az, pwsh, azd | assume-role, sso, shared-credentials-file, login, credential_process, config-file | adc-file, gcloud |

Stated: `platform` on AWS covers two rungs (the container endpoint, then
IMDS) — both are the machine's own identity and boto3 tries them in
that order; the doctor and every error say which answered. On GCP,
`workload` and `environment` are one file rung told apart by the file's
`type`; the wrong type is refused by name (the message names the other
name), never read as the other. The door's own key variable (rung 1) is
never part of a named credential: a name means "not a key". The Azure
continuation rule (developer commands tried through errors) holds under
`cli`.

Trade-off, stated: the chain stays the default when nothing is
configured. Microsoft would prefer opt-in; AWS and Google endorse the
chain; provenance and named credentials remove the actual harm
(ambiguity), so the zero-configuration laptop path stays zero.

**Provenance.** A credential a cloud chain (or a named credential)
resolved carries where it came from: the rung's fixture kind, its human
label, the name that selected it if any, and its expiry if known — never
the value. Every auth error an adapter raises from the wire names the
source of the credential it sent, as one line under the provider's
message: the rung, the environment variable, "an explicit api_key", the
stored login, or "an application-supplied callable (identity not
inspected)". The implementation is honest about the last: a caller's
callable is not introspected. Provenance is appended once and survives
the re-login hint. The doctor (AUTH-7) says the same before any request.

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
- (amended 2026-09-19, changes/2026-09-19-cloud-identity-and-endpoints.md
  D3) A plain string that is a JWS compact JWT (three base64url segments,
  the first decoding to a JSON object with `alg`) is an Entra/OAuth
  access token that a token-provider callable handed over as a string
  (`azure.identity.get_bearer_token_provider` returns `str`), never an
  API key: no door lm15 has issues a JWT-shaped key, and sent in a key
  header it is a bare 401 (live 2026-09-04). When the `ApiKey` scheme
  selected above is `api-key` or `x-api-key` and the policy also lists
  `bearer`, such a string travels as `bearer`. Before this date the
  reference refused it and named the `BearerToken` wrap; the wrap stays
  accepted and is the form when nothing should be read from a token's
  shape. Stated trade-off: a decision from appearance, made only where
  the alternative is a certain 401; the doctor reports "sent as bearer
  (JWT)".

Cost, stated: a token given to a key-header-only door that does not take
tokens (first-party `anthropic`) gets the provider's 401, not a local
error. A harness wire pin lands with the first Bedrock Claude HTTP 200
(account-gated today; stated, not absorbed).

A provider returns one of these. An explicit `api_keys` entry may be a
plain string (read as `ApiKey`), one of these values, or a provider.
Python/TS/Julia: a tagged value; Go/Rust: an interface/enum with the same
kind names. `expires_at` is RFC 3339; absent means non-expiring.

## AUTH-3 — Refresh state machine

For managed account credentials, [AUTH-20](auth-managed.md#auth-20--renewal-and-request-authentication)
defines actual expiry, bounded skew for short-lived tokens, double-checked
serialized renewal, durable in-flight markers, and conservative recovery after
possibly rotating exchanges. A failed selected credential never selects another
identity. A network outage is not automatically an invalid login.

Existing cloud-chain credential acquisition/caching remains unchanged: the
five-minute renewal window and provider-specific rules apply, and the cache is
keyed by provider plus identity-selecting settings (AWS profile/role; Azure
tenant/client/resource; GCP project/credential source). Managed saved cloud
recipes invoke those same chains explicitly. AUTH-20 does not change the
meaning or caching responsibility of application-supplied AUTH-2 callbacks.

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
- Stated limitation: locks coordinate only cooperating processes/backends;
  re-reading is not a cure for a foreign tool rotating the same credential.
  Managed auth does not borrow foreign CLI logins. AUTH-25 additionally requires
  atomic attempt/connection commits, scope isolation, identity generations and
  interrupted-exchange detection; plain per-value get/set is insufficient.

## AUTH-5 — Secrecy invariant

AUTH-21 in [auth-managed.md](auth-managed.md) extends this boundary to private
attempts, device codes, PKCE material, callback/session-sensitive URLs, typed UI,
relay consent and auth HTTP diagnostics. Private store encoding is not public
status serialization. Applications' own trusted secret callbacks are not sandboxed.

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

- For existing unmanaged key/cloud sources, missing/unreadable/malformed
  sources retain `NotConfiguredError`, `provider` and the actual configuration
  hint (`export GROQ_API_KEY=...`, select/configure the named cloud identity).
  Managed lifecycle failures use AUTH-24 `AuthOperationError` with a typed reason,
  commit state and recovery action; these are not fabricated provider HTTP errors.
- Existing unmanaged credential acquisition and model-request provider rejection
  retain their `AuthError` behavior and selected-source hints. Managed login and
  renewal lifecycle failures instead follow AUTH-24's specific reasons; they are
  not blanket-labelled 401 or automatically retryable.
- Lock contention → `LockTimeoutError` (ErrorCode `lock_timeout`,
  spec/vocabularies.md; named 2026-09-08), a root-level, retryable class
  deliberately **not** an `AuthError`: nothing is wrong with the
  credential. It carries `path` and `lock_path`. A language with a native
  timeout type may additionally subtype it (the reference's
  `CredentialLockTimeout` is both), never instead.

## AUTH-7 — Explainability (doctor)

Every implementation ships an `explain_auth` equivalent. With managed Auth it
walks AUTH-15, reports the selected scope/binding and any explicit overrides,
never resolves/refreshes credentials, and distinguishes absent storage from a
storage failure. `auth.status()` describes saved state; router diagnostics
describe the actual request selection. See AUTH-17/24 for network-free status
and explicit verification. Without managed Auth it retains the existing walk:

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
- (amended 2026-09-19) under a named credential walks exactly the rungs
  the name covers (rung 0 `api_keys` then those rungs; nothing else is a
  step, because nothing else runs) and says the chain is not walked;
  prints the base URL the door will send to and where it came from (the
  explicit entry, the vendor's endpoint variable by name, or the
  template) — `auth/named-credentials.json` pins these walks the way
  `auth/resolution.json` pins the chains; for a caller-supplied callable
  it reports the callable and that the underlying identity is not
  inspected;
- never includes secret values in its output. Presence checks may read
  values into memory; they must not retain or render them.

## AUTH-8 — Well-known paths

- lm15-owned credential store: `$LM15_CREDENTIALS_PATH`, else
  `$XDG_CONFIG_HOME/lm15/credentials.json`, else
  `~/.config/lm15/credentials.json`.
- Lock directory: `$LM15_LOCK_DIR`, else `$XDG_CACHE_HOME/lm15/locks`, else
  `~/.cache/lm15/locks`.
- Managed login does not read/write `~/.claude/.credentials.json`,
  `~/.codex/auth.json` or `~/.pi/agent/auth.json`. No auto-import, migration,
  dual-format writer or compatibility flow is required. Explicit external
  credential providers remain an application choice under AUTH-2.
- Borrowed cloud files (amended 2026-09-03): `~/.aws/credentials`,
  `~/.aws/config` (`AWS_SHARED_CREDENTIALS_FILE`, `AWS_CONFIG_FILE`),
  `~/.aws/sso/cache/*.json`, `~/.aws/login/cache/*.json`,
  `$CLOUDSDK_CONFIG|~/.config/gcloud/application_default_credentials.json`.
  Same rule: foreign formats, revalidated, never cleaned. lm15 never
  writes to them; refreshed cloud tokens live in memory (AUTH-3 cache),
  never in a foreign file.
- The managed store has its own versioned format (AUTH-25), not the former
  xAI/Pi entry shape. Unknown existing formats are refused without overwriting
  them; a caller deliberately chooses a supported store. These paths are
  consulted only by explicit local-store construction/operations, not by an
  otherwise unconfigured router.

## AUTH-9 — SDK-owned login, application-owned presentation

**Replaced by the 2026-09-22 review draft.** Every implementation exposes the
same managed operations defined in [AUTH-12–26](auth-managed.md): discovery,
login, begin/resume/cancel, key/recipe setup, status, verification, renewal,
logout and model-bound connection. Login returns secret-free Connection metadata;
ordinary inference never starts login. There is no xAI-only restriction or
requirement to install another provider's CLI.

The core requires explicit UI where a choice is needed. An optional interactive
`connect()` selects/reuses an account and model and returns a bound client. Both
connected login and resumable website login drive the same state machine.

AUTH-18 specifies S256 PKCE, state/issuer/redirect binding, device polling,
loopback-only native callbacks, supported manual returns and website session
ownership. Wrong-state error callbacks cannot terminate a legitimate attempt.
AUTH-19 defines cancellation/commit races; AUTH-20 defines uncertain exchange
outcomes; AUTH-21 defines secrets and relay consent. No implementation may reduce
these requirements to a provider-specific happy-path helper.

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
| `login_hint` | re-login/configuration guidance | names the selected managed login or explicit key/cloud source; never redirects a managed failure to ambient billing |
| `backend` | dialect-consulted variant (`api` is the public API) | a small stated set of branches inside the dialect |
| `backend_options` | string knobs the variant needs | those branches |
| `system_prefix` | text the backend requires first in system/instructions | payload |
| `base_url` | this access path's default base URL | construction, when the caller left the dialect default |
| `host` (amended 2026-09-03, 2026-09-19) | a host descriptor: URL template over the settings below (a root and a door path), `endpoint_env` (the vendor's endpoint variables, in order), `model_in` (`body`\|`path`), `anthropic_version_in` (`header`\|`body:<value>`), `stream_framing` (`sse`\|`aws-event-stream`), `required_headers` (`name: {setting}`), `sigv4_service` | URL build, payload, stream decoder |
| `settings` (amended 2026-09-03; the typed face of `backend_options`) | `region`, `workspace`, `project`, `location`, `resource`, `authority_host`, `scope`; each with its env fallbacks in order | construction; the doctor prints them |

Host settings and their env fallbacks (in order): `region` ←
`AWS_REGION`, `AWS_DEFAULT_REGION`, profile `region` — **no default,
raise**; `workspace` ← `ANTHROPIC_AWS_WORKSPACE_ID` — no default;
`project` ← `GOOGLE_CLOUD_PROJECT`, `GCLOUD_PROJECT`, the ADC file's
`quota_project_id`/`project_id` — no default; `location` ←
`GOOGLE_CLOUD_LOCATION` — default `global` (stated trade-off:
availability first; the doctor prints it); `resource` ←
`AZURE_OPENAI_RESOURCE` (`azure`, `azure-chat`), `ANTHROPIC_FOUNDRY_RESOURCE`
(`azure-anthropic`) — no default, and not required when an endpoint (below)
is given; `authority_host` ← `AZURE_AUTHORITY_HOST`, default
`https://login.microsoftonline.com`; `scope` default
`https://ai.azure.com/.default` on every Azure door (the classic
`https://cognitiveservices.azure.com/.default` is also accepted by the
resource; a caller sets it through the setting). Settings are never part
of the model string: `Request.model` stays `provider:model`.

**Endpoint override (amended 2026-09-19,
changes/2026-09-19-cloud-identity-and-endpoints.md D4).** A host's
`base_url` template is a *root* (scheme and host, before the first path
segment) and a *door path* (`/openai/v1`, `/anthropic/v1`,
`/v1/projects/{project}/locations/{location}/publishers/google`). A caller
may hand a door the whole root instead — a router `base_urls` entry, an
adapter `base_url=`, or, read by the router after the explicit entry and
before the template, the vendor's own variable named in `HostSpec.endpoint_env`:
`AZURE_OPENAI_ENDPOINT` (`azure`, `azure-chat`; the OpenAI SDK's
`AzureOpenAI` reads it), `ANTHROPIC_FOUNDRY_BASE_URL` (`azure-anthropic`;
anthropic-on-foundry.md:180-182), `AWS_ENDPOINT_URL_<SERVICE_ID>` then
`AWS_ENDPOINT_URL` (`bedrock-chat` → `BEDROCK_RUNTIME`; `bedrock-anthropic`
and `bedrock-mantle-chat` → `BEDROCK_MANTLE`; `aws-anthropic` →
`AWS_EXTERNAL_ANTHROPIC` — the SDK's rule, service id upper-cased with
`-` → `_`; aws-sdkref-endpoints.md names the rule, not these ids); Vertex
has no vendor variable this corpus can cite and takes the explicit entry
only. Rules:

- The endpoint replaces the root. The door path (rendered over the
  settings) is appended unless the endpoint already ends with it, or
  with a leading part of it: `https://acct.services.ai.azure.com`,
  `…/openai/v1` and Microsoft's `…/anthropic` all name one door. Stated
  trade-off: a gateway whose own path ends with a leading part of a door
  path cannot be spelled; none is known.
- The endpoint is `http(s)` with a host, without query, fragment or
  userinfo; a trailing slash is dropped. It is trusted configuration: it
  decides where credentials and data go, and is never derived from
  untrusted input.
- With an endpoint, the settings that appear only in the root of the
  template are not required (`resource`); settings in the door path
  (`project`, `location`) and the SigV4 signing `region` still are (the
  AWS SDK requires a region with `endpoint_url` too: the credential
  scope names it).
- The door's auth scheme, backend branches, error mapping, required
  headers and doctor stay attached: an endpoint changes the URL and
  nothing else. Before this amendment the reference refused a
  `base_urls` entry on a cloud door, and the only way to reach a Foundry
  root was to leave the `azure` door for `openai` + `base_urls`, which
  silently lost all of the above (reported by Pamela Fox, lm15-python
  issue #10, 2026-09-18).

**Default Azure host (D5, decided against the in-session plan with
evidence).** The `azure`/`azure-chat` template stays
`https://{resource}.openai.azure.com/openai/v1`. The Foundry console
shows `https://{account}.services.ai.azure.com`, which serves OpenAI and
non-OpenAI deployments alike and was proposed as the new default; but a
classic `OpenAI`-kind resource has no `services.ai.azure.com` name at all
(DNS 2026-09-19: the lab's `lm15-oai-*` resource resolves on
`openai.azure.com` only, NXDOMAIN on the other two; the lab's Foundry
`lm15-fdy-*` resource resolves on all three), so the alias is the only
host every resource kind answers on, and it saves one internal hop for
OpenAI models today. The Foundry root is one variable away
(`AZURE_OPENAI_ENDPOINT`), and the docs say to paste it whenever the
console shows one.

The policies (reference: `lm15/access.py`):

| Policy | Dialect | credential | auth_header | backend | Notable fields |
|---|---|---|---|---|---|
| `anthropic` | Anthropic | key | `x-api-key` | api | files, batches, models |
| `claude-code` | Anthropic | connection | bearer | claude-code | betas `claude-code-20250219,oauth-2025-04-20`; `x-app: cli`; `user-agent: claude-cli/<v>`; `anthropic-dangerous-direct-browser-access: true`; system prefix "You are Claude Code, Anthropic's official CLI for Claude."; no files/batch/live |
| `openai` | Responses | key | bearer | api | full surface |
| `openai-codex` | Responses | connection | bearer | chatgpt-codex | base `https://chatgpt.com/backend-api/codex`; `OpenAI-Beta: responses=experimental`; `originator`; `client_version` option; instructions prefix "You are a helpful assistant."; complete/stream/models only |
| `openai_chat` | Chat | key | bearer | api | complete, stream, models |
| `xai` | Chat (+ provider adapter) | key (unmanaged); explicit managed binding otherwise | bearer | api | base `https://api.x.ai/v1`; images, video, models |
| `gemini` | Gemini | key | `x-goog-api-key` | api | full surface incl. caches |
| `azure` / `azure-chat` | Responses / Chat | azure-chain | `api-key`, `bearer` | azure-openai | `https://{resource}.openai.azure.com/openai/v1`, or `AZURE_OPENAI_ENDPOINT` + `/openai/v1` (the Foundry root, amended 2026-09-19); model = deployment name; data-plane `/models` lists the resource catalog (live, contrary to docs); `azure` also carries Files, Batch, speech and Realtime |
| `azure-anthropic` | Anthropic | azure-chain | `x-api-key`, `bearer` | azure-foundry | `https://{resource}.services.ai.azure.com/anthropic/v1`, or `ANTHROPIC_FOUNDRY_BASE_URL` + `/anthropic/v1`; docs also claim `api-key`, but live it is 401 while `x-api-key` reaches deployment lookup; no batches/models/`fallbacks`; successful inference quota-blocked |
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

Managed authentication is composed through a scoped manager and an explicit
credential binding (AUTH-12/15/20), including account-dependent destinations and
headers. No per-language provider-name switch invents a parallel login registry.
Platform I/O stays per-language; meanings and state transitions do not. A
subscription adapter class, where retained for ergonomics, binds access policy
and authentication services rather than reimplementing a wire dialect.

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

Amended 2026-09-19 (AUTH-1 named credentials `platform`/`workload`/
`environment`/`cli` and provenance on every auth error; AUTH-2 a JWT
string travels as bearer; AUTH-7 named mode and the base URL; AUTH-10
endpoint override with the vendor's variables, `HostSpec.endpoint_env`,
`resource` optional with an endpoint, Azure default host kept with DNS
evidence) — ratified in session ("Yes, this is perfect. Go and implement
it completely"), one decision (D5, the Azure default host) revised by the
implementer with evidence and stated for assent; independent live
receipt for `azure-anthropic` by Pamela Fox (Microsoft), 2026-09-18,
`pamelafox/python-stack-foundry-models`; see
changes/2026-09-19-cloud-identity-and-endpoints.md and
auth/named-credentials.json.
