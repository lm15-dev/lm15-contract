# 2026-09-20 — Source parity repairs and live collector control-byte vectors

Implementation authorized in session by Maxime Rivest: complete the Python,
TypeScript/browser and Rust catch-up, commit the work, and leave execution of
tests for a subsequent decision. This entry records implementation work and
additional consumer evidence, not new runtime verification or a new ratification.

## DEL contributes six bytes to a live collector

Added two hand-authored cases to `consumer/live-collection-limits.json` for
U+007F (DEL). Basis: the compact ASCII JSON charge in
`changes/2026-09-15-live-collection-limits.md`, Shared policy: control and
non-ASCII characters use `\uXXXX` except the standard short control escapes.
The reference's compact `ensure_ascii=True` spelling of DEL is `\u007f`.
A text event containing only DEL therefore costs 31 bytes, and the following
`turn_end` event costs 19. Equality at 50 fits; the text event alone exceeds
30. These sizes follow the representation rule; no SDK output was used as an
oracle. The new cases exercise consumer collection, not provider traffic.

The old TypeScript counter treated DEL as one byte; Rust's new implementation
initially made the same mistake. Both counters now match the existing rule.
No provider fixture, golden expectation, or earlier consumer case was changed.
The new cases have not been executed in this implementation pass.

## Probability totals: correction to the initial study

INV-052 explicitly says that probability totals are not validated because
providers round. The initial study incorrectly called the absence of that
check a defect. Implementations retain that deliberate rule: no sum check
and no renormalization of provider-reported distributions. Missing or malformed
required measurements must not be replaced by invented zero probabilities.

## Data input boundaries and native score criteria

INV-013 excludes protocol/artifact parts from tool results, not an unmeasured
DataPart. INV-052 restricts measurements to assistant messages. Python and
TypeScript now admit data values in tool results while refusing attached
probabilities in tool results and live client input. Their existing text-wire
renderers already render the data value as compact JSON; Rust follows the same
rules. This closes the previous mismatch between ordinary and live validation.

MAP-14 §2 says TypeSafe ordered criteria carry descriptions, not titles. The
Python and TypeScript title fallback is removed to match that rule and Rust:
a level lacking a description uses its numeric key. Schema titles remain
unchanged for other wires and in the caller's schema.

Stream materialization in Python and TypeScript also now folds a complete
judgment JSON answer into DataPart, matching their non-streaming parsers and
Rust (MAP-14 §3 and INV-051). Partial/non-object JSON remains text; ordinary
structured output without judgments remains text; no probability is invented.
DataPart is still non-streamable: only the materialized answer is folded, not
the incoming text deltas.

These corrections have new native regression sources, not execution evidence.

## Cached prefixes retain their destination

The implementation review found the same routing bug in all three SDKs:
`router.cache` stripped the provider prefix for wire construction, then returned
that bare model in the reusable value. A later suffix passed to the router could
select another provider (for example Azure → OpenAI) or lose a router-local
declaration. Changing account/location silently violates the cloud-identity rule.

Added optional canonical `CachedPrefix.provider`, omitted when absent. Prefix
and resource model names remain their actual wire identifiers and retain the
existing equality constraint. Router-created prefixes carry the resolved
provider separately; their suffix requests use `provider:wiremodel`. The field
survives serialization. A suffix cannot substitute another provider/model.
Direct bare-model helpers keep their existing behavior; explicit own-provider
prefixes are stripped once at direct codec boundaries. No endpoint, credential
or account is embedded; reuse requires the same router configuration/account.

This is an additive representation amendment to the provisional cache surface,
implemented under the September 20 catch-up authorization and recorded for
maintainer review. **No separate ratification of this exact field is claimed.**
The alternative—qualifying a provider-reported CacheInfo.model, or keeping route
state only in an unserialized side table—would change a fact or lose safety on
save/reload. Python's new field is keyword-only; existing omitted-provider
canonical values remain unchanged. `serde/canonical.json` adds a hand-authored
routed-prefix vector based on the amended CachedPrefix table in spec/types.md.

## Scoring and batch boundaries

MAP-14 §1 requires ordinary schema fields to be answered, not discarded. Mixed
candidate-scoring requests now make one additional generated-JSON call under
the original schema, retaining ordinary fields and replacing only measured
judgment values. MAP-13 records that extra work before sending; strict mode
refuses it. Pure requested measurement is not itself an adaptation (MAP-14 §4).
Missing-ID fallback generates once, preserves the scoring bill and records, and
never pretends to have probabilities. Required fields and explicit completion
are checked without recovering truncated JSON. Privacy/billing/action controls
without an established measurement mapping refuse instead of disappearing.

Batch generation is not a client-controlled stream. A batch needing client-side
stop enforcement now refuses before credentials, upload or submission under
every adaptation policy, with feature `config.stop`. MAP-13 requires closing the
actual source at the cut; trimming finished batch output is not equivalent.
Provider-native batch stops remain supported. All items are preflighted before
an upload can occur.

Raw response/SSE decoding does not reconstruct execution records from a request
that might never have been built by the SDK. Rust now separates raw capture
decoding from prepared execution, matching the Python/TypeScript pure codec
boundary. Native drivers and the prepared wasm path retain adaptations and
client-side stopping. Response goldens are compared as stored: the implementation
pass removed an attempted in-memory augmentation of golden expectations rather
than treating it as legitimate conformance evidence.

Streaming parser failures now retain bounded first-body-byte evidence and
handshake diagnostics consistently on feed and EOF. Successful SSE handshakes
are not mislabeled as HTTP error statuses; canonical in-band error evidence
remains the closed ErrorDetail.http_response block.

## Credential lock identity

The three SDKs now resolve missing targets and symlinks consistently before
hashing a credential path (AUTH-4). Windows prefix/separator/case spelling is
normalized; unsupported ambiguous paths fail closed. Old/new Windows writers
and affected POSIX alias spellings require a coordinated restart, not deletion
of live lock files. Ordinary POSIX hashes are unchanged. Hardlink/mount aliases,
changing namespaces, foreign writers and cross-platform runtime verification
remain explicit boundaries. Rust path lookup is now fallible, not a guessed or
empty path. See each SDK's credential-lock-identity documentation.

## Platform boundaries

Fetch exposes decoded bodies, not compressed wire bytes. Browser CORS can hide
Content-Encoding and diagnostic headers; browsers may forbid an explicit
Accept-Encoding header. Implementations enforce the coding policy where
visible, never inflate Fetch-decoded bytes again, and document that hidden
headers cannot be checked. They do not claim separate socket connect/write
controls where the platform exposes none. This is a stated implementation
boundary, not a weakening of INV-053 for transports that see the wire.

Source-only implementation records and platform limitations are maintained in
the SDK documentation and the parity ledger. No conformance claim follows from
advancing a CONTRACT_PIN.
