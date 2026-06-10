# Usage: zeros-vs-absent distinction (None = "not reported"), 2026-06-10

Canonical-fact change in `Usage`: the three core counters
(`input_tokens`, `output_tokens`, `total_tokens`) become `int | null`
with default null. Null means "the provider did not report this
dimension" and is distinct from a reported `0`. Lands in lm15-python2
first (reference, no oracle authority); this entry records the
normative basis and the fixture additions.

## Normative citation (AUTHORITY.md, canonical facts, precedence 1)

`lm15-python2/docs/serde-rules.md`, omission rule: "Each typed
serializer omits its own empty optional fields. When a typed object …
is serialized, a field whose value is `null` … is omitted from that
object's JSON." All three counters are now optional fields of the
`Usage` type, so a null (not-reported) counter is omitted; a reported
`0` is an integer, not empty, and is always emitted. `Usage()` with
nothing reported serializes to `{}` and is omitted entirely by
enclosing serializers (e.g. `Response.usage`), per the same rule.
Type-docstring rules (also precedence-1 per AUTHORITY.md), updated in
`lm15/types.py::Usage` in the same change:

- `total_tokens` auto-computes as `input + output` only when BOTH are
  present; stays null when either is null; an explicit provider value
  always wins.
- Arithmetic (`InferencePricing.estimate`) treats null as "unknown" and
  skips the dimension (lower-bound estimate), never as zero.

## Fixture changes — additive only

Three new hand-authored vectors appended to `serde/canonical.json`
(mirrored in lm15-python2/conformance/serde/canonical.json):

- `usage.nothing_reported` — `{}` round-trips to `{}`.
- `usage.reported_zeros` — explicit zeros are preserved, never dropped.
- `usage.partial_input_only` — `{"input_tokens": 7}`: output and total
  stay null/omitted (no auto-total from one side).

No existing vector's expected value changes: `usage.full` and every
embedded usage object (`stream.end`, `response.with_citation`,
`live_server.turn_end`) carry full integer triples and serialize
byte-identically before and after.

## Goldens

Byte-stable. Real provider bodies report usage, and provider adapters
keep their wire-dialect coercions (notably Gemini, whose proto3 JSON
omits zero-valued fields: absent `candidatesTokenCount` means a
reported zero, so `gemini/max_output_tokens.json` keeps
`"output_tokens": 0`). Verified with `harness/check.py --direction all`
on all reviewed goldens.
