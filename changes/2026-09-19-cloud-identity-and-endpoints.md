# 2026-09-19 — Cloud identity and endpoints: named credentials, provenance, the endpoint as a URL root

Ratification: **RATIFIED in session 2026-09-19** — Maxime Rivest, after
the study of Pamela Fox's review of lm15 1.0.0rc1 on Microsoft Foundry
and the seven-scenario walk-through ("Yes, this is perfect. Go and
implement it completely, fully, and, excellently"). One decision, D5,
was revised by the implementer during implementation on new evidence and
is marked for explicit assent. Reference implementation: lm15-python
(branch `cloud-identity-endpoints`); ports follow (see "Ports").

Companion fixture: `auth/named-credentials.json` (20 cases). Amends
`spec/auth.md` AUTH-1, AUTH-2, AUTH-7, AUTH-10.

## The evidence

Pamela Fox (Microsoft, Python advocacy) tested 1.0.0rc1 on Foundry
between 2026-09-16 and 2026-09-18 (`pamelafox/python-stack-foundry-models`,
`examples/lm15_request.py`, `examples/lm15_router.py`; lm15-python issue
#10). What she found, in her words and in the code she wrote:

1. She did **not** use lm15's Azure chain: "I always use an explicit
   credential from the azure.identity package, not a credential chain,
   for production security and debugging reasons." Microsoft's SDK
   guideline: a client library must not build `DefaultAzureCredential`
   on the developer's behalf; production uses managed identity, picked
   by the developer. Her core objection to chains: "tricky to figure out
   where a credential is coming from."
2. The Foundry console shows `https://{account}.services.ai.azure.com`;
   it serves OpenAI and non-OpenAI deployments alike (she verified GPT,
   Kimi K2.6, DeepSeek V4 Flash and Claude Sonnet 4.5 keyless). The
   `openai.azure.com` alias saves one internal hop for OpenAI models
   today. Her verdict: the hard-coded alias "is probably fine, as long
   as developers can easily customize base URL".
3. She could customise the base URL only by **leaving the `azure` door**
   (`openai:` + `base_urls`): the router refused a `base_urls` entry on
   any cloud door, and the contract's promised `AZURE_OPENAI_ENDPOINT`
   fallback (AUTH-10, 2026-09-03) was never read by the reference. That
   bypass silently lost the `api-key` scheme, the `DeploymentNotFound`
   and content-filter mapping, and the doctor.
4. Her code had to write `api_keys={"openai": lambda: BearerToken(provider())}`
   where the OpenAI SDK takes `api_key=provider`.
5. The docs said both "lm15 never fetches tokens" and "the azure door
   walks DefaultAzureCredential's chain itself", and showed a scope
   (`cognitiveservices.azure.com/.default`) different from the code's
   default (`ai.azure.com/.default`).

The study generalised this across the three clouds (aiconvo 2026-09-19):
Google recommends its chain (ADC) and warns it picks the *user* on a
laptop; AWS endorses the chain but says "be explicit in production";
Microsoft is chain-averse. None objects to a chain existing; all object
to it being invisible.

## The rule

**lm15 never picks an identity silently. It either receives a credential,
or it says which one it picked.** And: default the mechanics freely;
default identity and data location cautiously — a default that decides
which account pays or which country data goes to must be visible and
printed by the doctor.

Three ways in, matched to three moments: the laptop (nothing configured;
the chain, with provenance), the deployment (`credentials={"azure":
"platform"}`: one identity, or fail), the expert (`api_keys={"azure":
provider}`: the caller's own credential object, no boilerplate). The
request code never changes between them. No production detector: a
container, a variable or an installed CLI cannot tell intent; the
developer says "platform".

## Decisions

**D1 — Named credentials (AUTH-1).** `credentials: {provider: name}`,
`name` ∈ {`platform`, `workload`, `environment`, `cli`}; the same four
words on every cloud, mapped to rungs per chain (table in AUTH-1). Bare
adapters take `credential=`. A named credential runs its rungs only and
never falls through; absent is `NotConfiguredError` naming the name, its
meaning on this cloud, and what was probed. A name plus an `api_keys`
entry for one provider is refused; a name on a non-cloud door is
refused; an unknown name is refused at construction. Trade-offs, stated:
universal names rather than cloud-specific ones (`managed-identity`,
`instance-role`) — an agent that learned one cloud has learned all
three; what is lost ("the name says what happens") is recovered by
provenance, which always prints the concrete mechanism. `platform` on AWS
is two rungs (container, then IMDS), a two-step mini-chain identical to
boto3's; the doctor says which answered. On GCP `workload` and
`environment` are one file rung told apart by `type`; the wrong type is
refused by name. The chain stays the default when nothing is configured
(Microsoft would prefer opt-in; AWS and Google endorse it; provenance
removes the actual harm).

**D2 — Provenance (AUTH-1, AUTH-7).** A resolved cloud credential
carries `CredentialSource {rung, label, named?, expires_at?}`. Every
`AuthError` from the wire names the source of the credential it sent —
one line under the provider message, before the guidance, added once,
surviving the re-login hint: the rung, `env $VAR`, "an explicit api_key",
the stored login, or "an application-supplied callable (identity not
inspected by lm15)". The reference exposes `provider.source` on the chain
provider and `lm.credential_origin()` on adapters. Never the value.

**D3 — A JWT string is a bearer token (AUTH-2).** Where an `ApiKey`
would take `api-key`/`x-api-key` and the policy also lists `bearer`, a
JWS-compact JWT string travels as bearer. Replaces the 2026-09-04 refusal
("wrap it: BearerToken(token)"); the wrap stays accepted. Trade-off: a
decision from appearance, made only where the alternative is a certain
401 and no door issues a JWT-shaped key.

**D4 — The endpoint is a URL root the door completes (AUTH-10).**
`HostSpec.base_url` splits into a root and a door path; `HostSpec.endpoint_env`
lists the vendor's variables. Order: explicit `base_urls` / `base_url=`,
then the vendor variable, then the template. The door path is appended
unless already present (or a leading part of it is); `http(s)` only, no
query/fragment/userinfo; trusted configuration. Root-only settings
(`resource`) become optional with an endpoint; path settings and the
SigV4 `region` do not. The door's scheme, backend, error mapping, headers
and doctor stay attached. Variables: `AZURE_OPENAI_ENDPOINT`,
`ANTHROPIC_FOUNDRY_BASE_URL`, `AWS_ENDPOINT_URL_BEDROCK_RUNTIME` /
`AWS_ENDPOINT_URL_BEDROCK_MANTLE` / `AWS_ENDPOINT_URL_AWS_EXTERNAL_ANTHROPIC`
then `AWS_ENDPOINT_URL` (the SDK's `<SERVICE_ID>` rule; the two mantle /
external ids follow the rule, no page cites them — stated). Vertex: no
citable vendor variable; explicit entry only — stated. `base_urls` is
reused rather than a new `endpoints` key: one concept, one name; the
cost is the append-unless-present rule above, pinned here.

**D5 — Azure default host: kept, not flipped. REVISED with evidence;
awaiting assent.** The in-session plan flipped the `azure`/`azure-chat`
template to `services.ai.azure.com`. During implementation, DNS
(2026-09-19) showed the lab's classic `OpenAI`-kind resource
(`lm15-oai-29d280ed6f8e`, the one every Azure receipt in this corpus was
taken on) resolves on `openai.azure.com` only — NXDOMAIN on
`services.ai.azure.com` and `cognitiveservices.azure.com` — while the
Foundry `AIServices` resource resolves on all three. A flipped default
would break every classic Azure OpenAI resource; the alias works on both
kinds and saves a hop for OpenAI models. So the template stays, and the
Foundry root is one variable away (`AZURE_OPENAI_ENDPOINT`), which the
docs tell the reader to paste whenever the console shows one. The
maintainer's plan is thereby not followed on this one point; the reason
is named here rather than absorbed.

**D6 — Scope per door (AUTH-10).** Every Azure door defaults to
`https://ai.azure.com/.default` (the chain's request; live on the OpenAI
doors 2026-09-04; Pamela's Foundry runs 2026-09-18);
`cognitiveservices.azure.com/.default` is accepted by the resource and
set through the `scope` setting. The docs now agree with the code.

**D7 — The docs lead with the three lines.** `cloud-hosts.md` is
restructured as the seven scenarios (laptop, endpoint, deployed, own
credential, gateway/sovereign, the 3 a.m. page, the one-shot block);
`authentication.md` no longer claims lm15 never obtains a token. For a
one-shot reader, human or agent, the nearest example is the wise one and
the production line is as short as the lazy one. No warnings, no
nagging.

## Fixtures

`auth/named-credentials.json` — 20 cases: each names a credential for a
door and pins the doctor's steps (only the named rungs), `configured`,
the base URL where an endpoint or vendor variable is present, the
relaxed `resource`, the still-required AWS `region`, GCP type refusal,
and the key-plus-name refusal. A separate file from `auth/resolution.json`
so the ports' existing suites do not break before they implement; the
port work item is exactly "consume this file".

Independent receipt (not reproduced in the lm15 lab, where Claude quota
is still 0): Pamela Fox's runs of `azure-anthropic` (Claude Sonnet 4.5)
and the OpenAI doors (GPT, Kimi, DeepSeek) on 2026-09-18 with an explicit
`AzureDeveloperCliCredential`, from `pamelafox/python-stack-foundry-models`.
Recorded as evidence with its caveat: the explicit-credential path, and
for OpenAI models the `openai` + `base_urls` bypass she used before D4.

## Ports

TypeScript, Rust, Go and Julia carry the same `HostSpec` tables and
chains. To land this amendment a port: adds `endpoint_env` to its host
table and the root/path split with the append-unless-present rule;
reads `credentials` / `credential=` and the `NAMED_RUNGS` table; carries
`CredentialSource` and prints it on auth errors; makes the doctor pass
`auth/named-credentials.json`; sends a JWT string as bearer. Nothing in
`auth/resolution.json` changed.

## Not done, stated

- Trimming the developer rungs the reference hand-copies across five
  languages (PowerShell, `aws login` DPoP refresh, SSO cache formats) —
  a separate decision before 1.0; named credentials make the
  deterministic rungs cheap and leave the expensive part where it was.
- An environment variable naming the credential (`LM15_CREDENTIAL`):
  not added; the name lives in code where it is reviewed. Azure's own
  `AZURE_TOKEN_CREDENTIALS` narrowing is still honoured inside the
  chain.
- A Vertex vendor endpoint variable: none this corpus can cite.
