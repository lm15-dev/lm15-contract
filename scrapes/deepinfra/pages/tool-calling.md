> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Tool Calling

> Let models call external functions — the foundation of AI agents.

Tool calling (also known as function calling) is the most important capability for building AI agents. It lets models decide when to invoke external tools — web search, code execution, database queries, API calls — and seamlessly weave the results into a final response. Without reliable tool calling, agentic systems break down.

**Tool call accuracy is a top priority for us.** We invest significant engineering effort in ensuring that function call parsing, argument extraction, and round-trip reliability are correct across all supported models. In Moonshot's [K2-Vendor-Verifier evaluation](https://github.com/MoonshotAI/K2-Vendor-Verifier?tab=readme-ov-file#k2-0905-evaluation-results) of Kimi K2, DeepInfra scored among the highest accuracy of any provider tested. The current Kimi model in our catalog is [`moonshotai/Kimi-K3`](https://deepinfra.com/moonshotai/Kimi-K3).

We provide an OpenAI-compatible tool calling API. For more background, see the [DeepInfra blog](https://deepinfra.com/blog/function-calling-feature).

## Setup

<CodeGroup>
  ```python Python theme={null}
  import os

  import openai
  import json

  client = openai.OpenAI(
      base_url="https://api.deepinfra.com/v1/openai",
      api_key=os.environ["DEEPINFRA_API_KEY"],
  )
  ```

  ```javascript JavaScript theme={null}
  import OpenAI from "openai";

  const client = new OpenAI({
      baseURL: "https://api.deepinfra.com/v1/openai",
      apiKey: process.env.DEEPINFRA_API_KEY,
  });
  ```
</CodeGroup>

## Define your function

<CodeGroup>
  ```python Python theme={null}
  def get_current_weather(location):
      """Get the current weather in a given location"""
      if "tokyo" in location.lower():
          return json.dumps({"location": "Tokyo", "temperature": "75"})
      elif "san francisco" in location.lower():
          return json.dumps({"location": "San Francisco", "temperature": "60"})
      elif "paris" in location.lower():
          return json.dumps({"location": "Paris", "temperature": "70"})
      else:
          return json.dumps({"location": location, "temperature": "unknown"})
  ```

  ```javascript JavaScript theme={null}
  async function get_current_weather(location) {
    if (location.toLowerCase().includes("tokyo")) {
      return JSON.stringify({"location": "Tokyo", "temperature": "75"});
    } else if (location.toLowerCase().includes("san francisco")) {
      return JSON.stringify({"location": "San Francisco", "temperature": "60"});
    } else if (location.toLowerCase().includes("paris")) {
      return JSON.stringify({"location": "Paris", "temperature": "70"});
    } else {
      return JSON.stringify({"location": location, "temperature": "unknown"});
    }
  }
  ```
</CodeGroup>

## Step 1: Send tools to the model

<CodeGroup>
  ```python Python theme={null}
  tools = [{
      "type": "function",
      "function": {
          "name": "get_current_weather",
          "description": "Get the current weather in a given location",
          "parameters": {
              "type": "object",
              "properties": {
                  "location": {
                      "type": "string",
                      "description": "The city and state, e.g. San Francisco, CA"
                  }
              },
              "required": ["location"]
          },
      }
  }]

  messages = [{"role": "user", "content": "What is the weather in San Francisco?"}]

  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=messages,
      tools=tools,
      tool_choice="auto",
  )
  tool_calls = response.choices[0].message.tool_calls
  for tool_call in tool_calls:
      print(tool_call.model_dump())
  ```

  ```javascript JavaScript theme={null}
  const tools = [{
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          }
        },
        "required": ["location"]
      },
    }
  }];

  const messages = [{"role": "user", "content": "What is the weather in San Francisco?"}];

  const response = await client.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: messages,
    tools: tools,
    tool_choice: "auto",
  });

  const tool_calls = response.choices[0].message.tool_calls;
  for (const tool_call of tool_calls) {
    console.log(tool_call);
  }
  ```
</CodeGroup>

Output:

```
{'id': 'call_X0xYqdnoUonPJpQ6HEadxLHE', 'function': {'arguments': '{"location": "San Francisco"}', 'name': 'get_current_weather'}, 'type': 'function'}
```

## Step 2: Execute the function and send results back

<CodeGroup>
  ```python Python theme={null}
  # Extend conversation with assistant's reply
  messages.append(response.choices[0].message)

  for tool_call in tool_calls:
      function_name = tool_call.function.name
      if function_name == "get_current_weather":
          function_args = json.loads(tool_call.function.arguments)
          function_response = get_current_weather(
              location=function_args.get("location")
          )

      messages.append({
          "tool_call_id": tool_call.id,
          "role": "tool",
          "content": function_response,
      })

  # Get a new response from the model with function results
  second_response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=messages,
      tools=tools,
      tool_choice="auto",
  )

  print(second_response.choices[0].message.content)
  ```

  ```javascript JavaScript theme={null}
  // Extend conversation with assistant's reply
  messages.push(response.choices[0].message);

  for (const tool_call of tool_calls) {
    const function_name = tool_call.function.name;

    if (function_name == "get_current_weather") {
      const function_args = JSON.parse(tool_call.function.arguments);
      const function_response = await get_current_weather(function_args.location);

      messages.push({
        "tool_call_id": tool_call.id,
        "role": "tool",
        "content": function_response,
      });
    }
  }

  const second_response = await client.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: messages,
    tools: tools,
    tool_choice: "auto",
  });

  console.log(second_response.choices[0].message.content);
  ```
</CodeGroup>

Output:

```
The current temperature in San Francisco, CA is 60 degrees.
```

## Tips

* Write clear, detailed function descriptions — model quality depends heavily on them
* Use lower temperatures (\< 1.0) to avoid erratic parameter values
* Avoid system messages when using tool calling
* Model quality degrades with more functions — keep the list focused
* Keep `top_p` and `top_k` at their defaults

## Supported features

| Feature               | Supported            |
| --------------------- | -------------------- |
| Single tool calls     | ✅                    |
| Parallel tool calls   | ✅ (quality may vary) |
| `tool_choice: "auto"` | ✅                    |
| `tool_choice: "none"` | ✅                    |
| Streaming mode        | ✅                    |
| Nested calls          | ❌                    |

## Notes

* Function definitions count toward your input token usage
* Inference usage is counted as normal when using tool calling
