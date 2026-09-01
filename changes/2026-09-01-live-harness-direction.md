# 2026-09-01 — live harness direction: recorded-transcript replay

Ratified: Maxime Rivest, 2026-09-01 (session assent "yes go!!" over the
announced next step: the recorded-transcript harness direction for live
sessions). Live sessions stay PROVISIONAL as a surface, but their CODEC
is now contract-checked: a port that decodes a recorded frame
differently, encodes a client event differently, or builds a different
setup frame goes red.

## The design

One new vet op, `replay_live` (PROTOCOL.md), replays a live session
transcript through the pure websocket codec — no socket, no session
mechanics:

- **setup**: LiveConfig → the connect-time frames, compared against the
  transcript's recorded setup frames (wire truth).
- **encode**: each canonical client event → its wire-frame BUNDLE,
  compared against the recorded frames; the grouping is contract
  (OpenAI `end_audio` → commit + response.create; text →
  item.create + response.create).
- **decode**: each verbatim recorded server frame → its canonical
  LiveServerEvent list, compared against the golden. An empty list is a
  real assertion — "this housekeeping frame is deliberately ignored"
  (Gemini `setupComplete`, OpenAI `conversation.item.added`, the benign
  cancel-race error).

What is deliberately OUT: session mechanics (locking, queues,
iteration, `turn()`/`Turn` sugar, reconnection) are per-language idiom.
The codec is the portability surface; the ergonomics layer rides on it.
Replay is fully deterministic — recorded transcripts freeze every id
and usage number, so no volatile paths were needed.

## The corpus (all live-captured 2026-09-01, both directions verbatim)

Seven transcripts, each from a real session that succeeded end to end
(the model's correct answer is the receipt, logged at capture time):

- `openai.live_text`, `openai.live_tools`, `openai.live_interrupt`,
  `openai.live_audio` — GA Realtime (`gpt-realtime-mini`): text turn,
  tool turn (argument deltas, SINGLE tool_call from output_item.done,
  function-call response.done ending NO turn, result + continuation),
  barge-in (status=cancelled → interrupted), audio turn (output_audio +
  transcript deltas, session.audio config).
- `gemini.live_text`, `gemini.live_tools`, `gemini.live_interrupt` —
  BidiGenerateContent (`gemini-3.1-flash-live-preview`, audio-native):
  setup/setupComplete handshake, audio + transcript turn with usage,
  tool turn, interrupted frame.

Case files carry `surface: "live"` + canonical `live_config`;
transcripts are the cases' `pinned_body` (JSONL of directed entries);
goldens pin the canonical decode only and were drafted through the
reference then reviewed against the pinned mapping rules (single
tool-call fire, no premature turn_end, terminal interrupts).

## Enforcement

- `harness/check.py` gains the `live` direction: three results per case
  ([setup]/[encode]/[decode]); 7 cases → 21 checks, green against the
  reference shim.
- `harness/selftest.py` gains two mutations, both proven caught:
  `live_dropped_event` (a decoded event vanishes) and
  `live_frame_key_drop` (an encoded frame loses a key). Baseline green
  in all 8 directions; 12 mutations total.
- `tools/audit.py`: live-surface cases are exempt from the
  canonical_request orphan rule by design and get their own
  completeness rule (live_config + pinned transcript + golden + directed
  frames), mirroring models.
- Reference: uniform pure hooks `_live_setup_frames` / `_live_encoder`
  on both live providers (sync live(), async live(), and the vet op all
  drive the same code).

## Trade-offs, stated

- Goldens are reference-drafted (like every golden) — the transcript is
  provider truth, the golden is the reviewed canonical mapping; a
  mapping dispute is settled against the transcript, not the golden.
- The corpus does not yet include: audio INPUT frames (send_audio
  bundles are pinned only by offline tests), the OpenAI cancel-race
  error frame, or a Gemini interrupted-with-VAD scenario. Additive
  captures when the surface graduates.
- Wire-frame comparison is parsed-JSON equality (key order/whitespace
  free), the request-direction standard — byte-exact framing is
  transport, not codec.
