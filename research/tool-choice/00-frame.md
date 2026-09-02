# Tool choice — the frame (no provider words)

## What the user is trying to do
Offer the model a set of tools and decide how strongly it must use them:
not at all, if it wants, at least one, exactly this one, one of these.
Decide whether several calls may come back at once.

## What the user wants to control
1. The mode: none / auto / required.
2. A restriction: only these names (one or several).
3. Parallelism: may the model return several calls in one turn.
4. The same for provider-executed tools (search, code) where the wire allows.

## What the user wants to observe
1. Which tool was called, with parsed arguments, in order.
2. Why the turn ended: a tool call, or text.
3. That a forced call happened when it was forced.

## What must never happen
1. A restriction that silently widens (a subset that becomes "any").
2. A forced call that silently becomes optional.
3. A parallel preference silently ignored when the wire has the knob.
4. A tool result the model cannot match to its call.
5. The same ToolChoice meaning different things on two providers that both express it.

## Questions
- Which modes and restriction shapes does each wire have, and for which tool kinds?
- Does "required" guarantee a call, and what stop reason comes back?
- Does parallel=false hold, and where is it silently ignored?
- Can a forced tool coexist with thinking, structured output, streaming?
- What does a call id look like and must it be echoed verbatim?
