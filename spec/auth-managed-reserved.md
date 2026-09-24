# Managed authentication — reserved rules

**Status: RESERVED, 2026-09-22. Design notes, not normative. Binds no
implementation until promoted to [the core](auth-managed.md).**

These rules were written on 2026-09-22 as part of the first managed-auth draft
and moved here unchanged the same day. They describe situations no LM15
implementation has met: a web server resuming a login across processes, database
and lease-based stores, hosted relays, remote provider definitions, selections
persisted across processes. Writing them early was useful thinking; freezing
them before a real flow tests them would be the wrong order (research the real
thing before hardening the abstraction).

Each block names its **promote when** trigger. Promotion means: the trigger is
met, the text is re-read against the implementation that met it, corrected, and
moved into the core with its scenarios. Nothing here is silently normative, and
nothing here may be cited as a reason to reject an implementation.

Numbering matches the core so a rule keeps its address when it moves.

## AUTH-12 (reserved) — Provider-instance security revisions

**Promote when:** a custom or enterprise provider instance can be registered at
runtime, or trusted definitions can change while attempts/selections exist.

A provider instance has a stable application-assigned ID and a revision/digest of
its trusted auth-relevant definition. That revision covers issuer/client identity,
credential destination policy, route bindings, relay policy and flow version.
Nonsecret display-label edits need not invalidate it. Changing security-relevant
configuration requires a new revision; existing attempts and selections MUST NOT
silently adopt it.

Tombstone generation metadata is retained for the lifetime of the store scope
(contains no credential); deleting and recreating a whole scope gives it a new
internal namespace epoch.

Application/SDK dependency authors, not an untrusted webpage visitor, register
provider code and destination policies.

## AUTH-13 (reserved) — Remote definitions and foreign descriptors

**Promote when:** an SDK loads provider definitions from outside its bundle, or
descriptors are exchanged between processes/registries.

Optional remote definition loading is a separate explicit operation; downloaded
data MUST NOT execute code or widen a credential destination policy.

Descriptors received from another registry/revision must be revalidated against
the receiver's definitions. A descriptor is data, not authority to add an issuer,
access a scope or forward secrets to its embedded URLs.

## AUTH-14 (reserved) — Database adapters

**Promote when:** the first non-file store adapter is implemented.

A database adapter MUST enforce the scope at its storage boundary. Detached
begin/resume attempts remain in the store until explicitly cancelled or expired.

## AUTH-17 (reserved) — Resumable operations

**Promote when:** the first application must continue a login in a different
request or process than the one that started it (Stage 7 web/server track).

| Operation | Result | Permitted effects |
|---|---|---|
| `begin_login`, `resume_login` | LoginAttempt | One advancement as specified in AUTH-18; may do bounded network I/O and private writes |
| `attempt` | LoginAttempt | Read only; never polls or renews |
| `prune` | safe cleanup summary | Local expiry/retention cleanup under store transactions, no provider request |

## AUTH-18 (reserved) — Resumable attempts across processes

**Promote when:** same trigger as AUTH-17 (reserved).

### Public snapshot and private state

A LoginAttempt exposes `id`, `instance_id`, `method_id`, `created_at`, `expires_at`,
`step_revision` and one step:

- `prompt`: AUTH-16 prompt;
- `redirect`: authorization URL and supported return mode;
- `device_code`: user-facing approval details and `next_poll_at`;
- `pending`: `next_poll_at` and safe progress stage;
- `complete`: committed Connection metadata;
- `cancelled`, `expired`, `denied`, `failed`, `superseded` or `indeterminate`:
  safe AUTH-24 problem and recommended action, where applicable.

The public ID has at least 128 unpredictable bits. It is a reference, **not** a
bearer authorization credential. All reads/resumes/cancels verify the initiating
application scope and session ownership. Browsers may keep the ID; verifiers,
device codes and tokens stay in the private attempt store. Public snapshots may
contain display-sensitive approval URLs/user codes and belong only to the
initiating user's UI; default repr/log output redacts them.

Private state records flow/schema revision, trusted instance revision, expected
binding-slot generation, issuer/client/redirect context, expected prompt/step,
state/PKCE material where applicable, expiry and exchange ownership. No executable
callbacks or language objects are serialized. The store owns cross-process
continuation; applications do not transport a secret serialized `pending.token`
as an alternative default.

Each prompt has an attempt-local ID and step revision.

### Begin, advance and connected execution

- `begin_login` validates choice/settings/return mode and reserves the slot's one
  active attempt without locking it for human approval. An existing active attempt
  yields `login_in_progress` with scoped recovery; it is not silently cancelled.
- `resume_login(id, input, step_revision)` takes `answer(prompt_id, value)`,
  `callback(returned_url_or_supported_code)` or `poll`. It does not contain an
  instruction to pick a different provider/scope/redirect/relay. It advances to the
  next externally observable wait or terminal step.
- A recorded terminal result wins over later input. Otherwise resume/cancel/prune
  first checks `now >= expires_at`: logical expiry wins and no further approval or
  exchange begins.
- Resuming checks exact step revision and one-time exchange ownership before any
  request. Wrong-step answers fail without corrupting a still-valid attempt.
  Duplicate delivery after successful commit returns the retained result without
  another token exchange. Concurrent delivery permits only one exchange owner;
  the other returns current pending/terminal status, not another request.
- A completed attempt's secret state is erased; its safe terminal record is
  retained for **24 hours after termination**, then may be removed. Cancelled,
  failed and expired attempts have the same metadata retention. Lookup after
  removal returns `attempt_unavailable`, not a new login. Effective expiry is
  enforced on every read/resume, even if no process ran at the deadline. Physical
  cleanup is performed by explicit `prune`, a documented backend TTL worker, or
  the next relevant write operation. A read-only inspector may report logical
  expiry but must not claim it erased disk state. With no running process/TTL
  service, wall-clock deletion is not guaranteed; raw storage/backup retention is
  separate. Logical deletion is not guaranteed forensic erasure on SSDs or backups.
- Connected `login` drives these exact operations, renders steps, waits and polls
  cancellably; it is not a second flow implementation.

Navigation/suspension is not cancellation: a resumable attempt survives while its
store/session and deadline survive. SDK helpers retain/reveal the safe attempt ID
for recovery, and `attempt(id)` recovers the durable state after native
cancellation prevented delivery of a committed result.

### Website return URIs

Website return URIs are preconfigured by the application and accepted by the
provider's registration, not an untrusted `next` URL. The app binds callback to
its authenticated session, protects begin/cancel/logout against CSRF, removes
code/state from the address after handling, and avoids analytics/referrer leaks.
The SDK does not proxy a provider's password/cookie login page. Browser callback
pages need a restrictive referrer policy and no unrelated scripts before
handling/scrubbing the return.

## AUTH-20 (reserved) — Lease fencing and server egress

**Promote when:** a lease/CAS store exists (fencing), or the SDK/relay runs
credential-bearing requests on behalf of untrusted clients (egress).

Leased stores need fencing against stale writes. A lost lease while an exchange
might still be in flight means **uncertain**, not permission for another worker
to repeat it. Other bindings should not be held during the network call; a file
backend may serialize more broadly and must disclose that contention cost.

A request requiring longer remaining validity than the default renewal lead must
declare it. Provider-specific minimums need evidence.

Server/relay hosts must enforce an explicit egress policy against SSRF, including
DNS resolution/rebinding, private/link-local/metadata addresses and redirect hops;
hostname allow-listing alone is not a complete egress policy. Private gateways
are explicit application allow rules, never inferred from submitted login text.
Discovery from a remote host must not expand its own trust boundary.

## AUTH-21 (reserved, promoted 2026-09-24) — Relay consent

**Promote when:** the browser relay is extended beyond its current single
provider (relay track).

**Promoted to core 2026-09-24.** The binding text is now
[auth-managed.md](auth-managed.md) AUTH-21, § Relay consent (record:
[changes/2026-09-24-ratification.md](../changes/2026-09-24-ratification.md)).
The paragraph below is the original reserved note, kept for history.

Consent to relay is bound to the instance, relay origin and stages of use
(authorization/renewal, catalog, inference). A changed relay or new stage requires
fresh consent/configuration. It is never inferred from a generic network failure.
The UI must say whether credentials, identity tokens and prompts traverse the
relay. An origin allow-list is not authentication of arbitrary non-browser relay
clients.

## AUTH-22 (reserved) — Per-environment profiles

**Promote when:** one row at a time, as that environment produces its first
end-to-end receipt. The "native interactive terminal" row is promoted with the
xAI migration.

| Environment | Supported building blocks | Boundary |
|---|---|---|
| Native interactive terminal | Terminal UI, private files, supported loopback/device/manual flow | Browser may be on another machine; opening is a UI action |
| SSH/headless native | Device approval, displayed link/manual return, explicit configuration | Never assume user's browser reaches server localhost |
| Native GUI | App UI and secure-storage adapter, approved browser handoff | No hard dependency on a GUI toolkit |
| Web page / browser WASM | Page UI, explicit browser store, approved page redirect/device/manual flow | No native filesystem, localhost listener, ambient CLI login, or unrestricted headers |
| Application server | Server-private scoped store, begin/resume, explicit selected auth | App owns user/session authentication, CSRF, callback routes and authorization of scope |
| Mobile | System browser/device flow, app lifecycle and secure storage where supplied | A new app callback scheme must be provider-approved; SDK language does not grant registration |
| Worker/serverless | Explicit storage/HTTP/UI bridge as supplied | No assumed persistent process, local callback or local disk |

A relay solves some HTTP/CORS/header problems, not provider authorization, client
registration, cookies, callbacks or model codecs. It cannot access the user's
local model server through the user's localhost.

Language bindings keep native mechanics: Python sync Auth plus native AsyncAuth,
TypeScript promises + AbortSignal, Go context, Rust async cancellation/drop plus
explicit durable cancel, R explicit interruption/cancellation controls, Julia task
interruption, Java interruption/explicit cancellation, .NET CancellationToken,
Ruby its documented interruption/cancellation hook, Swift task cancellation.

## AUTH-23 (reserved) — Serializable ModelSelection

**Promote when:** a caller needs to persist a selection and rebind it in another
process (for example a scheduled classification job).

Verification/catalog results are bound to the captured Connection ID and identity
generation. Persisting them rechecks that identity; a lost replacement/logout race
returns `connection_changed` instead of attaching the old result to a new account.

A serializable ModelSelection contains `scope_epoch`, `connection_id`,
`identity_generation`, `instance_id`, `binding_id`, `definition_revision`,
`provider` (the exact route) and `model_id`. Generation uses the AUTH-25 decimal
string encoding. Catalog evidence accompanies the choice but cannot widen its
binding. No credential or callable appears in a selection. `router.bind(selection)`
or the native equivalent validates it structurally against the attached manager
and definitions without I/O; current store/generation validation is performed at
request acquisition/dispatch. A known epoch/revision mismatch fails immediately.
Restoring a selection requires an authorized Auth scope and matching definitions;
serialized IDs confer no access. Changing accounts/models means explicitly making
a new selection/client. The helper returns/attaches a safe recovery reference for
already completed setup when it fails or is cancelled.

## AUTH-25 (reserved) — Cross-record invariants and non-file stores

**Note (2026-09-22, Python implementation):** the private-store layout the
first implementation actually uses is one file, provider entries in the
legacy/Pi shape plus a non-secret `_lm15` metadata block — not the envelope
in `auth-store.schema.json`. That schema and `store-vectors.json` are
therefore a superseded draft; see
[the implementation record](../changes/2026-09-22-managed-authentication-python.md)
P1. Re-derive them from the Python and TypeScript layouts before promoting
this section.

**Promote when:** the file store has passed MA-032, MA-037 and MA-042 in two
languages; then re-derive this list from what those implementations actually
needed, and promote the transaction primitive with the first database adapter.

In addition to the structural schema, every store commit/load enforces:

1. Scope IDs/epochs are unique; slot keys and connection/attempt IDs are unique
   within the authorized scope. No cross-scope references. IDs are unpredictable
   where AUTH-18 requires it; schema string validation alone cannot prove entropy.
2. A slot's active Connection ID points to exactly one connection whose instance,
   binding and identity generation match it. No orphan active credential records.
   A reserved Attempt ID points to exactly one nonterminal attempt for that slot
   with matching expected generation. A reservation never creates a connection.
3. A terminal attempt has no private protocol/exchange data and is not reserved
   by a slot. Its completion metadata records what committed then, not proof the
   connection is still active now. Logout can remove that connection while the
   safe completion receipt remains readable. Consult status for current presence.
4. `complete` records have a result; other terminal records do not. `exchanging`
   has a matching in-flight journal. An interrupted journal is reconciled or
   marked indeterminate before another exchange; it is not treated as expired
   ownership that can simply be replayed. Step/credential revisions match their
   journal. Known-safe unsuccessful exchanges clear it atomically.
5. Finite issue/expiry times satisfy expires_at > issued_at; duplicate expiry on
   an AUTH-2 request credential agrees with the material's actual expiry. Attempt
   creation < expiry, terminal time >= creation, and exchange deadline > start.
   Exact time comparisons parse RFC 3339, never compare localized strings.
6. Connection kind matches material: cloud_identity -> cloud_recipe,
   local_server -> local_recipe, account/api_key -> credential. Api-key form
   storage has renewal=none; account renewal follows the evidenced flow profile.
   `needs_login` keeps metadata but no credential material/journal. Indeterminate
   material is private recovery-only and cannot authenticate model requests.
7. Persisted instance/profile/security revisions exist in the trusted registry;
   routes/settings and private provider data validate against those versioned
   profiles. Nonsecret provider settings occur only in `connection.settings`,
   not a second cloud-recipe settings map; secret credentials cannot be stored
   there. Local recipe `base_url` is its single endpoint field; profiles reject
   a conflicting second spelling in settings. A new unknown required revision is
   refused before credential use. Shared bindings have one declared owner. No
   settings string is executable.
8. A commit never decreases identity/credential/step revisions, reuses a Connection
   ID for replacement, or deletes generation tombstones while the scope survives.
   This is checked against the previous authoritative state, not just new JSON.

Provider-specific private data must be namespaced and versioned; preserve
unrecognized private fields within a known compatible version. Unknown required
flow/schema versions fail before exchange/write. Reject duplicate JSON members
before collapsing objects into maps; a post-parse schema cannot detect that
ambiguity. Stored `reason` is a bounded stable managed reason or existing error
code, never a raw provider/user error description.

The logical store primitive is a **scoped serialized transaction** over declared
binding/attempt/connection keys, with consistent reads, all-or-nothing durable
commit and a definitive commit result when available. A compare-and-swap/lease
backend is acceptable only if it implements the same ordering/fencing guarantees.
Define a global lock order for multi-key operations to avoid deadlock. A backend
without the required semantics is unavailable for persistent managed auth, not a
best-effort conforming store.

Files add directory sync where required for the claimed durability. A browser
session store states tab lifetime; cross-tab shared stores require real
coordination or refuse shared mutable use. Store quotas/read-only/private-mode
failures are surfaced before authorization where detectable. This is the logical
record format database/keychain stores expose too, not a requirement that they
store all scopes in one physical JSON file; a database may distribute records
while preserving their semantics.

Structural vectors do not prove the cross-record or cross-process guarantees;
AUTH-26 requires both kinds of tests.
