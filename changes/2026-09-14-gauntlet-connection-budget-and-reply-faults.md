# 2026-09-14 — What the DSPy gauntlet found: what is fixed, what needs a decision

Ratification: PARTIAL — A1's shared timeout defaults, connection cap, and
explicit-caller-setting precedence were ratified by Maxime Rivest on 2026-09-15
in session (“I'm seeing the two items that you're mentioning. Yeah, this is
fine.”). See spec/vocabularies.md § Connection budget. This assent does not
ratify the remaining proposals in this document.

Originally drafted in session from a reading of
`cmpnd-ai/breaka-your-lm` (Drew Breunig, 2026-09-13; DSPy 3.4.0b1 with
lm15 1.0.0a1 vendored) and of the reference code it exercised. Part A is
implemented in lm15-python and needs ratification to become a rule every
port follows. Part B is a list of decisions only Maxime can make. Part C
is what the gauntlet got wrong.

## A. Implemented in lm15-python — proposed as contract rules

### A1. The connection budget is a portable value with the provider SDKs' defaults

`Timeouts(connect=10, read=600, write=600, pool=600)` and
`max_connections=100`, both on `RouterConfig`, shaping the ONE transport a
router builds and shares across every LM it constructs.

Why these numbers: a model that thinks for minutes before its first byte
is ordinary; OpenAI, Anthropic and litellm all wait 600 s. lm15 waited
60 s and reported the rest as `TransportError` — retryable — so DSPy's
retry loop restarted the generation three more times on the server
(gauntlet #1). Ten connections made 16 evaluation threads fail on one
local server instead of queueing (gauntlet #2); 100 is the httpx and
aiohttp norm, and a provider's rate limit, not the pool, is the practical
ceiling. Every timeout is per operation (the next byte), never per
request, so a stream that keeps trickling never trips it.

A1 defaults and precedence are now recorded in `spec/vocabularies.md`
("Connection budget"). The original broader rule proposal follows; lifecycle
claims are not newly ratified by the defaults assent: every port exposes the four timeouts and the connection cap
under those names and defaults; a read timeout's message states it is the
client's limit and names the knob (a user who cannot tell a client
timeout from a dead server retries the wrong thing); a router or client
owns one pool and closes it on `close()`; a dropped one leaks no socket.

Trade-off stated: an unreachable-but-accepting server now takes 600 s to
fail instead of 60 s. That is what every provider SDK does, and connect
(10 s) still fails fast on a host that is down.

### A2. Compressed replies are decoded, never handed to the JSON parser

Requests keep advertising `Accept-Encoding: identity` (compressed SSE
buffers in proxies and defeats streaming). A reply that arrives
`gzip`/`x-gzip`/`deflate` anyway is inflated incrementally; `br`/`zstd`
raise a transport `ProtocolError` naming the coding. Gauntlet #3: a gzip
200 became `'utf-8' codec can't decode byte 0x8b`.

Proposed rule: a port decodes what its standard library can and names
what it cannot; it never lets encoded bytes reach a parser.

### A3. A non-JSON 200 is `ProviderError`, not an escaped parser exception

`HttpResponse.json()` raises `ProviderError` (code `provider`, status,
content-type, first 200 bytes, request id) — the contract's existing
"a reply that cannot become a Response without inventing a fact" (MAP-9,
2026-09-07). Before: a raw `JSONDecodeError` escaped every `except
LM15Error` (DSPy surfaced it as `LMUnexpectedError`).

**The gauntlet asked for `ServerError`.** Rejected: the contract binds
`ServerError` to 5xx; inventing a 5xx from a 200 is inventing a fact. See
B3 for the retryability question this leaves open.

### A4. A lone surrogate is refused before the wire as a `ValueError`

Text containing U+D800..U+DFFF unpaired has no UTF-8 form and can reach no
provider; `json_dumps` raises `ValueError` naming the code point. Before:
`UnicodeEncodeError` in the transport, surfaced as a network fault
(gauntlet #7). `ValueError` because it is a local input error like
`Request(model="")`, not a provider or configuration error.

## B. Decisions for Maxime (not implemented)

### B1. Provider-only sampling fields sent to a wire that lacks them

Today `seed`, `logit_bias`, `frequency_penalty`, `presence_penalty` are
sent to Anthropic and the server answers 400 `Extra inputs are not
permitted` (`InvalidRequestError`); litellm refuses before the call with
`UnsupportedFeatureError`. MAP-5 says a setting the dialect cannot carry
raises before the wire. Question: is a field the server REJECTS loudly a
MAP-5 refusal (raise before the wire, `unsupported_feature`) or a faithful
pass-through (the server said no, and said why)? My recommendation: raise
before the wire — the family's rule is already MAP-5, the server's answer
is not guaranteed to stay loud (Moonshot swallowed sampling params
silently, live 2026-09-03), and a pre-wire refusal costs nothing. This is
a behaviour change on Anthropic and every Anthropic-wire preset.

### B2. Anthropic `json_object`: refuse at selection time

lm15 refuses `response_format={"type":"json_object"}` on the Messages API
(it has no any-JSON mode; litellm fakes one). Right, and stays. But the
refusal happens at execution; DSPy's `engine="auto"` needs it at
selection so it can fall back. Question for the DSPy boundary
(`request_from_openai_chat`): should an ingest-time capability check
exist so a caller can ask "can this route carry this request?" without
sending? Contract-neutral; a Python/DSPy ergonomics decision.

### B3. Is a non-JSON 200 retryable?

A3 makes it `ProviderError`, which the contract lists as NOT retryable.
A truncated body might succeed on retry; a gateway's HTML error page will
not. litellm retries. My recommendation: not retryable — the caller
cannot know the request was not served (it may have been, and billed),
and lm15 never guesses on the caller's money. If you disagree, the
change is one line in the retryable set.

### B4. One error class for "unknown model" across providers

OpenAI's 404 maps to `UnsupportedModelError`; Anthropic answers 400 with
`model: <name>` and lm15 maps it to `InvalidRequestError`; a caller who
catches `UnsupportedModelError` to fall back gets a different answer per
provider. The fix is a body-pattern rule in `docs/mapping-rules.md` for
each provider whose unknown-model error is a 400 (Anthropic's is
`invalid_request_error` with the message starting `model:`). Needs a
receipt per provider. Recommendation: do it; it is the kind of
harmonisation the contract exists for.

### B5. `ContextLengthError` for OpenAI-compatible local servers

LM Studio answers 400 with `request (N tokens) exceeds the available
context size (M tokens)`; lm15 maps it to plain `InvalidRequestError`.
Callers catch `ContextLengthError` to shrink prompts. The OpenAI-chat
dialect already pattern-matches OpenAI's wording; adding LM Studio's
(and Ollama's, vLLM's) needs one receipt each. Recommendation: do it,
per-preset, receipts attached.

### B6. Per-request timeouts on the contract's `Request`

A1 is per router. DSPy's `timeout=` is per LM instance, which A1 covers.
A per-call override (one long request among short ones) has no home:
`Request`/`Config` carry no transport fields by design (they are wire
semantics). Options: (a) leave it — build a second router; (b) a
`Config.extensions["lm15.read_timeout"]` hatch; (c) a typed field.
Recommendation: (a) now; revisit if a real consumer asks.

### B7. gevent

Async lm15 under `gevent.monkey.patch_all()` hangs (the executor thread
parks in gevent's hub). Full support is a transport rewrite; the honest
minimum is to detect the patch and raise `ConfigurationError` pointing at
the sync path. Recommendation: the honest minimum, and not promised for
1.0.

## C. What the gauntlet got wrong (no change)

- **"Anthropic `CacheConfig(mode='auto')` wrote no cache on a 3,618-token
  prefix above the 2,048 minimum."** Haiku 4.5's minimum is 4,096 tokens
  (`research/caching/10-facts.md:148`, from Anthropic's own table; Haiku
  3.x is 2,048). lm15 does attach `cache_control` to the system block
  (`providers/anthropic.py`, `use_cache` → `payload["system"]`). The test's
  prefix was below the minimum. Not a bug; the test needs a bigger prefix.
- **"One async pool leaks per finished event loop; `close()` cannot
  reclaim them."** That store (`lm._engine_store`) is DSPy's, keyed per
  loop by DSPy. An asyncio connection belongs to its loop by construction;
  the fix is DSPy discarding a pool when its loop closes. lm15's part —
  `AsyncLMRouter.aclose()` and closing idle sockets on collection even
  when the loop is gone — is done (A1).
- **"The missing-key message gives lm15 advice."** True and correct for
  lm15; DSPy should catch `NotConfiguredError` at its boundary and re-say
  it in DSPy terms (`dspy.LM(api_key=...)`). DSPy-side.
- gpt-5.6 reasoning-model regex, `openai/` → Chat Completions for a model
  whose tools live on Responses, `streamify` exception groups, strict
  Pydantic schemas, PyInstaller, MIPROv2's proposer: DSPy-side.
