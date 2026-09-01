# 2026-09-01 — OpenAI live captures land: batch and files debts close

Recorded: 2026-09-01. The account's billing hard limit — the one blocker
named in changes/2026-08-31-batch-lifecycle.md and
changes/2026-08-31-files-lifecycle.md — was lifted by the maintainer.
Every OpenAI claim that previously rested on documented shapes and
synthetic tests is now backed by live wire evidence. No contract
surface changes; this entry upgrades evidence status only.

## Batch (transcripts in lm15-dev/curl-fixtures/batch-2026-08-31/)

- Submit verified live: JSONL upload (`purpose=batch`) + `/v1/batches`
  create with `metadata.label` (openai-submit.json). Status polled
  through `validating` → `completed`, request_counts 2/2
  (openai-status-recheck.json).
- Results verified live: output file JSONL (openai-results.jsonl),
  parsed by the shipped code through the FROZEN chat response mapping —
  re-attach by id alone, entries in submission order (`Paris`,
  `Tokyo`), label and normalized created_at intact.
- List verified live (openai-list.json): `data` + `has_more`, label in
  metadata — `batches()` enumeration works against the real queue.
- Cancel verified live end to end: submit → `queued`, cancel →
  `cancelling` (≈10 minutes on the real wire) → `cancelled`
  (openai-cancel.json). The BatchJob.wait timeout path also fired
  live, exactly as specified. New live edge, pinned by test: a batch
  cancelled during `validating` reports `request_counts.total: 0` —
  the provider never registered the requests — so `results()` is
  honestly EMPTY; lm15 does not fabricate entries from the (expiring)
  input-file side-channel. Cross-provider note, stated: Anthropic's
  results file lists every request even when cancelled, so entry
  counts for cancelled-early jobs legitimately differ by provider —
  each mirrors its provider's own accounting.

## Files (transcripts in lm15-dev/curl-fixtures/files-2026-08-31/)

- The one arrow billing blocked is closed: upload a PDF → `file_id` in
  a chat request → gpt-5-nano answers the magic word (`PLUM`). The full
  five-op loop now has live shipped-code proof on ALL THREE providers.
- Successful `file_download` through the shipped code (batch output
  file, 7536 bytes) — the success path was previously curl-only.
- Async twins (`AsyncOpenAILM`) proven live: upload, wait_ready, list,
  delete, batches enumeration.

## OpenRouter (new key, smoke only)

Chat Completions dialect route works live (`openai/gpt-5-nano` →
`Rome`; 425 models listed); files raise UnsupportedFeatureError as
declared. No contract claims added — OpenRouter remains a compat
preset, not a first-party adapter.

## Still owed (stated, not absorbed)

- The harness `batch` and `files` directions (cases/goldens/mutations)
  — now fully UNBLOCKED: complete transcripts exist for all three
  providers on both surfaces.
- Batch docs graduation (recipe rewrite with captured outputs).
