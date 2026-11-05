"""Tests for harness/stream_checks.py: a variant must stay a legal stream
that says the same thing (or, for contradict, exactly one thing more).

    python3 -m unittest discover -s tools -p 'test_*.py'
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))

import stream_checks as sc  # noqa: E402


def sse(*payloads: dict, events: bool = False) -> bytes:
    out = []
    for p in payloads:
        head = f"event: {p['type']}\n" if events and "type" in p else ""
        out.append(head + "data: " + json.dumps(p) + "\n\n")
    return "".join(out).encode()


def payloads(body: bytes) -> list[dict]:
    return [f.payload for f in sc.parse_frames(body) if f.payload is not None]


RESPONSES = sse(
    {"type": "response.created", "sequence_number": 0, "response": {"id": "r"}},
    {"type": "response.output_item.added", "sequence_number": 1, "output_index": 0, "item": {"type": "function_call", "name": "f", "call_id": "c", "arguments": ""}},
    {"type": "response.function_call_arguments.delta", "sequence_number": 2, "output_index": 0, "delta": '{"city":'},
    {"type": "response.function_call_arguments.delta", "sequence_number": 3, "output_index": 0, "delta": ' "Paris"}'},
    {"type": "response.function_call_arguments.done", "sequence_number": 4, "output_index": 0, "arguments": '{"city": "Paris"}'},
    {"type": "response.output_item.done", "sequence_number": 5, "output_index": 0, "item": {"type": "function_call", "name": "f", "call_id": "c", "arguments": '{"city": "Paris"}'}},
    {"type": "response.completed", "sequence_number": 6, "response": {"id": "r", "output": [{"type": "function_call"}]}},
    events=True,
)


def responses_args(body: bytes) -> str:
    return "".join(p["delta"] for p in payloads(body) if p["type"] == "response.function_call_arguments.delta")


class ResponsesVariants(unittest.TestCase):
    def variant(self, name: str) -> bytes:
        return dict((n, b) for n, b, _ in sc.variants("responses", RESPONSES))[name]

    def test_split_keeps_the_text_and_renumbers(self) -> None:
        body = self.variant("split")
        self.assertEqual(responses_args(body), '{"city": "Paris"}')
        deltas = [p for p in payloads(body) if p["type"] == "response.function_call_arguments.delta"]
        self.assertGreater(len(deltas), 2)
        self.assertEqual([p["sequence_number"] for p in payloads(body)], list(range(len(payloads(body)))))
        self.assertIn(b"event: response.function_call_arguments.delta\n", body)  # event lines kept

    def test_merge_joins_consecutive_fragments(self) -> None:
        deltas = [p for p in payloads(self.variant("merge")) if p["type"] == "response.function_call_arguments.delta"]
        self.assertEqual([p["delta"] for p in deltas], ['{"city": "Paris"}'])

    def test_final_only_drops_restated_fragments_and_nothing_else(self) -> None:
        kept = [p["type"] for p in payloads(self.variant("final-only"))]
        self.assertNotIn("response.function_call_arguments.delta", kept)
        self.assertIn("response.output_item.done", kept)
        self.assertIn("response.function_call_arguments.done", kept)

    def test_contradict_breaks_the_prefix(self) -> None:
        args = responses_args(self.variant("contradict"))
        self.assertFalse('{"city": "Paris"}'.startswith(args))
        self.assertEqual(len(args), len('{"city": "Paris"}'))

    def test_expectations(self) -> None:
        self.assertEqual({n: e for n, _, e in sc.variants("responses", RESPONSES)},
                         {"split": "same", "merge": "same", "final-only": "same", "contradict": "refuse"})

    def test_final_copy(self) -> None:
        self.assertEqual(sc.final_copy("responses", sc.parse_frames(RESPONSES))["id"], "r")
        self.assertIsNone(sc.final_copy("chat", sc.parse_frames(RESPONSES)))

    def test_logprob_fragments_are_left_alone(self) -> None:
        body = sse({"type": "response.output_text.delta", "output_index": 0, "delta": "Hello", "logprobs": [{"token": "Hello"}]})
        self.assertEqual(sc.variants("responses", body), [])


class ChatVariants(unittest.TestCase):
    BODY = sse(
        {"id": "x", "choices": [{"index": 0, "delta": {"role": "assistant", "tool_calls": [{"index": 0, "id": "call_1", "type": "function", "function": {"name": "f", "arguments": '{"a":1}'}}]}, "finish_reason": None}]},
        {"id": "x", "choices": [{"index": 0, "delta": {"tool_calls": [{"index": 0, "function": {"arguments": ""}}]}, "finish_reason": None}]},
        {"id": "x", "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 1}},
    )

    def test_later_pieces_carry_no_identity(self) -> None:
        body = dict((n, b) for n, b, _ in sc.variants("chat", self.BODY))["split"]
        calls = [p["choices"][0]["delta"]["tool_calls"][0] for p in payloads(body) if p["choices"][0]["delta"].get("tool_calls")]
        self.assertEqual(calls[0]["id"], "call_1")
        self.assertTrue(all("id" not in c and "name" not in c["function"] for c in calls[1:-1]))
        self.assertEqual("".join(c["function"]["arguments"] for c in calls), '{"a":1}')
        self.assertNotIn("role", payloads(body)[1]["choices"][0]["delta"])

    def test_finish_chunk_untouched(self) -> None:
        body = dict((n, b) for n, b, _ in sc.variants("chat", self.BODY))["split"]
        self.assertEqual(payloads(body)[-1]["choices"][0]["finish_reason"], "tool_calls")


class GeminiVariants(unittest.TestCase):
    def test_rechunk_moves_calls_and_keeps_text_together(self) -> None:
        body = sse({"candidates": [{"content": {"parts": [{"text": "a"}, {"text": "b"}, {"functionCall": {"name": "f", "args": {}}},
                                                          {"functionCall": {"name": "f", "args": {"x": 1}}}], "role": "model"},
                                    "finishReason": "STOP", "index": 0}], "usageMetadata": {"promptTokenCount": 1}})
        out = payloads(dict((n, b) for n, b, _ in sc.variants("gemini", body))["rechunk"])
        self.assertEqual([[list(part) for part in p["candidates"][0]["content"]["parts"]] for p in out],
                         [[["text"], ["text"]], [["functionCall"]], [["functionCall"]]])
        self.assertEqual([p["candidates"][0].get("finishReason") for p in out], [None, None, "STOP"])
        self.assertTrue(all("usageMetadata" in p for p in out))


if __name__ == "__main__":
    unittest.main()
