# 2026-09-19 — Preserve provider rate-limit diagnostics

RATIFIED in session: Maxime Rivest, "Yes, ok, perfect, do it, go", after
reviewing which Azure capacity-error headers lm15 discarded and the proposal
to specify the behavior before implementing Python and TypeScript.

Normative rules: docs/error-diagnostics.md, linked from spec/vocabularies.md.
Shared fixtures: errors/diagnostic-headers.json.

Evidence: receipts/2026-09-19-azure-endpoint-alias/extended/. Responses on a
capacity-1 DeepSeek deployment failed with no_capacity on BOTH Azure hostname
families. Replies included a 1 RPM limit, negative remaining request balance,
reset values exceeding 60 seconds, Retry-After, and correlation IDs. Longer
spacing restored success on both hosts. Both hosts served DeepSeek and Kimi
successfully at a larger allowance. The initial hostname-only explanation was
not supported; collecting only the message concealed useful evidence.

Decisions:
- A closed, bounded, immutable diagnostic header snapshot on errors. Keep
  vendor spellings/units and duplicate values rather than invent a universal
  quota model or collapse contradictory evidence.
- Existing retry-hint precedence stays; numerical millisecond headers are a
  fallback. Reset headers are evidence, not automatic sleep instructions.
- Add apim-request-id fallback; keep existing body and header precedence.
- Render raw/advisory details without rewriting the provider message.
- Cover synchronous, asynchronous, auxiliary, rejected-stream and HTTP-200
  in-stream errors. Add optional `ErrorDetail.http_response` (default empty,
  omitted when empty), because ErrorDetail has no pre-existing metadata slot.
  This keeps saved/replayed streams truthful. No new ErrorCode or error class.
  Never label SSE failures 200.
- No automatic retries, endpoint switching, quota change or purchase.

Trade-offs: exact vendor evidence is less convenient than a fabricated common
quota/reset schema, but portable and honest. The allowlist omits unknown
vendor headers; adding more is an explicit contract extension. Size/count
bounds deliberately omit oversized/extra values rather than retain arbitrary
server output. Browser CORS may hide otherwise available headers. Snapshot
headers on a long-lived stream describe its handshake, not a live quota feed.

Python and TypeScript implement this amendment and consume the same fixture.
Other ports must implement it before claiming this diagnostics behavior;
pinning the spec alone is not proof of conformance. The separate TypeScript
cloud-identity/endpoint amendment is not implemented by this diagnostics task.
