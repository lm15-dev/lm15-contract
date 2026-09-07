# Tool-result content — attack

Each lens tries to break 30-model.md. A lens that finds a hole names the fix.

## Cold learner

"I put an image in `tool_result` and Groq raised. Why not just send it?"
The error says: this server takes text-only tool rows (HTTP 400 on the
array form); use the Responses/Anthropic/Gemini doors, or render to text
yourself. Fine. **Hole:** the message must name the receipt-backed reason,
not "unsupported" alone. Fix: the refusal text names the door and the
cause (`server rejects`, `server silently drops`).

## Library author on top (DSPy-style)

Wants one code path: build `ToolResultPart` with whatever the tool
returned, call `complete`. Gets: a raise on 8 bindings for images. Acceptable
only if the raise is *before* any wire and typed, so the library can catch
`UnsupportedFeatureError` and fall back to its own text rendering.
**Hole:** none, provided the raise is pre-wire (it is: `build_request`).

## Port implementer (Go / Rust)

Needs the verdict as data: a knob per preset with two values, and per
dialect a fixed block shape. The Gemini `$ref` interleave is the only
piece that is not a table; the model states it as a deviation (media after
text, no `$ref`). **Hole:** `name` resolution on Gemini walks the
transcript — spell out the rule: nearest preceding assistant
`ToolCallPart` with the same id; if none, the caller's `name`; if neither,
raise (never `"tool"`). Fix: MAP-10 rule 6.

## Provider-switcher mid-conversation

A transcript with image tool results built against Anthropic is replayed
to DeepSeek. Today: 200 and the model sees `[Unsupported Image]`. Under
MAP-10: raise before the wire, naming the part and the preset. The user
loses nothing silently. **Hole:** the raise must also fire for *history*,
not only the newest result — every message is mapped, so it does.

## Cost accountant

DeepSeek's silent degrade cost real tokens for an answer that could not be
right. OpenAI Chat the same. The rule saves that money. The pass itself:
~200 inference calls on cheap models, no cell above 2 calls; usage per
cell is in `20-results.json`. **Hole:** no per-cell dollar figure. Stated:
prices were not folded in; the bound is calls × list price.

## Agent-loop author

Two calls, two results, one turn. The `pair` cell proves association on
every `native` binding that answered. **Hole:** the `error` cell shows
Responses/Chat carry `is_error` only as text. An agent loop that branches
on "did the tool fail" on the *model's* side gets a prefix, not a flag.
Stated as the mapping; Anthropic and Gemini carry a real flag.

## Skeptic of the oracle

"Your grid is too small; OpenAI failed the control." Correct — and that is
why the control exists. Re-run at 256px/high: control OK, then the
tool-result cells OK on gpt-5.4. The 64px OpenAI misses are **retracted as
evidence** (kept in the ledger, not cited by a verdict). **Hole:** every
`reject` verdict resting on "200 + content not received" must have a
passing control on the same model at the same oracle. Checked: openai-chat
gpt-5.4 (control OK at 256px), deepseek (control itself failed at both
oracles → the 200-miss there is corroborated by the model's own
`[Unsupported Image]` text, which names the mechanism). Recorded.

## What the attack changed in the model

- MAP-10 rule 6 (name resolution) written out.
- Refusal messages must name the cause class and the door.
- The 64px OpenAI rows are struck from the evidence list of any verdict.
