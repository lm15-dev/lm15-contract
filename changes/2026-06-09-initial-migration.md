# 2026-06-09 — initial corpus migration

**What:** Copied the fixture corpus from `lm15-python2/conformance` (commit
`812a2cb` lineage, live-validated 2026-04-29 via the curl-fixtures pipeline)
into this repository as the single source of truth:

- `cases/` (96 case files, 3 providers) ← `conformance/provider_requests/cases`
- `bodies/` (96 capture directories) ← `conformance/provider_requests/results/bodies`
- `errors/` (3 provider files, 16 cases) ← `conformance/errors`
- `serde/canonical.json` (50 cases) ← `conformance/serde/canonical.json`

All migrated fixtures carry `provenance.source = "migrated-apr29"` (errors:
`"hand-authored"`), stamped by `tools/migrate_provenance.py`.

**Copy, not move:** the originals remain in `lm15-python2/conformance` and the
old suite keeps running against them until the Stage 2 harness cutover. Until
cutover, edits land in BOTH copies or not at all.

**Evidence:** verifier baseline and copy-count checks in
`verify/verify_stage01.sh` (S1.1); old suite green post-copy
(`conformance/run_all.py --strict`).

**Pre-migration fixture change carried in:** `anthropic/streaming.json` gained
`expect_lm15.usage = {required: true}` (S0.2). Evidence: the recorded body
`bodies/anthropic.streaming/2026-04-13T13-25-39Z.txt` already contains
`message_delta` with full usage (`input_tokens: 9, output_tokens: 12`); the
expectation pins the reference fix that consumes it
(lm15-python2 commits d73f2a4 red test + the message_delta fix).
