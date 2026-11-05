#!/usr/bin/env python3
"""Every kind of thing a pinned stream body carries has a decision.

Reads every pinned stream body (cases with a stream body, the same
classification as harness/check.py) and lists, per dialect, the kinds it
carries: event types, block and delta types, chunk, choice, delta,
candidate and part keys (mapping/stream-events.json `_doc` says exactly
which). Fails when:

- a body carries a kind `mapping/stream-events.json` does not list: a new
  event or key is a decision (read, duplicate of what, ignored why) made in
  the table before a case pins it — the 2026-11-05 Codex finding was a
  duplicate-looking event (`response.function_call_arguments.done`) that
  was the only carrier of the arguments;
- a body carries a kind the table marks `gap` (content the complete path
  reads and the stream path drops): a pinned stream then loses content;
- a `duplicate` row names, in `of`, a kind the table does not list;
- a row has a status outside read / duplicate / ignored / gap, or misses
  the field its status needs (`as`, `of`, `why`).

Rows no pinned body carries are listed as unpinned (documented behaviour
the corpus does not show), not failed.

Usage: python3 tools/check_stream_events.py [--list]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CONTRACT / "harness"))

import check  # noqa: E402
import stream_checks  # noqa: E402

TABLE = CONTRACT / "mapping" / "stream-events.json"
NEEDS = {"read": "as", "duplicate": "of", "ignored": "why", "gap": "why"}


def kinds(dialect: str, p: dict) -> list[str]:
    out: list[str] = []
    if dialect == "responses":
        t = str(p.get("type"))
        out.append(t)
        if t in ("response.output_item.added", "response.output_item.done") and isinstance(p.get("item"), dict):
            out.append(f"{t}:{p['item'].get('type')}")
    elif dialect == "anthropic":
        t = str(p.get("type"))
        out.append(t)
        if t == "content_block_start" and isinstance(p.get("content_block"), dict):
            out.append(f"{t}:{p['content_block'].get('type')}")
        if t == "content_block_delta" and isinstance(p.get("delta"), dict):
            out.append(f"{t}:{p['delta'].get('type')}")
    elif dialect == "chat":
        out += [f"chunk.{k}" for k, v in p.items() if v is not None and k != "choices"]
        for choice in p.get("choices") or []:
            if not isinstance(choice, dict):
                continue
            out += [f"choice.{k}" for k, v in choice.items() if v is not None and k != "delta"]
            delta = choice.get("delta")
            if isinstance(delta, dict):
                out += [f"delta.{k}" for k, v in delta.items() if v is not None and v != ""]
    elif dialect == "gemini":
        out += [f"chunk.{k}" for k, v in p.items() if v is not None and k != "candidates"]
        for cand in p.get("candidates") or []:
            if not isinstance(cand, dict):
                continue
            out += [f"candidate.{k}" for k, v in cand.items() if v is not None and k != "content"]
            content = cand.get("content")
            for part in (content.get("parts") if isinstance(content, dict) else None) or []:
                if isinstance(part, dict):
                    out += [f"part.{k}" for k in part]
    return out


def seen_kinds() -> tuple[dict[str, dict[str, set[str]]], list[str]]:
    seen: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    unread: list[str] = []
    for case in check.load_wire_cases():
        if "pinned_body" not in case or not check.is_stream_case(case) or case.get("framing"):
            continue
        dialect = stream_checks.dialect_of(case)
        frames = stream_checks.parse_frames(check.pinned_body(case)) if dialect else None
        if frames is None:
            unread.append(case["id"])
            continue
        for frame in frames:
            if frame.payload is not None:
                for kind in kinds(dialect, frame.payload):
                    seen[dialect][kind].add(case["id"])
    return seen, unread


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print every kind with the cases that carry it")
    args = ap.parse_args(argv)
    table = json.loads(TABLE.read_text(encoding="utf-8"))["dialects"]
    seen, unread = seen_kinds()
    problems: list[str] = []
    for dialect, rows in table.items():
        for kind, row in rows.items():
            status = row.get("status")
            if status not in NEEDS:
                problems.append(f"{dialect} {kind}: status {status!r} is not one of {sorted(NEEDS)}")
            elif not row.get(NEEDS[status]):
                problems.append(f"{dialect} {kind}: a {status} row needs `{NEEDS[status]}`")
            if status == "duplicate":
                target = str(row.get("of", "")).split(" ", 1)[0]
                if target not in rows:
                    problems.append(f"{dialect} {kind}: duplicate of {target!r}, which the table does not list")
    for dialect in sorted(seen):
        rows = table.get(dialect, {})
        for kind in sorted(seen[dialect]):
            cases = sorted(seen[dialect][kind])
            row = rows.get(kind)
            if row is None:
                problems.append(f"{dialect} {kind}: carried by {', '.join(cases[:3])}{'…' if len(cases) > 3 else ''}, "
                                "not in mapping/stream-events.json")
            elif row.get("status") == "gap":
                problems.append(f"{dialect} {kind}: a gap (the stream path drops it) carried by {', '.join(cases)}")
            if args.list:
                print(f"{dialect:9} {kind:48} {row.get('status') if row else 'MISSING':9} {len(cases)} case(s)")
    unpinned = [f"{d} {k}" for d, rows in table.items() for k in rows if k not in seen.get(d, {})]
    for case_id in unread:
        problems.append(f"{case_id}: stream body of no known dialect, or not UTF-8 SSE")
    if unpinned:
        print(f"unpinned rows (documented, no pinned body carries them): {len(unpinned)}")
        for row in unpinned:
            print(f"  {row}")
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"check_stream_events: {len(problems)} problem(s)")
        return 1
    total = sum(len(v) for v in seen.values())
    print(f"check_stream_events: OK ({total} kind(s) carried by pinned stream bodies, every one decided)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
