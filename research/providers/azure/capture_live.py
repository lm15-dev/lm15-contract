#!/usr/bin/env python3
"""Capture one Azure OpenAI GA Realtime text turn as a contract transcript."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "lm15-python"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _azure import load_lab_env  # noqa: E402
from lm15 import LiveConfig, access, serde  # noqa: E402
from lm15.providers import OpenAILM  # noqa: E402
from lm15.types import LiveClientTextEvent  # noqa: E402

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace the existing case after successful capture")
    parser.add_argument("--dry-run", action="store_true", help="refuse live work without reading credentials")
    args = parser.parse_args()
    if args.dry_run:
        print("Live-only WebSocket capture: no offline wire builder; no credentials read or calls made.")
        return 2
    contract = Path(__file__).resolve().parents[3]
    case_dir = contract / "cases" / "azure"
    if (case_dir / "live_text.json").exists() and not args.force:
        print("case exists (use --force); no calls made")
        return 2
    load_lab_env()
    resource = os.environ["AZURE_OPENAI_RESOURCE"]
    key = os.environ["AZURE_OPENAI_API_KEY"]
    lm = OpenAILM(api_key=key, access=access.AZURE, settings={"resource": resource})
    config = LiveConfig(model="gpt-realtime-mini", system="Be terse.")
    event = LiveClientTextEvent(text="Reply with exactly: azure live hello")
    setup = lm._live_setup_frames(config)
    frames = lm._live_encoder(config)(event)
    transcript: list[dict] = [
        {"dir": "client", "kind": "setup", "frames": setup},
        {"dir": "client", "kind": "event", "event": serde.live_client_event_to_dict(event), "frames": frames},
    ]
    with lm._live_connect(lm._live_url(config.model), lm._live_headers()) as ws:
        for frame in setup + frames:
            ws.send(json.dumps(frame))
        while True:
            raw = ws.recv(timeout=60)
            if isinstance(raw, bytes):
                import base64
                transcript.append({"dir": "server", "frame_b64": base64.b64encode(raw).decode("ascii")})
            else:
                transcript.append({"dir": "server", "frame": raw})
            payload = json.loads(raw)
            if payload.get("type") in ("response.done", "error", "response.error"):
                break

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    text = "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n" for row in transcript)
    if payload.get("type") != "response.done" or payload.get("response", {}).get("status") != "completed":
        receipts = contract / "receipts" / f"{ts[:10]}-azure"
        receipts.mkdir(parents=True, exist_ok=True)
        (receipts / f"failed-live-text-{ts}.jsonl").write_text(text.replace(key, "$AZURE_OPENAI_API_KEY"))
        print("turn failed; transcript kept under receipts, no case written")
        return 1
    body_dir = contract / "bodies" / "azure.live_text"
    body_dir.mkdir(parents=True, exist_ok=True)
    body_name = f"{ts}.jsonl"
    (body_dir / body_name).write_text(text)
    case_dir.mkdir(parents=True, exist_ok=True)
    case = {
        "id": "azure.live_text", "provider": "azure", "feature": "live_text", "surface": "live",
        "settings": {"resource": resource},
        "description": "Azure OpenAI GA Realtime text turn: api-key WebSocket, session.update, text deltas, response.done",
        "provenance": {"source": "live-capture", "date": ts[:10],
                       "evidence": f"live end-to-end against wss://{resource}.openai.azure.com/openai/v1/realtime, deployment gpt-realtime-mini; {len(transcript)-2} verbatim server frames at bodies/azure.live_text/{body_name}; changes/2026-09-04-azure-live.md"},
        "live_config": serde.live_config_to_dict(config), "pinned_body": body_name,
    }
    (case_dir / "live_text.json").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
    print(f"captured {len(transcript)-2} server frames -> {body_dir / body_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
