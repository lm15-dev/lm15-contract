# 2026-06-11 — Prompt caching is GA: anthropic cache orphans re-captured live

Resolution path (a) from changes/2026-06-10-orphan-adoption.md: re-capture.
Anthropic prompt caching no longer needs the `anthropic-beta:
prompt-caching-2024-07-31` header. Both wire fixtures were rebuilt from the
reference adapter's `build_request` output for an authored canonical request
using the canonical `config.cache` key (CacheConfig), sent live VERBATIM, and
accepted with cache activity in usage. No adapter change was needed.

## Receipts (live, api.anthropic.com, model claude-sonnet-4-5)

- **anthropic.cache_control** — 2026-06-11T01-28-08Z, request sha256
  `2b15ce527fb0834df142599a9d658ddb45e01db5b5190a1541a29164c34c049d`,
  HTTP 200, `cache_creation_input_tokens=4191`, response id
  `msg_01JscN4ubCEQ6drbi1yvJ4Kb`. Canonical: `config.cache.prefix_until_index=0`
  → per-block `cache_control: {"type": "ephemeral"}` on the last user content
  block (the old fixture's TOP-LEVEL `cache_control` shape is gone with the
  beta header).
- **anthropic.system_content_blocks** — 2026-06-11T01-28-10Z, request sha256
  `1f21a5beaa4e280cc899ab769343c0a8d428b14c21c4d9eed134c4f51c1c6761`,
  HTTP 200, `cache_creation_input_tokens=4195`, response id
  `msg_018upjVEVbcoVpqxtEpKpDxP`. Canonical: `config.cache: {}` (mode auto) +
  string system → system emitted as one text block carrying `cache_control`.

Prompt bodies grew (~4k-token prefix) because cache activity requires the
Sonnet 1024-token minimum cacheable prefix; pinned bodies replaced with the
fresh captures (old captures retained in bodies/ for history).

## Corpus effects

- Both cases gained `canonical_request` (+ provenance `live-recapture`),
  byte-match gated via `harness/check.py --direction request --case <id>`.
- Goldens drafted via tools/scribe_goldens.py (provenance `scribe-draft`,
  noted UNREVIEWED).
- tools/orphan-allowlist.json burned down 4 → 2; the remaining two
  (gemini.cached_content, openai.computer_use) are declared out of 1.0 scope
  by spec/SCOPE.md, cited in the allowlist comment.
