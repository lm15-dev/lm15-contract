# 2026-10-31 — A usage counter means one thing on every provider; the estimate is exact or unknown

Ratification: RATIFIED 2026-11-01 — Maxime Rivest, in session ("i approve
the usage counting decision"), after the change was implemented and passed
in all six SDKs. Transcribed.

Request: Maxime Rivest, 2026-10-31, in session. After a cost check for an
app found `InferencePricing.estimate` charging OpenAI's cached tokens twice:
"one thing in LM fifteen that's very important is to not have the illusion
of standardization, but be truly standardized"; "look at what we've been
taking right decision and what's been the deepest goal and the guiding star
of this project … if we need a 2.0 version, we'll do a 2.0 version"; then,
on the recommendation below, "I agree, go do it all and do it most
excellently". It reverses `2026-09-02-usage-semantics.md`, which was accepted in
a batch ("i accept all your recommendations").

## The problem

`Usage` gave every provider the same field names but not the same meanings
(`spec/types.md` table of 2026-09-02):

| | `input_tokens` includes cached? | `output_tokens` includes reasoning? |
|---|---|---|
| OpenAI, Gemini, xAI | yes | OpenAI yes; Gemini, xAI **no** |
| Anthropic | **no** | yes |

A program that switches provider kept running while its numbers quietly
changed meaning. That breaks the first promise (THEORY §3.9: change the
model string and the program keeps working *with the same meaning*), and
it is the failure THEORY §3.8 names: "pretending providers are identical is
how compatibility layers lie". It touches money, which §3.9 ranks highest.

The estimate showed the cost. It priced `input_tokens × input rate` plus
`cache_read_tokens × read rate`, which is right only where cached tokens
sit beside the input (Anthropic). On OpenAI, Gemini and xAI the cached
tokens were charged twice; on Gemini and xAI the reasoning was not charged
at all. Measured on a gpt-6.1-sol call with 100,000 input tokens, 90,000 of
them cached, 1,000 out: true cost $0.039, estimate $0.219 (5.6×). On the
recorded `gemini.thinking_level` reply the estimate missed 155 of 203 output
tokens. It also skipped unknown counters, so its docstring's "lower bound"
was false in both directions, and it had no notion of the long-prompt
prices both OpenAI (above 272,000 input tokens) and Anthropic Haiku 5.5
(above 100,000) charge.

## Why the 2026-09-02 rule falls

It gave two reasons. **Bill reconciliation**: the provider's own usage
object is already kept verbatim in `Response.provider_data` (MAP-3 for
streams), so canonical counters with one meaning cost reconciliation
nothing. **Dozens of goldens change**: work, not a principle; the migration
below is scripted and checked. What it gave up, cross-provider meaning, is
the thing lm15 exists for. This is the same move as 2026-09-14's (§3.9):
a rule that protected a secondary promise by breaking the first is replaced.

## Decision

1. **One meaning per counter** (`spec/types.md` § Usage, INV-029): input is
   everything the model read (cache reads, cache writes, provider tool
   tokens included); output everything it generated (reasoning and audio
   included); the other counters are parts of one of the two; total is
   their sum. Construction refuses parts larger than their wholes and a
   total that is not the sum.
2. **MAP-19** maps each wire onto those meanings: exact sums of the
   provider's counts or absent, never partial; when the provider's numbers
   contradict the wire's declared rule (a part above its whole, a total that
   is not the sum), the affected whole is withheld rather than wrong, and
   the provider's total stays. The provider's own numbers stay in
   `provider_data`.
3. **One new compat field**, `OpenAIChatCompat.reasoning_usage`
   (`in_completion` | `separate`, default `in_completion`, overridable per
   model): xAI is `separate`. Every other difference is a property of the
   dialect, so no other policy field is needed.
4. **`InferencePricing` gains `tiers`** (`PricingTier`: a threshold
   `above_input_tokens` and four optional rates; INV-057 orders them), and
   **`estimate(usage)` is exact or unknown** (`spec/types.md` § InferencePricing
   gives the six steps and the arithmetic order). An absent rate is
   unknown, never zero; an unreported cache counter is harmless only when
   its rate equals the input rate. It takes a `Usage` in every SDK.
5. **Model metadata becomes normative.** ModelInfo, ModelOrigin,
   InferenceModelInfo, InferencePricing and PricingTier move into
   `spec/types.md` (they lived only in `lm15-python/docs/model-hydration.md`);
   the reference's `surface_dump` reflects them, so `spec_drift` and the
   surface audit (serde kind `model_info`) now cover them.
6. **Major version 2 in every language** (amended 2026-11-01, at the
   maintainer's question "should they not all be 2.0 so lm15 users that are
   cross language won't be confused?"; the rule is now
   `playbooks/api-family.md` rule 8: the major version is the contract's
   generation). Python 2.0.0, TypeScript 2.0.0, R 2.0.0, Julia 2.0.0
   (`LanguageModel15`, registered directly at 2.0.0); Rust 2.0.0-rc.1 and
   Go v2.0.0-rc.1, which stay release candidates until each is declared
   stable. Go's module path becomes `github.com/lm15-dev/lm15-go/v2`, as
   Go requires for a major version above 1. The field names stay: they now
   carry the meaning they always seemed to, so an Anthropic, Gemini or xAI
   number changes.

## Evidence

All in the corpus; MAP-19's table cites each row. In short: Anthropic-wire
servers count cache beside the input (cache counters larger than
`input_tokens` in 18 recorded objects; Moonshot's own `prompt_tokens` and
`total_tokens` confirm it in all 15 of its objects); Chat Completions and
Responses servers count it inside (the same prompt reports the same prompt
count cached and uncached on OpenAI, Fireworks, Parasail, Meta, Moonshot,
DeepSeek and Bedrock; DeepSeek's hit + miss equals its prompt; xAI's text
tokens equal its prompt; Z.AI and Together by documentation only); reasoning
is inside the completion on every chat server with a recorded reasoning
count except xAI, whose 8 objects all sum prompt + completion + reasoning;
Gemini's total is prompt + tool use + answer + thoughts in all 151 recorded
objects that carry one, and its proto3 wire omits zeros
(`gemini.max_output_tokens`, `gemini.reasoning_off`). Prices for the vectors:
`developers.openai.com/api/docs/pricing` ("Short context: ≤272K input
tokens. Long context: >272K input tokens.") and
`platform.claude.com/docs/en/about-claude/pricing` (Haiku 5.5 over 100,000
tokens, "counts all of its input tokens, including cache reads and cache
writes"), read 2026-10-31.

## What changed in the corpus

- `spec/types.md`: § Usage rewritten; new § Model metadata (ModelInfo,
  ModelOrigin, InferenceModelInfo, InferencePricing with the estimate rule,
  PricingTier). `spec/invariants.md`: INV-029 amended, INV-057 added.
- `docs/mapping-rules.md`: MAP-19; MAP-3's usage paragraph points to it.
- **Goldens**: 113 Usage objects in 101 goldens, migrated by
  `tools/migrate_goldens_2026_10_31.py`. For each canonical Usage the tool
  finds the provider usage object in the case's recorded bodies that the
  1.x rule maps to exactly that Usage (zero findings: every old golden was
  verbatim to its body), computes MAP-19 from it with its own code (it
  imports no implementation), checks INV-029, and appends one sentence to
  the golden's provenance naming exactly what changed. The reference,
  changed independently, then passes every golden: two separate readings of
  the rule agree. What moved: Anthropic-wire input now includes the cache
  (Anthropic 3, DeepSeek 6, Meta 9, Moonshot 15 goldens); Gemini and Vertex
  output now includes thoughts and input includes tool-use tokens (e.g.
  `gemini.code_execution` input 23 → 238); Gemini's zero cache and
  reasoning counters are now `0`, not absent; xAI output now includes
  reasoning (8 goldens). No OpenAI, Responses-wire or other chat golden
  changed.
- `mapping/usage.json` (generated by `tools/make_usage_vectors.py`, which
  computes expected costs from the spec's rule with plain arithmetic): 20
  estimate vectors, 6 Usage and 5 pricing refusals, 3 Usage round trips,
  11 MAP-19 parse vectors on hand-authored edge bodies. Harness: the
  `mapping` direction runs them; new vet op `estimate_cost`
  (`harness/PROTOCOL.md`); the fake shim echoes them and the self-test
  gains four mutations (the 1.x double count, unknown answered 0.0, an
  INV-029 breach accepted, a withheld split answered with the wire's
  numbers), all caught.
- `serde/canonical.json`: two `model_info` vectors with tiers.
- `tables/providers.json`: `compat.chat.xai.reasoning_usage = "separate"`.
- `tools/audit.py`: every golden Usage satisfies INV-029 and none withholds
  its split (MAP-19 rule 3); `model_info` covers the model-metadata types.
- `changes/2026-09-02-usage-semantics.md`: marked superseded.

## Stated trade-offs

1. **Breaking, for every SDK user reading Anthropic input or Gemini/xAI
   output.** The numbers grow to their true meaning. Major version 2
   (decision 6) says so in every language; the names stay because they
   were always the right names. Go users also change their import path
   (`/v2`), and Rust and Go skip a stable 1.0.
2. **Old saved records.** A 1.x Usage that breaks INV-029 (most Anthropic
   records with cache writes, Gemini and xAI records with reasoning) is
   refused on load with a message naming this change; one that happens to
   satisfy it reads silently with the new meaning. lm15 has no version
   marker in canonical JSON to tell them apart.
3. **More `None` from `estimate`.** It now says unknown instead of a wrong
   number: when a provider does not report a cache split (Bedrock without
   caching, Groq, DeepInfra, TypeSafe) and the catalog prices cache reads
   differently from input; when a catalog states no cache-write rate and
   the provider reports no write count (Gemini, older OpenAI models); when
   audio was used. A catalog that knows writes cost the same as input must
   say so (`cache_write_per_million` equal to the input rate). Spending
   caps must decide what unknown means for them.
4. **What the estimate still cannot see** (stated in the spec, never
   guessed): service tiers (flex, priority, batch), regional multipliers,
   the higher write rate of a longer cache lifetime (Anthropic's
   `cache_creation.ephemeral_1h_input_tokens` stays in `provider_data`),
   server-side tool fees, and provider-reported costs (xAI
   `cost_in_usd_ticks`, DeepInfra `estimated_cost`).
5. **Documentation, not receipts, for three servers.** Z.AI, Together and
   Azure count cached tokens inside the prompt by their documentation; no
   same-prompt pair is recorded for them. Nine chat presets have no
   recorded reasoning count at all; the dialect's rule is their hypothesis
   (THEORY §3.17), and MAP-19 rule 3 withholds output the day one of them
   contradicts it in a reply that carries a total.
6. **The withhold alarm needs a total.** Anthropic-wire servers other than
   Moonshot send none, so a future Anthropic-wire server that counted cache
   inside `input_tokens` would be caught only when its cache exceeds its
   input. The recorded servers all count it beside.

## Ports

Python is the reference (`lm15-python`). TypeScript, Rust, Go, Julia and R
implement the same in this change set: the Usage checks, the five wire
rules, `reasoning_usage`, `PricingTier`, `estimate(usage)` and the
`estimate_cost` op. All six pass every direction of the harness at this
contract commit, including the 45 new `mapping/usage.json` vectors, whose
estimates agree to the bit. Each SDK's next release pins this commit.
