#!/usr/bin/env python3
"""Together AI live capture — model declarations; cases and probes in ../_inference_hosts.py.

Machinery: `research/providers/_capture.py`.  Receipts: `receipts/<date>-together/`.
Dossier: `research/providers/together/README.md`.

    TOGETHER_API_KEY=… python3 research/providers/together/capture.py [--dry-run] [--only a,b] [--force] [--no-probes]
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
    replayer="deepseek-ai/DeepSeek-V4.1-Flash",
    always_on="zai-org/GLM-5.3-Flash",
)

if __name__ == "__main__":
    run("together", env_var="TOGETHER_API_KEY", host="api.together.ai", models=MODELS)
