# 2026-09-01 — harness directions for the endpoint surfaces (files / batch / generation)

Ratified: Maxime Rivest, 2026-09-01 (session assent: "harness directions
for all four endpoint surfaces in one campaign (same recipe each)").

The batch, files, and media-generation surfaces had contract-pinned
types and serde kinds but no harness oracle: a port could implement all
four surfaces wrong and stay green. Three new directions close that —
`files`, `batch`, `generation` (image + speech share one direction; the
op pair discriminates by kind).

## Protocol

Six new vet ops, mirroring the reference implementation's pure
build/parse hooks (the seam every port implements):
`file_op_build`/`file_op_parse`, `batch_op_build`/`batch_op_parse`,
`generation_build`/`generation_parse`. Deviation from the models
precedent, stated: these are action-discriminated per surface (6 ops)
rather than one op per hook (~20) — the protocol stays readable and a
port's dispatcher maps actions to hooks mechanically.

## Corpus

13 new cases (63 harness results), every pinned body a live capture:

- files: anthropic / openai / gemini upload-get-list-delete-download
  step cases from the 2026-08-31 files campaign.
- batch: anthropic (incl. the OUT-OF-ORDER results body — the re-sort
  proof), openai (JSONL upload, label metadata, validating-cancel edge),
  gemini (inline submit, results inlined in the terminal operation).
- generation: openai image (jpeg via output_format), openai image_edit
  (fresh 2026-09-01 capture receipting the `image[]` multipart field),
  openai speech (raw MPEG body; content-type header pinned), gemini
  image (narration text next to the inline image), gemini speech
  (parameterized PCM MIME), xai image + image_edit (subscription OAuth
  captures; `image:{url}` data-URI edit, pixel-verified).

Two comparator mechanics, applied to BOTH sides identically: multipart
boundaries normalize to `BOUNDARY` (the only legitimately random byte),
and strings >= 512 chars digest to `sha256:<hex>` so goldens stay
reviewable while content drift is still caught exactly.

## Self-test

Seven new mutations, all caught red on green baselines: media-type
drift, dropped narration text, multipart field corruption, file
readiness flip, dropped query parameter, batch entry order swap
(pins the submission-order rule), and batch status vocabulary drift
(canonical word vs wire word).

## Audit

tools/audit.py learns the three surfaces (canonical payloads live in
`upload_request`/`batch_request`/`generation_request`/`steps`, with
models-style completeness rules) and the four generation serde kinds —
surface-coverage debt drops from 5 uncovered types to 1 (ToolCallInfo).
