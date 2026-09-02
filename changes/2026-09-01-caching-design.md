# 2026-09-01 — Caching: one model for every provider (MAP-6, proposed)

Ratification: PENDING — awaiting Maxime Rivest. This entry is the output
of the first design pass (`playbooks/design-pass.md`); the full record is
under `research/caching/`. Nothing in the reference implementation
changes until ratification. Do not push before ratification.

## What the pass established (receipts in research/caching/)

- Three tiers exist across 13 providers studied: **automatic**
  (best-effort, nothing to send), **breakpoint** (a mark on a block,
  guaranteed above a per-model minimum, 1.25× write), **resource** (a
  stored, named, billed-per-hour object; Gemini only among lm15's
  providers). `research/caching/10-facts.md`, `30-model.md`.
- The breakpoint tier has two shapes with opposite economics. A
  **fixed** breakpoint hits on fan-out. A **trailing** breakpoint
  (Anthropic top-level `cache_control`, OpenAI ≥5.6 implicit mode) hits
  only when the next request extends the previous one; with a changing
  last message it wrote the full prefix at 1.25× on every call and never
  read — measured 0 hits in 5 on both providers (`20-results.json`,
  cells `anthropic/automatic-toplevel/warm*`,
  `openai-responses/implicit/warm*`).
- Gemini implicit caching is real and best-effort: 1 hit in 10 and 1 in 9
  across two runs. Gemini explicit caches pin the model and must own
  system and tools (HTTP 400 otherwise); create, use, list, delete all
  work; TTL and token count are returned.
- Prefixes include tools and the model everywhere. Hits cross process
  boundaries everywhere. No client state is needed for T0/T1.
- lm15's current Gemini mapping answers `mode="auto"` with a hidden
  `cachedContents` POST per multi-turn request, keyed by the whole
  prefix: one billed resource per turn, none reused, failures swallowed
  below the minimum. It is I/O inside a pure hook and the reason
  `SCOPE.md` had to exclude the feature. `THEORY.md` F1.

## The rule — MAP-6, caching

1. **Absent `config.cache` sends nothing.** Automatic tiers apply
   server-side; adapters report `cache_read_tokens` /
   `cache_write_tokens` when the wire reports them, `null` otherwise.
2. **`mode="off"` sends nothing and, where a switch exists, disables
   writes**: OpenAI ≥5.6 `prompt_cache_options: {"mode": "explicit"}`
   with no breakpoints. (Open: <5.6 models reject the option — raise, or
   send nothing.)
3. **`mode="auto"` without an index is the cheapest safe instruction**:
   Anthropic marks the system block; every other provider sends nothing.
   Never the trailing marker (measured cost trap).
4. **`prefix_until_index=N` is a fixed breakpoint** after message N:
   Anthropic `cache_control` on the last block of message N; OpenAI
   (both dialects, ≥5.6) `prompt_cache_breakpoint` on the last text
   block, raising when that message is assistant/tool or does not end in
   text; every provider without an in-request marker RAISES. Never a
   hint.
5. **`retention="long"`**: Anthropic `ttl: "1h"`; OpenAI <5.6
   `prompt_cache_retention: "24h"`; OpenAI ≥5.6 and Gemini RAISE.
6. **`key`** is a best-effort affinity hint: OpenAI and OpenRouter
   `prompt_cache_key`; Anthropic, Gemini, and others RAISE.
7. **`resource`** (new field) names a stored cache: Gemini
   `cachedContent`; the adapter raises if the request also carries
   system or tools (the server's rule); every other provider RAISES.
8. **A cache resource is a provisional surface**, shaped like files:
   `cache_create / cache_get / cache_list / cache_delete /
   cache_update_ttl`, pure hooks, async mirrors, a harness direction,
   `CacheInfo` with `tokens` and `expires_at`. Providers without it raise
   on every verb.
9. **No hidden network calls.** `resolve_prompt_cache` and
   `_cached_content_ids` are removed from the Gemini adapters.
10. **Documentation must state the fan-out trap** on OpenAI ≥5.6 default
    and the tools-change miss, citing the receipts.

## Behaviour changes (stated, not absorbed)

- Gemini requests with `config.cache` absent or `auto` stop making a
  second request and stop creating billed resources. Users who relied on
  the accidental resource creation lose nothing they could see; they
  gain a `resource` field and a surface to do it on purpose.
- `prefix_until_index`, `retention="long"`, `key` now raise on providers
  that cannot express them. Previously silently ignored on most.
- `CacheConfig` gains `resource`; the serde adds one omit-empty string
  field (additive).

## Spec and code effects (after ratification)

- `spec/types.md`: CacheConfig table (+`resource`), the mapping
  paragraph replaced by the table in `30-model.md`; new `CacheInfo`,
  `CacheCreateRequest`, `CachePage` tables; `SCOPE.md` moves
  `gemini.cached_content` from out-of-scope to provisional.
- `docs/mapping-rules.md`: MAP-6 as above.
- Cases: `anthropic.cache_auto_system` (exists as `system_content_blocks`),
  `anthropic.cache_prefix_index` (exists as `cache_control`),
  `openai.prompt_cache_breakpoint` (exists), `openai.cache_off`,
  `gemini.cache_resource` (create/use/list/delete bodies captured
  today under `research/caching/receipts/gemini__explicit-resource__*`),
  `gemini.cache_resource_with_tools_raises` (client-side, test-pinned).
- Reference: Gemini adapter loses ~80 lines; gains the cache hooks;
  CacheConfig gains a field; raises added per the table; tests per cell.
- Ports: the mapping table is data; the surface is the files pattern.

## Open questions for the maintainer (from 40-attack.md)

1. `mode="off"` on OpenAI <5.6: raise, or send nothing.
2. `auto` on Anthropic: system-block marker (proposed) or trailing marker.
3. Does the cache-resource surface ship with the other provisional
   surfaces.

## Spend and expiry

Spend this pass: ~110 requests, ~330k input tokens across OpenAI,
Anthropic, Gemini, xAI, Groq, plus one Gemini cache resource for 5 min
(deleted). Estimated under 2 USD. Receipts expire 2026-12-01: rerun
`research/caching/20-experiments.py` and diff `20-results.json`.
