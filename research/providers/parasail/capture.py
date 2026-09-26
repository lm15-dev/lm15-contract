#!/usr/bin/env python3
"""Parasail live capture — model declarations; cases and probes in ../_inference_hosts.py.

Machinery: `research/providers/_capture.py`.  Receipts: `receipts/<date>-parasail/`.
Dossier: `research/providers/parasail/README.md`.

    PARASAIL_API_KEY=… python3 research/providers/parasail/capture.py [--dry-run] [--only a,b] [--force] [--no-probes]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _inference_hosts import Models, run  # noqa: E402

MODELS = Models(
    plain="meta-llama/Llama-3.3-70B-Instruct",
    reasoner="openai/gpt-oss-20b",
    off=None,
    replayer="openai/gpt-oss-20b",
    always_on=None,
)

if __name__ == "__main__":
    run("parasail", env_var="PARASAIL_API_KEY", host="api.parasail.io", models=MODELS)
