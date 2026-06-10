#!/usr/bin/env python3
"""Draft response/stream goldens from pinned bodies via the reference shim.

For every case carrying BOTH ``canonical_request`` and ``pinned_body``, the
scribe replays the pinned body through the vet shim — ``parse_response``, or
``replay_stream`` for stream cases (same classification as harness/check.py)
— and writes ``goldens/<provider>/<feature>.json``:

    {"canonical_response": ...,
     "events": [...],            # stream cases only
     "provenance": {"source": "scribe-draft", ...}}

DRAFT status and the circularity: the drafts are derived from lm15-python2,
which holds NO oracle authority (AUTHORITY.md). Re-running the python shim
against its own drafts is green by construction — the drafts pin regressions,
not correctness. Correctness comes only at human freeze, with evidence per
AUTHORITY.md (see changes/2026-06-10-golden-drafts.md). The scribe never
edits cases/, bodies/, errors/, or serde/.

Bodies that are error bodies, parses that legitimately fail, and parses that
trip the ``unmapped`` canary are recorded in ``goldens/_failures.json`` with
the error — honest, never silently skipped (no golden is written for them).

Usage: scribe_goldens.py [--shim python]
"""

from __future__ import annotations

import argparse
import base64
import datetime
import json
import sys
from pathlib import Path

CONTRACT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CONTRACT_ROOT / "harness"))

import check  # harness/check.py — Shim, corpus loaders, golden_path

FAILURES_FILE = check.GOLDENS_DIR / "_failures.json"

PROVENANCE_EVIDENCE = (
    "derived from pinned body via python -m lm15.vet @ lm15-python2 HEAD; "
    "DRAFT — not frozen, see AUTHORITY.md"
)


def draft_provenance(case: dict) -> dict:
    return {
        "source": "scribe-draft",
        "date": datetime.date.today().isoformat(),
        "evidence": PROVENANCE_EVIDENCE,
        "pinned_body": case["pinned_body"],
    }


def scribe(shim: check.Shim) -> tuple[dict[str, int], list[dict]]:
    counts = {"drafted": 0, "failed": 0, "no-body": 0, "no-canonical-request": 0}
    failures: list[dict] = []
    for case in check.load_wire_cases():
        case_id = case["id"]
        if "pinned_body" not in case:
            counts["no-body"] += 1
            print(f"  no-body  {case_id}")
            continue
        if "canonical_request" not in case:
            counts["no-canonical-request"] += 1
            continue

        body_b64 = base64.b64encode(check.pinned_body(case)).decode("ascii")
        streaming = check.is_stream_case(case)
        op = "replay_stream" if streaming else "parse_response"
        if streaming:
            reply = shim.call(
                op,
                provider=case["provider"],
                canonical_request=case["canonical_request"],
                body_b64=body_b64,
            )
        else:
            reply = shim.call(
                op,
                provider=case["provider"],
                canonical_request=case["canonical_request"],
                status=int(case.get("expect", {}).get("status", 200)),
                body_b64=body_b64,
            )

        error = None
        if not reply.get("ok"):
            error = reply.get("error") or {"type": "?", "message": "?"}
        elif reply["result"].get("unmapped"):
            # The harness fails any non-empty unmapped canary; a golden drawn
            # from such a parse could never pass — record it, don't write it.
            error = {
                "type": "UnmappedProviderFields",
                "message": f"parser recorded unmapped provider fields: {reply['result']['unmapped']}",
            }
        if error is not None:
            counts["failed"] += 1
            failures.append({"id": case_id, "op": op, "pinned_body": case["pinned_body"], "error": error})
            print(f"  FAILED   {case_id}: {error['type']}: {error['message']}")
            continue

        result = reply["result"]
        golden: dict = {"canonical_response": result["canonical_response"]}
        if streaming:
            golden["events"] = result["events"]
        golden["provenance"] = draft_provenance(case)

        path = check.golden_path(case)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(golden, indent=2, ensure_ascii=False) + "\n")
        counts["drafted"] += 1
    return counts, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--shim", default="python", help="shim name from harness/shims.json")
    args = parser.parse_args(argv)

    shim = check.load_shim(args.shim)
    try:
        if not shim.sandboxed:
            print("warning: unshare -rn unavailable — shim runs WITHOUT no-network enforcement", file=sys.stderr)
        counts, failures = scribe(shim)
    finally:
        try:
            shim.close()
        except Exception:
            pass

    check.GOLDENS_DIR.mkdir(parents=True, exist_ok=True)
    FAILURES_FILE.write_text(
        json.dumps(
            {
                "_doc": "Cases whose pinned body could not be drafted into a golden "
                        "(error bodies, parse failures, unmapped canary) — see tools/scribe_goldens.py.",
                "generated": datetime.date.today().isoformat(),
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )

    print(
        f"scribe_goldens: drafted {counts['drafted']}  failed {counts['failed']}  "
        f"no-body {counts['no-body']}  no-canonical-request {counts['no-canonical-request']}  "
        f"(failures: {FAILURES_FILE.relative_to(CONTRACT_ROOT)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
