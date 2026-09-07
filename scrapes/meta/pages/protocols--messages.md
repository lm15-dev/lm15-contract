---
meta:
  title: Messages API
  description: Call Muse Spark with the Messages API, the Anthropic Messages-compatible endpoint on Meta Model API.
  keywords: Messages API, Anthropic compatibility, Claude SDK, /v1/messages, count_tokens, thinking
cms:
  alias: /model-api/docs/protocols/messages
  target: aidmc
---

# Messages API

Build with [Muse Spark](/docs/models#muse-spark) through an Anthropic-compatible interface. The Messages API lets you run Muse Spark with the Anthropic SDK and Claude-oriented tools: swap the base URL and key and keep the rest of your code. Requests shaped for Anthropic's `/v1/messages` run on Meta Model API unchanged. The Messages API serves the Muse Spark text models; see [model availability](/docs/models#model-availability) for the full model-to-endpoint list.

## How it works {#how-it-works}

The Messages endpoint is a thin wire-format adapter over the same pipeline that powers the [Responses API](/docs/protocols/responses). We translate your Anthropic request into a Responses request, run it through shared auth, rate limiting, billing, safety, media resolution, and routing, then translate the result back. Only the request and response shape differs.

The adapter is stateless. It always runs with storage off, so there is no server-managed conversation and no `previous_response_id` equivalent. Replay history client-side by appending prior assistant turns to `messages`, exactly as you do against Anthropic.

Every request follows the Anthropic shape:

- **messages**: array of `user` and `assistant` turns, where `content` is a string or an array of [content blocks](#content-blocks).
- **system**: text blocks that set behavior instructions, the Anthropic equivalent of a `developer` message.
- **max_tokens**: required upper bound on tokens generated.
- **thinking**: reasoning control for Muse Spark. See [Reasoning](#reasoning).

See [Request fields](#request-fields) for the full set.

| Setting | Value |
| --- | --- |
| **Base URL** | `https://api.meta.ai` |
| **Endpoints** | `POST /v1/messages`, `POST /v1/messages/count_tokens` |
| **Model** | `muse-spark-1.1` |
| **Auth** | Bearer token (`MODEL_API_KEY`) |

## Basic usage {#basic-usage}

Send `POST /v1/messages` with `model`, `messages`, and the required `max_tokens`. Authenticate with your Model API key as a bearer token. Keep your existing Anthropic SDK setup and point it at Model API — pass the base URL and your key as a bearer token.

```python title="Python (Anthropic SDK)"
import os

from anthropic import Anthropic

client = Anthropic(
    base_url="https://api.meta.ai",
    auth_token=os.environ["MODEL_API_KEY"],
)

message = client.messages.create(
    model="muse-spark-1.3",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        },
    ],
)

print(message.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/messages",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/messages" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ]
}'
```


A successful call returns an Anthropic `message` object:

```json
{
  "id": "msg_abc123",
  "type": "message",
  "role": "assistant",
  "model": "muse-spark-1.1",
  "content": [
    {"type": "text", "text": "The capital of France is Paris."}
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 14,
    "output_tokens": 8
  }
}
```

## Request fields {#request-fields}

- **model** (required): model ID, such as `muse-spark-1.1`.
- **messages** (required): non-empty array. Roles are `user` and `assistant`; `content` is a string or an array of [content blocks](#content-blocks).
- **max_tokens** (required): upper bound on tokens generated. Maps to `max_output_tokens` on the underlying Responses request.
- **system**: string or array of `text` blocks that set behavior instructions. System content accepts text blocks only; any other block type returns `HTTP 400`.
- **temperature**: enforced to Anthropic's `0`–`1` range. **top_p**: passed through. Muse Spark runs best at the default `temperature=1.0`; leave sampling unset for most workloads, and set `temperature` or `top_p`, not both.
- **stream**: when `true`, the response streams as Anthropic SSE events. See [Response](#response).
- **metadata**: string values forwarded to Responses `metadata`. `metadata.user_id` also sets the [safety identifier](/docs/protocols/responses#safety-identifiers) for the request (the Anthropic-native equivalent of `safety_identifier`); values over 64 bytes are stably hashed to fit. Use a privacy-preserving value, such as a hash of an internal user ID.
- **service_tier**: `auto` and `standard_only` accepted; other values return `HTTP 400`.
- **thinking** / **output_config.effort**: reasoning control. See [Reasoning](#reasoning).
- **output_config.format**: `{type: "json_schema", schema}` constrains output to a JSON schema. See [structured output](/docs/structured-output).
- **tools** / **tool_choice**: see [Tools](#tools).

These top-level fields are not supported and return `HTTP 400`: `stop_sequences`, `top_k`, `container`, and `inference_geo`. Unknown top-level fields are also rejected.

## Content blocks {#content-blocks}

**User messages** accept:

- **text**: plain text input.
- **image**: source is `base64`, `url`, or `file` (an uploaded file ID). See [image understanding](/docs/image-understanding).
- **video**: source is `base64`, `url`, or `file`, with optional `fps`. See [video understanding](/docs/video-understanding).
- **document**: source is `base64`, `url`, `file`, `text`, or `content`. See [files](/docs/file-handling).
- **tool_result**: result of a prior tool call, keyed by `tool_use_id`. Maps to `function_call_output` underneath.
- **search_result**: prior search results forwarded as input text.

**Assistant messages** (when you replay prior turns) accept:

- **text**: prior text output.
- **tool_use**: a function call the model made on a prior turn.
- **server_tool_use**: replay of a built-in call, such as `web_search` or `tool_search`, from a prior turn.
- **thinking** / **redacted_thinking**: prior reasoning. `redacted_thinking` carries the encrypted blob; replay it to preserve chain of thought. See [reasoning](/docs/reasoning).

## Reasoning {#reasoning}

Muse Spark always reasons. Control depth with `thinking` and optional `output_config.effort`:

- **thinking: {type: "adaptive"}**: reason at the default effort with a summarized output. Add `output_config.effort` to override depth.
- **output_config.effort**: `low`, `medium`, `high`, and `xhigh` pass through.
- **thinking: {type: "enabled", budget_tokens: n}**: accepted for compatibility but not translated into an effort value. Requires `budget_tokens >= 1024` and `< max_tokens`. Use `output_config.effort` for depth control.
- **thinking: {type: "disabled"}**: requests no reasoning. Muse Spark does not support disabling reasoning, so this returns `HTTP 400`.
- **display**: `summarized` (default) returns a thinking summary; `omitted` returns encrypted reasoning only, with no visible summary.

## Tools {#tools}

The Messages endpoint supports developer-defined and built-in tools:

- **custom**: developer-defined function. Its `input_schema` becomes the function parameters, and it carries `description`, `strict`, and `defer_loading`. See [tool calling](/docs/tool-calling).
- **web_search**: built-in web search for grounded, cited answers. You can pass `user_location`; `allowed_domains`, `blocked_domains`, and `max_uses` return `HTTP 400`. See [search grounding](/docs/search-grounding).
- **tool_search**: built-in deferred-tool discovery. Mark deferrable tools with `defer_loading: true` to let the model load their schemas on demand. See [tool search](/docs/tool-search).

Map `tool_choice` as follows:

- **auto**: model decides whether to call a tool.
- **any**: requires a tool call.
- **none**: drops tools for this turn.
- **disable_parallel_tool_use**: when `true`, prevents parallel tool calls in a single turn. A named tool choice (`{type: "tool"}`) is not supported and returns `HTTP 400`.

## Response {#response}

A response is an Anthropic `message` object:

- **content**: array of blocks. Model text maps to `text`; reasoning maps to `thinking` (`encrypted_content` maps to `redacted_thinking`); a function call maps to `tool_use`; a built-in call such as `web_search_call` or `tool_search_call` maps to `server_tool_use`.
- **stop_reason**: `tool_use` when the model called a tool; `max_tokens` when it hit the output limit; `refusal` when it declined; otherwise `end_turn`.
- **usage**: `input_tokens`, `output_tokens`, `cache_read_input_tokens`, and `output_tokens_details.thinking_tokens` for reasoning tokens.

With `stream: true`, the response streams as the standard Anthropic event sequence: `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, and `message_stop`, with `Content-Type: text/event-stream`.

### Counting tokens {#count-tokens}

`POST /v1/messages/count_tokens` counts the input tokens an Anthropic-format request would consume without generating. Send the same body as `POST /v1/messages` minus the `max_tokens` requirement. The response is `{ "input_tokens": <integer> }`. See [token counting](/docs/token-counting).

## Error handling {#error-handling}

Errors use the Anthropic envelope:

```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "..."
  }
}
```

The `error.type` maps from the HTTP status: `400` is `invalid_request_error`, `401` is `authentication_error`, `403` is `permission_error`, `404` is `not_found_error`, `429` is `rate_limit_error`, `503` is `overloaded_error`, and other `5xx` responses are `api_error`.

## Next steps

- Ship with OpenAI-style requests when you prefer them: use the [Responses API](/docs/protocols/responses) or [Chat Completions](/docs/protocols/chat-completions) over the same models.
- Ground answers in live web data with [search grounding](/docs/search-grounding).
- Connect Muse Spark to your own code with [tool calling](/docs/tool-calling) and on-demand [tool search](/docs/tool-search).
- See the full request and response shape in the [Messages API reference](/docs/api-reference/messages/create-message).