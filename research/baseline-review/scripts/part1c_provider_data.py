#!/usr/bin/env python3
"""(c) check: the added end.provider_data equals the pinned-body frame that
supplied usage (else finish_reason), per MAP-3 / D9.  All 28 files."""
import json
from pathlib import Path

ROOT = Path("/home/maxime/Projects/lm15-dev/lm15-contract")
FILES = [l.strip() for l in """
goldens/anthropic/streaming.json
goldens/anthropic/streaming_tool_call.json
goldens/azure-chat/streaming.json
goldens/azure-chat/streaming_tool_call.json
goldens/bedrock-chat/streaming.json
goldens/bedrock-chat/streaming_tool_call.json
goldens/bedrock-mantle-chat/streaming.json
goldens/bedrock-mantle-chat/streaming_tool_call.json
goldens/deepseek/streaming.json
goldens/deepseek/streaming_tool_call.json
goldens/deepseek-anthropic/streaming.json
goldens/deepseek-anthropic/streaming_tool_call.json
goldens/meta-anthropic/streaming.json
goldens/meta-anthropic/streaming_tool_call.json
goldens/meta-chat/streaming.json
goldens/meta-chat/streaming_tool_call.json
goldens/moonshotai/streaming.json
goldens/moonshotai/streaming_tool_call.json
goldens/moonshotai-anthropic/streaming.json
goldens/moonshotai-anthropic/streaming_tool_call.json
goldens/openai_chat/streaming.json
goldens/openai_chat/streaming_sglang.json
goldens/openai_chat/streaming_tool_call.json
goldens/openai_chat/streaming_vllm.json
goldens/openai_chat/tool_call_unnamed.json
goldens/xai/streaming.json
goldens/zai/streaming.json
goldens/zai/streaming_tool_call.json
""".split()]


def sse_frames(text: str):
    frames = []
    for line in text.splitlines():
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload == "[DONE]" or not payload:
                continue
            try:
                frames.append(json.loads(payload))
            except json.JSONDecodeError:
                frames.append(("<unparsed>", payload))
    return frames


def body_for(rel: str):
    g = json.loads((ROOT / rel).read_text())
    prov = g["provenance"]
    case_id = rel.split("/")[1] + "." + Path(rel).stem
    # case id may use a different dir name; check bodies dir
    bdir = ROOT / "bodies" / case_id
    if not bdir.exists():
        # search for matching case file by golden dir
        for c in (ROOT / "cases").glob("*/*.json"):
            cj = json.loads(c.read_text())
            if cj.get("id", "").endswith("." + Path(rel).stem) and cj.get("provider") == rel.split("/")[1]:
                case_id = cj["id"]
                bdir = ROOT / "bodies" / case_id
                break
    pinned = prov.get("pinned_body")
    if pinned is None:
        for c in (ROOT / "cases").glob("*/*.json"):
            cj = json.loads(c.read_text())
            if cj.get("id") == case_id:
                pinned = cj.get("pinned_body") or cj["provenance"]["pinned_body"]
                break
    return g, case_id, bdir / pinned


def expected_frame(frames):
    """Frame that supplied usage; else the frame that supplied finish."""
    usage_frames = []
    finish_frames = []
    for f in frames:
        if not isinstance(f, dict):
            continue
        # chat dialect
        if f.get("object") == "chat.completion.chunk" or "choices" in f:
            if f.get("usage") is not None:
                usage_frames.append(f)
            if any(c.get("finish_reason") for c in f.get("choices") or []):
                finish_frames.append(f)
        # anthropic dialect
        elif f.get("type") == "message_delta":
            if f.get("usage") is not None:
                usage_frames.append(f)
            if (f.get("delta") or {}).get("stop_reason"):
                finish_frames.append(f)
        elif f.get("type") == "message_start":
            pass  # start-frame usage is not the terminal usage; D9 says message_delta
    if usage_frames:
        return usage_frames[-1], "usage", len(usage_frames)
    if finish_frames:
        return finish_frames[-1], "finish", len(finish_frames)
    return None, None, 0


def main():
    ok = 0
    for rel in FILES:
        g, case_id, body = body_for(rel)
        ends = [e for e in g["events"] if e.get("type") == "end"]
        assert len(ends) == 1, rel
        pd = ends[0].get("provider_data")
        text = body.read_text()
        frames = sse_frames(text)
        exp, how, n = expected_frame(frames)
        match = (pd == exp)
        # is provider_data at least *some* frame verbatim?
        some = any(pd == f for f in frames if isinstance(f, dict))
        usage_in_pd = pd.get("usage") is not None if isinstance(pd, dict) else None
        status = "OK" if match else ("FRAME-BUT-NOT-EXPECTED" if some else "NOT-A-FRAME")
        if match:
            ok += 1
        print(f"{status:24} {rel:52} body={body.name} rule={how} usage_frames={n} end.finish={ends[0].get('finish_reason')} end.usage={'yes' if ends[0].get('usage') else 'no'}")
        if not match:
            print("   provider_data:", json.dumps(pd)[:300])
            print("   expected     :", json.dumps(exp)[:300])
    print(f"\n{ok}/{len(FILES)} end.provider_data equal the D9 frame of the pinned body")


main()
