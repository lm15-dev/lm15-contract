#!/usr/bin/env python3
"""Promote the tool-result-content fixture candidates into cases/ and bodies/.

Offline. The expected wire of a promoted case is what MAP-10 requires — the
wire the reference adapter builds from the canonical request — validated
against the wire the server accepted live: the tool-result items must be
byte-equal except the two documented allowances (a text-only result is a
string where the probe sent a one-block array; a document filename), and
any difference inside the replayed assistant turn is listed in the case's
provenance (response-only fields the verbatim replay carried: status, id,
caller, index, refusal, annotations — the same drop every existing
multi_turn_tool_result case makes). Anything else is NOT promoted and is
printed.

Reject presets get `expect_lm15.raises` cases citing the receipt of the
server 400 or the silent degrade.

    ../lm15-python/.venv/bin/python tools/promote_tool_result_cases.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CONTRACT / "research" / "providers"))
sys.path.insert(0, str(CONTRACT.parent / "lm15-python"))
import media_tool_results as probe  # noqa: E402
from lm15 import serde  # noqa: E402
from lm15.vet import adapter_for_provider  # noqa: E402

RECEIPTS = CONTRACT / "receipts" / "2026-09-07-tool-result-media"
CHANGE = "changes/2026-09-07-tool-result-content.md"
NATIVE_CELLS = ("image", "mixed", "pair", "pdf", "error", "text")
# Bindings whose SDK build needs host settings the offline promoter does not
# carry (azure, bedrock…) or whose first turn is SSE (codex): their receipts
# stand as evidence in the ledger; no case here.
SKIP = {"azure", "azure-chat", "azure-anthropic", "bedrock-chat", "bedrock-mantle-chat", "bedrock-anthropic", "openai-codex", "ollama"}
# The `error` cell is promoted only where the wire carries a real flag that
# was sent live (Anthropic is_error, Gemini response.error); on Responses and
# Chat the `[error] ` prefix is MAP-10.5, pinned by lm15-python tests.
ERROR_NATIVE_DIALECTS = {"anthropic", "gemini"}
REJECTS = {  # provider → (cell receipt to cite, why)
    "groq": ("image", "server 400: messages[2].content must be a string"),
    "meta-chat": ("image", "server 400: content did not match any supported type"),
    "deepseek": ("image", "HTTP 200 and the model reports [Unsupported Image] (silent degrade; control cell failed too)"),
    "deepseek-anthropic": ("image", "HTTP 200 and the model reports [Unsupported Image] (silent degrade)"),
    "openai-chat": ("image", "HTTP 200 and the model did not receive the image while the same model read the USER image (control cell)"),
}


def diff(a, b, p="$"):
    if type(a) is not type(b):
        yield (p, a, b)
        return
    if isinstance(a, dict):
        for k in sorted(a.keys() | b.keys()):
            if k not in a or k not in b:
                yield (p + "." + k, a.get(k, "<absent>"), b.get(k, "<absent>"))
            else:
                yield from diff(a[k], b[k], p + "." + k)
    elif isinstance(a, list):
        if len(a) != len(b):
            yield (p + ".length", len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b)):
            yield from diff(x, y, f"{p}[{i}]")
    elif a != b:
        yield (p, a, b)


def classify(dialect: str, cell: str, path: str, sent, sdk, first_result: int) -> str | None:
    """None = not allowed. Otherwise the allowance name recorded in provenance."""
    # The replayed assistant turn: index 1 of messages/contents (after the user
    # turn); on Responses every input item before the first function_call_output.
    turn = {"anthropic": "$.messages[1]", "gemini": "$.contents[1]", "openai-chat": "$.messages[1]"}.get(dialect)
    if turn and path.startswith(turn + "."):
        return "replayed-assistant-turn: response-only field dropped by the canonical replay (as every multi_turn_tool_result case)"
    if dialect == "openai-responses" and path.startswith("$.input["):
        index = int(path[len("$.input["):path.index("]")])
        if 0 < index < first_result:
            return "replayed-assistant-turn: response-only field dropped by the canonical replay (as every multi_turn_tool_result case)"
    if cell in ("text", "error") and isinstance(sent, list) and isinstance(sdk, str) and len(sent) == 1 and sent[0].get("text") == sdk:
        return "text-only result: the probe sent a one-block array, the ratified cell is the string form"
    if path.endswith(".filename") and sent == "panel.pdf" and sdk == "file.pdf":
        return "document filename: the adapter's deterministic name (file.<subtype>)"
    return None


def latest_candidates():
    best: dict[tuple[str, str], Path] = {}
    for path in sorted(RECEIPTS.glob("*/*/*/fixture-candidate.json")):
        cand = json.loads(path.read_text())
        cell = cand["feature"].removeprefix("tool_result_")
        best[(cand["provider"], cell)] = path  # sorted: the latest run wins
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    written, skipped = [], []
    for (provider, cell), path in sorted(latest_candidates().items()):
        if provider in SKIP or cell not in NATIVE_CELLS:
            continue
        cand = json.loads(path.read_text())
        result = json.loads((path.parent / "result.json").read_text())
        if result["outcome"] not in ("content_received", "error_acknowledged"):
            continue
        dialect = probe.PROVIDERS[provider].dialect
        if cell == "error" and dialect not in ERROR_NATIVE_DIALECTS:
            continue
        if "canonical_request" not in cand:
            skipped.append((provider, cell, cand.get("canonical_or_build_error", "no canonical request")))
            continue
        adapter = adapter_for_provider(provider, "$" + next(iter(probe.PROVIDERS[provider].access.env_keys), "KEY"))
        request = serde.request_from_dict(cand["canonical_request"])
        sdk_body = json.loads(adapter.build_request(request, stream=False).body)
        allowances, blocked = [], []
        first_result = next((i for i, item in enumerate(sdk_body.get("input", [])) if item.get("type") == "function_call_output"), 0)
        for p, a, b in diff(cand["request"]["body"], sdk_body):
            why = classify(dialect, cell, p, a, b, first_result)
            (allowances if why else blocked).append((p, why or f"sent={str(a)[:60]!r} sdk={str(b)[:60]!r}"))
        if blocked:
            skipped.append((provider, cell, "; ".join(f"{p}: {w}" for p, w in blocked[:4])))
            continue
        feature = f"tool_result_{cell}"
        ts = json.loads((path.parent / "turn2.json").read_text())["timestamp"]
        body_name = f"{ts}.txt"
        case = {
            "id": f"{provider}.{feature}", "provider": provider, "feature": feature,
            "description": {
                "image": "MAP-10: an image-only tool result reaches the wire as a native block inside the result item (hidden-oracle visual check passed live)",
                "mixed": "MAP-10: text then image in one tool result, order kept",
                "pair": "MAP-10: two tool calls in one turn, two results (A image-only, B text+image), each under its own call id",
                "pdf": "MAP-10: a PDF document in a tool result as a native document block",
                "error": "MAP-10 rule 5: is_error reaches the wire's own flag",
                "text": "MAP-10 rule 7: a text-only tool result stays a string",
            }[cell],
            "base_url": adapter.base_url,
            "request": {**cand["request"], "body": sdk_body},
            "expect": {"status": 200},
            "expect_lm15": {"parts": {"text": {"min": 1}}, "usage": {"required": True}},
            "provenance": {
                "source": "live-capture", "date": ts[:10], "exchange": cand["provenance"]["exchange"],
                "evidence": f"{provider} {ts}, {result['model']}, HTTP 200; tool-result-content matrix cell '{cell}' (research/tool-result-content/20-results.md), "
                            f"hidden oracle received by the model; verbatim turn-2 body at bodies/{provider}.{feature}/{body_name}; turn-1 body and oracle in "
                            f"{path.parent.relative_to(CONTRACT)}/; the live wire was raw-patched, the pinned wire is the adapter's after MAP-10"
                            + ("; differences from the sent wire, all allowed: " + "; ".join(f"{p} — {w}" for p, w in allowances) if allowances else "; identical to the sent wire")
                            + f"; {CHANGE}",
            },
            "canonical_request": cand["canonical_request"],
            "canonical_request_provenance": {"source": "hand-authored", "date": ts[:10],
                                             "evidence": f"authored by research/providers/media_tool_results.py (cell {cell}); the assistant turn is the model's own, parsed from turn-1"},
            "pinned_body": body_name,
        }
        if not args.dry_run:
            (CONTRACT / "cases" / provider).mkdir(parents=True, exist_ok=True)
            (CONTRACT / "cases" / provider / f"{feature}.json").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
            body_dir = CONTRACT / "bodies" / f"{provider}.{feature}"
            body_dir.mkdir(parents=True, exist_ok=True)
            (body_dir / body_name).write_bytes((path.parent / "turn2-response.txt").read_bytes())
        written.append((provider, cell, len(allowances)))
    for provider, (cell, why) in REJECTS.items():
        runs = sorted(RECEIPTS.glob(f"*/{provider}/{cell}/result.json"))
        if not runs:
            skipped.append((provider, "raise", "no receipt"))
            continue
        rec = json.loads(runs[-1].read_text())
        model = rec["model"]
        exchanges = sorted(runs[-1].parent.glob("exchange-*.json"))
        exchange = str(exchanges[-1].relative_to(CONTRACT)) if exchanges else None
        canonical = {"model": model, "messages": [
            {"role": "user", "parts": [{"type": "text", "text": "Call fetch_panel with label A and describe the panel."}]},
            {"role": "assistant", "parts": [{"type": "tool_call", "id": "call_1", "name": "fetch_panel", "input": {"label": "A"}}]},
            {"role": "tool", "parts": [{"type": "tool_result", "id": "call_1", "content": [{"type": "image", "media_type": "image/png", "data": "iVBORw0KGgo="}]}]}],
            "tools": [{"type": "function", "name": "fetch_panel", "description": "Retrieve a visual panel by its label.",
                       "parameters": {"type": "object", "properties": {"label": {"type": "string", "enum": ["A", "B"]}}, "required": ["label"]}}]}
        case = {
            "id": f"{provider}.tool_result_image_raise", "provider": provider, "feature": "tool_result_image_raise",
            "description": f"MAP-10: an image in a tool result RAISES on this preset (tool_result_media=reject) — {why}. There is no wire request.",
            "expect_lm15": {"raises": {"op": "build_request", "type": "UnsupportedFeatureError", "code": "unsupported_feature"}},
            "provenance": {"source": "live-capture", "date": "2026-09-07", "exchange": exchange,
                           "evidence": f"tool-result-content matrix cell '{cell}' on {model}: {why}; receipt {runs[-1].parent.relative_to(CONTRACT)}/ "
                                       f"(turn1.json, turn2.json, turn2-response.txt, visual-oracle.json); ledger research/tool-result-content/20-results.md; {CHANGE}"},
            "canonical_request": canonical,
            "canonical_request_provenance": {"source": "hand-authored", "date": "2026-09-07",
                                             "evidence": "authored with the case from the matrix cell it pins; the reference raises at build_request (lm15-python tests/test_tool_result_media.py)"},
        }
        if not args.dry_run:
            (CONTRACT / "cases" / provider).mkdir(parents=True, exist_ok=True)
            (CONTRACT / "cases" / provider / "tool_result_image_raise.json").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        written.append((provider, "raise", 0))
    print("promoted:", len(written))
    for w in written:
        print("  ", w)
    print("not promoted:", len(skipped))
    for s in skipped:
        print("  ", s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
