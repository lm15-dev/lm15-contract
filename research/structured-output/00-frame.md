# Structured output — the frame (no provider words)

## What the user is trying to do
Get an answer that parses: valid JSON, or JSON that matches a schema they wrote, every time, without post-hoc repair.

## What the user wants to control
1. "Any valid JSON" versus "this schema".
2. Whether the schema is enforced (constrained decoding) or only requested.
3. Which schema dialect they may write (JSON Schema features that survive).

## What the user wants to observe
1. The text, parseable; `Response.json`.
2. Whether the provider refused or truncated instead of complying (finish reason).
3. Which schema features the provider rejected, loudly, at request time.

## What must never happen
1. A schema silently rewritten (a keyword dropped, a required list changed, additionalProperties flipped) so that the request is accepted.
2. "Enforced" claimed where the provider only "encourages".
3. A schema accepted by one provider and silently ignored by another.
4. Two canonical spellings for the same intent.

## Questions
- Which providers enforce (grammar) versus prompt; which need `strict`; which need every property required and `additionalProperties: false`?
- Which JSON Schema keywords are rejected per provider, at request time or silently?
- Can structured output coexist with tools, with thinking, with streaming?
- What is the wire shape for "any JSON" versus "this schema", and is a name required?
- What comes back on refusal or on max_tokens truncation?
