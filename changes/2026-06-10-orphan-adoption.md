# 2026-06-10 — Orphan adoption: canonical_requests for 23 of 27 orphan cases

The 27 allowlisted orphans (tools/orphan-allowlist.json) had live-validated
wire fixtures but no canonical_request. This change authors canonical
requests for 23 of them. No wire fixture (`request` block, headers, bodies)
was modified — only `canonical_request` / `canonical_request_provenance`
(and `"stream": true` flags on the two SSE cases) were added, each gated by
`harness/check.py --direction request` producing the recorded wire request
byte-identically against the unchanged fixture. Evidence per AUTHORITY.md:
wire-identical to the live-validated fixture via the harness; provenance
source `orphan-adoption`.

## Adopted (23)

- anthropic.inference_geo, anthropic.metadata, anthropic.service_tier
- gemini.safety_settings, gemini.store
- openai.background, openai.context_management, openai.conversation,
  openai.file_search, openai.include, openai.metadata,
  openai.previous_response_id, openai.prompt, openai.prompt_cache_key,
  openai.prompt_cache_retention, openai.reasoning_encrypted,
  openai.safety_identifier, openai.service_tier, openai.store,
  openai.stream_options, openai.top_logprobs, openai.truncation, openai.user

Notes:

- Provider-only knobs (metadata, store, service_tier, truncation, user,
  safety_identifier, include, top_logprobs, background, stream_options,
  context_management, conversation, previous_response_id, inference_geo,
  safetySettings, prompt_cache_key, prompt_cache_retention, and the
  file_search tool_choice shape) are carried via `config.extensions` —
  the legitimate provider-namespace channel. tools/audit.py reports them
  in its (report-only) extensions-passthrough burn-down list.
- openai.prompt_cache_key / prompt_cache_retention SHOULD map to the
  canonical `config.cache` (CacheConfig key/retention — the openai adapter
  supports it), but `lm15.serde.config_to_dict/config_from_dict` do not
  serialize `cache`, so a canonical_request dict cannot express it.
  Adopted via extensions for now; migrate to `config.cache` once serde
  round-trips CacheConfig (audit also reports CacheConfig as serde-uncovered).
- openai.reasoning_encrypted uses canonical `config.reasoning`
  (effort "low"); only the `include` knob rides extensions.
- openai.include / openai.top_logprobs use canonical `config.max_tokens`.
- openai.file_search uses a canonical BuiltinTool ("file_search"); its
  `tool_choice: {"type": "file_search"}` wire shape is not expressible by
  canonical ToolChoice (which would emit `{"type": "function", ...}`), so
  it rides extensions.
- openai.background and openai.stream_options gained `"stream": true`
  so the stream direction classifies their SSE pinned bodies correctly.
- Goldens for all 23 were drafted with tools/scribe_goldens.py
  (provenance `scribe-draft`, 2026-06-10). These drafts are UNREVIEWED —
  unlike the 69 goldens approved in goldens/REVIEW-2026-06-10.md — and
  pin regressions, not correctness, until human freeze.

## Still orphaned (4)

- **anthropic.cache_control** — the fixture records header
  `anthropic-beta: prompt-caching-2024-07-31`, but the reference adapter's
  `_headers()` only ever emits an `anthropic-beta` header for the
  code_execution builtin (`code-execution-2025-05-22`); the body
  (top-level `cache_control` via extensions) reproduces fine, the header
  cannot. Two lawful resolutions per AUTHORITY.md: (a) re-capture live —
  prompt caching is GA and likely no longer needs the beta header; if live
  accepts/omits it, update the wire fixture with the receipt; or (b) if
  live still requires the header, fix the adapter (lm15-python2) to send
  it when caching is requested — fix the code, never the fixture.
- **anthropic.system_content_blocks** — same `anthropic-beta:
  prompt-caching-2024-07-31` header problem (its system blocks carry
  cache_control); same two resolutions.
- **gemini.cached_content** — the fixture targets
  `POST .../v1beta/cachedContents`, a different endpoint that
  `build_request` (the only op the request direction exercises) can never
  produce; the adapter creates cached contents via an internal side call.
  Needs harness/protocol support for the cachedContents operation.
- **openai.computer_use** — the wire input contains provider-executed
  `computer_call` / `computer_call_output` items that `_build_input` cannot
  emit from any canonical Part (only function_call/function_call_output);
  adopting it would require smuggling the entire `input` array through
  extensions, which would misrepresent the conversation in canonical form.
  Needs a canonical mapping for provider-executed tool items first.
