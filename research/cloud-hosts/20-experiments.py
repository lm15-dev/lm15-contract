#!/usr/bin/env python3
"""Cloud hosts — the live experiment matrix (design-pass step 5).

Runs every "live cell" named in 10-facts-*.md and 30-model.md against
the doors a credential exists for, with fresh nonces, and writes
20-results.json (status, latency, usage, redacted response head, cost
estimate).  Standard library only.  Nothing here is the reference
implementation: the SigV4 signer below is a research tool that the
reference must re-derive from the spec and the harness must pin.

Credentials (all optional; a door without one is SKIPPED, never faked):

  AWS     AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY [+ AWS_SESSION_TOKEN], AWS_REGION
          ANTHROPIC_AWS_WORKSPACE_ID (aws-anthropic door)
          AWS_BEARER_TOKEN_BEDROCK (bearer cells)
  Azure   AZURE_OPENAI_RESOURCE + AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT
          ANTHROPIC_FOUNDRY_RESOURCE + ANTHROPIC_FOUNDRY_API_KEY
          `az` logged in (Entra bearer cells; scope probes)
  GCP     GOOGLE_CLOUD_PROJECT [+ GOOGLE_CLOUD_LOCATION]; `gcloud` logged in
          GOOGLE_API_KEY (vertex-express cells)

Budget: every inference cell sends "Say ok." with max_tokens 16.  At
2026-09 list prices a cell is < $0.01; the full matrix is ~60 cells,
under $1 plus listing calls.  Spend is totalled in the results file.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "20-results.json"
NONCE = uuid.uuid4().hex[:8]
PROMPT = f"Say ok. (nonce {NONCE})"


# --------------------------------------------------------------------- SigV4
def sigv4_headers(method: str, url: str, body: bytes, *, service: str, region: str,
                  access_key: str, secret: str, session_token: str | None,
                  headers: dict[str, str], now: dt.datetime | None = None) -> dict[str, str]:
    """AWS4-HMAC-SHA256 per aws-sigv4-create-signed-request.md:46-190."""
    now = now or dt.datetime.now(dt.timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date = now.strftime("%Y%m%d")
    u = urllib.parse.urlsplit(url)
    h = {k.lower(): " ".join(v.split()) for k, v in headers.items()}  # Trim + collapse inner runs of spaces (suite: get-header-value-trim)
    h["host"] = u.netloc
    h["x-amz-date"] = amz_date
    if session_token:
        h["x-amz-security-token"] = session_token
    payload_hash = hashlib.sha256(body).hexdigest()  # x-amz-content-sha256 header is S3-only (spec line 96)
    signed = ";".join(sorted(h))
    canonical_headers = "".join(f"{k}:{h[k]}\n" for k in sorted(h))
    query = "&".join(
        f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}"
        for k, v in sorted(urllib.parse.parse_qsl(u.query, keep_blank_values=True))
    )
    canonical = "\n".join([method, urllib.parse.quote(u.path or "/", safe="/-_.~"), query,
                           canonical_headers, signed, payload_hash])
    scope = f"{date}/{region}/{service}/aws4_request"
    sts = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()])
    k = ("AWS4" + secret).encode()
    for part in (date, region, service, "aws4_request"):
        k = hmac.new(k, part.encode(), hashlib.sha256).digest()
    sig = hmac.new(k, sts.encode(), hashlib.sha256).hexdigest()
    h["authorization"] = (f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, "
                          f"SignedHeaders={signed}, Signature={sig}")
    return h


# ------------------------------------------------------------------ tokens
def az_token(scope: str) -> str | None:
    try:
        out = subprocess.run(["az", "account", "get-access-token", "--output", "json", "--scope", scope],
                             capture_output=True, text=True, timeout=30, check=True).stdout
        return json.loads(out)["accessToken"]
    except Exception:  # noqa: BLE001
        return None


def gcloud_token() -> str | None:
    try:
        return subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True,
                              text=True, timeout=30, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------- HTTP
def call(method: str, url: str, headers: dict[str, str], body: bytes | None) -> dict:
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
            status = r.status
            rh = dict(r.headers)
    except urllib.error.HTTPError as e:
        raw = e.read()
        status = e.code
        rh = dict(e.headers)
    except Exception as e:  # noqa: BLE001
        return {"status": 0, "error": type(e).__name__, "latency_ms": round((time.perf_counter() - t0) * 1000)}
    text = raw.decode("utf-8", "replace")
    usage = None
    try:
        j = json.loads(text)
        usage = j.get("usage") or j.get("usageMetadata")
    except Exception:  # noqa: BLE001
        pass
    return {"status": status, "latency_ms": round((time.perf_counter() - t0) * 1000),
            "content_type": rh.get("Content-Type"), "usage": usage,
            "head": text[:600], "request_id": rh.get("x-request-id") or rh.get("request-id")
            or rh.get("x-amzn-requestid") or rh.get("apim-request-id")}


def redact(s: str) -> str:
    for k in ("AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AZURE_OPENAI_API_KEY",
              "ANTHROPIC_FOUNDRY_API_KEY", "GOOGLE_API_KEY", "AWS_BEARER_TOKEN_BEDROCK"):
        v = os.environ.get(k)
        if v:
            s = s.replace(v, f"<{k}>")
    return s


# ------------------------------------------------------------------ bodies
def messages_body(model: str | None, **extra) -> dict:
    b = {"max_tokens": 16, "messages": [{"role": "user", "content": PROMPT}]}
    if model:
        b["model"] = model
    b.update(extra)
    return b


def chat_body(model: str, **extra) -> dict:
    b = {"model": model, "max_tokens": 16, "messages": [{"role": "user", "content": PROMPT}]}
    b.update(extra)
    return b


def gemini_body(**extra) -> dict:
    b = {"contents": [{"role": "user", "parts": [{"text": PROMPT}]}],
         "generationConfig": {"maxOutputTokens": 16}}
    b.update(extra)
    return b


# ------------------------------------------------------------------- cells
def cells() -> list[dict]:
    """Each cell: id, door, method, url, headers, body, auth ('sigv4:<service>' | 'bearer' | 'api-key' | 'x-api-key' | 'none'), note."""
    c: list[dict] = []
    env = os.environ
    region = env.get("AWS_REGION", "us-east-1")
    j = lambda d: json.dumps(d).encode()  # noqa: E731

    # ---- AWS ----------------------------------------------------------
    ws = env.get("ANTHROPIC_AWS_WORKSPACE_ID")
    if ws:
        base = f"https://aws-external-anthropic.{region}.api.aws"
        H = {"content-type": "application/json", "anthropic-version": "2023-06-01", "anthropic-workspace-id": ws}
        c += [
            dict(id="aws-anthropic.basic", door="aws-anthropic", method="POST", url=f"{base}/v1/messages", headers=H,
                 body=j(messages_body("claude-haiku-4-5")), auth="sigv4:aws-external-anthropic", note="platform door, SigV4"),
            dict(id="aws-anthropic.beta-header", door="aws-anthropic", method="POST", url=f"{base}/v1/messages",
                 headers={**H, "anthropic-beta": "prompt-caching-2024-07-31"}, body=j(messages_body("claude-haiku-4-5")),
                 auth="sigv4:aws-external-anthropic", note="beta header passes (docs say yes)"),
            dict(id="aws-anthropic.models", door="aws-anthropic", method="GET", url=f"{base}/v1/models", headers=H,
                 body=None, auth="sigv4:aws-external-anthropic", note="models surface: blank cell"),
            dict(id="aws-anthropic.batches-list", door="aws-anthropic", method="GET", url=f"{base}/v1/messages/batches", headers=H,
                 body=None, auth="sigv4:aws-external-anthropic", note="batches surface: blank cell"),
            dict(id="aws-anthropic.inference-geo", door="aws-anthropic", method="POST", url=f"{base}/v1/messages", headers=H,
                 body=j(messages_body("claude-haiku-4-5", inference_geo="us")), auth="sigv4:aws-external-anthropic",
                 note="docs: 400 on 4.5 models; extension door"),
            dict(id="aws-anthropic.wrong-region", door="aws-anthropic", method="POST",
                 url=f"https://aws-external-anthropic.eu-west-1.api.aws/v1/messages", headers=H,
                 body=j(messages_body("claude-haiku-4-5")), auth="sigv4:aws-external-anthropic", note="host error envelope"),
        ]
    if env.get("AWS_ACCESS_KEY_ID"):
        mb = f"https://bedrock-mantle.{region}.api.aws/anthropic"
        H = {"content-type": "application/json", "anthropic-version": "2023-06-01"}
        c += [
            dict(id="bedrock-anthropic.basic", door="bedrock-anthropic", method="POST", url=f"{mb}/v1/messages", headers=H,
                 body=j(messages_body("anthropic.claude-haiku-4-5")), auth="sigv4:bedrock-mantle", note="mantle door, SSE wire"),
            dict(id="bedrock-anthropic.stream", door="bedrock-anthropic", method="POST", url=f"{mb}/v1/messages", headers=H,
                 body=j(messages_body("anthropic.claude-haiku-4-5", stream=True)), auth="sigv4:bedrock-mantle", note="framing: SSE expected"),
            dict(id="bedrock-anthropic.beta-header", door="bedrock-anthropic", method="POST", url=f"{mb}/v1/messages",
                 headers={**H, "anthropic-beta": "prompt-caching-2024-07-31"}, body=j(messages_body("anthropic.claude-haiku-4-5")),
                 auth="sigv4:bedrock-mantle", note="docs: not supported → what status?"),
            dict(id="bedrock-anthropic.structured-output", door="bedrock-anthropic", method="POST", url=f"{mb}/v1/messages", headers=H,
                 body=j(messages_body("anthropic.claude-haiku-4-5", output_format={"type": "json_schema", "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}})),
                 auth="sigv4:bedrock-mantle", note="docs: unsupported → loud or silent? (MAP-8)"),
            dict(id="bedrock-anthropic.old-model", door="bedrock-anthropic", method="POST", url=f"{mb}/v1/messages", headers=H,
                 body=j(messages_body("anthropic.claude-sonnet-4-5")), auth="sigv4:bedrock-mantle", note="C1: pre-4.7 model on mantle"),
            dict(id="bedrock-anthropic.version-other", door="bedrock-anthropic", method="POST", url=f"{mb}/v1/messages",
                 headers={**H, "anthropic-version": "2024-01-01"}, body=j(messages_body("anthropic.claude-haiku-4-5")),
                 auth="sigv4:bedrock-mantle", note="anthropic-version values other than 2023-06-01"),
            dict(id="bedrock-anthropic.models", door="bedrock-anthropic", method="GET", url=f"{mb}/v1/models", headers=H,
                 body=None, auth="sigv4:bedrock-mantle", note="docs: Models API unsupported"),
        ]
        rb = f"https://bedrock-runtime.{region}.amazonaws.com/openai/v1"
        H = {"content-type": "application/json"}
        c += [
            dict(id="bedrock-chat.models", door="bedrock-chat", method="GET", url=f"{rb}/models", headers=H, body=None,
                 auth="sigv4:bedrock", note="listing + pick a model id"),
            dict(id="bedrock-chat.basic", door="bedrock-chat", method="POST", url=f"{rb}/chat/completions", headers=H,
                 body=j(chat_body(env.get("BEDROCK_CHAT_MODEL", "anthropic.claude-haiku-4-5"))), auth="sigv4:bedrock", note="chat wire on runtime"),
            dict(id="bedrock-chat.stream-usage", door="bedrock-chat", method="POST", url=f"{rb}/chat/completions", headers=H,
                 body=j(chat_body(env.get("BEDROCK_CHAT_MODEL", "anthropic.claude-haiku-4-5"), stream=True, stream_options={"include_usage": True})),
                 auth="sigv4:bedrock", note="compat: stream_usage"),
            dict(id="bedrock-chat.tool-choice-required", door="bedrock-chat", method="POST", url=f"{rb}/chat/completions", headers=H,
                 body=j(chat_body(env.get("BEDROCK_CHAT_MODEL", "anthropic.claude-haiku-4-5"), tools=[{"type": "function", "function": {"name": "f", "parameters": {"type": "object"}}}], tool_choice="required")),
                 auth="sigv4:bedrock", note="compat: forced_tool_choice"),
            dict(id="bedrock-chat.json-schema", door="bedrock-chat", method="POST", url=f"{rb}/chat/completions", headers=H,
                 body=j(chat_body(env.get("BEDROCK_CHAT_MODEL", "anthropic.claude-haiku-4-5"), response_format={"type": "json_schema", "json_schema": {"name": "x", "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}})),
                 auth="sigv4:bedrock", note="compat: json_schema"),
            dict(id="bedrock-chat.reasoning-effort", door="bedrock-chat", method="POST", url=f"{rb}/chat/completions", headers=H,
                 body=j(chat_body(env.get("BEDROCK_CHAT_MODEL", "anthropic.claude-haiku-4-5"), reasoning_effort="low")),
                 auth="sigv4:bedrock", note="compat: thinking_format"),
        ]
    if env.get("AWS_BEARER_TOKEN_BEDROCK"):
        rb = f"https://bedrock-runtime.{region}.amazonaws.com/openai/v1"
        c += [dict(id="bedrock-chat.bearer", door="bedrock-chat", method="POST", url=f"{rb}/chat/completions",
                   headers={"content-type": "application/json"}, body=j(chat_body(env.get("BEDROCK_CHAT_MODEL", "anthropic.claude-haiku-4-5"))),
                   auth="bearer:AWS_BEARER_TOKEN_BEDROCK", note="bearer alternative to SigV4")]

    # ---- Azure --------------------------------------------------------
    res = env.get("AZURE_OPENAI_RESOURCE")
    dep = env.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-nano")
    if res and env.get("AZURE_OPENAI_API_KEY"):
        ab = f"https://{res}.openai.azure.com/openai/v1"
        H = {"content-type": "application/json"}
        c += [
            dict(id="azure.responses-basic", door="azure", method="POST", url=f"{ab}/responses", headers=H,
                 body=j({"model": dep, "input": PROMPT, "max_output_tokens": 16}), auth="api-key:AZURE_OPENAI_API_KEY", note="v1 Responses, api-key header"),
            dict(id="azure.x-api-key", door="azure", method="POST", url=f"{ab}/responses", headers=H,
                 body=j({"model": dep, "input": PROMPT, "max_output_tokens": 16}), auth="x-api-key:AZURE_OPENAI_API_KEY", note="blank cell: is x-api-key accepted on openai.azure.com?"),
            dict(id="azure-chat.basic", door="azure-chat", method="POST", url=f"{ab}/chat/completions", headers=H,
                 body=j(chat_body(dep)), auth="api-key:AZURE_OPENAI_API_KEY", note="v1 chat"),
            dict(id="azure.models", door="azure", method="GET", url=f"{ab}/models", headers=H, body=None,
                 auth="api-key:AZURE_OPENAI_API_KEY", note="blank cell: data-plane listing?"),
            dict(id="azure.not-a-deployment", door="azure", method="POST", url=f"{ab}/responses", headers=H,
                 body=j({"model": "gpt-4.1-not-deployed", "input": PROMPT}), auth="api-key:AZURE_OPENAI_API_KEY", note="404 envelope (C3)"),
            dict(id="azure.services-host", door="azure", method="POST", url=f"https://{res}.services.ai.azure.com/openai/v1/responses", headers=H,
                 body=j({"model": dep, "input": PROMPT, "max_output_tokens": 16}), auth="api-key:AZURE_OPENAI_API_KEY", note="alternate host form"),
        ]
        for scope in ("https://ai.azure.com/.default", "https://cognitiveservices.azure.com/.default"):
            tok = az_token(scope)
            if tok:
                c.append(dict(id=f"azure.entra-scope.{scope.split('//')[1].split('/')[0]}", door="azure", method="POST", url=f"{ab}/responses",
                              headers={**H, "authorization": f"Bearer {tok}"}, body=j({"model": dep, "input": PROMPT, "max_output_tokens": 16}),
                              auth="none", note=f"which scope works: {scope}"))
    fres = env.get("ANTHROPIC_FOUNDRY_RESOURCE")
    if fres and env.get("ANTHROPIC_FOUNDRY_API_KEY"):
        fb = f"https://{fres}.services.ai.azure.com/anthropic/v1"
        H = {"content-type": "application/json", "anthropic-version": "2023-06-01"}
        fm = env.get("ANTHROPIC_FOUNDRY_MODEL", "claude-haiku-4-5")
        c += [
            dict(id="azure-anthropic.basic", door="azure-anthropic", method="POST", url=f"{fb}/messages", headers=H,
                 body=j(messages_body(fm)), auth="api-key:ANTHROPIC_FOUNDRY_API_KEY", note="Foundry Messages"),
            dict(id="azure-anthropic.x-api-key", door="azure-anthropic", method="POST", url=f"{fb}/messages", headers=H,
                 body=j(messages_body(fm)), auth="x-api-key:ANTHROPIC_FOUNDRY_API_KEY", note="docs: both headers accepted"),
            dict(id="azure-anthropic.beta-header", door="azure-anthropic", method="POST", url=f"{fb}/messages",
                 headers={**H, "anthropic-beta": "prompt-caching-2024-07-31"}, body=j(messages_body(fm)), auth="api-key:ANTHROPIC_FOUNDRY_API_KEY", note="blank cell"),
            dict(id="azure-anthropic.structured-output", door="azure-anthropic", method="POST", url=f"{fb}/messages", headers=H,
                 body=j(messages_body(fm, output_format={"type": "json_schema", "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}})),
                 auth="api-key:ANTHROPIC_FOUNDRY_API_KEY", note="blank cell"),
            dict(id="azure-anthropic.web-search", door="azure-anthropic", method="POST", url=f"{fb}/messages", headers=H,
                 body=j(messages_body(fm, tools=[{"type": "web_search_20250305", "name": "web_search"}])),
                 auth="api-key:ANTHROPIC_FOUNDRY_API_KEY", note="docs: 400 by design when hosted on Azure"),
            dict(id="azure-anthropic.models", door="azure-anthropic", method="GET", url=f"{fb}/models", headers=H, body=None,
                 auth="api-key:ANTHROPIC_FOUNDRY_API_KEY", note="docs: Models API unsupported"),
        ]

    # ---- GCP ----------------------------------------------------------
    proj = env.get("GOOGLE_CLOUD_PROJECT")
    loc = env.get("GOOGLE_CLOUD_LOCATION", "global")
    tok = gcloud_token() if proj else None
    if proj and tok:
        host = "aiplatform.googleapis.com" if loc == "global" else f"{loc}-aiplatform.googleapis.com"
        vb = f"https://{host}/v1/projects/{proj}/locations/{loc}"
        H = {"content-type": "application/json", "authorization": f"Bearer {tok}"}
        gm = env.get("VERTEX_GEMINI_MODEL", "gemini-2.5-flash")
        cm = env.get("VERTEX_CLAUDE_MODEL", "claude-haiku-4-5@20251001")
        c += [
            dict(id="vertex.basic", door="vertex", method="POST", url=f"{vb}/publishers/google/models/{gm}:generateContent", headers=H,
                 body=j(gemini_body()), auth="none", note="Gemini on Vertex"),
            dict(id="vertex.stream-sse", door="vertex", method="POST", url=f"{vb}/publishers/google/models/{gm}:streamGenerateContent?alt=sse", headers=H,
                 body=j(gemini_body()), auth="none", note="SSE framing"),
            dict(id="vertex.models-google", door="vertex", method="GET", url=f"https://{host}/v1/publishers/google/models", headers=H, body=None,
                 auth="none", note="blank cell: listing URL + shape"),
            dict(id="vertex.models-anthropic", door="vertex-anthropic", method="GET", url=f"https://{host}/v1/publishers/anthropic/models", headers=H, body=None,
                 auth="none", note="blank cell"),
            dict(id="vertex-anthropic.basic", door="vertex-anthropic", method="POST", url=f"{vb}/publishers/anthropic/models/{cm}:rawPredict", headers=H,
                 body=j(messages_body(None, anthropic_version="vertex-2023-10-16")), auth="none", note="model in path, version in body"),
            dict(id="vertex-anthropic.stream", door="vertex-anthropic", method="POST", url=f"{vb}/publishers/anthropic/models/{cm}:streamRawPredict", headers=H,
                 body=j(messages_body(None, anthropic_version="vertex-2023-10-16", stream=True)), auth="none", note="SSE framing"),
            dict(id="vertex-anthropic.model-in-body", door="vertex-anthropic", method="POST", url=f"{vb}/publishers/anthropic/models/{cm}:rawPredict", headers=H,
                 body=j(messages_body(cm, anthropic_version="vertex-2023-10-16")), auth="none", note="does a body model field 400 or get ignored? (silent-drop check)"),
            dict(id="vertex-anthropic.beta-header", door="vertex-anthropic", method="POST", url=f"{vb}/publishers/anthropic/models/{cm}:rawPredict",
                 headers={**H, "anthropic-beta": "prompt-caching-2024-07-31"}, body=j(messages_body(None, anthropic_version="vertex-2023-10-16")),
                 auth="none", note="blank cell"),
            dict(id="vertex-anthropic.wrong-location", door="vertex-anthropic", method="POST",
                 url=f"https://europe-west1-aiplatform.googleapis.com/v1/projects/{proj}/locations/europe-west1/publishers/anthropic/models/{cm}:rawPredict",
                 headers=H, body=j(messages_body(None, anthropic_version="vertex-2023-10-16")), auth="none", note="host error envelope"),
            dict(id="vertex-chat.basic", door="vertex-chat", method="POST", url=f"{vb}/endpoints/openapi/chat/completions", headers=H,
                 body=j(chat_body(f"google/{gm}")), auth="none", note="OpenAI-compatible endpoint"),
        ]
    if env.get("GOOGLE_API_KEY"):
        gm = env.get("VERTEX_GEMINI_MODEL", "gemini-2.5-flash")
        c += [
            dict(id="vertex-express.query-key", door="vertex-express", method="POST",
                 url=f"https://aiplatform.googleapis.com/v1/publishers/google/models/{gm}:generateContent?key={env['GOOGLE_API_KEY']}",
                 headers={"content-type": "application/json"}, body=j(gemini_body()), auth="none", note="express mode, ?key="),
            dict(id="vertex-express.header-key", door="vertex-express", method="POST",
                 url=f"https://aiplatform.googleapis.com/v1/publishers/google/models/{gm}:generateContent",
                 headers={"content-type": "application/json", "x-goog-api-key": env["GOOGLE_API_KEY"]}, body=j(gemini_body()),
                 auth="none", note="blank cell: header form accepted?"),
        ]
    return c


def run() -> int:
    env = os.environ
    results = []
    spend_cells = 0
    for cell in cells():
        headers = dict(cell["headers"])
        auth = cell["auth"]
        if auth.startswith("sigv4:"):
            headers = sigv4_headers(cell["method"], cell["url"], cell["body"] or b"", service=auth.split(":", 1)[1],
                                    region=env.get("AWS_REGION", "us-east-1"), access_key=env["AWS_ACCESS_KEY_ID"],
                                    secret=env["AWS_SECRET_ACCESS_KEY"], session_token=env.get("AWS_SESSION_TOKEN"), headers=headers)
        elif auth.startswith("bearer:"):
            headers["authorization"] = f"Bearer {env[auth.split(':', 1)[1]]}"
        elif auth.startswith("api-key:"):
            headers["api-key"] = env[auth.split(":", 1)[1]]
        elif auth.startswith("x-api-key:"):
            headers["x-api-key"] = env[auth.split(":", 1)[1]]
        r = call(cell["method"], cell["url"], headers, cell["body"])
        r["head"] = redact(r.get("head", ""))
        if cell["method"] == "POST" and 200 <= r["status"] < 300:
            spend_cells += 1
        results.append({"id": cell["id"], "door": cell["door"], "note": cell["note"], "url": redact(cell["url"]),
                        "request_headers": sorted(k for k in headers), "at": dt.datetime.now(dt.timezone.utc).isoformat(), **r})
        print(f"  {cell['id']:<44} {r['status']:>3} {r.get('latency_ms', '-'):>6} ms  {cell['note']}")
        time.sleep(0.3)
    OUT.write_text(json.dumps({"nonce": NONCE, "date": dt.date.today().isoformat(), "cells": len(results),
                               "successful_inference_cells": spend_cells,
                               "spend_estimate_usd": round(spend_cells * 0.01, 2), "results": results}, indent=1) + "\n")
    print(f"---\n{len(results)} cells -> {OUT.name}; ~${spend_cells * 0.01:.2f}")
    return 0


if __name__ == "__main__":
    if not cells():
        print("No credentials in the environment; nothing to run. See the module docstring.", file=sys.stderr)
        sys.exit(2)
    sys.exit(run())
