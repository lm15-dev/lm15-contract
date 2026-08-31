#!/usr/bin/env python3
"""Enforce fixture provenance in the lm15-contract corpus.

Every fixture must say where it came from. Rules:
- every JSON file under cases/   : top-level "provenance" block
- every JSON file under errors/  : top-level "provenance" block
- every JSON file under auth/    : top-level "provenance" block
- serde/canonical.json           : every entry in .cases[] has "provenance"

A provenance block is an object with:
  source   : one of {live-capture, migrated-apr29, hand-authored}
  date     : YYYY-MM-DD
  evidence : non-empty pointer (commit, live receipt, changes/ entry)

Exit non-zero on any violation. See AUTHORITY.md for when provenance may
change: wire fixtures only with a live-validation receipt, canonical
fixtures only with a spec citation.

Usage: check_provenance.py [--root DIR]   (default: the repo containing this script)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED_SOURCES = {"live-capture", "migrated-apr29", "hand-authored"}
REQUIRED_KEYS = {"source", "date", "evidence"}


def check_block(block, where: str, problems: list[str]) -> None:
    if not isinstance(block, dict):
        problems.append(f"{where}: missing or non-object provenance block")
        return
    missing = REQUIRED_KEYS - set(block)
    if missing:
        problems.append(f"{where}: provenance missing keys {sorted(missing)}")
        return
    if block["source"] not in ALLOWED_SOURCES:
        problems.append(f"{where}: provenance source {block['source']!r} not in {sorted(ALLOWED_SOURCES)}")
    if not str(block["evidence"]).strip():
        problems.append(f"{where}: provenance evidence is empty")
    date = str(block["date"])
    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        problems.append(f"{where}: provenance date {date!r} is not YYYY-MM-DD")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    root: Path = args.root

    problems: list[str] = []
    scanned = 0

    for sub in ("cases", "errors", "auth"):
        base = root / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.json")):
            scanned += 1
            try:
                data = json.loads(path.read_text())
            except Exception as exc:
                problems.append(f"{path.relative_to(root)}: unreadable JSON ({exc})")
                continue
            check_block(data.get("provenance") if isinstance(data, dict) else None,
                        str(path.relative_to(root)), problems)

    serde_path = root / "serde" / "canonical.json"
    if serde_path.is_file():
        scanned += 1
        try:
            serde_cases = json.loads(serde_path.read_text()).get("cases", [])
        except Exception as exc:
            problems.append(f"serde/canonical.json: unreadable JSON ({exc})")
            serde_cases = []
        for case in serde_cases:
            case_id = case.get("id", "<no id>") if isinstance(case, dict) else "<non-object>"
            check_block(case.get("provenance") if isinstance(case, dict) else None,
                        f"serde/canonical.json:{case_id}", problems)

    if scanned == 0:
        print(f"check_provenance: nothing to scan under {root}", file=sys.stderr)
        return 2

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"check_provenance: {len(problems)} violation(s) across {scanned} file(s)")
        return 1

    print(f"check_provenance: OK ({scanned} file(s) scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
