# 2026-10-02 — The provider survey kit, backtested on six supported providers

Status: TOOLING (research/providers/, tools/test_provider_survey.py,
playbooks/provider.md § 2–3). No case, body, golden, preset or support claim
changes. The findings on supported providers below are reported for decision,
not acted on.

## Why

Expanding lm15 by the dozens of Chat Completions services Pi and LiteLLM
carry (research/landscape/REPORT.md: 50 with models on a wire lm15 speaks)
costs, per provider, the measurements behind a compat preset: which token
field caps a reply, whether usage arrives in a stream, which reasoning dial
the server reads, whether a forced tool choice or a JSON schema is honoured or
silently ignored. The 2026-09-26 batch did this by hand. The kit does it the
same way for any candidate, before lm15 has a registry row for it.

## What it is

- `research/providers/survey.py` — `init` (candidate.json and dossier from the
  landscape), `models`, `run` (~45 probes as a declared provider: raw bodies,
  so the receipts record the server, through `_capture.py`'s redaction and
  exchange hashes; 120 s per request, a timeout recorded as the result),
  `sweep` (per-model forced tool choice and reasoning off across many models,
  every sample kept, the worst deciding), `report` (offline: SURVEY.md with
  the drafted preset built as a real `OpenAIChatCompat`, the recorded replies
  parsed through lm15 with it, the recorded errors mapped through it, the code
  to paste, and `--compare <preset>` for a backtest).
- `research/providers/_survey_rules.py` — the decision rules, pure and
  offline, one per knob, each returning a value, a basis (decided, convention,
  not surveyable, needs you) and its evidence. The principles are the ratified
  ones: a loud refusal needs nothing (MAP-5/8); a silent ignore refuses
  client-side (MAP-8) or substitutes and records (MAP-13); what the probes
  cannot settle is asked, never guessed.
- `tools/test_provider_survey.py` — 13 tests in the contract's CI, built from
  the situations the backtests met; two injected rule bugs caught.

## Backtest: six supported providers as if they were candidates

Each provider's ratified preset is the answer key (`survey.py report <p>
--compare <p>`; receipts `receipts/2026-10-02-<p>-survey/`).

| Provider | Agree | Equivalent | Differ | Needs you | Not surveyable |
|---|---|---|---|---|---|
| Together AI | 8 | 0 | 0 | 0 | 1 |
| Fireworks AI | 8 | 0 | 0 | 0 | 1 |
| DeepInfra | 8 | 0 | 0 | 1 | 1 |
| DeepSeek | 8 | 1 | 0 | 0 | 2 |
| Z.AI | 9 | 0 | 0 | 1 | 2 |
| Groq | 6 | 1 | 0 | 1 | 2 |

No drafted value contradicts a ratified one. The three "needs you":

- **Z.AI** `thinking_format`: the surveyed model (glm-5.3-flash) cannot stop
  reasoning and spent the same at low and high, so no probe can show which
  dial the server reads. The ratified value came from a model that can stop
  (2026-09-03). The first draft of the rule decided here on "it reasoned"; the
  rule now needs a working off switch or a spend that follows the level.
- **Groq** `thinking_replay`: Groq refuses `reasoning_content` on a replayed
  turn but accepts and uses `reasoning` (recalled 2 of 3). lm15's replay
  sends `reasoning_content`, so Groq today runs on the default (the trace
  pasted as text). Using Groq's field would be a new knob (kind A′).
- **DeepInfra** `thinking_replay`: gpt-oss-120b recalled the replayed code
  word 1 of 3 times; the kit requires 2. The ratified preset accepted 1 of 3.

The two "equivalent" are servers that honour both forms (DeepSeek: both off
switches work; Groq: both token fields cap).

Per-model rules: Together's two `reasoning_off: lowest` families drafted from
one run. DeepInfra's 14-model forced-tool-choice allow-list: 12 reproduced by
`sweep` (24 models, two samples); the other two in § Findings.

## Findings on supported providers (for decision; nothing changed here)

1. **Together gpt-oss now honours a forced tool choice** (200 with the call;
   HTTP 500 on 2026-09-26). The ratified refusal is no longer needed.
   `receipts/2026-10-02-together-survey/probe-tool-choice-required-reasoner.json`.
2. **DeepInfra Qwen3.6-27B** is on the ratified allow-list but, in one of two
   samples, answered `tool_choice: none` by writing the call as text — the
   silent widening MAP-8 refuses. A third sample, or removal from the list.
3. **Groq no longer serves llama-3.3-70b-versatile** to this account (404
   `model_not_found`; the listing has no Llama). The website's default Groq
   model and several docs examples use it.
4. **Single samples mislead.** DeepInfra GLM-4.7 and Seed-2.0-mini honoured a
   forced choice in one sample and ignored it in the next; the ratified
   refusal stands. A sweep without `--repeat 2` is now flagged in the report.
5. **CORS is not what a script sees.** Together's preflight answered 403 to
   Python's default user agent and `*` to a browser's; the kit sends a
   browser's.

## Batch 2026-10

`research/providers/BATCH-2026-10.md`: the nine services both upstreams carry,
each with a candidate.json; addresses checked without an account (seven
answer a JSON 401 at `/chat/completions`, NVIDIA a 404, Cloudflare is a host
template and so kind B); all eight reachable ones allow a browser; key
variables confirmed in the docs for four.

## Stated trade-offs

- Survey receipts are committed (≈ 4.6 MB for the six backtests, DeepInfra's
  sweep most of it) as the kit's validation evidence. Later surveys add about
  350 KB each, plus a sweep.
- The kit speaks the Chat Completions wire only. A survey for the Anthropic
  Messages wire (MiniMax, Moonshot, DeepSeek also serve it) is follow-up work.
- Recall and refusal are sampled: a decided value from one survey is evidence
  for review, not a receipt; the playbook's live captures still pin the preset.
- Model ids in drafted overrides are exact; a ratified rule may widen one to a
  family prefix, which is a judgment the report shows side by side.
