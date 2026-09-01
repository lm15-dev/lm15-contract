# 2026-09-01 — logprobs output surface + kind-aware ToolChoice resolution

Ratified: Maxime Rivest, 2026-09-01 (session assent "yes good, go!" over the
design draft `lm15-python/docs/drafts/logprobs-and-builtin-tool-forcing.md`).
This is the "logprobs design pass" that `tools/extensions-verdicts.json` had
deferred `openai.top_logprobs` and `openai.include` to.

## 1. Logprobs — canonical token probabilities

New surface:

- `Config.logprobs: int | null` — `null` = off; `0` = chosen tokens only
  (data, always serialized); `n > 0` = also top-n alternatives. Provider
  caps (currently 0–20 everywhere) stay provider-owned.
- `TokenLogprob` (`token`, `logprob`, `bytes?`, `token_id?`, `top`) and
  `TopLogprob` (same minus `top`) — two flat types; the wire never nests
  alternatives inside alternatives.
- `Response.logprobs: TokenLogprob[] | null` — decoding telemetry, the
  `usage` category; `null` = not reported.
- `TextDelta.logprobs: TokenLogprob[]` — per-fragment tokens; stream
  materialization concatenates into `Response.logprobs`.

Mappings:

| Provider | Request | Response | Evidence |
|---|---|---|---|
| openai (Responses) | `top_logprobs` + `include: ["message.output_text.logprobs"]` | per-block `logprobs` entries, concatenated | live 2026-09-01 (complete, stream, `top_logprobs: 0`) |
| openai_chat dialect | `logprobs: true` (+ `top_logprobs` when n>0) | `choices[0].logprobs.content`; `refusal` stays provider_data | live 2026-09-01 (`bodies/openai_chat.logprobs`) |
| gemini | `responseLogprobs` (+ `logprobs` when n>0) | `logprobsResult` chosen/top zip; `avgLogprobs`/`logProbabilitySum` stay provider_data (derivable) | DOC-BASED — every currently served model rejects with "Logprobs is not enabled" (probed gemini-2.5-flash/-lite/-pro, gemini-3-flash-preview, gemini-3.6-flash, 2026-09-01) |
| anthropic | RAISES UnsupportedFeatureError | — | no wire field exists |

Known provider difference, preserved not normalized: Gemini documents its
alternatives count as *including* the chosen candidate; OpenAI counts
alternatives only. `top` is the provider-reported list as-is.

Corpus changes:

- `cases/openai/top_logprobs.json`, `cases/openai/include.json`:
  canonical_request rewritten from smuggled extensions onto
  `Config.logprobs` (wire UNCHANGED, harness proves build equality);
  the two deferred verdicts removed from extensions-verdicts.json.
- `goldens/openai/{top_logprobs,include}.json`: `logprobs` field added,
  regenerated from the SAME pinned bodies (only key that changed).
- New case + pinned live body + draft golden: `openai_chat.logprobs`
  (captured against api.openai.com — Groq, the corpus's usual dialect
  target, currently 404s its own pinned models).
- 4 new serde cases: `config.logprobs-zero`, `config.logprobs`,
  `delta.text-logprobs`, `response.with_logprobs`.
- No Gemini case: the request mapping is doc-based and cannot be
  live-validated until Google re-enables logprobs on a served model.

## 2. Builtin-tool forcing — no new field

`ToolChoice` is unchanged. `allowed` entries now resolve against
`Request.tools` by kind (INV-031 already guarantees presence; tool names
are unique). See spec/types.md ToolChoice for the per-provider table.

Evidence highlights:

- **Anthropic server-tool forcing WORKS**: `tool_choice
  {"type":"tool","name":"web_search"}` produced a forced
  `server_tool_use` (live 2026-09-01, `bodies/anthropic.tool_choice_builtin`).
  The API reference is silent on this; the capture is the authority.
- **OpenAI hosted-tool forcing + mixed allowed_tools** both accepted
  live (`bodies/openai.tool_choice_builtin`,
  `bodies/openai.tool_choice_allowed`).

Behavior corrections (all raise-over-degrade per durable principles):

- openai: a single allowed name with `mode="auto"` previously emitted
  `{"type":"function","name"}`, which FORCES the call — it now emits
  `allowed_tools` with mode auto. The stale "no multi-tool allowlist"
  comment was wrong; `ToolChoiceAllowed` exists on both OpenAI dialects.
- anthropic: proper-subset allowlists previously degraded to `any`/`auto`,
  silently letting the model call EXCLUDED tools — now raise.
  Allowlists naming every declared tool still map to `any`/`auto`.
- gemini: `allowedFunctionNames` was emitted under mode `AUTO`, which the
  docs forbid ("only when the Mode is ANY or VALIDATED") — auto-subsets
  now use `VALIDATED` (doc-exact semantics). Builtin names raise.
- openai_chat dialect: builtin forcing raises; multi-name subsets now use
  the dialect's nested `allowed_tools` form instead of silently degrading.

New cases + pinned live bodies + draft goldens:
`openai.tool_choice_builtin`, `openai.tool_choice_allowed`,
`anthropic.tool_choice_builtin`.

## Out of scope, flagged

- The openai_chat dialect still silently DROPS BuiltinTool entries from
  `Request.tools` (pre-existing; forcing one now raises, offering one
  still doesn't). Needs its own verdict.
- Gemini live logprobs re-capture when Google re-enables the knob.
- Groq's pinned openai_chat models 404 — the dialect corpus needs a
  refresh pass.

## Harness after this change (python shim)

request 117/0, response 108/0, stream 9/0, serde 98/0 — all green;
audit OK, provenance OK, secrecy OK. The 3 vocabularies.md video-enum
drift items are the separate unpushed video-generation stream's.
