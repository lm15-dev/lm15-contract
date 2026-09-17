# 2026-09-17 — Judgments: declared-level answers with probabilities, and TypeSafe (Jev) as a provider

Ratification: Maxime Rivest, 2026-09-17, in session ("yes, i like that
let's crystallize / note / register ratify all that we must to make add
to lm15 fully"), over the design explored the same day
(`lm15-dev/architecture-review/jev-judgments-2026-09-17/`). Status:
**provisional** surface (SCOPE.md), additive to the frozen chat core.

## The problem

TypeSafe's Jev answers typed questions about a state — pick one of these
keys, place this on ordered levels, is this true — and returns a
probability for every declared answer. Ordinary LLMs can be made to
answer the same questions (structured output gives the pick; a server
that scores named tokens gives the distribution), and applications
already consume exactly this shape: a factor with declared levels and
one probability per level (`predict_proba`, tidymodels `.pred_*`, MLJ
`UnivariateFinite`). lm15 had no way to ask for it, no part to carry it,
and no provider that produces it natively.

## Decisions

**D1 — Scope.** Jev enters as provider `typesafe` (dialect `typesafe`,
one Request in, one Response out). It passes the membership test of
`changes/2026-08-31-remove-embeddings.md`: its input is a text or data
part, its output is a data part — the same part any provider's
structured output produces. The surface is called **judgments**;
TypeSafe's own words (noul, System One) never enter the canonical
vocabulary.

**D2 — `DataPart`** (`type: "data"`, non-streamable). Fields: `value`
(any JSON value, opaque and verbatim per INV-002, always emitted — it is
the part's shape); `probabilities` (`{field: {key: float}}`, omit-empty;
keys are the declared answer keys as strings; each inner map is a
distribution over one judgment, summing to 1 within the provider's
rounding); `method` (`JudgmentMethod` or absent, omit-empty);
`continuation`. In a `user`/`system` message a DataPart is structured
input (Jev's state object; JSON text on wires that take only text) and
may carry `value` only (INV-052). In an `assistant` message it is the
answer to a `json_schema` request whose schema declares at least one
judgment (D4); otherwise structured output stays a `TextPart` as today —
frozen behaviour is untouched.

**D3 — `Config.probabilities`**: `null | "off" | "if_available" |
"required"` (`ProbabilityPolicy`; `null` = off). `off`: adapters spend
nothing extra (a provider that returns distributions anyway still
delivers them). `if_available`: a wire that cannot measure them records
`dropped` on `config.probabilities` and the part carries no
`probabilities`. `required`: such a wire refuses before sending
(`UnsupportedFeatureError`, `feature="config.probabilities"`, MAP-13
condition b: the program depends on the number). Never a one-hot, never
a self-reported number dressed as a measurement.

**D4 — The judgment schema convention** (MAP-14 §1). Inside
`response_format.schema` (INV-050 shape), a top-level property is a
judgment when it is one of: `type: boolean` (keys `true`/`false`); a
string `enum`, or `anyOf` of `{"const": <string>, "description"?,
"title"?}` (keys = the strings); an integer `enum` `0..n-1` or `anyOf` of
`{"const": <int>, "title"?, "description"?}` in order `0..n-1` (an
**ordered** judgment; keys `"0".."n-1"`, level names = titles). The
property's `description` is the question. Any other property is ordinary
structured output and never gets probabilities. This is plain JSON
Schema — nothing to strip, nothing provider-specific, and a beginner's
`{"enum": [...]}` already qualifies.

**D5 — Per-wire delivery** (MAP-14 §2), each cell receipted:

| wire | pick | probabilities | how |
|---|---|---|---|
| typesafe | native | native, `provider_classification` | judgment properties → Jev questions (boolean→noul, string→choice, ordered→score); state from messages (D6) |
| openai, openai-chat | native structured output, schema verbatim (`anyOf`/`const`/`title` honoured under `strict`) | absent | — |
| anthropic | native; a judgment property carrying `anyOf` has its `type` moved into each branch (the wire 400s otherwise) | absent | — |
| gemini | native; judgment properties are sent as `enum` with per-key descriptions folded into the property description (the wire ignores `const`: it answered `"Bordeaux-blend"`) | absent | — |
| openai-chat on a server that honours `logprob_token_ids` (vLLM ≥ 0.29 receipted; SGLang unreceipted, preset `none`) | from the distribution | exact, `candidate_sequence_likelihood`, plus `coverage` in `provider_data` | the token trie (D7) |

The Anthropic and Gemini rows are the MAP-13 rule-2 case (same meaning,
different spelling) and are not recorded. They touch INV-050's "adapters
never rewrite a keyword": INV-050 is amended with exactly this exception
— recognized judgment properties may be rewritten to the equivalent form
the wire honours, receipted per wire; every other keyword stays verbatim.

**D6 — State from messages (typesafe).** One user message holding one
text part and no system → `state` is that string. One user message
holding one data part → `state` is its `value`. Anything else →
`{"system": <text>?, "messages": [{"role", "content"}]}` so backticked
paths (`messages[0].content`) work as Jev's docs describe. Media,
tool calls and tool results have no wire slot → refuse (MAP-10).

**D7 — The token trie (vLLM/SGLang).** Every key path is tokenized in
its answer context through the server's `/tokenize` with the assistant
prefill (`continue_final_message`), so the model's chat template is
honoured and no retokenization is assumed. The answer terminator is
appended to every path (prefix-free; `P(key)` = the model writes exactly
this key and stops). Every trie node with children becomes one prompt
in ONE batched `/v1/completions` call with `logprob_token_ids` = the
union of child tokens, `max_tokens: 1`. Raw log-probs sum along each
path; one normalisation over the key set; `coverage` = the mass on the
key set before normalisation. Pure hooks (tokenize build/parse, scoring
build/parse) sequenced by a base driver, like files and batch. A server
that returns 200 without the requested ids has dropped the field
(receipted on vLLM 0.25.1): `required` → refuse; `if_available` →
`dropped` and no probabilities.

**D8 — Config on typesafe.** `max_tokens`, `temperature`, `top_p`,
`top_k`, `stop`, `seed`, penalties, `reasoning`, `logprobs`, `store`,
`user_id`, `service_tier`, `cache` → `dropped` (MAP-13). `tools`,
`tool_choice`, `n > 1`, a non-judgment schema property (Jev cannot
generate), more than 10 ordered levels or 255 keys, a missing
`response_format` → refuse. A judgment without a `description` gets the
property name as its instruction, recorded `defaulted`.

**D9 — Errors (typesafe).** `401 authentication_error` → `AuthError`;
`400 api_usage_error` "Unknown model" → `UnsupportedModelError`, other
400 → `InvalidRequestError`; `422` (pydantic `detail` list) →
`InvalidRequestError` with the first `loc` joined into the message;
`429` → `RateLimitError` (`retry-after` honoured); `529` and other 5xx →
`ServerError`. `provider_code` is `detail.error_type` when the body has
one; `x-typesafe-request-id` is the request id.

**D10 — Models.** `GET /v1/models` → one `ModelInfo(id=name,
provider="typesafe", api_family="typesafe_systemone")` per entry, the
wire entry verbatim in `origin.provider_data` (the shared
`model_infos_from_entries` rule).

**D11 — Streaming.** `stream=false` in the manifest; `stream()` raises
`UnsupportedFeatureError`. A one-shot answer wrapped in an iterator is
not a stream.

**D12 — Response accessors and helpers (per port, sugar).** `data`,
`probabilities`, `expected(field)` (= Σ p·i over an ordered judgment —
Jev's `score` is exactly this and is not stored) on the Response;
`choice`, `yes_no`, `score`, `judgments` helpers that EMIT the D4 schema,
as `tool(fn)` emits a tool schema. Jev's `confidence` is not derivable
and is kept verbatim in `provider_data.typesafe.answers`. Ports map to
their ecosystem's type as an optional extension (R ordered factor +
`.pred_*` columns, Julia `UnivariateFinite`, Python dict + `Categorical`).

**D13 — Harness.** `typesafe` cases run in the existing `request`,
`response`, `error` and `models` directions (no new op). The trie driver
gets its own direction later, with pinned tokenize and scoring bodies —
deferred like `image_gen` was, and declared so.

## Evidence

`receipts/2026-09-17-judgments/`: `jev-three-primitives.json` (score
7.01 with a 10-level legend, choice, noul in one call; `usage` 582/77),
`jev-pinned-version-string-state.json`, `jev-models.json`,
`jev-error-401.json`, `jev-error-422-missing-criteria.json`,
`jev-error-unknown-model.json`; the convention on the cloud wires
`openai-`, `openai-chat-`, `anthropic-` (`400` on `type`+`anyOf`, then
`-notype` and `-enum` 200) and `gemini-judgment-schema*.json` (`const`
ignored twice, `enum` honoured, thinking off); `vllm-0.29-lfm-trie.json`
(20 nodes, one call, 172 ms, ids honoured, distributions and coverage)
and `vllm-0.25.1-qwen-trie-negative.json` (200, ids silently absent).
Design measurements: `lm15-dev/architecture-review/jev-judgments-2026-09-17/`.

## Deferred, with reasons

- Sampling-based or self-reported probabilities (`sampled_frequency`,
  `self_reported`): different measurements; no receipt, no vocabulary
  value until one exists.
- Hosted `top_logprobs` scoring (≤ 20 alternatives, labels may be
  missing from the list): a partial distribution is not a distribution.
- Structured Jev instructions (objects) — JSON Schema `description` is
  a string; revisit if a second wire needs structured instructions.
- Jev's `confidence` as canonical: one provider's statistic; derivable
  alternatives (max-probability, entropy) are the user's.
