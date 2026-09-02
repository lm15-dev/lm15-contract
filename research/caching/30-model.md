# Caching — the abstract model and the mapping (proposal, 2026-09-01)

## Three tiers, observed on every provider studied

| Tier | Name | Who has it | Instruction | Guarantee | Write cost | Outlives the request |
|---|---|---|---|---|---|---|
| T0 | automatic | OpenAI (all), Gemini implicit, xAI, Groq, DeepSeek, Fireworks, vLLM, SGLang, Bedrock implicit, Vertex implicit | none | best-effort | none (OpenAI ≥5.6: 1.25× on its implicit trailing write) | no user-visible state |
| T1 | breakpoint | Anthropic (block / top-level), OpenAI ≥5.6 (block / implicit mode), Bedrock `cachePoint`, Azure, OpenRouter passthrough | a mark on a block | yes, above the minimum | 1.25× (2× for 1 h on Anthropic) | no user-visible state |
| T2 | resource | Gemini `cachedContents`, Vertex explicit | a name in the request | yes | input price once + storage per token-hour | yes: name, TTL, list, delete |

Two sub-shapes of T1 matter for cost:

- **fixed breakpoint** — the user marks the end of the stable part.
  Fan-out (same prefix, different question) hits every time. Measured:
  Anthropic explicit, OpenAI explicit.
- **trailing breakpoint** — the provider marks the end of the latest
  message. Append-only conversations hit; fan-out never hits and pays the
  write price on every call. Measured: Anthropic top-level automatic,
  OpenAI ≥5.6 implicit — 0 hits in 5 with a changing last message,
  full write each time.

Facts that constrain any design:

1. On every provider the prefix includes tools and the model. Changing
   either is a miss. Ports need no client state to get hits across
   processes (measured: hit from a second process on all T1/T0 providers
   that hit at all).
2. Minimum sizes are per model (1,024 / 2,048 / 4,096). Below them the
   request succeeds and caches nothing; no error anywhere.
3. T2 pins the model and owns system and tools; a request may not carry
   them beside the resource (Gemini 400).
4. Only T1 and T2 report writes; T0 reports reads only, and Groq reports
   nothing on a miss.

## What `CacheConfig` means under this model

`CacheConfig` keeps its four fields. Their meanings become exact.

| Field | Meaning | Anthropic | OpenAI ≥5.6 | OpenAI <5.6 | Gemini | xAI / Groq / compat `cache_control="none"` |
|---|---|---|---|---|---|---|
| `config.cache` absent | send nothing; T0 applies where it exists | nothing | nothing (implicit trailing write, provider default) | nothing | nothing (implicit) | nothing |
| `mode="off"` | send nothing, and disable writes where a switch exists | nothing | `prompt_cache_options: {mode: explicit}`, no breakpoints → no writes (doc line 74) | nothing (no switch; 400 if the option is sent) | nothing | nothing |
| `mode="auto"`, no index | the cheapest safe instruction | breakpoint on the system block (today's behaviour) | nothing (implicit trailing) | nothing | nothing | nothing |
| `prefix_until_index=N` | fixed breakpoint after message N | `cache_control` on the last block of message N (any block type) | `prompt_cache_breakpoint` on the last TEXT block; RAISE otherwise; <5.6 → server 400 | RAISE (no marker on the wire) | RAISE (no in-request marker; see `resource`) | RAISE |
| `retention="long"` | longer lifetime at extra cost | `ttl: "1h"` (2× write) | RAISE (30 m is the only value) | `prompt_cache_retention: "24h"` | RAISE (T2 only) | RAISE |
| `retention="short"` | provider default | nothing | nothing | nothing | nothing | nothing |
| `key` | best-effort affinity hint | RAISE (no key concept) | `prompt_cache_key` | `prompt_cache_key` | RAISE | OpenRouter `prompt_cache_key`; others RAISE |
| `resource` (new) | name of a stored cache to reference (T2) | RAISE | RAISE | RAISE | `cachedContent: name`; RAISE if the request also carries system or tools (the server would) | RAISE |

Observability, unchanged in shape: `Usage.cache_read_tokens`,
`Usage.cache_write_tokens`, `null` when not reported. T2 adds
`CacheInfo.tokens` and `expires_at` so storage cost is computable above
lm15.

## The T2 surface (provisional, Gemini today)

Same shape as files: pure build/parse hooks, shared drivers, async
mirrors, a harness direction.

- `cache_create(CacheCreateRequest(model, system?, tools?, messages, ttl_seconds?, label?)) -> CacheInfo`
- `cache_get(id) -> CacheInfo`, `cache_list(limit, cursor) -> CachePage`,
  `cache_delete(id)`, `cache_update_ttl(id, ttl_seconds) -> CacheInfo`
- `CacheInfo(id, model, tokens, created_at, expires_at, label, provider_data)`
- Providers without T2 raise `UnsupportedFeatureError` on every verb.
- `CacheConfig.resource = CacheInfo.id` links a request to it. The
  request then carries no system and no tools; the adapter raises before
  the server would, with the server's own reason.

## Why this and not the alternatives

- *Keep the hidden per-request `cachedContents` POST.* Rejected by the
  cost accountant: measured, it makes a billed resource per turn and
  reuses none; and by the port implementer: it is I/O inside a pure hook.
- *Map `prefix_until_index` onto a T2 resource automatically.* Rejected:
  the resource pins the model and swallows system and tools; a
  per-request marker cannot express a lifetime; the user cannot see or
  delete what was made.
- *Treat `prefix_until_index` as a hint where no marker exists.* Rejected
  by the API designer: one field must not be a control on two providers
  and a hint on three. Raise, and let provider-agnostic code use `auto`.
- *`mode="off"` sends nothing on OpenAI ≥5.6.* Rejected by the cost
  accountant: the implicit trailing write charges 1.25× on every fan-out
  call; the only real off switch is explicit mode with no marks. The
  price is a loud 400 on <5.6 models. Left as the one open sub-question.
- *`auto` on Anthropic places the trailing top-level marker.* Rejected by
  measurement: 0 hits, full write per call under fan-out.
- *Rename `key` to `affinity`.* Tempting; not proposed. `key` stays a
  hint, `resource` is the hard reference. Two fields, two meanings.
