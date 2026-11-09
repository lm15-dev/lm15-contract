#!/usr/bin/env python3
"""Tinker live capture: cases on both doors through lm15's own adapters.

    TINKER_API_KEY=… python3 research/providers/tinker/capture.py --door tinker [--dry-run] [--only a,b] [--force]
    TINKER_API_KEY=… python3 research/providers/tinker/capture.py --door tinker-anthropic [...]

Machinery: ../_capture.py, with Tinker's redaction (_tinker.py: the account's
email and organisation ids, in receipts AND in the verbatim bodies; a
redacted body's exchange hash is of the bytes as received). Survey and
decisions: README.md, SURVEY.md; change entry changes/2026-11-09-tinker-live.md.
Wire shapes only (terms § 1(e)): no latency is recorded.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tinker import CHECKPOINTS, ENV, HOST, TinkerCapture  # noqa: E402
from anthropic_survey import PIXEL  # noqa: E402
from _capture import CONTRACT, WEATHER  # noqa: E402
from lm15 import Config, ImagePart, Message, Reasoning, Request, ToolCallPart  # noqa: E402
from lm15.types import ToolResultPart  # noqa: E402

INKLING = "thinkingmachines/Inkling-Small"
QWEN = "Qwen/Qwen3.5-4B"
DEEPSEEK = "deepseek-ai/DeepSeek-V4.1-Flash:peft:262144"
SAY = (Message.user("Say ok."),)
MATH = (Message.user("What is 17*23? Reply with just the number."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
COUNT = (Message.user("Count from 1 to 20 separated by spaces."),)
LONG = "You are a helpful assistant who answers briefly. " * 60
OFF = Reasoning(effort="off")
STD = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
PLACE_SCHEMA = {"type": "json_schema", "name": "place", "strict": True, "schema": {
    "type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
    "required": ["city", "country"], "additionalProperties": False}}


class Cap(TinkerCapture):
    """TinkerCapture whose bodies are redacted too, and whose adapter may
    carry base_models (pinned on the case for the harness)."""

    base_models: dict[str, str] | None = None

    def send(self, treq):
        status, raw, ts, headers = super().send(treq)
        if raw:
            raw = self.redact(raw.decode("utf-8", "replace")).encode("utf-8")
        return status, raw, ts, headers

    def lm(self, model_key=None, *, clock=None, credential=None):
        adapter = super().lm(model_key, clock=clock, credential=credential)
        if self.base_models:
            adapter.base_models = dict(self.base_models)
        return adapter

    def write_case(self, feature, request, **kw):
        row = super().write_case(feature, request, **kw)
        path = CONTRACT / "cases" / self.provider / f"{feature}.json"
        if self.base_models and path.is_file() and not self.dry_run and "skipped" not in row:
            case = json.loads(path.read_text(encoding="utf-8"))
            case["base_models"] = dict(self.base_models)
            path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return row


def common(cap: Cap, force: bool, want, *, door: str) -> list[dict]:
    rows: list[dict] = []

    def case(feature, request, *, stream=False, description, expect=STD, note=""):
        if want(feature):
            rows.append(cap.write_case(feature, request, stream=stream, description=f"{door} {description}",
                                       expect_lm15=expect, evidence_note=note or "see the change entry", force=force))

    case("basic_text", Request(model=INKLING, messages=SAY, config=Config(max_tokens=300)),
         description="basic_text on Inkling-Small (reasons by default)")
    case("streaming", Request(model=INKLING, messages=SAY, config=Config(max_tokens=300)), stream=True,
         description="streaming (usage on the last event)", expect=None)
    case("reasoning_low", Request(model=INKLING, messages=MATH, config=Config(max_tokens=600, reasoning=Reasoning(effort="low"))),
         description="effort low on Inkling (the effort words)",
         expect={"parts": {"thinking": {"min": 1}, "text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}})
    case("reasoning_off", Request(model=INKLING, messages=MATH, config=Config(max_tokens=300, reasoning=OFF)),
         description="reasoning off on Inkling (honoured: no thinking)")
    case("tools", Request(model=INKLING, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)),
         description="tool call", expect={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}})
    case("streaming_tool_call", Request(model=INKLING, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=600)),
         stream=True, description="streaming tool call (arguments arrive whole)", expect=None)
    if want("multi_turn_tool_result"):
        first = Request(model=INKLING, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=800))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            case("multi_turn_tool_result", second,
                 description="tool result turn: the live turn-1 message replayed with its thinking (the replay the survey's "
                             "code word showed reaches the model)", note=info["note"])
    case("system_prompt", Request(model=INKLING, messages=(Message.developer("You answer in exactly two words."), *SAY),
                                  config=Config(max_tokens=300)),
         description="system prompt (a developer message: role system; the developer role is a 422 on the chat door)")
    case("stop_sequence", Request(model=INKLING, messages=COUNT, config=Config(max_tokens=100, reasoning=OFF, stop=(" 7",))),
         description="stop sequence: Tinker stops at it and returns it in the text; lm15 cuts it (MAP-22)",
         expect={"parts": {"text": {"min": 1}}, "usage": {"required": True}})
    case("streaming_stop_sequence", Request(model=INKLING, messages=COUNT, config=Config(max_tokens=100, reasoning=OFF, stop=(" 7",))),
         stream=True, description="streamed stop sequence: cut by the stream reader (MAP-22)", expect=None)
    if want("usage_cached"):
        warm = Request(model=INKLING, messages=SAY, system=LONG, config=Config(max_tokens=40, reasoning=OFF))
        rows.append(cap.probe("usage-cached-warmup", warm))
        case("usage_cached", warm, description="a repeated 560-token prompt: cached tokens are counted (exact cost, MAP-19)",
             expect={"parts": {"text": {"min": 1}}, "usage": {"required": True}})
    case("image_input", Request(model=INKLING, messages=(Message.user((ImagePart(data=PIXEL, media_type="image/png"),
                                                                         "What is the dominant color of this image? One word.")),),
                                config=Config(max_tokens=300, reasoning=OFF)),
         description="an image in the user turn (Inkling sees it; Qwen3.5-4B on this account refuses images, 400)")
    if want("tool_result_image"):
        call = ToolCallPart(id="call_panel", name="fetch_panel", input={"label": "A"})
        image = ImagePart(data=PIXEL, media_type="image/png")
        req = Request(model=INKLING, tools=(WEATHER,), config=Config(max_tokens=300, reasoning=OFF), messages=(
            Message.user("Call fetch_panel with label A, then tell me the panel's color in one word."),
            Message.assistant((call,)),
            Message(role="tool", parts=(ToolResultPart(id="call_panel", name="fetch_panel", content=(image,)),)),
        ))
        case("tool_result_image", req, description="an image in a tool result (received: the tool-result matrix, "
                                                   "receipts/2026-11-09-tool-result-media/); the call is the case's own",
             expect={"parts": {"text": {"min": 1}}, "usage": {"required": True}})
    return rows


def chat_only(cap: Cap, force: bool, want) -> list[dict]:
    rows: list[dict] = []

    def case(feature, request, *, description, expect=STD, base_models=None):
        if not want(feature):
            return
        cap.base_models = base_models
        try:
            rows.append(cap.write_case(feature, request, stream=False, description=f"tinker {description}",
                                       expect_lm15=expect, evidence_note="reasoning_survey.py receipts", force=force))
        finally:
            cap.base_models = None

    case("reasoning_off_switch", Request(model=QWEN, messages=MATH, config=Config(max_tokens=300, reasoning=OFF)),
         description="reasoning off on a switch family (Qwen 3.5): reasoning_effort false")
    case("reasoning_effort_switch", Request(model=QWEN, messages=SAY, config=Config(max_tokens=1200, reasoning=Reasoning(effort="high"))),
         description="an effort word on a switch family: reasoning_effort true, recorded as substituted (no levels)",
         expect={"adaptations": [{"field": "config.reasoning.effort", "action": "substituted", "asked": "high", "applied": "on"}]})
    case("reasoning_off_words", Request(model=DEEPSEEK, messages=MATH, config=Config(max_tokens=300, reasoning=OFF)),
         description="reasoning off on a words-and-switch family (DeepSeek V4.1): false; `none` is refused")
    case("checkpoint", Request(model=CHECKPOINTS[QWEN], messages=MATH, config=Config(max_tokens=300, reasoning=OFF)),
         description="a sampler checkpoint by its tinker:// path (one name, sent whole); base unnamed: the host default "
                     "(off is false), which its Qwen base takes")
    case("checkpoint_base_model", Request(model=CHECKPOINTS[INKLING], messages=MATH, config=Config(max_tokens=300, reasoning=OFF)),
         description="a checkpoint with its base named (base_models): Inkling's off word `none`",
         base_models={CHECKPOINTS[INKLING]: INKLING})
    case("response_format_json_schema", Request(model=INKLING, messages=(Message.user("Name one city and its country."),),
                                                config=Config(max_tokens=300, response_format=PLACE_SCHEMA)),
         description="response_format: ignored by Tinker (200, free text), dropped and recorded",
         expect={"adaptations": [{"field": "config.response_format", "action": "dropped", "asked": PLACE_SCHEMA}]})
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--door", choices=("tinker", "tinker-anthropic"), required=True)
    ap.add_argument("--only")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cap = Cap(args.door, env_var=ENV, default_model=INKLING, host=HOST, change_slug="tinker-live")
    cap.dry_run = args.dry_run
    cap.key()
    only = set(args.only.split(",")) if args.only else None
    want = lambda name: only is None or name in only  # noqa: E731
    rows = common(cap, args.force, want, door=args.door)
    if args.door == "tinker":
        rows += chat_only(cap, args.force, want)
    elif want("checkpoint"):
        rows.append(cap.write_case("checkpoint", Request(model=CHECKPOINTS[INKLING], messages=MATH,
                                                         config=Config(max_tokens=300, reasoning=Reasoning(effort="low"))),
                                   stream=False, description="tinker-anthropic a checkpoint by its tinker:// path, effort low",
                                   expect_lm15=STD, evidence_note="anthropic_survey.py", force=args.force))
    if not cap.dry_run:
        cap.write_receipt("SUMMARY.json", rows)
    for r in rows:
        name = r.get("feature") or r.get("probe")
        print(f"| {name} | {r.get('status', '-')} | {cap.redact(str(r.get('skipped') or r.get('parse') or r.get('summary') or r.get('error') or ''))[:150]} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
