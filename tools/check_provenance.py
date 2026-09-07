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

Further rules (verify/DECISIONS-2026-09-06.md, ratified 2026-09-06):
- D11: a case under cases/ with source live-capture and date >= 2026-09-06
  carries "exchange": the path, relative to the contract root, of the
  exchange receipt the capture tool wrote (research/providers/_capture.py,
  receipts/<date>-<provider>/exchange-*.json). The file must exist and be
  a JSON object with non-empty "request_sha256" and "response_sha256".
  Captures dated earlier stand without a hash (grandfathered, stated in
  AUTHORITY.md).
- D12: when a golden carries "reviewed", it is a non-empty string that
  starts with a YYYY-MM-DD date (the review date), as the existing frozen
  goldens do. No new source value marks review state.

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
# Goldens are derived artefacts: drafted by the reference shim from a pinned body,
# then (optionally) reviewed. Their source vocabulary is separate.
GOLDEN_SOURCES = {"scribe-draft", "hand-authored"}
REQUIRED_KEYS = {"source", "date", "evidence"}
# D11: live captures dated on or after this day carry an exchange receipt path.
EXCHANGE_REQUIRED_FROM = "2026-09-06"
EXCHANGE_HASHES = ("request_sha256", "response_sha256")


def _is_date(text: str) -> bool:
    return (len(text) == 10 and text[4] == "-" and text[7] == "-"
            and text[:4].isdigit() and text[5:7].isdigit() and text[8:].isdigit())


def check_block(block, where: str, problems: list[str], allowed: set[str] = ALLOWED_SOURCES) -> None:
    if not isinstance(block, dict):
        problems.append(f"{where}: missing or non-object provenance block")
        return
    missing = REQUIRED_KEYS - set(block)
    if missing:
        problems.append(f"{where}: provenance missing keys {sorted(missing)}")
        return
    if block["source"] not in allowed:
        problems.append(f"{where}: provenance source {block['source']!r} not in {sorted(allowed)}")
    if not str(block["evidence"]).strip():
        problems.append(f"{where}: provenance evidence is empty")
    date = str(block["date"])
    if not _is_date(date):
        problems.append(f"{where}: provenance date {date!r} is not YYYY-MM-DD")


def check_exchange(block: dict, where: str, root: Path, problems: list[str]) -> None:
    """D11: a live capture dated >= 2026-09-06 names its exchange receipt."""
    if block.get("source") != "live-capture":
        return
    date = str(block.get("date", ""))
    if not _is_date(date) or date < EXCHANGE_REQUIRED_FROM:
        return
    exchange = block.get("exchange")
    if not isinstance(exchange, str) or not exchange.strip():
        problems.append(f"{where}: live-capture dated {date} lacks provenance.exchange "
                        f"(required from {EXCHANGE_REQUIRED_FROM}; D11)")
        return
    rel = Path(exchange)
    if rel.is_absolute() or ".." in rel.parts:
        problems.append(f"{where}: provenance.exchange {exchange!r} must be a relative path inside the contract")
        return
    path = root / rel
    if not path.is_file():
        problems.append(f"{where}: provenance.exchange {exchange!r} does not exist")
        return
    try:
        receipt = json.loads(path.read_text())
    except Exception as exc:
        problems.append(f"{where}: provenance.exchange {exchange!r} is unreadable JSON ({exc})")
        return
    if not isinstance(receipt, dict):
        problems.append(f"{where}: provenance.exchange {exchange!r} is not a JSON object")
        return
    for key in EXCHANGE_HASHES:
        value = receipt.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{where}: provenance.exchange {exchange!r} lacks a non-empty {key}")


def check_reviewed(block: dict, where: str, problems: list[str]) -> None:
    """D12: a golden's ``reviewed`` line is a non-empty string starting with YYYY-MM-DD."""
    if "reviewed" not in block:
        return
    reviewed = block["reviewed"]
    if not isinstance(reviewed, str) or not reviewed.strip():
        problems.append(f"{where}: provenance.reviewed must be a non-empty string (D12)")
        return
    if not _is_date(reviewed[:10]):
        problems.append(f"{where}: provenance.reviewed must start with a YYYY-MM-DD date (D12); got {reviewed[:20]!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    root: Path = args.root

    problems: list[str] = []
    scanned = 0

    for sub in ("cases", "errors", "auth", "goldens"):
        base = root / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.json")):
            if sub == "goldens" and path.name.startswith("_"):
                continue  # goldens/_failures.json is a scribe report, not a fixture
            scanned += 1
            try:
                data = json.loads(path.read_text())
            except Exception as exc:
                problems.append(f"{path.relative_to(root)}: unreadable JSON ({exc})")
                continue
            block = data.get("provenance") if isinstance(data, dict) else None
            where = str(path.relative_to(root))
            if sub == "goldens":
                # Independent review 2026-09-02: 29 goldens had no block and
                # this checker never looked. Goldens are fixtures under
                # AUTHORITY.md; they carry provenance like everything else.
                check_block(block, where, problems, allowed=GOLDEN_SOURCES)
                if isinstance(block, dict):
                    check_reviewed(block, where, problems)
            else:
                check_block(block, where, problems)
                if sub == "cases" and isinstance(block, dict):
                    check_exchange(block, where, root, problems)

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
