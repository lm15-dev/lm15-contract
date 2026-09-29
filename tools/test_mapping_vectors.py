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
                                       capture_output=True, text=True)

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


if __name__ == "__main__":
    unittest.main()
