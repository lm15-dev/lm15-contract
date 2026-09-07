#!/usr/bin/env python3
"""Tool-result content matrix: does the model RECEIVE what a tool returned?

Design-pass runner (playbooks/design-pass.md step 5) for research/tool-result-content/.
Cells, each a fresh nonce so earlier runs cannot pollute:

  text        one call, the tool answers in text          (loop regression; the ratified text cell)
  image       one call, image only                         (the core question)
  mixed       one call, text + image                       (order + both kinds)
  pair        two calls in one turn, A image-only, B mixed (call association)
  pdf         one call, a PDF document                     (documents, where the wire claims them)
  error       one call, is_error=true                      (status must reach the model: no fabricated answer)
  control     no tool; the same image as USER content, unpatched SDK (does the MODEL see at all?)

Example (credentials loaded explicitly, never printed):
  ../lm15-python/.venv/bin/python research/providers/media_tool_results.py \
      --live --env-file ../.env --azure-lab --providers openai,anthropic --cells image,pair

Receipts follow _capture.py, one append-only folder per run. Turn-2 wires are
RAW-BODY PATCHED where the current adapter loses or refuses the content; the
receipt says so. No cases, goldens, pins or presets are modified here.
"""
from __future__ import annotations

import argparse
import base64
import copy
import concurrent.futures
import hashlib
import json
import os
import random
import re
import shlex
import struct
import subprocess
import sys
import time
import uuid
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, Capture, now_ts
from lm15 import Config, FunctionTool, ImagePart, LMRouter, Message, Request, RouterConfig, TextPart
from lm15.registry import PROVIDERS
from lm15.transports import StdlibTransport, TransportRequest
from lm15.vet import normalize_transport_request

MODELS = {
    "openai": "gpt-4.1-mini", "openai-chat": "gpt-4.1-mini",
    "anthropic": "claude-haiku-4-5", "gemini": "gemini-3.7-flash",
    "xai": "grok-4.20", "claude-code": "claude-sonnet-5", "openai-codex": "gpt-5.4-mini",
    "groq": "qwen/qwen3.8-27b", "openrouter": "openai/gpt-4.1-mini",
    "deepseek": "deepseek-v4-flash", "deepseek-anthropic": "deepseek-v4-flash",
    "zai": "glm-4.6v", "moonshotai": "kimi-k2.6", "moonshotai-responses": "kimi-k3",
    "moonshotai-anthropic": "kimi-k3", "meta": "muse-spark-1.3",
    "meta-chat": "muse-spark-1.3", "meta-anthropic": "muse-spark-1.3",
    "azure": "gpt-4.1-mini", "azure-chat": "gpt-4.1-mini",
    "azure-anthropic": "claude-haiku-4-5", "aws-anthropic": "claude-haiku-4-5",
    "bedrock-anthropic": "anthropic.claude-haiku-4-5",
    "bedrock-chat": "deepseek.v3.2", "bedrock-mantle-chat": "xai.grok-4.3",
    "vertex": "gemini-3.7-flash", "vertex-express": "gemini-3.7-flash",
    "vertex-anthropic": "claude-haiku-4-5", "ollama": "qwen3.5:0.8b",
    "vllm": "Qwen/Qwen2.5-VL-7B-Instruct", "sglang": "Qwen/Qwen2.5-VL-7B-Instruct",
}
CELLS = ("text", "image", "mixed", "pair", "pdf", "error", "control")
COLORS = {"red": (230, 20, 20), "green": (20, 190, 20), "blue": (20, 20, 230),
          "yellow": (240, 240, 20), "magenta": (230, 20, 230), "cyan": (20, 230, 230)}
GRID = ("Each panel is a grid of 3 columns and 2 rows of solid colors. Read it left to right across the top row, "
        "then left to right across the bottom row. Use only the names red, green, blue, yellow, magenta, cyan. ")
TOOL = FunctionTool(name="fetch_panel", description="Retrieve a visual panel by its label.", parameters={
    "type": "object", "properties": {"label": {"type": "string", "enum": ["A", "B"]}}, "required": ["label"],
})
TOOL_TEXT = "Panel returned by the requested tool."


def prompt(cell: str) -> str:
    if cell == "control":
        return GRID + 'Return ONLY JSON {"A":[six color names]} for the attached panel.'
    if cell == "pair":
        return ('Call fetch_panel twice in this turn: once with label "A" and once with label "B". After both tool results '
                'arrive, inspect each panel. ' + GRID + 'Return ONLY JSON {"A":[six color names],"B":[six color names]}. '
                'Do not guess before receiving the panels.')
    if cell == "error":
        return ('Call fetch_panel with label "A". ' + GRID + 'If the tool result reports an error or gives you no panel, '
                'return ONLY JSON {"A":null,"note":"<what the tool reported>"}. Otherwise return ONLY JSON {"A":[six color names]}.')
    return ('Call fetch_panel with label "A" (once). When the tool result arrives, inspect the panel. ' + GRID +
            'Return ONLY JSON {"A":[six color names]}. Do not guess before receiving the panel.')


CELL_PX = int(os.environ.get("LM15_PROBE_CELL_PX", "64"))      # 64 → 192x128; OpenAI vision needs ≥256 (control cell, 2026-09-07)
DETAIL = os.environ.get("LM15_PROBE_DETAIL")                    # "high" asks OpenAI-family wires for full-resolution vision


def panel(order: list[str], cell_px: int | None = None) -> bytes:
    """PNG with six colored cells; no labels, comments, or answer metadata."""
    px = cell_px or CELL_PX
    raw = b"".join(b"\x00" + b"".join(bytes(COLORS[order[(y // px) * 3 + x // px]])
                                    for x in range(3 * px)) for y in range(2 * px))
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 3 * px, 2 * px, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def pdf(order: list[str]) -> bytes:
    """A one-page PDF whose only text is the six color names in reading order.
    The model must read the DOCUMENT; the words are not in the prompt."""
    text = " ".join(order)
    stream = f"BT /F1 24 Tf 40 700 Td ({text}) Tj ET".encode()
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
               b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def decode_body(raw: bytes) -> dict:
    try:
        return json.loads(raw)
    except ValueError:
        # Codex is streaming-only: retain raw SSE and extract its actual terminal response.
        response, items = None, []
        for line in raw.decode("utf-8").splitlines():
            if not line.startswith("data:"):
                continue
            try:
                event = json.loads(line[5:].strip())
            except ValueError:
                continue
            if event.get("type") == "response.output_item.done":
                items.append(event["item"])
            if event.get("type") in {"response.completed", "response.incomplete", "response.failed"}:
                response = event.get("response")
        if not isinstance(response, dict):
            raise ValueError("No complete JSON or terminal Responses SSE response")
        if not response.get("output") and items:
            # The Codex backend's terminal frame carries output: []; the items
            # arrived as output_item.done (live 2026-09-07). Same shape, no invention.
            response["output"] = items
        return response


def conversation(dialect: str, body: dict, labels: set[str]) -> tuple[object, list[dict]]:
    if dialect == "openai-responses":
        turn = body["output"]
        calls = [{"id": p["call_id"], "name": p["name"], "args": json.loads(p["arguments"])}
                 for p in turn if p.get("type") == "function_call"]
    elif dialect == "anthropic":
        turn = {"role": "assistant", "content": body["content"]}
        calls = [{"id": p["id"], "name": p["name"], "args": p["input"]}
                 for p in body["content"] if p.get("type") == "tool_use"]
    elif dialect == "gemini":
        turn = body["candidates"][0]["content"]
        calls = [dict(id=f.get("id"), name=f["name"], args=f["args"])
                 for p in turn["parts"] if (f := p.get("functionCall"))]
    else:
        turn = body["choices"][0]["message"]
        calls = [{"id": p["id"], "name": p["function"]["name"], "args": json.loads(p["function"]["arguments"])}
                 for p in turn.get("tool_calls", [])]
    if len(calls) != len(labels) or {c["args"].get("label") for c in calls} != labels or any(c["name"] != "fetch_panel" for c in calls):
        raise ValueError(f"First response must call fetch_panel exactly once per label {sorted(labels)}; no synthetic replay or retry")
    return turn, calls


def wire_parts(dialect: str, parts: list[dict]) -> list[dict]:
    """Canonical-ish parts ({kind: text|image|pdf, ...}) → the dialect's tool-result blocks."""
    out = []
    for p in parts:
        if p["kind"] == "text":
            out.append({"openai-responses": {"type": "input_text", "text": p["text"]},
                        "anthropic": {"type": "text", "text": p["text"]},
                        "gemini": {"text": p["text"]}}.get(dialect, {"type": "text", "text": p["text"]}))
        elif p["kind"] == "image":
            uri = "data:image/png;base64," + p["data"]
            out.append({"openai-responses": {"type": "input_image", "image_url": uri, **({"detail": DETAIL} if DETAIL else {})},
                        "anthropic": {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": p["data"]}},
                        "gemini": {"inlineData": {"mimeType": "image/png", "data": p["data"]}}}.get(dialect, {"type": "image_url", "image_url": {"url": uri, **({"detail": DETAIL} if DETAIL else {})}}))
        elif p["kind"] == "pdf":
            uri = "data:application/pdf;base64," + p["data"]
            out.append({"openai-responses": {"type": "input_file", "filename": "panel.pdf", "file_data": uri},
                        "anthropic": {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": p["data"]}},
                        "gemini": {"inlineData": {"mimeType": "application/pdf", "data": p["data"]}}}.get(dialect, {"type": "file", "file": {"filename": "panel.pdf", "file_data": uri}}))
    return out


def tool_result(dialect: str, call: dict, parts: list[dict], is_error: bool) -> dict:
    blocks = wire_parts(dialect, parts)
    if dialect == "openai-responses":
        # No error flag on this wire: the status is stated in the text (the mapping the pass decides).
        return {"type": "function_call_output", "call_id": call["id"], "output": blocks}
    if dialect == "anthropic":
        item = {"type": "tool_result", "tool_use_id": call["id"], "content": blocks}
        if is_error:
            item["is_error"] = True
        return item
    if dialect == "gemini":
        text = [b["text"] for b in blocks if "text" in b]
        media = [b for b in blocks if "inlineData" in b]
        # No text → an empty response object: the media is the result (no fabricated text).
        fr = {"name": call["name"], "response": ({"error": text[0]} if is_error else ({"result": "\n".join(text)} if text else {}))}
        if call["id"] is not None:
            fr["id"] = call["id"]
        if media:
            fr["parts"] = media
        return {"functionResponse": fr}
    return {"role": "tool", "tool_call_id": call["id"], "content": blocks}


def followup(dialect: str, first: dict, turn: object, calls: list[dict], outputs: dict[str, tuple[list[dict], bool]]) -> dict:
    """The turn-2 body: the FIRST wire, the model's own turn replayed verbatim, then one result per call."""
    body = copy.deepcopy(first)
    results = [tool_result(dialect, call, *outputs[call["args"]["label"]]) for call in calls]
    if dialect == "openai-responses":
        body["input"].extend(copy.deepcopy(turn))
        body["input"].extend(results)
    elif dialect == "anthropic":
        body["messages"].extend([copy.deepcopy(turn), {"role": "user", "content": results}])
    elif dialect == "gemini":
        body["contents"].extend([copy.deepcopy(turn), {"role": "user", "parts": results}])
    else:
        body["messages"].append(copy.deepcopy(turn))
        body["messages"].extend(results)
    return body


def output_text(dialect: str, body: dict) -> str:
    if dialect == "openai-responses":
        return "\n".join(p.get("text", "") for item in body.get("output", []) for p in item.get("content", []))
    if dialect == "anthropic":
        return "\n".join(p.get("text", "") for p in body.get("content", []))
    if dialect == "gemini":
        return "\n".join(p.get("text", "") for p in body["candidates"][0]["content"].get("parts", []) if not p.get("thought"))
    return body["choices"][0]["message"].get("content") or ""


def answer_json(text: str) -> object:
    for pos, char in enumerate(text):
        if char == "{":
            try:
                answer, _ = json.JSONDecoder().raw_decode(text[pos:])
                if isinstance(answer, dict) and "A" in answer:
                    return answer
            except ValueError:
                pass
    return None


def register_header_secrets(cap, headers, placeholder_key=None):
    for key, value in headers:
        if key.lower() not in {"authorization", "x-api-key", "api-key", "x-goog-api-key", "x-amz-security-token"}:
            continue
        token = value[7:] if value.startswith("Bearer ") else value
        if token == placeholder_key:  # keyless local servers use public placeholders such as "ollama"
            continue
        cap._secret_values.add(value)
        cap._secret_values.add(token)
        if value.startswith("AWS4-HMAC-SHA256"):
            match = re.search(r"Credential=([^/,\s]+)/", value)
            if match:
                cap._secret_values.add(match.group(1))


class ProbeCapture(Capture):
    def write_receipt(self, name: str, payload: object) -> None:
        if (self.receipts / name).exists():
            raise FileExistsError("Receipt names must be append-only")
        super().write_receipt(name, payload)


def load_env(path: Path) -> None:
    """Read simple assignments without executing shell code; environment wins."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        tokens = shlex.split(value, comments=True)
        if key.strip().isidentifier() and len(tokens) == 1:
            os.environ.setdefault(key.strip(), tokens[0])


def outputs_for(cell: str, expected: dict[str, list[str]], media: dict[str, str]) -> dict[str, tuple[list[dict], bool]]:
    """What the tool 'returned' per label: (parts, is_error)."""
    if cell == "text":
        return {"A": ([{"kind": "text", "text": "Panel A colors in reading order: " + ", ".join(expected["A"])}], False)}
    if cell == "image":
        return {"A": ([{"kind": "image", "data": media["A"]}], False)}
    if cell == "mixed":
        return {"A": ([{"kind": "text", "text": TOOL_TEXT}, {"kind": "image", "data": media["A"]}], False)}
    if cell == "pair":
        return {"A": ([{"kind": "image", "data": media["A"]}], False),
                "B": ([{"kind": "text", "text": TOOL_TEXT}, {"kind": "image", "data": media["B"]}], False)}
    if cell == "pdf":
        return {"A": ([{"kind": "pdf", "data": media["A"]}], False)}
    if cell == "error":
        return {"A": ([{"kind": "text", "text": "panel service unavailable (HTTP 503)"}], True)}
    raise ValueError(cell)


def judge(cell: str, answer, expected: dict) -> str:
    if cell == "error":
        if answer is None:
            return "accepted_but_no_json_answer"
        return "error_acknowledged" if answer.get("A") is None else "error_ignored_colors_fabricated"
    want = {label: expected[label] for label in (["A", "B"] if cell == "pair" else ["A"])}
    if answer is None:
        return "accepted_but_no_json_answer"
    got = {label: answer.get(label) for label in want}
    return "content_received" if got == want else "accepted_but_content_not_received"


def run_cell(provider: str, model: str, cell: str, root: Path) -> dict:
    definition = PROVIDERS[provider]
    dialect = definition.dialect
    cap = ProbeCapture(provider, env_var=next(iter(definition.access.env_keys), "LM15_CAPTURE_CREDENTIAL"), default_model=model, host=provider)
    cap.receipts = root / provider / cell
    cap.transport = StdlibTransport(connect_timeout=8, read_timeout=90, write_timeout=15)
    row = {"provider": provider, "model": model, "dialect": dialect, "cell": cell, "inference_calls": 0,
           "kind": "raw-wire-discovery-probe" if cell != "control" else "unpatched-sdk-call", "sdk_fixture": False, "cost_usd": None}
    for key, value in os.environ.items():
        if value and any(tag in key for tag in ("API_KEY", "TOKEN", "SECRET", "PASSWORD")):
            cap._secret_values.add(value)
    rng = random.SystemRandom()
    expected = {label: rng.sample(list(COLORS), 6) for label in ("A", "B")}
    while expected["A"] == expected["B"]:
        expected["B"] = rng.sample(list(COLORS), 6)
    if cell == "pdf":
        media = {label: base64.b64encode(pdf(order)).decode() for label, order in expected.items()}
        ext = "pdf"
    else:
        media = {label: base64.b64encode(panel(order)).decode() for label, order in expected.items()}
        ext = "png"
    cap.write_receipt("visual-oracle.json", {"cell": cell, "expected": expected, "cell_px": CELL_PX, "detail": DETAIL, "note": "Never in the prompt; only inside the tool output artifact.",
                                            "artifact_sha256": {label: hashlib.sha256(base64.b64decode(data)).hexdigest() for label, data in media.items()}})
    for label, data in media.items():
        (cap.receipts / f"{label}.{ext}").write_bytes(base64.b64decode(data))
    started = time.monotonic()
    try:
        aws = {p: {"region": os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"}
               for p in MODELS if p.startswith(("aws-", "bedrock-"))}
        router = LMRouter(RouterConfig(settings=aws, transport=cap.transport))
        adapter = router.lm(f"{provider}:{model}")

        def exchange(request, label, provenance):
            register_header_secrets(cap, request.headers, definition.placeholder_key)
            row["inference_calls"] += 1
            t0 = time.monotonic()
            status, raw, ts, headers = cap.send(request)
            cap.write_receipt(label + "-response.txt", raw.decode("utf-8", "replace"))
            cap.write_receipt(label + ".json", {"timestamp": ts, "status": status, "latency_s": round(time.monotonic() - t0, 2), "sent": cap.wire_block(request),
                "response_sha256": hashlib.sha256(raw).hexdigest(), "response_headers": {k: v for k, v in headers.items() if k.lower() in {"content-type", "x-request-id", "request-id"}},
                "provenance": provenance})
            return status, raw

        if cell == "control":
            request = Request(model=model, messages=(Message.user((TextPart(text=prompt(cell)), ImagePart(media_type="image/png", data=media["A"], detail=DETAIL))),), config=Config(max_tokens=1600))
            status, raw = exchange(adapter.build_request(request, stream=False), "turn1", "adapter-built (unpatched SDK)")
            row["turn1_status"] = status
            if status != 200:
                row.update(outcome="first_call_rejected", detail=cap.redact(raw.decode("utf-8", "replace"))[:900])
                return row
            response = decode_body(raw)
            text = output_text(dialect, response)
            answer = answer_json(text)
            row.update(outcome=judge("image", answer, expected), answer=answer, expected={"A": expected["A"]}, output=cap.redact(text)[:1800], usage=response.get("usage", response.get("usageMetadata")))
            return row

        labels = {"A", "B"} if cell == "pair" else {"A"}
        first = Request(model=model, messages=(Message.user(prompt(cell)),), tools=(TOOL,), config=Config(max_tokens=1600))
        treq = adapter.build_request(first, stream=False)
        status, raw = exchange(treq, "turn1", "adapter-built")
        row["turn1_status"] = status
        if status != 200:
            row.update(outcome="first_call_rejected", detail=cap.redact(raw.decode("utf-8", "replace"))[:900])
            return row
        turn, calls = conversation(dialect, decode_body(raw), labels)
        second_body = followup(dialect, json.loads(treq.body), turn, calls, outputs_for(cell, expected, media))
        base = adapter.build_request(first, stream=False)
        second = TransportRequest(method=base.method, url=base.url, headers=base.headers,
            body=json.dumps(second_body, separators=(",", ":"), ensure_ascii=False).encode(),
            connect_timeout=8, read_timeout=90, write_timeout=15)
        if any(v.startswith("AWS4-HMAC-SHA256") for k, v in second.headers if k.lower() == "authorization"):
            from lm15.cloud.hosts import sign_request
            credential = adapter.api_key() if callable(adapter.api_key) else adapter.api_key
            second.headers = sign_request(adapter.access, adapter.host_settings, method=second.method, url=second.url,
                headers=[(k, v) for k, v in second.headers if k.lower() not in {"authorization", "x-amz-date", "x-amz-security-token", "host"}],
                body=second.body, credential=credential, now=adapter._now())
        status, raw = exchange(second, "turn2", "raw-body patched: first wire + verbatim model turn + tool results; NOT current SDK output")
        row["turn2_status"] = status
        if status != 200:
            row.update(outcome="tool_result_rejected", detail=cap.redact(raw.decode("utf-8", "replace"))[:1100])
            return row
        response = decode_body(raw)
        text = output_text(dialect, response)
        answer = answer_json(text)
        row.update(outcome=judge(cell, answer, expected), answer=answer, expected={l: expected[l] for l in sorted(labels)},
                   output=cap.redact(text)[:1800], usage=response.get("usage", response.get("usageMetadata")))
        return row
    except Exception as exc:
        row.update(outcome="blocked_or_inconclusive", error_type=type(exc).__name__, detail=cap.redact(str(exc))[:1100])
        return row
    finally:
        row["wall_s"] = round(time.monotonic() - started, 2)
        cap.write_receipt("result.json", row)
        cap.transport.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--live", action="store_true", help="Required acknowledgement before any provider or credential-network operation")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--azure-lab", action="store_true")
    parser.add_argument("--providers", default="openai,anthropic,gemini")
    parser.add_argument("--cells", default="text,image,mixed,pair,pdf,error,control")
    parser.add_argument("--model", help="Override model; requires exactly one provider")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    names = list(PROVIDERS) if args.providers == "all" else args.providers.split(",")
    cells = list(CELLS) if args.cells == "all" else args.cells.split(",")
    if set(names) - set(PROVIDERS) or len(names) != len(set(names)) or set(cells) - set(CELLS):
        parser.error("Unknown or duplicate providers/cells")
    if args.model and len(names) != 1:
        parser.error("--model requires a single provider")
    plan = {"providers": names, "cells": cells, "models": {n: args.model or MODELS[n] for n in names}, "cell_px": CELL_PX, "detail": DETAIL,
            "max_inference_calls": len(names) * (2 * len(cells) - ("control" in cells)), "automatic_retries": 0, "sdk_fixture": False,
            "capture_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if not args.live:
        print(json.dumps({"network": False, **plan}, indent=2))
        return 0
    if args.env_file:
        load_env(args.env_file)
    if args.azure_lab:
        from _azure import load_lab_env
        load_lab_env()
    root = args.run_dir or CONTRACT / "receipts" / (now_ts()[:10] + "-tool-result-media") / (now_ts() + "-" + uuid.uuid4().hex[:8])
    root.mkdir(parents=True, exist_ok=True)
    if args.worker:
        print(json.dumps(run_cell(names[0], args.model or MODELS[names[0]], cells[0], root)))
        return 0
    if (root / "plan.json").exists():
        parser.error("Use a new run directory; receipts are append-only")
    (root / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    print(f"Receipts: {root}", flush=True)

    def worker(name, cell):
        argv = [sys.executable, str(Path(__file__).resolve()), "--live", "--worker", "--providers", name, "--cells", cell, "--run-dir", str(root)]
        if args.model:
            argv += ["--model", args.model]
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=260)
            path = root / name / cell / "result.json"
            if path.exists():
                return json.loads(path.read_text())
            return {"provider": name, "cell": cell, "outcome": "worker_failed", "exit_code": completed.returncode, "stderr": completed.stderr[-600:]}
        except subprocess.TimeoutExpired:
            return {"provider": name, "cell": cell, "outcome": "worker_timeout", "note": "Already-written exchange receipts remain; no retry."}

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker, n, c) for n in names for c in cells]
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            rows.append(row)
            print(json.dumps({k: row[k] for k in ("provider", "model", "cell", "outcome", "turn1_status", "turn2_status", "error_type") if k in row}), flush=True)
    (root / "SUMMARY.json").write_text(json.dumps(rows, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
