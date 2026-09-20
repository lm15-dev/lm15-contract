# September 20 source implementation handoff

**No tests, builds, typechecks, native compilation or provider probes were run.**
Source review and git whitespace/diff inspection were performed; changed Rust
files were formatted through `rcargo fmt`. No dependency-resolution command was
requested. New regression sources are not evidence of passing behavior. SDK pins
name the updated target contract, not conformance. Do not publish on this record.

Starting SDK commits: Python `bbef28f`, TypeScript `fa3d23f`, Rust `62dcbff`.
Existing gateway work was preserved separately in baseline commit `c575b59`.

## Implemented scope

- Python/TypeScript baseline repairs: truthful Jev/scoring replies and usage,
  mixed judgment/free-form answers, strict generated/fallback parsing, preserved
  scoring bills, timeout inheritance, malformed auxiliary replies, offline plans,
  streamed judgment materialization, data-valued tool inputs and live admission.
- TypeScript catch-up: named cloud identity/source/endpoint handling, router-local
  provider declarations, native Node budgets/compression, browser limits,
  Unicode input faults, portable credential-lock source and packaging bridge.
- Rust catch-up: MAP-13 adaptations and score-preserving stops; MAP-14 types,
  helpers, TypeSafe and actual scoring driver; cloud identity/endpoints;
  diagnostics/serde/replay; budgets/compression; bounded live collection;
  complete blocking wrappers, cache/jobs/declarations/stores and testing helpers;
  prepared native/wasm execution separate from raw capture decoding.
- Cross-cutting review repairs: cached prefixes retain their destination; batches
  refuse stops they cannot enforce; shared credential-path identity; bounded SSE
  evidence retained on feed and EOF; response goldens are compared unchanged.

## One additive representation change to review

`CachedPrefix.provider` is optional canonical routing metadata. Wire-model facts
are not rewritten; a saved cached prefix can construct the same provider-qualified
suffix after reload. Old values without the field remain unchanged. The exact
field is recorded for maintainer review, not claimed separately ratified. Reusing
it still requires the same router configuration/account.

## Deliberate boundaries

- TypeScript native locking has source but no compiled macOS/Windows artifacts.
- Browser socket phases and CORS-hidden headers cannot be controlled or observed.
- Node's native transport is HTTP/1.1 without automatic redirects/proxy discovery;
  inject a suitable transport when needed. Rust's upload watchdog observes body
  consumption, not every socket write; active concurrency is not a global idle
  socket cap. Keep-alive remains enabled.
- Mixed scoring can add a generation call. Planning records that work; strict
  mode refuses it. No automatic provider-error retry was introduced.
- Old/new credential writers require coordinated rollout for changed Windows
  identities and affected aliases. Unsupported ambiguous paths fail closed.
- Shared uncommon cloud-login exclusions remain explicit; experimental expansion
  of those mechanisms was not included in this parity catch-up.
- Build/dist/site/native outputs were not regenerated. TypeScript's small
  CachedPrefix surface metadata entry was updated with source; regenerate and
  compare the complete reflection output when builds are authorized.

## Suggested next verification order — not executed

1. Compile/typecheck/package each SDK; Rust via `rcargo`, including native,
   blocking, codec-only and wasm configurations. Resolve/check the manually
   updated Cargo.lock and package asset inclusion.
2. Run focused new regressions: routing/cache, scoring bills/boundaries, batch
   stops, decoder/raw execution boundaries, stream diagnostics/stop ownership,
   live limits, timeouts/compression, credential identity/store locking.
3. Run the full native suites and shared contract directions against this pin,
   including the added routed-prefix and DEL-byte vectors. No golden expectations
   should be rewritten merely to make an implementation pass.
4. Build and exercise actual browser/native locking artifacts and cross-language
   exclusion on supported platforms. Paid live-provider checks require a separate
   deliberate decision; source work made no such calls.
