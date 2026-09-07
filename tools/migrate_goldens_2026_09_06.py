#!/usr/bin/env python3
"""Golden migration for the 2026-09-06 ratification (D5, D8, D9).

The record of a scripted, verifiable transform over frozen goldens, as the
MAP-3 and MAP-4 precedents were (see goldens/anthropic/streaming.json
provenance).  Rules: verify/DECISIONS-2026-09-06.md, "Golden migration".

Transforms, applied to every golden under goldens/:

  (a) D8 — remove message-level continuation entries whose kind is
      ``response_id`` or ``message_id`` (an entry on a ``role``-bearing
      message object, never on a part), and message-level
      ``ContinuationDelta`` events (no ``part_index``) of those kinds.
  (b) D5 — remove ``redacted`` keys from thinking parts; a part that had
      ``redacted: true`` gets ``text: ""``; a ThinkingDelta whose text is
      exactly ``[redacted]`` gets ``text: ""``.
  (b′) D5, found by the scribe diff on the first run (2026-09-06): a
      stream-materialized ThinkingPart is the fold of its ThinkingDeltas, so
      the assembler never set the ``redacted`` flag and the part reads
      ``text: "[redacted]"`` with an ``anthropic:redacted_thinking``
      continuation and no flag (goldens/meta-anthropic/streaming_tool_call
      .json, ``$.canonical_response.message.parts[0]`` and ``[1]``).  Such a
      part gets ``text: ""`` — the same rule as the deltas it folds.  Counted
      and named separately in the per-file summary.

Verification against the fixed reference:

  (c) D9 — ``tools/scribe_goldens.py --out DIR`` re-scribes every
      chat-surface golden from the reference into DIR (content only).  The
      migrated goldens are diffed against DIR: the ONLY allowed difference
      is an added ``provider_data`` (a JSON object) on ``end`` events.  Any
      other difference is a finding: it is printed with the file and JSON
      path, nothing is written, and the exit status is 1.

Writing (``--write``): final golden = migrated content + (c).  Every
existing provenance key is kept; the re-review sentence stating exactly what
changed is appended to ``reviewed`` (frozen goldens) or ``evidence`` (draft
goldens).  Goldens the transforms and (c) leave untouched are not rewritten.

Goldens the scribe does not cover (surface goldens such as batch, which
carry canonical responses inside ``entries``) are transformed by (a)/(b)
and reported as "not scribe-covered"; the harness ``--direction batch`` run
against the fixed reference is their verification.

Pipeline:

    python3 tools/scribe_goldens.py --out /tmp/scribe-2026-09-06
    python3 tools/migrate_goldens_2026_09_06.py --scratch /tmp/scribe-2026-09-06
    python3 tools/migrate_goldens_2026_09_06.py --scratch /tmp/scribe-2026-09-06 --write
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

CONTRACT_ROOT = Path(__file__).resolve().parent.parent
GOLDENS_DIR = CONTRACT_ROOT / "goldens"

DROPPED_KINDS = frozenset({"response_id", "message_id"})
CONTENT_KEYS = ("canonical_response", "events", "partial_response")
REVIEW_NOTE = (
    " Re-reviewed 2026-09-06 for D5/D8/D9 (verify/DECISIONS-2026-09-06.md, "
    "changes/2026-09-06-ratification.md): change verified by "
    "tools/migrate_goldens_2026_09_06.py to be exactly {what}."
)


@dataclass
class Summary:
    """What the transforms did to one golden."""

    continuations: list[str] = field(default_factory=list)  # "provider:kind"
    continuation_events: list[str] = field(default_factory=list)
    redacted_flags_true: int = 0
    redacted_flags_false: int = 0
    redacted_delta_texts: int = 0
    redacted_part_texts: int = 0
    end_provider_data_added: int = 0
    not_scribe_covered: bool = False

    @property
    def changed(self) -> bool:
        return bool(
            self.continuations or self.continuation_events or self.redacted_flags_true
            or self.redacted_flags_false or self.redacted_delta_texts or self.redacted_part_texts
            or self.end_provider_data_added
        )

    def describe(self) -> str:
        parts: list[str] = []
        if self.continuations:
            kinds = ", ".join(sorted(set(self.continuations)))
            n = len(self.continuations)
            text = f"removed {n} message-level {kinds} continuation{'s' if n != 1 else ''}"
            if self.continuation_events:
                m = len(self.continuation_events)
                text += f" and {'its' if m == 1 and n == 1 else 'their'} {m} delta event{'s' if m != 1 else ''}"
            parts.append(text)
        elif self.continuation_events:
            m = len(self.continuation_events)
            kinds = ", ".join(sorted(set(self.continuation_events)))
            parts.append(f"removed {m} message-level {kinds} continuation delta event{'s' if m != 1 else ''}")
        if self.redacted_flags_true:
            n = self.redacted_flags_true
            parts.append(f"rewrote {n} ThinkingPart{'s' if n != 1 else ''} with redacted=true to empty text without the flag")
        if self.redacted_flags_false:
            n = self.redacted_flags_false
            parts.append(f"dropped {n} ThinkingPart redacted=false flag{'s' if n != 1 else ''}")
        if self.redacted_delta_texts:
            n = self.redacted_delta_texts
            parts.append(f"rewrote {n} ThinkingDelta '[redacted]' text{'s' if n != 1 else ''} to empty")
        if self.redacted_part_texts:
            n = self.redacted_part_texts
            parts.append(
                f"rewrote {n} stream-materialized unflagged ThinkingPart '[redacted]' text{'s' if n != 1 else ''} "
                "to empty (the fold of the delta rule)"
            )
        if self.end_provider_data_added:
            parts.append("end provider_data added")
        return "; ".join(parts)


# ─── Transforms ──────────────────────────────────────────────────────

def _is_message_level_continuation_delta(event: object) -> str | None:
    if not isinstance(event, dict) or event.get("type") != "delta":
        return None
    delta = event.get("delta")
    if not isinstance(delta, dict) or delta.get("type") != "continuation":
        return None
    if "part_index" in delta and delta["part_index"] is not None:
        return None
    if delta.get("kind") in DROPPED_KINDS:
        return f"{delta.get('provider')}:{delta.get('kind')}"
    return None


def transform(node: object, summary: Summary) -> object:
    """Apply (a) and (b) recursively; returns the transformed node."""
    if isinstance(node, list):
        out = []
        for item in node:
            kind = _is_message_level_continuation_delta(item)
            if kind is not None:
                summary.continuation_events.append(kind)
                continue
            out.append(transform(item, summary))
        return out
    if not isinstance(node, dict):
        return node

    node = dict(node)
    # (a) message-level continuation entries: on an object with a role
    # (a Message), never on a part (parts have "type", no "role").
    if "role" in node and isinstance(node.get("continuation"), list):
        kept = []
        for entry in node["continuation"]:
            if isinstance(entry, dict) and entry.get("kind") in DROPPED_KINDS:
                summary.continuations.append(f"{entry.get('provider')}:{entry.get('kind')}")
                continue
            kept.append(entry)
        if kept:
            node["continuation"] = kept
        else:
            del node["continuation"]

    # (b) thinking parts and deltas.
    if node.get("type") == "thinking":
        if "redacted" in node:
            flag = node.pop("redacted")
            if flag is True:
                summary.redacted_flags_true += 1
                node["text"] = ""
            else:
                summary.redacted_flags_false += 1
        elif node.get("text") == "[redacted]" and "part_index" in node:
            summary.redacted_delta_texts += 1
            node["text"] = ""
        elif node.get("text") == "[redacted]" and any(
            isinstance(entry, dict) and entry.get("kind") == "redacted_thinking"
            for entry in (node.get("continuation") or [])
        ):
            summary.redacted_part_texts += 1  # (b′)
            node["text"] = ""

    return {key: transform(value, summary) for key, value in node.items()}


# ─── Diff against the scribe ─────────────────────────────────────────

_ABSENT = object()


def _render(path: tuple) -> str:
    out = "$"
    for seg in path:
        out += f"[{seg}]" if isinstance(seg, int) else f".{seg}"
    return out


def _diffs(expected: object, actual: object, path: tuple) -> list[tuple[tuple, object, object]]:
    """Every leaf difference between two JSON values as (path, expected, actual)."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        out = []
        for key in sorted(set(expected) | set(actual)):
            out.extend(_diffs(expected.get(key, _ABSENT), actual.get(key, _ABSENT), path + (key,)))
        return out
    if isinstance(expected, list) and isinstance(actual, list):
        out = []
        for i in range(max(len(expected), len(actual))):
            e = expected[i] if i < len(expected) else _ABSENT
            a = actual[i] if i < len(actual) else _ABSENT
            out.extend(_diffs(e, a, path + (i,)))
        return out
    if expected is _ABSENT and actual is _ABSENT:
        return []
    if type(expected) is type(actual) and expected == actual:
        return []
    return [(path, expected, actual)]


def _is_allowed_end_provider_data(path: tuple, migrated: dict, expected: object, actual: object) -> bool:
    """(c): ``events[i].provider_data`` absent in the migrated golden, a JSON
    object in the scribe output, on an ``end`` event."""
    if len(path) != 3 or path[0] != "events" or not isinstance(path[1], int) or path[2] != "provider_data":
        return False
    if expected is not _ABSENT or not isinstance(actual, dict):
        return False
    events = migrated.get("events")
    return isinstance(events, list) and path[1] < len(events) and events[path[1]].get("type") == "end"


@dataclass
class Finding:
    golden: Path
    path: str
    expected: object
    actual: object


def verify(golden: Path, migrated: dict, scratch: dict, summary: Summary) -> tuple[dict, list[Finding]]:
    """Diff the migrated golden against the scribe output; apply (c)."""
    final = copy.deepcopy(migrated)
    findings: list[Finding] = []
    for key in CONTENT_KEYS:
        for path, expected, actual in _diffs(migrated.get(key, _ABSENT), scratch.get(key, _ABSENT), (key,)):
            if _is_allowed_end_provider_data(path, migrated, expected, actual):
                final["events"][path[1]]["provider_data"] = actual
                summary.end_provider_data_added += 1
                continue
            findings.append(Finding(
                golden,
                _render(path),
                "<absent>" if expected is _ABSENT else expected,
                "<absent>" if actual is _ABSENT else actual,
            ))
    return final, findings


# ─── Provenance ──────────────────────────────────────────────────────

def annotate(final: dict, summary: Summary) -> None:
    provenance = final.get("provenance")
    if not isinstance(provenance, dict):
        raise SystemExit(f"golden without a provenance block: {final.keys()}")
    note = REVIEW_NOTE.format(what=summary.describe())
    key = "reviewed" if isinstance(provenance.get("reviewed"), str) and provenance["reviewed"] else "evidence"
    existing = str(provenance.get(key) or "").rstrip()
    if existing and not existing.endswith((".", ")")):
        existing += "."
    provenance[key] = existing + note


# ─── Main ────────────────────────────────────────────────────────────

def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scratch", metavar="DIR", required=True, help="output of tools/scribe_goldens.py --out DIR")
    parser.add_argument("--write", action="store_true", help="write the final goldens (default: dry run)")
    args = parser.parse_args(argv)
    scratch_dir = Path(args.scratch).resolve()
    if not scratch_dir.is_dir():
        parser.error(f"--scratch {scratch_dir} is not a directory")

    goldens = sorted(p for p in GOLDENS_DIR.glob("*/*.json"))
    finals: dict[Path, dict] = {}
    summaries: dict[Path, Summary] = {}
    findings: list[Finding] = []
    counts = {"goldens": 0, "changed": 0, "frozen_changed": 0, "not_scribe_covered_changed": 0,
              "scribe_covered": 0, "unchanged": 0}
    by_transform = {"a_continuations": 0, "a_events": 0, "b_true": 0, "b_false": 0, "b_delta": 0, "b_part": 0, "c_end": 0}

    for golden_path in goldens:
        counts["goldens"] += 1
        original = _load(golden_path)
        summary = Summary()
        migrated = transform(original, summary)
        rel = golden_path.relative_to(GOLDENS_DIR)
        scratch_path = scratch_dir / rel
        if scratch_path.exists():
            counts["scribe_covered"] += 1
            final, file_findings = verify(rel, migrated, _load(scratch_path), summary)
            findings.extend(file_findings)
        else:
            summary.not_scribe_covered = True
            final = migrated
        finals[golden_path] = final
        summaries[golden_path] = summary

    for golden_path in goldens:
        summary = summaries[golden_path]
        rel = golden_path.relative_to(GOLDENS_DIR)
        if not summary.changed:
            counts["unchanged"] += 1
            continue
        counts["changed"] += 1
        frozen = bool((_load(golden_path).get("provenance") or {}).get("reviewed"))
        if frozen:
            counts["frozen_changed"] += 1
        if summary.not_scribe_covered:
            counts["not_scribe_covered_changed"] += 1
        by_transform["a_continuations"] += len(summary.continuations)
        by_transform["a_events"] += len(summary.continuation_events)
        by_transform["b_true"] += summary.redacted_flags_true
        by_transform["b_false"] += summary.redacted_flags_false
        by_transform["b_delta"] += summary.redacted_delta_texts
        by_transform["b_part"] += summary.redacted_part_texts
        by_transform["c_end"] += summary.end_provider_data_added
        tag = "FROZEN" if frozen else "draft "
        cover = "" if not summary.not_scribe_covered else "  [not scribe-covered]"
        print(f"  {tag}  {rel}: {summary.describe()}{cover}")

    print()
    print(
        f"migrate_goldens_2026_09_06: {counts['goldens']} goldens, {counts['changed']} changed "
        f"({counts['frozen_changed']} frozen), {counts['unchanged']} unchanged, "
        f"{counts['scribe_covered']} scribe-covered, "
        f"{counts['not_scribe_covered_changed']} changed without scribe coverage"
    )
    print(
        f"  (a) removed {by_transform['a_continuations']} message-level id continuations "
        f"and {by_transform['a_events']} delta events; "
        f"(b) rewrote {by_transform['b_true']} redacted=true parts, dropped {by_transform['b_false']} "
        f"redacted=false flags, rewrote {by_transform['b_delta']} '[redacted]' deltas; "
        f"(b′) rewrote {by_transform['b_part']} unflagged materialized '[redacted]' parts; "
        f"(c) added {by_transform['c_end']} end provider_data"
    )

    if findings:
        print()
        print(f"STOP: {len(findings)} scribe-vs-migrated difference(s) outside (c); nothing written:")
        for f in findings:
            print(f"  {f.golden} {f.path}: golden={json.dumps(f.expected, ensure_ascii=False)[:200]} "
                  f"scribe={json.dumps(f.actual, ensure_ascii=False)[:200]}")
        return 1

    if not args.write:
        print("dry run: pass --write to write the final goldens")
        return 0

    written = 0
    for golden_path in goldens:
        summary = summaries[golden_path]
        if not summary.changed:
            continue
        final = finals[golden_path]
        annotate(final, summary)
        _dump(golden_path, final)
        written += 1
    print(f"wrote {written} goldens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
