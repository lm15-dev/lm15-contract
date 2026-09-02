# scrapes/ — the rolling provider-documentation scrape

Locally cached provider reference pages, refreshed in place. This is the
workspace's only copy: the reference implementation's doc-drift check reads
`scrapes/<provider>/pages/` directly, and design passes (`playbooks/
design-pass.md`, step 3) start from a fresh run of these scripts.

| Provider | Pages | Load-bearing page | Refresh |
|---|---|---|---|
| OpenAI | `openai/pages/` (39) | `responses--create.md` | `bash scrapes/openai/update.sh` |
| Anthropic | `anthropic/pages/` (25) | `messages--create.md` | `bash scrapes/anthropic/update.sh` |
| Gemini | `gemini/pages/` (14) | `generate-content.md` | `bash scrapes/gemini/update.sh` |
| xAI | `xai/pages/models.md` (1) | — | hand-fetched 2026-09-01; no script yet |

Every `update.sh` sources `fetch.sh`: a page is written only when the
server answers 200 with a body. A dead URL keeps the cached copy, is
printed, and makes the script exit 1. Never commit a page whose body is
"Not Found"; fix the URL in the script instead (18 pages rotted that way
before the guard existed, 2026-09-02).

This is distinct from `research/<topic>/sources/`: those are dated,
hashed snapshots frozen with a design pass and never refreshed. A scrape
here is the current page; a research source is the page as it was when a
rule was written.

Sources: OpenAI `developers.openai.com` (native `.md` and Stainless
`/index.md`), Anthropic `platform.claude.com/docs/en/api` (native `.md`),
Gemini `ai.google.dev` (native `.md.txt`).

History: moved from `curl-fixtures/api-references/` on 2026-09-02 after
that repository was found archived on GitHub with its scraper fixes
unpushable (`changes/2026-09-02-receipts-and-scrapes-home.md`). Earlier
commit history for these pages lives in the archived repository
(`lm15-dev/curl-fixtures`, commits `a6dae55`..`1af43bf`).
