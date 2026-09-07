# receipts/ — raw evidence behind change entries

Dated, append-only capture folders: verbatim HTTP bodies, headers, SSE
streams, WebSocket transcripts, live `/models` listings, and the probe
scripts that produced them. A `changes/` entry cites the folder that holds
its receipts; the folder holds what was actually observed, unedited.

Naming: `receipts/<YYYY-MM-DD>-<topic>/`, so a listing reads
chronologically. Never edit a file inside a receipt folder; a new
observation is a new dated folder.

Rules:

- Receipts are evidence, not the oracle. `AUTHORITY.md` still applies: a
  fixture changes only with a change entry, and the entry cites the receipt.
- No live secrets. `tools/check_secrecy.py` scans this directory; headers
  files must not carry Authorization values (curl `-D` output does not,
  request headers do — never save request headers).
- Binary media is fine when it is the observed artefact (a generated image
  or video), but keep it to what the entry needs.

| Folder | Cited by |
|---|---|
| `2026-09-07-tool-result-media/` | `changes/2026-09-07-tool-result-content.md` (the MAP-10 design pass: ≈230 cells over 31 bindings, hidden-oracle visual checks, raw-wire probes, the fixture candidates behind `cases/*/tool_result_*.json`); superseded the same-day `changes/2026-09-07-tool-result-media-live.md` |
| `2026-08-31-batch/` | `changes/2026-08-31-batch-lifecycle.md` |
| `2026-08-31-files/` | `changes/2026-08-31-files-lifecycle.md` |
| `2026-09-01-chat-builtin-tools/` | `changes/2026-09-01-chat-dialect-builtin-tools.md` |
| `2026-09-01-genmedia/` | `changes/2026-09-01-media-generation.md` |
| `2026-09-01-live/`, `2026-09-01-live-transcripts/` | `changes/2026-09-01-live-ergonomics.md`, `changes/2026-09-01-openai-live-captures.md`, `changes/2026-09-01-openai-realtime-ga.md` |
| `2026-09-01-logprobs-toolchoice/` | `changes/2026-09-01-provider-refresh.md`, lm15-python `docs/drafts/logprobs-and-builtin-tool-forcing.md` |
| `2026-09-01-model-listings/` | `changes/2026-09-01-provider-refresh.md` (the live `/models` listings and report behind the model-name refresh) |
| `2026-09-01-video/` | `changes/2026-09-01-video-generation.md`, `changes/2026-09-01-video-status-vocab-sync.md` |
| `2026-09-01-xai/` | `changes/2026-09-01-xai-provider.md` |
| `2026-09-03-deepseek-anthropic/` | `changes/2026-09-03-deepseek-anthropic-live.md` (15 discovery probes that shaped `AnthropicCompat`, then the capture's probes and SUMMARY) |
| `2026-09-03-zai/` | `changes/2026-09-03-zai-live.md` (probe receipts, the unfunded-account 429, models listing, SUMMARY) |
| `2026-09-03-deepseek/` | `changes/2026-09-03-deepseek-live.md` (probe receipts, models listing, SUMMARY of the capture) |

History: these folders lived in `lm15-dev/curl-fixtures/` (seven of them
never committed there) and `lm15-dev/model-listings/` (no repository) until
2026-09-02, when the curl-fixtures repository was found archived on GitHub.
Two folders had commit history there (`3ad5420`, `ced2abd`); the rest have
none. Moved verbatim; see `changes/2026-09-02-receipts-and-scrapes-home.md`.
