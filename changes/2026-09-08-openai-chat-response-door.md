# 2026-09-08 — MAP-12 rule 9: `response_from_openai_chat`, and one choice per Response

Ratification: PENDING — drafted 2026-09-08 in session (Maxime Rivest
directing: "go do the python and contract side"). Additive to the ratified
MAP-12 (`changes/2026-09-08-openai-chat-ingest.md`), plus one behaviour
change on an existing path, stated below.

## What this adds

1. **`response_from_openai_chat(body, model=None, choice=None)`** in the
   api family (four languages): a Chat Completions *response* body read
   into a canonical `Response`. It is `OpenAIChatLM.parse_response`'s
   reader exposed as a module function and as a method on the chat
   adapter (sync and async mirrors). No new verdict registry, no new op,
   no new direction: the `response` direction already pins what the
   reader maps and what it records as unmapped over every recorded chat
   body, and the reference's tests require the door and `parse_response`
   to agree byte for byte on each of them (99 bodies today, plus the one
   pinned MAP-9 refusal, which both refuse alike).
2. **MAP-12 rule 9** with the door's three rules: the whole body is
   `provider_data` (a key the reader does not know is neither refused
   nor lost — the response side has had its oracle, `_lm15_unmapped`,
   since June); `model` fills a body that carries none; several choices
   refuse unless `choice` names one.
3. Two litellm `ModelResponse.model_dump()` bodies captured live
   (`lm15-python/tests/fixtures/litellm_responses.json`: Gemini 3.8 with
   litellm's `thinking_blocks` / `thought_signatures` extras; gpt-4o-mini
   with a forced tool call and `n=2`) as the reference's fixtures — the
   consumer's actual input, not a retyped shape.

## The behaviour change, stated

`OpenAIChatLM.parse_response` now REFUSES a body with more than one
choice (`UnsupportedFeatureError`). Before, it read `choices[0]` and
dropped the rest. lm15 never sends `n`, so provider traffic never has
several choices — except when a caller smuggled `n` through
`config.extensions`, in which case the other choices were paid for and
silently lost. That is the loss MAP-12 rule 2 refuses on the request
side; refusing it on the read side is the same rule. No recorded body
in the corpus carries several choices; `--direction response` and
`--direction stream` are unchanged (302 / 0, 40 / 0).

## Considered and rejected

- **A verdict registry for response keys**, as the request side has. The
  request side needed one because reading a caller's body was new
  territory with no oracle. Response reading has had an oracle for three
  months: the unmapped recorder, failed by the harness on any recorded
  body, and goldens for 302 of them. A per-key JSON here would duplicate
  a stronger check with a weaker one.
- **A `compat` parameter for symmetry.** The reader consults no compat;
  a parameter with no effect would misdescribe the function. The
  method form carries the adapter's provider name into errors, which is
  the only server-specific thing on this path.
- **A list-returning variant for `n`.** `Response` is one message by
  contract (types.md); the caller reads each choice by index. Usage is
  reported once for all choices by the wire, so each `Response` carries
  the same `Usage` — stated in the reference test.
- **Reading streaming chunks.** A different reader (`parse_stream_events`
  over SSE events); nothing on the DSPy path needs it yet. Its own row
  when it does.

## What ports do

Expose the existing `parse_response` reader under the family name with
`model` and `choice`, and apply the multi-choice refusal in
`parse_response` too. No fixtures change; the reference test's
door-equals-parse_response property is the port's test to copy.

## Evidence

- `python3 harness/check.py --shim python --direction response` 302 / 0;
  `--direction stream` 40 / 0 after the refactor (behaviour-preserving
  on every recorded body).
- lm15-python: 1728 tests pass (103 new: the two litellm bodies, the
  choice rule on the `n=2` body, the model fallback, the error envelope,
  and the 99-body door-equals-parse_response property).
