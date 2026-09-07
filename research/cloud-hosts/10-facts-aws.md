# AWS — fact sheet

Sources: `sources/manifest.json`, frozen 2026-09-03. Every cell cites
`file:line` in `sources/`. A blank cell is a finding. Re-check date:
2026-12-03.

## Doors (which URL, which wire, which signing scope)

| Door | Base URL | Wire | SigV4 service | Bearer alternative | Streaming | Model id form | Cite |
|---|---|---|---|---|---|---|---|
| Claude Platform on AWS | `https://aws-external-anthropic.{region}.api.aws` | Claude API, `/v1/{endpoint}` verbatim | `aws-external-anthropic` | `x-api-key` from AWS-console key or short-term token (12 h max) | SSE | first-party ids (`claude-sonnet-5`), no prefix | anthropic-platform-on-aws.md:19-31, :208-210, :216-218, :246-262 |
| Claude in Amazon Bedrock ("mantle") | `https://bedrock-mantle.{region}.api.aws` | Messages API at `/anthropic/v1/messages`, same body as first-party | `bedrock-mantle` | `x-api-key` short-term bearer (12 h, "least preferred") | SSE ("standard SSE streaming") | `anthropic.` prefix (`anthropic.claude-opus-5`) | anthropic-on-bedrock.md:138-160, :58-70, :322, :327-338 |
| Bedrock Chat Completions (mantle) | `https://bedrock-mantle.{region}.api.aws/v1/chat/completions` | OpenAI Chat Completions; `GET /v1/models` lists (55, live 2026-09-04) | `bedrock-mantle` | `Authorization: Bearer` | SSE | un-versioned Bedrock ids (`openai.gpt-oss-20b`) | bedrock-openai-chat-completions.md:7, :14, :45; receipts/2026-09-04-bedrock-mantle-chat/ |
| Bedrock Chat Completions (runtime, "recommended") | `https://bedrock-runtime.{region}.amazonaws.com/openai/v1/chat/completions` | OpenAI Chat Completions; `GET /openai/v1/models` is 404 under SigV4 and bearer (live 2026-09-03/04) | `bedrock` | `Authorization: Bearer $AWS_BEARER_TOKEN_BEDROCK` | SSE | versioned Bedrock ids / inference profiles (`openai.gpt-oss-20b-1:0`) | bedrock-openai-chat-completions.md:8, :151, :178-179, :213-228; receipts/2026-09-03-bedrock-chat/probe-models-list.json |
| Bedrock InvokeModel (legacy) | `https://bedrock-runtime.{region}.amazonaws.com/model/{modelId}/invoke` and `/invoke-with-response-stream` | provider-native body; for Claude: Messages body with `anthropic_version: bedrock-2023-05-31`, no `model` | `bedrock` | bearer API key | **AWS event-stream binary framing**; payload events `{"chunk": {"bytes": blob}}` | ARN-versioned ids `anthropic.claude-sonnet-4-5-20250929-v1:0`, often **must** use an inference profile `us.`/`global.` prefix | bedrock-invoke-model-stream.md:13, :78-91, :182; bedrock-anthropic-messages.md:60; anthropic-on-bedrock-legacy.md:136-139, :336, :559 |
| Bedrock Converse (legacy) | `https://bedrock-runtime.{region}.amazonaws.com/model/{modelId}/converse` and `/converse-stream` | Converse: `messages`, `system`, `inferenceConfig`, `toolConfig`, `additionalModelRequestFields`, `guardrailConfig` | `bedrock` | bearer API key | AWS event-stream; events `messageStart`, `contentBlockStart/Delta/Stop`, `messageStop`, `metadata` | same as InvokeModel | bedrock-converse.md:14-59; bedrock-converse-stream.md:150-170 |
| ListFoundationModels (control plane) | `https://bedrock.{region}.amazonaws.com/foundation-models` | GET, JSON `modelSummaries[].modelId`, `inferenceTypesSupported` | `bedrock` (control plane host `bedrock.`, not `bedrock-runtime.`) | — | — | — | bedrock-list-foundation-models.md:5, :28-34; bedrock-endpoints.md:55-78 |

Feature gaps on the mantle Messages door (raise, MAP-8): structured
outputs, URL/Files sources, server-side tools, Agent Skills/MCP/programmatic
tool calling, Message Batches, Models API, `fallbacks`, `anthropic-beta`
header (anthropic-on-bedrock.md:358-367; anthropic-platform-on-aws.md:24).
Claude Platform on AWS passes `anthropic-beta` and needs an
`anthropic-workspace-id` header on every request
(anthropic-platform-on-aws.md:24, :244-262). Region is required, no default
(anthropic-platform-on-aws.md:181, :271).

Endpoint variants: `bedrock-fips.` hosts and `us-gov-*` regions
(bedrock-endpoints.md:55-59). Global vs regional: mantle offers "Global"
routing with no premium and "Regional" with a 10% premium; regional
routing across a geography uses an inference profile (US/EU/JP/AU)
(anthropic-on-bedrock.md:371-376). PrivateLink is supported for the
external-anthropic door (anthropic-platform-on-aws.md:33). Custom endpoint
override: `AWS_ENDPOINT_URL` and `AWS_ENDPOINT_URL_<SERVICE>`
(aws-sdkref-endpoints.md).

## Credential chain — boto3 order (the reference SDK for lm15-python)

botocore `create_credential_resolver` (aws-botocore-credentials-py.md:84-152)
builds `pre_profile + profile_providers + post_profile`:

| # | Provider (`METHOD`) | Reads | Needs | Cite |
|---|---|---|---|---|
| 1 | `env` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` | nothing | credentials-py:138-141, :1186; aws-sdkref-env-vars.md |
| 2 | `assume-role` | profile `role_arn` + `source_profile` / `credential_source` (Environment, Ec2InstanceMetadata, EcsContainer) | STS `AssumeRole` (signed HTTPS) | credentials-py:1536; aws-sdkref-assume-role.md |
| 3 | `assume-role-with-web-identity` | `AWS_WEB_IDENTITY_TOKEN_FILE` + `AWS_ROLE_ARN` (+ `AWS_ROLE_SESSION_NAME`), or profile `web_identity_token_file` | STS `AssumeRoleWithWebIdentity` (unsigned HTTPS POST) | credentials-py:207, :1880; aws-sts-assume-role-web-identity.md |
| 4 | `sso` | profile `sso_session` → `sso-session` section (`sso_start_url`, `sso_region`), `sso_account_id`, `sso_role_name`; token cache `~/.aws/sso/cache/<sha1(session or start_url)>.json` | `sso-oidc CreateToken` refresh (HTTPS) then `sso GetRoleCredentials` (HTTPS, bearer) | credentials-py:211, :2356-2359, :2299; aws-sdkref-sso-credentials.md:80, :107 |
| 5 | `shared-credentials-file` | `~/.aws/credentials` (`AWS_SHARED_CREDENTIALS_FILE`), profile from `AWS_PROFILE` | file read | credentials-py:212, :1364 |
| 6 | `login` | profile `login_session`; cache `~/.aws/login/cache` (`AWS_LOGIN_CACHE_DIRECTORY`); 15-minute creds refreshed up to 12 h | HTTPS refresh | credentials-py:213, :2722-2735; aws-sdkref-login-credentials.md |
| 7 | `custom-process` | profile `credential_process`; stdout JSON `{"Version":1,"AccessKeyId","SecretAccessKey","SessionToken","Expiration"(RFC3339)}` | subprocess | credentials-py:214, :1070; aws-sdkref-process-credentials.md:58-70 |
| 8 | `config-file` | `~/.aws/config` (`AWS_CONFIG_FILE`) static keys | file read | credentials-py:215, :1422 |
| 9 | `ec2-credentials-file`, `boto-config` | legacy boto2 files | file read | credentials-py:146-148, :1329, :1490 |
| 10 | `container-role` | `AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` (host `169.254.170.2`) or `AWS_CONTAINER_CREDENTIALS_FULL_URI`; `AWS_CONTAINER_AUTHORIZATION_TOKEN[_FILE]` → `Authorization` header | plain HTTP GET | credentials-py:149, :2069; aws-sdkref-container-credentials.md:31-41 |
| 11 | `iam-role` (IMDS) | `PUT /latest/api/token` with `X-aws-ec2-metadata-token-ttl-seconds`, then `GET /latest/meta-data/iam/security-credentials/<role>` with `X-aws-ec2-metadata-token`; host `169.254.169.254` or `[fd00:ec2::254]`; disabled by `AWS_EC2_METADATA_DISABLED=true` | plain HTTP | credentials-py:150, :1156; aws-imdsv2.md:101-102, :30; aws-sdkref-imds-credentials.md:27 |

The public AWS docs list the same rungs for boto3
(aws-boto3-credentials.md:19-45). The SDK reference says the exact chain
"varies" per SDK (aws-sdkref-credential-chain.md:16); Go SDK v2 does **not**
support the `login` provider (aws-sdkref-login-credentials.md:24). The
Anthropic AWS client adds two rungs ahead of the chain: constructor
`apiKey` → `x-api-key`, then explicit keys, then `awsProfile`, then
`ANTHROPIC_AWS_API_KEY`, then the default chain
(anthropic-platform-on-aws.md:266-271). Bedrock API keys read from
`AWS_BEARER_TOKEN_BEDROCK` (bedrock-api-keys.md:176-185); short-term keys
last ≤ 12 h and inherit the IAM principal, long-term keys are "for
exploration only" (bedrock-api-keys.md:4-5, :89).  A short-term key is
minted client-side: a SigV4 *query* presign of `POST
https://bedrock.amazonaws.com/?Action=CallWithBearerToken` (service
`bedrock`, 43200 s, empty-payload hash, `host` the only signed header),
then `bedrock-api-key-` + base64 of the URL without scheme + `&Version=1`
(aws-bedrock-token-generator 1.1.0 source; reproduced byte for byte by
`research/providers/_aws_bearer.py`).  Live 2026-09-04 (`us-east-1`): the
key answers 200 on the Chat Completions door under `Authorization: Bearer`;
`GET /openai/v1/models` is still 404 under it (the docs' listing claim does
not hold); the mantle door under `x-api-key` answers the same account-gate
403 as SigV4 for every Claude id.

Region: `AWS_REGION`, then profile `region`; the Anthropic client also
reads `AWS_DEFAULT_REGION` (aws-sdkref-region.md; anthropic-platform-on-aws.md:271).

## Signing — SigV4

Algorithm `AWS4-HMAC-SHA256`; canonical request = method, URI-encoded
path, sorted query, lowercase sorted headers (`host` and every `x-amz-*`
mandatory; `content-type` if present), signed-headers list, hex SHA-256 of
the payload; string-to-sign = algorithm, `x-amz-date`, credential scope
`YYYYMMDD/region/service/aws4_request`, hex hash of canonical request;
signing key = HMAC chain `AWS4`+secret → date → region → service →
`aws4_request`; temporary credentials add `x-amz-security-token`
(aws-sigv4-create-signed-request.md:46-190, :32). Only HMAC-SHA256 and
SHA-256 are needed: standard library in every lm15 language.

Deterministic under a fixed clock and fixed keys — the harness can pin the
`Authorization` header byte for byte. AWS's own doc examples use
`AKIAIOSFODNN7EXAMPLE` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
(aws-sdkref-env-vars.md); the fixture uses those.

## Stream framing — AWS event-stream (legacy doors only)

Binary, big-endian: prelude `total_length u32`, `headers_length u32`,
`prelude_crc u32`; headers (name-length u8, name, value-type u8, value);
payload; `message_crc u32` over everything before it. Header types include
string (type 7). Every message carries `:message-type` (`event` |
`exception` | `error`), plus `:event-type`/`:content-type` or
`:exception-type` or `:error-code`/`:error-message`
(aws-eventstream-smithy.md:40-62, :188-200, :256-307). Payload cap 24 MB,
headers cap 128 KB (:62-63; aws-botocore-eventstream-py.md:21-23). CRC32 is
standard library (`binascii.crc32`, aws-botocore-eventstream-py.md:15).
For InvokeModel the event payload is `{"chunk":{"bytes": base64}}` whose
decoded bytes are one provider SSE-style JSON event
(bedrock-invoke-model-stream.md:78-80).

Not needed for the two `api.aws` doors, which stream SSE
(anthropic-on-bedrock.md:138; bedrock-openai-chat-completions.md).

## Errors the host raises (before the model sees the request)

InvokeModel stream exceptions: `internalServerException`,
`modelStreamErrorException`, `throttlingException`,
`validationException` (bedrock-invoke-model-stream.md:81-91). On-demand
call to a model that needs an inference profile: `validationException`
"Invocation of model ID … with on-demand throughput isn't supported"
(anthropic-on-bedrock-legacy.md:136). Claude Platform on AWS before setup:
"Outbound web identity federation is disabled for your account"
(anthropic-platform-on-aws.md:189-195). Live capture must add: expired
session token, wrong region, no model access, throttled.

## Blank cells (findings)

- No scraped page gives the Bedrock `/openai/v1/chat/completions`
  feature list (thinking, tool_choice, response_format). Live cells.
- No scraped page states whether the mantle Messages door honours
  `anthropic-version` values other than `2023-06-01`. Live cell.
- Model listing for the `api.aws` doors: mantle chat lists via
  `/v1/models` (bedrock-openai-chat-completions.md:16-45); the mantle
  Messages door lists nothing ("Models API" unsupported,
  anthropic-on-bedrock.md:364); Claude Platform on AWS: not stated.
- SSO token cache file naming: botocore hashes the session name or start
  URL with SHA-1 (aws-botocore-credentials-py.md:2299); the exact cached
  JSON keys (`accessToken`, `expiresAt`, `clientId`, `clientSecret`,
  `refreshToken`, `registrationExpiresAt`) are read from the code, not
  from a doc page. Recorded as code-cited.
