#!/usr/bin/env python3
"""One-shot: stamp provenance onto the corpus migrated from lm15-python2/conformance.

Run once on 2026-06-09 during Stage 1 (see changes/2026-06-09-initial-migration.md).
Kept for the record; re-running is a no-op for already-stamped fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MIGRATED = {
    "source": "migrated-apr29",
    "date": "2026-06-09",
    "evidence": "lm15-python2/conformance@812a2cb (consolidated corpus, live-validated 2026-04-29 via curl-fixtures pipeline); copied to lm15-contract 2026-06-09",
}
HAND_AUTHORED = {
    "source": "hand-authored",
    "date": "2026-06-09",
    "evidence": "curated provider error bodies from lm15-python2/conformance@f0bd3ab; copied to lm15-contract 2026-06-09",
}


def stamp_file(path: Path, block: dict) -> bool:
    data = json.loads(path.read_text())
    if "provenance" in data:
        return False
    data["provenance"] = block
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return True


def main() -> None:
    stamped = 0
    for path in sorted((ROOT / "cases").rglob("*.json")):
        stamped += stamp_file(path, MIGRATED)
    for path in sorted((ROOT / "errors").rglob("*.json")):
        stamped += stamp_file(path, HAND_AUTHORED)

    serde_path = ROOT / "serde" / "canonical.json"
    data = json.loads(serde_path.read_text())
    changed = False
    for case in data.get("cases", []):
        if isinstance(case, dict) and "provenance" not in case:
            case["provenance"] = MIGRATED
            changed = True
    if changed:
        serde_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"stamped {stamped} files; serde {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
