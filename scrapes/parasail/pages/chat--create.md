> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/api-reference/chat-completions.md).

# Chat Completions

OpenAI-compatible chat completions API for serverless and dedicated model inference.

Parasail provides a fully OpenAI-compatible chat completions endpoint. Point your existing OpenAI SDK at Parasail's base URL—no code changes needed beyond the URL and API key.

## Endpoint compatibility matrix

The table below shows which Parasail products serve each OpenAI-compatible endpoint. All endpoints share the same base URL (`https://api.parasail.io/v1`) and the same bearer-token authentication.

| Endpoint                    | Serverless | Dedicated      | Batch                  |
| --------------------------- | ---------- | -------------- | ---------------------- |
| `POST /v1/chat/completions` | Yes        | Yes            | Yes                    |
| `POST /v1/completions`      | Yes        | Yes            | Yes                    |
| `POST /v1/embeddings`       | Yes        | Yes            | Yes                    |
| `POST /v1/responses`        | Yes        | Not documented | No                     |
| `GET /v1/models`            | Yes        | Yes            | N/A (listing endpoint) |

Batch serves the `/v1/chat/completions` and `/v1/embeddings` endpoints through JSONL input files. See the [Batch API reference](/parasail-docs/api-reference/batch-api.md).

This repository documents Responses API usage for the standard gateway and serverless docs. Dedicated Responses API support is not documented.

## Endpoint

```
POST https://api.parasail.io/v1/chat/completions
```

## Authentication

All requests use bearer-token authentication. Pass your API key in the `Authorization` header:

```
Authorization: Bearer <PARASAIL_API_KEY>
```

The OpenAI SDK reads this from the `api_key` argument. See [Authentication](/parasail-docs/api-reference/authentication.md) for how to create and store a key.

## Request

### Python (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)

response = client.chat.completions.create(
    model="parasail-deepseek-r1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of New York?"}
    ],
    max_completion_tokens=1024,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### cURL

```bash
curl https://api.parasail.io/v1/chat/completions \
  -H "Authorization: Bearer $PARASAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "parasail-deepseek-r1",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of New York?"}
    ],
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```

## Request parameters

| Parameter            | Type    | Default  | Description                                                      |
| -------------------- | ------- | -------- | ---------------------------------------------------------------- |
| `model`              | string  | required | Model ID (for example, `parasail-deepseek-r1`) or HuggingFace ID |
| `messages`           | array   | required | Array of message objects with `role` and `content`               |
| `temperature`        | float   | 1.0      | Controls randomness (0 = greedy decoding)                        |
| `top_p`              | float   | 1.0      | Nucleus sampling probability mass                                |
| `top_k`              | int     | -1       | Limits token selection to top-k tokens (pass in `extra_body`)    |
| `max_tokens`         | int     | None     | Maximum tokens to generate                                       |
| `repetition_penalty` | float   | 1.0      | Penalizes repeated tokens                                        |
| `presence_penalty`   | float   | 0.0      | Increases likelihood of new tokens                               |
| `frequency_penalty`  | float   | 0.0      | Penalizes frequently occurring tokens                            |
| `seed`               | int     | None     | Fixed seed for reproducible results                              |
| `stream`             | boolean | false    | Stream tokens as they're generated                               |
| `tools`              | array   | None     | Tool/function definitions for function calling                   |
| `tool_choice`        | string  | "auto"   | `"auto"`, `"required"`, `"none"`, or specific tool               |

These fields follow the OpenAI schema. For exhaustive field semantics, see the [OpenAI chat completions reference](https://platform.openai.com/docs/api-reference/chat/create). For sampling-parameter guidance, see [full parameter details](/parasail-docs/api-reference/parameters.md).

## Message roles

| Role        | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `system`    | Sets the model's behavior and persona                        |
| `user`      | The user's input                                             |
| `assistant` | The model's previous response (for multi-turn conversations) |

## Response

A successful request returns a `chat.completion` object. The response shape matches OpenAI:

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1727900000,
  "model": "parasail-deepseek-r1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Albany is the capital of New York."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 9,
    "total_tokens": 33
  }
}
```

| Field                       | Description                                             |
| --------------------------- | ------------------------------------------------------- |
| `id`                        | Unique identifier for the completion                    |
| `choices[].message.content` | The generated text                                      |
| `choices[].finish_reason`   | Why generation stopped (`stop`, `length`, `tool_calls`) |
| `usage`                     | Prompt, completion, and total token counts              |

See the [OpenAI response object reference](https://platform.openai.com/docs/api-reference/chat/object) for every field.

## Streaming

Set `stream: true` to receive tokens as they are generated. The response is a stream of server-sent events. Each event's data is a `chat.completion.chunk` object whose `choices[].delta` carries the incremental content; the stream ends with a `data: [DONE]` line.

```python
stream = client.chat.completions.create(
    model="parasail-deepseek-r1",
    messages=[{"role": "user", "content": "Write a haiku about the sea."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

## Error responses

Errors use OpenAI-compatible status codes and a JSON body with an `error` object (`message`, `type`, `code`).

| Status Code | Description                                                                            |
| ----------- | -------------------------------------------------------------------------------------- |
| `400`       | Malformed request—invalid JSON, missing required field, or unsupported parameter value |
| `401`       | Missing or invalid API key                                                             |
| `403`       | API key lacks access to the requested model or resource                                |
| `404`       | Model or endpoint not found                                                            |
| `429`       | Rate limit or quota exceeded—back off and retry                                        |
| `500`       | Internal server error—retry with exponential backoff                                   |

## Chat completions vs text completions

Parasail supports both endpoints:

* `/v1/chat/completions`—for dialog-based interactions (chatbots, assistants)
* `/v1/completions`—for single-prompt completion (translation, code generation, email drafting)

## Model availability

List available serverless models:

```bash
curl https://api.parasail.io/v1/models \
  -H "Authorization: Bearer $PARASAIL_API_KEY"
```

## Next steps

* [Chat completions guide](/parasail-docs/guides/chat-completions.md)—messages, roles, base vs instruct models, chat templates
* [Tool/function calling guide](/parasail-docs/guides/tool-function-calling.md)—function calling tutorial
* [Structured output guide](/parasail-docs/guides/structured-output.md)—JSON-formatted responses
* [Parameters reference](/parasail-docs/api-reference/parameters.md)—sampling parameters in depth
* [Serverless overview](/parasail-docs/products/overview.md)—using third-party tools like Cline and AnythingLLM
