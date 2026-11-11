#!/usr/bin/env python3
"""Write mapping/empty-parts.json: histories that hold parts with nothing
for the wire they are sent to (MAP-24, docs/mapping-rules.md;
changes/2026-11-11-empty-parts.md; lm15-contract issue #3).

    python3 tools/make_empty_parts_vectors.py          # write the file
    python3 tools/make_empty_parts_vectors.py --check  # exit 1 if it differs

Every vector is a canonical request (the model is filled in per provider)
built with ``build_request``.  Two kinds of expectation, both written here
by hand from the rule, never computed from an implementation:

- ``same_as``: MAP-24 rule 1 is an equivalence.  A part that writes nothing
  on a wire leaves that wire exactly as if the caller had not sent the
  part, and a message left with nothing as if the caller had not sent the
  message.  The harness builds the vector's request and the ``same_as``
  request (the same history with those parts and messages taken out) and
  the two wire requests must be equal, byte for byte.  The second request
  is an ordinary one; the cases pin how each dialect writes it.
- ``expect``: for the providers named, the keys of the built body that
  must equal the value given (``absent``: keys the body must not have).
  Used where the part must be WRITTEN: it carries state the dialect
  consumes (a signed thinking block, a Gemini thought signature, a
  Responses reasoning item), or it is a tool result.

In both kinds the built body must hold no text block with no characters and
no message with nothing in it (harness/check.py ``empty_wire_findings``).
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "mapping" / "empty-parts.json"

ASK = "Delete the test program now."
DONE = "Deleted."
NEXT = "Thanks. Reply with the single word: bye"

# The four dialect builders, and the presets whose compat changes what a
# thinking part or an assistant row becomes.
DIALECTS = ["anthropic", "gemini", "openai", "openai_chat"]
MODELS = {
    "anthropic": "claude-haiku-4-5",
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-5.4",
    "openai_chat": "gpt-5.4",
    # Chat Completions preset with thinking_replay "native" and
    # assistant_reasoning_content "include_empty".
    "deepseek": "deepseek-v4-flash",
    # Messages preset with thinking_replay "unsigned".
    "moonshotai-anthropic": "kimi-k3",
}


def text(value: str) -> dict:
    return {"type": "text", "text": value}


def user(*parts: Any) -> dict:
    return {"role": "user", "parts": [text(p) if isinstance(p, str) else p for p in parts]}


def assistant(*parts: Any) -> dict:
    return {"role": "assistant", "parts": [text(p) if isinstance(p, str) else p for p in parts]}


def state(provider: str, kind: str, data: dict) -> list:
    return [{"provider": provider, "kind": kind, "data": data}]


def hidden(continuation: list | None = None) -> dict:
    """Hidden thinking (MAP-7 rule 11): empty text, and its state if any."""
    part: dict = {"type": "thinking", "text": ""}
    if continuation is not None:
        part["continuation"] = continuation
    return part


OPENAI_STATE = state("openai", "reasoning_item", {"id": "rs_1", "encrypted_content": "gAAAA"})
ANTHROPIC_SIGNATURE = state("anthropic", "thinking_signature", {"signature": "sigA"})
ANTHROPIC_REDACTED = state("anthropic", "redacted_thinking", {"data": "blob"})
GEMINI_THOUGHT = state("gemini", "thought_signature", {"value": "sigG"})
GEMINI_TEXT = state("gemini", "thought_signature", {"value": "sigT"})

CALL = {"type": "tool_call", "id": "call_1", "name": "delete_program", "input": {}}
IMAGE = {"type": "image", "media_type": "image/png", "url": "https://example.com/receipt.png"}


def result(*content: Any) -> dict:
    return {"role": "tool", "parts": [{"type": "tool_result", "id": "call_1", "name": "delete_program",
                                       "content": [text(c) if isinstance(c, str) else c for c in content]}]}


def request(*messages: dict, **more: Any) -> dict:
    return {"messages": list(messages), **more}


# ─── the wire spellings the `expect` blocks are written in ───────────

def a_text(value: str) -> dict:
    return {"type": "text", "text": value}


A_USE = {"type": "tool_use", "id": "call_1", "name": "delete_program", "input": {}}
A_RESULT_OK = {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": "ok"}]}
G_CALL = {"functionCall": {"name": "delete_program", "args": {}, "id": "call_1"}}
G_RESULT_OK = {"role": "user", "parts": [{"functionResponse": {"name": "delete_program", "response": {"result": "ok"}, "id": "call_1"}}]}
R_REASONING = {"type": "reasoning", "id": "rs_1", "encrypted_content": "gAAAA", "summary": []}
R_CALL = {"type": "function_call", "call_id": "call_1", "name": "delete_program", "arguments": "{}"}
R_RESULT_OK = {"type": "function_call_output", "call_id": "call_1", "output": "ok"}
C_CALL_ROW = {"role": "assistant", "content": None,
              "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "delete_program", "arguments": "{}"}}]}
C_RESULT_OK = {"role": "tool", "tool_call_id": "call_1", "content": "ok"}


def a_user(value: str) -> dict:
    return {"role": "user", "content": [a_text(value)]}


def g_user(value: str) -> dict:
    return {"role": "user", "parts": [{"text": value}]}


def r_user(value: str) -> dict:
    return {"role": "user", "content": [{"type": "input_text", "text": value}]}


def r_assistant(value: str) -> dict:
    return {"role": "assistant", "content": [{"type": "output_text", "text": value}]}


def c_user(value: str) -> dict:
    return {"role": "user", "content": value}


REPORT = request(user(ASK), assistant(hidden(OPENAI_STATE), CALL), result("ok"),
                 assistant(hidden(OPENAI_STATE), DONE), user(NEXT))
REPORT_PLAIN = request(user(ASK), assistant(CALL), result("ok"), assistant(DONE), user(NEXT))

VECTORS: list[dict] = [
    {
        "id": "foreign-hidden-thinking",
        "why": "The report (issue #3): hidden reasoning from an OpenAI Responses model, before a tool call and before "
               "text, in a history sent to another dialect. Rule 2: state for another dialect is not state here; "
               "rule 1: with no text either, the part writes nothing. On its own dialect the item goes back natively "
               "(MAP-7 rule 8), `summary` present and empty.",
        "request": REPORT,
        "same_as": {"providers": ["anthropic", "gemini", "openai_chat", "deepseek", "moonshotai-anthropic"], "request": REPORT_PLAIN},
        "providers": ["anthropic", "gemini", "openai", "openai_chat", "deepseek", "moonshotai-anthropic"],
        "expect": {
            "anthropic": {"messages": [
                a_user(ASK), {"role": "assistant", "content": [A_USE]}, A_RESULT_OK,
                {"role": "assistant", "content": [a_text(DONE)]}, a_user(NEXT)]},
            "gemini": {"contents": [
                g_user(ASK), {"role": "model", "parts": [G_CALL]}, G_RESULT_OK,
                {"role": "model", "parts": [{"text": DONE}]}, g_user(NEXT)]},
            "openai": {"input": [
                r_user(ASK), R_REASONING, R_CALL, R_RESULT_OK, R_REASONING, r_assistant(DONE), r_user(NEXT)]},
            "openai_chat": {"messages": [
                c_user(ASK), C_CALL_ROW, C_RESULT_OK, {"role": "assistant", "content": DONE}, c_user(NEXT)]},
        },
    },
    {
        "id": "foreign-hidden-thinking-only-part",
        "why": "A reply cut during reasoning: its only part is another dialect's hidden reasoning. Rule 3: a message "
               "left with nothing to write is not written; the messages around it keep their order.",
        "request": request(user("Hello."), assistant(hidden(OPENAI_STATE)), user(NEXT)),
        "same_as": {"providers": ["anthropic", "gemini", "openai_chat", "deepseek", "moonshotai-anthropic"],
                    "request": request(user("Hello."), user(NEXT))},
        "providers": ["anthropic", "gemini", "openai", "openai_chat", "deepseek", "moonshotai-anthropic"],
        "expect": {
            "anthropic": {"messages": [a_user("Hello."), a_user(NEXT)]},
            "gemini": {"contents": [g_user("Hello."), g_user(NEXT)]},
            "openai": {"input": [r_user("Hello."), R_REASONING, r_user(NEXT)]},
            "openai_chat": {"messages": [c_user("Hello."), c_user(NEXT)]},
        },
    },
    {
        "id": "hidden-thinking-no-state",
        "why": "An empty thinking part with no state at all, before text and as the only part of a message: nothing to "
               "replay natively, no text to replay as text.",
        "request": request(user(ASK), assistant(hidden(), DONE), user("Are you there?"), assistant(hidden()), user(NEXT)),
        "same_as": {"request": request(user(ASK), assistant(DONE), user("Are you there?"), user(NEXT))},
        "providers": ["anthropic", "gemini", "openai", "openai_chat", "deepseek", "moonshotai-anthropic"],
    },
    {
        "id": "own-state-anthropic",
        "why": "Rule 1's other side: an empty thinking part that carries state the dialect consumes is written in its "
               "native form. Claude's thinking with display omitted is empty text with a signature (MAP-7 rule 7) and "
               "goes back as a thinking block; redacted thinking goes back as redacted_thinking. Every other dialect "
               "writes nothing for them.",
        "request": request(user(ASK), assistant(hidden(ANTHROPIC_SIGNATURE), CALL), result("ok"),
                           assistant(hidden(ANTHROPIC_REDACTED), DONE), user(NEXT)),
        "same_as": {"providers": ["gemini", "openai", "openai_chat"], "request": REPORT_PLAIN},
        "expect": {
            "anthropic": {"messages": [
                a_user(ASK),
                {"role": "assistant", "content": [{"type": "thinking", "thinking": "", "signature": "sigA"}, A_USE]},
                A_RESULT_OK,
                {"role": "assistant", "content": [{"type": "redacted_thinking", "data": "blob"}, a_text(DONE)]},
                a_user(NEXT)]},
        },
    },
    {
        "id": "own-state-gemini",
        "why": "Gemini 3.x sends parts with empty text that carry a thoughtSignature, on a thought part and on a text "
               "part; the signature is replay state (MAP-7 rule 8) and both go back as sent. Every other dialect "
               "writes nothing for them.",
        "request": request(user(ASK), assistant(hidden(GEMINI_THOUGHT), {"type": "text", "text": "", "continuation": GEMINI_TEXT}, DONE),
                           user(NEXT)),
        "same_as": {"providers": ["anthropic", "openai", "openai_chat"],
                    "request": request(user(ASK), assistant(DONE), user(NEXT))},
        "expect": {
            "gemini": {"contents": [
                g_user(ASK),
                {"role": "model", "parts": [{"text": "", "thought": True, "thoughtSignature": "sigG"},
                                            {"text": "", "thoughtSignature": "sigT"}, {"text": DONE}]},
                g_user(NEXT)]},
        },
    },
    {
        "id": "state-with-no-value",
        "why": "A server that signs nothing sends `signature: \"\"` (DeepSeek's and Moonshot's Messages doors), and a "
               "Gemini signature can be empty the same way. State with no value is no state to replay: with empty "
               "text too, the part writes nothing, on its own dialect as on the others.",
        "request": request(user(ASK),
                           assistant(hidden(state("anthropic", "thinking_signature", {"signature": ""})),
                                     {"type": "text", "text": "", "continuation": state("gemini", "thought_signature", {"value": ""})},
                                     DONE),
                           user(NEXT)),
        "same_as": {"request": request(user(ASK), assistant(DONE), user(NEXT))},
        "providers": ["anthropic", "gemini", "openai", "openai_chat", "deepseek", "moonshotai-anthropic"],
    },
    {
        "id": "empty-text-part",
        "why": "An empty text part before a tool call, before text and beside the user's text. No empty block, and "
               "where the wire joins text into one string, no newline for the part that is not there.",
        "request": request(user(ASK), assistant("", CALL), result("ok"), assistant("", DONE), user("", NEXT)),
        "same_as": {"request": REPORT_PLAIN},
    },
    {
        "id": "empty-text-only-part",
        "why": "MAP-2 reads a reply with no parts as one empty text part, and MAP-12 reads an assistant row with null "
               "content the same way; a caller may also send an empty user turn. Each is a message with nothing to "
               "write.",
        "request": request(user(ASK), assistant(""), user(""), assistant(DONE), user(NEXT)),
        "same_as": {"request": request(user(ASK), assistant(DONE), user(NEXT))},
    },
    {
        "id": "citation-without-text",
        "why": "A citation that quotes nothing (a URL and a title) has no text to write where a dialect writes a "
               "citation as its quoted text; none writes an empty block for it.",
        "request": request(user("What is the capital of France?"),
                           assistant("Paris.", {"type": "citation", "url": "https://example.com/france", "title": "France"}),
                           user(NEXT)),
        "same_as": {"request": request(user("What is the capital of France?"), assistant("Paris."), user(NEXT))},
    },
    {
        "id": "empty-system",
        "why": "A system prompt given as parts whose text is empty is no system prompt: no empty system block, no "
               "empty instruction, no empty system row.",
        "request": request(user(NEXT), system=[text("")]),
        "same_as": {"request": request(user(NEXT))},
    },
    {
        "id": "empty-system-part",
        "why": "An empty part among a system prompt's parts writes nothing, a joining newline included.",
        "request": request(user(NEXT), system=[text(""), text("Be brief.")]),
        "same_as": {"request": request(user(NEXT), system=[text("Be brief.")])},
    },
    {
        "id": "empty-developer-message",
        "why": "A developer message with no text is a message with nothing to write; a dialect that marks developer "
               "text with a prefix does not write the prefix alone.",
        "request": request({"role": "developer", "parts": [text("")]}, user(NEXT)),
        "same_as": {"request": request(user(NEXT))},
    },
    {
        "id": "tool-result-empty-output",
        "why": "Rule 4: a tool result is always written. An empty output is an answer (INV-014: one empty text part) "
               "and reaches every wire as the empty string, under its call.",
        "request": request(user(ASK), assistant(CALL), result(""), user(NEXT)),
        "expect": {
            "anthropic": {"messages": [
                a_user(ASK), {"role": "assistant", "content": [A_USE]},
                {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": ""}]},
                a_user(NEXT)]},
            "gemini": {"contents": [
                g_user(ASK), {"role": "model", "parts": [G_CALL]},
                {"role": "user", "parts": [{"functionResponse": {"name": "delete_program", "response": {"result": ""}, "id": "call_1"}}]},
                g_user(NEXT)]},
            "openai": {"input": [
                r_user(ASK), R_CALL, {"type": "function_call_output", "call_id": "call_1", "output": ""}, r_user(NEXT)]},
            "openai_chat": {"messages": [
                c_user(ASK), C_CALL_ROW, {"role": "tool", "tool_call_id": "call_1", "content": ""}, c_user(NEXT)]},
        },
    },
    {
        "id": "tool-result-empty-text-beside-image",
        "why": "Rule 4: inside a result that has another block, an empty text part writes no block (a Messages server "
               "refuses one there too: receipts/2026-11-11-empty-parts/moonshotai-anthropic).",
        "request": request(user(ASK), assistant(CALL), result("", IMAGE), user(NEXT)),
        "same_as": {"request": request(user(ASK), assistant(CALL), result(IMAGE), user(NEXT))},
        # The Chat Completions preset refuses an image in a tool row (MAP-10).
        "providers": ["anthropic", "gemini", "openai"],
    },
    {
        "id": "assistant-data-part-is-content",
        "why": "The edge of the rule: a data part is never a part with nothing. An assistant data part (a judged or "
               "structured answer kept in the history) is written on every wire as its value in compact canonical "
               "JSON (changes/2026-09-19-jev-state.md D3: \"An assistant data part ... renders the same way\"), so its "
               "message is written. Found by the history replay: three SDKs dropped it on the Responses and Chat "
               "Completions wires and one refused it.",
        "request": request(user("Is the invoice paid?"), assistant({"type": "data", "value": {"paid": True, "note": ""}}), user(NEXT)),
        "expect": {
            "anthropic": {"messages": [
                a_user("Is the invoice paid?"),
                {"role": "assistant", "content": [a_text('{"paid":true,"note":""}')]},
                a_user(NEXT)]},
            "gemini": {"contents": [
                g_user("Is the invoice paid?"),
                {"role": "model", "parts": [{"text": '{"paid":true,"note":""}'}]},
                g_user(NEXT)]},
            "openai": {"input": [
                r_user("Is the invoice paid?"), r_assistant('{"paid":true,"note":""}'), r_user(NEXT)]},
            "openai_chat": {"messages": [
                c_user("Is the invoice paid?"), {"role": "assistant", "content": '{"paid":true,"note":""}'}, c_user(NEXT)]},
        },
    },
    {
        "id": "nothing-to-send",
        "why": "A request whose every message has nothing to write has no equivalent: lm15 sends the empty list and the "
               "provider's own refusal is the answer (it names the missing input).",
        "request": request(user("")),
        "expect": {
            "anthropic": {"messages": []},
            "gemini": {"contents": []},
            "openai": {"input": []},
            "openai_chat": {"messages": []},
        },
    },
    {
        "id": "cache-index-after-left-out-message",
        "why": "CacheConfig.prefix_until_index names one of the CALLER's messages. A message left out before it does not "
               "move the mark to a later message.",
        "request": request(user("Here is the manual: chapter one."), assistant(hidden(OPENAI_STATE)),
                           user("And chapter two."), assistant("Noted."), user(NEXT),
                           config={"cache": {"mode": "auto", "prefix_until_index": 2}}),
        "same_as": {"request": request(user("Here is the manual: chapter one."), user("And chapter two."),
                                       assistant("Noted."), user(NEXT),
                                       config={"cache": {"mode": "auto", "prefix_until_index": 1}})},
        "providers": ["anthropic"],
    },
]


def document() -> dict:
    vectors = copy.deepcopy(VECTORS)
    ids = [v["id"] for v in vectors]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate vector id")
    for v in vectors:
        providers = v.get("providers") or DIALECTS
        for name in [*providers, *(v.get("same_as", {}).get("providers") or []), *v.get("expect", {})]:
            if name not in MODELS:
                raise SystemExit(f"{v['id']}: no model for provider {name}")
        covered = set(v.get("same_as", {}).get("providers") or (providers if "same_as" in v else [])) | set(v.get("expect", {}))
        missing = [p for p in providers if p not in covered]
        if missing:
            raise SystemExit(f"{v['id']}: no expectation for {missing}")
    return {
        "description": "MAP-24 vectors: histories that hold parts with nothing for the wire they are sent to (hidden "
                       "thinking carrying another dialect's state, empty text, a citation that quotes nothing, an empty "
                       "system prompt) and the parts that must still be written (state the dialect consumes, tool "
                       "results). The harness's mapping direction builds each vector's `request` with build_request for "
                       "each provider in the vector's `providers` (default: `dialects`), the model filled in from "
                       "`models`. `same_as`: the wire request must equal, whole, the one built from `same_as.request` "
                       "(for `same_as.providers`, default every provider of the vector). `expect`: for that provider, "
                       "each named key of the built body must equal the value given. Every built body must hold no "
                       "text block with no characters and no message with nothing in it. Generated by "
                       "tools/make_empty_parts_vectors.py; do not edit by hand.",
        "provenance": {
            "source": "hand-authored", "date": "2026-11-11",
            "evidence": "docs/mapping-rules.md MAP-24 (rules 1 to 4) and MAP-7 rules 8, 9 and 11; spec/invariants.md "
                        "INV-014; changes/2026-11-11-empty-parts.md. The `expect` blocks are written by hand in each "
                        "dialect's spelling as the cases pin it (cases/anthropic/foreign_reasoning_history.json, "
                        "cases/vertex/foreign_reasoning_history.json, cases/deepseek/foreign_reasoning_history.json, "
                        "cases/openai/reasoning_replay.json); the provider facts behind the rule are the receipts under "
                        "receipts/2026-11-11-empty-parts/.",
        },
        "dialects": DIALECTS,
        "models": MODELS,
        "build": vectors,
    }


def render() -> str:
    return json.dumps(document(), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text_out = render()
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text_out:
            print(f"{OUT.relative_to(ROOT)} differs from its generator; run tools/make_empty_parts_vectors.py", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text_out, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(VECTORS)} vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
