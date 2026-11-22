"""Offline tests of the audit guards themselves, including negative controls."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "harness"))
import audit
import check
import check_provenance as provenance


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.body = self.root / "bodies/example/body.json"
        self.body.parent.mkdir(parents=True)
        self.body.write_bytes(b'{"answer":42}')
        self.receipt = self.root / "receipt.json"
        self.receipt.write_text(json.dumps({"request_sha256": sha(b"request"), "response_sha256": sha(self.body.read_bytes())}), encoding="utf-8")
        self.block = {"source": "live-capture", "date": "2026-11-22", "exchange": "receipt.json"}
        self.case = {"id": "example", "pinned_body": "body.json"}

    def check(self, allow=None):
        problems, used = [], set()
        provenance.check_exchange(self.case, self.block, "case", self.root, problems, allow or {}, used)
        return problems, used

    def test_exact_and_single_newline_only(self):
        self.assertEqual(self.check()[0], [])
        raw = self.body.read_bytes()
        self.body.write_bytes(raw + b"\n")
        self.assertEqual(self.check()[0], [])
        self.body.write_bytes(raw + b"\n\n")
        self.assertTrue(self.check()[0])
        self.body.write_bytes(b'{"answer":43}')
        self.assertTrue(self.check()[0])

    def test_separate_response_exchange_is_used_and_checked(self):
        self.block["response_exchange"] = "response.json"
        self.assertTrue(self.check()[0])
        (self.root / "response.json").write_text(self.receipt.read_text(encoding="utf-8"), encoding="utf-8")
        self.receipt.write_text(json.dumps({"request_sha256": sha(b"request"), "response_sha256": sha(b"other")}), encoding="utf-8")
        self.assertEqual(self.check()[0], [])
        self.block["response_exchange"] = "../outside.json"
        self.assertTrue(self.check()[0])

    def test_redaction_exception_pins_both_hashes(self):
        original_sha = sha(self.body.read_bytes())
        self.body.write_bytes(b'{"answer":"redacted"}')
        allow = {"example": {"body_sha256": sha(self.body.read_bytes()), "receipt_sha256": original_sha}}
        self.assertEqual(self.check(allow), ([], {"example"}))
        self.body.write_bytes(b'{"answer":"changed"}')
        self.assertTrue(self.check(allow)[0])
        allow["example"]["body_sha256"] = sha(self.body.read_bytes())
        allow["example"]["receipt_sha256"] = sha(b"other receipt")
        self.assertTrue(self.check(allow)[0])


class ReviewRatchetTests(unittest.TestCase):
    def test_new_unreviewed_and_stale_entries_and_missing_registry_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tools").mkdir()
            (root / provenance.RECEIPT_ALLOWLIST_REL).write_text('{"cases":{}}', encoding="utf-8")
            ratchet = root / provenance.UNREVIEWED_RATCHET_REL
            ratchet.write_text('{"unreviewed":[]}', encoding="utf-8")
            (root / "goldens").mkdir()
            golden = root / "goldens/example.json"
            golden.write_text(json.dumps({"provenance": {"source": "scribe-draft", "date": "2026-11-22", "evidence": "pending independent review"}}), encoding="utf-8")
            def run():
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    return provenance.main(["--root", str(root)])
            self.assertNotEqual(run(), 0)
            ratchet.write_text('{"unreviewed":["goldens/example.json"]}', encoding="utf-8")
            self.assertEqual(run(), 0)
            golden.unlink()
            self.assertNotEqual(run(), 0)
            ratchet.unlink()
            self.assertNotEqual(run(), 0)


class ValidationTests(unittest.TestCase):
    def test_only_validation_rejections_pass(self):
        case = {"id": "invalid", "kind": "config", "value": {"max_tokens": False}}
        replies = [
            ({"ok": False, "error": {"type": "ValueError", "message": "invalid"}}, "pass"),
            ({"ok": False, "error": {"type": "TypeError", "message": "invalid"}}, "pass"),
            ({"ok": False, "error": {"type": "RuntimeError", "message": "crashed"}}, "fail"),
            ({"ok": False}, "fail"),
            ({}, "fail"),
            ({"ok": True, "result": {}}, "fail"),
        ]
        with patch.object(check, "load_serde_cases", return_value=[]), patch.object(check, "load_serde_reject_cases", return_value=[case]):
            for reply, status in replies:
                with self.subTest(reply=reply):
                    shim = Mock()
                    shim.call.return_value = reply
                    report = check.run_serde_direction(shim, None, ROOT)
                    self.assertEqual(report.results[0].status, status)

    def test_required_fixture_cannot_disappear_silently(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.json"
            for attribute, loader in [("SERDE_REJECT_FILE", check.load_serde_reject_cases), ("AUTH_NAMED_FILE", check.load_auth_named_fixture)]:
                with patch.object(check, attribute, missing), self.assertRaises(FileNotFoundError):
                    loader()


class StrictAuditTests(unittest.TestCase):
    def test_missing_reference_fails_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(audit.main(["--python2", directory, "--require-reference"]), 0)

    def test_refusal_without_receipt_is_reported(self):
        case = {"id": "test", "provenance": {"source": "live-capture", "evidence": "no receipt: hypothesis"}, "expect_lm15": {"raises": {"op": "build_request"}}}
        problems = []
        audit.check_refusal_receipts(ROOT, [(ROOT / "cases/test.json", case)], ROOT.parent / "lm15-python", problems)
        self.assertTrue(any("unreceipted guess" in p for p in problems))
        self.assertTrue(any("no existing receipt" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
