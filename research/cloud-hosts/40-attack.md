# Cloud hosts — attack pass

**Labelled: self-review by the same agent that wrote `30-model.md`, in
the same session. No second agent was available. A self-review is weaker
(playbook step 7); the maintainer should read this as "what the author
could see", not as independent verification.**

Each scenario names the lens, the concrete situation, the outcome under
the model, and whether the model changed because of it.

## Lens: security reviewer

**S1. Wrong identity.** Machine has `AWS_ACCESS_KEY_ID` (a dev key) and a
profile with `role_arn` for production. boto3 picks env first (rung 2 of
§3.1). lm15 picks env first. Same principal in CloudTrail. ✔ No change.

**S2. Silent fallback.** `AZURE_CLIENT_CERTIFICATE_PATH` set but the file
is unreadable. azure-identity: EnvironmentCredential is a "deployed"
credential; a failed attempt **stops** the chain
(azure-identity-readme.md:48-50). Under the model, rung 2 failing raises
`AuthError`; it does not fall through to `az`. ✔ Copied. Without this
rule a broken cert would silently use the developer's `az` login — the
exact bug the frame forbids.

**S3. Private key leaves the machine.** The service-account and
certificate rungs send a *signed JWT*, never the key. The reference must
never log the assertion either: the JWT is a bearer-equivalent for its
lifetime. Add to AUTH-5: assertions and STS/exchange bodies are secret
material. → **Model changed**: §5.6 secrecy patterns include `eyJ` JWTs.

**S4. Fixed test key in the corpus.** A real-looking RSA private key
sits in the repo. `check_secrecy.py` will flag it. Resolution: the key
lives at one allow-listed path, has a comment header naming it
test-only, and the scanner allow-lists that path only. Trade-off stated
in the `changes/` entry.

**S5. SSRF via metadata endpoints.** `GCE_METADATA_HOST`,
`AWS_CONTAINER_CREDENTIALS_FULL_URI`, `IDENTITY_ENDPOINT` are
attacker-controllable only if the environment is. Same as the SDKs.
The container rung must validate `FULL_URI` the way botocore does:
`_ALLOWED_HOSTS` = `169.254.170.2`, `169.254.170.23`, `fd00:ec2::23`,
plus loopback; anything else raises "Unsupported host … Can only
retrieve metadata from a loopback address or one of these hosts"
(aws-botocore-utils-py.md:3072-3122). → **Model changed**: rung
parameters carry that allow-list.

**S6. Doctor output leaks.** `explain_auth` prints which file won. It
must print paths and env var *names*, never values. Existing AUTH-5 and
the sentinel test cover this; the new `files` input plants the sentinel
in every file. ✔

## Lens: cold learner

**C1.** "I set `AWS_REGION` and my keys and called
`bedrock-anthropic:anthropic.claude-opus-5`. It says the model needs an
inference profile." That is the legacy `bedrock-runtime` message
(anthropic-on-bedrock-legacy.md:136), not the mantle door. Under the
model `bedrock-anthropic` is the mantle door where ids are
`anthropic.claude-opus-5` (anthropic-on-bedrock.md:327-338). The error
cannot occur there. But if the user meant Opus 4.6 or earlier, mantle
does not serve it (title: "Opus 4.7 and later"). → **Finding**: the
hint for a 404 on mantle must say "older Claude models are on the
legacy Bedrock door (`bedrock:` Converse, phase 2)". Recorded as a
live cell: what does mantle answer for `anthropic.claude-sonnet-4-5`?

**C2.** "Which Vertex? `vertex:` wants a project. I have an API key."
The router hint names `vertex-express:`. The doctor for `vertex` shows
`env:GOOGLE_API_KEY` as `absent` with a note "express keys route
through vertex-express". ✔ Stated trade-off in §8.

**C3.** "`azure:gpt-4.1` 404s." Azure wants the *deployment* name
(azure-openai-managed-identity.md:246). The 404 hint says so. ✔

## Lens: library author on top

**L1.** A gateway wants to hand a short-lived token to a worker. AWS
publishes token generators that read the chain and return a 12-hour
`x-api-key` token (anthropic-platform-on-aws.md:206-210; bedrock short-term
keys). Under the model, that token is an `ApiKey` from a
`CredentialProvider`; the worker's process has no AWS chain. ✔ The
generator algorithm itself is not scraped (GitHub READMEs) — out of
scope, stated; users bring the token.

**L2.** Multi-tenant SaaS wants one `Router` per tenant with different
cloud identities. Settings live in `backend_options` per LM instance, and
credentials per `api_keys` entry; nothing is process-global except env
fallbacks. ✔ But **token caches** (AUTH-3) are keyed by provider id
today. Two tenants on `azure` would share a cache. → **Model changed**:
cache key = provider id + a hash of the settings that select identity
(tenant, client id, resource / profile / project + credential source).
Add to the entry.

## Lens: port implementer (Go)

**P1.** Go SDK v2 has no `login` rung (aws-sdkref-login-credentials.md:24).
Does the Go port implement lm15's `aws-chain` rung 7 anyway? Yes: the
chain is lm15's, pinned by fixtures; the Go port reads the same cache
file. The harness `explain_auth` case with a materialized
`~/.aws/login/cache` file proves it. ✔

**P2.** Ten rung kinds, five schemes: is anything not expressible in Go
stdlib? SigV4 (crypto/hmac, sha256), RS256 (crypto/rsa, x509 PKCS#8),
INI parsing (hand-rolled, ~60 lines), subprocess, HTTP: all stdlib. Rust
needs `rsa` + `sha2` crates (already a stated Rust deviation). TS/Node:
`crypto.sign('RSA-SHA256')`, stdlib. Julia: `MbedTLS`/`OpenSSL_jll` —
Julia already links OpenSSL through stdlib `LibCURL`; state it in the
Julia README. ✔

**P3.** PKCS#12 dropped everywhere. Consistent across the family. ✔

## Lens: cost accountant

**A1.** Regional Bedrock endpoints carry a 10% premium; multi-region and
regional Vertex too; Claude Platform on AWS US geo is 1.1×
(anthropic-on-bedrock.md:374; anthropic-on-vertex.md:401-409;
anthropic-platform-on-aws.md:572-575). None of this is visible in
`Usage`. The model does not add a price field (out of scope for this
pass) but the doctor prints the resolved region/location/geo so the
accountant can see what was chosen. ✔ Stated.

**A2.** Each chain probe that hits the network (IMDS, MSI, metadata)
costs latency on every cold start, not money. Same as the SDKs. The
`unprobed` doctor state avoids paying it in the doctor. ✔

## Lens: provider-switcher mid-conversation

**M1.** History built on `anthropic:` replayed to `vertex-anthropic:`.
Same body; `model` moves to the path, `anthropic_version` to the body.
Thinking blocks with signatures: are Vertex signatures interchangeable
with first-party ones? Unknown. → **Live cell**: replay a first-party
thinking turn on each Messages door.

**M2.** History from `azure-chat:` (a DeepSeek deployment) to
`deepseek:`. Chat wire, but Azure's `reasoning_content` handling is
unknown. → Live cell in the compat preset capture.

## Lens: maintainer of the corpus

**K1.** Nine registry entries in one entry is the largest expansion so
far. Each needs cases, bodies, goldens, error envelopes, support row,
auth fixtures. That is nine capture campaigns. The order in §7 lets
each phase ratify alone. ✔

**K2.** The three chains will drift as the SDKs change (the AWS `login`
rung is new in 2026). Expiry: fact sheets carry 2026-12-03 re-check
dates; `sources/fetch.py` reruns; a diff in the resolver source files
is the trigger. ✔

## Changes made to the model by this pass

1. JWT assertions and exchange bodies are secret material (S3).
2. Container-credential URL allow-list copied from botocore (S5).
3. Token-cache key includes identity-selecting settings (L2).
4. Mantle-door 404 hint names the legacy door (C1); live cell added.
5. Two live cells added for mid-conversation switching (M1, M2).
