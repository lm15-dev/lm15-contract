# 2026-11-05 — A stream's final copy completes its fragments (MAP-20); stream checks that need no hand-written answer

Ratification: RATIFIED 2026-11-05 — Maxime Rivest, in session ("i
approve"), after the change was implemented, passed 2,132 of 2,132 checks
in all six SDKs and was released as 2.1.0. Transcribed.

**Status (when written): DECISION (maintainer, in session 2026-11-05: "ok perfect, go do it
completely and most excellently", on the plan below) + normative rule MAP-20
in `docs/mapping-rules.md`, the INV-051 amendment in `spec/invariants.md` and
the `stream_assembly` row in `spec/vocabularies.md`, ratified the same day (above). Wire
evidence: live receipts below.**

## The finding

A user's coding agent (figurer, a chart-reading agent on
`openai-codex:gpt-6.1-sol` through the Codex subscription login) reported:
"When Sol asks for several tool calls at once, they all arrive with empty
inputs. The server sends the inputs, but lm15 only reads them from partial
messages, and the server sends none in that case." It worked around it with
`ToolChoice(parallel=False)`.

Confirmed live the same day (`receipts/2026-11-05-stream-final-copy/openai-codex/`):

| Codex stream | Fragments (`*.delta`) | Final copies | lm15 before |
|---|---|---|---|
| two parallel calls | **none** | `function_call_arguments.done` and `output_item.done` per call | both calls `{}` |
| one call | 5 `function_call_arguments.delta` | the same two | right |
| text | `output_text.delta` | `output_text.done`, `content_part.done`, `output_item.done` | right |

Every SDK built a call's input from `output_item.added` and
`function_call_arguments.delta` only, so the six SDKs failed the same way;
on Codex `complete()` materializes the stream, so both calling styles did.
The accumulator then read "no input arrived" as `{}`, a valid-looking call.

Why the corpus did not see it: no pinned stream had two calls, none had an
item whose value arrived only in its final copy, and every stream check
compared an SDK with a golden scribed from the reference
(`tools/scribe_goldens.py`), so the reference's blind spot was the corpus's.

## What a stream's own words prove (the new checks)

An OpenAI Responses stream ends by restating the whole response
(`response.completed`). INV-051 already said the stream's Response equals
the complete call's; nothing checked it. Three checks now do, in the
`stream` direction and the corpus tools (PROTOCOL.md § Stream checks):

1. **`<case>~final-copy`** — the harness sends the final copy to
   `parse_response` and requires the stream's Response to equal it. It
   needs no golden: it failed the Codex case with nothing a person wrote.
2. **Stream variants** — legal re-shapings of every pinned stream, which
   must assemble to the case's own outcome: `split` (fragments cut at other
   boundaries), `merge` (consecutive fragments joined), `rechunk` (a
   Gemini chunk's parts one chunk each), `final-only` (Responses: every
   fragment of a restated item dropped, the Codex shape), and `contradict`
   (Responses: one fragment changed, which must be refused).
3. **`tools/check_stream_events.py` + `mapping/stream-events.json`** —
   every event type, delta type, part key and chunk key a pinned stream
   carries (77 kinds across four dialects) is classified read, duplicate
   (of what) or ignored (why); a new kind fails until someone decides it.
   `function_call_arguments.done` had been ignored as if it duplicated the
   fragments; it was the only carrier of the arguments.

The checks were run against the SDKs as they were (stream direction):

| | Python | TypeScript | Go |
|---|---|---|---|
| before | 163 pass, 38 fail | 163 pass, 42 fail | 163 pass, 42 fail |
| after | 205 / 205 | 205 / 205 | 205 / 205 |

Rust, Julia and R were changed before a baseline was taken; all six reach
205 / 205. `harness/selftest.py` gains four mutations (a final copy
ignored, a contradiction assembled, a stream that differs from its final
copy, assembly that depends on where fragments were cut); each is caught.

## What the checks and the probes found besides

The new checks failed the reference on a second pinned shape, and live
probes for parallel calls on every dialect found two more. All four are
the same promise broken (a stream must yield what the provider said):

- **Reasoning summaries ran together.** The complete path joins a reasoning
  item's summary parts with `\n`; the stream concatenated their fragments
  with nothing between (`**First idea****Second idea**`). Pinned by
  `openai-codex.streaming_reasoning_summary` (13 parts over 6 items).
- **A Responses stream cut short by the output limit lost its ending.** It
  ends with `response.incomplete`, not `response.completed`; four SDKs
  (Python, TypeScript, Rust, Go) ignored it. Where the server then closes
  without `[DONE]` (OpenAI, Azure, Codex, Moonshot) the stream had no end
  event and raised `StreamAssemblyError` (MAP-3) for a turn that ended
  normally; where it sends `[DONE]` (Meta) the turn ended `stop` with no
  usage instead of `length` with its usage. Julia and R already read it.
  Pinned by `meta.streaming_incomplete` (Meta's Responses wire,
  `max_output_tokens` 40).
- **Gemini parallel calls in separate chunks ran into one input.**
  gemini-2.5-pro and gemini-3-flash-preview send each parallel call in a
  chunk of its own (gemini-2.5-flash sends them in one). Every SDK gave a
  part its index within its chunk, so every call landed in slot 0 and their
  arguments concatenated (`{"partial_json": "{\"city\":\"Paris\"}{\"city\":\"Oslo\"}"}`);
  the complete path was right. Pinned by
  `gemini.streaming_parallel_tool_calls_chunked` and the `rechunk` variant.
- **The realtime completion path counted a call's arguments three times.**
  A realtime model called with `complete()`/`stream()` (Python and Go; R
  already completed from the final copy, the rule below) mapped
  `output_item.added`, each delta, `function_call_arguments.done` and
  `output_item.done` all as input fragments, and named a call `"tool"` when
  a frame carried no name (MAP-9 forbids it). Found by replaying
  `receipts/2026-09-01-live/openai-ga-full-frames.json`; pinned by unit
  tests in each SDK (the harness drives no WebSocket path).

## Decided

- **MAP-20** (`docs/mapping-rules.md`): at an item's final copy the reader
  emits what the fragments did not deliver — all of it, the rest, or
  nothing; fragments that are not its beginning are refused with
  `StreamAssemblyError` / `stream_assembly` and the item's `part_index`.
  OpenAI Responses (and Realtime): `response.output_item.done` is the one
  final copy read, for function-call arguments, message text and reasoning
  summaries; the per-run `.done` events duplicate it. Anthropic, Chat and
  Gemini have no final copy.
- **One stream reader per stream, in every SDK**: Python
  `BaseProviderLM.stream_reader(request)` (`StreamReader.feed`),
  TypeScript `ProviderLM.streamReader(request)` (exported `StreamReader`
  type), Rust `Dialect::stream_reader` / `wire::StreamReader`, Go an
  unexported reader behind `ParseStreamBody` and `Stream`, Julia
  `stream_reader` / `feed!`, R `.new_stream_reader`. The per-event mapping
  stays per event and a subclass's override of it is still used.
- **Arguments compare as JSON when their text differs**: the same value,
  object members in the same order (INV-002), is not a contradiction.
  Members in another order are: which order the model meant is a fact
  lm15 would otherwise choose.
- **The summary newline is emitted before the first fragment of each later
  part** (`summary_index`), so a streaming caller sees the same text the
  complete call returns, and a part with no fragment is completed from the
  final copy, newline included.
- **A Gemini part's slot is its place in the stream**: the first part of a
  chunk continues the previous chunk's last part when both are text (or
  both thought text); every other part opens the next slot.
- **`response.incomplete` ends a Responses stream** with the complete
  path's finish reason (`length`, `content_filter`) and its usage.

Considered and rejected:

- *Read only the final copies.* Simpler, and safe against double counting,
  but a streaming caller would see no argument or text until each item
  ends. Fragments stay the preview; the final copy completes them.
- *Read `response.completed` instead of each `output_item.done`.* One
  place for everything, but content would reach a streaming caller only at
  the very end, and `response.completed` on some servers carries no output.
  The harness reads it to check INV-051; readers read the per-item copy.
- *Trust the final copy when fragments disagree.* It is the provider's last
  word, but the fragments were already handed to a streaming caller; the
  Response would then say something the caller never saw. No live stream
  has disagreed; if one does, it is refused, not resolved.
- *A new delta field ("this fragment is the whole value").* It would let
  the accumulator replace instead of append without a reader, but every
  streaming consumer that prints deltas would print the value twice. A
  contract type change for a reader-local problem.
- *An interleaving variant* (fragments of two calls alternating). No
  provider was seen to interleave; a variant for an unobserved shape could
  fail an SDK for nothing. Added when a receipt shows it.

## Cases (live captures, wire built by the reference adapter)

`research/providers/parallel_tool_calls.py` (one weather tool, "call the
tool for both cities at once, in parallel"; a case is written only when the
provider's own body holds two or more calls):

| Case | Model | What it pins |
|---|---|---|
| `openai-codex.streaming_parallel_tool_calls` | gpt-6.1-sol | two calls, arguments only in final copies |
| `openai-codex.streaming_tool_call` | gpt-6.1-sol | one call, fragments then final copy |
| `openai-codex.streaming` | gpt-6.1-sol | text; the Codex door had no stream case |
| `openai-codex.streaming_reasoning_summary` | gpt-6.1-sol, effort high, summary detailed | 13 summary parts joined with newlines |
| `meta.streaming_parallel_tool_calls` | muse-spark-1.3 | Responses wire, fragments and final copies |
| `meta.streaming_incomplete` | muse-spark-1.3 | `response.incomplete`, finish `length` |
| `moonshotai-responses.streaming_parallel_tool_calls` | kimi-k3 | Responses wire with reasoning and text |
| `anthropic.streaming_parallel_tool_calls` | claude-haiku-4-5 | two `tool_use` blocks |
| `gemini.streaming_parallel_tool_calls` | gemini-2.5-flash | two calls in one chunk |
| `gemini.streaming_parallel_tool_calls_chunked` | gemini-2.5-pro | two calls, one chunk each |
| `deepseek.streaming_parallel_tool_calls` | deepseek-v4-flash | Chat Completions, two `tool_calls` indexes |

Their goldens are scribe drafts from the fixed reference; for the four
Codex and two Meta/Moonshot Responses cases, `~final-copy` checks them
against the provider's own final copy.

The Codex bodies are verbatim except each `"safety_identifier"` value (a
per-account pseudonym the server echoes), replaced by `"user-REDACTED"`;
the exchange receipts' `response_sha256` is of the bytes as received. The
wire pins `chatgpt-account-id: test-account` (PROTOCOL.md), never the real
account id.

Not a case: OpenAI's own API answered HTTP 200 with an in-stream
`insufficient_quota` error (the account had no credits); the body is
`receipts/.../openai/not-parallel-…txt` (the capture script's word, before it
learned to say "failed": it is a failure body, not a single-call stream).
The first `SUMMARY` of the Codex single-shape run was deleted with a
malformed retry row before any commit; their exchange receipts stand.

Cost: 7 metered calls (fractions of a cent each), 4 calls on the Codex
subscription, 3 Gemini probes.

## Not covered (stated; each predates this change, none is in a pinned stream)

- A message item's annotations are not completed from its final copy
  (they stream as whole `annotation.added` events).
- `reasoning_text` content streams as thinking; the complete path reads
  only the summary.
- A Responses message with several content parts is one TextPart on the
  stream, one per part on the complete path.
- A streamed refusal is text (there is no refusal delta); the complete
  path makes a RefusalPart.
- Gemini `groundingMetadata` is read by the complete path only
  (`gap` in `mapping/stream-events.json`, which fails the day a pinned
  stream carries it).
- Julia maps `response.failed` to a second error event after `error`; the
  others ignore it as a duplicate. Same outcome (the first error raises).

## Implementations

Python, TypeScript, Rust, Go, Julia and R move their pin to the commit
that carries this entry and release 2.1.0 (a minor release: new reader
API in three SDKs, new behaviour in all six, nothing removed or changed in
meaning; `playbooks/api-family.md` rule 8 keeps minor numbers per SDK, and
all six take the same one so a reader of the release notes sees one
change). Java, Ruby, .NET and Swift (pinned at `cfed007`) are not changed;
see `playbooks/parity.md`.
