> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Call functions

> One tool call per response, covering simple and multiple-tool patterns.

The two simplest patterns: one tool, one call (simple), and many tools available with the model picking one (multiple).

## Simple function calling

Suppose your application has access to a `get_current_weather` function that takes two named arguments, `location` and `unit`:

<CodeGroup>
  ```python Python theme={null}
  # Hypothetical function in your app
  get_current_weather(location="San Francisco, CA", unit="fahrenheit")
  ```

  ```typescript TypeScript theme={null}
  // Hypothetical function in your app
  getCurrentWeather({
    location: "San Francisco, CA",
    unit: "fahrenheit",
  });
  ```
</CodeGroup>

Make this function available to the LLM by passing its description to the `tools` key alongside the user's query. Suppose the user asks, "What is the current temperature of New York?"

<CodeGroup>
  ```python Python theme={null}
  import json
  from together import Together

  client = Together()

  response = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      messages=[
          {
              "role": "system",
              "content": "You are a helpful assistant that can access external functions. The responses from these function calls will be appended to this dialogue. Please provide responses based on the information from these function calls.",
          },
          {
              "role": "user",
              "content": "What is the current temperature of New York?",
          },
      ],
      tools=[
          {
              "type": "function",
              "function": {
                  "name": "get_current_weather",
                  "description": "Get the current weather in a given location",
                  "parameters": {
                      "type": "object",
                      "properties": {
                          "location": {
                              "type": "string",
                              "description": "The city and state, e.g. San Francisco, CA",
                          },
                          "unit": {
                              "type": "string",
                              "enum": ["celsius", "fahrenheit"],
                          },
                      },
                  },
              },
          }
      ],
  )

  print(
      json.dumps(
          response.choices[0].message.model_dump()["tool_calls"],
          indent=2,
      )
  )
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  const response = await together.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    messages: [
      {
        role: "system",
        content:
          "You are a helpful assistant that can access external functions. The responses from these function calls will be appended to this dialogue. Please provide responses based on the information from these function calls.",
      },
      {
        role: "user",
        content: "What is the current temperature of New York?",
      },
    ],
    tools: [
      {
        type: "function",
        function: {
          name: "getCurrentWeather",
          description: "Get the current weather in a given location",
          parameters: {
            type: "object",
            properties: {
              location: {
                type: "string",
                description: "The city and state, e.g. San Francisco, CA",
              },
              unit: {
                type: "string",
                description: "The unit of temperature",
                enum: ["celsius", "fahrenheit"],
              },
            },
          },
        },
      },
    ],
  });

  console.log(JSON.stringify(response.choices[0].message?.tool_calls, null, 2));
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
         "model": "Qwen/Qwen3.5-9B",
         "messages": [
           {
             "role": "system",
             "content": "You are a helpful assistant that can access external functions. The responses from these function calls will be appended to this dialogue. Please provide responses based on the information from these function calls."
           },
           {
             "role": "user",
             "content": "What is the current temperature of New York?"
           }
         ],
         "tools": [
           {
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
                   },
                   "unit": {
                     "type": "string",
                     "enum": ["celsius", "fahrenheit"]
                   }
                 }
               }
             }
           }
         ]
       }'
  ```
</CodeGroup>

The model responds with a single function call in the `tool_calls` array, specifying the function name and arguments needed to get the weather for New York.

```json JSON theme={null}
[
  {
    "index": 0,
    "id": "call_aisak3q1px3m2lzb41ay6rwf",
    "type": "function",
    "function": {
      "arguments": "{\"location\":\"New York, NY\",\"unit\":\"fahrenheit\"}",
      "name": "get_current_weather"
    }
  }
]
```

You can now programmatically execute the function call to answer the user's question.

### Streaming

Function calling also works with streaming responses. When you enable streaming, the model returns tool calls incrementally, accessible from the `delta.tool_calls` object in each chunk.

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  tools = [
      {
          "type": "function",
          "function": {
              "name": "get_weather",
              "description": "Get current temperature for a given location.",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "City and country e.g. Bogotá, Colombia",
                      }
                  },
                  "required": ["location"],
                  "additionalProperties": False,
              },
              "strict": True,
          },
      }
  ]

  stream = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      reasoning={"enabled": False},
      messages=[{"role": "user", "content": "What's the weather in NYC?"}],
      tools=tools,
      stream=True,
  )

  for chunk in stream:
      if not chunk.choices:
          continue
      delta = chunk.choices[0].delta
      tool_calls = getattr(delta, "tool_calls", [])
      print(tool_calls)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const client = new Together();

  const tools = [
    {
      type: "function",
      function: {
        name: "get_weather",
        description: "Get current temperature for a given location.",
        parameters: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "City and country e.g. Bogotá, Colombia",
            },
          },
          required: ["location"],
          additionalProperties: false,
        },
        strict: true,
      },
    },
  ];

  const stream = await client.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    reasoning: { enabled: false },
    messages: [{ role: "user", content: "What's the weather in NYC?" }],
    tools,
    stream: true,
  });

  for await (const chunk of stream) {
    const delta = chunk.choices[0]?.delta;
    const toolCalls = delta?.tool_calls ?? [];
    console.log(toolCalls);
  }
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
         "model": "Qwen/Qwen3.5-9B",
          "reasoning": {"enabled": false},
         "messages": [
           {
             "role": "user",
             "content": "What'\''s the weather in NYC?"
           }
         ],
         "tools": [
           {
             "type": "function",
             "function": {
               "name": "get_weather",
               "description": "Get current temperature for a given location.",
               "parameters": {
                 "type": "object",
                 "properties": {
                   "location": {
                     "type": "string",
                     "description": "City and country e.g. Bogotá, Colombia"
                   }
                 },
                 "required": ["location"],
                 "additionalProperties": false
               },
               "strict": true
             }
           }
         ],
         "stream": true
       }'
  ```
</CodeGroup>

The model responds with streamed function calls:

```json theme={null}
# delta 1
[
  {
    "index": 0,
    "id": "call_fwbx4e156wigo9ayq7tszngh",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": ""
    }
  }
]

# delta 2
[
  {
    "index": 0,
    "function": {
      "arguments": "{\"location\":\"New York City, USA\"}"
    }
  }
]
```

<Note>
  **Tool calls don't show up in** `message.content`**:** When a model decides to call a tool, the call lands in `message.tool_calls`, not in the content string. Some models return `null` for `message.content` on a tool-calling turn. Read the call from `message.tool_calls[0].function.name` and `.arguments`.
</Note>

## Multiple function calling

Multiple function calling makes several functions available and lets the model choose the best one based on the user's intent. The model has to understand the request and pick the appropriate tool from the options.

The example below provides two tools to the model. The model responds with one tool invocation.

<CodeGroup>
  ```python Python theme={null}
  import json
  from together import Together

  client = Together()

  tools = [
      {
          "type": "function",
          "function": {
              "name": "get_current_weather",
              "description": "Get the current weather in a given location",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "The city and state, e.g. San Francisco, CA",
                      },
                      "unit": {
                          "type": "string",
                          "enum": ["celsius", "fahrenheit"],
                      },
                  },
              },
          },
      },
      {
          "type": "function",
          "function": {
              "name": "get_current_stock_price",
              "description": "Get the current stock price for a given stock symbol",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "symbol": {
                          "type": "string",
                          "description": "The stock symbol, e.g. AAPL, GOOGL, TSLA",
                      },
                      "exchange": {
                          "type": "string",
                          "description": "The stock exchange (optional)",
                          "enum": ["NYSE", "NASDAQ", "LSE", "TSX"],
                      },
                  },
                  "required": ["symbol"],
              },
          },
      },
  ]

  response = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      messages=[
          {
              "role": "user",
              "content": "What's the current price of Apple's stock?",
          },
      ],
      tools=tools,
  )

  print(
      json.dumps(
          response.choices[0].message.model_dump()["tool_calls"],
          indent=2,
      )
  )
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  const tools = [
    {
      type: "function",
      function: {
        name: "getCurrentWeather",
        description: "Get the current weather in a given location",
        parameters: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA",
            },
            unit: {
              type: "string",
              description: "The unit of temperature",
              enum: ["celsius", "fahrenheit"],
            },
          },
        },
      },
    },
    {
      type: "function",
      function: {
        name: "getCurrentStockPrice",
        description: "Get the current stock price for a given stock symbol",
        parameters: {
          type: "object",
          properties: {
            symbol: {
              type: "string",
              description: "The stock symbol, e.g. AAPL, GOOGL, TSLA",
            },
            exchange: {
              type: "string",
              description: "The stock exchange (optional)",
              enum: ["NYSE", "NASDAQ", "LSE", "TSX"],
            },
          },
          required: ["symbol"],
        },
      },
    },
  ];

  const response = await together.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    messages: [
      {
        role: "user",
        content: "What's the current price of Apple's stock?",
      },
    ],
    tools,
  });

  console.log(JSON.stringify(response.choices[0].message?.tool_calls, null, 2));
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
         "model": "Qwen/Qwen3.5-9B",
         "messages": [
           {
             "role": "user",
             "content": "What'\''s the current price of Apple'\''s stock?"
           }
         ],
         "tools": [
           {
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
                   },
                   "unit": {
                     "type": "string",
                     "enum": ["celsius", "fahrenheit"]
                   }
                 }
               }
             }
           },
           {
             "type": "function",
             "function": {
               "name": "get_current_stock_price",
               "description": "Get the current stock price for a given stock symbol",
               "parameters": {
                 "type": "object",
                 "properties": {
                   "symbol": {
                     "type": "string",
                     "description": "The stock symbol, e.g. AAPL, GOOGL, TSLA"
                   },
                   "exchange": {
                     "type": "string",
                     "description": "The stock exchange (optional)",
                     "enum": ["NYSE", "NASDAQ", "LSE", "TSX"]
                   }
                 },
                 "required": ["symbol"]
               }
             }
           }
         ]
       }'
  ```
</CodeGroup>

In this example, both weather and stock functions are available. The model correctly identifies that the user is asking about stock prices and calls the `get_current_stock_price` function.

### Select a specific tool

To force the model to use a specific tool, pass the tool's name to the `tool_choice` parameter:

<CodeGroup>
  ```python Python theme={null}
  response = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      messages=[
          {
              "role": "user",
              "content": "What's the current price of Apple's stock?",
          },
      ],
      tools=tools,
      tool_choice={
          "type": "function",
          "function": {"name": "get_current_stock_price"},
      },
  )
  ```

  ```typescript TypeScript theme={null}
  const response = await together.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    messages: [
      {
        role: "user",
        content: "What's the current price of Apple's stock?",
      },
    ],
    tools,
    tool_choice: { type: "function", function: { name: "getCurrentStockPrice" } },
  });
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
         "model": "Qwen/Qwen3.5-9B",
         "messages": [
           {
             "role": "user",
             "content": "What'\''s the current price of Apple'\''s stock?"
           }
         ],
         "tools": [
           {
             "type": "function",
             "function": {
               "name": "get_current_stock_price",
               "description": "Get the current stock price for a given stock symbol",
               "parameters": {
                 "type": "object",
                 "properties": {
                   "symbol": {
                     "type": "string",
                     "description": "The stock symbol, e.g. AAPL, GOOGL, TSLA"
                   }
                 },
                 "required": ["symbol"]
               }
             }
           }
         ],
         "tool_choice": {
           "type": "function",
           "function": {
             "name": "get_current_stock_price"
           }
         }
       }'
  ```
</CodeGroup>

This forces the model to use the specified function regardless of the user's phrasing.

### `tool_choice` options

The `tool_choice` parameter controls how the model uses functions. It accepts:

**String values:**

* `"auto"` (default): The model decides whether to call a function or generate a text response.
* `"none"`: The model never calls functions, only generates text.
* `"required"`: The model must call at least one function.
