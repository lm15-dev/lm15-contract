#!/usr/bin/env python3
"""Gemini on Google Cloud, express mode (`vertex-express`) — case declarations.

Machinery: ``research/providers/_capture.py``.  Receipts: ``receipts/<date>-vertex-express/``.
An API key and nothing else: no project, no location, the key as ``?key=``
(vertex-express-mode.md:84, :181).

    GOOGLE_API_KEY=... python3 research/providers/vertex-express/capture.py [--dry-run] [--force]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import Capture  # noqa: E402
from lm15 import Config, Message, Request  # noqa: E402

cap = Capture("vertex-express", env_var="GOOGLE_API_KEY", default_model="gemini-2.5-flash", host="aiplatform.googleapis.com",
              change_slug="vertex-live")
SAY = (Message.user("Say ok."),)
TEXT_OK = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("basic_text"):
        rows.append(cap.write_case("basic_text", Request(model=model, messages=SAY, config=Config(max_tokens=400)), stream=False,
            description="Vertex express: generateContent with ?key= and no project", expect_lm15=TEXT_OK,
            evidence_note="Vertex API key bound to a service account", force=force))
    if want("streaming"):
        rows.append(cap.write_case("streaming", Request(model=model, messages=SAY, config=Config(max_tokens=400)), stream=True,
            description="Vertex express: streamGenerateContent?alt=sse&key=", expect_lm15=None, evidence_note="SSE", force=force))
    return rows


if __name__ == "__main__":
    cap.main(cases, lambda model, want: [])
