# 2026-11-22 — Repair three golden lineage issues

No canonical answer or provider recording changes; no review approval is added.

- `goldens/typesafe/judgments.json` now names `2026-09-19T12-48-39Z.txt`, as
  its active case does. The old Sept 17 and current Sept 19 replies have equal
  decoded JSON values, differing in probability-map object-member ordering.
  The current file matches the active case's full response receipt hash.
- `goldens/typesafe/judgments_data_state.json` now names
  `2026-09-19T12-48-41Z.txt`. The old/new reply files are byte-identical and the
  current file matches the active case's full response receipt hash.
- The obsolete `goldens/typesafe/conversation_state.json` moves byte-for-byte
  to `research/retired-goldens/typesafe/conversation_state.json`. Its case was
  explicitly withdrawn by `changes/2026-09-19-jev-state.md`, Consequences.
  Archive SHA-256: `dac793aaf8a2679df40f292ee2a88a2e3d69f3b851cbfcaad2c2612864ed2a08`.
  Original recordings and receipts remain untouched. Removing its ratchet entry
  is retirement, not independent review: backlog 335 → 334 after PR #9.

`tools/audit.py` now checks every golden has an active case selected by declared
provider/feature and that a golden's stated pinned body belongs to an active
owner. Multiple cases sharing a golden (including request-only refusals) are
supported. Two regression tests catch stale links and orphan goldens. No
historical hashes are manufactured to make a checker pass.
