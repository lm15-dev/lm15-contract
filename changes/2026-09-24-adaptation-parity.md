# 2026-09-24 — MAP-13 in every SDK: one grid, six identical answers

Status: implementation parity for a ratified rule (MAP-13, 2026-09-14); no rule
changes. Prompted by the documentation: a page about generation settings has to
be true in six languages, and R and Julia refused a JSON schema that the other
four dropped and recorded.

## What was wrong

- **R and Julia had no MAP-13 at all.** No adaptation records, no policy
  (`note` / `silent` / `refuse`), no `plan()`. Every setting a wire could not
  take was either refused (where the others adapt and record) or silently
  omitted: `seed`, `frequency_penalty` and `presence_penalty` were not even
  Config fields (promoted 2026-09-14), so both ports dropped them without a
  word, and sent no `seed` on the Chat Completions and Gemini wires that carry
  it. Anthropic's required `max_tokens` defaulted to 1024 instead of the class
  ceiling, unrecorded.
- **Python, TypeScript and Go dropped cache hints silently.** A `cache.key` or
  `retention="long"` sent to a server with no cache fields (Z.AI, DeepSeek,
  Groq, xAI, Bedrock, the Anthropic-wire servers without cache marks) vanished
  with no record. Rust recorded them; MAP-13 says Rust is right.
- **Rust's client-side stop record omitted `applied`.** MAP-13: `applied` is
  absent only for `dropped` and `satisfied`.
- R's and Julia's provider tables predated the Ollama correction
  (`thinking_format: reasoning_effort`), and their Chat Completions ingest still
  refused `top_k` and the `functions` / `function_call` spelling and put `seed`
  and the penalties in extensions.

The corpus could not see most of this: it pins 21 adaptation cells, and the
grid has hundreds.

## The check

`tools/differential_requests.py`: every (provider, model) pair the corpus uses ×
38 settings (each sampling knob, each effort level, budgets, summaries, both
answer formats, cache hints, five tool-choice forms), built by each shim and
compared with Python: outcome and error class, adaptation records (field,
action, asked, applied), body and URL. 1,881 requests.

Before: R and Julia differed from Python on 679 each (297 outcomes, 280 records,
102 bodies); Rust on 52; TypeScript and Go on 40. After: **all six identical on
all 1,881.**

## Changes

- Python, TypeScript, Go: the dropped cache key / retention is recorded (Chat
  Completions and Responses on servers without OpenAI cache fields; the
  Anthropic wire on servers without cache marks), with Rust's wording.
- Rust: the client-side stop record carries `applied`.
- R and Julia: MAP-13 ported — the Adaptation type (on Response and on the
  start event), the policy on clients and routers, `plan()` (offline, no key
  needed), every adaptation point the reference has, the client-side stop on
  the Responses wire (the stream is cut at the sequence and the source closed;
  usage not reported), refusals carrying `feature`; `seed`,
  `frequency_penalty`, `presence_penalty` added to Config; provider tables
  refreshed from the reference (their copy scripts now skip TypeSafe, whose
  dialect neither port implements); ingest reads `top_k`, the penalties and
  `seed` as Config fields and translates `functions` / `function_call`.
- New cases: `zai.cache_hints_dropped` and `openai.stop_client_side`, derived
  from existing live captures (the adapted settings never reach the wire).

## Checked

| SDK | Differential | Harness | Own tests |
|---|---|---|---|
| Python | reference | full, all green | 3,339 passed |
| TypeScript | 1,881/1,881 | request green | one FetchTransport test fails before and after (unrelated) |
| Go | 1,881/1,881 | request green | pass |
| Rust | 1,881/1,881 | request green | three unrelated tests fail before and after |
| R | 1,881/1,881 | request 369/388, ingest 169/169; the rest are features R lacks (data parts, judgments, TypeSafe, logprobs_complete) | runtime script: records, plan, refuse, silent, client-side stop |
| Julia | 1,881/1,881 | same as R | runtime script as R; test suite see below |

R and Julia ran through temporary `harness/shims.json` entries (machine paths),
not committed. Not done: MAP-14 judgments and data parts in R and Julia, which
the harness still reports.
