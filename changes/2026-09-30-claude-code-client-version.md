# 2026-09-30 — The Claude Code release is a setting; Claude's default max_tokens is its ceiling

Status: amends spec/auth.md AUTH-10 (backend settings) and
docs/mapping-rules.md MAP-7 rule 6 (the unset `max_tokens` on the Messages
API); harness/PROTOCOL.md gains `compare_headers` and the `client_version`
setting. Approved in session ("Yes, we should do all these and we should do
it well"); the names, the guidance sentence and the refusal of an unread
settings entry were chosen by the implementer and are stated below for
assent.

## Found

A user building on lm15 through FunctAI reported, 2026-09-30:

1. **The Claude Code version was hard-coded and stale.** `claude-opus-5-5`
   refused with *"Claude Code 2.1.170 does not support this model; version
   2.1.280 or newer is required."* The installed `claude` was 2.1.284. The
   only way to change the version was `ClaudeCodeLM(claude_code_version=…)`,
   which the router could not reach, so every Claude call needed its own
   hand-built client object, and the error said "run claude update", which
   changes nothing lm15 sends.
2. **`max` effort on Opus never answered.** Opus spent the whole reply
   budget (16k, then 64k) thinking; a `thinking_budget` of 32k had no effect.
3. **The default 16384 `max_tokens`** was too small for any long reply with
   reasoning on.

What the evidence says about each:

- (1) is lm15's. The refusal was first seen 2026-09-23 (conversation
  01a0c9f4, request `req_011CfKMizsVsBFXTfU7EVVhQ`; the same account with
  2.1.280 answered) and not fixed. It is live again today:
  `receipts/2026-09-30-claude-code/probe-error-client-version-floor.json`.
  Worse, no port could have failed on it: the harness dropped `user-agent`
  as transport noise, so the six claude-code cases pinned 2.1.170 and no
  comparison ever read it.
- (2) is Anthropic's model behaviour on the adaptive class: `budget_tokens`
  is rejected there (MAP-7, live 2026-09-02), so `max_tokens` — thinking and
  answer together — is the only bound, and `max` thinks until it. lm15
  already dropped the budget with a `dropped` note on the response
  (MAP-13); the note did not reach the user because FunctAI raised its own
  "reply cut off" error without it. lm15's part is (3) and a clearer note.
- (3) is lm15's. MAP-13's audit (changes/2026-09-14-adapt-visibly.md §4.8)
  recommended "the model max from the profile, else 16384"; only the
  fallback was built.

## Changed

**D1 — The default release is the latest, receipted.** `claude-code`'s
`backend_options.client_version` (new; the `user-agent` header is built
from the same constant) is **2.1.285**, the newest `@anthropic-ai/claude-code`
on npm on 2026-09-30. Evidence: `cases/claude-code/max_tokens_defaulted.json`
(`claude-opus-5-5`, HTTP 200 with `claude-cli/2.1.285`) and the six
`tool_result_*` cases re-validated below.

**D2 — `client_version` is a backend setting** (spec/auth.md AUTH-10,
`backend_settings`). `RouterConfig(settings={"claude-code": {"client_version":
"2.1.290"}})`, or `settings=` on an adapter built by hand, or — read by the
router only — `LM15_CLAUDE_CODE_VERSION`. The same mechanism covers
`openai-codex`'s existing `client_version` (`LM15_CODEX_CLIENT_VERSION`); its
default does not change (no evidence that 0.147.0 is refused). The doctor
prints the value and where it came from. Evidence:
`cases/claude-code/client_version_setting.json` (settings `2.1.280`, the
model's floor, HTTP 200); auth/resolution.json `oauth-fresh`,
`claude-code-client-version-env`, `claude-code-client-version-explicit`.

**D3 — The refusal says what to change.** The server's message stays; lm15
adds:

```
  To fix:
    - lm15 sends this version itself; updating Claude Code does not change it
    - Set the claude-code setting client_version to 2.1.280 or newer (or LM15_CLAUDE_CODE_VERSION=2.1.280)
```

`errors/cases/claude-code.json` pins the whole message: the first error case
to pin `message`, so every port produces the same sentence.

**D4 — A settings entry nothing reads is refused.** Before, a door without a
host ignored its `settings` entry; now it raises `NotConfiguredError` naming
the settings the door does declare ("this door takes no settings" when none).

**D5 — Claude's default `max_tokens` is its output ceiling** (MAP-7 rule 6):
128000 for the 4.6 generation and later (and any Claude name the table has
not met), 64000 for the 4.5 generation; the retired 3.x values stay. On the
manual class the ceiling is the wire value and the visible part is what the
thinking budget leaves. Non-Claude names on Anthropic-dialect servers keep
16384. Evidence: the Models API's `max_tokens` for every listed model
(`receipts/2026-09-30-claude-code/models-max-tokens.json`: `claude-opus-5-5`,
`claude-sonnet-5-5` and every 4.6+ model 128000; the three 4.5 models 64000),
`scrapes/anthropic/pages/models-overview.md` ("Max output"), and three live
calls: `claude-opus-5-5` with 128000 non-streaming
(`claude-code.max_tokens_defaulted`), `claude-haiku-4-5` with 64000
(`anthropic.data_part_text`, re-validated) and `claude-sonnet-4-5` with
budget 16384 inside 64000
(`receipts/2026-09-30-anthropic/probe-max-tokens-defaulted-reasoning.json`).

**D6 — The adaptive-class `thinking_budget` note says what bounds thinking**:
"…Thinking is bounded only by max_tokens, which covers thinking and answer
together: lower the effort or raise max_tokens". Reasons are not compared by
the harness; the ports carry the same words.

**D7 — The harness compares headers a case pins** (`compare_headers`,
harness/PROTOCOL.md). The seven claude-code wire cases pin `user-agent`.
Selftest mutation `pinned_header_stale` (a port still sending 2.1.170) is
caught.

## Fixtures and how they were re-validated

- `cases/claude-code/tool_result_{text,image,mixed,pair,pdf,error}.json`:
  the request the reference adapter builds today differs from the
  2026-09-07 pin **only** in `user-agent` (the capture script aborts on any
  other difference). Each was sent live with 2.1.285; every one returned
  HTTP 200 and the 2026-09-07 run's hidden oracle came back (the colours;
  for `error`, nothing fabricated). The pinned response bodies and goldens
  are the 2026-09-07 capture's, named by `provenance.response_exchange`:
  the request side is what changed.
- `cases/anthropic/data_part_text.json`: likewise, only `max_tokens`
  16384 → 64000 moved; HTTP 200, the data part and `stop` came back; the
  `defaulted` pin now says 64000.
- `cases/anthropic/max_tokens_defaulted.json` (hand-authored) now expects
  64000; new hand-authored `anthropic.max_tokens_defaulted_reasoning`
  (manual class, 47616 visible, 64000 on the wire; the same wire sent live,
  above) and `deepseek-anthropic.max_tokens_defaulted` (16384).
- New live captures: `claude-code.client_version_setting`,
  `claude-code.max_tokens_defaulted` (goldens drafted by the scribe, not
  reviewed).

Script: `research/providers/claude_code_client_version.py`.

## Trade-offs, stated

- **A pinned release still goes stale.** Anthropic raised the floor from
  below 2.1.170 to 2.1.280 within a month and publishes a release almost
  daily. The default is now the newest, and the setting and the env
  variable fix a deployed program without an lm15 release, but the table
  needs a bump whenever a new model needs a newer release. Rejected:
  reading the installed `claude --version` automatically — it costs a
  subprocess at startup, makes the same program send different bytes on
  different machines, and a user of lm15's own Claude sign-in may have no
  Claude Code installed at all. Rejected: retrying with the version the
  refusal names — lm15 would change the identity it claims without being
  asked.
- **An adapter built by hand reads no environment**, as for keys and host
  settings: `LM15_CLAUDE_CODE_VERSION` moves routed calls, not a
  `ClaudeCodeLM()` constructed directly (pass `settings=` there).
- **D4 can break a program that passed a settings entry lm15 ignored.** It
  was a no-op before, so the only program it breaks is one whose entry
  never did anything; the error names the fix.
- **A larger default lets a call run longer and cost more before it
  stops.** `max_tokens` is a ceiling, not a spend: Anthropic counts output
  tokens as produced, so a high value costs nothing unless used, and does
  not count against the output rate limit (rate-limits.md). A non-streaming
  reply that thinks for many minutes can still meet the transport's read
  timeout or an idle-connection drop (errors.md, "Long requests"); streaming
  avoids both. The server accepted 128000 non-streaming today.
- **A newer Claude with a lower ceiling** would get a loud 400 ("max_tokens:
  128000 > N"), never a silent truncation. So would a retired model a cloud
  still serves (3.7 Sonnet, Opus 4.1: retired on Anthropic's platforms,
  model-deprecations.md).
- **`max` effort on Opus can still use every token thinking.** No lm15
  default can change what the model chooses to spend; the note now says
  what bounds it. FunctAI's "cut off" error should carry lm15's notes
  (a FunctAI change, not made here).
- The claude-code door tells Anthropic it is Claude Code, and Anthropic now
  demonstrably checks the claim. That was R1's open question (is this use
  permitted?) and remains open; this change keeps the door working, it does
  not answer it.
