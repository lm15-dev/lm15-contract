# Independent wire/spec review — five Anthropic expected answers

Date: 2026-11-22. Scope: the complete `canonical_response` projection in five
existing goldens. **All five agree; no expected-answer values were changed.**
This records an independent derivation from saved wire bytes and normative
rules, not approval by the maintainer and not a fresh live-provider validation.
No SDK was used to generate the expected answers or decide the verdicts.

## Evidence and method

Read each case, its named body, its golden, and the rules below. The review
compares every canonical field, including field absence, exact text, ordering,
opaque signatures/tool input, and usage arithmetic. The small reproducible
check in `tools/test_reviewed_anthropic_goldens.py` imports only the standard
library; it also demonstrates seven plausible errors that it rejects.
It is narrowly scoped to these five already-examined replies, not another SDK
or a general golden generator.

Rules:

- `docs/mapping-rules.md` MAP-1: text/thinking/client tool calls become parts;
  provider execution metadata does not become a client action.
- MAP-7 rules 8 and 11; `spec/types.md` ThinkingPart and ContinuationState:
  preserve signed thinking and its dialect-specific state, even with empty text.
- MAP-19 rule 5; `spec/types.md` Usage; INV-029: Anthropic input is uncached
  input + cache read + cache creation. Output already includes reasoning.
  Total is input + output. Missing exact reasoning counts remain absent.
- `spec/vocabularies.md` Forward-compatibility policy: `end_turn` becomes
  `stop`; `tool_use` becomes `tool_call`; a client tool call forces that finish.
- `docs/serde-rules.md` Omission and Number rules: explicit zero counters stay;
  required thinking text stays even when empty; opaque state/input stays exact.
- `harness/PROTOCOL.md` parse_response and `spec/types.md` Response: these
  goldens omit `provider_data` by design. This is a review of the canonical
  projection, not a proof that an SDK preserves all raw provider metadata.

## Field-by-field decisions

For every row, response `id` and returned `model` are copied exactly from the
reply, not inferred from the requested model. Role is `assistant`. Parts retain
wire order. No message-level continuation, stop sequence, audio counters,
logprobs, or other unreported canonical fields are invented.

| Case | Parts and finish | Input arithmetic | Output / total | Reasoning |
|---|---|---|---|---|
| `anthropic.reasoning_off` | Exact text `3861`; `end_turn` → `stop` | 22 + 0 + 0 = **22** | **6 / 28** | Absent, not zero: no exact thinking count was reported |
| `anthropic.reasoning_budget` | Thinking text and signature, then answer text; `stop` | 56 + 0 + 0 = **56** | **220 / 276** | **188**, included within 220, not added again |
| `anthropic.reasoning_adaptive` | **Empty thinking text kept** with signature, then answer text; `stop` | 34 + 0 + 0 = **34** | **133 / 167** | **82**, included within 133 |
| `anthropic.tool_no_description` | `tool_use` with `caller.type=direct` → client `tool_call`; exact ID, name `get_weather`, input `{"city":"Montreal"}`; `tool_call` finish | 557 + 0 + 0 = **557** | **54 / 611** | Absent |
| `anthropic.cache_history` | Exact text `3861`; `stop` | **3 + 0 + 3275 = 3278** | **6 / 3284** | Absent |

All five retain `cache_read_tokens: 0`. Cache writes are zero except the final
row's 3275. Thinking signatures compare as whole strings, not shortened
fingerprints; visible thinking text and answer text compare character for
character. For the hidden-thinking row, omitting the first part would destroy
replay state even though the displayed answer would look the same.

`tool_no_description`'s name describes the request feature. This review checks
its returned client tool call; it does not re-certify request-building behavior.
Likewise, reviewing `reasoning_off` does not prove the server spends no hidden
tokens: it only establishes what this recorded response actually reports.

## Saved bytes examined

Paths are relative to `bodies/`; all names below end in `.txt`.
These SHA-256 values identify this review's input snapshot. **They are not new
capture receipts.** Four bodies predate the receipt requirement and have no
separate full response-hash receipt. Their authenticity remains at the strength
of the existing grandfathered record; a fresh capture is separate work.

| Body | SHA-256 |
|---|---|
| `anthropic.reasoning_off/2026-09-01T15-04-22Z.txt` | `966d32fedf91085294892a8fda9292cf37a943e3dd2ca8ae9885094f82295e1d` |
| `anthropic.reasoning_budget/2026-09-02T12-50-13Z.txt` | `faf3e87a79f97c1ddb024a2d6b33e164e5d9c7d21d3e2c30595780ae42462f40` |
| `anthropic.reasoning_adaptive/2026-09-02T12-50-10Z.txt` | `aff9abcd3e38f1674ddbd8996407e8e527bb411237a45c05667321aa0c33dc69` |
| `anthropic.tool_no_description/2026-10-02T21-10-01Z.txt` | `87d2c825e52c14f23054bc6f1ac799b4f085db5654956708f4cd7213c5abc85e` |
| `anthropic.cache_history/2026-09-02T12-04-48Z.txt` | `1e60c73f050ae964cfd3bbd997f14baa6b930aeaa5d4295f376c13e226c856b7` |

The tool-call body matches its original receipt's full response hash exactly:
`receipts/2026-10-02-tool-description/anthropic/exchange-2026-10-02T21-10-01Z-59c8d728867442e49dea86cc24897588.json`.
No newline tolerance or redaction exception was needed for that match.

## Provenance change

The five `provenance.reviewed` lines cite this document. Original scribe origin,
original dates, and historical evidence remain intact. The corresponding five
entries leave `tools/unreviewed-goldens-ratchet.json`: **340 → 335** on this
review branch. No capture bytes, canonical values, or normative rules change.
Human approval is not implied by the review labels or by green test runs.

Reproduce: `python3 -m unittest discover -s tools -p 'test_reviewed_anthropic_goldens.py' -v`.
