#!/usr/bin/env python3
"""Empty text, empty messages and another dialect's state in a history,
live on every dialect (changes/2026-11-11-empty-parts.md, MAP-24;
lm15-contract issue #3).

Why: a conversation answered by an OpenAI Responses model and continued on
Claude failed on every request with ``messages: text content blocks must be
non-empty``.  A hidden ``ThinkingPart`` (empty text, ``openai:reasoning_item``
state) was written to the Messages wire as ``{"type": "text", "text": ""}``.

Three modes, all through ``research/providers/_capture.py``:

``--probe``    The same cells for every door, as hand-written wire histories
               swapped into a body the reference adapter built (its URL,
               headers, tool declaration and limits).  Receipts only.
``--replay``   What the fixed reference adapter builds for a history that
               holds another dialect's recorded reply (taken from the
               contract's goldens), sent live.  Receipts only.
``--capture``  The cases under ``cases/<provider>/`` (reference-built wire,
               live-validated).

    set -a; source ../.env; set +a
    python3 research/providers/empty_parts.py --probe [--only anthropic,vertex] [--cells c02,c06] [--dry-run]
    python3 research/providers/empty_parts.py --replay [--only anthropic,vertex,groq]
    python3 research/providers/empty_parts.py --capture [--force]

Receipts: ``receipts/2026-11-11-empty-parts/<door>/``.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture import CONTRACT, Capture, now_ts  # noqa: E402
from lm15 import Config, FunctionTool, Message, Request, serde  # noqa: E402
from lm15.types import Reasoning, TextPart, ThinkingPart, ToolCallPart, ToolResultPart  # noqa: E402

DATE = "2026-11-11"
RECEIPTS = CONTRACT / "receipts" / f"{DATE}-empty-parts"
CHANGE = "empty-parts"

TOOL = FunctionTool(name="delete_program", description="Delete the test program.",
                    parameters={"type": "object", "properties": {}})
ASK = "Delete the test program now."
DONE = "Deleted."
NEXT = "Thanks. Reply with the single word: bye"
CALL_ID = "call_1"

# door -> (dialect, key variable, host, models).  One row per server that
# answered on 2026-11-11; OpenAI's API, the Gemini API, Together, Fireworks,
# DeepInfra and Cerebras answered 402/429 "no credits" (see the change entry).
DOORS: dict[str, tuple[str, str, str, list[str]]] = {
    "anthropic": ("messages", "ANTHROPIC_API_KEY", "api.anthropic.com", ["claude-haiku-4-5-20251001", "claude-opus-5-5"]),
    "deepseek-anthropic": ("messages", "DEEPSEEK_API_KEY", "api.deepseek.com/anthropic", ["deepseek-v4-flash"]),
    "moonshotai-anthropic": ("messages", "MOONSHOTAI_API_KEY", "api.moonshot.ai/anthropic", ["kimi-k3"]),
    "vertex": ("gemini", "", "aiplatform.googleapis.com", ["gemini-2.5-flash", "gemini-3.7-flash"]),
    "openai-codex": ("responses", "", "chatgpt.com/backend-api/codex", ["gpt-5.6-luna"]),
    "moonshotai-responses": ("responses", "MOONSHOTAI_API_KEY", "api.moonshot.ai", ["kimi-k3"]),
    "groq": ("chat", "GROQ_API_KEY", "api.groq.com", ["openai/gpt-oss-20b"]),
    "deepseek": ("chat", "DEEPSEEK_API_KEY", "api.deepseek.com", ["deepseek-v4-flash"]),
    "moonshotai": ("chat", "MOONSHOTAI_API_KEY", "api.moonshot.ai", ["kimi-k2.6"]),
    "zai": ("chat", "ZAI_API_KEY", "api.z.ai", ["glm-5.3-flash"]),
    "parasail": ("chat", "PARASAIL_API_KEY", "api.parasail.io", ["openai/gpt-oss-20b"]),
    # OpenAI's own models behind OpenRouter's Chat Completions door: a proxy,
    # not api.openai.com; recorded as such.
    "openrouter": ("chat", "OPENROUTER_API_KEY", "openrouter.ai", ["openai/gpt-4.1-mini"]),
}
VERTEX_SETTINGS = {"project": "lm15-vertex-live", "location": "global"}

CALL = object()          # the assistant's tool call
NOBLOCKS = object()      # a message written with zero blocks
NULL = object()          # Chat Completions: content null and no tool_calls


# ─── one history, four spellings ─────────────────────────────────────
#
# A history is a list of turns: ("user", [texts]), ("assistant", [texts or
# CALL]), ("tool", output).  NOBLOCKS / NULL in place of the list are the
# shapes a wire has for "a message with nothing in it".

class Messages:
    key = "messages"

    @staticmethod
    def turn(role, blocks):
        if role == "tool":
            return {"role": "user", "content": [{"type": "tool_result", "tool_use_id": CALL_ID, "content": blocks}]}
        if blocks is NOBLOCKS or blocks is NULL:
            return {"role": role, "content": []}
        return {"role": role, "content": [
            {"type": "tool_use", "id": CALL_ID, "name": TOOL.name, "input": {}} if b is CALL else {"type": "text", "text": b}
            for b in blocks]}

    @staticmethod
    def system(body, text, form):
        body["system"] = text if form == "string" else [{"type": "text", "text": text}]


class Gemini:
    key = "contents"

    @staticmethod
    def turn(role, blocks):
        if role == "tool":
            return {"role": "user", "parts": [{"functionResponse": {"name": TOOL.name, "response": {"result": blocks}}}]}
        role = "model" if role == "assistant" else "user"
        if blocks is NOBLOCKS or blocks is NULL:
            return {"role": role, "parts": []}
        return {"role": role, "parts": [
            {"functionCall": {"name": TOOL.name, "args": {}}} if b is CALL else {"text": b} for b in blocks]}

    @staticmethod
    def system(body, text, form):
        body["systemInstruction"] = {"parts": [{"text": text}]}


class Responses:
    key = "input"

    @staticmethod
    def turn(role, blocks):
        if role == "tool":
            return [{"type": "function_call_output", "call_id": CALL_ID, "output": blocks}]
        kind = "output_text" if role == "assistant" else "input_text"
        if blocks is NOBLOCKS or blocks is NULL:
            return [{"role": role, "content": []}]
        items, content = [], []
        for b in blocks:
            if b is CALL:
                if content:
                    items.append({"role": role, "content": content})
                    content = []
                items.append({"type": "function_call", "call_id": CALL_ID, "name": TOOL.name, "arguments": "{}"})
            else:
                content.append({"type": kind, "text": b})
        if content:
            items.append({"role": role, "content": content})
        return items

    @staticmethod
    def system(body, text, form):
        body["instructions"] = text


class Chat:
    key = "messages"

    @staticmethod
    def turn(role, blocks):
        if role == "tool":
            return {"role": "tool", "tool_call_id": CALL_ID, "content": blocks}
        if blocks is NULL:
            return {"role": role, "content": None}
        if blocks is NOBLOCKS:
            return {"role": role, "content": ""}
        texts = [b for b in blocks if b is not CALL]
        if role == "user":
            return {"role": "user", "content": texts[0] if len(texts) == 1 else [{"type": "text", "text": t} for t in texts]}
        # As the Chat builder writes an assistant row today: the text parts
        # joined by a newline, null when there is no text part at all.
        out = {"role": "assistant", "content": "\n".join(texts) if texts else None}
        if any(b is CALL for b in blocks):
            out["tool_calls"] = [{"id": CALL_ID, "type": "function", "function": {"name": TOOL.name, "arguments": "{}"}}]
        return out

    @staticmethod
    def system(body, text, form):
        body["messages"].insert(0, {"role": "system", "content": text})


DIALECTS = {"messages": Messages, "gemini": Gemini, "responses": Responses, "chat": Chat}

U, A, T = "user", "assistant", "tool"
LOOP = [(U, [ASK]), (A, [CALL]), (T, "ok")]

# (cell, what it asks, history, {extras}).  The same cells for every door.
CELLS: list[tuple[str, str, list, dict]] = [
    ("c01-control", "a tool round trip and a follow-up; nothing empty", [*LOOP, (A, [DONE]), (U, [NEXT])], {}),
    ("c02-empty-text-before-call", "an empty text block before the tool call (what lm15 wrote for a hidden thinking part)",
     [(U, [ASK]), (A, ["", CALL]), (T, "ok"), (A, [DONE]), (U, [NEXT])], {}),
    ("c03-empty-text-before-text", "an empty text block before the answer's text",
     [(U, [ASK]), (A, ["", DONE]), (U, [NEXT])], {}),
    ("c04-assistant-only-empty-text", "an assistant message whose only block is empty text",
     [(U, [ASK]), (A, [""]), (U, [NEXT])], {}),
    ("c05-assistant-no-blocks", "an assistant message with zero blocks",
     [(U, [ASK]), (A, NOBLOCKS), (U, [NEXT])], {}),
    ("c06-assistant-left-out", "that assistant message left out: two user messages in a row",
     [(U, [ASK]), (U, [NEXT])], {}),
    ("c07-two-assistants", "two assistant messages in a row (an empty user message left out between them)",
     [(U, [ASK]), (A, ["Which one?"]), (A, ["The test program, I assume."]), (U, [NEXT])], {}),
    ("c08-user-empty-text-beside-text", "an empty text block beside text in a user message",
     [(U, ["", NEXT])], {}),
    ("c09-user-only-empty-text", "a request whose one user message is empty text",
     [(U, [""])], {}),
    ("c10-empty-system", "an empty system prompt (the string form)", [(U, [NEXT])], {"system": ("", "string")}),
    ("c11-tool-result-empty", "a tool result whose output is the empty string (INV-014's empty output)",
     [(U, [ASK]), (A, [CALL]), (T, ""), (A, [DONE]), (U, [NEXT])], {}),
    ("c12-assistant-whitespace-only", "an assistant message whose only text is line breaks",
     [(U, [ASK]), (A, ["\n\n"]), (U, [NEXT])], {}),
    ("c13-whitespace-before-call", "a line break as its own text block before the tool call",
     [(U, [ASK]), (A, ["\n", CALL]), (T, "ok"), (A, [DONE]), (U, [NEXT])], {}),
    ("c14-user-whitespace-only", "a request whose one user message is a space", [(U, [" "])], {}),
    ("c15-assistant-first", "a conversation that starts with an assistant message (an empty first user message left out)",
     [(A, ["Hello."]), (U, [NEXT])], {}),
    ("c16-mid-loop", "the request right after a tool result, the call's message holding only the call",
     [*LOOP], {}),
    ("c17-no-messages", "a request with no message at all (every message had nothing to write)", [], {}),
    ("c18-system-only", "a system prompt and no message", [], {"system": ("Reply with the single word: bye", "string")}),
]
# Shapes one wire has and the others do not.
EXTRA: dict[str, list[tuple[str, str, list, dict]]] = {
    "messages": [
        ("x01-empty-system-block", "an empty system prompt (the array form)", [(U, [NEXT])], {"system": ("", "array")}),
        ("x02-tool-result-empty-block", "a tool result whose content is one empty text block",
         [(U, [ASK]), (A, [CALL]), (T, [{"type": "text", "text": ""}]), (A, [DONE]), (U, [NEXT])], {}),
        ("x03-whitespace-beside-text", "a space as its own text block before the answer's text",
         [(U, [ASK]), (A, [" ", DONE]), (U, [NEXT])], {}),
    ],
    "chat": [
        ("x01-assistant-null-no-calls", "an assistant row with content null and no tool_calls (what lm15 wrote for a message holding only a hidden thinking part)",
         [(U, [ASK]), (A, NULL), (U, [NEXT])], {}),
        ("x02-null-content-with-call", "the standard row: content null beside the tool call",
         [*LOOP, (A, [DONE]), (U, [NEXT])], {}),
    ],
    "gemini": [
        ("x01-mid-loop-skip-validator", "the request right after a tool result, the call carrying Google's documented "
         "placeholder signature skip_thought_signature_validator",
         [*LOOP], {"signature": "skip_thought_signature_validator"}),
    ],
    "responses": [],
}


def base_request(door: str, model: str) -> Request:
    # The Codex backend refuses max_output_tokens (cases/openai-codex/*.json).
    config = Config() if door == "openai-codex" else Config(max_tokens=400)
    return Request(model=model, messages=(Message.user("x"),), tools=(TOOL,), config=config)


def wire_history(dialect: str, history: list) -> list:
    d = DIALECTS[dialect]
    out: list = []
    for role, blocks in history:
        turn = d.turn(role, blocks)
        out.extend(turn) if isinstance(turn, list) else out.append(turn)
    return out


class LoginCapture(Capture):
    """A door reached with a stored sign-in read in place (the Codex CLI's):
    the adapter resolves the credential itself; the token and the account id
    never reach a receipt."""

    def lm(self, model_key=None, *, clock=None, credential=None):
        from lm15 import OpenAICodexLM

        return OpenAICodexLM(api_key="dry-run-key", account_id="dry-run-account") if self.dry_run \
            else OpenAICodexLM.from_codex_cli()

    def wire_block(self, treq) -> dict:
        for k, v in treq.headers:
            if k.lower() == "authorization" and v.startswith("Bearer "):
                self._secret_values.add(v[len("Bearer "):])
            if k.lower() == "chatgpt-account-id":
                self._secret_values.add(v)
        block = super().wire_block(treq)
        block["headers"] = {k: ("<redacted: the signed-in account>" if k.lower() == "chatgpt-account-id" else v)
                            for k, v in block["headers"].items()}
        return block

    def redact(self, text: str) -> str:
        for secret in sorted(self._secret_values, key=len, reverse=True):
            text = text.replace(secret, "<redacted>")
        return text


def cap_for(door: str, *, dry: bool) -> Capture:
    dialect, env, host, models = DOORS[door]
    if door == "openai-codex":
        cap: Capture = LoginCapture(door, env_var="CODEX_CLI_LOGIN", default_model=models[0], host=host, change_slug=CHANGE)
    else:
        cap = Capture(door, env_var=env or "GOOGLE_ADC", default_model=models[0], host=host, change_slug=CHANGE)
    cap.receipts = RECEIPTS / door
    cap.dry_run = dry
    if door == "vertex":
        cap.settings = dict(VERTEX_SETTINGS)
        cap.bearer_fixture()
    return cap


def outcome(cap: Capture, name: str, row: dict) -> dict:
    """The status and, on a refusal, the server's own sentence."""
    path = cap.receipts / f"probe-{name}.json"
    if "error" in row or not path.exists():
        return row
    got = json.loads(path.read_text(encoding="utf-8"))
    body = got["body"]
    out = {"status": got["status"]}
    if got["status"] != 200:
        text = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
        err = body.get("error", body) if isinstance(body, dict) else None
        if isinstance(err, list) and err:
            err = err[0].get("error", err[0]) if isinstance(err[0], dict) else None
        message = (err.get("message") if isinstance(err, dict) else None) or (body.get("detail") if isinstance(body, dict) else None)
        out["message"] = (message if isinstance(message, str) else text)[:300]
    elif isinstance(body, str) and "response.failed" in body:
        out["note"] = "the stream ended in response.failed"
    return out


def probe_door(door: str, only_cells: set[str], dry: bool) -> list[dict]:
    dialect, _, _, models = DOORS[door]
    cap = cap_for(door, dry=dry)
    d = DIALECTS[dialect]
    stream = door == "openai-codex"  # that backend only streams
    rows = []
    for model in models:
        base = base_request(door, model)
        built = json.loads(cap.lm().build_request(base, stream=stream).body)
        for cell, asks, history, extras in [*CELLS, *EXTRA[dialect]]:
            if only_cells and cell.split("-")[0] not in only_cells:
                continue
            body = json.loads(json.dumps(built))
            body[d.key] = wire_history(dialect, history)
            if "system" in extras:
                d.system(body, *extras["system"])
            if "signature" in extras:
                for content in body[d.key]:
                    for part in content.get("parts", []):
                        if "functionCall" in part:
                            part["thoughtSignature"] = extras["signature"]
            name = f"{model.replace('/', '_')}-{cell}"
            row = cap.probe(name, base, raw_body=body, stream=stream)
            row = {"door": door, "dialect": dialect, "model": model, "cell": cell, "asks": asks,
                   **outcome(cap, name, row), "exchange": getattr(cap, "last_exchange", None)}
            rows.append(row)
            print(json.dumps({k: row[k] for k in row if k not in ("asks", "exchange")}, ensure_ascii=False), flush=True)
    return rows


# ─── replay: another dialect's recorded reply, built by the reference ──

def golden_message(golden_id: str) -> Message:
    provider, feature = golden_id.split(".", 1)
    doc = json.loads((CONTRACT / "goldens" / provider / f"{feature}.json").read_text(encoding="utf-8"))
    return serde.message_from_dict(doc["canonical_response"]["message"])


def answered(message: Message) -> list[Message]:
    """The tool results a recorded reply's calls need before the next turn."""
    calls = [p for p in message.parts if isinstance(p, ToolCallPart)]
    if not calls:
        return []
    return [Message(role="tool", parts=tuple(ToolResultPart(id=c.id, name=c.name, content=(TextPart(text="ok"),)) for c in calls))]


def tools_for(message: Message) -> tuple[FunctionTool, ...]:
    seen: dict[str, FunctionTool] = {}
    for p in message.parts:
        if isinstance(p, ToolCallPart) and p.name not in seen:
            seen[p.name] = FunctionTool(name=p.name, description=f"The {p.name} tool.",
                                        parameters={"type": "object", "properties": {k: {"type": "string"} for k in p.input}})
    return tuple(seen.values())


# Recorded replies (the contract's goldens: what lm15 read from a real
# server) that hold what another dialect cannot read, or nothing at all.
SOURCES = [
    ("meta.tools", "a hidden reasoning item (empty text, openai:reasoning_item), text and a tool call: the shape of the report"),
    ("azure.reasoning_high", "a hidden OpenAI reasoning item before the answer's text"),
    ("meta.streaming_incomplete", "a reply cut during reasoning: its only part is the hidden reasoning item"),
    ("anthropic.reasoning_adaptive", "Claude's thinking with display omitted (empty text, anthropic:thinking_signature) and text"),
    ("meta-anthropic.tools", "two redacted thinking parts (empty text, anthropic:redacted_thinking) and a tool call"),
    ("deepseek-anthropic.tools", "thinking with text on a server that signs nothing, and a tool call"),
    ("gemini.thinking_level", "Gemini 3.x thinking with text, and text carrying a thought signature"),
    ("gemini.tool_config_any", "a Gemini tool call carrying a thought signature"),
    ("gemini.max_output_tokens", "a reply with no parts, read as one empty text part (MAP-2)"),
    ("openai.tool_choice_builtin", "text and two citations (web search)"),
]


def replay_request(door: str, model: str, golden_id: str, *, mid_loop: bool) -> Request:
    message = golden_message(golden_id)
    history = [Message.user(ASK), message, *answered(message)]
    if not mid_loop:
        history.append(Message.user(NEXT))
    if door == "openai-codex":
        config = Config()  # that backend refuses max_output_tokens
    elif door in ("anthropic", "vertex"):
        # Thinking on, as in the report: the server's own rules about earlier
        # thinking apply (Claude's signed blocks, Gemini's signatures).
        config = Config(max_tokens=600, reasoning=Reasoning(effort="low"))
    else:
        config = Config(max_tokens=600)
    return Request(model=model, messages=tuple(history), tools=tools_for(message) or (TOOL,), config=config)


def replay_door(door: str, dry: bool) -> list[dict]:
    dialect, _, _, models = DOORS[door]
    cap = cap_for(door, dry=dry)
    stream = door == "openai-codex"
    rows = []
    for model in models:
        for golden_id, what in SOURCES:
            if not (CONTRACT / "goldens" / golden_id.split(".", 1)[0] / f"{golden_id.split('.', 1)[1]}.json").exists():
                continue
            has_call = bool(answered(golden_message(golden_id)))
            for mid_loop in ((False, True) if has_call else (False,)):
                request = replay_request(door, model, golden_id, mid_loop=mid_loop)
                name = f"replay-{model.replace('/', '_')}-{golden_id}-{'mid-loop' if mid_loop else 'next-turn'}"
                try:
                    row = cap.probe(name, request, stream=stream)
                except Exception as exc:  # a typed refusal before the wire is an answer too
                    row = {"error": f"{type(exc).__name__}: {exc}"[:300]}
                row = {"door": door, "dialect": dialect, "model": model, "source": golden_id, "what": what,
                       "shape": "mid-loop" if mid_loop else "next-turn", **outcome(cap, name, row),
                       "exchange": getattr(cap, "last_exchange", None)}
                rows.append(row)
                print(json.dumps({k: row[k] for k in row if k not in ("what", "exchange")}, ensure_ascii=False), flush=True)
    return rows


# ─── cases: what the fixed reference builds, live ────────────────────

def hidden_reasoning() -> "ThinkingPart":
    """A hidden reasoning item as lm15 read it from a real reply (MAP-7 rules
    9 and 11): the first part of goldens/azure/reasoning_high.json."""
    part = golden_message("azure.reasoning_high").parts[0]
    assert isinstance(part, ThinkingPart) and part.text == "" and part.continuation[0].kind == "reasoning_item"
    return part


def call() -> ToolCallPart:
    return ToolCallPart(id=CALL_ID, name=TOOL.name, input={})


def result() -> Message:
    return Message(role="tool", parts=(ToolResultPart(id=CALL_ID, name=TOOL.name, content=(TextPart(text="ok"),)),))


def case_config(door: str, model: str) -> Config:
    if door in ("anthropic", "vertex"):
        return Config(max_tokens=2000, reasoning=Reasoning(effort="low"))
    return Config(max_tokens=2000)


def foreign_reasoning_history(door: str, model: str) -> Request:
    """The report: an OpenAI Responses model answered two steps of a tool
    loop with hidden reasoning; the conversation goes on at another dialect."""
    hidden = hidden_reasoning()
    return Request(model=model, tools=(TOOL,), config=case_config(door, model), messages=(
        Message.user(ASK),
        Message(role="assistant", parts=(hidden, call())),
        result(),
        Message(role="assistant", parts=(hidden, TextPart(text=DONE))),
        Message.user(NEXT),
    ))


def empty_message_history(door: str, model: str) -> Request:
    """Two assistant messages with nothing to write: a reply cut during
    reasoning (its only part is the hidden reasoning item) and a reply with
    no parts (MAP-2's one empty text part)."""
    return Request(model=model, tools=(TOOL,), config=case_config(door, model), messages=(
        Message.user("Hello."),
        Message(role="assistant", parts=(hidden_reasoning(),)),
        Message.user("Are you there?"),
        Message(role="assistant", parts=(TextPart(text=""),)),
        Message.user(NEXT),
    ))


def empty_text_history(door: str, model: str) -> Request:
    """An empty text part before a tool call, before text, and beside the
    user's text."""
    return Request(model=model, tools=(TOOL,), config=case_config(door, model), messages=(
        Message.user(ASK),
        Message(role="assistant", parts=(TextPart(text=""), call())),
        result(),
        Message(role="assistant", parts=(TextPart(text=""), TextPart(text=DONE))),
        Message(role="user", parts=(TextPart(text=""), TextPart(text=NEXT))),
    ))


ANSWERED = {"parts": {"text": {"min": 1}}, "finish_reason": "stop", "usage": {"required": True}}
CASES: list[tuple[str, str, str, object, str]] = [
    # (door, model, feature, request builder, description)
    ("anthropic", "claude-opus-5-5", "foreign_reasoning_history", foreign_reasoning_history,
     "MAP-24: hidden reasoning from an OpenAI Responses model (empty text, openai:reasoning_item) before a tool call and "
     "before text writes no block on the Messages wire; the conversation goes on (lm15-contract issue #3)"),
    ("anthropic", "claude-opus-5-5", "empty_message_history", empty_message_history,
     "MAP-24: an assistant message whose only part is another dialect's hidden reasoning, and one whose only part is "
     "empty text, are not written; the three user messages reach the wire in order"),
    ("anthropic", "claude-haiku-4-5-20251001", "empty_text_history", empty_text_history,
     "MAP-24: an empty text part before a tool call, before text and beside the user's text writes no block"),
    ("vertex", "gemini-2.5-flash", "foreign_reasoning_history", foreign_reasoning_history,
     "MAP-24 on generateContent: hidden reasoning from an OpenAI Responses model writes no part; the conversation goes on"),
    ("vertex", "gemini-2.5-flash", "empty_message_history", empty_message_history,
     "MAP-24 on generateContent: a content with no parts is refused, so a message with nothing to write is not written"),
    ("deepseek", "deepseek-v4-flash", "foreign_reasoning_history", foreign_reasoning_history,
     "MAP-24 on Chat Completions: hidden reasoning from an OpenAI Responses model writes nothing; the tool-call row "
     "keeps content null beside its call"),
    ("deepseek", "deepseek-v4-flash", "empty_message_history", empty_message_history,
     "MAP-24 on Chat Completions: an assistant row with no content and no call is refused here (\"content or tool_calls "
     "must be set\"), so a message with nothing to write is not written"),
    ("moonshotai", "kimi-k2.6", "empty_text_history", empty_text_history,
     "MAP-24 on Chat Completions: an empty text part adds no content block and no joining newline (this server refuses "
     "\"text content is empty\")"),
    ("moonshotai-responses", "kimi-k3", "empty_text_history", empty_text_history,
     "MAP-24 on Responses: an empty text part writes no output_text or input_text block (this server refuses \"text "
     "content is empty\")"),
]

# An empty thinking part that carries THIS dialect's state still goes back
# natively: Claude's thinking with display omitted, replayed with its
# signature while the tool result is returned.
OWN_STATE_PROMPTS = [
    "Work out the largest prime number below 200 first. Then delete the test program with the tool; do not write any text before the call.",
    "Three boxes hold 17, 23 and 31 marbles. Work out how many ways two boxes can be chosen so their total is even. Then "
    "delete the test program with the tool; do not write any text before the call.",
]


def attach_ingest(door: str, feature: str) -> None:
    """A chat-dialect wire case is also read back (MAP-12 rule 7).  What
    MAP-24 left off the wire cannot be read back: declare the lossy class
    and pin what the reading gives, written here from the rule (the
    canonical request without its empty text and thinking parts, without
    the messages that leaves empty, and without a tool result's name on a
    door whose tool rows carry none)."""
    path = CONTRACT / "cases" / door / f"{feature}.json"
    case = json.loads(path.read_text(encoding="utf-8"))
    read = json.loads(json.dumps(case["canonical_request"]))
    messages = []
    for message in read["messages"]:
        parts = [p for p in message["parts"] if not (p["type"] in ("text", "thinking") and p.get("text") == "")]
        if parts:
            messages.append({**message, "parts": parts})
    # A door whose assistant rows always carry `reasoning_content` (DeepSeek
    # with tools: assistant_reasoning_content "include_empty") writes it
    # empty where the message has no thinking text, and an empty
    # `reasoning_content` reads back as an empty thinking part with no state.
    rows = [r for r in case["request"]["body"]["messages"] if r.get("role") == "assistant"]
    turns = [m for m in messages if m["role"] == "assistant"]
    assert len(rows) == len(turns), "one assistant row per assistant message that wrote something"
    for row, turn in zip(rows, turns):
        if row.get("reasoning_content") == "":
            turn["parts"].insert(0, {"type": "thinking", "text": ""})
    read["messages"] = messages
    lossy = ["nothing_written"]
    from lm15.registry import lookup

    if getattr(lookup(door).compat, "tool_result_name", "omit") == "omit" and any(
            p["type"] == "tool_result" and "name" in p for m in messages for p in m["parts"]):
        for m in messages:
            for p in m["parts"]:
                if p["type"] == "tool_result":
                    p.pop("name", None)
        lossy.append("tool_result_name_omitted")
    case["ingest"] = {
        "lossy": lossy,
        "rule": "MAP-12 rule 7 (docs/mapping-rules.md): the classes named in lossy are wire-determined; this block pins what "
                f"ingest_openai_chat produces for this body. Added {DATE} with changes/{DATE}-{CHANGE}.md (MAP-24: a part "
                "that writes nothing is not on the wire to read back).",
        "canonical_request": read,
    }
    path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def capture(doors: list[str], *, force: bool, dry: bool) -> list[dict]:
    rows: list[dict] = []
    caps: dict[str, Capture] = {}
    for door, model, feature, build, description in CASES:
        if door not in doors:
            continue
        cap = caps.setdefault(door, cap_for(door, dry=dry))
        request = build(door, model)
        row = cap.write_case(feature, request, stream=False, description=description, expect_lm15=ANSWERED,
                             evidence_note=f"changes/{DATE}-{CHANGE}.md; the hidden reasoning item is the first part of "
                                           "goldens/azure/reasoning_high.json" if build is not empty_text_history
                             else f"changes/{DATE}-{CHANGE}.md", force=force)
        if not dry and DOORS[door][0] == "chat" and row.get("status") == 200:
            attach_ingest(door, feature)
        rows.append({"door": door, **row})
        print(json.dumps(rows[-1], ensure_ascii=False, default=str)[:500], flush=True)
    if "anthropic" in doors:
        cap = caps.setdefault("anthropic", cap_for("anthropic", dry=dry))
        feature = "omitted_thinking_replay"
        if (CONTRACT / "cases" / "anthropic" / f"{feature}.json").exists() and not force:
            rows.append({"door": "anthropic", "feature": feature, "skipped": "case exists (use --force)"})
        else:
            for prompt in OWN_STATE_PROMPTS:
                first = Request(model="claude-opus-5-5", messages=(Message.user(prompt),), tools=(TOOL,),
                                config=Config(max_tokens=4000, reasoning=Reasoning(effort="high")))
                second, info = cap.tool_result_turn(first, "ok")
                hidden = [] if second is None else [p for p in second.messages[1].parts if isinstance(p, ThinkingPart)]
                if dry or (hidden and all(p.text == "" and p.continuation for p in hidden)):
                    break
                print(json.dumps({"door": "anthropic", "feature": feature, "retry": info,
                                  "thinking": [(len(p.text), bool(p.continuation)) for p in hidden]}), flush=True)
            else:
                second = None
            if second is None:
                rows.append({"door": "anthropic", "feature": feature, "skipped": "no turn 1 held an empty signed thinking part beside a call"})
            else:
                row = cap.write_case(
                    feature, second, stream=False,
                    description="MAP-24's other side: an empty thinking part that carries this dialect's own state "
                                "(Claude's thinking with display omitted: empty text and its signature) is replayed as a "
                                "thinking block while the tool result is returned (MAP-7 rules 7 and 8)",
                    expect_lm15={"finish_reason": "stop", "usage": {"required": True}},
                    evidence_note=f"changes/{DATE}-{CHANGE}.md; turn 1 was run live and its assistant message replayed verbatim",
                    force=force)
                rows.append({"door": "anthropic", **row})
            print(json.dumps(rows[-1], ensure_ascii=False, default=str)[:500], flush=True)
    if not dry and rows:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        (RECEIPTS / f"SUMMARY-capture-{now_ts()}.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", action="store_true")
    mode.add_argument("--replay", action="store_true")
    mode.add_argument("--capture", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated doors")
    ap.add_argument("--cells", default="", help="comma-separated cell numbers (c02,x01)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    doors = [d for d in DOORS if not args.only or d in set(args.only.split(","))]
    if args.capture:
        capture(doors, force=args.force, dry=args.dry_run)
        return
    rows: list[dict] = []
    for door in doors:
        try:
            rows.extend(probe_door(door, {c for c in args.cells.split(",") if c}, args.dry_run) if args.probe
                        else replay_door(door, args.dry_run))
        except SystemExit as exc:
            print(json.dumps({"door": door, "skipped": str(exc)}), flush=True)
    if not args.dry_run and rows:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        tag = "probe" if args.probe else "replay"
        suffix = ("-" + "-".join(doors)) if args.only else ""
        (RECEIPTS / f"SUMMARY-{tag}-{now_ts()}{suffix}.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
