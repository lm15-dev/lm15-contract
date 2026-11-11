# 2026-11-11 — A part with nothing for a wire writes nothing (MAP-24; MAP-7 rule 8 amended)

**Status: DECISION (maintainer, in session 2026-11-11: "Okay, so let's
build it", on the plan below after reading it) + normative rule MAP-24,
the amended MAP-7 rule 8, notes on MAP-2, MAP-10 rule 1 and MAP-12 rule 7
in `docs/mapping-rules.md`, notes on `spec/types.md` ThinkingPart and
`spec/invariants.md` INV-015; to ratify. Wire evidence: live receipts
below. Issue: lm15-contract #3.**

## The finding

A production application (a tool-calling agent, `@lm15/lm15` 2.2.0,
reasoning effort medium) ran a conversation on `gpt-6-astra` (OpenAI
Responses) and was then pointed at Claude. Every later request in that
conversation failed in half a second, nothing billed:

```
InvalidRequestError: messages: text content blocks must be non-empty
```

The history is stored, so every retry sent the same body. The
conversation was stuck until the history was deleted.

Cause. A Responses reasoning item with no summary is read as
`ThinkingPart(text="", continuation=[openai:reasoning_item {...}])` (MAP-7
rules 9 and 11; correct, and unchanged). MAP-7 rule 8 said: "Without
state, a `ThinkingPart` is replayed as assistant text on every provider".
The Messages builder found no Anthropic state on the part, took it to be
"without state", and wrote its text, which is empty, as
`{"type": "text", "text": ""}`. The rule did not say what "as text" means
when there is no text, nor that another dialect's state counts as none.

It was wider than the report:

- **Not one part kind.** lm15 makes an empty `TextPart` on purpose (MAP-2:
  a reply with no parts; MAP-12: an assistant row with null content). The
  Messages builder wrote that as an empty block too, and a `CitationPart`
  with a URL and no quoted text as well.
- **Not one wire.** The generateContent builder wrote `{"text": ""}` for
  the same parts; the Chat Completions builder wrote an assistant row
  with `content: null` and no call for a message holding only hidden
  thinking, and `content: ""` for an empty text part; the Responses
  builder wrote `{"type": "output_text", "text": ""}` for an empty text
  part (it already skipped empty thinking).
- **Not one server.** See the receipts: Moonshot refuses an empty text
  block on its Messages, Responses and Chat Completions doors; DeepSeek
  and Moonshot refuse an assistant row with nothing in it; Gemini refuses
  a content with no parts.
- **Not caught.** Every SDK passed 2,266 of 2,266 contract checks. No
  case sent one dialect's reply into another dialect's history. lm15-rs
  already left the empty thinking part out (a comment in
  `src/dialects/anthropic/parts.rs` says why); the other five followed
  the reference. The SDKs disagreed on the wire and the corpus could not
  see it.

## What the providers do (`receipts/2026-11-11-empty-parts/`, `research/empty-parts/`)

`research/providers/empty_parts.py --probe`: 18 histories (and six that
only one wire has), written by hand in each dialect's spelling and
swapped into a body the reference built, on 14 server and model pairs:
Anthropic (Haiku 4.5, Opus 5.5), DeepSeek's and Moonshot's Messages
doors, Gemini 2.5 Flash and 3.7 Flash on Vertex, the Codex sign-in
(Responses, GPT-5.6 Luna), Moonshot's Responses door, and Chat
Completions on Groq, DeepSeek, Moonshot, Z.AI, Parasail and OpenRouter
(OpenAI's GPT-4.1 mini behind it). The full table is
`research/empty-parts/README.md`. What decides the rule:

| Shape | Accepted | Refused (HTTP 400) |
|---|---|---|
| An empty text block beside a tool call or text, in an assistant message | 10 | Anthropic ×2, Moonshot Messages, Moonshot Responses; as the only block also Moonshot Chat |
| The same in a user message | 9 | the same four, and Moonshot Chat |
| An assistant message with zero blocks | 9 | DeepSeek Messages, Moonshot Responses, Moonshot Chat, Vertex ×2 |
| An assistant Chat row, `content: null`, no call (6 chat doors) | 4 | DeepSeek, Moonshot |
| That message left out: two user messages in a row | 14 | none |
| Two assistant messages in a row | 14 | none |
| A conversation starting with an assistant message | 14 | none |
| A tool result whose output is `""` | 14 | none |
| A tool result whose block list holds an empty text block (Messages) | 3 | Moonshot Messages |
| An empty system prompt | 13 (on the Messages wire: the string form) | Moonshot Chat; the block form of the Messages wire: Anthropic ×2 and Moonshot |
| Text that is only whitespace, as a message's only text | 12 | Anthropic ×2 |
| A request with no message at all | 1 (Parasail) | 13, each naming the missing input ("at least one message is required", "messages must not be empty", "Empty input messages", ...) |
| A system prompt and no message | 7 (Chat Completions servers, Moonshot's three doors) | 7 (Anthropic ×2, DeepSeek Messages, Vertex ×2, Codex, Z.AI) |

Anthropic's reference states the same (`scrapes/anthropic/pages/messages--create.md`):
`TextBlockParam.text` has `minLength: 1`, and "Consecutive `user` or
`assistant` turns in your request will be combined into a single turn".

`--replay`: ten recorded replies (goldens) placed in a history, built by
the reference with MAP-24 applied, sent to the same 14 (196 requests).
Hidden Responses reasoning before a call and before text, a reply cut
during reasoning, an empty reply and citations all reached every other
dialect's servers with HTTP 200. What was still refused is listed under
"Not decided".

Not probed, stated: api.openai.com, the Gemini API, Together, Fireworks,
DeepInfra and Cerebras answered 402/429 "no credits" on 2026-11-11.
OpenAI's Responses dialect was reached through the Codex sign-in
(chatgpt.com, a different server from api.openai.com that speaks the same
dialect and takes the same builder), the Gemini wire through Vertex,
OpenAI's Chat Completions models only through OpenRouter. No receipt from
api.openai.com or generativelanguage.googleapis.com backs this change;
on those two wires the rule only removes bytes (an empty block, an empty
message), and the shapes it leaves are the ones their existing cases
pin.

## Decided

**MAP-24** (`docs/mapping-rules.md`), six rules:

1. A part writes its state or its content; with neither it writes
   nothing. No wire is sent a text block with no characters. The wire is
   exactly the one built without that part.
2. State of another dialect is not state here. A history that changed
   model is an ordinary input.
3. A message left with nothing to write is not written. Order kept, no
   filler, no role repair. A message index the caller gave still names
   the caller's message.
4. A tool result is always written; an empty output is the empty string.
5. Nothing is recorded, and the canonical history is not touched.
6. Every recorded reply is also a history: the harness builds each
   golden into every dialect.

**MAP-7 rule 8**, amended: "state is present" means state of the dialect
being written.

### Why each choice, and what was rejected

- **Write nothing, rather than a placeholder.** `"(hidden reasoning)"`
  or a single space would be lm15 writing model input nobody wrote; MAP-7
  rule 11 already refused placeholder text for the same part on the way
  in.
- **Write nothing, rather than refuse.** A typed refusal before the wire
  leaves the conversation exactly as stuck as the provider's 400, one
  layer earlier. MAP-13 rule 4 allows a refusal when a real choice is
  needed, the program depends on the thing, or a wrong guess costs
  money or data; none holds: the next model could never have read the
  part.
- **No `Adaptation` record.** MAP-13 records what the wire got instead of
  what was asked. Here nothing the caller or a model wrote is withheld:
  the part has no characters, and its state is addressed to another
  provider. Recording it would put a note on every request of every
  conversation that ever changed model, and under `adaptations="refuse"`
  would bring the stuck conversation back. Decision G (thinking with text
  replayed as assistant text) is not recorded either; this is the same
  kind of translation.
- **Every wire, not only the servers that refuse.** As MAP-17 chose for
  an absent tool description: tolerance is not contract. A per-server
  list would have to be probed again for every OpenAI-compatible host,
  and Moonshot is the proof (it shares three builders with servers that
  accept the empty block).
- **Leave the message out, rather than send it empty.** A wire's spelling
  of an empty message is refused by three vendors; leaving it out is
  accepted by all 14, and Anthropic documents what happens to the two
  turns of one role that result. Rejected: writing a filler assistant
  turn to keep roles alternating. No probed server needs alternation,
  and the filler would be invented content. Stated risk: a
  Chat-Completions-compatible server whose chat template requires strict
  alternation (some local templates do) will refuse two user messages in
  a row with its own error; before this change it received an assistant
  row with `content: ""` or `null` instead. None was reachable to probe.
- **The rule as an equivalence.** "The wire equals the wire without that
  part" decides every corner without a new sentence: no joining newline,
  no array form for a lone text, no `[developer]` prefix alone, and it is
  checked by building both requests.
- **Tool results stay.** An empty output is the tool's answer and keeps
  its call paired (INV-014). All 14 accepted the empty string.
- **Thinking and text, one rule.** The report was about thinking; the
  same block came from an empty `TextPart`, which lm15 also makes on
  purpose. Fixing one would have left the other for the next report.
- **A request with nothing to send is sent as it is.** Considered: a
  typed refusal before the wire. Every server but one already refuses an
  empty message list in its own words, and a system prompt with no
  message is a request half of them answer; lm15 has no reason to forbid
  it. Stated cost: a request whose ONLY message is empty text was
  answered by 6 of the 14 servers before this change (it reached them as
  `content: ""` or an empty block) and is now refused by 13, because it
  reaches them as no message.

### Not decided (each with its receipts; follow-up issues filed)

1. **Whitespace-only text.** Anthropic's own door refuses a message whose
   only text is whitespace. Leaving it out withholds characters, so it
   would be a recorded adaptation. Not seen in production.
2. **State of the same dialect from another server.** Anthropic refused a
   signature from DeepSeek's Messages door (`Invalid signature in thinking
   block`) and a redacted block from Meta's (`Invalid data in
   redacted_thinking block`); the Codex door refused reasoning items from
   Azure and Meta; Gemini 3.7 on Vertex refused a signature recorded on
   the Gemini API. MAP-7 rule 8 (D7) says the server judges; these are
   its judgments, and each is a stuck conversation of the same kind as
   the one fixed here. The builder cannot tell the issuer: a
   `ContinuationState` names its dialect only.
3. **A turn in progress moved to another provider.** Gemini 3.x refuses a
   current-turn function call without its `thoughtSignature` (Google
   documents the placeholder `skip_thought_signature_validator` for
   history from another model; receipt: accepted); DeepSeek's Messages
   door refuses a current turn without its thinking. Claude answers (its
   reference says thinking is switched off for that request).
4. **What a citation in a history should be.** Pinned now: such a
   history builds on every wire, and a citation quoting nothing writes
   nothing. Left as the reference has it: two builders write no citation,
   two write its quoted text as assistant text.
5. **A cache mark asked for on a message that writes nothing.** Pinned:
   a mark on a message AFTER a left-out one stays on the caller's
   message. Not pinned: the index naming the left-out message itself
   (the reference marks the last message written before it on the
   Messages wire; the OpenAI wires refuse a mark on a message with no
   text block, as before).

Found on the way, not part of this change: a refresh of the scrapes on
2026-11-11 shows three request parameters the reference's doc-drift check
does not know (`access_programs` on Responses; `diagnostics` and `speed`
on Messages) and one dead URL in `scrapes/gemini/update.sh`
(`batch-mode.md`). The refresh was not committed: it would turn the
reference's drift check red until each is classified.

## Fixtures

- `mapping/empty-parts.json`: 17 hand-written vectors, 72 checks
  (`tools/make_empty_parts_vectors.py`). The report's history, the same
  with no state, a message whose only part is hidden, own-dialect state
  kept (Claude's omitted thinking and redacted thinking; Gemini's
  signatures on empty parts), state with no value, empty text in each
  role, a citation with no text, empty system and developer text, tool
  results, an assistant data part (content, never empty), a request with
  nothing to send, a cache index after a left-out message; the Chat
  preset that writes `reasoning_content` on every row (deepseek) and the
  Messages preset that replays unsigned thinking (moonshotai-anthropic).
- History replay: every golden with a message (477 on 2026-11-11) in the
  four dialects, 1,908 checks, no hand-written answers
  (`mapping/history-replay.json`). Run against the reference at 2.3.0
  (`af6ebbc`) it fails 87 checks over 58 recorded replies (gemini 42,
  anthropic 24, openai_chat 20, openai 1), and `empty-parts` fails 55 of
  72.
- Ten live cases, wire built by the fixed reference, each HTTP 200
  (`research/providers/empty_parts.py --capture`):
  `anthropic.foreign_reasoning_history` (the report, Opus 5.5, thinking
  on), `anthropic.empty_message_history`, `anthropic.empty_text_history`
  (Haiku 4.5), `anthropic.omitted_thinking_replay` (turn 1 run live;
  Claude's own empty thinking block goes back with its signature while
  the tool result is returned), `vertex.foreign_reasoning_history`,
  `vertex.empty_message_history`, `deepseek.foreign_reasoning_history`,
  `deepseek.empty_message_history`, `moonshotai.empty_text_history`,
  `moonshotai-responses.empty_text_history`. The hidden reasoning item in
  them is the first part of `goldens/azure/reasoning_high.json`: a real
  one. Goldens are scribe drafts, not reviewed.
- MAP-12 lossy class `nothing_written` (the three Chat cases read back
  without what was not written); `tools/openai-chat-ingest-verdicts.json`.
- Harness: `empty_wire_findings`, the two runners, four mutations in the
  self-test (63 caught). `harness/PROTOCOL.md` § The `mapping` direction.

Checks: 2,266 → 4,269 (request +10, response +10, ingest +3, mapping
+1,980).

## Implementations

Each SDK moves its pin to this commit with the rule: Python (reference),
TypeScript, Rust, Go, Julia, R. The parity ledger (`playbooks/parity.md`)
has the commits.

### What the new checks found in the SDKs

The new checks were run against each SDK as released (2.3.0) before it
was changed, and every one failed some: the reference 55 of the 72 vector
checks and 87 of the 1,908 replays (above); the other five between about
100 and 175 checks each while the fixtures were being written (the
numbers moved with the vector set and were not re-measured at the end).
Beyond the empty block itself:

- **Rust** already left hidden thinking of another dialect out of the
  Messages wire, and then wrote the message with `content: []`, which
  three vendors refuse.
- **Julia and R refused an assistant citation** on the Responses and Chat
  Completions wires (`UnsupportedFeatureError`), where the reference and
  the three other SDKs write nothing for it: a reply with citations, as
  lm15 reads one from web search, could not be sent back to OpenAI at
  all. Both now follow the reference.
- **An assistant data part on the two OpenAI wires.**
  `changes/2026-09-19-jev-state.md` D3 says an assistant data part "renders
  the same way" as a user one (its compact JSON on a text slot). On the
  Responses and Chat Completions wires Python, TypeScript and Go dropped
  it without a word, Julia refused it, and Rust and R wrote it. All six
  write it now; the vector `assistant-data-part-is-content` pins it. No
  new rule: D3, implemented where it was not.
- **Rust, Julia and R wrote a citation in an assistant message** on the
  Messages and generateContent wires as `title — url — text`; the
  reference writes the text it quotes. They follow the reference now
  (AUTHORITY.md: no rule or fixture said otherwise).
- **R sent a thinking part whose signature is the empty string** as a
  signed thinking block; the other five treat an empty signature as no
  state. Pinned by the vector `state-with-no-value`.

## Spend

About 490 probe and replay requests and 12 captures, most under 500
tokens in and 50 out: well under one US dollar by the usage fields.
