# Managed-auth acceptance scenarios

**REVIEW DRAFT, 2026-09-22. Required tests, not a report of tests already passing.**

Rules: [AUTH-12–26](../../spec/auth-managed.md). Driver/evidence levels:
[README](README.md). Every scenario runs against public SDK operations with fake
HTTP, private sandbox storage, injected complete environment, deterministic time
and scheduling barriers unless explicitly labelled integration/live. No real
credentials, paid inference or user HOME access are needed for deterministic tests.

For all scenarios, assert both the expected result **and forbidden effects**.
Examples: "no fallback" means a trap credential callback/transport was not invoked,
not just that the final error text looks right. Seed secret sentinels in all private
channels, including errors, and assert their absence from every public rendering.
Capture ordering before redacting private traces in the comparator.

## A. Discovery and source selection

### MA-001 — Construction is inert (AUTH-13/14/17)

Given traps on file access, lock creation, HTTP, browser opening and subprocesses,
construct local and memory Auth, clone a handle, enumerate providers/methods, and
construct an explicit bound client. Assert no trap fires. Descriptors may read
loaded definitions and declared host capabilities only; construction must not
probe whether the configured account is real.

### MA-002 — Names are discoverable but not authority (AUTH-13)

Enumerate named built-ins and an explicitly registered custom provider. Feed the
returned descriptors into login. IDs/labels round-trip; labels are not accepted as
IDs. Feed a descriptor from another registry revision carrying an attacker URL:
reject before browser/network/storage mutation; do not register it implicitly.

### MA-003 — A missing choice asks, never guesses (AUTH-13/16)

Two supported providers/methods remain. With UI, show their stable option IDs and
use the returned choice, independent of definition order. Without UI, fail
interaction_required before external authorization. A single supported option may
proceed with visible identity guidance; unavailable/unverified options are not
silently selected.

### MA-004 — Resolution vectors agree with actual use (AUTH-15)

Replay every `resolution.json` case through inspection and public request
preparation. The decision-phase trace has zero network/callbacks/writes. Subsequent
fake acquisition uses only the selected source or refuses with the pinned reason.
Reorder maps to prove order is not an identity-selection rule.

### MA-005 — Explicit credential failure is not a fallback (AUTH-15/20)

A selected explicit callback raises; ambient key and saved login both exist. Assert
only that callback was invoked once for the request. No ambient credential, store
renewal or model call follows. The offline doctor never invokes the callback.

### MA-006 — Managed cloud recipes are deliberate (AUTH-15/17)

With empty managed Auth, plant working Azure CLI/platform credentials and an API
key; no cloud source is invoked. Configure a saved `platform` recipe: only the
existing named rungs run on explicit use. Configure `chain`: its existing order and
provenance remain. A failing named source never broadens into the whole chain.

### MA-007 — Existing API-key and Azure regression boundary (AUTH-15/26)

Run unchanged unmanaged shared-key, key-kind/header, JWT, named-cloud, endpoint and
error-provenance fixtures. Add a managed file on disk and show their source/wire
is unchanged. Do not retain the ten retired implicit-login vectors as obligations
of the new managed mode (README lists them).

### MA-008 — Scope/instance separation (AUTH-12/14/15)

The backend contains Bob's valid connection and Alice's missing one for the same
provider, plus a connection for a different enterprise instance. Alice's request
cannot read/select/renew either. A forged scope/instance in a descriptor or HTTP
callback is not permission. Return no metadata revealing Bob's account exists.

### MA-009 — Binding ownership is explicit (AUTH-12/13/15)

Two sibling routes deliberately share one binding; connect once and resolve both.
Logout through its selected connection removes access for both and reports them.
A similarly named route/host with no declared binding cannot use the credential.
Conflicting binding owners fail registration; two otherwise valid configured
instances without a selection fail interaction_required, not last-used selection.

## B. Protocol and interaction

### MA-010 — Connected and resumable login are one protocol (AUTH-16/18)

Run identical fake approval once through `login` and once through begin/resume on
two process instances sharing the store. Expected authorization/token requests,
scopes, final connection and private material are equivalent; UI scheduling aside,
neither path has extra requests or a second protocol implementation.

### MA-011 — PKCE and randomness (AUTH-18)

Pin RFC 7636 Appendix B S256 output. Production-platform tests generate valid
43–128-character unreserved verifiers with cryptographic entropy; independently
generate state. Concurrent attempts have different verifier/state/opaque IDs.
Deterministic test randomness is explicitly injected, not a production fallback.
A profile without state requires its documented equivalent return binding.

### MA-012 — Validate errors as well as success callbacks (AUTH-18)

While awaiting a legitimate return, deliver wrong path, wrong state, duplicate
code/state parameters, wrong issuer context, and an error callback with wrong
state, and a mixed success-code/error return. Reject them with generic escaped
pages, no token exchange and no termination
of the legitimate wait. A valid-bound denial terminates as login_denied.

### MA-013 — Bind address is not redirect URI (AUTH-18/22)

A profile registers `http://localhost:1455/auth/callback` and binds 127.0.0.1.
Exchange uses the exact registered URI. Reject wildcard/LAN listeners. Occupy the
port: fail or explicitly select a supported manual/device mode; never widen the
bind, pick an unregistered port, or claim success while no return can be received.

### MA-014 — Native HTTP listener hardening (AUTH-18/21)

Submit non-GET callbacks, oversized URLs, malformed encodings, duplicate query
parameters and HTML/terminal control text. Reject safely; no raw code or URL in
logs/errors. Browser success/error pages have no-store and safe content/referrer
policy. Closing/cancellation releases the port. No listener is imported/created on
a browser runtime merely to enumerate methods.

### MA-015 — Manual input races callback (AUTH-16/18)

Show a paste prompt; deliver the valid callback first. UI receives prompt
cancellation, the callback owns the single exchange, and a delayed pasted answer
cannot exchange again or change the committed connection. Repeat with manual input
winning first and with UI cancellation winning before either.

### MA-016 — Device polling pace and deadline (AUTH-18)

With provider interval omitted, first follow the profile's initial-wait rule and
then use 5 s minimum default between polls. Feed pending, slow_down without interval,
slow_down with a smaller interval, and slow_down with a larger required interval.
Intervals never shrink and grow by at least 5 s on slow_down. Early manual poll
returns next_poll_at with zero HTTP. At expiry no new poll starts. Test finite
interval validation and monotonic waits with a changed wall clock.

### MA-017 — Device approval can include a second exchange (AUTH-18/20)

A poll returns an authorization result requiring a token/key-mint exchange.
Complete that documented sequence once, not an invented generic bearer token.
A one-poll resume may perform its bounded follow-on exchanges but never wait
indefinitely or start another pending poll inside that same advancement.

### MA-018 — Preflight local prerequisites before authorization (AUTH-17)

Inject read-only store, missing lock support, absent required callback capability
and unavailable browser storage. Login fails before device-start HTTP or browser
opening. No silently substituted memory store. Also inject a failure after this
check: login must not announce durable success until commit actually succeeds.

### MA-019 — Prompt typing and literal secrets (AUTH-16)

Text, secret, select and manual-code prompts share stable field/prompt IDs.
Reject undeclared select IDs and stale step revisions. A key starting with `!` or
containing `$NAME` is stored literally; no command/environment expansion occurs.
A secret has no prefilled saved value. Callback exceptions are sanitized failures.

### MA-020 — Untrusted approval URLs cannot launch programs (AUTH-18/21)

A device/authorization response offers a file/custom scheme, wrong issuer host,
userinfo URL, or unexpected redirect host. No browser/system launch, token request
or following redirect occurs. Only the evidenced profile's trusted HTTPS approval
policy is accepted; a new enterprise gateway must be configured explicitly.

## C. Attempt ownership and lifecycle

### MA-021 — Attempt IDs do not authorize access (AUTH-14/18)

Bob knows Alice's real attempt ID. Read/resume/cancel as Bob produces the same
attempt_unavailable behavior as an unknown ID, with no Alice metadata or HTTP.
Changing the claimed scope in the request does not change the server-authorized
scope. Anonymous callback code alone is not an application-session identity.

### MA-022 — One active attempt per binding (AUTH-18)

Begin twice concurrently in one slot. Exactly one reservation wins. The other gets
login_in_progress and authorized recovery, not another browser/device-start call.
Attempts in different bindings/scopes can proceed independently where supported.
A direct set_api_key/configure into the reserved slot also returns login_in_progress;
it cannot bypass reservation or silently overwrite a pending approval.

### MA-023 — Duplicate delivery before/after commit (AUTH-18/25)

Send the same callback from two workers at a barrier. One owns the exchange; the
other observes pending or the retained result. Deliver it again after commit:
return the same committed Connection ID without HTTP. Wrong-step answers cannot
advance. No shim-only deduplication separate from SDK/store behavior.

### MA-024 — Attempt expiry and retention (AUTH-18)

Begin at fixed time with no provider deadline: 15-minute local default. An explicit
20-minute local budget at begin is allowed, but a shorter provider/caller deadline
wins and no resume extends it. Once expired, no poll/exchange/commit may proceed.
Terminalization/prune erases private state; safe metadata remains for 24 hours after
termination. Read-only inspection reports logical expiry without claiming disk
cleanup. Test a stopped process: validity still expires, physical deletion requires
later prune/backend TTL. Restart does not reset expiry; purged lookup returns
attempt_unavailable.

### MA-025 — Replacement is conditional, old connection remains usable (AUTH-19)

Save C1. Unconditional setup refuses connection_exists. Begin explicit replacement
of C1/generation G; while approval waits, requests through C1 still work. Cancel,
deny and expire separately: C1 stays. Complete: new C2 ID and G+1 atomically replace
C1, and the attempt receipt names C2. Renewal of C1 alone does not change G.

### MA-026 — Competing identity changes cannot be overwritten (AUTH-19)

Begin replacement against G, then commit logout or a different explicit replacement.
Release the original exchange result. It cannot commit against the new generation,
create an orphan credential or overwrite the winner. It becomes superseded with
connection_changed, and secrets from its terminal attempt are erased.

### MA-027 — Cancel before exchange, during approval and during exchange (AUTH-19)

Place cancellation at each barrier. Stop new work, dismiss prompts, release owned
resources. If a remote grant was already made, do not imply it was revoked. If no
local commit occurred, the old connection remains. A possibly consumed exchange
is not retried by restarting the same attempt.

### MA-028 — Cancel versus commit has one durable winner (AUTH-19)

Run both orderings. Cancel commits first -> no credential commit can succeed.
Credential commit first -> cancel_login returns complete, not a false cancelled
result. A native caller cancellation that loses delivery can inspect attempt(id)
to discover the result. The UI must not claim nothing was saved from task abort
alone. No provider revoke request is used as hidden compensation.

### MA-029 — Logout is scoped, idempotent and generation-safe (AUTH-19)

Logout C1: clear its secrets, increment tombstone generation, cancel its pending
attempts, invalidate caches. Repeat after C2 replaces it: C2 survives. Other scopes
and bindings, environment keys and cloud/foreign files are unchanged. No remote
request, subscription cancellation or claim of provider-wide logout.

### MA-030 — Logout versus request dispatch (AUTH-19/20)

Pause after reading credentials but before local dispatch admission. Logout commits
first -> the request cannot send. Reverse order: already admitted bytes may be
sent/completed; diagnostics do not claim remote revocation. Future requests fail.
Repeat with a client cache populated before another process performs logout.

### MA-031 — Closing is not logout or global teardown (AUTH-14/23)

Close a bound client: owned resources released; saved connection remains. A shared
caller-owned Auth/transport remains usable by another client. Closing a manager
stops its connected operations according to durable cancellation rules; detached
begin/resume attempts survive until deadline unless explicitly cancelled. No
process-global default is changed.

## D. Renewal, uncertainty and storage

### MA-032 — Renewal is double-checked across requests/processes (AUTH-20)

Two requests read an expiring credential. Barrier before lock acquisition. One
renews and commits credential revision R+1; the other re-reads it and does no
renewal. Both snapshots use its matching token/account headers/endpoint. Repeat
with two different SDK languages sharing the real file-store lock (integration).

### MA-033 — Expiry uses actual time, not double-subtracted skew (AUTH-20)

Issue a one-hour token at 10:00: expiry 11:00, renewal due 10:55. Issue a one-minute
token at 10:00: expiry 10:01, renewal due 10:00:54. Save/reload from another language:
identical times. Unknown expiry is not never. A freshly renewed short token can
serve a request with sufficient validity without an immediate second renewal.

### MA-034 — Non-expiring minted keys do not invent refresh traffic (AUTH-20)

A documented key-mint method yields explicit expiry=never and renewal=none.
Requests at later times do not renew. Provider rejection still fails; never means
no automatic expiry, not irrevocable authorization. No maximum-integer timestamp.

### MA-035 — Meta-like renewal is not necessarily refresh_token grant (AUTH-20)

A fake identity token mints a short-lived model key. Renewal mints another key,
retains the identity material and persists before model dispatch. Identity rejection
marks needs_login; an unsupported attempt to refresh the identity is not invented.
Flow details for real Meta must later be pinned by its own evidenced profile.
For any profile with a stable authenticated account identifier, return a different
identifier on renewal: refuse connection_changed rather than silently changing
the principal behind the same bound client. Opaque tokens are not proof of a
verified human account label.

### MA-036 — Definitive rejection versus safe transient failure (AUTH-20/24)

Feed an evidenced permanent invalid_grant -> needs_login and unusable secrets
removed; no environment fallback. Feed a documented definitely-not-consumed
transient response -> credentials retained, operation fails retryably, no hidden
retry. Unknown provider text alone is not enough to classify a failure permanent.

### MA-037 — Crash after rotating exchange is not exactly-once magic (AUTH-20/25)

Persist in-flight marker, let fake provider rotate, kill worker before local commit.
Restart: marker proves possible consumption; do not repeat the old refresh. Mark
indeterminate and require profile-supported reconciliation or new login. Repeat for
code exchange. A lost database lease/fencing token while network work may continue
must not permit a second remote exchange merely because the lease expired.

### MA-038 — Storage failure after authorization never reports success (AUTH-19)

Provider returns a valid grant; commit fails before durable write. No Connection
success result, old connection preserved, private failed-attempt secrets erased
when terminalization is possible. Failure says not saved. Simulate unknown commit
outcome separately: report unknown, inspect before reauthorizing; don't assert old
state remained when it may not have.

### MA-039 — Logout or replacement wins against stale renewal commit (AUTH-19/20)

Hold a renewal result and arrange a newer identity generation before its commit
through a supported concurrent/lease-loss schedule. Stale owner cannot write. If
serialization prevents that schedule in the backend, assert logout waits within
its budget and then invalidates the fresh result. Both implementations yield no
post-logout resurrection, not necessarily identical internal lock timing.

### MA-040 — Schema and cross-record invariants (AUTH-25)

Replay store-vectors.json with date-time checking. Additionally reject duplicate
IDs, cross-scope references, orphan credentials, slot/generation mismatch,
terminal reserved attempt, complete without result, negative lifetime,
request/material expiry disagreement, wrong kind/material pairing and unknown
required profile revision. At the raw parser boundary reject duplicate JSON members,
non-finite numbers and invalid UTF-8 in stores and auth replies before map conversion.
No overwrite, memory fallback or secret rendering. An invalid reply after a possibly
consumed exchange is uncertainty, not permission to repeat that exchange.

### MA-041 — Large revisions and tombstones survive languages (AUTH-25)

Use generation/revision decimal strings above 2^53, write in one SDK and load in
another without rounding. Logout and recreate a slot; old generation cannot match.
Keep tombstones for scope lifetime. Recreate the whole scope with a new epoch;
old selections/attempts cannot bind even if user-visible scope ID is reused.

### MA-042 — Real locking and crash-safe private writes (AUTH-4/25)

Integration: aliased/symlinked paths identify the same guarded file, contention
returns LockTimeoutError, no secrets in path errors. Process death releases native
locks but leaves detectable in-flight work. Readers observe old or new complete
JSON, never a partial file. Validate required Unix permissions/Windows ACL behavior,
atomic replacement and declared durability, not just in-memory mutex tests.

### MA-043 — No secrets retained in terminal attempts (AUTH-18/21/25)

Complete, deny, cancel, expire, supersede and fail independently. Inspect private
storage: no verifier/device code/grant material remains in terminal attempt records.
Safe completion receipt can remain even after its connection is logged out, but
cannot itself authenticate or recreate the deleted connection.

## E. Secrecy, networking and platforms

### MA-044 — Adversarial error/redaction boundary (AUTH-21/24)

Plant sentinels in tokens, device code, verifier, return URLs, provider descriptions,
HTTP bodies, nested causes and arbitrary cancellation reasons. Print/debug/serialize
public status, selections, errors and SDK traces: none emits private material or
session-sensitive URLs/codes. The initiating UI receives only the intended URL/user
code. Store/HTTP adapters can receive private data only as their explicit duty.

### MA-045 — Destination policy guards every credential-bearing stage (AUTH-20/21)

Inject a token with a malicious dynamic endpoint, a catalog advertising a new host,
an unexpected 3xx, and a caller base-URL override to an unrelated server. No secret
is forwarded. A separately configured trusted gateway binding can work, but changing
its issuer/client/relay/allowed-destination revision invalidates old attempts and
bound selections. Test DNS/private-network SSRF controls for custom server gateways.

### MA-046 — Relay consent is narrow and explicit (AUTH-21/22)

A direct request fails with a browser network error. No relay retry occurs. Permit
catalog-only relay to R1; inference/token exchange cannot use that consent. Changing
to R2 requires consent again. UI describes token/identity/prompt transit accurately.
Origin allow-listing does not authorize cross-user scope access or an open proxy.

### MA-047 — Login and model enablement are separate effects (AUTH-17)

Fake Copilot returns available and unconfigured models. Login succeeds without
policy-changing enable calls. A separate explicitly authorized action may enable
models and reports its own failure; it does not retroactively label valid login
failed. Similarly no paid inference test or cloud-resource creation inside verify.

### MA-048 — Browser/module capability boundaries (AUTH-13/22)

Load discovery, types and pure request construction in an actual browser realm
without node/http/fs modules. Unsupported loopback/foreign-file/ambient CLI methods
are unavailable before clicking. Browser WASM has the same constraints; the language
name does not silently select a proxy or native escape hatch.

### MA-049 — Redirect/session integration (AUTH-18/22)

Integration: two browser sessions start logins, then exchange callback URLs. Neither
can commit the other's credential. Cross-site return missing its app session must
restore/verify ownership, not infer scope from code. CSRF-protected begin/cancel/
logout and callback binding are exercised; scrub URL and prohibit referrer/analytics
leakage. Browser-only storage lost on navigation reports missing attempt, not guessed
state. Provider-approved redirect registration is a separate live requirement.

### MA-050 — Device/SSH integration (AUTH-18/22)

Run SDK on a remote/headless host, browser on another host. Device-code flow works
without callback listener. Manual redirect works only for supported profiles and
valid attempt context. Terminal helper does not open a browser on the remote host
when disabled. No localhost callback or arbitrary port substitution is assumed.

### MA-051 — Native cancellation mechanisms and finite waits (AUTH-19/22)

For each SDK cancel during UI wait, sleep, HTTP, lock wait and result delivery.
No new requests after cancellation, no leaked listeners/tasks, no raw traceback
with secrets. Async APIs use native nonblocking waits; Python in a running notebook
loop is not subjected to hidden asyncio.run(). Durable commit races follow MA-028.

### MA-052 — Verification is explicit and accurately limited (AUTH-17/24)

Status/listing do not refresh, execute callbacks or use the network. verify with a
supported check performs only that check (plus required renewal), reports timestamp
and check ID. Unsupported check returns unverified with zero inference. A public
model list accepting any key cannot be treated as proof of credential validity.
Race verification/catalog completion with logout/replacement: the old result cannot
be persisted as a verification or catalog of the new Connection ID.

### MA-053 — Account metadata is escaped and not public telemetry (AUTH-12/21)

Provider sends an account label containing HTML, terminal escapes or a secret echo.
Render safely and apply bounded/profile-approved metadata extraction; do not copy
an arbitrary response as account metadata. Decoding a JWT for a required request
header does not establish verified identity or app-session ownership.

## F. Model selection and convenience

### MA-054 — No mystery strings on the happy path (AUTH-13/23)

Bare interactive connect offers saved connections/new providers and model choices,
using returned descriptors/IDs end to end. No user must type an internal provider
ID; the resulting canonical Request still contains the exact routed model.
Unknown service labels are not silently treated as provider aliases.

### MA-055 — No UI or network magic in a server (AUTH-16/23)

Call bare interactive connect without a TTY/UI. Fail interaction_required before
reading a saved credential or starting authorization. Supplying explicit app UI
and scope is allowed; it still does not install global identity or mutate env.

### MA-056 — Catalog provenance and capability filtering (AUTH-23)

Combine bundled, cached, account-listed and manual model choices with timestamps
and supported/unsupported/unknown structured-output evidence. Strict filter offers
only supported choices. Catalog fetch fails -> show error; cached/manual choice
requires explicit labelled selection. Never send an inference probe to test support.

### MA-057 — Catalog choice is not authority to change destination (AUTH-20/23)

An account catalog names a model/route outside the connection's declared binding.
Exclude/refuse it; do not acquire credentials for a different host. Same bare model
name under two routes remains two choices. Provider catalog data cannot register
new code, arbitrary auth callbacks or a new relay.

### MA-058 — Saved login survives later picker cancellation (AUTH-23)

Login commits C1, then user cancels model choice (or catalog fails). No bound client
is returned; C1 stays saved. UI/error recovery metadata says setup already committed
and identifies C1 safely. No automatic logout/revoke. Repeat when connect merely
reused an existing connection: no unnecessary new login or writes.

### MA-059 — Bound client is thin and canonical (AUTH-23)

Given same messages/tools/config, bound-client sugar and its pure request()
produce the same canonical Request and provider bytes as explicit router code.
complete returns full Response; stream returns canonical events. No history,
string-only return, hidden retries or tool execution. Wrong Request.model fails
selection_mismatch before credential acquisition.

### MA-060 — Bound identity versus general router replacement (AUTH-15/23)

Bind a client to C1. Refresh C1 -> client continues with new material. Replace with
C2 -> old client fails connection_changed. A general managed router explicitly
configured to follow that slot sees C2 on its next request and reports it. It still
cannot fall back to ambient identity after C2 logout.

### MA-061 — Reproducible classification composition (AUTH-23)

Fixture cookbook: a bound model receives independent row requests, including a
blank-row skip implemented by the app. Validate constrained returned labels; no
invented probability/confidence when the provider reports none. dplyr/purrr and
DuckDB compose existing request operations; export from a materialized result does
not secretly re-run classification. Re-executing SQL can still reissue calls and
must be documented, not marketed as exactly-once processing.

## G. Release and completeness gates

### MA-062 — Per-provider exceptions and real wire evidence (AUTH-20/26)

Profile suites cover Claude browser/manual, Codex browser/device, Copilot second
token/account endpoint/catalog, xAI device, Kimi coding endpoint, Meta key mint,
OpenRouter non-expiring key and Radius gateway discovery/protocol. Use docs/live
provenance for exact requests; fake-provider success alone is not a live support
claim. No Gemini CLI/Antigravity login or hidden ninth built-in requirement.

### MA-063 — Packaging prerequisite failures (AUTH-17/22)

Integration on claimed OS/runtime: missing TS lock addon/flock, R callback packages,
read-only directories, inaccessible database and browser storage quota/private-mode
failures surface before approval when detectable. No unsafe unlocked write or
silent memory fallback to make the happy-path screenshot work.

### MA-064 — Same behavior in all ten languages, separate platform claims (AUTH-26)

Publish results per SDK and native/browser/mobile/server profile against one
contract revision. Existing API-key/cloud gates remain green. Add the mutation
self-tests required by README. No skips counted as implementation, no fixture
rewrites to fit Python, and no source-only/browser-preflight success sold as a live
account login. Authorized live tests explicitly disclose approval, data and cost.
