# 2026-09-02 — The four MAP-8 refusals pinned as build-request raises

Ratification: not required. No rule changes; the four refusals were
ratified with MAP-8 (`2026-09-02-tool-choice-structured-output.md`) on the
receipts of that pass. This entry adds the fixtures that make them
portable, using the pinned-raise mechanism ratified with MAP-9.

## Cases

Each carries a `canonical_request` and
`expect_lm15.raises {op: build_request, type: UnsupportedFeatureError,
code: unsupported_feature}`; no wire request, no body, no golden — a shim
that produces a wire request here has mapped a cell the receipts refute.

| Case | Rule | Receipt (`research/tool-choice/receipts/`) |
|---|---|---|
| `xai.tool_choice_allowed` | MAP-8 §1: allowlists on xAI | `xai__grok-4.6__tc:allow-lookup-ask-weather/…` — only `lookup` allowed, model called `weather` |
| `gemini.tool_choice_parallel_false` | MAP-8 §2: no parallel knob | `gemini__gemini-2.5-flash__tc:parallel-false/…` — two calls returned; same on 3.7 |
| `xai.tool_choice_forced_with_format` | MAP-8 §3: force lost under a schema | `xai__grok-4.6__tc:force+schema/…` — JSON text, no call |
| `anthropic.response_format_json_object` | MAP-8 §6: no any-JSON mode | `anthropic__claude-sonnet-5__so:json_object/…` — HTTP 400; same on 4.5 |

## Harness

- `expect_lm15.raises` gains a required `op` (`build_request`,
  `parse_response`, `replay_stream`). Without it the stream case from
  MAP-9 was ambiguous: the request direction tried to hold it to a raise at
  build time. The declaration now names the op, and a case that refuses at
  build is not run by the parse/replay directions at all (not a "skip").
- The MAP-9 stream golden no longer repeats the error class and code; the
  case is the one declaration, the golden holds what was salvaged.
- New mutation `build_maps_a_refused_cell` (a wire request answered where a
  refusal is pinned): caught. 25 mutations total.
- The scribe passes over build-time refusals; nothing to draft.

## Evidence

Harness 13/13 green (request 143); selftest 25/25; audit, provenance,
secrecy, spec_drift green. Reference: the four raises already pinned by
`lm15-python/tests/test_tool_choice_structured_output.py`, unchanged.

## Stated trade-off

The canonical requests are hand-authored to match the experiment cells,
not byte-copies of the probe scripts' requests (those were built by hand
in `20-experiments.py`, outside lm15). The receipt proves the provider
behaviour; the case pins lm15's refusal of the same intent.
