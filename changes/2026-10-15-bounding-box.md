# 2026-10-15 — Bounding boxes: a judgment that answers where, on every wire

Request: Maxime Rivest, 2026-10-15, in session ("support the new bounding
box for the decision models … so that they all get turned into bounding
boxes too, like we're doing for the other types … in all of the
languages and make a release"). Lifts the deferral in
`changes/2026-10-14-jev-images.md` ("Box questions … a canonical box
needs its own design"). The judgments surface stays provisional
(SCOPE.md). D1–D5 follow TypeSafe's documented wire and lm15's existing
judgment convention; nothing already ratified changes meaning. **The
convention (D1) and the probabilities rule (D3) await Maxime's
ratification**; both are implemented in all six SDKs so they can be
judged on working code.

## The problem

TypeSafe's Jev 1.14 adds a fourth question type, **Box**
(`docs.typesafe.ai/primitives/box`, read 2026-10-15; "dreamer-ready",
i.e. beta): `{"type": "box", "instructions": "the coffee mug in
`photo`"}`, no `criteria`, answered by
`{"type": "box", "box": {"top", "bottom", "left", "right"}, "confidence"}`
— each edge a fraction from 0 to 1 of the image's height (`top`,
`bottom`) or width (`left`, `right`), measured from the top-left corner.
It needs `jev-preview` or `jev-1.14.0` and the
`TypeSafe-Danger-Zone-Images: true` header.

Every other judgment kind already reaches every wire: Jev answers it
natively, the cloud models answer it as structured output, a vLLM server
measures it. A box had no spelling in lm15 at all, so a program that
asks "where is the mug?" could not be written once and run anywhere.

## Decisions

**D1 — A box is a judgment declared by its shape (MAP-14 §1; to
ratify).** A top-level property of a `json_schema` is a **bounding box**
when it is an object schema (`type: "object"` or no `type`) whose
`properties` are exactly `top`, `bottom`, `left` and `right`, in any
order, each with `type: "number"`. Every other keyword on it
(descriptions, `required`, `additionalProperties`, bounds) is the
caller's and travels verbatim. Its meaning is Jev's: the smallest
rectangle around what the property's `description` names, in the
request's image, edges as fractions of the image measured from the
top-left corner. A box declares no answer keys: it is **answered, never
scored** — the same position "ordinary structured output" already holds
in MAP-14, but recognized, so Jev can be asked it and the answer is a
`DataPart` everywhere.

Plain JSON Schema, as the other kinds are: nothing to strip, nothing
provider-specific, and a box a caller writes by hand qualifies. Stated
trade-off: recognition is by shape, so an unrelated object of exactly
four numbers named `top`/`bottom`/`left`/`right` is read as a box. On a
generated-JSON wire this changes nothing but the answer's part (a
`DataPart` instead of a `TextPart`; `.text`, `.json` and `.data` read
both, `types.md` §Response amended 2026-10-10); on `typesafe` it becomes
a Box question, which is what such a property can only mean there.

**D2 — Per wire (MAP-14 §2).**
- `typesafe`: a box is `{"type": "box", "instructions": <description>}`
  (no `criteria`; a missing description is `defaulted` to the property
  name, as for every kind). The opt-in header goes with **an image or a
  box question** (amends 2026-10-14 D3): live, a Box question without an
  image is refused without the header exactly as an image is
  (`probe-error-box-header-off`), so a build that left it out could only
  ever produce that 400.
- `openai`, `openai-chat`, `anthropic`, `gemini`: the schema goes
  verbatim (INV-050; no rewrite is needed — the receipted rewrites touch
  only `anyOf`, which a box does not use).
- `openai-chat` on a server that scores named tokens (MAP-14 §4): a box
  is not scorable; it is answered by the generated-JSON call that
  already answers ordinary properties (`client_side`, recorded), and the
  trie measures the keyed judgments beside it. A request whose judgments
  are all boxes takes the ordinary generated path.

**D3 — The answer (MAP-14 §3; to ratify).** `DataPart.value[name]` is
the box object. On `typesafe` it is Jev's `box` verbatim — numbers as
written (serde number rule 4), in Jev's order — after checking it is
exactly the four edges, each a finite number in `[0, 1]` (a reply that
is not is a `ProviderError`, like a malformed distribution). Jev's
`confidence` stays verbatim in `provider_data.typesafe.answers`, as for
every kind (2026-09-17 D12). A box never has a `probabilities` entry.
`config.probabilities` concerns only judgments with declared keys: a
request whose judgments are all boxes asked for nothing measurable, so
no wire records `dropped` for it and `required` refuses nothing. Beside
a keyed judgment, the policy applies to that judgment exactly as before.

**D4 — The helper `bounding_box(instruction)`** (per port, sugar, like
`choice`/`yes_no`/`score`): emits the D1 shape with each edge's meaning
in its `description` (TypeSafe's SDK wording) and `required` +
`additionalProperties: false` (OpenAI `strict` needs both). It writes
**no `minimum`/`maximum`**: Anthropic refuses them on a number (HTTP 400,
"For 'number' type, properties maximum, minimum are not supported",
`receipts/2026-10-15-anthropic/probe-box-edge-bounds.json`), and the
helper must work on every wire. Names: `bounding_box` (Python, Rust,
Julia, R), `boundingBox` (TypeScript), `BoundingBox` (Go) — not `box`:
`box` is a reserved word in Rust, masks `graphics::box` in R, and names a
heap pointer in Rust and boxing in several languages; "bounding box" is
the field's own term.

**D5 — What is not done, with reasons.**
- **No refusal when the request has no image.** Jev answers 200 with a
  box around most of the frame and confidence 0.02
  (`probe-box-without-image`); a cloud model invents a box. lm15 does not
  judge whether any question is answerable from its input (a `choice`
  about "the image" with no image is not refused either).
- **No model check.** Box needs Jev 1.14; on `jev-latest` (1.13 today)
  Jev answers a bare `400 api_usage_error "Invalid request."`
  (`probe-box-on-jev-latest`, pinned `errors/cases/typesafe.json`
  `typesafe.box_older_model` → `InvalidRequestError`). A list of model
  names that may ask boxes would go stale when `jev-latest` moves; the
  helper's documentation names `jev-preview`. Stated cost: that 400 does
  not say why.
- **No "not found".** Jev has none; a box is always four edges. Pair a
  `yes_no` with it (TypeSafe's own advice).
- **No pixel conversion helper.** One multiplication by the image's
  width or height; shown in the documentation.
- **No rescaling of a cloud model's numbers.** An answer in the wrong
  frame is the model's answer (INV-002); see Evidence.

## Evidence

- `docs.typesafe.ai/primitives/box.md`, `images.md`, the JavaScript SDK
  reference (`BoxQuestion`, `BoxResponse`, `BoxCoordinates`, `box()`) and
  the Python SDK changelog (v0.7.5, 2026-10-14: "support `Box` questions
  and answers"), read 2026-10-15.
- `research/providers/typesafe/images/shapes.png` (640x480): a red
  square at top 0.20, bottom 0.60, left 0.55, right 0.85; a blue circle
  at top 0.583, bottom 0.917, left 0.10, right 0.35.
- `receipts/2026-10-15-typesafe/`, jev-preview = jev-1.14.0:
  `cases/typesafe/judgments_box.json` (red 0.19/0.62/0.55/0.85
  confidence 0.75; blue 0.58/0.95/0.11/0.35 confidence 0.94; `has_red`
  0.97); probes `box-on-jev-latest` (400), `box-without-image` (200,
  confidence 0.02), `error-box-header-off` (400, the images gate).
- `receipts/2026-10-15-anthropic/`: `cases/anthropic/judgments_box.json`
  (claude-haiku-4-5, 200, schema verbatim) and `probe-box-edge-bounds`
  (400 on `minimum`/`maximum`).
- `receipts/2026-10-15-vertex/`: `cases/vertex/judgments_box.json`
  (gemini-2.5-flash on the gemini dialect, 200, schema verbatim).
- `receipts/2026-10-15-openai-codex/`: gpt-5.6-luna through the
  Responses dialect, 200, schema verbatim, red and blue boxes exact to
  0.01 (router-level receipt: a subscription sign-in the harness cannot
  replay, so no case; `openai` and `gemini` direct were unavailable that
  day — no credits / spend cap).
- Accuracy, one synthetic image, max edge error over both boxes (not a
  quality claim): Jev 1.14 ≤ 0.04; gpt-5.6-luna ≤ 0.01; Claude Sonnet 4.5
  ≈ 0.15; Gemini 2.5 Flash ≈ 0.15; Claude Haiku 4.5 0.30–0.40 (it
  answered the red square as pixels ÷ 1000: 0.352 for x = 352 px).
  Rewording the edge descriptions three ways changed neither Claude
  model's error: the frame is the model's, not the schema's.

## Consequences

- `docs/mapping-rules.md` MAP-14 §1–§3 amended; `spec/types.md`
  §DataPart and `Config.probabilities` note boxes.
- Ports: the schema reader recognizes a box (kind `box`, no keys); the
  probability policy, the trie and the candidate-likelihood fold read
  only keyed judgments; the typesafe dialect asks Box questions, sends
  the header with them and reads the box verbatim; the helper is added.
  No new type, no new field, no new vocabulary value.
