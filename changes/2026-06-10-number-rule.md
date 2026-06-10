# Number rule: declared JSON number type per numeric field, 2026-06-10

Canonical-fact change closing a panel-found one-wire-form violation:
`Config(temperature=1)` serialized as `1` while `Config(temperature=1.0)`
serialized as `1.0` — the canonical wire form depended on which Python
literal the caller typed, which a Rust/Go/JS/Julia port cannot reproduce.

## Normative citation (AUTHORITY.md, canonical facts, precedence 1)

`lm15-python2/docs/serde-rules.md`, new "Number rule" section, added in
the same change (lm15-python2): every numeric field in the canonical
model has a DECLARED JSON number type.

- Float fields (`Config.temperature`, `Config.top_p`, the
  `InferencePricing`/`TrainingPricing` rates, embedding vector elements,
  error `retry_after`) always serialize as JSON floats (`1.0`, never `1`).
- Int fields (`Config.max_tokens`, `Config.top_k`, `Reasoning` budgets,
  `CacheConfig.prefix_until_index`, `Usage` counters,
  `InferenceModelInfo.context_window`/`max_output_tokens`,
  `AudioFormat.sample_rate`/`channels`, Delta `part_index`) always
  serialize as JSON ints (`2`, never `2.0`).
- Constructors coerce same-valued cross-type input (int `1` -> `1.0` for
  a float field; float `2.0` -> `2` for an int field); non-integral
  floats for int fields are rejected; bool never coerces.
- Opaque payloads (`extensions`, tool `input`, `parameters`,
  `response_format`, builtin `config`, `provider_data`, continuation
  `data`, pricing `dimensions`) are untouched: `{"x": 1}` stays int `1`.

## Fixture changes

Additive vectors appended to `serde/canonical.json` (mirrored in
`lm15-python2/conformance/serde/canonical.json`):

- `config.number-float-fields-integral` — `{"temperature": 1.0, "top_p":
  1.0}` round-trips with the floats in float form (harness compares
  strictly: `1 != 1.0`).
- `config.number-int-fields` — `{"max_tokens": 64, "top_k": 2}` stays in
  int form.
- `model_info.number-integral-pricing` — integral pricing rates
  (`1.0`, `2.0`) stay in float form.

One existing canonical block changes form:
`cases/gemini/temperature.json` `canonical_request.config.temperature`
`1` -> `1.0` (spec citation: Number rule above; canonical fact, no wire
receipt required per AUTHORITY.md). The live-validated **wire fixture is
byte-identical and untouched**: `request.body.generationConfig.temperature`
remains `1`. The Gemini adapter maps integral float knobs to proto3-JSON
integer form on the wire (provider wire dialect, a different layer from
the canonical form), verified by `harness/check.py --direction all`.

No other case, body, or golden contains a cross-typed numeric value
(scanned all fixtures for int-typed `temperature`/`top_p` and
float-typed int fields).
