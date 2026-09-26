> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Streaming

> Stream chat completion responses token by token using server-sent events.

DeepInfra supports streaming responses via server-sent events (SSE), the same protocol as OpenAI. Set `stream: true` in your request to enable it.

## Examples

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  openai = OpenAI(
      api_key=os.environ["DEEPINFRA_API_KEY"],
      base_url="https://api.deepinfra.com/v1/openai",
  )

  stream = openai.chat.completions.create(
      model="deepseek-ai/DeepSeek-V4-Flash-0731",
      messages=[{"role": "user", "content": "Hello"}],
      stream=True,
  )

  for event in stream:
      if event.choices[0].finish_reason:
          print(event.choices[0].finish_reason,
                event.usage['prompt_tokens'],
                event.usage['completion_tokens'])
      else:
          print(event.choices[0].delta.content, end="", flush=True)
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
    stream: true,
  });

  for await (const chunk of completion) {
    if (chunk.choices[0].finish_reason) {
      console.log(chunk.choices[0].finish_reason,
                  chunk.usage.prompt_tokens,
                  chunk.usage.completion_tokens);
    } else {
      process.stdout.write(chunk.choices[0].delta.content);
    }
  }
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "stream": true,
        "messages": [
          {
            "role": "user",
            "content": "Hello!"
          }
        ]
      }'
  ```
</CodeGroup>

## SSE format

Each streamed chunk is a `data:` line containing a JSON object:

```
data: {"id":"chatcmpl-...","object":"chat.completion.chunk","choices":[{"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":5}}

data: [DONE]
```

The final chunk before `[DONE]` contains usage information.

## Notes

* Streaming works for all supported models
* Usage stats are available in the last chunk (when `finish_reason` is set)
* The `completion_tokens` and `prompt_tokens` counts are the same as non-streaming
