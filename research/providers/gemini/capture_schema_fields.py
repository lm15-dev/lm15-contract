#!/usr/bin/env python3
"""Gemini schema fields (MAP-16) — live cases and the probe matrix.

Machinery: ``research/providers/_capture.py``.  Receipts:
``receipts/<date>-gemini/``.

    GEMINI_API_KEY=… python3 research/providers/gemini/capture_schema_fields.py [--dry-run] [--only a,b] [--force]

Gemini carries a schema in one of two fields: an OpenAPI one
(``responseSchema``, ``functionDeclarations[].parameters``) that parses
only its own Schema object, and a JSON Schema one (``responseJsonSchema``,
``parametersJsonSchema``).  The probes send every schema of
``mapping/gemini-schema-field.json`` in all four fields, verbatim, and
record which the provider accepts; the vectors' expectations are read from
these receipts.  The two cases pin the adapter's choice end to end: a tool
whose parameters carry ``additionalProperties`` (the finding of
lm15-go receipts/2026-09-26-live-smoke), and a response schema that uses
``$defs`` / ``$ref`` (a Pydantic-shaped schema).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import CONTRACT, Capture  # noqa: E402
from lm15 import Config, FunctionTool, Message, Reasoning, Request  # noqa: E402

cap = Capture("gemini", env_var="GEMINI_API_KEY", default_model="gemini-2.5-flash",
              host="generativelanguage.googleapis.com", change_slug="gemini-schema-fields")

VECTORS = json.loads((CONTRACT / "mapping" / "gemini-schema-field.json").read_text(encoding="utf-8"))

FORECAST = FunctionTool(
    name="get_forecast",
    description="Weather forecast for a city on a date.",
    parameters={
        "type": "object",
        "properties": {"location": {"type": "string", "description": "City name"},
                       "date": {"type": "string", "description": "YYYY-MM-DD"}},
        "required": ["location", "date"],
        "additionalProperties": False,
    },
)
PYDANTIC_SHAPED = {
    "type": "object",
    "properties": {"person": {"$ref": "#/$defs/Person"}},
    "required": ["person"],
    "$defs": {"Person": {"type": "object", "title": "Person",
                         "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                         "required": ["name", "age"]}},
}


def cases(model: str, force: bool, want) -> list[dict]:
    rows = []
    if want("tool_parameters_json_schema"):
        rows.append(cap.write_case(
            "tool_parameters_json_schema",
            Request(model=model, tools=(FORECAST,),
                    messages=(Message.user("Use the tool: what is the forecast for Montreal on 2026-10-01?"),),
                    config=Config(max_tokens=200, reasoning=Reasoning(effort="off"))),
            stream=False,
            description="A tool schema with additionalProperties (outside Gemini's OpenAPI Schema object) goes as "
                        "functionDeclarations[].parametersJsonSchema, verbatim (MAP-16); under parameters the same "
                        "schema is a 400 (receipts/2026-09-26-gemini/probe-*)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="the model called get_forecast; MAP-16",
            force=force,
        ))
    if want("response_json_schema_defs"):
        rows.append(cap.write_case(
            "response_json_schema_defs",
            Request(model=model, messages=(Message.user("Extract the person: Ada is 36 years old."),),
                    config=Config(max_tokens=200, reasoning=Reasoning(effort="off"), response_format={"type": "json_schema", "name": "extraction",
                                                                   "schema": PYDANTIC_SHAPED})),
            stream=False,
            description="A response schema using $defs/$ref (a Pydantic-shaped schema, no additionalProperties) goes as "
                        "responseJsonSchema (MAP-16); under responseSchema it is a 400 'Unknown name \"$ref\"'",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="text parses as the schema's JSON; MAP-16",
            force=force,
        ))
    return rows


def probes(model: str, want) -> list[dict]:
    rows = []
    base = Request(model=model, messages=(Message.user("Give the value."),))
    for vector in VECTORS["cases"]:
        schema = vector["schema"]
        for field in ("responseSchema", "responseJsonSchema", "parameters", "parametersJsonSchema"):
            name = f"{vector['id']}.{field}"
            if not want(name) and not want(vector["id"]):
                continue
            body: dict = {"contents": [{"role": "user", "parts": [{"text": "Give the value."}]}],
                          "generationConfig": {"maxOutputTokens": 64, "thinkingConfig": {"thinkingBudget": 0}}}
            if field.startswith("response"):
                body["generationConfig"].update({"responseMimeType": "application/json", field: schema})
            else:
                body["tools"] = [{"functionDeclarations": [{"name": "f", field: schema}]}]
            rows.append(cap.probe(name, base, raw_body=body))
    return rows


if __name__ == "__main__":
    cap.main(cases, probes)
