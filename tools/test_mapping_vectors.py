"""The mapping/ vectors: mapping/gemini-schema-field.json against the
receipts it was read from, and mapping/opaque-order.json against its
generator and the recorded replies its bodies come from.

mapping/gemini-schema-field.json:

Every vector was sent verbatim in Gemini's four schema fields on 2026-09-26
(research/providers/gemini/capture_schema_fields.py). Where exactly one
kind of field (OpenAPI or JSON Schema) accepted it in both places, the
vector must name that kind; where both or neither did, MAP-16 decides and
the receipts constrain nothing. A vector without its four receipts fails:
an expectation nobody observed is not evidence.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VECTORS = ROOT / "mapping" / "gemini-schema-field.json"
RECEIPTS = ROOT / "receipts" / "2026-09-26-gemini"
FIELDS = ("responseSchema", "parameters", "responseJsonSchema", "parametersJsonSchema")


class GeminiSchemaFieldVectors(unittest.TestCase):
    def test_every_decisive_receipt_agrees_with_its_vector(self) -> None:
        doc = json.loads(VECTORS.read_text(encoding="utf-8"))
        self.assertTrue(doc["cases"])
        for vector in doc["cases"]:
            with self.subTest(vector=vector["id"]):
                status = {}
                for field in FIELDS:
                    receipt = RECEIPTS / f"probe-{vector['id']}.{field}.json"
                    self.assertTrue(receipt.is_file(), f"no receipt {receipt.name}")
                    data = json.loads(receipt.read_text(encoding="utf-8"))
                    self.assertEqual(data["sent"]["body"].get("generationConfig", {}).get(field,
                                     (data["sent"]["body"].get("tools") or [{}])[0].get("functionDeclarations", [{}])[0].get(field)),
                                     vector["schema"], f"{receipt.name} did not send this vector's schema")
                    status[field] = data["status"]
                openapi_ok = status["responseSchema"] == 200 and status["parameters"] == 200
                json_ok = status["responseJsonSchema"] == 200 and status["parametersJsonSchema"] == 200
                if openapi_ok != json_ok:
                    self.assertEqual(vector["openapi"], openapi_ok,
                                     f"only the {'OpenAPI' if openapi_ok else 'JSON Schema'} fields accepted {vector['id']}")


class OpaqueOrderVectors(unittest.TestCase):
    """mapping/opaque-order.json (INV-002; changes/2026-09-29-index-member-names.md)."""

    @classmethod
    def setUpClass(cls) -> None:
        import subprocess
        import sys
        sys.path.insert(0, str(ROOT / "harness"))
        import check  # noqa: E402
        cls.check = check
        cls.doc = json.loads((ROOT / "mapping" / "opaque-order.json").read_text(encoding="utf-8"))
        cls.generated = subprocess.run([sys.executable, str(ROOT / "tools" / "make_opaque_order_vectors.py"), "--check"],
                                       capture_output=True, text=True, encoding="utf-8")

    def test_the_file_is_the_generator_output(self) -> None:
        # Every parse body is re-derived from its recorded source: a hand
        # edit, or a source that changed, fails here.
        self.assertEqual(self.generated.returncode, 0, self.generated.stderr)

    def test_every_vector_holds_an_order_javascript_would_change(self) -> None:
        for vector in self.doc["build"]:
            with self.subTest(vector=vector["id"]):
                self.assertTrue(self.check.reordered_objects(vector["request"]))
        for vector in self.doc["parse"]:
            with self.subTest(vector=vector["id"]):
                self.assertTrue(self.check.reordered_objects(vector["tool_input"]))

    def test_member_names_identify_one_order(self) -> None:
        # The harness finds each object by its member names; two objects
        # with the same names and different orders would be ambiguous.
        for vector in self.doc["build"]:
            with self.subTest(vector=vector["id"]):
                orders = self.check.reordered_objects(vector["request"])
                self.assertEqual(len({frozenset(o) for o in orders}), len(orders))

    def test_parse_bodies_come_from_recorded_replies(self) -> None:
        for vector in self.doc["parse"]:
            with self.subTest(vector=vector["id"]):
                self.assertTrue(vector["derived_from"].startswith("bodies/"))
                self.assertTrue((ROOT / vector["derived_from"]).is_file())

    def test_array_index_names(self) -> None:
        is_index = self.check.is_index_name
        for name in ("0", "1", "10", "2024", "4294967294"):
            self.assertTrue(is_index(name), name)
        for name in ("", "01", "-1", "1.0", "1e3", " 1", "4294967295", "99999999999", "a1", "\u0661"):
            self.assertFalse(is_index(name), name)
        self.assertEqual(self.check.javascript_order(["b", "10", "9", "a", "0"]), ["0", "9", "10", "b", "a"])

    def test_the_order_check_looks_inside_json_strings(self) -> None:
        wanted = [("reasoning", "2024")]
        good = {"arguments": json.dumps({"reasoning": "r", "2024": 1})}
        bad = {"arguments": json.dumps({"2024": 1, "reasoning": "r"})}
        self.assertIsNone(self.check.member_order_difference(wanted, good, "$"))
        self.assertIsNotNone(self.check.member_order_difference(wanted, bad, "$"))
        self.assertIsNotNone(self.check.member_order_difference(wanted, {"x": 1}, "$"))  # absent



class EmptyPartsVectors(unittest.TestCase):
    """mapping/empty-parts.json and the history replay (MAP-24;
    changes/2026-11-11-empty-parts.md)."""

    @classmethod
    def setUpClass(cls) -> None:
        import subprocess
        import sys
        sys.path.insert(0, str(ROOT / "harness"))
        import check  # noqa: E402
        cls.check = check
        cls.doc = json.loads((ROOT / "mapping" / "empty-parts.json").read_text(encoding="utf-8"))
        cls.generated = subprocess.run([sys.executable, str(ROOT / "tools" / "make_empty_parts_vectors.py"), "--check"],
                                       capture_output=True, text=True, encoding="utf-8")

    def test_the_file_is_what_its_generator_writes(self) -> None:
        self.assertEqual(self.generated.returncode, 0, self.generated.stderr)

    @staticmethod
    def _writes_nothing(part: dict) -> bool:
        """What a `same_as` request may take out: empty text, empty
        thinking (whatever its state: `same_as.providers` names the
        dialects that do not consume it), a citation that quotes nothing."""
        if part.get("type") in ("text", "thinking"):
            return part.get("text") == ""
        return part.get("type") == "citation" and not part.get("text")

    def _removal_only(self, full: list, kept: list, where: str) -> None:
        """`kept` is `full` with some items taken out, every one of them a
        part that writes nothing or a container left empty by that."""
        j = 0
        for item in full:
            if j < len(kept) and self._same(item, kept[j], where):
                j += 1
                continue
            self.assertTrue(self._empty(item), f"{where}: `same_as` drops something that is not empty: {json.dumps(item)[:120]}")
        self.assertEqual(j, len(kept), f"{where}: `same_as` holds something the request does not")

    def _empty(self, item: dict) -> bool:
        if "parts" in item:  # a message
            return all(self._writes_nothing(p) for p in item["parts"])
        return self._writes_nothing(item)

    def _same(self, a: dict, b: dict, where: str) -> bool:
        if "parts" in a and "parts" in b:  # two messages: same role, parts by removal only
            if a["role"] != b["role"]:
                return False
            try:
                self._removal_only(a["parts"], b["parts"], where)
            except AssertionError:
                return False
            return True
        if a.get("type") == "tool_result" and b.get("type") == "tool_result":
            head = {k: v for k, v in a.items() if k != "content"} == {k: v for k, v in b.items() if k != "content"}
            if not head:
                return False
            try:
                self._removal_only(a["content"], b["content"], where)
            except AssertionError:
                return False
            return True
        return a == b

    def test_same_as_is_the_request_with_only_empty_parts_taken_out(self) -> None:
        for vector in self.doc["build"]:
            same = vector.get("same_as")
            if same is None:
                continue
            with self.subTest(vector=vector["id"]):
                full, kept = vector["request"], same["request"]
                self._removal_only(full["messages"], kept["messages"], vector["id"])
                full_system, kept_system = full.get("system") or [], kept.get("system") or []
                self._removal_only(full_system, kept_system, vector["id"] + ".system")
                self.assertTrue(kept["messages"], "a request with no message has no equivalent; pin it with `expect`")
                for message in kept["messages"]:
                    for part in message["parts"]:
                        self.assertFalse(self._writes_nothing(part) and not part.get("continuation"),
                                         "`same_as` still holds an empty part")

    def test_every_provider_of_a_vector_has_an_expectation(self) -> None:
        for vector in self.doc["build"]:
            providers = vector.get("providers") or self.doc["dialects"]
            same = vector.get("same_as")
            covered = set(vector.get("expect") or {}) | set((same.get("providers") or providers) if same else [])
            self.assertEqual([p for p in providers if p not in covered], [], vector["id"])
            for provider in providers:
                self.assertIn(provider, self.doc["models"], vector["id"])

    def test_no_expectation_holds_what_the_rule_forbids(self) -> None:
        for vector in self.doc["build"]:
            for provider, body in (vector.get("expect") or {}).items():
                self.assertEqual(self.check.empty_wire_findings(body), [], f"{vector['id']}[{provider}]")

    def test_the_scanner_finds_each_forbidden_shape_and_nothing_else(self) -> None:
        find = self.check.empty_wire_findings
        empty = {"type": "text", "text": ""}
        forbidden = {
            "a Messages text block": {"messages": [{"role": "assistant", "content": [empty, {"type": "tool_use", "id": "c", "name": "f", "input": {}}]}]},
            "a Messages message with no block": {"messages": [{"role": "assistant", "content": []}]},
            "a Messages system block": {"system": [empty], "messages": []},
            "a Messages tool result block": {"messages": [{"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "c", "content": [empty, {"type": "image", "source": {}}]}]}]},
            "a Gemini part": {"contents": [{"role": "model", "parts": [{"text": ""}]}]},
            "a Gemini thought part with no signature": {"contents": [{"role": "model", "parts": [{"text": "", "thought": True}]}]},
            "a Gemini content with no parts": {"contents": [{"role": "model", "parts": []}]},
            "a Gemini system part": {"systemInstruction": {"parts": [{"text": ""}]}, "contents": []},
            "a Responses output_text": {"input": [{"role": "assistant", "content": [{"type": "output_text", "text": ""}]}]},
            "a Responses input_text": {"input": [{"role": "user", "content": [{"type": "input_text", "text": ""}]}]},
            "Responses instructions": {"instructions": "", "input": []},
            "a Responses tool output block": {"input": [{"type": "function_call_output", "call_id": "c",
                                                         "output": [{"type": "input_text", "text": ""}]}]},
            "a Chat row with null content and no call": {"messages": [{"role": "assistant", "content": None}]},
            "a Chat row with null content and empty reasoning": {"messages": [{"role": "assistant", "content": None, "reasoning_content": ""}]},
            "a Chat row with empty content": {"messages": [{"role": "user", "content": ""}]},
            "a Chat system row with empty content": {"messages": [{"role": "system", "content": ""}]},
            "a Chat content block": {"messages": [{"role": "user", "content": [empty, {"type": "text", "text": "x"}]}]},
        }
        for name, body in forbidden.items():
            self.assertTrue(find(body), name)
        allowed = {
            "a Gemini part with empty text and its signature": {"contents": [{"role": "model", "parts": [
                {"text": "", "thoughtSignature": "s"}, {"text": "", "thought": True, "thoughtSignature": "s"}]}]},
            "a signed thinking block with empty thinking": {"messages": [{"role": "assistant", "content": [
                {"type": "thinking", "thinking": "", "signature": "s"}, {"type": "text", "text": "x"}]}]},
            "a reasoning item with an empty summary": {"input": [{"type": "reasoning", "id": "rs", "summary": []}]},
            "a tool result with the empty string": {"messages": [{"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "c", "content": ""}]}]},
            "a Chat tool row with the empty string": {"messages": [{"role": "tool", "tool_call_id": "c", "content": ""}]},
            "a Responses tool output with the empty string": {"input": [{"type": "function_call_output", "call_id": "c", "output": ""}]},
            "a Chat row with null content beside its call": {"messages": [{"role": "assistant", "content": None, "tool_calls": [{}]}]},
            "a Chat row with null content and reasoning": {"messages": [{"role": "assistant", "content": None, "reasoning_content": "x"}]},
            "an empty text inside a tool call's input": {"messages": [{"role": "assistant", "content": [
                {"type": "tool_use", "id": "c", "name": "f", "input": {"type": "text", "text": ""}}]}]},
            "whitespace": {"messages": [{"role": "assistant", "content": [{"type": "text", "text": "\n"}]}]},
            "an empty list of messages": {"messages": []},
        }
        for name, body in allowed.items():
            self.assertEqual(find(body), [], name)

    def test_no_pinned_wire_holds_what_the_rule_forbids(self) -> None:
        """A capture cannot pin an empty block: every recorded request body
        in cases/ is scanned."""
        for case in self.check.load_wire_cases():
            body = (case.get("request") or {}).get("body")
            if isinstance(body, dict):
                self.assertEqual(self.check.empty_wire_findings(body), [], case.get("id"))

    def test_history_replay_covers_every_golden_with_a_message(self) -> None:
        requests = self.check.history_replay_requests()
        goldens = [p for p in sorted((ROOT / "goldens").glob("*/*.json"))
                   if (json.loads(p.read_text(encoding="utf-8")).get("canonical_response") or {}).get("message", {}).get("parts")]
        self.assertEqual(len(requests), len(goldens))
        self.assertGreater(len(requests), 400)
        doc = self.check.load_history_replay()
        ids = {f"history-replay.{gid}[{dialect}]" for gid, _ in requests for dialect in doc["dialects"]}
        for pinned in doc.get("refusals") or {}:
            self.assertIn(pinned, ids, f"refusals names {pinned}, which is not a history replay check")


if __name__ == "__main__":
    unittest.main()
