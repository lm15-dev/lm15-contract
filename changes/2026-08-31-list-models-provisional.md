# 2026-08-31 — list_models: live model listing (PROVISIONAL surface)

Adds a provisional non-chat endpoint to the contract: **live model
listing**. Every adapter exposes `list_models()` returning a sequence of
canonical `ModelInfo` values (the ratified canonical JSON in
`lm15-python/docs/model-hydration.md` — no new types). SCOPE.md's
PROVISIONAL list gains this surface; like live sessions, it has **no
harness direction yet** and conformance does not require it.

## Canonical mapping (normative for this surface)

For each entry in the provider's list response:

- `id` — the usable `Request.model` string for that adapter. This is the
  wire `id` verbatim for `openai`, `openai_chat`, `anthropic`; the wire
  `name` with the `models/` prefix stripped for `gemini` (build_request
  re-prefixes); the wire `slug` for `openai-codex`.
- `provider` — the adapter's provider string.
- `api_family` — `openai_responses` (openai, openai-codex),
  `openai_chat`, `anthropic_messages` (anthropic, claude-code),
  `gemini_generate_content`.
- `origin` — `{"type": "provider", "provider_data": <wire entry>}` with
  the wire entry embedded VERBATIM (opaque-payload rule, never cleaned).
- Entries without a usable id string are skipped, never invented.

Listing is ADVISORY metadata per the model-hydration guardrail: it must
never change what `build_request` produces.

## Wire mapping

| adapter | request | entries under |
|---|---|---|
| openai | `GET {base}/models` | `data` |
| openai_chat | `GET {base}/models` | `data` |
| anthropic | `GET {base}/models?limit=1000` | `data` |
| claude-code | inherited from anthropic (OAuth headers) | `data` |
| gemini | `GET {base}/models?pageSize=1000` | `models` |
| openai-codex | `GET {base}/models?client_version=<codex-cli-version>` | `models` |

Pagination note: `limit=1000` / `pageSize=1000` fetch the whole catalog
in one page today (anthropic `has_more: false`, gemini no
`nextPageToken`, both observed live below). Multi-page catalogs are
future additive work.

Errors flow through each adapter's normal `normalize_error` mapping.
The Codex backend's non-OpenAI error envelope (`{"detail": "..."}`) is
recovered by the openai-codex adapter; an unknown model slug maps to
`UnsupportedModelError` (observed live 2026-08-31: HTTP 400, detail
"The 'gpt-5.3-codex' model is not supported when using Codex with a
ChatGPT account.").

## Live receipts (wire-fact evidence per AUTHORITY.md)

All captures HTTP 200, verbatim bodies pinned under
`bodies/<provider>.models/<timestamp>.txt`:

| provider | endpoint host | timestamp (UTC) | entries |
|---|---|---|---|
| openai | api.openai.com | 2026-08-31T13-40-29Z | 132 |
| openai_chat | api.groq.com | 2026-08-31T13-40-29Z | 14 |
| anthropic | api.anthropic.com | 2026-08-31T13-40-29Z | 10 |
| gemini | generativelanguage.googleapis.com | 2026-08-31T13-40-29Z | 53 |
| openai_codex | chatgpt.com/backend-api/codex | 2026-08-31T13-40-42Z | 9 |
| claude_code | api.anthropic.com (OAuth) | 2026-08-31T13-40-42Z | 10 |

All six bodies were parsed by the reference implementation
(lm15-python) into ModelInfo tuples with the counts above, and a
ModelInfo serde round-trip on live entries passed
(`model_info_to_dict` / `model_info_from_dict`).

## Implementation surface (reference: lm15-python)

- `EndpointSupport.models` (bool, default false) — capability flag.
- `BaseProviderLM.list_models()` shared driver over two adapter hooks
  (`_models_request`, `_models_from_body`); async twins mirror it.
- `ProviderLM` protocol gains `list_models(self) -> tuple[ModelInfo, ...]`.

Ports (Go, Rust, TypeScript, Julia) implement the same method name,
flag, and mapping rules. Provisional: fixtures carry no freeze
guarantee; breaking changes in 1.x are permitted with a changes/ entry.
