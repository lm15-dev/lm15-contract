# 2026-09-11 — Gemini `streamGenerateContent` answers 200 with an empty body when thinking eats the token budget

Status: FINDING (wire fact, live). No contract change proposed; the
2026-09-11 stream-completion rule already gives it the right outcome.

## What was observed

`POST /v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse` with
`generationConfig.maxOutputTokens: 20` on the prompt "Reply with the single
word: pong": in roughly one call out of three the server answers
`HTTP 200`, `Content-Length: 0`, no SSE frame at all. The other calls
answer one frame with the text and a final frame with
`finishReason: MAX_TOKENS` (usage: 8 prompt, 1 candidate, 15 thoughts —
the budget is consumed by thinking).

Reproduced with raw `curl` (2 of 4 calls empty), on fresh connections and
on lm15's pooled connections alike, so it is the server, not the client.
With `maxOutputTokens: 200` it did not occur (0 of 6). The non-streaming
`generateContent` never returned an empty body (0 of 8 at 20 tokens): it
answers a body with `finishReason: MAX_TOKENS` and no parts.

Session: found while running the live core loop against the reference at
`lm15-python` 1d55420 before judging 1.0 readiness.

## What lm15 does with it

Before `changes/2026-09-11-stream-completion-and-error-metadata.md`, the
reference's `ResponseStream` / `materialize_response` returned a
`Response` for this stream: empty text, `finish_reason="stop"` (MAP-9
rule 5: `None` becomes `stop`), no usage — a finished turn that never
happened. Since that rule, the wrappers raise `StreamAssemblyError`
("ended without an end event", `partial` = an empty Response), and the
raw event iterator yields nothing. That is the correct outcome and needs
no adapter change: the provider sent no fact to map.

## Open question, not decided

Whether a stream with zero frames deserves its own wording ("the provider
closed the stream without sending any frame; HTTP 200, empty body") so a
caller can tell a truncated stream from an empty one. The class would stay
`stream_assembly`. Left for a later pass; the message today is truthful.
