> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Chat Completions

> OpenAI-compatible chat completions API — just change the base URL and model name.

DeepInfra offers an OpenAI-compatible chat completions API for all [LLM models](https://deepinfra.com/models/text-generation) at the best prices for open-source model inference. For other model types (embeddings, image generation, speech, reranking, and more), see [More APIs](/apis/completions). The endpoint is:

```
https://api.deepinfra.com/v1/openai
```

The only changes you need to make from your existing OpenAI code:

1. Set `base_url` to `https://api.deepinfra.com/v1/openai`
2. Set `api_key` to your DeepInfra token
3. Set `model` to a model from [our catalog](https://deepinfra.com/models)

## Install the SDK

<CodeGroup>
  ```bash Python theme={null}
  pip install openai
  ```

  ```bash JavaScript theme={null}
  npm install openai
  ```
</CodeGroup>

## Basic chat completion

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  openai = OpenAI(
      api_key=os.environ["DEEPINFRA_API_KEY"],
      base_url="https://api.deepinfra.com/v1/openai",
  )

  chat_completion = openai.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Hello"}],
  )

  print(chat_completion.choices[0].message.content)
  print(chat_completion.usage.prompt_tokens, chat_completion.usage.completion_tokens)
  ```

  ```javascript JavaScript theme={null}
  import OpenAI from "openai";

  const openai = new OpenAI({
    apiKey: process.env.DEEPINFRA_API_KEY,
    baseURL: "https://api.deepinfra.com/v1/openai",
  });

  const completion = await openai.chat.completions.create({
    messages: [{ role: "user", content: "Hello" }],
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
  });

  console.log(completion.choices[0].message.content);
  console.log(completion.usage.prompt_tokens, completion.usage.completion_tokens);
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
            "content": "Hello!"
          }
        ]
      }'
  ```
</CodeGroup>

## Multi-turn conversations

To create a longer conversation, include the full message history in every request. The model uses this context to provide better answers.

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  openai = OpenAI(
      api_key=os.environ["DEEPINFRA_API_KEY"],
      base_url="https://api.deepinfra.com/v1/openai",
  )

  chat_completion = openai.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[
          {"role": "system", "content": "Respond like a michelin starred chef."},
          {"role": "user", "content": "Can you name at least two different techniques to cook lamb?"},
          {"role": "assistant", "content": "Bonjour! Let me tell you, my friend, cooking lamb is an art form..."},
          {"role": "user", "content": "Tell me more about the second method."},
      ],
  )

  print(chat_completion.choices[0].message.content)
  ```

  ```javascript JavaScript theme={null}
  import OpenAI from "openai";

  const openai = new OpenAI({
    baseURL: "https://api.deepinfra.com/v1/openai",
    apiKey: process.env.DEEPINFRA_API_KEY,
  });

  const completion = await openai.chat.completions.create({
    messages: [
      {role: "system", content: "Respond like a michelin starred chef."},
      {role: "user", content: "Can you name at least two different techniques to cook lamb?"},
      {role: "assistant", content: "Bonjour! Let me tell you, my friend, cooking lamb is an art form..."},
      {role: "user", content: "Tell me more about the second method."}
    ],
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
  });

  console.log(completion.choices[0].message.content);
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "messages": [
          {"role": "system", "content": "Respond like a michelin starred chef."},
          {"role": "user", "content": "Can you name at least two different techniques to cook lamb?"},
          {"role": "assistant", "content": "Bonjour! Let me tell you..."},
          {"role": "user", "content": "Tell me more about the second method."}
        ]
      }'
  ```
</CodeGroup>

The longer the conversation, the more tokens it uses. The maximum conversation length is determined by the model's context size.

## Supported parameters

| Parameter              | Notes                                                                                                                                  |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                | Model name, or `MODEL_NAME:VERSION`, or `deploy_id:DEPLOY_ID`                                                                          |
| `messages`             | Roles: `system`, `user`, `assistant`                                                                                                   |
| `max_tokens`           | Max tokens to generate. See [Max output tokens](#max-output-tokens)                                                                    |
| `stream`               | See [Streaming](/chat/streaming)                                                                                                       |
| `temperature`          | Sampling temperature between 0 and 2. Higher values produce more random output; lower values more deterministic. Default: `1.0`        |
| `top_p`                | Nucleus sampling threshold — only tokens comprising the top `top_p` probability mass are considered. Default: `1.0`                    |
| `stop`                 | Up to 4 sequences where the API will stop generating further tokens                                                                    |
| `n`                    | Number of completion sequences to return. Default: `1`                                                                                 |
| `presence_penalty`     | Penalizes tokens that have already appeared in the text, encouraging the model to discuss new topics. Range: -2.0 to 2.0. Default: `0` |
| `frequency_penalty`    | Penalizes tokens based on how often they've appeared so far, reducing repetition. Range: -2.0 to 2.0. Default: `0`                     |
| `response_format`      | See [Structured Outputs](/chat/structured-outputs)                                                                                     |
| `tools`, `tool_choice` | See [Tool Calling](/chat/tool-calling)                                                                                                 |
| `service_tier`         | Select a service tier (`"priority"` or `"flex"`) for tagged models. See [Service Tier](#service-tier) below.                           |
| `fail_fast`            | Reject with HTTP 429 instead of queueing when the model is at capacity. See [Fail fast](#fail-fast) below. Default: `false`            |
| `reasoning_effort`     | Controls reasoning depth for reasoning models. See [Reasoning Models](/chat/reasoning).                                                |

<Note>
  We may not be 100% compatible with all OpenAI parameters. Let us know on Discord or by email if something you need is missing.
</Note>

For the complete parameter reference, see the [API reference](/api-reference/chat-completions/openai-chat-completions).

## Service tier

Set the optional `service_tier` parameter to run a request on a non-standard tier. Two tiers are available on tagged models: **priority** (faster, at a premium) and **flex** (cheaper, best-effort). Leave `service_tier` unset for standard real-time scheduling and pricing.

### Priority

Set `service_tier` to `"priority"` to request priority inference on supported models. Priority requests get faster time-to-first-token and higher throughput during peak demand.

<Warning>
  Priority inference incurs a 50% surcharge on top of the model's standard per-token price.
</Warning>

<CodeGroup>
  ```python Python theme={null}
  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Hello!"}],
      extra_body={"service_tier": "priority"},
  )
  ```

  ```javascript JavaScript theme={null}
  const response = await openai.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: [{ role: "user", content: "Hello!" }],
    service_tier: "priority",
  });
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "service_tier": "priority",
        "messages": [
          {
            "role": "user",
            "content": "Hello!"
          }
        ]
      }'
  ```
</CodeGroup>

### Flex

Set `service_tier` to `"flex"` to run Chat Completions requests at a lower cost in exchange for slower response times and occasional resource unavailability. It's ideal for non-production or lower-priority tasks such as model evaluations, data enrichment, and asynchronous workloads. When a model is busy, a flex request may wait up to 10 minutes for available capacity before it runs or is rejected with an HTTP 429, so use it for work you can retry.

<Note>
  Flex inference is billed at a 20% discount off the model's standard per-token price.
</Note>

<CodeGroup>
  ```python Python theme={null}
  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Hello!"}],
      extra_body={"service_tier": "flex"},
  )
  ```

  ```javascript JavaScript theme={null}
  const response = await openai.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: [{ role: "user", content: "Hello!" }],
    service_tier: "flex",
  });
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "service_tier": "flex",
        "messages": [
          {
            "role": "user",
            "content": "Hello!"
          }
        ]
      }'
  ```
</CodeGroup>

The response includes a `service_tier` field confirming which tier was actually used. Not all models support these tiers — check the model page for availability. If a model doesn't support the requested tier, the request is served at the standard tier and billed at the standard price; no error is returned.

## Fail fast

By default, a request sent to a model that is at capacity waits in the queue until capacity frees up. Set the optional `fail_fast` parameter to `true` to get an immediate HTTP 429 instead of waiting.

This is meant for latency-sensitive callers that would rather go somewhere else than sit in a queue — for example, clients that fail over to another provider on rejection. The 429 arrives as soon as the request would have been queued, so you don't spend your latency budget waiting.

<CodeGroup>
  ```python Python theme={null}
  response = client.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Hello!"}],
      extra_body={"fail_fast": True},
  )
  ```

  ```javascript JavaScript theme={null}
  const response = await openai.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: [{ role: "user", content: "Hello!" }],
    fail_fast: true,
  });
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "fail_fast": true,
        "messages": [
          {
            "role": "user",
            "content": "Hello!"
          }
        ]
      }'
  ```
</CodeGroup>

Rejection is capacity-aware rather than backlog-triggered: a `fail_fast` request is rejected only when the model is busy enough that serving it would actually be slow. Whenever there is spare capacity the request is admitted and served exactly as if `fail_fast` were unset, so enabling it does not cost you throughput on an idle model.

When a request is rejected, the response is an HTTP 429 carrying the `engine_overloaded` code:

```json theme={null}
{
  "error": {
    "message": "Model busy, retry later",
    "type": "invalid_request_error",
    "param": null,
    "code": "engine_overloaded"
  }
}
```

<Note>
  A rejected request never reaches the model, so no inference happens and nothing is billed.
</Note>

If you set both `fail_fast: true` and `service_tier: "priority"`, `fail_fast` wins — the explicit request not to wait is honored, and you get a 429 rather than a priority slot in the queue.

## Max output tokens

The maximum number of tokens that can be generated in a single response is model-dependent, with a hard cap of 16384 tokens for most models. Set `max_tokens` to control the limit for a specific request.

### Continuing responses beyond the limit

If you need a longer response, use response continuation: send a follow-up request with the previous response included as an assistant message, and the model will continue from where it left off.

```bash theme={null}
curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "messages": [
            {"role": "user", "content": "Write a very long essay about AI."},
            {"role": "assistant", "content": "<previous truncated response>"}
        ],
        "max_tokens": 4096
    }'
```

Note: response continuation cannot extend past the model's total context window. A 400 error is returned when the total context size is exceeded.

## What's next

<CardGroup cols={2}>
  <Card title="Streaming" icon="wave-pulse" href="/chat/streaming">
    Stream tokens as they're generated.
  </Card>

  <Card title="Structured Outputs" icon="brackets-curly" href="/chat/structured-outputs">
    Get responses in JSON format.
  </Card>

  <Card title="Tool Calling" icon="wrench" href="/chat/tool-calling">
    Give models access to external functions.
  </Card>

  <Card title="Vision" icon="eye" href="/chat/vision">
    Send images alongside text.
  </Card>

  <Card title="Reasoning Models" icon="brain-circuit" href="/chat/reasoning">
    Control chain-of-thought reasoning behavior.
  </Card>
</CardGroup>
