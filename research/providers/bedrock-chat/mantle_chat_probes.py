#!/usr/bin/env python3
"""The OTHER Chat Completions door: bedrock-mantle.{region}.api.aws/v1
(bedrock-openai-chat-completions.md:5-8: "Amazon Bedrock API key or AWS
credentials"; the model listing is documented HERE, not on bedrock-runtime).

Questions, each a receipt under receipts/<date>-bedrock-chat/probe-mantle-chat-*.json:
  - does Nova 2 answer over plain Chat Completions on this host?  (bedrock-runtime
    validates Nova 2 bodies against Nova's native schema: nova_probes.py)
  - does gpt-oss answer here too (same door, second host)?
  - does GET /v1/models list, under SigV4 and under a short-term key?

Ad-hoc access policy, not a registry entry: evidence first.

    AWS_REGION=us-east-1 python3 research/providers/bedrock-chat/mantle_chat_probes.py [--bearer ~/.config/lm15/aws-bearer.env]
"""
from __future__ import annotations

import dataclasses
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _aws import REGION  # noqa: E402
from _capture import Capture  # noqa: E402
from lm15 import Config, Message, Request, access  # noqa: E402
from lm15.credentials import BearerToken  # noqa: E402
from lm15.features import HostSpec  # noqa: E402
from lm15.providers.openai_chat import OpenAIChatLM  # noqa: E402
from lm15.cloud.chains import ChainContext, resolve  # noqa: E402

MANTLE_CHAT = dataclasses.replace(
    access.BEDROCK_CHAT,
    host=HostSpec(base_url="https://bedrock-mantle.{region}.api.aws/v1", settings=access.BEDROCK_CHAT.host.settings, sigv4_service="bedrock-mantle"),
    backend="bedrock-mantle",
)


def main(argv: list[str]) -> int:
    if {"--dry-run", "--help", "-h"}.intersection(argv):
        print(__doc__)
        print("Live-only probe: no dry-run mode; no credentials read or calls made.")
        return 2 if "--dry-run" in argv else 0
    cap = Capture("bedrock-chat", env_var="AWS_BEARER_TOKEN_BEDROCK", default_model="amazon.nova-2-lite-v1:0",
                  host=f"bedrock-mantle.{REGION}.api.aws", settings={"region": REGION})
    cap.aws_fixture()
    from lm15.compat import OPENAI_CHAT_PRESETS

    def lm(credential):
        return OpenAIChatLM(api_key=credential, access=MANTLE_CHAT, compat=OPENAI_CHAT_PRESETS["bedrock"], settings={"region": REGION})

    creds = [("sigv4", cap.credential)]
    if "--bearer" in argv:
        for line in Path(argv[argv.index("--bearer") + 1]).expanduser().read_text().splitlines():
            if line.startswith("AWS_BEARER_TOKEN_BEDROCK="):
                os.environ["AWS_BEARER_TOKEN_BEDROCK"] = line.split("=", 1)[1].strip()
        creds.append(("bearer", resolve(access.BEDROCK_CHAT, ChainContext.online(settings={"region": REGION}))))
    rows = []
    for scheme, cred in creds:
        adapter = lm(cred)
        cap.lm = lambda model_key=None, clock=None, credential=None, _a=adapter: _a  # type: ignore[method-assign]
        for model in (argv[argv.index("--models") + 1].split(",") if "--models" in argv else ("amazon.nova-2-lite-v1:0", "openai.gpt-oss-20b-1:0")):
            rows.append({"scheme": scheme, **cap.probe(f"mantle-chat-{scheme}-{model.replace('.', '-').replace(':', '_')}", Request(model=model, messages=(Message.user("Say ok."),), config=Config(max_tokens=50)))})
        treq = adapter._models_request()
        status, raw, ts, _ = cap.send(treq)
        text = raw.decode("utf-8", "replace")
        try:
            body = json.loads(text)
        except ValueError:
            body = text
        cap.write_receipt(f"probe-mantle-chat-{scheme}-models.json", {"sent": cap.wire_block(treq), "status": status, "body": body, "timestamp": ts})
        ids = [m.get("id") for m in body.get("data", [])] if isinstance(body, dict) else None
        rows.append({"scheme": scheme, "probe": "models", "status": status, "count": len(ids) if ids else None, "sample": (ids or [])[:8]})
    for r in rows:
        print(json.dumps(r)[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
