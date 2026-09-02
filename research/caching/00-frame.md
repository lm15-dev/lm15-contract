# Caching — the frame (no provider words)

## What the user is trying to do

Send the same beginning of a conversation many times (a system prompt, a
tool set, a document, the history so far) and not pay full price or full
latency for it each time.

## What the user wants to control

1. **Whether** reuse is attempted at all.
2. **Where** the reusable part ends, when the provider needs to be told.
3. **How long** the reusable state should live, when the provider offers
   a choice.
4. **Which** stored state to reuse, when reuse is by name.

## What the user wants to observe

1. How many tokens were read from cache, how many were written.
2. What that cost (rates differ for write, read, and storage).
3. Whether a request created something that outlives the request.

## What must never happen

1. Money spent on cache state the user did not ask for.
2. A request that silently does a second network call.
3. State created outside the request that the user cannot list or delete.
4. A control that is set and silently ignored.
5. A boundary moved silently to make a request valid.
6. The same `CacheConfig` meaning different tiers on different providers.

## Questions the pass must answer with receipts

- Which providers cache without being asked, and is it reliable?
- Which need a marker, and where may the marker go (which block types)?
- Which need a stored resource, with what lifetime and storage price?
- What are the minimums below which nothing is cached, per model?
- What does the response report, and is it reported when nothing hit?
- Does a cached prefix survive a model change, a tool-set change, a
  system-prompt change, a second process?
- What does a cache write cost versus a read, per provider?
