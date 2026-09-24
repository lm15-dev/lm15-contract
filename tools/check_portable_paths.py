#!/usr/bin/env python3
"""Every tracked path must be storable on Windows, macOS and Linux.

A name Windows cannot store (``< > : " | ? *``, control characters, a trailing
dot or space, a reserved device name such as ``CON`` or ``aux.txt``), or two
names that differ only in case (one file on Windows and macOS), makes
``git clone`` fail there. Found 2026-09-24: 316 receipt files named
``…__tc:auto`` made this repository uncloneable on Windows, and with it every
SDK's Windows CI. Exit non-zero on any such path.
"""
from __future__ import annotations

import collections
import re
import subprocess
import sys

FORBIDDEN = re.compile(r'[<>:"|?*\x00-\x1f\\]')
RESERVED = re.compile(r"(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?")


def problems(paths: list[str]) -> list[str]:
    out = []
    for path in paths:
        for part in path.split("/"):
            if FORBIDDEN.search(part):
                out.append(f"{path}: character not allowed on Windows")
            elif part.endswith((".", " ")):
                out.append(f"{path}: name ends with a dot or space")
            elif RESERVED.fullmatch(part):
                out.append(f"{path}: reserved device name on Windows")
            else:
                continue
            break
    by_lower = collections.defaultdict(set)
    for path in paths:
        by_lower[path.lower()].add(path)
    out += [f"differ only in case: {', '.join(sorted(v))}" for v in by_lower.values() if len(v) > 1]
    return out


def main() -> int:
    paths = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True).stdout.decode().split("\0")
    found = problems([p for p in paths if p])
    for line in found:
        print(line)
    print(f"check_portable_paths: {'OK' if not found else f'{len(found)} problem(s)'} ({len(paths) - 1} path(s))")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
