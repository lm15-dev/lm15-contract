#!/usr/bin/env python3
"""DeepInfra live capture — model declarations; cases and probes in ../_inference_hosts.py.

Machinery: `research/providers/_capture.py`.  Receipts: `receipts/<date>-deepinfra/`.
Dossier: `research/providers/deepinfra/README.md`.

    DEEPINFRA_API_KEY=… python3 research/providers/deepinfra/capture.py [--dry-run] [--only a,b] [--force] [--no-probes]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _inference_hosts import Models, run  # noqa: E402

MODELS = Models(
    plain="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    reasoner="openai/gpt-oss-120b",
    off="deepseek-ai/DeepSeek-V4.1-Flash",
    replayer="openai/gpt-oss-120b",
    always_on=None,
    forcing="deepseek-ai/DeepSeek-V4.1-Flash",
)

if __name__ == "__main__":
    run("deepinfra", env_var="DEEPINFRA_API_KEY", host="api.deepinfra.com", models=MODELS)
