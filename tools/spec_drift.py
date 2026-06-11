#!/usr/bin/env python3
"""spec_drift — the spec-rot gate.

Runs the reference vet shim's ``surface_dump`` (reflection over
lm15-python's public dataclasses and string vocabularies) and fails when
any reflected type, field, or enum value is missing from the spec tables in
``spec/types.md`` / ``spec/vocabularies.md``.

- MISSING (in reflection, absent from spec) → hard fail, exit 1.
- EXTRA (in spec prose/tables, absent from reflection) → report only.
  Extra prose is allowed: the spec may document in-memory-only details.

Parsing convention (matches how the spec files are written):
- ``spec/types.md``: a type is a ``### TypeName`` heading; its fields are
  the first-column backticked cells of markdown tables in that section.
- ``spec/vocabularies.md``: an enum is matched to the section whose
  ``## Heading`` equals the enum name OR whose "Runtime mirror" line names
  it; its values are all backticked tokens inside that section's tables.

Shim resolution: ``harness/shims.json`` entry "python" (default
``../lm15-python``). If that checkout is absent the gate SKIPS itself with
exit 0 and a loud notice (same convention as lm15-python's CI vet smoke
test); set ``LM15_SPEC_DRIFT_STRICT=1`` to turn a missing shim into a
failure.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# LM15_SPEC_DIR overrides the spec location (used to teeth-test the gate on
# a mutated copy without touching the repo).
_SPEC_DIR = Path(os.environ.get("LM15_SPEC_DIR", ROOT / "spec")) if "LM15_SPEC_DIR" in os.environ else ROOT / "spec"
TYPES_MD = _SPEC_DIR / "types.md"
VOCABS_MD = _SPEC_DIR / "vocabularies.md"
SHIMS = ROOT / "harness" / "shims.json"

_CODE = re.compile(r"`([^`]+)`")


def surface_dump() -> dict | None:
    shim = json.loads(SHIMS.read_text())["python"]
    cwd = (ROOT / shim["cwd"]).resolve()
    cmd = shim["command"]
    if not cwd.is_dir() or not (cwd / cmd[0]).exists():
        return None
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        input='{"op":"surface_dump","id":"drift"}\n',
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        sys.exit(f"spec_drift: shim exited {proc.returncode}: {proc.stderr.strip()}")
    reply = json.loads(proc.stdout.strip().splitlines()[0])
    if not reply.get("ok"):
        sys.exit(f"spec_drift: surface_dump failed: {reply.get('error')}")
    return reply["result"]


def split_sections(text: str, levels: tuple[str, ...]) -> list[tuple[str, str]]:
    """Return (heading, body) for each markdown heading at the given levels."""
    sections: list[tuple[str, str]] = []
    heading = None
    body: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if m and m.group(1) in levels:
            if heading is not None:
                sections.append((heading, "\n".join(body)))
            heading, body = m.group(2).strip(), []
        else:
            body.append(line)
    if heading is not None:
        sections.append((heading, "\n".join(body)))
    return sections


def table_first_cells(body: str) -> set[str]:
    """First-column backticked cell of every markdown table row."""
    out: set[str] = set()
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        m = _CODE.match(cells[0])
        if m:
            out.add(m.group(1).split("`")[0])
    return out


def table_code_tokens(body: str) -> set[str]:
    """Every backticked token appearing inside a table row."""
    out: set[str] = set()
    for line in body.splitlines():
        if line.lstrip().startswith("|"):
            out.update(_CODE.findall(line))
    return out


def check_types(reflected: dict, failures: list[str], extras: list[str]) -> None:
    sections = {h: b for h, b in split_sections(TYPES_MD.read_text(), ("###",))}
    for type_name, info in sorted(reflected.items()):
        body = sections.get(type_name)
        if body is None:
            failures.append(f"types.md: missing section '### {type_name}'")
            continue
        documented = table_first_cells(body)
        for field in info["fields"]:
            if field not in documented:
                failures.append(f"types.md: {type_name} missing field row `{field}`")
        for extra in sorted(documented - set(info["fields"])):
            extras.append(f"types.md: {type_name} documents extra field `{extra}`")
    for extra_type in sorted(set(sections) - set(reflected)):
        extras.append(f"types.md: extra section '### {extra_type}' (not reflected)")


def check_enums(reflected: dict, failures: list[str], extras: list[str]) -> None:
    sections = split_sections(VOCABS_MD.read_text(), ("##",))
    for enum_name, values in sorted(reflected.items()):
        body = None
        for heading, sec_body in sections:
            if heading == enum_name or re.search(
                rf"Runtime mirror[s]?:[^\n]*`{re.escape(enum_name)}`", sec_body
            ):
                body = sec_body
                break
        if body is None:
            failures.append(f"vocabularies.md: missing section for enum '{enum_name}'")
            continue
        tokens = table_code_tokens(body)
        for value in values:
            if value not in tokens:
                failures.append(
                    f"vocabularies.md: {enum_name} missing value `{value}`"
                )


def main() -> int:
    result = surface_dump()
    if result is None:
        msg = "spec_drift: python shim not found (lm15-python not checked out as sibling)"
        if os.environ.get("LM15_SPEC_DRIFT_STRICT"):
            print(f"{msg} — strict mode, failing", file=sys.stderr)
            return 2
        print(f"{msg} — SKIPPED (set LM15_SPEC_DRIFT_STRICT=1 to fail instead)")
        return 0

    failures: list[str] = []
    extras: list[str] = []
    check_types(result["types"], failures, extras)
    check_enums(result["enums"], failures, extras)

    n_fields = sum(len(t["fields"]) for t in result["types"].values())
    n_values = sum(len(v) for v in result["enums"].values())
    print(
        f"spec_drift: checked {len(result['types'])} types / {n_fields} fields, "
        f"{len(result['enums'])} enums / {n_values} values against spec/"
    )
    for line in extras:
        print(f"  note (extra prose, allowed): {line}")
    if failures:
        for line in failures:
            print(f"  DRIFT: {line}", file=sys.stderr)
        print(
            f"spec_drift: FAIL — {len(failures)} reflected surface item(s) missing "
            "from spec/ (update spec/types.md / spec/vocabularies.md with a "
            "changes/ entry)",
            file=sys.stderr,
        )
        return 1
    print("spec_drift: OK — spec covers the reflected surface")
    return 0


if __name__ == "__main__":
    sys.exit(main())
