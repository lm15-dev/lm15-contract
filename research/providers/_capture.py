"""Shared machinery for provider live captures — the controlled validator.

A provider's ``capture.py`` declares its cases and probes; this module does
everything else the same way for every provider:

- holds the key (environment by default; cloud entry points may explicitly
  resolve their chain or load the external lab state before a live run),
- builds every wire through the reference adapter exactly as the router
  would (``lm15.vet.adapter_for_provider`` → the registry entry),
- sends it verbatim and writes evidence in the contract's shapes:
  ``cases/<provider>/<feature>.json``, ``bodies/<provider>.<feature>/<ts>.txt``,
  ``errors/cases/<provider>.json``, ``receipts/<date>-<provider>/``,
- ``--dry-run`` prints every wire (key replaced by ``$<ENV_VAR>``) and
  sends nothing, writes nothing.

Usage from a provider script::

    from _capture import Capture, WEATHER
    cap = Capture("zai", env_var="ZAI_API_KEY", default_model="glm-5.3-flash")

    def cases(model, force, want): ...   # call cap.write_case / cap.models_case
    def probes(model, want): ...         # call cap.probe
    cap.main(cases, probes, error_probes=(("unauthenticated", "AuthError"), ...))
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Callable, Iterable

CONTRACT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CONTRACT.parent / "lm15-python"))

from lm15 import FunctionTool, Message, Request, serde  # noqa: E402
from lm15.errors import LM15Error  # noqa: E402
from lm15.providers.base import HttpResponse  # noqa: E402
from lm15.transports import StdlibTransport, TransportRequest  # noqa: E402
from lm15.types import ThinkingPart, ToolCallPart  # noqa: E402
from lm15.vet import _parse_stream_body, _response_result, adapter_for_provider, normalize_transport_request  # noqa: E402

WEATHER = FunctionTool(
    name="get_weather",
    description="Get current weather for a city",
    parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
)


def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())


class Capture:
    def __init__(self, provider: str, *, env_var: str, default_model: str, host: str,
                 settings: dict[str, str] | None = None, change_slug: str | None = None) -> None:
        self.provider = provider
        self.env_var = env_var
        # Cloud-host settings (AUTH-10: region, resource, project…), pinned
        # into every case so the harness rebuilds the same URL.  Never a
        # secret: a resource name or region is not credential material.
        self.settings = dict(settings or {})
        # A SigV4 door signs with the REAL keys on the wire but pins the case
        # with the harness's fixed pair and the capture instant, so the
        # Authorization header in the fixture is what a port must reproduce
        # (auth/sigv4-vectors.json fixed keys; PROTOCOL.md credential/now).
        self.fixture_credential = None  # set by aws_fixture()
        self.credential = None  # a CredentialValue for the wire when the key is not a string (SigV4)
        self.placeholder = f"${env_var}"
        self.default_model = default_model
        self.host = host  # for provenance strings, e.g. "api.deepseek.com"
        self.date = time.strftime("%Y-%m-%d", time.gmtime())
        self.change_entry = f"changes/{self.date}-{change_slug or (provider + '-live')}.md"
        self.receipts = CONTRACT / "receipts" / f"{self.date}-{provider}"
        self.dry_run = False
        self.prepare: Callable[[], None] | None = None
        self._secret_values: set[str] = set()
        self.transport = StdlibTransport()

    # ─── plumbing ────────────────────────────────────────────────────

    def _key_string(self) -> str:
        if self.dry_run:
            return "dry-run-key"
        value = os.environ.get(self.env_var, "")
        if not value:
            sys.exit(f"{self.env_var} is not set; this script never reads a .env file")
        return value

    def key(self):  # type: ignore[override]
        if self.credential is not None:
            return self.credential
        return self._key_string()

    def aws_fixture(self) -> None:
        """Send with the profile's real AWS credentials (lm15's own chain);
        pin every case with the fixed test pair + the capture instant."""
        from lm15.credentials import AwsCredentials
        from lm15.cloud.chains import ChainContext, resolve
        from lm15.registry import lookup

        policy = lookup(self.provider).access
        self.fixture_credential = AwsCredentials("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY")
        self.credential = (self.fixture_credential if self.dry_run else
                           resolve(policy, ChainContext.online(settings=self.settings)))
        if not isinstance(self.credential, AwsCredentials):
            raise ValueError("SigV4 capture requires AWS credentials; use bearer_probes.py for the bearer rung")
        self.placeholder = "<sigv4 with the fixed test pair; see case.credential/now>"

    def lm(self, model_key=None, *, clock=None, credential=None):
        key = credential if credential is not None else (model_key if model_key is not None else self.key())
        # Probes can override the door's credential (for example with an
        # Entra token). Redact those values too if an error echoes them.
        for value in (key if isinstance(key, str) else None,
                      getattr(key, "value", None), getattr(key, "secret_access_key", None),
                      getattr(key, "session_token", None), getattr(key, "access_key_id", None)):
            if isinstance(value, str) and value:
                self._secret_values.add(value)
        return adapter_for_provider(self.provider, key, settings=self.settings or None, clock=clock)

    def pinned_wire(self, request: Request, *, stream: bool, ts: str, treq):
        """The case's wire block: for a SigV4 door, the same request re-signed
        with the fixed pair at ``ts``; otherwise the sent request redacted."""
        if self.fixture_credential is None:
            return self.wire_block(treq), {}
        from lm15.credentials import parse_rfc3339

        fixed = parse_rfc3339(ts[:10] + "T" + ts[11:].replace("-", ":"))
        adapter = self.lm(credential=self.fixture_credential, clock=lambda: fixed)
        pinned = adapter.build_request(request, stream=stream)
        norm = normalize_transport_request(pinned)
        block = {"method": norm["method"], "url": norm["url"], "params": norm["params"], "headers": norm["headers"], "body": norm["body"]}
        from lm15.credentials import credential_to_dict, format_rfc3339

        return block, {"credential": credential_to_dict(self.fixture_credential), "now": format_rfc3339(fixed)}

    def wire_block(self, treq) -> dict:
        norm = normalize_transport_request(treq)
        headers = {}
        for k, v in norm["headers"].items():
            # Every credential-carrying header the dialects use; a new header
            # name here is a new leak vector (x-api-key was missed once,
            # 2026-09-03, and caught by tools/check_secrecy.py before commit).
            if k.lower() == "authorization":
                headers[k] = f"Bearer {self.placeholder}" if v.startswith("Bearer ") else "<redacted: signed with the real key>"
            elif k.lower() == "x-amz-security-token":
                headers[k] = "<redacted>"
            elif k.lower() in ("x-api-key", "x-goog-api-key", "api-key"):
                headers[k] = self.placeholder
            else:
                headers[k] = v
        params = {k: self.placeholder if k.lower() in ("key", "api_key", "api-key", "access_token") else v
                  for k, v in norm["params"].items()}
        return {"method": norm["method"], "url": norm["url"], "params": params, "headers": headers, "body": norm["body"]}

    def send(self, treq) -> tuple[int, bytes, str, dict]:
        ts = now_ts()
        if self.dry_run:
            print(json.dumps(self.wire_block(treq), indent=2, ensure_ascii=False))
            return 0, b"", ts, {}
        with self.transport.stream(treq) as r:
            raw = r.read()
            status, headers = r.status, dict(r.headers)
        # Hash the actual transport input BEFORE redaction or fixture re-signing.
        # Preserve every attempt separately; SUMMARY.json is only the latest run.
        hashed = {"method": treq.method, "url": treq.url, "headers": list(treq.headers),
                  "body_b64": base64.b64encode(treq.body or b"").decode("ascii")}
        sent = self.wire_block(treq)
        self.write_receipt(f"exchange-{ts}-{uuid.uuid4().hex}.json", {
            "timestamp": ts, "provider": self.provider, "status": status,
            "model": sent["body"].get("model") if isinstance(sent["body"], dict) else None,
            "sent": sent,
            "request_sha256": hashlib.sha256(json.dumps(hashed, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest(),
            "request_hash_format": "sha256 of UTF-8 compact JSON: method,url,headers (ordered pairs),body_b64; unredacted transport input",
            "response_sha256": hashlib.sha256(raw).hexdigest(), "response_bytes": len(raw),
            "note": "sent is redacted; request hash cannot be reconstructed from it; body/model may be absent on account surfaces",
        })
        return status, raw, ts, headers

    def redact(self, text: str) -> str:
        from lm15.credentials import AwsCredentials

        if isinstance(self.credential, AwsCredentials):
            for secret in (self.credential.secret_access_key, self.credential.session_token or ""):
                if secret:
                    text = text.replace(secret, "<redacted>")
            text = text.replace(self.credential.access_key_id, "AKIDEXAMPLE")
        k = "" if self.dry_run else os.environ.get(self.env_var, "")
        for secret in sorted(self._secret_values | ({k} if k else set()), key=len, reverse=True):
            text = text.replace(secret, self.placeholder)
        return text

    def write_receipt(self, name: str, payload: object) -> None:
        if self.dry_run:
            return
        self.receipts.mkdir(parents=True, exist_ok=True)
        text = payload if isinstance(payload, str) else json.dumps(payload, indent=2, ensure_ascii=False)
        (self.receipts / name).write_text(self.redact(text) + ("\n" if not text.endswith("\n") else ""))

    def parse(self, adapter, request: Request, raw: bytes, *, stream: bool):
        if stream:
            events = _parse_stream_body(adapter, request, raw)
            return {"parse": f"{len(events)} stream events"}
        resp = adapter.parse_response(request, HttpResponse(200, "OK", [], raw))
        result = _response_result(resp)
        usage = serde.usage_to_dict(resp.usage) if resp.usage else None
        return {"parse": f"finish={resp.finish_reason} usage={usage} unmapped={result.get('unmapped')}",
                "usage": usage, "finish_reason": resp.finish_reason, "unmapped": result.get("unmapped"), "response": resp}

    # ─── cases ───────────────────────────────────────────────────────

    def write_case(self, feature: str, request: Request, *, stream: bool, description: str,
                   expect_lm15: dict | None, evidence_note: str, force: bool) -> dict:
        """Build through the adapter, send, pin body + case. Returns a receipt row."""
        case_path = CONTRACT / "cases" / self.provider / f"{feature}.json"
        if case_path.exists() and not force:
            return {"feature": feature, "skipped": "case exists (use --force)"}
        adapter = self.lm()
        treq = adapter.build_request(request, stream=stream)
        status, raw, ts, _ = self.send(treq)
        row = {"feature": feature, "status": status, "timestamp": ts, "model": request.model}
        if self.dry_run:
            return row
        if status != 200:
            # A failed capture is evidence of the failure, not a case: keep the
            # body under receipts/ and leave cases/ and bodies/ untouched.
            self.write_receipt(f"failed-{feature}-{ts}.txt", raw.decode("utf-8", "replace"))
            row["skipped"] = f"HTTP {status}: body kept under receipts/, no case written"
            return row
        body_dir = CONTRACT / "bodies" / f"{self.provider}.{feature}"
        body_dir.mkdir(parents=True, exist_ok=True)
        body_name = f"{ts}.txt"
        (body_dir / body_name).write_bytes(raw)
        if status == 200:
            try:
                parsed = self.parse(adapter, request, raw, stream=stream)
                parsed.pop("response", None)
                row.update(parsed)
            except Exception as exc:  # the capture must still land the body; the parse failure is the finding
                row["parse"] = f"PARSE FAILED: {type(exc).__name__}: {exc}"
        case = {
            "id": f"{self.provider}.{feature}",
            "provider": self.provider,
            "feature": feature,
            "description": description,
            "base_url": adapter.base_url,
            **({"settings": self.settings} if self.settings else {}),
            **self.pinned_wire(request, stream=stream, ts=ts, treq=treq)[1],
            "request": self.pinned_wire(request, stream=stream, ts=ts, treq=treq)[0],
            "expect": {"status": status},
            "provenance": {
                "source": "live-capture",
                "date": ts[:10],
                "evidence": f"{self.host} {ts}, {request.model}, HTTP {status}; {evidence_note}; adapter-built wire "
                            f"({type(adapter).__name__}, compat+access '{self.provider}'); verbatim body at bodies/{self.provider}.{feature}/{body_name}; "
                            f"{self.change_entry}",
            },
            "canonical_request": serde.request_to_dict(request),
            "canonical_request_provenance": {
                "source": "hand-authored",
                "date": ts[:10],
                "evidence": f"authored with the case (research/providers/{self.provider}/capture.py); wire side generated by the "
                            "reference adapter and live-validated (receipt above)",
            },
            "pinned_body": body_name,
        }
        if stream:
            case["stream"] = True
        if expect_lm15:
            case["expect_lm15"] = expect_lm15
        case_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        time.sleep(1.0)
        return row

    def tool_result_turn(self, first: Request, tool_output: str) -> tuple[Request | None, dict]:
        """Run turn 1 live (or script it in dry-run) and return the turn-2 request
        that replays the model's own assistant message plus a tool result.
        The load-bearing case for thinking_replay; the replay is never faked."""
        adapter = self.lm()
        status, raw, ts, _ = self.send(adapter.build_request(first, stream=False))
        if self.dry_run:
            message = Message.assistant((ThinkingPart(text="Need the tool."),
                                         ToolCallPart(id="call_dry", name=WEATHER.name, input={"city": "Paris"})))
        elif status != 200:
            self.write_receipt(f"failed-multi_turn_tool_result-turn1-{ts}.txt", raw.decode("utf-8", "replace"))
            return None, {"skipped": f"turn 1 HTTP {status}: body kept under receipts/"}
        else:
            message = adapter.parse_response(first, HttpResponse(status, "OK", [], raw)).message
        calls = [p for p in message.parts if isinstance(p, ToolCallPart)]
        if not calls:
            return None, {"skipped": f"turn 1 made no tool call (status {status})"}
        thinking = [p for p in message.parts if isinstance(p, ThinkingPart)]
        second = Request(model=first.model, messages=(*first.messages, message, Message.tool(calls[0].id, tool_output)),
                         tools=first.tools, config=first.config)
        note = f"turn-1 call {calls[0].name} {calls[0].input}, {len(thinking)} thinking part(s) replayed as reasoning_content"
        return second, {"note": note}

    def models_probe(self) -> dict:
        """GET /models as a receipt only (a door whose listing is a blank cell)."""
        adapter = self.lm()
        treq = adapter._models_request()
        try:
            status, raw, ts, _ = self.send(treq)
        except LM15Error as exc:
            return {"probe": "models-list", "error": self.redact(f"{type(exc).__name__}: {exc}")}
        if self.dry_run:
            return {"probe": "models-list", "status": status}
        text = raw.decode("utf-8", "replace")
        self.write_receipt("probe-models-list.json", {"sent": self.wire_block(treq), "status": status, "body": text[:4000], "timestamp": ts})
        return {"probe": "models-list", "status": status, "summary": self.redact(text)[:120]}

    def models_case(self, force: bool) -> dict:
        case_path = CONTRACT / "cases" / self.provider / "models.json"
        if case_path.exists() and not force:
            return {"feature": "models", "skipped": "case exists (use --force)"}
        adapter = self.lm()
        treq = adapter._models_request()
        status, raw, ts, _ = self.send(treq)
        if self.dry_run:
            return {"feature": "models", "status": status}
        if status != 200:
            self.write_receipt(f"failed-models-{ts}.txt", raw.decode("utf-8", "replace"))
            return {"feature": "models", "status": status,
                    "skipped": "listing failed: body kept under receipts/, no case written"}
        body_dir = CONTRACT / "bodies" / f"{self.provider}.models"
        body_dir.mkdir(parents=True, exist_ok=True)
        (body_dir / f"{ts}.txt").write_bytes(raw)
        try:
            data = json.loads(raw)
        except ValueError:
            data = raw.decode("utf-8", "replace")
        ids = [e.get("id") for e in data.get("data", [])] if status == 200 and isinstance(data, dict) else []
        if self.fixture_credential is not None:
            from lm15.credentials import credential_to_dict, format_rfc3339, parse_rfc3339

            fixed = parse_rfc3339(ts[:10] + "T" + ts[11:].replace("-", ":"))
            pinned = self.lm(credential=self.fixture_credential, clock=lambda: fixed)._models_request()
            norm = normalize_transport_request(pinned)
            request_block = {"method": norm["method"], "url": norm["url"], "params": norm["params"], "headers": norm["headers"], "body": norm["body"]}
            extra = {"credential": credential_to_dict(self.fixture_credential), "now": format_rfc3339(fixed)}
        else:
            request_block = self.wire_block(treq)
            extra = {}
        case_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(json.dumps({
            "id": f"{self.provider}.models", "provider": self.provider, "feature": "models", "surface": "models",
            **({"settings": self.settings} if self.settings else {}),
            **extra,
            "description": f"{self.provider} model catalog listing (GET /models)",
            "request": request_block,
            "provenance": {"source": "live-capture", "date": ts[:10],
                           "evidence": f"{self.host} /models {ts}, HTTP {status}, {len(ids)} entries {ids}; "
                                       f"verbatim at bodies/{self.provider}.models/{ts}.txt; {self.change_entry}"},
            "entries_key": "data", "pinned_body": f"{ts}.txt", "expect": {"status": status},
        }, indent=2, ensure_ascii=False) + "\n")
        self.write_receipt("models.json", data)
        return {"feature": "models", "status": status, "entries": ids}

    # ─── account surfaces: image generation, files ──────────────────

    def image_case(self, feature: str, request, *, description: str, evidence_note: str, force: bool) -> dict:
        """Image generation/edit through the adapter's own door; pins the
        `surface: generation` case shape the harness's generation direction
        reads (cases/xai/image_gen.json is the precedent)."""
        case_path = CONTRACT / "cases" / self.provider / f"{feature}.json"
        if case_path.exists() and not force:
            return {"feature": feature, "skipped": "case exists (use --force)"}
        adapter = self.lm()
        treq = adapter._image_generate_request(request)
        status, raw, ts, headers = self.send(treq)
        row = {"feature": feature, "status": status, "timestamp": ts, "model": request.model}
        if self.dry_run:
            return row
        if status != 200:
            self.write_receipt(f"failed-{feature}-{ts}.txt", raw.decode("utf-8", "replace"))
            row["skipped"] = f"HTTP {status}: body kept under receipts/, no case written"
            return row
        body_dir = CONTRACT / "bodies" / f"{self.provider}.{feature}"
        body_dir.mkdir(parents=True, exist_ok=True)
        body_name = f"{ts}.json"
        (body_dir / body_name).write_bytes(raw)
        try:
            parsed = adapter._image_generation_from_response(request, HttpResponse(200, "OK", [], raw))
            row["parse"] = (f"{len(parsed.images)} image(s) {[i.media_type for i in parsed.images]} "
                            f"usage={serde.usage_to_dict(parsed.usage) if parsed.usage else None}")
            self.receipts.mkdir(parents=True, exist_ok=True)
            for i, img in enumerate(parsed.images):
                if img.data:
                    ext = (img.media_type or "image/bin").split("/")[-1]
                    (self.receipts / f"{feature}-{i}.{ext}").write_bytes(img.bytes)
        except Exception as exc:
            row["parse"] = f"PARSE FAILED: {type(exc).__name__}: {exc}"
        wire = self.wire_block(treq)
        if wire.get("body") is None and treq.body:
            wire["body_b64"] = base64.b64encode(treq.body).decode("ascii")
        case = {
            "id": f"{self.provider}.{feature}",
            "provider": self.provider,
            "feature": feature,
            "surface": "generation",
            "kind": "image",
            "description": description,
            "base_url": adapter.base_url,
            **({"settings": self.settings} if self.settings else {}),
            "provenance": {
                "source": "live-capture",
                "date": ts[:10],
                "evidence": f"{self.host} {ts}, {request.model}, HTTP {status}; {evidence_note}; adapter-built wire "
                            f"({type(adapter).__name__}, compat+access '{self.provider}'); verbatim body at bodies/{self.provider}.{feature}/{body_name}; "
                            f"{self.change_entry}",
            },
            "generation_request": serde.image_generation_request_to_dict(request),
            "request": wire,
            "pinned_body": body_name,
            "expect": {"status": status},
        }
        case_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        time.sleep(1.0)
        return row

    def speech_case(self, request, *, description: str, evidence_note: str, force: bool) -> dict:
        """One text-to-speech request with the raw media body and its
        content-type pinned as a ``surface: generation`` speech case."""
        feature = "speech_gen"
        case_path = CONTRACT / "cases" / self.provider / f"{feature}.json"
        if case_path.exists() and not force:
            return {"feature": feature, "skipped": "case exists (use --force)"}
        adapter = self.lm()
        treq = adapter._speech_generate_request(request)
        status, raw, ts, response_headers = self.send(treq)
        row = {"feature": feature, "status": status, "timestamp": ts, "bytes": len(raw)}
        if self.dry_run:
            return row
        if status != 200:
            self.write_receipt(f"failed-{feature}-{ts}.txt", raw.decode("utf-8", "replace"))
            row["skipped"] = f"HTTP {status}: body kept under receipts/, no case written"
            return row
        content_type = next((v for k, v in response_headers.items() if k.lower() == "content-type"), "")
        body_dir = CONTRACT / "bodies" / f"{self.provider}.{feature}"
        body_dir.mkdir(parents=True, exist_ok=True)
        body_name = f"{self.provider}-speech-{ts}.bin"
        (body_dir / body_name).write_bytes(raw)
        case = {
            "id": f"{self.provider}.{feature}", "provider": self.provider,
            "feature": feature, "surface": "generation", "kind": "speech",
            "description": description, "base_url": adapter.base_url,
            **({"settings": self.settings} if self.settings else {}),
            "provenance": {"source": "live-capture", "date": self.date,
                           "evidence": f"{self.host} HTTP 200 raw speech body ({len(raw)} bytes, {content_type}) {ts}; "
                                       f"{evidence_note}; verbatim at bodies/{self.provider}.{feature}/{body_name}; "
                                       f"{self.change_entry}"},
            "generation_request": serde.speech_generation_request_to_dict(request),
            "request": self.wire_block(treq), "pinned_body": body_name,
            "expect": {"status": status}, "response_headers": {"content-type": content_type},
        }
        case_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        self.write_receipt(f"speech-{ts}.json", {"sent": self.wire_block(treq), "status": status,
                                                  "bytes": len(raw), "content_type": content_type, "timestamp": ts})
        return row

    def files_case(self, upload, *, description: str, evidence_note: str, force: bool, download: bool = True) -> dict:
        """Files lifecycle upload → get → list → download → delete through the
        adapter's own doors; pins the `surface: files` steps shape
        (cases/openai/files.json is the precedent).  A non-200 on a step is
        recorded and the lifecycle continues so the file is still deleted."""
        feature = "files"
        case_path = CONTRACT / "cases" / self.provider / f"{feature}.json"
        if case_path.exists() and not force:
            return {"feature": feature, "skipped": "case exists (use --force)"}
        adapter = self.lm()
        body_dir = CONTRACT / "bodies" / f"{self.provider}.{feature}"
        steps: list[dict] = []
        notes: list[str] = []

        def step(op: str, treq, *, parse: str | None, fields: dict) -> tuple[int, bytes]:
            status, raw, ts, _ = self.send(treq)
            wire = self.wire_block(treq)
            if wire.get("body") is None and treq.body:
                wire["body_b64"] = base64.b64encode(treq.body).decode("ascii")
            entry: dict = {"file_op": op, **fields, "request": wire}
            if self.dry_run:
                steps.append(entry)
                return 0, b""
            notes.append(f"{op} HTTP {status} {ts}")
            if 200 <= status < 300 and parse is not None:
                body_dir.mkdir(parents=True, exist_ok=True)
                name = f"{self.provider}-{op}.json"
                (body_dir / name).write_bytes(raw)
                entry["pinned_body"] = name
                entry["parse"] = parse
            elif status != 200:
                self.write_receipt(f"failed-files-{op}-{ts}.txt", raw.decode("utf-8", "replace"))
            entry["expect"] = {"status": status}
            steps.append(entry)
            return status, raw

        status, raw = step("upload", adapter._file_upload_request(upload), parse="info",
                           fields={"upload_request": serde.file_upload_request_to_dict(upload)})
        file_id = "file-dry-run"
        if not self.dry_run:
            if not 200 <= status < 300:
                return {"feature": feature, "status": status, "skipped": "upload failed: body kept under receipts/, no case written"}
            file_id = adapter._file_info_from_body(raw.decode("utf-8")).id
        # Azure OpenAI returns 201 + status=pending and /content is 204 until
        # processing completes.  Poll outside the pinned steps, then pin one
        # terminal GET and the useful download (other providers finish on the
        # first poll).  The public file_wait_ready() follows the same rule.
        if not self.dry_run:
            info = None
            for _ in range(60):
                get_status, get_raw, _, _ = self.send(adapter._file_get_request(file_id))
                if 200 <= get_status < 300:
                    info = adapter._file_info_from_body(get_raw.decode("utf-8"))
                    if info.readiness != "pending":
                        break
                time.sleep(1.0)
            notes.append(f"wait_ready terminal={getattr(info, 'readiness', 'unknown')}")
        step("get", adapter._file_get_request(file_id), parse="info", fields={"file_id": file_id})
        step("list", adapter._file_list_request(20, None), parse="page", fields={"limit": 20})
        if download:
            step("download", adapter._file_download_request(file_id), parse=None, fields={"file_id": file_id})
        step("delete", adapter._file_delete_request(file_id), parse=None, fields={"file_id": file_id})
        row = {"feature": feature, "status": 200, "parse": "; ".join(notes)}
        if self.dry_run:
            return row
        case = {
            "id": f"{self.provider}.{feature}",
            "provider": self.provider,
            "feature": feature,
            "surface": "files",
            "description": description,
            "base_url": adapter.base_url,
            **({"settings": self.settings} if self.settings else {}),
            "provenance": {
                "source": "live-capture",
                "date": self.date,
                "evidence": f"{self.host} Files lifecycle {self.date} ({'; '.join(notes)}); {evidence_note}; adapter-built wires "
                            f"({type(adapter).__name__}, compat+access '{self.provider}'); verbatim bodies at bodies/{self.provider}.{feature}/; "
                            f"{self.change_entry}",
            },
            "steps": steps,
        }
        case_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        return row

    def batch_case(self, request, *, description: str, evidence_note: str, force: bool) -> dict:
        """OpenAI-style Batch lifecycle: JSONL file upload, submit, status,
        cancel, list.  A completed result is not required: queue acceptance
        and state transitions prove the account surface without waiting for
        a provider's 24-hour completion window."""
        feature = "batch"
        case_path = CONTRACT / "cases" / self.provider / f"{feature}.json"
        if case_path.exists() and not force:
            return {"feature": feature, "skipped": "case exists (use --force)"}
        adapter = self.lm()
        body_dir = CONTRACT / "bodies" / f"{self.provider}.{feature}"
        steps: list[dict] = []
        notes: list[str] = []

        def wire(treq) -> dict:
            out = self.wire_block(treq)
            if out.get("body") is None and treq.body:
                out["body_b64"] = base64.b64encode(treq.body).decode("ascii")
            return out

        def send_json(name: str, treq) -> tuple[int, dict, str]:
            status, raw, ts, _ = self.send(treq)
            body_name = f"{self.provider}-{name}.json"
            if self.dry_run:
                # Build every subsequent wire without an upload or a queued job.
                return 200, {"id": "file-dry-run" if name == "batch-upload" else "batch-dry-run"}, body_name
            data = json.loads(raw.decode("utf-8", "replace"))
            body_dir.mkdir(parents=True, exist_ok=True)
            (body_dir / body_name).write_bytes(raw)
            notes.append(f"{name} HTTP {status} {ts}")
            return status, data, body_name

        upload_req = adapter._batch_upload_request(request)
        upload_status, upload_body, _ = send_json("batch-upload", upload_req)
        steps.append({"action": "upload", "batch_request": serde.batch_request_to_dict(request),
                      "requests": [wire(upload_req)], "expect": {"status": upload_status}})
        if not 200 <= upload_status < 300:
            return {"feature": feature, "status": upload_status, "skipped": "batch file upload failed"}

        submit_req = adapter._batch_submit_request(request, upload_body)
        submit_status, submit_body, submit_name = send_json("batch-submit", submit_req)
        steps.append({"action": "submit", "batch_request": serde.batch_request_to_dict(request),
                      "requests": [wire(submit_req)], "upload_body": upload_body,
                      "pinned_body": submit_name, "parse": "job", "expect": {"status": submit_status}})
        if not 200 <= submit_status < 300:
            return {"feature": feature, "status": submit_status, "skipped": "batch submit failed"}
        batch_id = adapter._batch_job_from_body(json.dumps(submit_body)).id

        status_req = adapter._batch_status_request(batch_id)
        status_code, _, status_name = send_json("batch-status", status_req)
        steps.append({"action": "status", "batch_id": batch_id, "requests": [wire(status_req)],
                      "pinned_body": status_name, "parse": "job", "expect": {"status": status_code}})

        cancel_req = adapter._batch_cancel_request(batch_id)
        cancel_status, _, cancel_name = send_json("batch-cancel", cancel_req)
        steps.append({"action": "cancel", "batch_id": batch_id, "requests": [wire(cancel_req)],
                      "pinned_body": cancel_name, "parse": "job", "golden_key": "cancel",
                      "expect": {"status": cancel_status}})

        list_req = adapter._batch_list_request(20)
        list_status, _, list_name = send_json("batch-list", list_req)
        steps.append({"action": "list", "limit": 20, "requests": [wire(list_req)],
                      "pinned_body": list_name, "parse": "list", "expect": {"status": list_status}})

        case = {
            "id": f"{self.provider}.{feature}", "provider": self.provider,
            "feature": feature, "surface": "batch", "description": description,
            "base_url": adapter.base_url, **({"settings": self.settings} if self.settings else {}),
            "provenance": {"source": "live-capture", "date": self.date,
                           "evidence": f"{self.host} Batch lifecycle {self.date} ({'; '.join(notes)}); "
                                       f"{evidence_note}; adapter-built wires; verbatim bodies at "
                                       f"bodies/{self.provider}.{feature}/; {self.change_entry}"},
            "steps": steps,
        }
        if not self.dry_run:
            case_path.parent.mkdir(parents=True, exist_ok=True)
            case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        return {"feature": feature, "status": submit_status, "parse": "; ".join(notes)}

    # ─── probes ──────────────────────────────────────────────────────

    def probe(self, name: str, request: Request | None = None, *, raw_body: dict | None = None,
              model_key=None, stream: bool = False, headers: dict[str, str] | None = None) -> dict:
        """Send one request; record status + body under receipts/. Never a case.

        ``raw_body`` replaces the adapter-built JSON body verbatim (for wire
        shapes lm15 does not emit); the headers and URL still come from the
        adapter.
        """
        adapter = self.lm(model_key)
        base = request if request is not None else Request(model=raw_body["model"], messages=(Message.user("x"),))  # type: ignore[index]
        treq = adapter.build_request(base, stream=stream)
        if raw_body is not None:
            treq = TransportRequest(method=treq.method, url=treq.url, headers=treq.headers,
                                    body=json.dumps(raw_body).encode(), connect_timeout=treq.connect_timeout,
                                    read_timeout=treq.read_timeout, write_timeout=treq.write_timeout)
        if headers:
            # Replace the credential header(s) with the caller's (a door that
            # accepts several schemes: x-api-key vs api-key vs Entra bearer);
            # on a SigV4 door the caller's headers are added and the request
            # is re-signed below.
            drop = {"authorization", "x-api-key", "api-key", "x-goog-api-key"} if self.fixture_credential is None else set()
            kept = [(k, v) for k, v in treq.headers if k.lower() not in drop and k.lower() not in {h.lower() for h in headers}]
            treq = TransportRequest(method=treq.method, url=treq.url, headers=kept + list(headers.items()),
                                    body=treq.body, connect_timeout=treq.connect_timeout,
                                    read_timeout=treq.read_timeout, write_timeout=treq.write_timeout)
        if (raw_body is not None or headers) and self.fixture_credential is not None:
            # A SigV4 door: the signature covers the body and the signed
            # headers, so any change must be re-signed with the same (real)
            # credential and clock.
            from lm15.cloud.hosts import sign_request

            treq.headers = sign_request(adapter.access, adapter.host_settings, method=treq.method, url=treq.url,
                                        headers=[(k, v) for k, v in treq.headers if k.lower() not in ("authorization", "x-amz-date", "x-amz-security-token", "host")],
                                        body=treq.body, credential=adapter.api_key() if callable(adapter.api_key) else adapter.api_key, now=adapter._now())
        try:
            status, raw, ts, headers = self.send(treq)
        except LM15Error as exc:
            return {"probe": name, "error": self.redact(f"{type(exc).__name__}: {exc}")}
        if self.dry_run:
            return {"probe": name, "status": status}
        text = raw.decode("utf-8", "replace")
        try:
            body = json.loads(text)
        except ValueError:
            body = text
        self.write_receipt(f"probe-{name}.json", {"sent": self.wire_block(treq), "status": status, "body": body, "timestamp": ts,
                                                  "response_headers": {k: v for k, v in headers.items() if k.lower() in ("content-type", "x-request-id")}})
        time.sleep(1.0)
        # Redact before summary truncation: cutting a credential first would
        # leave an unmatched prefix in console output.
        safe_body = json.loads(self.redact(json.dumps(body, ensure_ascii=False)))
        return {"probe": name, "status": status, "summary": _summary(safe_body)}

    def errors_file(self, names: Iterable[str]) -> None:
        """Fold captured error probes into errors/cases/<provider>.json (verbatim bodies;
        the expected block is the reference's current mapping, DRAFT until reviewed)."""
        out = {"provenance": {"source": "live-capture", "date": self.date,
                              "evidence": f"{self.host} error envelopes captured verbatim {self.date} by research/providers/{self.provider}/capture.py; "
                                          f"receipts/{self.date}-{self.provider}/probe-error-*.json"},
               "cases": []}
        adapter = adapter_for_provider(self.provider, "vet-parse-only", settings=self.settings or None)
        for name in names:
            path = self.receipts / f"probe-error-{name}.json"
            if not path.exists():
                continue
            rec = json.loads(path.read_text())
            if rec["status"] < 400 or not isinstance(rec["body"], dict):
                continue
            err = adapter.normalize_error(rec["status"], json.dumps(rec["body"]))
            out["cases"].append({
                "id": f"{self.provider}.{name.replace('-', '_')}",
                "provider": self.provider,
                **({"settings": self.settings} if self.settings else {}),
                "status": rec["status"],
                "body": rec["body"],
                "expected": {"class": type(err).__name__, "code": err.code, "provider": self.provider,
                             "provider_code": getattr(err, "provider_code", None), "status": rec["status"]},
                "provenance": {"source": "live-capture", "date": rec["timestamp"][:10],
                               "evidence": f"{self.host} HTTP {rec['status']} verbatim {rec['timestamp']} — receipts/{self.date}-{self.provider}/probe-error-{name}.json; "
                                           "expected block is the reference's current mapping, DRAFT until reviewed"},
            })
        if out["cases"]:
            path = CONTRACT / "errors" / "cases" / f"{self.provider}.json"
            path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

    # ─── entry point ─────────────────────────────────────────────────

    def main(self, cases: Callable[[str, bool, Callable[[str], bool]], list[dict]],
             probes: Callable[[str, Callable[[str], bool]], list[dict]],
             *, error_probes: Iterable[str] = ()) -> None:
        ap = argparse.ArgumentParser(description=f"{self.provider} live capture (see research/providers/_capture.py)")
        ap.add_argument("--force", action="store_true", help="overwrite existing case files")
        ap.add_argument("--only", help="comma-separated feature/probe names")
        ap.add_argument("--model", default=self.default_model)
        ap.add_argument("--no-probes", action="store_true")
        ap.add_argument("--no-cases", action="store_true")
        ap.add_argument("--dry-run", action="store_true", help="build and print every wire; send nothing, write nothing")
        args = ap.parse_args()
        self.dry_run = args.dry_run
        if self.prepare is not None:
            self.prepare()
        self.key()  # fail early
        only = set(args.only.split(",")) if args.only else None

        def want(name: str) -> bool:
            return only is None or name in only

        rows: list[dict] = []
        if not args.no_cases:
            rows += cases(args.model, args.force, want)
        if not args.no_probes:
            rows += probes(args.model, want)
            if not self.dry_run:
                self.errors_file(error_probes)
        if not self.dry_run:
            self.write_receipt(f"SUMMARY-{now_ts()}-{uuid.uuid4().hex}.json", rows)
            self.write_receipt("SUMMARY.json", rows)
        print(f"\nreceipts → {self.receipts}\n")
        print("| item | status | detail |\n|---|---|---|")
        for r in rows:
            name = r.get("feature") or r.get("probe")
            detail = r.get("skipped") or r.get("parse") or r.get("summary") or r.get("error") or r.get("entries") or ""
            safe_detail = self.redact(str(detail))[:140]
            print(f"| {name} | {r.get('status', '-')} | {safe_detail} |")


def _summary(body) -> str:
    if isinstance(body, dict):
        if "error" in body:
            return json.dumps(body["error"], ensure_ascii=False)[:200]
        if body.get("type") == "message":  # Anthropic Messages shape
            blocks = body.get("content") or []
            text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
            return (f"model={body.get('model')} stop={body.get('stop_reason')} blocks={[b.get('type') for b in blocks]} "
                    f"text={text[:60]!r} usage={body.get('usage')}")
        ch = (body.get("choices") or [{}])[0]
        msg = ch.get("message", {})
        u = body.get("usage", {})
        return (f"finish={ch.get('finish_reason')} content={str(msg.get('content'))[:60]!r} "
                f"reasoning={'yes' if msg.get('reasoning_content') else 'no'} usage_keys={sorted(u)} "
                f"details={u.get('prompt_tokens_details')} hit={u.get('prompt_cache_hit_tokens')}")
    return str(body)[:200]
