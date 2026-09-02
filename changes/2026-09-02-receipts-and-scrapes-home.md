# 2026-09-02 — Receipts and the doc scrape move into the contract

Ratification: not required. No fixture, golden, spec row, or rule changed;
this entry records where evidence and the rolling scrape now live, and
why, so the citations in eleven earlier entries resolve from a clean clone.

## What was found

Pushing today's scraper fix to `lm15-dev/curl-fixtures` failed: GitHub
reports the repository archived (read-only). Its local clone had four
unpushed commits since 2026-09-01. Worse, seven of the nine dated capture
folders that recent change entries cite as their receipts were never
committed anywhere (`batch-2026-08-31`, `files-2026-08-31`,
`genmedia-2026-09-01`, `live-2026-09-01`, `live-transcripts-2026-09-01`,
`video-2026-09-01`, `xai-2026-09-01`), and `lm15-dev/model-listings/` was a
loose directory with no repository at all. A fresh clone of this contract
therefore cited evidence that existed only on one disk.

## What moved

- `scrapes/`: the rolling doc scrape (`fetch.sh`, three `update.sh`, 78
  pages, the hand-fetched xAI models page) from
  `curl-fixtures/api-references/`. The scripts run unchanged from the new
  location (Gemini refreshed as proof).
- `receipts/<date>-<topic>/`: the nine capture folders plus
  `model-listings`, renamed date-first so a listing reads chronologically,
  copied verbatim. `receipts/README.md` maps each folder to the entries
  that cite it.
- Citations rewritten by path in the 2026-08-31 and 2026-09-01 entries,
  `playbooks/design-pass.md`, and lm15-python (`conformance/sources.py`,
  `check_endpoint_fixtures.py` comments, CONTRIBUTING, a draft). The
  lm15-python doc-drift check now reads `lm15-contract/scrapes/`, so the
  reference depends on one sibling checkout, not two.
- `tools/check_secrecy.py` scans both directories (1972 files, clean).

## Stated trade-offs

1. Clone size grows by about 14 MB (two multi-megabyte image-edit bodies
   and one MP4 are the observed artefacts the media entries cite). Accepted:
   evidence that cannot be cloned is not evidence.
2. Commit history for the two folders that were committed in curl-fixtures
   (`3ad5420`, `ced2abd`) and the scrape pages (`a6dae55`..`1af43bf`) is not
   carried over; it stays readable in the archived repository, and the
   READMEs cite the SHAs. Rewriting history into this repository was
   judged not worth the risk of touching its own.
3. `curl-fixtures` is left as it is: archived remotely, unchanged locally.
   Its old pipeline (`cases/`, `results/`, coverage tooling) was superseded
   by this repository on 2026-06-09 and nothing reads it. The 130 loose
   edits in its working tree (an untracked 2026-08-24 live run of the old
   pipeline, coverage regenerations) are not carried over: no entry cites
   them.
4. Editing path citations inside ratified entries is an editorial change
   only; no evidence or wording changed. Precedent: the 2026-06 path rename.
