# lm15 1.0 scope

What the 1.0 freeze covers, what is provisional, and what is out of scope.
Companion to [types.md](types.md), [vocabularies.md](vocabularies.md),
[invariants.md](invariants.md), and `harness/PROTOCOL.md`.

## FROZEN — the chat core, auth resolution, and model listing

The 1.0 contract freezes exactly the surface the seven harness directions
exercise (`request`, `response`, `stream`, `error`, `serde`, `auth`,
`models`):

- **Canonical types** — Part/Message/Request/Response/StreamEvent/Delta,
  Tool, Config family, Usage, ContinuationState (types.md tables).
- **Canonical serde** — the one omission rule, the Number rule, opaque
  payload verbatimness, and the from_dict leniencies (serde-rules.md,
  INV-040..048).
- **Errors** — the canonical class hierarchy, ErrorCode vocabulary, and HTTP
  mapping (vocabularies.md "ErrorCode").
- **Request building** — canonical Request → provider wire request for the
  four adapters (`openai`, `openai_chat`, `anthropic`, `gemini`),
  including the four blessed extension knobs (INV-049).
- **Response parsing and streaming** — provider body/SSE → canonical
  Response and the post-coalesce event trace (MAP-1..3).
- **Credential resolution** — the AUTH-1 chain as observed through AUTH-7
  explain output, and the AUTH-5 secrecy invariant (spec/auth.md, ratified
  2026-08-31; harness `auth` direction over `auth/resolution.json`).
- **Model listing** — `list_models()` wire requests and the wire-entry →
  `ModelInfo` mapping for all six adapters (harness `models` direction;
  mapping rules in `changes/2026-08-31-list-models-provisional.md`, promoted
  by `changes/2026-08-31-list-models-harness.md`). What freezes is the
  MAPPING and the request shape — pinned bodies are catalog snapshots, and
  catalog contents change server-side without contract meaning. Multi-page
  catalogs remain future additive work.

Frozen means: ports must match exactly; the corpus is the oracle per
AUTHORITY.md; behavior changes require maintainer ratification.

## PROVISIONAL — may change in 1.x

These surfaces ship in 1.0 but are NOT frozen. The intent is additive
evolution, but breaking changes in a 1.x release are permitted with a
`changes/` entry (no major-version bump required):

- **Non-chat endpoints** — files, batch, image generation,
  audio generation (the `FileUploadRequest`/`FileInfo`/`FilePage`/`Batch*`/
  `ImageGeneration*`/`AudioGeneration*` types and their adapter routes).
  Media generation stays in because its outputs are the SAME typed parts
  the chat surface accepts as inputs (`ImagePart`, `AudioPart`) — the
  conversation with the arrow reversed.
- **Live sessions** — `LiveConfig` and the live client/server event types;
  the live surface has no harness direction yet.

Ports may implement provisional surfaces, but conformance does not require
them and their fixtures carry no freeze guarantee.

## OUT OF SCOPE for 1.0

- **Embeddings** — removed pre-1.0 (2026-08-31,
  `changes/2026-08-31-remove-embeddings.md`). Membership principle: lm15
  speaks to models through Parts — messages in, messages (or the same
  typed media parts) out. Embeddings are representation, not conversation:
  text in, meaning-vector out, and nothing round-trips through the Part
  vocabulary. They were the one surface held "by cohabitation" rather than
  by type-system symmetry; a scope with no exceptions is easier to defend.
  Use a provider's own client for vectors.

- **`gemini.cached_content`** — Gemini explicit caching requires a
  cache-creation side channel (a separate `/cachedContents` POST before the
  chat request), which the contract's pure build/parse model cannot express;
  CacheConfig covers only in-request cache hints.
- **`openai.computer_use`** — provider-executed computer use surfaces
  execution traces that MAP-1 keeps out of canonical parts; canonical access
  would need a NEW part type via MAP-1's amendment path (additive, never a
  reinterpretation of `tool_call`).

Both remain reachable today via `config.extensions` passthrough and
`provider_data`, with no contract guarantee.

## Post-1.0 change policy

The frozen surface changes only ADDITIVELY: new types, new fields with
omitted-when-absent semantics, new vocabulary values, new serde kinds, new
harness ops — each with a `changes/` entry per AUTHORITY.md. Removing or
changing the meaning of anything frozen is a breaking change requiring
maintainer ratification and a major version. Enforcement is mechanical: the
surface ratchet (`tools/audit.py` over `surface_dump`) catches removals, and
`tools/spec_drift.py` fails CI when reflection and the spec tables diverge.

---

Ratified by maintainer delegation, 2026-06-11.
