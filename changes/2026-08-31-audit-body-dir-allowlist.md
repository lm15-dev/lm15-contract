# 2026-08-31 — audit: body-dir allowlist for provisional surfaces

`tools/audit.py` hard-failed on the six `bodies/<provider>.models/`
directories landed by `changes/2026-08-31-list-models-provisional.md`:
body directories without case files. The surface is PROVISIONAL with no
harness direction, so case files cannot exist yet — but the live captures
are the evidence for the surface and must stay.

Change: the orphan ratchet gains a second key, `body_dirs`, in
`tools/orphan-allowlist.json`, listing body directories that belong to
provisional surfaces. Same ratchet discipline as `orphans`:

- the audit hard-fails on any NEW unlisted body-dir orphan;
- the audit hard-fails on any STALE entry (a case file now exists);
- burn rule: remove each entry in the same commit that adds its case file.

This is CI plumbing, not an oracle change: no fixture, golden, or expected
value moved. The six entries carry their evidence in the list-models
changes entry (live receipts, 2026-08-31).
