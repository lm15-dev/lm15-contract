> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Prompt Caching

> Reduce latency and cost by caching repeated prompt prefixes.

Prompt caching allows DeepInfra to reuse the KV (key-value) cache from previous requests when the beginning of your prompt is identical. This reduces both latency and cost for workloads that repeatedly send the same prefix — such as a long system prompt, a large document, or a fixed set of few-shot examples.

## How it works

When you send a request, DeepInfra checks whether the beginning of your prompt matches a cached prefix from a recent request on the same model. If it does, the cached KV state is reused instead of recomputing it, which:

* **Reduces time-to-first-token** — the model skips processing the cached portion
* **Lowers cost** — cached input tokens are billed at a reduced rate

## Usage

Prompt caching is **automatic** — no extra parameters required. Just structure your prompts so that the reused content appears at the beginning.

```python theme={null}
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)

# Long system prompt that stays the same across requests
SYSTEM_PROMPT = """You are a helpful AI assistant with deep expertise in Python.
[... thousands of tokens of instructions or context ...]
"""

# First request — full processing
response1 = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash-0731",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "How do I use list comprehensions?"},
    ],
)

# Second request — cached prefix reused, faster and cheaper
response2 = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash-0731",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "What are Python generators?"},
    ],
)
```

## Best practices

**Put stable content first.** The cache matches from the beginning of the prompt. Place your system prompt, documents, and few-shot examples before the user's message.

**Keep the prefix identical.** Even a single character difference will invalidate the cache. Avoid dynamic content (timestamps, user IDs, etc.) in the cacheable prefix.

**Longer prefixes save more.** Prompt caching is most effective with long, repeated prefixes — think multi-page documents, long system prompts, or RAG context.

## Common use cases

| Use case                             | Cached prefix       |
| ------------------------------------ | ------------------- |
| Chatbot with a long system prompt    | System prompt       |
| RAG / document Q\&A                  | Retrieved documents |
| Few-shot classification              | Examples            |
| Code assistant with a large codebase | Codebase context    |
| Multi-turn conversation              | Previous turns      |

## Checking cache usage

The response usage object indicates how many tokens were served from cache:

```json theme={null}
{
  "usage": {
    "prompt_tokens": 5000,
    "completion_tokens": 50,
    "total_tokens": 5050,
    "prompt_tokens_details": {
      "cached_tokens": 4800
    }
  }
}
```

In this example, 4800 of the 5000 input tokens were cached.

## Explicit cache keys

By default, caching is automatic based on prefix matching. The `prompt_cache_key` parameter lets you explicitly tag a request with a cache key, improving cache hit rates when your prompts share the same logical content but differ slightly in formatting or ordering.

We recommend using a **session-scoped key** like `userid-chatsessionid` (e.g. `"user123-chat456"`). Within a single chat session, the conversation history grows incrementally — each new request reuses all previous turns plus one new message. A per-session cache key ensures these near-identical prompts always hit the cache.

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
      messages=[
          {"role": "system", "content": "You are a helpful coding assistant."},
          {"role": "user", "content": "How do I use async/await?"},
      ],
      extra_body={"prompt_cache_key": "user123-chat456"},
  )
  ```

  ```javascript JavaScript theme={null}
  import OpenAI from "openai";

  const openai = new OpenAI({
    apiKey: process.env.DEEPINFRA_API_KEY,
    baseURL: "https://api.deepinfra.com/v1/openai",
  });

  const response = await openai.chat.completions.create({
    model: "deepseek-ai/DeepSeek-V4-Flash-0731",
    messages: [
      { role: "system", content: "You are a helpful coding assistant." },
      { role: "user", content: "How do I use async/await?" },
    ],
    prompt_cache_key: "user123-chat456",
  });
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "prompt_cache_key": "user123-chat456",
        "messages": [
          {
            "role": "system",
            "content": "You are a helpful coding assistant."
          },
          {
            "role": "user",
            "content": "How do I use async/await?"
          }
        ]
      }'
  ```
</CodeGroup>

Requests with the same `prompt_cache_key` and model will share a KV cache, even if their prompt prefixes aren't byte-for-byte identical.

| Parameter          | Type     | Description                                                                              |
| ------------------ | -------- | ---------------------------------------------------------------------------------------- |
| `prompt_cache_key` | `string` | An explicit key for cache lookup. Requests with the same key and model share a KV cache. |

<Note>
  Need a prefix to stay cached for a guaranteed window? [Prompt cache retention](/chat/prompt-cache-retention) lets you retain a prompt for 5 minutes or 1 hour with `prompt_cache_options`, billed at a cache-write premium upfront and reused at the cache-read rate.
</Note>

## Notes

* Prompt caching is available on supported models — check the model page for details
* Cache entries expire after a period of inactivity
* Caches are per-model and per-account
* When using `prompt_cache_key`, the key is scoped per-model and per-account
