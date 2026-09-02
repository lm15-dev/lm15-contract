# Caching — attack on the model (2026-09-01)

**Label:** self-review by the same agent that wrote `30-model.md`. No
second agent was available in this session. A self-review is weaker: it
shares the author's blind spots. Treat every "holds" below as "not yet
broken", not "proven".

## Scenarios, one lens each

**1. Ten-turn chat, `CacheConfig()` default, each provider.** (cold learner)
- Anthropic: system block marked; every turn reads the system, pays full
  price on history. Holds, but suboptimal — the trailing automatic form
  would read history too. Trade-off stated in §Open below.
- OpenAI ≥5.6: implicit trailing breakpoint; each turn reads the previous
  turn's prefix and writes the new suffix at 1.25×. Holds; this is the
  provider's default and the append-only case it was built for.
- Gemini, xAI, Groq: nothing sent; T0 does what it does. Holds.

**2. Fan-out: one 5k-token document, 200 different questions.** (cost accountant)
- With `CacheConfig()`: Anthropic reads the system only if the document
  is in the system (user choice); OpenAI ≥5.6 pays 1.25× × 200 with 0
  hits — the measured trap. The rule must say this in the docs, and the
  fix is one field: `prefix_until_index=0`. Holds only if documented
  loudly. Added to §8's spec text.
- With `prefix_until_index=0`: Anthropic and OpenAI ≥5.6 read every time.
  Gemini raises; the user creates a resource and passes `resource=`.
  Holds.

**3. Provider switch mid-conversation with `prefix_until_index=3`.** (switcher)
- Anthropic → OpenAI: message 3 must end with text on OpenAI; if it is
  an assistant turn, raise. The user learns at the switch, not silently.
  Holds. Cost: provider-agnostic code with a fixed index is not fully
  agnostic. Stated.

**4. Two processes, same prefix.** (library author)
- All T1/T0 hits are server-side; measured hits from a second process on
  Anthropic, OpenAI, and T2 Gemini. lm15 keeps no client state. Holds.
  T2: the resource name must be shared by the application; lm15 does
  not invent a registry. Holds.

**5. Port implementer, Go and Rust.** (porter)
- Every mapping is a pure rewrite of the request body from
  `CacheConfig`; the T2 verbs are pure build/parse hooks like files.
  The one raise-before-server check (resource + system/tools) is a
  request inspection. Holds.

**6. Model below the minimum.** (cost accountant)
- No provider errors; nothing is cached; Anthropic and OpenAI charge no
  write below the minimum (measured: 0/0). Holds without client-side
  minimum tables, which would rot.

**7. Tools change between turns.** (cold learner)
- Miss everywhere (measured). Not lm15's to fix; the docs should say
  "keep tools stable" once, citing the receipts.

**8. `retention="long"` on a provider without it.** (switcher)
- Raises on OpenAI ≥5.6 and Gemini. A user who wrote agnostic code with
  `retention="long"` hits a raise on their second provider. This is the
  price of rule 4 in the frame (no silent ignore). Stated.

**9. `mode="off"` on gpt-5.4.** (cold learner)
- Proposed mapping sends `prompt_cache_options`, which <5.6 rejects.
  The user asked for "off" on a model that has no switch. Two honest
  answers: raise (consistent) or send nothing (silently stays on, but
  costs nothing extra on <5.6 since writes are free). This is the one
  place where "silent" costs the user nothing. **Open question for the
  maintainer**, see §8.

**10. Gemini resource with system prompt in the request.** (porter)
- Adapter raises with the server's own wording before sending. Holds.
  Risk: the server rule changes and the client check is stale; the
  receipt has an expiry (step 10).

## What the attack did not cover

- Streaming: does the usage on the stream end event carry the same
  cache fields? Not measured this run. Cases exist for non-stream only.
- Batch: cache behaviour inside batch jobs. Not measured.
- Images/documents in the prefix (Anthropic caches them; OpenAI text
  blocks only). Not measured.
- Latency claims: recorded but not analysed; the receipts hold the ms.

## Open for the maintainer

1. `mode="off"` on OpenAI <5.6: raise, or send nothing.
2. `auto` on Anthropic: system block only (safe, small) or the trailing
   automatic marker (better for chats, a trap for fan-out).
3. Whether the T2 surface ships in the Python 1.0 with the other
   provisional surfaces, given "all surfaces in all languages".
