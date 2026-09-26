# 2026-09-26 — Google Cloud identities on `vertex` / `vertex-express`, live-verified

Status: DRAFT (evidence only: no case, body, golden or rule changes).
Two proposed rule changes at the end need ratification before any port
copies them.

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

## Proposed, needs ratification

1. **AUTH-10 project fallbacks.** After `GOOGLE_CLOUD_PROJECT` /
   `GCLOUD_PROJECT` and the credential file, read gcloud's active
   configuration (`CLOUDSDK_CORE_PROJECT`, then
   `$CLOUDSDK_CONFIG/configurations/config_<active>` `[core] project`) and,
   on the `metadata` rung, `computeMetadata/v1/project/project-id`.
   google-auth reads both; without them `credentials={"vertex":
   "platform"}` on Cloud Run fails with "project not set" unless the app
   sets the variable by hand. Cost: the metadata read is a network call at
   settings time (the doctor reports it `unprobed`).
2. **API keys on the `vertex` door.** Google accepts a Vertex API key in
   `x-goog-api-key` on the project-scoped global and regional URLs (curl,
   200). Adding it as a second scheme gives key users residency control,
   but a plain string would then be ambiguous between a key and an
   access token (`ya29.`) unless AUTH-2 reads Google's key shape (`AIza`).
   Today the string is sent as a bearer token and Google answers 401.
