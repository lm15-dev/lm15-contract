"""Shared machinery for provider live captures — the controlled validator.

A provider's ``capture.py`` declares its cases and probes; this module does
everything else the same way for every provider:

- holds the key (from ``<ENV_VAR>`` only; never a .env file, never disk),
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
import json
import os
import sys
import time
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
    def __init__(self, provider: str, *, env_var: str, default_model: str, host: str) -> None:
        self.provider = provider
        self.env_var = env_var
        self.placeholder = f"${env_var}"
        self.default_model = default_model
        self.host = host  # for provenance strings, e.g. "api.deepseek.com"
        self.date = time.strftime("%Y-%m-%d", time.gmtime())
        self.receipts = CONTRACT / "receipts" / f"{self.date}-{provider}"
        self.dry_run = False
        self.transport = StdlibTransport()

    # ─── plumbing ────────────────────────────────────────────────────

    def key(self) -> str:
        value = os.environ.get(self.env_var, "")
        if self.dry_run:
            return value or "dry-run-key"
        if not value:
            sys.exit(f"{self.env_var} is not set; this script never reads a .env file")
        return value

    def lm(self, model_key: str | None = None):
        return adapter_for_provider(self.provider, model_key or self.key())

    def wire_block(self, treq) -> dict:
        norm = normalize_transport_request(treq)
        headers = {}
        for k, v in norm["headers"].items():
            headers[k] = f"Bearer {self.placeholder}" if k.lower() == "authorization" else v
        return {"method": norm["method"], "url": norm["url"], "params": norm["params"], "headers": headers, "body": norm["body"]}

    def send(self, treq) -> tuple[int, bytes, str, dict]:
        ts = now_ts()
        if self.dry_run:
            print(json.dumps(self.wire_block(treq), indent=2, ensure_ascii=False))
            return 0, b"", ts, {}
        with self.transport.stream(treq) as r:
            raw = r.read()
            return r.status, raw, ts, dict(r.headers)

    def redact(self, text: str) -> str:
        k = os.environ.get(self.env_var, "")
        return text.replace(k, self.placeholder) if k else text

    def write_receipt(self, name: str, payload: object) -> None:
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
            "request": self.wire_block(treq),
            "expect": {"status": status},
            "provenance": {
                "source": "live-capture",
                "date": ts[:10],
                "evidence": f"{self.host} {ts}, {request.model}, HTTP {status}; {evidence_note}; adapter-built wire "
                            f"(OpenAIChatLM, compat+access '{self.provider}'); verbatim body at bodies/{self.provider}.{feature}/{body_name}; "
                            f"changes/{self.date}-{self.provider}-live.md",
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

    def models_case(self, force: bool) -> dict:
        case_path = CONTRACT / "cases" / self.provider / "models.json"
        if case_path.exists() and not force:
            return {"feature": "models", "skipped": "case exists (use --force)"}
        adapter = self.lm()
        treq = adapter._models_request()
        status, raw, ts, _ = self.send(treq)
        if self.dry_run:
            return {"feature": "models", "status": status}
        body_dir = CONTRACT / "bodies" / f"{self.provider}.models"
        body_dir.mkdir(parents=True, exist_ok=True)
        (body_dir / f"{ts}.txt").write_bytes(raw)
        try:
            data = json.loads(raw)
        except ValueError:
            data = raw.decode("utf-8", "replace")
        ids = [e.get("id") for e in data.get("data", [])] if status == 200 and isinstance(data, dict) else []
        case_path.parent.mkdir(parents=True, exist_ok=True)
        case_path.write_text(json.dumps({
            "id": f"{self.provider}.models", "provider": self.provider, "feature": "models", "surface": "models",
            "description": f"{self.provider} model catalog listing (GET /models)",
            "request": self.wire_block(treq),
            "provenance": {"source": "live-capture", "date": ts[:10],
                           "evidence": f"{self.host} /models {ts}, HTTP {status}, {len(ids)} entries {ids}; "
                                       f"verbatim at bodies/{self.provider}.models/{ts}.txt; changes/{self.date}-{self.provider}-live.md"},
            "entries_key": "data", "pinned_body": f"{ts}.txt", "expect": {"status": status},
        }, indent=2, ensure_ascii=False) + "\n")
        self.write_receipt("models.json", data)
        return {"feature": "models", "status": status, "entries": ids}

    # ─── probes ──────────────────────────────────────────────────────

    def probe(self, name: str, request: Request | None = None, *, raw_body: dict | None = None,
              model_key: str | None = None, stream: bool = False) -> dict:
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
        try:
            status, raw, ts, headers = self.send(treq)
        except LM15Error as exc:
            return {"probe": name, "error": f"{type(exc).__name__}: {exc}"}
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
        return {"probe": name, "status": status, "summary": _summary(body)}

    def errors_file(self, names: Iterable[str]) -> None:
        """Fold captured error probes into errors/cases/<provider>.json (verbatim bodies;
        the expected block is the reference's current mapping, DRAFT until reviewed)."""
        out = {"provenance": {"source": "live-capture", "date": self.date,
                              "evidence": f"{self.host} error envelopes captured verbatim {self.date} by research/providers/{self.provider}/capture.py; "
                                          f"receipts/{self.date}-{self.provider}/probe-error-*.json"},
               "cases": []}
        adapter = adapter_for_provider(self.provider, "vet-parse-only")
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
            self.write_receipt("SUMMARY.json", rows)
        print(f"\nreceipts → {self.receipts}\n")
        print("| item | status | detail |\n|---|---|---|")
        for r in rows:
            name = r.get("feature") or r.get("probe")
            detail = r.get("skipped") or r.get("parse") or r.get("summary") or r.get("error") or r.get("entries") or ""
            print(f"| {name} | {r.get('status', '-')} | {str(detail)[:140]} |")


def _summary(body) -> str:
    if isinstance(body, dict):
        if "error" in body:
            return json.dumps(body["error"], ensure_ascii=False)[:200]
        ch = (body.get("choices") or [{}])[0]
        msg = ch.get("message", {})
        u = body.get("usage", {})
        return (f"finish={ch.get('finish_reason')} content={str(msg.get('content'))[:60]!r} "
                f"reasoning={'yes' if msg.get('reasoning_content') else 'no'} usage_keys={sorted(u)} "
                f"details={u.get('prompt_tokens_details')} hit={u.get('prompt_cache_hit_tokens')}")
    return str(body)[:200]
