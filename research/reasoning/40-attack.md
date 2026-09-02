# Reasoning — attack on the model (2026-09-02)

**Label:** self-review by the author. Weaker than an independent review.

1. **Beginner writes `Reasoning(effort="high")` and switches providers.**
   OpenAI verbatim; Anthropic adaptive verbatim; Anthropic 4.5 → budget
   16384 (table); Gemini 2.5 → budget 16384; Gemini 3.7 → level high;
   xAI verbatim; Groq gpt-oss verbatim; Groq Qwen → server 400 (only
   none/default). Holds: same code runs, one loud failure where the
   model has no dial, no silent downgrade anywhere.
2. **`effort="off"` fan-out.** OpenAI none; Anthropic omit; Gemini 2.5
   Flash 0; Gemini 3.x RAISE; xAI RAISE. The Gemini 3.x raise is the
   only client-side model check in the rule; without it the user pays
   58 tokens per call silently (measured). Holds.
3. **`Reasoning()` with no effort.** Now a TypeError at construction.
   Migration: `Reasoning(effort="off")`. Breaking before 1.0, stated.
4. **`thinking_budget` on Sonnet 5.** RAISE with the provider's own
   sentence. Previously the adapter sent `enabled` + budget → server 400
   anyway. Holds, and the message now says why.
5. **Gemini 3.x tool loop without signatures.** Already carried by
   `ContinuationState`; the accumulator attaches them on streams. Holds
   (receipt: 400 without, 200 with).
6. **OpenAI tool loop under `store: false`.** Reasoning items now round-
   trip through `ThinkingPart.continuation`. Holds; measured optional but
   documented as required for continuity.
7. **Groq Qwen `<think>` leak.** `compat="groq"` sends
   `include_reasoning: true` and parses `message.reasoning`; measured
   default leaks into content because `reasoning_format` defaults to raw
   for Qwen. Fix: the groq preset sends `reasoning_format: "parsed"`
   whenever reasoning is not off. Needs a receipt at implementation.
8. **Port implementer.** The table is data; two model-class functions
   (Anthropic, Gemini) and one grading table are the only logic. Holds.
9. **`summary="detailed"` on Anthropic.** RAISE, though thinking is
   shown anyway. A user who wanted "show me" and wrote "detailed" hits
   a raise. Trade-off: `auto` is the portable spelling; the raise tells
   them. Holds, stated.
10. **Temperature with thinking.** Anthropic 400, OpenAI 400 (any
    temperature on these models), Gemini fine. No client rule; the
    servers are loud. Holds.

Not covered: streaming deltas of reasoning items on OpenAI; interleaved
thinking between tool calls on Anthropic; Bedrock (source missing).
