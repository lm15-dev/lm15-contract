> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Agentic function calling patterns

> Tool use across multiple steps or conversation turns, covering multi-step and multi-turn agent loops.

To build agent loops, chain tool calls inside one response (multi-step), and conversations that thread tools across many turns (multi-turn).

## Multi-step function calling

Multi-step function calling chains sequential function calls within one conversation turn. The model calls a function, you process the result, and the result is fed back to inform the final response.

Here's an example of passing the result of a tool call from one completion into a second follow-up completion:

<CodeGroup>
  ```python Python theme={null}
  import json
  from together import Together

  client = Together()


  ## Example function to make available to model
  def get_current_weather(location, unit="fahrenheit"):
      """Get the weather for some location"""
      if "chicago" in location.lower():
          return json.dumps(
              {"location": "Chicago", "temperature": "13", "unit": unit}
          )
      elif "san francisco" in location.lower():
          return json.dumps(
              {"location": "San Francisco", "temperature": "55", "unit": unit}
          )
      elif "new york" in location.lower():
          return json.dumps(
              {"location": "New York", "temperature": "11", "unit": unit}
          )
      else:
          return json.dumps({"location": location, "temperature": "unknown"})


  # 1. Define a list of callable tools for the model
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
                          "description": "The unit of temperature",
                          "enum": ["celsius", "fahrenheit"],
                      },
                  },
              },
          },
      }
  ]

  # Create a running messages list to append to over time
  messages = [
      {
          "role": "system",
          "content": "You are a helpful assistant that can access external functions. The responses from these function calls will be appended to this dialogue. Please provide responses based on the information from these function calls.",
      },
      {
          "role": "user",
          "content": "What is the current temperature of New York, San Francisco and Chicago?",
      },
  ]

  # 2. Prompt the model with tools defined
  response = client.chat.completions.create(
      model="Qwen/Qwen3.5-9B",
      messages=messages,
      tools=tools,
  )

  # Save function call outputs for subsequent requests
  tool_calls = response.choices[0].message.tool_calls

  if tool_calls:
      # Add the assistant's response with tool calls to messages
      messages.append(
          {
              "role": "assistant",
              "content": "",
              "tool_calls": [tool_call.model_dump() for tool_call in tool_calls],
          }
      )

      # 3. Execute the function logic for each tool call
      for tool_call in tool_calls:
          function_name = tool_call.function.name
          function_args = json.loads(tool_call.function.arguments)

          if function_name == "get_current_weather":
              function_response = get_current_weather(
                  location=function_args.get("location"),
                  unit=function_args.get("unit"),
              )

              # 4. Provide function call results to the model
              messages.append(
                  {
                      "tool_call_id": tool_call.id,
                      "role": "tool",
                      "name": function_name,
                      "content": function_response,
                  }
              )

      # 5. The model should be able to give a response with the function results!
      function_enriched_response = client.chat.completions.create(
          model="Qwen/Qwen3.5-9B",
          messages=messages,
      )
      print(
          json.dumps(
              function_enriched_response.choices[0].message.model_dump(),
              indent=2,
          )
      )
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";
  import type { ChatCompletionMessageParam } from "together-ai/resources/chat/completions";

  const together = new Together();

  // Example function to make available to model
  function getCurrentWeather({
    location,
    unit = "fahrenheit",
  }: {
    location: string;
    unit: "fahrenheit" | "celsius";
  }) {
    let result: { location: string; temperature: number | null; unit: string };
    if (location.toLowerCase().includes("chicago")) {
      result = {
        location: "Chicago",
        temperature: 13,
        unit,
      };
    } else if (location.toLowerCase().includes("san francisco")) {
      result = {
        location: "San Francisco",
        temperature: 55,
        unit,
      };
    } else if (location.toLowerCase().includes("new york")) {
      result = {
        location: "New York",
        temperature: 11,
        unit,
      };
    } else {
      result = {
        location,
        temperature: null,
        unit,
      };
    }

    return JSON.stringify(result);
  }

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
  ];

  const messages: ChatCompletionMessageParam[] = [
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
  ];

  const response = await together.chat.completions.create({
    model: "Qwen/Qwen3.5-9B",
    messages,
    tools,
  });

  const toolCalls = response.choices[0].message?.tool_calls;
  if (toolCalls) {
    messages.push({
      role: "assistant",
      content: "",
      tool_calls: toolCalls,
    });
    for (const toolCall of toolCalls) {
      if (toolCall.function.name === "getCurrentWeather") {
        const args = JSON.parse(toolCall.function.arguments);
        const functionResponse = getCurrentWeather(args);

        messages.push({
          role: "tool",
          tool_call_id: toolCall.id,
          content: functionResponse,
        });
      }
    }

    const functionEnrichedResponse = await together.chat.completions.create({
      model: "Qwen/Qwen3.5-9B",
      messages,
      tools,
    });

    console.log(
      JSON.stringify(functionEnrichedResponse.choices[0].message, null, 2),
    );
  }
  ```
</CodeGroup>

And here's the final output from the second call:

```json JSON theme={null}
{
  "content": "The current temperature in New York is 11 degrees Fahrenheit, in San Francisco it is 55 degrees Fahrenheit, and in Chicago it is 13 degrees Fahrenheit.",
  "role": "assistant"
}
```

In this run, the model generated three tool call descriptions, your code iterated over them to execute each one, and the results were passed back so the model could produce a final answer.

## Multi-turn function calling

Multi-turn function calling maintains context across multiple conversation turns. Functions can be called at any point in the conversation, and previous function results inform future decisions.

<CodeGroup>
  ```python Python theme={null}
  import json
  from together import Together

  client = Together()

  # Define all available tools for the travel assistant
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
                          "description": "The unit of temperature",
                          "enum": ["celsius", "fahrenheit"],
                      },
                  },
                  "required": ["location"],
              },
          },
      },
      {
          "type": "function",
          "function": {
              "name": "get_restaurant_recommendations",
              "description": "Get restaurant recommendations for a specific location",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "The city and state, e.g. San Francisco, CA",
                      },
                      "cuisine_type": {
                          "type": "string",
                          "description": "Type of cuisine preferred",
                          "enum": [
                              "italian",
                              "chinese",
                              "mexican",
                              "american",
                              "french",
                              "japanese",
                              "any",
                          ],
                      },
                      "price_range": {
                          "type": "string",
                          "description": "Price range preference",
                          "enum": ["budget", "mid-range", "upscale", "any"],
                      },
                  },
                  "required": ["location"],
              },
          },
      },
  ]


  def get_current_weather(location, unit="fahrenheit"):
      """Get the weather for some location"""
      if "chicago" in location.lower():
          return json.dumps(
              {
                  "location": "Chicago",
                  "temperature": "13",
                  "unit": unit,
                  "condition": "cold and snowy",
              }
          )
      elif "san francisco" in location.lower():
          return json.dumps(
              {
                  "location": "San Francisco",
                  "temperature": "65",
                  "unit": unit,
                  "condition": "mild and partly cloudy",
              }
          )
      elif "new york" in location.lower():
          return json.dumps(
              {
                  "location": "New York",
                  "temperature": "28",
                  "unit": unit,
                  "condition": "cold and windy",
              }
          )
      else:
          return json.dumps(
              {
                  "location": location,
                  "temperature": "unknown",
                  "condition": "unknown",
              }
          )


  def get_restaurant_recommendations(
      location, cuisine_type="any", price_range="any"
  ):
      """Get restaurant recommendations for a location"""
      restaurants = {}

      if "san francisco" in location.lower():
          restaurants = {
              "italian": ["Tony's Little Star Pizza", "Perbacco"],
              "chinese": ["R&G Lounge", "Z&Y Restaurant"],
              "american": ["Zuni Café", "House of Prime Rib"],
              "seafood": ["Swan Oyster Depot", "Fisherman's Wharf restaurants"],
          }
      elif "chicago" in location.lower():
          restaurants = {
              "italian": ["Gibsons Italia", "Piccolo Sogno"],
              "american": ["Alinea", "Girl & Goat"],
              "pizza": ["Lou Malnati's", "Giordano's"],
              "steakhouse": ["Gibsons Bar & Steakhouse"],
          }
      elif "new york" in location.lower():
          restaurants = {
              "italian": ["Carbone", "Don Angie"],
              "american": ["The Spotted Pig", "Gramercy Tavern"],
              "pizza": ["Joe's Pizza", "Prince Street Pizza"],
              "fine_dining": ["Le Bernardin", "Eleven Madison Park"],
          }

      return json.dumps(
          {
              "location": location,
              "cuisine_filter": cuisine_type,
              "price_filter": price_range,
              "restaurants": restaurants,
          }
      )


  def handle_conversation_turn(messages, user_input):
      """Handle a single conversation turn with potential function calls"""
      # 3. Add user input to messages
      messages.append({"role": "user", "content": user_input})

      # 4. Get model response with tools
      response = client.chat.completions.create(
          model="zai-org/GLM-5.3",
          messages=messages,
          tools=tools,
      )

      tool_calls = response.choices[0].message.tool_calls

      if tool_calls:
          # 5. Add assistant response with tool calls
          messages.append(
              {
                  "role": "assistant",
                  "content": response.choices[0].message.content or "",
                  "tool_calls": [
                      tool_call.model_dump() for tool_call in tool_calls
                  ],
              }
          )

          # 6. Execute each function call
          for tool_call in tool_calls:
              function_name = tool_call.function.name
              function_args = json.loads(tool_call.function.arguments)

              print(f"🔧 Calling {function_name} with args: {function_args}")

              # Route to appropriate function
              if function_name == "get_current_weather":
                  function_response = get_current_weather(
                      location=function_args.get("location"),
                      unit=function_args.get("unit", "fahrenheit"),
                  )
              elif function_name == "get_restaurant_recommendations":
                  function_response = get_restaurant_recommendations(
                      location=function_args.get("location"),
                      cuisine_type=function_args.get("cuisine_type", "any"),
                      price_range=function_args.get("price_range", "any"),
                  )

              # 7. Add function response to messages
              messages.append(
                  {
                      "tool_call_id": tool_call.id,
                      "role": "tool",
                      "name": function_name,
                      "content": function_response,
                  }
              )

          # 8. Get final response with function results
          final_response = client.chat.completions.create(
              model="zai-org/GLM-5.3",
              messages=messages,
          )

          # 9. Add final assistant response to messages for context retention
          messages.append(
              {
                  "role": "assistant",
                  "content": final_response.choices[0].message.content,
              }
          )

          return final_response.choices[0].message.content


  # Initialize conversation with system message
  messages = [
      {
          "role": "system",
          "content": "You are a helpful travel planning assistant. You can access weather information and restaurant recommendations. Use the available tools to provide comprehensive travel advice based on the user's needs.",
      }
  ]

  # TURN 1: Initial weather request
  print("TURN 1:")
  print(
      "User: What is the current temperature of New York, San Francisco and Chicago?"
  )
  response1 = handle_conversation_turn(
      messages,
      "What is the current temperature of New York, San Francisco and Chicago?",
  )
  print(f"Assistant: {response1}")

  # TURN 2: Follow-up with activity and restaurant requests based on previous context
  print("\nTURN 2:")
  print(
      "User: Based on the weather, which city would be best for outdoor activities? And can you find some restaurant recommendations for that city?"
  )
  response2 = handle_conversation_turn(
      messages,
      "Based on the weather, which city would be best for outdoor activities? And can you find some restaurant recommendations for that city?",
  )
  print(f"Assistant: {response2}")
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";
  import type { ChatCompletionMessageParam } from "together-ai/resources/chat/completions";

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
          required: ["location"],
        },
      },
    },
    {
      type: "function",
      function: {
        name: "getRestaurantRecommendations",
        description: "Get restaurant recommendations for a specific location",
        parameters: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA",
            },
            cuisineType: {
              type: "string",
              description: "Type of cuisine preferred",
              enum: [
                "italian",
                "chinese",
                "mexican",
                "american",
                "french",
                "japanese",
                "any",
              ],
            },
            priceRange: {
              type: "string",
              description: "Price range preference",
              enum: ["budget", "mid-range", "upscale", "any"],
            },
          },
          required: ["location"],
        },
      },
    },
  ];

  function getCurrentWeather({
    location,
    unit = "fahrenheit",
  }: {
    location: string;
    unit?: string;
  }) {
    if (location.toLowerCase().includes("chicago")) {
      return JSON.stringify({
        location: "Chicago",
        temperature: "13",
        unit,
        condition: "cold and snowy",
      });
    } else if (location.toLowerCase().includes("san francisco")) {
      return JSON.stringify({
        location: "San Francisco",
        temperature: "65",
        unit,
        condition: "mild and partly cloudy",
      });
    } else if (location.toLowerCase().includes("new york")) {
      return JSON.stringify({
        location: "New York",
        temperature: "28",
        unit,
        condition: "cold and windy",
      });
    } else {
      return JSON.stringify({
        location,
        temperature: "unknown",
        condition: "unknown",
      });
    }
  }

  function getRestaurantRecommendations({
    location,
    cuisineType = "any",
    priceRange = "any",
  }: {
    location: string;
    cuisineType?: string;
    priceRange?: string;
  }) {
    let restaurants = {};

    if (location.toLowerCase().includes("san francisco")) {
      restaurants = {
        italian: ["Tony's Little Star Pizza", "Perbacco"],
        chinese: ["R&G Lounge", "Z&Y Restaurant"],
        american: ["Zuni Café", "House of Prime Rib"],
        seafood: ["Swan Oyster Depot", "Fisherman's Wharf restaurants"],
      };
    } else if (location.toLowerCase().includes("chicago")) {
      restaurants = {
        italian: ["Gibsons Italia", "Piccolo Sogno"],
        american: ["Alinea", "Girl & Goat"],
        pizza: ["Lou Malnati's", "Giordano's"],
        steakhouse: ["Gibsons Bar & Steakhouse"],
      };
    } else if (location.toLowerCase().includes("new york")) {
      restaurants = {
        italian: ["Carbone", "Don Angie"],
        american: ["The Spotted Pig", "Gramercy Tavern"],
        pizza: ["Joe's Pizza", "Prince Street Pizza"],
        fine_dining: ["Le Bernardin", "Eleven Madison Park"],
      };
    }

    return JSON.stringify({
      location,
      cuisine_filter: cuisineType,
      price_filter: priceRange,
      restaurants,
    });
  }

  async function handleConversationTurn(
    messages: ChatCompletionMessageParam[],
    userInput: string,
  ) {
    messages.push({ role: "user", content: userInput });

    const response = await together.chat.completions.create({
      model: "Qwen/Qwen3.5-9B",
      messages,
      tools,
    });

    const toolCalls = response.choices[0].message?.tool_calls;

    if (toolCalls) {
      messages.push({
        role: "assistant",
        content: response.choices[0].message?.content || "",
        tool_calls: toolCalls,
      });

      for (const toolCall of toolCalls) {
        const functionName = toolCall.function.name;
        const functionArgs = JSON.parse(toolCall.function.arguments);

        let functionResponse: string;

        if (functionName === "getCurrentWeather") {
          functionResponse = getCurrentWeather(functionArgs);
        } else if (functionName === "getRestaurantRecommendations") {
          functionResponse = getRestaurantRecommendations(functionArgs);
        } else {
          functionResponse = "Function not found";
        }

        messages.push({
          role: "tool",
          tool_call_id: toolCall.id,
          content: functionResponse,
        });
      }

      const finalResponse = await together.chat.completions.create({
        model: "Qwen/Qwen3.5-9B",
        messages,
      });

      const content = finalResponse.choices[0].message?.content || "";
      messages.push({
        role: "assistant",
        content,
      });

      return content;
    } else {
      const content = response.choices[0].message?.content || "";
      messages.push({
        role: "assistant",
        content,
      });
      return content;
    }
  }

  // Example usage
  async function runMultiTurnExample() {
    const messages: ChatCompletionMessageParam[] = [
      {
        role: "system",
        content:
          "You are a helpful travel planning assistant. You can access weather information and restaurant recommendations. Use the available tools to provide comprehensive travel advice based on the user's needs.",
      },
    ];

    console.log("TURN 1:");
    console.log(
      "User: What is the current temperature of New York, San Francisco and Chicago?",
    );
    const response1 = await handleConversationTurn(
      messages,
      "What is the current temperature of New York, San Francisco and Chicago?",
    );
    console.log(`Assistant: ${response1}`);

    console.log("\nTURN 2:");
    console.log(
      "User: Based on the weather, which city would be best for outdoor activities? And can you find some restaurant recommendations for that city?",
    );
    const response2 = await handleConversationTurn(
      messages,
      "Based on the weather, which city would be best for outdoor activities? And can you find some restaurant recommendations for that city?",
    );
    console.log(`Assistant: ${response2}`);
  }

  runMultiTurnExample();
  ```
</CodeGroup>

In this example, the assistant:

1. **Turn 1:** Calls weather functions for three cities and provides temperature information.
2. **Turn 2:** Remembers the previous weather data, analyzes which city is best for outdoor activities (San Francisco with 65°F), and automatically calls the restaurant recommendation function for that city.

The model maintains context across turns and makes informed decisions based on previous interactions.
