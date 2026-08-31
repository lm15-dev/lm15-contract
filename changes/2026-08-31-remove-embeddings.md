# 2026-08-31 — remove the embeddings surface (pre-1.0 scope cut)

Ratified: Maxime Rivest, 2026-08-31 (session assent: "we have never
released 1.0.0 yet and we are shaping up for it. so yes. now cut
embeddings."); transcribed.

Removes embeddings from lm15 entirely — types, adapter methods, support
flag, spec tables, docs. 1.0.0 has never shipped, so this is a pre-release
scope cut, not a breaking release; the surface was PROVISIONAL and never
harness-covered.

## Why (membership principle, now stated in SCOPE.md)

lm15's scope test is type-system symmetry: models you speak to through
Parts, that answer in Parts (chat) or in the same typed media parts
(generation). Embeddings are representation, not conversation — text in,
meaning-vector out, nothing round-trips through the Part vocabulary. It
was the one surface justified "by cohabitation" (same providers, same
keys) rather than by the type system. Cutting it leaves a scope with no
exceptions.

## What is removed

- Reference (lm15-python): `EmbeddingRequest`/`EmbeddingResponse` types
  and exports, the `ProviderLM.embeddings` protocol method, the base and
  async stubs, the openai (`/embeddings`) and gemini
  (`:embedContent`/`:batchEmbedContents`) implementations, the
  `EndpointSupport.embeddings` flag, endpoint conformance checks, tests,
  and all doc/cookbook/README coverage (cookbook 12 renamed to
  `12-batch-media-generation.md`).
- Contract: the two `spec/types.md` tables; the `EmbeddingResponse.vectors`
  citation in INV-008 and the `EmbeddingRequest.inputs` citation in
  INV-020 (both rules keep their other subjects); the PROVISIONAL listing
  in `spec/SCOPE.md`, replaced by an OUT OF SCOPE entry carrying the
  membership principle.

## What is deliberately NOT removed

- Historical `changes/` entries that mention embedding types
  (2026-06-10-number-rule, 2026-06-10-may-feature-vectors,
  2026-06-11-scope-1-0): immutable records of what was true when written.
- Model-catalog goldens listing `text-embedding-*` / `gemini-embedding-*`
  ids: those are wire facts of the providers' model lists, not lm15
  surface.
- Verbatim provider-docs mirrors mentioning embedding weights
  (file_search hybrid ranking): foreign wire documentation.

## Downstream effect

- The audit's surface-coverage report shrinks from 11 to 9 uncovered
  types; the reflected surface drops to 59 types.
- Anyone using the unreleased alpha's `embeddings()` must switch to a
  provider's own client for vectors. Stated, not buried.

## Evidence at landing time

- lm15-python: full suite 677 passed; endpoint conformance 12/12.
- Contract: provenance, audit, spec_drift, secrecy all OK; harness all
  seven directions green; selftest baseline green, 10/10 mutations caught.
