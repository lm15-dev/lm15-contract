# Tool choice + structured output — attack (2026-09-02, self-review, labelled)

1. **Beginner forces a tool on xAI with a schema set.** Now RAISE with the
   receipt's wording; before, JSON text came back and the loop broke.
2. **`parallel=False` on Gemini in agnostic code.** RAISE. Cost: the
   agnostic user drops the field for Gemini. Under MAP-6 A1's test the
   fallback would spend nothing, but the outcome is NOT observable from
   usage (a second call arrives and the caller executes it) — so the
   exception does not apply; raise is right.
3. **Allowlist on xAI.** RAISE. The receipt shows the excluded tool
   called; a silent widen is the worst kind.
4. **Migrating provider-native `response_format` dicts.** Two corpus
   cases (`gemini.response_schema`, `openai.structured_output`) rewrite to
   the canonical shape; the wire must stay byte-identical. Users who
   passed native shapes get a ValueError with the two accepted shapes and
   the `extensions` door in the message.
5. **Anthropic `json_object`.** RAISE with guidance ("give a schema; the
   Messages API has no any-JSON mode"). Before: a server 400 with the
   provider's wording. Both loud; the client message names the fix.
6. **Schema keywords Anthropic rejects.** Untouched, verbatim, server 400.
   lm15 must not strip `minimum` to please one provider (frame rule 1).
7. **Ports.** Table is data; INV-050 is a shape check.

Not covered: streaming with structured output (Groq forbids; others
unmeasured); refusals under a schema; Bedrock.
