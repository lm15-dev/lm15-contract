# 2026-11-12 — Google `external_account` with an AWS source (AUTH-1 `gcp-chain`)

**Status: asked for in session 2026-11-12 ("I want to do option two"); the
details below chosen by the implementer and stated for assent; to ratify.
Evidence: google-auth's own code (`research/cloud-hosts/sources/gcp-google-auth-aws-py.md`,
run as the oracle for the vectors), and a live receipt below.**

## Why

spec/auth.md listed AWS among an `external_account`'s credential sources
from 2026-09-03, and every SDK refused it as a stated gap. A Bigspin
service runs on ECS; its Google Cloud organization forbids API keys
(the console: "API Keys are Disallowed. Your organization's security
policy disallows API keys. Please use Application Default Credentials
(ADC) instead."). Workload identity
federation from the AWS role is the way Google recommends, and the only
one left that holds no long-lived secret.

## What

1. **The subject token is google-auth's, byte for byte.** A signed
   `POST https://sts.{region}.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15`
   (the file's `regional_cred_verification_url`), SigV4 service `sts`,
   empty payload; serialized as google-auth `aws.py` does (headers in
   signing order, `x-goog-cloud-target-resource` appended unsigned,
   `json.dumps(separators=(",", ":"), sort_keys=True)`, `quote(safe="/")`).
   Two vectors in `auth/token-vectors.json` (with and without a session
   token; region from `AWS_REGION` and from `AWS_DEFAULT_REGION`) were
   computed by google-auth 2.62.2 itself, the clock pinned. The STS body
   stays lm15's JSON form (google-auth sends the same fields as a form;
   Google's STS takes both, and the other sources already use JSON).
2. **Validation as google-auth's:** `environment_id` must be `aws<N>`
   with N = 1, and `regional_cred_verification_url` present; otherwise
   `NotConfiguredError` before any request.
3. **Region:** `AWS_REGION`, `AWS_DEFAULT_REGION`, else `region_url`
   (an availability zone; its last character dropped).
4. **AWS credentials:** the environment's keys; **then the container
   endpoint** (`AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` / `FULL_URI`, the
   aws-chain's container rung with its host checks and authorization
   token); then EC2 metadata at the file's `url`.
   *The container endpoint is an lm15 addition, stated.* google-auth
   reads only the environment and EC2 metadata, so on ECS (and EKS Pod
   Identity) it finds no keys, and EC2 metadata answers with the host's
   role, or nothing (awsvpc tasks). Google's documented answer is a
   programmatic supplier; lm15 has the endpoint already, and a task's
   role is the identity a person federating "this service" means. A
   configuration that works with google-auth works the same way here: the
   endpoint is only read where AWS sets it.
5. **IMDSv2:** when `imdsv2_session_token_url` is given, one session
   token (TTL 300) per acquisition, sent to `region_url` and `url`
   (google-auth asks for one per call; one is enough and is what IMDS
   expects).

Not done, stated: web identity (`AWS_WEB_IDENTITY_TOKEN_FILE`) and AWS
profiles as the AWS identity: google-auth reads neither; EKS with IRSA can
federate its own OIDC token through a `file` source instead.

## Live receipt (2026-11-12)

Project `lm15-vertex-live`: pool `lm15-pool`, AWS provider `lm15-aws`
(account 221082216065, attribute condition: one IAM user's ARN),
service account `lm15-live` impersonated (`roles/iam.workloadIdentityUser`
for that subject). The credential file from
`gcloud iam workload-identity-pools create-cred-config … --aws`. lm15-python
on lambda, `credentials={"vertex": "workload"}`, `vertex:gemini-2.5-flash`,
temporary credentials from `aws sts get-session-token`:

- the environment's keys (session token signed): answered "Blue", 1.2 s;
- the same keys served at a loopback `AWS_CONTAINER_CREDENTIALS_FULL_URI`
  with `AWS_CONTAINER_AUTHORIZATION_TOKEN`, as the ECS agent serves a
  task's role: answered "Blue", 1.1 s; the endpoint was asked once, with
  the token.

The first try failed at impersonation with 403 for two minutes after the
grant (Google's propagation, which the error's hint names); the STS
exchange, the part this change adds, was accepted on the first request.
