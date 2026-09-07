"""Offline checks for live-probe construction; no credentials or network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import media_tool_results as probe


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.calls = [{"id": "id_b", "name": "fetch_panel", "args": {"label": "B"}},
                      {"id": "id_a", "name": "fetch_panel", "args": {"label": "A"}}]
        self.expected = {"A": list(probe.COLORS), "B": list(reversed(probe.COLORS))}
        self.outputs = probe.outputs_for("pair", self.expected, {"A": "AAA", "B": "BBB"})

    def test_registry_coverage(self):
        self.assertEqual(set(probe.MODELS), set(probe.PROVIDERS))

    def test_chat_association_and_image_only_vs_mixed(self):
        turn = {"role": "assistant", "content": None, "reasoning_content": "opaque", "tool_calls": []}
        first = {"messages": [{"role": "user", "content": "request"}], "model": "test"}
        body = probe.followup("openai-chat", first, turn, self.calls, self.outputs)
        self.assertEqual(first["messages"], [{"role": "user", "content": "request"}])
        self.assertEqual(body["messages"][1], turn)
        b, a = body["messages"][2:]
        self.assertEqual((b["tool_call_id"], [p["type"] for p in b["content"]]), ("id_b", ["text", "image_url"]))
        self.assertEqual((a["tool_call_id"], len(a["content"])), ("id_a", 1))
        self.assertTrue(a["content"][0]["image_url"]["url"].endswith("AAA"))

    def test_responses_replays_every_item(self):
        turn = [{"type": "reasoning", "encrypted_content": "opaque"}, {"type": "function_call", "call_id": "id_a"}]
        body = probe.followup("openai-responses", {"input": []}, turn, self.calls, self.outputs)
        self.assertEqual(body["input"][:2], turn)
        self.assertEqual(body["input"][2]["call_id"], "id_b")
        self.assertEqual([p["type"] for p in body["input"][3]["output"]], ["input_image"])

    def test_anthropic_results_follow_whole_assistant_turn_and_error_flag(self):
        turn = {"role": "assistant", "content": [{"type": "thinking", "signature": "opaque"}]}
        body = probe.followup("anthropic", {"messages": []}, turn, self.calls, self.outputs)
        self.assertEqual(body["messages"][0], turn)
        parts = body["messages"][1]["content"]
        self.assertEqual(parts[0]["tool_use_id"], "id_b")
        self.assertEqual(parts[1]["content"][0]["source"]["data"], "AAA")
        err = probe.tool_result("anthropic", self.calls[1], [{"kind": "text", "text": "boom"}], True)
        self.assertTrue(err["is_error"])

    def test_gemini_nested_media_error_key_and_no_fabricated_id(self):
        turn = {"role": "model", "parts": [{"thoughtSignature": "opaque", "functionCall": {"name": "fetch_panel"}}]}
        self.calls[0]["id"] = None
        body = probe.followup("gemini", {"contents": []}, turn, self.calls, self.outputs)
        self.assertEqual(body["contents"][0], turn)
        b, a = [p["functionResponse"] for p in body["contents"][1]["parts"]]
        self.assertNotIn("id", b)
        self.assertEqual(b["response"]["result"], probe.TOOL_TEXT)
        self.assertEqual(a["response"], {})
        self.assertEqual((a["id"], a["parts"][0]["inlineData"]["data"]), ("id_a", "AAA"))
        err = probe.tool_result("gemini", self.calls[1], [{"kind": "text", "text": "boom"}], True)["functionResponse"]
        self.assertEqual(err["response"], {"error": "boom"})

    def test_pdf_cell_builds_document_blocks(self):
        parts = probe.outputs_for("pdf", self.expected, {"A": "UERG", "B": ""})["A"][0]
        self.assertEqual(probe.wire_parts("openai-responses", parts)[0]["type"], "input_file")
        self.assertEqual(probe.wire_parts("anthropic", parts)[0]["type"], "document")
        self.assertEqual(probe.wire_parts("gemini", parts)[0]["inlineData"]["mimeType"], "application/pdf")
        data = probe.pdf(list(probe.COLORS))
        self.assertTrue(data.startswith(b"%PDF-1.4") and b"red green blue" in data)

    def test_no_invented_tool_turn(self):
        with self.assertRaises(ValueError):
            probe.conversation("openai-chat", {"choices": [{"message": {"content": "no tool"}}]}, {"A"})

    def test_terminal_sse(self):
        data = {"type": "response.completed", "response": {"output": []}}
        self.assertEqual(probe.decode_body(("data: " + json.dumps(data) + "\n\ndata: [DONE]\n").encode()), {"output": []})
        with self.assertRaises(ValueError):
            probe.decode_body(b"data: [DONE]\n")

    def test_png_and_judge(self):
        data = probe.panel(list(probe.COLORS))
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertNotIn(b"tEXt", data)
        self.assertEqual(probe.answer_json('```json\n{"A":[],"B":[]}\n```'), {"A": [], "B": []})
        self.assertIsNone(probe.answer_json('{"B":[]}'))
        self.assertEqual(probe.judge("image", {"A": self.expected["A"]}, self.expected), "content_received")
        self.assertEqual(probe.judge("pair", {"A": self.expected["A"], "B": []}, self.expected), "accepted_but_content_not_received")
        self.assertEqual(probe.judge("error", {"A": None, "note": "503"}, self.expected), "error_acknowledged")
        self.assertEqual(probe.judge("error", {"A": ["red"] * 6}, self.expected), "error_ignored_colors_fabricated")

    def test_public_placeholder_is_not_a_secret(self):
        cap = probe.ProbeCapture("ollama", env_var="UNSET_CAPTURE_TEST_KEY", default_model="test", host="test")
        probe.register_header_secrets(cap, [("authorization", "Bearer ollama")], "ollama")
        self.assertEqual(cap.redact('provider="ollama"'), 'provider="ollama"')
        probe.register_header_secrets(cap, [("authorization", "Bearer private-value")], "ollama")
        self.assertNotIn("private-value", cap.redact("Bearer private-value"))
        probe.register_header_secrets(cap, [("authorization", "AWS4-HMAC-SHA256 Credential=example-access-id/20260907/region/bedrock/aws4_request, Signature=example")])
        self.assertNotIn("example-access-id", cap.redact("error echoed example-access-id"))
        cap.transport.close()

    def test_append_only_and_secret_echo_redaction(self):
        with tempfile.TemporaryDirectory() as folder:
            cap = probe.ProbeCapture("openai", env_var="UNSET_CAPTURE_TEST_KEY", default_model="test", host="test")
            cap.receipts = Path(folder)
            cap._secret_values.add("test-secret-sentinel")
            cap.write_receipt("one.json", {"body": "test-secret-sentinel"})
            self.assertNotIn("test-secret-sentinel", (Path(folder) / "one.json").read_text())
            with self.assertRaises(FileExistsError):
                cap.write_receipt("one.json", {})
            cap.transport.close()


if __name__ == "__main__":
    unittest.main()
