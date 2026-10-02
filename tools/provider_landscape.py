#!/usr/bin/env python3
"""Track which providers and models Pi and LiteLLM support, against lm15.

Three inputs, one hand-kept table, three generated files:

- **Pi** — the published ``@earendil-works/pi-ai`` npm package (its
  ``dist/providers/data/*.json`` model catalogs, the ``KnownProvider``
  union, and each provider module's id, name and auth labels).  The npm
  tarball is checked against the registry's sha512 integrity.
- **LiteLLM** — the release tag ``v<version>`` of BerriAI/litellm (version
  from PyPI): the ``LlmProviders`` enum, the endpoint-support table, the
  JSON-declared OpenAI-compatible providers, ``openai_compatible_providers``
  and the model price/context table.  Each file's sha256 is recorded.
- **lm15** — ``spec/support-matrix.json`` (the ratified list: AUTHORITY.md),
  read on every run, plus the Python reference's Claude output-ceiling
  table, captured at update time.

``research/landscape/classification.json`` is the reviewed mapping: every
upstream provider is ``supported`` / ``partial`` (with lm15 provider
strings), ``missing``, ``out-of-scope`` or ``not-a-provider``.  Upstream
providers that offer only surfaces lm15 rules out (embeddings, vector
stores, web search, guardrails, agents …) are classified automatically.

Generated (never edit by hand): ``snapshot.json`` (the upstream extract),
``REPORT.md`` and ``models.tsv``.

Commands
  update   fetch the latest (or --pi-version / --litellm-version) upstream,
           rewrite snapshot.json, regenerate, print what changed.  Network.
  report   regenerate REPORT.md and models.tsv from the snapshot.  Offline.
  check    offline gate: every upstream provider classified, no stale entry,
           every lm15 name real, no "missing" entry that lm15 now ships,
           generated files current.  Exit 1 on any problem.
  suggest  print classification stubs for unclassified providers (a human
           reviews them; this never writes).

``--pi-package DIR`` / ``--litellm-dir DIR`` read an installed package
instead of the network (offline updates, tests).

Stdlib only.  Never edits the support matrix.
"""

from __future__ import annotations

import argparse
import ast
import base64
import datetime as _dt
import fnmatch
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "landscape"
MATRIX = ROOT / "spec" / "support-matrix.json"
AUTH_SPEC = ROOT / "spec" / "auth.md"
DEFAULT_LM15_PYTHON = ROOT.parent / "lm15-python"

PI_PACKAGE = "@earendil-works/pi-ai"
LITELLM_PACKAGE = "litellm"
LITELLM_REPO_RAW = "https://raw.githubusercontent.com/BerriAI/litellm"
LITELLM_FILES = (
    "litellm/types/utils.py",
    "litellm/constants.py",
    "litellm/provider_endpoints_support_backup.json",
    "litellm/llms/openai_like/providers.json",
    "litellm/model_prices_and_context_window_backup.json",
)

STATUSES = ("supported", "partial", "missing", "out-of-scope", "not-a-provider")
WITH_LM15 = {"supported", "partial"}
NEEDS_NOTE = {"partial", "out-of-scope", "not-a-provider"}

# lm15 support-matrix columns that name a surface a model can sit on.
LM15_SURFACES = ("complete", "live", "images", "speech", "video", "batches", "files")

# Model kinds (Pi model `type`, LiteLLM `mode`) -> the lm15 surface that
# serves them.  OUT: a kind lm15 rules out (SCOPE.md: embeddings) or that is
# not a model exchange at all.  NONE: no lm15 surface yet, and no ruling
# either — a real gap, not a non-goal.
OUT, NONE = "out-of-scope", "no-lm15-surface"
KIND_SURFACE = {
    "chat": "complete", "completion": "complete", "responses": "complete",
    "classifier": "complete", "evaluation": "complete",  # judgments; lm15 `typesafe` complete
    "image": "images", "image_generation": "images", "image_edit": "images",
    "audio_speech": "speech", "realtime": "live", "video_generation": "video",
    "embedding": OUT, "vector_store": OUT, "search": OUT, "guardrail": OUT,
    "audio_transcription": NONE, "rerank": NONE, "moderation": NONE, "ocr": NONE,
}

# LiteLLM endpoint flags (provider_json_field spelling) -> surface.  Flags
# whose endpoint "bridges_to_chat_completion" are LiteLLM translating chat
# into another API shape, not evidence about the provider; they are dropped
# using the flag in the upstream file itself.
ENDPOINT_SURFACE = {
    "chat_completions": "complete", "text_completion": "complete",
    "generateContent": "complete", "bedrock_converse": "complete",
    "bedrock_invoke": "complete",
    "image_generations": "images", "image_edits": "images", "image_variations": "images",
    "audio_speech": "speech", "text_to_speech": "speech",
    "realtime": "live", "batches": "batches", "files": "files",
    "video_generations": "video", "videos": "video",
    "audio_transcriptions": NONE, "rerank": NONE, "moderations": NONE, "ocr": NONE,
    "embeddings": OUT, "search": OUT, "fine_tuning": OUT, "assistants": OUT,
    "vector_stores_create": OUT, "vector_stores_search": OUT, "vector_store_files": OUT,
    "rag_ingest": OUT, "rag_query": OUT, "skills": OUT, "container": OUT,
    "container_files": OUT, "count_tokens": OUT, "compact": OUT, "mcp": OUT,
    "apply_guardrail": OUT,
}

# Upstream wire names -> the lm15 dialect that speaks the same wire.  A
# "missing" provider on such a wire is reachable today through a declared
# provider (RouterConfig(providers=...)), without a receipt.
PI_WIRE_DIALECT = {
    "openai-completions": "openai-chat", "openai-responses": "openai",
    "anthropic-messages": "anthropic", "google-generative-ai": "gemini",
    "google-vertex": "vertex", "azure-openai-responses": "azure",
    "openai-codex-responses": "openai-codex", "typesafe-system-one": "typesafe",
}


# ─── small utilities ────────────────────────────────────────────────


class LandscapeError(RuntimeError):
    pass


def _get(url: str, *, timeout: float = 120.0) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "lm15-contract/provider_landscape"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except Exception as exc:  # urllib raises several unrelated classes
        raise LandscapeError(f"GET {url} failed: {exc}") from exc


def _json(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(name: str) -> str:
    """Comparable form of a provider id: `together_ai`, `together-ai` and
    `together` agree; so do `moonshot` and `moonshotai`."""
    key = re.sub(r"[^a-z0-9]", "", name.lower())
    return key[:-2] if key.endswith("ai") and len(key) > 4 else key


def _git_head(path: Path) -> str | None:
    try:
        head = subprocess.run(["git", "-C", str(path), "rev-parse", "--short=12", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(path), "status", "--porcelain", "--", "lm15/providers/anthropic.py"],
                               capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return head + ("+dirty" if dirty else "")


# ─── upstream: Pi ───────────────────────────────────────────────────


def _pi_wanted(path: str) -> bool:
    if path in ("package.json", "dist/types.d.ts", "dist/env-api-keys.js"):
        return True
    if path.startswith("dist/providers/data/") and path.endswith(".json"):
        return not path.rsplit("/", 1)[1].startswith(".")  # .manifest.json is hashes
    return (path.startswith("dist/providers/") and path.endswith(".js")
            and path.count("/") == 2 and not path.endswith(".models.js"))


def fetch_pi(version: str | None) -> tuple[dict[str, Any], dict[str, bytes]]:
    quoted = urllib.parse.quote(PI_PACKAGE, safe="@")
    meta = _json(_get(f"https://registry.npmjs.org/{quoted}/{version or 'latest'}"))
    tarball_url, integrity = meta["dist"]["tarball"], meta["dist"]["integrity"]
    tarball = _get(tarball_url)
    algorithm, _, expected = integrity.partition("-")
    if algorithm != "sha512":
        raise LandscapeError(f"unexpected npm integrity algorithm {algorithm!r}")
    actual = base64.b64encode(hashlib.sha512(tarball).digest()).decode("ascii")
    if actual != expected:
        raise LandscapeError(f"{tarball_url}: sha512 mismatch (registry {expected}, got {actual})")
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as archive:
        for member in archive.getmembers():
            path = member.name.split("/", 1)[1] if "/" in member.name else member.name
            if member.isfile() and _pi_wanted(path):
                handle = archive.extractfile(member)
                if handle is not None:
                    files[path] = handle.read()
    source = {"package": PI_PACKAGE, "version": meta["version"], "from": tarball_url, "integrity": integrity}
    return source, files


def read_pi_package(directory: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    files = {p.relative_to(directory).as_posix(): p.read_bytes()
             for p in directory.rglob("*") if p.is_file() and _pi_wanted(p.relative_to(directory).as_posix())}
    if "package.json" not in files:
        raise LandscapeError(f"{directory} has no package.json (pass the pi-ai package root)")
    version = _json(files["package.json"])["version"]
    return {"package": PI_PACKAGE, "version": version, "from": f"local package {directory.name}",
            "integrity": None}, files


def extract_pi(files: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    providers: dict[str, dict[str, Any]] = {}

    def entry(pid: str) -> dict[str, Any]:
        return providers.setdefault(pid, {"source": "pi", "id": pid, "name": None, "wires": set(),
                                          "base_urls": set(), "env_keys": set(), "auth": [],
                                          "models": []})

    for path in sorted(files):
        if not path.startswith("dist/providers/data/"):
            continue
        catalog = _json(files[path])
        for wire, models in catalog.items():
            if not isinstance(models, dict):
                continue
            for model in models.values():
                if not isinstance(model, dict) or "provider" not in model:
                    raise LandscapeError(f"{path}: unexpected Pi catalog shape (schema changed?)")
                record = entry(model["provider"])
                record["wires"].add(model.get("api") or wire)
                if model.get("baseUrl"):
                    record["base_urls"].add(model["baseUrl"])
                item = {"id": model["id"], "kind": model.get("type", "chat"), "wire": model.get("api") or wire}
                if model.get("maxTokens"):
                    item["max_output"] = model["maxTokens"]
                record["models"].append(item)

    types = files.get("dist/types.d.ts", b"").decode("utf-8")
    known = re.search(r"type KnownProvider\s*=([^;]+);", types)
    if known:
        for pid in re.findall(r'"([^"]+)"', known.group(1)):
            entry(pid)

    env_constants = dict(re.findall(r'export const ([A-Z][A-Z0-9_]*_ENV) = "([^"]+)"',
                                    files.get("dist/env-api-keys.js", b"").decode("utf-8")))
    for path in sorted(files):
        if not (path.startswith("dist/providers/") and path.endswith(".js")):
            continue
        text = files[path].decode("utf-8")
        found = re.search(r'createProvider\(\{\s*id:\s*"([^"]+)",\s*name:\s*"([^"]+)"', text)
        if not found or found.group(1) not in providers:
            continue
        record = providers[found.group(1)]
        record["name"] = found.group(2)
        record["auth"] = sorted({n for n in re.findall(r'name:\s*"([^"]+)"', text) if n != found.group(2)})
        literals = set(re.findall(r'"([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)"', text))
        literals |= {env_constants[c] for c in re.findall(r"\b([A-Z][A-Z0-9_]*_ENV)\b", text) if c in env_constants}
        record["env_keys"] = {k for k in literals if "KEY" in k or "TOKEN" in k}

    for record in providers.values():
        record["wires"] = sorted(record["wires"])
        record["base_urls"] = sorted(record["base_urls"])
        record["env_keys"] = sorted(record["env_keys"])
        record["models"].sort(key=lambda m: (m["kind"], m["id"]))
        hints = sorted({PI_WIRE_DIALECT[w] for w in record["wires"] if w in PI_WIRE_DIALECT})
        record["lm15_wire"] = hints
    return providers


# ─── upstream: LiteLLM ──────────────────────────────────────────────


def fetch_litellm(version: str | None, ref: str | None) -> tuple[dict[str, Any], dict[str, bytes]]:
    pypi = _json(_get(f"https://pypi.org/pypi/{LITELLM_PACKAGE}/{version + '/' if version else ''}json"))
    resolved = pypi["info"]["version"]
    ref = ref or f"v{resolved}"
    files = {path: _get(f"{LITELLM_REPO_RAW}/{ref}/{path}") for path in LITELLM_FILES}
    source = {"package": LITELLM_PACKAGE, "version": resolved, "from": f"github BerriAI/litellm@{ref}",
              "sha256": {path: _sha256(data) for path, data in files.items()}}
    return source, files


def read_litellm_dir(directory: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    base = directory.parent
    files = {path: (base / path).read_bytes() for path in LITELLM_FILES}
    version = "unknown"
    for metadata in sorted(base.glob("litellm-*.dist-info/METADATA")):
        found = re.search(r"^Version: (\S+)$", metadata.read_text(encoding="utf-8"), re.M)
        if found:
            version = found.group(1)
    return {"package": LITELLM_PACKAGE, "version": version, "from": f"local package {directory}",
            "sha256": {path: _sha256(data) for path, data in files.items()}}, files


def _class_strings(source: str, class_name: str) -> list[str]:
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [s.value.value for s in node.body
                    if isinstance(s, ast.Assign) and isinstance(s.value, ast.Constant)
                    and isinstance(s.value.value, str)]
    raise LandscapeError(f"class {class_name} not found in LiteLLM source")


def _list_literal(source: str, name: str) -> list[str]:
    for node in ast.parse(source).body:
        target = node.target if isinstance(node, ast.AnnAssign) else (
            node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None)
        if isinstance(target, ast.Name) and target.id == name and getattr(node, "value", None) is not None:
            return [v for v in ast.literal_eval(node.value) if isinstance(v, str)]
    raise LandscapeError(f"{name} not found in LiteLLM source")


def extract_litellm(files: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    enum = _class_strings(files["litellm/types/utils.py"].decode("utf-8"), "LlmProviders")
    compatible = set(_list_literal(files["litellm/constants.py"].decode("utf-8"), "openai_compatible_providers"))
    support = _json(files["litellm/provider_endpoints_support_backup.json"])
    openai_like = _json(files["litellm/llms/openai_like/providers.json"])
    prices = _json(files["litellm/model_prices_and_context_window_backup.json"])

    bridged = {spec.get("provider_json_field", key) for key, spec in support.get("endpoints", {}).items()
               if isinstance(spec, dict) and spec.get("bridges_to_chat_completion")}
    providers: dict[str, dict[str, Any]] = {}

    def entry(pid: str) -> dict[str, Any]:
        return providers.setdefault(pid, {"source": "litellm", "id": pid, "name": None, "docs": None,
                                          "origins": set(), "endpoints": [], "base_urls": [],
                                          "env_keys": [], "lm15_wire": [], "models": []})

    for pid in enum:
        entry(pid)["origins"].add("enum")
    for pid, spec in support.get("providers", {}).items():
        record = entry(pid)
        record["origins"].add("endpoints")
        record["name"] = re.sub(r"\s*\(`[^`]*`\)\s*$", "", spec.get("display_name") or "") or None
        record["docs"] = spec.get("url")
        record["endpoints"] = sorted(k for k, v in spec.get("endpoints", {}).items() if v is True and k not in bridged)
    for pid, spec in openai_like.items():
        record = entry(pid)
        record["origins"].add("openai_like")
        record["base_urls"] = [spec["base_url"]] if spec.get("base_url") else []
        record["env_keys"] = [spec["api_key_env"]] if spec.get("api_key_env") else []
    for key, model in prices.items():
        provider = model.get("litellm_provider") if isinstance(model, dict) else None
        if key == "sample_spec" or not isinstance(provider, str):
            continue
        record = entry(provider)
        record["origins"].add("prices")
        item = {"id": key, "kind": model.get("mode") or "chat"}
        if isinstance(model.get("max_output_tokens"), int):
            item["max_output"] = model["max_output_tokens"]
        if model.get("deprecation_date"):
            item["deprecation"] = model["deprecation_date"]
        record["models"].append(item)

    for pid, record in providers.items():
        record["origins"] = sorted(record["origins"])
        record["models"].sort(key=lambda m: (m["kind"], m["id"]))
        if pid in compatible or "openai_like" in record["origins"]:
            record["lm15_wire"] = ["openai-chat"]
    return providers


# ─── lm15 ────────────────────────────────────────────────────────────


def load_matrix(path: Path = MATRIX) -> dict[str, dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["providers"]


def lm15_python_facts(lm15_python: Path) -> dict[str, Any] | None:
    """The reference's hard-coded Claude output ceilings — the one model
    table lm15 keeps (MAP-7 rule 6).  Parsed, never imported."""
    source = lm15_python / "lm15" / "providers" / "anthropic.py"
    if not source.is_file():
        return None
    values: dict[str, Any] = {}
    for node in ast.parse(source.read_text(encoding="utf-8")).body:
        target = node.target if isinstance(node, ast.AnnAssign) else (
            node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None)
        if isinstance(target, ast.Name) and target.id in ("_CLAUDE_OUTPUT_CEILINGS", "_DEFAULT_MAX_TOKENS"):
            values[target.id] = ast.literal_eval(node.value)
    if "_CLAUDE_OUTPUT_CEILINGS" not in values:
        return None
    return {"from": f"lm15-python@{_git_head(lm15_python) or 'unknown'} lm15/providers/anthropic.py",
            "claude_output_ceilings": [list(pair) for pair in values["_CLAUDE_OUTPUT_CEILINGS"]],
            "default_max_tokens": values.get("_DEFAULT_MAX_TOKENS")}


def claude_ceiling(table: list[list[Any]], model: str) -> int | None:
    lowered = model.lower()
    for marker, ceiling in table:
        if marker in lowered:
            return ceiling
    return None


# ─── classification ─────────────────────────────────────────────────


def load_classification(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))["providers"]


def offered(record: dict[str, Any]) -> dict[str, set[str]]:
    """What upstream evidence says the provider offers: lm15 surface (or the
    OUT / NONE marker, or `?` for a kind this tool does not know) -> the
    upstream model kinds and endpoint flags behind it."""
    found: dict[str, set[str]] = {}
    for model in record["models"]:
        found.setdefault(KIND_SURFACE.get(model["kind"], "?"), set()).add(model["kind"])
    for endpoint in record.get("endpoints", []):
        found.setdefault(ENDPOINT_SURFACE.get(endpoint, "?"), set()).add(endpoint)
    return found


def auto_status(record: dict[str, Any]) -> str | None:
    """`out-of-scope` when everything the provider offers is something lm15
    rules out; None when a human must decide."""
    found = offered(record)
    if found and set(found) == {OUT}:
        return "only offers " + ", ".join(sorted(found[OUT]))
    return None


def effective(key: str, record: dict[str, Any], classes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if key in classes:
        return {"status": classes[key]["status"], "lm15": classes[key].get("lm15", []),
                "note": classes[key].get("note", ""), "auto": False,
                "model_rules": classes[key].get("model_rules", [])}
    reason = auto_status(record)
    if reason:
        return {"status": "out-of-scope", "lm15": [], "note": reason, "auto": True, "model_rules": []}
    return {"status": "unclassified", "lm15": [], "note": "", "auto": False, "model_rules": []}


def model_status(model: dict[str, Any], verdict: dict[str, Any],
                 matrix: dict[str, dict[str, Any]]) -> tuple[str, str]:
    surface = KIND_SURFACE.get(model["kind"])
    if surface in (OUT, NONE):
        return surface, ""
    if surface is None:
        return "unknown-kind", ""
    candidates = list(verdict["lm15"])
    if verdict["status"] == "partial":
        candidates = []
        for pattern, provider in verdict["model_rules"]:
            if fnmatch.fnmatchcase(model["id"], pattern):
                candidates = [provider]
                break
        if not candidates:
            return "unknown", ""
    if not candidates:
        return "provider-" + verdict["status"], ""
    for provider in candidates:
        if matrix.get(provider, {}).get("supports", {}).get(surface):
            return "yes", provider
    return "surface-missing", ",".join(candidates)


def evaluate(snapshot: dict[str, Any], classes: dict[str, dict[str, Any]],
             matrix: dict[str, dict[str, Any]]) -> list[str]:
    """Every problem the offline check fails on, as actionable lines."""
    problems: list[str] = []
    providers = snapshot["providers"]
    lm15_norm = {norm(p): p for p in matrix}
    for key, record in sorted(providers.items()):
        if key not in classes and auto_status(record) is None:
            problems.append(f"UNCLASSIFIED {key}: add it to classification.json (run `suggest` for a stub)")
    for key, spec in sorted(classes.items()):
        where = f"classification {key}"
        if key not in providers:
            problems.append(f"STALE {where}: upstream no longer lists it — delete the entry")
        status = spec.get("status")
        if status not in STATUSES:
            problems.append(f"BAD {where}: status {status!r} is not one of {', '.join(STATUSES)}")
            continue
        lm15 = spec.get("lm15", [])
        if status in WITH_LM15 and not lm15:
            problems.append(f"BAD {where}: {status} needs the lm15 provider strings that serve it")
        if status not in WITH_LM15 and lm15:
            problems.append(f"BAD {where}: {status} must not list lm15 providers")
        if status in NEEDS_NOTE and not spec.get("note"):
            problems.append(f"BAD {where}: {status} needs a note saying why")
        for name in lm15 + [p for _, p in spec.get("model_rules", [])]:
            if name not in matrix:
                problems.append(f"BAD {where}: lm15 provider {name!r} is not in spec/support-matrix.json")
        if spec.get("model_rules") and status != "partial":
            problems.append(f"BAD {where}: model_rules only apply to partial entries")
        if status == "missing" and key in providers:
            clash = lm15_norm.get(norm(providers[key]["id"]))
            if clash and clash not in spec.get("distinct_from", []):
                problems.append(f"SUSPECT {where}: marked missing but lm15 now ships {clash!r} — "
                                f"classify it supported, or add \"distinct_from\": [\"{clash}\"]")
    return problems


# ─── output ─────────────────────────────────────────────────────────


def dump_json(value: Any) -> str:
    """Indented JSON with each model record on one line, so upstream model
    churn shows as one line per model in a diff."""
    def render(item: Any, depth: int) -> str:
        pad = "  " * depth
        if isinstance(item, dict) and item and not ("id" in item and "kind" in item):
            body = ",\n".join(f'{pad}  {json.dumps(k)}: {render(v, depth + 1)}' for k, v in item.items())
            return "{\n" + body + "\n" + pad + "}"
        if isinstance(item, list) and item and any(isinstance(v, (dict, list)) for v in item):
            body = ",\n".join(pad + "  " + render(v, depth + 1) for v in item)
            return "[\n" + body + "\n" + pad + "]"
        return json.dumps(item, ensure_ascii=False)
    return render(value, 0) + "\n"


def _cell(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _counts(models: Iterable[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for model in models:
        counts[model["kind"]] = counts.get(model["kind"], 0) + 1
    return ", ".join(f"{n} {k}" for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))) or "—"


def render(snapshot: dict[str, Any], classes: dict[str, dict[str, Any]],
           matrix: dict[str, dict[str, Any]], auth_spec: str = "") -> tuple[str, str]:
    providers = snapshot["providers"]
    verdicts = {key: effective(key, rec, classes) for key, rec in providers.items()}
    rows: list[tuple[str, ...]] = []
    for key, record in sorted(providers.items()):
        for model in record["models"]:
            status, via = model_status(model, verdicts[key], matrix)
            rows.append((record["source"], record["id"], model["id"], model["kind"], status, via))
    tsv = "source\tprovider\tmodel\tkind\tlm15\tlm15_provider\n" + "".join("\t".join(r) + "\n" for r in rows)

    src = snapshot["sources"]
    out: list[str] = []
    w = out.append
    w("# Provider landscape: Pi and LiteLLM against lm15\n")
    w("Generated by `tools/provider_landscape.py` — do not edit. Reviewed mapping: "
      "[classification.json](classification.json); per-model rows: [models.tsv](models.tsv).\n")
    w(f"- **Pi** `{src['pi']['package']}` {src['pi']['version']} ({src['pi']['from']})")
    w(f"- **LiteLLM** {src['litellm']['version']} ({src['litellm']['from']})")
    w(f"- **lm15** `spec/support-matrix.json`: {len(matrix)} provider strings")
    w(f"- Upstream fetched on {snapshot['fetched_on']}\n")
    w("A provider is *supported* when lm15 has a registered provider string with live receipts for it, "
      "*partial* when lm15 covers some of its wires or models, *missing* when it is in scope but lm15 has "
      "no entry. A model is reachable (`yes` in models.tsv) when its provider is supported and the lm15 "
      "provider registers the surface the model needs. Upstream listing a provider proves only that "
      "the upstream library knows it; it is no live evidence for lm15.\n")

    w("## Summary\n")
    w("| | providers | supported | partial | missing | out of scope | not a provider | models | reachable via lm15 |")
    w("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for source in ("pi", "litellm"):
        keys = [k for k, r in providers.items() if r["source"] == source]
        by = {s: sum(1 for k in keys if verdicts[k]["status"] == s) for s in STATUSES + ("unclassified",)}
        mine = [r for r in rows if r[0] == source]
        reachable = sum(1 for r in mine if r[4] == "yes")
        label = "Pi" if source == "pi" else "LiteLLM"
        extra = f" (+{by['unclassified']} unclassified)" if by["unclassified"] else ""
        w(f"| {label} | {len(keys)}{extra} | {by['supported']} | {by['partial']} | {by['missing']} | "
          f"{by['out-of-scope']} | {by['not-a-provider']} | {len(mine)} | {reachable} |")
    w("")

    # Gaps, grouped across sources by `service` or normalized id.
    groups: dict[str, list[str]] = {}
    for key, record in providers.items():
        if verdicts[key]["status"] in ("missing", "unclassified"):
            service = classes.get(key, {}).get("service") or norm(record["id"])
            groups.setdefault(service, []).append(key)
    groups = {(service if any(classes.get(k, {}).get("service") == service for k in keys)
               else min((providers[k]["id"] for k in keys), key=lambda i: (len(i), i))): keys
              for service, keys in groups.items()}

    def gap_rank(item: tuple[str, list[str]]) -> tuple[int, int, str]:
        keys = item[1]
        sources = {providers[k]["source"] for k in keys}
        models = sum(1 for k in keys for m in providers[k]["models"] if KIND_SURFACE.get(m["kind"]) not in (OUT, NONE))
        return (-len(sources), -models, item[0])

    w("## Missing: in scope, no lm15 provider\n")
    w("Ranked by how many of the two libraries carry the service, then by model count. "
      "*lm15 wire* names the lm15 dialect that already speaks the provider's wire — those are reachable today "
      "through a declared provider (`RouterConfig(providers=...)`) and need a registry entry plus live receipts, "
      "not a new adapter.\n")
    w("| service | Pi | LiteLLM | lm15 wire | in-scope models | note |")
    w("|---|---|---|---|---:|---|")
    for service, keys in sorted(groups.items(), key=gap_rank):
        pi_ids = ", ".join(f"`{providers[k]['id']}`" for k in sorted(keys) if providers[k]["source"] == "pi") or "—"
        ll_ids = ", ".join(f"`{providers[k]['id']}`" for k in sorted(keys) if providers[k]["source"] == "litellm") or "—"
        wires = sorted({x for k in keys for x in providers[k]["lm15_wire"]}) or ["—"]
        models = sum(1 for k in keys for m in providers[k]["models"] if KIND_SURFACE.get(m["kind"]) not in (OUT, NONE))
        notes = "; ".join(dict.fromkeys(classes.get(k, {}).get("note", "") for k in keys if classes.get(k, {}).get("note")))
        if any(verdicts[k]["status"] == "unclassified" for k in keys):
            notes = ("**unclassified** " + notes).strip()
        w(f"| {_cell(service)} | {pi_ids} | {ll_ids} | {', '.join(wires)} | {models} | {_cell(notes)} |")
    w("")

    w("## Supported and partial\n")
    w("*Upstream also offers* lists what the upstream data shows for that provider that none of its lm15 "
      "providers register: an lm15 surface name, or an upstream kind lm15 has no surface for. LiteLLM endpoint "
      "flags that LiteLLM only bridges to chat are ignored; surfaces lm15 rules out are not listed.\n")
    w("| upstream | status | lm15 | models (reachable / all) | upstream also offers | note |")
    w("|---|---|---|---|---|---|")
    for key, record in sorted(providers.items(), key=lambda kv: (kv[1]["source"], kv[1]["id"])):
        verdict = verdicts[key]
        if verdict["status"] not in WITH_LM15:
            continue
        registered = {s for p in verdict["lm15"] for s, on in matrix.get(p, {}).get("supports", {}).items() if on is True}
        found = offered(record)
        extra = [s for s in LM15_SURFACES if s in found and s not in registered]
        extra += [f"{k} (no lm15 surface)" for k in sorted({k.rstrip("s") for k in found.get(NONE, ())})]
        extra += [f"{k} (unknown to this tool)" for k in sorted(found.get("?", ()))]
        mine = [r for r in rows if r[0] == record["source"] and r[1] == record["id"]]
        reach = f"{sum(1 for r in mine if r[4] == 'yes')} / {len(mine)}"
        lm15 = ", ".join(f"`{p}`" for p in verdict["lm15"])
        w(f"| {record['source']}:`{record['id']}` | {verdict['status']} | {lm15} | {reach} | "
          f"{', '.join(extra) or '—'} | {_cell(verdict['note'])} |")
    w("")

    w("## Sign-in and keys: Pi against lm15\n")
    w("For Pi providers lm15 serves: Pi's own sign-in labels and the credential variables its modules read "
      "(best-effort extraction from the published JS), against the matrix's auth modes and env keys. "
      "*Pi reads, lm15 ignores* lists variables neither in the matrix's env keys nor named in spec/auth.md "
      "(where the cloud credential chains are defined): a credential set there for Pi is not found by lm15.\n")
    w("| Pi | Pi sign-in labels | lm15 auth modes | lm15 env keys | Pi reads, lm15 ignores |")
    w("|---|---|---|---|---|")
    for key, record in sorted(providers.items()):
        verdict = verdicts[key]
        if record["source"] != "pi" or verdict["status"] not in WITH_LM15:
            continue
        modes = sorted({m for p in verdict["lm15"] for m in matrix.get(p, {}).get("auth_modes", [])})
        keys = sorted({k for p in verdict["lm15"] for k in matrix.get(p, {}).get("env_keys", [])})
        ignored = [k for k in record.get("env_keys", [])
                   if k not in keys and not re.search(rf"\b{re.escape(k)}\b", auth_spec)]
        w(f"| `{record['id']}` | {_cell(', '.join(record.get('auth', [])) or '—')} | {', '.join(modes) or '—'} | "
          f"{', '.join(keys) or '—'} | {', '.join(ignored) or '—'} |")
    w("")

    used = {p for v in verdicts.values() for p in v["lm15"]} | {
        p for v in verdicts.values() for _, p in v["model_rules"]}
    only = sorted(set(matrix) - used)
    w("## lm15 provider strings no upstream entry maps to\n")
    w(", ".join(f"`{p}`" for p in only) + "\n" if only else "None.\n")

    facts = snapshot.get("lm15_facts")
    w("## Claude output ceilings: lm15 against Pi and LiteLLM\n")
    if not facts:
        w("Not captured: run `update` with the lm15-python checkout beside the contract.\n")
    else:
        w(f"lm15 sends a Claude model's output ceiling as `max_tokens` when the caller sets none (MAP-7 rule 6). "
          f"Table from {facts['from']}; any non-Claude name gets {facts['default_max_tokens']}. "
          f"Rows where an upstream value differs; upstream catalogs are not evidence either — "
          f"the Models API receipt decides.\n")
        w(f"*Retired* compares LiteLLM's deprecation date with the fetch date ({snapshot['fetched_on']}); "
          f"a mismatch on a retired model is harmless.\n")
        w("| model | lm15 | Pi | LiteLLM | LiteLLM deprecation | retired |")
        w("|---|---:|---:|---:|---|---|")
        seen: dict[str, dict[str, Any]] = {}
        for key in ("pi:anthropic", "litellm:anthropic"):
            for model in providers.get(key, {}).get("models", []):
                if KIND_SURFACE.get(model["kind"]) == "complete":
                    slot = seen.setdefault(model["id"], {})
                    slot[key.split(":")[0]] = model.get("max_output")
                    if model.get("deprecation"):
                        slot["deprecation"] = model["deprecation"]
        mismatches = 0
        for model_id, slot in sorted(seen.items()):
            ours = claude_ceiling(facts["claude_output_ceilings"], model_id)
            theirs = {v for k, v in slot.items() if k in ("pi", "litellm") and v is not None}
            if ours is not None and theirs and theirs != {ours}:
                mismatches += 1
                deprecation = slot.get("deprecation", "")
                retired = "yes" if deprecation and deprecation <= snapshot["fetched_on"] else "**no**"
                w(f"| `{model_id}` | {ours} | {slot.get('pi', '—')} | {slot.get('litellm', '—')} | "
                  f"{deprecation} | {retired} |")
        if not mismatches:
            w("| (none) | | | | | |")
        w("")

    w("## Out of scope and not providers\n")
    w("<details><summary>List</summary>\n")
    w("| upstream | status | why |")
    w("|---|---|---|")
    for key, record in sorted(providers.items(), key=lambda kv: (kv[1]["source"], kv[1]["id"])):
        verdict = verdicts[key]
        if verdict["status"] in ("out-of-scope", "not-a-provider"):
            why = verdict["note"] + (" (automatic)" if verdict["auto"] else "")
            w(f"| {record['source']}:`{record['id']}` | {verdict['status']} | {_cell(why)} |")
    w("\n</details>\n")
    return "\n".join(out), tsv


# ─── commands ───────────────────────────────────────────────────────


def _paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    data = Path(args.data_dir)
    return data / "snapshot.json", data / "classification.json", data / "REPORT.md", data / "models.tsv"


def _auth_spec(args: argparse.Namespace) -> str:
    path = Path(args.auth_spec)
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _load_snapshot(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise LandscapeError(f"{path} does not exist — run `update` first")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def regenerate(args: argparse.Namespace) -> list[str]:
    snapshot_path, class_path, report_path, tsv_path = _paths(args)
    report, tsv = render(_load_snapshot(snapshot_path), load_classification(class_path), load_matrix(Path(args.matrix)),
                         _auth_spec(args))
    _write(report_path, report)
    _write(tsv_path, tsv)
    return [str(report_path), str(tsv_path)]


def describe_changes(old: dict[str, Any] | None, new: dict[str, Any]) -> list[str]:
    if not old:
        return [f"first snapshot: {len(new['providers'])} upstream providers"]
    lines = []
    for source in ("pi", "litellm"):
        before, after = old["sources"][source]["version"], new["sources"][source]["version"]
        if before != after:
            lines.append(f"{source}: {before} -> {after}")
    for key in sorted(set(new["providers"]) - set(old["providers"])):
        lines.append(f"+ provider {key} ({len(new['providers'][key]['models'])} models)")
    for key in sorted(set(old["providers"]) - set(new["providers"])):
        lines.append(f"- provider {key}")
    for key in sorted(set(old["providers"]) & set(new["providers"])):
        a = {m["id"] for m in old["providers"][key]["models"]}
        b = {m["id"] for m in new["providers"][key]["models"]}
        if a != b:
            added, removed = sorted(b - a), sorted(a - b)
            sample = ", ".join(added[:4]) + (" …" if len(added) > 4 else "")
            lines.append(f"~ {key}: +{len(added)} -{len(removed)} models" + (f" (+ {sample})" if added else ""))
    return lines or ["no upstream change"]


def cmd_update(args: argparse.Namespace) -> int:
    snapshot_path, _, _, _ = _paths(args)
    pi_source, pi_files = (read_pi_package(Path(args.pi_package)) if args.pi_package else fetch_pi(args.pi_version))
    ll_source, ll_files = (read_litellm_dir(Path(args.litellm_dir)) if args.litellm_dir
                           else fetch_litellm(args.litellm_version, args.litellm_ref))
    providers: dict[str, Any] = {}
    for pid, record in sorted(extract_pi(pi_files).items()):
        providers[f"pi:{pid}"] = record
    for pid, record in sorted(extract_litellm(ll_files).items()):
        providers[f"litellm:{pid}"] = record
    snapshot = {
        "_doc": "Generated by tools/provider_landscape.py update. Do not edit; see research/landscape/README.md.",
        "fetched_on": args.today or _dt.date.today().isoformat(),
        "sources": {"pi": pi_source, "litellm": ll_source},
        "lm15_facts": lm15_python_facts(Path(args.lm15_python)),
        "providers": providers,
    }
    old = json.loads(snapshot_path.read_text(encoding="utf-8")) if snapshot_path.is_file() else None
    _write(snapshot_path, dump_json(snapshot))
    for line in describe_changes(old, snapshot):
        print(line)
    written = regenerate(args)
    print("wrote", snapshot_path, *written)
    problems = evaluate(snapshot, load_classification(_paths(args)[1]), load_matrix(Path(args.matrix)))
    for problem in problems:
        print(problem)
    if problems:
        print(f"{len(problems)} classification problem(s): review them, then run `check`.")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    print("wrote", *regenerate(args))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    snapshot_path, class_path, report_path, tsv_path = _paths(args)
    snapshot, classes, matrix = _load_snapshot(snapshot_path), load_classification(class_path), load_matrix(Path(args.matrix))
    problems = evaluate(snapshot, classes, matrix)
    report, tsv = render(snapshot, classes, matrix, _auth_spec(args))
    for path, text in ((report_path, report), (tsv_path, tsv)):
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            problems.append(f"OUTDATED {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: "
                            f"run `python3 tools/provider_landscape.py report`")
    for problem in problems:
        print("FAIL", problem)
    sources = snapshot["sources"]
    print(f"provider landscape: {len(snapshot['providers'])} upstream providers "
          f"(pi {sources['pi']['version']}, litellm {sources['litellm']['version']}, fetched "
          f"{snapshot['fetched_on']}), {len(matrix)} lm15 providers, {len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_suggest(args: argparse.Namespace) -> int:
    snapshot_path, class_path, _, _ = _paths(args)
    snapshot, classes, matrix = _load_snapshot(snapshot_path), load_classification(class_path), load_matrix(Path(args.matrix))
    lm15_norm = {norm(p): p for p in matrix}
    stubs: dict[str, Any] = {}
    for key, record in sorted(snapshot["providers"].items()):
        if key in classes or auto_status(record):
            continue
        match = lm15_norm.get(norm(record["id"]))
        hint = (record.get("name") or record["id"]) + " — " + _counts(record["models"])
        if record.get("lm15_wire"):
            hint += "; wire: " + ", ".join(record["lm15_wire"])
        stubs[key] = ({"status": "supported", "lm15": [match], "_review": hint} if match
                      else {"status": "missing", "_review": hint})
    print(json.dumps(stubs, indent=2, ensure_ascii=False))
    print(f"# {len(stubs)} stub(s). Review each, drop `_review`, paste into classification.json.", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--data-dir", default=str(DATA))
    parser.add_argument("--matrix", default=str(MATRIX))
    parser.add_argument("--auth-spec", default=str(AUTH_SPEC), help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    update = sub.add_parser("update", help="fetch upstream, rewrite snapshot, regenerate")
    update.add_argument("--pi-version", help="npm version of @earendil-works/pi-ai (default: latest)")
    update.add_argument("--pi-package", help="read an installed pi-ai package directory instead of npm")
    update.add_argument("--litellm-version", help="PyPI version of litellm (default: latest)")
    update.add_argument("--litellm-ref", help="git ref to read LiteLLM files from (default: v<version>)")
    update.add_argument("--litellm-dir", help="read an installed `litellm` package directory instead")
    update.add_argument("--lm15-python", default=str(DEFAULT_LM15_PYTHON))
    update.add_argument("--today", help=argparse.SUPPRESS)
    sub.add_parser("report", help="regenerate REPORT.md and models.tsv (offline)")
    sub.add_parser("check", help="offline consistency gate (exit 1 on problems)")
    sub.add_parser("suggest", help="print classification stubs for unclassified providers")
    args = parser.parse_args(argv)
    handler = {"update": cmd_update, "report": cmd_report, "check": cmd_check, "suggest": cmd_suggest}[args.command]
    try:
        return handler(args)
    except LandscapeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
