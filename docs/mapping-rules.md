# Canonical mapping rules

Normative rules for mapping between provider wires and the canonical lm15
representation (MAP-1..MAP-9 mostly the response side; MAP-10 the request
side of message content; MAP-12 the reverse direction, a foreign request
body read INTO a canonical Request). Companion to `serde-rules.md` (which governs the JSON wire
format); these govern WHAT becomes a canonical part. Goldens and conformance
fixtures cite these rules by number.

## MAP-1 — Parts are what the application must act on

A canonical message part is something the application must handle or display:
text, thinking, citations, media, a client-side tool call (which obligates the
caller to execute it and return a tool_result), or a tool result.

Provider-executed builtin tool activity is **not** represented as parts. This
includes Anthropic `server_tool_use` / `code_execution_tool_result` blocks and
container metadata, OpenAI `code_interpreter_call` / `web_search_call` items,
and Gemini `executableCode` / `codeExecutionResult` parts. The user-relevant
*outputs* of such tools (answer text, citations, generated media) are mapped
to parts as usual; the execution mechanics remain available verbatim in
`provider_data`.

**Why:** a `tool_call` part is a contract — "the caller must execute this."
Agent loops iterate tool_call parts and run them. Surfacing provider-executed
calls as tool_call parts would cause every agent loop to re-execute work the
provider already performed. If canonical access to execution traces is needed
later, it must be a NEW part type (additive), never a reinterpretation of
tool_call.

## MAP-2 — A response message is never empty

When a provider response yields no canonical parts (e.g. the model spent its
entire output budget on hidden reasoning and was truncated), the canonical
message is a single empty `TextPart` (`text: ""`).

**Why:** `Message.parts` is non-empty by invariant, everywhere, for every
producer — relaxing it for one edge case would weaken a guarantee all ports
and consumers rely on. Erroring would turn a legitimate provider response into
a crash. With the empty part, `response.text == ""` plus the finish_reason
(e.g. `"length"`) reads as exactly what happened.

## MAP-3 — A stream yields exactly one end event, and it is final

An lm15 stream yields EXACTLY ONE `StreamEndEvent`, as the final event of the
stream, carrying the `finish_reason` and `usage` accumulated across all of the
provider's terminal frames.

Providers split their terminal data across multiple frames: OpenAI-compatible
servers (vLLM, SGLang, ollama, Groq) send a `finish_reason`-bearing chunk,
then — with `stream_options.include_usage` — a usage-only chunk, then
`[DONE]`; Anthropic sends `message_delta` (stop_reason + usage) followed by a
bare `message_stop`. Adapters stay stateless and may emit one per-frame end
event for each such terminal frame, but that is an internal detail: a
provider-agnostic coalescer (`lm15.result.coalesce_stream`) absorbs every
adapter end event — later non-`None` fields fill gaps, a non-`None` field is
never overwritten by `None` — and emits the single merged end event once the
underlying iterator is exhausted. The canonical event trace (goldens, the vet
shim's `replay_stream`, conformance `parse_stream`) is the POST-coalesce
trace.

**Why:** multiple end events made every consumer's merge semantics
load-bearing, and they failed in live testing. `Result` treated the first end
event as terminal (`break` on `type == "end"`), so the post-finish usage-only
chunk that vLLM/SGLang/ollama send was never applied and the materialized
`Response.usage` came out all zeros (pinned as a known-bug baseline in the
streaming_vllm/streaming_sglang draft goldens before this rule). With exactly
one final end event, "the end event" and "the stream's finish_reason and
usage" are the same thing by construction, in every port.

**Terminal frames that say nothing say nothing.** A bare terminator (`[DONE]`
on either OpenAI dialect, Anthropic `message_stop`) maps to an end event with
`finish_reason=None` and `usage=None`. It must not claim `stop`: the merge
rule lets a later non-`None` value replace an earlier one, so a `[DONE]`
carrying `stop` would overwrite the `tool_call` that `response.completed`
had already established. The event trace would then contradict the
materialized `Response`.

**`StreamEndEvent.provider_data` is the wire frame that supplied `usage`,
verbatim (the JSON object of that frame; when several frames carry usage,
the last one — the coalescer's later-fills reading); if no frame supplied
usage, the frame that supplied `finish_reason`. Bare terminators contribute nothing.
It is an escape hatch, not a canonical fact: the harness compares it for
presence and JSON type only.** Chat: the usage chunk. Anthropic: the
`message_delta` frame. Responses: `response.completed` (the event
payload's `response` object, as today). Gemini: the last chunk. xAI: same
as its wire. (Ratified 2026-09-06,
lm15-contract/changes/2026-09-06-ratification.md D9.)

**Usage counters at the wire boundary (INV-029).** An adapter never invents
`0` for a counter the provider did not send; absent stays `None` and
`Usage` auto-sums `total_tokens` only when both primaries are present. One
stated exception: Gemini's proto3-JSON wire omits zero-valued fields, so
inside a present `usageMetadata` an absent `promptTokenCount` or
`candidatesTokenCount` is a reported `0` (pinned by the reviewed golden
`gemini.max_output_tokens`: `candidatesTokenCount` absent, `totalTokenCount`
= prompt + thoughts). When `usageMetadata` itself is absent, every counter
is `None`. Secondary Gemini counters (cache, thoughts) stay verbatim: absent
is "not reported".

---

## MAP-4 — A stream opens with exactly one start event

An lm15 stream that yields any delta or end event yields EXACTLY ONE
`StreamStartEvent`, before all of them. Dialects with a real start frame
(OpenAI Responses `response.created`, Anthropic `message_start`) pass it
through with its `id` and `model`; dialects without one (chat completions,
Gemini SSE) get a synthesized start carrying the request's model, added by
the same coalescer that enforces MAP-3. Duplicate starts collapse to the
first. Error events never force a start: a stream that fails to open has no
start.

**Why:** live testing (dspy-greenfield `tests/live`, 2026-08-16) showed the
event vocabulary split by dialect — Responses API streams began with a start
event, chat-completions and Gemini streams began with a bare delta — so any
consumer that keyed on the start event worked on one provider and broke on
the next. One vocabulary means the trace shape is provider-independent.

## MAP-5 — Explicit reasoning-off reaches the wire or fails loudly

`Config(reasoning=Reasoning(effort="off"))` is an explicit instruction, not
a default (the tri-state is defined in spec/types.md §Reasoning). Every
adapter must translate it into the provider's native disable mechanism:

- OpenAI Responses dialect: `reasoning: {"effort": "none"}`
- Chat Completions `reasoning_effort` servers (incl. Groq, vLLM, SGLang):
  `reasoning_effort: "none"`
- OpenRouter: `reasoning: {"enabled": false}`
- DeepSeek: `thinking: {"type": "disabled"}`
- Qwen/DashScope, Z.AI: `enable_thinking: false`
- Gemini: `thinkingConfig: {"thinkingBudget": 0}`
- Anthropic and Claude Code: omit `thinking` — thinking is opt-in there,
  so absence IS the native off switch.
- xAI: RAISES `UnsupportedFeatureError`. Grok reasoning models have no
  off switch and api.x.ai silently ignores disable-shaped fields.

When the selected model cannot honor the disable (gpt-5-mini's floor is
`"minimal"`; gemini-2.5-pro rejects budget 0), the provider's 400 surfaces
unchanged. An adapter must never omit the field and let the model reason at
its default — that is a silent paid no-op.

**Why:** live testing (2026-09-01) showed omission was not off:
gpt-5-mini spent 64 hidden reasoning tokens, Groq gpt-oss-20b spent 45,
and grok-4.6 spent 158 while accepting `thinking: {"type": "disabled"}`
without effect. Reasoning tokens are billed output; an explicit off that
silently does nothing charges the caller for what they disabled.

## MAP-6 — Caching: one model for every provider

Every provider caches prompt prefixes in up to three tiers; 13 providers
were studied on 2026-09-01, six of them measured live (OpenAI both
dialects, Anthropic, Gemini, xAI, Groq) and seven from documentation only
(lm15-contract/research/caching/):

- **automatic** — nothing to send, best-effort, no user-visible state
  (OpenAI all classes, Gemini implicit, xAI, Groq, DeepSeek, Fireworks,
  vLLM, SGLang);
- **breakpoint** — a mark on a block, guaranteed above a per-model
  minimum, 1.25x write price (Anthropic; OpenAI gpt-5.6 and later);
- **resource** — a stored, named object with a lifetime and a storage
  price per token-hour, pinned to one model (Gemini `cachedContents`,
  Vertex; any future provider with the same shape).

`CacheConfig` names INTENTS. Each adapter maps an intent to the best tier
it has; the outcome is always visible in `Usage.cache_read_tokens` /
`cache_write_tokens`.

1. **No `config.cache`: send nothing.** Automatic tiers apply server-side.
2. **`mode="off"`: send nothing, and disable cache WRITES where a switch
   exists** — OpenAI gpt-5.6+ `prompt_cache_options: {"mode":
   "explicit"}` with no marks. Pre-5.6 OpenAI models reject the option and
   write for free, so they get nothing (option 2, ratified 2026-09-01).
3. **`mode="auto"` with no prefix: the cheapest safe instruction.**
   Anthropic marks the system block; every other provider sends nothing.
   Never the trailing marker: with a changing last message it wrote the
   full prefix at 1.25x on every call and read nothing (measured on both
   Anthropic top-level `cache_control` and OpenAI implicit mode).
4. **Prefix intents are marks where marks exist, and fall back to the
   automatic tier where they do not.** `prefix="stable"` marks the end of
   system + tools (Anthropic: the system block; OpenAI: the system prompt
   is rendered as the first developer/system message with the mark,
   because top-level `instructions` cannot carry one). `prefix="history"`
   marks the last block of the last message (Anthropic); on OpenAI 5.6+
   implicit mode already does exactly that, so nothing is sent.
   `prefix_until_index=N` marks the last block of message N (Anthropic:
   any block; OpenAI: a text block, else RAISE). On the OpenAI 5.6+ class
   a placed mark travels with `prompt_cache_options: {mode: "explicit"}`:
   without the mode the warm call still wrote the volatile suffix at
   1.25x (pinned 18 tokens after reading 3066); with it the warm call
   writes 0 and the cold write shrinks to exactly the marked prefix
   (3088 → 3070). Amended 2026-09-02 on the independent review's probe
   3; no mark, no mode (explicit mode with no mark caches nothing).
   Providers without marks
   (Gemini, xAI, Groq, older OpenAI, compat servers with
   `cache_control="none"`) send nothing. The fallback is permitted by two
   conditions, both required: it spends nothing, and its outcome is
   observable in usage. It must not be extended to fields that fail
   either condition.
5. **`retention="long"`** names a specific mechanism: Anthropic `ttl:
   "1h"` (2x write); OpenAI, every class, `prompt_cache_retention:
   "24h"`; Gemini (lifetime belongs to the stored object) RAISES. The
   5.6+ class used to RAISE on a doc line about `prompt_cache_options.ttl`
   (30m only) — a different field. Every pinned 5.6 body already echoes
   `prompt_cache_retention: "24h"` as its default, and sending it answers
   200 with the same echo (review probe 2, 2026-09-02). Amended.
6. **`key`** is a best-effort affinity hint: OpenAI and OpenRouter
   `prompt_cache_key`; Anthropic and Gemini RAISE.
7. **`resource`** is a `CacheInfo.id` from the resource tier. The adapter
   references the object and sends only what the object does not hold —
   Gemini: `cachedContent` + the messages after `prefix_until_index`, no
   `systemInstruction`/`tools`/`toolConfig` (the server rejects them next
   to a cache). Providers without the tier RAISE.
8. **The resource tier is a surface**, shaped like files: `cache_create
   (prefix: Request, ttl_seconds, label)`, `cache_get`, `cache_list`,
   `cache_delete`, `cache_update(id, ttl_seconds)`, pure hooks, async
   mirrors, the `cache` harness direction, `EndpointSupport.caches`.
   `lm.cache(prefix)` returns a `CachedPrefix`: on the resource tier it
   creates the object (one explicit, billed call); elsewhere it is pure.
   `cached + messages` builds the Request with the boundary at the seam.
9. **No hidden network calls.** An adapter's `build_request` never
   creates cache state. (Removed 2026-09-02: the Gemini adapter's
   per-request `cachedContents` POST, which made a billed object per
   turn and reused none.)
10. **Docs state the fan-out trap**: on OpenAI 5.6+ with no config, one
    document and many questions writes at 1.25x every time and never
    reads; `prefix="stable"` or `lm.cache(prefix)` is the one-line fix.
    A tools change is a miss everywhere.

**Why:** the caching design pass (lm15-contract/changes/2026-09-01-caching-design.md,
research/caching/). Provider agnosticism is defined as: the same code
runs everywhere, does the best thing the provider offers, and shows the
result — not identical bytes saved everywhere.

## MAP-7 — Reasoning: one dial, two spellings, no silent drops

Measured 2026-09-02 across OpenAI, Anthropic, Gemini, xAI, Groq (134
cells) and 17 sources (lm15-contract/research/reasoning/).

1. **Absent `config.reasoning` sends nothing**: the model decides. Every
   provider's default is adaptive now; "adaptive" is not a level.
2. **`effort` is the one dial**, required, vocabulary `off, minimal, low,
   medium, high, xhigh, max`. Providers with levels get the word
   verbatim (OpenAI; Anthropic adaptive class as `output_config.effort`;
   Gemini 3.x as `thinkingLevel`; xAI and Groq as `reasoning_effort`).
   Model-unsupported words fail with the server's 400. Words with no
   native level on a provider RAISE client-side: Anthropic `minimal`,
   Gemini 3.x `xhigh`/`max`.
3. **Budget-only model classes express effort as a budget** through one
   grading table — minimal 1024, low 2048, medium 8192, high 16384,
   xhigh 24576, max 32768 — Anthropic's manual class (4.5 and earlier:
   `budget_tokens`) and Gemini 2.5 (`thinkingBudget`). The design's one
   invented mapping; stated, receipted on both.
4. **`effort="off"`** sends the native disable (OpenAI `none`; Anthropic
   omits `thinking`; Gemini 2.5 `thinkingBudget: 0`; compat disable
   forms) and RAISES where the provider cannot disable or accepts the
   disable without honouring it: xAI, Gemini 3.x (3.7 Flash took
   `thinkingBudget: 0` and spent 58 tokens). MAP-5, extended.
5. **`thinking_budget`** maps where the wire has a budget (Anthropic
   manual class; Gemini, both classes) and RAISES elsewhere (OpenAI,
   Anthropic adaptive class, xAI, the chat dialect). On budget classes
   the budget is the spelling and `effort` stays the intent; they are
   not a conflict.
6. **`total_budget` is gone.** `Config.max_tokens` is the ceiling: on
   Anthropic's manual class the adapter adds the thinking budget to it;
   on the adaptive class it is the total (provider semantics).
7. **`summary`** is visibility: `None` = provider default; `"auto"` =
   show the thinking where a knob exists (OpenAI `summary: auto`; Gemini
   `includeThoughts: true`; Groq preset `reasoning_format: parsed` —
   receipted 2026-09-02 on qwen3.6-27b: the default leaks a raw
   `<think>` block into `content`, `parsed` returns `message.reasoning`
   and clean content) and
   is satisfied silently where thinking is always returned (Anthropic,
   xAI); `"concise"`/`"detailed"` verbatim on OpenAI Responses, RAISE
   elsewhere. Gemini gets `includeThoughts` only when asked.
8. **Replay.** Native when the continuation state is present: Anthropic
   signed blocks, Gemini signatures (required on 3.x function calls —
   400 without), OpenAI reasoning items (`openai:reasoning_item` with
   `id` and `encrypted_content`, replayed as `{"type": "reasoning",
   "summary": [...]}` — `summary` is required even when empty, 400
   without). Without state, a `ThinkingPart` is replayed as assistant
   text on every provider (decision G); the chat dialect's
   `thinking_replay` default is `as_text`. **`ContinuationState.provider`
   names the dialect that consumes the state (`openai`, `anthropic`,
   `gemini`, `xai` where xAI has its own wire), never the door. A Meta or
   Azure reasoning item is `openai:reasoning_item`. State replays
   verbatim on any door of that dialect; the server judges.** (Ratified
   2026-09-06, D7.)
9. **An OpenAI reasoning item with no summary is an empty `ThinkingPart`**
   carrying its replay state, never dropped. `Usage.reasoning_tokens`
   comes from every provider's exact field.
10. **Model-class detection** (Anthropic adaptive vs manual; Gemini 2.5
    vs 3.x) is by model-name table — a table that rots; the server 400s
    loudly when wrong; `extensions` overrides.
11. **Hidden thinking is a `ThinkingPart` with empty `text` and
    continuation state. There is no flag and no placeholder text.**
    Anthropic `redacted_thinking` → `ThinkingPart(text="",
    continuation=[anthropic:redacted_thinking {"data": <blob>}])`. In a
    stream: `ThinkingDelta(text="")` at `content_block_start`,
    `ContinuationDelta(part_index=i)` at `content_block_stop`. Replay is
    unchanged (the blob goes back as `redacted_thinking`). A Responses
    reasoning item with no summary is already "empty text + state" (rule
    9): one concept, not two. `[redacted]` was English presentation text,
    not provider text. (Ratified 2026-09-06, D5; `ThinkingPart.redacted`
    removed.)
12. **Thinking comes only from a typed wire field. lm15 never parses
    delimiters (`<think>`, `<reasoning>`, …) out of provider text. Where
    a server knob separates reasoning (Groq `reasoning_format: parsed`,
    rule 7), the preset sends the knob.** Bedrock runtime gpt-oss inline
    tags stay literal text; a live cell (does the runtime accept a
    parsed-reasoning knob?) is a follow-up, not done here. (Ratified
    2026-09-06, D10.)

**Why:** the reference knew one Anthropic class and one Gemini class, so
every `Reasoning` on Sonnet 5 was a 400 and every one on Gemini 3.x used
a deprecated field; it silently dropped budgets, summaries, and OpenAI
reasoning items; and it downgraded `xhigh` to `high`. The design pass
record: lm15-contract/changes/2026-09-02-reasoning-design.md.

## MAP-8 — Tool choice and structured output: no silent cells, one shape

Measured 2026-09-02 (141 cells; lm15-contract/research/tool-choice/,
research/structured-output/). The 2026-09-01 kind-aware `ToolChoice`
mapping holds; three cells were silent, and `response_format` had no
canonical shape.

1. **xAI ignores allowlists.** `tool_choice.allowed` subsets RAISE on
   xAI; a single name with `mode="required"` maps to the forced-function
   form, which held. The single cell of 2026-09-02 was repeated five
   times with fresh nonces on the review's request: 5/5 called the
   disallowed tool (`research/review-2026-09-02/`).
2. **Gemini has no parallel knob.** `parallel=False` RAISES on Gemini
   (two calls came back regardless). The MAP-6 fallback exception does
   not apply: the outcome is not observable from usage.
3. **xAI drops a forced tool next to a `response_format`** (JSON text,
   no call): the pair RAISES on xAI. Elsewhere the server decides —
   Gemini and Groq 400, OpenAI and Anthropic let the call win.
4. **INV-050: `response_format` is `{"type": "json_object"}` or
   `{"type": "json_schema", "schema", "name"?, "strict"?}`**, validated at
   `Config` construction. Provider-native spellings belong in
   `extensions`. `schema` is verbatim: lm15 never rewrites a keyword to
   make a request pass (Anthropic rejects `minimum`; OpenAI and Groq
   strict mode need every property required — their 400s are the
   contract).
5. Mapping: OpenAI Responses `text.format` (`name` defaults to
   `"response"`); chat dialect, xAI, Groq, compat `response_format
   .json_schema {name, schema, strict}`; Anthropic `output_config.format
   {type: json_schema, schema}` — `json_object` RAISES (no any-JSON
   mode); Gemini `responseMimeType` + `responseJsonSchema` or
   `responseSchema` by the `additionalProperties` rule.
6. `strict` goes verbatim where the wire has it and is satisfied where
   enforcement is always on (Anthropic, Gemini). `name` is a label, not
   a control: dropped where there is no slot.

**Why:** two canonical spellings for one intent, with the wire deciding
which, violates principle 2 of types.py; and a restriction that widens
silently is the worst failure a tool-using loop can have.

---

## MAP-9 — Stream assembly never invents a tool-call name

When a stream's tool-call fragments for one part index never carry a
`name`, the assembler (`lm15.result.StreamAccumulator.response`) does not
guess. It raises `StreamAssemblyError` (ErrorCode `stream_assembly`) whose
`partial` is the Response assembled from everything else that arrived —
text, thinking, media, citations, named calls, usage, the provider's finish
reason — with the unnamed call(s) left out, and whose `part_index` is the
first offending part. Wrappers surface it at the earliest point the defect
is known: `materialize_response` when called, `ResponseStream` at the end
of iteration (text already yielded stays yielded).

What lm15 does mint: a missing `id` becomes `tool_call_<index>`. That is an
lm15-owned correlator, stated, needed because Gemini sends no call ids; it
is not a guess about what the model meant.

**The complete path is the same rule** (2026-09-07,
`changes/2026-09-07-complete-tool-call-no-guess.md`). A non-streaming body
whose tool call carries no name — a Responses `function_call` item, a chat
`tool_calls[i].function`, an Anthropic `tool_use` block, a Gemini
`functionCall` part — is refused at `parse_response` with `ProviderError`
(ErrorCode `provider`): the provider's reply is not actionable, and there
is nothing to salvage from a body the caller never saw stream by. Before
this date the reference substituted the literal `"tool"` — the guess the
stream path had already refused, made on the complete path, so the same
turn answered differently under `stream=True` (INV-051). Pinned by the
four `<dialect>.tool_call_unnamed_complete` cases.

**Assembly algorithm** (the same in every port; written down 2026-09-02
after the independent review found it lived only in code):

1. `part_index` names a **slot**, not a part. A slot may accumulate
   several kinds at once, because the chat dialect indexes text, thinking,
   and tool calls independently (a text delta and a tool-call delta both
   arrive at index 0 — pinned by `openai_chat.tool_call_unnamed` and
   `xai.streaming`).
2. Per slot, per kind, fragments concatenate in arrival order: text and
   thinking by string, audio by base64 chunk, tool-call input by string
   (parsed as JSON at the end, best-effort), tool-call `id`/`name` last
   non-`None` wins, image and citation parts replace.
3. At materialization, slots are visited in ascending index; within one
   slot the parts are emitted in this fixed kind order: **thinking, text,
   image, audio, citations, tool call**. Continuation state attached to
   the slot goes on every part emitted from it.
4. A slot that received only continuation state (no content of any kind)
   emits one empty `TextPart` carrying that state, so the state is not
   lost. A message with no parts at all emits one empty `TextPart`
   (MAP-2).
5. `finish_reason`: the end event's word wins; `None` becomes `tool_call`
   when a tool call was assembled, else `stop`; a provider `stop` next to
   an assembled tool call becomes `tool_call`.
6. The stream's `id` is the start event's id when the dialect has a start
   frame (Anthropic `message_start`, Responses `response.created`); the
   chat dialect has no start frame and its per-chunk `id` is **not**
   lifted into the Response (pinned by the reviewed `openai_chat.streaming`
   and by `xai.streaming`; a wire fact dropped by rule, stated here).
   The fields the wire withholds on the stream path (INV-051), per
   dialect, today: chat dialect — `id` (this rule) and the served `model`
   snapshot (a chunk's `model` may be the dated snapshot while the complete
   body's is the alias; the stream keeps the request's model, MAP-4);
   Gemini — `id` (no start frame carries one). Nothing else. A minted
   tool-call id is `tool_call_<index>` on both paths (parity verified
   2026-09-06 over every pinned stream body; the complete Gemini path
   used to mint `fc_<index>`, corrected the same day with the three
   frozen Gemini goldens re-reviewed). Continuation state
   is never withheld: state known at start is emitted immediately after
   `start` as a message-level `ContinuationDelta`; state known at a
   part's end is emitted at that end. No dialect emits
   `openai:response_id`, `gemini:response_id`, or `anthropic:message_id`
   continuation: `Response.id` (and `StreamStartEvent.id`) carry the id;
   server-side chaining knobs (`previous_response_id`, `conversation`)
   stay `extensions` per INV-049. (Ratified 2026-09-06, D8.)

**Why:** an unnamed call is not actionable (MAP-1), and every shipped
dialect names a call on its first fragment — pinned 2026-09-02 as four
stream cases, `<dialect>.streaming_tool_call` on OpenAI Responses, OpenAI
Chat, Anthropic, and Gemini — so a missing name is an adapter defect, not
model behaviour. The previous rule filled the name from
`Request.tools` by position — one declared tool, else the tool at the
part's rank among all parts, else the literal `"tool"`. That guess flipped
when the model emitted text before the call, and an agent loop dispatching
on the guessed name would run the wrong function with no error. That is the
silent failure MAP-8 refuses on the wire; MAP-9 refuses it in assembly.
`partial` exists so a caller who wants the turn's text can still have it,
on the same principle as the MAP-3 coalescer: never fabricate, never
discard what arrived.

Pinned by `lm15-contract/cases/openai_chat/tool_call_unnamed.json`, a
hand-built degraded OpenAI-compatible stream (arguments and id, no
`function.name`), whose golden pins the raise, the salvaged partial, and
the event trace. The `partial.finish_reason` is the provider's `tool_call`,
kept as reported even though the partial holds no call: the caller is
holding the error and knows why.

---

## MAP-10 — Message content reaches the wire natively or raises

Measured 2026-09-07 (≈220 cells over 31 bindings; `lm15-contract/research/
tool-result-content/`, receipts `receipts/2026-09-07-tool-result-media/`).
Before this rule every dialect except Anthropic rendered
`ToolResultPart.content` through a lossy text join: an image returned by a
tool became a caption or the literal string `[{"type": "image"}]`, the
request got HTTP 200, and the model answered as if the tool had returned
less. MAP-5..8 forbade silent drops for *knobs*; nobody had applied the
same rule to *parts inside messages*. This rule does.

1. **Every part reaches the wire as a native block, or the adapter raises
   before any wire.** A part in any message — including inside
   `ToolResultPart.content` — maps to the dialect's own block for that
   kind (image, document, …) inside the same wire item, or
   `build_request` raises `UnsupportedFeatureError`. There is no
   `extensions` door for a part: a part is not a knob.
2. **No lossy rendering of a non-text part.** A caption, a type name, a
   placeholder, a data URI as prose, or base64 as text is a silent
   substitution and is forbidden. `parts_to_text` (and its port
   equivalents) renders only text-bearing parts and is used only on the
   cells this document names; passing a media part to it is a bug.
3. **The threshold is "the model received it", not HTTP 200.** A server
   that accepts the bytes and shows the model a marker
   (`[Unsupported Image]`, DeepSeek; a silently ignored `image_url` on
   an OpenAI Chat tool row) is *unsupported* for that part kind. The
   preset says `reject`; the raise names the mechanism ("server silently
   drops" vs "server rejects") and the sibling door that carries it.
4. **A wire slot that exists is used, whatever its shape.** Gemini nests
   media under `functionResponse.parts`; Responses turns `output` into an
   array; Anthropic takes blocks in `tool_result.content`. Refusing a part
   the wire carries is a missing mapping, not caution. Model gating that
   fails loudly server-side (Gemini 2.5: HTTP 400 "Multimodal function
   responses are not supported for this model") is left to the server;
   lm15 keeps no model allowlist for message content.
5. **Order, association and status survive.** Blocks keep the caller's
   order inside the result item; each result rides under its own call id;
   `is_error` maps to the wire's flag (`is_error`, Gemini
   `response.error`) or, where the wire has none (Responses, Chat), the
   text of the result is prefixed `[error] ` — stated here so a port
   produces the same bytes.
6. **Names are resolved, never invented.** Where the wire requires the
   function name on a result (Gemini `functionResponse.name`): the
   caller's `ToolResultPart.name` if given; else the name of the nearest
   preceding assistant `ToolCallPart` with the same id in the transcript;
   else raise. `"tool"` as a default name is forbidden.
7. **Text-only content is a string where the wire takes a string.** That
   is not lossy and is the ratified cell for every binding.
8. **The verdict per (preset, part kind) is data**, a typed compat knob
   (`tool_result_media: native | reject` on the Chat, Responses and
   Anthropic compat tables; `spec/types.md`), pinned by
   `cases/<provider>/tool_result_*.json` (native) and `expect_lm15.raises`
   cases (reject). A blank cell is drift (`tools/check_content_coverage.py`).

Measured verdicts (2026-09-07; the ledger is
`research/tool-result-content/20-results.md`):

- native for images: openai (Responses; gpt-5.4 exact at a readable
  oracle), openai-codex, meta (Responses), moonshotai-responses,
  anthropic, claude-code, meta-anthropic, moonshotai-anthropic, gemini
  (3.x; 2.5 answers 400), xai, moonshotai, zai.
- native for documents: openai (Responses), anthropic, claude-code,
  meta-anthropic, gemini.
- reject (server 400): groq, meta-chat, bedrock-chat; documents on xai
  (its own 400 names /v1/responses), moonshotai (all three doors),
  openai-chat, zai.
- reject (200, model did not receive): openai-chat and azure-chat
  (control passed on the same model), deepseek, deepseek-anthropic.
- reject until a receipt exists: openrouter (401 during the pass), ollama
  (source drops the call id on image rows; live timeouts), vllm, sglang
  (no server reachable), the blocked cloud hosts.

Stated deviation: Gemini's documented `$ref`-by-`displayName` interleave is
not emitted; lm15 puts text in `response` and media in `parts`, in order.

## MAP-11 — A provider id placed in a URL path is percent-encoded

An id the provider handed back (`FileInfo.id`, `BatchJobInfo.id`,
`CacheInfo.id`, `VideoJobInfo.id`) is an opaque string. When an adapter
places it in a URL path (`…/files/{id}`, `…/batches/{id}/cancel`,
`…/videos/{id}/content`, `…/{resource}:download`), it is percent-encoded
per RFC 3986 over its UTF-8 bytes: every byte outside the unreserved set
(`A–Z a–z 0–9 - . _ ~`) becomes `%XX` (uppercase hex).

1. **Resource-name dialects keep `/`.** Where the wire's ids are resource
   names whose segments are part of the route (Gemini: `files/abc`,
   `cachedContents/abc`, `batches/abc`, `models/m/operations/abc`), `/` is
   left literal and everything else is encoded (the reference's
   `quote(id, safe="/")`). A `:` inside such an id is encoded: the
   dialect appends its own `:download` / `:cancel` after the id.
2. **Flat-id dialects encode `/` too** (OpenAI, Anthropic, xAI:
   `quote(id, safe="")`). A literal slash there would turn one operation
   into another on the same route table — `file_get("x/content")` would
   download `x`.
3. **Never decode first.** An id is sent as given; a provider that returned
   a pre-encoded id would be double-encoded and answer 404 — loud. The
   alternative, sending reserved bytes raw, misroutes silently (`?` starts
   a query string, `#` a fragment). Every failure mode of this rule is
   loud; that is the point.
4. **Server-provided URLs are not ids.** A full URL the provider returned
   (Anthropic's `results_url`, a Gemini file `uri`, a Sora content URL) is
   used verbatim; only the id-to-path placement encodes.
5. Ids in JSON bodies (`input_file_id`, a batch `custom_id`) and in query
   parameters are JSON / query-encoded by the ordinary rules; MAP-11 is
   about the path.

Pinned by one hand-authored case per surface and dialect
(`cases/<provider>/{files,batch,cache,video}_id_escaping.json`): an id
carrying a space, `?`, `#`, `%` and, on the resource-name dialect, a `:`.

## MAP-12 — A Chat Completions request body reads into a canonical Request, or refuses

Status: RATIFIED 2026-09-08 (`changes/2026-09-08-openai-chat-ingest.md`).
Provisional surface (`spec/SCOPE.md`).

MAP-1..11 map lm15's canonical types OUT to a wire and a wire's response
back IN. This rule is the one place lm15 reads a *foreign request* — the
JSON object a client would POST to `/chat/completions`, the format every
litellm / OpenAI-SDK caller, log file and framework adapter already holds —
into a canonical `Request`. It exists so that migration to lm15 has one
correct converter with stated refusals instead of one lossy converter per
caller.

1. **One function, one preset.** `request_from_openai_chat(body, compat)`
   (`playbooks/api-family.md`) reads the spellings of ONE Chat Completions
   dialect: the same resolved compat policy the dialect adapter writes
   with (`OpenAIChatCompat` preset, per-model overrides applied). On the
   adapter, `lm.request_from_openai_chat(body)` is the same function under
   that adapter's policy. Another server's spelling of a knob (DeepSeek's
   `thinking` on the OpenAI preset, `user_id` where the server spells it
   `user`) is REFUSED: it would be sent and ignored, the silent paid no-op
   MAP-5 forbids.
2. **Every key has exactly one verdict**, recorded as data in
   `tools/openai-chat-ingest-verdicts.json` and enforced two ways by
   `tools/audit.py` (every key, content-block type, tool type and
   tool_choice form in a chat-dialect case body has a row; every top-level
   body parameter the scraped OpenAI reference documents has a row):
   - **map** — reads into the named canonical field.
   - **extensions** — passes verbatim into `config.extensions[key]`
     (`seed`, `logit_bias`, `presence_penalty`, `frequency_penalty`,
     `metadata`, `verbosity`, `moderation`, OpenRouter's `provider`):
     generation knobs the wire documents, no canonical field expresses,
     and a chat server receives unchanged. The builder re-emits
     `extensions` verbatim, so they round-trip.
   - **refuse** — `UnsupportedFeatureError` (`unsupported_feature`) naming
     the key and what the canonical model cannot carry: `n` (lm15 reads one
     choice; the others would be lost silently), the deprecated
     `functions` / `function_call` / `role: function` shape, `audio`,
     `modalities`, `prediction`, `web_search_options`, `top_k`, a
     per-message `name`, a `custom` tool, `strict: true` on a tool, a
     content block with no canonical part. A key with NO verdict is
     refused too: lm15 never drops a key it did not decide about.
   - **call-mode** — `stream` and `stream_options` say HOW a request is
     sent, not WHAT is asked; a `Request` has no stream flag
     (`stream=` is an argument of `complete()` / `stream()`). They are
     read and dropped. This bucket is closed at these two keys and is
     the only drop this rule makes.
   - **default** — a value equal to the wire's default reads as absent
     because the bytes an adapter would send are identical:
     `response_format {type: text}`, `function.strict: false`,
     `logprobs: false`, and a `json_schema.name` of exactly `"response"`
     (the builder's default label for an unnamed schema, MAP-8 rule 5).
3. **Rows.** The first row, when `system` or `developer`, is
   `Request.system` (a lone text block reads as the string form); a later
   `system` / `developer` row is a `developer` Message at that position.
   Consecutive `tool` rows form ONE tool Message (the builder writes one
   row per `ToolResultPart`; this is its inverse). An assistant row's parts
   come out in a fixed order — `reasoning_content` (ThinkingPart, a typed
   field, read on every preset), `content` (text / refusal blocks),
   `refusal`, `tool_calls` — and an assistant row with `content: null` and
   nothing else is one empty TextPart (MAP-2, applied to history).
   `tool_calls[].function.arguments` is `json.loads`-ed exactly; a string
   that is not a JSON object is malformed (the lenient parse of provider
   output, MAP-9's `parse_json_object`, is not used on caller input).
4. **Content blocks.** `text` → TextPart; `image_url` → ImagePart (a
   data URI becomes inline data with the URI's media type; another URL
   stays a URL with the media type guessed from its path, else the
   default — the wire carries none); `input_audio` → AudioPart
   (`audio/wav` | `audio/mpeg`); `file` → DocumentPart by `file_id` or by
   the `file_data` data URI (`filename` refused: no slot); `refusal` →
   RefusalPart. A `prompt_cache_breakpoint` on the system row's text
   block is `CacheConfig(prefix="stable")`; on the last text block of
   message N it is `prefix_until_index=N`; anywhere else it is malformed
   (the builder places it nowhere else). A block whose canonical part the
   chat BUILDER cannot carry back out (`input_audio`, MAP-10) still reads
   in: the Request is faithful and the SEND raises loudly — ingest is not
   where a wire gap is hidden.
5. **Nothing is parsed out of prose.** MAP-7 rule 12 applies in this
   direction too: a `[error] ` prefix on a tool row (MAP-10 rule 5) reads
   back as text with `is_error=false`; a `<think>` block reads back as
   text. Reversing a prose marker would be a guess.
6. **Malformed is not unsupported.** A wrong JSON type, a missing required
   key, an unparsable arguments string, two spellings of one knob that
   disagree (`max_tokens` ≠ `max_completion_tokens`; `user` next to
   `safety_identifier`) raise `ValueError` / `TypeError`, as serde does
   (INV-046). The contract pins refusals (rule 2) across ports; malformed
   input is a reference-test concern and its exception class is not pinned.
7. **The round trip is the test, and its lossy cells are pinned, not
   skipped.** For every chat-dialect wire case in the corpus (118 on
   2026-09-08, across ten doors), the harness `ingest` direction reads the
   recorded body back and requires `canonical_request` exactly — except
   where the WIRE lost information on the way out, in which case the case
   declares the class under `ingest.lossy` and pins what ingest DOES
   produce under `ingest.canonical_request`. The closed lossy vocabulary,
   each class wire-determined:
   - `thinking_as_text` — `compat.thinking_replay="as_text"` (decision G,
     MAP-7 rule 8) folds a ThinkingPart into assistant text; it reads back
     as a TextPart (rule 5).
   - `tool_result_name_omitted` — `compat.tool_result_name="omit"` drops
     `ToolResultPart.name`; the wire has no other slot.
   - `leading_developer_as_system` — the builder writes `Request.system`
     and a leading developer Message to the same instruction row; it
     reads back as `Request.system`.
   21 of the 118 cases carry a declaration (17 one class, 4 two — the xai
   tool-result cases). Adding a class is an additive change to this rule
   and to the registry's `lossy` table; `tools/audit.py` fails a
   declaration whose pin equals `canonical_request` (stale).
8. **Foreign shapes are pinned by ingest-surface cases**
   (`cases/<door>/ingest_*.json`, `surface: "ingest"`): the body, and
   either the hand-authored canonical request or the pinned refusal
   (`expect_lm15.raises {op: ingest_openai_chat}`). 38 on 2026-09-08,
   including the exact bodies DSPy's `ChatAdapter` produces (the first
   consumer).

9. **The reading side is the adapter's own reader, exposed** (added
   2026-09-08, `changes/2026-09-08-openai-chat-response-door.md`).
   `response_from_openai_chat(body, model=None, choice=None)` reads a Chat
   Completions *response* body — a server's, or a client library's
   imitation of one (litellm's `ModelResponse.model_dump()`, a cache
   entry) — into a canonical `Response` with the SAME reader
   `OpenAIChatLM.parse_response` runs on provider traffic. It therefore
   needs no verdict table and no new direction: what it maps and what it
   records as unmapped (`_lm15_unmapped`) are already pinned by the
   `response` direction over every recorded chat body, and the reference
   test suite requires the door and `parse_response` to agree byte for
   byte on each of them. The whole body is `provider_data`; a key the
   reader does not know is neither refused nor lost. An error envelope
   raises the typed provider error. `model` fills `Response.model` when
   the body carries none. **A body with more than one choice is refused
   unless `choice` names one** — a `Response` is one message, and reading
   `choices[0]` of three silently is the loss rule 2 refuses on the
   request side as `n`. This applies to `parse_response` too: before this
   date a caller who smuggled `n` through `config.extensions` got the
   first choice silently; now the adapter refuses at parse time. No
   `compat` parameter: the response shape does not vary by server the
   way the request shape does, and a parameter with no effect would
   misdescribe the function.

**What this rule does not do.** It does not turn a `Response` back into
a Chat Completions response body for serving behind an OpenAI-compatible
endpoint (a separate, later row, when a server on lm15 exists to need
it). It does not read streaming chunks. It does not read the Responses
API, Anthropic or Gemini formats; each would be its own rule with its
own verdict table if ever wanted. It does not add a `Request.from_*` or
`Response.from_*` constructor: the canonical types stay vendor-free; the
converters are dialect-module functions (`playbooks/api-family.md` rule 3).

**Why.** The DSPy integration (2026-09-08) needed `LMRequest.from_call(
model, messages, **kwargs)` — OpenAI-format messages in, canonical request
out — and every other litellm migration needs the same thing. Written in
DSPy it would be one converter per caller, each deciding silently what to
do with `n`, `name`, `input_audio` and a stray `thinking`; written once
here it is data-checked in every port. The verdict-registry pattern is
INV-049's (`tools/extensions-verdicts.json`): a mapping nobody decided is
an audit failure, not a hope.

---

History: MAP-1 and MAP-2 were implicit in the reference adapters; they were
ratified as written rules on 2026-06-10 after the adversarial golden review
flagged anthropic.container, openai.code_interpreter (MAP-1) and
gemini.max_output_tokens (MAP-2) — see
`lm15-contract/goldens/REVIEW-2026-06-10.md`. MAP-3 was written on 2026-06-10
after live vLLM/SGLang/ollama testing showed the multi-end merge losing usage.
MAP-5 was written on 2026-09-01 after a reasoning-off audit found four
adapters silently omitting the disable (see
`lm15-contract/changes/2026-09-01-reasoning-off.md`). MAP-6 was written on
2026-09-01/02 from the first design pass, MAP-7 and MAP-8 on 2026-09-02 from the second, third, and fourth (`lm15-contract/playbooks/design-pass.md`).
MAP-9 was first written on 2026-09-02 as a transcription of the
positional name guess that had lived in the accumulator since its first
version, then replaced the same day by the refusal rule after the
maintainer chose it over the guess
(`lm15-contract/changes/2026-09-02-stream-assembly-no-guess.md`).
On 2026-09-06 the ratification session added the MAP-3 `provider_data`
rule, MAP-7 rules 11–12 and the MAP-7.8 dialect sentence, and the
MAP-9.6 withheld-field list with INV-051
(`lm15-contract/changes/2026-09-06-decisions.md`,
`lm15-contract/changes/2026-09-06-ratification.md`).
MAP-10 was written on 2026-09-07 from the tool-result-content design pass
after the Rust port review probed a cell the corpus did not cover
(`lm15-contract/changes/2026-09-07-tool-result-content.md`).
MAP-11 was written on 2026-09-08 after the Rust port's surfaces probe found
both implementations interpolating ids raw into paths
(`lm15-contract/changes/2026-09-08-id-path-escaping.md`).
MAP-12 was drafted on 2026-09-08 when the DSPy integration needed
OpenAI-format messages read into a canonical Request and the alternative
was one silent converter per caller
(`lm15-contract/changes/2026-09-08-openai-chat-ingest.md`, pending).
