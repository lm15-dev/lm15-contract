#!/usr/bin/env python3
"""Enforce the secrecy invariant (spec/auth.md AUTH-5) across the corpus.

Two independent checks:

1. Sentinel discipline. The planted sentinel ``SECRET-SENTINEL-DO-NOT-PRINT``
   may appear in fixture *inputs* (``env``, ``borrowed_file``, ``body``,
   ``key``/credential value positions) but never inside any ``expect`` /
   ``expected`` block — an expectation containing the sentinel would pin a
   secret-leaking rendering as correct.

2. Live-secret scan. No file in the corpus may contain material matching
   known credential shapes (Anthropic/OpenAI/Google/GitHub key prefixes,
   Slack tokens, AWS access key ids). Captured bodies are verbatim by rule,
   so a hit here means a capture leaked a real credential and must be
   re-captured with the credential revoked.

Exit non-zero on any violation.

Usage: check_secrecy.py [--root DIR]   (default: the repo containing this script)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SENTINEL = "SECRET-SENTINEL-DO-NOT-PRINT"
EXPECTATION_KEYS = {"expect", "expected", "expect_lm15"}

# Deliberately specific prefixes: broad entropy heuristics drown reviewers
# in false positives, which teaches them to ignore the gate.
LIVE_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("anthropic api key", re.compile(r"sk-ant-(?:api|oat|ort)[0-9a-zA-Z]*-[A-Za-z0-9_-]{16,}")),
    ("openai api key", re.compile(r"sk-(?:proj|svcacct)-[A-Za-z0-9_-]{20,}")),
    ("google api key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("github token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("aws access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
)

SCANNED_SUFFIXES = {".json", ".txt", ".md"}
SKIPPED_PARTS = {".git", "__pycache__", "node_modules"}


def sentinel_in_expectations(node: object, in_expectation: bool, where: str, problems: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            sentinel_in_expectations(
                value, in_expectation or key in EXPECTATION_KEYS, f"{where}.{key}", problems
            )
    elif isinstance(node, list):
        for index, value in enumerate(node):
            sentinel_in_expectations(value, in_expectation, f"{where}[{index}]", problems)
    elif isinstance(node, str) and in_expectation and SENTINEL in node:
        problems.append(f"{where}: sentinel inside an expectation block")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    root: Path = args.root

    problems: list[str] = []
    scanned = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        if any(part in SKIPPED_PARTS for part in path.parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        relative = str(path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            problems.append(f"{relative}: unreadable ({exc})")
            continue
        scanned += 1

        for label, pattern in LIVE_SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                # Never echo the secret itself; name the shape and location.
                line = text.count("\n", 0, match.start()) + 1
                problems.append(f"{relative}:{line}: material matching {label}")

        if path.suffix == ".json" and SENTINEL in text:
            try:
                data = json.loads(text)
            except ValueError:
                continue  # unreadable JSON is check_provenance's problem
            sentinel_in_expectations(data, False, relative, problems)

    if scanned == 0:
        print(f"check_secrecy: nothing to scan under {root}", file=sys.stderr)
        return 2

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"check_secrecy: {len(problems)} violation(s) across {scanned} file(s)")
        return 1

    print(f"check_secrecy: OK ({scanned} file(s) scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
