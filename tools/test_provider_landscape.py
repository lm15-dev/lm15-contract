"""Offline tests for tools/provider_landscape.py; no network, no credentials."""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provider_landscape as pl

MATRIX = {
    "groq": {"supports": {"complete": True, "stream": True, "images": False}},
    "openai": {"supports": {"complete": True, "images": True, "speech": True}},
    "bedrock-anthropic": {"supports": {"complete": True}},
    "vllm": {"supports": {"complete": True}},
}


def pi_files() -> dict[str, bytes]:
    groq = {"openai-completions": {
        "chat:llama": {"id": "llama", "api": "openai-completions", "provider": "groq",
                       "baseUrl": "https://api.groq.com/openai/v1", "maxTokens": 8192, "type": "chat"}}}
    acme = {"acme-native": {
        "chat:a1": {"id": "a1", "api": "acme-native", "provider": "acme", "type": "chat"},
        "image:i1": {"id": "i1", "api": "acme-native", "provider": "acme", "type": "image"}}}
    return {
        "package.json": b'{"version": "9.9.9"}',
        "dist/types.d.ts": b'export type KnownProvider =\n | "groq"\n | "acme"\n | "dynamic";\n',
        "dist/env-api-keys.js": b'export const GROQ_KEY_ENV = "GROQ_API_KEY";\n',
        "dist/providers/groq.js": b'createProvider({\n id: "groq",\n name: "Groq",\n'
                                  b' auth: { apiKey: envApiKeyAuth("Groq API key", [GROQ_KEY_ENV]) } })',
        "dist/providers/data/groq.json": json.dumps(groq).encode(),
        "dist/providers/data/acme.json": json.dumps(acme).encode(),
    }


def litellm_files() -> dict[str, bytes]:
    utils = 'class LlmProviders(str, Enum):\n    GROQ = "groq"\n    TAVILY = "tavily"\n    VLLM = "vllm"\n'
    constants = 'openai_compatible_providers: list = ["groq"]\n'
    support = {"endpoints": {"responses": {"provider_json_field": "responses", "bridges_to_chat_completion": True},
                             "chat_completions": {"provider_json_field": "chat_completions"}},
               "providers": {"groq": {"display_name": "Groq (`groq`)", "url": "u",
                                      "endpoints": {"chat_completions": True, "responses": True, "audio_speech": True}},
                             "tavily": {"display_name": "Tavily", "endpoints": {"search": True}}}}
    openai_like = {"newhost": {"base_url": "https://new.example/v1", "api_key_env": "NEWHOST_API_KEY"}}
    prices = {"sample_spec": {"litellm_provider": "doc"},
              "groq/llama": {"litellm_provider": "groq", "mode": "chat", "max_output_tokens": 8192},
              "groq/whisper": {"litellm_provider": "groq", "mode": "audio_transcription"},
              "bedrock/anthropic.claude-x": {"litellm_provider": "bedrock", "mode": "chat"},
              "bedrock/amazon.nova": {"litellm_provider": "bedrock", "mode": "chat"},
              "bedrock/titan-embed": {"litellm_provider": "bedrock", "mode": "embedding",
                                      "deprecation_date": "2020-01-01"}}
    return {"litellm/types/utils.py": utils.encode(), "litellm/constants.py": constants.encode(),
            "litellm/provider_endpoints_support_backup.json": json.dumps(support).encode(),
            "litellm/llms/openai_like/providers.json": json.dumps(openai_like).encode(),
            "litellm/model_prices_and_context_window_backup.json": json.dumps(prices).encode()}


def snapshot() -> dict:
    providers = {f"pi:{k}": v for k, v in pl.extract_pi(pi_files()).items()}
    providers.update({f"litellm:{k}": v for k, v in pl.extract_litellm(litellm_files()).items()})
    return {"fetched_on": "2026-10-02", "providers": providers, "lm15_facts": None,
            "sources": {"pi": {"package": "p", "version": "9.9.9", "from": "x"},
                        "litellm": {"package": "l", "version": "1.0", "from": "y"}}}


class ExtractTests(unittest.TestCase):
    def test_pi_providers_models_and_metadata(self):
        pi = pl.extract_pi(pi_files())
        self.assertEqual(set(pi), {"groq", "acme", "dynamic"})  # KnownProvider adds catalog-less ids
        self.assertEqual(pi["groq"]["name"], "Groq")
        self.assertEqual(pi["groq"]["env_keys"], ["GROQ_API_KEY"])  # resolved through the _ENV constant
        self.assertEqual(pi["groq"]["lm15_wire"], ["openai-chat"])
        self.assertEqual(pi["groq"]["models"], [{"id": "llama", "kind": "chat", "wire": "openai-completions",
                                                 "max_output": 8192}])
        self.assertEqual(pi["acme"]["lm15_wire"], [])
        self.assertEqual([m["kind"] for m in pi["acme"]["models"]], ["chat", "image"])

    def test_pi_unknown_catalog_shape_is_loud(self):
        files = pi_files()
        files["dist/providers/data/bad.json"] = b'{"x": {"y": "not a model"}}'
        with self.assertRaises(pl.LandscapeError):
            pl.extract_pi(files)

    def test_litellm_union_of_sources_and_bridged_flags_dropped(self):
        ll = pl.extract_litellm(litellm_files())
        self.assertEqual(set(ll), {"groq", "tavily", "vllm", "newhost", "bedrock"})
        self.assertEqual(ll["groq"]["name"], "Groq")
        self.assertEqual(ll["groq"]["endpoints"], ["audio_speech", "chat_completions"])  # `responses` is bridged
        self.assertEqual(ll["groq"]["lm15_wire"], ["openai-chat"])
        self.assertEqual(ll["newhost"]["lm15_wire"], ["openai-chat"])
        self.assertEqual(ll["newhost"]["env_keys"], ["NEWHOST_API_KEY"])
        self.assertNotIn("doc", ll)  # sample_spec is not a provider
        self.assertEqual(ll["bedrock"]["models"][-1]["deprecation"], "2020-01-01")

    def test_auto_out_of_scope_only_when_everything_is_ruled_out(self):
        ll = pl.extract_litellm(litellm_files())
        self.assertEqual(pl.auto_status(ll["tavily"]), "only offers search")
        self.assertIsNone(pl.auto_status(ll["groq"]))
        self.assertIsNone(pl.auto_status(ll["vllm"]))  # offers nothing known: a human decides


class EvaluateTests(unittest.TestCase):
    def classes(self) -> dict:
        return {"pi:groq": {"status": "supported", "lm15": ["groq"]},
                "litellm:groq": {"status": "supported", "lm15": ["groq"]},
                "pi:acme": {"status": "missing"}, "pi:dynamic": {"status": "missing"},
                "litellm:newhost": {"status": "missing"},
                "litellm:vllm": {"status": "missing", "distinct_from": ["vllm"]},
                "litellm:bedrock": {"status": "partial", "lm15": ["bedrock-anthropic"], "note": "n",
                                    "model_rules": [["*anthropic.claude*", "bedrock-anthropic"]]}}

    def test_clean(self):
        self.assertEqual(pl.evaluate(snapshot(), self.classes(), MATRIX), [])

    def test_each_problem_is_reported(self):
        classes = self.classes()
        del classes["pi:acme"]
        classes["pi:gone"] = {"status": "missing"}
        classes["litellm:groq"] = {"status": "supported", "lm15": ["groqq"]}
        classes["pi:dynamic"] = {"status": "partial", "lm15": ["groq"]}
        classes["litellm:newhost"] = {"status": "missing", "lm15": ["groq"]}
        del classes["litellm:vllm"]["distinct_from"]
        problems = "\n".join(pl.evaluate(snapshot(), classes, MATRIX))
        for needle in ("UNCLASSIFIED pi:acme", "STALE classification pi:gone", "'groqq' is not in",
                       "partial needs a note", "missing must not list", "SUSPECT classification litellm:vllm"):
            self.assertIn(needle, problems)

    def test_model_status(self):
        snap, classes = snapshot(), self.classes()
        verdict = lambda key: pl.effective(key, snap["providers"][key], classes)
        models = {m["id"]: m for m in snap["providers"]["litellm:bedrock"]["models"]}
        self.assertEqual(pl.model_status(models["bedrock/anthropic.claude-x"], verdict("litellm:bedrock"), MATRIX),
                         ("yes", "bedrock-anthropic"))
        self.assertEqual(pl.model_status(models["bedrock/amazon.nova"], verdict("litellm:bedrock"), MATRIX), ("unknown", ""))
        self.assertEqual(pl.model_status(models["bedrock/titan-embed"], verdict("litellm:bedrock"), MATRIX), (pl.OUT, ""))
        whisper = {"id": "groq/whisper", "kind": "audio_transcription"}
        self.assertEqual(pl.model_status(whisper, verdict("litellm:groq"), MATRIX), (pl.NONE, ""))
        image = {"id": "i1", "kind": "image"}
        self.assertEqual(pl.model_status(image, {"status": "supported", "lm15": ["groq"], "model_rules": []}, MATRIX),
                         ("surface-missing", "groq"))
        self.assertEqual(pl.model_status(image, verdict("pi:acme"), MATRIX), ("provider-missing", ""))


class CommandTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = pl.main(list(args))
        return code, out.getvalue()

    def test_update_report_check_cycle_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg, litellm = root / "pi-ai", root / "site" / "litellm"
            for rel, data in pi_files().items():
                (pkg / rel).parent.mkdir(parents=True, exist_ok=True)
                (pkg / rel).write_bytes(data)
            for rel, data in litellm_files().items():
                (root / "site" / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / "site" / rel).write_bytes(data)
            matrix = root / "matrix.json"
            matrix.write_text(json.dumps({"providers": MATRIX}), encoding="utf-8")
            data = root / "data"
            common = ["--data-dir", str(data), "--matrix", str(matrix), "--auth-spec", str(root / "auth.md")]
            code, out = self.run_cli(*common, "update", "--pi-package", str(pkg), "--litellm-dir", str(litellm),
                                     "--lm15-python", str(root / "absent"), "--today", "2026-10-02")
            self.assertEqual(code, 0)
            self.assertIn("first snapshot", out)
            self.assertEqual(self.run_cli(*common, "check")[0], 1)  # nothing classified yet
            code, _ = self.run_cli(*common, "suggest")
            self.assertEqual(code, 0)
            (data / "classification.json").write_text(json.dumps({"providers": EvaluateTests().classes()}), encoding="utf-8")
            self.assertEqual(self.run_cli(*common, "check")[0], 1)  # report predates the classification
            self.assertEqual(self.run_cli(*common, "report")[0], 0)
            code, out = self.run_cli(*common, "check")
            self.assertEqual(code, 0, out)
            report = (data / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("| acme |", report)  # missing service listed
            self.assertIn("speech", report)  # groq: upstream offers speech, lm15 groq does not
            tsv = (data / "models.tsv").read_text(encoding="utf-8").splitlines()
            self.assertIn("litellm\tgroq\tgroq/llama\tchat\tyes\tgroq", tsv)
            # A second identical update reports no change and leaves check green.
            code, out = self.run_cli(*common, "update", "--pi-package", str(pkg), "--litellm-dir", str(litellm),
                                     "--lm15-python", str(root / "absent"), "--today", "2026-10-02")
            self.assertIn("no upstream change", out)
            self.assertEqual(self.run_cli(*common, "check")[0], 0)

    def test_npm_integrity_is_enforced(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for rel, data in pi_files().items():
                info = tarfile.TarInfo("package/" + rel)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        tarball = buffer.getvalue()
        good = "sha512-" + base64.b64encode(hashlib.sha512(tarball).digest()).decode()

        def fake_get(integrity):
            def get(url, timeout=0):
                if url.endswith(".tgz"):
                    return tarball
                return json.dumps({"version": "9.9.9", "dist": {"tarball": "https://r/x.tgz", "integrity": integrity}}).encode()
            return get

        with patch.object(pl, "_get", fake_get(good)):
            source, files = pl.fetch_pi(None)
        self.assertEqual(source["version"], "9.9.9")
        self.assertIn("dist/providers/data/groq.json", files)
        with patch.object(pl, "_get", fake_get("sha512-" + base64.b64encode(b"x" * 64).decode())):
            with self.assertRaises(pl.LandscapeError):
                pl.fetch_pi(None)


class RepositoryTests(unittest.TestCase):
    """The committed landscape stays consistent with the committed matrix."""

    def test_committed_landscape_checks_clean(self):
        if not (pl.DATA / "snapshot.json").is_file():
            self.skipTest("no committed snapshot")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = pl.main(["check"])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
