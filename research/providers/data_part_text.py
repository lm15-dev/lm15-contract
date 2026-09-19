#!/usr/bin/env python3
"""D3 of changes/2026-09-19-jev-state.md, live on every chat wire: a data
part in a user message reaches a text-only wire as its compact JSON, and
the model answers the declared judgments about it.

Machinery: ``research/providers/_capture.py``.  One case per wire, the
same request everywhere (a `{note, price_eur}` object and two judgments):

    OPENAI_API_KEY=… GROQ_API_KEY=… ANTHROPIC_API_KEY=… GEMINI_API_KEY=… \\
        python3 research/providers/data_part_text.py [--dry-run] [--only openai,groq] [--force]

Receipts: ``receipts/2026-09-19-<provider>/``; cases ``cases/<provider>/data_part_text.json``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import Capture  # noqa: E402
from lm15 import Config, Message, Request  # noqa: E402
from lm15.judgments import judgments, score, yes_no  # noqa: E402
from lm15.types import data  # noqa: E402

NOTE = ("Ripe blackberry and cassis lead, framed by toasty oak and firm, fine-grained tannins. "
        "Long, layered finish with graphite and dried herbs. Impressive now; will reward a decade in the cellar.")
VALUE = {"note": NOTE, "price_eur": 48}
QUESTIONS = judgments(
    quality=score("How good is the wine in `note`?", {"faulty": "Faulty or unpleasant", "simple": "Simple and sound",
                                                      "good": "Good, well made", "excellent": "Excellent, complex and structured",
                                                      "profound": "Profound, exceptional"}),
    ageing=yes_no("Does `note` say the wine will improve with age?"),
)
WIRES = {
    "openai": ("OPENAI_API_KEY", "gpt-5-mini", "api.openai.com", "input_text"),
    "groq": ("GROQ_API_KEY", "openai/gpt-oss-20b", "api.groq.com", "a plain string"),
    "anthropic": ("ANTHROPIC_API_KEY", "claude-haiku-4-5", "api.anthropic.com", "text"),
    "gemini": ("GEMINI_API_KEY", "gemini-2.5-flash", "generativelanguage.googleapis.com", "text"),
}
DATA_OK = {"parts": {"data": {"min": 1}}, "finish_reason": "stop"}


def main() -> None:
    ap = argparse.ArgumentParser(description="D3 live capture on every chat wire")
    ap.add_argument("--only", help="comma-separated providers")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    chosen = set(args.only.split(",")) if args.only else set(WIRES)
    rows = []
    for provider, (env, model, host, slot) in WIRES.items():
        if provider not in chosen:
            continue
        cap = Capture(provider, env_var=env, default_model=model, host=host, change_slug="jev-state")
        cap.dry_run = args.dry_run
        request = Request(model=model, messages=(Message.user(data(VALUE)),),
                          config=Config(response_format=QUESTIONS, probabilities="if_available"))
        rows.append(cap.write_case(
            "data_part_text", request, stream=False,
            description=f"A user data part reaches this wire as its compact JSON in a {slot} slot (D3), and the model answers "
                        "the declared judgments about the object's keys; probabilities are recorded dropped where the wire measures none",
            expect_lm15=DATA_OK,
            evidence_note="changes/2026-09-19-jev-state.md D3; types.md §DataPart ('JSON text on wires that take only text')",
            force=args.force))
        if not args.dry_run:
            cap.write_receipt("SUMMARY.json", rows[-1])
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
