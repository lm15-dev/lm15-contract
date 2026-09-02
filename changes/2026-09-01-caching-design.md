# 2026-09-01 — Caching: one model for every provider (MAP-6, proposed)

Ratification: PENDING — awaiting Maxime Rivest. This entry is the output of the first design pass (`playbooks/design-pass.md`); the full record is under `research/caching/`. Nothing in the reference implementation changes until ratification. Do not push before ratification.

## What the pass established (receipts in research/caching/)

- Three tiers exist across 13 providers studied: **automatic** (best-effort, nothing to send), **breakpoint** (a mark on a block, guaranteed above a per-model minimum, 1.25× write), **resource** (a stored, named, billed-per-hour object; Gemini only among lm15's providers). `research/caching/10-facts.md`, `30-model.md`.
- The breakpoint tier has two shapes with opposite economics. A **fixed** breakpoint hits on fan-out. A **trailing** breakpoint (Anthropic top-level `cache_control`, OpenAI ≥5.6 implicit mode) hits only when the next request extends the previous one; with a changing last message it wrote the full prefix at 1.25× on every call and never read — measured 0 hits in 5 on both providers (`20-results.json`, cells `anthropic/automatic-toplevel/warm*`, `openai-responses/implicit/warm*`).
- Gemini implicit caching is real and best-effort: 1 hit in 10 and 1 in 9 across two runs. Gemini explicit caches pin the model and must own system and tools (HTTP 400 otherwise); create, use, list, delete all work; TTL and token count are returned.
- Prefixes include tools and the model everywhere. Hits cross process boundaries everywhere. No client state is needed for T0/T1.
- lm15's current Gemini mapping answers `mode="auto"` with a hidden `cachedContents` POST per multi-turn request, keyed by the whole prefix: one billed resource per turn, none reused, failures swallowed below the minimum. It is I/O inside a pure hook and the reason `SCOPE.md` had to exclude the feature. `THEORY.md` F1.

## The rule — MAP-6, caching

1. **Absent `config.cache` sends nothing.** Automatic tiers apply server-side; adapters report `cache_read_tokens` / `cache_write_tokens` when the wire reports them, `null` otherwise.
2. **`mode="off"` sends nothing and, where a switch exists, disables writes**: OpenAI ≥5.6 `prompt_cache_options: {"mode": "explicit"}` with no breakpoints. (Open: <5.6 models reject the option — raise, or send nothing.)
3. **`mode="auto"` without an index is the cheapest safe instruction**: Anthropic marks the system block; every other provider sends nothing. Never the trailing marker (measured cost trap).
4. **`prefix_until_index=N` is a fixed breakpoint** after message N: Anthropic `cache_control` on the last block of message N; OpenAI (both dialects, ≥5.6) `prompt_cache_breakpoint` on the last text block, raising when that message is assistant/tool or does not end in text; every provider without an in-request marker RAISES. Never a hint.
5. **`retention="long"`**: Anthropic `ttl: "1h"`; OpenAI <5.6 `prompt_cache_retention: "24h"`; OpenAI ≥5.6 and Gemini RAISE.
6. **`key`** is a best-effort affinity hint: OpenAI and OpenRouter `prompt_cache_key`; Anthropic, Gemini, and others RAISE.
7. **`resource`** (new field) names a stored cache: Gemini `cachedContent`; the adapter raises if the request also carries system or tools (the server's rule); every other provider RAISES.
8. **A cache resource is a provisional surface**, shaped like files: `cache_create / cache_get / cache_list / cache_delete / cache_update_ttl`, pure hooks, async mirrors, a harness direction, `CacheInfo` with `tokens` and `expires_at`. Providers without it raise on every verb.
9. **No hidden network calls.** `resolve_prompt_cache` and `_cached_content_ids` are removed from the Gemini adapters.
10. **Documentation must state the fan-out trap** on OpenAI ≥5.6 default
    and the tools-change miss, citing the receipts.

## Behaviour changes (stated, not absorbed)

- Gemini requests with `config.cache` absent or `auto` stop making a second request and stop creating billed resources. Users who relied on the accidental resource creation lose nothing they could see; they gain a `resource` field and a surface to do it on purpose.
- `prefix_until_index`, `retention="long"`, `key` now raise on providers that cannot express them. Previously silently ignored on most.
- `CacheConfig` gains `resource`; the serde adds one omit-empty string field (additive).

## Spec and code effects (after ratification)

- `spec/types.md`: CacheConfig table (+`resource`), the mapping paragraph replaced by the table in `30-model.md`; new `CacheInfo`, `CacheCreateRequest`, `CachePage` tables; `SCOPE.md` moves `gemini.cached_content` from out-of-scope to provisional.
- `docs/mapping-rules.md`: MAP-6 as above.
- Cases: `anthropic.cache_auto_system` (exists as `system_content_blocks`), `anthropic.cache_prefix_index` (exists as `cache_control`), `openai.prompt_cache_breakpoint` (exists), `openai.cache_off`, `gemini.cache_resource` (create/use/list/delete bodies captured today under `research/caching/receipts/gemini__explicit-resource__*`), `gemini.cache_resource_with_tools_raises` (client-side, test-pinned).
- Reference: Gemini adapter loses ~80 lines; gains the cache hooks; CacheConfig gains a field; raises added per the table; tests per cell.
- Ports: the mapping table is data; the surface is the files pattern.

## Open questions for the maintainer (from 40-attack.md)

1. `mode="off"` on OpenAI <5.6: raise, or send nothing.
2. `auto` on Anthropic: system-block marker (proposed) or trailing marker.
3. Does the cache-resource surface ship with the other provisional surfaces.

## Spend and expiry

Spend this pass: ~110 requests, ~330k input tokens across OpenAI, Anthropic, Gemini, xAI, Groq, plus one Gemini cache resource for 5 min (deleted). Estimated under 2 USD. Receipts expire 2026-12-01: rerun `research/caching/20-experiments.py` and diff `20-results.json`.

## Amendments after the cookbook test (2026-09-01, same day)

The maintainer tested the proposal against a beginner's cookbook and a provider switch. Two of the proposed rules failed that test; the amendments below replace them. `research/caching/50-cookbook-draft.md` is the test.

**A1 — Prefix intents fall back to the automatic tier where no marker exists.** Rule 4 above ("every provider without an in-request marker RAISES") is withdrawn for prefix intents. `prefix="stable"`, `prefix="history"`, and `prefix_until_index=N` send nothing on Gemini, xAI, Groq, older OpenAI, and compat servers without `cache_control`, and the automatic tier applies. Justification, and the two conditions that bound the exception: the dropped control **costs nothing** (no write charge, no resource created) and the outcome **is observable** (`usage.cache_read_tokens`). `retention="long"`, `key`, and `resource` name specific mechanisms whose loss changes cost or meaning; they still raise. Provider agnosticism is defined as: the same code runs everywhere, does the best thing the provider offers, and shows the result.

**A2 — Named prefix intents.** `CacheConfig.prefix: "stable" | "history"
| None`, mutually exclusive with `prefix_until_index`. `"stable"` marks
the end of system + tools (Anthropic: the system block; OpenAI ≥5.6: the last text block of the first developer message, since top-level `instructions` cannot carry a breakpoint — mapping needs a receipt). `"history"` marks the last block of the last message (Anthropic's trailing marker; OpenAI ≥5.6: nothing, implicit mode already does it). `mode="auto"` with no prefix means `"stable"`. This resolves open question 2 (Anthropic default) without index arithmetic.

**A3 — `CachedPrefix`, the ergonomic over the resource surface.** `lm.cache(prefix: Request) -> CachedPrefix` (also on the routers): pure on marker and automatic providers; on Gemini it calls `cache_create` and returns the object's `id`, `tokens`, `expires_at`. `CachedPrefix` is a frozen, serializable value carrying the prefix Request's model, system, tools, messages, a content hash, and the optional resource fields. `cached.request(messages, config=None) -> Request` appends messages and sets `CacheConfig(prefix_until_index=<end of prefix>, resource=<id>)`; `cached + messages` is Python sugar for it. Adding a suffix that redefines `system` or `tools` raises. `cached.delete()` frees the resource where one exists. With `resource` set, the Gemini adapter omits `systemInstruction`, `tools`, and `toolConfig` from the wire (they are in the object by construction) instead of raising; rule 7 is amended accordingly. The contract pins the built `Request` and wire bytes; the sugar is per-language.

Open questions 2 is resolved by A2. Open questions 1 and 3 stand.

**Open question 1 resolved (2026-09-01, Maxime Rivest in session: "i agree, option 2").** `mode="off"` on OpenAI ≥5.6 sends `prompt_cache_options: {"mode": "explicit"}` with no breakpoints (the provider's real off switch; stops the 1.25× implicit writes). On every other provider, including OpenAI <5.6 where the option is rejected and writes are free, `mode="off"` sends nothing. Same two conditions as A1: no money is spent by the fallback, and the outcome is visible in usage. Rule 2 above is amended to say so.

**Open question 3 resolved (2026-09-01, Maxime Rivest in session: "its a yes but make sure it is NOT google / gemini specific").** The cache resource is a canonical tier, not a Gemini feature. Rules 7 and 8 are restated provider-neutrally: `CacheConfig.resource` holds a `CacheInfo.id` (opaque, provider-owned format); `cache_create` takes a `Request` prefix (model, system, tools, messages; a non-default config raises), `ttl_seconds`, `label`; `CacheInfo` carries `id, model, tokens, created_at, expires_at, label, provider_data`; `cache_get`, `cache_list` (cursor page), `cache_delete`, `cache_update(id, ttl_seconds)`; `EndpointSupport.caches` declares support. What the wire does with `resource` is per adapter (Gemini omits system/tools because its object owns them; a future provider may not). Model pinning is a property of the tier. Gemini is the first implementer; Vertex the second; all other adapters raise on every verb, as files do on subscription adapters.

## Implementation landed (2026-09-02, awaiting ratification of this entry)

Reference: lm15-python — `CacheConfig.prefix/resource`, `CacheInfo`, `CachePage`, `CachedPrefix`; the mapping table on all adapters (OpenAI both dialects incl. the gpt-5.6+ off switch and the stable-prefix developer-message rendering, Anthropic history/stable marks, Gemini resource wire + raises, compat gating); the cache surface (hooks, drivers, async mirrors, `lm.cache`, `router.cache`, `EndpointSupport.caches`); removal of the Gemini hidden `cachedContents` POST; MAP-6 in docs/mapping-rules.md; cookbook 19 with live outputs; 922 tests.

Contract: 8 new live cases (openai/openai_chat `cache_off` and `cache_stable`, anthropic `cache_history`, gemini `cache_history_fallback`, `cache_resource`, and the `gemini.cache` lifecycle surface case), 7 drafted goldens, the `cache` harness direction (`cache_op_build`/`cache_op_parse`, PROTOCOL.md), two selftest mutations (23 total), `caches` column in spec/support-matrix.json, SCOPE.md moves the resource tier to provisional, orphan `gemini.cached_content` burned down. The scribe gained a guard: it never rewrites an existing golden without `--overwrite`, and never a reviewed one.

Receipts of note: `openai.cache_off` — 3k-token prefix on gpt-5.6-sol, `cache_write_tokens == 0` (implicit mode wrote 3088 per call); `anthropic.cache_history` — turn 1 writes 3271, turn 2 reads 3275 and writes 24; `gemini.cache_resource` — `cachedContentTokenCount == 3580` against the object created in `gemini.cache`.

Trade-offs taken in code, stated: (1) the gpt-5.6 class is detected by a `gpt-<major>.<minor>` parse — names outside that pattern keep implicit writes on `mode="off"` until a release, `extensions` overrides; (2) with `resource` set and no `prefix_until_index`, all messages are sent (the object is assumed to hold system/tools only); (3) `prefix="stable"` on OpenAI moves the system prompt from `instructions` into the first input item — a wire change visible in the pinned case.
