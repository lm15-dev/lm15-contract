"""Golden ownership follows declared provider/feature, never directory spelling."""
import json
from pathlib import Path
import tempfile
import unittest

import audit


class GoldenLinksTests(unittest.TestCase):
    def test_active_link_stale_body_and_retirement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "goldens/door/model.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"provenance": {"pinned_body": "current.txt"}}), encoding="utf-8")
            owner = {"provider": "door", "feature": "model", "pinned_body": "current.txt"}
            cases = [(root / "cases/different-folder/another-name.json", owner)]
            problems = []
            audit.check_golden_links(root, cases, problems)
            self.assertEqual(problems, [])
            owner["pinned_body"] = "newer.txt"
            audit.check_golden_links(root, cases, problems)
            self.assertIn("differs", problems[0])
            problems = []
            audit.check_golden_links(root, [], problems)
            self.assertIn("no active case", problems[0])

    def test_shared_golden_can_have_refusal_and_response_owners(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "goldens/p/f.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"provenance":{"pinned_body":"body.txt"}}', encoding="utf-8")
            cases = [(root / "case.json", {"provider": "p", "feature": "f"}),
                     (root / "other.json", {"provider": "p", "feature": "f", "pinned_body": "body.txt"})]
            problems = []
            audit.check_golden_links(root, cases, problems)
            self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
