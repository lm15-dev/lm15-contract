#!/usr/bin/env python3
"""Consumer-side cases for the inference hosts' per-model rules.

Each rule in the four presets that changes a request before the wire — a
refusal, a clamp, a substituted reasoning-off — is pinned here as a case with
no live exchange of its own: the wire side is the reference build, and the
evidence is the probe receipt that showed the server's behaviour
(receipts/2026-09-26-<host>/probe-*.json).  Same shapes as the Bedrock and
Z.AI pins (cases/bedrock-chat/response_format_json_schema_gpt_oss.json,
cases/zai/tool_choice_required.json).

    python3 research/providers/_inference_hosts_pins.py [--force]

Sends nothing; needs no key.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, WEATHER  # noqa: E402  (also puts lm15-python on sys.path)
from lm15 import Config, Message, Reasoning, Request, ToolChoice, serde  # noqa: E402
from lm15.errors import LM15Error  # noqa: E402
from lm15.vet import adapter_for_provider, normalize_transport_request  # noqa: E402

DATE = "2026-09-26"
CHANGE = "changes/2026-09-26-inference-hosts-live.md"
MATH = (Message.user("What is 17*23? Reply with just the number."),)
SAY = (Message.user("Say ok."),)

PLACEHOLDER = {"deepinfra": "$DEEPINFRA_API_KEY", "together": "$TOGETHER_API_KEY",
               "fireworks": "$FIREWORKS_API_KEY", "parasail": "$PARASAIL_API_KEY"}


def receipts(host: str, *names: str) -> str:
    return ", ".join(f"receipts/{DATE}-{host}/probe-{n}.json" for n in names)


PINS = [
    # ── DeepInfra ────────────────────────────────────────────────────
    dict(host="deepinfra", feature="tool_choice_required", exchange_probe="tool-choice-required-plain",
         request=Request(model="meta-llama/Llama-3.3-70B-Instruct-Turbo", messages=SAY, tools=(WEATHER,),
                         config=Config(max_tokens=300, tool_choice=ToolChoice(mode="required"))),
         description="MAP-8: a forced tool choice on DeepInfra raises (default for every model but DeepSeek V4). Receipt: "
                     "required and a named function answered plain text with no call on Llama 3.3 and gpt-oss; none on Llama "
                     "wrote the call into the text. No wire request: UnsupportedFeatureError at build time.",
         evidence="api.deepinfra.com 2026-09-26: " + receipts("deepinfra", "tool-choice-required-plain", "tool-choice-required-reasoner",
                                                              "tool-choice-named-plain", "tool-choice-none-plain")
                  + " (HTTP 200, finish stop, no tool_calls)"),
    dict(host="deepinfra", feature="tool_choice_required_deepseek", exchange_probe="tool-choice-required-forcing",
         request=Request(model="deepseek-ai/DeepSeek-V4.1-Flash", messages=SAY, tools=(WEATHER,),
                         config=Config(max_tokens=300, tool_choice=ToolChoice(mode="required"))),
         description="The DeepSeek V4 family is let through (compat model_overrides): it honours required and a named function "
                     "on DeepInfra. The wire carries tool_choice verbatim.",
         evidence="api.deepinfra.com 2026-09-26: " + receipts("deepinfra", "tool-choice-required-forcing", "tool-choice-named-forcing")
                  + " (HTTP 200, finish tool_calls)"),
    dict(host="deepinfra", feature="reasoning_off_gpt_oss", exchange_probe="off-reasoner",
         request=Request(model="openai/gpt-oss-120b", messages=MATH, config=Config(max_tokens=1500, reasoning=Reasoning(effort="off"))),
         description="MAP-13 §4.2: gpt-oss cannot stop reasoning and DeepInfra accepts reasoning_effort none and runs it as low; "
                     "the lowest level is sent and the substitution recorded (compat reasoning_off=lowest).",
         evidence="api.deepinfra.com 2026-09-26: " + receipts("deepinfra", "off-reasoner", "shape-reasoning-disabled")
                  + " (HTTP 200, reasoning_content present on an explicit off)"),
    # ── Together ─────────────────────────────────────────────────────
    dict(host="together", feature="tool_choice_required_gpt_oss", exchange_probe="tool-choice-required-reasoner",
         request=Request(model="openai/gpt-oss-120b", messages=SAY, tools=(WEATHER,),
                         config=Config(max_tokens=600, tool_choice=ToolChoice(mode="required"))),
         description="gpt-oss on Together answers a forced tool choice with HTTP 500 every time; a 500 is retryable, so the "
                     "refusal happens before the wire (compat model_overrides openai/gpt-oss forced_tool_choice=reject). "
                     "Llama and DeepSeek on Together are unaffected.",
         evidence="api.together.ai 2026-09-26: " + receipts("together", "tool-choice-required-reasoner")
                  + " (HTTP 500 'Internal server error'); " + receipts("together", "tool-choice-required-plain", "tool-choice-named-plain")
                  + " (Llama honours it)"),
    dict(host="together", feature="reasoning_off_gpt_oss", exchange_probe="off-reasoner",
         request=Request(model="openai/gpt-oss-120b", messages=MATH, config=Config(max_tokens=1500, reasoning=Reasoning(effort="off"))),
         description="MAP-13 §4.2: gpt-oss on Together accepts reasoning_effort none, hides the trace and still bills reasoning "
                     "tokens; the lowest declared level (low) is sent and the substitution recorded.",
         evidence="api.together.ai 2026-09-26: " + receipts("together", "off-reasoner", "shape-reasoning-disabled")
                  + " (HTTP 200, no reasoning field, completion_tokens_details.reasoning_tokens > 0)"),
    dict(host="together", feature="reasoning_off_glm", exchange_probe="off-always-on",
         request=Request(model="zai-org/GLM-5.3-Flash", messages=MATH, config=Config(max_tokens=1500, reasoning=Reasoning(effort="off"))),
         description="MAP-13 §4.2: GLM-5.3 always reasons (Z.AI: 400 on off) and Together accepts none and reasons anyway; "
                     "the lowest level is sent and the substitution recorded.",
         evidence="api.together.ai 2026-09-26: " + receipts("together", "off-always-on")
                  + " (HTTP 200, reasoning_content present on an explicit off)"),
    dict(host="together", feature="reasoning_effort_max_gpt_oss", exchange_probe="effort-word-max",
         request=Request(model="openai/gpt-oss-120b", messages=MATH, config=Config(max_tokens=1500, reasoning=Reasoning(effort="max"))),
         description="MAP-13: gpt-oss on Together runs xhigh, max and even an unknown word at its default (medium); the declared "
                     "levels low|medium|high clamp max to high and record it.",
         evidence="api.together.ai 2026-09-26: " + receipts("together", "effort-word-xhigh", "effort-word-max", "effort-word-bogus",
                                                            "effort-high")
                  + " (HTTP 200 for every word; reasoning tokens at xhigh/max/bogus track medium, not high)"),
]


def exchange_of(host: str, probe: str) -> str:
    """The exchange receipt the capture tool wrote for a probe (D11): same
    timestamp, same redacted request."""
    rec = json.loads((CONTRACT / "receipts" / f"{DATE}-{host}" / f"probe-{probe}.json").read_text(encoding="utf-8"))
    hits = []
    for path in sorted((CONTRACT / "receipts" / f"{DATE}-{host}").glob("exchange-*.json")):
        ex = json.loads(path.read_text(encoding="utf-8"))
        if ex["timestamp"] == rec["timestamp"] and ex["sent"] == rec["sent"]:
            hits.append(path)
    if len(hits) != 1:
        raise SystemExit(f"{host} probe-{probe}: expected one exchange receipt, found {len(hits)}")
    return str(hits[0].relative_to(CONTRACT))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    for pin in PINS:
        host, feature, request = pin["host"], pin["feature"], pin["request"]
        path = CONTRACT / "cases" / host / f"{feature}.json"
        if path.exists() and not args.force:
            print(f"skip {path.relative_to(CONTRACT)} (exists)")
            continue
        adapter = adapter_for_provider(host, PLACEHOLDER[host])
        case: dict = {"id": f"{host}.{feature}", "provider": host, "feature": feature}
        try:
            treq, adaptations = adapter._build(request, False)
        except LM15Error as exc:
            case["description"] = pin["description"]
            case["expect_lm15"] = {"raises": {"op": "build_request", "type": type(exc).__name__, "code": exc.code,
                                              **({"feature": exc.feature} if getattr(exc, "feature", None) else {})}}
            treq = None
        else:
            norm = normalize_transport_request(treq)
            case["request"] = {k: norm[k] for k in ("method", "url", "params", "headers", "body")}
            case["description"] = pin["description"]
            records = [{k: v for k, v in (("field", a.field), ("action", a.action), ("asked", a.asked), ("applied", a.applied))
                        if v is not None} for a in adaptations]
            if records:
                case["expect_lm15"] = {"adaptations": records}
                # MAP-13: reading the wire back gives the request after the adaptation.
                applied = request
                for a in adaptations:
                    if a.field == "config.reasoning.effort":
                        from dataclasses import replace
                        applied = replace(applied, config=replace(applied.config, reasoning=replace(applied.config.reasoning, effort=a.applied)))
                case["ingest"] = {"lossy": ["adapted"], "canonical_request": serde.request_to_dict(applied),
                                  "note": "MAP-13: reading the wire back gives the request AFTER the recorded adaptation "
                                          "(expect_lm15.adaptations); the adaptation is lossy by design"}
        case["provenance"] = {"source": "live-capture", "date": DATE,
                              "evidence": pin["evidence"] + f"; consumer-side pin — the wire side is the reference build, "
                                                            f"no live exchange of its own; {CHANGE}",
                              # D11: the exchange of the probe that carries the finding.
                              "exchange": exchange_of(host, pin["exchange_probe"])}
        case["canonical_request"] = serde.request_to_dict(request)
        case["canonical_request_provenance"] = {
            "source": "hand-authored", "date": DATE,
            "evidence": "authored from the probe cells it pins (research/providers/_inference_hosts_pins.py)"}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(CONTRACT)}: {'raises' if treq is None else ('adapts' if 'ingest' in case else 'sends')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
