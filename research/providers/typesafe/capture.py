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
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import Capture  # noqa: E402
from lm15 import Config, Message, Request  # noqa: E402
from lm15.judgments import choice, judgments, score, yes_no  # noqa: E402
from lm15.types import data  # noqa: E402

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
    if want("pinned-version"):
        rows.append(cap.probe("pinned-version", Request(model="jev-1.13.0", messages=base.messages, config=base.config)))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes, error_probes=("unauthenticated", "unknown-model", "validation"))
