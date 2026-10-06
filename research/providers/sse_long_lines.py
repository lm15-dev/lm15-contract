#!/usr/bin/env python3
"""How long does a single server-sent-events line or event get, live?
(changes/2026-10-06-sse-event-bound.md, INV-056)

Every SDK refused an SSE line over 64 KiB and an event over 1 MiB.  A user's
long OpenAI Responses answer failed at the last moment with
``SSE line exceeds limit (68021 > 65536)``.  This script measures the
servers instead of guessing.

``--probe``   Streams that are expected to carry one large line each, sent
              verbatim, measured line by line.  Receipts only (exchange
              receipt with hashes + a size table per event type); the bodies
              of the image probes are several MB of base64 and are NOT kept
              in the repository (hash and size are recorded instead).

              responses-instructions  gpt-4.1-mini, 72 KB system prompt, a
                                      one-word answer: Responses echoes the
                                      whole response object (instructions
                                      included) in response.created,
                                      response.in_progress and
                                      response.completed.
              responses-image         gpt-4.1-mini + the image_generation
                                      tool, high quality 1536x1024: the image
                                      in response.output_item.done and again
                                      in response.completed.
              gemini-image-4k         gemini-3-pro-image, imageSize 4K,
                                      streamGenerateContent: the image in one
                                      data line.

``--capture`` One case, ``cases/openai/streaming_long_line.json``, built by
              the reference adapter and pinned verbatim: the same request
              as responses-instructions with a bilingual system prompt of 1,000,000 characters (1.1 MB
              of UTF-8, under OpenAI's 1,048,576-character cap), so
              three echo lines are each over 1 MiB and one fixture pins
              both former limits (64 KiB per line, 1 MiB per event).  A
              first capture pair (the 72 KB stream, 0.23 MB, and a
              gemini-2.5-flash-image stream with its 2.67 MB image line)
              is kept as receipts only: as cases they would have added
              about 11 MB to the corpus (the reference's golden writes a
              Gemini image three times), for no fact the 1.1 MB case does
              not pin.

    set -a; source ../.env; set +a
    python3 research/providers/sse_long_lines.py --probe [--only responses-instructions,...]
    python3 research/providers/sse_long_lines.py --capture [--force]

Receipts: ``receipts/2026-10-06-sse-long-lines/<provider>/``.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, Capture, now_ts  # noqa: E402
from lm15 import BuiltinTool, Config, Message, Request  # noqa: E402

RECEIPTS = CONTRACT / "receipts" / "2026-10-06-sse-long-lines"
CHANGE = "sse-event-bound"


JAPANESE = {"monarch butterfly": "オオカバマダラ", "arctic tern": "キョクアジサシ", "humpback whale": "ザトウクジラ",
            "leatherback turtle": "オサガメ", "bar-tailed godwit": "オオソリハシシギ", "caribou": "カリブー",
            "wildebeest": "ヌー", "european eel": "ヨーロッパウナギ", "sockeye salmon": "ベニザケ",
            "ruby-throated hummingbird": "ノドアカハチドリ", "christmas island red crab": "クリスマスアカガニ",
            "desert locust": "サバクトビバッタ"}


def long_system_prompt(target_chars: int = 72 * 1024, *, japanese: bool = False) -> str:
    """A deterministic reference sheet, long enough that its echo alone puts
    one SSE line over a limit.  Real prompts of this size are ordinary:
    few-shot demonstrations, a retrieved document, a style guide.

    ``japanese`` adds each animal's Japanese name.  OpenAI caps
    ``instructions`` at 1,048,576 characters; a line over 1 MiB of bytes
    needs characters wider than one byte, which a bilingual sheet has."""
    animals = list(JAPANESE)
    lines = ["You are a field-guide assistant. The reference sheet below lists migration notes; "
             "answer only what the user asks."]
    i = 0
    total = len(lines[0]) + 1
    while total < target_chars:
        animal = animals[i % len(animals)]
        name = f"{animal} ({JAPANESE[animal]})" if japanese else animal
        lines.append(f"Note {i + 1:04d}: the {name} is recorded at survey station {(i * 37) % 997:03d}, "
                     f"season {1 + i % 4}, with {(i * 13) % 211 + 5} individuals counted and no tag recovered.")
        total += len(lines[-1]) + 1
        i += 1
    return "\n".join(lines)


SYSTEM = long_system_prompt()
INSTRUCTIONS_REQUEST = Request(
    model="gpt-4.1-mini",
    system=SYSTEM,
    messages=(Message.user("Reply with the single word OK."),),
    config=Config(max_tokens=16),
)
IMAGE_PROMPT = ("A detailed photograph of a busy coral reef at midday: dozens of fish species, "
                "sea turtles, fine sand texture, light rays through the water, sharp focus everywhere.")


def measure(raw: bytes) -> dict:
    """Per event type: the longest line (bytes, terminator excluded) and the
    longest event (bytes from its first line to the blank line, inclusive)."""
    by_type: dict[str, dict] = {}
    longest_line = 0
    longest_event = 0
    event_bytes = 0
    lines = 0
    current_type = None
    for line in raw.split(b"\n"):
        lines += 1
        size = len(line.rstrip(b"\r"))
        longest_line = max(longest_line, size)
        event_bytes += len(line) + 1
        if line.startswith(b"data:"):
            m = re.match(rb'data:\s*\{"type"\s*:\s*"([^"]+)"', line)
            current_type = m.group(1).decode() if m else ("(gemini chunk)" if b'"candidates"' in line[:200] else "(data)")
            row = by_type.setdefault(current_type, {"count": 0, "longest_line": 0})
            row["count"] += 1
            row["longest_line"] = max(row["longest_line"], size)
        if line.strip() == b"":
            longest_event = max(longest_event, event_bytes)
            event_bytes = 0
    longest_event = max(longest_event, event_bytes)
    return {"body_bytes": len(raw), "lines": lines, "longest_line": longest_line,
            "longest_event": longest_event, "by_type": by_type}


def openai_cap(dry: bool) -> Capture:
    cap = Capture("openai", env_var="OPENAI_API_KEY", default_model="gpt-4.1-mini", host="api.openai.com",
                  change_slug=CHANGE)
    cap.receipts = RECEIPTS / "openai"
    cap.dry_run = dry
    return cap


def gemini_cap(dry: bool) -> Capture:
    cap = Capture("gemini", env_var="GEMINI_API_KEY", default_model="gemini-3-pro-image",
                  host="generativelanguage.googleapis.com", change_slug=CHANGE)
    cap.receipts = RECEIPTS / "gemini"
    cap.dry_run = dry
    return cap


def probe(name: str, dry: bool) -> dict:
    if name == "responses-instructions":
        cap = openai_cap(dry)
        treq = cap.lm().build_request(INSTRUCTIONS_REQUEST, stream=True)
        keep_body = True
    elif name == "responses-image":
        cap = openai_cap(dry)
        request = Request(model="gpt-4.1-mini", messages=(Message.user(IMAGE_PROMPT + " Generate the image."),),
                          tools=(BuiltinTool("image_generation", {"quality": "high", "size": "1536x1024"}),),
                          config=Config(max_tokens=2048))
        treq = cap.lm().build_request(request, stream=True)
        keep_body = False
    elif name == "gemini-image-4k":
        cap = gemini_cap(dry)
        request = Request(model="gemini-3-pro-image", messages=(Message.user(IMAGE_PROMPT),),
                          config=Config(extensions={"output": "image"}))
        treq = cap.lm().build_request(request, stream=True)
        body = json.loads(treq.body)
        # The one raw patch: ask for the largest size the model offers.
        body.setdefault("generationConfig", {}).setdefault("imageConfig", {})["imageSize"] = "4K"
        treq.body = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode()
        keep_body = False
    else:
        raise SystemExit(f"unknown probe {name}")
    started = time.monotonic()
    status, raw, ts, _ = cap.send(treq)
    row = {"probe": name, "status": status, "timestamp": ts, "seconds": round(time.monotonic() - started, 1),
           "exchange": getattr(cap, "last_exchange", None)}
    if dry:
        return row
    row.update(measure(raw) if status == 200 else {"body_head": cap.redact(raw.decode("utf-8", "replace"))[:400]})
    if status == 200 and keep_body:
        cap.write_receipt(f"probe-{name}-{ts}-response.txt", raw.decode("utf-8"))
    cap.write_receipt(f"probe-{name}-{ts}-sizes.json", row)
    return row


CASE_REQUEST = Request(
    model="gpt-4.1-mini",
    system=long_system_prompt(1_000_000, japanese=True),
    messages=(Message.user("Reply with the single word OK."),),
    config=Config(max_tokens=16),
)


def capture(force: bool, dry: bool) -> list[dict]:
    cap = openai_cap(dry)
    return [cap.write_case(
        "streaming_long_line", CASE_REQUEST, stream=True,
        description=("INV-056: a bilingual system prompt of 1,000,000 characters (1.1 MB) is echoed by Responses in response.created, "
                     "response.in_progress and response.completed: three SSE lines, each over the former "
                     "64 KiB line and 1 MiB event limits; the stream parses to the one-word answer"),
        expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
        evidence_note=f"changes/2026-10-06-{CHANGE}.md (INV-056)",
        force=force)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", action="store_true")
    mode.add_argument("--capture", action="store_true")
    ap.add_argument("--only", help="comma-separated probe names")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    names = ["responses-instructions", "responses-image", "gemini-image-4k"]
    if args.only:
        names = [n for n in names if n in set(args.only.split(","))]
    rows = [probe(n, args.dry_run) for n in names] if args.probe else capture(args.force, args.dry_run)
    for row in rows:
        print(json.dumps({k: v for k, v in row.items() if k != "by_type"}, ensure_ascii=False))
        if "by_type" in row:
            for kind, info in sorted(row["by_type"].items(), key=lambda kv: -kv[1]["longest_line"])[:6]:
                print(f"    {kind:45s} x{info['count']:<5d} longest line {info['longest_line']:>10,d} B")
    if not args.dry_run:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        text = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
        for env in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
            if os.environ.get(env):
                text = text.replace(os.environ[env], f"${env}")
        (RECEIPTS / f"SUMMARY-{'probe' if args.probe else 'capture'}-{now_ts()}.json").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
