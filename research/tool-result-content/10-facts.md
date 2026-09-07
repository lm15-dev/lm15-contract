# Tool-result content — fact sheets

Same columns for every binding. A cell cites a `sources/manifest.json` id
(`[id]`), a receipt under `receipts/2026-09-07-tool-result-media/` (`[rx:…]`,
detail in `20-results.json`), or says **blank**. Blank cells are findings.
`[browser-read]` marks a source the fetch could not save (403); it was read
in-session only and a rule never rests on it alone.

Columns:

- **Wire slot** — where a tool result's non-text content goes on the
  request schema, per the provider's own reference.
- **Kinds** — media kinds the slot documents.
- **Status** — how `is_error` is expressed.
- **Name** — whether the wire needs the function name on the result.
- **Model gate** — documented model restrictions.
- **Live** — what the matrix observed (cell → outcome).

## Responses dialect

| Binding | Wire slot | Kinds | Status | Name | Model gate | Live |
|---|---|---|---|---|---|---|
| openai | `function_call_output.output` string **or** array of `input_text`/`input_image`/`input_file` [openai-responses] | image, file | none on the wire (blank) | not needed (`call_id`) | vision models only; docs do not enumerate (blank) | see 20-results: gpt-4.1-mini, gpt-5.4-mini, gpt-5.4 |
| openai-codex | same wire; Codex's own client sends `InputImage` inside `FunctionCallOutput` [codex] | image (implementation) | blank | not needed | blank | 20-results |
| azure | Azure v1 Responses is the OpenAI wire [azure]; array form not separately documented (blank) | inherits | blank | not needed | deployment-dependent | 20-results |
| moonshotai-responses | Responses wire; array form **blank** in Kimi docs [kimi-index][browser-read] | blank | blank | not needed | kimi-k3 only (registry note) | 20-results |
| meta | `FunctionCallOutputItemParam.output`: text **or** `FunctionCallOutputContentListParam` = input_text/input_image/input_file [meta-responses] | image, file | blank | not needed | muse-spark | 20-results |

## Chat Completions dialect

| Binding | Wire slot | Kinds | Status | Name | Model gate | Live |
|---|---|---|---|---|---|---|
| openai-chat | `ChatCompletionToolMessageParam.content`: string or **text parts only** [openai-chat] | none | blank | not needed (`tool_call_id`) | — | 20-results (200 + no answer = silent degrade) |
| azure-chat | OpenAI Chat schema [azure] | none | blank | not needed | deployment-dependent | 20-results |
| xai | tool `Message.content` → `Content` → `ContentPart` incl. image [xai] | image (schema) | blank | not needed | vision models | 20-results |
| groq | SDK: tool content → generic content-part union incl. image [groq-tool][groq-parts]; **server: 400 "must be a string"** [rx:groq/pair] | schema says image; server says none | blank | not needed | — | tool_result_rejected |
| openrouter | `ChatToolMessage.content` → `ChatContentItems` → `ChatContentImage` [openrouter][browser-read] | image (schema) | blank | not needed | upstream-dependent | blocked: 401 (account) |
| deepseek | tool `content` is a string [deepseek-chat] | none | blank | not needed | — | 200, model reports `[Unsupported Image]` |
| zai | blank (API reference rendering did not expose the tool branch) [zai-api]; GLM-4.6V advertises "visual comprehension of tool outputs" [zai-model] | blank | blank | not needed | glm-4.6v | 20-results |
| moonshotai | K2.6 quickstart shows a `role: tool` content array with `video_url` [kimi-tools][browser-read] | video (doc), image (inferred) | blank | not needed | kimi-k2.6 | 20-results |
| meta-chat | `ChatCompletionRequestToolMessage.content`: string or text parts only [meta-chat] | none | blank | not needed | — | 400 "did not match any supported type" |
| bedrock-chat | Chat door, OpenAI schema; tool content string [bedrock-tools] | none | blank | not needed | per model | 400 validation_error |
| bedrock-mantle-chat | same door family [bedrock-mantle] | blank | blank | not needed | per model; grok-4.3 "isn't supported on this route" [rx] | blocked |
| ollama | `openai.go` accepts image arrays on any role but builds those messages **without** `ToolCallID` [ollama] | image (parsed) | blank | `name` or lookup by id | model-dependent | 20-results |
| vllm | `chat_utils.py` keeps `tool_call_id`, parses multimodal parts before role handling [vllm] | image (parser) | blank | not needed | template-dependent | blocked: no server |
| sglang | generic message type: role tool + multimodal content array + `tool_call_id` [sglang] | image (schema) | blank | not needed | template-dependent | blocked: no server |

## Anthropic Messages dialect

| Binding | Wire slot | Kinds | Status | Name | Model gate | Live |
|---|---|---|---|---|---|---|
| anthropic | `tool_result.content`: string or blocks: text, image, document, search_result… [anthropic-type] (SDK `ToolResultBlockParam`) | image, document | `is_error: true` | not needed (`tool_use_id`) | — | 20-results |
| claude-code | same wire, subscription policy | inherits | `is_error` | not needed | — | 20-results |
| deepseek-anthropic | compatibility table: image blocks ✓, tool_result.content ✓; nested media example blank [deepseek-anthropic] | blank | `is_error` (table) | not needed | — | 200, model reports `[Unsupported Image]` |
| moonshotai-anthropic | Messages wire; nested media blank [kimi-messages][browser-read] | blank | blank | not needed | kimi-k3 | 20-results |
| meta-anthropic | `AnthropicContentBlock` open union naming image, document, tool_result; nesting not specified [meta-messages] | blank | blank | not needed | — | 20-results |
| azure-anthropic | Messages wire on Foundry [azure-anthropic][browser-read] | inherits | `is_error` | not needed | deployment | blocked: DeploymentNotFound |
| aws-anthropic | "same request shape" [aws-anthropic][browser-read] | inherits | `is_error` | not needed | — | blocked: host settings |
| bedrock-anthropic | Mantle Messages [bedrock-anthropic][browser-read] | inherits | `is_error` | not needed | — | blocked: 403 |
| vertex-anthropic | rawPredict Messages [vertex-anthropic][browser-read] | inherits | `is_error` | not needed | — | blocked: OAuth refresh 400 |

## Gemini dialect

| Binding | Wire slot | Kinds | Status | Name | Model gate | Live |
|---|---|---|---|---|---|---|
| gemini | `functionResponse.parts[]` with `inlineData`; `response` may `$ref` a part by `displayName` [gemini] | image/png, jpeg, webp; application/pdf, text/plain [gemini] | `response.error` key (function-calling reference) | **required** (`functionResponse.name`) | **Gemini 3 series only** [gemini] | 20-results: 3.7-flash and 2.5-flash |
| vertex | same, plus `fileData`; Preview [vertex] | same + fileData | `response.error` | required | Gemini 3 and later [vertex] | blocked: OAuth refresh 400 |
| vertex-express | same wire, express host [vertex-express] | same | same | required | same | blocked: no GOOGLE_API_KEY |

## Blank cells that matter

- No Chat-dialect server documents an error flag on a tool message; no
  Responses server does either. Status must ride in the text on those wires.
- Kimi, Z.AI and Meta-Messages document nothing about nested media in a
  tool result; the live column is the only evidence for them.
- Gemini requires the function **name** on a result and lm15's
  `ToolResultPart.name` is optional: the adapter resolves it from the
  matching call in the transcript (never `"tool"`).
