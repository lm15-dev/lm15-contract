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

## Addendum, same session: message objects dumped back into history

The first real chat loop tried against ingest failed: every loop appends
`response.choices[0].message` — a pydantic object — to `messages`, and
its `model_dump()` carries `annotations: []`, `audio: null`,
`function_call: null`, `refusal: null` (OpenAI SDK 2.x) or
`provider_specific_fields: {"refusal": null}` (litellm). Ingest refused
the row on `annotations`. Five verdict rows added
(`tools/openai-chat-ingest-verdicts.json` § messages_rows):

- `assistant.annotations` → **map**: OpenAI's `url_citation` entries
  become `CitationPart(url, title, text = the content span)`; an empty
  list is nothing.
- `assistant.provider_specific_fields`, `thinking_blocks`, `images` →
  **default**: litellm's object model, not the wire; null / empty reads
  as absent, non-empty is refused with the key named.
- null-valued keys read as absent everywhere (already the reference's
  behaviour; now stated).

Four ingest-surface cases pin it: the SDK's and litellm's dumped
message objects verbatim (captured 2026-09-08), a non-empty
`url_citation`, and litellm's `provider_specific_fields` carrying a
refusal string (refused). `--direction ingest`: 160 / 0.

**Finding, not decided here:** the chat BUILDER silently drops a
`CitationPart` on an assistant history row (`_build_messages` renders
text, refusal and thinking only; the request wire has no `annotations`
slot). That is a MAP-10-class cell — a part that reaches no wire and
raises nothing — that predates this entry and now becomes reachable
from a real input. Options are raise (MAP-10 rule 1 as written), or
state citations as presentation-only on replay (as `Response.text`
already treats them). The maintainer decides; a probe case should pin
whichever.

## Addendum 2, same session: `complete_from_openai_chat` — the other libraries' call, as-is

The maintainer asked whether `router.complete(model=..., messages=...,
max_completion_tokens=...)` could be made to work. Overloading `complete`
was rejected (one method, two meanings of `messages`); a named method
was chosen, and it takes both libraries' model strings as written. The
api-family page gains the row and the stated exception to rule 3. Design:

- `openai_chat_model_string`: lm15 `provider:model` as-is; litellm
  `provider/model` via `LITELLM_PROVIDER_PREFIXES` (data: openai →
  openai-chat, anthropic, gemini, groq, openrouter, deepseek, xai,
  ollama, ollama_chat, hosted_vllm → vllm, moonshot → moonshotai,
  azure → azure-chat); only the first segment is the provider
  (`groq/openai/gpt-oss-20b`); an unlisted prefix, or one litellm maps
  to two lm15 doors (`bedrock/`, `vertex_ai/`), is `UnknownModelError`
  naming it — never routed by rule. A bare name goes by the router's
  rules, except an OpenAI model takes the `openai-chat` door.
- The body is read with the DESTINATION door's compat when it speaks
  the chat wire (`deepseek/…` reads `thinking`), else OpenAI's.
- Client keywords are refused with the `RouterConfig` place named;
  `stream=True` refused on `complete_from_...` (`stream_from_...` exists).

Trade-offs stated: the same bare `gpt-4o-mini` reaches a different door
through this method than through `router.complete` (Chat vs Responses)
— deliberate, documented, visible on `lm.provider`; the litellm prefix
table is data that rots as litellm adds providers (unknown → refused).
Verified live 2026-09-08 through all four doors (OpenAI chat, Anthropic,
Gemini, Groq streamed) with strings exactly as the two libraries write
them. Ports follow the row. The general router's `/` refusal stands.

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
