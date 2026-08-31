# 2026-08-31 — list_models becomes a harness direction (models)

Ratified: Maxime Rivest, 2026-08-31 (session assent: "i ratify, commit and
push, and cover list_models for port readiness"); transcribed.

Promotes the provisional model-listing surface
(`changes/2026-08-31-list-models-provisional.md`) to harness-covered
conformance. What freezes is the MAPPING (wire GET request shape; wire
entry → canonical `ModelInfo`), not catalog contents — pinned bodies are
snapshots of a changing server-side catalog.

## What lands

- `harness/PROTOCOL.md` — two new ops: `build_models_request` (the wire GET
  request, body null) and `parse_models_response` (canonical ModelInfo
  list, INCLUDING `origin.provider_data`).
- `harness/check.py` — new direction `models` (in `--direction all`), two
  results per case (`<id>[build]`, `<id>[parse]`):
  - build compares the wire request like the request direction;
  - parse strips `origin.provider_data`, compares the mapped surface
    against `goldens/<provider>/models.json`, and verifies the
    verbatim-embedding rule mechanically: the stripped `provider_data`
    values must be an order-preserving subsequence of the body's entries
    under the case's `entries_key` (skips allowed, inventions and edits
    not).
- Six case files (`cases/*/models.json`, ids `<provider>.models`) binding
  the six live-receipted bodies from the provisional entry; the
  `tools/orphan-allowlist.json` `body_dirs` list burns down to empty in
  this commit per its own rule.
- Six goldens drafted by the reference shim and cross-checked against the
  receipts table: openai 132, openai_chat (Groq) 14, anthropic 10,
  gemini 53, openai-codex 9, claude-code 10 entries.
- `harness/fake_shim.py` + `harness/selftest.py` — two new proven
  mutations: `models_wrong_id` (parse drift) and `models_param_drop`
  (query-parameter loss).
- `tools/audit.py` — models-surface cases are exempt from the
  chat-orphan rule (no canonical_request by design) and get their own
  completeness rule: request + pinned_body + entries_key + golden, or the
  audit fails.
- `spec/SCOPE.md` — model listing moves from PROVISIONAL to FROZEN
  (mapping and request shape), alongside an overdue FROZEN entry for the
  auth direction. Live sessions and non-chat endpoints remain provisional.

## Subscription dialects in a deterministic harness

`openai-codex` and `claude-code` are covered with harness-injected
credentials: the shim constructs Codex with the pinned account id
`test-account` (PROTOCOL.md) because the header is compared verbatim and a
real account id must never enter the corpus; the injected api_key stands in
for OAuth bearer tokens. `client_version=0.147.0` pins the reference
constant and bumps via a changes/ entry. The claude-code `user-agent`
(`claude-cli/<version>`) is transport noise per DROP_HEADERS and stays
unpinned.

## Evidence at landing time

- `harness/check.py --shim python --direction models`: pass 12 / fail 0
  (6 build + 6 parse), inside the no-network sandbox.
- `harness/selftest.py`: baseline green in all seven directions; all 10
  mutations caught red.
- Golden counts equal the live-receipt counts for all six providers, and
  the ordered-subsequence embedding check passed with zero skipped entries.

## Stated trade-offs

- Goldens pin the mapped surface only; the verbatim wire entries live once,
  in the pinned bodies, and the harness checks embedding mechanically. The
  alternative (duplicating every wire entry into goldens) would re-pin
  ~400 KB of body content as reviewable golden text.
- The fixture `request` blocks were transcribed from the reference adapter
  against the receipted endpoints (hosts, params, and entry counts
  corroborated by the live receipts). Header sets therefore inherit
  reference behavior at transcription time; a header the reference wrongly
  omitted would be frozen as omitted until a live recapture says otherwise.
- The build-side fixtures pin `client_version` and `chatgpt-account-id`
  exactly, so ports must share those constants; drift against the real
  Codex CLI version becomes a deliberate contract bump, never silent.
- Pagination is unexercised (all six catalogs fit one page today);
  multi-page listing remains additive future work, stated in SCOPE.md.
