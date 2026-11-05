#!/usr/bin/env python3
"""Parallel tool calls, streamed, on every dialect — live captures for MAP-20.

One request per door: two cities, one weather tool, "call the tool for both
cities at once". The stream is pinned as ``cases/<provider>/streaming_parallel_tool_calls.json``
when the model really made two or more calls; otherwise the exchange stays
a receipt and no case is written (a single call pins nothing new).

Why (changes/2026-11-05-stream-final-copy.md): on 2026-11-05 the Codex
backend sent the arguments of parallel calls only in
``response.function_call_arguments.done`` / ``response.output_item.done``,
never as ``...arguments.delta``, and every SDK assembled each call with
input ``{}``. No pinned stream had two calls, and none had a call whose
arguments arrived only in the item's final copy.

    set -a; . ../.env; set +a
    python3 research/providers/parallel_tool_calls.py [--dry-run] [--only openai-codex,anthropic] [--force]

``openai-codex`` signs in with the local Codex CLI login (a ChatGPT
subscription, no API billing). Its wire is pinned with the harness's
``chatgpt-account-id: test-account`` (PROTOCOL.md), never the real account
id, and the body's ``safety_identifier`` (a per-account pseudonym the
server echoes) is replaced before the body is written; the exchange
receipt keeps the sha256 of the bytes as received.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, WEATHER, Capture, now_ts  # noqa: E402
from lm15 import Config, Message, Request  # noqa: E402
from lm15.types import Reasoning  # noqa: E402

FEATURE = "streaming_parallel_tool_calls"
PROMPT = "Get the weather in Paris and in Oslo. Call the tool for both cities at once, in parallel."
SLUG = "stream-final-copy"

# door -> (environment variable, model, host for provenance)
DOORS: dict[str, tuple[str, str, str]] = {
    "openai-codex": ("LM15_CAPTURE_CREDENTIAL", "gpt-6.1-sol", "chatgpt.com/backend-api/codex (Codex CLI login)"),
    "openai": ("OPENAI_API_KEY", "gpt-5.4-mini", "api.openai.com"),
    "meta": ("META_API_KEY", "muse-spark-1.3", "api.meta.ai"),
    "moonshotai-responses": ("MOONSHOTAI_API_KEY", "kimi-k3", "api.moonshot.ai"),
    "anthropic": ("ANTHROPIC_API_KEY", "claude-haiku-4-5", "api.anthropic.com"),
    "gemini": ("GEMINI_API_KEY", "gemini-2.5-flash", "generativelanguage.googleapis.com"),
    "deepseek": ("DEEPSEEK_API_KEY", "deepseek-v4-flash", "api.deepseek.com"),
    # gemini-2.5-pro and gemini-3-flash-preview send each parallel call in a
    # chunk of its own (probe 2026-11-05); gemini-2.5-flash sends them in one.
    "gemini@chunked": ("GEMINI_API_KEY", "gemini-2.5-pro", "generativelanguage.googleapis.com"),
}
# A door spelled provider@variant pins under the provider, feature FEATURE_variant.
def door_provider(door: str) -> str:
    return door.split("@", 1)[0]


def door_feature(door: str) -> str:
    return FEATURE + ("_" + door.split("@", 1)[1] if "@" in door else "")

SAFETY_ID = re.compile(rb'"safety_identifier"\s*:\s*"user-[A-Za-z0-9_-]+"')


class CodexCapture(Capture):
    """The Codex door: the real account id on the wire, the harness's on the pin."""

    def __init__(self, **kwargs) -> None:
        super().__init__("openai-codex", **kwargs)
        self.account_id: str | None = None

    def lm(self, model_key=None, *, clock=None, credential=None):
        from lm15.providers.openai_codex import OpenAICodexLM

        token = self.key()
        self._secret_values.add(token)
        adapter = OpenAICodexLM(api_key=token, account_id=self.account_id)
        self.account_id = adapter.account_id
        if self.account_id:
            self._secret_values.add(self.account_id)
        return adapter

    def wire_block(self, treq) -> dict:
        block = super().wire_block(treq)
        if "chatgpt-account-id" in block["headers"]:
            block["headers"]["chatgpt-account-id"] = "test-account"
        return block

    def send(self, treq):
        status, raw, ts, headers = super().send(treq)  # hashes the bytes as received
        return status, SAFETY_ID.sub(b'"safety_identifier":"user-REDACTED"', raw), ts, headers


def capture_for(door: str) -> Capture:
    env_var, model, host = DOORS[door]
    if door == "openai-codex":
        from lm15.auth import get_codex_cli_access_token

        credential = get_codex_cli_access_token()
        os.environ["LM15_CAPTURE_CREDENTIAL"] = credential.access_token
        cap = CodexCapture(env_var=env_var, default_model=model, host=host, change_slug=SLUG)
        cap.account_id = credential.account_id
        cap.placeholder = "$CHATGPT_OAUTH_TOKEN"  # the spelling cases/openai_codex/models.json pins
        return cap
    return Capture(door_provider(door), env_var=env_var, default_model=model, host=host, change_slug=SLUG)


def request_for(model: str) -> Request:
    return Request(model=model, messages=(Message.user(PROMPT),), tools=(WEATHER,))


# The Codex door had no stream case at all: its text and single-call streams
# are pinned next to the parallel one (``--codex-singles``), so the corpus
# shows which of its items arrive in fragments and which only in final copies.
CODEX_SINGLES = {
    "streaming": (Request(model="gpt-6.1-sol", messages=(Message.user("Say ok."),)),
                  "Codex text stream: which text events the subscription backend sends (MAP-20 final copies)",
                  {"parts": {"text": {"min": 1}}, "finish_reason": "stop"}),
    "streaming_tool_call": (Request(model="gpt-6.1-sol", messages=(Message.user("What is the weather in Paris? Use the tool."),), tools=(WEATHER,)),
                            "Codex single tool call, streamed: whether its arguments arrive in fragments or only in the item's final copy (MAP-20)",
                            {"parts": {"tool_call": {"min": 1}}, "finish_reason": "tool_call"}),
    # A reasoning item whose summary has several parts: the complete path
    # joins them with "\n"; the stream must yield the same text (INV-051).
    "streaming_reasoning_summary": (
        Request(model="gpt-6.1-sol", messages=(Message.user(
            "A wildlife survey counts herons at 4 ponds over 6 days with detection rates 0.6, 0.7, 0.8 and 0.9 by pond. "
            "Daily raw counts at pond A: 3,5,4,6,2,5; B: 7,6,8,5,7,6; C: 2,3,2,4,3,3; D: 9,8,10,9,8,9. Estimate the true "
            "mean population per pond, compare the ponds, check whether any pond shows a trend, and plan a better survey. "
            "Think it through carefully."),),
            config=Config(reasoning=Reasoning(effort="high", summary="detailed"))),
        "Codex reasoning with a detailed summary, streamed: a reasoning item's summary arrives as several parts, "
        "which the complete path joins with a newline (INV-051, MAP-20)",
        {"parts": {"thinking": {"min": 1}, "text": {"min": 1}}, "finish_reason": "stop"}),
}


def run_incomplete(door: str, *, dry_run: bool, force: bool) -> dict:
    """A Responses stream cut short by the output limit: OpenAI's documented
    ending for it is ``response.incomplete``, not ``response.completed``."""
    cap = capture_for(door)
    cap.dry_run = dry_run
    cap.receipts = CONTRACT / "receipts" / f"{cap.date}-{SLUG}" / door
    model = DOORS[door][1]
    request = Request(model=model, messages=(Message.user("Describe the life of a grey heron in about 300 words."),),
                      config=Config(max_tokens=40))
    row = cap.write_case("streaming_incomplete", request, stream=True,
                         description="A Responses stream cut short by max_output_tokens: it ends with response.incomplete; "
                                     "the turn's finish reason is length and its usage is counted (MAP-3, MAP-20 change)",
                         expect_lm15={"finish_reason": "length", "usage": {"required": True}},
                         evidence_note="max_output_tokens 40 on a 300-word answer", force=force)
    row["door"] = f"{door}/streaming_incomplete"
    if not dry_run and not row.get("skipped"):
        case = json.loads((CONTRACT / "cases" / door / "streaming_incomplete.json").read_text(encoding="utf-8"))
        row["wire_events"] = wire_event_counts((CONTRACT / "bodies" / case["id"] / case["pinned_body"]).read_bytes())
    return row


def run_codex_singles(*, dry_run: bool, force: bool) -> list[dict]:
    cap = capture_for("openai-codex")
    cap.dry_run = dry_run
    cap.receipts = CONTRACT / "receipts" / f"{cap.date}-{SLUG}" / "openai-codex"
    rows = []
    for feature, (request, description, expect) in CODEX_SINGLES.items():
        row = cap.write_case(feature, request, stream=True, description=description, expect_lm15=expect,
                             evidence_note="the subscription door's stream shape for this item kind", force=force)
        row["door"] = f"openai-codex/{feature}"
        if not dry_run and not row.get("skipped"):
            case = json.loads((CONTRACT / "cases" / "openai-codex" / f"{feature}.json").read_text(encoding="utf-8"))
            row["wire_events"] = wire_event_counts((CONTRACT / "bodies" / case["id"] / case["pinned_body"]).read_bytes())
        rows.append(row)
    return rows


def run(door: str, *, dry_run: bool, force: bool) -> dict:
    cap = capture_for(door)
    cap.dry_run = dry_run
    cap.receipts = CONTRACT / "receipts" / f"{cap.date}-{SLUG}" / door.replace("@", "-")
    model = DOORS[door][1]
    request = request_for(model)
    feature = door_feature(door)
    row = cap.write_case(
        feature, request, stream=True,
        description=("Two parallel tool calls, streamed: each call's arguments must reach the Response whole, "
                     "from fragments, from the item's final copy, or both (MAP-20)"),
        expect_lm15={"parts": {"tool_call": {"min": 2}}, "finish_reason": "tool_call"},
        evidence_note="parallel tool calls asked for in the prompt; the receipt row counts the calls",
        force=force)
    row["door"] = door
    if dry_run or row.get("skipped"):
        return row
    case_path = CONTRACT / "cases" / door_provider(door) / f"{feature}.json"
    case = json.loads(case_path.read_text(encoding="utf-8"))
    body = (CONTRACT / "bodies" / case["id"] / case["pinned_body"]).read_bytes()
    row["wire_events"] = wire_event_counts(body)
    # Count the calls from the provider's own words, not the SDK under test:
    # the body's final copy (Responses), content blocks (Anthropic), parts
    # (Gemini), or distinct tool_calls indexes (Chat).
    row["calls"] = provider_call_count(body)
    failed = any(p.get("type") in ("error", "response.failed") or "error" in p for p in sse_payloads(body))
    if failed:
        # An in-stream failure on HTTP 200 (the 2026-11-05 OpenAI run:
        # insufficient_quota) is evidence of the failure, not of the shape.
        case_path.unlink()
        (CONTRACT / "bodies" / case["id"] / case["pinned_body"]).unlink()
        try:
            (CONTRACT / "bodies" / case["id"]).rmdir()
        except OSError:
            pass
        cap.write_receipt(f"failed-{feature}-{row['timestamp']}.txt", body.decode("utf-8", "replace"))
        row["skipped"] = "in-stream failure on HTTP 200: body kept under receipts/, no case written"
        return row
    if row["calls"] < 2:
        case_path.unlink()
        (CONTRACT / "bodies" / case["id"] / case["pinned_body"]).unlink()
        try:
            (CONTRACT / "bodies" / case["id"]).rmdir()
        except OSError:
            pass
        cap.write_receipt(f"not-parallel-{row['timestamp']}.txt", body.decode("utf-8", "replace"))
        row["skipped"] = f"{row['calls']} call(s): not parallel; body kept under receipts/, no case written"
    return row


def sse_payloads(body: bytes) -> list[dict]:
    out = []
    for line in body.decode("utf-8", "replace").splitlines():
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data != "[DONE]":
                try:
                    value = json.loads(data)
                except ValueError:
                    continue
                if isinstance(value, dict):
                    out.append(value)
    return out


def wire_event_counts(body: bytes) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in sse_payloads(body):
        key = str(p.get("type") or ("chat.chunk" if "choices" in p else "gemini.chunk" if "candidates" in p else "?"))
        counts[key] = counts.get(key, 0) + 1
    return counts


def provider_call_count(body: bytes) -> int:
    payloads = sse_payloads(body)
    for p in reversed(payloads):
        if p.get("type") == "response.completed":
            return sum(1 for item in p["response"].get("output", []) if item.get("type") == "function_call")
    anthropic = [p for p in payloads if p.get("type") == "content_block_start"
                 and (p.get("content_block") or {}).get("type") == "tool_use"]
    if anthropic:
        return len(anthropic)
    gemini = 0
    chat: set[int] = set()
    for p in payloads:
        for cand in p.get("candidates") or []:
            gemini += sum(1 for part in (cand.get("content") or {}).get("parts") or [] if "functionCall" in part)
        for choice in p.get("choices") or []:
            for tc in (choice.get("delta") or {}).get("tool_calls") or []:
                chat.add(int(tc.get("index", 0)))
    return gemini or len(chat)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="comma-separated doors: " + ",".join(DOORS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--codex-singles", action="store_true", help="also pin the Codex text and single-call streams")
    ap.add_argument("--incomplete", help="comma-separated Responses doors: pin a stream cut short by the output limit")
    args = ap.parse_args()
    doors = [d for d in args.only.split(",") if d] if args.only is not None else list(DOORS)
    rows = []
    if args.codex_singles:
        rows += run_codex_singles(dry_run=args.dry_run, force=args.force)
    for door in (args.incomplete.split(",") if args.incomplete else []):
        rows.append(run_incomplete(door, dry_run=args.dry_run, force=args.force))
    for door in doors:
        if door not in DOORS:
            sys.exit(f"unknown door {door!r}; known: {', '.join(DOORS)}")
        try:
            rows.append(run(door, dry_run=args.dry_run, force=args.force))
        except SystemExit as exc:  # a missing key is a row, not the end of the run
            rows.append({"door": door, "skipped": str(exc)})
        except Exception as exc:
            rows.append({"door": door, "error": f"{type(exc).__name__}: {str(exc)[:300]}"})
    if not args.dry_run:
        out = CONTRACT / "receipts" / f"{now_ts()[:10]}-{SLUG}"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"SUMMARY-{now_ts()}-{uuid.uuid4().hex[:8]}.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k in ("door", "status", "calls", "skipped", "error", "wire_events", "parse")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
