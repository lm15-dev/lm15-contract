> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Reasoning Models

> Configure chain-of-thought reasoning with reasoning_effort and the reasoning parameter.

Some models on DeepInfra support extended chain-of-thought reasoning — the model "thinks through" a problem step by step before producing a final answer. By default, reasoning models produce a reasoning trace alongside the response. You can control this behavior with the `reasoning_effort` parameter.

## Supported models

Reasoning is available on models that support chain-of-thought, including:

* `deepseek-ai/DeepSeek-V4-Flash-0731`
* `deepseek-ai/DeepSeek-V4-Pro-0813`
* `zai-org/GLM-5.2`
* `moonshotai/Kimi-K3`
* `inclusionAI/Ling-3.0-flash`

Check the [model catalog](https://deepinfra.com/models) for the latest list.

## Controlling reasoning effort

Use `reasoning_effort` to control how much reasoning the model performs. Higher effort means deeper thinking but more output tokens and higher latency.

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ["DEEPINFRA_API_KEY"],
      base_url="https://api.deepinfra.com/v1/openai",
  )

  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Prove that the square root of 2 is irrational."}],
      extra_body={"reasoning_effort": "high"},
  )

  print(response.choices[0].message.content)
  ```

  ```javascript JavaScript theme={null}
  import OpenAI from "openai";

  const openai = new OpenAI({
    apiKey: process.env.DEEPINFRA_API_KEY,
    baseURL: "https://api.deepinfra.com/v1/openai",
  });

  const response = await openai.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: [{ role: "user", content: "Prove that the square root of 2 is irrational." }],
    reasoning_effort: "high",
  });

  console.log(response.choices[0].message.content);
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "reasoning_effort": "high",
        "messages": [
          {
            "role": "user",
            "content": "Prove that the square root of 2 is irrational."
          }
        ]
      }'
  ```
</CodeGroup>

## Disabling reasoning

Set `reasoning_effort` to `"none"` to disable chain-of-thought entirely. The model will respond directly without a reasoning trace — faster and cheaper.

<CodeGroup>
  ```python Python theme={null}
  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "What is the capital of France?"}],
      extra_body={"reasoning_effort": "none"},
  )
  ```

  ```javascript JavaScript theme={null}
  const response = await openai.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: [{ role: "user", content: "What is the capital of France?" }],
    reasoning_effort: "none",
  });
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "reasoning_effort": "none",
        "messages": [
          {
            "role": "user",
            "content": "What is the capital of France?"
          }
        ]
      }'
  ```
</CodeGroup>

## The `reasoning` parameter

For more granular control, use the `reasoning` object instead of `reasoning_effort`:

<CodeGroup>
  ```python Python theme={null}
  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Solve this step by step: 15! / 13!"}],
      extra_body={
          "reasoning": {
              "effort": "medium",
              "enabled": True,
          }
      },
  )
  ```

  ```javascript JavaScript theme={null}
  const response = await openai.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: [{ role: "user", content: "Solve this step by step: 15! / 13!" }],
    reasoning: {
      effort: "medium",
      enabled: true,
    },
  });
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "reasoning": {
          "effort": "medium",
          "enabled": true
        },
        "messages": [
          {
            "role": "user",
            "content": "Solve this step by step: 15! / 13!"
          }
        ]
      }'
  ```
</CodeGroup>

Setting `"enabled": false` is equivalent to `reasoning_effort: "none"`.

## When to use reasoning

| Use case                                | Recommended setting                     |
| --------------------------------------- | --------------------------------------- |
| Math, logic, and code problems          | `"high"` (default for reasoning models) |
| Multi-step analysis                     | `"medium"` or `"high"`                  |
| Simple Q\&A, translation, summarization | `"none"`                                |
| Cost-sensitive workloads                | `"none"` or `"low"`                     |

## Supported parameters

| Parameter           | Type      | Description                                                        |
| ------------------- | --------- | ------------------------------------------------------------------ |
| `reasoning_effort`  | `string`  | Controls reasoning depth: `"none"`, `"low"`, `"medium"`, `"high"`. |
| `reasoning`         | `object`  | Fine-grained reasoning config.                                     |
| `reasoning.effort`  | `string`  | Same values as `reasoning_effort`.                                 |
| `reasoning.enabled` | `boolean` | Explicitly enable or disable reasoning.                            |

## Notes

* Reasoning tokens count toward output token billing
* Disabling reasoning on a reasoning model makes it behave like a standard chat model
* `reasoning_effort: "none"` is equivalent to `reasoning: { enabled: false }`
* Not all models support reasoning — using these parameters on a non-reasoning model has no effect

<CardGroup cols={2}>
  <Card title="Chat Completions" icon="comments" href="/chat/overview">
    Full chat completions API reference.
  </Card>

  <Card title="Streaming" icon="wave-pulse" href="/chat/streaming">
    Stream reasoning responses token by token.
  </Card>

  <Card title="Prompt Caching" icon="database" href="/chat/prompt-caching">
    Cache long prompts for faster reasoning.
  </Card>
</CardGroup>
