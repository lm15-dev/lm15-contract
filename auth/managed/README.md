# Managed-auth contract examples and acceptance suite

**2026-09-22 REVIEW DRAFT. No SDK or new harness implementation is included.**

This directory specifies the tests for [AUTH-12–26](../../spec/auth-managed.md).
It is hand-authored canonical evidence, not captured provider behavior.

| Artifact | Purpose |
|---|---|
| `resolution.json` | Exact identity-selection decisions with competing sources and bound selections |
| `store-vectors.json` | Private v1 storage schema examples and invalid structural cases |
| `scenarios.md` | Ordered lifecycle, protocol, security, platform and convenience acceptance scenarios |
| `../../spec/auth-store.schema.json` | Normative private envelope/record schema |

## Resolution vector interpretation

`resolution.json` describes the decision phase **before credential acquisition**.
Its `definitions` are test-only route descriptors (`openai-alt` is a synthetic
application declaration, not a new built-in); no provider HTTP behavior is asserted. The driver builds equivalent public Auth/router/selection
configuration and captures its source decision and denied-source trace. It must
also assert that actual request preparation obeys that decision using a fake
credential provider/transport; it may not implement a second selection table in
the shim.

Each case has:

- `given.mode`: unmanaged router, managed router, or model/connection-bound client;
- `given.route`: exact route requested;
- `given.explicit`: configuration provider IDs mapped to symbolic credential
  references; `{ "empty": true }` is an explicit unusable value;
- optional `given.named`: an explicitly selected cloud source;
- `given.env`: complete injected environment with symbolic values; omitted = {};
- optional `given.connections`: authorized-scope active connection summaries;
- optional `given.bound`: pinned selection, including definition revision;
- optional `given.store_error`: injected read failure;
- `expect`: `selected` with source details and next action (`acquire`,
  `renew_if_due`, or `none`), or `blocked` with canonical code/reason.

Common defaults: authorized scope `alice`, public instance, definition revision
`v1`, model `example-model`, no connections, no explicit/named/ambient sources,
no injected storage error. All setup is synthetic, with no real HOME/environment
access. A connection's scope, instance and route membership are exact; the tests
must include inaccessible records in the fake backend, not merely omit them.
`state=renewal_due` selects that connection for subsequent renewal; these decision
vectors do not themselves contact a provider or promise renewal will succeed.

Symbolic credential names are not secret values. The future driver materializes
distinct sentinel-bearing secrets only at its private boundaries. Expected output
contains source identity/reference names, never rendered credentials. For every
case, the decision phase has **zero network calls, zero secret-provider callback
invocations, and zero writes**. Failed/unused sources are not invoked to inspect
whether they would work. Tests of acquisition failures and no fallback follow in
`scenarios.md`.

`selected` is a normalized comparator outcome, not a new public SDK return type;
`blocked` is the reason request acquisition must refuse. The doctor can express
that same decision as a report. This avoids making the public inspector throw
merely because no account is connected, while still requiring identical source
selection in diagnostics and real calls.

`spec/auth-resolution.schema.json` defines the structural vector format. The
driver additionally checks all route/connection/selection references against the
case definitions. The schema is not a substitute implementation of resolution.

## Store vector interpretation

`store-vectors.json` uses `input` as the private store input and `expect.valid`
as the structural JSON Schema verdict with date-time format checking enabled.
Patch cases derive their input from a named earlier valid vector using ordered
`replace`, `add` or `remove` operations with RFC 6901 JSON Pointer paths. This
avoids copying tokens throughout the corpus. Patches apply only to the designated
base value; fixture IDs are unique and bases cannot be forward/cyclic references.

The sentinel is deliberately in private **inputs**. The secrecy checker forbids
it in expected/public output. A private schema pass is not a license to print
that record. Public projection/redaction and AUTH-25 cross-record invariants are
separate scenarios; the valid vectors are also intended to satisfy those semantic
invariants. JSON Schema cannot prove randomness, monotonic history or locking.

## Validate these artifacts now

From the contract root:

```bash
uv run --no-project --with 'jsonschema[format]>=4.18,<5' python tools/check_managed_auth.py --self-test
python3 tools/check_provenance.py
python3 tools/check_secrecy.py
```

The recorded results and the deliberate source/spec mismatch are in
[VALIDATION.md](VALIDATION.md). These are not SDK runtime results.

The format extra is required: the checker first proves an invalid calendar date
is rejected, rather than silently accepting it because an optional date validator
was not installed. It checks structural verdicts, vector identities, scenario
numbering and local links. Its five mutations test bad **artifacts**, not the
runtime authentication requirements below. No live-provider support follows.

## Required future harness operations

The existing `auth` direction does not execute these login protocols. Add a
separately reported managed-auth direction before promoting support; do not make a
shim fabricate a pass by echoing expected values. Required capabilities:

1. Inject full environment, sandbox store, definitions, clock, deterministic
   randomness, UI answers, HTTP replies and barriers. Fail any access to actual
   HOME, subprocess, network or credentials. Runtime secure randomness must still
   have a real-platform test; deterministic injection is only for tests.
2. Drive public discovery, login/begin/resume/cancel, key/recipe setup, inspection,
   verify, logout, connect/bind and request-preparation APIs. Normalize only casing
   and native cancellation wrappers; retain operation ordering and outcome data.
3. Record observable actions (`prompt`, `notice`, HTTP dispatch, lock/reservation,
   private commit, safe result/error), with secret **references**, not values.
   The harness must inspect the real private HTTP request/store before redacting,
   so a fake implementation cannot pass without sending/storing the right material.
4. Expose barriers before/after remote exchange and before local commit/dispatch,
   allowing deterministic cancellation, competing refresh, replacement and logout.
   Use separate processes and mixed languages for actual shared-store race tests.
5. Kill a process after the provider consumed a code/rotated a token but before
   commit; prove the next owner diagnoses uncertainty and does not repeat it.
6. Replay the same flow once through connected login and once through begin/resume;
   compare the wire/actions/committed result apart from UI scheduling.
7. Require mutation self-tests: wrong state accepted, cross-scope ID accepted,
   secret rendered, ambient fallback, double refresh, logout resurrection,
   descriptor endpoint widening, unsafe one-use retry, model/account switch,
   premature success before persistence, native module in browser build. Each
   planted violation must turn a passing scenario red.

The HTTP profile of each real provider is a separate fixture family with the
right live/docs provenance. The scenarios here use fake endpoints by default.
Secret-bearing auth traffic is never captured through normal model request logging.
Authorized live evidence is redacted at capture time and approved separately.

## Existing fixture transition — explicit, no compatibility project

No current provider wire bodies/goldens are rewritten for this draft. Existing
unmanaged key/shared-key/cloud/named-credential/endpoint vectors remain regression
gates without weakening their expectations.

These ten cases in `auth/resolution.json` describe the retired implicit-login
source rules and must be replaced in the new managed harness, **not** counted as
new managed conformance:

- `oauth-fresh`
- `oauth-missing`
- `oauth-expired-with-refresh-token`
- `oauth-expired-no-refresh-token`
- `oauth-never-falls-back-to-env`
- `xai-explicit-key-shadows-subscription`
- `xai-subscription-shadows-env`
- `xai-subscription-only`
- `xai-env-rescues-unusable-login`
- `xai-nothing-configured`

They remain untouched while this is a review draft so that the previously pinned
contract remains reproducible. On ratification/harness transition, archive these
old source-policy cases under their historical contract commit and stop including
them in the new default gate. Do not add SDK dual behavior or deprecation machinery
to make both versions pass. Existing access-policy wire fixtures for valid explicit
credentials remain useful; they do not require retaining borrowed CLI-file lookup.

The draft changes CredentialPolicy and adds AuthOperationError; current runtime
reflection can therefore differ intentionally until implementation. Such drift is
not fixed by editing runtime snapshots or claiming a documentation-only pass proves
SDK parity. No SDK CONTRACT_PIN or provider support row is updated by this step.
