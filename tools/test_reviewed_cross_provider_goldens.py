"""Seven saved-wire/spec reviews; deliberately no SDK imports or scribe calls.

This is a scoped, reproducible derivation, not a general provider implementation.
See goldens/REVIEW-2026-11-22-cross-provider.md for decisions and limitations.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = {
    "xai/structured_output": "cda57801f9c23948a76526ae8a34a26a756970f65ad08da19f255e05bef1e211",
    "gemini/streaming_parallel_tool_calls_chunked": "594627359d5d487635505d152bef0e22da8caf1b503fdb828f8627add38aa820",
    "openai_chat/tool_call_unnamed": "8a48b565e2db84f5851f3693ba07dee81aa53824b10b6b2d319a9ed7b2f8e5fe",
    "openai-codex/streaming_parallel_tool_calls": "8cb155e1712dcd7b5dacb21407386960e9d29bbe65bfad3a1ef4be15663f516f",
    "tinker/reasoning_effort_switch": "ccf10dd206ee525e7e17e85f8495abb92f8b3b46d58da0116b914c366708df9a",
    "tinker/response_format_json_schema": "7e140a95294af4ed657a2e69e4f59aefb502e3590d1cee4da41241217fce0bd6",
    "gemini/live_tool_no_description": "f07bc29c4e0e14167e7d1467201bb99cc6183824302931a0341b23fb6cf94985",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def delta(event_type, **fields):
    return {"type": "delta", "delta": {"type": event_type, **fields}}


def response(model, parts, usage, finish="stop", identity=None):
    return {**({"id": identity} if identity is not None else {}), "model": model,
            "message": {"role": "assistant", "parts": parts}, "finish_reason": finish, "usage": usage}


def sse(raw):
    return [json.loads(line[5:].strip()) for line in raw.decode().splitlines()
            if line.startswith("data:") and line[5:].strip() != "[DONE]"]


class CrossProviderGoldenReview(unittest.TestCase):
    def source(self, name):
        case = read(ROOT / "cases" / f"{name}.json")
        golden = read(ROOT / "goldens" / f"{name}.json")
        self.assertEqual(case["pinned_body"], golden["provenance"]["pinned_body"])
        raw = (ROOT / "bodies" / case["id"] / case["pinned_body"]).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(sha, SNAPSHOTS[name])
        prov = case["provenance"]
        receipt_path = prov.get("response_exchange") or prov.get("exchange")
        if receipt_path:
            receipt = read(ROOT / receipt_path)
            expected = receipt["response_sha256"]
            if sha != expected and not (raw.endswith(b"\n") and hashlib.sha256(raw[:-1]).hexdigest() == expected):
                exception = read(ROOT / "tools/receipt-hash-allowlist.json")["cases"][case["id"]]
                self.assertEqual((sha, expected), (exception["body_sha256"], exception["receipt_sha256"]))
        return case, raw

    def derive(self, name):
        case, raw = self.source(name)
        if name.startswith(("xai/", "tinker/")):
            wire = json.loads(raw)
            message = wire["choices"][0]["message"]
            self.assertEqual(wire["choices"][0]["finish_reason"], "stop")
            parts = [{"type": "thinking", "text": message["reasoning_content"]}, {"type": "text", "text": message["content"]}]
            u = wire["usage"]
            if name.startswith("xai/"):
                self.assertEqual((u["prompt_tokens"], u["completion_tokens"], u["completion_tokens_details"]["reasoning_tokens"]), (254, 9, 111))
                usage = {"input_tokens": 254, "output_tokens": 9 + 111, "total_tokens": 374, "cache_read_tokens": 192,
                         "reasoning_tokens": 111, "input_audio_tokens": 0, "output_audio_tokens": 0}
                self.assertEqual(u["prompt_tokens_details"]["cached_tokens"], 192)
                self.assertEqual(u["prompt_tokens_details"]["audio_tokens"], 0)
                self.assertEqual(u["completion_tokens_details"]["audio_tokens"], 0)
            else:
                prompt, output = (13, 143) if name.endswith("reasoning_effort_switch") else (21, 192)
                self.assertEqual((u["prompt_tokens"], u["completion_tokens"]), (prompt, output))
                self.assertEqual(u["prompt_tokens_details"]["cached_tokens"], 0)
                usage = {"input_tokens": prompt, "output_tokens": output, "total_tokens": prompt + output, "cache_read_tokens": 0}
            self.assertEqual(usage["total_tokens"], u["total_tokens"])
            return {"canonical_response": response(wire["model"], parts, usage, identity=wire["id"])}
        if name == "gemini/live_tool_no_description":
            frames = [json.loads(base64.b64decode(e["frame_b64"])) for e in map(json.loads, raw.decode().splitlines()) if e["dir"] == "server"]
            self.assertEqual(frames[:2], [{"setupComplete": {}}, {"serverContent": {}}])
            call, = frames[2]["toolCall"]["functionCalls"]
            self.assertEqual((call["name"], call["id"], call["args"]), ("get_weather", "fc_2902157236849646253", {"city": "Montreal"}))
            return {"events": [[], [], [{"type": "tool_call", "id": call["id"], "name": call["name"], "input": call["args"]}]]}
        frames = sse(raw)
        model = case["canonical_request"]["model"]
        if name.startswith("gemini/"):
            self.assertEqual(len(frames), 2)
            parts, events = [], [{"type": "start", "model": model}]
            for index, frame in enumerate(frames):
                part, = frame["candidates"][0]["content"]["parts"]
                call = part["functionCall"]
                self.assertEqual(call, {"name": "get_weather", "args": {"city": ["Paris", "Oslo"][index]}})
                canonical = {"type": "tool_call", "id": f"tool_call_{index}", "name": call["name"], "input": call["args"]}
                events.append(delta("tool_call", part_index=index, input=json.dumps(call["args"], separators=(",", ":")), name=call["name"]))
                if "thoughtSignature" in part:
                    state = {"provider": "gemini", "kind": "thought_signature", "data": {"value": part["thoughtSignature"]}}
                    canonical["continuation"] = [state]
                    events.append(delta("continuation", part_index=index, **state))
                parts.append(canonical)
            self.assertEqual(frames[-1]["candidates"][0]["finishReason"], "STOP")
            u = frames[-1]["usageMetadata"]
            self.assertEqual((u["promptTokenCount"], u["candidatesTokenCount"], u["thoughtsTokenCount"], u["totalTokenCount"]), (60, 31, 328, 419))
            usage = {"input_tokens": 60, "output_tokens": 31 + 328, "total_tokens": 419, "cache_read_tokens": 0, "reasoning_tokens": 328}
            events.append({"type": "end", "finish_reason": "tool_call", "usage": usage, "provider_data": frames[-1]})
            return {"canonical_response": response(model, parts, usage, "tool_call"), "events": events}
        if name.startswith("openai_chat/"):
            events = [{"type": "start", "model": model}]
            text = ""
            for frame in frames:
                for choice in frame["choices"]:
                    d = choice["delta"]
                    if d.get("content"):
                        text += d["content"]
                        events.append(delta("text", part_index=0, text=d["content"]))
                    for call in d.get("tool_calls", []):
                        self.assertNotIn("name", call["function"])
                        fields = {"part_index": call["index"], "input": call["function"]["arguments"]}
                        if "id" in call:
                            fields["id"] = call["id"]
                        events.append(delta("tool_call", **fields))
            self.assertEqual(text, "Checking.")
            self.assertEqual(frames[-2]["choices"][0]["finish_reason"], "tool_calls")
            self.assertEqual(frames[-1]["usage"], {"prompt_tokens": 48, "completion_tokens": 11, "total_tokens": 59})
            usage = {"input_tokens": 48, "output_tokens": 11, "total_tokens": 59}
            events.append({"type": "end", "finish_reason": "tool_call", "usage": usage, "provider_data": frames[-1]})
            self.assertEqual(case["expect_lm15"]["raises"], {"op": "replay_stream", "type": "StreamAssemblyError", "code": "stream_assembly"})
            return {"partial_response": response(model, [{"type": "text", "text": text}], usage, "tool_call"), "events": events}
        # This Codex recording has no argument fragments; only item final copies
        # supply them. The other 'done' event and completed.output are duplicates.
        self.assertEqual(name, "openai-codex/streaming_parallel_tool_calls")
        self.assertFalse(any(f["type"] == "response.function_call_arguments.delta" for f in frames))
        start = frames[0]["response"]
        final = frames[-1]["response"]
        events = [{"type": "start", "id": start["id"], "model": start["model"]}]
        parts = []
        for frame in frames:
            if frame["type"] in {"response.output_item.added", "response.output_item.done"}:
                item = frame["item"]
                self.assertEqual(item["type"], "function_call")
                events.append(delta("tool_call", part_index=frame["output_index"], input=item["arguments"], id=item["call_id"], name=item["name"]))
                if frame["type"] == "response.output_item.done":
                    parts.append({"type": "tool_call", "id": item["call_id"], "name": item["name"], "input": json.loads(item["arguments"])})
        self.assertEqual([p["input"] for p in parts], [{"city": "Paris"}, {"city": "Oslo"}])
        self.assertEqual([p["id"] for p in parts], [p["call_id"] for p in final["output"]])
        self.assertEqual(final["status"], "completed")
        self.assertEqual(final["usage"]["input_tokens"], 74)
        self.assertEqual(final["usage"]["output_tokens"], 49)
        self.assertEqual(final["usage"]["total_tokens"], 123)
        self.assertEqual(final["usage"]["input_tokens_details"], {"cached_tokens": 0, "cache_write_tokens": 0})
        self.assertEqual(final["usage"]["output_tokens_details"], {"reasoning_tokens": 0})
        usage = {"input_tokens": 74, "output_tokens": 49, "total_tokens": 123, "cache_read_tokens": 0, "cache_write_tokens": 0, "reasoning_tokens": 0}
        events.append({"type": "end", "finish_reason": "tool_call", "usage": usage, "provider_data": final})
        return {"canonical_response": response(start["model"], parts, usage, "tool_call", start["id"]), "events": events}

    def verify(self, name, golden):
        # Also distinguish canonical 0 from 0.0; dict equality would not.
        self.assertEqual(json.dumps(golden, sort_keys=True), json.dumps(self.derive(name), sort_keys=True))

    def test_entire_reviewed_projections(self):
        for name in SNAPSHOTS:
            with self.subTest(case=name):
                golden = read(ROOT / "goldens" / f"{name}.json")
                golden.pop("provenance")
                self.verify(name, golden)

    def test_tinker_adaptation_evidence_is_not_just_the_adapted_request(self):
        survey = ROOT / "receipts/2026-11-09-tinker-survey"
        rejected = read(survey / "probe-reasoning-oai-Qwen-Qwen3.5-4B-high.json")
        self.assertEqual(rejected["status"], 400)
        self.assertEqual(rejected["sent"]["body"]["reasoning_effort"], "high")
        self.assertIn("accepts true or false", rejected["body"]["detail"])
        schema = read(survey / "probe-json-schema.json")
        self.assertEqual(schema["status"], 200)
        self.assertIn("response_format", schema["sent"]["body"])
        with self.assertRaises(ValueError):
            json.loads(schema["body"]["choices"][0]["message"]["content"])
        for name, field, action in [("reasoning_effort_switch", "config.reasoning.effort", "substituted"), ("response_format_json_schema", "config.response_format", "dropped")]:
            case = read(ROOT / "cases/tinker" / f"{name}.json")
            expected = {"field": field, "action": action, "asked": "high", "applied": "on"} if action == "substituted" else {"field": field, "action": action, "asked": case["canonical_request"]["config"]["response_format"]}
            self.assertEqual(case["expect_lm15"]["adaptations"], [expected])
            if action == "substituted":
                self.assertIs(case["request"]["body"]["reasoning_effort"], True)
            else:
                self.assertNotIn("response_format", case["request"]["body"])

    def test_derivation_detects_plausible_wrong_answers(self):
        for name in SNAPSHOTS:
            with self.subTest(case=name):
                expected = self.derive(name)
                changed = copy.deepcopy(expected)
                if "canonical_response" in changed:
                    changed["canonical_response"]["usage"]["output_tokens"] += 1
                else:
                    changed["events"].pop()
                with self.assertRaises(AssertionError):
                    self.verify(name, changed)


if __name__ == "__main__":
    unittest.main()
