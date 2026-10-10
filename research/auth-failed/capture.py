#!/usr/bin/env python3
"""Capture every reachable provider's answer to a key it does not accept.

usage: python capture.py OUT_DIR   (run with ../lm15-python importable and
the lab's keys in the environment; the real keys are only used to know
which providers are reachable — every request carries KEY below instead)

Each request is the one lm15-python builds for a one-word prompt, sent
unchanged through its own transport; the reply is recorded as received
(status and JSON body), with the class lm15-python raised. The key sent is
a fixed, obviously fake value, so nothing secret can be captured. Written
for changes/2026-10-10-bad-key-and-misplaced-key.md (MAP-18).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import lm15
from lm15.providers import base

KEY = "lm15-invalid-key-0000000000"

ROUTES = {
    "openai": "gpt-4.1-mini",
    "openai-chat": "gpt-4.1-mini",
    "anthropic": "claude-haiku-4-5",
    "gemini": "gemini-2.5-flash",
    "xai": "grok-3-mini",
    "groq": "openai/gpt-oss-20b",
    "deepseek": "deepseek-chat",
    "deepseek-anthropic": "deepseek-chat",
    "moonshotai": "kimi-k2.6",
    "moonshotai-anthropic": "kimi-k2.6",
    "openrouter": "openai/gpt-4o-mini",
    "zai": "glm-4.5-air",
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "fireworks": "accounts/fireworks/models/gpt-oss-120b",
    "deepinfra": "openai/gpt-oss-20b",
    "parasail": "parasail-gpt-oss-120b",
    "meta": "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "meta-chat": "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "typesafe": "jev-latest",
}


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    seen: dict = {}
    original = base.BaseProviderLM._http_error

    def recording(self, response):
        seen["status"] = response.status
        try:
            seen["body"] = json.loads(response.body)
        except ValueError:
            seen["body"] = response.body.decode("utf-8", "replace")
        return original(self, response)

    base.BaseProviderLM._http_error = recording
    for provider, model in ROUTES.items():
        seen.clear()
        router = lm15.LMRouter(lm15.RouterConfig(api_keys={provider: KEY}))
        request = lm15.Request(model=f"{provider}:{model}", messages=(lm15.Message.user("Say ok."),),
                               config=lm15.Config(max_tokens=16))
        try:
            router.complete(request)
            raised = None
        except lm15.LM15Error as exc:
            raised = type(exc).__name__
        if "status" not in seen:
            print(f"{provider:22} no HTTP error recorded ({raised})")
            continue
        record = {
            "sent": {"model": model, "prompt": "Say ok.", "api_key": KEY,
                     "via": f"lm15-python {lm15.__version__} LMRouter().complete(), request built and sent unchanged"},
            "status": seen["status"],
            "body": seen["body"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lm15_python_before": raised,
            "redacted": "nothing (the key sent is fake and fixed)",
        }
        (out / f"{provider}.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
        print(f"{provider:22} {seen['status']} {raised}")


if __name__ == "__main__":
    main()
