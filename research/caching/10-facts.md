# Caching — fact sheets (2026-09-01)

Every cell cites a scraped line (`sources/<name>.md:<line>`) or a receipt
(`20-results.json` cell, body under `receipts/`). Blank means: not found
in the source and not measured. Measured cells use a fresh random ~3k-token
prefix, a 45 s idle gap, a ~280-token "below minimum" prefix, one added
tool, a sibling model, and a second OS process.

Columns: **Mechanism** (automatic / marker / resource) · **Instruction**
(what the request must carry) · **Minimum** · **Lifetime** · **Prices**
(write, read, storage, relative to input) · **Reports** · **Prefix
includes** · **Measured**.

## Anthropic (Messages API)

- Mechanism: marker, two forms. (a) explicit `cache_control` on content
  blocks, up to 4 breakpoints, 20-block lookback
  (`anthropic-prompt-caching.md:16,514,531`). (b) NEW: automatic — one
  top-level `cache_control` and the breakpoint moves to the last
  cacheable block every request (`:15,276,472,480`); walks backwards
  silently if the last block is ineligible (`:521`); 400 if it collides
  with an explicit TTL or 4 explicit breakpoints exist (`:519,520`).
- Instruction: required; nothing is cached without a marker.
- Minimum: 1,024 tokens (Sonnet 4.5/4.6/5, Opus 4.8), 2,048 (Opus 4.7,
  Mythos), 4,096 (Opus 4.5/4.6, Haiku 4.5) (`:601-604`).
- Lifetime: 5 min default, refreshed on read at no cost; 1 h at 2× write
  (`:212,217,484,487`). Measured from request start (`:214`).
- Prices: write 1.25× (5 m) or 2× (1 h); read 0.1× (0.025× on Fable/Mythos
  5.1) (`:259-261,254`).
- Reports: `cache_creation_input_tokens`, `cache_read_input_tokens`;
  `input_tokens` is the UNCACHED remainder (receipt: input 19 with 3251
  cached).
- Prefix includes: tools, system, messages, in that order (`:225`).
- Measured, explicit block (`anthropic/explicit-block`): cold write 3251;
  warm ×3 read 3251 (deterministic); after 45 s read; below minimum
  (283) nothing; +1 tool → new write 3791 (tools are in the prefix);
  sibling model → miss; second process → hit.
- Measured, automatic top-level (`anthropic/automatic-toplevel`): cold
  write 3267; warm ×3 with a different last message → **write 3267 each,
  0 reads**; second process with an identical last message → hit. The
  trailing breakpoint includes the changing suffix, so fan-out never
  matches and pays 1.25× on every call.

## OpenAI (Responses and Chat Completions)

Three model classes (`openai-prompt-caching.md:189-197`):

| | GPT-5.6 and later | GPT-4.1 … GPT-5.5 (older) | Older reasoning/… |
|---|---|---|---|
| Implicit breakpoints | end of latest eligible user/tool message (`:83`) | every 2,048 tokens | model-dependent intervals |
| Explicit breakpoints | yes: `prompt_cache_breakpoint` on text blocks; `prompt_cache_options.mode` implicit/explicit (`:73-85,298`) | no | no |
| Minimum | 1,024 visible tokens | 2,048 | 2,048 |
| Write charge | 1.25× (`:67,194`) | none | none |
| Read charge | 0.1× | model-dependent | model-dependent |
| Lifetime | ≥30 min after write/reuse, `ttl: "30m"` only (`:117`) | ~30 min, up to 24 h with `prompt_cache_retention` (`:134`) | 5–10 min in-memory or 24 h |

- Instruction: none needed (implicit is on by default, `:13`); explicit
  marks are optional on 5.6+. `prompt_cache_key` groups requests for
  routing on all classes (`:177,321-326`); >15 rpm per prefix overflows
  (`:157`). Top-level `instructions` cannot carry a breakpoint (`:79`).
  In explicit mode with no breakpoints, nothing is written (`:74`) — the
  only true off switch on 5.6+.
- Prefix includes: model, tools, `parallel_tool_calls`, settings before
  the breakpoint (`:31,41-43`).
- Reports: `input_tokens_details.cached_tokens` and (5.6+)
  `cache_write_tokens`; chat: `prompt_tokens_details.*`. Older classes
  round `cached_tokens` down to a multiple of 128 (`:99`).
- Measured, 5.6 explicit breakpoint (`openai-responses/breakpoint`,
  `openai-chat/breakpoint`): cold write 3088; warm ×3 read 3070 + write
  18 (the implicit trailing breakpoint still writes the new suffix);
  45 s read; below minimum nothing; +1 tool → miss + full write; sibling
  model (5.6-luna) → miss; second process → hit.
- Measured, 5.6 implicit only (`openai-responses/implicit`): cold write
  3088; warm ×3 with a different last message → **write 3088 each, 0
  reads**; second process with an identical last message → hit. Same
  cost trap as Anthropic automatic.
- Measured, older class (`openai-responses/pre56`, gpt-5.4-mini): cold
  no write charge; warm ×3 read 2816 (= 3091 rounded to 128 below the
  question); tools/sibling → miss; second process → hit.

## Google Gemini (Gemini API)

- Mechanism: two tiers. Implicit: on by default for 2.5+, "no cost
  saving guarantee" (`gemini-explicit-caching.md:4,12-13,26-29`).
  Explicit: a `cachedContents` resource created once and referenced by
  name (`:5,36-38`), guaranteed.
- Instruction: implicit none; explicit `cachedContent: "cachedContents/…"`.
- Minimum: not stated on the scraped page (the API rejects small
  prefixes; the old adapter's swallowed 400s were this).
- Lifetime: explicit TTL default 1 h, settable (`:42-43`); implicit
  unspecified.
- Prices: implicit reads at the cached-input rate (2.5 Flash: $0.0375 vs
  $0.375/M, i.e. 0.1×); explicit adds storage at $0.50 per 1M tokens per
  hour, rising to $1.00 in 2027 (`gemini-pricing.md:55,66,84`).
- Reports: `usageMetadata.cachedContentTokenCount`, `cacheTokensDetails`.
- Constraints (measured, `gemini/explicit-resource`): a request that
  references a cache may not also carry `system_instruction`, `tools`, or
  `tool_config` — HTTP 400 "move those values to CachedContent"; the
  request model must equal the cache's model — HTTP 400. Create, use ×2
  (3574 cached tokens, deterministic), list, delete all HTTP 200; the
  create response carries `expireTime` and `usageMetadata.totalTokenCount`.
- Measured, implicit (`gemini/implicit`, 2.5-flash, nothing sent): 1 hit
  in 10 calls (3066 on warm2); earlier probe 1 in 9. Best-effort is the
  honest word.

## xAI (Chat Completions dialect)

- Mechanism: automatic, no knob. Source: pricing table lists a "Cached
  input" rate per model (`xai-prompt-caching.md:7-20`, e.g. grok-4.6
  $0.50 vs $2.00 = 0.25×; grok-4.3 $0.20 vs $1.25 = 0.16×). No caching
  guide page was found (manifest).
- Reports: `prompt_tokens_details.cached_tokens`, `cost_in_usd_ticks`.
- Measured (`xai/automatic`, grok-4.3): 128 cached on EVERY call
  including cold and below-minimum (a fixed system-level block);
  warm ×3 immediately → still 128; **after 45 s → 3200** (multiple of
  128); +tool → 192; second process (immediately) → 128. The cache
  becomes available seconds after the first request, not on the next
  call.

## Groq (Chat Completions dialect)

- Mechanism: automatic, "no code changes, no additional fees", not
  guaranteed (`groq-prompt-caching.md:4,10`); 50% discount on hits
  (`:7,17`); expires after 2 h unused (`:9`); gpt-oss models only
  (`:14`).
- Reports: `prompt_tokens_details.cached_tokens` when hit (`:269-272`).
- Measured (`groq/automatic`, gpt-oss-20b): no `cached_tokens` field on
  any of 10 calls, 3k prefix, including after 45 s. No hit observed.
- Side fact: gpt-oss-20b rejects `reasoning_effort: "none"` (accepts
  low|medium|high) — the loud MAP-5 failure, receipt
  `groq__automatic__cold/`.

## OpenRouter

- Mechanism: passes through the upstream provider's mechanism; adds
  sticky routing per conversation, 10 min, keyed by `session_id`, else
  `prompt_cache_key`, else a hash of the first system + user messages
  (`openrouter-prompt-caching.md:40-66`). Supports Anthropic-style
  `cache_control` and OpenAI 5.6 explicit breakpoints (`:36,152-158`).
- Reports: `cached_tokens`, `cache_write_tokens`, and a `cache_discount`
  dollar figure (`:110,132-133`).
- Measured: not — the environment's key returned 401 "User not found".

## Amazon Bedrock (not in lm15)

- Mechanism: implicit (best effort) and explicit `cachePoint` blocks
  (`bedrock-prompt-caching.md:19-39`); minimums per model (Opus 5: 1,024;
  Haiku 4.5: 4,096) (`:44-47`); a checkpoint below the minimum succeeds
  but caches nothing (`:50`); TTL ~5 min, reset on hit (`:52-55`).
- Shape: the Anthropic marker model with a different spelling.

## Google Vertex (not in lm15)

- Mechanism: implicit on by default (90% discount on hits) and explicit
  caches with storage cost; both report `cachedContentTokenCount`
  (`vertex-context-cache.md:463-481`).
- Shape: the Gemini two-tier model.

## Azure OpenAI (not in lm15)

- Mechanism: identical to OpenAI: no write charge before 5.6, writes on
  5.6+, `prompt_cache_key`, explicit breakpoints on both APIs, 4 write
  slots, 50-breakpoint lookback, `ttl: "30m"` only, 1,024 minimum
  (`azure-prompt-caching.md:29-55`).

## DeepSeek, Fireworks, vLLM, SGLang (compat servers)

- DeepSeek: automatic disk cache, best-effort, persisted at request
  boundaries and fixed intervals, cleared after hours to days
  (`deepseek-kv-cache.md:5-12,35-36`); reports `prompt_cache_hit_tokens`
  / `prompt_cache_miss_tokens` (page section "Checking Cache Hit").
- Fireworks: automatic longest-prefix reuse, tools are part of the
  prompt, hours of lifetime; reports via response header
  `fireworks-cached-prompt-tokens` (`fireworks-prompt-caching.md:34-39,
  263-281`).
- vLLM: automatic prefix caching, server flag; no per-request knob.
- SGLang: RadixAttention, automatic; source page was an HTML shell
  (manifest: weak).
- Shape: all automatic; nothing to send; observability varies.

## Mistral, Together

- No caching page fetched (manifest: MISSING). Not claimed.
