# Follow-up: Foundry aliases, authentication and low-capacity throttling

Date: 2026-09-19. This investigation supersedes the provisional interpretation
in the parent README. All probes are real HTTPS requests, not mocks; no model
SDK, automatic retries, or hostname fallback was used.

## Conclusions

1. On this AIServices account in eastus2, **both** `openai.azure.com` and
   `services.ai.azure.com` successfully serve **DeepSeek-V4-Flash** and
   **Kimi-K2.6**, using **Responses** and **Chat Completions**.
2. On both hosts, Responses succeeds using an API key, Entra tokens scoped to
   `https://ai.azure.com/.default`, and Entra tokens scoped to
   `https://cognitiveservices.azure.com/.default` (both models tested).
3. DeepSeek Responses also succeeds on both hosts with `store=false`, with
   streaming, with `max_output_tokens=16`, and with `?api-version=preview`.
   Streaming was checked for a terminal `response.completed` event whose
   response status was `completed`, not just HTTP 200.
4. The original `429 no_capacity` error was reproduced on **both** hosts at
   the smallest deployment allowance. Its headers expose rate limiting, and
   longer request spacing restored success on both hosts at that allowance.
   These failures are not evidence of non-OpenAI incompatibility on the alias.
5. The portal recommends the `services.ai.azure.com/openai/v1` endpoint in
   the generated Kimi code, while its project home also displays an
   "Azure OpenAI endpoint" under `openai.azure.com/openai/v1`. The resource's
   management API advertises multiple endpoints. Different endpoint labels
   and scopes in the portal do not imply mutually exclusive model catalogs.

This does not establish equivalence for every model or every Foundry feature,
and does not test Claude's separate `/anthropic/v1` API. It also does not
measure a reliable latency difference. Classic OpenAI-kind resources are a
separate question: these tests only used the AIServices account.

## Test controls and results

Account: `lm15-fdy-29d280ed6f8e`, kind AIServices, location eastus2,
resource group `lm15-lab`. No existing model deployments were present before
this investigation. Deployment billing mode was GlobalStandard pay-per-token,
not Provisioned Throughput. No tenant or account security settings changed.

Models:
- DeepSeek-V4-Flash, format DeepSeek, version 2026-04-23.
- Kimi-K2.6, format MoonshotAI, version 2026-04-20.

The default prompt was `Reply with exactly OK.` and the output budget was
256 tokens. The baseline request body hashes match across host pairs for
both models and both surfaces. Authentication values were held in process
memory, never written to receipts. For the baseline, the same Entra token
was used for all eight requests. Other phases deliberately changed only
recorded variables. Each receipt stores the URL, body/hash, auth mode (not
its secret), timestamps, status, response headers (excluding cookies and
credentials), and verbatim response body. Headers name the expected served
model version and East US 2 on both aliases.

| Phase | Conditions | Results |
|---|---|---|
| `baseline-*` | capacity 10; both models × both APIs × both hosts; reverse host order for Kimi | 8/8 HTTP 200 |
| `auth-*` | capacity 10; both models × both hosts × API key / cognitive-services-scoped Entra token | 8/8 HTTP 200 |
| `variant-*` | capacity 10; DeepSeek Responses; stateless, stream, output budget 16, preview query | 8/8 HTTP 200 |
| `capacity1-*` | existing DeepSeek deployment changed from 10 to 1 in management API | 4/4 HTTP 200, **but data-plane headers still advertised 10 RPM / 10,000 TPM** |
| `fresh1-*` | fresh deployment created at capacity 1, original deployment name, both hosts alternated | first B request 200, then A/B/A each 429 `no_capacity` |
| `slow1-*` | same fresh capacity-1 deployment; long idle before A, at least 150 seconds after A finished before B | 2/2 HTTP 200, headers confirm 1 RPM / 1,000 TPM |

Total follow-up inference calls: **34**, comprising **31 HTTP 200** and
**3 HTTP 429**. The 24 higher-allowance tests all succeeded. Additional GET
probes: `/openai/v1/models` was 200 on both hosts; `/openai/v1/deployments`
was 404 on both. Those GETs are not inference calls and do not prove that a
catalog entry is deployed.

## What explains the apparent hostname difference?

The fresh capacity-1 test reproduced the exact `no_capacity` body returned in
the initial investigation. On A, a failure reported:

- `x-ratelimit-limit-requests: 1`
- `x-ratelimit-remaining-requests: -1`
- `x-ratelimit-reset-requests: 105`
- `x-ratelimit-limit-tokens: 1000`
- `x-ratelimit-remaining-tokens: 995`
- `x-ratelimit-type: Tokens`
- `retry-after: 39`

B subsequently returned the same error, with reset-requests 86 seconds.
The experiment had waited more than 65 seconds between calls, which was
not enough under these effective conditions. Waiting longer produced
successful completed responses on both hosts, still at 1 RPM / 1,000 TPM.

The headers are not internally transparent: the error labels tokens even
though the token balance is almost full, and the request balance can become
negative. We cannot establish Azure's internal accounting, hidden internal
retries, or shared-pool allocation from these observations. Do not assert a
specific double-charge or two-hop mechanism. The defensible conclusion is
**rate/capacity throttling on a very small deployment, not an unsupported
host**. The exact internal reason for the longer reset remains unknown.

The intermediate downscale test is **not** proof that capacity 1 worked:
management reported capacity 1 while replies still reported the old 10 RPM
limit. Treat that as observed control-plane/data-plane lag, not a fixed or
measured propagation SLA. The final fresh deployment does establish success
at the original small allowance because its actual response headers say so.

## Documentation and portal evidence

Snapshots in this directory:
- `api-lifecycle.md`: Microsoft explicitly accepts both URL forms and
  documents non-OpenAI Chat Completions plus a link for Foundry Responses.
  https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle
- `generate-responses.md`: Microsoft's Foundry Responses guide uses a
  services.ai project endpoint. That is another supported route; our tests
  used the account-level endpoint successfully without adding a project path.
  https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/generate-responses
- `quota.md`: discusses estimated token budgets, distributed rate-limit
  enforcement, and temporary shared-pool adjustments. It does not identify
  the exact backend cause for this particular test.
  https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/quota
- `portal-endpoint-example.json`: the actual generated Kimi example, endpoint
  fields and page URL, captured through the user's browser; no API key.
- `resource.json`: management-plane account metadata and advertised endpoints.

## Consequences for lm15

Prefer the explicit endpoint supplied by Azure, including services.ai for
Foundry. Retain the openai.azure.com resource-name shortcut for existing
classic Azure OpenAI users. Do not silently retry on another hostname after
a 429: that would conceal throttling rather than fix a compatibility issue.
A generic `DeploymentNotFound` must not be presented as evidence that the
alias cannot serve non-OpenAI models. There is no need to ask Pamela to run
this basic compatibility test; we now have direct evidence ourselves.

## Cleanup

All three temporary deployments were deleted. `cleanup.json` records their
names and the subsequent empty deployment listing. Existing accounts,
project, authentication settings and quota entitlements were left intact.
