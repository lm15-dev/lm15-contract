#!/usr/bin/env python3
"""Amazon Nova 2 on Bedrock's Chat Completions door: wire-shape discovery.

The catalog sweep (receipts/2026-09-03-bedrock-chat/door-catalog-sweep.json)
had every Nova 2 id answer 400 "#/messages/0/content: expected type:
JSONArray, found: String".  These raw-body probes find which message roles
need the array form, and what else the family accepts, so the compat knob
is shaped by receipts and not by guesswork.

    AWS_REGION=us-east-1 python3 research/providers/bedrock-chat/nova_probes.py [--only a,b]

Receipts: receipts/<date>-bedrock-chat/probe-nova-*.json.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _aws import REGION  # noqa: E402
from _capture import Capture  # noqa: E402

MODEL = os.environ.get("BEDROCK_NOVA_MODEL", "amazon.nova-2-lite-v1:0")
cap = Capture("bedrock-chat", env_var="AWS_BEARER_TOKEN_BEDROCK", default_model=MODEL,
              host=f"bedrock-runtime.{REGION}.amazonaws.com", settings={"region": REGION})

T = lambda s: [{"text": s}]  # noqa: E731  — Nova native content block (Converse shape); the OpenAI part form is refused: "extraneous key [type]"
WEATHER_TOOL = {"type": "function", "function": {"name": "get_weather", "description": "Weather for a city",
                "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}


def main(argv: list[str]) -> int:
    cap.dry_run = "--dry-run" in argv
    cap.aws_fixture()
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    want = lambda n: only is None or n in only  # noqa: E731
    base = {"model": MODEL, "max_completion_tokens": 50}
    rows = []
    P = lambda name, body: rows.append(cap.probe(f"nova-{name}", raw_body={k: v for k, v in {**base, **body}.items() if v is not None}))  # noqa: E731
    if want("user"):
        P("user-string", {"messages": [{"role": "user", "content": "Say ok."}]})
        P("user-openai-part", {"messages": [{"role": "user", "content": [{"type": "text", "text": "Say ok."}]}]})
        P("user-native-block", {"messages": [{"role": "user", "content": T("Say ok.")}]})
    if want("system"):
        P("system-string", {"messages": [{"role": "system", "content": "Answer in two words."}, {"role": "user", "content": T("Say ok.")}]})
        P("system-array", {"messages": [{"role": "system", "content": T("Answer in two words.")}, {"role": "user", "content": T("Say ok.")}]})
        P("developer-array", {"messages": [{"role": "developer", "content": T("Answer in two words.")}, {"role": "user", "content": T("Say ok.")}]})
    if want("assistant"):
        turns = [{"role": "user", "content": T("My name is Ada.")}]
        P("assistant-string", {"messages": turns + [{"role": "assistant", "content": "Hello Ada."}, {"role": "user", "content": T("What is my name?")}]})
        P("assistant-array", {"messages": turns + [{"role": "assistant", "content": T("Hello Ada.")}, {"role": "user", "content": T("What is my name?")}]})
    if want("max_tokens"):
        P("max-tokens-field", {"max_completion_tokens": None, "max_tokens": 50, "messages": [{"role": "user", "content": T("Say ok.")}]})
    if want("tools"):
        P("tools", {"max_completion_tokens": 300, "messages": [{"role": "user", "content": T("What is the weather in Paris? Use the tool.")}], "tools": [WEATHER_TOOL]})
        P("tool-choice-required", {"max_completion_tokens": 300, "messages": [{"role": "user", "content": T("Say ok.")}], "tools": [WEATHER_TOOL], "tool_choice": "required"})
        # Tool result replay: assistant tool_calls with content null, then role tool with a string
        assistant = {"role": "assistant", "content": None, "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": "{\"city\":\"Paris\"}"}}]}
        P("tool-result-string", {"max_completion_tokens": 300, "messages": [{"role": "user", "content": T("Weather in Paris? Use the tool.")}, assistant,
                                                                              {"role": "tool", "tool_call_id": "call_1", "content": "Sunny, 22°C"}], "tools": [WEATHER_TOOL]})
        P("tool-result-array", {"max_completion_tokens": 300, "messages": [{"role": "user", "content": T("Weather in Paris? Use the tool.")}, assistant,
                                                                             {"role": "tool", "tool_call_id": "call_1", "content": T("Sunny, 22°C")}], "tools": [WEATHER_TOOL]})
    if want("json_schema"):
        P("json-schema", {"max_completion_tokens": 300, "messages": [{"role": "user", "content": T("Where is the Eiffel Tower?")}],
                          "response_format": {"type": "json_schema", "json_schema": {"name": "place", "strict": True, "schema": {"type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}}, "required": ["city", "country"], "additionalProperties": False}}}})
    if want("reasoning"):
        P("reasoning-effort-low", {"max_completion_tokens": 300, "messages": [{"role": "user", "content": T("Say ok.")}], "reasoning_effort": "low"})
    if want("user_field"):
        P("user-field", {"messages": [{"role": "user", "content": T("Say ok.")}], "user": "lm15-probe-user"})
    if want("stream"):
        rows.append(cap.probe("nova-stream", raw_body={**base, "messages": [{"role": "user", "content": T("Say ok.")}], "stream": True, "stream_options": {"include_usage": True}}, stream=True))
    if want("image"):
        # A tiny 1x1 PNG data URI: does the door forward image_url to Nova?
        png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        P("image-url", {"max_completion_tokens": 50, "messages": [{"role": "user", "content": [{"text": "What colour is this?"}, {"type": "image_url", "image_url": {"url": png}}]}]})
        P("image-native", {"max_completion_tokens": 50, "messages": [{"role": "user", "content": [{"text": "What colour is this?"}, {"image": {"format": "png", "source": {"bytes": png.split(",", 1)[1]}}}]}]})
    for r in rows:
        print(r)
    return 0


if __name__ == "__main__" and {"--help", "-h"}.intersection(sys.argv):
    print(__doc__)
    sys.exit(0)

if __name__ == "__main__" and "--native" not in sys.argv:
    sys.exit(main(sys.argv[1:]))


def native(argv: list[str]) -> None:
    """Is the door a pass-through to the model's native schema?  Send the
    Nova native body (Nova user guide: messages[].content[].text,
    system[].text, inferenceConfig.maxTokens, toolConfig) to
    /openai/v1/chat/completions with no OpenAI field at all."""
    body = {"messages": [{"role": "user", "content": [{"text": "Say ok."}]}],
            "system": [{"text": "Answer in two words."}],
            "inferenceConfig": {"maxTokens": 50}}
    print(cap.probe("nova-native-body", raw_body={"model": MODEL, **body}))
    # and without model (the validator said [model] is extraneous)
    from lm15 import Message, Request
    print(cap.probe("nova-native-body-no-model", Request(model=MODEL, messages=(Message.user("x"),)), raw_body=body))


if __name__ == "__main__" and "--native" in sys.argv:
    cap.dry_run = "--dry-run" in sys.argv
    cap.aws_fixture()
    native(sys.argv)
