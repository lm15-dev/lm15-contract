# 2026-11-22 — Five Anthropic goldens independently reviewed

Review-only: no wire bytes, canonical values, normative rules, or SDK behavior
changed. See [the field-by-field review](../goldens/REVIEW-2026-11-22-anthropic.md).

- Reviewed `reasoning_off`, `reasoning_budget`, `reasoning_adaptive`,
  `tool_no_description`, and `cache_history` against saved replies and MAP-1,
  MAP-7, MAP-19, the vocabulary finish mapping, and canonical serialization rules.
- All five canonical responses agree. Added `provenance.reviewed` pointing to the
  evidence; preserved their original `scribe-draft` origin and capture dates.
- The unreviewed-golden ratchet decreases from 340 to 335.
- Added a stdlib-only reproducible check of the five entire canonical projections,
  with seven wrong-answer mutations that must fail. It never calls an SDK.

Limits: this is a saved-wire/spec review, not a human approval or fresh live
capture. Four bodies predate the receipt requirement. Their new review snapshot
hashes identify examined bytes; they do not replace missing historical receipts.
The fifth body's original full response hash matches exactly. No request-building
behavior is re-certified, and no library pins need to move for this review-only
change. This review is proposed separately from the audit-remediation checkpoint.
