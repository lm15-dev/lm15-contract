# 2026-09-26 — Google Cloud identities on `vertex` / `vertex-express`, live-verified; the project from Google's own places; API keys on `vertex`

Status: D1 and D2 **RATIFIED in session 2026-09-26** — Maxime Rivest:
"Yes, LM15 should copy them. It should find a project. Yes, LM15 should
support API keys on the regular vertex door." Wire facts are live
receipts (`receipts/2026-09-26-vertex/`, `receipts/2026-09-26-vertex-express/`);
goldens are scribe drafts (AUTHORITY.md), not frozen.

Contract changes: spec/auth.md AUTH-2 (token shapes), AUTH-7 (settings
origin), AUTH-8 (gcloud configuration paths), AUTH-10 (project sources,
the `from` vocabulary, the `vertex` and `vertex-anthropic` rows);
spec/support-matrix.json (`vertex` auth modes); harness/PROTOCOL.md
(`explain_auth` reply `settings`); auth/resolution.json (13 cases);
cases/vertex (12), cases/vertex-express (2), errors/cases/vertex.json (3),
their bodies and draft goldens; research/providers/vertex/capture.py,
research/providers/vertex-express/capture.py; three frozen sources under
research/cloud-hosts/sources/ (`gcp-google-auth-cloud-sdk-py.md`,
`gcp-gcloud-configurations.md`, `gcp-gcloud-named-configs-py.md`).

## What this proves

The `gcp-chain` (AUTH-1) and AUTH-10 settings against a real project,
`lm15-vertex-live` (created for this run, billing on, APIs
`aiplatform`, `iamcredentials`, `sts`, `apikeys`, `compute`). Every row
answered a `gemini-2.5-flash` `generateContent` with HTTP 200 through
lm15-python's own resolver (the credential code of lm15 1.0.1; the VM row
ran the published wheel). No token or key was printed; test credentials
lived in `~/.config/lm15-live/` (mode 700, outside every repo).

| AUTH-1 rung / name | Setup | Result |
|---|---|---|
| `adc-file`, `authorized_user` | `gcloud auth login --update-adc` | 200; one refresh per router, reused across calls |
| `gcloud` | ADC file absent, gcloud on PATH | 200 |
| `adc-env`, `service_account` (`"environment"`) | JSON key via `GOOGLE_APPLICATION_CREDENTIALS` | 200; RS256 assertion from the stdlib signer accepted by `oauth2.googleapis.com`; project from `project_id` |
| `adc-env`, `impersonated_service_account` | source = the ADC `authorized_user`, target granted `serviceAccountTokenCreator` | 200 |
| `adc-env`, `external_account` (`"workload"`) | OIDC pool provider with an uploaded JWKS; file source; direct principal access and `service_account_impersonation_url` | 200 both; STS exchange and generateAccessToken accepted |
| `metadata` (`"platform"`) | e2-micro VM, attached service account, `cloud-platform` scope | 200 via the default chain and via the name |
| explicit bearer | `gcloud auth print-access-token` as a string | 200 |
| `vertex-express` query key | Vertex-restricted API key bound to a service account | 200 complete and stream |

Named-credential refusals held live: `"workload"` on a `service_account`
file and `"environment"` on an `external_account` file were refused by
name; `"platform"` off Google Cloud answered nothing and did not fall
through. Locations `global`, `us-central1`, `europe-west4` served; `us`
and `eu` routed to `aiplatform.{loc}.rep.googleapis.com` and Google
answered "model not found" for `gemini-2.5-flash` (a model-availability
fact, not a host fact). `vertex-anthropic` authenticated and routed; a new
project's Claude quota is 0 (HTTP 429), so no Claude 200 exists yet.

Observed provider behaviour worth pinning in docs: a project, role or
service account created minutes earlier answers 403
`IAM_PERMISSION_DENIED` until IAM propagates (1–5 minutes here).

## Diagnostics (implementation-side, within AUTH-5/AUTH-21)

lm15-python now attaches the action that fixes each Google failure (stale
ADC login → `gcloud auth application-default login`; impersonation →
`roles/iam.serviceAccountTokenCreator`; STS → issuer/audience/condition;
wire 403 → `roles/aiplatform.user` and propagation; wire 401 → not an
OAuth token, keys go to `vertex-express`; nothing found → the commands).
From a failed exchange it shows only the status and a fixed-vocabulary
OAuth word, as AUTH-21 allows; service-account emails are not printed.
Ports (TS, Rust, Go, Julia, R) still carry the old "HTTP 400" + API-key
text and should follow; no fixture pins the wording.

## D1 — the project from Google's own places (AUTH-10)

Before: `GOOGLE_CLOUD_PROJECT`, `GCLOUD_PROJECT`, then the ADC file's
`quota_project_id`/`project_id`. `gcloud config set project` was ignored,
and `credentials={"vertex": "platform"}` on Cloud Run failed with
"project not set" unless the application exported the variable by hand.
google-auth reads gcloud's configuration and the metadata server; so does
lm15 now, in the order AUTH-10 lists (credential file, gcloud
configuration, ADC file, metadata server).

- gcloud's configuration is read from its files, not by running
  `gcloud config get project` as google-auth does: offline, no subprocess
  at construction, and the doctor can report it. The layout is gcloud's
  own code (gcloud 581.0.0, frozen excerpt).
- The ADC file's `quota_project_id` moved after gcloud's configuration:
  google-auth takes no project from an `authorized_user` file, and
  `gcloud auth application-default login` copies the then-current
  project into it, so a later `gcloud config set project` would otherwise
  lose to a stale copy. Cost, stated: a user whose quota project and
  gcloud project differ now gets the gcloud project, as google-auth does.
- The metadata server is asked only when every other source is empty,
  that is, only where the alternative was a configuration error. Cost,
  stated: off Google Cloud, that error now arrives after at most the
  1-second metadata timeout (plus name resolution), unless `NO_GCE_CHECK`
  is set. Python and Go ask at construction; TypeScript and Rust, whose
  construction is synchronous and I/O is not, ask once before the first
  request (AUTH-10 allows either).

## D2 — API keys on the `vertex` door (AUTH-2, AUTH-10)

Google accepts a Vertex API key in `x-goog-api-key` on the project-scoped
global and regional hosts (curl and lm15, 2026-09-26: generateContent,
streamGenerateContent, countTokens; `europe-west4`). The `vertex` policy
lists `x-api-key` (the Gemini dialect's `x-goog-api-key`) first, then
`bearer`: a plain string is a key, unless it has a token's shape — the
JWT rule of 2026-09-19 plus Google's `ya29.` prefix. The key this run
created begins `AQ.` (bound to a service account), not the older `AIza`:
recognising keys by prefix would already be wrong, recognising tokens is
not. Every token lm15's Google chain produces is a `BearerToken` value and
unaffected.

- No env key on `vertex`: `GOOGLE_API_KEY` is the Gemini API's and
  `vertex-express`'s variable, commonly set, and reading it here would
  silently replace the ADC identity and its billing.
- `vertex-anthropic` keeps bearer only: rawPredict answered 401 "API
  keys are not supported by this API" to the same key.
- Cost, stated: before this date every plain string on `vertex` went as
  bearer. A token of another shape given as a plain string now goes as a
  key; the 401 guidance names `BearerToken(value)`.

## Recorded cases

`cases/vertex/`: `basic_text`, `streaming`, `system_prompt`, `tools`,
`streaming_tool_call`, `multi_turn_tool_result`, `response_format_json_schema`,
`reasoning_low`, `regional_location` (europe-west4 host and path) and
`access_token_string` (a `ya29.` plain string → `Authorization: Bearer`),
each sent with a token from lm15's gcp-chain and pinned with
`credential: {"kind": "bearer_token", "value": "test-access-token-123"}`
(or the `ya29.` string); `api_key_basic_text`, `api_key_streaming` sent
with the Vertex key and pinned as `x-goog-api-key: $VERTEX_API_KEY` (the
harness injects its own key). `cases/vertex-express/`: `basic_text`,
`streaming` (`?key=`). `errors/cases/vertex.json`: an expired/invalid
token (401 → AuthError), an unknown model (404 → UnsupportedModelError),
a project without access (403 → AuthError).

## Ports (2026-09-26)

TypeScript (`b962fde`), Go (`6ab1ca0`) and Rust (`fab039c`) implement D1,
D2, the settings origin and the Google diagnostics. Graded against this
contract with `--no-check-pin`: every `vertex`, `vertex-express` and
auth-resolution case passes in all three; their only failures are the
four open-model hosts of `changes/2026-09-26-inference-hosts-live.md`
(and the managed `discovery` list that includes them), which no port
carries yet. Their `CONTRACT_PIN` stays at `3763eec` until those hosts
are ported; moving it earlier would pin a contract the ports fail.
Rust carries the OAuth word in the message only (`AuthError::Rejected`
has no code field; a public enum change was not worth it for this).

Live, per language, through lm15's own chain against `lm15-vertex-live`
(the same 13 setups in each: gcloud login with the project from gcloud's
configuration, the gcloud rung alone, a service-account key, `"environment"`,
an impersonated service account, workload identity federation direct and
through a service account, a plain access-token string, a Vertex API key
on `vertex` (complete, stream, europe-west4) and on `vertex-express`), all
200 in Python, TypeScript, Go and Rust. The three refusals (a revoked ADC
login, nothing configured, no project off Google Cloud) name their fix in
all four. On an Ubuntu 24.04 VM with an attached service account and no
project anywhere (no variable, no gcloud configuration), each of the four
resolved the project from the metadata server and answered through the
default chain, the named `"platform"` identity, and a stream (12/12).

