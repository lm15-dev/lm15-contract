> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Function calling best practices

> Design tools, write descriptions, and control tool selection so Together models call functions reliably.

The quality of your tool definitions, system prompt, and selection controls determines how reliably a model calls functions. These practices apply to every function-calling model on Together AI. Examples use GLM-5.3 (`zai-org/GLM-5.3`), the recommended function-calling model, but the same patterns work across the [serverless](/docs/serverless/models) and [dedicated model inference](/docs/dedicated-endpoints/models) catalogs.

## Write clear descriptions

The function description is the single biggest factor in tool-calling accuracy. It is the only context the model has for deciding when to call a tool and how to fill its arguments. Treat each description as a short spec:

* State what the tool does, and when to use it (and when not to).
* Describe what each parameter means, its expected format, and how it changes the result.
* Note caveats and limits: what the tool does not return, and any edge cases.
* Describe what the output represents, so the model knows how to use the result.

Aim for three to four sentences per tool, more for complex tools. Apply the intern test: if a new engineer could correctly call the function given only the schema, the model can too. Every question they would ask is context to add to the description or system prompt.

The example below contrasts a description the model can act on with one that leaves it guessing.

<CodeGroup>
  ```json Good theme={null}
  {
    "type": "function",
    "function": {
      "name": "get_current_stock_price",
      "description": "Retrieves the current stock price for a given ticker symbol. The ticker must be a valid symbol for a company on a major US exchange like NYSE or NASDAQ. Returns the latest trade price in USD. Use this when the user asks for the current or most recent price of a specific stock. It does not return any other company information, historical prices, or after-hours quotes.",
      "parameters": {
        "type": "object",
        "properties": {
          "symbol": {
            "type": "string",
            "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
          }
        },
        "required": ["symbol"]
      }
    }
  }
  ```

  ```json Poor theme={null}
  {
    "type": "function",
    "function": {
      "name": "get_current_stock_price",
      "description": "Gets the stock price for a ticker.",
      "parameters": {
        "type": "object",
        "properties": {
          "symbol": {
            "type": "string"
          }
        },
        "required": ["symbol"]
      }
    }
  }
  ```
</CodeGroup>

The good version says what the tool returns, when to reach for it, and what it explicitly does not cover. The poor version leaves the model to infer the exchange, currency, and whether historical prices are in scope.

Put concrete examples and recurring failure cases in the description text or the system prompt. Together's chat completions API follows the OpenAI tool schema, so the tool definition accepts `type`, `function.name`, `function.description`, and `function.parameters` (a JSON Schema object). It has no separate field for input examples, so fold any examples into the prose you already control.

## Make invalid states unrepresentable

Use the JSON Schema in `parameters` to constrain what the model can produce, rather than validating after the fact.

* **Use specific types and enums:** Give every parameter a type (`string`, `integer`, `boolean`), and an `enum` when the valid values are a fixed set. The model picks from the list instead of inventing a value.
* **Mark required fields:** List the parameters the model must supply in `required`. Leave genuinely optional ones out.
* **Avoid representable invalid states:** A `toggle_light(on: bool, off: bool)` signature allows `on=true, off=true`. Replace it with a single `state` enum of `["on", "off"]` so the contradiction cannot occur.
* **Close the schema:** Set `"additionalProperties": false` on the parameters object so the model cannot add fields you do not handle.

For stricter conformance, add `"strict": true` to the function definition. Together's API accepts it and constrains the generated arguments to match your schema.

```python Python theme={null}
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current temperature for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]
```

## Keep the active tool set small

The more tools you expose at once, the more chances the model has to pick the wrong one. Keep the set passed in `tools` focused on the current task. Aim for fewer than 20 active tools as a soft target, and evaluate accuracy as you add more.

* **Consolidate related operations:** Instead of `create_ticket`, `update_ticket`, and `close_ticket`, expose one `manage_ticket` tool with an `action` enum. Fewer, more capable tools reduce selection ambiguity.
* **Namespace tool names:** When tools span multiple services, prefix the name with the service: `github_list_prs`, `slack_send_message`. This keeps selection unambiguous as the library grows.
* **Scope tools to context:** If you have a large catalog of tools, pass only the subset relevant to the current conversation rather than all of them on every request.

Use descriptive names without spaces, periods, or dashes (`get_current_weather`, not `get current weather`).

## Offload work from the model to your code

Don't ask the model to produce information your application already has.

* **Drop arguments you already know:** If you already hold an `order_id` from an earlier step, don't define it as a parameter. Expose `submit_refund()` with no arguments and pass the `order_id` in your own code when you execute the call.
* **Combine always-sequential calls:** If you always call `mark_location()` right after `query_location()`, merge the marking logic into the query tool. One round trip is more reliable than two.

Every argument the model doesn't have to generate is one it cannot get wrong.

## Guide the model with the system prompt

The system prompt sets the policy the model follows when deciding whether and how to call a tool.

* **Give the model a role:** `You are a travel planning assistant with access to weather and restaurant tools.`
* **State when to use each tool, and when not to.** Tell the model exactly what to do for the cases you care about.
* **Forbid guessing:** `Do not guess values. If a required detail is missing, ask the user for it before calling a tool.`
* **Encourage clarification:** Instruct the model to ask a follow-up question when the request is ambiguous, rather than calling a tool with assumed arguments.

## Control tool selection with `tool_choice`

The `tool_choice` parameter decides whether the model may call a tool on a given request. See [`tool_choice` options](/docs/inference/function-calling/single-call#tool_choice-options) for the full reference.

* `"auto"` (default): the model decides whether to call a tool or reply with text.
* `"required"`: the model must call at least one tool.
* A specific tool: pass `{"type": "function", "function": {"name": "get_current_stock_price"}}` to force that tool regardless of phrasing.
* `"none"`: the model replies with text only.

## Handle responses and errors robustly

Tool calls come back in `message.tool_calls`, not `message.content` (which is often `null` on a tool-calling turn). Build the loop defensively:

* **Check `finish_reason`:** It is `"tool_calls"` when the model wants you to run a tool, and `"stop"` for a normal text reply. Branch on it instead of assuming a tool was called.
* **Parse arguments as JSON:** `function.arguments` is a JSON-encoded string. Parse it inside a try/except, and handle the case where the model produces malformed or incomplete JSON.
* **Return informative tool errors:** When a tool fails, return a clear error message in the `tool` message content (for example, `{"error": "No stock found for symbol XYZ"}`) so the model can recover or explain the failure to the user, rather than throwing.
* **Validate high-consequence calls:** Before executing a tool with real side effects (placing an order, sending a refund, deleting data), confirm the call with the user.

Apply standard security practice to anything a tool executes: validate and sanitize arguments before acting on them, authenticate calls to external APIs, and keep secrets out of tool arguments.

## Tune for reliable calls

* **Lower the temperature:** A low `temperature` (for example, `0`) makes tool selection and argument generation more deterministic. Raise it only if you need more varied behavior.
* **Stream when latency matters:** Tool calls stream incrementally through `delta.tool_calls`. Use [streaming](/docs/inference/function-calling/single-call#streaming) to start handling a call before the full response arrives.
* **Watch your token budget:** Tool descriptions and schemas count toward input tokens. If you approach the limit, tighten descriptions or split a large tool set into smaller, task-specific groups.

## When to fine-tune

Strong descriptions and a focused tool set cover most cases. If you need higher accuracy across a large number of tools or a difficult domain-specific task, fine-tune a model on your own tool-calling data. See [function-calling fine-tuning](/docs/fine-tuning/function-calling) for dataset format and the training workflow.
