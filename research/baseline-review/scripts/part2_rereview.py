#!/usr/bin/env python3
"""Part 2: independent re-review of the 88 new goldens against their pinned
bodies and the 2026-09-06 decisions (D5, D6, D7, D8, D9, D10) plus INV-051.

Stdlib only. Does not import lm15.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/maxime/Projects/lm15-dev/lm15-contract")
OLD = "cf298d2"
PROVIDERS = ["meta", "meta-chat", "meta-anthropic", "azure", "azure-chat", "bedrock-chat", "bedrock-mantle-chat"]
DIALECT = {  # D7: continuation provider is the dialect
    "meta": "openai", "azure": "openai",
    "meta-chat": "openai_chat", "azure-chat": "openai_chat", "bedrock-chat": "openai_chat", "bedrock-mantle-chat": "openai_chat",
    "meta-anthropic": "anthropic",
}
CHAT_FINISH = {"stop": "stop", "tool_calls": "tool_call", "length": "length", "content_filter": "content_filter"}
ANTH_FINISH = {"end_turn": "stop", "tool_use": "tool_call", "max_tokens": "length", "stop_sequence": "stop"}


def load(p):
    return json.loads(Path(p).read_text())


def git_show(rel):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{OLD}:{rel}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def case_for(provider, stem):
    for c in (ROOT / "cases").glob("*/*.json"):
        cj = load(c)
        if cj.get("provider") == provider and cj.get("id", "").split(".", 1)[1] == stem:
            return cj
    return None


def sse_frames(text):
    out = []
    for line in text.splitlines():
        if line.startswith("data:"):
            p = line[5:].strip()
            if p and p != "[DONE]":
                out.append(json.loads(p))
    return out


def clean(d):
    """Drop None values (serde omission) for comparison."""
    return {k: v for k, v in d.items() if v is not None}


# ───────── usage mapping ─────────

def usage_openai_responses(u):
    if not u:
        return None
    itd, otd = u.get("input_tokens_details") or {}, u.get("output_tokens_details") or {}
    return clean({
        "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"), "total_tokens": u.get("total_tokens"),
        "cache_read_tokens": itd.get("cached_tokens"), "cache_write_tokens": itd.get("cache_write_tokens"),
        "reasoning_tokens": otd.get("reasoning_tokens"),
    })


def usage_chat(u):
    if not u:
        return None
    ptd, ctd = u.get("prompt_tokens_details") or {}, u.get("completion_tokens_details") or {}
    return clean({
        "input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens"), "total_tokens": u.get("total_tokens"),
        "cache_read_tokens": ptd.get("cached_tokens"), "reasoning_tokens": ctd.get("reasoning_tokens"),
        "input_audio_tokens": ptd.get("audio_tokens"), "output_audio_tokens": ctd.get("audio_tokens"),
    })


def usage_anthropic(u):
    if not u:
        return None
    i, o = u.get("input_tokens"), u.get("output_tokens")
    otd = u.get("output_tokens_details") or {}
    return clean({
        "input_tokens": i, "output_tokens": o, "total_tokens": (i + o) if i is not None and o is not None else None,
        "cache_read_tokens": u.get("cache_read_input_tokens"), "cache_write_tokens": u.get("cache_creation_input_tokens"),
        "reasoning_tokens": otd.get("thinking_tokens"),
    })


# ───────── body → expected response (complete path) ─────────

def responses_from_body(resp):
    parts = []
    has_call = False
    for item in resp.get("output") or []:
        t = item.get("type")
        if t == "reasoning":
            text = "".join(s.get("text", "") for s in item.get("summary") or [] if s.get("type") == "summary_text")
            data = {"id": item["id"]}
            if item.get("encrypted_content"):
                data["encrypted_content"] = item["encrypted_content"]
            parts.append({"type": "thinking", "text": text, "continuation": [{"provider": "openai", "kind": "reasoning_item", "data": data}]})
        elif t == "message":
            for c in item.get("content") or []:
                if c.get("type") == "output_text":
                    parts.append({"type": "text", "text": c["text"]})
                elif c.get("type") == "refusal":
                    parts.append({"type": "refusal", "text": c["refusal"]})
        elif t == "function_call":
            has_call = True
            parts.append({"type": "tool_call", "id": item["call_id"], "name": item["name"], "input": json.loads(item["arguments"])})
    status = resp.get("status")
    reason = (resp.get("incomplete_details") or {}).get("reason")
    if has_call:
        finish = "tool_call"
    elif status == "incomplete" and reason == "content_filter":
        finish = "content_filter"
    elif status == "incomplete" and reason == "max_output_tokens":
        finish = "length"
    else:
        finish = "stop"
    return {"id": resp.get("id"), "model": resp.get("model"), "message": {"role": "assistant", "parts": parts},
            "finish_reason": finish, "usage": usage_openai_responses(resp.get("usage"))}


def chat_from_body(body, keep_id=True):
    ch = body["choices"][0]
    m = ch["message"]
    parts = []
    if m.get("reasoning"):
        parts.append({"type": "thinking", "text": m["reasoning"]})
    if m.get("content"):
        parts.append({"type": "text", "text": m["content"]})
    for tc in m.get("tool_calls") or []:
        parts.append({"type": "tool_call", "id": tc["id"], "name": tc["function"]["name"], "input": json.loads(tc["function"]["arguments"])})
    fr = CHAT_FINISH.get(ch.get("finish_reason"), ch.get("finish_reason"))
    if any(p["type"] == "tool_call" for p in parts) and fr == "stop":
        fr = "tool_call"
    return {"id": body.get("id") if keep_id else None, "model": body.get("model"), "message": {"role": "assistant", "parts": parts},
            "finish_reason": fr, "usage": usage_chat(body.get("usage"))}


def anthropic_from_body(body):
    parts = []
    for blk in body.get("content") or []:
        t = blk["type"]
        if t == "redacted_thinking":
            parts.append({"type": "thinking", "text": "", "continuation": [{"provider": "anthropic", "kind": "redacted_thinking", "data": {"data": blk["data"]}}]})
        elif t == "thinking":
            p = {"type": "thinking", "text": blk.get("thinking", "")}
            if blk.get("signature"):
                p["continuation"] = [{"provider": "anthropic", "kind": "thinking", "data": {"signature": blk["signature"]}}]
            parts.append(p)
        elif t == "text":
            parts.append({"type": "text", "text": blk["text"]})
        elif t == "tool_use":
            parts.append({"type": "tool_call", "id": blk["id"], "name": blk["name"], "input": blk["input"]})
    fr = ANTH_FINISH.get(body.get("stop_reason"), body.get("stop_reason"))
    if any(p["type"] == "tool_call" for p in parts):
        fr = "tool_call"
    return {"id": body.get("id"), "model": body.get("model"), "message": {"role": "assistant", "parts": parts},
            "finish_reason": fr, "usage": usage_anthropic(body.get("usage"))}


# ───────── body → expected stream trace ─────────

def responses_stream(frames):
    events = []
    start = None
    completed = None
    for f in frames:
        t = f.get("type")
        if t == "response.created":
            start = {"type": "start", "id": f["response"]["id"], "model": f["response"]["model"]}
            events.append(start)
        elif t == "response.output_item.added":
            it, idx = f["item"], f["output_index"]
            if it["type"] == "reasoning":
                events.append({"type": "delta", "delta": {"type": "thinking", "part_index": idx, "text": ""}})
            elif it["type"] == "function_call":
                events.append({"type": "delta", "delta": {"type": "tool_call", "part_index": idx, "id": it["call_id"], "name": it["name"], "input": ""}})
        elif t == "response.output_item.done":
            it, idx = f["item"], f["output_index"]
            if it["type"] == "reasoning":
                data = {"id": it["id"]}
                if it.get("encrypted_content"):
                    data["encrypted_content"] = it["encrypted_content"]
                events.append({"type": "delta", "delta": {"type": "continuation", "part_index": idx, "provider": "openai", "kind": "reasoning_item", "data": data}})
        elif t == "response.output_text.delta":
            events.append({"type": "delta", "delta": {"type": "text", "part_index": f["output_index"], "text": f["delta"]}})
        elif t == "response.function_call_arguments.delta":
            events.append({"type": "delta", "delta": {"type": "tool_call", "part_index": f["output_index"], "input": f["delta"]}})
        elif t == "response.completed":
            completed = f["response"]
    r = responses_from_body(completed)
    events.append({"type": "end", "finish_reason": r["finish_reason"], "usage": r["usage"], "provider_data": completed})
    return events, r


def chat_stream(frames, req_model):
    events = [{"type": "start", "model": req_model}]
    finish = None
    usage = None
    pd = None
    for f in frames:
        for ch in f.get("choices") or []:
            d = ch.get("delta") or {}
            idx = ch.get("index", 0)
            if d.get("reasoning"):
                events.append({"type": "delta", "delta": {"type": "thinking", "part_index": idx, "text": d["reasoning"]}})
            if d.get("content"):
                events.append({"type": "delta", "delta": {"type": "text", "part_index": idx, "text": d["content"]}})
            for tc in d.get("tool_calls") or []:
                ev = {"type": "tool_call", "part_index": idx, "input": (tc.get("function") or {}).get("arguments") or ""}
                if tc.get("id"):
                    ev["id"] = tc["id"]
                if (tc.get("function") or {}).get("name"):
                    ev["name"] = tc["function"]["name"]
                events.append({"type": "delta", "delta": ev})
            if ch.get("finish_reason"):
                finish = CHAT_FINISH.get(ch["finish_reason"], ch["finish_reason"])
                if pd is None:
                    pd = f
        if f.get("usage") is not None:
            usage = usage_chat(f["usage"])
            pd = f
    end = {"type": "end", "finish_reason": finish, "usage": usage, "provider_data": pd}
    events.append(end)
    return events


def anthropic_stream(frames):
    events = []
    usage_acc = {}
    finish = None
    pd = None
    for f in frames:
        t = f.get("type")
        if t == "message_start":
            m = f["message"]
            events.append({"type": "start", "id": m["id"], "model": m["model"]})
            usage_acc.update({k: v for k, v in (m.get("usage") or {}).items() if v is not None})
        elif t == "content_block_start":
            cb, idx = f["content_block"], f["index"]
            if cb["type"] == "redacted_thinking":
                events.append({"type": "delta", "delta": {"type": "thinking", "part_index": idx, "text": ""}})
                events.append(("PENDING_REDACTED", idx, cb["data"]))
            elif cb["type"] == "thinking":
                if cb.get("thinking"):
                    events.append({"type": "delta", "delta": {"type": "thinking", "part_index": idx, "text": cb["thinking"]}})
            elif cb["type"] == "tool_use":
                events.append({"type": "delta", "delta": {"type": "tool_call", "part_index": idx, "id": cb["id"], "name": cb["name"], "input": ""}})
            elif cb["type"] == "text" and cb.get("text"):
                events.append({"type": "delta", "delta": {"type": "text", "part_index": idx, "text": cb["text"]}})
        elif t == "content_block_delta":
            d, idx = f["delta"], f["index"]
            if d["type"] == "text_delta":
                events.append({"type": "delta", "delta": {"type": "text", "part_index": idx, "text": d["text"]}})
            elif d["type"] == "thinking_delta":
                events.append({"type": "delta", "delta": {"type": "thinking", "part_index": idx, "text": d["thinking"]}})
            elif d["type"] == "input_json_delta":
                events.append({"type": "delta", "delta": {"type": "tool_call", "part_index": idx, "input": d["partial_json"]}})
            elif d["type"] == "signature_delta":
                events.append({"type": "delta", "delta": {"type": "continuation", "part_index": idx, "provider": "anthropic", "kind": "thinking", "data": {"signature": d["signature"]}}})
        elif t == "content_block_stop":
            idx = f["index"]
            for i, e in enumerate(events):
                if isinstance(e, tuple) and e[0] == "PENDING_REDACTED" and e[1] == idx:
                    events[i] = None
                    events.append({"type": "delta", "delta": {"type": "continuation", "part_index": idx, "provider": "anthropic", "kind": "redacted_thinking", "data": {"data": e[2]}}})
        elif t == "message_delta":
            finish = ANTH_FINISH.get((f.get("delta") or {}).get("stop_reason"), (f.get("delta") or {}).get("stop_reason"))
            usage_acc.update({k: v for k, v in (f.get("usage") or {}).items() if v is not None})
            pd = f
    events = [e for e in events if e is not None and not isinstance(e, tuple)]
    events.append({"type": "end", "finish_reason": finish, "usage": usage_anthropic(usage_acc), "provider_data": pd})
    return events


# ───────── MAP-9 materialization of an event trace ─────────

def materialize(events):
    slots = {}
    msg_cont = []
    start = {}
    end = {}
    order = ["thinking", "text", "image", "audio", "citations", "tool_call"]
    for e in events:
        if e["type"] == "start":
            start = e
        elif e["type"] == "end":
            end = e
        elif e["type"] == "delta":
            d = e["delta"]
            if d["type"] == "continuation":
                if d.get("part_index") is None:
                    msg_cont.append({"provider": d["provider"], "kind": d["kind"], "data": d["data"]})
                else:
                    slots.setdefault(d["part_index"], {}).setdefault("_cont", []).append({"provider": d["provider"], "kind": d["kind"], "data": d["data"]})
                continue
            s = slots.setdefault(d["part_index"], {})
            if d["type"] in ("text", "thinking"):
                s[d["type"]] = s.get(d["type"], "") + d["text"]
            elif d["type"] == "tool_call":
                tc = s.setdefault("tool_call", {"id": None, "name": None, "input": ""})
                tc["input"] += d.get("input") or ""
                if d.get("id") is not None:
                    tc["id"] = d["id"]
                if d.get("name") is not None:
                    tc["name"] = d["name"]
    parts = []
    has_call = False
    for idx in sorted(slots):
        s = slots[idx]
        cont = s.get("_cont")
        emitted = 0
        for kind in order:
            if kind not in s:
                continue
            if kind in ("text", "thinking"):
                p = {"type": kind, "text": s[kind]}
            else:
                tc = s[kind]
                has_call = True
                try:
                    inp = json.loads(tc["input"]) if tc["input"] else {}
                except json.JSONDecodeError:
                    inp = tc["input"]
                p = {"type": "tool_call", "id": tc["id"], "name": tc["name"], "input": inp}
            if cont:
                p["continuation"] = cont
            parts.append(p)
            emitted += 1
        if emitted == 0 and cont:
            parts.append({"type": "text", "text": "", "continuation": cont})
    if not parts:
        parts.append({"type": "text", "text": ""})
    fr = end.get("finish_reason")
    if fr is None:
        fr = "tool_call" if has_call else "stop"
    elif fr == "stop" and has_call:
        fr = "tool_call"
    msg = {"role": "assistant", "parts": parts}
    if msg_cont:
        msg["continuation"] = msg_cont
    return clean({"id": start.get("id"), "model": start.get("model"), "message": msg, "finish_reason": fr, "usage": end.get("usage")})


# ───────── decision checks ─────────

def walk(n, fn, path="$"):
    fn(n, path)
    if isinstance(n, dict):
        for k, v in n.items():
            walk(v, fn, f"{path}.{k}")
    elif isinstance(n, list):
        for i, v in enumerate(n):
            walk(v, fn, f"{path}[{i}]")


def decision_checks(g, provider, is_stream, findings, notes):
    dialect = DIALECT[provider]

    def fn(n, path):
        if not isinstance(n, dict):
            return
        # D8: no message-level id state anywhere
        if n.get("kind") in ("response_id", "message_id"):
            findings.append((path, "D8/INV-051: message-level id continuation present"))
        # D7: continuation provider is the dialect
        if "kind" in n and "provider" in n and n.get("type") in (None, "continuation") and "data" in n:
            want = "openai" if dialect in ("openai", "openai_chat") else dialect
            if n["provider"] != want:
                findings.append((path, f"D7/MAP-7.8: continuation provider {n['provider']!r}, dialect is {want!r}"))
        # D5: no redacted flag, no placeholder
        if n.get("type") == "thinking":
            if "redacted" in n:
                findings.append((path, "D5: redacted flag present"))
            if n.get("text") == "[redacted]":
                findings.append((path, "D5/MAP-7.11: placeholder text"))
            for c in n.get("continuation") or []:
                if c.get("kind") == "redacted_thinking" and n.get("text") != "":
                    findings.append((path, "D5: redacted_thinking state with non-empty text"))
        # D10: no thinking parts on bedrock runtime (inline tags stay text)
        if provider == "bedrock-chat" and n.get("type") == "thinking":
            findings.append((path, "D10/MAP-7.12: thinking part from inline tags on the runtime door"))
        if n.get("type") == "text" and "<reasoning>" in (n.get("text") or ""):
            notes.append(f"{path}: inline <reasoning> kept literal (D10)")

    walk(g.get("canonical_response"), fn, "$.canonical_response")
    if is_stream:
        walk(g.get("events"), fn, "$.events")
        ends = [e for e in g["events"] if e["type"] == "end"]
        starts = [e for e in g["events"] if e["type"] == "start"]
        if len(ends) != 1 or g["events"][-1]["type"] != "end":
            findings.append(("$.events", "MAP-3: not exactly one final end"))
        if len(starts) != 1 or g["events"][0]["type"] != "start":
            findings.append(("$.events", "MAP-4: not exactly one initial start"))
        if ends and not isinstance(ends[0].get("provider_data"), dict):
            findings.append(("$.events[end].provider_data", "D9/MAP-3: end provider_data absent or not an object"))


# ───────── main ─────────

def review_one(gp: Path):
    provider, stem = gp.parent.name, gp.stem
    rel = gp.relative_to(ROOT).as_posix()
    g = load(gp)
    case = case_for(provider, stem)
    pinned = g["provenance"].get("pinned_body") or (case or {}).get("pinned_body")
    findings, notes = [], []
    kind = "other"
    old = git_show(rel)
    unchanged = (old == g)
    frozen = bool(g["provenance"].get("reviewed"))

    if "canonical_response" in g and case is not None:
        body_path = ROOT / "bodies" / case["id"] / pinned
        text = body_path.read_text()
        is_stream = "events" in g
        dialect = DIALECT[provider]
        decision_checks(g, provider, is_stream, findings, notes)
        cr = g["canonical_response"]
        if is_stream:
            kind = "stream"
            frames = sse_frames(text)
            if dialect == "openai":
                exp_events, exp_resp = responses_stream(frames)
            elif dialect == "openai_chat":
                exp_events = chat_stream(frames, case["canonical_request"]["model"])
                exp_resp = materialize(exp_events)
            else:
                exp_events = anthropic_stream(frames)
                exp_resp = materialize(exp_events)
            # compare event traces (excluding provider_data content, which is escape hatch; but check equality anyway)
            ge = [dict(e) for e in g["events"]]
            pd_equal = None
            for e in ge:
                if e["type"] == "end":
                    pd_equal = (e.get("provider_data") == exp_events[-1].get("provider_data"))
            strip = lambda evs: [{k: v for k, v in e.items() if k != "provider_data"} for e in evs]
            if strip(ge) != strip([clean(e) if e["type"] != "delta" else e for e in exp_events]):
                findings.append(("$.events", "trace differs from body-derived trace"))
                notes.append("expected: " + json.dumps(strip(exp_events))[:600])
                notes.append("golden  : " + json.dumps(strip(ge))[:600])
            if pd_equal is False:
                findings.append(("$.events[end].provider_data", "D9: not the usage/finish frame of the pinned body"))
            # INV-051: materialize golden events and compare with canonical_response
            mat = materialize(g["events"])
            if mat != cr:
                findings.append(("$.canonical_response", "INV-051: materialized events != canonical_response"))
                notes.append("materialized: " + json.dumps(mat)[:500])
                notes.append("canonical   : " + json.dumps(cr)[:500])
            if exp_resp != cr and dialect == "openai":
                findings.append(("$.canonical_response", "differs from response.completed-derived response"))
                notes.append("expected: " + json.dumps(exp_resp)[:500])
        else:
            kind = "complete"
            body = json.loads(text)
            if dialect == "openai":
                exp = responses_from_body(body)
            elif dialect == "openai_chat":
                exp = chat_from_body(body)
            else:
                exp = anthropic_from_body(body)
            exp = clean(exp)
            if exp != cr:
                findings.append(("$.canonical_response", "differs from body-derived response"))
                for k in ("id", "model", "finish_reason", "usage", "message"):
                    if exp.get(k) != cr.get(k):
                        notes.append(f"{k}: expected {json.dumps(exp.get(k))[:300]} golden {json.dumps(cr.get(k))[:300]}")
    else:
        # endpoint goldens: models / files / batch / image / speech / live
        kind = "endpoint"
        if stem == "models":
            body = json.loads((ROOT / "bodies" / case["id"] / pinned).read_text())
            ids = [m["id"] for m in body["data"] if m.get("id")]
            gids = [m["id"] for m in g["models"]] if "models" in g else None
            if gids is None:
                # find list of dicts with id
                for v in g.values():
                    if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                        gids = [m["id"] for m in v]
                        break
            if gids != ids:
                findings.append(("$.models", "model id list differs from pinned body"))
            provs = {m.get("provider") for v in g.values() if isinstance(v, list) for m in v if isinstance(m, dict)}
            if provs - {provider}:
                findings.append(("$.models[*].provider", f"provider {provs}"))
            notes.append(f"{len(ids)} ids equal and ordered; provider={provider}")
        elif stem == "files":
            fold = {"uploaded": "pending", "pending": "pending", "error": "failed", "failed": "failed", "processed": "ready"}
            for step in ("upload", "get"):
                raw = g[step]["provider_data"]["status"]
                want = fold.get(raw, "ready")
                if g[step]["readiness"] != want:
                    findings.append((f"$.{step}.readiness", f"D6: raw {raw!r} -> {want!r}, golden {g[step]['readiness']!r}"))
                else:
                    notes.append(f"{step}: raw status {raw!r} -> {g[step]['readiness']!r} (D6)")
                ts = datetime.fromtimestamp(g[step]["provider_data"]["created_at"], tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                if g[step]["created_at"] != ts:
                    findings.append((f"$.{step}.created_at", "epoch->UTC mismatch"))
            for i, it in enumerate(g["list"]["items"]):
                raw = it["provider_data"]["status"]
                if it["readiness"] != fold.get(raw, "ready"):
                    findings.append((f"$.list.items[{i}].readiness", f"D6 fold: raw {raw!r}"))
        if unchanged:
            notes.append("byte-identical to cf298d2; prior review verdict stands")
    return {"rel": rel, "kind": kind, "frozen": frozen, "unchanged": unchanged, "findings": findings, "notes": notes,
            "source": g["provenance"].get("source")}


def main():
    results = []
    for prov in PROVIDERS:
        for gp in sorted((ROOT / "goldens" / prov).glob("*.json")):
            results.append(review_one(gp))
    assert len(results) == 88, len(results)
    n_ok = 0
    for r in results:
        verdict = "REVIEWED-OK" if not r["findings"] else "FINDING"
        n_ok += verdict == "REVIEWED-OK"
        print(f"{verdict:12} {r['kind']:9} {'changed' if not r['unchanged'] else 'same   '} {r['rel']}")
        for p, m in r["findings"]:
            print(f"     FINDING {p}: {m}")
        for n in r["notes"]:
            print(f"     note: {n[:400]}")
    print(f"\n{n_ok}/88 REVIEWED-OK")
    json.dump(results, open("/tmp/rereview/part2_results.json", "w"), indent=1, ensure_ascii=False)


main()
