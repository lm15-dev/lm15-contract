#!/usr/bin/env python3
"""Build the synthetic example day under gateway/examples/<day>/.

The rows illustrate the capture record (gateway/schema/capture-v1.json).
They are SYNTHETIC: no gateway ran. What is real is the provider bytes —
every response body is a pinned body from bodies/ and every canonical
Request/Response/event trace is the reviewed golden for the same case —
so a reader sees genuine wire shapes and genuine canonical forms. What is
invented is stated per row in `_provenance.json`: timings, pids, request
headers, response headers, ids. `wire_sha256` is deliberately absent:
there was no unredacted wire (AUTHORITY.md; see gateway/README.md
"Promotion").

Deterministic: running it twice yields identical bytes. The checker
(tools/check_gateway.py) verifies the output like any fixture; this
script never runs in CI and never touches anything outside its own day.

Usage: python3 gateway/examples/build.py [--root DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

DAY = "2026-09-19"
PIN = None  # filled from CONTRACT_PIN of lm15-go at build time, see main()

CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def ulid(t: datetime, label: str) -> str:
    """A real ULID: 48-bit ms timestamp, then 80 bits derived from `label`."""
    ms = int(t.timestamp() * 1000)
    ts = ""
    for _ in range(10):
        ts = CROCKFORD[ms & 31] + ts
        ms >>= 5
    rnd = int.from_bytes(hashlib.sha256(label.encode()).digest()[:10], "big")
    tail = ""
    for _ in range(16):
        tail = CROCKFORD[rnd & 31] + tail
        rnd >>= 5
    return ts + tail


def stamp(hms: str, ms: int) -> datetime:
    return datetime.strptime(f"{DAY}T{hms}.{ms:03d}Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def iso(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


def http_message(start_line: str, headers: list[tuple[str, str]], body: bytes) -> bytes:
    head = start_line + "\r\n" + "".join(f"{k}: {v}\r\n" for k, v in headers) + "\r\n"
    return head.encode() + body


class Day:
    def __init__(self, root: Path):
        self.dir = root / "gateway" / "examples" / DAY
        self.exchanges: list[dict] = []
        self.events: list[dict] = []
        self.scan: list[dict] = []
        self.decoded: list[dict] = []
        self.provenance: dict[str, str] = {}
        self.blobs: dict[str, bytes] = {}

    def blob(self, data: bytes, content_encoding: str | None = None) -> dict:
        h = hashlib.sha256(data).hexdigest()
        self.blobs[h] = data
        ref = {"sha256": h, "bytes": len(data)}
        if content_encoding:
            ref["content_encoding"] = content_encoding
        return ref

    def write(self) -> None:
        if self.dir.exists():
            shutil.rmtree(self.dir)
        for name, rows in (("exchanges", self.exchanges), ("events", self.events),
                           ("scan", self.scan), ("decoded", self.decoded)):
            p = self.dir / name / f"{DAY}.jsonl"
            p.parent.mkdir(parents=True)
            p.write_text("".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n" for r in rows))
        for h, data in self.blobs.items():
            suffix = ".jsonl" if data.startswith(b"{") else ".http"
            p = self.dir / "raw" / h[:2] / f"{h}{suffix}"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        (self.dir / "_provenance.json").write_text(json.dumps({
            "synthetic": True,
            "built_by": "gateway/examples/build.py",
            "statement": "No gateway ran. Response bodies are pinned bodies from bodies/; canonical forms are the reviewed goldens for the same cases. Timings, pids, ids, request headers and response headers are invented to illustrate the record. wire_sha256 is absent because no unredacted wire existed; these rows can never be promoted to gateway/captures/.",
            "rows": self.provenance,
        }, indent=2, ensure_ascii=False) + "\n")


def sse_frames(body: bytes) -> list[tuple[str, int]]:
    """(event name, bytes) per SSE event, splitting on the blank line."""
    out = []
    for chunk in body.decode().split("\n\n"):
        if not chunk.strip():
            continue
        name = next((l[len("event:"):].strip() for l in chunk.splitlines() if l.startswith("event:")), None)
        out.append((name, len(chunk.encode()) + 2))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    root = ap.parse_args().root
    pin = (root / ".." / "lm15-go" / "CONTRACT_PIN").read_text().strip() if (root / ".." / "lm15-go" / "CONTRACT_PIN").exists() else "0" * 40
    day = Day(root)

    def case(provider: str, feature: str) -> tuple[dict, bytes, dict]:
        c = json.loads((root / "cases" / provider / f"{feature}.json").read_text())
        body = (root / "bodies" / f"{provider}.{feature}" / c["pinned_body"]).read_bytes()
        g = json.loads((root / "goldens" / provider / f"{feature}.json").read_text())
        return c, body, g

    # ---- 1. Claude Code, Anthropic Messages, streamed ------------------------
    c, body, g = case("anthropic", "streaming")
    t = stamp("14:03:12", 481)
    id1 = ulid(t, "claude-code streaming")
    req_body = json.dumps(c["request"]["body"], separators=(",", ":")).encode()
    req = day.blob(http_message("POST /v1/messages HTTP/1.1", [
        ("host", "api.anthropic.com"),
        ("content-type", "application/json"),
        ("anthropic-version", "2023-06-01"),
        ("x-api-key", "[redacted:108]"),
        ("user-agent", "claude-cli/2.1.276 (external, cli)"),
        ("accept", "text/event-stream"),
        ("content-length", str(len(req_body))),
    ], req_body))
    resp = day.blob(http_message("HTTP/1.1 200 OK", [
        ("content-type", "text/event-stream; charset=utf-8"),
        ("request-id", "req_011CT4synthetic0000000001"),
        ("content-length", str(len(body))),
    ], body))
    frames = sse_frames(body)
    offsets = [412, 415, 640, 905, 1010, 1012, 1018, 1019]
    day.exchanges.append({
        "v": 1, "id": id1, "t": iso(t), "t_end": iso(stamp("14:03:13", 502)),
        "tag": "claude-code",
        "origin": {"user_agent": "claude-cli/2.1.276 (external, cli)", "pid": 1453480, "exe": "/home/maxime/.local/share/claude/versions/2.1.276"},
        "provider": "anthropic", "api_family": "anthropic_messages",
        "method": "POST", "path": "/v1/messages", "transport": "sse",
        "upstream": {"url": "https://api.anthropic.com/v1/messages", "status": 200,
                     "request_id": "req_011CT4synthetic0000000001", "ttfb_ms": 409, "latency_ms": 1017},
        "model": {"asked": "claude-sonnet-4-5", "sent": "claude-sonnet-4-5", "served": "claude-sonnet-4-5-20250929"},
        "usage": g["canonical_response"]["usage"],
        "redacted": ["x-api-key"],
        "raw": {"request": req, "response": resp},
    })
    for seq, ((name, n), off) in enumerate(zip(frames, offsets)):
        row = {"v": 1, "id": id1, "seq": seq, "t_offset_ms": off, "bytes": n}
        if name:
            row["event"] = name
        day.events.append(row)
    day.decoded.append({
        "v": 1, "id": id1, "t": iso(stamp("14:03:13", 540)),
        "decoder": {"name": "lm15-python", "version": "1.0.0rc3"}, "contract_pin": pin,
        "status": "full", "request": c["canonical_request"], "response": g["canonical_response"], "events": g["events"],
    })
    day.provenance[id1] = "request body: cases/anthropic/streaming.json; response body: bodies/anthropic.streaming/" + c["pinned_body"] + "; canonical: goldens/anthropic/streaming.json; events timing invented"

    # ---- 2. Codex, OpenAI Responses, not streamed ---------------------------
    c, body, g = case("openai", "basic_text")
    t = stamp("14:05:40", 12)
    id2 = ulid(t, "codex responses")
    req_body = json.dumps(c["request"]["body"], separators=(",", ":")).encode()
    req = day.blob(http_message("POST /v1/responses HTTP/1.1", [
        ("host", "api.openai.com"),
        ("content-type", "application/json"),
        ("authorization", "[redacted:171]"),
        ("user-agent", "codex_cli_rs/0.153.4 (Linux 6.12; x86_64)"),
        ("content-length", str(len(req_body))),
    ], req_body))
    resp = day.blob(http_message("HTTP/1.1 200 OK", [
        ("content-type", "application/json"),
        ("x-request-id", "req_synthetic0000000000000002"),
        ("content-length", str(len(body))),
    ], body), content_encoding="gzip")
    day.exchanges.append({
        "v": 1, "id": id2, "t": iso(t), "t_end": iso(stamp("14:05:41", 233)),
        "tag": "codex",
        "origin": {"user_agent": "codex_cli_rs/0.153.4 (Linux 6.12; x86_64)", "pid": 1460021, "exe": "/nix/store/i0p1gqyr0mq8fg76566p62lqhk4kc1bw-codex-0.153.4/bin/codex"},
        "provider": "openai", "api_family": "openai_responses",
        "method": "POST", "path": "/v1/responses", "transport": "http",
        "upstream": {"url": "https://api.openai.com/v1/responses", "status": 200,
                     "request_id": "req_synthetic0000000000000002", "ttfb_ms": 1198, "latency_ms": 1201},
        "model": {"asked": "gpt-4.1-mini", "sent": "gpt-4.1-mini", "served": "gpt-4.1-mini-2025-04-14"},
        "usage": g["canonical_response"]["usage"],
        "redacted": ["authorization"],
        "raw": {"request": req, "response": resp},
    })
    day.events.append({"v": 1, "id": id2, "seq": 0, "t_offset_ms": 1201, "bytes": len(body)})
    day.decoded.append({
        "v": 1, "id": id2, "t": iso(stamp("14:05:41", 260)),
        "decoder": {"name": "lm15-python", "version": "1.0.0rc3"}, "contract_pin": pin,
        "status": "full", "request": c["canonical_request"], "response": g["canonical_response"],
    })
    day.provenance[id2] = "request body: cases/openai/basic_text.json; response body: bodies/openai.basic_text/" + c["pinned_body"] + "; canonical: goldens/openai/basic_text.json; content_encoding gzip is illustrative"

    # ---- 3. aiconvo's memory pass through Pi, rewritten by a rule -----------
    c, body, g = case("anthropic", "basic_text")
    t = stamp("14:07:02", 907)
    id3 = ulid(t, "aiconvo rewrite")
    asked = dict(c["request"]["body"], model="claude-haiku-4-5")
    req_body = json.dumps(asked, separators=(",", ":")).encode()
    req = day.blob(http_message("POST /v1/messages HTTP/1.1", [
        ("host", "api.anthropic.com"),
        ("content-type", "application/json"),
        ("anthropic-version", "2023-06-01"),
        ("x-api-key", "[redacted:108]"),
        ("user-agent", "pi-coding-agent/0.58.0"),
        ("content-length", str(len(req_body))),
    ], req_body))
    resp = day.blob(http_message("HTTP/1.1 200 OK", [
        ("content-type", "application/json"),
        ("request-id", "req_011CT4synthetic0000000003"),
        ("content-length", str(len(body))),
    ], body))
    day.exchanges.append({
        "v": 1, "id": id3, "t": iso(t), "t_end": iso(stamp("14:07:03", 611)),
        "tag": "aiconvo-memory",
        "origin": {"user_agent": "pi-coding-agent/0.58.0", "pid": 1460388, "exe": "/home/maxime/.nix-profile/bin/node"},
        "provider": "anthropic", "api_family": "anthropic_messages",
        "method": "POST", "path": "/v1/messages", "transport": "http",
        "upstream": {"url": "https://api.anthropic.com/v1/messages", "status": 200,
                     "request_id": "req_011CT4synthetic0000000003", "ttfb_ms": 690, "latency_ms": 701},
        "model": {"asked": "claude-haiku-4-5", "sent": "claude-sonnet-4-5", "served": "claude-sonnet-4-5-20250929"},
        "usage": g["canonical_response"]["usage"],
        "route": {"rule": "memory-on-sonnet", "lane": "rewrite"},
        "redacted": ["x-api-key"],
        "raw": {"request": req, "response": resp},
    })
    day.events.append({"v": 1, "id": id3, "seq": 0, "t_offset_ms": 701, "bytes": len(body)})
    day.decoded.append({
        "v": 1, "id": id3, "t": iso(stamp("14:07:03", 640)),
        "decoder": {"name": "lm15-python", "version": "1.0.0rc3"}, "contract_pin": pin,
        "status": "full", "request": dict(c["canonical_request"], model="claude-haiku-4-5"), "response": g["canonical_response"],
    })
    day.provenance[id3] = "request body: cases/anthropic/basic_text.json with model rewritten to claude-haiku-4-5 to show a rewrite lane; response body: bodies/anthropic.basic_text/" + c["pinned_body"] + "; canonical: goldens/anthropic/basic_text.json; the decoded request carries the model AS ASKED (what the application meant), the exchange row carries asked and sent"

    # ---- 4. Claude Code lists models: a non-model call, kept ----------------
    t = stamp("14:03:11", 990)
    id4 = ulid(t, "claude-code models")
    req = day.blob(http_message("GET /v1/models?limit=20 HTTP/1.1", [
        ("host", "api.anthropic.com"),
        ("anthropic-version", "2023-06-01"),
        ("x-api-key", "[redacted:108]"),
        ("user-agent", "claude-cli/2.1.276 (external, cli)"),
    ], b""))
    listing = json.dumps({"data": [{"type": "model", "id": "claude-sonnet-4-5-20250929", "display_name": "Claude Sonnet 4.5", "created_at": "2025-09-29T00:00:00Z"}], "has_more": False, "first_id": "claude-sonnet-4-5-20250929", "last_id": "claude-sonnet-4-5-20250929"}, separators=(",", ":")).encode()
    resp = day.blob(http_message("HTTP/1.1 200 OK", [
        ("content-type", "application/json"),
        ("request-id", "req_011CT4synthetic0000000004"),
        ("content-length", str(len(listing))),
    ], listing))
    day.exchanges.append({
        "v": 1, "id": id4, "t": iso(t), "t_end": iso(stamp("14:03:12", 210)),
        "tag": "claude-code",
        "origin": {"user_agent": "claude-cli/2.1.276 (external, cli)", "pid": 1453480, "exe": "/home/maxime/.local/share/claude/versions/2.1.276"},
        "provider": "anthropic", "api_family": "unknown",
        "method": "GET", "path": "/v1/models?limit=20", "transport": "http",
        "upstream": {"url": "https://api.anthropic.com/v1/models?limit=20", "status": 200,
                     "request_id": "req_011CT4synthetic0000000004", "ttfb_ms": 212, "latency_ms": 214},
        "redacted": ["x-api-key"],
        "raw": {"request": req, "response": resp},
    })
    day.events.append({"v": 1, "id": id4, "seq": 0, "t_offset_ms": 214, "bytes": len(listing)})
    day.decoded.append({
        "v": 1, "id": id4, "t": iso(stamp("14:03:12", 230)),
        "decoder": {"name": "lm15-python", "version": "1.0.0rc3"}, "contract_pin": pin,
        "status": "none", "notes": ["GET /v1/models is a catalog listing, not a model call; kept because it left the machine"],
    })
    day.provenance[id4] = "listing body invented (one entry, Anthropic list shape); shows api_family unknown, no model, decoded status none"

    # ---- 5. An agent sent a .env it read: verbatim, marked ------------------
    c, body, g = case("anthropic", "basic_text")
    t = stamp("14:12:55", 74)
    id5 = ulid(t, "claude-code env leak")
    env_text = "Here is my .env, why does the deploy fail?\n\nAWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_REGION=us-east-1\n"
    leaky = {"model": "claude-sonnet-4-5", "max_tokens": 1024, "messages": [{"role": "user", "content": [{"type": "text", "text": env_text}]}]}
    req_body = json.dumps(leaky, separators=(",", ":")).encode()
    req_bytes = http_message("POST /v1/messages HTTP/1.1", [
        ("host", "api.anthropic.com"),
        ("content-type", "application/json"),
        ("anthropic-version", "2023-06-01"),
        ("x-api-key", "[redacted:108]"),
        ("user-agent", "claude-cli/2.1.276 (external, cli)"),
        ("content-length", str(len(req_body))),
    ], req_body)
    req = day.blob(req_bytes)
    needle = b"AKIAIOSFODNN7EXAMPLE"
    off = req_bytes.index(needle)
    resp = day.blob(http_message("HTTP/1.1 200 OK", [
        ("content-type", "application/json"),
        ("request-id", "req_011CT4synthetic0000000003"),
        ("content-length", str(len(body))),
    ], body))  # identical bytes to exchange 3's response: same blob, one file (content addressing)
    day.exchanges.append({
        "v": 1, "id": id5, "t": iso(t), "t_end": iso(stamp("14:12:56", 301)),
        "tag": "claude-code",
        "origin": {"user_agent": "claude-cli/2.1.276 (external, cli)", "pid": 1453480, "exe": "/home/maxime/.local/share/claude/versions/2.1.276"},
        "provider": "anthropic", "api_family": "anthropic_messages",
        "method": "POST", "path": "/v1/messages", "transport": "http",
        "upstream": {"url": "https://api.anthropic.com/v1/messages", "status": 200,
                     "request_id": "req_011CT4synthetic0000000003", "ttfb_ms": 1211, "latency_ms": 1224},
        "model": {"asked": "claude-sonnet-4-5", "sent": "claude-sonnet-4-5", "served": "claude-sonnet-4-5-20250929"},
        "usage": g["canonical_response"]["usage"],
        "redacted": ["x-api-key"],
        "secrets": {"found": 1, "kinds": ["aws access key id"], "action": "marked",
                    "locations": [{"blob": "request", "offset": off, "length": len(needle), "kind": "aws access key id"}]},
        "raw": {"request": req, "response": resp},
    })
    day.events.append({"v": 1, "id": id5, "seq": 0, "t_offset_ms": 1224, "bytes": len(body)})
    day.decoded.append({
        "v": 1, "id": id5, "t": iso(stamp("14:12:56", 330)),
        "decoder": {"name": "lm15-python", "version": "1.0.0rc3"}, "contract_pin": pin,
        "status": "full",
        "request": {"model": "claude-sonnet-4-5", "messages": [{"role": "user", "parts": [{"type": "text", "text": env_text}]}], "config": {"max_tokens": 1024}},
        "response": g["canonical_response"],
    })
    day.provenance[id5] = "request invented around AWS's published example access key id AKIAIOSFODNN7EXAMPLE (chosen so tools/check_secrecy.py stays clean; a real id of that shape is what the gateway marks); response body: bodies/anthropic.basic_text/" + c["pinned_body"] + " — the same bytes as the rewrite exchange, so the same blob file: content addressing in action"

    # ---- 6. Aborted: the application went away mid-request ------------------
    t = stamp("14:15:30", 0)
    id6 = ulid(t, "pi aborted")
    req_body = json.dumps({"model": "claude-sonnet-4-5", "max_tokens": 4096, "stream": True, "messages": [{"role": "user", "content": [{"type": "text", "text": "Summarise the repository."}]}]}, separators=(",", ":")).encode()
    req = day.blob(http_message("POST /v1/messages HTTP/1.1", [
        ("host", "api.anthropic.com"),
        ("content-type", "application/json"),
        ("anthropic-version", "2023-06-01"),
        ("x-api-key", "[redacted:108]"),
        ("user-agent", "pi-coding-agent/0.58.0"),
        ("accept", "text/event-stream"),
        ("content-length", str(len(req_body))),
    ], req_body))
    day.exchanges.append({
        "v": 1, "id": id6, "t": iso(t),
        "tag": "pi",
        "origin": {"user_agent": "pi-coding-agent/0.58.0", "pid": 1461902, "exe": "/home/maxime/.nix-profile/bin/node"},
        "provider": "anthropic", "api_family": "anthropic_messages",
        "method": "POST", "path": "/v1/messages", "transport": "sse",
        "upstream": {"url": "https://api.anthropic.com/v1/messages"},
        "model": {"asked": "claude-sonnet-4-5", "sent": "claude-sonnet-4-5"},
        "error": {"code": "transport", "message": "application closed the connection 0.8 s after sending the request, before any upstream byte arrived; upstream request cancelled"},
        "redacted": ["x-api-key"],
        "raw": {"request": req},
    })
    day.decoded.append({
        "v": 1, "id": id6, "t": iso(stamp("14:15:31", 5)),
        "decoder": {"name": "lm15-python", "version": "1.0.0rc3"}, "contract_pin": pin,
        "status": "partial", "notes": ["no response: the exchange aborted before any upstream byte"],
        "request": {"model": "claude-sonnet-4-5", "messages": [{"role": "user", "parts": [{"type": "text", "text": "Summarise the repository."}]}], "config": {"max_tokens": 4096}},
    })
    day.provenance[id6] = "request invented; shows an abort: no t_end, no response blob, no usage, error.code transport, decoded status partial"

    # ---- scan: what the coverage view saw during the same minutes -----------
    day.scan += [
        {"v": 1, "t": iso(stamp("14:03:12", 500)), "pid": 1453480, "exe": "/home/maxime/.local/share/claude/versions/2.1.276",
         "remote": "127.0.0.1:4315", "match": "ip", "coverage": "covered"},
        {"v": 1, "t": iso(stamp("14:05:40", 20)), "pid": 1460021, "exe": "/nix/store/i0p1gqyr0mq8fg76566p62lqhk4kc1bw-codex-0.153.4/bin/codex",
         "remote": "127.0.0.1:4315", "match": "ip", "coverage": "covered"},
        {"v": 1, "t": iso(stamp("14:06:10", 344)), "pid": 1387744, "exe": "/home/maxime/.local/share/cursor/cursor", "cmdline": "cursor --type=utility",
         "host": "api.openai.com", "remote": "162.159.140.245:443", "match": "ip", "shared_range": True,
         "coverage": "observed", "recipe": "cursor"},
        {"v": 1, "t": iso(stamp("14:06:10", 350)), "pid": 1387744, "exe": "/home/maxime/.local/share/cursor/cursor", "cmdline": "cursor --type=utility",
         "host": "api.openai.com", "remote": "162.159.140.245:443", "match": "dns",
         "coverage": "observed", "recipe": "cursor"},
        {"v": 1, "t": iso(stamp("14:09:48", 71)), "pid": 1302210, "exe": "/nix/store/2b0m6w5q3p0y7m4l4b1c0b0s0sh8z0r8-some-electron-app/bin/some-app",
         "host": "generativelanguage.googleapis.com", "remote": "172.217.113.4:443", "match": "ip",
         "coverage": "observed_not_coverable"},
    ]
    day.provenance["scan"] = "all invented; shows covered, observed (same connection first by ip on a shared range, then confirmed by the dns helper), and observed_not_coverable"

    day.write()
    print(f"wrote {day.dir}: {len(day.exchanges)} exchanges, {len(day.events)} events, {len(day.scan)} scan, {len(day.decoded)} decoded, {len(day.blobs)} blobs")


if __name__ == "__main__":
    main()
