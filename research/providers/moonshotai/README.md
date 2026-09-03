# Moonshot AI (Kimi API Platform) — provider dossier

Covers all three provider strings: `moonshotai` (Chat Completions),
`moonshotai-responses`, `moonshotai-anthropic`.  The capture scripts live
one per string (`moonshotai/`, `moonshotai-responses/`,
`moonshotai-anthropic/capture.py`); this file is the one dossier.

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-03 | maintainer request ("add support for moonshotai"; key set as `MOONSHOTAI_API_KEY`) |
| researched | 2026-09-03 | this dossier; `scrapes/moonshotai/pages/` (61 pages, native Markdown, index at platform.kimi.ai/docs/llms.txt); `sources/` (terms, privacy) |
| implemented | 2026-09-03 | `lm15.registry.PROVIDERS["moonshotai" / "moonshotai-responses" / "moonshotai-anthropic"]`, `lm15.access.MOONSHOTAI*`, compat presets `moonshotai` on all three dialects, chat thinking shape `kimi`, Anthropic thinking shape `effort`, knobs `reasoning_efforts` (chat, Anthropic), `AnthropicCompat.thinking_replay` / `sampling_params` |
| offline-conformant | 2026-09-03 | auth cases `moonshotai*` (5); support matrix (3 rows); registry tests (`TestMoonshotai`, 9); four pinned refusals |
| live-verified | 2026-09-03 | chat: 15 cases, 1 refusal, 4 envelopes, 19 probes (`changes/2026-09-03-moonshotai-live.md`); Responses: 11 cases, 9 envelopes, 16 probes; Anthropic: 10 cases, 3 refusals, 3 envelopes, 20 probes (`changes/2026-09-03-moonshotai-wires.md`); `receipts/2026-09-03-moonshotai*/` |
| supported | — | after a reviewer ratifies the change entry |

## Identity

- Service: Kimi API Platform ("Kimi OpenPlatform"), MOONSHOT AI PTE. LTD.,
  Singapore (`sources/moonshotai-terms-of-service.md`, last updated
  2026-07-30).  Docs at platform.kimi.ai; API host `api.moonshot.ai`.
- lm15 provider string: `moonshotai` — the **Chat Completions** wire only.
- Base URL: `https://api.moonshot.ai/v1` (`api--overview.md`).
- Console: https://platform.kimi.ai/console/api-keys.
- Env keys, in declared order: `MOONSHOTAI_API_KEY` (lm15's
  `<provider>_API_KEY` convention; the name the maintainer set) then
  `MOONSHOT_API_KEY` (the name Moonshot's docs and SDK examples use).
  Both are vendor-named, so reading both cannot pick up another tool's
  secret (the objection to Meta's `MODEL_API_KEY`).  Stated trade-off:
  with both set to different keys the first wins silently; the doctor
  shows the shadowed rung (auth case `moonshotai-first-env-shadows-vendor-env`).
- Keys are per platform: a platform.kimi.ai key does not open the Chinese
  platform and vice versa (`errors.md` "Platform key isolation" → 401).
- **Three wires, three provider strings** (one string names one wire —
  `changes/2026-09-03-provider-registry.md`):

  | string | dialect | class | base URL | surfaces |
  |---|---|---|---|---|
  | `moonshotai` | Chat Completions | `OpenAIChatLM(compat="moonshotai")` | `/v1` | complete, stream, models |
  | `moonshotai-responses` | Responses | `OpenAILM(compat="moonshotai")` | `/v1` | complete, stream, responses_api, models; `web_search` built-in |
  | `moonshotai-anthropic` | Anthropic Messages | `AnthropicLM(compat="moonshotai")` | `/anthropic/v1` | complete, stream (GET /models is 404 there — live) |

  Files (purposes
  `file-extract`, `image`, `video` — content extraction and vision input,
  not the OpenAI files surface) and Batches (JSONL) exist and are not
  registered.  Kimi Code is a separate subscription product
  (`guide--product-plans.md`).

## Models (live `GET /models`, 4 ids)

`kimi-k3` (flagship, 1M context, always reasons, effort low|high|max),
`kimi-k2.7-code` and `kimi-k2.7-code-highspeed` (thinking always on,
Preserved Thinking always on), `kimi-k2.6` (thinking on by default, can be
disabled).  `kimi-k2.5`, `kimi-k2*` and the `moonshot-v1*` series were
retired on 2026-08-31 and answer 404 (`models.md`).  Pricing (`pricing--k3.md`):
K3 $3.00 / $0.30 cache-hit / $15.00 per 1M tokens.  Rate limits depend on
cumulative recharge (`pricing--limits.md`: Tier 0 under $10 is **3 RPM**;
Tier 1 at $10 is 100 RPM).

## The reasoning dial is split by model family

`api--models-overview.md` and `guide--thinking-models.md` document two
wire shapes: `kimi-k3` takes top-level `reasoning_effort` and "does not
support the `thinking` parameter"; `kimi-k2.6` takes
`thinking: {type: enabled|disabled, keep: null|"all"}` and "does not
support `reasoning_effort`".  lm15 expresses this as one shape, `"kimi"`,
split by **intent** rather than by model name: an effort word goes out as
`reasoning_effort` alone; `off` goes out as `thinking: {type: disabled}`
alone.  Live, the families are more lenient than their docs:

| sent | to | docs say | live 2026-09-03 | consequence |
|---|---|---|---|---|
| `thinking: {enabled}` + `reasoning_effort: low` (the `deepseek` shape) | kimi-k3 | do not pass `thinking` | 200, 11 reasoning tokens (`probe-k3-thinking-enabled-plus-effort`) | accepted, but not sent: it carries nothing K3 uses |
| `thinking: {disabled}` | kimi-k3 | unsupported | **200, honoured**: no `reasoning_content`, no `completion_tokens_details` (`probe-error-k3-thinking-disabled`; pinned `moonshotai.reasoning_off`) | `effort="off"` works on K3 — docs contradicted |
| `reasoning_effort: low` | kimi-k2.6 | not supported | **200, ignored**: 44 reasoning tokens for "Say ok." (`probe-error-k26-reasoning-effort`) | silent no-op.  **Stated trade-off:** the adapter does not sniff model names, so an effort word on K2.x is not refused; the docs say not to set one |
| `reasoning_effort: medium` / `bogus` | kimi-k3 | low, high, max | **200 each**, 17 reasoning tokens each (`probe-error-k3-effort-medium`, `probe-error-bad-effort`) | the server validates nothing → new compat knob `reasoning_efforts=("low","high","max")` raises client-side (MAP-7 rule 2); pinned refusal `moonshotai.reasoning_effort_medium` |
| `thinking: {enabled, keep: "all"}` | kimi-k2.6 | Preserved Thinking | 200 (`probe-k26-thinking-keep-all`) | not sent by lm15; cross-turn preservation on K2.6 is an `extensions` opt-in (open item) |
| omitted | kimi-k3 | default `max` | `basic_text`: **134 reasoning tokens for "Say ok."** | omit = provider default, as everywhere; the docs note says so |

## Wire facts, each with its receipt

| lm15 knob | Kimi wire | Live 2026-09-03 | Compat / decision |
|---|---|---|---|
| `max_tokens` | `max_completion_tokens`; `max_tokens` marked deprecated in the OpenAPI | both accepted (`probe-max-tokens-deprecated`) | `max_tokens_field="max_completion_tokens"` — the documented one |
| thinking replay | pass the complete assistant message back "as-is (including `reasoning_content`)"; "required" for K3 | `multi_turn_tool_result`: 200 with it; a hand-built loop **without** it: 200 too (`probe-error-missing-reasoning-content-with-tools`) | `thinking_replay="native"`; `assistant_reasoning_content` left default (K3 does not demand it, DeepSeek does) |
| streaming | SSE, `data: [DONE]`; `stream_options.include_usage` → extra chunk with empty `choices` | usage arrives twice: inside the finish chunk's choice (undocumented) and on the documented final chunk; lm15 reads the latter; 6 `reasoning_content` deltas precede 1 `content` delta | `stream_usage="include"` |
| streaming tool call | argument deltas | id + name on the first fragment, then 5 `arguments` fragments (`streaming_tool_call`) | MAP-9 satisfied (a name on the first fragment) |
| tools | function tools; `tool_choice` auto/none/required/named on K3; K2.x refuses `required` | K3 `required` → called (`get_weather_0`), `none` → text; K2.6 `required` → **400** "incompatible with thinking enabled" | honoured or loud — no `forced_tool_choice` knob; tool-call ids are `<name>_<n>`, not `call_…` |
| structured output | `response_format` text / json_object / json_schema (strict, "MFJS") | json_object: honoured; json_schema strict: `{"city":"Paris","country":"France"}`, exactly the schema | both sent; no `json_schema` knob |
| user identity | `safety_identifier`; no `user` documented | `safety_identifier` → 200 (`user_id` case); `user` → 200, no echo (`probe-user-field-user`) | `user_field="safety_identifier"` — the documented name |
| temperature | fixed per model ("do not pass") | `0.5` → **400** "only 1 is allowed for this model" | loud; pinned envelope `moonshotai.temperature` |
| caching | automatic; `prompt_cache_key` the only knob; docs: hits need >256 prompt tokens | `cached_tokens` at usage top level **and** in `prompt_tokens_details`; a hit at 89 prompt tokens (docs contradicted) | `cache_control="openai_implicit"` (key forwarded, no mark); parser already reads `prompt_tokens_details.cached_tokens` |
| usage | `completion_tokens_details.reasoning_tokens` | every reasoning body | maps to `reasoning_tokens` |
| system prompt | `role: system` | `system_prompt`: "Ok ok" | `instruction_role="system"` |
| models | `GET /models` → `data[].id` | 4 ids | `models: true` |
| errors | `{"error": {"type", "message"}}`, no `code` | 401 `invalid_authentication_error`; 404 `resource_not_found_error` "Not found the model … or Permission denied" → `UnsupportedModelError`; 400 `invalid_request_error` ×2 | `exceeded_current_quota_error` (insufficient balance, HTTP 429, `errors.md`) → `BillingError` — documentation-evidenced, a funded account cannot trigger it |
| K2.6 off | `thinking: {disabled}` | `k26_reasoning_off`: `reasoning_content: ""` present, 1 reasoning token | honoured (the 1 token is the empty trace) |

## The Responses wire (`moonshotai-responses`), live 2026-09-03

Stateless by declaration and by wire: `store: false`, `previous_response_id:
null` on every body; reasoning comes back as a `reasoning` item whose
`summary[].text` IS the reasoning and `encrypted_content` is absent, and
goes back verbatim (`multi_turn_tool_result`: the item with its summary
text → 200; a hand-built loop without it → 200 too,
`probe-replay-without-reasoning-item`).  This is what the dialect already
sends for a ThinkingPart with text, so no new knob.

| lm15 knob | wire | live | decision |
|---|---|---|---|
| effort | `reasoning.effort` low\|high\|max | `none` → **400** "not supported"; `bogus` → **400**; `medium` → 200 (40 reasoning tokens) | this wire validates, so the word goes verbatim (MAP-7 rule 2 — the server decides); no allowlist here, unlike the other two wires; `medium` is an undocumented accepted level |
| `reasoning.summary` | not in schema | `auto` → 200 | sent when set; nothing to translate |
| `tool_choice` | `auto` only | `required`, `none` → **400** | loud; no knob |
| `text.format` | json_schema only | json_object → **400**; json_schema strict → exact | loud; `json_object` users get the server's error |
| builtin tools | function\|custom\|namespace\|web_search | `web_search` → 200 with a leading `web_search_call` item (4,627 input tokens); `code_execution` verbatim → **400** | `builtin_tools="verbatim"` (the canonical name is the wire type); names the server lacks fail loudly |
| caching | `prompt_cache_key`; `prompt_cache_retention` **not supported** (400) | `CacheConfig(retention="long")` → 400 | `cache_control="openai_implicit"`; retention is loud, documented in the docs note |
| temperature | not in schema | 0.5 → **400** "only 1 is allowed" | loud |
| `max_output_tokens: 1` | — | 200, `status: incomplete`, empty output | as OpenAI |
| system prompt | `developer` role item ("handled as a system instruction") | `system_prompt` | `developer_role="developer"` |
| models | same `GET /v1/models` | 4 ids | `models: true` |
| errors | OpenAI envelope with `code` (`model_not_found` on 400, not 404) | 9 envelopes pinned | existing mappings |
| kimi-k2.6 | docs: kimi-k3 only | 200 | no `model_prefixes` on this wire; the server decides |

Streaming vocabulary observed: `response.created/in_progress`,
`output_item.added/done`, `content_part.added/done`, `output_text.delta/done`,
`reasoning_summary_part.added/done`, `reasoning_summary_text.delta/done`,
`function_call_arguments.delta/done`, `response.completed`.

## The Anthropic wire (`moonshotai-anthropic`), live 2026-09-03

Bearer token (schema `bearerAuth`; Claude Code guide sets
`ANTHROPIC_AUTH_TOKEN`); `x-api-key` is accepted too
(`probe-x-api-key-header`, 200) — the documented one is sent.

| lm15 knob | wire | live | decision |
|---|---|---|---|
| reasoning | **no `thinking` field**; `output_config.effort` low\|high\|max | effort alone → 200; `thinking: {adaptive}` → 200 (ignored); `{enabled, budget_tokens}` → 200 (240 thinking tokens, budget not visibly applied); **`{disabled}` → 200, honoured** (no block, no thinking_tokens) | new `thinking_format="effort"`: the dial alone; off as `disabled`; pinned `moonshotai-anthropic.reasoning_off` |
| effort words | low\|high\|max | `medium` → 200 (12 thinking tokens), `bogus` → **200** (70) | the server validates nothing → `reasoning_efforts=("low","high","max")`; pinned refusal `reasoning_effort_medium` |
| thinking replay | blocks come back with `signature: ""` (or none) | unsigned block replayed → 200 (`probe-replay-unsigned-thinking-block`); loop without the block → 200 too | new `thinking_replay="unsigned"`: the block goes back as `thinking`; the dialect default would send it as text, putting the reasoning into the spoken turn |
| streaming | `thinking_delta` ×23, `text_delta`, **no `signature_delta`** | `streaming` | parser unchanged |
| tools | `tool_use`; ids `<name>_<n>`; `tool_choice` auto\|any\|none | `any` → called; `none` → text; named → **400** "tool_choice 'specified' is incompatible with thinking enabled" | loud |
| `disable_parallel_tool_use` | not in the schema | hand-sent → 200, one call (proves nothing) | `parallel_tool_calls="reject"` (documentation-evidenced, the DeepSeek precedent); pinned refusal |
| temperature / top_k | not in the schema | 0.5 → **200**; top_k 1 → **200** — while the chat wire answers 400 "only 1 is allowed" | new `sampling_params="reject"`; pinned refusal `temperature` |
| stop_sequences | ≤5, ≤32 bytes | "5" → stopped at "1, 2, 3, 4, " | honoured |
| structured output | `output_config.format` json_schema | exact `{"city":"Paris","country":"France"}` | `structured_output="send"` |
| caching | automatic; no `cache_control` in the schema | a hand-sent mark → 200, `cache_creation_input_tokens: 0`; reads happen anyway (`cache_read_input_tokens: 88` on an 88-token prompt) | `cache_control="none"` |
| usage | Anthropic-style **disjoint** (`input_tokens: 0` + `cache_read_input_tokens: 88`), `output_tokens_details.thinking_tokens`, plus OpenAI-style extras (`prompt_tokens`…) | every body | parser reads the Anthropic fields; the extras are ignored |
| models | `/anthropic/v1/models` | **404** `url.not_found` (`receipts/…/discovery-models-404.txt`) | `models: false`; list through `moonshotai` |
| errors | Anthropic envelope; `invalid_authentication_error`, `resource_not_found_error` | 401, 404, 400 pinned | both types added to the Anthropic-dialect map; the model rule gives `UnsupportedModelError` as on the chat wire |
| kimi-k2.6 | docs: kimi-k3 only | 200 with thinking | `model_prefixes=("kimi-",)` refuses only non-Kimi ids |

## Terms-of-service verdict

Source: `sources/moonshotai-terms-of-service.md` (sha256 in header).  §1
grants "a non-exclusive license … to use Moonshot AI's APIs to integrate
the Services into your own applications … and to offer those Customer
Applications to End Users".  Restrictions that matter to a library user:
no reverse engineering of the models (§3.2(4)), no developing competing
models or services without authorization (§3.2(5)), no buying, selling or
transferring API keys (§3.2(9)), no consequential decisions about a person
from output (§5(3)).  **§4 "Content": Customer Content "may be used" to
"provide, maintain, develop, support, and improve the Services" unless an
enterprise arrangement or separate written agreement says otherwise** —
i.e. API traffic can train or tune Moonshot's models by default.  The
docs must say so (they do, `docs/providers-and-models.md`).  Governing law
Singapore, SIAC arbitration (§12); data stored in Singapore
(`sources/moonshotai-privacy-policy.md` "Data storage").  Export and
sanctions clause (§13) names US, Singapore and EU law.

**Verdict: allowed, API key only, Chat Completions wire.  Users must know
the default content-use clause.**

## Open items

- `kimi-k2.6` Preserved Thinking across turns needs `thinking.keep: "all"`;
  lm15 does not send it (K3 refuses nothing but uses nothing from it, and
  the adapter does not sniff models).  Door: `compat.extensions`.
- `finish_reason: content_filter` and the 400 `content_filter` envelope
  (`errors.md`) were not observed; the adapter records them unmapped until
  seen.
- Partial Mode (`partial: true` on a trailing assistant message —
  `guide--partial-mode.md`) is Moonshot's assistant prefill; lm15 has no
  canonical prefill and does not send it.
- Vision input (`image_url`, `video_url`, `ms://<file_id>` references)
  documented on K3 and K2.6; not captured.  The matrix's `images` column
  means generation and stays false.
- Request signatures (`X-Msh-Request-Nonce` → `Msh-Request-Signature`,
  `signatures-verify.md`) are a provenance feature lm15 does not expose.
- Files and Batches: see Identity.

## Pi comparison (input, not authority)

Pi 0.84.1 registers `moonshotai` and `moonshotai-cn` (the Chinese platform,
api.moonshot.cn) plus `kimi-coding`.  lm15 registers the international
platform only; the CN platform has its own keys and terms and would need
its own review.
