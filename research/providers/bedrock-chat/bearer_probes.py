#!/usr/bin/env python3
"""The bearer-key cells of the two Bedrock doors (open cells in
changes/2026-09-03-bedrock-chat-live.md): a short-term key minted by
research/providers/_aws_bearer.py, read from the file it wrote, exercised
through lm15's own aws-chain env rung (never pasted, never printed).

    python3 research/providers/bedrock-chat/bearer_probes.py [--file ~/.config/lm15/aws-bearer.env] [--only a,b] [--force]

Cells:
  chat-bearer-basic      bedrock-chat  POST /chat/completions  Authorization: Bearer
  chat-bearer-case       bedrock-chat  the same, written as cases/bedrock-chat/bearer_basic_text.json
                         (credential pinned as {"kind":"bearer_token","value":"bedrock-api-key-FIXTURE"};
                         PROTOCOL.md 2026-09-04: the harness compares the header verbatim)
  chat-bearer-models     bedrock-chat  GET  /models            (404 under SigV4; docs show it with a key)
  mantle-bearer-haiku    bedrock-anthropic  x-api-key, anthropic.claude-haiku-4-5 (403 under SigV4 — account gate?)
  mantle-bearer-sonnet5  bedrock-anthropic  x-api-key, anthropic.claude-sonnet-5
  mantle-error-gated     bedrock-anthropic  the 403 permission_error envelope, for errors/cases (--errors)
Receipts under receipts/<date>-bedrock-chat/probe-bearer-*.json and
receipts/<date>-bedrock-anthropic/probe-bearer-*.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _capture import Capture  # noqa: E402
from lm15 import Config, Message, Request  # noqa: E402
from lm15.cloud.chains import ChainContext, explain, resolve  # noqa: E402
from lm15.credentials import BearerToken  # noqa: E402
from lm15.registry import lookup  # noqa: E402


def load_env_file(path: Path) -> None:
    for line in path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main(argv: list[str]) -> int:
    if {"--dry-run", "--help", "-h"}.intersection(argv):
        print(__doc__)
        print("Live-only probe: no dry-run mode; no credentials read or calls made.")
        return 2 if "--dry-run" in argv else 0
    file = Path(argv[argv.index("--file") + 1] if "--file" in argv else "~/.config/lm15/aws-bearer.env").expanduser()
    load_env_file(file)
    region = os.environ.get("AWS_BEARER_TOKEN_REGION") or os.environ.get("AWS_REGION") or "us-east-1"
    os.environ["AWS_REGION"] = region
    rows = []
    for provider, host in (("bedrock-chat", f"bedrock-runtime.{region}.amazonaws.com"), ("bedrock-anthropic", f"bedrock-mantle.{region}.api.aws")):
        policy = lookup(provider).access
        ctx = ChainContext.online(settings={"region": region})
        cred = resolve(policy, ctx)
        assert isinstance(cred, BearerToken), f"{provider}: the chain yielded {cred.kind}, expected the env bearer rung"
        steps, _ = explain(policy, ctx, explicit=False)
        selected = [s for s in steps if s.state == "selected"]
        cap = Capture(provider, env_var="AWS_BEARER_TOKEN_BEDROCK", default_model="", host=host, settings={"region": region}, change_slug="bedrock-bearer")
        cap.credential = cred  # the chain's product, a BearerToken, not the raw string
        only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
        want = lambda n: only is None or n in only  # noqa: E731
        if provider == "bedrock-chat":
            if want("case"):
                cap.fixture_credential = BearerToken("bedrock-api-key-FIXTURE")
                rows.append(cap.write_case("bearer_basic_text", Request(model="openai.gpt-oss-20b-1:0", messages=(Message.user("Say ok."),), config=Config(max_tokens=50)), stream=False,
                    description="Bedrock Chat Completions door with a short-term Bedrock API key: the aws-chain's env rung (AWS_BEARER_TOKEN_BEDROCK -> BearerToken) travels as Authorization: Bearer; credential pinned, header compared verbatim (PROTOCOL.md 2026-09-04)",
                    expect_lm15={"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}},
                    evidence_note="bedrock-api-keys.md:176-185, bedrock-openai-chat-completions.md:151; key minted by research/providers/_aws_bearer.py from the profile's IAM keys", force="--force" in argv))
                cap.fixture_credential = None
            if not want("probes"):
                continue
            rows.append(cap.probe("bearer-basic", Request(model="openai.gpt-oss-20b-1:0", messages=(Message.user("Say ok."),), config=Config(max_tokens=50))))
            lm = cap.lm()
            treq = lm._models_request()
            status, raw, ts, hdrs = cap.send(treq)
            text = raw.decode("utf-8", "replace")
            try:
                body = json.loads(text)
            except ValueError:
                body = text
            cap.write_receipt("probe-bearer-models.json", {"sent": cap.wire_block(treq), "status": status, "body": body, "timestamp": ts})
            n = len(body.get("data", [])) if isinstance(body, dict) else None
            rows.append({"probe": "bearer-models", "status": status, "models": n})
        else:
            if want("errors"):
                rows.append(cap.probe("error-model-gated", Request(model="anthropic.claude-haiku-4-5", messages=(Message.user("Say ok."),), config=Config(max_tokens=50))))
            if not want("probes"):
                continue
            for name, model in (("bearer-haiku", "anthropic.claude-haiku-4-5"), ("bearer-sonnet5", "anthropic.claude-sonnet-5"), ("bearer-opus47", "anthropic.claude-opus-4-7")):
                rows.append(cap.probe(name, Request(model=model, messages=(Message.user("Say ok."),), config=Config(max_tokens=50))))
        rows[-1]["chain_selected"] = [s.kind for s in selected]
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
