"""Five wire/spec reviews, not SDK-derived expected answers.

Scope and field-by-field reasoning: goldens/REVIEW-2026-11-22-anthropic.md.
Only stdlib JSON and the saved provider bytes are used; no lm15 imports.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
# Snapshot hashes identify bytes examined in this review. For the four old
# captures they are NOT historical exchange receipts or proof of authenticity.
REVIEWED = {
    "reasoning_off": ("966d32fedf91085294892a8fda9292cf37a943e3dd2ca8ae9885094f82295e1d", "msg_011CecvaTx78zuMTDLDk7eDr", "claude-sonnet-4-5-20250929", (22, 0, 0, 6, None), ["text"]),
    "reasoning_budget": ("faf3e87a79f97c1ddb024a2d6b33e164e5d9c7d21d3e2c30595780ae42462f40", "msg_011CeeeAAd3e7rkGosfN1zoX", "claude-sonnet-4-5-20250929", (56, 0, 0, 220, 188), ["thinking", "text"]),
    "reasoning_adaptive": ("aff9abcd3e38f1674ddbd8996407e8e527bb411237a45c05667321aa0c33dc69", "msg_011Ceee9xiRrtZz8ZYhKz3Kr", "claude-sonnet-5", (34, 0, 0, 133, 82), ["thinking", "text"]),
    "tool_no_description": ("87d2c825e52c14f23054bc6f1ac799b4f085db5654956708f4cd7213c5abc85e", "msg_011Cfe6YBxmqdBD9ky56PRPo", "claude-haiku-4-5-20251001", (557, 0, 0, 54, None), ["tool_use"]),
    "cache_history": ("1e60c73f050ae964cfd3bbd997f14baa6b930aeaa5d4295f376c13e226c856b7", "msg_011CeeahJ1wPjt64Qcivndic", "claude-sonnet-4-5-20250929", (3, 0, 3275, 6, None), ["text"]),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ReviewedAnthropicGoldens(unittest.TestCase):
    def load(self, name):
        case = read_json(ROOT / "cases" / "anthropic" / f"{name}.json")
        golden = read_json(ROOT / "goldens" / "anthropic" / f"{name}.json")
        self.assertEqual(case["pinned_body"], golden["provenance"]["pinned_body"])
        raw = (ROOT / "bodies" / case["id"] / case["pinned_body"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), REVIEWED[name][0])
        if "exchange" in case["provenance"]:
            receipt = read_json(ROOT / case["provenance"]["exchange"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["response_sha256"])
        return json.loads(raw), golden["canonical_response"]

    def verify(self, name, wire, answer):
        _, identity, model, counts, kinds = REVIEWED[name]
        self.assertEqual(wire["id"], identity)
        self.assertEqual(wire["model"], model)
        self.assertEqual(wire["type"], "message")
        self.assertEqual(wire["role"], "assistant")
        self.assertEqual([block["type"] for block in wire["content"]], kinds)
        parts = []
        for block in wire["content"]:
            if block["type"] == "text":
                parts.append({"type": "text", "text": block["text"]})
            elif block["type"] == "thinking":
                # MAP-7.8/.11: keep signed thinking, including empty text.
                parts.append({"type": "thinking", "text": block["thinking"], "continuation": [{
                    "provider": "anthropic", "kind": "thinking_signature", "data": {"signature": block["signature"]},
                }]})
            elif block["type"] == "tool_use":
                # MAP-1: this is a client call, not server_tool_use.
                self.assertEqual(block["caller"], {"type": "direct"})
                self.assertEqual(block["name"], "get_weather")
                self.assertEqual(block["input"], {"city": "Montreal"})
                parts.append({"type": "tool_call", "id": block["id"], "name": block["name"], "input": block["input"]})
            else:
                self.fail("review does not cover this content kind")
        if name == "reasoning_adaptive":
            self.assertEqual(parts[0]["text"], "")
        wire_usage = wire["usage"]
        uncached, read, written, output, thinking = counts
        self.assertEqual((wire_usage["input_tokens"], wire_usage["cache_read_input_tokens"], wire_usage["cache_creation_input_tokens"], wire_usage["output_tokens"], wire_usage.get("output_tokens_details", {}).get("thinking_tokens")), counts)
        # MAP-19.5 and INV-029: cache counts are beside wire input, reasoning
        # is already inside wire output. Never add the thinking count twice.
        usage = {"input_tokens": uncached + read + written, "output_tokens": output,
                 "total_tokens": uncached + read + written + output,
                 "cache_read_tokens": read, "cache_write_tokens": written}
        if thinking is not None:
            usage["reasoning_tokens"] = thinking
        self.assertEqual(wire["stop_reason"], "tool_use" if kinds == ["tool_use"] else "end_turn")
        # Exact projection, not a subset: catches omissions and invented fields.
        self.assertEqual(answer, {"id": identity, "model": model,
                                 "message": {"role": "assistant", "parts": parts},
                                 "finish_reason": "tool_call" if kinds == ["tool_use"] else "stop",
                                 "usage": usage})

    def test_five_reviewed_answers_match_wire_and_rules(self):
        for name in REVIEWED:
            with self.subTest(name=name):
                self.verify(name, *self.load(name))

    def test_review_detects_wrong_usage_lost_state_and_wrong_finish(self):
        mutations = [
            ("cache_history", lambda a: a["usage"].update(input_tokens=3, total_tokens=9)),
            ("reasoning_budget", lambda a: a["usage"].update(output_tokens=408, total_tokens=464)),
            ("reasoning_off", lambda a: a["usage"].update(reasoning_tokens=0)),
            ("reasoning_off", lambda a: a["usage"].pop("cache_read_tokens")),
            ("reasoning_adaptive", lambda a: a["message"]["parts"].pop(0)),
            ("reasoning_budget", lambda a: a["message"]["parts"][0]["continuation"][0]["data"].update(signature="changed")),
            ("tool_no_description", lambda a: a.update(finish_reason="stop")),
        ]
        for index, (name, mutate) in enumerate(mutations):
            with self.subTest(mutation=index, case=name):
                wire, answer = self.load(name)
                changed = copy.deepcopy(answer)
                mutate(changed)
                with self.assertRaises(AssertionError):
                    self.verify(name, wire, changed)


if __name__ == "__main__":
    unittest.main()
