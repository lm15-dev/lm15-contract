#!/usr/bin/env python3
"""Provider survey kit: from a candidate provider to a reviewed draft in an hour.

For a server that speaks the Chat Completions wire (playbooks/provider.md
kind A), before lm15 has a registry row for it:

    python3 research/providers/survey.py init <id>          # candidate.json + dossier skeleton, prefilled from the landscape
    python3 research/providers/survey.py models <id> --env-file ../.env   # GET /models, to pick the model roles
    python3 research/providers/survey.py run <id> --env-file ../.env [--dry-run] [--only a,b]
    python3 research/providers/survey.py report <id> [--compare <preset>]

``run`` sends a fixed battery of ~40 small requests (research/providers/
_survey_rules.py PROBES) as a DECLARED provider — raw bodies, so what is
recorded is the server's behaviour, not lm15's — through the same machinery
as every capture (_capture.py: redaction, exchange hashes, receipts). Receipts
go to ``receipts/<date>-<id>-survey/``, append-only by date.

``report`` is offline. It applies the decision rules (_survey_rules.py) to the
receipts, builds the drafted preset as a real ``OpenAIChatCompat`` (an
illegal knob value fails here), parses the recorded replies through lm15 with
it, maps the recorded errors through it, and writes
``research/providers/<id>/SURVEY.md``: each knob with its value, its basis
(decided by the server's behaviour, a convention, not surveyable, or needs
you) and its evidence; the decisions for the maintainer; and the code to
paste — compat preset, base URL, access policy, registry row, litellm prefix,
auth case, secrecy pattern. ``--compare <preset>`` adds a backtest against a
ratified preset: how the kit was validated (changes/2026-10-02-provider-survey-kit.md).

Nothing here edits the registry, the corpus or a preset: the draft is a
proposal a person reviews, then the playbook's steps land it with live
captures (``_inference_hosts.run``) as for any provider.

Credentials: the environment, or ``--env-file`` (simple assignments, never
executed; the environment wins). Keys are never printed or written.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONTRACT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import _survey_rules as rules  # noqa: E402

SAY = "Say ok."
COUNT = "Count from 1 to 50 separated by spaces."
MATH = "What is 17*23? Reply with just the number."
WEATHER_TOOL = {"type": "function", "function": {
    "name": "get_weather", "description": "Get current weather for a city",
    "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}
PLACE_FORMAT = {"type": "json_schema", "json_schema": {"name": "place", "strict": True, "schema": {
    "type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
    "required": ["city", "country"], "additionalProperties": False}}}
CODE_WORD_TRACE = (f"The user's hidden code word is {rules.CODE_WORD}. I must mention the code word in my "
                   "final answer. Now call get_weather for Paris.")
LONG_SYSTEM = "You are a helpful assistant who answers briefly. " * 60
SURVEY_ORIGIN = "https://lm15.dev"
# A survey request that has not answered in this long is recorded as a timeout
# and the survey moves on; lm15's own default (600 s per read) suits a slow
# local model, not a battery of small probes (a DeepInfra request hung for 13
# minutes on 2026-10-02).
PROBE_TIMEOUT_S = 120.0
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0 Safari/537.36"


def candidate_dir(pid: str) -> Path:
    return HERE / pid


def load_spec(pid: str) -> dict[str, Any]:
    path = candidate_dir(pid) / "candidate.json"
    if not path.is_file():
        sys.exit(f"{path.relative_to(CONTRACT)} does not exist: run `survey.py init {pid}` first")
    spec = json.loads(path.read_text(encoding="utf-8"))
    problems = rules.validate_spec(spec)
    if problems:
        sys.exit(f"{path.relative_to(CONTRACT)}:\n  " + "\n  ".join(problems))
    return spec


def load_env(path: Path | None) -> None:
    """Simple assignments only, never executed; the environment wins."""
    if path is None or not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line[7:] if line.startswith("export ") else line
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        tokens = shlex.split(value, comments=True)
        if key.strip().isidentifier() and len(tokens) == 1:
            os.environ.setdefault(key.strip(), tokens[0])


# ─── init ────────────────────────────────────────────────────────────


def cmd_init(args: argparse.Namespace) -> int:
    pid = args.id
    folder = candidate_dir(pid)
    path = folder / "candidate.json"
    if path.exists() and not args.force:
        sys.exit(f"{path.relative_to(CONTRACT)} exists (--force to rewrite)")
    snapshot = json.loads((CONTRACT / "research" / "landscape" / "snapshot.json").read_text(encoding="utf-8"))["providers"]
    classes = json.loads((CONTRACT / "research" / "landscape" / "classification.json").read_text(encoding="utf-8"))["providers"]
    service = args.service or pid
    upstream = {k: v for k, v in snapshot.items()
                if classes.get(k, {}).get("service") == service or rules_norm(v["id"]) == rules_norm(pid)}
    # The entry spelled like the provider first (litellm `mistral`, not `codestral`).
    ranked = sorted(upstream.items(), key=lambda kv: rules_norm(kv[1]["id"]) != rules_norm(pid))
    pi = next((v for k, v in ranked if k.startswith("pi:")), None)
    ll = next((v for k, v in ranked if k.startswith("litellm:")), None)
    # Only a Chat Completions root: Pi entries on that wire, LiteLLM's openai_like table.
    chat_urls = [u for v in upstream.values() for u in v.get("base_urls", [])
                 if "{" not in u and ("openai-completions" in v.get("wires", []) or "openai_like" in v.get("origins", []))]
    env_keys = [k for v in upstream.values() for k in v.get("env_keys", [])]
    hints = sorted({m["id"] for v in upstream.values() for m in v["models"] if m["kind"] in ("chat", "completion")})
    spec = {
        "id": pid,
        "name": (pi or ll or {}).get("name") or pid,
        "dialect": "openai-chat",
        "base_url": chat_urls[0] if chat_urls else None,
        "env_key": env_keys[0] if env_keys else f"{pid.upper().replace('-', '_')}_API_KEY",
        "console_url": None,
        "terms_url": None,
        "litellm_prefix": ll["id"] if ll else None,
        "models": {"plain": None, "reasoner": None, "off": None, "replayer": None, "always_on": None},
        "_review": [
            "Every value prefilled here comes from Pi or LiteLLM (research/landscape/snapshot.json) and is NOT evidence: "
            "confirm base_url and env_key in the provider's own docs.",
            "models: plain = a non-reasoning instruct model; reasoner = a model with a reasoning dial; off = a reasoning "
            "model that can stop reasoning (or null); replayer = the model for the replay probe (defaults to reasoner); "
            "always_on = a model that cannot stop reasoning (or null). `survey.py models` lists what the server serves.",
            "Delete this _review list once the values are confirmed.",
        ],
        "_upstream": {"keys": sorted(upstream), "base_urls": sorted(set(chat_urls)), "env_keys": sorted(set(env_keys)),
                      "model_hints": hints[:40]},
    }
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme = folder / "README.md"
    if not readme.exists():
        readme.write_text(DOSSIER.format(name=spec["name"], id=pid, date=time.strftime("%Y-%m-%d")), encoding="utf-8")
    print(f"wrote {path.relative_to(CONTRACT)}" + ("" if readme.exists() else f" and {readme.relative_to(CONTRACT)}"))
    print(f"upstream: {', '.join(sorted(upstream)) or 'none found — fill every field from the docs'}")
    return 0


def rules_norm(name: str) -> str:
    key = re.sub(r"[^a-z0-9]", "", name.lower())
    return key[:-2] if key.endswith("ai") and len(key) > 4 else key


DOSSIER = """# {name} — provider dossier

| State | Date | Evidence |
|---|---|---|
| candidate | {date} | `candidate.json` (survey kit) |
| researched | | `scrapes/{id}/`; terms and privacy frozen under `sources/`; the terms verdict below |
| surveyed | | `receipts/<date>-{id}-survey/`; `SURVEY.md` |
| implemented | | registry row, access policy, compat preset in lm15-python |
| offline-conformant | | support-matrix row; auth case; tables exported; every SDK green at the pin |
| live-verified | | `receipts/<date>-{id}/`, cases, error envelopes, the change entry |
| supported | | the change entry ratified |

## Identity

- lm15 provider string: `{id}`. (Fill from the docs: service, base URL, console, env key, what is not registered.)

## Terms-of-service verdict

TODO before any live capture: what the terms forbid recording, whether a third-party client may use the key,
where data is stored. Sources frozen under `sources/` with sha256 (playbooks/provider.md § 3).

## Open items
"""


# ─── the declared provider the survey talks to ───────────────────────


def survey_capture(spec: dict[str, Any], *, dry_run: bool):
    from urllib.parse import urlsplit

    from _capture import Capture
    from lm15.compat import OpenAIChatCompat
    from lm15.features import AccessPolicy, EndpointSupport
    from lm15.providers import OpenAIChatLM

    class SurveyCapture(Capture):
        """A Capture whose adapter is a declared provider built from the
        candidate spec: no registry row exists yet."""

        def send(self, treq):
            from dataclasses import replace

            return super().send(replace(treq, connect_timeout=min(treq.connect_timeout or 30.0, 30.0),
                                        read_timeout=PROBE_TIMEOUT_S, write_timeout=PROBE_TIMEOUT_S))

        def probe(self, name, request=None, **kwargs):
            row = super().probe(name, request, **kwargs)
            if "error" in row and not self.dry_run:
                # No reply (a timeout, a dropped connection): recorded as the
                # result, so the rules read "no answer", never a stale file.
                self.write_receipt(f"probe-{name}.json", {"status": None, "error": row["error"], "body": None,
                                                          "timestamp": time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())})
            return row

        def lm(self, model_key=None, *, clock=None, credential=None, compat=None):
            key = credential if credential is not None else (model_key if model_key is not None else self.key())
            if isinstance(key, str) and key:
                self._secret_values.add(key)
            access = AccessPolicy(provider=spec["id"], supports=EndpointSupport(complete=True, stream=True, models=True),
                                  auth_modes=("bearer",), env_keys=(spec["env_key"],), base_url=spec["base_url"])
            return OpenAIChatLM(api_key=key, base_url=spec["base_url"], access=access,
                                compat=compat or OpenAIChatCompat(instruction_role="system", max_tokens_field="max_tokens",
                                                                  stream_usage="include"))

    cap = SurveyCapture(spec["id"], env_var=spec["env_key"], default_model=spec["models"]["plain"],
                        host=urlsplit(spec["base_url"]).netloc, change_slug=f"{spec['id']}-live")
    cap.receipts = CONTRACT / "receipts" / f"{cap.date}-{spec['id']}-survey"
    cap.dry_run = dry_run
    return cap


# ─── run ─────────────────────────────────────────────────────────────


def chat(model: str, messages: list[dict], cap_field: str, cap: int = 200, **extra: Any) -> dict:
    return {"model": model, "messages": messages, cap_field: cap, **extra}


def user(text: str) -> list[dict]:
    return [{"role": "user", "content": text}]


def replay_body(model: str, field_name: str | None, cap_field: str) -> dict:
    assistant: dict[str, Any] = {"role": "assistant", "content": "", "tool_calls": [
        {"id": "call_probe", "type": "function", "function": {"name": "get_weather", "arguments": "{\"city\":\"Paris\"}"}}]}
    if field_name:
        assistant[field_name] = CODE_WORD_TRACE
    return chat(model, [{"role": "user", "content": "What's the weather in Paris?"}, assistant,
                        {"role": "tool", "tool_call_id": "call_probe", "content": "22C and sunny"}],
                cap_field, 800, tools=[WEATHER_TOOL])


def battery(spec: dict[str, Any], cap_field: str) -> list[tuple[str, dict, dict]]:
    """(probe name, raw body, probe options) after the two cap probes, in order."""
    m = spec["models"]
    plain, reasoner = m["plain"], m.get("reasoner")
    replayer = m.get("replayer") or reasoner
    sse = {"stream": True, "stream_options": {"include_usage": True}}
    named = {"type": "function", "function": {"name": "get_weather"}}
    b: list[tuple[str, dict, dict]] = [
        ("basic", chat(plain, user(SAY), cap_field, 100), {}),
        ("stream", chat(plain, user(SAY), cap_field, 100, **sse), {"stream": True}),
        ("role-system", chat(plain, [{"role": "system", "content": "Whatever the user says, reply with exactly the word PINEAPPLE."},
                                     *user("Say hello.")], cap_field, 50), {}),
        ("role-developer", chat(plain, [{"role": "developer", "content": "Whatever the user says, reply with exactly the word PINEAPPLE."},
                                        *user("Say hello.")], cap_field, 50), {}),
        ("user-field", chat(plain, user(SAY), cap_field, 50, user="lm15-survey"), {}),
        ("tools", chat(plain, user("What is the weather in Paris? Use the tool."), cap_field, 300, tools=[WEATHER_TOOL]), {}),
        ("stream-tools", chat(plain, user("What is the weather in Paris? Use the tool."), cap_field, 300, tools=[WEATHER_TOOL], **sse),
         {"stream": True}),
        ("tool-choice-required", chat(plain, user(SAY), cap_field, 300, tools=[WEATHER_TOOL], tool_choice="required"), {}),
        ("tool-choice-named", chat(plain, user(SAY), cap_field, 300, tools=[WEATHER_TOOL], tool_choice=named), {}),
        ("tool-choice-none", chat(plain, user("What is the weather in Paris? Use the tool."), cap_field, 300,
                                  tools=[WEATHER_TOOL], tool_choice="none"), {}),
        ("json-schema", chat(plain, user("Name one city and its country."), cap_field, 200, response_format=PLACE_FORMAT), {}),
        ("usage-repeat-1", chat(plain, [{"role": "system", "content": LONG_SYSTEM}, *user(SAY)], cap_field, 20), {}),
        ("usage-repeat-2", chat(plain, [{"role": "system", "content": LONG_SYSTEM}, *user(SAY)], cap_field, 20), {}),
        ("error-auth", chat(plain, user(SAY), cap_field, 10), {"model_key": "lm15-survey-invalid-key"}),
        ("error-model", chat("lm15-survey/no-such-model", user(SAY), cap_field, 10), {}),
    ]
    if reasoner:
        think = lambda **kw: chat(reasoner, user(MATH), cap_field, 1500, **kw)  # noqa: E731
        b += [
            ("effort-low", think(reasoning_effort="low"), {}),
            ("effort-high", think(reasoning_effort="high"), {}),
            ("effort-none", think(reasoning_effort="none"), {}),
            *((f"effort-word-{w}", think(reasoning_effort=w), {}) for w in ("minimal", "medium", "xhigh", "max", "bogus")),
            ("shape-thinking-enabled", think(thinking={"type": "enabled"}), {}),
            ("shape-thinking-disabled", think(thinking={"type": "disabled"}), {}),
            ("shape-reasoning-object", think(reasoning={"effort": "low"}), {}),
            ("tool-choice-required-reasoner", chat(reasoner, user(SAY), cap_field, 600, tools=[WEATHER_TOOL], tool_choice="required"), {}),
        ]
        if m.get("off"):
            b.append(("effort-none-off-model", chat(m["off"], user(MATH), cap_field, 600, reasoning_effort="none"), {}))
        if m.get("always_on"):
            b.append(("effort-none-always-on", chat(m["always_on"], user(MATH), cap_field, 1500, reasoning_effort="none"), {}))
    if replayer:
        b += [(f"replay-{f or 'absent'}-{n}", replay_body(replayer, f, cap_field), {})
              for f in ("reasoning_content", "reasoning", None) for n in (1, 2, 3)]
    return b


def preflight(cap, spec: dict[str, Any]) -> dict:
    """A browser's CORS preflight for POST /chat/completions from lm15.dev (the website's question)."""
    url = spec["base_url"] + "/chat/completions"
    # A browser's user agent: edge firewalls (Cloudflare) answer 403 to
    # Python's default one, which says nothing about what a browser gets.
    req = urllib.request.Request(url, method="OPTIONS", headers={
        "User-Agent": BROWSER_UA, "Origin": SURVEY_ORIGIN, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type"})
    if cap.dry_run:
        print(f"OPTIONS {url} (Origin: {SURVEY_ORIGIN})")
        return {"probe": "cors", "status": 0}
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            status, headers = r.status, {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as exc:
        status, headers = exc.code, {k.lower(): v for k, v in exc.headers.items()}
    except OSError as exc:
        return {"probe": "cors", "error": str(exc)}
    kept = {k: v for k, v in headers.items() if k.startswith("access-control-")}
    cap.write_receipt("probe-cors.json", {"sent": {"method": "OPTIONS", "url": url, "headers": {"Origin": SURVEY_ORIGIN}},
                                          "status": status, "headers": kept, "timestamp": time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())})
    return {"probe": "cors", "status": status, "summary": kept.get("access-control-allow-origin", "no allow-origin")}


def models_probe(cap) -> dict:
    """GET /models, kept whole up to 300 KB, else as its ids in the same shape."""
    adapter = cap.lm()
    treq = adapter._models_request()
    status, raw, ts, _ = cap.send(treq)
    if cap.dry_run:
        return {"probe": "models", "status": status}
    try:
        body: Any = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        body = raw.decode("utf-8", "replace")[:4000]
    if len(raw) > 300_000 and isinstance(body, (dict, list)):
        entries = body if isinstance(body, list) else body.get("data", [])
        ids = [{"id": e.get("id")} for e in entries if isinstance(e, dict)]
        body = ids if isinstance(body, list) else {"data": ids, "_reduced": f"{len(raw)} bytes, ids kept"}
    cap.write_receipt("probe-models.json", {"sent": cap.wire_block(treq), "status": status, "body": body, "timestamp": ts})
    n = len(body) if isinstance(body, list) else len(body.get("data", [])) if isinstance(body, dict) else 0
    return {"probe": "models", "status": status, "summary": f"{n} entries"}


def cmd_models(args: argparse.Namespace) -> int:
    load_env(args.env_file)
    spec = json.loads((candidate_dir(args.id) / "candidate.json").read_text(encoding="utf-8"))
    for key in ("base_url", "env_key"):
        if not spec.get(key):
            sys.exit(f"candidate.json: {key} is required to list models")
    spec.setdefault("models", {})["plain"] = spec["models"].get("plain") or "unset"
    cap = survey_capture(spec, dry_run=args.dry_run)
    adapter = cap.lm()
    status, raw, _, _ = cap.send(adapter._models_request())
    if cap.dry_run:
        return 0
    body = json.loads(raw.decode("utf-8", "replace")) if raw else None
    entries = body if isinstance(body, list) else (body or {}).get("data", [])
    print(f"HTTP {status}: {len(entries)} models")
    for e in entries:
        if isinstance(e, dict):
            print(" ", e.get("id"), *(f"{k}={e[k]}" for k in ("owned_by", "type", "context_length") if k in e))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    load_env(args.env_file)
    spec = load_spec(args.id)
    cap = survey_capture(spec, dry_run=args.dry_run)
    cap.key()  # fail early, never printed
    only = set(args.only.split(",")) if args.only else None
    want = lambda name: only is None or name in only  # noqa: E731
    plain = spec["models"]["plain"]
    rows: list[dict] = []
    # The two caps run first: the field that works carries every later probe.
    # A partial run (--only) reuses today's caps when they are recorded.
    for field_name in ("max_completion_tokens", "max_tokens"):
        name = f"cap-{field_name}"
        if only is None or want(name) or not (cap.receipts / f"probe-{name}.json").is_file():
            rows.append(cap.probe(name, raw_body=chat(plain, user(COUNT), field_name, 8)))
    cap_field = "max_tokens"
    if not cap.dry_run:
        mct = json.loads((cap.receipts / "probe-cap-max_completion_tokens.json").read_text(encoding="utf-8"))
        cap_field = "max_completion_tokens" if rules.capped(mct) else "max_tokens"
    for name, body, opts in battery(spec, cap_field):
        if want(name):
            rows.append(cap.probe(name, raw_body=body, **opts))
    if want("stream") and not cap.dry_run:
        rec = json.loads((cap.receipts / "probe-stream.json").read_text(encoding="utf-8"))
        if rules.loud(rec):
            rows.append(cap.probe("stream-plain", raw_body=chat(plain, user(SAY), cap_field, 100, stream=True), stream=True))
    if want("models"):
        rows.append(models_probe(cap))
    if want("cors"):
        rows.append(preflight(cap, spec))
    if not cap.dry_run and only is None:
        cap.write_receipt("survey.json", {"spec": {k: v for k, v in spec.items() if not k.startswith("_")},
                                          "cap_field": cap_field, "probes": [r.get("probe") for r in rows],
                                          "date": cap.date})
    print(f"\nreceipts → {cap.receipts.relative_to(CONTRACT)}\n\n| probe | status | detail |\n|---|---|---|")
    for r in rows:
        print(f"| {r.get('probe')} | {r.get('status', '-')} | {cap.redact(str(r.get('summary') or r.get('error') or ''))[:120]} |")
    return 0


# ─── sweep ───────────────────────────────────────────────────────────


def cmd_sweep(args: argparse.Namespace) -> int:
    """The per-model probes across many models: forced tool choice (5 probes)
    and reasoning off (1), for the model_overrides a host with many model
    families needs. Receipts join the day's survey folder as sweep-<model>-<mode>."""
    load_env(args.env_file)
    spec = load_spec(args.id)
    models = [m for m in (args.models or "").split(",") if m]
    if args.models_file:
        models += [line.strip() for line in Path(args.models_file).read_text(encoding="utf-8").splitlines()
                   if line.strip() and not line.startswith("#")]
    if not models:
        sys.exit("--models a,b or --models-file FILE")
    probes = set(args.probes.split(","))
    cap = survey_capture(spec, dry_run=args.dry_run)
    cap.key()
    folder = cap.receipts
    cap_field = "max_tokens"
    meta_path = folder / "survey.json"
    if meta_path.is_file():
        cap_field = json.loads(meta_path.read_text(encoding="utf-8")).get("cap_field", cap_field)
    suffix = f"-r{args.repeat}" if args.repeat > 1 else ""
    print("| model | forced tool choice | reasoning off |\n|---|---|---|")
    for model in models:
        slug = rules.sweep_slug(model) + suffix
        per: dict[str, dict | None] = {}
        if "tool-choice" in probes:
            for mode, (choice, question) in rules.SWEEP_TOOL_MODES.items():
                name = f"sweep-{slug}-{mode}"
                cap.probe(name, raw_body=chat(model, user(question), cap_field, 2000, tools=[WEATHER_TOOL], tool_choice=choice))
                per[f"sweep-{mode}"] = None if cap.dry_run else json.loads((folder / f"probe-{name}.json").read_text(encoding="utf-8"))
        off = None
        if "reasoning-off" in probes:
            name = f"sweep-{slug}-effort-none"
            cap.probe(name, raw_body=chat(model, user(MATH), cap_field, 1500, reasoning_effort="none"))
            off = None if cap.dry_run else json.loads((folder / f"probe-{name}.json").read_text(encoding="utf-8"))
        if cap.dry_run:
            continue
        tool = rules.sweep_tool_choice(per) if "tool-choice" in probes else ("not sent", "")
        print(f"| `{model}` | {tool[0]} | {rules.sweep_reasoning_off(off)[0] if off is not None else 'not sent'} |", flush=True)
    if not cap.dry_run:
        index = folder / "sweep.json"
        known = json.loads(index.read_text(encoding="utf-8"))["models"] if index.is_file() else []
        index_data = json.loads(index.read_text(encoding="utf-8")) if index.is_file() else {}
        cap.write_receipt("sweep.json", {"models": list(dict.fromkeys(known + models)), "probes": sorted(probes),
                                         "samples": max(args.repeat, index_data.get("samples", 1))})
    return 0


def sweep_results(folder: Path, receipts: dict[str, dict]) -> dict[str, dict[str, tuple[str, str]]]:
    """Per model, every sample (`--repeat N` adds -rN probes), combined worst-first."""
    index = folder / "sweep.json"
    if not index.is_file():
        return {}
    meta = json.loads(index.read_text(encoding="utf-8"))
    out: dict[str, dict[str, tuple[str, str]]] = {}
    for model in meta["models"]:
        tool_samples, off_samples = [], []
        for n in range(1, int(meta.get("samples", 1)) + 1):
            slug = rules.sweep_slug(model) + (f"-r{n}" if n > 1 else "")
            per = {f"sweep-{mode}": receipts.get(f"sweep-{slug}-{mode}") for mode in rules.SWEEP_TOOL_MODES}
            if any(per.values()):
                tool_samples.append(rules.sweep_tool_choice(per))
            if f"sweep-{slug}-effort-none" in receipts:
                off_samples.append(rules.sweep_reasoning_off(receipts[f"sweep-{slug}-effort-none"]))
        row: dict[str, tuple[str, str]] = {}
        if tool_samples:
            row["tool_choice"] = rules.sweep_worst(tool_samples)
        if off_samples:
            row["reasoning_off"] = rules.sweep_worst(off_samples)
        out[model] = row
    return out


# ─── report ──────────────────────────────────────────────────────────


def load_receipts(folder: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(folder.glob("probe-*.json")):
        out[path.stem[len("probe-"):]] = json.loads(path.read_text(encoding="utf-8"))
    return out


def latest_survey(pid: str) -> Path:
    found = sorted((CONTRACT / "receipts").glob(f"*-{pid}-survey"))
    if not found:
        sys.exit(f"no receipts/<date>-{pid}-survey folder: run `survey.py run {pid}` first")
    return found[-1]


def lm15_checks(spec: dict, receipts: dict, knobs: dict, overrides: list) -> tuple[list[str], dict[str, str]]:
    """Build the draft as a real compat, parse the recorded replies through it,
    and map the recorded errors. Problems are findings, never exceptions."""
    import _capture  # noqa: F401  (puts the sibling lm15-python checkout on the path)
    from lm15 import Message, Request
    from lm15.compat import OpenAIChatCompat
    from lm15.providers.base import HttpResponse
    from lm15.vet import _parse_stream_body

    problems: list[str] = []
    try:
        compat = OpenAIChatCompat(**knobs, model_overrides=tuple((p, k) for p, k in overrides))
    except (TypeError, ValueError) as exc:
        return [f"the drafted preset is not a legal OpenAIChatCompat: {exc}"], {}
    cap = survey_capture(spec, dry_run=True)
    adapter = cap.lm(model_key="vet-parse-only", compat=compat)
    for name, stream in (("basic", False), ("tools", False), ("json-schema", False), ("stream", True), ("stream-tools", True)):
        rec = receipts.get(name)
        if not rules.ok(rec):
            continue
        req = Request(model=spec["models"]["plain"], messages=(Message.user("x"),))
        body = rec["body"] if isinstance(rec["body"], str) else json.dumps(rec["body"])
        try:
            if stream:
                events = _parse_stream_body(adapter, req, body.encode())
                if not any(getattr(e, "type", "") == "end" for e in events):
                    problems.append(f"{name}: lm15 parsed {len(events)} events and no end event")
            else:
                resp = adapter.parse_response(req, HttpResponse(200, "OK", [], body.encode()))
                unmapped = (resp.provider_data or {}).get("_lm15_unmapped") if isinstance(resp.provider_data, dict) else None
                if unmapped:
                    problems.append(f"{name}: lm15 parsed the reply but left fields unmapped: {unmapped}")
                if name == "tools" and not resp.tool_calls:
                    problems.append("tools: the reply was 200 but lm15 found no tool call in it")
        except Exception as exc:  # a parse failure is the finding
            problems.append(f"{name}: lm15 could not parse the recorded reply: {type(exc).__name__}: {exc}")
    errors: dict[str, str] = {}
    for name, expect in (("error-auth", "AuthError"), ("error-model", "UnsupportedModelError")):
        rec = receipts.get(name)
        if rec is None or (rec.get("status") or 0) < 400:
            errors[name] = f"not an error reply ({rules.say(rec)})"
            continue
        body = rec["body"] if isinstance(rec["body"], str) else json.dumps(rec["body"])
        err = adapter.normalize_error(rec["status"], body)
        got = type(err).__name__
        errors[name] = got if got == expect else f"{got} (expected {expect}: " + (
            "a MAP-15 form in spec/model-not-found.json, from this receipt" if name == "error-model" else "check the mapping") + ")"
    return problems, errors


def py(value: Any) -> str:
    if isinstance(value, list):
        return "(" + ", ".join(py(v) for v in value) + ("," if len(value) == 1 else "") + ")"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{py(k)}: {py(v)}" for k, v in value.items()) + "}"
    return json.dumps(value) if isinstance(value, str) else repr(value)


def cmd_report(args: argparse.Namespace) -> int:
    spec = load_spec(args.id)
    folder = Path(args.receipts) if args.receipts else latest_survey(args.id)
    receipts = load_receipts(folder)
    meta = json.loads((folder / "survey.json").read_text(encoding="utf-8")) if (folder / "survey.json").is_file() else {}
    findings = rules.analyze(receipts, spec["models"])
    knobs, overrides = rules.draft_preset(findings)
    swept = sweep_results(folder, receipts)
    sweep_undecided: list[str] = []
    if swept:
        swept_overrides, sweep_undecided = rules.sweep_overrides(knobs.get("forced_tool_choice"), swept)
        merged = dict(overrides)
        for model, extra in swept_overrides:
            merged.setdefault(model, {}).update(extra)
        overrides = sorted(merged.items())
    parse_problems, errors = lm15_checks(spec, receipts, knobs, overrides)
    facts = rules.facts(receipts)
    pid, const = spec["id"], spec["id"].upper().replace("-", "_")
    rel = folder.relative_to(CONTRACT)
    out: list[str] = []
    w = out.append
    w(f"# {spec['name']} — survey report\n")
    w(f"Generated by `research/providers/survey.py report {pid}` from `{rel}/` "
      f"({len(receipts)} probe receipts, token field `{meta.get('cap_field', '?')}`). Do not edit; re-run the report.\n")
    w(f"- Base URL `{spec['base_url']}`, key `{spec['env_key']}`; models: " +
      ", ".join(f"{k} `{v}`" for k, v in spec["models"].items() if v) + "\n")
    w("A **decided** value follows from the server's recorded behaviour under the rules in "
      "`research/providers/_survey_rules.py`; a **convention** is what every Chat Completions preset sets; "
      "**not surveyable** values come from the docs or another runner; **needs you** means the probes could not "
      "settle it. Nothing here is ratified: the draft is reviewed, then captured live (playbooks/provider.md § 3).\n")
    w("## Findings\n")
    w("| knob | drafted | basis | evidence |\n|---|---|---|---|")
    for f in findings:
        value = f"`{f.value}`" if f.value is not None else "(inherit)"
        if f.override:
            value += f"; `{f.override[0]}`: `{f.override[1]}`"
        w(f"| `{f.knob}` | {value} | {f.status.replace('-', ' ')} | {f.note.replace('|', '/')} |")
    w("")
    asks = [f for f in findings if f.status == rules.NEEDS_YOU] + [
        rules.Finding("lm15", None, rules.NEEDS_YOU, [], p) for p in parse_problems]
    asks += [rules.Finding(n, None, rules.NEEDS_YOU, [], f"error mapping: {v}") for n, v in errors.items()
             if not v.endswith("Error") or "expected" in v]
    asks += [rules.Finding("sweep", None, rules.NEEDS_YOU, [], u) for u in sweep_undecided]
    if swept:
        w(f"## Sweep: {len(swept)} models\n")
        samples = json.loads((folder / "sweep.json").read_text(encoding="utf-8")).get("samples", 1)
        w("Per model: a forced tool choice (required, named, none, with an unprompted control and a second try) and "
          f"reasoning off; {samples} sample(s) per model, the worst deciding. Overrides are drafted against the "
          "provider-wide value above." + (" **One sample is not enough: models flip between runs (DeepInfra GLM-4.7 "
          "and Seed-2.0-mini, 2026-10-02). Run `sweep --repeat 2` before trusting this table.**" if samples < 2 else "") + "\n")
        w("| model | forced tool choice | reasoning off |\n|---|---|---|")
        for model, row in swept.items():
            tool, off = row.get("tool_choice", ("-", "")), row.get("reasoning_off", ("-", ""))
            w(f"| `{model}` | {tool[0]} ({tool[1]}) | {off[0]} |")
        w("")
    w("## Decisions for you\n")
    w("\n".join(f"- **{a.knob}**: {a.note}" for a in asks) + "\n" if asks else "None: every surveyable knob was decided.\n")
    w("## Other facts\n")
    w(f"- Model listing: {'GET /models answers ' + str(facts['models']['count']) + ' entries (' + facts['models']['shape'] + ')' if facts['models']['listed'] else 'not a list (' + str(facts['models']['status']) + '): models=false'}")
    w(f"- Cached tokens on a repeated prompt: nested `{facts['cached_tokens']['nested']}`, flat `{facts['cached_tokens']['flat']}`")
    w(f"- Browser (CORS preflight from {SURVEY_ORIGIN}): " + (
        f"allow-origin `{facts['cors']['allow_origin']}` — the website can call it directly" if facts['cors']['allow_origin']
        else f"no allow-origin (HTTP {facts['cors']['status']}) — the website needs the relay"))
    w(f"- Errors through the draft: bad key → {errors.get('error-auth')}; unknown model → {errors.get('error-model')}")
    w(f"- Tool call: {facts['tools']}\n")
    if args.compare:
        sys.path.insert(0, str(CONTRACT.parent / "lm15-python"))
        tables = json.loads((CONTRACT / "tables" / "providers.json").read_text(encoding="utf-8"))
        ratified = tables["compat"]["chat"].get(args.compare)
        if ratified is None:
            sys.exit(f"no chat preset {args.compare!r} in tables/providers.json")
        rows = rules.compare(findings, ratified)
        counts = {v: sum(1 for r in rows if r["verdict"] == v) for v in ("agree", "equivalent", "differ", "needs you", "not surveyable")}
        w(f"## Backtest against the ratified `{args.compare}` preset\n")
        w(", ".join(f"{n} {v}" for v, n in counts.items()) + ".\n")
        w("| knob | ratified | drafted | verdict |\n|---|---|---|---|")
        for r in rows:
            w(f"| `{r['knob']}` | `{r['ratified']}` | `{r['drafted']}` | {r['verdict']} |")
        w("\nPer-model overrides (a drafted prefix is the surveyed model's exact id; a ratified one may cover its family):\n")
        w("| knob | ratified | drafted | verdict |\n|---|---|---|---|")
        for r in rules.compare_overrides(overrides, ratified.get("model_overrides") or []):
            w(f"| `{r['knob']}` | {r['ratified']} | {r['drafted']} | {r['verdict']} |")
        w("")
    w("## Draft code (review before pasting; playbooks/provider.md § 3)\n")
    knob_lines = "".join(f"        {k}={py(v)},\n" for k, v in knobs.items())
    over = "".join(f"            ({py(p)}, {py(k)}),\n" for p, k in overrides)
    w("`lm15/compat.py` — `OPENAI_CHAT_PRESETS` and `OPENAI_CHAT_PRESET_BASE_URLS`:\n")
    w("```python\n"
      f"    # {spec['name']}: surveyed {meta.get('date', '?')} ({rel}/); live receipts: receipts/<date>-{pid}/.\n"
      f"    {py(pid)}: OpenAIChatCompat(\n{knob_lines}" + (f"        model_overrides=(\n{over}        ),\n" if over else "") + "    ),\n\n"
      f"    {py(pid)}: {py(spec['base_url'])},\n```\n")
    supports = "complete=True, stream=True" + (", models=True" if facts["models"]["listed"] else "")
    w("`lm15/access.py`, `lm15/registry.py`" + (", `lm15/router.py` (litellm prefix)" if spec.get("litellm_prefix") else "") + ":\n")
    w("```python\n"
      f"{const} = AccessPolicy(\n    provider={py(pid)},\n    supports=EndpointSupport({supports}),\n"
      f"    auth_modes=(\"bearer\",),\n    env_keys=({py(spec['env_key'])},),\n    base_url=OPENAI_CHAT_PRESET_BASE_URLS[{py(pid)}],\n)\n\n"
      f"    _chat_bound(\n        _access.{const},\n        console_url={py(spec.get('console_url'))},\n"
      f"        note={py(spec['name'] + ' (Chat Completions dialect)')},\n    ),\n" +
      (f"\n    {py(spec['litellm_prefix'])}: {py(pid)},\n" if spec.get("litellm_prefix") else "") + "```\n")
    auth_case = {"id": f"{pid}-env-selected", "provider": pid, "env": {spec["env_key"]: "SECRET-SENTINEL-DO-NOT-PRINT"},
                 "api_keys_providers": [], "expect": {"configured": True, "steps": [
                     {"kind": "api_keys", "state": "absent"}, {"kind": f"env:{spec['env_key']}", "state": "selected"}]}}
    w("`auth/resolution.json`:\n\n```json\n" + json.dumps(auth_case, indent=2) + "\n```\n")
    prefix = key_prefix(spec["env_key"])
    w("`tools/check_secrecy.py`: " + (f"keys start `{prefix}` — add `(\"{pid} api key\", re.compile(r\"\\b{re.escape(prefix)}[A-Za-z0-9_-]{{20,}}\"))`."
                                      if prefix else "the key has no recognisable prefix: search every capture for the literal key before commit (as DeepInfra).") + "\n")
    w("Then: frozen terms, `_inference_hosts.py` captures (a `Models` declaration from candidate.json), support-matrix row, "
      "`tools/export_provider_tables.py`, router cases for the litellm prefix, the change entry, ratification, ports "
      "(`tools/gen_tables.py`), website (`connections.ts`).\n")
    path = candidate_dir(pid) / "SURVEY.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {path.relative_to(CONTRACT)}: {sum(f.status == rules.DECIDED for f in findings)} decided, "
          f"{len(asks)} for you" + (f"; backtest vs {args.compare}" if args.compare else ""))
    return 0


def key_prefix(env_key: str) -> str | None:
    """The key's non-secret leading tag (`fw_`, `tgp_v1_`, `psk-`), if it has one; never more."""
    value = os.environ.get(env_key, "")
    m = re.match(r"^([A-Za-z]{2,5}(?:_v\d)?[_-])", value)
    return m.group(1) if m and len(value) > 24 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", help="candidate.json and a dossier skeleton, prefilled from the landscape")
    p.add_argument("id")
    p.add_argument("--service", help="the landscape service group, when it differs from the id")
    p.add_argument("--force", action="store_true")
    for name, helptext in (("models", "list the models the server serves"), ("run", "send the probe battery")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("id")
        p.add_argument("--env-file", type=Path)
        p.add_argument("--dry-run", action="store_true", help="print every request; send and write nothing")
        if name == "run":
            p.add_argument("--only", help="comma-separated probe names")
    p = sub.add_parser("sweep", help="per-model probes across many models (forced tool choice, reasoning off)")
    p.add_argument("id")
    p.add_argument("--models", help="comma-separated model ids")
    p.add_argument("--models-file", help="one model id per line")
    p.add_argument("--probes", default="tool-choice,reasoning-off")
    p.add_argument("--repeat", type=int, default=1, help="sample number N (>1 adds -rN probes; every sample is kept and the worst wins)")
    p.add_argument("--env-file", type=Path)
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("report", help="decide the knobs and write SURVEY.md (offline)")
    p.add_argument("id")
    p.add_argument("--receipts", help="a survey receipts folder (default: the latest)")
    p.add_argument("--compare", help="backtest against this ratified chat preset")
    args = parser.parse_args(argv)
    return {"init": cmd_init, "models": cmd_models, "run": cmd_run, "sweep": cmd_sweep, "report": cmd_report}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
