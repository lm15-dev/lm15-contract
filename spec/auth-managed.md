# Managed authentication and interactive connection — core

**Status: REVIEW DRAFT, 2026-09-22 (core tier). Normative candidate, not an
implementation or support claim.**

This is the managed-authentication part of [auth.md](auth.md), numbered AUTH-12
through AUTH-26. It is split in two tiers:

- **Core (this file).** The rules a first implementation (xAI migration, then one
  browser login) must obey, and the decisions the maintainer must ratify now. See
  the [one-page ratification list](../changes/2026-09-22-managed-authentication-ratification.md).
- **Reserved ([auth-managed-reserved.md](auth-managed-reserved.md)).** Rules
  written for situations no implementation has met yet: multi-process web servers
  resuming a login, database/lease stores, relays, remote provider definitions,
  serialized selections. They are design notes. Each states what must exist
  before it is promoted to core. Until then they bind nobody.

The reserved text was written first and moved out unchanged on 2026-09-22 so it
can be pressure-tested by real flows before it hardens. A rule that the first two
implementations contradict is fixed in the spec, not worked around in code.

MUST, MUST NOT, SHOULD and MAY are normative (RFC 2119/8174). A SHOULD exception
must be stated and tested. Language spellings in examples are illustrative; operations, results and state transitions are the
contract. Python is not the oracle.

## Reading map

| Question | Rule |
|---|---|
| What are we connecting? | AUTH-12 |
| How do I discover the choices? | AUTH-13 |
| What owns the saved identity? | AUTH-14 |
| Which identity is actually used? | AUTH-15 |
| What must my UI implement? | AUTH-16 |
| Which operations perform I/O? | AUTH-17 |
| How does a login run, and what protects it? | AUTH-18 |
| What do cancel, replace and logout mean? | AUTH-19 |
| How is a credential renewed and sent? | AUTH-20 |
| What is secret, and where may it go? | AUTH-21 |
| What differs between a terminal, a browser and a server? | AUTH-22 |
| What does `connect()` return? | AUTH-23 |
| What can fail, and what is safe to retry? | AUTH-24 |
| What must a store guarantee? | AUTH-25 |
| How is this proved in every SDK? | AUTH-26 |

Companions: [worked examples](../docs/auth-examples.md),
[acceptance scenarios](../auth/managed/scenarios.md) (tiered the same way),
[resolution vectors](../auth/managed/resolution.json),
[conformance boundary](../auth/managed/README.md),
[decision log](../changes/2026-09-22-managed-authentication.md).

## AUTH-12 — Vocabulary and ownership

| Term | Exact meaning |
|---|---|
| **Service** | A presentation group, such as Anthropic or OpenAI. It grants no routing, identity or credential-sharing permission. |
| **Provider / route** | A registered LM15 access path with one wire behavior, e.g. `anthropic`, `claude-code`, `openai-codex`. Existing provider string rules apply. |
| **Provider instance** | A trusted configured deployment of a provider definition: public service, a particular enterprise domain, or a particular gateway. A different credential destination is a different instance. |
| **Login method** | A named way to establish a connection for that instance: account authorization, an API-key form, a cloud-source recipe, or local-server configuration. Not an account and not a pricing plan. |
| **Credential binding** | An explicit declaration of the routes, request protocols and destinations a connection may authenticate. Never inferred from display names or similar URLs. |
| **Scope** | An application-authorized storage namespace, such as a local profile or an application user's private store. A scope string alone is not authorization to access it. |
| **Connection** | Secret-free metadata for one saved credential or source recipe in a scope. `kind` is `account`, `api_key`, `cloud_identity` or `local_server`. |
| **Credential** | Secret-bearing material used for a request or renewal. AUTH-2 request credential kinds remain unchanged. An account flow may produce an API key rather than an OAuth access token. |
| **Attempt** | A finite, private-state login operation, including collecting settings, approval, exchange and commit. Not a conversation and not an application-user session. |
| **Model selection** | An exact route and model ID bound to a particular connection ID and provider-instance/binding definition. Not merely a bare model-family string. |
| **Bound client** | The result of `connect()`: an explicit model selection plus the scoped services needed to resolve its authentication for each request. No conversation memory. |

A binding slot is addressed by **(scope, provider instance, binding ID)**. Version
1 allows one active connection per slot; applications wanting separate personal
and work connections use separate scopes or explicit configured instances. There
is no global current account, implicit account rotation or fleet-wide account
picker. This is a stated limit, not an accidental restriction of a string-keyed
file.

A Connection has at least `id`, `instance_id`, `binding_id`, `kind`, `method_id`,
`routes`, `label`, `created_at`, and an identity generation (AUTH-19). Optional
provider account labels are untrusted display text: do not claim an email/name
was verified because it was decoded from an unverified JWT. Metadata may be
personal even when it is not a credential: safe from secret leakage is not
permission for public logs.

**Ownership:** login returns a Connection, not tokens. The Auth manager owns
lifecycle orchestration; the chosen store owns persistence; the app owns scope
and presentation; the provider owns authorization and billing. UI/storage
callbacks and provider plugins are trusted application code, not a sandbox.

Provider-instance security revisions and their effect on existing attempts are
reserved (AUTH-12 reserved).

## AUTH-13 — Discovery, descriptors and availability

1. Built-in providers MUST have discoverable named descriptors appropriate to the
   language (`providers.openai_codex`, `providers.openaiCodex`, etc.). Functions
   also accept registered stable IDs for configuration and custom providers.
   Unknown IDs fail before credential access or network I/O. Labels are never IDs.
2. `providers()` and `methods(provider?)` return immutable descriptors using only
   loaded definitions and declared host capabilities. They do not read credential
   files, execute credential callbacks, refresh, resolve DNS or contact providers.
3. A method descriptor contains `id` (within an instance), `label`, `kind`, `flow`,
   declared input fields, route binding, availability and provider-specific
   guidance. Fields name stable IDs, type (`text`, `secret`, `select`), requiredness
   and safe labels/options. No saved secret is a default or a placeholder.
4. `flow` is `authorization_code`, `device_code`, `form` or `source_recipe`.
   A method may expose supported delivery modes: loopback, manual return, page
   redirect, device approval. It MUST NOT advertise a mode not implemented and
   accepted by that provider's client registration. Device login is not assumed
   solely because an account login exists.
5. Availability is `supported`, `unavailable` or `unverified`, with a reason.
   Supported means the SDK/platform implementation and recorded evidence permit
   attempting it, not that this account qualifies or today's network is reachable.
   Unavailable methods are not selectable. Unverified methods are excluded from
   default pickers; explicit programmatic opt-in must identify that uncertainty.
   Implementation, browser/CORS evidence and live account eligibility are separate
   dimensions; an HTTP preflight is not an end-to-end login receipt.
6. The UI may group by service; operations remain instance/method/route-specific.
   If multiple methods or providers remain after filtering and the caller omitted
   a choice, ask through the supplied UI. Without a UI, return
   `interaction_required` before authorization I/O. Do not choose by list order.
   A single supported option may be selected mechanically, but the interactive
   helper still shows the selected identity/access path before authorization.
7. Account login MUST NOT be labelled free, unlimited or included merely because
   it is OAuth. `kind=account` includes credit-funded key minting. Billing notices
   distinguish known provider policy from unknown account entitlements; no filter
   named subscription can promise an allowance the SDK has not established.

Remote definition loading and descriptors received from another registry
revision are reserved (AUTH-13 reserved).

## AUTH-14 — Manager construction and explicit scope

An Auth manager binds a store scope, trusted provider definitions and platform
services. Construction validates arguments but does not read secrets, create
files, probe storage permissions, launch a helper or use the network. `local()`
chooses AUTH-8 paths explicitly; `memory()` is process-lifetime storage. Other
stores are application-supplied. Construction is not sign-in. Local path/default
selection captures its nonsecret configuration and absolute path anchor at
construction; a later working-directory change must not silently choose a
different store. Physical path/permission checks happen only at an explicit
store operation.

Closing a manager cancels connected operations it owns under AUTH-19, releases
owned platform resources, and never logs out. Closing a bound client does not
close a caller-owned manager or transport. All close operations are idempotent;
they do not install/remove a process-global identity.

Every operation and cache is scoped. Scope namespacing is part of the store's
authorization boundary, not a string concatenated into a filesystem path. A
server MUST derive scope from its own validated application session, never from
an untrusted provider name, callback parameter or tenant field. Sharing a store
backend between Auth instances does not share identity unless the authorized
scope and binding are deliberately the same.

Managed operations do not discover or copy Claude Code, Codex or Pi credential
files. There is no automatic migration, compatibility wrapper or implicit
foreign-store fallback. A future import feature is a separate design: copying a
rotating refresh token can break both consumers, and LM15 locks do not coordinate
foreign tools. Existing cloud-file discovery under AUTH-1 is different and
remains supported.

## AUTH-15 — Identity selection, with and without a manager

There are two explicit construction modes; not an environment-driven production
heuristic.

### A. No managed Auth attached

Existing API-key and cloud callers keep AUTH-1/2/7/10/11 behavior: explicit values
and credential providers, shared explicit-key rules, declared environment keys,
keyless placeholders, named cloud identities, cloud chains and endpoint settings.
No new managed file is searched. Account-only routes require an explicit accepted
credential or an attached Auth; they do not borrow another tool's login. The
retired `oauth`/`oauth-unless-explicit` implicit-file rules are not preserved.

### B. Managed Auth attached to a general router or adapter

For the exact requested route:

1. Select an explicit credential entry, including AUTH-1's shared explicit-key
   rule. An empty value, ambiguous shared entry or failing selected callable is an
   error, not permission to continue. A simultaneous named cloud identity is a
   construction error, as today.
2. Otherwise an explicit named cloud identity selects exactly its existing rungs.
3. Otherwise select the active connection in the one declared binding slot for
   this route/instance in the attached scope. If routing/configuration leaves
   multiple possible instances or bindings, require a selection; do not choose by
   insertion order, model name, hostname similarity or last use.
4. An absent connection produces `login_required`. Revoked, expired-unrenewable,
   uncertain, unreadable and malformed selections fail by their own reasons.
   **None falls through to environment keys, foreign files, another connection or
   the machine's cloud identity.**
5. A truly keyless local route remains usable without identity. It is not a
   general bypass for an unconfigured hosted provider.

A saved cloud connection is a **recipe**, not a captured token: one named identity
or an explicitly chosen default cloud chain, plus its declared settings and allowed
destination policy. Executing that selected recipe uses the existing cloud rules,
including their settings/environment behavior and provenance. A chain can change
its selected principal when its inputs change; the UI/doctor MUST name this fact.
A strict single-principal deployment uses a deterministic named credential or its
own credential provider.

For managed account/key/local connections, host/endpoint settings come from the
saved connection and trusted explicit configuration, not ambient endpoint
variables. An override may narrow/refine the allowed destination; it cannot send
an account token to an unrelated host. To change trust, explicitly configure a
new binding/instance and connect it. Existing **unmanaged** API-key/cloud
endpoint overrides are unchanged. An explicit credential override in mode B is
deliberate application configuration; its source and effective endpoint must be
visible in router diagnostics. `auth.status()` alone cannot describe that request.

### C. Client returned by `connect()`

A bound client pins the connection **ID**, provider instance, route and model. It
follows credential renewal of that ID, not a slot's later replacement. No
per-request account, credential, route or model override is accepted.
Replacement or logout makes the old client fail `connection_changed` or
`login_required`, never follow the new identity. Deliberately call `connect()` or
bind a new selection to use the new connection. Generic managed routers, by
contrast, consult their active slot on each request and expose that source.

**Trade-off:** attaching managed Auth disables ambient convenience. This prevents
logout from switching to the server owner's paid identity. The unmanaged API-key
and Azure/cloud experience is not changed to obtain this safety.

## AUTH-16 — The interaction boundary

Provider flows request data or emit notices; they do not own a terminal/framework.
A UI adapter implements two operations and respects cancellation:

| Operation | Variants and minimum data |
|---|---|
| `prompt` -> answer | `text` (field ID, label), `secret` (field ID, label), `select` (option IDs, labels, descriptions), `manual_code` (label, accepted form) |
| `notify` | `auth_url` (URL, instructions), `device_code` (user code, verification URL, expiry, next poll time), `progress` (safe stage), `info` (safe guidance and links) |

A select answer is the option ID, not label or list position. Requiredness and
shape are validated before use. Secret answers, manual redirect URLs and codes are
private inputs. Text entered as a key is literal data: no `!shell`, environment
interpolation or executable configuration language is introduced by this UI.
Existing explicitly supplied credential callbacks/cloud subprocess recipes remain
separate mechanisms.

A prompt has its own cancellation lifetime as well as the operation's. Callback
completion invalidates a simultaneously displayed manual prompt; dismiss it and
ignore stale answers. UI callback failure is a sanitized operation failure, not a
reason to print the raw callback exception or continue headlessly.

Only a UI adapter explicitly selected by the app may open a browser or emit
terminal output. Core `login` requires a supplied UI if interaction is needed.
The separately named/imported **interactive** `connect()` helper may construct the
terminal adapter by default on an interactive terminal. On a server/noninteractive
host it MUST fail before secret/network access unless an appropriate UI and
selection were explicitly supplied. It MUST NOT read stdin indefinitely, guess a
user from environment variables or install a UI process-wide.

## AUTH-17 — Public operations and side effects

These are semantic names; snake_case/camelCase and sync/async variants follow the
language. Durations are named/unit-explicit in bindings; public serialized times
are RFC 3339 UTC. Omitted input is not a magic different mode from explicit default.

| Operation | Result | Permitted effects |
|---|---|---|
| construct manager / descriptors | manager / values | Argument validation only |
| `providers`, `methods` | descriptors | Definitions + declared capabilities only |
| `connections`, `status`, managed `explain_auth` | secret-free metadata | Scoped store reads; no refresh, network, subprocess or credential callback |
| `login` | Connection | Explicit UI, authorization, bounded polling/exchange, atomic persistence |
| `cancel_login` | terminal attempt snapshot | Durable cancellation; close owned resources, never provider revocation |
| `close` | none | Release owned resources; cancel owned connected operations, not logout |
| `set_api_key` | Connection | Validate and atomically save literal credential/settings; no network verification |
| `configure` | Connection | Save validated cloud/local recipe and settings; no credential acquisition or model call |
| `verify` | Verification | Explicit supported non-inference provider check; may resolve/renew the selected credential |
| `logout` | ForgetResult | Scoped local invalidation/deletion; no provider request |
| `model_choices(refresh=false)` | catalog with provenance | Definition/store reads only |
| `model_choices(refresh=true)` | catalog with provenance | Explicit account catalog request(s), bounded pagination, permitted renewal; no inference |
| `bind(selection)` | BoundClient | Structural validation only; no network |
| interactive `connect` | BoundClient | Choice UI, explicitly selected login/setup, catalog discovery and binding; no inference |
| bound `request` / `plan` | canonical Request / plan | Pure construction/planning with the exact selected model; no credential acquisition |
| bound `complete` / `stream` | canonical Response / StreamEvents | Per-request selected authentication, necessary renewal, provider model request |

`begin_login`, `resume_login`, `attempt` and `prune` (resumable, cross-process
login) are reserved (AUTH-17 reserved).

Constructing a default file store MUST NOT touch disk. Before any new external
authorization, `login` checks required storage/locking capability and reserves
its private attempt plus necessary local resources. A failed reservation means no
provider authorization request or browser opening. A later disk failure can still
occur; never claim this precheck guarantees the eventual write.

Read failures are not an empty store. Unknown schemas and malformed data are typed
storage errors; do not overwrite them, switch to memory, or consult another scope.
A caller may explicitly choose a different store after receiving the failure.

`verify` without a supported safe check returns `unverified` with a reason and
makes no model request. `valid` means that specified check succeeded at a timestamp,
not that every model, quota, permission or future request is valid. Metadata checks
may be metered by providers; do not advertise a universal zero-cost guarantee.

Account/model-policy changes (e.g. enabling Copilot models), provider revocation,
creating cloud resources and paid test prompts are **not implied by login/verify**.
They require separate explicitly described actions and evidence. An account flow
that mints a key or grants scopes must disclose that effect before approval.

## AUTH-18 — Running a login, and what protects it

### Connected login

`login` runs one attempt to completion while the program stays alive: it renders
each step through the AUTH-16 UI, waits and polls cancellably, exchanges, and
commits atomically (AUTH-19). It does not retry a failed exchange without a proven
safe retry classification (AUTH-20).

- Default attempt lifetime is **15 minutes**, measured from begin. The caller may
  explicitly select another positive finite budget before beginning; use the
  earliest of that local deadline, caller cancellation/deadline and any
  provider/profile deadline. No poll may extend an existing deadline, and a
  provider expiry is never extended by restarting a local poll loop. Durable
  time is wall-clock UTC; in-process waits use monotonic deadlines. Clock errors
  fail safely rather than lengthen approval.
- Device flow: early polls return the unchanged next permissible time without
  network I/O. `pending` uses the provider interval, default 5 seconds, with a
  minimum positive wait. `slow_down` MUST NOT decrease the interval: use at least
  the previous interval + 5 seconds and any larger server-required interval.
  Provider-specific exceptions require wire evidence, not silent per-language
  variations. A device poll issues at most one poll request; documented follow-on
  token/key exchanges after approval may complete within the bounded budget.
- Recheck the deadline immediately before credential commit: a result received
  before expiry cannot be saved after it. A completed durable commit is not undone
  by a later deadline/abort.
- A completed attempt's secret state is erased on termination, whatever the
  outcome.

Resumable attempts (public snapshot, private state, `begin`/`resume`, step
revisions, exchange ownership across processes, 24-hour terminal retention)
are reserved (AUTH-18 reserved).

### Browser and OAuth protections

Use RFC 9700 security guidance, RFC 7636 S256 PKCE for authorization-code flows,
RFC 8252 loopback/native-app restrictions and RFC 8628 device-flow rules.
Provider profiles must pin the actual supported registration and deviations.

- Fresh cryptographically random verifier and independent state per attempt;
  verify PKCE syntax and the RFC 7636 Appendix B vector. If a provider does not
  echo `state`, use an evidenced equivalent binding (e.g. one-time random callback
  path plus PKCE and application session binding); never silently omit all checks.
- Validate expected issuer/client/redirect context, path, state and duplicate
  parameters before accepting success **or an error callback**. A return carrying
  both success-code and error fields is invalid. Wrong path/state receives a
  generic rejection and does not terminate the legitimate wait. Error
  descriptions supplied by an untrusted URL never become rendered SDK diagnostics.
- Native listeners bind loopback only (`127.0.0.1`, or `::1` where the declared
  registration supports it), never wildcard/LAN. Binding address and exact
  registered redirect URI are separate: do not rewrite `localhost` to an IP in a
  token exchange. Port conflict returns actionable failure or an explicitly chosen
  supported alternative, never a wider bind or arbitrary redirect substitution.
- Manual entry is accepted only when the method profile permits it. A supplied
  redirect URL is parsed against that attempt's exact registered return context;
  a bare code cannot supply state, so is allowed only with the attempt's stored
  PKCE/context, explicitly declared by the profile.
- Callback URL/request limits and auth-response limits are finite: default request
  target 8 KiB, callback headers 32 KiB, auth HTTP response body 1 MiB. Refuse before
  unbounded buffering. A profile/app may explicitly choose other finite limits;
  it cannot disable them by an untrusted response.
- Authorization URLs opened by a helper must match the declared HTTPS issuer
  policy. The UI is told the provider; it never opens arbitrary schemes from a
  provider response. Local return URLs are handled as returns, not launch commands.
- No long-lived client secret is embedded in a public browser/native application.
  A provider requiring a confidential client needs an application backend with its
  own approved registration. A relay cannot waive this requirement.

Website return-URI, CSRF and session-binding rules for server applications are
reserved (AUTH-18 reserved).

## AUTH-19 — Lifecycle, replacement and cancellation

Every binding slot has a monotonically increasing **identity generation**, even
when empty. Each stored credential has a separate monotonically increasing
**credential revision**. Connection IDs are never reused.

### Creation and replacement

`login`, `set_api_key` and `configure` do not overwrite an active connection by
default. They return `connection_exists`. Replacement requires the caller's
explicit target Connection ID/generation; interactive UI may obtain that consent.
An attempt reserves the observed identity generation. Commit atomically checks
that generation, stores a **new Connection ID**, increments identity generation,
and marks the attempt complete. Refresh may occur while replacement is pending;
it changes credential revision only and does not invalidate the user's intended
replacement. A different replacement or logout does.

A direct `set_api_key`/`configure` targeting a slot with an active login attempt
returns `login_in_progress`; it does not silently supersede that attempt. The app
must cancel it deliberately first. Direct setup otherwise uses the same
expected-generation/new-ID commit rules without a provider authorization
round-trip.

Old credentials remain active until replacement commits. Cancel, denial, expiry,
validation error or storage failure preserves the old active connection. If commit
loses a generation race, fail `connection_changed`; never resurrect old state.
A successful remote grant may already exist even if saving fails. The UI says
"not saved"; no usable Connection is returned and no unrelated login is revoked
as compensation. Once that attempt terminates as failed, its private result is
erased and authorization must restart after storage is repaired. If commit outcome
is unknown, inspect the authoritative state before starting again; never repeat
a one-use exchange just to discover whether the write succeeded.

### Logout

`logout` targets a Connection ID (or an unambiguously resolved binding slot with
expected generation). It atomically invalidates that connection, increments the
slot generation and cancels its active attempt. Secret records and SDK caches are
removed/invalidated. It never calls a remote revoke endpoint, edits environment
variables or deletes foreign cloud/CLI files. Repeating logout of the same ID is
idempotent; it MUST NOT remove a newer ID occupying that slot.

Any later attempt completion/refresh commit referencing the removed generation
fails. Other scopes and bindings remain untouched. Aliased routes sharing one
binding all lose access; the result lists affected routes. Logout is local
forgetting, not subscription cancellation or a claim that all provider sessions
were revoked.

### Cancellation and commit races

Caller cancellation, the UI's cancel action and operation deadlines stop waits,
new polling and unsent exchanges; release resources and invalidate pending UI.
`cancel_login` is a **durable**, serialized operation returning the actual terminal
state. If cancellation commits first, credential commit is forbidden. If credential
commit won first, cancellation returns `complete`; undo requires explicit logout.

Native task/AbortSignal/context cancellation may prevent delivery of a result
that already committed. It does not prove nothing changed: the SDK must not report
"nothing saved" without reading the authoritative state. Process death cannot run
cleanup; persistent expiry/ownership rules still apply.

After a credential snapshot has been admitted for sending, logout cannot recall
bytes already sent. The request path rechecks generation at final local dispatch
admission (AUTH-20); a logout that committed before admission prevents dispatch.
An already admitted request may finish or be aborted on a best-effort basis. No
claim of instantaneous provider-side revocation is made.

Tombstone/epoch retention across scope deletion is reserved (AUTH-19 reserved).

## AUTH-20 — Renewal and request authentication

1. Each request resolves a single private snapshot: Connection ID/generation,
   credential revision, request credential, account headers, destination and
   trusted definition revision. Account switching cannot combine A's token with
   B's account header or endpoint. Generation is checked again at local dispatch
   admission; a lost race is not silently rebound. When the profile exposes a
   stable principal/account identifier through an authenticated exchange, renewal
   must preserve it or fail `connection_changed` for explicit reauthorization.
   Do not relabel a different principal as renewal of the same Connection.
   Opaque credentials cannot independently prove a provider's human identity;
   pinning guarantees the local credential lineage/selection, not immutable
   external IAM permissions, billing entitlements or a verified account label.
2. Stored account expiry is the provider's actual expiry, not a timestamp already
   reduced by skew. `never` is an explicit provider-proven property, not an omitted
   expiry or a large magic number. Unknown expiry is represented as `unknown`;
   managed login profiles must define how such a credential remains usable or fail
   the token response, rather than treating unknown as non-expiring.
3. For a finite account credential with known issue time/lifetime, renewal becomes
   due at `expires_at - min(300 seconds, lifetime / 10)`. This keeps a five-minute
   buffer for long tokens without making a short-lived token permanently due.
   After one renewal, accept a positive-lifetime result sufficient for that request,
   or fail; do not spin renewing within the same request. Existing cloud-chain
   caching/skew rules under AUTH-3 are unchanged.
4. On renewal: lock/serialize the binding, re-read authoritative generation and
   credential revision, and reuse a sibling's sufficiently fresh result. Otherwise
   write a durable `renewal_in_flight` marker **before** the possibly rotating
   exchange; hold exclusive ownership through the bounded exchange and atomic
   write. Refresh does not change Connection ID or identity generation. An
   unresolved in-flight marker prevents request acquisition from using that
   material, even if its recorded expiry would otherwise be fresh: await the owner
   or apply uncertainty recovery, never bypass the marker.
5. No lock is held while a human approves a login. Network exchange budget defaults
   to 30 seconds per request and is bounded by the operation deadline. Lock waiting
   defaults to 30 seconds and is cancellable. Callers may shorten/explicitly change
   these finite budgets; never use an unbounded refresh lock.
6. A provider-declared permanent rejection marks `needs_login`, clears unusable
   renewal secrets, and fails without another identity. A known safe transient
   failure retains credentials and clears its in-flight marker. Ambiguous timeout,
   crash or cancellation after a one-use/rotating exchange may have reached the
   provider is `indeterminate`: preserve recovery metadata, do not reuse the old
   one-use credential automatically. Reconcile only through a documented provider
   recovery mechanism; otherwise require fresh login. Missing `refresh_token` in a
   response preserves the old one only if that provider's profile permits it.
7. Device polling is protocol progress, not a generic retry loop. Other retries
   require explicit operation semantics proving repetition safe. SDKs must not add
   inference retries, hidden 401-replay or account fallback under the banner of
   authentication. No exactly-once network guarantee is possible across
   provider/store crashes; the contract guarantees local commit ordering and
   conservative uncertainty handling.
8. Safe transient renewal failure does not delete an account, and callers can retry
   deliberately. The selected operation fails; the SDK does not silently send the
   nearly expired token or charge an environment key instead. This trades some
   availability for predictable identity and expiration behavior.
9. Destination policies apply to token, key-mint, catalog and model requests and
   redirects. Unexpected HTTP redirects with credentials are refused. Dynamic
   account endpoints (Copilot) must be validated against the provider's allowed
   origins/path policy, not accepted merely because a token string contains a URL.
   Custom gateways are trusted application configuration with separately scoped
   bindings. TLS certificate verification is mandatory for credential-bearing HTTPS.
10. Pure LM15 build/plan operations remain offline. Network authentication
    preparation happens before pure encoding/dispatch, not inside serialization,
    repr or model planning. An explicitly supplied AUTH-2 callable keeps its
    existing per-request semantics; managed sources must not smuggle interactive
    work into it.

Lease fencing for distributed stores and server-side egress/SSRF policy are
reserved (AUTH-20 reserved).

## AUTH-21 — Secret and privacy boundary

Three data classes must not be confused:

| Class | Examples | Permitted destinations |
|---|---|---|
| **Credential/private protocol material** | API/access/refresh/identity tokens, private keys, PKCE verifier, device code, code-exchange results, client secrets, raw auth responses | Private store, authorized provider exchange/request, deliberately configured relay; low-level trusted storage/transport adapters only |
| **User/session-sensitive display material** | Authorization URL/state, returned redirect/code, user code, verification link, attempt ID, account label/ID, enterprise settings | Initiating user's UI/session and required protocol; not automatic logs, analytics or public status endpoints |
| **Public descriptions** | Provider labels, method IDs, non-user-specific documentation | Catalog, documentation, UI |

SDK-generated repr/debug/inspection, diagnostics, exceptions (including causes),
traces and auth HTTP logs MUST omit credential/private material and redact
session-sensitive URLs/codes. Status objects contain no secret values. Account
labels are opt-in display metadata, not a telemetry payload. Never attach a raw
token response or reflected provider error description to a public error.
Application-supplied callbacks may mishandle data; the SDK must minimize what each
receives and state that trust boundary, not claim to sandbox them.

Bearer-equivalent values may travel only in the fields required by the provider
protocol. Never place a refresh token/verifier in an ordinary navigation URL.
OAuth itself returns short-lived codes/state in URLs; they are the explicit,
protected exception. Native listener access logs must be disabled. HTML/terminal
display escapes untrusted provider/account text.

Browser storage is readable by same-origin scripts; a private file is not encrypted
at rest. These limitations must be stated. Do not promise keychain security from
`0600`, or stronger isolation because the caller used WASM.

Auth exchanges are never captured as ordinary model traffic: the auth path does
not inherit body-capture defaults from model-call logging or a gateway.

Relay consent rules are reserved (AUTH-21 reserved).

## AUTH-22 — Platforms: declared capabilities, separate evidence

An SDK reports declared capabilities; it does not run probing code during
`methods()`. A native pass is not a browser pass: browser directness must be
evidenced separately for authorization, token exchange, renewal, catalogs and
inference. Provider pages can normally be opened as navigation even when their
token API refuses cross-origin fetch; those are distinct operations.

Language bindings keep native mechanics: Python sync Auth plus native AsyncAuth
and CancelledError, TypeScript promises + AbortSignal, Go context, Rust async
cancellation/drop plus explicit durable cancel; the full per-language list is in
the reserved file. Cancellation of an in-memory task
is not a proof of durable cancel; AUTH-19 always applies. No sync wrapper may
secretly start an event loop in an already-running loop. Browser builds must not
import native callback/filesystem modules merely to list providers or build a
request.

The per-environment profile table (SSH, GUI, mobile, serverless, relay limits) is
reserved (AUTH-22 reserved) and promoted one row at a time as each environment
gets its first receipt.

## AUTH-23 — Model selection and `connect()`

### Model choices are evidence-bearing data

Each choice has exact route, model ID, originating instance/Connection ID,
catalog source (`bundled`, `cached`, `provider`, `application`), freshness where
known and capability evidence (`supported`, `unsupported`, `unknown`) for requested
features. Account-listed availability is not a pricing or quota promise. Catalog
fetch failure is surfaced; an explicit cached/manual alternative must be labelled,
not silently substituted. Provider calls use the same scoped selected identity and
destination policy as inference. A model list MUST NOT widen that policy.

`capability="structured-output"` is a strict requested capability: only supported
choices are automatically offered. Unknown can be considered only by explicit
caller/user opt-in identifying uncertainty. A choice does not override LM15's
request validation or actual provider response. Manual model IDs remain possible
as an explicit, labelled unverified choice. No paid inference probe, model ranking
or provider-policy enablement happens while listing models.

### The interactive convenience

`connect()` lives in an explicitly interactive module/function family. It is a
recipe over discovery, scoped Auth and model selection, not a parallel login
implementation. With no arguments on a native terminal it:

1. Uses a lazily constructed local Auth and terminal UI, displaying store location
   and persistence intent before new authorization.
2. Offers saved connection metadata and "connect another". It does not refresh or
   verify every saved account just to populate the menu. Do not select the first
   saved account silently; a previously explicit caller selection may skip this.
3. Reuses the selected connection, or runs the chosen login/setup flow. Core
   `login` is not an ambiguous "reuse or replace" operation; connect orchestrates
   those separate choices and obtains replacement consent if needed. A selected
   connection marked `needs_login` is offered explicit reauthorization; it is not
   reused as if ready. A renewal failure during setup may offer a deliberate new
   login, but cannot silently create one or select another account.
4. Explicitly fetches/uses the selected connection's model catalog with visible
   source/freshness, offers supported choices and checks route binding. No guessing
   from a model family name. A caller-specified valid selection can skip the picker.
5. Returns a BoundClient and a secret-free selection summary. It does not send a
   model prompt, set process environment/defaults or change existing routers.

A completed login is persisted **before** model choice. If the user then cancels
model selection or catalog fetching fails, the connection remains saved and the UI
says so. There is no pretend whole-wizard rollback or silent provider revocation.
The caller may explicitly logout that new connection. Stated trade-off: valuable
authorization survives a later choice failure, but connect is not one atomic
transaction.

The BoundClient exposes selection metadata and has `request(messages, tools?,
config?, ...)` that produces an ordinary canonical Request with the selected routed
model. `complete`/`stream` may accept those canonical fields as ergonomic sugar;
they produce the same Request and full Response/StreamEvent types as the ordinary
router. They also accept a full Request only when its model exactly equals that
selection. Contradictions fail before I/O. No string-only response, hidden message
history, automatic tool loop, inferred follow-up, automatic fallback or new retry
policy is introduced. Request/Response serialization gains no credential fields.

Bound clients pin route/model/Connection ID but re-resolve renewable material per
request. Cloning/sharing one shares the same selection/scope, not an independent
copy of a rotating token. Closing is not logout. A selection contains no
credential or callable; serialized IDs confer no access.

The serializable ModelSelection record (epochs, revisions, `router.bind` from
persisted data) is reserved (AUTH-23 reserved).

## AUTH-24 — Errors, cancellation and recovery

Managed lifecycle errors are `AuthOperationError` at the LM15 root with
`code="auth_operation"` and a closed `reason` below. They are not fabricated HTTP
401s and do not imply credentials are wrong. Public metadata includes operation,
instance, method, attempt/connection reference where safe, stage, commit state
(`not_committed`, `committed`, `unknown`) and a recovery action. Messages are helpful
but not matched as protocol. Bad argument types use the language's normal argument
error; unknown registered IDs are `not_configured`.

`recovery` is one of `provide_input`, `choose_method`, `resume_attempt`,
`inspect_attempt`, `restart_login`, `select_connection`, `repair_storage`,
`operator_action` or `none`. It is guidance, not an automatic retry instruction.
`stage` is one of `discovery`, `reservation`, `interaction`, `authorization`,
`polling`, `exchange`, `persistence`, `resolution`, `renewal`, `verification`,
`catalog` or `dispatch`. Provider-specific progress text may accompany a stage,
but cannot invent an error code or expose a raw response.

| reason | Meaning / normal recovery |
|---|---|
| `interaction_required` | A deliberate choice/input is missing; supply UI or selection |
| `method_unavailable` | Host/provider cannot run the requested method; choose another supported mode |
| `connection_exists` | Explicit replacement target/consent needed |
| `login_in_progress` | Resume or durably cancel the slot's existing attempt |
| `login_required` | No usable selected connection; explicitly sign in |
| `connection_changed` | Pinned identity/generation/definition no longer matches; select again |
| `login_denied` | Validated provider denial; start again only on user request |
| `login_expired` | Attempt deadline reached; start a new attempt |
| `invalid_login_state` | Wrong step/state/return context; reject input, preserve legitimate wait where appropriate |
| `attempt_unavailable` | Missing, inaccessible or purged attempt; do not disclose another scope's existence |
| `indeterminate` | An exchange/write may have happened; inspect/reconcile, never blind retry |
| `storage_unavailable` | Cannot safely read/reserve/commit; repair storage, no memory fallback |
| `unsupported_store_version` | Unknown persistent format; explicit tooling/operator action required |
| `selection_mismatch` | Request/model/credential override contradicts a bound selection |
| `credential_rejected` | Selected renewal/session permanently rejected; sign in again |

Native cancellation remains idiomatic; normalized conformance outcome is
`cancelled`, not an AuthError and not retryable. SDK-created cancellation errors
do not copy arbitrary secret-bearing signal reasons into messages/causes.
Deadline expiry outside the login-attempt lifetime uses the existing timeout
mechanism; attempt expiry is `login_expired`. Lock contention retains AUTH-6
LockTimeoutError. Definite safe transport/rate-limit failures may retain the
existing typed errors with sanitized diagnostics and safe operation context.
AUTH-20 indeterminate classification takes precedence over "retryable network
error" for a possibly consumed code or rotated token. Auth-endpoint diagnostics
use the stricter secrecy boundary, never wholesale token-response passthrough.

No AuthOperationError enters the global automatic/retryable set merely because
its English message says try again. Model-inference HTTP errors keep their current
classes, provenance and evidence-backed metadata; this amendment does not alter
Azure/API-key provider error mapping.

Connection status separates `presence` (`saved`, `absent`), `usability`
(`ready`, `renewal_due`, `needs_login`, `indeterminate`, `unknown`), and optional
last Verification (`valid`, `rejected`, `unverified`, timestamp and check identity).
`ready` is a local assessment, not remote verification. Absence of expiry does
not justify a verified badge. An unreadable store produces an error, not `absent`.

## AUTH-25 — Persistence: what every store must guarantee

Public Connection/Attempt/Selection snapshots are not credential-store records.
The private store keeps versioned records for binding slots (identity generation,
active Connection ID, reserved Attempt ID), connections (credential revision,
settings, actual expiry, renewal material and recovery state), attempts, and a
renewal/exchange journal sufficient to detect interrupted one-use work.

Persistent envelope version is **1**, independent of canonical Request JSON and
of provider token-response schemas. Timestamps are RFC 3339 UTC; finite
intervals use named units; generations and revisions serialize as nonnegative
**decimal strings** (JavaScript integer precision). No legacy xAI/Pi/Claude/Codex
importer or dual-format writer is required. Secret serialization is explicit and restricted to store adapters.
Do not serialize native objects, code, a Python pickle or a language-specific enum
layout. Private-store and auth-response JSON must be strict UTF-8 JSON without
duplicate member names or non-finite numbers, with bounded sizes (AUTH-18).

Mandatory atomicity: credential commit + attempt completion is one durable
operation; logout + generation invalidation is one durable operation. A commit
never decreases identity/credential revisions or reuses a Connection ID. An
unsupported format, integrity violation or unreadable store fails closed without
writing or probing another identity.

Files use AUTH-4's private atomic writes and canonical-path locking. Unix modes
and Windows semantics must be documented; `0600` text is not a Windows security
implementation.

Auth caches must include scope, instance/definition revision, binding, Connection
ID and credential revision/expiry. A label, provider name or access-token hash
alone is not an adequate cache key. Cross-process changes must be observed before
request dispatch admission; stale caches cannot bypass logout.

The draft envelope schema is [auth-store.schema.json](auth-store.schema.json) with
examples in [store-vectors.json](../auth/managed/store-vectors.json). It is a
draft artifact: the file store implementation may change it before ratification.
The full cross-record invariant list, the transaction primitive for
database/lease stores, and browser cross-tab rules are reserved (AUTH-25
reserved).

## AUTH-26 — Acceptance and honest support claims

Every release SDK implements these behaviors with native mechanisms. Which
languages are release SDKs is a separate, explicit maintainer decision; this
specification does not enlarge that list. Platform profiles are separate from
language names. A native pass is not a browser/mobile pass; source availability
is not a working provider integration.

The initial account inventory is Claude, Codex, Copilot, xAI, Kimi Code, Meta,
OpenRouter and Radius; ordinary key/cloud/local setup uses the same public
operations. Gemini CLI and Antigravity account login are excluded. GitLab Duo is
an optional extension example, not an unannounced ninth built-in. Radius requires
its model protocol as well as login; do not advertise a usable model connection
when only authorization was implemented.

Provider flow profiles and wire fixtures must be grounded in provider docs/live
receipts per AUTHORITY.md. The Pi 0.87.0 study is implementation reference, not
permission, live validation or a universal provider promise. Public client IDs,
scopes and accepted redirect URIs must be reviewed against their intended use.

Conformance has four independent evidence levels:

1. Specification and scenario/schema validation (this deliverable).
2. Deterministic fake-provider/store/clock tests and mixed-language storage races.
3. Real browser/native UI integration and install/prerequisite tests.
4. Authorized live login, request and renewal receipts per provider/platform,
   with secrets redacted and costs/approval explicit.

Existing API-key, shared-key, Azure/cloud-chain and endpoint/error fixtures remain
regression gates. Old implicit-login fixtures are explicitly superseded as listed
in the managed conformance README, not silently weakened or still counted as
proof of the new contract. The harness operations required to drive the new
scenarios are specified in that README; implementing them is later work. No
support-matrix promotion or SDK pin update follows merely from adding this
specification.

**Promotion order.** Core scenarios (see the tier table in
[scenarios.md](../auth/managed/scenarios.md)) gate the xAI migration and the first
browser login. Reserved rules and their scenarios are promoted only when the
trigger named in the reserved file is met, and only after the core has survived
two real implementations.
