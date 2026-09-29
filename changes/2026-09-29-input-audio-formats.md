# 2026-09-29 — input_audio reads any common audio format as its true media type

Status: proposed amendment to MAP-12 rule 4 (ratified 2026-09-08); no other
rule changes.

## Found

DSPy renders `dspy.Audio` as a Chat Completions `input_audio` block whose
`format` is the file's MIME subtype with any `x-` prefix removed: `ogg` for an
ogg/opus phone recording, `mpeg` for an `.mp3` file, `flac`, `aac`. DSPy reads
that body into a canonical Request with `request_from_openai_chat` before any
provider is chosen (MAP-12's first consumer). MAP-12 rule 4 admitted only `wav`
and `mp3`, so the same recording sent to `vertex:gemini-3.8-flash` failed at
ingest with `input_audio.format must be one of ['mp3', 'wav']`, although
Gemini takes `audio/ogg` natively (reported from a live Gemini call on
2026-09-29: the clip sent as `inlineData` `audio/ogg` transcribed correctly;
no receipt is attached, and the new case needs none, since it pins a canonical
reading, not a wire fact).

`wav | mp3` is OpenAI's own server's list (`scrapes/openai/pages/chat--create.md`
§ `input_audio.format`). It is not a limit of the Chat Completions shape:
Google's Chat Completions server documents "OpenAI supports both wav
(audio/wav) and mp3 (audio/mp3). Using Gemini, all valid MIME types are
supported" (`research/cloud-hosts/sources/vertex-openai-compat.md`), and
`generateContent` takes `audio/*` (`scrapes/gemini/pages/generate-content.md`,
`Blob.mimeType`). Refusing the others at ingest hid a wire gap where rule 4
says it must not be hidden: "ingest is not where a wire gap is hidden".

## Changed

- MAP-12 rule 4: `input_audio.format` reads as its true media type: `wav` →
  `audio/wav`, `mp3` | `mpeg` → `audio/mpeg`, and `ogg`, `opus`, `flac`, `aac`,
  `aiff`, `webm` → `audio/<format>`, the types Gemini's references name. A label
  is never relabelled as another type. Any other format stays malformed
  (rule 6), so a typo is not read as a media type nobody sends.
- `tools/openai-chat-ingest-verdicts.json`: the `input_audio` row says the same.
- Case `openai_chat.ingest_input_audio_ogg` pins the ogg reading.

Unchanged: a builder with no slot for audio still raises before the wire
(MAP-10). The Chat Completions builder carries no audio on any preset, and
Anthropic has no audio block; Gemini sends the part as `inlineData` with its
media type.

Left out: `m4a` / `mp4`. The file is `audio/mp4` by IANA and Python's
`mimetypes`, while Gemini's Interactions reference names `audio/m4a`; which
spelling Gemini accepts has no receipt yet.
