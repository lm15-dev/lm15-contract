#!/usr/bin/env python3
"""TypeSafe (Jev) live capture — case and probe declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-typesafe/``.

    TYPESAFE_API_KEY=… python3 research/providers/typesafe/capture.py [--dry-run] [--only a,b] [--force]

Model default ``jev-latest`` (resolves to jev-1.13.0, 2026-09-17).  The
cases are the state shapes of changes/2026-09-19-jev-state.md D1 — a
string, an object (with a named context key and backtick paths), an
array — over the MAP-14 judgment convention (changes/2026-09-17-judgments.md);
the error probes are the documented envelopes (401 authentication_error,
400 api_usage_error unknown model, 422 pydantic detail list).

Images (changes/2026-10-14-jev-images.md): ``judgments_image_state`` and
``judgments_image_parts`` send the two drawings under ``images/`` (320x280:
the server refused 320x256 and 300x270 with "Invalid image dimensions."
on 2026-10-14 although its docs give a 256-pixel side minimum) and ask
questions only a model that received the pixels answers right (shape,
colour, which image);
``error-images-off`` is the same image request without the opt-in header.

Bounding boxes (changes/2026-10-15-bounding-box.md): ``judgments_box``
sends ``images/shapes.png`` (640x480: a red square with edges top 0.20,
bottom 0.60, left 0.55, right 0.85; a blue circle top 0.583, bottom 0.917,
left 0.10, right 0.35) and asks for both boxes and a yes/no, on
``jev-preview`` — Box needs Jev 1.14.  The probes record what lm15 does not
prevent: a Box on ``jev-latest`` (1.13 on 2026-10-15), a Box with no image
in the request, and a Box sent without the opt-in header.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import Capture  # noqa: E402
from lm15 import Config, Message, Request  # noqa: E402
from lm15.judgments import bounding_box, choice, judgments, score, yes_no  # noqa: E402
from lm15.types import data, image  # noqa: E402

cap = Capture("typesafe", env_var="TYPESAFE_API_KEY", default_model="jev-latest", host="api.typesafe.ai",
              change_slug="judgments")

NOTE = ("Ripe blackberry and cassis lead, framed by toasty oak and firm, fine-grained tannins. "
        "Long, layered finish with graphite and dried herbs. Impressive now; will reward a decade in the cellar.")
LEVELS = {
    "faulty": "Faulty or unpleasant - the note is mostly criticism",
    "barely_ok": "Barely acceptable - drinkable, nothing to recommend it",
    "simple": "Simple and sound - correct, plain, forgettable",
    "everyday": "Pleasant everyday wine - some appeal, little depth",
    "good": "Good - clear varietal character, well made",
    "very_good": "Very good - balanced, with something to say",
    "excellent": "Excellent - complex and structured",
    "outstanding": "Outstanding - depth and length, built to age",
    "superb": "Superb - among the best of its type",
    "profound": "Profound - the note treats it as exceptional",
}
WINE = judgments(
    quality=score("How good is this wine, according to the note?", LEVELS),
    style=choice("What is the dominant style described?",
                 {"fruit": "Fruit-forward", "oak": "Oak-driven", "mineral": "Mineral, savoury", "other": None}),
    ageing=yes_no("Does the note say the wine will improve with age?"),
)
DATA_OK = {"parts": {"data": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}

IMAGES = Path(__file__).resolve().parent / "images"
IMAGES_CHANGE = "changes/2026-10-14-jev-images.md"


def red_circle():
    return image(data=(IMAGES / "red-circle.png").read_bytes(), media_type="image/png")


def blue_square():
    return image(data=(IMAGES / "blue-square.jpg").read_bytes(), media_type="image/jpeg")


BOX_CHANGE = "changes/2026-10-15-bounding-box.md"
BOX_MODEL = "jev-preview"  # docs.typesafe.ai/primitives/box: "Box questions need Jev 1.14"
SHAPES_BOXES = judgments(
    red=bounding_box("the red square in the image"),
    blue=bounding_box("the blue circle in the image"),
    has_red=yes_no("Is there a red square in the image?"),
)


def shapes():
    return image(data=(IMAGES / "shapes.png").read_bytes(), media_type="image/png")


def box_cases(force: bool, want) -> list[dict]:
    rows = []
    entry, cap.change_entry = cap.change_entry, BOX_CHANGE
    try:
        if want("judgments_box"):
            rows.append(cap.write_case(
                "judgments_box",
                Request(model=BOX_MODEL, messages=(Message.user(shapes()),),
                        config=Config(response_format=SHAPES_BOXES, probabilities="if_available")),
                stream=False,
                description="Two bounding-box judgments and a yes/no over one image (D1-D3): each box is a Jev Box "
                            "question (no criteria), the header goes with it, the answer's box is the value verbatim "
                            "with no distribution; the yes/no keeps its distribution",
                expect_lm15=DATA_OK,
                evidence_note="changes/2026-10-15-bounding-box.md D1-D3; docs.typesafe.ai/primitives/box",
                force=force))
        if want("judgments_box_text_state"):
            rows.append(cap.write_case(
                "judgments_box_text_state",
                Request(model=BOX_MODEL, messages=(Message.user("A kitchen with a coffee mug."),),
                        config=Config(response_format=judgments(mug=bounding_box("the coffee mug")))),
                stream=False,
                description="A box question with no image in the request (D2, D5): the opt-in header still goes with it "
                            "(the gate covers Box questions), lm15 does not refuse the unanswerable question, and Jev "
                            "answers a box around most of the frame with a confidence near 0",
                expect_lm15=DATA_OK,
                evidence_note="changes/2026-10-15-bounding-box.md D2/D5; probe error-box-header-off is this request without the header",
                force=force))
    finally:
        cap.change_entry = entry
    return rows


def box_probes(want) -> list[dict]:
    rows = []
    request = Request(model=BOX_MODEL, messages=(Message.user(shapes()),),
                      config=Config(response_format=judgments(red=bounding_box("the red square in the image"))))
    if want("box-on-jev-latest"):
        # Box needs Jev 1.14; jev-latest is 1.13 today and answers a bare 400.
        rows.append(cap.probe("box-on-jev-latest", Request(model="jev-latest", messages=request.messages, config=request.config)))
    if want("box-without-image"):
        # No image in the request: a 200 with a box around the whole frame and a low confidence.
        rows.append(cap.probe("box-without-image", Request(model=BOX_MODEL, messages=(Message.user("A kitchen with a coffee mug."),),
                                                          config=request.config)))
    if want("error-box-header-off"):
        # The gate covers Box questions too, with or without an image (D2).
        rows.append(cap.probe("error-box-header-off", Request(model=BOX_MODEL, messages=(Message.user("A kitchen with a coffee mug."),),
                                                             config=request.config),
                              headers={"Authorization": f"Bearer {cap.key()}", "TypeSafe-Danger-Zone-Images": None}))
    return rows


def image_cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    entry, cap.change_entry = cap.change_entry, IMAGES_CHANGE
    try:
        if want("judgments_image_state"):
            rows.append(cap.write_case(
                "judgments_image_state",
                Request(model=model, messages=(Message.user(red_circle()),),
                        config=Config(response_format=judgments(
                            shape=choice("What shape is drawn in the image?",
                                         {"circle": None, "square": None, "triangle": None}),
                            red=yes_no("Is the shape red?")),
                            probabilities="if_available")),
                stream=False,
                description="One user image part is the state (D1): the state is its reference string, the PNG bytes "
                            "an asset under that reference; the request carries TypeSafe-Danger-Zone-Images: true (D3)",
                expect_lm15=DATA_OK,
                evidence_note="changes/2026-10-14-jev-images.md D1/D3; docs.typesafe.ai/images 'Sending images in a request'",
                force=force))
        if want("judgments_image_parts"):
            rows.append(cap.write_case(
                "judgments_image_parts",
                Request(model=model, messages=(Message.user(["Listing: a red ball.", red_circle(), blue_square()]),),
                        config=Config(response_format=judgments(
                            first_matches=yes_no("Does the first image match the listing?"),
                            second_blue=yes_no("Is the shape in `[2]` a blue square?"),
                            same_shape=yes_no("Do the two images show the same shape?")),
                            probabilities="if_available")),
                stream=False,
                description="A user message holding images beside other parts is the array of its parts in order (D2): "
                            "text verbatim, each image its reference; a PNG and a JPEG asset; a backtick path reaches an element",
                expect_lm15=DATA_OK,
                evidence_note="changes/2026-10-14-jev-images.md D2/D3; docs.typesafe.ai/images 'State'",
                force=force))
    finally:
        cap.change_entry = entry
    return rows


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("judgments"):
        rows.append(cap.write_case(
            "judgments",
            Request(model=model, messages=(Message.user("Tasting note:\n" + NOTE),),
                    config=Config(response_format=WINE, probabilities="if_available")),
            stream=False,
            description="Three judgments (10-level ordered, choice with descriptions, yes/no) from one json_schema request → one systemone call; "
                        "string state from the single user text part (D6); answers → DataPart with probabilities, method provider_classification",
            expect_lm15=DATA_OK,
            evidence_note="MAP-14 §2 mapping (boolean→noul, string→choice, ordered→score); changes/2026-09-17-judgments.md D5/D6",
            force=force))
    if want("judgments_data_state"):
        rows.append(cap.write_case(
            "judgments_data_state",
            Request(model=model, messages=(Message.user(data({"tasting_note": NOTE, "producer": "unknown"})),),
                    config=Config(response_format=judgments(
                        ageing=yes_no("Does `tasting_note` say the wine will improve with age?")))),
            stream=False,
            description="A single user DataPart is the state object verbatim (D6): backticked paths in instructions resolve against it",
            expect_lm15=DATA_OK,
            evidence_note="changes/2026-09-17-judgments.md D2/D6",
            force=force))
    if want("judgments_context_key"):
        # What a system prompt becomes on Jev (2026-09-19 D2): a named key of the state, written by the caller.
        rows.append(cap.write_case(
            "judgments_context_key",
            Request(model=model, messages=(Message.user(data({
                "instructions": "These are tasting notes written by a sommelier. Judge the wine described, not the writing.",
                "note": NOTE, "price_eur": 48})),),
                    config=Config(response_format=judgments(
                        quality=score("How good is the wine in `note`, for its `price_eur`, read as `instructions` says?", LEVELS),
                        ageing=yes_no("Does `note` say the wine will improve with age?")),
                        probabilities="if_available")),
            stream=False,
            description="A user data object is the state verbatim (D1): the caller's context rides as a named key beside the content, "
                        "and questions point at keys with backtick paths — Jev's own idiom for what a system prompt would carry",
            expect_lm15=DATA_OK,
            evidence_note="changes/2026-09-19-jev-state.md D1/D2; docs.typesafe.ai/primitives 'Reference specific fields'",
            force=force))
    if want("judgments_array_state"):
        rows.append(cap.write_case(
            "judgments_array_state",
            Request(model=model, messages=(Message.user(data(["Hi", "My customer number is TS1337.", "My card was charged twice for order A-104."])),),
                    config=Config(response_format=judgments(
                        refund_requested=yes_no("Does the customer ask for a refund?"),
                        department=choice("Which team should handle this?", {"billing": "Payment or subscription issues", "technical": "Bugs or integration problems", "sales": "Pricing or account questions"})),
                        probabilities="if_available")),
            stream=False,
            description="A user data array is the state verbatim (D1): a sequence of messages as docs.typesafe.ai/concepts/state shows it",
            expect_lm15=DATA_OK,
            evidence_note="changes/2026-09-19-jev-state.md D1",
            force=force))
    rows += image_cases(model, force, want)
    rows += box_cases(force, want)
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    base = Request(model=model, messages=(Message.user(NOTE),), config=Config(response_format=WINE))
    if want("error-unauthenticated"):
        rows.append(cap.probe("error-unauthenticated", base, headers={"Authorization": "Bearer apikey_invalid"}))
    if want("error-unknown-model"):
        rows.append(cap.probe("error-unknown-model", Request(model="no-such-model", messages=base.messages, config=base.config)))
    if want("error-validation"):
        rows.append(cap.probe("error-validation", base, raw_body={"model": model, "state": NOTE,
                                                                  "questions": {"q": {"type": "choice", "instructions": "x"}}}))
    if want("error-images-off"):
        # The documented gate, live: the same image request with the opt-in header removed.
        image_request = Request(model=model, messages=(Message.user(red_circle()),),
                                config=Config(response_format=judgments(red=yes_no("Is the shape red?"))))
        rows.append(cap.probe("error-images-off", image_request, headers={"Authorization": f"Bearer {cap.key()}", "TypeSafe-Danger-Zone-Images": None}))
    if want("pinned-version"):
        rows.append(cap.probe("pinned-version", Request(model="jev-1.13.0", messages=base.messages, config=base.config)))
    rows += box_probes(want)
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "unknown-model", "validation"))
