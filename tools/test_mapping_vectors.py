"""mapping/gemini-schema-field.json against the receipts it was read from.

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


if __name__ == "__main__":
    unittest.main()
