# 2026-08-31 — MAP-4: stream goldens gain the leading StreamStartEvent

## Normative rule (canonical-fact citation)

`lm15-python/docs/mapping-rules.md` **MAP-4**, written at lm15-python
`452a2fe`: an lm15 stream that yields any delta or end event yields EXACTLY
ONE `StreamStartEvent`, before all of them. Dialects with a real start frame
(OpenAI Responses `response.created`, Anthropic `message_start`) pass it
through with its `id` and `model`; dialects without one (chat completions,
Gemini SSE) get a synthesized start carrying the REQUEST's model, added by
the same coalescer that enforces MAP-3. Duplicate starts collapse to the
first. Error events never force a start.

Serde shape per `spec/types.md` § StreamStartEvent: `type` always; `id` and
`model` omit-empty. A synthesized start therefore serializes as
`{"type": "start", "model": "<request model>"}` — no `id`.

## Why this entry exists

MAP-4 landed in the reference implementation and rule text (lm15-python
`452a2fe`) WITHOUT the changes/ entry AUTHORITY.md requires and WITHOUT the
matching golden updates. Result: the reference failed the harness on the four
no-start-frame stream cases while the ports passed by matching stale goldens
— the scoreboard was inverted. This entry completes the rule change.

## Reference-implementation bug found and fixed (not an oracle edit)

`lm15/vet.py` called `coalesce_stream(raw_events())` without
`model=request.model`, so the shim's synthesized start dropped the model that
MAP-4 requires (the runtime paths in `providers/base.py` /
`providers/async_base.py` passed it correctly). Fixed in lm15-python together
with this entry; regression test
`tests/test_vet_shim.py::test_replay_stream_synthesized_start_carries_model`.
The goldens below encode the RULE's shape, not pre-fix shim output.

## Golden changes (re-scribed via tools/scribe_goldens.py --shim python)

Stream-direction goldens only. The full re-scribe touched 111 files; 107
whose only diff was a provenance re-stamp were restored byte-identical.
For each changed golden the diff was verified mechanically: exactly one
synthesized start prepended (`old_events == new_events[1:]`),
`canonical_response` byte-identical, start model == case
`canonical_request.model`:

- `gemini/streaming` — `{"type": "start", "model": "gemini-2.5-flash"}`;
  3 -> 4 events.
- `openai_chat/streaming` (Groq) —
  `{"type": "start", "model": "llama-3.1-8b-instant"}`; 10 -> 11 events.
- `openai_chat/streaming_vllm` —
  `{"type": "start", "model": "Qwen/Qwen3.5-0.8B"}`; 22 -> 23 events.
- `openai_chat/streaming_sglang` —
  `{"type": "start", "model": "Qwen/Qwen3.5-0.8B"}`; 10 -> 11 events.

Untouched: `anthropic/streaming`, `openai/streaming`,
`openai/stream_options`, `openai/background` (native start frames already in
the traces), and every case, body, error, and serde vector.

`reviewed` stamps: retained verbatim with an appended re-review note citing
MAP-4 and this entry, per the stamp-preservation rule established in
changes/2026-06-10-map3-single-end-event.md.

## Port impact

At the time of this entry the Go, Rust, and TypeScript ports implement the
pre-MAP-4 trace (no synthesized start) and will fail these four cases until
their coalescers are updated. That is the correct direction of failure:
implementations chase the oracle, never the reverse.

## Ratification

Prepared 2026-08-31 in-session at the maintainer's direction ("go, implement
this") after the divergence report. Oracle change pending Maxime Rivest's
review of this commit before push.
