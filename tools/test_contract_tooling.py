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
import check_provenance
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


class AuthScopeTests(unittest.TestCase):
    """D14: --auth-scope core|cloud|all partitions the auth cases by the provider's policy."""

    CLOUD_CHAIN_PROVIDERS = {  # spec/auth.md policy table rows with aws-chain / azure-chain / gcp-chain
        "azure", "azure-chat", "azure-anthropic", "aws-anthropic", "bedrock-anthropic",
        "bedrock-chat", "bedrock-mantle-chat", "vertex", "vertex-anthropic",
    }

    def run_scope(self, scope):
        shim = Mock()
        shim.call.return_value = {"ok": False, "error": {"type": "Stub", "message": "stub"}}
        report = check.run_auth_direction(shim, None, scope)
        providers = [call.kwargs["provider"] for call in shim.call.call_args_list]
        return report, providers

    def test_derived_cloud_providers_match_the_spec_policy_table(self):
        derived = check.cloud_auth_providers(check.load_auth_fixture())
        fixture_providers = {c["provider"] for c in check.load_auth_fixture()["cases"]}
        self.assertEqual(set(derived), self.CLOUD_CHAIN_PROVIDERS & fixture_providers)
        self.assertNotIn("vertex-express", derived)  # policy `key`, not gcp-chain

    def test_core_runs_the_non_cloud_cases_only(self):
        fixture = check.load_auth_fixture()
        total = len(fixture["cases"])
        core_report, core_providers = self.run_scope("core")
        cloud_report, cloud_providers = self.run_scope("cloud")
        all_report, _ = self.run_scope("all")
        self.assertTrue(core_providers)
        self.assertTrue(cloud_providers)
        self.assertFalse(set(core_providers) & self.CLOUD_CHAIN_PROVIDERS, core_providers)
        self.assertTrue(set(cloud_providers) <= self.CLOUD_CHAIN_PROVIDERS, cloud_providers)
        self.assertEqual(len(core_report.results) + len(cloud_report.results), total)
        self.assertEqual(len(all_report.results), total)
        print(f"\nauth scope: core {len(core_report.results)} / cloud {len(cloud_report.results)} / all {total}")

    def test_unknown_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            check.auth_case_in_scope({"provider": "openai"}, "everything", frozenset())


class EndProviderDataRuleTests(unittest.TestCase):
    """D9: end-event provider_data compares by presence + JSON type only."""

    START = {"type": "start", "id": "resp_1", "model": "m"}

    def events(self, provider_data=..., text="hi"):
        end = {"type": "end", "finish_reason": "stop"}
        if provider_data is not ...:
            end["provider_data"] = provider_data
        return [dict(self.START), {"type": "delta", "delta": {"type": "text", "text": text}}, end]

    def compare(self, golden, actual):
        expected, got, diff = check.end_provider_data_rule(golden, actual)
        if diff is None:
            diff = check.first_difference(expected, got, ("events",))
        return diff

    def test_content_change_is_not_a_failure(self):
        golden = self.events({"usage": {"total_tokens": 5}, "id": "chunk-1"})
        actual = self.events({"completely": "different", "nested": [1, 2, 3]})
        self.assertIsNone(self.compare(golden, actual))

    def test_dropped_field_is_caught(self):
        golden = self.events({"usage": {"total_tokens": 5}})
        diff = self.compare(golden, self.events())
        self.assertIsNotNone(diff)
        self.assertEqual(diff.path, "$.events[2].provider_data")
        self.assertIn("presence required", diff.note)

    def test_type_change_is_caught(self):
        golden = self.events({"usage": {"total_tokens": 5}})
        diff = self.compare(golden, self.events(["not", "an", "object"]))
        self.assertIsNotNone(diff)
        self.assertEqual(diff.path, "$.events[2].provider_data")
        self.assertIn("type mismatch object != array", diff.note)

    def test_absent_in_golden_ignores_shim_value(self):
        golden = self.events()
        self.assertIsNone(self.compare(golden, self.events({"anything": True})))
        self.assertIsNone(self.compare(golden, self.events()))

    def test_rule_never_widens_to_other_events_or_fields(self):
        golden = self.events({"usage": {"total_tokens": 5}})
        diff = self.compare(golden, self.events({"usage": {"total_tokens": 5}}, text="changed"))
        self.assertIsNotNone(diff)
        self.assertEqual(diff.path, "$.events[1].delta.text")
        # A start event's provider_data stays under the strict comparator.
        actual = self.events({"usage": {"total_tokens": 5}})
        actual[0]["provider_data"] = {}
        diff = self.compare(golden, actual)
        self.assertIsNotNone(diff)
        self.assertEqual(diff.path, "$.events[0].provider_data")

    def test_inputs_are_not_mutated(self):
        golden = self.events({"usage": 1})
        actual = self.events({"usage": 2})
        before = (json.dumps(golden), json.dumps(actual))
        self.compare(golden, actual)
        self.assertEqual(before, (json.dumps(golden), json.dumps(actual)))


class ProvenanceTests(unittest.TestCase):
    """D11 (exchange receipts from 2026-09-06) and D12 (reviewed line shape)."""

    def run_checker(self, root):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = check_provenance.main(["--root", str(root)])
        return result, output.getvalue()

    def write_case(self, root, name, provenance):
        (root / "cases" / "x").mkdir(parents=True, exist_ok=True)
        (root / "cases" / "x" / f"{name}.json").write_text(json.dumps({"id": f"x.{name}", "provenance": provenance}))

    def write_receipt(self, root, rel, payload):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload) if not isinstance(payload, str) else payload)

    def test_live_capture_from_cutoff_requires_a_hashed_exchange_receipt(self):
        receipt = {"request_sha256": "a" * 64, "response_sha256": "b" * 64}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rel = "receipts/2026-09-06-x/exchange-1.json"
            self.write_receipt(root, rel, receipt)
            self.write_case(root, "ok", {"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": rel})
            self.write_case(root, "later", {"source": "live-capture", "date": "2026-10-01", "evidence": "e", "exchange": rel})
            self.write_case(root, "old", {"source": "live-capture", "date": "2026-09-05", "evidence": "e"})
            self.write_case(root, "hand", {"source": "hand-authored", "date": "2026-09-07", "evidence": "e"})
            result, output = self.run_checker(root)
            self.assertEqual(result, 0, output)

    def test_live_capture_from_cutoff_failures(self):
        good = {"request_sha256": "a" * 64, "response_sha256": "b" * 64}
        failing = {
            "missing": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e"}, None, "lacks provenance.exchange"),
            "empty": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": ""}, None, "lacks provenance.exchange"),
            "absent-file": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": "receipts/none.json"}, None, "does not exist"),
            "absolute": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": "/etc/hostname"}, None, "relative path"),
            "traversal": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": "../outside.json"}, None, "relative path"),
            "not-json": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": "receipts/r.json"}, "not json", "unreadable JSON"),
            "not-object": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": "receipts/r.json"}, [1], "not a JSON object"),
            "no-request-hash": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": "receipts/r.json"}, {"response_sha256": "b" * 64}, "non-empty request_sha256"),
            "empty-response-hash": ({"source": "live-capture", "date": "2026-09-06", "evidence": "e", "exchange": "receipts/r.json"}, {**good, "response_sha256": ""}, "non-empty response_sha256"),
        }
        for name, (provenance, receipt, message) in failing.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                if receipt is not None:
                    self.write_receipt(root, "receipts/r.json", receipt)
                self.write_case(root, name, provenance)
                result, output = self.run_checker(root)
                self.assertEqual(result, 1, output)
                self.assertIn(message, output)

    def test_exchange_rule_applies_to_cases_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "errors").mkdir()
            (root / "errors" / "e.json").write_text(json.dumps({"provenance": {"source": "live-capture", "date": "2026-09-06", "evidence": "e"}}))
            result, output = self.run_checker(root)
            self.assertEqual(result, 0, output)

    def write_golden(self, root, name, provenance):
        (root / "goldens" / "p").mkdir(parents=True, exist_ok=True)
        (root / "goldens" / "p" / f"{name}.json").write_text(json.dumps({"canonical_response": {}, "provenance": provenance}))

    def test_reviewed_line_shape(self):
        base = {"source": "scribe-draft", "date": "2026-09-06", "evidence": "e"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_golden(root, "unreviewed", base)
            self.write_golden(root, "reviewed", {**base, "reviewed": "2026-09-06 reviewed by Maxime Rivest against the pinned body."})
            result, output = self.run_checker(root)
            self.assertEqual(result, 0, output)
        for name, reviewed in {"empty": "", "blank": "  ", "no-date": "reviewed 2026-09-06 by M.",
                               "bool": True, "null": None, "short": "2026-09"}.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_golden(root, name, {**base, "reviewed": reviewed})
                result, output = self.run_checker(root)
                self.assertEqual(result, 1, output)
                self.assertIn("D12", output)


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
