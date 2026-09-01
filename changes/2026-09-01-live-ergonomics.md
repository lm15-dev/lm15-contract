# 2026-09-01 — live ergonomics: turn-scoped iteration, Turn, native async

Ratified: Maxime Rivest, 2026-09-01 (session assent "yes" over the
expert-audited four-point slate: (1) turn()/Turn in with the
half-duplex caveat documented, (2) no combined send-and-drain verb,
(3) NATIVE async live — the thread-wrapper recommendation was reversed
under audit, (4) live event types stay separate-but-parallel to stream
deltas). Live remains a PROVISIONAL surface; no canonical types,
vocabularies, or serde kinds change.

## What ships (reference implementation)

- `session.turn()` — an iterator scoped to one turn that ends itself
  after yielding the terminal event (`turn_end` / `interrupted` /
  `error`), the stream() idiom. Tool calls are yielded mid-iteration
  (the caller holds the session and can answer inline).
- `Turn` + `session.turn().result()` — the materialized turn: joined
  text, decoded audio bytes (+ media type), `tool_calls` as
  ToolCallInfo data, usage, `ended_by`, error, raw events. When the
  model requests a tool, `result()` returns with
  `ended_by="tool_call"` instead of deadlocking against a model that
  waits for the caller — the exact `finish_reason="tool_call"`
  contract of complete(). Verified live 2026-09-01: the handoff
  behaves IDENTICALLY on OpenAI GA Realtime and Gemini
  BidiGenerateContent (transcripts in
  lm15-dev/curl-fixtures/live-2026-09-01/lm15-ergonomics-proof.txt).
- Native async live: `await lm.live(config)` on AsyncOpenAILM /
  AsyncGeminiLM returns `AsyncWebSocketLiveSession` over
  `websockets.asyncio` — a real awaitable socket sharing the sync
  adapters' pure codecs verbatim (Gemini's setup handshake was
  refactored into pure pieces both drive). The previously drafted
  thread wrapper is REMOVED, with the audit reason on record: a
  blocked sync recv in a worker thread cannot be cancelled from the
  event loop, and cancellation (barge-in, hangup) is the heart of
  realtime; the "native is a much bigger job" claim was checked and
  found false (same client shape, shared codecs).

## Boundaries, stated

- `turn()`/`Turn` are per-language ergonomics like BatchJob, NOT
  contract surface: the LiveSession protocol and the future transcript
  harness direction pin the EVENT STREAM, not this sugar. Ports choose
  their own idiom.
- Half-duplex caveat carried in docs and docstrings: live is
  full-duplex; with voice-activity detection the model can speak
  spontaneously and turns can overlap — plain session iteration is the
  primary surface for continuously listening agents; `turn()` serves
  send-then-listen apps.
- `.result()` buffers text and audio in memory until the turn ends —
  documented; latency-sensitive playback iterates events.
- No combined send-and-drain verb (rejected: hides the duplex
  transport, invites blocking misuse; cost accepted: a few more lines).
- The rejected-turn asymmetry is deliberate: iteration does NOT stop
  at tool calls (the caller can answer), materialization DOES (it
  cannot).

## Evidence at landing time

- Live proof on BOTH providers, sync and async: plain turn,
  materialized turn with audio+usage, tool handoff and continuation,
  async turn — real outputs re-captured for cookbook recipe 13 from
  the exact snippets shown.
- 16 new offline tests (scripted sessions, sync + async), including a
  cancellation test that encodes the thread-wrapper rejection reason;
  no-loop culture pinned (Turn holds tool calls as data only).
