# lm15 contract scope

What the frozen contract covers, what is provisional, and what is out of scope.
Companion to [types.md](types.md), [vocabularies.md](vocabularies.md),
[invariants.md](invariants.md), and `harness/PROTOCOL.md`.

*(Originally ratified as the 1.0 freeze on 2026-06-11; updated to reflect the
2.x contract — 2.4.0 across six SDKs at parity: Python, TypeScript, Rust, Go,
Julia, and R — with 18 harness directions and 2.0 one-meaning `Usage`
semantics under MAP-19.)*

## 2026-09-22 managed-authentication amendment — RATIFIED CORE (implemented)

[AUTH-12–26](auth-managed.md) defines SDK-owned login/lifecycle and an explicitly
interactive `connect()` returning a model-bound client. It preserves existing
API-key/cloud-only use, canonical request/response types, and subscription
access. Explicit key/named cloud authority wins; otherwise subscriptions
precede ambient keys. Existing Claude/Codex paths cannot be retired until a
permitted replacement proves equivalent account access under R1.
See [the amendment](../changes/2026-09-22-managed-authentication.md) for decisions,
[examples](../docs/auth-examples.md) and [acceptance suite](../auth/managed/README.md).

The core is ratified, implemented, and graded across SDKs by the `managed`
harness direction (45 runs). Reserved details (non-file stores, cross-tab
browser rules) remain reserved until promoted. Existing key/cloud/subscription
gates remain required; only the unsafe xAI fallback expectation is corrected
under R3.

The narrow bound-client convenience fills the selected model in a canonical
Request and returns full canonical results. It does not add conversation state,
an agent loop, model ranking, account fallback or inference retries. Provider
revocation, full same-slot multi-account arbitration and automatic imports from
foreign CLI login files are outside this first managed-auth contract.

## FROZEN — the chat core, auth resolution, model listing, and 2.0 usage

The frozen contract covers the core surfaces graded across the harness
directions (`request`, `response`, `stream`, `error`, `serde`, `auth`,
`token`, `models`, `router`, `mapping`, `managed`):

- **Canonical types** — 12 closed `Part` variants (`DataPart` added under
  MAP-14), Message/Request/Response/StreamEvent/Delta, Tool, Config family,
  `Adaptation` (MAP-13), `Usage` (2.0 one-meaning counters under MAP-19,
  `changes/2026-10-31-usage-one-meaning.md`), `InferencePricing`, and
  `ContinuationState` (types.md tables).
- **Canonical serde** — the one omission rule, the Number rule, opaque
  payload verbatimness, and the from_dict leniencies (serde-rules.md,
  INV-040..048), pinned by `serde/canonical.json` (round-trip) and
  `serde/reject.json` (`validate` invalid-input rejections).
- **Errors** — the canonical class hierarchy, ErrorCode vocabulary, and HTTP
  mapping (vocabularies.md "ErrorCode"), checking `class`, `code`, `provider`,
  `provider_code`, `status`, `request_id`, and `message`.
- **Request building** — canonical Request → provider wire request across all
  pinned doors (38 providers in `spec/support-matrix.json` and
  `tables/providers.json`), including the blessed extension knobs (INV-049)
  and visible adaptations (MAP-13).
- **Response parsing and streaming** — provider body/SSE → canonical
  Response and the post-coalesce event trace (MAP-1..4, MAP-9, MAP-20,
  MAP-24, INV-051).
- **Credential resolution & cloud signing** — the AUTH-1 chain and named
  cloud identities as observed through AUTH-7 explain output, the AUTH-5
  secrecy invariant, and SigV4 / token-exchange vectors (spec/auth.md;
  harness `auth` over `auth/resolution.json` + `auth/named-credentials.json`,
  and `token` over `auth/sigv4-vectors.json` + `auth/token-vectors.json`).
- **Model listing and routing** — `list_models()` wire requests and wire-entry
  → `ModelInfo` mapping (harness `models`), plus deterministic model-string
  routing (harness `router`).

Frozen means: ports must match exactly; the corpus is the oracle per
AUTHORITY.md; behavior changes require maintainer ratification.

## PROVISIONAL — may evolve additively or with a `changes/` entry

These surfaces ship and have their own harness directions (`files`, `batch`,
`generation`, `video`, `live`, `cache`, `ingest`), but are NOT frozen under
the same major-version gate as the core:

- **Non-chat endpoints** — files, batch, image generation, audio generation,
  and video generation (`FileUploadRequest`/`FileInfo`/`FilePage`/`Batch*`/
  `ImageGeneration*`/`SpeechGeneration*`/`VideoGeneration*`/`VideoJobInfo`
  types and their adapter routes; harness directions `files`, `batch`,
  `generation`, `video`). Media generation stays in because its outputs are
  the SAME typed parts the chat surface accepts as inputs (`ImagePart`,
  `AudioPart`, `VideoPart`) — the conversation with the arrow reversed.
- **Live sessions** — `LiveConfig` and the live client/server event types,
  graded by the `live` harness direction.
- **Chat Completions ingest** — `request_from_openai_chat` (MAP-12,
  ratified 2026-09-08;
  changes/2026-09-08-openai-chat-ingest.md): a chat request body read INTO
  a canonical Request under one preset's spellings, with a verdict per
  wire key (`tools/openai-chat-ingest-verdicts.json`) and the harness
  `ingest` direction. Provisional because the verdict table follows a
  wire lm15 does not own: a key OpenAI adds tomorrow needs a row, and a
  lossy class may be added when a new preset loses new information. No
  canonical type changes.
- **Judgments** — `DataPart`, `Config.probabilities`, the MAP-14 schema
  convention, and the `typesafe` provider (TypeSafe Jev, 2026-09-17,
  changes/2026-09-17-judgments.md). In by the same test that kept media
  generation: the answer is a Part that the chat surface also accepts as
  input (structured data in, structured data out). Provisional because
  one provider measures natively and the candidate-likelihood path
  depends on a server feature (`logprob_token_ids`) whose harness
  direction is deferred.
- **The gateway capture record** — `gateway/schema/capture-v1.json` and
  the day layout under `gateway/` (2026-09-19,
  changes/2026-09-19-capture-record.md; product boundary in
  changes/2026-09-19-gateway-boundary.md). Not a canonical type: it is
  what the lm15 gateway writes and what dashboards, decoders and the
  routing rules read, and it embeds the canonical `Usage`, `Adaptation`,
  `ErrorCode`, `Request` and `Response` verbatim under the decoder's
  contract pin. Provisional because no gateway has run yet: the first
  promoted capture under `gateway/captures/` is expected to add
  omit-empty fields. Checked by `tools/check_gateway.py`.
- **Cache resources** — the stored tier of MAP-6 (`CacheInfo`, `CachePage`,
  `CachedPrefix`, the `cache_*` verbs, the `cache` harness direction),
  added 2026-09-02 (changes/2026-09-01-caching-design.md). Provider-
  neutral in shape; Gemini is the first implementer.

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

- ~~`gemini.cached_content`~~ — was out of scope because the old adapter
  created the object inside `complete()`. Since 2026-09-02 the object is
  an explicit, provisional surface (above) and `CacheConfig.resource`
  references it from a pure `build_request`; the orphan case is superseded
  by `gemini.cache` + `gemini.cache_resource`.
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
