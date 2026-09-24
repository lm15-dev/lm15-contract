"""Mutation self-test for tools/check_gateway.py, in the spirit of
harness/selftest.py: copy the example day, break exactly one thing, and
FAIL unless the checker catches it. Also proves the clean copy is green,
so every red below is attributable to its mutation.

When the `jsonschema` library is importable, every example row is also
validated by it against gateway/schema/capture-v1.json, so the small
validator inside check_gateway.py cannot drift from real JSON Schema
semantics unnoticed. Without the library that cross-check is skipped
(stated), never silently passed.
"""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import check_gateway  # noqa: E402

DAY = "2026-09-19"


def run(root: Path) -> tuple[int, str]:
    out = io.StringIO()
    argv = sys.argv
    sys.argv = ["check_gateway.py", "--root", str(root)]
    try:
        with redirect_stdout(out):
            code = check_gateway.main()
    finally:
        sys.argv = argv
    return code, out.getvalue()


class Sandbox:
    """A throwaway copy of gateway/ with helpers to mutate one row or blob."""

    def __init__(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="lm15-gateway-check-"))
        shutil.copytree(ROOT / "gateway", self.tmp / "gateway")
        self.day = self.tmp / "gateway" / "examples" / DAY

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rows(self, stream: str) -> list[dict]:
        p = self.day / stream / f"{DAY}.jsonl"
        return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]

    def write(self, stream: str, rows: list[dict]) -> None:
        p = self.day / stream / f"{DAY}.jsonl"
        p.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8")

    def mutate(self, stream: str, index: int, fn) -> None:
        rows = self.rows(stream)
        fn(rows[index])
        self.write(stream, rows)

    def blob_path(self, sha: str) -> Path:
        return self.day / "raw" / sha[:2] / f"{sha}.http"


MUTATIONS = {
    "unknown field": ("exchanges", 0, lambda r: r.__setitem__("cost_usd", 0.01)),
    "wrong api_family spelling": ("exchanges", 0, lambda r: r.__setitem__("api_family", "anthropic")),
    "hyphenless provider": ("exchanges", 1, lambda r: r.__setitem__("provider", "openai_codex")),
    "version bump": ("exchanges", 0, lambda r: r.__setitem__("v", 2)),
    "local-time timestamp": ("exchanges", 0, lambda r: r.__setitem__("t", "2026-09-19T10:03:12.481-04:00")),
    "ulid not matching t": ("exchanges", 0, lambda r: r.__setitem__("t", "2026-09-19T14:03:12.482Z")),
    "t_end before t": ("exchanges", 0, lambda r: r.__setitem__("t_end", "2026-09-19T14:03:12.000Z")),
    "latency below ttfb": ("exchanges", 0, lambda r: r["upstream"].__setitem__("latency_ms", 1)),
    "model call without model": ("exchanges", 0, lambda r: r.pop("model")),
    "model call without model, completed with error": ("exchanges", 4, lambda r: (r.pop("model"), r.__setitem__("error", {"code": "server", "message": "x"}))),
    "model without sent": ("exchanges", 0, lambda r: r["model"].pop("sent")),
    "usage counter negative": ("exchanges", 0, lambda r: r["usage"].__setitem__("output_tokens", -1)),
    "usage counter invented": ("exchanges", 0, lambda r: r["usage"].__setitem__("billed_tokens", 5)),
    "adaptations outside translate": ("exchanges", 0, lambda r: r.__setitem__("adaptations", [{"field": "config.seed", "action": "dropped", "reason": "no seed on Anthropic"}])),
    "adaptation action invented": ("exchanges", 2, lambda r: (r.__setitem__("route", {"lane": "translate"}), r.__setitem__("adaptations", [{"field": "config.seed", "action": "ignored", "reason": "x"}]))),
    "route without lane": ("exchanges", 2, lambda r: r["route"].pop("lane")),
    "secret query in path": ("exchanges", 3, lambda r: r.__setitem__("path", "/v1/models?key=AIzaSyFAKEFAKEFAKE")),
    "secret query in upstream url": ("exchanges", 3, lambda r: r["upstream"].__setitem__("url", "https://api.anthropic.com/v1/models?api_key=x")),
    "userinfo in upstream url": ("exchanges", 3, lambda r: r["upstream"].__setitem__("url", "https://user:pw@api.anthropic.com/v1/models")),
    "redacted list lies (claims more)": ("exchanges", 0, lambda r: r.__setitem__("redacted", ["x-api-key", "authorization"])),
    "redacted list lies (claims less)": ("exchanges", 0, lambda r: r.__setitem__("redacted", [])),
    "error code invented": ("exchanges", 5, lambda r: r["error"].__setitem__("code", "client_abort")),
    "abort with usage": ("exchanges", 5, lambda r: r.__setitem__("usage", {"input_tokens": 1})),
    "no response and no error": ("exchanges", 5, lambda r: r.pop("error")),
    "marked secret without location": ("exchanges", 4, lambda r: r["secrets"].pop("locations")),
    "secret location past blob end": ("exchanges", 4, lambda r: r["secrets"]["locations"][0].__setitem__("offset", 10**9)),
    "scrubbed secret with location": ("exchanges", 4, lambda r: r["secrets"].__setitem__("action", "scrubbed")),
    "blob length lies": ("exchanges", 0, lambda r: r["raw"]["request"].__setitem__("bytes", 7)),
    "example claims wire hash": ("exchanges", 0, lambda r: r["raw"]["request"].__setitem__("wire_sha256", "0" * 64)),
    "event on unknown exchange": ("events", 0, lambda r: r.__setitem__("id", "01M2WZMVQ1JCGPB7CM1MGYBF9Z")),
    "event seq gap": ("events", 3, lambda r: r.__setitem__("seq", 42)),
    "event offsets go backwards": ("events", 1, lambda r: r.__setitem__("t_offset_ms", 0)),
    "dir on a non-websocket": ("events", 0, lambda r: r.__setitem__("dir", "in")),
    "decoded on unknown exchange": ("decoded", 0, lambda r: r.__setitem__("id", "01M2WZMVQ1JCGPB7CM1MGYBF9Z")),
    "decoded full without response": ("decoded", 0, lambda r: r.pop("response")),
    "decoded none with request": ("decoded", 3, lambda r: r.__setitem__("request", {})),
    "decoded partial without notes": ("decoded", 5, lambda r: r.pop("notes")),
    "decoder name invented": ("decoded", 0, lambda r: r["decoder"].__setitem__("name", "litellm")),
    "contract pin not a commit": ("decoded", 0, lambda r: r.__setitem__("contract_pin", "main")),
    "scan coverage invented": ("scan", 0, lambda r: r.__setitem__("coverage", "maybe")),
    "scan remote not ip:port": ("scan", 0, lambda r: r.__setitem__("remote", "api.openai.com")),
    "scan match invented": ("scan", 2, lambda r: r.__setitem__("match", "guess")),
}


class CheckGatewayTeeth(unittest.TestCase):
    def test_clean_copy_is_green(self):
        sb = Sandbox()
        try:
            code, out = run(sb.tmp)
            self.assertEqual(code, 0, out)
        finally:
            sb.cleanup()

    def test_every_mutation_is_caught(self):
        for name, (stream, index, fn) in MUTATIONS.items():
            with self.subTest(mutation=name):
                sb = Sandbox()
                try:
                    sb.mutate(stream, index, fn)
                    code, out = run(sb.tmp)
                    self.assertEqual(code, 1, f"mutation {name!r} was not caught:\n{out}")
                finally:
                    sb.cleanup()

    def test_blob_tampering_is_caught(self):
        for name, tamper in {
            "one byte changed": lambda data: b"X" + data[1:],
            "api key unredacted": lambda data: data.replace(b"x-api-key: [redacted:108]", b"x-api-key: sk-ant-not-a-real-key-but-not-redacted-either"),
            "authorization unredacted": lambda data: data.replace(b"authorization: [redacted:171]", b"authorization: Bearer nope"),
            "content-encoding kept": lambda data: data.replace(b"content-type:", b"content-encoding: gzip\r\ncontent-type:", 1),
            "content-length lies": lambda data: data.replace(b"content-length: ", b"content-length: 9", 1),
            "not an http message": lambda data: data.replace(b"\r\n\r\n", b"\n\n"),
        }.items():
            with self.subTest(tamper=name):
                sb = Sandbox()
                try:
                    caught_any = False
                    # Apply to the first blob whose bytes change, rewriting the row's hash so
                    # ONLY the tampering (not the hash mismatch) can be what the checker sees —
                    # except for "one byte changed", where the hash mismatch IS the check.
                    for row in sb.rows("exchanges"):
                        for which in ("request", "response"):
                            ref = row.get("raw", {}).get(which)
                            if not ref:
                                continue
                            p = sb.blob_path(ref["sha256"])
                            data = p.read_bytes()
                            new = tamper(data)
                            if new == data:
                                continue
                            if name == "one byte changed":
                                p.write_bytes(new)
                            else:
                                h = hashlib.sha256(new).hexdigest()
                                q = sb.blob_path(h)
                                q.parent.mkdir(exist_ok=True)
                                q.write_bytes(new)
                                p.unlink()
                                rows = sb.rows("exchanges")
                                for r in rows:
                                    for w in ("request", "response"):
                                        if r.get("raw", {}).get(w, {}).get("sha256") == ref["sha256"]:
                                            r["raw"][w] = {"sha256": h, "bytes": len(new), **({"content_encoding": ref["content_encoding"]} if "content_encoding" in ref else {})}
                                sb.write("exchanges", rows)
                            caught_any = True
                            break
                        if caught_any:
                            break
                    self.assertTrue(caught_any, f"tamper {name!r} changed no blob")
                    code, out = run(sb.tmp)
                    self.assertEqual(code, 1, f"tamper {name!r} was not caught:\n{out}")
                finally:
                    sb.cleanup()

    def test_orphan_blob_is_caught(self):
        sb = Sandbox()
        try:
            h = hashlib.sha256(b"orphan").hexdigest()
            p = sb.blob_path(h)
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(b"orphan")
            code, out = run(sb.tmp)
            self.assertEqual(code, 1, out)
            self.assertIn("no exchange references", out)
        finally:
            sb.cleanup()

    def test_missing_provenance_is_caught(self):
        sb = Sandbox()
        try:
            (sb.day / "_provenance.json").unlink()
            code, out = run(sb.tmp)
            self.assertEqual(code, 1, out)
        finally:
            sb.cleanup()

    def test_captures_day_needs_receipt_and_wire_hashes(self):
        sb = Sandbox()
        try:
            cap = sb.tmp / "gateway" / "captures" / DAY
            shutil.copytree(sb.day, cap)
            (cap / "_provenance.json").unlink()
            code, out = run(sb.tmp)
            self.assertEqual(code, 1, out)
            self.assertIn("_receipt.json", out)
            self.assertIn("wire_sha256", out)
        finally:
            sb.cleanup()

    def test_schema_with_unimplemented_keyword_is_refused(self):
        sb = Sandbox()
        try:
            p = sb.tmp / "gateway" / "schema" / "capture-v1.json"
            s = json.loads(p.read_text(encoding="utf-8"))
            s["$defs"]["exchange"]["properties"]["tag"] = {"type": "string", "format": "hostname"}
            p.write_text(json.dumps(s), encoding="utf-8")
            code, out = run(sb.tmp)
            self.assertEqual(code, 1, out)
            self.assertIn("not implemented", out)
        finally:
            sb.cleanup()

    def test_cross_check_with_jsonschema_library(self):
        try:
            import jsonschema  # type: ignore
        except ImportError:
            self.skipTest("jsonschema not installed: real-validator cross-check skipped (run under nix-shell -p 'python3.withPackages (p: [p.jsonschema])' to exercise it)")
        schema = json.loads((ROOT / "gateway" / "schema" / "capture-v1.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        for stream, defname in check_gateway.STREAMS.items():
            p = ROOT / "gateway" / "examples" / DAY / stream / f"{DAY}.jsonl"
            sub = {"$ref": f"#/$defs/{defname}", "$defs": schema["$defs"]}
            v = jsonschema.Draft202012Validator(sub)
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                errs = list(v.iter_errors(json.loads(line)))
                self.assertEqual(errs, [], f"{stream}:{i}: {[e.message for e in errs]}")
        # And the two validators agree on every mutation that is a pure schema matter.
        for name, (stream, index, fn) in MUTATIONS.items():
            sb = Sandbox()
            try:
                sb.mutate(stream, index, fn)
                rows = sb.rows(stream)
                defname = check_gateway.STREAMS[stream]
                mine = check_gateway.Validator(schema).validate(rows[index], schema["$defs"][defname])
                theirs = list(jsonschema.Draft202012Validator({"$ref": f"#/$defs/{defname}", "$defs": schema["$defs"]}).iter_errors(rows[index]))
                self.assertEqual(bool(mine), bool(theirs), f"{name}: check_gateway says {mine}, jsonschema says {[e.message for e in theirs]}")
            finally:
                sb.cleanup()


if __name__ == "__main__":
    unittest.main()
