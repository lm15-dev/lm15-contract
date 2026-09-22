# 2026-09-22 — Managed authentication, explicit identity, interactive connect

## Status and authority

**RATIFIED CORE, 2026-09-22. R1–R3 preserve subscription access and precedence;
R10 starts with Python and TypeScript. Reserved details remain non-normative.
No SDK implementation in this change.**

The maintainer requested a shared written definition covering concepts, identity
precedence, lifecycle, I/O, secrecy and platforms before implementation.
He clarified that no legacy API compatibility is needed, but losing working
subscription access is unacceptable. Existing API-key/Azure users also remain
supported. The initial implementation scope is Python and TypeScript. Earlier discussion approved
the direction of scoped auth, UI independence, resumable login and an interactive
`connect()` that hides routine assembly, not consequential choices.

This change amends `spec/auth.md`, adds its managed supplement
`spec/auth-managed.md` (AUTH-12–26, core tier) and `spec/auth-managed-reserved.md`
(rules written ahead of any implementation that needs them; each names the
trigger that promotes it), examples, schema/fixtures and acceptance scenarios, and makes the scope/API-family/vocabulary consequences explicit.
It does not amend the evidence precedence in AUTHORITY.md. Core decisions below
are ratified; entries concerning reserved rules remain design notes until
explicit promotion. Upstream protocol details still require wire evidence.

The maintainer's yes/no list is
[2026-09-22-managed-authentication-ratification.md](2026-09-22-managed-authentication-ratification.md).
The split into core/reserved was made on 2026-09-22 after review judged the
first draft front-loaded server, database and relay rules no implementation had
yet tested. The later subscription-first correction supersedes the original
retirement proposal; it is not a blanket ratification of reserved text.

### Ratification and fixture correction

The maintainer corrected the proposal: “subs is always better then keys except
when keys are explicitly used”, edited R10 to “Starting with python and
typescript.”, accepted R11/R12, and said “otherwise i ratify.”

- R1: no Claude/Codex cutover before separate provider-permission and live
  login → inference → renewal evidence with the intended account/billing behavior.
- R2/R3: explicit key/named cloud authority wins; otherwise subscriptions precede
  ambient keys. Failure/logout never silently switches billing sources.
- All existing access-preservation fixtures remain. The canonical expectation
  `xai-env-rescues-unusable-login` is corrected to
  `xai-unusable-login-blocks-env` under AUTH-1/AUTH-15 and R3: configured=false,
  the environment rung shadowed (blocked), no key acquisition. The old commit
  preserves the historical expectation; this change is not based on SDK output.
- `auth/managed/resolution.json` replaces the draft's two anti-subscription
  decisions and adds explicit/failure/logout/ambiguity regressions. They are
  synthetic canonical cases, not evidence of provider support.
- No SDK pins, support rows or wire fixtures change. The old runtime may fail the
  corrected xAI behavior until implementation; do not weaken this gate to hide it.

## Evidence and limits

- Current source/contract study: `../architecture-review/pi-auth-parity-2026-09-21.md`.
- Official Earendil Pi reference: tag `v0.87.0`, commit
  `16787ad5b2dc748047f314ca1bfe7708f30f54f3`, especially `packages/ai/src/auth/`,
  `providers/`, and coding-agent auth storage/UI. This is implementation reference,
  not live provider evidence or permission to use a particular registration.
- Design inputs: the four mock-ups in `../architecture-review/`, followed by the
  maintainer's review in this conversation. The final decisions below supersede
  conflicting prototype ideas (implicit global Auth, ambient managed fallback,
  secret portable pending tokens, and requiring every beginner to assemble Auth/UI/router).
- Security sources to follow: RFC 9700 (OAuth security BCP), RFC 7636 (S256 PKCE),
  RFC 8252 (native apps), RFC 8628 (device authorization), RFC 2119/8174 (normative
  terms). Provider-specific exceptions require an evidenced flow profile.
- No new live login, token exchange, paid request, deployment or credential-file
  inspection was performed to write this amendment.

## Decisions and expert objections considered

Each row states the rejected alternative and its cost; none is an unstated
implementation shortcut.

| Decision | Rejected alternative / why | Accepted trade-off |
|---|---|---|
| **D1. Separate service, route, instance, binding and connection** (AUTH-12) | A provider string used for all five conflates menu grouping, wire protocol, enterprise host and identity; credential leakage/account confusion follows | More internal concepts; ordinary users see a picker and a bound client |
| **D2. Descriptors plus stable IDs** (AUTH-13) | String-only APIs require memorizing IDs; closed built-in enums alone block custom providers | Named built-ins and dynamic descriptors coexist; receiver revalidates registry/revision |
| **D3. Native language APIs over one behavior contract** (AUTH-22) | One mandatory Node subprocess or hosted auth service erases SDK independence and changes trust/deployment | More implementation work; Python and TypeScript first, with the same scenario suite; other languages are follow-up |
| **D4. Explicit authority first, otherwise subscription-first** (AUTH-15) | Env-first selection or fallback after logout can silently change who pays | Respect scope and route boundaries; ambiguity requires selection; API-key/cloud-only use remains supported |
| **D5. Bound client pins connection ID and exact model** (AUTH-23) | Following the active slot after replacement can change the account halfway through a CSV without code changes | Old bound clients stop after replacement; caller explicitly selects again |
| **D6. Interactive connect assembles the advanced API** (AUTH-16/23) | Making every cookbook construct five objects exposes plumbing; installing a global account hides ownership | One convenience client/facade, returning full canonical results, with a pure Request escape hatch |
| **D7. One active connection/attempt per binding slot in v1** (AUTH-12/18) | Full multi-account arbitration/default selection multiplies policy before the basic contract is proven | Personal/work accounts require explicit scopes/instances; future same-slot account picker is not promised |
| **D8. Preserve subscription access until a replacement is proven** (AUTH-14, R1/R2) | Retiring CLI access assumes new login grants equivalent subscription entitlement; copying rotating tokens creates unsafe dual owners | Temporary coexistence and provider-specific evidence work; stop/review if safe coexistence cannot be established. No blanket API compatibility layer required |
| **D9. Reserved: private resumable attempt, public opaque ID** (AUTH-18 reserved) | A self-contained secret `pending.token` moves verifier/device-secret handling into every app and still needs replay/ownership management | Begin needs storage and one-time commit coordination; a public ID alone cannot authorize resume |
| **D10. Transactions, generations and durable exchange markers** (AUTH-19/20/25) | Plain get/set loses rotated tokens; lease fencing alone cannot stop a second remote exchange after lease loss | Stronger storage adapter requirements and contention; uncertain rotating exchanges stop for recovery rather than guessing |
| **D11. Cancellation is ordered against commit, not a promise of rollback** (AUTH-19) | Returning cancelled as proof of no effect is false after remote approval or a winning local commit | Apps can inspect attempt state; cancellation after commit requires explicit logout to undo local storage |
| **D12. Keep saved login after model-picker cancellation** (AUTH-23) | Whole-wizard rollback may erase a valuable grant or pretend to revoke it remotely | connect is not atomic; helper says what was saved and returns a safe recovery reference |
| **D13. Actual expiry plus bounded renewal lead** (AUTH-20) | Subtracting skew on load and save double-counts it; fixed five minutes makes one-minute tokens perpetually due | Managed account lead is min(300 s, lifetime/10); cloud semantics remain unchanged; short-token behavior is newly pinned |
| **D14. No blind retries of ambiguous one-use work** (AUTH-20/24) | Generic retry-on-network-error may spend a rotated token twice; exactly-once across provider/store crash is impossible | Some failures require a fresh login even if the old credential might still work; preserve identity safety over availability |
| **D15. Stored, usable and verified are separate** (AUTH-17/24) | A green connected boolean misrepresents cached state as live eligibility | More informative status fields; explicit verification may still be unsupported or provider-metered |
| **D16. Platform-specific availability/evidence** (AUTH-22) | WASM is not a CORS bypass; successful native login or preflight is not a complete browser receipt | Some methods are unavailable/unverified; separate native, browser, mobile and server test evidence |
| **D17. Consent before relay and account-policy side effects** (AUTH-17/21) | A transparent proxy changes who sees tokens/prompts; Copilot model enabling changes account settings | More deliberate setup; no automatic relay fallback or model enablement inside login |
| **D18. Keep inference canonical and stateless** (AUTH-23) | A string-returning chat wrapper or hidden history/agent loop would change LM15's foundation | Bound-client sugar constructs ordinary Requests; users still own conversation, SQL/UDF execution and retry policies |
| **D19. Literal key entry, not a secret-command mini-language** (AUTH-16) | Interpreting pasted keys as shell/env expressions introduces execution and injection into an innocent form | Advanced users supply explicit credential providers or approved cloud recipes instead |
| **D20. Local AuthOperationError reasons, not synthetic 401s** (AUTH-24) | Expired attempts, lost races and broken stores are not provider credential rejection; errors cannot safely share automatic retry behavior | New root code and closed reason vocabulary; ordinary model/API-key/cloud HTTP errors are unchanged |
| **D21. Bounded attempt defaults; retention details reserved** (AUTH-18) | Infinite polling/private-state retention makes leaks and abandoned grants permanent; provider expiry alone may be absent | Local login defaults to 15 minutes (explicit finite budget allowed before begin, never beyond provider expiry); 24-hour terminal retention and scope-lifetime tombstones remain reserved, not first-rollout requirements |
| **D22. No runtime/fixture claims from this specification** (AUTH-26) | A green documentation check or Python-only unit suite is not SDK/provider parity | Follow-on harness, cross-language race, UI and authorized live tests remain required; support matrix/pins stay unchanged |

## Compatibility boundary

`oauth` and `oauth-unless-explicit` are **not retired**. Existing Claude/Codex
access and xAI subscription precedence remain until the ratified replacement
gates pass. The new `connection` policy is additive, not permission to reclassify
xAI as env-key-only. Login methods describe protocols separately from authority.
No auto-import or independent copy of rotating foreign credentials is introduced;
LM15's locks do not coordinate foreign tools. Safe coexistence needs evidence.

The following **existing callers retain their behavior** when managed Auth is not
attached: explicit API keys/credential callbacks, shared explicit keys, declared
environment order, local placeholders, named Azure/AWS/GCP credentials, default
cloud chains, cloud endpoint overrides, JWT-to-bearer handling and error provenance.
Their fixtures must not be weakened to make managed mode look green.

With managed Auth attached, explicit credentials/named identities still win on a
general router. Otherwise eligible subscriptions are preferred within the
selected scope; multiple eligible accounts require choice. Absence/failure in
managed mode does not authorize ambient fallback. A bound
client has no per-request identity override at all. `auth.status()` describes the
store; the router doctor describes the actual request selection, including any
explicit override. Login returns metadata, never a public token bag.

## Normative consequences and evidence gates

- `spec/auth.md`: revised entry rules/boundary and links to AUTH-12–26; long cloud
  chain/named-credential/endpoint rules preserved.
- `spec/vocabularies.md`: additive `connection` policy and `auth_operation` root code;
  managed-only vocabularies live in the supplement rather than pretending they are
  current canonical Request fields.
- `spec/SCOPE.md`, `playbooks/api-family.md`: ratified core managed/auth convenience
  surface and narrowly scoped exception for model-bound request construction.
- `docs/auth-examples.md`: non-executable language-native illustrations, no Python
  reference algorithm used as an oracle.
- `auth/managed/`: deterministic resolution vectors, lifecycle/platform scenarios,
  schema examples and conformance protocol requirements. New harness/runtime work
  is not performed here.
- `tools/check_managed_auth.py`: checks these specification artifacts and includes
  bad-artifact mutation self-tests. This is not a login engine, SDK implementation
  or behavioral conformance runner.

Ratification is not a reason to revise live wire fixtures or recorded receipts.
`auth/managed/README.md` identifies the retained subscription fixtures and the
single corrected xAI fallback expectation. Their gate remains active; no archive,
skip, broad policy retirement or claim of SDK conformance follows from ratification.

## Follow-on work, not hidden decisions

Implement the specified native types, private schemas/store guarantees and
scenario-driving harness; supply evidenced provider flow profiles; port primitives
and integrations in Python then TypeScript; add terminal/custom UI and model discovery;
implement the thin bound client; extend/deploy a relay only with its own security
review and consent model; collect platform/account receipts with permission.

No production design choice is delegated to "whatever Python does". Runtime
implementation techniques may vary only while meeting the same externally
observable ordering, safety, I/O and error rules.
