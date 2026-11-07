# 2026-11-07 — Anthropic shows the thinking only when asked (MAP-7 rule 7 amended)

**Status: DECISION (maintainer, in session 2026-11-07: "ok go do it, yes do
the library side!!", on the plan below, after being told it reverses the
INV-049 reasoning) + the amended MAP-7 rule 7 in `docs/mapping-rules.md`,
the `summary` row of `spec/types.md` §Reasoning and the INV-049 note in
`spec/invariants.md`; to ratify. Wire evidence: live receipts below.**

## The finding

A FunctAI user on `claude-opus-5-5` asked for reasoning with a summary
(`Reasoning(effort, summary="auto")`) and got a thinking block with empty
text. MAP-7 rule 7 said `summary` "is satisfied silently where thinking is
always returned (Anthropic, xAI)", so lm15 sent nothing for it, and INV-049
kept Anthropic's `thinking.display` out of the canonical model "because no
other provider exposes one". Both rested on Anthropic returning the thinking
whenever thinking runs. That stopped being true.

Anthropic's thinking page, fetched 2026-11-07
(`receipts/2026-11-07-anthropic-thinking-display/anthropic-docs-thinking-2026-11-07.md`),
§ Controlling thinking display: `"summarized"` is the default on Claude Opus
4.6, Sonnet 4.6 and earlier; `"omitted"` (a thinking block with an empty
`thinking` field and its signature, billed the same) is the default on Opus
4.7, Opus 4.8 and every Claude 5 model (Opus 5 and 5.5, Sonnet 5 and 5.5,
Haiku 5.5, Fable 5 and 5.1, Mythos). `display` works with `type: adaptive`
and `type: enabled`; it is invalid with `disabled`. The API reference
snapshot under `scrapes/anthropic/pages/messages--create.md` still says
"Defaults to `summarized`" for every model; live behaviour wins
(AUTHORITY.md).

## Live evidence (`receipts/2026-11-07-anthropic-thinking-display/anthropic/`)

`research/providers/thinking_display.py`: every Claude model the account
lists, the same small puzzle, thinking on in the model's own form (adaptive
+ `output_config.effort: low`, or `enabled` + `budget_tokens: 1024`), with
and without `display: "summarized"`; the models that chose not to think at
low effort again with a harder question at `high` (`--hard`). Text length
of the thinking block / thinking tokens:

| Model | no `display` | `display: "summarized"` |
|---|---|---|
| claude-opus-5-5 | **0** / 66 | 188 / 50 |
| claude-sonnet-5-5 (hard) | **0** / 275 | 341 / 266 |
| claude-haiku-5-5 (hard) | **0** / 451 | 321 / 444 |
| claude-fable-5-1 (hard) | **0** / 367 | 417 / 369 |
| claude-opus-5 | **0** / 60 | 129 / 57 |
| claude-sonnet-5 | **0** / 90 | 219 / 115 |
| claude-fable-5 | **0** / 59 | 146 / 59 |
| claude-opus-4-8 | **0** / 71 | 248 / 107 |
| claude-opus-4-7 (hard) | **0** / 189 | 172 / 110 |
| claude-opus-4-6 (hard) | 1608 / 1488 | 1320 / 1196 |
| claude-sonnet-4-6 | 70 / 62 | 70 / 62 |
| claude-opus-4-5-20251101 (manual) | 723 / 408 | 879 / 491 |
| claude-haiku-4-5-20251001 (manual) | 908 / 501 | 744 / 445 |
| claude-sonnet-4-5-20250929 (manual) | 879 / 470 | 624 / 332 |

Every model answered `display: "summarized"` with HTTP 200: there is no
model the knob breaks, so no model table is needed for it (MAP-7 rule 10's
tables rot). `SUMMARY-2026-11-07.json` and `SUMMARY-2026-11-07-hard.json`
hold every row; one `probe-*.json` per request.

## The decision

**MAP-7 rule 7, Anthropic:** any `summary` adds `"display": "summarized"` to
the `thinking` object the request sends (`adaptive` or `enabled`), on every
model, where the compat's `thinking_format` is `anthropic` (api.anthropic.com,
the Claude Code login, and Claude on Azure, AWS, Bedrock and Vertex). No
`summary` sends no `display`: the model's default, as rule 1 leaves every
unset dial. `concise`/`detailed` are still substituted with `auto` (MAP-13),
which now also sends the knob; the note says "it returns one summary of the
thinking". `effort="off"` forbids `summary` (INV-026), so `display` never
meets `disabled`.

Why `summary` and not a new field: rule 7 already defines `summary` as
visibility, "`auto` = show the thinking where a knob exists". Anthropic now
has the knob and hides the thinking without it, so it joins OpenAI
(`summary: auto`), Gemini (`includeThoughts`) and Groq (`reasoning_format:
parsed`). Nothing else about the canonical model changes.

The other servers of the Messages wire keep rule 7 as it was (satisfied
silently): DeepSeek (`thinking_format` `deepseek`), Meta (`adaptive`) and
Moonshot (`effort`) are other companies' servers, return their thinking as
they always have, and were not shown to accept `display`.

**INV-049** keeps the `anthropic.thinking` and `anthropic.thinking_budget`
cases blessed: they spell `display: "summarized"` through `extensions`,
which still reaches the wire verbatim, and `"omitted"` and the beta
`"updates"` have no canonical spelling. Their verdicts in
`tools/extensions-verdicts.json` say so.

## Cases (live captures, wire built by the reference adapter)

`research/providers/thinking_display.py --cases`, `Reasoning(effort="low",
summary="auto")`, `max_tokens` 3000:

| Case | Model | What it pins |
|---|---|---|
| `anthropic.reasoning_summary` | claude-opus-5-5 | `thinking: {type: adaptive, display: summarized}`; a thinking part with text |
| `anthropic.streaming_reasoning_summary` | claude-opus-5-5 | the same, streamed: 21 `thinking_delta` events |
| `anthropic.reasoning_summary_budget` | claude-haiku-4-5-20251001 | `thinking: {type: enabled, budget_tokens: 2048, display: summarized}` |

Their goldens are scribe drafts from the amended reference. A shim that does
not send `display` fails the request direction of all three.

`harness/selftest.py`: the `stream_final_copy_diverges` mutation chose "the
first stream case whose feature is `streaming_reasoning_summary`", meaning
the Codex stream whose summary has several parts; the new Anthropic case
sorted first and has no final copy. The selector now names the provider
(`openai-codex`), as its neighbours do.

Cost: 55 metered calls to api.anthropic.com (42 probes, 10 at high effort, 3 cases; cents).

## Found, not changed here (stated)

- **`effort="off"` does not turn Claude 5's thinking off.** Rule 4 says
  Anthropic omits `thinking` for off; on Claude 5 "thinking is already on"
  (Anthropic's page), and live, a request with no `thinking` object thought
  on Opus 5.5, Opus 5, Sonnet 5, Haiku 5.5 and Fable 5 (57 to 228 thinking
  tokens). `thinking: {type: disabled}` is accepted by Opus 5, Sonnet 5 and
  Haiku 5.5 and refused with HTTP 400 by Opus 5.5, Fable 5 and Fable 5.1
  ("use adaptive and output_config.effort"); Sonnet 5.5 asks for
  `{type: between_tools}` instead. A silent drop under MAP-5; it needs its
  own decision (send `disabled` and let the server refuse loudly, or raise
  client-side by model class), and is left for one.
- Claude on Bedrock, Vertex and Azure was not probed (no credentials here);
  the knob goes to them by the same rule. Anthropic documents it for the
  Messages API those doors carry; a door that refuses it answers HTTP 400,
  and only when a summary was asked for.

## Implementations

Python, TypeScript, Rust, Go, Julia and R move their pin to the commit that
carries this entry and release 2.2.0 (a minor release: a request that asks
for a summary now sends one more field; nothing removed or changed in
meaning for requests that do not). Java, Ruby, .NET and Swift (pinned at
`cfed007`) are not changed; see `playbooks/parity.md`.
