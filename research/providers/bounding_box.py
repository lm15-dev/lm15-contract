#!/usr/bin/env python3
"""Bounding-box judgments on the generated-JSON wires, live
(changes/2026-10-15-bounding-box.md D2).

The same request on every wire: ``typesafe/images/shapes.png`` (a red
square at top 0.20, bottom 0.60, left 0.55, right 0.85; a blue circle at
top 0.583, bottom 0.917, left 0.10, right 0.35), two ``bounding_box``
judgments and a ``yes_no``.  The schema goes verbatim (INV-050): the
helper's edges are plain ``number`` with the range in their descriptions.

    ANTHROPIC_API_KEY=… python3 research/providers/bounding_box.py --only anthropic
    GOOGLE_CLOUD_PROJECT=lm15-vertex-live python3 research/providers/bounding_box.py --only vertex   # the Google chain
    python3 research/providers/bounding_box.py --only openai-codex   # a ChatGPT sign-in; router receipt, no case

Cases ``cases/<provider>/judgments_box.json``; receipts
``receipts/<date>-<provider>/``.  The ``anthropic`` run also probes the
same schema with ``minimum``/``maximum`` on every edge (the reason the
helper writes neither).  ``openai-codex`` signs in with a subscription
the harness cannot replay, so it leaves a router-level receipt (request
schema and answer) and no case; the openai dialect's wire is pinned
offline by ``cases/openai/judgments`` (schema verbatim).
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, Capture, now_ts  # noqa: E402
from lm15 import Config, LMRouter, Message, Request, serde  # noqa: E402
from lm15.judgments import bounding_box, judgments, yes_no  # noqa: E402
from lm15.types import image  # noqa: E402

SHAPES = Path(__file__).resolve().parent / "typesafe" / "images" / "shapes.png"
QUESTIONS = judgments(
    red=bounding_box("the red square in the image"),
    blue=bounding_box("the blue circle in the image"),
    has_red=yes_no("Is there a red square in the image?"),
)
# The yes/no is unmeasured on these wires: if_available records the drop (MAP-14 §3).
DATA_OK = {"parts": {"data": {"min": 1}}, "finish_reason": "stop",
           "adaptations": [{"field": "config.probabilities", "action": "dropped", "asked": "if_available"}]}
DESCRIPTION = ("Two bounding-box judgments and a yes/no over one image on a generated-JSON wire (D2): the schema "
               "goes verbatim, the answer's JSON object is the DataPart value; no distribution is measured, so "
               "if_available records config.probabilities dropped (for the yes/no; a box asks for none)")


def request(model: str) -> Request:
    return Request(model=model, messages=(Message.user(image(data=SHAPES.read_bytes(), media_type="image/png")),),
                   config=Config(response_format=QUESTIONS, probabilities="if_available", max_tokens=2000))


def anthropic(force: bool, dry: bool) -> list[dict]:
    cap = Capture("anthropic", env_var="ANTHROPIC_API_KEY", default_model="claude-haiku-4-5",
                  host="api.anthropic.com", change_slug="bounding-box")
    cap.dry_run = dry
    rows = [cap.write_case("judgments_box", request("claude-haiku-4-5"), stream=False, description=DESCRIPTION,
                           expect_lm15=DATA_OK, evidence_note="changes/2026-10-15-bounding-box.md D2/D4", force=force)]
    bounded = copy.deepcopy(QUESTIONS)
    for prop in ("red", "blue"):
        for edge in bounded["schema"]["properties"][prop]["properties"].values():
            edge.update(minimum=0, maximum=1)
    probe = request("claude-haiku-4-5")
    rows.append(cap.probe("box-edge-bounds", Request(model=probe.model, messages=probe.messages,
                                                     config=Config(response_format=bounded, max_tokens=2000))))
    if not dry:
        cap.write_receipt("SUMMARY-bounding-box.json", rows)
    return rows


def vertex(force: bool, dry: bool) -> list[dict]:
    cap = Capture("vertex", env_var="VERTEX_API_KEY", default_model="gemini-2.5-flash", host="aiplatform.googleapis.com",
                  change_slug="bounding-box",
                  settings={"project": os.environ.get("GOOGLE_CLOUD_PROJECT", "lm15-vertex-live"), "location": "global"})
    cap.dry_run = dry
    cap.bearer_fixture()
    rows = [cap.write_case("judgments_box", request("gemini-2.5-flash"), stream=False, description=DESCRIPTION,
                           expect_lm15=DATA_OK, evidence_note="changes/2026-10-15-bounding-box.md D2; the gemini dialect on Vertex",
                           force=force)]
    if not dry:
        cap.write_receipt("SUMMARY-bounding-box.json", rows)
    return rows


def openai_codex(dry: bool) -> list[dict]:
    model = "openai-codex:gpt-5.6-luna"
    req = request(model)
    req = Request(model=model, messages=req.messages,  # this backend has no output cap and refuses max_tokens
                  config=Config(response_format=QUESTIONS, probabilities="if_available"))
    if dry:
        return [{"provider": "openai-codex", "dry_run": True}]
    response = LMRouter().complete(req)
    ts = now_ts()
    receipts = CONTRACT / "receipts" / f"{ts[:10]}-openai-codex"
    receipts.mkdir(parents=True, exist_ok=True)
    row = {"provider": "openai-codex", "model": model, "timestamp": ts, "finish_reason": response.finish_reason,
           "schema_sent": QUESTIONS["schema"], "answer": response.data,
           "parts": [p.type for p in response.message.parts],
           "usage": serde.usage_to_dict(response.usage) if response.usage else None,
           "adaptations": [{"field": a.field, "action": a.action} for a in response.adaptations],
           "note": "router-level receipt (subscription sign-in; not replayable by the harness); the Responses dialect "
                   "built the wire and the schema went verbatim"}
    (receipts / f"bounding-box-{ts}.json").write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    time.sleep(1.0)
    return [row]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="comma-separated: anthropic,vertex,openai-codex")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    chosen = set(args.only.split(",")) if args.only else {"anthropic", "vertex", "openai-codex"}
    rows: list[dict] = []
    if "anthropic" in chosen:
        rows += anthropic(args.force, args.dry_run)
    if "vertex" in chosen:
        rows += vertex(args.force, args.dry_run)
    if "openai-codex" in chosen:
        rows += openai_codex(args.dry_run)
    for row in rows:
        print(json.dumps(row, ensure_ascii=False, default=str)[:400])


if __name__ == "__main__":
    main()
