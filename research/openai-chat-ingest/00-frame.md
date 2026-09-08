# Frame — reading a Chat Completions request into lm15

Drafted 2026-09-08. No provider words in this page on purpose
(`playbooks/design-pass.md` step 1).

## The user

Someone who already has requests in the one format most tools speak: a
JSON object with a model name, a list of role/content rows, maybe tools
and a few generation knobs. They hold it because a framework built it, a
log recorded it, or a previous client library expected it. They want the
same request as an lm15 `Request`, so the rest of lm15 (routing, typed
parts, every provider) applies to it.

## What they control

- The body: the object they already have.
- Which server dialect the body was written for (a preset name), because
  several servers spell the same knob differently and lm15 refuses to
  guess which server a body was meant for.

## What they observe

- Exactly one of: a `Request`, or an error that names the key or block
  lm15 could not carry and says where that thing belongs instead.
- For a `Request` that lm15's own adapter had written from a canonical
  request, the SAME canonical request back — except where the wire itself
  had no place for a piece of information, and then the loss is named.

## What must never happen

- A key silently dropped. If the body asked for something, the `Request`
  carries it, or the user is told it was not carried.
- A knob forwarded to a server that ignores it. (This is why a foreign
  spelling is refused rather than passed through.)
- A guess: about which tool a nameless call meant, about whether a text
  prefix was an error flag, about which server a body was for.
- A second public way to say something the canonical types already say.
  The result is a plain `Request`; nothing is hidden behind the converter.

## Yardstick

A converter passes if a person can predict, from the verdict table alone,
what any body reads into, and if every body lm15's own adapter has ever
written reads back into the request it was written from, or into a request
whose difference is named in a closed list.
