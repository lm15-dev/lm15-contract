#!/usr/bin/env python3
"""DeepInfra: which model families honour a forced tool choice?

The preset's first rule (2026-09-26) refused a forced tool choice on every
DeepInfra model but DeepSeek V4, from four models.  This survey widens the
sample across the families DeepInfra serves, so the rule's breadth rests on
receipts.  Per model, three raw probes (the adapter would refuse them):

- required  — "Say ok." with one tool: honoured = a tool call.
- named     — the same with {"type":"function","function":{"name":...}}.
- none      — "What is the weather in Paris? Use the tool.": honoured = no call.
- control-auto, required-2 — a forced call counts as honoured only if the
  model makes no call unprompted and the second forced try calls too.

Receipts: receipts/<date>-deepinfra/probe-survey-<model>-<mode>.json.

    DEEPINFRA_API_KEY=… python3 research/providers/deepinfra/tool_choice_survey.py [--models a,b]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import WEATHER, Capture  # noqa: E402

MODELS = (
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "Qwen/Qwen3.8-Flash", "Qwen/Qwen3.6-27B", "Qwen/Qwen3-235B-A22B-Instruct-2507", "Qwen/Qwen3-Next-80B-A3B-Instruct",
    "Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo",
    "zai-org/GLM-5.3-Flash", "zai-org/GLM-4.7", "moonshotai/Kimi-K2.6", "MiniMaxAI/MiniMax-M2.7-Turbo",
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506", "google/gemma-4-26B-A4B-it", "microsoft/phi-4",
    "nvidia/NVIDIA-Nemotron-3.5-Lightning", "ibm-granite/granite-4.2-8b", "ByteDance/Seed-2.0-mini",
    "XiaomiMiMo/MiMo-V2.6-Flash", "tencent/Hy3", "openai/gpt-oss-20b",
    "deepseek-ai/DeepSeek-V3.2", "deepseek-ai/DeepSeek-V4-Flash",
    "google/gemini-3.1-flash-lite", "anthropic/claude-haiku-4-5",
)
TOOLS = [{"type": "function", "function": {"name": WEATHER.name, "description": WEATHER.description,
                                           "parameters": WEATHER.parameters}}]
MODES = {
    "required": ("required", "Say ok."),
    "named": ({"type": "function", "function": {"name": WEATHER.name}}, "Say ok."),
    "none": ("none", "What is the weather in Paris? Use the tool."),
    # Controls for "honoured": with no forcing, does the model call the tool
    # on "Say ok." anyway?  A second forced try guards against a lucky call.
    "control-auto": ("auto", "Say ok."),
    "required-2": ("required", "Say ok."),
}


def verdict(mode: str, rec: dict) -> str:
    if rec.get("status") != 200 or not isinstance(rec.get("body"), dict) or "choices" not in rec["body"]:
        return f"HTTP {rec.get('status')}"
    message = rec["body"]["choices"][0]["message"]
    called = bool(message.get("tool_calls"))
    text = message.get("content") or ""
    if mode == "control-auto":
        return "calls unprompted" if called else "no call"
    if mode == "none":
        if called:
            return "IGNORED (called)"
        return "IGNORED (call written as text)" if re.search(r"get_weather|<function|\"name\"", text) else "honoured"
    return "honoured" if called else "IGNORED (text)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--models")
    args = ap.parse_args()
    models = args.models.split(",") if args.models else MODELS
    cap = Capture("deepinfra", env_var="DEEPINFRA_API_KEY", default_model=models[0], host="api.deepinfra.com",
                  change_slug="inference-hosts-live")
    cap.key()
    table = []
    for model in models:
        slug = re.sub(r"[^A-Za-z0-9.]+", "-", model).strip("-")
        row = {"model": model}
        for mode, (choice, question) in MODES.items():
            name = f"survey-{slug}-{mode}"
            cap.probe(name, raw_body={"model": model, "max_tokens": 600, "tool_choice": choice, "tools": TOOLS,
                                      "messages": [{"role": "user", "content": question}]})
            rec = json.loads((cap.receipts / f"probe-{name}.json").read_text(encoding="utf-8"))
            row[mode] = verdict(mode, rec)
        table.append(row)
        print(json.dumps(row), flush=True)
    cap.write_receipt("survey-tool-choice.json", table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
