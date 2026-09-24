# 2026-09-24 — A provider's "no such model" is `unsupported_model` (MAP-15)

Status: written at the maintainer's request ("can we correctly fix the model
not found?"); ratified 2026-09-24 (changes/2026-09-24-ratification.md).

## What was wrong

The same mistake, a model name the provider does not have, raised different
classes. OpenAI, Gemini, Groq, Meta, Moonshot and xAI (today) answered
`UnsupportedModelError`; Anthropic, Claude Code, DeepSeek (both wires),
Z.AI and OpenRouter answered `InvalidRequestError`. The documentation had to
say "the provider refuses" without naming one class a program could catch.

Two causes:

1. **A synthetic Anthropic case.** `errors/cases/anthropic.json` pinned
   `anthropic.model_not_found` with the body `"model claude-missing not
   found"`, which has no provenance and is not what Anthropic sends. The live
   answer is `{"type":"not_found_error","message":"model: claude-haiku-9"}`
   (the field path, then the value). The marker test ("model" plus "not
   found"/"does not exist"/…) passed the synthetic body and failed the real
   one, in every SDK, while the corpus stayed green.
2. **Five DRAFT expectations.** DeepSeek, DeepSeek's Anthropic wire, Z.AI,
   xAI (2026-09-01) and Bedrock Chat answer an unknown model with HTTP 400 and
   a generic code; their cases recorded "the reference's current mapping,
   DRAFT until reviewed". This is the review.

## The rule

MAP-15 in `docs/mapping-rules.md`: the provider says the requested model does
not exist or is not available to the caller → `unsupported_model`, whatever
the status. Recognized by a model-specific code, by a not-found class about a
model (the existing marker test, unchanged and still limited to not-found
replies), or by a **pinned form** in the new `spec/model-not-found.json`:
exact `provider_code` plus fixed message text, each from a live receipt.

Rejected alternative: extending the marker test to every 400. "This model does
not support image input" names a model and a refusal; it would have become a
missing model. Pinned forms cannot widen.

Stated trade-off: a provider that rewords its answer falls back to
`InvalidRequestError`, the parent class, until a new receipt adds the form.

## Evidence

`receipts/2026-09-24-model-not-found/`: one request for a model that does not
exist, to every provider reachable from the lab (18 routes), sent unchanged
from the Python adapters' own request builders. Account identifiers (the
OpenRouter user id, the xAI team id) are redacted; nothing else is changed.
Each file records what lm15-python answered before this change.

Observed on the way: xAI now answers 404 `not-found` (it was 400
`invalid-argument` on 2026-09-01); Z.AI now answers code `1211`, "Unknown
Model" (it was `1214` with `modelCode: does not exist` on 2026-09-03). Both
old and new forms are kept: each was a real answer.

## Cases

- `anthropic.model_not_found`: the synthetic body replaced by the live one.
- `deepseek.model_not_found`, `deepseek-anthropic.model_not_found`,
  `zai.model_not_found`, `xai.model_not_found`,
  `bedrock-chat.model_not_found`: expected `UnsupportedModelError` (bodies
  unchanged; they were live).
- New: `zai.model_not_found_1211`, `xai.model_not_found_404`,
  `openrouter.model_not_found` (a new file; OpenRouter had no error cases).

## Implementations

The same table and check in every SDK, on the complete, stream and (R) live
error paths:

| SDK | Error direction at this commit | Notes |
|---|---|---|
| Python | 90/90 | full suite 3,339 passed; live: all 18 routes answer `UnsupportedModelError`; `CONTRACT_PIN` moved here |
| TypeScript | 90/90 | pin not moved (it predates managed auth); one unrelated FetchTransport test fails before and after |
| Rust | 90/90 | pin not moved; three unrelated tests fail before and after (preset address, cache resource, hosted doors) |
| Go | 90/90 | pin not moved; `go test ./...` passes |
| R | 87/90 | the 3 failures are `typesafe.*`: R has no TypeSafe provider (unrelated); pin not moved |
| Julia | 87/90 | same 3 `typesafe.*` cases; pin not moved |

R and Julia were run through their own vet programs (`exec/lm15-vet.R`,
`bin/vet.jl`) with temporary `harness/shims.json` entries (machine-specific
paths), which were not committed.
