# 2026-09-24 — Message media reaches the wire natively or raises, in every SDK

Status: implementation parity for a ratified rule (MAP-10: "message content
reaches the wire natively or raises"); no rule changes.

## Found

Fixing lm15-rs's long-failing unit tests (a test expected user audio to reach
OpenAI's Responses input; Rust had begun refusing it in the 2026-09-20
catch-up pass) led to a comparison of every media kind in every role across
the four CI'd SDKs. In 21 cells lm15-python, lm15-ts and lm15-go **lost the
part silently**, with no record:

- Anthropic Messages, user or assistant audio, video or binary: sent as an
  empty text block.
- OpenAI Responses and Chat Completions, any media in an assistant message:
  the part (on Responses, the whole message) dropped, or `content: null`.

lm15-rs refused all 21, as MAP-10 requires. In 6 other cells it was Rust that
diverged: it refused user audio, video and binary on the Responses input,
which the reference sends natively (`input_audio`, `input_video`,
`input_file`; Meta documents `input_video`). And for a developer turn with an
image or document on the Anthropic wire, Rust sent it as a `[developer]` user
turn where the reference refuses (a developer turn is rendered as text there).

## Changed

- lm15-python, -ts, -go: one preflight per dialect (`check_message_media`),
  the cells where the dialect has no slot in that role; `feature` is the
  part's path (`messages[i].parts[j]`), as lm15-rs already reported.
- lm15-rs: user media on the Responses input is sent (the reference); a
  developer turn's media on the Anthropic wire is refused.
- Cases: `anthropic.user_audio_refused`, `openai.assistant_image_refused`,
  `openai_chat.assistant_audio_refused`.
- `tools/differential_requests.py` grows ten media variants (user, assistant
  and developer roles): 2,565 requests, identical in Python, TypeScript, Go
  and Rust. A wider sweep (every corpus provider × 3 roles × 5 kinds, 330
  cells) finds no SDK losing a part silently.

Open: whether OpenAI's own Responses endpoint accepts `input_video` has no
receipt; the reference sends it and the server's answer decides. A friendlier
Anthropic rendering of a developer turn's media (as Rust did) would need a
rule change.
