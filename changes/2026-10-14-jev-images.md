# 2026-10-14 — Images reach Jev: an image part is a reference in the state, its bytes an asset

Request: Maxime Rivest, 2026-10-14, in session ("add support for image
jev in lm15", over TypeSafe's announcement that Jev reads images behind
the `TypeSafe-Danger-Zone-Images: true` header). D1, D3 and D4 follow
from TypeSafe's documented wire and change nothing already ratified.
**D2 amends 2026-09-19 D2 and awaits Maxime's ratification**; it is
implemented so the decision can be judged on working code, and reverting
it is one rule in each port (the refusal it replaces is still the
behaviour for text-only messages).

## The problem

Until today the typesafe dialect refused every media part before the wire
(2026-09-17 D8: "Jev reads text or data"). TypeSafe now documents images
(`docs.typesafe.ai/images`, `primitives/box`, read 2026-10-14; marked
"dreamer-ready", i.e. beta): every image is listed once in a top-level
`assets` map, keyed by a reference string, and the reference is written
wherever the image belongs — a whole state value, or inside a string of
the state, a question's `instructions` or its `criteria`. Assets are PNG
or JPEG, sent base64 in the JSON body or as multipart file parts, and a
request that carries one must send `TypeSafe-Danger-Zone-Images: true`
(live without it: HTTP 400 `api_usage_error`, "Images are experimental.
Send the header TypeSafe-Danger-Zone-Images: true to use them.").

lm15's portable way to show a model a picture is an `ImagePart` in the
user message. That request answered judgments on the openai, anthropic
and gemini wires and was refused on the one wire built for judgments.

## Decisions

**D1 — One image part is the state.** A typesafe request whose one user
message holds one image part sends `state` = that image's reference and
the bytes under `assets[reference]` as
`{"type": "image", "format": "png" | "jpg", "data_base64": <the part's base64>}`.
Nothing else changes: the questions come from the judgment schema as
before, and a question names the image in words ("the shape in the
image"). The reference is `<lm15-image-N>`, N counting the message's
image parts from 1 in order: deterministic (cases and ports reproduce it
byte for byte, which a random UUID — TypeSafe's own advice — would not),
and closed by `>` so `<lm15-image-1>` never matches inside
`<lm15-image-10>` (systemone replaces references as plain text,
left to right).

**D2 — A message holding images beside other parts is the array of its
parts, in order (amends 2026-09-19 D2; to ratify).** Text verbatim, a
data part's value verbatim, each image its reference:
`["Listing: a red ball.", "<lm15-image-1>", "<lm15-image-2>"]`.
2026-09-19 D2 refused a second part because a data part with named keys
always carried what the caller meant without an invented shape. That
door does not exist for images: a data part holds JSON, not pictures, so
refusing would leave no lm15 request at all that shows Jev two images or
an image with a caption — the comparisons TypeSafe's docs lead with.
The array is the least shape the adapter can add: the message's own
parts, in its own order, no key, no role. Jev reads arrays as state
(2026-09-19 D1, `judgments_array_state`), and a question reaches an
element by path (`` `[2]` ``, receipted). A message of text and data
parts only is still refused as before.

**D3 — The header goes with the image.** A request whose body carries
`assets` sends `TypeSafe-Danger-Zone-Images: true`. The caller who puts
an image in a Jev request has made the opt-in the header exists for; a
build that left it out could only ever produce the 400 above. No
adaptation is recorded: nothing the caller asked for changes. Stated
consequence: lm15 cannot show TypeSafe's "beta" warning at run time; the
documentation carries it.

**D4 — What has no slot is refused at the part** (MAP-10 rule 1, never a
fetch or a conversion): an image addressed by `url` or `file_id`
(systemone assets are inline bytes), an image whose `media_type` is not
`image/png`, `image/jpeg` or `image/jpg` (TypeSafe reads PNG and JPEG
only), and audio, video, document and binary parts.
`UnsupportedFeatureError`, `feature` = `messages[i].parts[j]`. `detail`
is not sent — the wire has no such hint — exactly as on anthropic and
gemini.

## Not taken, with reasons

- **Multipart upload.** TypeSafe recommends it (base64 makes each image
  about a third larger, counted in the 32 MiB body limit). Every port
  already speaks base64 JSON; images are capped at 1568 pixels a side,
  so a request of a few images is far from the limit. Revisit if a
  receipt shows a real request hitting it.
- **Box questions.** A box answer is four generated numbers, not a
  pick among declared keys; MAP-14 refuses free-form properties, and a
  canonical box needs its own design (a judgment kind or a new part).
- **Images inside `instructions` or `criteria`.** A JSON Schema
  `description` is a string; lm15 has no way to carry a picture there.
- **Client-side size checks.** systemone rejects out-of-range images
  with a clear 400; lm15 does not decode images.
- **De-duplication.** The same picture in two parts is two assets; the
  wire would read it twice either way.

## Evidence

- `docs.typesafe.ai/images.md`, `primitives/box.md` (read 2026-10-14).
- Receipts `receipts/2026-10-14-typesafe/`, jev-latest = jev-1.13.0:
  `judgments_image_state` (one PNG; shape `circle` p=1.0, red 1.0;
  558 input tokens) and `judgments_image_parts` (text + PNG + JPEG;
  first matches the listing 0.98, `` `[2]` `` is a blue square 0.99,
  same shape 0.01 — answers only a model that received both pictures
  gets right); `probe-error-images-off.json` (the 400 without the
  header, now `errors/cases/typesafe.json` `typesafe.images_off`).
- Finding, failed receipts `failed-judgments_image_*`: 320x256 and
  300x270 images were refused ("Invalid image dimensions.") although the
  docs give a 256-pixel side minimum; 280x280 and 320x280 passed. The
  capture images are 320x280. Reported here, not enforced by lm15.
- Cases: `cases/typesafe/judgments_image_state.json`,
  `judgments_image_parts.json` (live); refusals `image_refused.json`
  (URL, re-grounded), `image_file_id_refused.json`,
  `image_format_refused.json`, `audio_refused.json`.

## Consequences

- `docs/mapping-rules.md` MAP-14 §2 typesafe row extended.
- Ports: the typesafe state builder admits image parts (D1/D2), the
  payload gains `assets` between `state` and `questions`, the build adds
  the header (D3), and the part loop refuses D4's cases. No new type, no
  new field, no new vocabulary value.
