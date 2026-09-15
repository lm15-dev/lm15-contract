# 2026-09-14 — Adapt freely, never invisibly: the audit

Ratification: RATIFIED — Maxime Rivest, 2026-09-14, session assent
("brilliant, I agree so") over the rule, the mechanism and the eight
open cells of §4, all as recommended. Rule text: `docs/mapping-rules.md`
MAP-13; theory: `lm15-dev/THEORY.md` §3.9 and §3.17. Drafted in session
after the principle was agreed ("portability first; visible, not
blocking; a clear way to turn it off"). This document is (1) the rule, (2) the mechanism,
(3) an audit of every pre-wire refusal and every silent default in the
reference, each with a verdict, (4) the open choices, (5) the trade-offs.
Nothing below is implemented yet.

## 1. The rule

lm15 exists to lower the friction of universality: change the model or
provider string and the program keeps working. That is the first promise.
The second — never change what the caller asked for — is subordinate to
it, and is satisfied by VISIBILITY, not by refusal.

> Adapt freely. Never adapt invisibly. Refuse only when adapting would be
> a guess that could hurt.

An adaptation is a guess that could hurt when any of these holds:

1. **A real choice is needed** — two reasonable answers exist and picking
   one is presumptuous (a thinking budget with no effort word: which
   effort is 4,000 tokens?).
2. **The program depends on it** — continuing produces a failure later,
   further from the cause (a media part with no slot on the wire: the
   model answers without having seen the image; a stored cache object
   that does not exist on this provider).
3. **No sensible adaptation exists** — nothing to map to and nothing safe
   to drop.
4. **A wrong guess costs money, leaks data, or is hard to notice** —
   dropping `max_tokens` means unbounded spend; a lost privacy setting is
   a leak.

Everything else is adapted and recorded.

Refusals that survive keep the existing form (`UnsupportedFeatureError`
before the wire) and gain a structured `feature` field (the config path,
e.g. `config.top_k`, `tools[2]`, `messages[0].parts[1]`) so the layer that
owns the caller's intent can act without parsing prose.

## 2. The mechanism

### 2a. `Adaptation` record

```
Adaptation:
  field:   str        # config path: "config.seed", "config.temperature"
  action:  "dropped" | "clamped" | "substituted" | "client_side" | "satisfied" | "defaulted"
  asked:   JsonValue  # what the caller set (absent for "defaulted")
  applied: JsonValue  # what went to the wire (absent for "dropped")
  reason:  str        # one sentence, names the provider fact
```

`satisfied` = the provider's default already is what was asked (nothing
sent, nothing lost). `defaulted` = lm15 supplied a value the wire
requires and the caller did not set (Anthropic `max_tokens`). Both are
recorded because the caller could not otherwise know.

Translations — the adapter's ordinary job (`stop` → `stop_sequences`,
`effort` → `budget_tokens` by the MAP-7 table) — are NOT adaptations and
are never recorded. A note exists only where the wire got something
other than what was asked.

### 2b. Where it lives

- `Response.adaptations: tuple[Adaptation, ...]` (empty by default;
  omitted on the wire when empty per the omission rule).
- `StreamStartEvent.adaptations` — adaptations are known before the
  wire, so they ride the first event; the coalesced Response carries
  them too.
- `lm.plan(request) -> tuple[Adaptation, ...]` and
  `router.plan(request)` — the pre-flight: what WOULD be adapted, no
  network. This is also the answer to "can this route carry this
  request?" that DSPy's engine selection needs (the 2026-09-14 gauntlet
  doc, B2): a plan with a refusal raises the same
  `UnsupportedFeatureError` the call would.

### 2c. The switch

`RouterConfig(adaptations=...)` and the same keyword on every direct LM
constructor:

- `"note"` (default) — adapt and record.
- `"silent"` — adapt and record nothing (`Response.adaptations` empty).
- `"refuse"` — today's behaviour: any deviation (`dropped`, `clamped`,
  `substituted`, `client_side`) is an `UnsupportedFeatureError` before the
  wire.  `satisfied` and `defaulted` change nothing the caller asked for
  and are recorded, not refused (found while implementing: a strict user
  who set no `max_tokens` must not be refused for the wire's required
  field being filled).

Per-field override, additive, later if asked for:
`adaptations={"default": "note", "config.seed": "silent"}`.

Nothing prints. Ever. The note is data on the response. A consumer that
chooses to log adaptations logs each distinct one once per process.

`drop_params` in the OpenAI-chat ingest's client-keyword table now maps to
`adaptations="silent"` instead of "nothing".

## 3. The audit

Every `UnsupportedFeatureError` raised before the wire in the four chat
adapters plus xAI, every silent default, and the ingest refusals.
Verdicts: **ADAPT** (with the action), **SATISFIED**, **KEEP** (still
refuse, with the rule number), **CHOICE** (Maxime decides).

### 3a. Sampling and generation knobs

| Setting | Provider | Today | Verdict | Why |
|---|---|---|---|---|
| `top_k` | OpenAI Responses, Chat Completions wire | refuse | **ADAPT: dropped** | A sampling hint. Vercel's SDK drops it with a warning. `temperature=0` is the portable spelling of "greedy". |
| `seed` | Anthropic | extension → server 400 | **ADAPT: dropped** (after promotion, §3f) | Best-effort even on OpenAI. Nothing the program can depend on. |
| `frequency_penalty`, `presence_penalty` | Anthropic | extension → 400 | **ADAPT: dropped** (after promotion) | Sampling hints. |
| `temperature > 1` | Anthropic (0–1; OpenAI/Gemini 0–2) | server 400 | **ADAPT: clamped to 1.0** | Both scales default to 1.0; 0–1 is the same "cool half" on all three, and 1–2 exists only on two. "Hotter than this provider allows" → hottest. Never rescale (÷2 invents a meaning). Declare the canonical range as 0–2. |
| `temperature`, `top_p`, `top_k` | Moonshot Anthropic wire (server ignores silently) | refuse | **ADAPT: dropped** | The refusal existed only to make the server's silence visible. The note now does that. |
| `stop` | OpenAI Responses wire (no field) | refuse | **ADAPT: client_side** | Truncate at the first stop sequence in the coalescer (complete and stream). The model runs past it and the extra tokens are billed — bounded by `max_tokens`, stated in the note. Several SDKs do this. |
| `max_tokens` unset | Anthropic (field required) | silent 1024 | **ADAPT: defaulted** — and raise the default | 1024 truncates ordinary answers with no note; a user switching from OpenAI sees cut-off text. Default to the model's documented max output where the profile knows it, else a generous fixed value (16384 proposed; Anthropic's own SDK examples use 8192+), and record `defaulted`. |
| `n > 1` | everywhere | refuse | **KEEP** (rule 2) | A canonical Response is one message; the caller fans out. |
| `logprobs` | Anthropic, xAI ≥ 4.20 | refuse | **CHOICE** | The program reads them. But `Response.logprobs` is optional: the program sees `None`, not a crash later. Vercel treats it as unsupported-setting warning. Recommendation: ADAPT: dropped. |

### 3b. Reasoning (MAP-5, MAP-7)

| Setting | Provider | Today | Verdict | Why |
|---|---|---|---|---|
| `reasoning.summary="concise"/"detailed"` | Anthropic, Gemini, Chat wire | refuse | **ADAPT: substituted → "auto"** | A visibility preference between levels the wire lacks. The intent (show the thinking) is met. |
| `reasoning.effort="minimal"` | Anthropic adaptive class (floor "low") | refuse | **ADAPT: clamped → "low"** | Ordinal dial; nearest level. |
| `reasoning.effort` word with no level (e.g. `xhigh` on low/medium/high) | any server with a declared level set | refuse | **ADAPT: clamped** to the nearest declared level | Same. The refusal was there because the server would accept the word silently; the note now says what was sent. |
| `reasoning.thinking_budget` with `effort` also set | OpenAI, Anthropic adaptive, Chat wire (no budget) | refuse | **ADAPT: dropped** | Effort carries the intent (MAP-7 rule 5 already says budget is spelling, effort is intent). |
| `reasoning.thinking_budget` alone | same | refuse | **KEEP** (rule 1) | Which effort is 4,000 tokens? A real choice. Message says: add `effort`. |
| `reasoning=off` | Gemini 3 (no honoured off switch), xAI Grok reasoning models | refuse | **CHOICE** | Adapt → `effort="low"`: the closest to "none". Costs thinking tokens the caller said not to spend (rule 4, bounded, visible in `usage.reasoning_tokens`). Recommendation: ADAPT: substituted, because the alternative — crash on a model switch — is worse than a bounded, visible spend. |
| `reasoning.effort` on the `ollama` preset | refuse (2026-09-11 decision) | **WRONG FACT — translate** | The preset says `thinking_format="none"` with the comment "no live receipt for the policy yet". Ollama's own source (`research/tool-result-content/sources/ollama.txt:536-560`, `thinkFromReasoningEffort`) accepts `reasoning_effort` and `reasoning.effort`, maps them to `think`, clamps `minimal`→`low` and `xhigh`→`max`, and 400s an unknown word. The preset becomes `thinking_format="reasoning_effort"`; `cases/ollama/reasoning_effort_refused.json` pinned a non-fact and is replaced by a live receipt. `lmstudio` copies the same unreceipted policy and is unverified either way: receipt first. |

### 3c. Tools and structured output (MAP-8)

| Setting | Provider | Today | Verdict | Why |
|---|---|---|---|---|
| `tool_choice.allowed` subset | Anthropic, xAI (no subset form) | refuse | **ADAPT: client_side** | Send only the allowed tools in `tools`. That IS the semantics of "may only call these". The message already told the user to do it by hand. |
| `tool_choice.parallel=False` | Gemini (no knob), Anthropic-wire servers that ignore it | refuse | **ADAPT: dropped** | A preference. Agent loops iterate tool-call parts as a list anyway. |
| `response_format` (json_schema) | servers that accept and ignore `output_config.format` | refuse | **ADAPT: dropped** | Made visible by the note; the message keeps "describe the shape in the prompt". |
| `response_format={"type":"json_object"}` | Anthropic (no any-JSON mode) | refuse | **CHOICE — needs a live receipt** | If `output_config.format` accepts an open schema (`{"type":"object"}`), that is a translation. If not, a prompt instruction would be inventing (rule 3) → KEEP. One live call decides. |
| forced tool + `response_format` | xAI (server drops the call) | refuse | **KEEP** (rule 2) | A real conflict; the program depends on the call. |
| builtin tools with no wire mapping; forcing builtin tools | Chat wire, Gemini, Groq | refuse | **KEEP** (rule 2) | The program depends on the tool running. |
| Chat-ingest `functions` / `function_call` (deprecated shape) | ingest | refuse | **ADAPT: translated** to `tools` / `tool_choice` | A pure spelling change; the expert would translate. Silent (a translation, not an adaptation). |

### 3d. Caching (MAP-6)

| Setting | Provider | Today | Verdict | Why |
|---|---|---|---|---|
| `cache.key` | Anthropic, Gemini (no affinity key) | refuse | **ADAPT: dropped** | Defined as "a best-effort routing hint". Best-effort hints are dropped with a note, by definition. |
| `cache.retention="long"` | providers without a lifetime knob; Gemini in-request | refuse | **ADAPT: dropped** | You get the default lifetime; observable in `cache_read_tokens`. Costs LESS money, not more. |
| `cache.resource` | OpenAI, Anthropic (no stored-cache tier) | refuse | **KEEP** (rule 2) | The program references an object that does not exist here. |
| `cache.prefix_until_index` on a non-text block | OpenAI | refuse | **ADAPT: substituted** — walk back to the nearest eligible text block | The intent is "cache up to here"; the nearest eligible boundary is the obvious answer. Note says where the mark landed. |

### 3e. Account and policy knobs

| Setting | Provider | Today | Verdict | Why |
|---|---|---|---|---|
| `store=False` | Anthropic (no field) | refuse | **SATISFIED** | Anthropic offers no retrievable stored-response object; the caller's wish holds by construction. Record `satisfied`. (Anthropic's trust-and-safety retention is a separate fact, stated in the reason.) |
| `store=True` | Anthropic | refuse | **ADAPT: dropped** | Nothing canonical can be built on it (`previous_response_id` is an OpenAI extension). Note. |
| `user_id` | Gemini (no field) | refuse | **CHOICE** | Abuse attribution. Some organisations require it for compliance; nothing in the program depends on it at run time. Recommendation: ADAPT: dropped with note; the compliance case sets `adaptations="refuse"`. |
| `service_tier` | Gemini | translate (native `serviceTier`, live 2026-09-01) | **WRONG CELL in this draft** | Gemini, OpenAI and Anthropic all carry a service tier; the draft listed a refusal that does not exist. No adaptation anywhere. Item 6 of §4 is withdrawn. |
| batch `label` | Anthropic (no metadata field) | refuse | **ADAPT: dropped** | Convenience; correlate by id. |

### 3f. Promotions (what becomes canonical)

`seed: int | None`, `frequency_penalty: float | None`,
`presence_penalty: float | None` on `Config`. OpenAI (both dialects) and
every OpenAI-compatible preset carry them verbatim; Gemini carries them
as `generationConfig.seed / frequencyPenalty / presencePenalty` — which
means today's verbatim extension sends them to the WRONG PLACE on Gemini
(400 `Unknown name`). Anthropic drops with a note. Same promotion test as
2026-09-01 (`service_tier`, `user_id`, `store`): two or more providers
sell the concept. The ingest verdict "harmless verbatim" for `seed` is
withdrawn.

`logit_bias` stays an extension: token ids are model-specific, so it
was never portable.

### 3g. Content (MAP-10) — unchanged

Every "a part has no slot on this wire" refusal stays (rule 2: the model
would answer without having seen the input). These gain the `feature`
field (`messages[i].parts[j]`) so a consumer can decide to strip media
itself; lm15 does not.

### 3h. Non-chat endpoints — unchanged

Image/speech/video/batch/files refusals (no wire slot, not mapped yet,
no list endpoint) stay: provisional surface, rule 3.

### 3i. Ingest refused keys (MAP-12)

`n` KEEP. `functions`/`function_call` → translate (§3c). `audio`,
`modalities`, `prediction`, `web_search_options` → **CHOICE**: `prediction`
is a latency hint and belongs in extensions (harmless verbatim on OpenAI,
dropped-with-note elsewhere once promotion rules exist for extensions);
the other three name outputs the canonical Response cannot carry → KEEP.
`top_k` → the canonical field (§3a).

## 4. The choices for Maxime, in one list

1. `logprobs` on providers without them: drop with note (recommended) or keep refusing.
2. `reasoning=off` on models with no off switch (Gemini 3, Grok): substitute `effort="low"` with note (recommended) or keep refusing.
3. ~~ollama reasoning~~ — withdrawn: not a choice, a wrong fact (§3b). LM Studio needs a live receipt before any verdict.
4. `json_object` on Anthropic: one live receipt decides translate-vs-keep.
5. `user_id` on Gemini: drop with note (recommended) or keep refusing.
6. ~~`service_tier` on Gemini~~ — withdrawn: Gemini carries `serviceTier` natively (the draft's cell was wrong); nothing to decide.
7. `temperature > 1` on Anthropic: clamp with note (recommended) or keep the server's 400.
8. Anthropic default `max_tokens`: model max from the profile, else 16384 (recommended), with a `defaulted` note.
9. `prediction` in ingest: extensions (recommended) or keep refusing.

## 5. Process rule proposed

A compat preset field with no receipt is a hypothesis, not a fact, and a
refusal cannot be ratified on a hypothesis. Concretely: `tools/audit.py`
flags any case whose refusal rests on a preset field whose comment says
"no receipt", and the case file must cite the receipt path. The
2026-09-11 ollama decision would have been caught.

## 6. Trade-offs, stated

- **Surface growth.** `Adaptation`, `Response.adaptations`,
  `StreamStartEvent.adaptations`, `plan()`, the `adaptations=` switch,
  `UnsupportedFeatureError.feature`, three promoted Config fields: all
  frozen, all ported to five languages. The cost of universality done
  properly.
- **Behaviour reversals.** Roughly twenty refusals become adaptations.
  Every pinned case that asserted a refusal is rewritten; each gets the
  adaptation it now produces pinned instead. Three-day-old and
  two-week-old decisions are reversed (§3b, §3d) — under a better rule,
  and said so here.
- **A note can be ignored.** That is by design: data, not noise. The cost
  is that a caller who never looks at `adaptations` and never sets
  `"refuse"` can run for months with `seed` dropped. That is the
  agreed price of portability; the strict mode exists for those who
  disagree.
- **`plan()` doubles the build path.** The adapter builds a request twice
  for a pre-flight. Fine for one call; a consumer selecting engines per
  call pays it per call. Cacheable by request hash if it matters.
- **Client-side `stop` streams under the hood, on `complete()` too, and
  closes the connection at the cut** (decision in session 2026-09-14,
  "ok, we do that"). Whether the provider stops generating on a closed
  connection is its own behaviour (review of dspy#10409 caught the
  overclaim "nothing past it is billed"). The price is the usage report, which rides only the final
  frame: it is "not reported" on a cut call, never estimated (the exact
  alternatives — the count-tokens endpoint for input, logprob entries for
  output text tokens — cost a call or constrain the request, and neither
  sees reasoning tokens; they may become an opt-in). A call whose text
  never reaches the sequence completes normally, usage included.
- **"Satisfied" claims can rot.** `store=False` on Anthropic rests on a
  provider fact. Each `satisfied` verdict carries a dated receipt in the
  case file and is re-checked when the provider's terms change.
