# 2026-09-04 — Bedrock short-term keys: the bearer rung live, and an AUTH-2 fix it exposed

Status: RATIFIED 2026-09-06 (AUTH-2 rule text as written in spec/auth.md; verify/DECISIONS-2026-09-06.md D1, changes/2026-09-06-ratification.md).
Closes the bearer cells left open in
`changes/2026-09-03-bedrock-chat-live.md`; touches AUTH-2 (one table
cell) and the harness protocol (one rule).

## What was found offline, before any call

With `AWS_BEARER_TOKEN_BEDROCK` in the environment, `bedrock-anthropic`
and `aws-anthropic` raised `NotConfiguredError` ("a bearer_token
credential cannot travel under sigv4/x-api-key") — and the hint said to
set the very variable that was set.  Cause: the aws-chain's env rung
yields a `BearerToken` (AUTH-1 rung 1, ratified 2026-09-03), and the
AUTH-2 table let a `BearerToken` travel under `bearer` only; those two
doors carry their keys as `x-api-key` (anthropic-on-bedrock.md:68, :322).
The chain and the scheme table disagreed about the chain's own product.

## The decision (AUTH-2, amended)

A `BearerToken` travels under `bearer` where the door offers it, else
under `x-api-key`.  The token's own preference decides, not the policy
order: on `azure-anthropic` (`api-key`, `x-api-key`, `bearer`) an Entra
token must still go as `bearer`, and it does (test).  An `ApiKey` is
unchanged (policy order picks among `bearer`/`x-api-key`/`api-key`/
`query-key`); `AwsCredentials` is unchanged (`sigv4`).

WHY not the other fixes: making the env rung yield `ApiKey` for the
mantle door and `BearerToken` for the chat door would give one variable
two kinds by door — the kind says what the credential *is* (a 12-hour
token), not which header carries it.  Reordering `azure-anthropic` to
put `bearer` before `x-api-key` would work today and silently break the
first future door that lists them the other way.

Trade-off, stated: a `BearerToken` handed to a key-header-only door that
does not accept tokens there (first-party `anthropic`: `x-api-key` only)
no longer fails locally; the provider answers 401.  The local error was
correct for that door and wrong for Bedrock; the header cannot tell
them apart, and the door's own 401 is honest.

## Live cells (`us-east-1`, receipts `receipts/2026-09-04-bedrock-chat/probe-bearer-*.json`, `…-bedrock-anthropic/probe-bearer-*.json`)

The key was minted from the profile's IAM keys by
`research/providers/_aws_bearer.py` — the algorithm of AWS's
`aws-bedrock-token-generator` 1.1.0 (a SigV4 query presign of
`POST https://bedrock.amazonaws.com/?Action=CallWithBearerToken`,
service `bedrock`, 43200 s; then `bedrock-api-key-` + base64), reproduced
byte for byte against the official generator at a fixed clock with the
AWS test pair (two vectors in the script, `--selftest`).  Written to
`~/.config/lm15/aws-bearer.env` (mode 600), read by the probe through
lm15's own chain (`env:AWS_BEARER_TOKEN_BEDROCK` selected), never pasted
or printed.

| cell | door | scheme | HTTP | closes |
|---|---|---|---|---|
| `Say ok.` (gpt-oss-20b) | `bedrock-chat` | `Authorization: Bearer` | **200** | the bearer rung, live |
| `GET /openai/v1/models` | `bedrock-chat` | bearer | 404 `<UnknownOperationException/>` | `supports.models` stays false; the docs' listing claim does not hold under either scheme |
| Haiku 4.5, Sonnet 5, Opus 4.7 | `bedrock-anthropic` | `x-api-key` | 403 `permission_error` "not available for this account" | the gate is on the account, not on the auth scheme |

## Artifacts

- `cases/bedrock-chat/bearer_basic_text.json` (+ body, + scribe-draft
  golden): pins `credential: {"kind":"bearer_token","value":"bedrock-api-key-FIXTURE"}`
  and `authorization: Bearer bedrock-api-key-FIXTURE`.
- `harness/PROTOCOL.md`: when a case pins a string-kind credential, the
  harness sends it and compares the auth header byte for byte (no rewrite
  to the injected `api_key`), the rule SigV4 cases already follow.
  Without this the case could not see which header a port chose.
  `harness/selftest.py`: new mutation `pinned_credential_scheme_drift`
  (the token sent as `x-api-key`) — caught.
- `errors/cases/bedrock-anthropic.json`: `model_gated` (403
  `permission_error`, verbatim) → `AuthError`, the dialect's existing
  `permission_error` mapping.  Removed `bad_max_tokens`: its body was the
  gate, not a parameter error (the gate fires before validation); the
  probe stays and folds in once Claude is open.
- `tools/check_secrecy.py`: `bedrock api key` shape (base64 of the
  presigned URL), first capture; the test-pair vectors are excluded by
  their fixed base64 spelling, a real key id is caught (checked).
- `spec/auth.md` AUTH-2 table + amendment footer.

## Not done, stated

- The `BearerToken → x-api-key` rule has no harness case: the only doors
  that need it are Claude doors this account cannot call (403).  It is
  pinned by the spec table and `tests/test_cloud_hosts.py::
  TestBearerTokenInKeyHeader`; the harness pin lands with the first
  mantle 200.
- lm15 does not mint short-term keys.  With AWS credentials it signs
  directly; minting is a login primitive for bearer-only tools and stays
  a research script until a use inside lm15 exists.
- Harness at HEAD: request 277 / response 223 / stream 38 / error 76 /
  auth 37 / token 19 — 0 failures; selftest 28/28; all four checkers OK.
