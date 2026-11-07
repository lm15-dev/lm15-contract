#!/usr/bin/env python3
"""Anthropic thinking display, by model: whether thinking text comes back
without asking, and with ``display: "summarized"`` — live probes for the
MAP-7 rule 7 amendment (changes/2026-11-07-anthropic-thinking-display.md).

Why: on 2026-11-07 a FunctAI user on claude-opus-5-5 asked lm15 for
reasoning with a summary (``Reasoning(effort, summary="auto")``) and got a
thinking block with empty text. MAP-7 rule 7 says Anthropic returns
thinking whenever thinking runs, so ``summary`` sends nothing there.
Anthropic's thinking page (fetched 2026-11-07) says ``display`` defaults
to ``"omitted"`` on Opus 4.7, 4.8 and every Claude 5 model.

Per model, raw bodies (the adapter's URL and headers):

- ``<model>-default``: thinking on in the model's own form (adaptive +
  output_config.effort, or enabled + budget_tokens), no ``display``;
- ``<model>-summarized``: the same with ``display: "summarized"``;
- ``<model>-absent`` (Claude 5 only): no ``thinking`` object at all
  (the docs: "thinking is already on" on Claude 5);
- ``<model>-disabled`` (Claude 5 only): ``thinking: {type: disabled}``.

    set -a; . ../.env; set +a
    python3 research/providers/thinking_display.py [--dry-run] [--only claude-opus-5-5,...]
    python3 research/providers/thinking_display.py --cases [--force]   # the cases, built by the reference

``--cases`` pins what the amended rule sends: ``Reasoning(summary="auto")``
built by the reference adapter, on the adaptive class (complete and
streamed) and on the manual class.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, Capture  # noqa: E402
from lm15 import Config, Message, Request  # noqa: E402
from lm15.types import Reasoning  # noqa: E402

SLUG = "anthropic-thinking-display"
PROMPT = "Pens cost 3, notebooks 7. I spent 50 on at least one of each. How many pens at most? Answer with the number only."
# For models that chose not to think on PROMPT at low effort (adaptive: the model decides).
HARD = ("Find every pair of positive integers (a, b) with a <= b such that a*b + a + b = 2026 and gcd(a, b) = 1. "
        "Answer with the list only.")
ADAPTIVE = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-1", "claude-opus-5",
            "claude-sonnet-5", "claude-fable-5", "claude-opus-4-8", "claude-opus-4-7", "claude-sonnet-4-6",
            "claude-opus-4-6"]
MANUAL = ["claude-opus-4-5-20251101", "claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"]
CLAUDE5 = [m for m in ADAPTIVE if "-4-" not in m]


def body(model: str, thinking: dict | None, *, effort: bool, level: str = "low", prompt: str = PROMPT) -> dict:
    out: dict = {"model": model, "max_tokens": 8000,
                 "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]}
    if thinking is not None:
        out["thinking"] = thinking
    if effort:
        out["output_config"] = {"effort": level}
    return out


def shape(cap: Capture, name: str) -> dict:
    """What the receipt shows: the status, each block's type and text length, the thinking tokens."""
    path = cap.receipts / f"probe-{name}.json"
    if not path.exists():
        return {}
    got = json.loads(path.read_text(encoding="utf-8"))
    b = got["body"]
    if not isinstance(b, dict) or "content" not in b:
        return {"status": got["status"], "error": (b.get("error", {}) if isinstance(b, dict) else {}).get("message", str(b)[:200])}
    blocks = [(x["type"], len(x.get("thinking") or x.get("text") or "")) for x in b["content"]]
    usage = b.get("usage", {})
    details = usage.get("output_tokens_details") or {}
    return {"status": got["status"], "blocks": blocks, "output_tokens": usage.get("output_tokens"),
            "thinking_tokens": details.get("thinking_tokens")}


CASES = [
    ("reasoning_summary", "claude-opus-5-5", False,
     "Reasoning with a summary on the adaptive class: thinking.display \"summarized\" (MAP-7 rule 7, amended "
     "2026-11-07); without it Opus 5.5 returns a thinking block with empty text"),
    ("streaming_reasoning_summary", "claude-opus-5-5", True,
     "The same, streamed: the summary arrives as thinking_delta events (MAP-7 rule 7, amended 2026-11-07)"),
    ("reasoning_summary_budget", "claude-haiku-4-5-20251001", False,
     "Reasoning with a summary on the manual class: budget_tokens with display \"summarized\" (MAP-7 rule 7, "
     "amended 2026-11-07; the model's default is already summarized, the knob is sent the same way)"),
]


def write_cases(cap: Capture, force: bool) -> list[dict]:
    rows = []
    for feature, model, stream, description in CASES:
        request = Request(model=model, messages=(Message.user(PROMPT),),
                          config=Config(max_tokens=3000, reasoning=Reasoning(effort="low", summary="auto")))
        row = cap.write_case(feature, request, stream=stream, description=description,
                             expect_lm15={"parts": {"thinking": {"min": 1}, "text": {"min": 1}}, "finish_reason": "stop"},
                             evidence_note="Reasoning(effort low, summary auto); the thinking block's text is non-empty",
                             force=force)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False, default=str)[:400], flush=True)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--hard", action="store_true", help="HARD at effort high, default and summarized only")
    ap.add_argument("--cases", action="store_true", help="write the cases (reference-built wire)")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    only = {m for m in args.only.split(",") if m}
    cap = Capture("anthropic", env_var="ANTHROPIC_API_KEY", default_model="claude-opus-5-5", host="api.anthropic.com",
                  change_slug=SLUG)
    cap.dry_run = args.dry_run
    cap.receipts = CONTRACT / "receipts" / f"{cap.date}-{SLUG}" / "anthropic"
    if args.cases:
        write_cases(cap, args.force)
        return
    rows = []
    for model in ADAPTIVE + MANUAL:
        if only and model not in only:
            continue
        on = {"type": "adaptive"} if model in ADAPTIVE else {"type": "enabled", "budget_tokens": 1024}
        tries = [("default", on, model in ADAPTIVE),
                 ("summarized", {**on, "display": "summarized"}, model in ADAPTIVE)]
        if args.hard:
            tries = tries[:2]
        elif model in CLAUDE5:
            tries += [("absent", None, False), ("disabled", {"type": "disabled"}, False)]
        for label, thinking, effort in tries:
            name = f"{model}-{label}" + ("-hard" if args.hard else "")
            row = cap.probe(name, raw_body=body(model, thinking, effort=effort, level="high" if args.hard else "low",
                                                prompt=HARD if args.hard else PROMPT))
            row.update(shape(cap, name))
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    if not args.dry_run:
        cap.write_receipt(f"SUMMARY-{cap.date}{'-hard' if args.hard else ''}.json", rows)


if __name__ == "__main__":
    main()
