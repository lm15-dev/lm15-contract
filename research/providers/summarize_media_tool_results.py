#!/usr/bin/env python3
"""Fold every run under receipts/<date>-tool-result-media/ into the design-pass
ledger (research/tool-result-content/20-results.json + 20-results.md).

Offline. Append-only inputs; the ledger is regenerated in full (it is derived,
receipts are the evidence). Fixture candidates (for cells whose content was
received) are written next to their receipts, never into cases/.
"""
from __future__ import annotations

import base64
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import media_tool_results as probe
from lm15 import ImagePart, TextPart, ToolResultPart, serde
from lm15.providers.base import HttpResponse
from lm15.types import ToolCallPart
from lm15.vet import adapter_for_provider

PASS = probe.CONTRACT / "research" / "tool-result-content"
SHORT = {"content_received": "OK", "accepted_but_content_not_received": "200-miss", "accepted_but_no_json_answer": "200-nojson",
         "tool_result_rejected": "400", "first_call_rejected": "t1-fail", "blocked_or_inconclusive": "blocked",
         "error_acknowledged": "err-OK", "error_ignored_colors_fabricated": "err-FAB", "visual_match": "OK",
         "accepted_but_visual_check_failed": "200-miss", "image_result_rejected": "400"}


def fixture_candidate(folder: Path, result: dict) -> dict:
    """The seed of a contract case: the sent wire, the artifact, and the canonical
    request the SDK would have to build to produce it."""
    cell = result["cell"]
    first = probe.Request(model=result["model"], messages=(probe.Message.user(probe.prompt(cell)),),
                          tools=(probe.TOOL,), config=probe.Config(max_tokens=1600))
    second_receipt = json.loads((folder / "turn2.json").read_text())
    candidate = {
        "id": f"{result['provider']}.tool_result_{cell}", "provider": result["provider"], "feature": f"tool_result_{cell}",
        "status": "DRAFT; not an active corpus fixture",
        "request": second_receipt["sent"], "response_artifact": "turn2-response.txt", "expect": {"status": 200},
        "oracle": result["expected"],
        "provenance": {"source": "live-capture", "date": second_receipt["timestamp"][:10],
                       "exchange": None, "evidence": str(folder.relative_to(probe.CONTRACT)) + "/turn2.json; raw patched wire; visual-oracle.json"},
    }
    exchanges = sorted(folder.glob("exchange-*.json"))
    if len(exchanges) >= 2:
        candidate["provenance"]["exchange"] = str(exchanges[-1].relative_to(probe.CONTRACT))
    try:
        adapter = adapter_for_provider(result["provider"], "fixture-parse-only")
        response = adapter.parse_response(first, HttpResponse(200, "OK", [], (folder / "turn1-response.txt").read_bytes()))
        oracle = json.loads((folder / "visual-oracle.json").read_text())
        results = []
        for call in response.message.parts:
            if not isinstance(call, ToolCallPart):
                continue
            label = call.input["label"]
            kind = "pdf" if cell == "pdf" else "png"
            data = base64.b64encode((folder / f"{label}.{kind}").read_bytes()).decode()
            media = {l: base64.b64encode((folder / f"{l}.{kind}").read_bytes()).decode() for l in ("A", "B")}
            parts, is_error = probe.outputs_for(cell, oracle["expected"], media)[label]
            canon = []
            for p in parts:
                if p["kind"] == "text":
                    canon.append(TextPart(text=p["text"]))
                elif p["kind"] == "image":
                    canon.append(ImagePart(media_type="image/png", data=data, detail=oracle.get("detail")))
                else:
                    from lm15 import DocumentPart
                    canon.append(DocumentPart(media_type="application/pdf", data=data))
            results.append(ToolResultPart(id=call.id, name=call.name, content=tuple(canon), is_error=is_error))
        second = probe.Request(model=first.model, messages=(*first.messages, response.message, probe.Message.tool(tuple(results))),
                               tools=first.tools, config=first.config)
        candidate["canonical_request"] = serde.request_to_dict(second)
        actual = adapter.build_request(second, stream=False)
        candidate["python_body_matches_sent"] = json.loads(actual.body) == second_receipt["sent"]["body"]
    except Exception as exc:
        candidate["python_body_matches_sent"] = False
        candidate["canonical_or_build_error"] = f"{type(exc).__name__}: {exc}"
    return candidate


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    rows = []
    for path in sorted(root.glob("*/*/result.json")) + sorted(root.glob("*/*/*/result.json")):
        row = json.loads(path.read_text())
        row["provider"] = path.parent.name if path.parent.parent.parent == root else path.parent.parent.name
        row.setdefault("cell", "pair")          # the first probe (v0) was the two-call cell only
        row["run"] = path.relative_to(root).parts[0]
        row["receipt"] = str(path.parent.relative_to(probe.CONTRACT))
        oracle = path.parent / "visual-oracle.json"
        if oracle.exists():
            o = json.loads(oracle.read_text())
            row["cell_px"], row["detail"] = o.get("cell_px", 64), o.get("detail")
        row["outcome_short"] = SHORT.get(row["outcome"], row["outcome"])
        if row["outcome"] in ("content_received", "visual_match", "error_acknowledged") and row["cell"] != "control" and (path.parent / "turn2.json").exists():
            cand = path.parent / "fixture-candidate.json"
            if not cand.exists():
                cand.write_text(json.dumps(fixture_candidate(path.parent, row), indent=2, ensure_ascii=False) + "\n")
            row["python_body_matches_sent"] = json.loads(cand.read_text()).get("python_body_matches_sent")
        rows.append(row)
    ledger = {"experiments": len(rows), "inference_attempts": sum(r.get("inference_calls", 0) for r in rows),
              "outcomes": dict(Counter(r["outcome"] for r in rows)), "results": rows,
              "cost_note": "Usage fields are recorded per cell (result.json usage); provider price lists were not folded in. Total spend is bounded by inference_attempts × the models' list prices; no cell exceeded 2 calls.",
              "note": "Derived from append-only receipts. outcome judges whether the MODEL RECEIVED the content (hidden oracle), never whether the request got HTTP 200."}
    (PASS / "20-results.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    # The matrix: latest run per (provider, model, cell_px/detail) wins a cell; older runs stay in the JSON.
    cells = list(probe.CELLS)
    grid: dict[tuple, dict] = defaultdict(dict)
    for r in sorted(rows, key=lambda r: r["run"]):
        grid[(r["provider"], r["model"], f"{r.get('cell_px', 64)}px/{r.get('detail') or 'auto'}")][r["cell"]] = r
    lines = ["# Tool-result content — live matrix", "", f"{len(rows)} cells, {ledger['inference_attempts']} inference calls, "
             "no automatic retries. Cell = did the model receive the tool's content (hidden oracle). "
             "`OK` received · `200-miss` accepted, content not received · `200-nojson` accepted, no parseable answer · "
             "`400` tool-result wire rejected · `t1-fail` first call failed · `blocked` credentials/model/loop · "
             "`err-OK` is_error acknowledged · `err-FAB` error ignored, colors fabricated.", "",
             "| Binding | Model | Oracle | " + " | ".join(cells) + " |", "|---|---|---|" + "---|" * len(cells)]
    for (prov, model, oracle), by in sorted(grid.items()):
        lines.append(f"| {prov} | {model} | {oracle} | " + " | ".join(by[c]["outcome_short"] if c in by else "—" for c in cells) + " |")
    lines += ["", "Older runs of the same cell are kept in `20-results.json` (field `run`)."]
    (PASS / "20-results.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: v for k, v in ledger.items() if k != "results"}, indent=2))


if __name__ == "__main__":
    main()
