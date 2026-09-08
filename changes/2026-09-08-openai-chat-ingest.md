# 2026-09-08 — MAP-12: a Chat Completions request body reads into a canonical Request

Ratification: RATIFIED 2026-09-08 — Maxime Rivest, in session ("i
ratify, go do it in rust and typescript"), after the two design choices
below, the trade-offs and the evidence were put to him. Transcribed.
Drafted the same day in session.

## What this adds

One rule, one op, one direction, one registry, no canonical type change:

1. **`docs/mapping-rules.md` MAP-12.** A Chat Completions request body —
   the JSON object a client POSTs to `/chat/completions` — reads into a
   canonical `Request` under ONE preset's spellings, or refuses with
   `UnsupportedFeatureError` naming the key. Every wire key has exactly
   one verdict: `map`, `extensions`, `refuse`, `call-mode` (`stream`,
   `stream_options` only), or `default` (a value equal to the wire's
   default reads as absent).
2. **`tools/openai-chat-ingest-verdicts.json`.** The verdicts as data, on
   the INV-049 pattern (`tools/extensions-verdicts.json`). `tools/audit.py`
   enforces it two ways: every top-level key, content-block type, tool
   type and `tool_choice` form in any chat-dialect case body has a row,
   and every top-level body parameter the scraped OpenAI reference
   documents (`scrapes/openai/pages/chat--create.md`, 37 parameters) has a
   row. 45 body rows today. A key with no row is refused by the reference
   and is an audit failure in the corpus.
3. **`harness/PROTOCOL.md` op `ingest_openai_chat`** and
   **`--direction ingest`** (`harness/check.py`). The direction runs the
   round trip over every chat-dialect wire case that has a
   `canonical_request` and no build-time refusal — 118 cases across ten
   doors (openai_chat 25, moonshotai 17, azure-chat 13, zai 12, deepseek
   11, bedrock-chat 11, bedrock-mantle-chat 10, meta-chat 10, xai 8,
   openai-chat 1) — plus the ingest-surface cases. `harness/fake_shim.py`
   echoes the direction and `harness/selftest.py` proves two mutations
   are caught (`ingest_drops_config`, `ingest_maps_a_refused_key`).
4. **Lossy cells pinned, not skipped.** 21 of the 118 round trips cannot
   be exact because the WIRE lost information on the way out. Each such
   case now carries `ingest: {lossy: [...], canonical_request: ...}` —
   the class(es) from MAP-12's closed vocabulary and what ingest DOES
   produce. Three classes, all wire-determined:
   - `thinking_as_text` (5 cases: bedrock-mantle-chat.multi_turn_tool_result,
     xai.tool_result_{text,image,mixed,pair}) — `thinking_replay="as_text"`
     folds a ThinkingPart into text; MAP-7 rule 12 forbids reading it back.
   - `tool_result_name_omitted` (14 cases: deepseek, meta-chat, moonshotai
     ×4, openai-chat, zai ×3 `tool_result_*`, and the four xai cases above)
     — `tool_result_name="omit"` drops the result's function name.
   - `leading_developer_as_system` (6 cases: deepseek, moonshotai, zai
     `system_prompt` and `response_format_json_object`) — the builder
     writes `Request.system` and a leading developer Message to the same
     instruction row.
   The audit fails a declaration whose pin equals `canonical_request`.
   The classification was produced by APPLYING each class's transformation
   to the case's `canonical_request` and requiring equality with ingest's
   output — not by eyeballing the diff (`/tmp` script in session; the
   transformations are the three rules as written in MAP-12 rule 7).
5. **38 ingest-surface cases** (`surface: "ingest"`,
   `cases/openai_chat/ingest_*.json`, `cases/groq/ingest_*.json`): foreign
   shapes the builder never writes — content arrays, data-URI images,
   `input_audio`, `file`, `max_tokens` on the OpenAI preset, a bare-string
   `stop`, `logprobs`+`top_logprobs`, the pydantic-derived `json_schema`
   shape, forced `tool_choice`, `parallel_tool_calls` alone, a leading
   `developer` row, a second `system` row, coalescing tool rows,
   `content: null`, `reasoning_content` in history, the extensions keys,
   the stream flag, `safety_identifier`, `reasoning_effort: none`, a
   breakpoint on a user message, Groq's builtin tool and
   `reasoning_format` door, and the EXACT bodies DSPy's `ChatAdapter`
   produces (text and image) — plus 10 pinned refusals (`n`, `functions`,
   a message `name`, a `custom` tool, `strict: true`, `top_k`, a foreign
   `thinking` spelling, `web_search_options`, an unknown content block,
   `prompt_cache_key` on a preset without cache control). The expected
   canonical request of every case was written by hand and the reference
   was then required to agree (the authoring script stops on any
   disagreement); none was echoed from the implementation. Provenance:
   `hand-authored`, evidence naming this entry and the scraped reference.
6. **`playbooks/api-family.md`** row: `request_from_openai_chat(body,
   compat)` in four languages, plus the method form on the chat adapter.
   **`playbooks/port.md`** module 4b (does not gate 1.0). **`spec/SCOPE.md`**
   PROVISIONAL bullet.
7. **The reference** (`lm15-python`, same-day commit): the decoder lives in
   `lm15/providers/openai_chat.py` directly under the encoders it inverts
   (`_chat_content_parts`, `_response_format_to_chat`, `_build_messages`,
   `_payload`), exported as `lm15.request_from_openai_chat`; the vet op;
   unit tests for the malformed-input class the contract does not pin.

## The two design choices put to the maintainer

**A. Three verdict buckets, decided by a registry file.** `map` /
`extensions` / `refuse` (plus the two closed helpers `call-mode` and
`default`). The alternative — strict-by-default, refuse everything not
mapped — was rejected because `config.extensions` is ALREADY the contract's
documented door for provider syntax the canonical model does not express
(INV-049; port.md rule 4 "a raise or a documented `extensions` door, never
omission"), and because the builder re-emits extensions verbatim, which is
what makes those keys round-trip. The other alternative — put every
unknown key in extensions — was rejected because `n: 2` in extensions
would reach the server, produce two choices, and lm15 would silently read
one: exactly the silent loss the rule exists to prevent. A key nobody
decided about is therefore refused, and the registry is what makes
"nobody decided" a checkable state.

**B. Ingest takes a preset.** The function reads the spellings of one
compat policy — the one the builder writes with — so `ingest(build(r,
p), p) == r` is a well-defined property checkable on all 118 recorded
bodies, and a body carrying another server's spelling is refused instead
of forwarded to a server that ignores it. The alternative — accept every
preset's spelling at once — makes the round trip undefined (two spellings
of one knob in one body collide silently) and turns the function into a
guess about which server the body was meant for.

## Trade-offs, stated

- **`[error] ` and `<think>` are not reversed.** A transcript exported
  from litellm in which a tool result begins with `[error] ` reads back
  with `is_error=false`. That is a real loss for that migrator. Reversing
  a prose marker is a guess, and MAP-7 rule 12 already forbids parsing
  delimiters out of text in the other direction; one rule, both ways.
- **A leading developer message reads as `Request.system`.** The wire has
  one instruction row for both; a caller who authored `Message.developer`
  first and reads their own body back gets `system`. Same bytes on the
  wire; stated as a lossy class.
- **Consecutive tool rows coalesce into one tool Message.** A canonical
  transcript with two one-result tool Messages in a row reads back as one
  two-result Message. The flagship `Message.tool({id: out, ...})` shape
  produces exactly the coalesced form, and the builder emits identical
  bytes for both; the corpus holds no case of the other shape. Stated.
- **`strict: true` on a tool is refused, `strict: false` is dropped.**
  Refusing `false` would refuse what the OpenAI SDK emits by default for
  every tool; dropping `true` would lose an enforcement the caller asked
  for. The asymmetry is the wire's: `false` is the default.
- **`input_audio` reads in although no chat preset can send it back
  out.** The Request is faithful; the send raises (MAP-10). The
  alternative — refuse at ingest — would hide a builder gap behind a
  converter refusal and make the converter's behaviour depend on which
  preset happens to be missing a mapping today.
- **`stream` / `stream_options` are dropped.** Twenty of the 118 recorded
  bodies are streaming captures; refusing them would refuse every recorded
  stream. The keys describe the call, not the request, and the adapter
  sets them from its own compat when it streams. This is the only drop
  MAP-12 makes and the bucket is closed at these two keys.
- **A `json_schema.name` of exactly `"response"` reads as absent.** It is
  the builder's default label; a user who chose that name loses nothing
  the wire can see. Without this the 11 `structured_output` round trips
  would all be lossy for a label.
- **`Response → chat response dict` (serving / proxy use) is deferred**
  to its own row. DSPy parses `Response` directly; nothing on the
  deadline needs it.
- **The scrape is the reference's own documentation, not a live
  receipt.** MAP-12 is a canonical fact (how JSON reads into types), not
  a wire fact; the design-pass steps that capture live behaviour (3–5)
  do not apply. The 118 recorded bodies ARE live captures, and the round
  trip over them is the evidence that the decoder inverts what real
  servers accepted.

## Considered and rejected

- A `Request.from_openai_chat(...)` classmethod: discoverable, but it
  makes the canonical type know a vendor format (api-family rule 3;
  THEORY §3.10). Module function in the dialect, method on the adapter.
- A `(model, messages, **kwargs)` signature (DSPy's `from_call` shape):
  one shape per language is the family rule; a body object is what every
  port can take (`serde_json::Value`, `map[string]any`). DSPy builds the
  dict in one line.
- A DSPy-private converter instead of a contract rule: it would have been
  faster this week and would have left every other litellm migrator to
  write their own, each deciding `n` and `name` silently. The corpus was
  already there; the rule cost a day.
- Separate lossy-case skip list: a skip is a hole. A pin of what ingest
  produces is a fact the harness checks, and the audit's staleness rule
  means a builder improvement that makes a cell exact is noticed.
- Reading every preset's spellings at once (see choice B).

## What ports do

Rust (contract-complete at the previous pin) gains one unstarted direction:
at the new pin `--direction ingest` reports its 156 cases red (the shim
answers "unknown op") until the port implements it, and the port's README
states the direction as not started meanwhile (port.md rule 6 — the
harness has no per-port skip list, deliberately). The Rust release shim
was not built on this machine during the session, so its ingest result was
not observed here; the statement above is what the harness does with an
unknown op. The verdict registry is data (rule 2): port it as data. The exhaustive `match` on the
wire block `type` with an explicit refuse arm is where Rust's compiler
catches a missing verdict — the review should run
`tools/differential.py` extended with the DSPy adapter bodies through
both shims. TypeScript picks the module up in its order (module 4b sits
beside module 4). Go and Julia when they reach module 4.

## Evidence

- `python3 harness/check.py --shim python --direction ingest --no-check-pin`:
  156 pass, 0 fail, 0 skip (118 round trips + 38 ingest-surface).
- `python3 harness/selftest.py`: baseline green in every direction
  including `ingest`; 39 mutations caught (37 before + 2).
- `python3 tools/audit.py`: OK — the first run of the new check caught a
  missing verdict for a content-block type in a case the same session
  authored (`video_url`), which is the check doing its job; the row was
  added with its reason.
- `tools/check_provenance.py`, `tools/check_secrecy.py`,
  `tools/check_content_coverage.py`: OK.
- The reference's full pytest suite and the other harness directions:
  green (recorded in the lm15-python commit).

## What ratification covers

MAP-12 as written (rules 1–8), the verdict registry as the enforced
source of "decided", the three lossy classes, and the `ingest` op and
direction. `lm15-python/CONTRACT_PIN` moves to the ratified commit; the
Rust and TypeScript ports implement module 4b next; the DSPy typed-LM
branch may depend on the pinned function.
