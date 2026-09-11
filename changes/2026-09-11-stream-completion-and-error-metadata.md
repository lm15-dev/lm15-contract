# 2026-09-11 — Stream completion is strict; a complete Response is never withheld; HTTP error metadata from headers

Ratification: PENDING — drafted 2026-09-11 from three Python commits that
landed on `main` this week without a contract entry (`9cac603`, `acb8090`,
`9d764b2`, and their correction in the commit that cites this file). The
maintainer's direction in session: "go implement your plan most
excellently", after the review that found one of the three behaviours
wrong (below, § 2). Python is the reference for all of it; Rust and
TypeScript are ported in the same batch. Nothing here is a provider wire
fact; it is consumer-side behaviour the family must share.

## What this changes

### 1. `stream_assembly` covers two more defects (MAP-3 on the consumer side)

`spec/vocabularies.md` § ErrorCode: `StreamAssemblyError` is raised by the
stream-to-Response wrappers (`materialize_response`, `ResponseStream`, and
their async mirrors) when:

- **the stream ended without an end event.** Before this date the reference
  returned a `Response` with `finish_reason=None` and `usage=None` and
  called it success. A dropped connection looked like a finished turn: the
  silent degradation the family forbids. `partial` carries what did
  assemble.
- **an event arrived after the end event.** MAP-3 says the end event is
  final. Material after it has no place in the Response; dropping it would
  be silent loss, merging it would be invention. `partial` carries the
  complete Response as it stood at the end event.

Both are source defects (an adapter, a coalescer, or a caller-built event
source), never model behaviour — every shipped dialect ends exactly once
after coalescing — so the message points at the source, as MAP-9's does at
the adapter.

### 2. A failure AFTER the end event never withholds the Response

Once the end event has been yielded, the Response is complete and the
provider has billed the turn. Two things can still fail: the source can
raise while the wrapper drains it to exhaustion (checking for trailing
events), and the source's `close()` can raise.

**Rule:** neither replaces the Response. The wrapper returns the Response
unchanged, reports the failure through the language's warning/diagnostic
channel, and — where a stream object exists — records it on that object
so a caller can read it programmatically. It is never raised from the
response accessor.

- Python: `warnings.warn(..., StreamCleanupWarning)` (a `RuntimeWarning`
  subclass; a caller who wants it fatal runs `-W
  error::lm15.errors.StreamCleanupWarning`), and
  `ResponseStream.cleanup_errors` / `AsyncResponseStream.cleanup_errors`.
- Rust and TypeScript: the idiomatic equivalent (below, § Ports).

**Before this rule** (Python `9d764b2`, one day on `main`): such a failure
was re-raised as `StreamAssemblyError` with the *complete* Response in
`partial`. The motive was sound — an error after completion must never
drive a retry that re-bills — but the effect was to hide a finished,
billed answer behind an exception over a socket's afterlife, and to call a
complete Response "partial". Returning the Response satisfies the motive
more simply: no error, no retry.

**Boundary, stated precisely.** "After the end event" means the wrapper
has *yielded* the merged end event. The coalescer (MAP-3) emits that event
only once the raw source is exhausted, so a read failure on the raw source
— even after a `finish_reason`-bearing frame — happens BEFORE completion:
the terminal frames may be incomplete (the usage chunk, `[DONE]`). That
stays what it is (a retryable `TransportError`, or whatever the source
raised), with nothing warned. This is pinned by
`lm15-python/tests/test_error_metadata_and_completion.py`
(`drain-coalesced`).

**Cleanup on a stream that is closed unfinished** (the caller's
`close()`/`aclose()` on a stream with no Response yet) is unchanged: a
`close()` that raises propagates to the caller, who asked for it.

### 3. HTTP error metadata: headers fill what the body did not say

`spec/vocabularies.md` § Error metadata:

- **`request_id`.** When the provider's error body carries no request id,
  the adapter reads the first present of these response headers, in this
  order: `x-request-id`, `request-id`, `x-amzn-requestid`,
  `x-amz-request-id`, `x-ms-request-id`. A body value is never replaced.
  Nothing is invented: absent in both stays absent. (OpenAI and xAI send
  `x-request-id`; Anthropic `request-id`; Bedrock `x-amzn-requestid`;
  Azure `x-ms-request-id`.)
- **`retry_after`.** A body-derived value wins when it is a finite,
  non-negative number of seconds. Otherwise the `Retry-After` header fills
  the gap: delta-seconds, or an HTTP-date measured from now (never
  negative). A hint that is not finite, is negative, or does not parse is
  DROPPED, not stored: an infinite or NaN `retry_after` becomes an
  infinite sleep in the first caller that trusts it.
- These apply on **every** path that can produce a `ProviderError` from an
  HTTP reply: complete, stream (the pre-body error), and the auxiliary
  endpoints (files, batches, caches, model listing, image / speech / video
  generation). Python `9cac603` and `acb8090` fixed the async and
  auxiliary paths, which had been dropping `Retry-After` (lm15-python
  issues #6 and #7, reported by a user).

## Why this is contract, not a Python detail

The family's promise is that the same stream produces the same outcome in
every language. "A stream with no end event is an error" versus "is a
Response with no usage" is a different outcome; so is "the response
accessor throws after a close failure" versus "returns". A caller who
ports between languages must not discover these by surprise. The header
list for `request_id` is a wire fact about five providers that every port
would otherwise re-derive.

## Considered and rejected

- **Keep the Python `9d764b2` behaviour** (post-completion failure raises
  with the Response in `partial`). Rejected: withholds a billed answer;
  misnames a complete Response; and a caller that wants non-retryable
  semantics gets them more simply from "no error".
- **Silently ignore post-completion failures.** Rejected: an unhealthy
  connection is a fact the caller may want (pool hygiene, monitoring). The
  warning channel is the honest, non-blocking place for it.
- **A new ErrorCode for "ended without end event".** Rejected: the failure
  the caller acts on is the same as MAP-9's — "this stream cannot become a
  Response without inventing a fact"; the fix is the same (fix the source);
  `partial` carries the same salvage. One code, three named causes.
- **Stop reading at the end event instead of draining** (the pre-`9d764b2`
  behaviour). Rejected: trailing events would go undetected; for every
  coalesced source the drain is free (the coalescer has already exhausted
  the raw source before it emits the end event).

## Evidence

- Not a wire exchange; no harness direction drives it. Each implementation
  pins it in its test suite: `lm15-python/tests/test_error_metadata_and_completion.py`
  (missing end, trailing event, close/drain failure after completion under
  one-shot / ResponseStream / coalesced, sync and async; header-derived
  request ids on complete/stream/list_models; invalid hints),
  `tests/test_retry_after_parity.py`, `tests/test_auxiliary_retry_after.py`.
- `tools/spec_drift.py` unchanged: no new code, no new class.

## Ports

- Rust: `ResponseStream` / `materialize_response` refuse a stream with no
  end event and a trailing event (`Lm15Error::StreamAssemblyError` with
  `partial`); a post-completion failure is reported via `tracing::warn!`
  (or `log::warn!`, whichever the crate uses) and exposed on the stream
  object; `attach_error_metadata` reads the header list above.
- TypeScript: the same on `ResponseStream` / `materializeResponse`;
  post-completion failures via `process.emitWarning` and
  `stream.cleanupErrors`; `attachErrorMetadata` reads the header list.

## Trade-offs, stated

- A warning is weaker than an exception: a caller who never looks at
  warnings will not notice an unhealthy connection. Accepted: the answer
  they asked for is intact, and the warning can be made fatal per process.
- The wrappers drain the source after the end event. For every shipped
  dialect this costs nothing (the coalescer has exhausted the source); a
  caller-built source that keeps yielding after its end will now be
  refused where it was previously tolerated.
- The header list is ordered and fixed; a proxy that sets `x-request-id`
  in front of a provider that uses `request-id` will win. Accepted: the
  body wins whenever the provider put the id there, which the five named
  providers do on their own error shapes.
