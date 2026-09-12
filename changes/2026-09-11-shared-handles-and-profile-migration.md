# Shared video handles, live turns, and explicit profile migration

Status: implementation authorized by Maxime Rivest, 2026-09-11, in session:
“Good nice go implemented excellently and fully” following the recommendation
to port job handles, specify then port turns, simplify profiles before spreading,
and keep OAuth callback listeners optional. The detailed operational rules below
are recorded for review; they do not freeze these provisional surfaces.

## VideoJob (Python sync/async, TypeScript Node/browser, Rust async/blocking)

- A handle owns a provider binding and the last VideoJobInfo snapshot. Reading
  id, status, progress or info does no I/O. Raw submit/status/result/list remain.
- video_generate submits once and returns a handle; video_job(id) fetches a
  snapshot and reattaches; video_jobs wraps the list. Missing provider list
  support remains a refusal; handles never invent discovery.
- refresh performs one status request and updates the snapshot only on success.
- wait polls every five seconds by default, with a 300-second default timeout;
  explicit None/null disables the deadline. Poll intervals must be finite and
  positive; timeout must be finite and non-negative. Zero timeout performs no
  network request for an unfinished job. A terminal snapshot returns immediately.
- A failed/expired/cancelled job is terminal too: wait returns its handle, not
  success at generating a video. result delegates to the raw result operation;
  no hidden polling, submission or retries. Provider errors propagate unchanged.
- Timeout is a local VideoWaitTimeout (Rust VideoWaitError::TimedOut), carrying
  the last snapshot, not the provider's HTTP TimeoutError. Async cancellation
  stops waiting, never resubmits, and does not promise to cancel generation or
  billing. Python sync deadlines are cooperative around status I/O (the existing
  transport deadline bounds an in-flight call); async waits bound that await too.
  A custom TS provider ignoring AbortSignal may finish its in-flight read later.

## Live Turn and TurnView

These are half-duplex collectors over canonical LiveServerEvent, not new wire
or serde types. Full-duplex clients retain session.recv / raw iteration.

- session.turn() creates a lazy view, never sends a prompt or runs a tool.
- Event iteration includes and stops after turn_end, interrupted or error.
  A tool_call is yielded but is not an iteration boundary: the application
  can send the tool result and continue. Rust's borrowed view forwards send
  and send_tool_result because it holds the mutable session borrow.
- result() consumes until that boundary OR the first complete tool_call. It
  seals the view at tool_call so it cannot deadlock waiting for the caller.
  Following events, including late usage, stay for the next view. Tool-call
  fragments are not actionable until a complete tool_call event exists.
- Views retain all events they consumed, including those already yielded to
  the caller. result after partial/full iteration includes them, and repeated
  result returns the same materialized turn without further reads. A view
  has one active reader. close/drop of a view does not close the live session.
- Turn contains ended_by, text, decoded audio bytes, audio_media_type,
  tool_calls, usage, error, and events. ok is true only for turn_end.
  snapshot() exposes partial data as ended_by=incomplete, never as success.
- text concatenates text events. Audio concatenates decoded chunks, taking the
  first stated media type; conflicting stated media types are refused rather
  than presenting mixed encodings as one audio file. Missing type stays absent.
- Usage is the field-wise sum of usage and turn_end events consumed by this
  view. A missing counter on either side stays unknown (INV-029). No deduplication
  by matching values, inferred zero, or reassignment to earlier turns. In
  particular usage arriving after a tool_call belongs to the following view;
  usage preceding interruption is retained. Counter overflow is refused.
- A wire error event returns Turn(ended_by=error, error=the event's detail).
  EOF before a boundary raises TransportError; transport/decoding errors keep
  their identity. snapshot remains available for salvage. No fabricated terminal
  event. Cancellation is not an error event and propagates to the caller.
- Collecting a turn buffers events/audio. Raw session iteration is the unbuffered
  alternative. Stop one reader before starting another. Blocking consumers must
  use transport/session timeouts; async callers can use cancellation/deadlines.

## Profiles

ProviderProfile/EndpointProfile are deprecated Python compatibility APIs, not
new cross-language requirements. Keep their current behavior during migration;
no removal version is promised here. Their unique capability is per-model and
alias-selected overrides, not just a URL wrapper. Migration explicitly selects
model metadata and merges partial compat values in the existing order:
base < endpoint < selected model < request override. None inherits; auto resets
that field to the dialect default. The existing merge helpers do the work.
OpenAILM.resolved_compat(request) exposes the final resolved policy without I/O.
Direct compat/base_url is preferred for the common case. No new profile
resolution system is introduced in the other languages.

## OAuth callback listeners

Optional host-specific infrastructure, implemented when a concrete owned flow
needs it. Keep Python's listener. Neither mandatory port parity nor a permanent
ban. Browser redirect handling is not a localhost HTTP server.

## Trade-offs

- Handles add maintained API/state, but leave raw verbs available and never hide
  paid submissions behind polling or property access.
- A bounded default wait changes Python's former unbounded default; users who
  intentionally wait indefinitely pass None explicitly.
- Turn views retain events and seal result at tool calls. This fixes lost data
  after partial iteration and makes repeated result predictable, at a memory cost.
- Profiles remain temporarily redundant for compatibility rather than breaking
  existing model-policy selection before users can migrate.
- Implementation parity is separate from live-provider verification. Tests use
  scripted providers/events and shared semantic vectors; no paid video generation
  or OAuth logins are needed to establish these local rules.
