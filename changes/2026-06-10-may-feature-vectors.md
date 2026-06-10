# May-feature canonical serde vectors (cache_config, continuation_state, Config.cache)

Six hand-authored vectors appended to `serde/canonical.json` (55 -> 61),
landing the may-features lane handoff (lm15-python2@60cc874: CacheConfig and
ContinuationState serde, `Config.cache` wiring, kinds `cache_config` and
`continuation_state` in the vet shim's KIND_SERDE).

Spec citation (canonical fixtures change only with one, per AUTHORITY.md):
`lm15-python2/docs/serde-rules.md` — the omission rule (typed serializers
omit their own empty optional fields) and opaque-payload verbatim rule —
plus the type docstrings for `CacheConfig` (mode/retention vocabularies,
off+retention/key invariant) and `ContinuationState` introduced at 60cc874.
Each vector carries its own provenance block.

Coverage note (from the authoring lane): this closes CacheConfig,
ContinuationState, CacheMode, and CacheRetention from the surface-coverage
gap list. Deliberately NOT covered here: ToolCallInfo (a callback view of
ToolCallPart — a second wire form would be a mistake) and the
Batch/Embedding/FileUpload/Image/Audio endpoint-transport types plus
BatchStatus (provider-API-specific wire shapes; belong to endpoint fixtures,
not the portable canonical-JSON contract — deserves its own lane).
