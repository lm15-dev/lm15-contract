#!/usr/bin/env python3
"""Golden migration for MAP-19, one meaning per usage counter (2026-10-31).

The record of a scripted, verifiable transform over the goldens, as the
2026-09-06 migration was.  Rules: docs/mapping-rules.md MAP-19 and
changes/2026-10-31-usage-one-meaning.md.

For every Usage object in every golden (a ``usage`` member anywhere: a
response, a stream end event, a live turn end, a batch entry, a generation
response) this tool:

  (a) finds its source: the provider usage object in the case's recorded
      bodies that the 1.x rule (counters provider-verbatim, 2026-09-02)
      maps to exactly this Usage (or, on a re-run, that MAP-19 maps to it).  No source, or two sources that disagree
      under MAP-19, is a finding: nothing is written, exit status 1.
  (b) computes the MAP-19 Usage from that source, with this file's own
      reading of the rule (it imports nothing from any implementation).
  (c) checks the result against INV-029 (parts within wholes, total =
      input + output).

Verification: the reference (lm15-python), changed independently from its own
reading of MAP-19, must then pass every harness direction against the
migrated goldens (response, stream, live, batch, generation): two separate
readings of the rule agree. On 2026-10-31 it did, and so did the five ports.

Writing (``--write``): each changed golden gets its new usage objects and one
sentence appended to its provenance (``reviewed`` when frozen, else
``evidence``) naming exactly what changed.  Unchanged goldens are not
rewritten.

    python3 tools/migrate_goldens_2026_10_31.py            # report only
    python3 tools/migrate_goldens_2026_10_31.py --write
"""

from __future__ import annotations

import argparse
import base64
import copy
import json
import sys
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
GOLDENS = ROOT / "goldens"
BODIES = ROOT / "bodies"
TABLES = ROOT / "tables" / "providers.json"
COUNTERS = ("input_tokens", "output_tokens", "total_tokens", "cache_read_tokens", "cache_write_tokens",
            "reasoning_tokens", "input_audio_tokens", "output_audio_tokens")
NOTE = ("Re-reviewed 2026-10-31 for MAP-19 (changes/2026-10-31-usage-one-meaning.md): "
        "usage verified by tools/migrate_goldens_2026_10_31.py to be exactly {what}.")

# ─── Which wire rule a golden directory reads under ──────────────────────


def dialects() -> dict[str, tuple[str, str | None]]:
    """provider id → (dialect, chat preset) from the published tables."""
    tables = json.loads(TABLES.read_text(encoding="utf-8"))
    chat_presets = set(tables["compat"]["chat"])
    # An adapter-owned row (xai) names no preset; its adapter uses the preset of its own name.
    out = {row["id"]: (row["dialect"], row.get("compat") or (row["id"] if row["id"] in chat_presets else None))
           for row in tables["providers"]}
    out["openai_chat"] = ("openai-chat", "openai")  # the corpus's older spelling of openai-chat
    return out


SEPARATE_REASONING = {"xai"}  # chat presets whose completion_tokens exclude reasoning (MAP-19 rule 4)

# ─── Raw provider usage objects in a case's bodies ───────────────────────


def _json_objects(text: str) -> Iterator[Any]:
    text = text.strip()
    try:
        yield json.loads(text)
        return
    except ValueError:
        pass
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            line = line[5:].strip()
        if line[:1] in ("{", "["):
            try:
                yield json.loads(line)
            except ValueError:
                pass


def _usage_objects(node: Any) -> Iterator[dict]:
    if isinstance(node, str) and node[:1] == "{":  # a recorded live frame is a JSON text inside the record
        try:
            node = json.loads(node)
        except ValueError:
            return
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("usage", "usageMetadata") and isinstance(value, dict):
                yield value
            if key == "frame_b64" and isinstance(value, str):  # a recorded binary live frame
                try:
                    value = base64.b64decode(value).decode("utf-8")
                except ValueError:
                    continue
            yield from _usage_objects(value)
    elif isinstance(node, list):
        for item in node:
            yield from _usage_objects(item)


def raw_usages(case_id: str, pinned: str | None) -> list[dict]:
    paths: list[Path] = []
    for directory in sorted(BODIES.glob(f"{case_id}*")):
        if directory.is_dir():
            files = sorted(p for p in directory.iterdir() if p.is_file())
            if pinned and (directory / pinned).is_file() and directory.name == case_id:
                files = [directory / pinned] + [p for p in files if p.name != pinned]
            paths.extend(files)
        elif directory.is_file():
            paths.append(directory)
    found: list[dict] = []
    for path in paths:
        for obj in _json_objects(path.read_text(encoding="utf-8", errors="replace")):
            found.extend(_usage_objects(obj))
    return found


# ─── The 1.x rule (provider-verbatim) and the MAP-19 rule ────────────────


def _d(obj: Any, *keys: str) -> dict:
    for key in keys:
        if isinstance(obj, dict) and isinstance(obj.get(key), dict):
            return obj[key]
    return {}


def _clean(u: dict[str, Any]) -> dict[str, int]:
    out = {k: v for k, v in u.items() if v is not None}
    if "total_tokens" not in out and "input_tokens" in out and "output_tokens" in out:
        out["total_tokens"] = out["input_tokens"] + out["output_tokens"]
    return {k: out[k] for k in COUNTERS if k in out}


def _modality(details: Any, modality: str) -> int | None:
    if not isinstance(details, list):
        return None
    counts = [e.get("tokenCount", 0) for e in details if isinstance(e, dict) and e.get("modality") == modality]
    return sum(counts) if counts else None


def old_rule(dialect: str, raw: dict) -> dict[str, int] | None:
    if dialect == "anthropic":
        if "input_tokens" not in raw and "output_tokens" not in raw:
            return None
        thinking = _d(raw, "output_tokens_details").get("thinking_tokens")
        return _clean({"input_tokens": raw.get("input_tokens"), "output_tokens": raw.get("output_tokens"),
                       "cache_read_tokens": raw.get("cache_read_input_tokens"),
                       "cache_write_tokens": raw.get("cache_creation_input_tokens"), "reasoning_tokens": thinking})
    if dialect == "gemini":
        if not raw:
            return None
        out = 0
        for key in ("candidatesTokenCount", "responseTokenCount"):
            if key in raw:
                out = raw[key]
                break
        return _clean({"input_tokens": raw.get("promptTokenCount", 0), "output_tokens": out,
                       "total_tokens": raw.get("totalTokenCount"), "cache_read_tokens": raw.get("cachedContentTokenCount"),
                       "reasoning_tokens": raw.get("thoughtsTokenCount"),
                       "input_audio_tokens": _modality(raw.get("promptTokensDetails"), "AUDIO"),
                       "output_audio_tokens": _modality(raw.get("candidatesTokensDetails") or raw.get("responseTokensDetails"), "AUDIO")})
    if dialect == "openai-chat":
        if "prompt_tokens" not in raw and "completion_tokens" not in raw:
            return None
        pd, cd = _d(raw, "prompt_tokens_details"), _d(raw, "completion_tokens_details")
        cached = pd.get("cached_tokens") if pd.get("cached_tokens") is not None else raw.get("cached_tokens")
        return _clean({"input_tokens": raw.get("prompt_tokens"), "output_tokens": raw.get("completion_tokens"),
                       "total_tokens": raw.get("total_tokens"), "reasoning_tokens": cd.get("reasoning_tokens"),
                       "cache_read_tokens": cached, "cache_write_tokens": pd.get("cache_write_tokens"),
                       "input_audio_tokens": pd.get("audio_tokens"), "output_audio_tokens": cd.get("audio_tokens")})
    if dialect in ("openai-responses", "typesafe"):
        if "input_tokens" not in raw and "output_tokens" not in raw:
            return None
        ind = _d(raw, "input_tokens_details", "input_token_details")
        outd = _d(raw, "output_tokens_details", "output_token_details")
        return _clean({"input_tokens": raw.get("input_tokens"), "output_tokens": raw.get("output_tokens"),
                       "total_tokens": raw.get("total_tokens"), "reasoning_tokens": outd.get("reasoning_tokens"),
                       "cache_read_tokens": ind.get("cached_tokens"), "cache_write_tokens": ind.get("cache_write_tokens"),
                       "input_audio_tokens": ind.get("audio_tokens"), "output_audio_tokens": outd.get("audio_tokens")})
    return None


def _withhold(u: dict[str, int | None]) -> dict[str, int | None]:
    """MAP-19 rule 3: a part larger than its whole withholds the whole; a
    provider total that is not input + output withholds both."""
    i, o, t = u.get("input_tokens"), u.get("output_tokens"), u.get("total_tokens")
    if i is not None and (sum(u.get(k) or 0 for k in ("cache_read_tokens", "cache_write_tokens")) > i
                          or (u.get("input_audio_tokens") or 0) > i):
        u["input_tokens"] = i = None
    if o is not None and ((u.get("reasoning_tokens") or 0) > o or (u.get("output_audio_tokens") or 0) > o):
        u["output_tokens"] = o = None
    if t is not None and i is not None and o is not None and t != i + o:
        u["input_tokens"] = u["output_tokens"] = None
    return u


def _sum(*values: int | None) -> int | None:
    return None if any(v is None for v in values) else sum(v for v in values if v is not None)


def new_rule(dialect: str, preset: str | None, raw: dict) -> dict[str, int]:
    if dialect == "anthropic":
        thinking = _d(raw, "output_tokens_details").get("thinking_tokens")
        u = {"input_tokens": _sum(raw.get("input_tokens"), raw.get("cache_read_input_tokens"), raw.get("cache_creation_input_tokens")),
             "output_tokens": raw.get("output_tokens"), "total_tokens": raw.get("total_tokens"),
             "cache_read_tokens": raw.get("cache_read_input_tokens"),
             "cache_write_tokens": raw.get("cache_creation_input_tokens"), "reasoning_tokens": thinking}
    elif dialect == "gemini":
        n = lambda k: raw.get(k) or 0  # noqa: E731 — proto3 JSON omits zeros inside a present usageMetadata
        answer = 0
        for key in ("candidatesTokenCount", "responseTokenCount"):
            if key in raw:
                answer = raw[key]
                break
        audio_in = [_modality(raw.get(k), "AUDIO") for k in ("promptTokensDetails", "toolUsePromptTokensDetails")]
        u = {"input_tokens": n("promptTokenCount") + n("toolUsePromptTokenCount"),
             "output_tokens": answer + n("thoughtsTokenCount"), "total_tokens": raw.get("totalTokenCount"),
             "cache_read_tokens": n("cachedContentTokenCount"), "reasoning_tokens": n("thoughtsTokenCount"),
             "input_audio_tokens": None if all(a is None for a in audio_in) else sum(a or 0 for a in audio_in),
             "output_audio_tokens": _modality(raw.get("candidatesTokensDetails") or raw.get("responseTokensDetails"), "AUDIO")}
    elif dialect == "openai-chat":
        pd, cd = _d(raw, "prompt_tokens_details"), _d(raw, "completion_tokens_details")
        cached = pd.get("cached_tokens") if pd.get("cached_tokens") is not None else raw.get("cached_tokens")
        prompt, completion, total, reasoning = raw.get("prompt_tokens"), raw.get("completion_tokens"), raw.get("total_tokens"), cd.get("reasoning_tokens")
        output = completion
        if preset in SEPARATE_REASONING and completion is not None:
            if reasoning is not None:
                output = completion + reasoning
            elif not (total is not None and prompt is not None and total == prompt + completion):
                output = None
        u = {"input_tokens": prompt, "output_tokens": output, "total_tokens": total, "reasoning_tokens": reasoning,
             "cache_read_tokens": cached, "cache_write_tokens": pd.get("cache_write_tokens"),
             "input_audio_tokens": pd.get("audio_tokens"), "output_audio_tokens": cd.get("audio_tokens")}
    else:  # openai-responses (and Realtime), typesafe: already one meaning
        ind = _d(raw, "input_tokens_details", "input_token_details")
        outd = _d(raw, "output_tokens_details", "output_token_details")
        u = {"input_tokens": raw.get("input_tokens"), "output_tokens": raw.get("output_tokens"),
             "total_tokens": raw.get("total_tokens"), "reasoning_tokens": outd.get("reasoning_tokens"),
             "cache_read_tokens": ind.get("cached_tokens"), "cache_write_tokens": ind.get("cache_write_tokens"),
             "input_audio_tokens": ind.get("audio_tokens"), "output_audio_tokens": outd.get("audio_tokens")}
    return _clean(_withhold(u))


def inv029(u: dict[str, int]) -> str | None:
    i, o = u.get("input_tokens"), u.get("output_tokens")
    if i is not None and (u.get("cache_read_tokens", 0) + u.get("cache_write_tokens", 0) > i or u.get("input_audio_tokens", 0) > i):
        return "a part of input exceeds input"
    if o is not None and (u.get("reasoning_tokens", 0) > o or u.get("output_audio_tokens", 0) > o):
        return "a part of output exceeds output"
    if "total_tokens" in u and i is not None and o is not None and u["total_tokens"] != i + o:
        return "total is not input + output"
    return None


# ─── Walking the goldens ─────────────────────────────────────────────────


def usage_sites(node: Any, path: str = "$") -> Iterator[tuple[str, dict, str]]:
    if isinstance(node, dict):
        for key, value in node.items():
            sub = f"{path}.{key}"
            if key == "provider_data":
                continue  # the provider's own object, verbatim: not a canonical Usage
            if key == "usage" and isinstance(value, dict):
                yield sub, node, key
            else:
                yield from usage_sites(value, sub)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from usage_sites(item, f"{path}[{index}]")


def describe(old: dict, new: dict) -> str:
    changes = []
    for key in COUNTERS:
        a, b = old.get(key), new.get(key)
        if a != b:
            changes.append(f"{key} {'absent' if a is None else a} → {'absent' if b is None else b}")
    return ", ".join(changes)


def migrate(write: bool) -> int:
    table = dialects()
    findings: list[str] = []
    changed_files = 0
    changed_sites = 0
    for golden_path in sorted(GOLDENS.glob("*/*.json")):
        provider = golden_path.parent.name
        if provider not in table:
            continue
        dialect, preset = table[provider]
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        provenance = golden.get("provenance") or {}
        case_id = f"{provider}.{golden_path.stem}"
        if not any(BODIES.glob(f"{case_id}*")) and not (ROOT / "cases" / provider.replace("-", "_") / golden_path.name).exists() \
                and not (ROOT / "cases" / provider / golden_path.name).exists():
            print(f"skipped (no case, no body: withdrawn): {golden_path.relative_to(ROOT)}")
            continue
        raws = raw_usages(case_id, provenance.get("pinned_body"))
        updated = copy.deepcopy(golden)
        notes: list[str] = []
        for path, parent, key in list(usage_sites(updated)):
            old = parent[key]
            if not any(k in old for k in COUNTERS):
                continue
            # A source is the recorded usage the golden was read from: under the
            # 1.x rule before migration, under MAP-19 after it (a re-run then
            # changes nothing, and still proves every golden has a source).
            new_candidates = {json.dumps(new_rule(dialect, preset, raw), sort_keys=True)
                              for raw in raws
                              if _clean(dict(old)) in (old_rule(dialect, raw), new_rule(dialect, preset, raw))}
            if not new_candidates:
                findings.append(f"{golden_path.relative_to(ROOT)} {path}: no recorded usage maps to {old} under the 1.x rule")
                continue
            if len(new_candidates) > 1:
                findings.append(f"{golden_path.relative_to(ROOT)} {path}: sources disagree under MAP-19: {sorted(new_candidates)}")
                continue
            new = {key: value for key, value in json.loads(new_candidates.pop()).items()}
            new = {key: new[key] for key in COUNTERS if key in new}  # canonical member order
            problem = inv029(new)
            if problem:
                findings.append(f"{golden_path.relative_to(ROOT)} {path}: MAP-19 result {new} breaks INV-029 ({problem})")
                continue
            if new != old:
                parent[key] = new
                notes.append(f"{path}: {describe(old, new)}")
                changed_sites += 1
        if notes:
            changed_files += 1
            print(f"{golden_path.relative_to(ROOT)}")
            for note in notes:
                print(f"    {note}")
            if write:
                field = "reviewed" if "reviewed" in provenance else "evidence"
                sentence = NOTE.format(what="; ".join(notes))
                prior = updated["provenance"].get(field, "").rstrip()
                if prior and not prior.endswith("."):
                    prior += "."
                updated["provenance"][field] = f"{prior} {sentence}".strip()
                golden_path.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{changed_sites} usage objects in {changed_files} goldens change; {len(findings)} findings")
    for finding in findings:
        print("FINDING:", finding)
    return 1 if findings else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true", help="write the migrated goldens (default: report only)")
    args = parser.parse_args()
    if args.write:
        status = migrate(write=False)
        if status:
            print("\nnothing written: resolve the findings first", file=sys.stderr)
            return status
    return migrate(write=args.write)


if __name__ == "__main__":
    sys.exit(main())
