# 2026-06-11 — Editorial: reference implementation renamed lm15-python2 → lm15-python

The reference implementation repository was renamed from `lm15-python2` to
`lm15-python` (the legacy 0.2.x line it displaced now lives on that repo's
`legacy-0.2` branch). This entry records an **editorial path rename only** —
no rule, fixture, type, or vocabulary changed.

Updated (live references):
- `AUTHORITY.md`, `spec/types.md`, `spec/vocabularies.md`,
  `harness/PROTOCOL.md` — prose and relative links
- `harness/shims.json` — python shim `cwd` is now `../lm15-python`
- `tools/spec_drift.py`, `tools/audit.py`, `tools/scribe_goldens.py`,
  `tools/attach_canonical_requests.py`, `.github/workflows/contract.yml` —
  sibling-checkout paths and notices

Deliberately untouched (historical records, true at the time they were
written): provenance/evidence strings in `goldens/`, `changes/` entries,
`tools/migrate_provenance.py`, and the migration sentence in `README.md`.

Evidence: repository rename performed 2026-06-11; no behavioral diff —
harness run against the renamed sibling passes identically.
