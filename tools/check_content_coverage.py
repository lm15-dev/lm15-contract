#!/usr/bin/env python3
"""MAP-10 content-coverage gate: every (binding × tool-result media kind) cell
is pinned — by a native case or by a refusal case — or is an OPEN cell the
support matrix admits. A blank cell is drift, the blind spot the 2026-09-07
Rust review fell through (297 request cases, zero with media in a tool result).

Pinned means, per binding:
  image    : cases/<binding>/tool_result_image.json  (native) or
             cases/<binding>/tool_result_image_raise.json (reject)
  document : cases/<binding>/tool_result_pdf.json or a raise case for documents,
             OR the binding's image cell is a raise (reject covers every kind),
             OR the preset is `images` (documents raise; the reference's
             tests pin it: the wire never got a document receipt).

Open cells: bindings listed in OPEN below with the reason (no receipt yet:
credentials, deployment, no server). Adding a binding to the registry without
a cell here fails. Exit non-zero on drift.

Usage: check_content_coverage.py [--root DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# bindings whose preset is `images`: documents raise, pinned by the reference's
# tests and the ledger's document 400s (no server accepted a document there)
IMAGES_ONLY = ("xai", "moonshotai", "moonshotai-responses", "moonshotai-anthropic", "zai")

# binding → why its cell is open (blank by declaration, not by omission)
OPEN: dict[str, str] = {
    "openrouter": "account 401 during the 2026-09-07 pass; preset reject until a receipt",
    "ollama": "0.8b local model timed out; source shows image rows lose ToolCallID; preset reject until a receipt",
    "vllm": "no server reachable during the pass; preset reject until a receipt",
    "sglang": "no server reachable during the pass; preset reject until a receipt",
    "azure": "hosted door (needs settings); OpenAI Responses wire, image cell 200-miss on gpt-4.1-mini only — ledger row, no case yet",
    "azure-chat": "hosted door; rate-limited during the pass; preset reject (openai) applies",
    "azure-anthropic": "deployment not found during the pass",
    "aws-anthropic": "host settings not configured during the pass",
    "bedrock-anthropic": "403 during the pass",
    "bedrock-chat": "400 on the array form (ledger); hosted door, no offline case build; preset reject applies",
    "bedrock-mantle-chat": "model not on route during the pass; preset reject applies",
    "vertex": "OAuth refresh failed during the pass",
    "vertex-express": "no GOOGLE_API_KEY during the pass",
    "vertex-anthropic": "OAuth refresh failed during the pass",
    "openai-codex": "first turn is SSE; image received live (5/6 on the mini model); same wire as openai — no offline case build yet",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    root = args.root
    matrix = json.loads((root / "spec" / "support-matrix.json").read_text())
    bindings = sorted(matrix.get("providers", matrix).keys()) if isinstance(matrix, dict) else []
    problems: list[str] = []
    pinned = 0
    for binding in bindings:
        folder = root / "cases" / binding
        image = (folder / "tool_result_image.json").exists()
        image_raise = (folder / "tool_result_image_raise.json").exists()
        pdf = (folder / "tool_result_pdf.json").exists()
        if image_raise:
            pinned += 1
            continue
        if not image:
            if binding in OPEN:
                continue
            problems.append(f"{binding}: no tool_result_image case and no raise case (MAP-10 cell blank)")
            continue
        pinned += 1
        if not pdf and binding not in IMAGES_ONLY:
            problems.append(f"{binding}: image pinned but no tool_result_pdf case; add the receipt or list it under IMAGES_ONLY")
    for binding in OPEN:
        if binding not in bindings:
            problems.append(f"OPEN lists {binding!r}, not a registry binding")
        elif (root / "cases" / binding / "tool_result_image.json").exists():
            problems.append(f"{binding}: has a tool_result_image case but is still declared OPEN — remove it from OPEN")
    for p in problems:
        print("FAIL", p)
    print(f"check_content_coverage: {'OK' if not problems else str(len(problems)) + ' violation(s)'} — "
          f"{pinned} binding(s) pinned, {len(OPEN)} open, {len(bindings)} in the matrix")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
