> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Call functions in parallel

> Multiple tool calls in one response, covering parallel calls to the same tool and to different tools.

Patterns where the model returns multiple tool calls in a single response, run together.

## Parallel function calling

In parallel function calling, the same function is called multiple times simultaneously with different parameters. This is more efficient than making sequential calls for similar operations.

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
              "content": "What is the current temperature of New York, San Francisco and Chicago?",
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
        content:
          "What is the current temperature of New York, San Francisco and Chicago?",
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
             "content": "What is the current temperature of New York, San Francisco and Chicago?"
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

In response, the `tool_calls` key of the LLM's response will look like this:

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
  },
  {
    "index": 1,
    "id": "call_agrjihqjcb0r499vrclwrgdj",
    "type": "function",
    "function": {
      "arguments": "{\"location\":\"San Francisco, CA\",\"unit\":\"fahrenheit\"}",
      "name": "get_current_weather"
    }
  },
  {
    "index": 2,
    "id": "call_17s148ekr4hk8m5liicpwzkk",
    "type": "function",
    "function": {
      "arguments": "{\"location\":\"Chicago, IL\",\"unit\":\"fahrenheit\"}",
      "name": "get_current_weather"
    }
  }
]
```

The model returns three function calls. You can execute them programmatically to answer the user's question.

## Parallel multiple function calling

This pattern combines parallel and multiple function calling: multiple different functions are available, and one user prompt triggers multiple different function calls simultaneously. The model chooses which functions to call AND calls them in parallel.

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
              "content": "What's the current price of Apple and Google stock? What is the weather in New York, San Francisco and Chicago?",
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
        content:
          "What's the current price of Apple and Google stock? What is the weather in New York, San Francisco and Chicago?",
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
             "content": "What'\''s the current price of Apple and Google stock? What is the weather in New York, San Francisco and Chicago?"
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

This produces five function calls: two for stock prices (Apple and Google) and three for weather (New York, San Francisco, and Chicago), all executed in parallel.

```json JSON theme={null}
[
  {
    "id": "call_8b31727cf80f41099582a259",
    "type": "function",
    "function": {
      "name": "get_current_stock_price",
      "arguments": "{\"symbol\": \"AAPL\"}"
    },
    "index": null
  },
  {
    "id": "call_b54bcaadceec423d82f28611",
    "type": "function",
    "function": {
      "name": "get_current_stock_price",
      "arguments": "{\"symbol\": \"GOOGL\"}"
    },
    "index": null
  },
  {
    "id": "call_f1118a9601c644e1b78a4a8c",
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "arguments": "{\"location\": \"San Francisco, CA\"}"
    },
    "index": null
  },
  {
    "id": "call_95dc5028837e4d1e9b247388",
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "arguments": "{\"location\": \"New York, NY\"}"
    },
    "index": null
  },
  {
    "id": "call_1b8b58809d374f15a5a990d9",
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "arguments": "{\"location\": \"Chicago, IL\"}"
    },
    "index": null
  }
]
```
