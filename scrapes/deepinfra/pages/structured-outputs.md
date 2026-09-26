> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Structured Outputs

> Get model responses in JSON format using response_format.

In addition to text, the DeepInfra API can return responses in JSON format. This is supported in both our inference API and our OpenAI-compatible API, across [many of our models](https://deepinfra.com/models?q=json).

There are two modes:

| Mode          | How to use                                      | When to use                        |
| ------------- | ----------------------------------------------- | ---------------------------------- |
| `json_object` | `{"type": "json_object"}`                       | Any valid JSON object, schema-free |
| `json_schema` | `{"type": "json_schema", "json_schema": {...}}` | Enforces a strict output schema    |

## json\_object mode

The simplest way to get JSON output. The model returns a valid JSON object but you don't control the exact shape.

<CodeGroup>
  ```python Python theme={null}
  import os

  import openai
  import json

  client = openai.OpenAI(
      base_url="https://api.deepinfra.com/v1/openai",
      api_key=os.environ["DEEPINFRA_API_KEY"],
  )

  messages = [
      {
          "role": "user",
          "content": "Provide a JSON list of 3 famous scientific breakthroughs in the past century, all of the countries which contributed, and in what year."
      }
  ]

  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=messages,
      response_format={"type": "json_object"},
  )

  print(response.choices[0].message.content)
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "messages": [
          {
            "role": "user",
            "content": "Provide a JSON list of 3 famous scientific breakthroughs."
          }
        ],
        "response_format": {"type": "json_object"}
      }'
  ```
</CodeGroup>

## json\_schema mode

Enforces a strict output schema using [JSON Schema](https://json-schema.org/). The model is constrained to produce only values that match your schema — useful when downstream code depends on a fixed structure.

<CodeGroup>
  ```python Python theme={null}
  import os

  import openai
  import json

  client = openai.OpenAI(
      base_url="https://api.deepinfra.com/v1/openai",
      api_key=os.environ["DEEPINFRA_API_KEY"],
  )

  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[
          {
              "role": "user",
              "content": "Extract the name, country, and year from: 'Alexander Fleming discovered Penicillin in the UK in 1928.'"
          }
      ],
      response_format={
          "type": "json_schema",
          "json_schema": {
              "name": "breakthrough",
              "strict": True,
              "schema": {
                  "type": "object",
                  "properties": {
                      "name": {"type": "string"},
                      "country": {"type": "string"},
                      "year": {"type": "integer"}
                  },
                  "required": ["name", "country", "year"],
                  "additionalProperties": False
              }
          }
      }
  )

  print(json.loads(response.choices[0].message.content))
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "messages": [
          {
            "role": "user",
            "content": "Extract the name, country, and year from: '\''Alexander Fleming discovered Penicillin in the UK in 1928.'\''"
          }
        ],
        "response_format": {
          "type": "json_schema",
          "json_schema": {
            "name": "breakthrough",
            "strict": true,
            "schema": {
              "type": "object",
              "properties": {
                "name": {"type": "string"},
                "country": {"type": "string"},
                "year": {"type": "integer"}
              },
              "required": ["name", "country", "year"],
              "additionalProperties": false
            }
          }
        }
      }'
  ```
</CodeGroup>

Output:

```json theme={null}
{"name": "Penicillin", "country": "UK", "year": 1928}
```

## Tips

**Always prompt the model to produce JSON.** While not strictly required for `json_object`, mentioning the expected format in your prompt improves consistency.

**Prefer `json_schema` for production.** When your code depends on specific field names or types, `json_schema` with `"strict": true` eliminates shape surprises.

**Watch for truncation.** If the model stops due to `max_tokens` or `length`, the JSON may be incomplete. Always validate before parsing.

## Caveats

<Warning>
  JSON mode can affect model alignment. When forced to produce structured output, some models are more likely to hallucinate values rather than say "I don't know." This is especially visible for prompts about real-time data (weather, stock prices, etc.).

  Example: asking "What's the weather in San Francisco?" with JSON mode enabled may cause the model to fabricate a weather forecast rather than explaining it doesn't have real-time data.
</Warning>

**Best practices:**

* Use JSON mode for structured data extraction tasks, not for general question answering
* Keep prompts specific about the expected schema
* Validate model output before using it in production systems
* Use lower temperatures (\< 0.7) for more consistent structure
