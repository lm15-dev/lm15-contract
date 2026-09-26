> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Tool Calling

> Connect models to external tools and APIs

Tool calling (also known as function calling) enables models to intelligently select and use external tools based on user input. You can build agents that access APIs, retrieve real-time data, or perform actions—all through [OpenAI-compatible](https://platform.openai.com/docs/guides/function-calling) tool specifications.

**How it works:**

1. Define tools using [JSON Schema](https://json-schema.org/learn/getting-started-step-by-step) (name, description, parameters)
2. Model analyzes the query and decides whether to call a tool
3. If needed, model returns structured tool calls with parameters
4. You execute the tool and send results back for the final response

## Quick example

Define tools and send a request - the model will return structured tool calls when needed:

Initialize the client:

<CodeGroup>
  ```python Python (Fireworks SDK) theme={null}
  from fireworks import Fireworks

  client = Fireworks()
  ```

  ```python Python (OpenAI SDK) theme={null}
  import os
  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ.get("FIREWORKS_API_KEY"),
      base_url="https://api.fireworks.ai/inference/v1"
  )
  ```
</CodeGroup>

Define the tools and make the request:

```python theme={null}
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
    tools=tools,
    temperature=0.1
)

print(response.choices[0].message.tool_calls)
# Output: [ChatCompletionMessageToolCall(id='call_abc123', function=Function(arguments='{"location":"San Francisco"}', name='get_weather'), type='function')]
```

<Tip>
  For best results with tool calling, use a low temperature (0.0-0.3) to reduce hallucinated parameter values and ensure more deterministic tool selection.
</Tip>

<AccordionGroup>
  <Accordion title="Complete workflow: Execute tools and get final response">
    ```python theme={null}
    import json

    # Step 1: Define your tools
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }]

    # Step 2: Send initial request
    messages = [{"role": "user", "content": "What's the weather in San Francisco?"}]
    response = client.chat.completions.create(
        model="accounts/fireworks/models/kimi-k2-instruct-0905",
        messages=messages,
        tools=tools,
        temperature=0.1
    )

    # Step 3: Check if model wants to call a tool
    if response.choices[0].message.tool_calls:
        # Step 4: Execute the tool
        tool_call = response.choices[0].message.tool_calls[0]

        # Your actual tool implementation
        def get_weather(location, unit="celsius"):
            # In production, call your weather API here
            return {"temperature": 72, "condition": "sunny", "unit": unit}

        # Parse arguments and call your function
        function_args = json.loads(tool_call.function.arguments)
        function_response = get_weather(**function_args)

        # Step 5: Send tool response back to model
        messages.append(response.choices[0].message)  # Add assistant's tool call
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(function_response)
        })

        # Step 6: Get final response
        final_response = client.chat.completions.create(
            model="accounts/fireworks/models/kimi-k2-instruct-0905",
            messages=messages,
            tools=tools,
            temperature=0.1
        )

        print(final_response.choices[0].message.content)
        # Output: "It's currently 72°F and sunny in San Francisco."
    ```
  </Accordion>
</AccordionGroup>

## Defining tools

Tools are defined using [JSON Schema](https://json-schema.org/understanding-json-schema/reference) format. Each tool requires:

* **name**: Function identifier (a-z, A-Z, 0-9, underscores, dashes; max 64 characters)
* **description**: Clear explanation of what the function does (used by the model to decide when to call it)
* **parameters**: JSON Schema object describing the function's parameters

<Tip>
  Write detailed descriptions and parameter definitions. The model relies on these to select the correct tool and provide appropriate arguments.
</Tip>

### Parameter types

JSON Schema supports: `string`, `number`, `integer`, `object`, `array`, `boolean`, and `null`. You can also:

* Use `enum` to restrict values to specific options
* Mark parameters as `required` or optional
* Provide descriptions for each parameter
* Reuse subschemas via `$defs` / `definitions` and `$ref`, including recursive references (e.g. linked lists, trees, mutually recursive types)
* Carry `$id`, `$schema`, and other annotation keywords (no external fetches are performed)

<Tip>
  The same JSON Schema feature set is supported in tool `parameters` and in `response_format={"type": "json_schema", ...}`. See [JSON Schema Support](/structured-responses/structured-response-formatting#json-schema-support) for the full list, including the rules for resolving `$ref` and how to reach definitions placed inside nested subschemas.
</Tip>

<Accordion title="Example: parameters that reuse a subschema via `$defs`">
  A common shape produced by pydantic v2, Instructor, and LangChain `TypeAdapter`. The `$defs` block holds the reusable subschemas and properties reference them by `$ref`:

  ```python theme={null}
  tools = [{
      "type": "function",
      "function": {
          "name": "submit_order",
          "description": "Submit an order with line items and a customer",
          "parameters": {
              "type": "object",
              "$defs": {
                  "Product":  {"type": "object", "properties": {"name": {"type": "string"}, "price": {"type": "number"}}, "required": ["name", "price"]},
                  "Customer": {"type": "object", "properties": {"name": {"type": "string"}, "email": {"type": "string"}}, "required": ["name", "email"]}
              },
              "properties": {
                  "items":    {"type": "array", "items": {"$ref": "#/$defs/Product"}},
                  "customer": {"$ref": "#/$defs/Customer"}
              },
              "required": ["items", "customer"]
          }
      }
  }]
  ```
</Accordion>

<Accordion title="Example: Defining multiple tools">
  ```python theme={null}
  tools = [
      {
          "type": "function",
          "function": {
              "name": "get_weather",
              "description": "Get current weather for a location",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "City name, e.g. San Francisco"
                      },
                      "unit": {
                          "type": "string",
                          "enum": ["celsius", "fahrenheit"],
                          "description": "Temperature unit"
                      }
                  },
                  "required": ["location"]
              }
          }
      },
      {
          "type": "function",
          "function": {
              "name": "search_restaurants",
              "description": "Search for restaurants by cuisine type",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "cuisine": {
                          "type": "string",
                          "description": "Type of cuisine (e.g., Italian, Mexican)"
                      },
                      "location": {
                          "type": "string",
                          "description": "City or neighborhood"
                      },
                      "price_range": {
                          "type": "string",
                          "enum": ["$", "$$", "$$$", "$$$$"]
                      }
                  },
                  "required": ["cuisine", "location"]
              }
          }
      }
  ]
  ```
</Accordion>

## Additional configurations

### tool\_choice

The [`tool_choice`](/api-reference/post-chatcompletions) parameter controls how the model uses tools:

* **`auto`** (default): Model decides whether to call a tool or respond directly
* **`none`**: Model will not call any tools
* **`required`**: Model must call at least one tool
* **Specific function**: Force the model to call a particular function

```python theme={null}
# Force a specific tool
response = client.chat.completions.create(
    model="accounts/fireworks/models/kimi-k2-instruct-0905",
    messages=[{"role": "user", "content": "What's the weather?"}],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_weather"}},
    temperature=0.1
)
```

<Note>
  Some models support parallel tool calling, where multiple tools can be called in a single response. Check the model's capabilities before relying on this feature.
</Note>

## Streaming

<Accordion title="Using tool calls with streaming responses">
  Tool calls work with streaming responses. Arguments are sent incrementally as the model generates them:

  ```python theme={null}
  import json

  tools = [{
      "type": "function",
      "function": {
          "name": "get_weather",
          "description": "Get the current weather for a city",
          "parameters": {
              "type": "object",
              "properties": {
                  "city": {"type": "string", "description": "City name"},
                  "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
              },
              "required": ["city"]
          }
      }
  }]

  stream = client.chat.completions.create(
      model="accounts/fireworks/models/kimi-k2-instruct-0905",
      messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
      tools=tools,
      stream=True,
      temperature=0.1
  )

  # Accumulate tool call data
  tool_calls = {}

  for chunk in stream:
      if chunk.choices[0].delta.tool_calls:
          for tool_call in chunk.choices[0].delta.tool_calls:
              index = tool_call.index
              
              if index not in tool_calls:
                  tool_calls[index] = {"id": "", "name": "", "arguments": ""}
              
              if tool_call.id:
                  tool_calls[index]["id"] = tool_call.id
              if tool_call.function and tool_call.function.name:
                  tool_calls[index]["name"] = tool_call.function.name
              if tool_call.function and tool_call.function.arguments:
                  tool_calls[index]["arguments"] += tool_call.function.arguments
      
      if chunk.choices[0].finish_reason == "tool_calls":
          for tool_call in tool_calls.values():
              args = json.loads(tool_call["arguments"])
              print(f"Calling {tool_call['name']} with {args}")
          break
  ```
</Accordion>

## Troubleshooting

<AccordionGroup>
  <Accordion title="Model isn't calling tools when expected">
    * Check that your tool descriptions are clear and detailed
    * Ensure the user query clearly indicates a need for the tool
    * Try using `tool_choice="required"` to force tool usage
    * Verify your model supports tool calling (check `supportsTools` field)
  </Accordion>

  <Accordion title="Tool arguments are incorrect or malformed">
    * Add more detailed parameter descriptions
    * Use lower temperature (0.0-0.3) for more deterministic outputs
    * Provide examples in parameter descriptions
    * Use `enum` to constrain values to specific options
  </Accordion>

  <Accordion title="Getting JSON parsing errors">
    * Always validate tool call arguments before parsing
    * Handle partial or malformed JSON gracefully in production
    * Use try-catch blocks when parsing `tool_call.function.arguments`
  </Accordion>

  <Accordion title="400 &#x22;Error resolving schema reference&#x22; or &#x22;Error validating JSON Schema&#x22;">
    The schema in `parameters` (or `response_format`) is reaching a `$ref` Fireworks cannot resolve. Common causes:

    * **External `$ref` URI** (e.g. `https://example.com/schema.json`). Only in-document JSON Pointer fragments (`#/...`) are supported. Inline the referenced subschema or hoist it into `$defs`.
    * **Wrong fragment path**, e.g. `#/components/schemas/Foo` when the document has no `components` key. Match the pointer to the actual document layout.
    * **Older deployment image.** Recursive `$ref`, root `$id`, and nested `$defs` placed under a property all became supported in mid-2026 and earlier images returned 400 on those shapes. If you control a self-hosted/dedicated deployment, redeploy on a current image.

    For the full set of supported reference forms, see [JSON Schema Support](/structured-responses/structured-response-formatting#json-schema-support).
  </Accordion>
</AccordionGroup>

## Next steps

<CardGroup cols={2}>
  <Card title="Structured Outputs" icon="brackets-curly" href="/structured-responses/structured-response-formatting">
    Enforce JSON schemas for consistent responses
  </Card>

  <Card title="Text Models" icon="message" href="/guides/querying-text-models">
    Learn about chat completions and other APIs
  </Card>

  <Card title="Deployments" icon="server" href="/guides/ondemand-deployments">
    Deploy models on dedicated GPUs
  </Card>

  <Card title="API Reference" icon="code" href="/api-reference/post-chatcompletions">
    Full chat completions API documentation
  </Card>
</CardGroup>
