# 2026-09-01 — media generation rebuilt on captured wire truth

Ratified: Maxime Rivest, 2026-09-01 (session assent: "ok, so we are
ready to implement all that?" over the media-generation design draft's
13 decisions, each grounded in same-day live captures; the draft is
`lm15-python/docs/cookbooks/drafts/media-generation.md`).

The pre-contract `image_generate`/`audio_generate` prototypes are
replaced by a capture-grounded surface across OpenAI, Gemini, and xAI
(Anthropic has no generation wire and raises).

## Contract surface

- Types (spec/types.md): `AudioGenerationRequest`/`AudioGenerationResponse`
  are RENAMED `SpeechGenerationRequest`/`SpeechGenerationResponse` —
  both implementing wires sell text-to-speech and nothing more; the old
  name promised music/sound-effects no wire offers.  Pre-1.0 cut.
- `ImageGenerationRequest` gains `images` (input images for edits, as
  ordinary ImageParts with all four addressing modes).  Verified
  honored on all three wires by pixel-checking a controlled edit
  (red-circle input must survive the edit); the check also caught that
  xAI's `generations` endpoint silently ignores input images — edits
  must route to `/images/edits`.
- `ImageGenerationResponse` gains `text` — Gemini routinely returns
  narration next to the image; dropping it was silent data loss.
- Media types come from the wire, never from code: OpenAI images state
  `output_format`, OpenAI speech types raw bytes via the content-type
  HEADER (server default captured: `audio/mpeg`), Gemini `inlineData`
  MIME verbatim (parameterized `audio/L16;codec=pcm;rate=24000`
  included), xAI states `mime_type` per image and it is JPEG.  The
  prototype's hardcoded `image/png` was a coincidence on two wires and
  a lie on the third.
- No client-side defaults: the prototype's `voice="alloy"` /
  `format="wav"` injections are removed; both fields are optional on
  every wire (captured) and omission means the server decides.
- `size` and `voice` are portable fields carrying the provider's own
  vocabularies (the `model` precedent).  Where a field has no wire slot
  the adapter raises (Gemini `format`; xAI `size`; >1 input image on
  xAI; url/file_id-addressed edit inputs on OpenAI).
- Usage is parsed where tokens exist (OpenAI and Gemini images, Gemini
  speech), honestly empty where they do not (OpenAI speech raw bytes;
  xAI reports only `cost_in_usd_ticks`, preserved in provider_data).
- `EndpointSupport.audio` renamed `speech` (one word, one meaning).

## Serde

Four new kinds — `image_generation_request`, `image_generation_response`,
`speech_generation_request`, `speech_generation_response` — with eight
canonical fixtures generated through the ratified reference serde and
strict-roundtrip-verified (90/90 corpus green).  Media payloads travel
as the Parts they are; the part kind's base64 rules apply unchanged.

## Reference implementation

Pure build/parse hooks per provider (the files/batch pattern), sync
drivers in the base, async drivers over the same hooks.  Adapter
routing: OpenAI `/images/generations` ↔ `/images/edits` (multipart)
switched by `images` presence; Gemini composes the frozen chat mapping
(`generateContent`) for both image and TTS models; xAI
`/images/generations` ↔ `/images/edits` with `image:{url|file_id}`
(data URIs verified honored).  Live-proven on all three wires
2026-09-01, sync and async.

## Evidence

`lm15-contract/receipts/2026-09-01-genmedia/` (OpenAI images + edits +
speech, Gemini image + edit + speech, pixel-check inputs) and
`lm15-contract/receipts/2026-09-01-xai/` (catalogs, images, edits,
rejected shapes — negative results pinned too).

## Deferred, with reasons

- Video generation: job-shaped on every wire (Sora, Veo, grok-imagine
  captured live); reuses the batch ticket pattern and gets its own
  design pass.
- Harness `image_gen`/`speech_gen` directions: land with pinned bodies
  from the capture corpus under the corpus rules, as a follow-up.
- OpenAI masks, `n`, quality/background; xAI quality/resolution tiers:
  `extensions` until a second wire grows the same knob.
