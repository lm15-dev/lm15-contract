#!/usr/bin/env python3
"""Enforce fixture provenance in the lm15-contract corpus.

Every fixture must say where it came from. Rules:
- every JSON file under cases/   : top-level "provenance" block
- every JSON file under errors/  : top-level "provenance" block
- every JSON file under auth/    : top-level "provenance" block
- every JSON file under mapping/ : top-level "provenance" block (2026-09-26)
- serde/canonical.json           : every entry in .cases[] has "provenance"

A provenance block is an object with:
  source   : one of {live-capture, migrated-apr29, hand-authored}
  date     : YYYY-MM-DD
  evidence : non-empty pointer (commit, live receipt, changes/ entry)

Further rules (changes/2026-09-06-decisions.md, ratified 2026-09-06):
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
import hashlib
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
RECEIPT_ALLOWLIST_REL = Path("tools") / "receipt-hash-allowlist.json"
UNREVIEWED_RATCHET_REL = Path("tools") / "unreviewed-goldens-ratchet.json"


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


def _load_receipt(exchange: str, field_name: str, where: str, root: Path, problems: list[str]) -> dict | None:
    rel = Path(exchange)
    if rel.is_absolute() or ".." in rel.parts:
        problems.append(f"{where}: provenance.{field_name} {exchange!r} must be a relative path inside the contract")
        return None
    path = root / rel
    if not path.is_file():
        problems.append(f"{where}: provenance.{field_name} {exchange!r} does not exist")
        return None
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        problems.append(f"{where}: provenance.{field_name} {exchange!r} is unreadable JSON ({exc})")
        return None
    if not isinstance(receipt, dict):
        problems.append(f"{where}: provenance.{field_name} {exchange!r} is not a JSON object")
        return None
    for key in EXCHANGE_HASHES:
        value = receipt.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{where}: provenance.{field_name} {exchange!r} lacks a non-empty {key}")
        elif key == "response_sha256" and (len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
            problems.append(f"{where}: provenance.{field_name} {exchange!r} lacks a valid SHA-256 {key}")
        # Some historical request receipts explicitly retain only a hash
        # prefix. This guard verifies response bytes, not request receipts.
    return receipt


def check_exchange(
    data: dict,
    block: dict,
    where: str,
    root: Path,
    problems: list[str],
    receipt_allowlist: dict[str, dict],
    used_allowlist: set[str],
) -> None:
    """D11: a live capture dated >= 2026-09-06 names its exchange receipt, and its
    pinned_body bytes must match receipt.response_sha256 (or carry a pinned entry
    in tools/receipt-hash-allowlist.json for documented redactions / live transcripts)."""
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
    req_receipt = _load_receipt(exchange, "exchange", where, root, problems)
    resp_exchange = block.get("response_exchange")
    if resp_exchange is not None:
        if not isinstance(resp_exchange, str) or not resp_exchange.strip():
            problems.append(f"{where}: provenance.response_exchange must be a non-empty string")
            resp_receipt = None
        else:
            resp_receipt = _load_receipt(resp_exchange, "response_exchange", where, root, problems)
    else:
        resp_receipt = req_receipt

    pinned_body = data.get("pinned_body")
    case_id = data.get("id")
    if not pinned_body or not isinstance(case_id, str) or resp_receipt is None:
        return
    expected_sha = resp_receipt.get("response_sha256")
    if not isinstance(expected_sha, str) or not expected_sha.strip():
        return
    body_path = root / "bodies" / case_id / str(pinned_body)
    if not body_path.is_file():
        return  # audit.py reports missing pinned_body files
    raw = body_path.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha == expected_sha:
        return
    # Known capture writer convention: a single trailing newline appended to the
    # saved body file when the receipt hashed the raw wire bytes without one.
    if raw.endswith(b"\n") and hashlib.sha256(raw[:-1]).hexdigest() == expected_sha:
        return
    allow = receipt_allowlist.get(case_id)
    if allow is not None:
        used_allowlist.add(case_id)
        if allow.get("body_sha256") != actual_sha or allow.get("receipt_sha256") != expected_sha:
            problems.append(
                f"{where}: pinned_body {pinned_body!r} hash changed against tools/receipt-hash-allowlist.json "
                f"(actual={actual_sha[:12]}, pinned={str(allow.get('body_sha256'))[:12]})"
            )
        return
    problems.append(
        f"{where}: pinned_body {pinned_body!r} sha256 {actual_sha[:12]} does not match "
        f"receipt response_sha256 {expected_sha[:12]} (D11)"
    )


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

    receipt_allowlist_path = root / RECEIPT_ALLOWLIST_REL
    receipt_allowlist: dict[str, dict] = {}
    used_allowlist: set[str] = set()
    if receipt_allowlist_path.is_file():
        receipt_allowlist = dict(json.loads(receipt_allowlist_path.read_text(encoding="utf-8")).get("cases", {}))
    else:
        problems.append(f"{RECEIPT_ALLOWLIST_REL}: required hash-exception registry missing")

    ratchet_path = root / UNREVIEWED_RATCHET_REL
    unreviewed_allowed: set[str] | None = None
    if ratchet_path.is_file():
        unreviewed_allowed = set(json.loads(ratchet_path.read_text(encoding="utf-8")).get("unreviewed", []))
    else:
        problems.append(f"{UNREVIEWED_RATCHET_REL}: required review-backlog ratchet missing")
    unreviewed_seen: set[str] = set()

    for sub in ("cases", "errors", "auth", "router", "mapping", "goldens"):
        base = root / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.json")):
            if sub == "goldens" and path.name.startswith("_"):
                continue  # goldens/_failures.json is a scribe report, not a fixture
            scanned += 1
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
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
                    if "reviewed" not in block:
                        unreviewed_seen.add(where)
            else:
                check_block(block, where, problems)
                if sub == "cases" and isinstance(block, dict):
                    check_exchange(data, block, where, root, problems, receipt_allowlist, used_allowlist)

    for stale_id in sorted(set(receipt_allowlist) - used_allowlist):
        problems.append(
            f"{RECEIPT_ALLOWLIST_REL}: stale entry {stale_id!r} — pinned_body now matches "
            f"receipt response_sha256 or case was removed; delete the entry (ratchet only goes down)"
        )

    if unreviewed_allowed is not None:
        for new_unreviewed in sorted(unreviewed_seen - unreviewed_allowed):
            problems.append(
                f"{new_unreviewed}: new golden lacks provenance.reviewed (D12 ratchet: "
                f"review every new golden before merging; {UNREVIEWED_RATCHET_REL} never grows)"
            )
        for stale_golden in sorted(unreviewed_allowed - unreviewed_seen):
            problems.append(
                f"{UNREVIEWED_RATCHET_REL}: stale entry {stale_golden!r} — golden is now reviewed "
                f"or removed; delete the entry so the unreviewed backlog only shrinks"
            )

    for serde_name in ("canonical.json", "reject.json"):
        serde_path = root / "serde" / serde_name
        if serde_path.is_file():
            scanned += 1
            try:
                serde_cases = json.loads(serde_path.read_text(encoding="utf-8")).get("cases", [])
            except Exception as exc:
                problems.append(f"serde/{serde_name}: unreadable JSON ({exc})")
                serde_cases = []
            for case in serde_cases:
                case_id = case.get("id", "<no id>") if isinstance(case, dict) else "<non-object>"
                check_block(case.get("provenance") if isinstance(case, dict) else None,
                            f"serde/{serde_name}:{case_id}", problems)

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
