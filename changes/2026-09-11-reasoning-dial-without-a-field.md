# 2026-09-11 — A reasoning dial the wire cannot carry is a raise, never an omission

Ratification: PENDING — drafted in session by the agent building the
three-language playground (lm15-ts examples/provider-page); put to Maxime
Rivest with the fixes already implemented in the reference and both ports.

## What was found

`lm15-ts/tests/provider_examples.test.ts` builds the playground's request in
three languages — TypeScript (`lm15/browser`), Python (lm15-python under
Pyodide), Rust (lm15-rs compiled to wasm32) — and compares the bytes. For
`ollama` with `config.reasoning = { effort: "low" }`:

- **Rust refused**: `UnsupportedFeatureError: ollama: reasoning.effort="low"
  has no field on this server (compat thinking_format='none'); omit
  config.reasoning, or pass the server's own knob through extensions`
  (`src/dialects/openai_chat/payload.rs`, which cites MAP-5 and MAP-7 and
  notes "the reference sent nothing").
- **Python and TypeScript sent the request with no reasoning field at all.**

The Rust port was right and said so in a comment nobody read back into the
reference. The rule is not new: `docs/mapping-rules.md` MAP-5 (a setting
the dialect cannot carry raises before the wire) and MAP-7 rule 2 (an
effort word with no native level raises client-side rather than
downgrading silently); `playbooks/port.md` rule 4 (a raise or an
extensions door, never omission). The `ollama` and `lmstudio` presets have
`thinking_format = "none"` — no reasoning field exists on that wire — so a
caller who set the dial got a silent no-op and, on a model that reasons by
default, paid for hidden tokens they asked to limit.

## What this changes

`cases/ollama/reasoning_effort_refused.json` pins the outcome:
`build_request` raises `UnsupportedFeatureError` (`unsupported_feature`)
when `config.reasoning` is set and the bound compat's `thinking_format` is
`none`. The message names the server's knob path (`extensions`) as the
door, as Rust's did.

- lm15-python: `OpenAIChatLM._payload` raises before the wire (the
  reference; same message as Rust).
- lm15-ts: `OpenAIChatLM.payload` raises before the wire.
- lm15-rs: unchanged.

No live receipt is needed: this is a consumer-side refusal (the wire is
never reached), pinned by a hand-authored case with its rule cited, like
`cases/zai/tool_choice_required.json`.

## Trade-off, stated

A caller who set `reasoning` on an ollama model as a harmless default now
gets an error where they used to get a call. That is the family's rule —
silent omission is the failure mode it exists to prevent — and the message
says exactly what to do (omit it, or use `extensions` for the server's own
field).
