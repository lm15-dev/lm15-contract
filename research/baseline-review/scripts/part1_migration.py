#!/usr/bin/env python3
"""Independent verification of the 2026-09-06 golden migration.

For every golden: old = git show cf298d2:<path>, new = working tree.
Independently apply the allowed transforms (a), (b), (d) to the old golden,
then diff the result against the new golden.  Remaining differences must be
exactly (c) added provider_data on `end` events and (e) provenance appended
sentence.  Everything else is reported with its JSON path.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/maxime/Projects/lm15-dev/lm15-contract")
OLD = "cf298d2"
GEMINI_D = {"goldens/gemini/tools.json", "goldens/gemini/tool_config_auto.json", "goldens/gemini/tool_config_any.json"}
DROP_KINDS = {"response_id", "message_id"}
_ABSENT = object()

NOTE_RE = re.compile(
    r"^ Re-reviewed 2026-09-06 for D5/D8/D9 \(changes/2026-09-06-decisions\.md, "
    r"changes/2026-09-06-ratification\.md\): change verified by "
    r"tools/migrate_goldens_2026_09_06\.py to be exactly (?P<what>.+)\.$"
)


def git_show(rel: str) -> dict | None:
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{OLD}:{rel}"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def render(path) -> str:
    out = "$"
    for seg in path:
        out += f"[{seg}]" if isinstance(seg, int) else f".{seg}"
    return out


# ---------- independent transform: (a), (b), (d) ----------

def is_msg_level_cont_delta(ev) -> str | None:
    if not isinstance(ev, dict) or ev.get("type") != "delta":
        return None
    d = ev.get("delta")
    if not isinstance(d, dict) or d.get("type") != "continuation":
        return None
    if d.get("part_index") is not None:
        return None
    if d.get("kind") in DROP_KINDS:
        return f"{d.get('provider')}:{d.get('kind')}"
    return None


def transform(node, counts: Counter, gemini: bool, path=()):
    if isinstance(node, list):
        out = []
        for i, item in enumerate(node):
            k = is_msg_level_cont_delta(item)
            if k is not None:
                counts[f"a_event:{k}"] += 1
                continue
            out.append(transform(item, counts, gemini, path + (i,)))
        return out
    if not isinstance(node, dict):
        return node
    node = dict(node)
    # (a) message-level continuation entries (objects with a role)
    if "role" in node and isinstance(node.get("continuation"), list):
        kept = []
        for e in node["continuation"]:
            if isinstance(e, dict) and e.get("kind") in DROP_KINDS:
                counts[f"a_entry:{e.get('provider')}:{e.get('kind')}"] += 1
                continue
            kept.append(e)
        if kept:
            node["continuation"] = kept
        else:
            del node["continuation"]
    # (b) thinking parts / deltas
    if node.get("type") == "thinking":
        if "redacted" in node:
            counts[f"b_redacted_key:{node['redacted']}"] += 1
            del node["redacted"]
        if node.get("text") == "[redacted]":
            counts["b_text_placeholder"] += 1
            node["text"] = ""
    # (d) gemini minted ids
    if gemini and node.get("type") == "tool_call" and isinstance(node.get("id"), str):
        m = re.fullmatch(r"fc_(\d+)", node["id"])
        if m:
            counts["d_gemini_id"] += 1
            node["id"] = f"tool_call_{m.group(1)}"
    return {k: transform(v, counts, gemini, path + (k,)) for k, v in node.items()}


# ---------- diff ----------

def diffs(a, b, path=()):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out.extend(diffs(a.get(k, _ABSENT), b.get(k, _ABSENT), path + (k,)))
        return out
    if isinstance(a, list) and isinstance(b, list):
        out = []
        for i in range(max(len(a), len(b))):
            out.extend(diffs(a[i] if i < len(a) else _ABSENT, b[i] if i < len(b) else _ABSENT, path + (i,)))
        return out
    if a is _ABSENT and b is _ABSENT:
        return []
    if type(a) is type(b) and a == b:
        return []
    return [(path, a, b)]


def classify(path, old_v, new_v, new_golden, notes: dict) -> str | None:
    """Return a transform tag if allowed, else None."""
    # (c) added provider_data on end events (top-level events only)
    if (len(path) == 3 and path[0] == "events" and isinstance(path[1], int) and path[2] == "provider_data"
            and old_v is _ABSENT and isinstance(new_v, dict)):
        evs = new_golden.get("events")
        if isinstance(evs, list) and path[1] < len(evs) and evs[path[1]].get("type") == "end":
            return "c_end_provider_data"
        return None
    # (e) provenance
    if len(path) == 2 and path[0] == "provenance" and path[1] in ("reviewed", "evidence"):
        if isinstance(old_v, str) and isinstance(new_v, str):
            for base in (old_v.rstrip() + ".", old_v):
                if new_v.startswith(base):
                    tail = new_v[len(base):]
                    m = NOTE_RE.match(tail)
                    if m:
                        notes["what"] = m.group("what")
                        notes["key"] = path[1]
                        return f"e_provenance_{path[1]}"
                    # allow a different appended sentence but flag it for inspection
                    notes["what"] = tail
                    notes["key"] = path[1]
                    notes["nonstandard"] = True
                    return f"e_provenance_{path[1]}_nonstandard"
        return None
    return None


def main() -> int:
    goldens = sorted(p for p in (ROOT / "goldens").glob("*/*.json"))
    assert len(goldens) == 327, len(goldens)
    totals = Counter()
    per_file = {}
    out_of_scope = []
    missing_old = []
    changed_files = 0
    c_files = []
    for gp in goldens:
        rel = gp.relative_to(ROOT).as_posix()
        new = json.loads(gp.read_text())
        old = git_show(rel)
        if old is None:
            missing_old.append(rel)
            continue
        counts = Counter()
        mig = transform(old, counts, rel in GEMINI_D)
        notes = {}
        rest = []
        for path, a, b in diffs(mig, new):
            tag = classify(path, a, b, new, notes)
            if tag is None:
                rest.append((render(path), a, b))
            else:
                counts[tag] += 1
        if old != new:
            changed_files += 1
        if counts.get("c_end_provider_data"):
            c_files.append(rel)
        # provenance sanity: key sets equal
        po, pn = old.get("provenance", {}), new.get("provenance", {})
        if set(po) != set(pn):
            rest.append(("$.provenance<keys>", sorted(po), sorted(pn)))
        # every transform applied to old must be visible in the file diff, else the
        # transform was a no-op relative to new (i.e. new still has the old value) -> would appear in rest
        per_file[rel] = (counts, notes, rest)
        totals.update(counts)
        for r in rest:
            out_of_scope.append((rel, *r))

    # ---- report ----
    print(f"goldens: {len(goldens)}; changed vs {OLD}: {changed_files}; missing in {OLD}: {missing_old}")
    print("\nTransform counts (leaf-level):")
    for k in sorted(totals):
        print(f"  {k}: {totals[k]}")
    files_by = Counter()
    for rel, (counts, notes, rest) in per_file.items():
        for k in counts:
            files_by[k.split(":")[0]] += 1
    print("\nFiles touched per transform family:")
    for k in sorted(files_by):
        print(f"  {k}: {files_by[k]}")
    print(f"\nFiles with (c) end provider_data added: {len(c_files)}")
    print("\nOut-of-scope differences:")
    if not out_of_scope:
        print("  NONE")
    for rel, p, a, b in out_of_scope:
        sa = "<absent>" if a is _ABSENT else json.dumps(a, ensure_ascii=False)[:160]
        sb = "<absent>" if b is _ABSENT else json.dumps(b, ensure_ascii=False)[:160]
        print(f"  {rel} {p}: old/migrated={sa} new={sb}")

    # (e) consistency: a changed file must carry a note; an unchanged file must not
    print("\nProvenance note consistency:")
    problems = 0
    for rel, (counts, notes, rest) in per_file.items():
        content_changed = any(not k.startswith("e_") for k in counts)
        has_note = any(k.startswith("e_") for k in counts)
        if content_changed and not has_note:
            print(f"  {rel}: content changed but no provenance note")
            problems += 1
        if has_note and not content_changed:
            print(f"  {rel}: provenance note but no content change")
            problems += 1
        if notes.get("nonstandard"):
            print(f"  {rel}: NONSTANDARD note on {notes['key']}: {notes['what'][:200]}")
    if not problems:
        print("  all changed files carry exactly one appended note; no note on unchanged files")

    # (e) frozen -> reviewed, draft -> evidence
    print("\nNote placement (frozen->reviewed, draft->evidence):")
    bad = 0
    for rel, (counts, notes, rest) in per_file.items():
        if not notes:
            continue
        old = git_show(rel)
        frozen = bool((old.get("provenance") or {}).get("reviewed"))
        want = "reviewed" if frozen else "evidence"
        if notes["key"] != want:
            print(f"  {rel}: note on {notes['key']} but golden is {'frozen' if frozen else 'draft'}")
            bad += 1
    if not bad:
        print("  correct for every annotated golden")

    # note text vs. actual counts (does "what" describe what happened?)
    print("\nNote text vs. observed transform (spot check of numbers):")
    mism = 0
    for rel, (counts, notes, rest) in per_file.items():
        if not notes or notes.get("nonstandard"):
            continue
        what = notes["what"]
        a_entries = sum(v for k, v in counts.items() if k.startswith("a_entry:"))
        a_events = sum(v for k, v in counts.items() if k.startswith("a_event:"))
        b_true = counts.get("b_redacted_key:True", 0)
        b_false = counts.get("b_redacted_key:False", 0)
        c = counts.get("c_end_provider_data", 0)
        checks = []
        if a_entries:
            checks.append(re.search(rf"removed {a_entries} message-level", what) is not None)
        if a_events:
            checks.append(re.search(rf"\b{a_events} delta event", what) is not None)
        if b_true:
            checks.append(re.search(rf"rewrote {b_true} ThinkingPart", what) is not None)
        if b_false:
            checks.append(re.search(rf"dropped {b_false} ThinkingPart redacted=false", what) is not None)
        if c:
            checks.append("end provider_data added" in what)
        else:
            checks.append("end provider_data added" not in what)
        if not all(checks):
            mism += 1
            print(f"  {rel}: note '{what[:160]}' vs counts {dict(counts)}")
    if not mism:
        print("  every note's numbers agree with the observed transform")

    json.dump(
        {rel: {"counts": dict(c), "notes": n, "rest": [(p, str(a), str(b)) for p, a, b in r]} for rel, (c, n, r) in per_file.items()},
        open("/tmp/rereview/part1_per_file.json", "w"), indent=1, ensure_ascii=False,
    )
    return 1 if out_of_scope else 0


if __name__ == "__main__":
    sys.exit(main())
