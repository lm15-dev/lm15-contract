# 2026-09-06 — Preserve reasoning items in Responses streams

Status: correction under existing MAP-7 rules 8–9 and MAP-9 rules 2–4.
This does not ratify a new type, provider policy, or continuation namespace.

## Evidence

Independent comparison found that these pinned streams contain reasoning
items which their draft canonical expectations fail to preserve:

| Case | Pinned body | Reasoning item id |
|---|---|---|
| `meta.streaming` | `2026-09-03T11-46-11Z.txt` | `rs_6a995e03f8832c117f39455d:rs_01a067173d7e74009ebb127a618f9828` |
| `meta.streaming_tool_call` | `2026-09-03T11-42-17Z.txt` | `rs_6a995d1a81a9da7f11864982:rs_01a06713ade378f1977b31d81102b9c6` |
| `moonshotai-responses.streaming` | `2026-09-03T13-16-15Z.txt` | `rs_THs4eKuJdKB1gDX0AJFlyndY` |
| `moonshotai-responses.streaming_tool_call` | `2026-09-03T13-16-28Z.txt` | `rs_uWD3y5lP6WsXJ6nxiFQ0M4Ky` |

Each body contains `response.output_item.added` and
`response.output_item.done` for that item at output index zero. Meta returns
an empty summary. Moonshot returns streamed summary text. The old Meta
expectations omit the thinking part; the Moonshot expectations retain the
text but omit its replay state.

The Meta finding is recorded in
`research/baseline-review/2026-09-06-meta-canonical.md`, D1. Parent review
also inspected both Moonshot bodies. No new live call or implementation
output supplied the expected identifiers.

## Canonical correction

`lm15-python/docs/mapping-rules.md` MAP-7.9 requires an empty ThinkingPart
with replay state for an empty-summary Responses reasoning item. MAP-7.8
names `openai:reasoning_item`; this correction keeps that existing namespace.
MAP-9.2–4 joins thinking fragments and attaches indexed continuation state
to that part. Required empty text remains present under the serde rules.

The four traces now start the reasoning slot with an empty ThinkingDelta
at `output_item.added`. They attach the final id and any encrypted content
with one ContinuationDelta at `output_item.done`. This avoids duplicate text
from completed snapshots and uses the final replay payload, not an early
incomplete payload. It also preserves an unfinished empty thinking slot if
the stream stops before the completed item arrives.

Only these fields change: the two added events, missing Meta thinking parts,
and reasoning continuation on all four responses. Existing text, tool input,
identity, finish reason, usage, and terminal provider data stay unchanged.
The golden provenance cites this correction but remains draft: unrelated
review questions and historical wire-evidence gaps are not resolved here.

## Limits

The schema still needs a separate decision for redacted Anthropic thinking
in stream assembly. Message-level response-id continuation and cross-host
replay policy are not changed by this correction. No new event field is added.
