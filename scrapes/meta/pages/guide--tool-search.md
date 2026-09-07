---
meta:
  title: Tool search
  description: Let the model discover and load tools on demand to cut token usage and preserve cache across large tool sets.
  keywords: tool search, deferred tools, defer_loading, namespaces, hosted tool search, token savings
cms:
  alias: /model-api/docs/tool-search
  target: aidmc
---

# Tool search

Build agents with hundreds of tools without loading the whole library on every turn. Tool search keeps deferred definitions out of the prompt until the model needs them, so you cut input tokens and keep the cache prefix intact.

> [!NOTE] Responses API only
> Tool search runs on the [Responses API](/docs/protocols/responses). It extends [tool calling](/docs/tool-calling) and [namespaces](/docs/tool-calling#function-name-rules), so start with those if you are new to defining tools.

## How it works {#how-it-works}

By default every tool in `tools` loads into context up front and you pay for those definitions each turn. Tool search defers that cost: you mark tools as deferred and the model loads only what it decides it needs.

Turn it on with two changes:

1. Add `{"type": "tool_search"}` to your `tools` array.
2. Mark each tool you want to defer with `defer_loading: true`.

A deferred tool's **name and description stay visible** from the start; only its parameter schema is withheld until tool search loads it. When the model loads a tool, the API appends it at the **end** of the context, preserving the cache prefix from earlier turns and keeping cost and latency low.

There are two execution modes:

- **[Hosted](#hosted)**: the API searches the deferred tools you declared and loads the matching subset in the same response. Use this when you know the full inventory at request time.
- **[Client-executed](#client)**: the model issues a search request, your app performs the lookup, and you return the tools to load. Use this when availability depends on project or tenant state the API can't see.

## Defer tools and group them into namespaces {#deferring-tools}

You can defer standalone [function](/docs/tool-calling#defining-tools) tools, but grouping them into a [namespace](/docs/tool-calling#function-name-rules) gives the model a cleaner surface to search and saves more tokens. For a namespace the model sees only the namespace name and description up front; the functions inside load through tool search.

Set `defer_loading: true` on the functions **inside** the namespace, not on the namespace object itself. A namespace can mix deferred and non-deferred functions: non-deferred functions are callable immediately, deferred ones load on demand.

```json
{
  "tools": [
    {
      "type": "namespace",
      "name": "crm",
      "description": "CRM tools for customer lookup and order management.",
      "tools": [
        {
          "type": "function",
          "name": "list_open_orders",
          "description": "List open orders for a customer ID.",
          "defer_loading": true,
          "parameters": {
            "type": "object",
            "properties": { "customer_id": { "type": "string" } },
            "required": ["customer_id"],
            "additionalProperties": false
          }
        }
      ]
    },
    { "type": "tool_search" }
  ]
}
```

Write clear, high-level namespace descriptions. The model uses them to decide which namespace to load. Keep each namespace focused, aim for fewer than 10 functions, and put richer detail in the deferred function descriptions that load only when needed.

## Hosted tool search {#hosted}

Hosted tool search is the simplest option when you know the full set of tools up front. Declare your tools, add `{"type": "tool_search"}`, and let the API decide what to load.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="List open orders for customer CUST-12345.",
    parallel_tool_calls=False,
    tools=[
        {
            "type": "namespace",
            "name": "crm",
            "description": "CRM tools for customer lookup and order management.",
            "tools": [
                {
                    "type": "function",
                    "name": "get_customer_profile",
                    "description": "Fetch a customer profile by customer ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "customer_id",
                        ],
                        "additionalProperties": False,
                    },
                },
                {
                    "type": "function",
                    "name": "list_open_orders",
                    "description": "List open orders for a customer ID.",
                    "defer_loading": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "customer_id",
                        ],
                        "additionalProperties": False,
                    },
                },
            ],
        },
        {
            "type": "tool_search",
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

const response = await client.responses.create({
  model: 'muse-spark-1.3',
  input: 'List open orders for customer CUST-12345.',
  parallel_tool_calls: false,
  tools: [
    {
      type: 'namespace',
      name: 'crm',
      description: 'CRM tools for customer lookup and order management.',
      tools: [
        {
          type: 'function',
          name: 'get_customer_profile',
          description: 'Fetch a customer profile by customer ID.',
          parameters: {
            type: 'object',
            properties: {
              customer_id: {
                type: 'string',
              },
            },
            required: [
              'customer_id',
            ],
            additionalProperties: false,
          },
        },
        {
          type: 'function',
          name: 'list_open_orders',
          description: 'List open orders for a customer ID.',
          defer_loading: true,
          parameters: {
            type: 'object',
            properties: {
              customer_id: {
                type: 'string',
              },
            },
            required: [
              'customer_id',
            ],
            additionalProperties: false,
          },
        },
      ],
    },
    {
      type: 'tool_search',
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
    "https://api.meta.ai/v1/responses",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "input": "List open orders for customer CUST-12345.",
        "parallel_tool_calls": False,
        "tools": [
            {
                "type": "namespace",
                "name": "crm",
                "description": "CRM tools for customer lookup and order management.",
                "tools": [
                    {
                        "type": "function",
                        "name": "get_customer_profile",
                        "description": "Fetch a customer profile by customer ID.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_id": {
                                    "type": "string",
                                },
                            },
                            "required": [
                                "customer_id",
                            ],
                            "additionalProperties": False,
                        },
                    },
                    {
                        "type": "function",
                        "name": "list_open_orders",
                        "description": "List open orders for a customer ID.",
                        "defer_loading": True,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_id": {
                                    "type": "string",
                                },
                            },
                            "required": [
                                "customer_id",
                            ],
                            "additionalProperties": False,
                        },
                    },
                ],
            },
            {
                "type": "tool_search",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "List open orders for customer CUST-12345.",
  "parallel_tool_calls": false,
  "tools": [
    {
      "type": "namespace",
      "name": "crm",
      "description": "CRM tools for customer lookup and order management.",
      "tools": [
        {
          "type": "function",
          "name": "get_customer_profile",
          "description": "Fetch a customer profile by customer ID.",
          "parameters": {
            "type": "object",
            "properties": {
              "customer_id": {
                "type": "string"
              }
            },
            "required": [
              "customer_id"
            ],
            "additionalProperties": false
          }
        },
        {
          "type": "function",
          "name": "list_open_orders",
          "description": "List open orders for a customer ID.",
          "defer_loading": true,
          "parameters": {
            "type": "object",
            "properties": {
              "customer_id": {
                "type": "string"
              }
            },
            "required": [
              "customer_id"
            ],
            "additionalProperties": false
          }
        }
      ]
    },
    {
      "type": "tool_search"
    }
  ]
}'
```


If the model needs a deferred tool, `output` contains two items before the final function call:

- **`tool_search_call`**: records the search the model ran, including the `paths` it searched.
- **`tool_search_output`**: the loaded definitions, now callable.

```json
[
  {
    "type": "tool_search_call",
    "id": "tsc_abc123",
    "call_id": null,
    "execution": "server",
    "status": "completed",
    "arguments": { "paths": ["crm"] }
  },
  {
    "type": "tool_search_output",
    "id": "tso_abc123",
    "call_id": null,
    "execution": "server",
    "status": "completed",
    "tools": [
      {
        "type": "namespace",
        "name": "crm",
        "description": "CRM tools for customer lookup and order management.",
        "tools": [
          {
            "type": "function",
            "name": "list_open_orders",
            "description": "List open orders for a customer ID.",
            "defer_loading": true,
            "parameters": {
              "type": "object",
              "properties": { "customer_id": { "type": "string" } },
              "required": ["customer_id"],
              "additionalProperties": false
            }
          }
        ]
      }
    ]
  },
  {
    "type": "function_call",
    "name": "list_open_orders",
    "namespace": "crm",
    "call_id": "call_abc123",
    "arguments": "{\"customer_id\":\"CUST-12345\"}"
  }
]
```

In hosted mode `execution` is `"server"` and `call_id` is `null`. The API runs the search and load step for you; you handle the resulting `function_call` the same way you handle ordinary [tool calling](/docs/tool-calling#multi-turn-tool-results).

## Client-executed tool search {#client}

Client-executed tool search hands the lookup to your app. Use it when available tools depend on state the API can't see at request time, such as which integrations a tenant has enabled.

Set `execution: "client"` on the `tool_search` tool and provide a `description` and `parameters` schema for the search arguments your app expects. The model emits a `tool_search_call` and stops; you run the search and return a `tool_search_output` with the tools to load.

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

# First request -- the model asks your app to find tools
first = client.responses.create(
    model="muse-spark-1.1",
    input="Find the shipping ETA tool, then use it for order_42.",
    tools=[
        {
            "type": "tool_search",
            "execution": "client",
            "description": "Find the project-specific tools needed to continue the task.",
            "parameters": {
                "type": "object",
                "properties": {"goal": {"type": "string"}},
                "required": ["goal"],
                "additionalProperties": False,
            },
        }
    ],
    parallel_tool_calls=False,
)

# The model emits a tool_search_call and stops
search_call = next(
    item for item in first.output if item.type == "tool_search_call"
)

# Your application performs the lookup and picks the tools to load
loaded_tools = [
    {
        "type": "function",
        "name": "get_shipping_eta",
        "description": "Look up shipping ETA details for an order.",
        "defer_loading": True,
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
    }
]

# Second request -- return a tool_search_output echoing the same call_id
second = client.responses.create(
    model="muse-spark-1.1",
    input=[
        *first.output,
        {
            "type": "tool_search_output",
            "execution": "client",
            "call_id": search_call.call_id,
            "status": "completed",
            "tools": loaded_tools,
        },
    ],
)

print(second.output)
```

On the first turn the model returns only the search request:

```json
[
  {
    "type": "tool_search_call",
    "id": "tsc_xyz789",
    "call_id": "call_abc123",
    "execution": "client",
    "status": "completed",
    "arguments": { "goal": "Find the shipping ETA tool for order_42." }
  }
]
```

Return the tools to load in a `tool_search_output` that echoes the same `call_id`. On the next turn the loaded tool is callable like any other function. The `tools` array in your `tool_search_output` defines exactly what becomes available; anything you omit stays unavailable. Changing the loaded set on a later turn breaks the cache from that point forward, so keep it stable once loaded.

## Constraints {#constraints}

- **Responses API only**: tool search is not available on the [Chat Completions API](/docs/protocols/chat-completions). It is also reachable through the [Messages API](/docs/protocols/messages) adapter.
- **One `tool_search` tool per request**: declaring more than one returns `HTTP 400`.
- **Hosted tool search needs at least one deferred tool**: a `{"type": "tool_search"}` tool with no tool marked `defer_loading: true` returns `HTTP 400`.
- **Deferred tools need a `tool_search` tool**: marking a tool `defer_loading: true` without adding `tool_search` returns `HTTP 400`.
- **`tool_search` is a reserved name**: you cannot also declare a `function` tool named `tool_search`.
- **Not combinable with [structured output](/docs/structured-output)**: a request that uses tool search cannot also set a `json_schema` response format (`text.format`); the combination returns `HTTP 400`. This applies to both hosted and client-executed modes.

## Next steps

- Define the functions and namespaces you will defer with [tool calling](/docs/tool-calling), then add `defer_loading` to shrink the prompt.
- Pair a loaded tool with [structured output](/docs/structured-output) on a follow-up turn once tool search is out of the loop.
- Check the [Responses API reference](/docs/api-reference/responses) for the full `tool_search`, `tool_search_call`, and `tool_search_output` schemas.