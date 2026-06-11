# 2026-06-11 — release ratification batch

Maintainer assent in session ("I ratified the spec and the golden drafts is all good"):

1. **spec/ ratified**: types.md, vocabularies.md, invariants.md footers changed
   DRAFT -> RATIFIED. Canonical-facts authority now includes spec/.
2. **AUTHORITY.md amended + re-ratified**: canonical-facts precedence item 1 now
   names the ratified spec/ files alongside serde-rules.md and mapping-rules.md.
3. **39 draft goldens frozen**: every golden without a `reviewed` provenance
   stamp (23 orphan-adoption + 16 openai_chat incl. vllm/sglang) received the
   2026-06-11 batch-freeze stamp. All 108 goldens are now reviewed oracle.
