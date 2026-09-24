# 2026-09-24 — Every path storable on Windows

Status: repair (no normative rule changes; no case expectation changes).

`git clone` of this repository failed on Windows: 316 receipt files under
`research/tool-choice/receipts/` sat in 141 folders named after their
experiment cell, such as `xai__grok-4.6__tc:parallel-default`, and Windows
does not allow `:` in a name. Found when lm15-python's CI first ran on
Windows: its test job clones the contract and failed before any test ran.

- The folders are renamed with `=` for `:` (`…__tc=parallel-default`). Cell
  names are unchanged: `tc:auto` is still the cell in
  `research/tool-choice/20-results.json` and in every change record; only the
  folder built from it changed. The experiment script
  (`research/tool-choice/20-experiments.py`) now writes `=` too.
- The seven files that point into those folders (four cases' provenance, the
  MAP-8 change record, the results ledger, one probe script) are updated;
  every reference resolves.
- `tools/check_portable_paths.py`, now in CI, rejects any tracked path that
  Windows, or a case-insensitive file system, cannot store.

## Text encodings (same day)

Python reads and writes text in the platform's default encoding unless told
otherwise, and on Windows that is not UTF-8: a case holding `é` read back as
two other characters (found by lm15-python's Windows CI). Every text-mode
`open`, `read_text`, `write_text` and text-mode subprocess call in `harness/`,
`tools/` and `research/` now names `encoding="utf-8"` (253 calls), and CI runs
every step with `PYTHONWARNDEFAULTENCODING=1` and `EncodingWarning` as an
error, so an implicit encoding fails on Linux too. Harness results are
unchanged for every port.

## Paths on the wire (same day)

INV-009 said a path serializes "as its string", which is `/data/clip.mp4` on
POSIX but `\data\clip.mp4` on Windows for the same input, so the corpus's
`file_upload_request.path` vector failed on Windows (lm15-python's first
Windows CI run). Clarified: the separator on the wire is `/` on every OS.
Nothing changes on POSIX, and Windows accepts `/` (`C:/Users/...`). This
is a clarification of the rule's intent (one canonical form per value, INV
serde determinism), not a new rule; lm15-python implements it
(`serde._wire_path`). Other ports serialize the string they hold, which is
already `/`-separated unless a Windows caller passes `\`; the next Windows CI
run for each port checks it.
