# Z.AI (GLM) — provider dossier

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-01 | Pi 0.84.1 `/login zai` |
| researched | 2026-09-03 | this dossier; `scrapes/zai/pages/` (22 pages); `sources/` (terms, privacy) |
| implemented | 2026-09-03 | `lm15.registry.PROVIDERS["zai"]`, `lm15.access.ZAI`, compat preset `zai` (rewritten) |
| offline-conformant | 2026-09-03 | auth case `zai-env-selected`; support matrix; registry tests; two pinned refusals |
| live-verified | 2026-09-03 | 10 cases, 2 refusal cases, 4 error envelopes, 16 probes: `changes/2026-09-03-zai-live.md`, `receipts/2026-09-03-zai/` |
| supported | — | after a reviewer ratifies the change entry |

## Identity

- Service: Z.AI open platform, JINGSHENG HENGXING TECHNOLOGY PTE. LTD, Singapore
  (`sources/zai-terms-of-use.md`).
- lm15 provider string: `zai` — the **general** Chat Completions endpoint only.
- Base URL: `https://api.z.ai/api/paas/v4` (`introduction.md`).
- Console: https://z.ai/manage-apikey/apikey-list.  Env key: `ZAI_API_KEY`.
- **Not named by lm15:** the GLM Coding Plan.  It is a subscription with its
  own endpoint, its own error codes (1309–1321, `api-code.md`) and its own
  terms (`docs.z.ai/devpack/usage-policy`).  A key from that plan against the
  general endpoint answers `1315` ("limited to enterprise coding package
  scenarios").  Registering it would need a terms review and is out of scope.

## What the preset got wrong before this pass

`OpenAIChatCompat.preset("zai")` had `thinking_format="zai"`, which the
serializer rendered as Qwen's `enable_thinking: true|false`.  Z.AI's wire is
`thinking: {"type": "enabled"|"disabled"}` plus `reasoning_effort`
(`chat--create.md` ChatThinking) — byte-identical to DeepSeek's.  The research
source `research/reasoning/sources/zai-thinking.md` had said so since
2026-09-02; the code and `tests/test_providers.py` pinned the wrong shape
anyway.  Fixed: the preset uses `thinking_format="deepseek"` (a shape name,
not a company) and the dead `"zai"` vocabulary value is removed.

## Wire facts, each with its receipt

| lm15 knob | Z.AI wire | Live 2026-09-03 | Compat / decision |
|---|---|---|---|
| reasoning default | on; effort `max` on GLM-5.3 | `basic_text`: 127 reasoning tokens for "Say ok." (`streaming`: 213) | omit = provider default, as everywhere; **the default is expensive — say so in docs** |
| reasoning off | `thinking: {type: disabled}` | GLM-5.3-flash: **400** `1210` "always engages in thinking … use low, high, or max"; GLM-5.2: 200, honoured | loud → no raise needed (unlike xAI's silent ignore) |
| effort | `reasoning_effort` low/high/max on 5.3 | `medium`, `minimal`, `bogus`: 400 `1210` on 5.3-flash | verbatim pass-through (MAP-7); the server refuses loudly |
| thinking replay | return `reasoning_content` with tool results (interleaved thinking) | `multi_turn_tool_result`: 200 with it; probe without it: **200 too** | `thinking_replay="native"`; `assistant_reasoning_content` left default (Z.AI does not demand it, DeepSeek does) |
| `max_tokens` | `max_tokens` (≤128K) | all cases | `max_tokens_field="max_tokens"` |
| streaming | SSE, `data: [DONE]`; `stream_options` undocumented | usage arrived on the final chunk anyway; tool call arrived whole in one chunk without `tool_stream` | `stream_usage="include"` |
| tools | function tools, `tool_choice` **auto only** | `required` → text answer, no call; `none` → called the tool; both HTTP 200 | **`forced_tool_choice="reject"`** → `UnsupportedFeatureError` before the wire; pinned `zai.tool_choice_required` |
| structured output | `response_format.type` ∈ text, json_object | `json_object`: honoured; `json_schema`: **200 with fenced free-form JSON**, schema ignored | **`json_schema="reject"`** → raise before the wire; pinned `zai.response_format_json_schema` |
| user identity | `user_id`, 6–128 chars | `user_id: "abc"` → 400 `1214` (validated); `user` → 200, no echo | `user_field="user_id"` |
| temperature | documented `[0, 1]` | `1.3` → 200, silently accepted | no lm15 action; documented |
| caching | implicit; `prompt_tokens_details.cached_tokens` | two identical 377-token prompts: `cached_tokens: 0` both times | parser already reads the field; no hit observed |
| usage | `completion_tokens_details.reasoning_tokens` present (undocumented) | every body | maps to `reasoning_tokens` |
| models | `GET /models` → `data[].id` | 10 ids (glm-4.5 … glm-5.3-flash) | `models: true` |
| errors | `{"error": {"code": "<string>", "message"}}` | 401 code `"401"` (docs say 1000/1001); unknown model 400 code `1214` (docs say 1211); **balance 429 code `1113`** | 1113 → `BillingError` (was `RateLimitError`, retryable — fixed); unknown model stays `InvalidRequestError` (no message-text guessing) |

## Terms-of-service verdict

Source: `sources/zai-terms-of-use.md` (sha256 in header).  Additional Terms
for API Services § 1(a): "the right to use Z.ai's API to integrate the
Services into your applications or to develop downstream systems,
applications or functions to your end users".  Restrictions that matter to
a library user: no training or distilling competing models (§ 1(f)(xii)),
no high-stakes automated decision-making (§ 1(f)(iii–iv)), no use through
"unauthorized third-party software" (§ 1(f)(x) — a documented-API client is
authorized use).  Governing law Singapore (§ XIII.3); data processed in
Singapore (`sources/zai-privacy-policy.md`).  For US users, no PHI/GLBA/COPPA
data (§ 11).

**Verdict: allowed, API key only, general endpoint only.**

## Open items

- `insufficient_system_resource`-class finish reasons (`sensitive`,
  `model_context_window_exceeded`, `network_error`, `chat--create.md:730`)
  were not observed; the adapter records them unmapped until seen.
- GLM-5.3-Flash accepts image/video/file input (`model--glm-5.3-flash.md`);
  not captured.  The matrix's `images` column means generation and stays false.
- Z.AI also sells image, video, ASR and web-search endpoints; none registered.

## Pi comparison (input, not authority)

Pi 0.84.1 registers `zai` and `zai-coding-cn`.  lm15 registers the general
endpoint only and states why above.
