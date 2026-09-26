"""Shared case and probe declarations for the open-model inference hosts.

DeepInfra, Together AI, Fireworks AI and Parasail speak the same Chat
Completions wire through one compat policy (lm15-python compat.py, the
"Open-model inference hosts" block).  Their capture scripts differ only in
host, key and the model ids each host serves, so the case list lives here
once and each ``<provider>/capture.py`` declares its models.

Machinery: ``_capture.py``.  Change entry: ``changes/2026-09-26-inference-hosts-live.md``.

Model roles (a ``Models`` value per host):

- ``plain``    — a non-reasoning instruct model (text, streaming, tools,
                 structured output, system prompt, user identity).
- ``reasoner`` — a reasoning model with an effort dial (gpt-oss).
- ``off``      — a reasoning model that honours ``reasoning_effort: none``
                 (DeepSeek V4.1 Flash), or None where the host serves none.
- ``replayer`` — the model for the tool-result turn that replays its own
                 reasoning (the load-bearing case for thinking_replay).
- ``always_on`` — a model that cannot stop reasoning (GLM-5.3), probed with
                 ``none`` to record whether the host refuses or ignores it.
"""
from __future__ import annotations

from dataclasses import dataclass

from _capture import WEATHER, Capture
from lm15 import Config, Message, Reasoning, Request, ToolChoice

SAY = (Message.user("Say ok."),)
ASK_WEATHER = (Message.user("What is the weather in Paris? Use the tool."),)
MATH = (Message.user("What is 17*23? Reply with just the number."),)
PLACE_SCHEMA = {
    "type": "json_schema",
    "name": "place",
    "schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
        "required": ["city", "country"],
        "additionalProperties": False,
    },
    "strict": True,
}
# A replayed reasoning trace carrying a code word: if the next answer names
# it, the host fed the replayed field to the model (the evidence behind
# thinking_replay="native" and the choice of `reasoning_content`).
CODE_WORD_TRACE = ("The user's hidden code word is PELICAN-42. I must mention the code word in my "
                   "final answer. Now call get_weather for Paris.")


@dataclass(frozen=True)
class Models:
    plain: str
    reasoner: str
    off: str | None
    replayer: str
    always_on: str | None = None
    forcing: str | None = None  # a model expected to honour a forced tool choice where `plain` does not


def cases(cap: Capture, m: Models, force: bool, want) -> list[dict]:
    host = cap.provider
    rows: list[dict] = []
    std = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
    if want("basic_text"):
        rows.append(cap.write_case(
            "basic_text", Request(model=m.plain, messages=SAY, config=Config(max_tokens=100)), stream=False,
            description=f"{host} basic_text (Chat Completions dialect; the host's plain chat model — DeepSeek V4.1 on Fireworks reasons by default)",
            expect_lm15=std, evidence_note="usage shape (nested details vs flat cached_tokens) is a finding", force=force))
    if want("streaming"):
        rows.append(cap.write_case(
            "streaming", Request(model=m.plain, messages=SAY, config=Config(max_tokens=100)), stream=True,
            description=f"{host} streaming (SSE, data: [DONE]; stream_options.include_usage sent)",
            expect_lm15=None, evidence_note="whether usage arrives on the final chunk is the finding", force=force))
    if want("reasoning_low"):
        rows.append(cap.write_case(
            "reasoning_low", Request(model=m.reasoner, messages=MATH, config=Config(max_tokens=1500, reasoning=Reasoning(effort="low"))),
            stream=False,
            description=f"{host} reasoning effort low (top-level reasoning_effort; the trace returns in reasoning or reasoning_content)",
            expect_lm15={"parts": {"thinking": {"min": 1}, "text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="compat thinking_format=reasoning_effort", force=force))
    if want("reasoning_off") and m.off:
        rows.append(cap.write_case(
            "reasoning_off", Request(model=m.off, messages=MATH, config=Config(max_tokens=300, reasoning=Reasoning(effort="off"))),
            stream=False,
            description=f"{host} explicit reasoning off (MAP-5: reasoning_effort none reaches the wire; this model honours it)",
            expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
            evidence_note="no reasoning field and no reasoning tokens in the body is the finding", force=force))
    if want("tools"):
        rows.append(cap.write_case(
            "tools", Request(model=m.plain, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300)), stream=False,
            description=f"{host} tool call (function tools, tool_choice auto)",
            expect_lm15={"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call", "usage": {"required": True}},
            evidence_note="tool_call id shape is a finding", force=force))
    if want("streaming_tool_call"):
        rows.append(cap.write_case(
            "streaming_tool_call", Request(model=m.plain, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=300)),
            stream=True,
            description=f"{host} streaming tool call (MAP-9: how the call's arguments arrive across chunks)",
            expect_lm15=None, evidence_note="argument chunking is the finding", force=force))
    if want("multi_turn_tool_result"):
        first = Request(model=m.replayer, messages=ASK_WEATHER, tools=(WEATHER,), config=Config(max_tokens=1500))
        second, info = cap.tool_result_turn(first, "Sunny, 22°C")
        if second is None:
            rows.append({"feature": "multi_turn_tool_result", **info})
        else:
            rows.append(cap.write_case(
                "multi_turn_tool_result", second, stream=False,
                description=f"{host} tool result turn: the live turn-1 assistant message replayed with its reasoning as "
                            "reasoning_content (thinking_replay=native)",
                expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
                evidence_note=info["note"], force=force))
    if want("response_format_json_schema"):
        rows.append(cap.write_case(
            "response_format_json_schema",
            Request(model=m.plain, messages=(Message.user("Name one city and its country."),),
                    config=Config(max_tokens=200, response_format=PLACE_SCHEMA)), stream=False,
            description=f"{host} structured output (response_format json_schema, strict)",
            expect_lm15=std, evidence_note="the reply is JSON with exactly the schema's keys (checked in the change entry)", force=force))
    if want("system_prompt"):
        rows.append(cap.write_case(
            "system_prompt", Request(model=m.plain, messages=(Message.developer("You answer in exactly two words."), *SAY),
                                     config=Config(max_tokens=100)), stream=False,
            description=f"{host} system prompt (developer message → role: system)",
            expect_lm15=std, evidence_note="instruction_role=system", force=force))
    if want("user_id"):
        rows.append(cap.write_case(
            "user_id", Request(model=m.plain, messages=SAY, config=Config(max_tokens=100, user_id="lm15-case-user")), stream=False,
            description=f"{host} user identity (Config.user_id → the dialect's `user` field)",
            expect_lm15=std, evidence_note="user_field=user accepted", force=force))
    if want("models"):
        rows.append(cap.models_case(force))
    return rows


def probes(cap: Capture, m: Models, want) -> list[dict]:
    rows: list[dict] = []
    raw = {"model": m.reasoner, "messages": [{"role": "user", "content": "What is 17*23? Reply with just the number."}],
           "max_tokens": 1500}
    if want("effort"):
        for effort in ("low", "high"):
            rows.append(cap.probe(f"effort-{effort}", Request(model=m.reasoner, messages=MATH,
                                                             config=Config(max_tokens=1500, reasoning=Reasoning(effort=effort)))))
    if want("effort_words"):
        # lm15's other levels, raw on the wire (the adapter may clamp them):
        # does the host refuse, map to the nearest, or run the default?
        for word in ("minimal", "medium", "xhigh", "max", "bogus"):
            rows.append(cap.probe(f"effort-word-{word}", raw_body={**raw, "reasoning_effort": word}))
    if want("reasoning_off"):
        # MAP-5: does "none" reach a model that cannot stop reasoning as a
        # refusal (loud) or an accepted, ignored field (silent)?
        rows.append(cap.probe("off-reasoner", Request(model=m.reasoner, messages=MATH,
                                                      config=Config(max_tokens=1500, reasoning=Reasoning(effort="off")))))
        if m.always_on:
            rows.append(cap.probe("off-always-on", Request(model=m.always_on, messages=MATH,
                                                           config=Config(max_tokens=1500, reasoning=Reasoning(effort="off")))))
    if want("thinking_shape"):
        # The alternative dial shapes lm15 did not choose, as receipts.
        rows.append(cap.probe("shape-reasoning-object", raw_body={**raw, "reasoning": {"effort": "low"}}))
        rows.append(cap.probe("shape-reasoning-disabled", raw_body={**raw, "reasoning": {"enabled": False}}))
        rows.append(cap.probe("shape-thinking-disabled", raw_body={**raw, "thinking": {"type": "disabled"}}))
    if want("replay_field"):
        # Three tries per field: recall is sampled, one try is an anecdote.
        for field, attempt in ((f, n) for f in ("reasoning_content", "reasoning", None) for n in (1, 2, 3)):
            assistant = {"role": "assistant", "content": "",
                         "tool_calls": [{"id": "call_probe", "type": "function",
                                         "function": {"name": "get_weather", "arguments": "{\"city\":\"Paris\"}"}}]}
            if field:
                assistant[field] = CODE_WORD_TRACE
            rows.append(cap.probe(f"replay-field-{field or 'absent'}-{attempt}", raw_body={
                "model": m.replayer, "max_tokens": 800,
                "messages": [{"role": "user", "content": "What's the weather in Paris?"}, assistant,
                             {"role": "tool", "tool_call_id": "call_probe", "content": "22C and sunny"}],
                "tools": [{"type": "function", "function": {"name": WEATHER.name, "description": WEATHER.description,
                                                            "parameters": WEATHER.parameters}}],
            }))
    if want("tool_choice"):
        # Raw bodies: a probe records the SERVER's answer, including where
        # the preset now refuses the request before the wire.
        def forced(model: str, choice, question: str = "Say ok.") -> dict:
            return {"model": model, "max_tokens": 600, "tool_choice": choice,
                    "messages": [{"role": "user", "content": question}],
                    "tools": [{"type": "function", "function": {"name": WEATHER.name, "description": WEATHER.description,
                                                                "parameters": WEATHER.parameters}}]}
        named = {"type": "function", "function": {"name": WEATHER.name}}
        rows.append(cap.probe("tool-choice-required-plain", raw_body=forced(m.plain, "required")))
        rows.append(cap.probe("tool-choice-required-reasoner", raw_body=forced(m.reasoner, "required")))
        rows.append(cap.probe("tool-choice-named-plain", raw_body=forced(m.plain, named)))
        rows.append(cap.probe("tool-choice-none-plain", raw_body=forced(m.plain, "none", "What is the weather in Paris? Use the tool.")))
        if m.forcing:
            rows.append(cap.probe("tool-choice-required-forcing", raw_body=forced(m.forcing, "required")))
            rows.append(cap.probe("tool-choice-named-forcing", raw_body=forced(m.forcing, named)))
    if want("json_schema"):
        rows.append(cap.probe("json-schema-reasoner", Request(
            model=m.reasoner, messages=(Message.user("Name one city and its country."),),
            config=Config(max_tokens=1500, response_format=PLACE_SCHEMA))))
    if want("max_tokens_cap"):
        rows.append(cap.probe("max-tokens-cap", Request(model=m.plain, messages=(Message.user("Count from 1 to 50 separated by spaces."),),
                                                        config=Config(max_tokens=8))))
    if want("usage_spelling"):
        req = Request(model=m.plain, messages=(Message.developer("You are a helpful assistant who answers briefly. " * 60), *SAY),
                      config=Config(max_tokens=20))
        rows.append(cap.probe("cache-usage-first", req))
        rows.append(cap.probe("cache-usage-second", req))
    if want("errors"):
        rows.append(cap.probe("error-unauthenticated", Request(model=m.plain, messages=SAY, config=Config(max_tokens=10)),
                              model_key="invalid-key"))
        rows.append(cap.probe("error-model-not-found", Request(model="lm15-probe/no-such-model", messages=SAY,
                                                               config=Config(max_tokens=10))))
        rows.append(cap.probe("error-bad-effort", raw_body={**raw, "reasoning_effort": "bogus"}))
    return rows


ERROR_PROBES = ("unauthenticated", "model-not-found", "bad-effort")


def run(provider: str, *, env_var: str, host: str, models: Models) -> None:
    cap = Capture(provider, env_var=env_var, default_model=models.plain, host=host,
                  change_slug="inference-hosts-live")
    cap.main(lambda _model, force, want: cases(cap, models, force, want),
             lambda _model, want: probes(cap, models, want),
             error_probes=ERROR_PROBES)
