#!/usr/bin/env python3
"""Audit / ratchet the lm15-contract corpus.

Four checks, each with FAIL/REPORT lines and a one-line summary:

1. ORPHANS (HARD)            : case files without canonical_request (Stage 2
   debt, allowlisted in tools/orphan-allowlist.json — the audit fails on any
   NEW orphan and on any STALE allowlist entry, so the list only shrinks);
   body directories without a case file; cases with a body dir but no
   pinned_body; pinned_body filenames that do not exist on disk.
2. VOLATILE LINT (HARD)      : every case "volatile" map must use classes in
   {id, timestamp, usage-count, duration}, declare at most 6 paths, and never
   touch text content, tool inputs, or tool names (PROTOCOL.md, comparison
   semantics).
3. RAW-PROVIDER LINT (report-only): cases whose canonical_request smuggles
   provider wire syntax through config.extensions — the
   "extensions-passthrough" burn-down list, reported with exact ids.
4. SURFACE COVERAGE (report-only): types/enums from the reference shim's
   surface_dump (python -m lm15.vet, run as a subprocess in lm15-python2)
   that no serde kind appearing in serde/canonical.json covers. "Covered"
   means directly addressable as the top-level value of that kind's serde —
   nested-only types are honest gaps, not silently excused.

Hard checks exit non-zero on violation; report-only checks never affect the
exit code. Per AUTHORITY.md this tool never edits fixtures — it only reports.

Usage: audit.py [--root DIR] [--python2 DIR] [--allowlist FILE]
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

VOLATILE_CLASSES = {"id", "timestamp", "usage-count", "duration"}
MAX_VOLATILE_PATHS = 6
# PROTOCOL.md: text content, tool names, and tool inputs may NEVER be volatile.
FORBIDDEN_VOLATILE_SUBSTRINGS = ("text", "tool_call.input", "name")

# Surface-coverage lens: serde kind -> (type-name patterns, enum names) that
# the kind's serde directly serializes at top level (fnmatch globs, one "*").
# Anything in surface_dump matched by no kind present in serde/canonical.json
# is reported as a gap.
KIND_COVERS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "part": (("*Part",), ("PartType", "PART_TYPES")),
    "message": (("Message",), ("Role", "ROLE_VALUES")),
    "tool": (("FunctionTool", "BuiltinTool"), ()),
    "tool_choice": (("ToolChoice",), ("ToolChoiceMode", "TOOL_CHOICE_MODES")),
    "reasoning": (("Reasoning",), ("ReasoningEffort", "REASONING_EFFORTS",
                                   "ReasoningSummary", "REASONING_SUMMARIES")),
    "config": (("Config",), ()),
    "error_detail": (("ErrorDetail",), ("ErrorCode", "ERROR_CODES")),
    "delta": (("*Delta",), ("DeltaType", "DELTA_TYPES")),
    "usage": (("Usage",), ()),
    "stream_event": (("Stream*Event",), ("StreamEventType",)),
    "request": (("Request",), ()),
    "response": (("Response",), ("FinishReason", "FINISH_REASONS")),
    "audio_format": (("AudioFormat",), ("AudioEncoding", "AUDIO_ENCODINGS")),
    "live_config": (("LiveConfig",), ()),
    "live_client_event": (("LiveClient*Event",), ("LiveClientEventType",)),
    "live_server_event": (("LiveServer*Event",), ("LiveServerEventType",)),
}


def load_cases(root: Path) -> list[tuple[Path, dict]]:
    cases: list[tuple[Path, dict]] = []
    for path in sorted(root.glob("cases/*/*.json")):
        cases.append((path, json.loads(path.read_text())))
    return cases


# ─── 1. ORPHANS (hard) ───────────────────────────────────────────────

def check_orphans(root: Path, cases: list[tuple[Path, dict]],
                  allowlist: set[str], problems: list[str]) -> str:
    orphans = {data.get("id", str(path.relative_to(root)))
               for path, data in cases if "canonical_request" not in data}
    case_ids = {data.get("id") for _, data in cases}

    for case_id in sorted(orphans - allowlist):
        problems.append(f"ORPHANS {case_id}: no canonical_request and not in "
                        f"tools/orphan-allowlist.json — attach one (with provenance) "
                        f"or this is a new orphan; the allowlist never grows")
    for case_id in sorted(allowlist - orphans):
        problems.append(f"ORPHANS tools/orphan-allowlist.json: stale entry {case_id!r} — "
                        + ("case now has canonical_request; remove the entry "
                           "(the ratchet only goes down)"
                           if case_id in case_ids else "no such case file"))

    bodies = root / "bodies"
    body_dirs = sorted(p.name for p in bodies.iterdir() if p.is_dir()) if bodies.is_dir() else []
    for name in body_dirs:
        if name not in case_ids:
            problems.append(f"ORPHANS bodies/{name}/: body directory without a case file")

    for path, data in cases:
        case_id = data.get("id", str(path.relative_to(root)))
        body_dir = bodies / str(case_id)
        pinned = data.get("pinned_body")
        if body_dir.is_dir() and not pinned:
            problems.append(f"ORPHANS {case_id}: body dir exists but case has no pinned_body")
        if pinned and not (body_dir / str(pinned)).is_file():
            problems.append(f"ORPHANS {case_id}: pinned_body {pinned!r} does not exist "
                            f"under bodies/{case_id}/")

    return (f"ORPHANS: {len(cases)} case(s), {len(body_dirs)} body dir(s), "
            f"{len(orphans & allowlist)} allowlisted orphan(s) pending burn-down")


# ─── 2. VOLATILE LINT (hard) ─────────────────────────────────────────

def lint_volatile_map(where: str, volatile, problems: list[str]) -> int:
    if not isinstance(volatile, dict):
        problems.append(f"VOLATILE {where}: \"volatile\" must be a map of "
                        f"json-path -> class, got {type(volatile).__name__}")
        return 0
    if len(volatile) > MAX_VOLATILE_PATHS:
        problems.append(f"VOLATILE {where}: {len(volatile)} volatile paths "
                        f"(max {MAX_VOLATILE_PATHS})")
    for path, klass in volatile.items():
        if klass not in VOLATILE_CLASSES:
            problems.append(f"VOLATILE {where}: path {path!r} has class {klass!r}, "
                            f"not in {sorted(VOLATILE_CLASSES)}")
        for forbidden in FORBIDDEN_VOLATILE_SUBSTRINGS:
            if forbidden in str(path):
                problems.append(f"VOLATILE {where}: path {path!r} contains {forbidden!r} — "
                                f"text content, tool inputs, and tool names may NEVER "
                                f"be volatile (PROTOCOL.md)")
    return len(volatile)


def check_volatile(root: Path, cases: list[tuple[Path, dict]],
                   problems: list[str]) -> str:
    maps = 0
    paths = 0
    for path, data in cases:
        if "volatile" not in data:
            continue
        maps += 1
        where = data.get("id", str(path.relative_to(root)))
        paths += lint_volatile_map(where, data["volatile"], problems)

    serde_path = root / "serde" / "canonical.json"
    if serde_path.is_file():
        for case in json.loads(serde_path.read_text()).get("cases", []):
            if isinstance(case, dict) and "volatile" in case:
                maps += 1
                where = f"serde/canonical.json:{case.get('id', '<no id>')}"
                paths += lint_volatile_map(where, case["volatile"], problems)

    return f"VOLATILE: {paths} volatile path(s) across {maps} map(s)"


# ─── 3. RAW-PROVIDER LINT (report-only) ──────────────────────────────

def report_extensions_passthrough(root: Path, cases: list[tuple[Path, dict]]) -> str:
    smugglers: list[str] = []
    for path, data in cases:
        canonical = data.get("canonical_request")
        if not isinstance(canonical, dict):
            continue
        config = canonical.get("config")
        if isinstance(config, dict) and config.get("extensions"):
            smugglers.append(str(data.get("id", path.relative_to(root))))
    for case_id in smugglers:
        print(f"REPORT extensions-passthrough: {case_id}")
    return (f"extensions-passthrough (report-only): {len(smugglers)} case(s) smuggle "
            f"provider wire syntax through config.extensions — burn-down list above")


# ─── 4. SURFACE COVERAGE (report-only) ───────────────────────────────

def shim_surface_dump(python2: Path) -> tuple[dict | None, str]:
    """Call the reference vet shim's surface_dump op. Returns (result, reason)."""
    shim_python = python2 / ".venv" / "bin" / "python"
    if not shim_python.is_file():
        return None, f"no shim interpreter at {shim_python}"
    try:
        proc = subprocess.run(
            [str(shim_python), "-m", "lm15.vet"],
            input='{"op": "surface_dump", "id": "audit"}\n',
            capture_output=True, text=True, cwd=python2, timeout=120,
        )
    except Exception as exc:
        return None, f"shim failed to run: {exc}"
    line = proc.stdout.splitlines()[0] if proc.stdout.splitlines() else ""
    try:
        reply = json.loads(line)
    except Exception:
        return None, f"shim emitted no JSON reply (exit {proc.returncode})"
    if not reply.get("ok"):
        return None, f"shim error: {reply.get('error')}"
    return reply["result"], ""


def report_surface_coverage(root: Path, python2: Path) -> str:
    surface, reason = shim_surface_dump(python2)
    if surface is None:
        print(f"REPORT surface-coverage: skipped — {reason}")
        return f"surface coverage (report-only): skipped ({reason})"

    serde_path = root / "serde" / "canonical.json"
    serde_cases = json.loads(serde_path.read_text()).get("cases", []) if serde_path.is_file() else []
    kinds_present = {c.get("kind") for c in serde_cases if isinstance(c, dict)}

    def covered(name: str, column: int) -> bool:
        return any(fnmatch.fnmatchcase(name, pattern)
                   for kind in kinds_present & set(KIND_COVERS)
                   for pattern in KIND_COVERS[kind][column])

    gap_types = sorted(t for t in surface.get("types", {}) if not covered(t, 0))
    gap_enums = sorted(e for e in surface.get("enums", {}) if not covered(e, 1))
    for name in gap_types:
        print(f"REPORT surface-coverage: type {name} covered by no serde kind")
    for name in gap_enums:
        print(f"REPORT surface-coverage: enum {name} covered by no serde kind")
    return (f"surface coverage (report-only): {len(gap_types)} type(s) and "
            f"{len(gap_enums)} enum(s) uncovered by the {len(kinds_present)} "
            f"serde kind(s) in serde/canonical.json")


# ─── main ────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--python2", type=Path, default=None,
                        help="lm15-python2 checkout for the vet shim (default: sibling of --root)")
    parser.add_argument("--allowlist", type=Path, default=None,
                        help="orphan allowlist (default: <root>/tools/orphan-allowlist.json)")
    args = parser.parse_args(argv)
    root: Path = args.root
    python2: Path = args.python2 or root.parent / "lm15-python2"
    allowlist_path: Path = args.allowlist or root / "tools" / "orphan-allowlist.json"

    problems: list[str] = []

    try:
        cases = load_cases(root)
    except Exception as exc:
        print(f"FAIL audit: unreadable case file ({exc})")
        return 1
    if not cases:
        print(f"audit: nothing to scan under {root}", file=sys.stderr)
        return 2

    allowlist: set[str] = set()
    if allowlist_path.is_file():
        allowlist = set(json.loads(allowlist_path.read_text()).get("orphans", []))
    else:
        problems.append(f"ORPHANS {allowlist_path}: allowlist file missing")

    summaries = [
        check_orphans(root, cases, allowlist, problems),
        check_volatile(root, cases, problems),
        report_extensions_passthrough(root, cases),
        report_surface_coverage(root, python2),
    ]

    for problem in problems:
        print(f"FAIL {problem}")
    for summary in summaries:
        print(f"audit: {summary}")
    if problems:
        print(f"audit: {len(problems)} hard violation(s)")
        return 1
    print("audit: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
