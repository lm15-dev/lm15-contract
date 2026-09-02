# 2026-08-31 — files lifecycle: account-scoped storage as a full surface

Ratified: Maxime Rivest, 2026-08-31 (session assent: "ok go, implement
the `files`" over the design closed across the batch-design and
file-APIs research sessions); transcribed, with two deviations forced
by live wire facts and one by a frozen invariant — each stated below.

Files stop being an upload-only stub. The portable lifecycle is five
operations — upload, get, list, delete, download — plus a `wait_ready`
poller, on OpenAI, Anthropic, and Gemini, with an async twin each.

## Contract surface

- Types (spec/types.md): `FileUploadRequest` loses `model` (files are
  account-scoped on every provider; the field implied a scoping no wire
  has). `FileUploadResponse` is REPLACED by `FileInfo` (id, filename?,
  media_type?, size_bytes?, created_at?, expires_at? both ISO-8601 UTC
  normalized, readiness, downloadable tri-state, provider_data
  verbatim). New `FilePage` (items + opaque `next_cursor`).
- `FileInfo.id` is the canonical media-Part `file_id` reference:
  OpenAI/Anthropic ids verbatim; **Gemini the file URI verbatim** —
  model requests address files by URI while the REST resource lives at
  `files/<id>`; the adapter derives one from the other. This fixes the
  pre-existing bug where upload returned the resource name that the
  frozen chat mapping would have placed, invalid, into
  `fileData.fileUri`.
- Vocabularies (spec/vocabularies.md): new closed `FileReadiness`
  (`pending`/`ready`/`failed`) with documented provider folds; NOT the
  provider wire words. Suffix-matched on Gemini per the
  `BATCH_STATE_*` drift precedent.
- `purpose` is NOT portable surface: an OpenAI storage classification.
  The reference defaults to `user_data` (current OpenAI guidance;
  formerly `assistants`), sets `batch` itself for batch inputs, and
  honors `extensions["purpose"]`.
- Serde: three new kinds `file_upload_request`, `file_info`,
  `file_page` (PROTOCOL.md list, audit coverage lens, seven fixtures in
  serde/canonical.json, dual-landed). `bytes_data` travels as base64;
  `path` serializes as a plain string — the media-part precedent, and
  REQUIRED by frozen INV-009 ("on the wire a path serializes as its
  string"); the earlier "path is runtime-only" draft idea is dropped
  for that named reason. Uncovered-surface debt drops to 5 types (the
  four media-generation types and ToolCallInfo).
- Download is a CORE operation on all three providers — the research
  claim "Gemini has no download" was overturned live: the endpoint
  (`files/<id>:download?alt=media`) exists and refuses non-generated
  files. Which files download is per-file provider policy (Anthropic:
  tool-generated only; OpenAI: by purpose; Gemini: generated only);
  lm15 forwards the provider's typed refusal and never second-guesses.
- `downloadable` is tri-state: Anthropic reports it verbatim; Gemini is
  derived from the server's stated rule (`downloadUri` present → true,
  `source: UPLOADED` → false); OpenAI does not report it per file →
  null.
- Deletion returns nothing: a successful response IS the confirmation;
  acknowledgement bodies differ per provider and carry no canonical
  information.
- Enumerability is a core op (`file_list`), same reasoning as
  `batch_list`: the provider is the system of record. Cursors are
  opaque canonical strings (OpenAI `last_id`+`has_more`; Anthropic
  `next_page` → `?page=`; Gemini `nextPageToken`).
- `file_wait_ready` mirrors BatchJob.wait: returns the terminal
  snapshot (`ready` or `failed`), the caller inspects; only Gemini
  uploads are ever `pending`.
- Single-shot upload only in this cut; Gemini's resumable protocol for
  very large media is future additive work (stated trade-off: very
  large video uploads are not yet portable).
- Subscription adapters (claude-code, openai-codex) block all five
  drivers: files are an API-key surface.

## Wire facts established live (2026-08-31, transcripts in
lm15-contract/receipts/2026-08-31-files/)

- Anthropic Files is GA multipart/form-data — NO beta header required
  (the raw-body + x-filename upload shipped before was stale);
  `downloadable` and `expires_at` on the wire; list cursor is an opaque
  `next_page` token accepted as `?page=`; delete returns
  `{id, type: "file_deleted"}`; download of a user upload refuses 400
  `file_not_downloadable`.
- OpenAI upload with `purpose=user_data` verified; file metadata has NO
  MIME type; epoch timestamps; batch-purpose files carry epoch
  `expires_at`; list pages with `after=<last_id>` + `has_more`;
  download SUCCEEDED live for a batch-purpose file and refused 400 for
  `user_data`; delete returns `{deleted: true}`.
- Gemini multipart/related upload carries `display_name` (raw protocol
  drops the filename — the reason for the multipart switch); upload
  wraps the object in `{"file": ...}` while get/list return it bare;
  `sizeBytes` is int64-as-string; `expirationTime` ~48h with nanosecond
  fractions; `uri` addressing; list pages with `pageToken`; delete
  returns `{}`; `:download?alt=media` refuses non-generated files 400
  "Only GENERATED files can be downloaded".

## Not yet landed (stated, not absorbed)

- The harness `files` direction and its cases/goldens (transcripts are
  in the workspace; they land with the direction under AUTHORITY rules,
  together with the still-owed `batch` direction).
- Resumable (large-media) upload.

## Evidence at landing time

- lm15-python: 729 tests green including 32 new files tests (readiness
  folds, cursor round trips on all three pagination dialects, typed
  download refusals, the Gemini URI-into-chat-wire loop, wait_ready
  polling/timeout, subscription blocks, async twin, serde round trips
  incl. `downloadable: false` survival).
- Live end-to-end with the shipped code: on Anthropic and Gemini the
  FULL loop (upload → wait_ready → the file answering a question in a
  chat request via Part.file_id → get → list → typed download refusal
  → delete → typed get-after-delete). On OpenAI all five file
  operations succeeded live; only the chat-with-file completion was
  blocked by the account's billing hard limit (429, the same wall as
  the batch campaign) — that one arrow rests on the frozen chat
  mapping's existing input_file case, stated, not absorbed.
- All contract gates green; serde direction covers the new kinds.
