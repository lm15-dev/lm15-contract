"""Offline regression tests for corpus tooling; no credentials or provider calls."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "tools"))
import check
import audit
import check_secrecy


class HarnessFilesTests(unittest.TestCase):
    def test_file_expansion_is_confined(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "contract"
            root.mkdir()
            (root / "vector.txt").write_text("# test comment\nfixture\n")
            (root / "escape").symlink_to(Path(directory) / "outside.txt")
            with patch.object(check, "CONTRACT_ROOT", root):
                self.assertEqual(check.expand_files({"$file": "vector.txt", "strip_comment_lines": True}), "fixture\n")
                for path in ("../outside.txt", str(root / "vector.txt"), "escape", ".env", "lab.env", ".env.local"):
                    with self.subTest(path=path), self.assertRaises(ValueError):
                        check.expand_files({"$file": path})

    def test_auth_materialization_rejects_escape(self):
        for path in ("/outside.txt", "relative.txt", "~/../../outside.txt"):
            fixture = {"sentinel": "fixture", "cases": [{
                "id": "sandbox-test", "provider": "azure", "env": {}, "files": {path: "fixture"},
            }]}
            shim = Mock()
            with self.subTest(path=path), patch.object(check, "load_auth_fixture", return_value=fixture):
                with self.assertRaises(ValueError):
                    check.run_auth_direction(shim, None)
                shim.call.assert_not_called()


class SecrecyTests(unittest.TestCase):
    def scan(self, root):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = check_secrecy.main(["--root", str(root)])
        return result, output.getvalue()

    def test_jsonl_is_scanned_without_echoing_material(self):
        token = "ya29." + "x" * 40
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "transcript.jsonl").write_text(json.dumps({"frame": token}))
            result, output = self.scan(root)
        self.assertEqual(result, 1)
        self.assertIn("google access token", output)
        self.assertNotIn(token, output)

    def test_allowed_path_does_not_allow_replacement_jwt(self):
        token = "eyJ" + "a" * 20 + "." + "b" * 20 + "." + "c" * 30
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "auth").mkdir()
            (root / "auth" / "token-vectors.json").write_text(json.dumps({"token": token}))
            result, output = self.scan(root)
        self.assertEqual(result, 1)
        self.assertIn("signed jwt", output)
        self.assertNotIn(token, output)

    def test_example_suffix_is_not_a_blanket_aws_exemption(self):
        pattern = dict(check_secrecy.LIVE_SECRET_PATTERNS)["aws access key id"]
        self.assertIsNone(pattern.search("AKIAIOSFODNN7EXAMPLE"))
        self.assertIsNotNone(pattern.search("ASIA" + "A" * 9 + "EXAMPLE"))

    def test_test_id_prefix_does_not_exempt_bedrock_tokens(self):
        pattern = dict(check_secrecy.LIVE_SECRET_PATTERNS)["bedrock api key"]
        self.assertIsNotNone(pattern.search("bedrock-api-key-" + "A" * 130))


class AuditTests(unittest.TestCase):
    def test_policy_vocab_is_checked_not_blindly_exempted(self):
        surface = {"types": {}, "enums": {"StreamFraming": ["sse", "invented-framing"]}}
        problems = []
        with patch.object(audit, "shim_surface_dump", return_value=(surface, "")):
            summary = audit.check_surface_coverage(ROOT, ROOT.parent / "lm15-python", problems)
        self.assertTrue(any("StreamFraming differs" in problem for problem in problems))
        self.assertIn("not serde/runtime coverage", summary)


@unittest.skipUnless((ROOT.parent / "lm15-python" / "lm15").is_dir(), "capture tests require read-only Python sibling")
class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "research" / "providers"))
        import _capture
        cls.capture = _capture

    def test_dry_run_entry_points_do_not_resolve_send_or_write(self):
        from lm15.cloud import chains
        from lm15.transports import StdlibTransport
        scripts = {
            "azure": "basic_text,files,batch,headers,services-host",
            "azure-chat": "basic_text,headers",
            "azure-anthropic": "basic_text,headers,beta",
            "bedrock-chat": "basic_text",
            "bedrock-anthropic": "basic_text",
            "bedrock-mantle-chat": "basic_text,models,refusals,family",
        }
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            with patch.object(self.capture, "CONTRACT", sandbox), \
                 patch.dict(os.environ, {"HOME": directory, "PATH": "/no-executables"}, clear=True), \
                 patch.object(chains, "resolve", side_effect=AssertionError("credential resolution attempted")), \
                 patch.object(StdlibTransport, "stream", side_effect=AssertionError("network attempted")), \
                 patch("subprocess.run", side_effect=AssertionError("subprocess attempted")), \
                 patch.object(self.capture.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                for provider, features in scripts.items():
                    script = ROOT / "research" / "providers" / provider / "capture.py"
                    with self.subTest(provider=provider), patch.object(sys, "argv", [str(script), "--dry-run", "--force", "--only", features]):
                        runpy.run_path(str(script), run_name="__main__")
                self.assertEqual(list(sandbox.iterdir()), [])

    def test_live_only_scripts_refuse_dry_run_before_credentials(self):
        from lm15.cloud import chains
        import _azure
        scripts = ("bedrock-chat/bearer_probes.py", "bedrock-chat/mantle_chat_probes.py", "azure/capture_live.py")
        with patch.object(chains, "resolve", side_effect=AssertionError("credential resolution attempted")), \
             patch.object(_azure, "load_lab_env", side_effect=AssertionError("lab credentials accessed")), \
             patch("subprocess.run", side_effect=AssertionError("subprocess attempted")), \
             contextlib.redirect_stdout(io.StringIO()):
            for relative in scripts:
                script = ROOT / "research" / "providers" / relative
                with self.subTest(script=relative), patch.object(sys, "argv", [str(script), "--dry-run"]):
                    with self.assertRaises(SystemExit) as result:
                        runpy.run_path(str(script), run_name="__main__")
                    self.assertEqual(result.exception.code, 2)

    def test_shared_change_entry_slug(self):
        cap = self.capture.Capture("meta-chat", env_var="UNUSED_TEST_KEY", default_model="test", host="example.invalid", change_slug="meta-live")
        self.assertEqual(cap.change_entry, f"changes/{cap.date}-meta-live.md")

    def test_failed_models_capture_does_not_pin_a_case(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(self.capture, "CONTRACT", Path(directory)):
            cap = self.capture.Capture("meta-chat", env_var="UNUSED_TEST_KEY", default_model="test", host="example.invalid")
            cap.lm = Mock()
            cap.send = Mock(return_value=(404, b'{"error":"no listing"}', "2026-09-04T00-00-00Z", {}))
            result = cap.models_case(force=True)
            self.assertEqual(result["status"], 404)
            self.assertFalse((Path(directory) / "cases").exists())
            self.assertFalse((Path(directory) / "bodies").exists())
            self.assertEqual(len(list(cap.receipts.glob("failed-models-*"))), 1)

    def test_probe_redacts_before_truncating_an_echoed_credential(self):
        from lm15 import Message, Request
        secret = "fixture-only-long-value-" * 30
        cap = self.capture.Capture("azure", env_var="UNUSED_TEST_KEY", default_model="test", host="example.invalid")
        cap._secret_values.add(secret)
        cap.lm = Mock()
        cap.send = Mock(return_value=(401, json.dumps({"error": {"message": secret}}).encode(), "2026-09-04T00-00-00Z", {}))
        cap.wire_block = Mock(return_value={})
        cap.write_receipt = Mock()
        with patch.object(self.capture.time, "sleep"):
            row = cap.probe("echo", Request(model="test", messages=(Message.user("test"),)))
        self.assertNotIn("fixture-only-long-value", row["summary"])
        self.assertIn("$UNUSED_TEST_KEY", row["summary"])

    def test_exchange_hashes_actual_request_and_raw_response(self):
        request = SimpleNamespace(method="POST", url="https://example.invalid/path?key=fixture-value",
                                  headers=[("authorization", "Bearer fixture-value")], body=b"{}")
        response = SimpleNamespace(status=200, headers={}, read=lambda: b"verbatim body\n")
        with tempfile.TemporaryDirectory() as directory, patch.object(self.capture, "CONTRACT", Path(directory)):
            cap = self.capture.Capture("azure", env_var="UNUSED_TEST_KEY", default_model="test", host="example.invalid")
            cap.transport = Mock()
            cap.transport.stream.return_value = contextlib.nullcontext(response)
            for _ in range(2):
                cap.send(request)
            receipts = list(cap.receipts.glob("exchange-*.json"))
            self.assertEqual(len(receipts), 2)
            text = receipts[0].read_text()
            self.assertNotIn("fixture-value", text)
            receipt = json.loads(text)
            hashed = {"method": request.method, "url": request.url, "headers": request.headers, "body_b64": "e30="}
            self.assertEqual(receipt["request_sha256"], hashlib.sha256(json.dumps(hashed, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest())
            self.assertEqual(receipt["response_sha256"], hashlib.sha256(b"verbatim body\n").hexdigest())

    def test_sigv4_capture_cannot_pin_a_bearer_call_as_aws(self):
        from lm15.cloud import chains
        from lm15.credentials import BearerToken
        cap = self.capture.Capture("bedrock-chat", env_var="UNUSED_TEST_KEY", default_model="test", host="example.invalid", settings={"region": "us-east-1"})
        with patch.object(chains.ChainContext, "online"), patch.object(chains, "resolve", return_value=BearerToken("fixture-value")):
            with self.assertRaisesRegex(ValueError, "SigV4 capture requires AWS credentials"):
                cap.aws_fixture()

    def test_dry_run_receipt_writer_is_a_noop(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(self.capture, "CONTRACT", Path(directory)):
            cap = self.capture.Capture("azure", env_var="UNUSED_TEST_KEY", default_model="test", host="example.invalid")
            cap.dry_run = True
            cap.write_receipt("probe.json", {"test": True})
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
