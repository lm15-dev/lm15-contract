#!/usr/bin/env python3
"""Tinker: which reasoning settings does each model family take, on each door?

Tinker forwards one request shape to many model families and answers per
family (live 2026-11-09: Qwen3.5-4B takes `reasoning_effort` true|false only,
gpt-oss low|medium|high, Inkling the documented words). A checkpoint's
family is its base model's, which its `tinker://` name does not show. This
survey sends every setting to every sampleable model, and to a checkpoint,
on both doors, and records accepted / refused / reasoned.

Raw bodies (the adapter is not asked to build them). Per model and setting
one request: "What is 17*23? Reply with just the number." with a 64-token cap
— enough to see reasoning start, too short to finish a long trace.

Receipts: receipts/<date>-tinker-survey/probe-reasoning-<door>-<model>-<setting>.json
and survey-reasoning.json (the table). Wire shapes only (terms § 1(e)):
no latency is recorded.

    TINKER_API_KEY=… python3 research/providers/tinker/reasoning_survey.py [--models a,b] [--doors oai,anthropic]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tinker import CHECKPOINTS, GONE, capture  # noqa: E402

MODELS = (
    "Qwen/Qwen3-8B", "Qwen/Qwen3.5-4B", "Qwen/Qwen3.5-9B", "Qwen/Qwen3.5-9B-Base", "Qwen/Qwen3.5-35B-A3B-Base",
    "Qwen/Qwen3.5-397B-A17B", "Qwen/Qwen3.6-35B-A3B", "Qwen/Qwen3.8-27B",
    "deepseek-ai/DeepSeek-V4.1-Flash:peft:262144",
    "moonshotai/Kimi-K2.6", "moonshotai/Kimi-K3.1-Pro:peft:262144",
    "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16", "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16",
    "nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16", "nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16",
    "openai/gpt-oss-20b", "openai/gpt-oss-120b",
    "thinkingmachines/Inkling", "thinkingmachines/Inkling-Small", "thinkingmachines/Inkling-2-Small",
    "thinkingmachines/Inkling-Small:peft:262144:sampling-nvfp4",
    "zai-org/GLM-5.3-Flash:peft:262144",
    *CHECKPOINTS.values(),
)
QUESTION = [{"role": "user", "content": "What is 17*23? Reply with just the number."}]
CAP = 64
OAI = {
    "absent": {}, "false": {"reasoning_effort": False}, "true": {"reasoning_effort": True},
    **{w: {"reasoning_effort": w} for w in ("none", "minimal", "low", "medium", "high", "xhigh", "max", "bogus")},
    "float-0.5": {"reasoning_effort": 0.5},
}
ANTHROPIC = {
    "absent": {}, "thinking-disabled": {"thinking": {"type": "disabled"}},
    "thinking-enabled": {"thinking": {"type": "enabled", "budget_tokens": 1024}},
    "thinking-adaptive": {"thinking": {"type": "adaptive"}},
    **{f"effort-{w}": {"output_config": {"effort": w}} for w in ("low", "medium", "high", "xhigh", "max", "bogus")},
}


def slug(model: str) -> str:
    names = {v: f"checkpoint-{k.split('/')[-1]}" for k, v in CHECKPOINTS.items()} | {GONE: "checkpoint"}
    return names.get(model) or re.sub(r"[^A-Za-z0-9.]+", "-", model).strip("-")


def verdict(door: str, rec: dict) -> str:
    body = rec.get("body")
    if rec.get("status") != 200:
        detail = body.get("detail") if isinstance(body, dict) else None
        if detail is None and isinstance(body, dict) and isinstance(body.get("error"), dict):
            detail = body["error"].get("message")
        return f"{rec.get('status')}: {str(detail if detail is not None else body)[:160]}"
    if door == "oai":
        msg = body["choices"][0]["message"]
        reasoning, text = msg.get("reasoning_content") or "", msg.get("content") or ""
    else:
        reasoning = "".join(b.get("thinking", "") for b in body.get("content", []) if b.get("type") == "thinking")
        text = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
    inline = "<think>" in text or text.lstrip().lower().startswith(("thinking process", "okay, ", "we need", "the user"))
    return f"200: reasoning={len(reasoning)}c text={text.strip()[:24]!r}" + (" INLINE-REASONING?" if inline else "")


def run_model(model: str, doors: list[str]) -> dict:
    row = {"model": model}
    for door in doors:
        cap = capture("tinker" if door == "oai" else "tinker-anthropic")
        cap.receipts = cap.receipts.parent / f"{cap.date}-tinker-survey"
        for name, extra in (OAI if door == "oai" else ANTHROPIC).items():
            probe = f"reasoning-{door}-{slug(model)}-{name}"
            body = {"model": model, "messages": QUESTION, "max_tokens": CAP, **extra}
            got = cap.probe(probe, raw_body=body)
            if "error" in got:
                row[f"{door}:{name}"] = got["error"][:160]
                continue
            rec = json.loads((cap.receipts / f"probe-{probe}.json").read_text(encoding="utf-8"))
            row[f"{door}:{name}"] = verdict(door, rec)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--models")
    ap.add_argument("--doors", default="oai,anthropic")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    models = args.models.split(",") if args.models else MODELS
    doors = args.doors.split(",")
    with ThreadPoolExecutor(args.workers) as pool:
        table = list(pool.map(lambda m: run_model(m, doors), models))
    cap = capture()
    cap.receipts = cap.receipts.parent / f"{cap.date}-tinker-survey"
    name = "survey-reasoning.json" if not args.models else f"survey-reasoning-{'-'.join(slug(m) for m in models)[:80]}.json"
    cap.write_receipt(name, table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
