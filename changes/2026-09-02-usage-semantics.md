# 2026-09-02 — Usage counters are provider-verbatim, and the spec says so

Ratification: accepted in advance — Maxime Rivest, in session ("i accept
all your recommendations"), for the recommendation in
`2026-09-02-review-followup.md` (review §4 item 3). Transcribed here;
stamp on reading.

## What changed

Spec text only. `spec/types.md` Usage gains a normative paragraph and a
per-provider inclusion table, each cell pinned by an existing golden:

| Provider | `input_tokens` ⊇ cached | `output_tokens` ⊇ reasoning | `total_tokens` |
|---|---|---|---|
| OpenAI (both dialects) | yes | yes | input + output |
| Anthropic | no (cache counters disjoint) | yes | not reported; lm15 sums input + output (excludes cache) |
| Gemini | yes | no | prompt + candidates + thoughts |
| xAI | yes | no | prompt + completion + reasoning |

No golden, vector, or byte changes.

## Why verbatim

A bill reconciles against the provider's own numbers. Normalising in the
adapters (say, always excluding cache from `input_tokens`) would produce
a number no invoice shows, touch dozens of goldens, and still leave
`total_tokens` provider-shaped. What is lost is cross-provider
comparability of a single field; the table gives a consumer the rule to
apply. Stated trade-off: `Usage` alone does not know its provider.
