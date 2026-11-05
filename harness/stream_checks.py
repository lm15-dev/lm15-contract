"""Stream checks that need no hand-written answer (INV-051, MAP-20).

Two kinds, both driven from the pinned stream bodies by ``harness/check.py``'s
``stream`` direction (PROTOCOL.md § "Stream checks"):

- **final-copy** — a dialect whose stream ends by restating the whole
  response (OpenAI Responses: ``response.completed``) is read twice by the
  shim under test: the stream through ``replay_stream``, the restatement
  through ``parse_response``. INV-051 says the two Responses are equal, so
  the check needs no golden: it caught the 2026-11-05 Codex finding (two
  parallel calls with input ``{}``) with nothing written by a person.
- **variants** — legal re-shapings of a recorded stream that must
  assemble to the same outcome as the recording (the golden's Response, or
  its pinned refusal):

  * ``split``  — every text-like fragment cut into pieces of 1, 2, 3, 4,
    5, 1, 2… characters (a fragment is any boundary the provider chooses);
  * ``merge``  — consecutive fragments of one target joined into one
    (Gemini sends whole calls, the Codex backend whole arguments);
  * ``rechunk`` — Gemini only: a chunk's parts sent one chunk each
    (gemini-2.5-pro sends parallel calls that way), text that continues
    text of its kind kept together;
  * ``final-only`` — Responses only: every fragment of an item that is
    restated by ``response.output_item.done`` dropped, the shape the Codex
    backend sent for parallel calls (receipts/2026-11-05-stream-final-copy);
  * ``contradict`` — Responses only: one fragment changed so it is no
    longer the beginning of its item's final copy; the stream must be
    refused with ``StreamAssemblyError`` / ``stream_assembly`` (MAP-20
    rule 3), never assembled from either side.

What a variant never touches: media fragments (base64 audio and image
chunks need not split on arbitrary characters), fragments that carry token
logprobs (their scores belong to their text), opaque signatures, and any
chunk that also carries a finish reason, usage, a second fragment or a key
the variant does not know. Frames it does not change keep their bytes; the
frames it re-serializes keep their key order. Responses
``sequence_number`` values are renumbered so a variant stays a legal
stream.

stdlib only; imports nothing from lm15.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any, Callable

JsonObject = dict[str, Any]

# Split sizes, cycled: every boundary class (inside an escape, a word, a
# multi-byte character's neighbours) is hit within a few fragments, at a
# third of the events a one-character split would make.
SPLIT_SIZES = (1, 2, 3, 4, 5)

RESPONSES_FRAGMENTS = {
    "response.output_text.delta": "text",
    "response.refusal.delta": "text",
    "response.function_call_arguments.delta": "arguments",
    "response.reasoning_summary_text.delta": "summary",
    "response.reasoning_text.delta": "reasoning_text",
}
# The fragment kinds an item's final copy restates (MAP-20 rule 2), by item type.
RESPONSES_RESTATED = {"message": {"text"}, "function_call": {"arguments"}, "reasoning": {"summary"}}
RESPONSES_FINAL_EVENTS = ("response.completed", "response.incomplete")

CHAT_TEXT_FIELDS = ("content", "reasoning_content", "reasoning")
CHAT_DELTA_KEYS = frozenset({"role", "content", "reasoning_content", "reasoning", "tool_calls", "refusal"})
ANTHROPIC_FRAGMENTS = {"text_delta": "text", "input_json_delta": "partial_json", "thinking_delta": "thinking"}


# ─── SSE frames ──────────────────────────────────────────────────────

@dataclass
class Frame:
    lines: list[str]                 # the frame's lines, verbatim, no terminators
    payload: JsonObject | None = None  # the data, when it is exactly one JSON-object line
    changed: bool = False

    def render(self) -> str:
        if not self.changed or self.payload is None:
            return "\n".join(self.lines) + "\n\n"
        data = "data: " + json.dumps(self.payload, ensure_ascii=False, separators=(",", ":"))
        out = [line if not line.startswith("data:") else data for line in self.lines]
        return "\n".join(out) + "\n\n"

    def with_payload(self, payload: JsonObject) -> "Frame":
        return Frame(list(self.lines), payload, True)


def parse_frames(body: bytes) -> list[Frame] | None:
    """The body as SSE frames, or None when it is not plain UTF-8 SSE."""
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return None
    frames: list[Frame] = []
    current: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw == "":
            if current:
                frames.append(_frame(current))
                current = []
            continue
        current.append(raw)
    if current:
        frames.append(_frame(current))
    return frames


def _frame(lines: list[str]) -> Frame:
    data = [line[5:].lstrip(" ") if line.startswith("data:") else None for line in lines]
    data_lines = [d for d in data if d is not None]
    payload = None
    if len(data_lines) == 1 and data_lines[0] not in ("", "[DONE]"):
        try:
            value = json.loads(data_lines[0])
        except ValueError:
            value = None
        if isinstance(value, dict):
            payload = value
    return Frame(lines, payload)


def render(frames: list[Frame]) -> bytes:
    return "".join(f.render() for f in frames).encode("utf-8")


def dialect_of(case: JsonObject) -> str | None:
    url = str((case.get("request") or {}).get("url", "")).split("?", 1)[0]
    if url.endswith("/responses"):
        return "responses"
    if url.endswith("/chat/completions"):
        return "chat"
    if url.endswith("/messages"):
        return "anthropic"
    if ":streamGenerateContent" in url:
        return "gemini"
    return None


# ─── Final copy (INV-051) ────────────────────────────────────────────

def final_copy(dialect: str, frames: list[Frame]) -> JsonObject | None:
    """The complete-path body the stream restates at its end, or None.

    Only OpenAI Responses restates the whole response; Anthropic's
    ``message_start`` carries an empty message, and the chat and Gemini
    dialects restate nothing.
    """
    if dialect != "responses":
        return None
    for frame in reversed(frames):
        p = frame.payload
        if p is not None and p.get("type") in RESPONSES_FINAL_EVENTS and isinstance(p.get("response"), dict):
            return p["response"]
    return None


# ─── Variants ────────────────────────────────────────────────────────

@dataclass
class Fragment:
    target: tuple            # what the fragment adds to (merge joins only equal targets)
    get: Callable[[JsonObject], str]
    put: Callable[[JsonObject, str], None]
    later: Callable[[JsonObject], None] = field(default=lambda p: None)  # strip first-only keys from a later piece


def _path_setter(*path: Any) -> tuple[Callable[[JsonObject], str], Callable[[JsonObject, str], None]]:
    def get(p: JsonObject) -> str:
        cur: Any = p
        for key in path:
            cur = cur[key]
        return cur

    def put(p: JsonObject, value: str) -> None:
        cur: Any = p
        for key in path[:-1]:
            cur = cur[key]
        cur[path[-1]] = value

    return get, put


def _set(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def fragment_of(dialect: str, p: JsonObject) -> Fragment | None:
    """The one text-like fragment this payload carries, when it carries
    exactly one and nothing a variant must not duplicate or drop."""
    if dialect == "responses":
        kind = RESPONSES_FRAGMENTS.get(str(p.get("type")))
        if kind is None or not isinstance(p.get("delta"), str) or _set(p.get("logprobs")):
            return None
        target = (p.get("type"), p.get("output_index"), p.get("item_id"), p.get("content_index"), p.get("summary_index"))
        return Fragment(target, *_path_setter("delta"))
    if dialect == "anthropic":
        if p.get("type") != "content_block_delta" or not isinstance(p.get("delta"), dict):
            return None
        key = ANTHROPIC_FRAGMENTS.get(str(p["delta"].get("type")))
        if key is None or not isinstance(p["delta"].get(key), str):
            return None
        return Fragment((p.get("index"), p["delta"]["type"]), *_path_setter("delta", key))
    if dialect == "chat":
        return _chat_fragment(p)
    if dialect == "gemini":
        return _gemini_fragment(p)
    return None


def _chat_fragment(p: JsonObject) -> Fragment | None:
    choices = p.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return None
    choice = choices[0]
    if _set(choice.get("finish_reason")) or _set(p.get("usage")) or _set(choice.get("logprobs")):
        return None
    delta = choice.get("delta")
    if not isinstance(delta, dict):
        return None
    if any(_set(v) for k, v in delta.items() if k not in CHAT_DELTA_KEYS) or _set(delta.get("refusal")):
        return None
    texts = [k for k in CHAT_TEXT_FIELDS if isinstance(delta.get(k), str) and delta[k] != ""]
    calls = delta.get("tool_calls")
    call_args = None
    if _set(calls):
        if not isinstance(calls, list) or len(calls) != 1 or not isinstance(calls[0], dict):
            return None
        fn = calls[0].get("function")
        if not isinstance(fn, dict) or not isinstance(fn.get("arguments"), str) or fn["arguments"] == "":
            return None
        call_args = calls[0]
    if len(texts) + (call_args is not None) != 1:
        return None
    if texts:
        key = texts[0]

        def later_text(q: JsonObject) -> None:
            q["choices"][0]["delta"].pop("role", None)

        return Fragment(("text", key), *_path_setter("choices", 0, "delta", key), later=later_text)

    def later_call(q: JsonObject) -> None:
        d = q["choices"][0]["delta"]
        d.pop("role", None)
        call = d["tool_calls"][0]
        for k in ("id", "type"):
            call.pop(k, None)
        call["function"] = {"arguments": call["function"]["arguments"]}

    starts = _set(call_args.get("id")) or _set(call_args["function"].get("name"))
    # A chunk that starts a call is never merged INTO an earlier one: the
    # target carries "start" so it only merges with what follows it.
    return Fragment(("call", call_args.get("index"), "start" if starts else "more"),
                    *_path_setter("choices", 0, "delta", "tool_calls", 0, "function", "arguments"), later=later_call)


def _gemini_fragment(p: JsonObject) -> Fragment | None:
    cands = p.get("candidates")
    if not isinstance(cands, list) or len(cands) != 1 or not isinstance(cands[0], dict):
        return None
    cand = cands[0]
    if set(cand) - {"content", "index"}:
        return None  # finishReason, safety, grounding, citations: not duplicated, not dropped
    content = cand.get("content")
    if not isinstance(content, dict) or set(content) - {"parts", "role"}:
        return None
    parts = content.get("parts")
    if not isinstance(parts, list) or len(parts) != 1 or not isinstance(parts[0], dict):
        return None
    part = parts[0]
    if set(part) - {"text", "thought"} or not isinstance(part.get("text"), str) or part["text"] == "":
        return None
    return Fragment(("text", bool(part.get("thought"))), *_path_setter("candidates", 0, "content", "parts", 0, "text"))


def _pieces(text: str) -> list[str]:
    out, i, k = [], 0, 0
    while i < len(text):
        n = SPLIT_SIZES[k % len(SPLIT_SIZES)]
        out.append(text[i:i + n])
        i += n
        k += 1
    return out


def split_variant(dialect: str, frames: list[Frame]) -> list[Frame] | None:
    out: list[Frame] = []
    touched = False
    for frame in frames:
        frag = fragment_of(dialect, frame.payload) if frame.payload is not None else None
        if frag is None or len(frag.get(frame.payload)) < 2:
            out.append(frame)
            continue
        for i, piece in enumerate(_pieces(frag.get(frame.payload))):
            payload = copy.deepcopy(frame.payload)
            frag.put(payload, piece)
            if i:
                frag.later(payload)
            out.append(frame.with_payload(payload))
        touched = True
    return _renumber(dialect, out) if touched else None


def merge_variant(dialect: str, frames: list[Frame]) -> list[Frame] | None:
    out: list[Frame] = []
    head: tuple[Fragment, JsonObject] | None = None
    touched = False

    def flush() -> None:
        nonlocal head
        head = None

    for frame in frames:
        frag = fragment_of(dialect, frame.payload) if frame.payload is not None else None
        if frag is None:
            flush()
            out.append(frame)
            continue
        if head is not None and _mergeable(head[0].target, frag.target):
            hfrag, hpayload = head
            if dialect == "gemini":
                # The later chunk's envelope (its cumulative usage) wins.
                merged = copy.deepcopy(frame.payload)
                frag.put(merged, hfrag.get(hpayload) + frag.get(frame.payload))
                out[-1] = out[-1].with_payload(merged)
                head = (frag, merged)
            else:
                hfrag.put(hpayload, hfrag.get(hpayload) + frag.get(frame.payload))
                out[-1] = out[-1].with_payload(hpayload)
            touched = True
            continue
        payload = copy.deepcopy(frame.payload)
        out.append(frame.with_payload(payload) if dialect == "responses" else Frame(frame.lines, payload, False))
        head = (frag, payload)
    return _renumber(dialect, out) if touched else None


def _mergeable(first: tuple, then: tuple) -> bool:
    if first and first[0] == "call":
        # chat: a call's later chunks join its start or each other.
        return then[0] == "call" and then[1] == first[1] and then[2] == "more"
    return first == then


def final_only_variant(dialect: str, frames: list[Frame]) -> list[Frame] | None:
    if dialect != "responses":
        return None
    restated = _restated_items(frames)
    out = [f for f in frames if not _restated_fragment(f, restated)]
    return _renumber(dialect, out) if len(out) != len(frames) else None


def contradict_variant(dialect: str, frames: list[Frame]) -> list[Frame] | None:
    if dialect != "responses":
        return None
    restated = _restated_items(frames)
    out = list(frames)
    for i, frame in enumerate(frames):
        if not _restated_fragment(frame, restated) or not frame.payload.get("delta"):
            continue
        payload = copy.deepcopy(frame.payload)
        first = payload["delta"][0]
        payload["delta"] = ("%" if first == "#" else "#") + payload["delta"][1:]
        out[i] = frame.with_payload(payload)
        return _renumber(dialect, out)
    return None


def _restated_items(frames: list[Frame]) -> dict[Any, str]:
    """output_index -> item type, for items with a final copy (output_item.done)."""
    items: dict[Any, str] = {}
    for f in frames:
        p = f.payload
        if p is not None and p.get("type") == "response.output_item.done" and isinstance(p.get("item"), dict):
            items[p.get("output_index")] = str(p["item"].get("type"))
    return items


def _restated_fragment(frame: Frame, restated: dict[Any, str]) -> bool:
    p = frame.payload
    if p is None:
        return False
    kind = RESPONSES_FRAGMENTS.get(str(p.get("type")))
    item_type = restated.get(p.get("output_index"))
    return kind is not None and item_type is not None and kind in RESPONSES_RESTATED.get(item_type, set())


def _renumber(dialect: str, frames: list[Frame]) -> list[Frame]:
    if dialect != "responses":
        return frames
    out: list[Frame] = []
    n = 0
    for frame in frames:
        p = frame.payload
        if p is not None and isinstance(p.get("sequence_number"), int):
            if p["sequence_number"] != n:
                q = copy.deepcopy(p)
                q["sequence_number"] = n
                frame = frame.with_payload(q)
            n += 1
        out.append(frame)
    return out


def _gemini_kind(part: Any) -> str | None:
    if not isinstance(part, dict):
        return None
    if "text" in part:
        return "thought" if part.get("thought") else "text"
    return "other"


def rechunk_variant(dialect: str, frames: list[Frame]) -> list[Frame] | None:
    """Gemini only: a chunk holding several parts sent as several chunks,
    the shape gemini-2.5-pro uses for parallel calls (one call per chunk,
    receipts/2026-11-05-stream-final-copy/gemini-chunked). A part is moved
    to a chunk of its own unless it is text following text of the same kind
    (thought or not): a chunk's first text part continues the previous
    chunk's last one, so moving it would join two parts into one. The
    candidate's finish reason and other keys ride the last chunk; the
    chunk-level keys (usage, model version, response id) every chunk."""
    if dialect != "gemini":
        return None
    out: list[Frame] = []
    touched = False
    for frame in frames:
        p = frame.payload
        cands = p.get("candidates") if p is not None else None
        if not isinstance(cands, list) or len(cands) != 1 or not isinstance(cands[0], dict):
            out.append(frame)
            continue
        content = cands[0].get("content")
        parts = content.get("parts") if isinstance(content, dict) else None
        if not isinstance(parts, list) or len(parts) < 2:
            out.append(frame)
            continue
        groups: list[list[Any]] = [[parts[0]]]
        for prev, part in zip(parts, parts[1:]):
            kind = _gemini_kind(part)
            if kind in ("text", "thought") and kind == _gemini_kind(prev):
                groups[-1].append(part)
            else:
                groups.append([part])
        if len(groups) == 1:
            out.append(frame)
            continue
        for i, group in enumerate(groups):
            q = copy.deepcopy(p)
            cand = q["candidates"][0]
            cand["content"]["parts"] = group
            if i < len(groups) - 1:
                for key in list(cand):
                    if key not in ("content", "index"):
                        del cand[key]
            out.append(frame.with_payload(q))
        touched = True
    return out if touched else None


VARIANTS: tuple[tuple[str, Callable[[str, list[Frame]], list[Frame] | None], str], ...] = (
    ("split", split_variant, "same"),
    ("merge", merge_variant, "same"),
    ("rechunk", rechunk_variant, "same"),
    ("final-only", final_only_variant, "same"),
    ("contradict", contradict_variant, "refuse"),
)


def variants(dialect: str, body: bytes) -> list[tuple[str, bytes, str]]:
    """``(name, body, expectation)`` for every variant that changes this body."""
    frames = parse_frames(body)
    if frames is None:
        return []
    out = []
    for name, make, expect in VARIANTS:
        made = make(dialect, frames)
        if made is not None:
            out.append((name, render(made), expect))
    return out
