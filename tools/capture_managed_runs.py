#!/usr/bin/env python3
"""Fill `expect` in auth/managed/runs/*.json from a shim's normalized output.

For authoring only: run it against the reference, then READ every captured
expectation against AUTH-12–26 before committing. Existing expectations are
kept unless --force; --case limits the capture to one case.

    python3 tools/capture_managed_runs.py --shim python [--case ID] [--force]
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))

import check  # noqa: E402
import managed  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shim", default="python")
    parser.add_argument("--case")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    shim = check.load_shim(args.shim)
    changed = 0
    try:
        with tempfile.TemporaryDirectory(prefix="lm15-managed-capture-") as tmp:
            for path in sorted(managed.RUNS_DIR.glob("*.json")):
                data = json.loads(path.read_text(encoding="utf-8"))
                for case in data["cases"]:
                    if args.case and case["id"] != args.case:
                        continue
                    if "expect" in case and not args.force:
                        continue
                    fields = managed.shim_fields({**case, "sentinel": case.get("sentinel", data.get("sentinel"))}, Path(tmp))
                    reply = shim.call("managed_run", **fields)
                    if not reply.get("ok"):
                        print(f"{case['id']}: shim failed: {reply.get('error')}", file=sys.stderr)
                        continue
                    result = reply["result"]
                    problem = managed.secrecy_violation(result, fields["sentinel"]) or \
                        managed.check_oauth_relations(result.get("events") or [])
                    if problem:
                        print(f"{case['id']}: NOT captured: {problem}", file=sys.stderr)
                        continue
                    case["expect"] = managed.normalize(result)
                    changed += 1
                path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    finally:
        shim.close()
    print(f"captured {changed} case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
