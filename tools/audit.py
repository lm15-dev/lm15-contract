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
   surface_dump (python -m lm15.vet, run as a subprocess in lm15-python)
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
    "cache_config": (("CacheConfig",), ("CacheMode", "CACHE_MODES",
                                         "CacheRetention", "CACHE_RETENTIONS")),
    "continuation_state": (("ContinuationState",), ()),
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
    "batch_request": (("BatchRequest",), ()),
    "image_generation_request": (("ImageGenerationRequest",), ()),
    "image_generation_response": (("ImageGenerationResponse",), ()),
    "speech_generation_request": (("SpeechGenerationRequest",), ()),
    "speech_generation_response": (("SpeechGenerationResponse",), ()),
    "video_generation_request": (("VideoGenerationRequest",), ()),
    "video_job": (("VideoJobInfo",), ("VideoStatus", "VIDEO_STATUSES", "VIDEO_TERMINAL_STATUSES")),
    "batch_job": (("BatchJobInfo",), ("BatchStatus", "BATCH_STATUSES", "BATCH_TERMINAL_STATUSES")),
    "batch_entry": (("BatchEntry",), ("BatchOutcome", "BATCH_OUTCOMES")),
    "file_upload_request": (("FileUploadRequest",), ()),
    "file_info": (("FileInfo",), ("FileReadiness", "FILE_READINESS_VALUES")),
    "file_page": (("FilePage",), ()),
}


def load_cases(root: Path) -> list[tuple[Path, dict]]:
    cases: list[tuple[Path, dict]] = []
    for path in sorted(root.glob("cases/*/*.json")):
        cases.append((path, json.loads(path.read_text())))
    return cases


# ─── 1. ORPHANS (hard) ───────────────────────────────────────────────

def check_orphans(root: Path, cases: list[tuple[Path, dict]],
                  allowlist: set[str], body_dir_allowlist: set[str],
                  problems: list[str]) -> str:
    # Models-, live-, and endpoint-surface cases carry no canonical_request
    # by design: the listing surface has no canonical Request; the live
    # surface's canonical inputs are live_config + client events; the files/
    # batch/generation surfaces carry their canonical payloads inline
    # (upload_request / batch_request / generation_request), checked by the
    # completeness rules below.  Each has its own harness direction.
    orphans = {data.get("id", str(path.relative_to(root)))
               for path, data in cases
               if "canonical_request" not in data
               and data.get("surface") not in ("models", "live", "files", "batch", "generation", "video")}
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
        if name not in case_ids and name not in body_dir_allowlist:
            problems.append(f"ORPHANS bodies/{name}/: body directory without a case file")
    for name in sorted(body_dir_allowlist):
        if name in case_ids:
            problems.append(
                f"ORPHANS bodies/{name}/: STALE allowlist entry — a case file now exists; "
                "remove it from body_dirs in the same commit"
            )

    for path, data in cases:
        case_id = data.get("id", str(path.relative_to(root)))
        body_dir = bodies / str(case_id)
        pinned = data.get("pinned_body")
        step_pins = [
            name for step in (data.get("steps") or [])
            for name in ([step.get("pinned_body")] if step.get("pinned_body") else [])
            + list(step.get("fetched_from") or [])
            + ([step.get("status_body_from")] if step.get("status_body_from") else [])
            + ([step.get("upload_body")] and [] or [])
        ]
        if body_dir.is_dir() and not pinned and not step_pins:
            problems.append(f"ORPHANS {case_id}: body dir exists but case has no pinned_body")
        if pinned and not (body_dir / str(pinned)).is_file():
            problems.append(f"ORPHANS {case_id}: pinned_body {pinned!r} does not exist "
                            f"under bodies/{case_id}/")
        if data.get("surface") == "generation":
            for key in ("kind", "generation_request", "request", "pinned_body"):
                if key not in data:
                    problems.append(f"ORPHANS {case_id}: generation-surface case missing {key!r} — "
                                    "both harness phases need it")
            golden = root / "goldens" / str(data.get("provider")) / f"{data.get('feature')}.json"
            if not golden.is_file():
                problems.append(f"ORPHANS {case_id}: generation-surface case has no golden at "
                                f"goldens/{data.get('provider')}/{data.get('feature')}.json — "
                                "the parse phase would silently skip")
        if data.get("surface") in ("files", "batch", "video"):
            steps = data.get("steps")
            if not isinstance(steps, list) or not steps:
                problems.append(f"ORPHANS {case_id}: {data.get('surface')}-surface case has no steps")
            else:
                for i, step in enumerate(steps):
                    has_wire = "request" in step or "requests" in step
                    if not has_wire:
                        problems.append(f"ORPHANS {case_id}: step {i} pins no wire request block")
                    fetched = step.get("fetched_from", [])
                    fetched = [fetched] if isinstance(fetched, str) else list(fetched)
                    for name in fetched or ([step["pinned_body"]] if "pinned_body" in step else []):
                        if not (bodies / str(case_id) / str(name)).is_file():
                            problems.append(f"ORPHANS {case_id}: step {i} references missing body {name!r}")
            golden = root / "goldens" / str(data.get("provider")) / f"{data.get('feature')}.json"
            if not golden.is_file():
                problems.append(f"ORPHANS {case_id}: {data.get('surface')}-surface case has no golden")
        if data.get("surface") == "models":
            for key in ("request", "pinned_body", "entries_key"):
                if key not in data:
                    problems.append(f"ORPHANS {case_id}: models-surface case missing {key!r} — "
                                    "both harness phases need it")
            golden = root / "goldens" / str(data.get("provider")) / f"{data.get('feature')}.json"
            if not golden.is_file():
                problems.append(f"ORPHANS {case_id}: models-surface case has no golden at "
                                f"goldens/{data.get('provider')}/{data.get('feature')}.json — "
                                "the parse phase would silently skip")
        if data.get("surface") == "live":
            for key in ("live_config", "pinned_body"):
                if key not in data:
                    problems.append(f"ORPHANS {case_id}: live-surface case missing {key!r} — "
                                    "the replay needs it")
            golden = root / "goldens" / str(data.get("provider")) / f"{data.get('feature')}.json"
            if not golden.is_file():
                problems.append(f"ORPHANS {case_id}: live-surface case has no golden at "
                                f"goldens/{data.get('provider')}/{data.get('feature')}.json — "
                                "the decode phase would silently skip")
            transcript_path = bodies / str(case_id) / str(data.get("pinned_body", ""))
            if transcript_path.is_file():
                for i, line in enumerate(transcript_path.read_text().splitlines()):
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    if entry.get("dir") not in ("client", "server"):
                        problems.append(f"ORPHANS {case_id}: transcript line {i} has no "
                                        "client/server dir — not a directed frame")
                        break

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


# ─── 3. RAW-PROVIDER LINT (hard: every passthrough case needs a verdict) ─

def check_extensions_verdicts(root: Path, cases: list[tuple[Path, dict]],
                              problems: list[str]) -> str:
    """Every config.extensions passthrough case must carry an explicit
    verdict (tools/extensions-verdicts.json): blessed permanent (INV-049)
    or deferred to a NAMED design pass. An unlisted passthrough case is a
    dodged design question — hard violation. Stale registry entries (case
    gone, or extensions removed by promotion) are violations too: the
    registry mirrors the corpus exactly, both directions."""
    registry_path = root / "tools" / "extensions-verdicts.json"
    if not registry_path.is_file():
        problems.append(f"EXTENSIONS {registry_path}: verdict registry missing")
        return "extensions-verdicts: registry missing"
    registry = json.loads(registry_path.read_text())
    blessed = dict(registry.get("blessed", {}))
    deferred = dict(registry.get("deferred", {}))
    overlap = set(blessed) & set(deferred)
    for case_id in sorted(overlap):
        problems.append(f"EXTENSIONS {case_id}: listed as BOTH blessed and deferred")

    smugglers: set[str] = set()
    for path, data in cases:
        canonical = data.get("canonical_request")
        if not isinstance(canonical, dict):
            continue
        config = canonical.get("config")
        if isinstance(config, dict) and config.get("extensions"):
            smugglers.add(str(data.get("id", path.relative_to(root))))

    undecided = smugglers - set(blessed) - set(deferred)
    for case_id in sorted(undecided):
        problems.append(f"EXTENSIONS {case_id}: config.extensions passthrough with NO verdict — "
                        "promote the knob to a canonical field, bless it (INV-049 + registry), "
                        "or defer it to a NAMED design pass in tools/extensions-verdicts.json")
    for case_id in sorted((set(blessed) | set(deferred)) - smugglers):
        problems.append(f"EXTENSIONS tools/extensions-verdicts.json: stale entry {case_id!r} — "
                        "no such passthrough case (promoted or removed); delete the entry")
    for case_id in sorted(deferred):
        print(f"REPORT extensions-deferred: {case_id} — {deferred[case_id]}")
    return (f"extensions-verdicts: {len(smugglers)} passthrough case(s) — "
            f"{len(blessed & smugglers if isinstance(blessed, set) else set(blessed) & smugglers)} blessed permanent (INV-049), "
            f"{len(set(deferred) & smugglers)} deferred to named design passes, "
            f"{len(undecided)} undecided")


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


def check_support_matrix(root: Path, python2: Path, problems: list[str]) -> str:
    """HARD: spec/support-matrix.json must equal the reference's reflected
    provider manifests (surface_dump.providers), both directions.  A skipped
    comparison (no shim) is report-only — the pin still binds ports."""
    pinned_path = root / "spec" / "support-matrix.json"
    if not pinned_path.is_file():
        problems.append("SUPPORT-MATRIX: spec/support-matrix.json is missing")
        return "support matrix: MISSING"
    pinned = json.loads(pinned_path.read_text()).get("providers", {})
    surface, reason = shim_surface_dump(python2)
    if surface is None:
        print(f"REPORT support-matrix: comparison skipped — {reason}")
        return f"support matrix: pinned {len(pinned)} provider(s), comparison skipped ({reason})"
    reflected = surface.get("providers")
    if reflected is None:
        problems.append("SUPPORT-MATRIX: reference surface_dump exposes no providers section")
        return "support matrix: reference exposes no providers"
    for provider in sorted(set(pinned) | set(reflected)):
        if provider not in pinned:
            problems.append(f"SUPPORT-MATRIX: provider {provider!r} exists in the reference "
                            "but is not pinned — pin it (with receipts) or remove the adapter")
        elif provider not in reflected:
            problems.append(f"SUPPORT-MATRIX: provider {provider!r} is pinned but missing "
                            "from the reference")
        elif pinned[provider] != reflected[provider]:
            for key in sorted(set(pinned[provider]) | set(reflected[provider])):
                if pinned[provider].get(key) != reflected[provider].get(key):
                    problems.append(f"SUPPORT-MATRIX: {provider}.{key} drift — pinned "
                                    f"{pinned[provider].get(key)!r}, reference {reflected[provider].get(key)!r}")
    return f"support matrix: {len(pinned)} provider(s) pinned and matching"


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
                        help="lm15-python checkout for the vet shim (default: sibling of --root)")
    parser.add_argument("--allowlist", type=Path, default=None,
                        help="orphan allowlist (default: <root>/tools/orphan-allowlist.json)")
    args = parser.parse_args(argv)
    root: Path = args.root
    python2: Path = args.python2 or root.parent / "lm15-python"
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
    body_dir_allowlist: set[str] = set()
    if allowlist_path.is_file():
        allowlist_data = json.loads(allowlist_path.read_text())
        allowlist = set(allowlist_data.get("orphans", []))
        body_dir_allowlist = set(allowlist_data.get("body_dirs", []))
    else:
        problems.append(f"ORPHANS {allowlist_path}: allowlist file missing")

    summaries = [
        check_orphans(root, cases, allowlist, body_dir_allowlist, problems),
        check_volatile(root, cases, problems),
        check_extensions_verdicts(root, cases, problems),
        report_surface_coverage(root, python2),
        check_support_matrix(root, python2, problems),
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
