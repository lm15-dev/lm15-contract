# Tool-result content — frame

The yardstick for this pass. No provider words.

## What the caller controls

A tool ran on the caller's side. The caller hands its output back to the
model as one `ToolResultPart`:

- `id` — which call this answers (the model's own id, echoed).
- `content` — an ordered list of presentational parts: text, images,
  documents, audio, video, binary (INV-013 forbids only protocol parts:
  tool calls, tool results, thinking, refusals). INV-014: never empty.
- `is_error` — the tool failed; the content is the failure, not a result.
- `name` — the tool's name, optional (the id already identifies the call).

The caller uses the same value for every provider. That is the whole
promise of the type.

## What the caller observes

The next response. The caller cannot see the wire. They can only judge
whether the model behaved as if it had received what the tool returned.

## What must never happen

1. **Silent loss.** A part the caller put in `content` is not on the wire,
   and no error was raised. The model answers as if the tool returned less
   than it did. The caller pays for that answer.
2. **Silent substitution.** A part is replaced by something that is not
   the part: a caption, a type name, a placeholder, base64 as prose.
3. **Silent degrade with 200.** The wire carried the bytes, the server
   accepted the request, and the model still did not receive the content
   (it saw a marker such as `[Unsupported Image]`). From the caller's seat
   this is identical to (1).
4. **Lost association.** Two results, two calls, and the model receives
   them under the wrong ids, or under none.
5. **Lost status.** `is_error=true` reaches the model as an ordinary
   result; the model treats a failure as data.
6. **Invented facts.** A function name the caller never gave, an id that
   does not match, a synthetic assistant turn built to make a replay fit.
7. **A refusal where the wire has a slot.** Raising on content a provider
   accepts natively is not safety; it is a missing mapping.

## What is allowed

- A different wire *shape* for the same content (nested parts, a reference
  from a structured field to an attachment, a content array where another
  server takes a string) — provided every part, its order, its status and
  its call id survive.
- Raising `UnsupportedFeatureError` **before any wire** when a part has no
  faithful slot on this provider/model. The message names the part kind,
  the provider, and the door that carries it.
- Text-only rendering of a *text-only* result. That is not lossy.

## The three questions this pass keeps apart

1. Can lm15 encode the part faithfully on this wire? (a mapping question:
   answered from the provider's documented request schema)
2. Does this provider/model accept and *use* that encoding? (a live
   question: answered by a receipt whose oracle is hidden from the prompt)
3. Did the model solve the task well? (not lm15's promise; a model
   quality question, recorded but never a verdict on the mapping)

A verdict on (1) or (2) never rests on (3).

## Out of scope

Server-executed tools (their results never pass through the caller),
generated media in *responses* (MAP-1 already covers parts the
application must act on), and live/realtime tool results
(`LiveClientToolResultEvent`, same rule, separate wire; noted, not run).
