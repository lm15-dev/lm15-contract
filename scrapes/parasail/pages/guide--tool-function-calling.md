> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/guides/tool-function-calling.md).

# Tool/Function Calling

Let Parasail models call your functions and tools via the Chat Completions and Responses APIs.

## Overview

Tool (function) calling lets a model decide when to invoke an external function—a weather API, a database query, a calculator—and emit a structured request for it. Your application runs the function and feeds the result back to the model.

Parasail exposes tool calling through two OpenAI-compatible surfaces:

* **Chat Completions API** (`/v1/chat/completions`)—the classic single-call interface. You pass `tools`, inspect `message.tool_calls`, run the tool, and append a `tool` message for the next call.
* **Responses API** (`/v1/responses`)—the newer agentic interface built for multi-step loops. You pass `tools`, inspect `response.output` for `function_call` items, and append `function_call_output` items.

Both use the same base URL and API key:

```
https://api.parasail.io/v1
```

The **tool schema** (name, description, JSON Schema parameters) is the same in both APIs—only the wrapper shape and the response handling differ. Pick Chat Completions for simple one-shot tool calls, and the Responses API for multi-turn agentic workflows.

## Supported models

The following serverless models return structured tool calls, verified against the live endpoints in August 2026. Verify current availability via the [models endpoint](/parasail-docs/api-reference/models-endpoint.md).

Treat this table as a starting point for validation. Test your actual tool schema and prompt before depending on tool calls in production.

| Model                                  | Tools | Tool Choice |
| -------------------------------------- | ----- | ----------- |
| parasail-kimi-k3                       | ✅     | ✅           |
| parasail-kimi-k27-code                 | ✅     | ✅           |
| parasail-kimi-k26                      | ✅     | ✅           |
| parasail-deepseek-v4-pro               | ✅     | ✅           |
| parasail-glm-52                        | ✅     | ✅           |
| parasail-glm-51                        | ✅     | ✅           |
| parasail-minimax-m3                    | ✅     | ✅           |
| parasail-deepseek-v4-flash             | ✅     | ✅           |
| parasail-qwen3p6-35b-a3b               | ✅     | ✅           |
| parasail-qwen35-397b-a17b              | ✅     | ✅           |
| parasail-qwen3p5-35b-a3b               | ✅     | ✅           |
| parasail-qwen3-coder-next              | ✅     | ✅           |
| parasail-qwen3-235b-a22b-instruct-2507 | ✅     | ✅           |
| parasail-qwen-3-next-80b-instruct      | ✅     | ✅           |
| parasail-qwen3-vl-235b-a22b-instruct   | ✅     | ✅           |
| parasail-qwen3vl-8b-instruct           | ✅     | ✅           |
| parasail-llama-4-maverick-instruct-fp8 | ✅     | ✅           |
| parasail-llama-33-70b-fp8              | ✅     | ✅           |
| parasail-mimo-v25                      | ✅     | ✅           |
| parasail-trinity-large-thinking        | ✅     | ✅           |
| parasail-gemma-4-26b-a4b-it            | ✅     | ✅           |
| parasail-gemma-4-31b-it                | ✅     | ✅           |
| parasail-gpt-oss-120b                  | ✅     | ✅           |
| parasail-gpt-oss-120b-fast             | ✅     | ✅           |
| parasail-gpt-oss-20b                   | ✅     | ✅           |

`parasail-qwen25-vl-72b-instruct` also emits tool calls, but only reliably with `tool_choice="required"`. With `tool_choice="auto"` it tends to answer in prose instead of calling the tool.

Models outside this table—including `parasail-mistral-small-32-24b`, `parasail-gemma3-27b-it`, `parasail-cydonia-24-v41`, `parasail-ui-tars-1p5-7b`, and `parasail-skyfall-36b-v2-fp8`—don't support the `tools` parameter today. Depending on the model, a request with `tools` returns an error or plain text with no `tool_calls`. Embedding and speech models such as `parasail-bge-m3` and `parasail-resemble-tts-en` don't accept `tools` at all.

{% tabs %}
{% tab title="Chat Completions API" %}
In the Chat Completions API, each tool must be wrapped as `{"type": "function", "function": {...}}`. The `function` object holds the `name`, `description`, and a JSON Schema `parameters`.

```python
import os
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retrieve weather information for a given location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                },
                "required": ["location", "date"],
            },
        },
    }
]

messages = [
    {"role": "user", "content": "What's the weather like in Manhattan Beach on 2025-06-03?"}
]

response = client.chat.completions.create(
    model="parasail-qwen3p5-35b-a3b",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

tool_call = response.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)
print(json.dumps(args, indent=2))
```

Expected arguments:

```json
{
  "location": "Manhattan Beach",
  "date": "2025-06-03"
}
```

### Returning the tool result

Run your function, then append the assistant's tool call and a `tool` message with the result before calling the model again:

```python
def get_weather(location, date):
    # Replace with a real API call
    return {"location": location, "date": date, "weather": "Sunny", "temperature": "75F"}

result = get_weather(**args)

messages.append(response.choices[0].message)  # the assistant's tool call
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result),
    }
)

final = client.chat.completions.create(
    model="parasail-qwen3p5-35b-a3b",
    messages=messages,
    tools=tools,
)
print(final.choices[0].message.content)
```

{% endtab %}

{% tab title="Responses API" %}
In the Responses API, tools are defined with a flat shape—`type`, `name`, `description`, and `parameters` at the top level (no nested `function` object). Tool calls come back as `function_call` items in `response.output`, and you return results as `function_call_output` items.

```python
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>",
)

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "default": "celsius",
                },
            },
            "required": ["city"],
        },
    }
]

def handle_tool_call(name, arguments):
    args = json.loads(arguments)
    if name == "get_weather":
        return json.dumps({"city": args["city"], "temperature": 22, "condition": "sunny"})
    return json.dumps({"error": "unknown function"})

# Initial request (store must be false on the Parasail gateway)
response = client.responses.create(
    model="parasail-kimi-k27-code",
    store=False,
    tools=tools,
    input=[{"role": "user", "content": "What's the weather in Tokyo?"}],
)

# Agentic loop—continue until the model stops calling tools
while response.output:
    tool_calls = [item for item in response.output if item.type == "function_call"]
    if not tool_calls:
        break

    next_input = list(response.output)
    for tool_call in tool_calls:
        result = handle_tool_call(tool_call.name, tool_call.arguments)
        next_input.append(
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": result,
            }
        )

    response = client.responses.create(
        model="parasail-kimi-k27-code",
        store=False,
        tools=tools,
        input=next_input,
    )

print(response.output_text)
```

The Responses API requires `store=False` on every request. See the [Responses API reference](/parasail-docs/products/overview/responses-api.md) for the full compatibility table.
{% endtab %}
{% endtabs %}

## Chat Completions tools vs. Responses tools

|                    | Chat Completions                                                    | Responses API                                                     |
| ------------------ | ------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Tool definition    | `{"type": "function", "function": {name, description, parameters}}` | `{"type": "function", name, description, parameters}` (flat)      |
| Where calls appear | `message.tool_calls[]`                                              | `response.output[]` items with `type == "function_call"`          |
| Returning results  | `{"role": "tool", "tool_call_id": ..., "content": ...}`             | `{"type": "function_call_output", "call_id": ..., "output": ...}` |
| Best for           | One-shot tool calls                                                 | Multi-step agentic loops                                          |

The underlying schema—the function `name`, `description`, and JSON Schema `parameters`—is identical between the two; only the wrapper and the result-handling differ.

## Next steps

* [Structured output guide](/parasail-docs/guides/structured-output.md)
* [Chat Completions API reference](/parasail-docs/api-reference/chat-completions.md)
* [Responses API reference](/parasail-docs/api-reference/responses-api.md)
* [Models endpoint](/parasail-docs/api-reference/models-endpoint.md)
