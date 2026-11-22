# Cross-provider saved-wire/spec review — seven expected answers

2026-11-22. All seven existing goldens agree with the saved replies and rules.
**No canonical answer, event trace, or recorded wire bytes changed.** The review
also exposed an untested malformed-live-call boundary, fixed separately in
Python and TypeScript with failing tests first.

This is a technical review of recorded evidence, not a fresh API capture or a
claim of additional human approval. SDK output was not used to decide expected
values. `tools/test_reviewed_cross_provider_goldens.py` reproduces the entire
reviewed projections with stdlib JSON, explicit counts and saved wire fields;
seven deliberate wrong-answer mutations must fail the same comparisons.

## Field-by-field decisions

In all complete responses, returned ID/model stay exact, role is assistant, and
text/thinking are verbatim in wire order. Unreported counters stay absent;
reported zeroes stay zero. Response provider_data is excluded by the vet
protocol, while stream-end provider_data is the usage-supplying object (MAP-3).
The review compares the latter against the saved object, stronger than the
harness's normal presence/type-only D9 check. No runtime privacy guarantee is
inferred from that comparison.

| Golden | Derivation and rules |
|---|---|
| `xai/structured_output` | Typed `reasoning_content`, then JSON text; finish stop. MAP-19.4's separate-reasoning rule: prompt **254**, answer **9**, reasoning **111**, canonical output **120**, total **374**. Cache read **192** is part of input, not added. Both audio counts are reported zero. ID/model retained. |
| `gemini/streaming_parallel_tool_calls_chunked` | MAP-20 Gemini slot rule: the Paris and Oslo calls in separate chunks become slots 0 and 1, never concatenated. Missing wire IDs become `tool_call_0/1` (MAP-9). First call alone carries its exact thought signature (MAP-7.8). No response ID is invented (MAP-9.6), request model is retained. Final cumulative usage replaces, not adds to, first chunk usage: **60 + (31 + 328) = 419**, output **359**, reasoning **328**, cached zero (MAP-19.6). STOP next to calls yields `tool_call`. Trace: start, call 0, continuation 0, call 1, one end. |
| `openai_chat/tool_call_unnamed` | Explicitly synthetic, not live. MAP-9: name never arrives in any of the three call fragments; keep every input fragment and ID as sent, but refuse assembly. Partial response retains `Checking.`, usage **48/11/59**, and provider finish `tool_call`, with no fabricated call. Chat chunk ID is not lifted into Response (MAP-9.6). Trace retains start/text/three call deltas/one end. |
| `openai-codex/streaming_parallel_tool_calls` | Two calls carry arguments only in `response.output_item.done`. MAP-20: ignore duplicate `function_call_arguments.done` and final response restatements for content; added events open calls with empty input, item finals supply each argument string exactly once. Paris and Oslo remain separate with their exact **call_id**, not item IDs. Response ID/model come from start. Usage **74/49/123**, cache read/write and reasoning all explicitly zero (MAP-19.7). Finish is `tool_call`. Trace: start/four call deltas/end. |
| `tinker/reasoning_effort_switch` | Thinking/text preserved; **13/143/156**, cached zero, no invented reasoning count. Requested `high` becomes wire boolean `true` and a `substituted` record (`applied: on`), per MAP-13 and `changes/2026-11-09-tinker-live.md`. Strict mode must refuse before network access. |
| `tinker/response_format_json_schema` | Thinking then free text `Tokyo is a city in Japan.`; **21/192/213**, cached zero. Schema is absent from the adapted request and pinned as `dropped`, not falsely enforced. The asked value remains the exact requested schema. Strict mode must refuse before sending. |
| `gemini/live_tool_no_description` | Transcript setup/housekeeping frames yield empty groups; the third server frame yields exactly one call: `fc_2902157236849646253`, `get_weather`, `{"city":"Montreal"}`. No synthetic usage, finish, or tool name is appended. Client frames do not become server output. |

Authority: `docs/mapping-rules.md` MAP-1, MAP-3/4, MAP-7.8, MAP-9,
MAP-13, MAP-19 and MAP-20; `spec/vocabularies.md` finish mapping;
`spec/types.md` parts/Usage/live events; `docs/serde-rules.md`; and
`harness/PROTOCOL.md` response, stream and live projections.

## Tinker policy evidence is more than an adapted request

A request from which lm15 already removed a schema cannot prove the server
ignores schemas. The review therefore also reads:

- `receipts/2026-11-09-tinker-survey/probe-json-schema.json`: the actual sent
  request **contains** a strict JSON schema; HTTP 200 returns `Paris, France.`
  as free text. This supports the documented drop policy for that recorded model.
- `.../probe-reasoning-oai-Qwen-Qwen3.5-4B-high.json`: the actual request sends
  `high`; HTTP 400 explicitly says the model accepts true or false. The
  `reasoning_effort_switch` case then records an accepted boolean request.

The SDK tests independently exercise visible notes and strict refusal. Python's
policy-free `build_request` hook is not the strict-policy entrypoint: the test
uses `complete` with an empty fake transport to prove it refuses before sending.
TypeScript owns that scope in `buildRequest`. No test touches a live provider.

## Evidence identity and limits

`tools/test_reviewed_cross_provider_goldens.py` pins the seven SHA-256 snapshot
hashes and checks original response receipts wherever linked. Three cases have
matching full response hashes (the Gemini chunked stream and both Tinker cases,
with the single-newline capture convention where applicable). Codex has an existing
exact hash-pinned privacy-redaction exception; Gemini Live's existing exception
records that the saved JSONL contains both directions while the receipt hashed
server frames. Neither exception is relaxed. xAI predates mandatory full
receipts; the unnamed Chat fixture is intentionally hand-authored. Snapshot
hashes identify the reviewed bytes and do not manufacture historical receipts.

## Boundary defect found and fixed

Both Gemini Live session decoders substituted `"tool"` for a missing/empty name
and coerced a numeric name into text. Python's live-completion stream did too.
A valid fixture cannot expose this. New missing/null/empty/numeric-name tests
failed before the fix on both supported envelopes; valid names (including a
literal real name `"tool"`) keep their IDs and arguments unchanged afterward.

Completed live calls now raise ProviderError before returning a misleading
call; Python completion fragments leave the name absent so StreamAssemblyError
can retain partial text and usage. Eight shared synthetic controls derive the
bad calls from the recorded named call, without editing the original transcript.
The harness self-test deliberately accepts a nameless live call and must catch it.
A socket-level TypeScript test also caught its session rewrapping the decoder's
ProviderError as TransportError. The session now preserves canonical decoder
errors while retaining transport wrapping for unexpected exceptions; it rejects
pending readers and closes the socket, without undoing earlier delivered text.

Trade-off: a malformed completed frame is refused as a unit. Earlier delivered
frames remain delivered; no live partial-response object is invented. This
pass does not redesign live missing-ID correlation or all live Config mappings.
Those remain separately scoped concerns, not silently claimed fixed here.

## Backlog accounting

Seven reviewed lines are added with original scribe provenance retained.
After PR #9's five reviews and the separately documented retirement of one
obsolete TypeSafe golden, this batch reduces the remaining active unreviewed
backlog **334 → 327**. Twelve reviews and one retirement are distinct actions.
