# Reasoning — the frame (no provider words)

## What the user is trying to do

Decide how much hidden thinking a model does before it answers, pay for
exactly that, and get the thinking back when the provider shows it.

## What the user wants to control

1. **How much** thinking: none, a little, a lot, as much as the model
   wants — one dial.
2. **A hard cap** in tokens, when the provider counts thinking separately.
3. **Whether to see it**: the raw trace, a summary, or nothing.
4. **Replay**: send a previous turn's thinking back so a multi-step tool
   conversation stays valid.

## What the user wants to observe

1. How many tokens went to thinking, separately from the answer.
2. The thinking itself, as a typed part, marked when the provider
   redacted or summarized it.
3. Whatever opaque state the provider needs back on the next turn
   (signatures), carried with the part, never shown as content.

## What must never happen

1. A dial that is set and silently ignored (a budget dropped, an effort
   downgraded to a different level, a summary request that returns
   nothing without saying so).
2. Thinking billed after the user asked for none.
3. Thinking replayed as visible assistant text on a provider that has a
   native form for it.
4. A next turn that fails because state the provider gave us was not
   carried back.
5. The same `Reasoning` meaning a different amount of thinking on two
   providers when both can express that amount.

## Questions the pass must answer with receipts

- Which providers have an effort dial, with which vocabulary, and which
  values does each model accept?
- Which have a token budget, with what floor and ceiling, and does it
  live inside or outside `max_tokens`?
- Which return the trace, a summary, or nothing, and what must be
  replayed?
- What is reported in usage, and is it exact?
- What is incompatible with thinking (temperature, tool choice forcing,
  prefill)?
- Which providers have no off switch, and what happens when you send one?
