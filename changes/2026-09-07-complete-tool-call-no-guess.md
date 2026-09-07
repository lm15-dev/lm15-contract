# 2026-09-07 — A nameless tool call on the complete path is refused (MAP-9 extended)

Ratification: RATIFIED 2026-09-07 — Maxime Rivest, in session ("i ratify"),
after the entry was drafted with the four cases, the reference fixed and
both shims green (response 302/0/1 each), and after the question "is this
a big ratification?" was answered: one sentence of rule closing a gap in
the 2026-09-02 rule, no golden changed, one judgment call (the class).
Transcribed. The complete-path paragraph of MAP-9 and the four
`<dialect>.tool_call_unnamed_complete` pins are normative from this date.
Drafted after the Rust module 5 review found the reference guessing on
the complete path what MAP-9 forbids on the stream path.

## What this changes

One rule, four pins, one reference fix:

1. **The rule.** MAP-9 gains a paragraph: a complete (non-streaming) body
   whose tool call carries no name is refused at `parse_response` with
   `ProviderError` (ErrorCode `provider`). The four sites: a Responses
   `function_call` item without `name`, a chat `tool_calls[i].function`
   without `name`, an Anthropic `tool_use` block without `name`, a Gemini
   `functionCall` without `name`. Nothing is salvaged: a complete body
   has no partial the caller already saw.
2. **The pins.** Four hand-authored cases,
   `<dialect>.tool_call_unnamed_complete`: each dialect's live `tools`
   capture with the name removed and nothing else changed, the wire
   request copied from that case, `expect_lm15.raises` at `parse_response`.
   The goldens carry provenance only (a refusal with nothing salvaged).
3. **The reference.** `lm15/providers/{openai,openai_chat,anthropic,gemini}.py`
   drop the `or "tool"` fallback and raise `ProviderError` naming the
   path. Five unit tests.

## Why

- The stream rule (2026-09-02) says lm15 never guesses which tool the
  model meant. The complete path did exactly that: `name=str(item.get("name") or "tool")`.
  The same turn answered a `ToolCallPart(name="tool")` under
  `stream=False` and a `StreamAssemblyError` under `stream=True` — the
  parity INV-051 asks for was broken by the rule that motivated it.
- `"tool"` is not a default, it is a fabricated fact. An agent loop that
  looks the name up in its function table fails later and further from
  the cause; one with a catch-all dispatches the wrong function with no
  error. That is the silent failure MAP-8 and MAP-9 exist to refuse.
- The refusal costs nothing in practice: every shipped provider names
  every call (the four `tools` captures, every `streaming_tool_call`),
  so the path fires only on a broken reply.
- This is not the request-side "universal feel" tension (a knob a
  provider lacks, where a sensible default or a build-time refusal are
  both defensible). The provider *replied*; the reply is missing the one
  fact the caller must act on. No default exists for it.

## Class: `ProviderError`, not `StreamAssemblyError`

`stream_assembly` is defined as "a stream cannot become a Response
without inventing a fact" and carries `partial` / `part_index`, both
meaningless for a complete body. `ProviderError` says what happened: the
provider's reply is not actionable. Considered and rejected: a new
ErrorCode (a class per malformed field would not scale; the message
names the path); `InvalidRequestError` (the caller's request was fine).

## Evidence

- Rust (`lm15-rs` c64d551) already refuses at all four sites with
  `ProviderError` and passes the four new cases unchanged; the reference
  fix brings the two ports back into agreement.
- Reference after the fix: `--direction response` 302 pass / 0 fail / 1
  skip; `--direction stream` 40 pass; the full pytest suite green.
- `tools/audit.py`: clean.

## Trade-offs, stated

- A provider that one day legitimately sends a nameless call (none does)
  would fail loudly rather than degrade; that is the intended side of the
  line.
- The `"tool"` fallback also covered a call whose name is the empty
  string; that is now refused too (an empty name is no name).
