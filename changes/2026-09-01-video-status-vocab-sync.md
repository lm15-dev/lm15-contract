# 2026-09-01 — spec sync: VideoStatus vocabulary tables

Ratified: Maxime Rivest, 2026-09-01 ("fix the spec drift").

## What this is (and is not)

`tools/spec_drift.py` flagged three reflected surface items missing
from `spec/vocabularies.md`: `VideoStatus`, `VIDEO_STATUSES`, and
`VIDEO_TERMINAL_STATUSES`. The vocabulary itself was ratified with the
video-generation surface (changes/2026-09-01-video-generation.md) and
is live in the reference implementation, the serde corpus, and the
`video` harness direction (24/24 green). Only the human-readable
vocabulary tables were never written. This entry adds them.

No value is added, removed, or renamed. No adapter behavior changes.
This is documentation catching up to an already-ratified surface, not
a new decision.

## Spec surface

- `## VideoStatus` section: five values
  (`queued`/`running`/`completed`/`failed`/`cancelled`), runtime
  mirror `VIDEO_STATUSES`, provider folds transcribed from the shipped
  adapters (openai `_VIDEO_STATUS_MAP`, xai `_VIDEO_STATUS_MAP`,
  gemini's done/error derivation).
- `## VIDEO_TERMINAL_STATUSES` section: derived subset
  (`completed`/`failed`/`cancelled`), backing `VideoJobInfo.done`,
  parallel to BATCH_TERMINAL_STATUSES.
- One behavior is now WRITTEN DOWN rather than newly decided: the
  video adapters raise `ProviderError` on an unknown wire status,
  which deviates from forward-compatibility rule 2 (fold, never
  crash). The deviation was ratified with the surface — the harness
  status-vocabulary-drift selftest mutation exists precisely to keep
  it — and the section states it as an explicit exception with its
  reason (a folded fallback would steer a polling loop wrong).

## Evidence

Folds transcribed from `lm15-python/lm15/providers/{openai,xai,gemini}.py`
as pinned by the video campaign's live captures
(`lm15-contract/receipts/2026-09-01-video/`, `receipts/2026-09-01-xai/`).
`tools/spec_drift.py` green after this entry; no fixture changes.
