# Meta Model API (Muse) — provider dossier

Covers all three provider strings: `meta`, `meta-chat`, `meta-anthropic`.
The capture scripts live one per string (`meta/`, `meta-chat/`,
`meta-anthropic/capture.py`); this file is the one dossier.

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-03 | maintainer request ("add this provider, all they offer that we support") |
| researched | 2026-09-03 | `scrapes/meta/pages/` (60 native-Markdown pages, index at dev.meta.ai/docs/llms.txt) |
| implemented | 2026-09-03 | `lm15.registry.PROVIDERS["meta" / "meta-chat" / "meta-anthropic"]`, `lm15.access.META*`, compat presets `meta` on all three dialects |
| offline-conformant | 2026-09-03 | auth cases `meta-*` (3); support matrix (3 rows); registry tests (`TestMeta`, 7) |
| live-verified | 2026-09-03 | 34 cases, 19 error envelopes, 51 probes: `changes/2026-09-03-meta-live.md`, `receipts/2026-09-03-meta*/` |
| supported | — | after a reviewer ratifies the change entry **and** the terms review below is closed |

## Identity

- Service: Meta Model API, Meta Platforms (`dev.meta.ai`).  Models: Muse
  Spark 1.1/1.2/1.3 (text, 1M context), Muse Image 1.0 (image out), Muse
  Voice Transcribe 1.0 (speech-to-text), Muse Glimmer (open weights,
  self-hosted — not an API model).
- Base URL: `https://api.meta.ai/v1` for every surface (`overview.md`).
- Console: https://dev.meta.ai/ (API keys tab).  Key shape: the docs say
  `LLM|<team id>|<secret>` (`authentication.md`); a key issued 2026-09-03 is
  `LLM_<15 digits>_<27 alphanumerics>`.  `tools/check_secrecy.py` knows both.
- Env key: `META_API_KEY` only.  Meta's docs and SDK examples name the
  variable `MODEL_API_KEY`; lm15 does **not** read it.  A vendor-less name
  can be another tool's secret, and reading it would send that secret to
  Meta without the user asking — a credential-leak class of bug that no
  quickstart convenience pays for.  The registry note and the docs tell a
  quickstart user to export the key under the vendor name.
- Auth: `Authorization: Bearer` on all three wires, including the Anthropic
  one (`protocols--messages.md` passes the key as `auth_token`).

## Three wires, three provider strings

`protocols.md`: "same models, same auth, same cost per token".  A provider
string names ONE wire behavior (`changes/2026-09-03-provider-registry.md`),
so one service over three dialects is three entries — the `openai` /
`openai-chat` and `deepseek` / `deepseek-anthropic` precedents.

| string | dialect | class | why it exists | surfaces |
|---|---|---|---|---|
| `meta` | Responses | `OpenAILM(compat="meta")` | Meta's recommended default; the only wire that carries reasoning across turns; `web_search`; the account surfaces live on the same root | complete, stream, files, images, models, responses_api |
| `meta-chat` | Chat Completions | `OpenAIChatLM(compat="meta")` | drop-in for existing messages-array code | complete, stream, models |
| `meta-anthropic` | Anthropic Messages | `AnthropicLM(compat="meta")` | drop-in for Anthropic-SDK code | complete, stream, models |

The Responses dialect could not bind before this pass (`_COMPAT_TABLES`
had chat and Anthropic only; `OpenAILM` resolved its compat from the base
URL alone).  It now takes `compat=` like its siblings, presets live in
`OPENAI_RESPONSES_PRESETS`, and the registry validates the binding the same
way.  No behavior change for `openai` / `openai-codex`: their entries are
still adapter-owned and the `openai` preset is byte-identical to the old
if-chain branch (harness: request 209 / response 173 / stream 26, 0 failures).

## Wire facts, each with its receipt (`receipts/2026-09-03-meta*/`)

### Common to all three wires

| lm15 knob | Meta wire | Live 2026-09-03 | Decision |
|---|---|---|---|
| reasoning default | on, model-set effort | Responses `basic_text` with `max_output_tokens: 600`: **status `incomplete`, `output: []`, 597 reasoning tokens** (`bodies/meta.basic_text/2026-09-03T11-41-50Z.txt`); recaptured at 3000 | omit = provider default; docs say so in `docs/providers-and-models.md` (set effort low, give max_tokens room) |
| reasoning off | `none` / `thinking: disabled` | **400** on all three wires (`probe-error-reasoning-none`, `probe-error-thinking-disabled`) | loud → sent as asked, no pre-wire raise (the reasoning-off precedent, `changes/2026-09-02-reasoning-design.md`) |
| effort words | `minimal…xhigh` (Responses/Chat); `low…xhigh` (Messages) | Responses/Chat: `minimal` 200 (41 reasoning tokens), `xhigh` 200, `bogus` 400 listing the set; Messages: `minimal` **400** | verbatim pass-through (MAP-7); the server refuses loudly |
| `tool_choice` beyond `auto` | not supported | `required` / `none` / named → **400** on all three wires (`probe-tool-choice-*`) | loud → no `forced_tool_choice="reject"` needed (unlike Z.AI's silent 200) |
| `logprobs` | not supported on a reasoning model | 400 (`probe-error-logprobs`, both OpenAI wires) | loud |
| caching | automatic prefix caching; `prompt_cache_key`, `prompt_cache_retention` honoured; "you do not … mark breakpoints" | chat `cache-second`: `cached_tokens: 369` of 374; Messages: `cache_read_input_tokens: 369`; a hand-sent `prompt_cache_breakpoint` mark: **200, no signal** (`probe-cache-breakpoint-mark-raw`) | new `cache_control="openai_implicit"` on Responses/Chat: key + retention forwarded, the undocumented mark never placed (a field the server swallows is not sent — MAP-8); an explicit `CacheConfig` is not an error (the prefix is cached anyway, the `"none"` precedent); Messages `cache_control="none"` |
| usage | `*_details.reasoning_tokens` / `thinking_tokens`, `cached_tokens` | every body | parsers unchanged |
| errors | OpenAI envelope with `type` + `code` (`code` often null) | 401 `invalid_api_key`; 404 `model_not_found` → `UnsupportedModelError`; Messages wire uses the Anthropic envelope (`not_found_error`) | existing mappings; 19 envelopes pinned in `errors/cases/meta*.json` |
| models | `GET /models`, OpenAI shape, 7 ids incl. the image and transcribe models | 200 on all three (the Anthropic dialect's parser reads it) | `models: true` on all three |

### `meta` (Responses)

| lm15 knob | Meta wire | Live | Decision |
|---|---|---|---|
| system prompt | top-level `instructions` (developer-level) | `system_prompt` | preset `developer_role="developer"` |
| `max_tokens` | `max_output_tokens`, min 16 | `probe-error-max-tokens-below-16`: 400 | loud |
| reasoning replay | `reasoning` items; `encrypted_content` "omitted by default, set include" | **docs contradicted**: turn 1 with `store: false` and no `include` returned `encrypted_content` anyway; id-only replay under the default `store: true` → 200; unstored encrypted replay → 200 (`probe-reasoning-*`) | lm15's existing replay (id + summary [], encrypted_content when present) works stateless and stateful with no knob |
| commentary phase | assistant text before a `function_call` carries `phase: "commentary"`; docs: replay without it is 400 | server emits it on `tools`; **untagged replay answered 200** (`bodies/meta.multi_turn_tool_result/2026-09-03T11-42-21Z.txt`, `probe-commentary-text-before-call`) | new compat `commentary_phase="tag"`: the tag goes back because the docs say dropping it "can degrade quality", not to avoid an error; OpenAI never gets the field |
| `web_search` builtin | schema enum `web_search` \| `web_search_2025_08_26` | adapter-built `web_search` → 200, searched (`probe-web-search-builtin`); OpenAI's `web_search_preview` also 200 but undocumented (`probe-web-search-preview-spelling`); canonical `code_execution` sent verbatim → **400** "did not match any supported type" (`probe-error-builtin-code-execution`) | new compat `builtin_tools="verbatim"` (first written `"meta"`, renamed the same day): the documented name goes out unchanged; names Meta lacks go out verbatim and fail loudly (no pre-wire refusal needed) |
| structured output | `text.format` json_schema | 200, schema honoured | existing mapping |
| `user_id` | `safety_identifier` | 200 | existing mapping |
| image generation | `POST /images/generations`, `b64_json` default, `output_format` echoed (`webp` default) | 200, 1600×1600 webp, pixel-checked (red circle) — `receipts/2026-09-03-meta/image_gen-0.webp` | existing `image_generate`; media type read from the wire |
| image edit | multipart; **`image[]` rejected**: "use `image[N]` with indices numbered consecutively from 0" | `image[]` → 400 (`probe-error-image-edit-array-key`, the OpenAI-preset wire sent by hand after the first capture's failed receipt was mistakenly deleted and then re-run under a probe name); `image[0]` → 200, edit honoured (blue square bottom-right on the red input) | new compat `edit_image_field="indexed"`; OpenAI keeps `image[]` (pinned) |
| files | `POST /files` purpose `user_data`; download allowed | upload/get/list/download/delete all 200 (`cases/meta/files.json`) — download of `user_data` works here (OpenAI refuses it) | existing files lifecycle |
| `top_p: 0` | rejected | 400 | loud |

### `meta-chat` (Chat Completions)

| lm15 knob | Meta wire | Live | Decision |
|---|---|---|---|
| instruction role | `developer` documented; `system` merged at the same level | 200 | `instruction_role="developer"` |
| `max_tokens` | `max_completion_tokens`; `max_tokens` deprecated alias | both 200 (`probe-max-tokens-alias`) | documented name |
| thinking on the wire | `reasoning_content` **redacted to empty for external keys** | absent on every body (`probe-reasoning-content-redacted`) | no replay knob; `thinking_format="reasoning_effort"` |
| `user_id` | `safety_identifier` (`user` deprecated, still honoured) | both 200 | `user_field="safety_identifier"` (new vocabulary value) |
| `stop`, `n > 1` | not supported | 400, 400 | loud |
| stream usage | `stream_options.include_usage` | usage on a final choices-empty chunk | `stream_usage="include"` |

### `meta-anthropic` (Messages)

| lm15 knob | Meta wire | Live | Decision |
|---|---|---|---|
| thinking | `thinking: {type: adaptive}` + `output_config.effort`; `enabled + budget_tokens` accepted, **not translated** | adaptive+low 200; `enabled`+1024 budget 200 (`probe-thinking-enabled-budget`) | new `thinking_format="adaptive"`: every model is the adaptive class, no model-name table; `thinking_budget` raises (silent no-op, MAP-8) |
| thinking blocks | `redacted_thinking` only (encrypted); `display: summarized` default | every body: `redacted_thinking` + `text`, no visible summary | replayed verbatim as thinking blocks; `multi_turn_tool_result` 200 |
| `cache_control` marks | undocumented on this wire | hand-sent mark: 200, `cache_creation_input_tokens: 0`, `cache_read_input_tokens: 369` (`probe-cache-control-mark`) — ignored, cache is implicit | `cache_control="none"` (the DeepSeek precedent: not placed, not an error) |
| `output_config.format` | json_schema | 200, `{"city":"Paris","country":"France"}` | `structured_output="send"` |
| `disable_parallel_tool_use` | documented | 200 (`probe-parallel-false`) | `parallel_tool_calls="send"` |
| `top_k`, `stop_sequences` | not supported | 400, 400 | loud |
| `user_id` | `metadata.user_id` (also the safety identifier) | 200 | existing mapping |
| auth | bearer | 200; 401 without | `auth_header="bearer"` |

## What Meta offers that lm15 does not wire

- **Speech-to-text** (`muse-voice-transcribe-1.0`): `POST /v1/asr/transcribe`
  (multipart) and `wss://api.meta.ai/v1/asr/realtime` — Meta's own event
  vocabulary (`speechStart`, `transcript`, `speechEnd`, `speechComplete`,
  `speaker`; `guide--speech-to-text.md`).  lm15 has no transcription
  surface (`EndpointSupport.speech` means text-to-speech).  Adding one is a
  design pass (`playbooks/design-pass.md`): canonical request/response types,
  a new `EndpointSupport` column, and every port — not a provider entry.
- **Token counting** (`POST /v1/responses/input_tokens`,
  `/v1/messages/count_tokens`): lm15 has no count-tokens door.
- **Background responses**, `previous_response_id`, response retrieval /
  cancel / delete: server-managed state lm15's stateless model does not use.
- **Tool search** (`defer_loading`), **video understanding** input,
  **image understanding** input: the first is a new tool kind; the other two
  are input parts the dialects may already carry but were not captured here.
- **Muse Glimmer**: open weights, served through vLLM / SGLang / llama.cpp —
  reach it through `vllm:` / `sglang:` / `ollama:`, not through `meta`.

## Terms-of-service review — OPEN

`dev.meta.ai/legal` is a rendered application (no Markdown endpoint, no
`.md` mirror; `curl` returns an empty shell) and the trusted browser was
unavailable during this pass, so no terms text was frozen under `sources/`.
What the docs themselves state (`pricing-rate-limits.md`, `models.md`):

- Standard tier (`muse-spark-1.3`, `-1.2`, `-1.1`, `muse-image-1.0`):
  "your prompts and completions are not used to train Meta models".
- Contributor tier (`muse-spark-1.3-contributor`, `-1.2-contributor`):
  discounted "in exchange for permission to use your prompts and completions
  to train future Meta models".  lm15 registers no default model; a user
  who types `-contributor` chose it.
- Pay-as-you-go, per-token / per-image / per-audio-hour; rate limits are
  per team, shared by every key on the team.
- HTTP 402 on a billing problem (`error-handling.md`).

**Before `supported`:** a reviewer opens `dev.meta.ai/legal` in a browser,
freezes the developer terms and privacy policy under
`research/providers/meta/sources/` with sha256, and writes the verdict here
(the Z.AI and DeepSeek dossiers are the shape).

## Open items

- `store` defaults to `true` on the Responses wire (Meta keeps the
  conversation server-side; `protocols--responses.md`).  lm15 sends
  nothing unless `Config.store` is set — the same as for OpenAI, whose
  default is also `true`.  A user who wants no server copy sets
  `store=False`; live, that still returned `encrypted_content`, so
  stateless replay keeps working.
- `reasoning.summary`: `auto` returned a one-sentence summary
  (`reasoning_summary` case); `concise` / `detailed` not probed.
- Streaming: the Responses stream carries `response.output_item.added/done`
  for the reasoning item and no reasoning deltas; lm15 emits 3 events for
  "Say ok." (start, one text delta, end).  Mid-stream `error` events
  (`server_shutting_down`) were not observed.
- `phase: "commentary"` is reconstructed from structure (assistant text
  followed by a tool call in the same turn), not preserved from the
  response — lm15's `TextPart` carries no provider state, and adding some
  is a canonical-type change (a design pass), not a compat knob.  Where the
  rule fires it is Meta's own definition, so it cannot mis-tag; it
  **under-fires** for text before a provider-executed tool (the
  `web_search` probe: `message(commentary)` → `web_search_call` → …), since
  lm15 drops `web_search_call` items and that text replays untagged.
  Live, untagged replay answers 200; the documented cost is quality.
- Image `size` is an aspect-ratio hint (output is always 1600×1600 here);
  `output_format` / `reasoning_strength` / `moderation` ride `extensions`.
