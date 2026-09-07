---
meta:
  title: Chat completion
  description: Send messages and receive model-generated responses using the chat completions endpoint.
  keywords: chat completion, messages, conversation, OpenAI compatibility, developer message, instructions
cms:
  alias: /model-api/docs/protocols/chat-completions
  target: aidmc
---

# Chat completion

Ship conversational features with the core Meta Model API endpoint. You send a structured list of messages and get back a model-generated reply. The endpoint is OpenAI-compatible: point the OpenAI Python SDK or any OpenAI-compatible client at the Model API base URL and keep the rest of your code.

Use Chat Completions for single-turn prompts or simple multi-turn exchanges that drop into existing OpenAI code. When you need reasoning to carry across turns for tool loops, coding assistants, search grounding, or file inputs, use the [Responses API](/docs/protocols/responses).

Chat Completions serves the [Muse Spark](/docs/models#muse-spark) text models. For which models run on which endpoint, see [model availability](/docs/models#model-availability).

> [!NOTE] Muse Spark always reasons
> Muse Spark is a reasoning model that thinks internally to improve response quality. Control how much it thinks with `reasoning_effort`. Muse Spark always reasons, so `reasoning_effort: "none"` returns `HTTP 400`. Chat Completions does not carry reasoning across turns. For agentic and multi-step workflows that need continuity, use the [Responses API](/docs/protocols/responses).

## How it works {#how-it-works}

Every request contains a `messages` array. Each message has a `role` and `content`. The model reads the full array in order and generates the next turn.

Five roles are supported:

- **`user`**: input from the end user that the model responds to.
- **`assistant`**: a prior model response you include when replaying history.
- **`developer`**: your behavior instructions for tone, persona, output format, and constraints. This is the highest-precedence role you can set.
- **`system`**: accepted for OpenAI compatibility and treated at the same level as `developer`, so it carries no extra precedence. Prefer `developer`.
- **`tool`**: result of a tool the model invoked, with the `tool_call_id` it answers. See [tool calling](/docs/tool-calling).

The model processes the full sequence on every request. It has no built-in memory between requests. You control context by choosing what to include in `messages`.

### Instruction messages {#system-messages}

Use `developer` messages to set standing rules for the conversation: persona, output format, topic boundaries, reference data. They work by role, not position, so they do not need to appear first.

**`developer` outranks `user`.** When instructions conflict, `developer` wins. The `system` role is kept for compatibility and is merged at the same level as `developer`. Think of `developer` as the function definition and `user` as the arguments it operates on.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "developer",
            "content": "You are a senior backend engineer reviewing pull requests. For each code snippet the user shares, respond with: 1) a one-line summary of what the code does, 2) any bugs or issues, 3) one concrete improvement suggestion. Be direct. Do not repeat the code back.",
        },
        {
            "role": "user",
            "content": "def div(a, b):\n    return a / b",
        },
    ],
)

print(response.model_dump_json(indent=2))
```

Include a `developer` message in most apps. A clear instruction message improves quality consistently and cuts down on corrective prompting later.

## Basic usage {#basic-usage}

A minimal request needs `model` and `messages`.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "user",
            "content": "What are three differences between TCP and UDP?",
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.chat.completions.create({
  model: 'muse-spark-1.3',
  messages: [
    {
      role: 'user',
      content: 'What are three differences between TCP and UDP?',
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "messages": [
            {
                "role": "user",
                "content": "What are three differences between TCP and UDP?",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "messages": [
    {
      "role": "user",
      "content": "What are three differences between TCP and UDP?"
    }
  ]
}'
```


#### Example response

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1714502400,
  "model": "muse-spark-1.1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here are three key differences between TCP and UDP..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 19,
    "total_tokens": 44
  }
}
```

The response matches the OpenAI chat completions shape. Generated text lives at `response.choices[0].message.content`.

## Streaming {#streaming}

By default the API returns the complete response in one payload. For long responses, stream tokens incrementally via server-sent events (SSE) so you can render output as it arrives.

Set `stream=True` to enable streaming:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

stream = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "user",
            "content": "Explain how garbage collection works in Python.",
        },
    ],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const stream = await client.chat.completions.create({
  model: 'muse-spark-1.3',
  messages: [
    {
      role: 'user',
      content: 'Explain how garbage collection works in Python.',
    },
  ],
  stream: true,
});

for await (const chunk of stream) {
  const delta = chunk.choices[0]?.delta?.content;
  if (delta) {
    process.stdout.write(delta);
  }
}
process.stdout.write('\n');
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    },
    json={
        "model": "muse-spark-1.3",
        "messages": [
            {
                "role": "user",
                "content": "Explain how garbage collection works in Python.",
            },
        ],
        "stream": True,
    },
    stream=True,
)
response.raise_for_status()

for raw_line in response.iter_lines(decode_unicode=False):
    if not raw_line:
        continue
    line = raw_line.decode("utf-8", errors="replace")
    if not line.startswith("data: "):
        continue
    data = line.removeprefix("data: ")
    if data == "[DONE]":
        break
    chunk = json.loads(data)
    delta = chunk["choices"][0].get("delta", {}).get("content")
    if delta:
        print(delta, end="", flush=True)
print()
```
```shell title="curl"
curl -N -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
  "model": "muse-spark-1.3",
  "messages": [
    {
      "role": "user",
      "content": "Explain how garbage collection works in Python."
    }
  ],
  "stream": true
}'
```


Each chunk carries a `delta` with the next piece of content. The final chunk includes `finish_reason`.

Use streaming for chat UIs, CLIs, and anywhere perceived latency matters. Streaming changes when you start seeing text, not total generation time.

Streaming also sidesteps the server-side non-streaming time limit: a non-streaming request that runs too long returns [`HTTP 504` (`gateway_timeout`)](/docs/error-handling#504), whereas streaming requests are exempt. For long or large generations, set `stream=True`.

## Multi-turn conversations {#multi-turn}

For multi-turn chat, append each new user message and each assistant reply to the `messages` array and send the full array on every turn.

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

messages = [
    {"role": "developer", "content": "You are a concise coding tutor."},
    {"role": "user", "content": "What is a Python decorator?"},
]

# First turn
response = client.chat.completions.create(
    model="muse-spark-1.1",
    messages=messages,
)

assistant_reply = response.choices[0].message.content
print("Assistant:", assistant_reply)

# Append the assistant's response and the next user message
messages.append({"role": "assistant", "content": assistant_reply})
messages.append({"role": "user", "content": "Show me an example that logs function execution time."})

# Second turn
response = client.chat.completions.create(
    model="muse-spark-1.1",
    messages=messages,
)

print("Assistant:", response.choices[0].message.content)
```

The model sees the full history each time, so the second answer can reference the first. You own the array; the API does not retain state between requests.

> [!NOTE] Use Responses for agentic work
> For agentic and multi-step work, use the [Responses API](/docs/protocols/responses) instead. It preserves reasoning across turns with stateless encrypted replay and can manage history for you with `previous_response_id`.

### Managing conversation length

Messages accumulate tokens, which increases latency, cost, and pressure on the context window. Two patterns help you stay within budget: keep a **sliding window** that always retains `developer` and `system` instructions while trimming older user and assistant pairs past a threshold, or periodically **summarize** the conversation into a single assistant message and continue from there.

## Conversation structure {#conversation-structure}

The API validates that `messages` is well-formed. When it cannot safely interpret a sequence, it returns `HTTP 400` instead of guessing.

The most common issue for tool-using apps:

- When an `assistant` message contains `tool_calls`, send one `tool` message per call with the matching `tool_call_id` before the next `assistant` turn. Include the full assistant message with its `tool_calls` when you replay history. Omitting it returns `HTTP 400`. See [tool calling](/docs/tool-calling#multi-turn-tool-results).

Send clean history and fix forward on `400`. See [error handling](/docs/error-handling#invalid-conversation-structure) for the full list of structural checks.

## Parameters {#parameters}

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | -- | The model to use for completion (such as `muse-spark-1.1`). |
| `messages` | array | Yes | -- | The conversation history. Each element is an object with `role` and `content`. |
| `temperature` | number | No | 1.0 | Controls randomness. Range: 0 to 2. Muse Spark is tuned to run at the default of `1.0` and performs best there; leave it unset for most workloads. To make output more focused, prefer clearer instructions over lowering `temperature`. |
| `top_p` | number | No | 1.0 | Nucleus sampling threshold. The model considers tokens whose cumulative probability mass reaches `top_p`. Must be greater than 0 (`0 < top_p ≤ 1`); `top_p: 0` returns `HTTP 400`. Leave it at the default of `1.0` for most workloads. Use `temperature` or `top_p`, not both. |
| `frequency_penalty` | number | No | `0` | Penalizes tokens in proportion to how often they have already appeared, reducing verbatim repetition. Range: -2 to 2. |
| `presence_penalty` | number | No | `0` | Penalizes tokens that have already appeared at all, nudging the model toward new topics. Range: -2 to 2. |
| `max_completion_tokens` | integer | No | Model-dependent | Maximum number of tokens to generate. The response may be shorter if the model reaches a natural stopping point. The deprecated alias `max_tokens` is still accepted. `max_output_tokens` is a Responses API parameter and is rejected on Chat Completions. |
| `stream` | boolean | No | `false` | When `true`, the response is delivered as server-sent events. See [Streaming](#streaming). |
| `reasoning_effort` | string | No | model-set | Controls how much reasoning the model performs before answering. Accepted values: `"none"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`. When omitted, the model reasons by default; set this parameter to control how much. `"none"` (disable reasoning) is **not supported by Muse Spark** and returns `HTTP 400`. |
| `seed` | integer | No | `null` | If specified, the system makes a best-effort attempt at deterministic results. Determinism is not guaranteed. |
| `n` | integer | No | `1` | Number of completions to generate. Only `n=1` is supported; values greater than 1 return `HTTP 400`. |
| `prompt_cache_retention` | string | No | `null` | Hint for prompt-cache retention. Accepted values: `"in_memory"`, `"24h"`. Actual retention is managed server-side. |
| `safety_identifier` | string | No | `null` | A stable, privacy-preserving identifier for the end user behind the request (up to 64 characters). Lets Meta target any usage-policy enforcement at that individual user rather than your whole application. Recommended but not required; hash usernames or emails before sending. See [Safety identifiers](/docs/protocols/responses#safety-identifiers). |
| `prompt_cache_key` | string | No | `null` | Groups related requests to improve prompt-cache hit rates. Replaces the caching role of the deprecated `user` field. |
| `user` | string | No | `null` | **Deprecated.** A stable end-user identifier, superseded by `safety_identifier` (abuse detection) and `prompt_cache_key` (caching). Still honored: when both `user` and `safety_identifier` are sent, `safety_identifier` takes precedence. |
| `logprobs` | boolean | No | `false` | Log probabilities for each output token. Muse Spark is a reasoning model, so this is not supported — `logprobs: true` returns `HTTP 400`. |
| `top_logprobs` | integer | No | `null` | Number of most likely tokens to return at each position (0-20). Requires `logprobs: true`. |

For the full parameter reference, including `tools`, `response_format`, and `tool_choice`, see the [Chat completions API reference](/docs/api-reference/chat-completions).

> [!NOTE] Keep default sampling
> Muse Spark is tuned to run at the default sampling settings (`temperature: 1.0`, `top_p: 1.0`) and performs best there. Leave both unset unless you have a specific reason to change them, and adjust only one — `temperature` or `top_p`, not both. To make output more focused or repeatable, prefer clearer instructions (and `seed` for best-effort reproducibility) over lowering `temperature`.

> [!NOTE] Output and input share the budget
> Your output-token limit (`max_completion_tokens`, or the deprecated `max_tokens` alias) shares the model's context window with the input: `input_tokens` plus the requested output tokens must fit within the context window. Don't set it to the full context window when the request has any input: the two share one budget. Requesting more than the model's configured maximum returns `HTTP 400`. See [error handling](/docs/error-handling#context-window-exceeded).

## Error handling {#error-handling}

The API returns standard HTTP codes with an OpenAI-style error envelope. With chat completions you will most often see:

- **`400` Bad Request**: Invalid type or value, such as non-integer `top_logprobs`, `top_p: 0`, or `n` greater than `1`; an unsupported parameter; malformed conversation structure; or **context length exceeded** when input plus requested output tokens exceed the model's context window. Fix the request before retrying.
- **`429` Too Many Requests**: Rate limit exceeded. Retry with exponential backoff and jitter.

For the full set of codes, error shapes, and remediation including the context-window-exceeded format, see [error handling](/docs/error-handling).

## OpenAI compatibility notes {#openai-compatibility}

Model API accepts OpenAI-compatible requests by default. A small set of OpenAI parameters is not supported and returns `HTTP 400`:

| Parameter | Notes |
|-----------|-------|
| `stop` | Not supported on reasoning models. This matches OpenAI's behavior on `o3` and `o4-mini`. |
| `n` greater than `1` | Parallel sampling is not supported. Only `n=1` is allowed. |
| `verbosity` | Not implementable without model retraining. |
| `logit_bias` | Unsupported on reasoning models. |
| `prediction` | Unsupported on reasoning models. |
| `web_search_options` | Search grounding is not available on Chat Completions. Use the Responses API with the tools-based `web_search` built-in tool instead. See [search grounding](/docs/search-grounding). |
| `modalities` | Not supported; any value returns `HTTP 400`. |
| `audio` | No audio output. |

Sending `text.format`, which belongs to the Responses API, to the Chat Completions endpoint also returns `HTTP 400`. Use `response_format` for structured output here. See [structured output](/docs/structured-output).

Model API validates conversation structure more strictly than some providers. A `messages` array accepted elsewhere may return `HTTP 400` here, and the reverse. The most frequent case is tool-call replay: keep each assistant `tool_calls` message paired with its `tool` results. See [Conversation structure](#conversation-structure).

## Go beyond text generation {#beyond-text-generation}

Chat Completions handles plain text generation. When you need more, use a focused feature:

- Need valid JSON that matches a schema? Use [structured output](/docs/structured-output).
- Need the model to call your functions? Use [tool calling](/docs/tool-calling).
- Need the model to analyze images? Use [image understanding](/docs/image-understanding).
- Need answers grounded in live web data? Use [search grounding](/docs/search-grounding) via the [Responses API](/docs/protocols/responses).

## Next steps

- Shape reasoning for quality and cost with [reasoning](/docs/reasoning) and carry chain-of-thought across turns.
- Move stateful, multi-turn flows to the [Responses API](/docs/protocols/responses) and use `previous_response_id`.
- Lock output to a JSON schema with [structured output](/docs/structured-output).
- Wire up external actions with [tool calling](/docs/tool-calling) for reliable agent loops.
- Check the [Chat completions API reference](/docs/api-reference/chat-completions) for the full request and response schema.