#!/usr/bin/env python3
"""Write tables/providers.json from the reference's provider_tables op.

The file is the reference's provider tables as data — the registry rows and
their access policies, the managed-login declared providers, the compat
presets of the three re-usable dialects with their base-URL and alias
tables, the router's built-in rules and litellm prefixes, and the
managed-login service labels — published at a contract commit so every port
generates its copy from the same bytes at its CONTRACT_PIN
(tables/README.md). It is not an oracle: the corpus is (AUTHORITY.md).
`tools/audit.py` fails when the file and the reference differ.

    python3 tools/export_provider_tables.py [--python2 ../lm15-python] [--check]

`--check` writes nothing and exits 1 when the file is stale.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit import TABLES_PATH, shim_op  # noqa: E402


def render(tables: dict) -> str:
    return json.dumps(tables, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--python2", type=Path, default=ROOT.parent / "lm15-python")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    tables, reason = shim_op(args.python2.resolve(), "provider_tables")
    if tables is None:
        print(f"error: {reason}", file=sys.stderr)
        return 2
    path = ROOT / TABLES_PATH
    text = render(tables)
    if args.check:
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != text:
            print(f"{TABLES_PATH} is stale: run python3 tools/export_provider_tables.py")
            return 1
        print(f"{TABLES_PATH}: current")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {TABLES_PATH}: {len(tables['providers'])} providers, {len(tables['declared_login'])} declared, "
          f"{len(tables['routing']['default_rules'])} rules, {len(tables['routing']['litellm_prefixes'])} litellm prefixes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
