"""mapping/usage.json and the MAP-19 golden migration stay what their tools make.

Offline: no shim, no network. The harness's mapping direction checks what
the SDKs answer; these tests check that the vectors and the migrated goldens
are still the output of the tools that justify them.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import make_usage_vectors  # noqa: E402
import migrate_goldens_2026_10_31 as migration  # noqa: E402


class UsageVectorsTest(unittest.TestCase):
    def test_the_file_is_the_generator_output(self) -> None:
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "make_usage_vectors.py"), "--check"],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_expected_costs_follow_the_spec_arithmetic(self) -> None:
        # The 1.x double count would have charged the cached tokens at the
        # input rate as well: the vector exists to pin the difference.
        doc = json.loads((ROOT / "mapping" / "usage.json").read_text(encoding="utf-8"))
        cached = next(v for v in doc["estimate"] if v["id"] == "cached_history")
        self.assertEqual(cached["cost"], 10000 * 2.0 / 1_000_000 + 90000 * 0.1 / 1_000_000 + 1000 * 10.0 / 1_000_000)
        unknown = [v["id"] for v in doc["estimate"] if v["cost"] is None]
        self.assertIn("cache_read_unknown", unknown)
        self.assertIn("audio_tokens", unknown)

    def test_every_parse_vector_satisfies_inv_029(self) -> None:
        doc = json.loads((ROOT / "mapping" / "usage.json").read_text(encoding="utf-8"))
        for vector in doc["parse"]:
            with self.subTest(vector=vector["id"]):
                self.assertTrue(make_usage_vectors.inv029(vector["usage"]))


class GoldenMigrationTest(unittest.TestCase):
    def test_the_goldens_are_already_migrated(self) -> None:
        # A second run finds every golden at its MAP-19 value: nothing to change
        # and no recorded usage without a source.
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "migrate_goldens_2026_10_31.py")],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout[-2000:])
        self.assertIn("0 usage objects in 0 goldens change; 0 findings", result.stdout)

    def test_the_rule_reads_each_wire(self) -> None:
        anthropic = {"input_tokens": 3, "cache_creation_input_tokens": 3275, "cache_read_input_tokens": 0, "output_tokens": 6}
        self.assertEqual(migration.new_rule("anthropic", None, anthropic),
                         {"input_tokens": 3278, "output_tokens": 6, "total_tokens": 3284,
                          "cache_read_tokens": 0, "cache_write_tokens": 3275})
        xai = {"prompt_tokens": 254, "completion_tokens": 9, "total_tokens": 374,
               "completion_tokens_details": {"reasoning_tokens": 111}}
        self.assertEqual(migration.new_rule("openai-chat", "xai", xai)["output_tokens"], 120)
        self.assertNotIn("output_tokens", migration.new_rule("openai-chat", "openai", xai))
        gemini = {"promptTokenCount": 19, "candidatesTokenCount": 48, "thoughtsTokenCount": 155, "totalTokenCount": 222}
        self.assertEqual(migration.new_rule("gemini", None, gemini)["output_tokens"], 203)


if __name__ == "__main__":
    unittest.main()
