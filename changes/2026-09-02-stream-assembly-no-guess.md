# 2026-09-02 — Stream assembly never invents a tool-call name (MAP-9, proposed)

Ratification: PENDING — awaiting Maxime Rivest. The design was proposed in
session and accepted in principle ("I agree, this is really good, do that");
the stamp is the separate act, as for MAP-6 to MAP-8. Do not push before
ratification.

## What this changes

Three things, one of them structural for the harness:

1. **The rule.** When a stream's tool-call fragments for one part index
   never carry a name, the assembler raises `StreamAssemblyError` (new
   ErrorCode `stream_assembly`, direct child of `LM15Error`). The error
   carries `partial` — the Response assembled from everything else that
   arrived, with the unnamed call(s) left out — and `part_index`. Before,
   the accumulator guessed: one declared tool, else the tool at the part's
   rank among all parts, else the literal `"tool"`. A text part before the
   call shifted the guess; an agent loop dispatching on it ran the wrong
   function with no error.
2. **A minted id stays.** A missing call `id` becomes `tool_call_<index>`:
   an lm15-owned correlator (Gemini sends none), stated, not a guess.
3. **Goldens can pin a raise.** `expect_lm15.raises {type, code}` on a
   case; golden `{"error": {type, code}, "partial_response"?, "events"?}`;
   the shim's error reply gains `code`, `partial_response`, and (for
   `replay_stream`) `events`. The harness fails a case that answers
   `ok: true` where a raise is pinned. Until now the three MAP-8 raises
   and every other refusal lived only in the reference's unit tests, which
   no port runs; this is the mechanism that makes a refusal portable.

## Why raise, and why carry the partial

- An unnamed call is not actionable (MAP-1). Making `name` optional would
  push a null check into every consumer in five languages.
- Every shipped dialect names a call on its first fragment (OpenAI Chat in
  the first delta, Responses in `output_item.added`, Anthropic in
  `content_block_start`, Gemini in the whole `functionCall` part). A missing
  name is an adapter defect. The guess hid the defect and turned it into a
  wrong dispatch; the raise names the adapter as the fix.
- Keeping "one declared tool" as a safe guess was considered and rejected:
  nearly safe is still a guess, and it still hides the defect.
- The partial exists on the MAP-3 principle: never fabricate, never
  discard what arrived. A stream may have produced a page of text before
  the bad call.

## Evidence

- New case `openai_chat.tool_call_unnamed`: a hand-built degraded
  OpenAI-compatible stream (chunk shape from the Groq capture
  `bodies/openai_chat.streaming/2026-06-10T19-18-23Z.txt`; tool call with
  `id` and `arguments`, no `function.name`). Its golden pins the raise, the
  salvaged partial (`"Checking."`, usage 48/11/59, finish `tool_call` as
  the provider reported it), and the six-event trace. Wire request generated
  by the reference; request direction green.
- lm15-python: five MAP-9 tests (raise with one declared tool; partial
  carries text and usage; named calls still assemble and a missing id is
  minted; a name on any fragment suffices; `ResponseStream` raises at end
  of iteration with text already yielded). 953 tests green.
- Harness: 13/13 directions green (stream now 10). Selftest: 24 mutations
  caught, including the new `assembly_guesses_name` (the pre-MAP-9
  behaviour answered with a Response → CAUGHT "expected raise
  StreamAssemblyError; shim returned a response").
- spec_drift green after `stream_assembly` and the class entered
  spec/vocabularies.md; audit, provenance, secrecy green.

## Stated trade-offs

1. `partial.finish_reason` is the provider's word (`tool_call`) even though
   the partial holds no call. Kept as reported; the caller holds the error.
2. The pinned case is synthetic, marked `hand-authored` with the shape's
   source cited. No provider produces this stream today; that is the point.
3. Error messages are not pinned across ports; only class and code are.
4. The harness now has two golden shapes (`canonical_response` vs `error`).
   One key decides which comparison runs; the scribe drafts both.

## Follow-up (not in this entry)

The three MAP-8 raises (xAI allowlist, Gemini `parallel=false`, xAI forced
tool with `response_format`) and Anthropic `json_object` can now be pinned
as request-direction raises with the same mechanism. The request direction
does not yet read `expect_lm15.raises`; that is a separate, mechanical
change and should land with its four cases.
