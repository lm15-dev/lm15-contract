# 2026-06-10 — model_info canonical serde vectors

Added 5 hand-authored canonical serde fixtures (kind `model_info`) to
`serde/canonical.json`:

- `model_info.full` — inference + training + pricing + non-default origin
- `model_info.minimal` — required fields only (id, provider, api_family)
- `model_info.pricing-cache` — InferencePricing cache_read/cache_write fields
- `model_info.extensions-empty-object` — `extensions` containing an empty
  object, pinning the opaque-payload verbatim rule (empty objects inside
  opaque payloads are user data, never stripped)
- `model_info.origin-provider-data` — ModelOrigin.provider_data with empty
  string and zero values (opaque, verbatim) plus non-USD currency and
  pricing dimensions

## Spec citation (AUTHORITY.md canonical-facts rule)

These are canonical facts justified by normative rules:

- `lm15-python2/docs/model-hydration.md` — the model-hydration contract:
  field-by-field canonical JSON schema for ModelInfo and its nested
  InferenceModelInfo / TrainingModelInfo / InferencePricing /
  TrainingPricing / ModelOrigin types (field names exactly the dataclass
  field names).
- `lm15-python2/docs/serde-rules.md` — the omission rule: typed objects
  omit their own empty optional fields; opaque payloads (`extensions`,
  `dimensions`, `provider_data`) round-trip verbatim.

Provenance on each fixture: source `hand-authored`, date `2026-06-10`,
evidence citing `docs/model-hydration.md` and this entry. The same vectors
were appended to `lm15-python2/conformance/serde/canonical.json` per the
both-copies rule in `lm15-python2/conformance/README.md`.
