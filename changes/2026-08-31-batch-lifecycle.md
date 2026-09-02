# 2026-08-31 — batch lifecycle: the third execution mode

Ratified: Maxime Rivest, 2026-08-31 (session assent: "i think you can
implement batch fully now" over the twelve decisions of the design draft
lm15-python/docs/cookbooks/drafts/batch-jobs.md); transcribed.

Batch becomes a real execution mode next to complete and stream: many
canonical Requests in, a ticket out, canonical Responses back — at the
provider's queue discount, with partial failure as a first-class
outcome. The submit-only stub (and its silent full-price local fan-out
under a fabricated, un-refetchable batch id) is gone.

## Contract surface

- Types (spec/types.md): `BatchRequest` gains `label`; `BatchResponse`
  is replaced by `BatchJobInfo` (id, status, label, created_at
  normalized to ISO-8601 UTC, provider_data verbatim) and `BatchEntry`
  (index, outcome, response | error). Entries are ALWAYS in submission
  order; providers return results out of order (observed live,
  Anthropic, 2026-08-31), so re-sorting is normative.
- Vocabularies (spec/vocabularies.md): `BatchStatus` re-cut to
  `queued/running/cancelling/completed/failed/cancelled/expired`
  (`submitted` folded into `queued`); new `BatchOutcome`
  (`succeeded/errored/cancelled/expired`); documented provider folds.
  Job lifecycle and entry fate are deliberately separate dimensions.
- Serde: three new kinds `batch_request`, `batch_job`, `batch_entry`
  (PROTOCOL.md list, audit coverage lens, seven fixtures in
  serde/canonical.json, dual-landed). Uncovered-surface debt drops to
  7 types / 0 enums.
- Five pure operations per provider (submit, status, results, cancel,
  list), exposed by the reference as build/parse hooks so async twins
  and a future harness `batch` direction drive identical code. Entry
  bodies parse through the FROZEN chat response mapping — no second
  parser.
- Enumerability is a core op: `batch_list` exists because queues
  remember and submitters forget; recovery from a lost id never
  depends on client-side care. `label` maps to provider metadata;
  where the wire has no label field the submit REJECTS (no silent
  drop) — Anthropic verified live: `metadata: Extra inputs are not
  permitted`.

## Wire facts established live (2026-08-31, transcripts in
lm15-contract/receipts/2026-08-31-batch/)

- Anthropic Message Batches: create (inline requests), status, results
  JSONL (returned OUT of submission order), list, no label field.
- Gemini Batch Mode: `:batchGenerateContent` inline create; states are
  `BATCH_STATE_*` (NOT the documented `JOB_STATE_*` — probing beat the
  docs); `displayName` optional; inline results under
  `response.inlinedResponses.inlinedResponses[]` with `metadata.key`;
  list via `GET /v1beta/batches` → `operations`.
- OpenAI Batch: JSONL file upload (`purpose=batch`) verified; batch
  creation BLOCKED at capture time by the account's billing hard limit
  — the OpenAI adapter ships against its documented shapes and synthetic
  tests, with live capture owed as soon as billing allows. No fixture
  claims what was not captured.

## Not yet landed (stated, not absorbed)

- The harness `batch` direction and its cases/goldens: they require
  pinned bodies under AUTHORITY rules; Anthropic and Gemini transcripts
  exist in the workspace and land with the direction; OpenAI waits on
  billing headroom.
- The design draft's graduation (recipe rewrite with captured outputs).

## Evidence at landing time

- lm15-python: 699 tests green including 22 new batch tests
  (out-of-order re-sort, fill-in for expired jobs, label honesty,
  handle wait/timeout semantics, async twin, serde round trips, no
  silent fallback anywhere).
- Live end-to-end with the shipped code: re-attach by id, ordered
  results, `batches()` enumeration, labels and normalized timestamps
  verified against api.anthropic.com and generativelanguage.googleapis.com.
- All contract gates green; serde direction covers the new kinds.
