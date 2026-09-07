---
meta:
  title: Tool calling
  description: Define functions the model can invoke, execute them locally, and return results for the model to incorporate.
  keywords: tool calling, function calling, tools, function execution, agents
cms:
  alias: /model-api/docs/tool-calling
  target: aidmc
---

# Tool calling

Ship agents that call your services mid-conversation. You define the functions, you run them, and the model uses the results to decide what to do next. That loop lets you build multi-turn agents that gather live information, take actions, and adapt based on outcomes.

> [!NOTE] Responses API is recommended
> The [Responses API](/docs/protocols/responses) is the recommended path for tool calling and multi-turn agents: it preserves reasoning across tool turns for stronger multi-step performance and threads calls and results with `previous_response_id` or stateless reasoning replay. If your product or agent harness is built on Chat Completions, tool calling is fully supported there too. The patterns below apply to both endpoints; endpoint differences are called out inline.

This page covers **developer-defined tools**: functions you describe in `tools` and execute in your own code. The API also offers two **built-in tools** that run server-side: `web_search` (see [search grounding](/docs/search-grounding)) and `tool_search` (see [tool search](/docs/tool-search)). You can combine built-in and developer-defined tools in a single request.

## How it works {#how-it-works}

1. You send a request with `tools` containing one or more tool definitions.
2. The model evaluates the user message and decides whether to use a tool.
3. If a tool is needed, the model returns a `tool_calls` array on the assistant message. The array can hold multiple calls, each with a function name and arguments.
4. You execute each call locally and return one result per call as a `tool` message.
5. The model incorporates those results into its next response.

The model does not execute developer-defined tools itself. Your app handles execution for every tool you define in `tools`. The built-in `web_search` tool used by [search grounding](/docs/search-grounding) is the exception: it runs server-side and returns results directly to the model.

## When to use tool calling {#when-to-use-tool-calling}

### Finding information

Give the model access beyond its training data:

- **Real-time data**: Weather, stock prices, sports scores, news headlines.
- **Calculations**: Arithmetic, financial projections, or domain-specific computations.
- **Database access**: Query your own data for pricing, inventory, or customer records.
- **[Web search](/docs/search-grounding)**: Search engines or knowledge bases for general information retrieval.

For web search, [search grounding](/docs/search-grounding) is a built-in alternative that requires no custom tool implementation.

### Performing actions

Let the model trigger side effects on the user's behalf:

- **Sending messages**: Emails, notifications, chat messages.
- **Triggering jobs**: Background workflows, CI/CD pipelines, batch processing.
- **Calling APIs**: External services, payment processors, third-party integrations.

## Defining tools {#defining-tools}

Define tools in `tools` using the `function` or `custom` type. Each `function` tool specifies a name, description, and JSON Schema for its parameters. A `custom` tool takes freeform text input instead of structured JSON parameters — use it when your tool accepts arbitrary text rather than a typed schema.

> [!NOTE] Use tools, not functions
> Use the `tools` parameter, not the deprecated `functions` or `function_call` fields.

With the recommended [Responses API](/docs/protocols/responses), these fields sit at the top level of the tool object:

```json
{
  "type": "function",
  "name": "get_weather",
  "description": "Return current weather for the given location.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City name, e.g. 'Seattle'"
      }
    },
    "required": ["location"],
    "additionalProperties": false
  }
}
```

[Chat Completions](/docs/protocols/chat-completions) uses the same fields but nests them under a `function` key — see [Tool calling with Chat Completions](#chat-completions-tool-calling).

Write clear, specific descriptions for the tool and for each parameter. The model uses them to decide when and how to call the tool.

> [!TIP] Root type is auto-added
> If a function tool's `parameters` schema omits the root `"type": "object"`, Model API adds it before the schema reaches the model, so the tool isn't silently dropped for missing a root type. An explicit root `type` stays unchanged. Declaring `"type": "object"` yourself is still recommended for clarity and portability.

### Custom tools {#custom-tools}

A `custom` tool is a client-defined, client-executed tool that takes **freeform text input** instead of structured JSON parameters. Use it when your tool accepts arbitrary text rather than a typed schema. Custom tools are Responses-API-only; sending `{"type": "custom", ...}` to Chat Completions returns `HTTP 400`.

A `custom` tool carries the same `name`, `description`, `strict`, and `defer_loading` fields as a `function` tool, but omits `parameters`:

```json
{
  "type": "custom",
  "name": "run_shell",
  "description": "Execute a shell command supplied as freeform text."
}
```

Custom tools follow the same `parallel_tool_calls` and `tool_choice` behavior as function tools, and their names are **exempt** from the single-dot restriction described in [Function name rules](#function-name-rules).

## Function name rules {#function-name-rules}

Function tool names must match `^[a-zA-Z0-9_.-]+$` (alphanumeric, underscores, hyphens, and dots) and **contain at most one dot**. Names with two or more dots return `HTTP 400`.

If your tooling uses multi-segment namespaced names, common in MCP and Agents SDK integrations, use a **namespace tool** instead of encoding dots in the function name. The namespace tool groups related functions under a shared prefix: the outer `name` must contain zero dots, while inner function `name` values may contain up to one dot. For a full example of defining and calling a namespace tool, see [Tool search](/docs/tool-search#deferring-tools).

## Tool calling with the Responses API {#responses-api-tool-calling}

Define tools in the flat format shown in [Defining tools](#defining-tools). When the model calls a tool, the response `output` array contains a `function_call` item with the name, arguments, `call_id`, and `status`. `status` is `"in_progress"` while streaming and `"completed"` on the final `output_item.done` event. Return the result in a follow-up request with `previous_response_id` and a `function_call_output` input item referencing `call_id`.

The example below calls the Responses API, executes the returned function call, and returns the result with `previous_response_id`.

```python title="Python (OpenAI SDK)"
import os
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)


def get_weather(location: str) -> dict:
    """Placeholder -- replace with a real API call."""
    return {"location": location, "temperature": "15°C", "condition": "Cloudy"}


tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Return current weather for the given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name",
                }
            },
            "required": ["location"],
        },
    }
]

# First request -- model requests a tool call
response = client.responses.create(
    model="muse-spark-1.1",
    input="What is the weather in Seattle?",
    tools=tools,
)

# Check for function_call items in the output
for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        result = get_weather(**args)

        # Second request -- return the tool result with previous_response_id
        response = client.responses.create(
            model="muse-spark-1.1",
            input=[
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            ],
            previous_response_id=response.id,
            tools=tools,
        )

        print(response.output_text)
        # "The current weather in Seattle is 15°C and cloudy."
```

Key differences from [chat completion](/docs/protocols/chat-completions) tool calling:

- **Flat tool definitions**: `name`, `description`, and `parameters` sit at the top level, not nested under `function`.
- **`function_call` output items**: instead of `tool_calls` on the assistant message, the Responses API returns `function_call` items in the `output` array.
- **`function_call_output` input items**: instead of appending a `tool` message, you send a `function_call_output` item with `call_id` and the result.
- **`previous_response_id` for context**: you don't rebuild message history. The server reconstructs the conversation from the prior response.

> [!NOTE] Ordering of tool results
> When you use `previous_response_id`, the server does not enforce strict ordering of `function_call_output` items, since ordering context is already captured in the referenced response. When you build history manually without `previous_response_id`, keep tool results in the same order as their corresponding tool calls.

## Tool calling with Chat Completions {#chat-completions-tool-calling}

If your application or agent harness is built on [Chat Completions](/docs/protocols/chat-completions), tool calling is fully supported there too — use the pattern below. Chat Completions uses the nested tool definition format (function metadata under a `function` key, as shown in [Defining tools](#defining-tools)). The model returns tool calls as a `tool_calls` array on the assistant message, and you return each result as a `tool` message.

### Single-turn tool call {#single-turn-tool-call}

Send a request with tools. When the model needs a tool, it returns a `tool_calls` array on the assistant message.

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
            "content": "What is the weather in Seattle?",
        },
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Return current weather for the given location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name",
                        },
                    },
                    "required": [
                        "location",
                    ],
                },
            },
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
      content: 'What is the weather in Seattle?',
    },
  ],
  tools: [
    {
      type: 'function',
      function: {
        name: 'get_weather',
        description: 'Return current weather for the given location.',
        parameters: {
          type: 'object',
          properties: {
            location: {
              type: 'string',
              description: 'City name',
            },
          },
          required: [
            'location',
          ],
        },
      },
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
                "content": "What is the weather in Seattle?",
            },
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Return current weather for the given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name",
                            },
                        },
                        "required": [
                            "location",
                        ],
                    },
                },
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
      "content": "What is the weather in Seattle?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Return current weather for the given location.",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name"
            }
          },
          "required": [
            "location"
          ]
        }
      }
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
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"Seattle, WA\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 85,
    "completion_tokens": 24,
    "total_tokens": 109
  }
}
```

When the model requests tool calls, `finish_reason` is `"tool_calls"` and `message.content` is typically `null` or empty. The array can contain multiple calls in one turn; execute each one and return a `tool` result per call as shown in [multi-turn tool results](#multi-turn-tool-results).

### Multi-turn tool results {#multi-turn-tool-results}

After executing the tool, send the result back so the model can produce a final answer. This is the core pattern for agentic tool use.

The steps:

1. Append the full assistant message (including `tool_calls`) to the history.
2. Append a `tool` message with `tool_call_id` and the result as `content`.
3. Send the updated history in the next request.

```python title="Python (OpenAI SDK)"
import os
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)


def get_weather(location: str) -> dict:
    """Placeholder -- replace with a real API call."""
    return {"location": location, "temperature": "15°C", "condition": "Cloudy"}


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Return current weather for the given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name",
                    }
                },
                "required": ["location"],
            },
        },
    }
]

messages = [
    {"role": "user", "content": "What is the weather in Seattle?"},
]

# First request -- model requests a tool call
response = client.chat.completions.create(
    model="muse-spark-1.1",
    messages=messages,
    tools=tools,
)
msg = response.choices[0].message

# Append the assistant message with its tool calls
messages.append(
    {
        "role": "assistant",
        "content": msg.content or "",
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ],
    }
)

# Execute each tool and append results
for tc in msg.tool_calls:
    args = json.loads(tc.function.arguments)
    result = get_weather(**args)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result),
        }
    )

# Second request -- model incorporates the tool result
response = client.chat.completions.create(
    model="muse-spark-1.1",
    messages=messages,
    tools=tools,
)

print(response.choices[0].message.content)
# "The current weather in Seattle is 15°C and cloudy."
```

## Strict tool schemas {#strict}

Function tools accept an optional `strict` flag. Today it controls only **schema validation**: whether the server checks your `parameters` against the supported strict subset.

- **`strict` defaults to `false`**: when you omit `strict` or set it to `false`, the schema is accepted as-is. A schema that omits a root `type` is normalized rather than rejected (see the tip under [Defining tools](#defining-tools)).
- **Set `strict: true`**: the server validates your schema against the strict subset, for example `additionalProperties: false` and every property listed in `required`. A schema that violates the subset returns `HTTP 400`, but only when `strict: true`; the same schema with `strict` omitted is accepted. See [Structured output → Strict mode](/docs/structured-output#strict-mode) for the full subset rules.

> [!IMPORTANT] Always validate tool-call arguments
> Regardless of `strict`, the model's generated arguments are guided by your `parameters` schema but are not guaranteed to validate against it. Always parse and validate arguments in your own code before using them.

This `strict` default applies to both Responses and Chat Completions API function tools.

## Guidelines {#guidelines}

- **Handle parallel tool calls**: The model may return multiple calls in `tool_calls` in one turn, for example looking up three cities at once. Execute every call, then append one `tool` message per call, each with its own `tool_call_id`, before the next request. The multi-turn example above already loops over `tool_calls` to do this. To limit the model to one call per turn, set `parallel_tool_calls: false` (default `true`). This flag takes effect only when you provide function `tools`; with no function tools it is accepted but has no effect, matching OpenAI. It applies to both Chat Completions and the [Responses API](/docs/protocols/responses).
- **`max_tool_calls` limits built-in tools only**: `max_tool_calls` caps the model's **built-in** tool calls (such as `web_search`), counted across all built-in tools; the model ignores calls beyond the limit. It has a minimum of 1 and no enforced maximum. It does not limit client-side function-tool calls. To bound function-tool calls, set `parallel_tool_calls: false` or cap turns in your own loop.
- **`tool_choice` must be `"auto"`**: Only `"auto"` (the default) is supported on both Chat Completions and the [Responses API](/docs/protocols/responses); `"none"`, `"required"`, and named function choices return `HTTP 400` ("only `"auto"` is supported for `tool_choice`"). With `"auto"`, the model decides whether to call a tool, so your app should handle both a tool call and a plain text response.
- **Tool-call arguments stream**: With `stream: true`, the model streams arguments incrementally. On Chat Completions, accumulate `tool_calls` deltas across chunks by `index`; on the [Responses API](/docs/protocols/responses), consume `response.function_call_arguments.delta` events and finalize on `response.function_call_arguments.done`.
- **Always include the full assistant message**: When returning tool results, include the complete assistant message with its `tool_calls` array before the `tool` message. Omitting it returns `HTTP 400`.
- **Match `tool_call_id` / `call_id` to the originating call**: On Chat Completions, each `tool` message must carry the `tool_call_id` of the call it answers. On the Responses API, when you construct input manually without `previous_response_id`, every `function_call_output.call_id` must match a `function_call.call_id` in the same request; a mismatch returns `HTTP 400`. With `previous_response_id`, the server resolves these from stored history.
- **Keep `call_id` within 1–64 characters**: Every `call_id` on both `function_call` and `function_call_output` items must be 1 to 64 characters. An empty or overlength `call_id` returns `HTTP 400`.
- **Tool name validation applies only to the most recent assistant turn**: When you provide a `tools` array, the server validates that `tool_calls[].function.name` matches a defined tool name. Historical assistant messages with tool calls that reference tools no longer in the current `tools` array do not cause validation errors, as long as those calls already have corresponding tool results in history.
- **Use `tools`, not deprecated fields**: `functions` and `function_call` are deprecated. Use `tools` and `tool_choice`.
- **Use structured output for complex arguments**: If you need strict control over tool argument formats, combine tool calling with [structured output](/docs/structured-output) via `response_format`.
- **Defer large tool sets**: When you have many tools, front-loading every definition wastes tokens. Mark tools with `defer_loading: true` and add the `tool_search` tool so the model loads only what it needs on demand. See [tool search](/docs/tool-search).

## Next steps

Now that you can call tools, keep your agent fast and reliable.

- Defer large libraries with [tool search](/docs/tool-search) to keep prompts small and preserve cache.
- Lock argument shapes with [structured output](/docs/structured-output) for predictable parsing.
- Check the full request and response schema in the [Chat Completions API reference](/docs/api-reference/chat-completions).