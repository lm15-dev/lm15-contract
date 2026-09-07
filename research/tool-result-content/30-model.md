# Tool-result content — the abstract model and every provider's cell

## The model

A `ToolResultPart` is `(id, content: [Part…], is_error, name?)`. On every
wire it becomes one **result item** that carries:

| Canonical | Must survive as |
|---|---|
| `id` | the wire's call reference (`call_id`, `tool_use_id`, `tool_call_id`, `functionResponse.id`) |
| `content` order | the order of blocks/parts inside the result item |
| each text part | a text block |
| each image / document part | a native media block **inside the result item** |
| `is_error` | the wire's error mechanism; where the wire has none, the text carries it and the mapping says so |
| `name` | `functionResponse.name` where required, resolved from the transcript's matching call when the caller gave none |

Two outcomes exist per (dialect, part kind): **native** (a block inside the
result item) or **raise** (`UnsupportedFeatureError` before any wire). There
is no `extension` door: a message part is not a knob, and a caller cannot
"pass provider syntax through extensions" for something that lives inside a
message.

Text-only content stays a string where the wire takes a string (the
ratified text cell; every provider passed it, 20-results `text`).

## Verdicts per dialect

Verdicts come from the request schema (question 1 of the frame) and the
live matrix (question 2). Model quality (question 3) is recorded, never a
verdict. `[rx]` = 20-results.md row.

### Responses dialect — `function_call_output.output` array

| Part kind | Verdict | Evidence |
|---|---|---|
| text | native (string when text-only, `input_text` in an array otherwise) | schema [openai-responses]; `text` cell OK on every Responses binding |
| image | **native** `input_image` (data URI / URL / file_id; `detail` when set) | doc [openai-responses]; openai gpt-5.4 image/mixed/pair OK at 256px/high [rx]; meta OK; moonshotai-responses OK; codex received (5/6, mini model) |
| document | **native** `input_file` (`file_data` + filename / file_id / file_url) | doc; openai `pdf` OK on gpt-4.1-mini and gpt-5.4 [rx]. Kimi Responses: 400 "unknown content part type input_file" → the preset says `reject` for documents |
| audio / video / binary | raise | no slot documented for a function output (blank) |
| `is_error` | text carries it: the output is prefixed `[error] ` (stated in MAP-10) | wire has no flag (blank); `error` cell err-OK on openai, codex, meta, moonshotai-responses |

Per-binding knob (`OpenAIResponsesCompat.tool_result_media`): openai, codex,
azure, meta = `native`; moonshotai = `native` for images, documents
`reject`. Model gating (gpt-4.1-mini 5/6, mini models) is the model's
vision, not the mapping; no allowlist.

### Chat Completions dialect — `role: tool` content

| Part kind | Verdict | Evidence |
|---|---|---|
| text | native string | schema; `text` cell OK everywhere |
| image | **per preset**: `native` = content array with `image_url`; `reject` = raise | xai, moonshotai, zai, meta-chat…: see table below |
| document | per preset; only where the server documents a `file` part on a tool row | xai 400 "use /v1/responses"; kimi 400; openai-chat 400; zai 400 → `reject` everywhere today |
| audio / video / binary | raise (kimi documents `video_url` on a tool row [kimi-tools][browser-read]; not exercised → not ratified) | |
| `is_error` | text carries it (`[error] ` prefix) | `error` cell err-OK on every chat binding that answered |

| Preset | `tool_result_media` | Evidence |
|---|---|---|
| openai (openai-chat, azure-chat) | **reject** | schema text-only [openai-chat][meta-chat-like]; 200 + content not received on gpt-4.1-mini, gpt-5.4 at both oracles while the same model read the USER image [rx control] → silent degrade |
| xai | native (image) | image/mixed/pair OK [rx] |
| moonshotai | native (image) | image/mixed/pair OK [rx] |
| zai | native (image) | image/mixed OK; pair blocked (single tool call returned) [rx] |
| meta | reject | 400 [rx] |
| groq | reject | 400 "must be a string" [rx], schema says otherwise [groq-parts] — the server wins |
| deepseek | reject | 200 + `[Unsupported Image]` at both oracles [rx] — silent degrade |
| bedrock, bedrock-mantle | reject | 400 validation_error [rx]; mantle blank |
| openrouter | reject until a receipt | schema native [openrouter][browser-read]; account blocked (401) |
| ollama | reject until a receipt | source drops `ToolCallID` on image rows [ollama]; live: timeouts on a 0.8b model (blank) |
| vllm, sglang | reject until a receipt | parser/schema native [vllm][sglang]; no server reachable (blank) |

### Anthropic Messages dialect — `tool_result.content` blocks

| Part kind | Verdict | Evidence |
|---|---|---|
| text | native | |
| image | **native** `image` block | doc [anthropic-type]; anthropic, claude-code, meta-anthropic, moonshotai-anthropic OK [rx] |
| document | native `document` block, `reject` on presets whose server 400s | anthropic, claude-code, meta-anthropic OK; moonshotai-anthropic 400 "unsupported content type … document" [rx] |
| audio / video / binary | raise | not in `ToolResultBlockParam` [anthropic-type] |
| `is_error` | native `is_error: true` | err-OK on every Messages binding [rx] |

`deepseek-anthropic`: 200 + `[Unsupported Image]` → preset `reject` for
media (silent degrade). The rest: `native`.

### Gemini dialect — `functionResponse.parts`

| Part kind | Verdict | Evidence |
|---|---|---|
| text | native: `response.result` | |
| image / document | **native**: nested `parts[]` with `inlineData` (`fileData` for a `file_id`; `path` read and inlined) | doc [gemini][vertex]; gemini-3.7-flash image/mixed/pair/pdf OK [rx] |
| model gate | **none in lm15**: Gemini 2.5 answers HTTP 400 "Multimodal function responses are not supported for this model" [rx] — the loud failure is the contract (MAP-5 precedent) | |
| audio / video / binary | raise (MIME list is images + pdf + text/plain [gemini]) | |
| `is_error` | native: `response: {"error": <text>}` | doc (function-calling reference: an `error` key); err-OK on 3.7-flash [rx] |
| `name` | required; resolved from the matching `functionCall` in the transcript; never `"tool"` | |
| ordering | text goes in `response`, media in `parts`; interleaving is expressed with `$ref` by `displayName` when a text part follows a media part (documented; not exercised → a **stated deviation**: lm15 emits media after text and does not emit `$ref`) | |

## Cross-cutting rules the cells imply

1. **The threshold is "the model received it", not HTTP 200.** DeepSeek and
   OpenAI Chat both return 200 and lose the image. Both are `reject`.
2. **A generated SDK's schema is not evidence of a server.** Groq.
3. **Model gating is the provider's job when it fails loudly** (Gemini 2.5).
   lm15 keeps no model allowlist for tool-result media.
4. **Model quality is not a mapping verdict.** gpt-4.1-mini at 5/6, the
   Codex mini at 5/6: the image reached the model.
5. **Refusals are per preset, typed, and name the door.** The error message
   says which sibling dialect carries it (xai's own 400 does exactly this).
