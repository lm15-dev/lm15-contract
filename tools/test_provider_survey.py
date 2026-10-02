"""Offline tests for the provider survey rules (research/providers/_survey_rules.py).

Each case is a recorded server behaviour reduced to the fields the rules read;
several are the exact situations the 2026-10-02 backtests met (Z.AI's
always-on reasoner, DeepSeek's two working off switches, Groq's replay field,
a reasoning model cut short, a tool call written as text). No network, no lm15.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "providers"))
import _survey_rules as rules  # noqa: E402


def reply(content: str = "ok", *, finish: str = "stop", tool: bool = False, reasoning_tokens: int = 0,
          trace: str = "", usage: dict | None = None, status: int = 200) -> dict:
    message: dict = {"role": "assistant", "content": content}
    if tool:
        message["tool_calls"] = [{"id": "c1", "type": "function", "function": {"name": "get_weather", "arguments": "{}"}}]
    if trace:
        message["reasoning_content"] = trace
    u = {"prompt_tokens": 10, "completion_tokens": 5, **(usage or {})}
    if reasoning_tokens:
        u["completion_tokens_details"] = {"reasoning_tokens": reasoning_tokens}
    return {"status": status, "body": {"choices": [{"message": message, "finish_reason": finish}], "usage": u}}


def refused(message: str = "bad request", status: int = 400) -> dict:
    return {"status": status, "body": {"error": {"message": message}}}


def sse(*, usage: bool = True, done: bool = True) -> dict:
    lines = ['data: {"choices":[{"delta":{"content":"ok"}}]}']
    if usage:
        lines.append('data: {"choices":[],"usage":{"prompt_tokens":3,"completion_tokens":1}}')
    if done:
        lines.append("data: [DONE]")
    return {"status": 200, "body": "\n\n".join(lines)}


def find(findings: list, knob: str) -> rules.Finding:
    return next(f for f in findings if f.knob == knob)


MODELS = {"plain": "p", "reasoner": "r", "off": None, "replayer": "r", "always_on": None}


class KnobRules(unittest.TestCase):
    def test_max_tokens_field(self):
        f = rules.rule_max_tokens_field({"cap-max_completion_tokens": reply("1 2", finish="length"),
                                         "cap-max_tokens": reply("1 2", finish="length")})
        self.assertEqual((f.value, f.status, f.also), ("max_completion_tokens", rules.DECIDED, ["max_tokens"]))
        f = rules.rule_max_tokens_field({"cap-max_completion_tokens": reply("1 2 3 " * 30, usage={"completion_tokens": 90}),
                                         "cap-max_tokens": reply("1 2", finish="length")})
        self.assertEqual(f.value, "max_tokens")
        f = rules.rule_max_tokens_field({"cap-max_completion_tokens": refused(), "cap-max_tokens": refused()})
        self.assertEqual(f.status, rules.NEEDS_YOU)

    def test_stream_usage(self):
        self.assertEqual(rules.rule_stream_usage({"stream": sse()}).value, "include")
        f = rules.rule_stream_usage({"stream": refused(), "stream-plain": sse(usage=False)})
        self.assertEqual(f.value, "omit")
        self.assertEqual(rules.rule_stream_usage({"stream": sse(usage=False)}).status, rules.NEEDS_YOU)

    def test_thinking_format_needs_a_working_off_switch_or_a_spend_that_follows(self):
        # Z.AI glm-5.3-flash: cannot stop reasoning; low and high spent the same.
        zai = {"effort-low": reply("391", reasoning_tokens=7), "effort-high": reply("391", reasoning_tokens=7),
               "effort-none": refused("This model always engages in thinking"),
               "shape-thinking-enabled": reply("391", reasoning_tokens=40),
               "shape-thinking-disabled": refused("This model always engages in thinking")}
        self.assertEqual(rules.rule_thinking_format(zai, True).status, rules.NEEDS_YOU)
        # DeepSeek: both off switches work, so both shapes are valid.
        deepseek = {"effort-low": reply(reasoning_tokens=19), "effort-high": reply(reasoning_tokens=18),
                    "effort-none": reply(), "shape-thinking-enabled": reply(reasoning_tokens=18),
                    "shape-thinking-disabled": reply()}
        f = rules.rule_thinking_format(deepseek, True)
        self.assertEqual((f.value, f.status, f.also), ("reasoning_effort", rules.DECIDED, ["deepseek"]))
        # Only the thinking toggle works: the deepseek shape.
        toggle = {**deepseek, "effort-none": reply(reasoning_tokens=30)}
        self.assertEqual(rules.rule_thinking_format(toggle, True).value, "deepseek")
        # The spend follows the level, no off switch tested.
        spend = {"effort-low": reply(reasoning_tokens=12), "effort-high": reply(reasoning_tokens=117), "effort-none": refused()}
        self.assertEqual(rules.rule_thinking_format(spend, True).value, "reasoning_effort")
        self.assertEqual(rules.rule_thinking_format({}, False).status, rules.NEEDS_YOU)

    def test_reasoning_efforts_and_off(self):
        loose = {f"effort-word-{w}": reply() for w in ("minimal", "medium", "xhigh", "max", "bogus")}
        self.assertEqual(rules.rule_reasoning_efforts(loose, True).status, rules.NEEDS_YOU)
        strict = {**loose, "effort-word-bogus": refused()}
        self.assertEqual(rules.rule_reasoning_efforts(strict, True).status, rules.DECIDED)
        f = rules.rule_reasoning_off({"effort-none": reply(reasoning_tokens=66)}, True, "openai/gpt-oss-120b")
        self.assertEqual((f.value, f.override), (None, ("openai/gpt-oss-120b", {"reasoning_off": "lowest"})))
        self.assertIsNone(rules.rule_reasoning_off({"effort-none": refused()}, True, "r").override)
        always = rules.rule_reasoning_off_always_on({"effort-none-always-on": reply(reasoning_tokens=8)}, "zai-org/GLM-5.3-Flash")
        self.assertEqual(always[0].override, ("zai-org/GLM-5.3-Flash", {"reasoning_off": "lowest"}))

    def test_thinking_replay(self):
        def replay(rc, rs, absent):
            out = {}
            for name, spec in (("reasoning_content", rc), ("reasoning", rs), ("absent", absent)):
                for n, item in enumerate(spec, 1):
                    out[f"replay-{name}-{n}"] = item
            return out
        hit, miss = reply(f"The word is {rules.CODE_WORD}"), reply("22C")
        f = rules.rule_thinking_replay(replay([hit, hit, miss], [miss] * 3, [miss] * 3), True)[0]
        self.assertEqual((f.value, f.status), ("native", rules.DECIDED))
        # Groq: reasoning_content refused, `reasoning` recalled.
        f = rules.rule_thinking_replay(replay([refused()] * 3, [hit, hit, miss], [miss] * 3), True)[0]
        self.assertEqual(f.status, rules.NEEDS_YOU)
        self.assertIn("`reasoning` field is accepted and recalled 2/3", f.note)
        # Recalled without any trace: the probe proves nothing.
        f = rules.rule_thinking_replay(replay([hit] * 3, [hit] * 3, [hit, miss, miss]), True)[0]
        self.assertIsNone(f.value)
        # A turn without reasoning_content refused: DeepSeek's include_empty.
        fs = rules.rule_thinking_replay(replay([hit] * 3, [miss] * 3, [refused()] * 3), True)
        self.assertEqual(find(fs, "assistant_reasoning_content").value, "include_empty")

    def test_forced_tool_choice_and_json_schema(self):
        silent = {"tool-choice-required": reply("ok"), "tool-choice-named": reply(tool=True), "tool-choice-none": reply(tool=False)}
        self.assertEqual(rules.rule_forced_tool_choice(silent, None).value, "reject")
        good = {"tool-choice-required": reply(tool=True), "tool-choice-named": reply(tool=True), "tool-choice-none": reply("sunny?"),
                "tool-choice-required-reasoner": {"status": 500, "body": {"error": "x"}}}
        f = rules.rule_forced_tool_choice(good, "openai/gpt-oss")
        self.assertEqual((f.value, f.override), (None, ("openai/gpt-oss", {"forced_tool_choice": "reject"})))
        self.assertEqual(rules.rule_json_schema({"json-schema": reply('{"city": "Paris", "country": "France"}')}).value, None)
        self.assertEqual(rules.rule_json_schema({"json-schema": reply("```json\n{\"name\": \"Paris\"}\n```")}).value, "reject")
        self.assertEqual(rules.rule_json_schema({"json-schema": refused()}).status, rules.DECIDED)

    def test_draft_preset_never_takes_a_needs_you_value(self):
        findings = [rules.Finding("a", "x", rules.DECIDED, [], ""), rules.Finding("b", "y", rules.NEEDS_YOU, [], ""),
                    rules.Finding("c", None, rules.DECIDED, [], "", override=("m", {"reasoning_off": "lowest"}))]
        knobs, overrides = rules.draft_preset(findings)
        self.assertEqual(knobs, {"a": "x"})
        self.assertEqual(overrides, [("m", {"reasoning_off": "lowest"})])

    def test_compare(self):
        findings = [rules.Finding("max_tokens_field", "max_completion_tokens", rules.DECIDED, [], "", also=["max_tokens"]),
                    rules.Finding("stream_usage", None, rules.NEEDS_YOU, [], "")]
        rows = {r["knob"]: r["verdict"] for r in rules.compare(findings, {"max_tokens_field": "max_tokens",
                                                                          "stream_usage": "include", "user_field": "user_id"})}
        self.assertEqual(rows, {"max_tokens_field": "equivalent", "stream_usage": "needs you", "user_field": "not surveyable"})
        o = rules.compare_overrides([("openai/gpt-oss-120b", {"reasoning_off": "lowest"})], [["openai/gpt-oss", {"reasoning_off": "lowest"}]])
        self.assertEqual(o[0]["verdict"], "agree")


class Sweep(unittest.TestCase):
    def modes(self, **verdict_by_mode) -> dict:
        defaults = {"required": reply(tool=True), "named": reply(tool=True), "none": reply("It is sunny?"),
                    "control-auto": reply("ok"), "required-2": reply(tool=True)}
        defaults.update(verdict_by_mode)
        return {f"sweep-{m}": rec for m, rec in defaults.items()}

    def test_verdicts(self):
        self.assertEqual(rules.sweep_tool_choice(self.modes())[0], "honours")
        # Qwen3.6-27B on DeepInfra: the call written out as text under tool_choice none.
        self.assertEqual(rules.sweep_tool_choice(self.modes(none=reply('<tool_code>{"name": "get_weather"}')))[0], "ignores")
        # GLM-4.7: the budget ran out while reasoning: no answer to judge.
        self.assertEqual(rules.sweep_tool_choice(self.modes(none=reply("", finish="length")))[0], "inconclusive")
        self.assertEqual(rules.sweep_tool_choice(self.modes(**{"control-auto": reply(tool=True)}))[0], "inconclusive")
        self.assertEqual(rules.sweep_tool_choice(self.modes(required={"status": 500, "body": {}}))[0], "fails")
        self.assertEqual(rules.sweep_tool_choice(self.modes(none={"status": None, "body": None}))[0], "inconclusive")
        loud = {m: refused() for m in ("required", "named", "none", "control-auto", "required-2")}
        self.assertEqual(rules.sweep_tool_choice(self.modes(**loud))[0], "refuses-loudly")

    def test_worst_sample_wins(self):
        verdict, detail = rules.sweep_worst([("honours", "a"), ("ignores", "b")])
        self.assertEqual(verdict, "ignores")
        self.assertIn("2 samples", detail)

    def test_overrides_against_the_provider_wide_value(self):
        results = {"a": {"tool_choice": ("honours", "")}, "b": {"tool_choice": ("ignores", "")},
                   "c": {"tool_choice": ("inconclusive", "x"), "reasoning_off": ("ignores", "")}}
        allow, undecided = rules.sweep_overrides("reject", results)
        self.assertEqual(allow, [("a", {"forced_tool_choice": "send"}), ("c", {"reasoning_off": "lowest"})])
        self.assertEqual(len(undecided), 1)
        deny, _ = rules.sweep_overrides(None, results)
        self.assertEqual(deny, [("b", {"forced_tool_choice": "reject"}), ("c", {"reasoning_off": "lowest"})])


class Spec(unittest.TestCase):
    def test_validate(self):
        good = {"id": "cerebras", "name": "Cerebras", "dialect": "openai-chat", "base_url": "https://api.cerebras.ai/v1",
                "env_key": "CEREBRAS_API_KEY", "models": {"plain": "llama", "reasoner": None}}
        self.assertEqual(rules.validate_spec(good), [])
        for broken, needle in (({"id": "Cerebras"}, "id:"), ({"base_url": "https://x/{account}/v1"}, "base_url"),
                               ({"base_url": "https://api.cerebras.ai/v1/"}, "base_url"), ({"models": {"reasoner": "r"}}, "models.plain"),
                               ({"models": {"plain": "p", "fast": "f"}}, "unknown role"), ({"dialect": "gemini"}, "dialect")):
            self.assertTrue(any(needle in p for p in rules.validate_spec({**good, **broken})), (broken, needle))

    def test_committed_candidates_are_valid(self):
        root = Path(__file__).resolve().parents[1] / "research" / "providers"
        for path in sorted(root.glob("*/candidate.json")):
            spec = json.loads(path.read_text(encoding="utf-8"))
            if spec.get("base_url") is None or not (spec.get("models") or {}).get("plain"):
                continue  # an `init` skeleton awaiting the docs: complete it before `run`
            self.assertEqual(rules.validate_spec(spec), [], str(path))


if __name__ == "__main__":
    unittest.main()
