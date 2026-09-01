# 2026-09-01 — xAI joins the corpus; the support matrix is pinned

Ratified: Maxime Rivest, 2026-09-01 ("xAI chat cases + support-matrix
pinning together"; the adapter itself landed 2026-09-01 with
subscription device-code OAuth after the xAI team recommended
subscription access).

## xAI cases

Provider `xai` (Chat Completions dialect at api.x.ai, preset pinned
live: max_tokens, deepseek-shaped reasoning_content,
stream_options.include_usage). Six additions, every body a live
capture via subscription OAuth:

- `xai.basic_text` — reasoning + text in one message; cached_tokens in
  usage.
- `xai.streaming` — SSE with usage in the final chunk. This case shares
  its canonical_request with basic_text (both captured "Say ok."); the
  fake shim now treats the stream flag as part of the wire identity.
- `xai.tools` — a tool_call WITH reasoning_content in the same message.
- `xai.models` — the 12-entry catalog with aliases and token prices.
- `errors/cases/xai.json` — xAI's own envelope (`{"code","error"}`,
  not OpenAI's): model-not-found 400 and unauthenticated 401, captured
  verbatim. The reference refolds it so the wire code lands in
  provider_code instead of being dropped.

Media-generation and image-edit xAI cases landed earlier today with the
generation direction (changes/2026-09-01-endpoint-harness-directions.md).

## Support matrix

`spec/support-matrix.json` pins provider → EndpointSupport booleans,
auth modes, and env-key conventions for all 7 first-class adapters.
`surface_dump` gains a reflected `providers` section, and tools/audit.py
compares pin against reflection in BOTH directions as a HARD check: an
adapter (or port) silently changing who supports what is contract
drift. Widening support lands in the matrix first, with live receipts.
