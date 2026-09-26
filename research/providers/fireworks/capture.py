#!/usr/bin/env python3
"""Fireworks AI live capture — model declarations; cases and probes in ../_inference_hosts.py.

Machinery: `research/providers/_capture.py`.  Receipts: `receipts/<date>-fireworks/`.
Dossier: `research/providers/fireworks/README.md`.

    FIREWORKS_API_KEY=… python3 research/providers/fireworks/capture.py [--dry-run] [--only a,b] [--force] [--no-probes]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _inference_hosts import Models, run  # noqa: E402

MODELS = Models(
    plain="accounts/fireworks/models/deepseek-v4p1-flash",
    reasoner="accounts/fireworks/models/gpt-oss-120b",
    off="accounts/fireworks/models/deepseek-v4p1-flash",
    replayer="accounts/fireworks/models/gpt-oss-120b",
    always_on="accounts/fireworks/models/glm-5p3-flash",
)

if __name__ == "__main__":
    run("fireworks", env_var="FIREWORKS_API_KEY", host="api.fireworks.ai", models=MODELS)
