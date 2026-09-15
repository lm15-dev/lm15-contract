# Bounded live-turn collection

Status: RATIFIED — Maxime Rivest, 2026-09-15, in session: “run the test and
I'm ratifying”, after the implementation summary named the 16 MiB / 10,000-event
defaults, configurable limits, partial-data preservation, open-session behavior,
and new `collection_limit` error code. Implementation had been authorized
in the preceding request. This ratification does not cover unrelated proposals.

## Problem and scope

The 2026-09-11 shared-handle decision intentionally retains all consumed events
in TurnView, including events already yielded. A peer that never emits a turn
boundary can therefore grow that collection indefinitely. Retention remains
part of the API: silently deleting old events would break result()/snapshot().

This change bounds the consumer's turn collection, not the whole live session,
WebSocket frame size, network buffering, process memory, or elapsed duration.
It does not spool conversations to disk or synthesize a provider end event.

## Shared policy

- Each turn view has `max_bytes=16777216` (16 MiB) and `max_events=10000` by
  default. Either budget can be increased/decreased per view. Both are positive
  finite integers; booleans, zero, negatives, fractions and null are rejected
  before reading. Raw session iteration remains the deliberate no-collection
  alternative; no unlimited collector mode is introduced.
- The byte charge is the length of each accepted canonical live-server event
  serialized to compact ASCII JSON: no optional whitespace, separators `,` and
  `:`, quotes/backslashes escaped, standard short control escapes, other control
  and non-ASCII code units escaped as `\uXXXX` (surrogate pairs for supplementary
  characters), `/` unescaped. Omission and number rules are the existing
  canonical serde rules. Count the entire event, including keys, metadata,
  tool input, error details and base64 audio, not just text or decoded audio.
  No separator is counted between events. Object key order does not affect size.
- Equality fits. Every accepted event counts, including empty text, usage,
  tool-call fragments and terminal events. A terminal event must also fit.
- Before receiving another event, if the event-count cap has been reached,
  fail without consuming that next event. No speculative read to look for an end.
- Otherwise receive one event, determine whether its byte charge fits, and only
  then append/count/yield it. Counting may stop once overflow is established;
  do not build another serialized copy of the entire history.
- On overflow raise a local, non-retryable `CollectionLimitError`, code
  `collection_limit`. It is not a provider error, network fault, or completed
  turn. No HTTP status, fabricated usage, automatic retry, interrupt, close,
  drain, or further receive is performed.
- The failure carries the breached limit name, configured maximum, retained
  byte/event counts, and all accepted `partial_events`. A byte overflow also
  carries `rejected_event`: the received event that could not fit, neither
  yielded nor included in partial_events. A count overflow has no rejected
  event because it performed no receive. Never include payload text in the
  error message. These are local error attachments, not fields in ErrorDetail.
- The view is sealed after failure. Further next/result calls raise the same
  failure without reading more, even after close(). snapshot()/error.partial
  materialize accepted events on demand with ended_by=incomplete and ok=false,
  even if the last accepted event happens to be a tool call. Error construction
  itself must not concatenate text or decode/copy accumulated audio. If prior
  payloads cannot be materialized (e.g. malformed audio), partial_events remains
  available without decoding.
- The underlying session remains open, under application control. For recovery,
  process rejected_event first (when present), then use raw session reads to
  continue or drain deliberately to an actual boundary; or explicitly interrupt
  or close the session. A fresh view at this point is a continuation fragment,
  not a magically restarted full turn. Closing a view still does not close the
  session. Dropping an exception discards its rejected event by caller choice.
- Existing successful result() semantics remain: stop at a tool call, leave
  following events for the next view, and return the same cached Turn on repeat.
  Async cancellation and non-limit source errors retain their existing behavior.

## Defaults and trade-offs

16 MiB is a round conservative payload budget for an explicitly buffering
convenience, not a measured percentile. For illustration, 24 kHz mono 16-bit PCM
requires about 3.84 MB/minute after base64 encoding, before event overhead;
16 MiB allows roughly four minutes on the byte budget alone. 10,000 events
allow roughly three minutes at 50 events/second. Actual formats and chunk rates
vary. Long legitimate turns may need larger limits or raw reading.

- This bounds accumulated data, not exact resident memory. Language objects,
  materialized text/audio, concurrent views, transport buffers and any rejected
  event cost additional memory. A single oversized incoming event is already
  allocated before collection can inspect it and is retained on the exception
  for recovery; message-size protection belongs to the transport separately.
- Keeping the rejected event avoids silent content loss but temporarily retains
  one more event outside the accepted-data budget. Applications should process
  or release it rather than keeping exceptions indefinitely.
- Re-serializing each event for a predictable byte charge adds CPU work. It uses
  the existing canonical serializer instead of a second list of payload fields
  that could forget tool inputs, errors or future variants. No new dependency.
- At an exact event cap, the next event might have ended the turn. We still stop
  before reading it: a cap is a cap, and the application can recover via raw reads.
- The additional public error code must propagate to ports; no cross-language
  parity or test success is claimed by writing this rule.

## Python usage

```python
from lm15 import CollectionLimitError

view = session.turn(max_bytes=32 * 1024 * 1024, max_events=20_000)
try:
    turn = view.result()              # async: await view.result()
except CollectionLimitError as error:
    events_so_far = error.partial_events
    event_that_did_not_fit = error.rejected_event
    # Choose explicitly: process these, continue raw reads, interrupt, or close.
    # error.partial / view.snapshot() assemble the partial Turn only if wanted.
```

Raw session.recv()/iteration does not collect events in a TurnView. Applications
that collect those events themselves are responsible for their own storage.

## Shared evidence and port implementation

`consumer/live-collection-limits.json` contains hand-written consumer cases for
exact boundaries, terminal admission, count-before-read, empty events, Unicode,
audio and tool input. These are not provider exchanges and must not be submitted
to live provider APIs. Python's `tests/test_live_collection_limits.py` executes
these cases for sync and async views and adds repeated-failure, endless-peer,
recovery, validation, lazy materialization and taxonomy tests. Port maintainers
must exercise the same vectors with their native collectors. The general vet
harness currently has no collector operation; these vectors need native tests,
not a claim that replay_live covers collector limits.

Verification after test authorization and ratification: Python tests passed
(2,492 passed, 5 local-Ollama tests skipped; paid subscription smoke tests
excluded) in 4.34 seconds with 16 workers. The collection tests and shared
consumer vectors ran in this suite. All 16 Python contract directions passed
with their existing skips; harness self-test caught all 40 mutations, and
spec/provenance checks passed. These results describe uncommitted working trees,
not a released or pinned revision. Contract pins, DSPy's bundled copy and other
language implementations are unchanged.
