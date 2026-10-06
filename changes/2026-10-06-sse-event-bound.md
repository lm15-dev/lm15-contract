# 2026-10-06 — A stream takes any event a complete reply would (INV-056)

**Status: DECISION (maintainer, in session 2026-10-06: "yes, fix that
completely") + normative rule INV-056 in `spec/invariants.md`, not yet
ratified. Wire evidence: live receipts below.**

## The finding

A user's pilot run (statlm, 2026-10-06) lost a 26-minute OpenAI reading at
its last event: `TransportError: SSE line exceeds limit (68021 > 65536)`. The
answer had been generated and billed; lm15 refused the line that carried it.

Every SDK had the same two limits, none of them a decision: the reference's
`parse_sse(max_line_bytes=64 * 1024, max_event_bytes=1024 * 1024)`, copied
into TypeScript, Rust, Go and Julia; R had 1 MiB / 8 MiB. 64 KiB is the
default token size of Go's `bufio.Scanner`, a limit known for exactly this
failure. No contract text named a limit, no case carried a line over 64 KiB,
and the harness's `replay_stream` direction feeds the shim's own parser, so
the corpus could not see it.

The same SDKs read a non-streamed reply of any size (`resp.read()` in
Python, `io.ReadAll` in Go): the limit existed on one path only. (R's
transport bounds a whole reply at 128 MiB on both paths; see below.)

## What the servers send (receipts/2026-10-06-sse-long-lines)

`research/providers/sse_long_lines.py --probe`, request built by the
reference adapter, sent verbatim, measured line by line:

| Probe | Model | Longest line | Where |
|---|---|---|---|
| responses-instructions: 72 KB system prompt, one-word answer | gpt-4.1-mini | 75,859 B | `response.created`, `response.in_progress`, `response.completed`: each repeats the whole response object, `instructions` included |
| responses-image: `image_generation` tool, high, 1536x1024 | gpt-4.1-mini | 4,170,031 B | the image in `response.output_item.done`, and again in `response.completed` |
| gemini-image-4k: `imageSize: 4K` (the one raw patch) | gemini-3-pro-image | 29,674,245 B | the whole image in one `data:` line |

So a Responses stream fails on a long system prompt before any output, and
on a long answer after all of it (the user's case: `response.completed`
repeats the full text). The image probes' bodies (8.4 MB, 29.7 MB) are not
kept in the repository; their exchange receipts record the request and the
response hash and size, and `probe-*-sizes.json` the per-event-type line
lengths. The 72 KB probe's body is kept verbatim.

What other SDKs do, read from installed sources: openai-python 3.19.2
`SSEDecoder` ("Decode SSE incrementally without imposing a line or event size
limit"); openai-go v3.61.0 and anthropic-sdk-go v1.72.0 raise `bufio.Scanner`
to `MaxScanTokenSize<<9` (32 MiB), 10% above the Gemini 4K line.

## Decided

- **No default limit on a line or an event (INV-056).** Considered and
  rejected:
  - *Raise the limits* (to 32 MiB like the Go SDKs, or 64 MiB). Any number is
    a guess the next image size breaks: the measured 29.7 MB is one image;
    a response with several, or a larger size, crosses it. And the limit
    bounds nothing: every SDK accumulates the stream into the whole
    Response, so a server can make an SDK hold as much as it sends with
    lines of any length. It only refuses replies, and only on the streaming
    path, which INV-051 says must yield what the complete call does.
  - *A configurable limit on every client.* New API surface in six SDKs for
    a knob whose only safe default is "off". If a memory bound is wanted it
    is a bound on the whole reply, applied alike to complete and stream
    calls; for the contract that is a separate decision, not made here.
    R's `transport_curl` already has exactly that (`max_response_bytes`,
    128 MiB by default, counted over every chunk of a complete or a
    streamed reply); INV-056 keeps it.
  The low-level parsers keep their caps as opt-in parameters where an SDK
  exposes them (Python `parse_sse(max_line_bytes=, max_event_bytes=)`,
  TypeScript `SseLimits`, Rust `SseLimits` with `usize::MAX` meaning none,
  Julia keywords with `nothing`, Go's internal `Limits` with 0). Going over a
  cap the caller set is still `TransportError`.
- **Line splitting is linear.** Without a limit, a 30 MB line arrives in
  about 1,900 reads; four SDKs searched (and TypeScript and R re-copied) the
  whole pending line after every read. Measured on the old code: Python
  3.5 s for a 30 MB line, TypeScript 1.8 s for 4 MB, R 2.7 s for 4 MB, Julia
  3.1 s for 30 MB (per-byte bookkeeping), all but Julia growing with the
  square of the line. Now each byte is searched once and a line is joined
  once: 30 MB in 0.2 s (Python), 0.3 s (TypeScript), 0.15 s (Go), 0.5 s
  (Julia), 1.3 s (R).
- Line grammar is unchanged (which terminators each SDK accepts differs:
  Julia also ends a line on a bare CR; the others on LF, stripping one CR).
  Not in scope here.

## Case (live capture, wire built by the fixed reference adapter)

`cases/openai/streaming_long_line.json` (gpt-4.1-mini, Responses, stream):
a bilingual field-guide system prompt of 1,000,022 characters (1,091,898
bytes of UTF-8; OpenAI caps `instructions` at 1,048,576 characters, receipt
`failed-streaming_long_line-2026-10-06T16-10-39Z.txt`, so the line needs
characters wider than a byte to pass 1 MiB) and "Reply with the single word
OK." The stream's three echo lines are 1,100,381 / 1,100,385 / 1,100,760
bytes: each over both former limits, so one case pins both. The golden is a
scribe draft (`goldens/openai/streaming_long_line.json`), not reviewed.

Stated cost: the case is 2.2 MB, its body 3.3 MB and its golden 1.1 MB (the
prompt appears in each); the text is highly regular and compresses about
tenfold in git. A first capture pair (the 72 KB prompt, and a
`gemini-2.5-flash-image` stream whose image line is 2,667,905 bytes) was
captured and then not committed as cases: the Gemini pair would have added
about 11 MB of incompressible base64 (the reference's golden writes the image
three times) and the 72 KB stream pins only the smaller limit. Their exchange
receipts stay (`exchange-2026-10-06T16-07-07Z-*`, `16-07-10Z-*`).

What the case does not pin: line splitting across network reads. The
harness hands a shim the whole body at once; the chunked path and its
linear time are pinned by each SDK's own tests.

## Implementations

Each SDK moves its pin to this commit with the fix: Python, TypeScript,
Rust, Go, Julia, R. Java, Ruby, .NET and Swift (pinned at `cfed007`) have
the same limits and are not changed here; see `playbooks/parity.md`.
