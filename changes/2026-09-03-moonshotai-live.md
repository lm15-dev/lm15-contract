# 2026-09-03 — Moonshot AI (Kimi) live-verified; the `kimi` thinking shape and a client-side effort allowlist

Status: DRAFT, pending ratification.  A registry provider through the
pathway of `changes/2026-09-03-provider-registry.md`; dossier at
`research/providers/moonshotai/README.md`; scrapes at
`scrapes/moonshotai/pages/` (61 native-Markdown pages).

## Why this provider

The maintainer funded a platform.kimi.ai account and set
`MOONSHOTAI_API_KEY`.  Kimi K3 is a 1M-context reasoning model with a
documented Chat Completions wire; lm15 had no `moonshot` preset at all.
Scope of this entry: the Chat Completions wire (`moonshotai`), the
documented primary.  The Responses wire (kimi-k3 only, `tool_choice:
auto` only, reasoning replayed as `summary` text on a stateless server —
the Responses adapter has no knob for that replay yet) and the Anthropic
Messages wire (`/anthropic`) are separate provider strings for a later
entry, per the one-string-one-wire rule.  Files and Batches exist on the
service and are not registered.

## Cases (`cases/moonshotai/`, bodies verbatim; `kimi-k3` unless noted)

| case | body | HTTP | what it pins |
|---|---|---|---|
| `moonshotai.basic_text` | 2026-09-03T12-45-14Z | 200 | reasoning on by default (effort max): **134 reasoning tokens for "Say ok."** |
| `moonshotai.streaming` | 12-45-20Z | 200 | 6 `reasoning_content` deltas before 1 `content` delta; usage on the documented final chunk (and, undocumented, inside the finish chunk's choice) |
| `moonshotai.reasoning_low` | 12-45-22Z | 200 | top-level `reasoning_effort: low` alone — the `kimi` shape; 11 reasoning tokens |
| `moonshotai.reasoning_off` | 12-45-25Z | 200 | `thinking: {type: disabled}` alone; **honoured by K3** — no `reasoning_content`, no `completion_tokens_details` — against its docs |
| `moonshotai.tools` | 12-45-27Z | 200 | tool call with `reasoning_content`; ids are `<name>_<n>` (`get_weather_0`), `content: ""` |
| `moonshotai.streaming_tool_call` | 12-45-32Z | 200 | id + name on the first fragment, 5 argument fragments |
| `moonshotai.multi_turn_tool_result` | 12-45-43Z | 200 | the live turn-1 message replayed with its `reasoning_content` (`thinking_replay=native`) |
| `moonshotai.response_format_json_object` | 12-45-47Z | 200 | JSON mode |
| `moonshotai.response_format_json_schema` | 12-45-52Z | 200 | strict schema honoured exactly (`{"city":"Paris","country":"France"}`) |
| `moonshotai.system_prompt` | 12-45-57Z | 200 | `role: system` |
| `moonshotai.user_id` | 12-46-03Z | 200 | `Config.user_id` → `safety_identifier` (compat `user_field`) |
| `moonshotai.k26_reasoning_off` | 12-46-06Z | 200 | `kimi-k2.6` + `thinking: disabled`: `reasoning_content: ""`, 1 reasoning token |
| `moonshotai.k26_basic_text` | 12-46-08Z | 200 | `kimi-k2.6` thinks by default: 84 reasoning tokens |
| `moonshotai.models` | 12-46-10Z | 200 | 4 ids |
| `moonshotai.reasoning_effort_medium` | — | raise | **refusal** (below) |

Goldens drafted (`goldens/moonshotai/`, scribe-draft; `models.json` from
the shim).  Harness (python shim): request 223, response 184, stream 28,
error 52, auth 20, models 26 — 0 failures in these directions.

## A new thinking shape: `kimi`

Moonshot documents two reasoning wires keyed by model family
(`api--models-overview.md`): `kimi-k3` takes top-level `reasoning_effort`
(low|high|max, default max) and "does not support the `thinking`
parameter"; `kimi-k2.6` takes `thinking: {type: enabled|disabled, keep}`
and "does not support `reasoning_effort`".  No existing
`OpenAIChatThinkingFormat` sends either alone: `deepseek` sends both,
`reasoning_effort` cannot switch K2.6 off.

`"kimi"` splits by **intent**, not by model name: an effort word →
`reasoning_effort` alone; `off` → `thinking: {type: disabled}` alone.  Each
is exactly the documented field for the family that has that intent.
Live, the families are lenient in both directions
(`receipts/2026-09-03-moonshotai/`):

- K3 with the `deepseek` shape (`thinking: enabled` + effort): 200.  Not
  sent — it carries nothing K3 uses.
- K3 with `thinking: disabled`: **200, honoured** (no reasoning tokens).
  Docs contradicted; pinned as `moonshotai.reasoning_off`.
- K2.6 with `reasoning_effort: low`: 200, **ignored** (44 reasoning
  tokens).  Stated trade-off: the adapter does not sniff model names, so
  an effort word on K2.x is a silent no-op the docs warn about
  (`docs/providers-and-models.md`) rather than a refusal.  The alternative
  — a model-name table in the chat dialect — was rejected: it is a second
  copy of the provider's catalog and would rot on the next model.

## A silent cell → a client-side allowlist (MAP-7 rule 2)

K3 documents `low|high|max`.  Live: `reasoning_effort: medium` → 200 with
17 reasoning tokens; `reasoning_effort: bogus` → **200 with 17 reasoning
tokens** (`probe-error-k3-effort-medium`, `probe-error-bad-effort`).  The
server validates nothing, so `minimal`/`medium`/`xhigh` would silently run
at some undisclosed level.  MAP-7 rule 2 says words with no native level
raise client-side.  New compat field
`OpenAIChatCompat.reasoning_efforts: tuple[str, ...] | None` (default
`None` = the server validates; most do with a 400).  The `moonshotai`
preset lists `("low", "high", "max")`; any other word raises
`UnsupportedFeatureError` at `build_request`.  Pinned as
`moonshotai.reasoning_effort_medium` with `expect_lm15.raises`.  `off` is
never in the list — the off switch is `thinking_format`'s business.

## Decisions closed by the wire

| question | wire | decision |
|---|---|---|
| `max_tokens` vs `max_completion_tokens` | OpenAPI marks `max_tokens` deprecated; both 200 | send `max_completion_tokens` |
| `tool_choice` beyond auto | K3: `required` called the tool, `none` answered text; K2.6 `required` → **400** "incompatible with thinking enabled" | honoured or loud; no `forced_tool_choice` knob |
| `json_schema` | strict schema honoured exactly | sent; no `json_schema` knob |
| `user` vs `safety_identifier` | `safety_identifier` documented; `user` 200 with no echo | send the documented name |
| `reasoning_content` required with tools? | hand-built loop without it: 200 | `assistant_reasoning_content` stays default |
| temperature | `0.5` → **400** "only 1 is allowed for this model" | loud; envelope pinned |
| cache usage | `cached_tokens` at usage top level **and** `prompt_tokens_details.cached_tokens`; hit at 89 prompt tokens (docs say >256) | parser unchanged |
| `max_tokens` below the trace | `5` → 200, `finish_reason: length`, empty content | documented in the dossier; the Z.AI precedent |

## Error envelopes (`errors/cases/moonshotai.json`, 4)

`{"error": {"type", "message"}}`, no `code`.  401
`invalid_authentication_error` → `AuthError`; 404
`resource_not_found_error` "Not found the model … or Permission denied"
→ `UnsupportedModelError` (the dialect's 404 + "model … not found" rule);
400 `invalid_request_error` ×2 → `InvalidRequestError`.  Not observed and
mapped from `errors.md`: **`exceeded_current_quota_error` (insufficient
balance or disabled account, HTTP 429) → `BillingError`**, added to the
Chat Completions error mapping next to OpenAI's `insufficient_quota` and
Z.AI's `1113`; a funded account cannot trigger it on purpose, so the row
is documentation-evidenced (AUTHORITY.md precedence 2) and says so in the
code.

## Two env names

`MOONSHOTAI_API_KEY` (lm15's `<provider>_API_KEY` convention; the name the
maintainer set) then `MOONSHOT_API_KEY` (the name Moonshot's docs and SDK
examples use, `api--overview.md`).  Both are vendor-named, so reading both
cannot pick up another tool's secret — the objection to Meta's
`MODEL_API_KEY` does not apply.  Stated trade-off: with both set to
different keys the first wins silently; `auth/resolution.json` pins the
three cases (`moonshotai-env-selected`, `moonshotai-vendor-env-selected`,
`moonshotai-first-env-shadows-vendor-env`) so the doctor shows the
shadowed rung.

## Terms

Moonshot AI PTE. LTD., Singapore; SIAC arbitration; data stored in
Singapore.  **§4: Customer Content "may be used" to improve the Services
unless an enterprise agreement says otherwise.**  The docs note says so.
Verdict in the dossier: allowed, API key, Chat Completions wire.

## Reference changes (lm15-python)

- `compat.py`: `"kimi"` in `OpenAIChatThinkingFormat` and the resolved
  literal; `reasoning_efforts` field (validated: tuple of effort words,
  never `off`), resolved through; `moonshotai` preset; base URL.
- `providers/openai_chat.py`: the `kimi` branches; the allowlist raise.
- `providers/openai.py`: `exceeded_current_quota_error` → `BillingError`.
- `access.py`: `MOONSHOTAI` (two env keys); `registry.py`: the entry.
- `tests/test_registry.py`: `TestMoonshotai` (5); `tests/test_providers.py`:
  the reasoning-off table gains the preset.
- Docs: providers table and note, authentication table, router pages,
  README, CHANGELOG.

## Also in this entry

- `research/providers/moonshotai/capture.py`: declarations on the shared
  capture machinery; 19 probes.
- `tools/check_secrecy.py`: the platform.kimi.ai key shape.
- `scrapes/moonshotai/update.sh` + 61 pages; `scrapes/README.md` row.
- `auth/resolution.json` (+ the reference's conformance copy): 3 cases.
- `spec/support-matrix.json`: `moonshotai` row, pinned with these receipts.

Ratified-by: (pending)
