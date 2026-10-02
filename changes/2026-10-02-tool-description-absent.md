# 2026-10-02 — A tool with no description is left off the wire (MAP-17)

**Status: DECISION (maintainer, in session 2026-10-02: "yes, do it fully")
+ normative rule MAP-17 and a note on `spec/types.md` FunctionTool, not
yet ratified. Wire evidence: live receipts below.**

## The finding

A user reported that a function tool with no description made Anthropic
refuse the request, from both lm15-python and LM15.jl; they had worked
around it by adding a description in their own live check.

Every SDK built the same wire for such a tool: Anthropic
`{"name": ..., "description": null, "input_schema": ...}`, and the same
`null` on every other dialect (Responses, Chat Completions,
`functionDeclarations`, Realtime `session.update`). None of it was a
decision. The reference wrote `"description": tool.description`; the
ports copied it (lm15-rs said so in a comment: "sent as `null` when
absent, as the reference does"). The corpus never caught it because
every tool in every case had a description: no case exercised the cell.

The canonical side was already right: `spec/types.md` marks
`FunctionTool.description` optional and omit-empty, and the MAP-12
ingest reads a Chat Completions `"description": null` as absent. The gap
was only on the way out, and it turned a valid canonical request into a
400 on the providers that check the type.

## What the providers do (receipts/2026-10-02-tool-description)

`research/providers/tool_description_absent.py --probe` built one
request through the reference adapter (a `get_weather` tool with a name
and a schema, no description) and sent it twice per wire: description
`null`, and description key left out. Raw-patched only in that one key.

| Wire | Model | `null` | key left out |
|---|---|---|---|
| anthropic | claude-haiku-4-5 | **400** `tools.0.custom.description: Input should be a valid string` | 200, tool call |
| groq (Chat Completions) | openai/gpt-oss-20b | **400** `'tools.0.function.description' : Value is not nullable` | 200, tool call |
| openai (Responses) | gpt-4.1-mini | 200 | 200 |
| openai-chat | gpt-4.1-mini | 200 | 200 |
| gemini | gemini-2.5-flash | 200 | 200 |
| deepseek | deepseek-v4-flash | 200 | 200 |
| deepseek-anthropic | deepseek-v4-flash | 200 | 200 |
| moonshotai | kimi-k2.6 | 200 | 200 |
| together | openai/gpt-oss-120b | 200 (then 503) | 503 (then 200) |
| zai | glm-5.3-flash | 200 | 200 |
| vertex (generateContent, ADC bearer) | gemini-2.5-flash | 200 | 200 |
| OpenAI Realtime `session.update` | gpt-realtime-mini | `session.updated` | `session.updated` |
| Gemini Live `setup` | gemini-3.1-flash-live-preview | `setupComplete` | `setupComplete` |

Together's 503s were `service_unavailable`, alternating between the two
variants across two runs; both variants have a 200 on record. The
vertex pair was run after the others (`SUMMARY-probe-vertex-*.json`),
because of what Google's reference says (below).

What the references say (`scrapes/`), which is less uniform than the
servers:

- Anthropic `Tool.description: optional string`; OpenAI Chat
  Completions `function.description: optional string`. `null` is not a
  string; Anthropic and Groq enforce that.
- OpenAI Responses `description: optional string or null`: `null` is
  documented there, and leaving the key out is too.
- Gemini `FunctionDeclaration.description`: "`string` Required"
  (`scrapes/gemini/pages/generate-content.md`). Both Google doors
  (Gemini API and Vertex) answered a declaration without one with a
  normal tool call, and treat `null` the same as absent. Under
  AUTHORITY.md live behavior outranks documentation; the receipts are the
  evidence. There is no better spelling to send instead: in proto3 JSON
  `""` and `null` both read as the empty default, so they would fail any
  future server-side "required" check exactly as an absent key would,
  and inventing a description (the tool's name, say) would be lm15
  writing model input the caller never wrote. Stated risk: if Google
  starts enforcing its documented "Required", a tool with no
  description will fail on Gemini with Google's 400, the same way it
  fails today on Anthropic for `null`; the case's live revalidation is
  where that would show.

Correction inside the receipts, stated rather than edited (receipts are
append-only): `SUMMARY-probe-2026-10-02T21-08-08Z.json` records both
Gemini Live variants as `refused`. That was the probe's classifier, not
the server: Gemini Live sends its JSON as binary frames, and the first
version of the script searched the base64 text for `setupComplete`. The
verbatim frame in both exchange receipts is `{"setupComplete": {}}`. The
script was fixed to decode the frame, and the rerun
(`SUMMARY-probe-2026-10-02T21-08-28Z.json`) records both as `accepted`.

## Decided

- **MAP-17** (docs/mapping-rules.md): an absent description (`null` or
  `""`) reaches every wire with no description key; a present one is sent
  verbatim; key order is otherwise unchanged.
- `""` is treated as absent, not sent. Canonical JSON already makes
  `""` and `null` the same value (omit-empty), so a request and its serde
  round trip must build the same wire. lm15-go already did this.
- **Omit everywhere, not only where the server refuses.** Considered and
  rejected: omitting only for Anthropic and Groq. Leaving the key out is
  what every one of these references documents and was accepted by every
  server probed; `null` working elsewhere is tolerance, not contract, and
  a per-provider list would have to be re-probed for every new
  OpenAI-compatible host (Groq was the proof: it shares the Chat
  Completions builder with servers that accept `null`).
- The rule is scoped to this one field. The other `null`s on lm15 wires
  are values the wire defines (Chat Completions assistant `content: null`
  beside tool calls; TypeSafe criteria); a scan of every dialect's build
  of a minimal tool request (all 29 configurable providers in the
  reference registry) found the tool description was the only `null`.

## Cases (live captures, wire built by the fixed reference adapter)

`research/providers/tool_description_absent.py --capture`:

- `cases/anthropic/tool_no_description.json` (claude-haiku-4-5)
- `cases/openai/tool_no_description.json` (gpt-4.1-mini, Responses)
- `cases/openai-chat/tool_no_description.json` (gpt-4.1-mini, Chat Completions)
- `cases/gemini/tool_no_description.json` (gemini-2.5-flash)
- `cases/openai/live_tool_no_description.json` (gpt-realtime-mini)
- `cases/gemini/live_tool_no_description.json` (gemini-3.1-flash-live-preview)

Every one answered with a call to `get_weather` for Montreal. One case per
dialect builder: the other providers of a dialect share its builder, and
the probe table above is their evidence. Goldens are scribe drafts
(`goldens/*/tool_no_description.json`, `goldens/*/live_tool_no_description.json`),
not reviewed.

Not pinned by a case: a cached prefix's tools on Gemini (`cachedContents`)
and batch bodies. In every SDK both go through the same tool builder as
the pinned generateContent / Messages / Responses wires, so the pinned
cases exercise the code that builds them; a separate `cachedContents`
capture would cost a stored prefix of at least 1,024 tokens to prove the
same declaration helper again, and Gemini accepted both spellings on
generateContent. Stated trade-off: that path is covered by shared code,
not by its own recorded exchange.

## Implementations

Each SDK moves its pin to this commit with the fix: Python, TypeScript,
Rust, Go, Julia, R.
