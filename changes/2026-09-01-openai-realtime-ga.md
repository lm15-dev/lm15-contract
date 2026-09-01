# 2026-09-01 — OpenAI Realtime: beta shape is dead, GA shape verified live

Recorded: 2026-09-01, during the live-ergonomics investigation the
maintainer ordered ("yes investigate gpt realtime!"). Live sessions
remain a PROVISIONAL surface (spec/SCOPE.md); no canonical types or
vocabularies change. This entry pins wire facts and two mapping rules.

## The headline fact

The OpenAI adapter's live path targeted the retired beta Realtime API
and could not connect at all: the `OpenAI-Beta: realtime=v1` header
now hard-closes the socket (close code 4000,
`invalid_request_error.beta_api_shape_disabled`, observed live
2026-09-01). `supports.live=True` on OpenAI was dead wire code; the
cookbook's "Gemini is the only provider with live support" was the
truth. The adapter now speaks the GA shape and the claim is inverted:
both first-party live providers are live-verified.

## GA wire facts (captures in lm15-dev/curl-fixtures/live-2026-09-01/)

- No beta header. `session.update` requires `session.type: "realtime"`;
  `modalities` → `output_modalities`; audio config nests under
  `session.audio.{input,output}` with format objects
  (`{"type": "audio/pcm", "rate": N}`); voice under audio.output.
- Server events: `response.output_text.delta`,
  `response.output_audio.delta`,
  `response.output_audio_transcript.delta` (transcript → canonical
  text events), `response.function_call_arguments.delta` (carries
  call_id), `response.output_item.done`, `response.done` (usage detail
  keys renamed: `input_token_details`/`output_token_details`, no "s"),
  `error`.
- Client frames unchanged from beta: `conversation.item.create`,
  `input_audio_buffer.append`/`.commit`, `response.cancel`.
- Interrupt: `response.cancel` → `response.done` with
  `status: "cancelled"`, `status_details.reason: client_cancelled` →
  canonical `interrupted` event (usage of the cancelled turn dropped —
  mirrors Gemini).
- Verified live end to end with the shipped session: text turn, audio
  out + transcript, audio in (append/commit, VAD off), tool loop,
  barge-in. One-shot `stream()` over the realtime websocket also
  verified (`Lima.`, usage intact). Gemini live regression: green.

## Two mapping rules (pinned by tests from captured frames)

1. **A response that requests tool calls does not end the turn.** GA
   ends the WIRE response at a function_call; the semantic turn is
   still open (the model awaits results; the continuation arrives as a
   further response). Emitting turn_end there breaks the shared
   tool-dispatch loop that Gemini's live path teaches. Corollary: the
   tool_call event is emitted ONLY from `response.output_item.done` —
   `function_call_arguments.done` duplicates it (both observed for one
   call) and mapping both double-sends tool results.
2. **The barge-in race is benign.** `response_cancel_not_active`
   (captured verbatim) surfaces when interrupt() fires twice or after
   the response finished; it is swallowed, matching Gemini's tolerance
   of repeated interrupts.

## Design choice, stated

With `input_format` set, the adapter disables server VAD
(`turn_detection: null`): a turn happens exactly when the caller sends
end_audio() (commit + response.create), making `send_audio`/`end_audio`
deterministic and provider-parallel. Trade-off: continuous-conversation
VAD on OpenAI requires re-enabling turn_detection through extensions;
Gemini always segments server-side.

## Evidence at landing time

- 14 new offline tests decode verbatim captured frames (single-fire
  tool calls, GA usage keys, cancelled→interrupted, benign race,
  session shape); 764 tests green.
- The live-ergonomics pass proper (turn-scoped iteration, turn
  materialization, async live) is designed but awaits maintainer
  ratification — this entry is investigation fallout only.
