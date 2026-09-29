#!/usr/bin/env python3
"""Write mapping/opaque-order.json: opaque objects whose member order a
JavaScript object cannot hold, built into every dialect's wire and read
back from every dialect's reply.

INV-002 and serde-rules.md omission rule 3: opaque payloads round-trip
exactly, key order included (changes/2026-09-25-opaque-key-order.md). A
JavaScript object enumerates array-index names ("0", "10", "2024") first,
in numeric order, whatever order they were written in; every recorded case
before 2026-09-29 had opaque objects whose order JavaScript keeps, so the
harness's order check could not see that host's reordering
(changes/2026-09-29-index-member-names.md).

    python3 tools/make_opaque_order_vectors.py          # write the file
    python3 tools/make_opaque_order_vectors.py --check  # exit 1 if it differs

Two kinds of vector:

- ``build``: a canonical request (the model is filled in per provider)
  built with ``build_request`` for each of the four chat dialects.
- ``parse``: a reply body read with ``parse_response`` (complete) or
  ``replay_stream`` (streamed). Each body is a RECORDED reply
  (``derived_from``) with one change, made here and nowhere else: the tool
  call's arguments replaced by ``READ_INPUT`` (in every place the reply
  carries them, and re-split over the same number of fragments when the
  reply streams them). The bodies are therefore hand-authored, not recorded
  traffic; they claim nothing about a provider, only that lm15 reads what
  the bytes say, in their order. tools/test_mapping_vectors.py re-derives
  every body from its source and fails on any drift.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "mapping" / "opaque-order.json"

MODELS = {
    "openai": "gpt-4.1-mini",
    "openai_chat": "gpt-4.1-mini",
    "anthropic": "claude-sonnet-4-5",
    "gemini": "gemini-2.5-flash",
}

# A schema a caller writes reasoning-first: the order a model fills strict
# structured output in (OpenAI: "outputs will be produced in the same order
# as the ordering of keys in the schema"). JavaScript would write "1",
# "2024", "reasoning": the answer before the reasoning meant to produce it.
SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "2024": {"type": "integer"},
        "1": {"type": "string"},
    },
    "required": ["reasoning", "2024", "1"],
    "additionalProperties": False,
}

# Deeper: index names out of numeric order ("10" before "9"), and a nested
# object schema with its own.
NESTED_SCHEMA = {
    "type": "object",
    "properties": {
        "10": {"type": "string"},
        "9": {"type": "string"},
        "item": {
            "type": "object",
            "properties": {"z": {"type": "string"}, "0": {"type": "string"}},
            "required": ["z", "0"],
        },
    },
    "required": ["10", "9", "item"],
}

CALL_INPUT = {"reasoning": "r", "2024": 7, "1": "x"}

USER = {"role": "user", "parts": [{"type": "text", "text": "Record it."}]}


def _tool(schema: dict) -> dict:
    return {"type": "function", "name": "record", "description": "Record the answer.", "parameters": schema}


BUILD = [
    {
        "id": "tool-parameters",
        "why": "a FunctionTool's parameters (JSON Schema)",
        "request": {"messages": [USER], "tools": [_tool(SCHEMA)]},
    },
    {
        "id": "tool-parameters-nested",
        "why": "index names out of numeric order, and a nested schema's own properties",
        "request": {"messages": [USER], "tools": [_tool(NESTED_SCHEMA)]},
    },
    {
        "id": "response-format-schema",
        "why": "a json_schema response_format: the order a model writes structured output in",
        "request": {"messages": [USER], "config": {"response_format": {
            "type": "json_schema", "name": "answer", "schema": SCHEMA, "strict": True}}},
    },
    {
        "id": "tool-call-input",
        "why": "a tool call's input sent back in the history (an object, or the arguments string)",
        "request": {"messages": [
            USER,
            {"role": "assistant", "parts": [{"type": "tool_call", "id": "call_1", "name": "record", "input": CALL_INPUT}]},
            {"role": "tool", "parts": [{"type": "tool_result", "id": "call_1", "content": [{"type": "text", "text": "ok"}]}]},
        ], "tools": [_tool(SCHEMA)]},
    },
    {
        "id": "extensions",
        "why": "an extensions value, merged into the body verbatim",
        "request": {"messages": [USER], "config": {"extensions": {"metadata": {"b": "x", "10": "y"}}}},
    },
    {
        "id": "extensions-index-names",
        "why": "an object of index names only, not in numeric order (Chat Completions logit_bias)",
        "providers": ["openai_chat"],
        "request": {"messages": [USER], "config": {"extensions": {"logit_bias": {"1234": -100, "15": 5}}}},
    },
    {
        "id": "data-part",
        "why": "a DataPart's value, sent as its JSON text",
        "request": {"messages": [{"role": "user", "parts": [{"type": "data", "value": {"b": 1, "10": 2}}]}]},
    },
]

# What each reply's tool call carries instead of its recorded arguments.
READ_INPUT = {"reasoning": "It is 2024.", "2024": {"b": 1, "0": 2}, "1": [{"y": 1, "3": 2}]}

# (id, provider, stream, case file whose pinned body is the source)
PARSE_SOURCES = [
    ("anthropic", False, "cases/anthropic/tools.json"),
    ("anthropic", True, "cases/anthropic/streaming_tool_call.json"),
    ("openai", False, "cases/openai/tools.json"),
    ("openai", True, "cases/openai/streaming_tool_call.json"),
    ("openai_chat", False, "cases/openai_chat/tools.json"),
    ("openai_chat", True, "cases/openai_chat/streaming_tool_call.json"),
    ("gemini", False, "cases/gemini/tools.json"),
    ("gemini", True, "cases/gemini/streaming_tool_call.json"),
]


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _parses_to(text: str, target: Any) -> bool:
    try:
        return json.loads(text) == target
    except (ValueError, TypeError):
        return False


def _replace(value: Any, old: Any, new: Any) -> tuple[Any, int]:
    """Every object equal to ``old`` becomes ``new``; every string that is
    ``old``'s JSON becomes ``new``'s compact JSON. Returns the count."""
    if isinstance(value, dict):
        if value == old:
            return copy.deepcopy(new), 1
        count = 0
        out = {}
        for key, item in value.items():
            out[key], n = _replace(item, old, new)
            count += n
        return out, count
    if isinstance(value, list):
        count = 0
        out_list = []
        for item in value:
            replaced, n = _replace(item, old, new)
            out_list.append(replaced)
            count += n
        return out_list, count
    if isinstance(value, str) and value.lstrip().startswith("{") and _parses_to(value, old):
        return compact(new), 1
    return value, 0


def _split(text: str, n: int) -> list[str]:
    size, extra = divmod(len(text), n)
    pieces, at = [], 0
    for i in range(n):
        step = size + (1 if i < extra else 0)
        pieces.append(text[at:at + step])
        at += step
    return pieces


# Where each streaming dialect carries an argument fragment: a getter and a
# setter on one event's data, or None when the event carries none.
Fragment = tuple[Callable[[dict], str], Callable[[dict, str], None]]


def _fragment(provider: str, data: dict) -> Fragment | None:
    if provider == "anthropic":
        delta = data.get("delta")
        if data.get("type") == "content_block_delta" and isinstance(delta, dict) and delta.get("type") == "input_json_delta":
            return (lambda d: d["delta"]["partial_json"], lambda d, s: d["delta"].__setitem__("partial_json", s))
    elif provider == "openai":
        if data.get("type") == "response.function_call_arguments.delta":
            return (lambda d: d["delta"], lambda d, s: d.__setitem__("delta", s))
    elif provider == "openai_chat":
        for choice in data.get("choices") or []:
            for call in (choice.get("delta") or {}).get("tool_calls") or []:
                fn = call.get("function") or {}
                if "arguments" in fn:
                    return (lambda d: d["choices"][0]["delta"]["tool_calls"][0]["function"]["arguments"],
                            lambda d, s: d["choices"][0]["delta"]["tool_calls"][0]["function"].__setitem__("arguments", s))
    return None


def _sse_events(text: str) -> list[list[str]]:
    blocks = [b for b in text.replace("\r\n", "\n").split("\n\n") if b.strip()]
    return [b.split("\n") for b in blocks]


def derive_stream(provider: str, text: str, old: Any, new: Any) -> str:
    events = _sse_events(text)
    parsed: list[tuple[list[str], dict | None]] = []
    for lines in events:
        data_lines = [ln[len("data:"):].lstrip() for ln in lines if ln.startswith("data:")]
        others = [ln for ln in lines if not ln.startswith("data:")]
        if len(data_lines) != 1:
            raise SystemExit(f"{provider}: an SSE event without exactly one data line: {lines!r}")
        try:
            data = json.loads(data_lines[0])
        except ValueError:
            parsed.append((lines, None))  # e.g. data: [DONE]
            continue
        parsed.append((others, data))
    fragments = [(data, frag) for _, data in parsed if isinstance(data, dict) and (frag := _fragment(provider, data))]
    joined = "".join(get(data) for data, (get, _) in fragments)
    if fragments and not _parses_to(joined, old):
        raise SystemExit(f"{provider}: the recorded fragments do not join to the recorded input: {joined!r}")
    filled = [(data, frag) for data, frag in fragments if frag[0](data) != ""]
    pieces = _split(compact(new), len(filled)) if filled else []
    for (data, (_, put)), piece in zip(filled, pieces):
        put(data, piece)
    total = len(filled)
    out_blocks = []
    for head, data in parsed:
        if data is None:
            out_blocks.append("\n".join(head))
            continue
        # A fragment is not a whole input: _replace would not match it anyway.
        replaced, n = _replace(data, old, new)
        total += n
        out_blocks.append("\n".join([*head, "data: " + compact(replaced)]))
    if total == 0:
        raise SystemExit(f"{provider}: the stream never carried the recorded input")
    return "\n\n".join(out_blocks) + "\n\n"


def derive_complete(provider: str, text: str, old: Any, new: Any) -> str:
    replaced, n = _replace(json.loads(text), old, new)
    if n == 0:
        raise SystemExit(f"{provider}: the reply never carried the recorded input")
    return compact(replaced)


def recorded_input(case: dict, body: str, stream: bool) -> Any:
    """The tool call input the recorded reply carries (the golden's)."""
    golden = json.loads((ROOT / "goldens" / case["provider"] / f"{case['feature']}.json").read_text(encoding="utf-8"))
    calls = [p for p in golden["canonical_response"]["message"]["parts"] if p.get("type") == "tool_call"]
    if len(calls) != 1:
        raise SystemExit(f"{case['id']}: expected one tool call in the golden, found {len(calls)}")
    return calls[0]["input"]


def parse_vectors() -> list[dict]:
    out = []
    for provider, stream, case_path in PARSE_SOURCES:
        case = json.loads((ROOT / case_path).read_text(encoding="utf-8"))
        body_path = f"bodies/{case['id']}/{case['pinned_body']}"
        text = (ROOT / body_path).read_text(encoding="utf-8")
        old = recorded_input(case, text, stream)
        body = derive_stream(provider, text, old, READ_INPUT) if stream else derive_complete(provider, text, old, READ_INPUT)
        request = copy.deepcopy(case["canonical_request"])
        out.append({
            "id": f"read-{provider.replace('_', '-')}{'-stream' if stream else ''}",
            "provider": provider,
            "stream": stream,
            "derived_from": body_path,
            "canonical_request": request,
            "body": body,
            "tool_input": READ_INPUT,
        })
    return out


def document() -> dict:
    return {
        "description": (
            "INV-002 vectors: opaque objects with array-index member names (\"10\", \"2024\") after other names, "
            "or out of numeric order, which a JavaScript object enumerates first. The harness's mapping direction "
            "builds each `build` vector for each provider in `providers` (or the vector's own list) with "
            "build_request, and reads each `parse` vector with parse_response or replay_stream. Every object in a "
            "vector whose order JavaScript would change must reach the result with the same member names, in the "
            "same order: in the wire body (inside a JSON string too, e.g. a Chat Completions `arguments`), or in "
            "the canonical response (a tool call's `input`). Generated by tools/make_opaque_order_vectors.py; do not "
            "edit by hand."
        ),
        "provenance": {
            "source": "hand-authored",
            "date": "2026-09-29",
            "evidence": (
                "spec/invariants.md INV-002; docs/serde-rules.md omission rule 3; changes/2026-09-25-opaque-key-order.md; "
                "changes/2026-09-29-index-member-names.md. Each parse body is its `derived_from` recorded body with the "
                "tool call's arguments replaced (tools/make_opaque_order_vectors.py, checked by tools/test_mapping_vectors.py)."
            ),
        },
        "providers": MODELS,
        "build": BUILD,
        "parse": parse_vectors(),
    }


def render() -> str:
    return json.dumps(document(), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 when mapping/opaque-order.json differs")
    args = parser.parse_args()
    text = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT)} differs from tools/make_opaque_order_vectors.py", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
