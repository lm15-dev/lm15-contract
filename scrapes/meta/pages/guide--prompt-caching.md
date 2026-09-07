---
meta:
  title: Prompt caching
  description: Prompt caching is automatic — repeated prompt prefixes are served from cache to cut latency and input-token cost, with no key or setup required.
  keywords: prompt caching, KV cache, prefix caching, prompt_cache_key, cached_tokens, latency
cms:
  alias: /model-api/docs/prompt-caching
  target: aidmc
---

# Prompt caching

Reuse the same system prompt, examples, and history without reprocessing them on every turn. Meta Model API caches the stable prefix automatically — no flag or key to manage — so repeated prefixes cut time-to-first-token and input cost.

## How it works {#how-it-works}

Model API uses **prefix caching**. For each request it compares the start of your tokenized prompt to recently cached key-value (KV) state. Where the leading tokens match, that prefix is served from cache and only the tokens after the first difference are computed from scratch.

It runs on every request with no action from you. You do not pass a cache key, set a flag, or mark breakpoints. Send your normal request and you get the benefit when a recent request shared the same prefix. Your main control is order: put stable content first, such as system prompt, instructions, and examples, and put variable content last, such as the user message. That keeps the reusable prefix as long as possible.

## See what was cached {#cached-tokens}

Every response tells you how much of the input came from cache. Check the endpoint-specific `usage` object:

```json
{
  "usage": {
    "input_tokens": 1847,
    "output_tokens": 98,
    "total_tokens": 1945,
    "input_tokens_details": {
      "cached_tokens": 1792
    },
    "output_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```

```json
{
  "usage": {
    "prompt_tokens": 1847,
    "completion_tokens": 98,
    "total_tokens": 1945,
    "prompt_tokens_details": {
      "cached_tokens": 1792
    }
  }
}
```

Chat Completions reports it at `usage.prompt_tokens_details.cached_tokens`; Responses reports it at `usage.input_tokens_details.cached_tokens`. In both cases `cached_tokens` counts input tokens served from cache. A value above zero means the server reused a cached prefix and skipped that prefill. Zero is expected on the first request with a new prefix or after eviction.

> [!NOTE] cached_tokens billing
> `cached_tokens` is a **subset** of your input tokens, not an extra charge. The cached prefix is still counted once in `input_tokens` (Responses) / `prompt_tokens` (Chat Completions); `cached_tokens` reports how much of that total came from cache instead of recomputation. Cached input tokens are billed at a **reduced rate** compared to uncached input, so a higher hit rate lowers your input cost. See [Pricing and rate limits](/docs/pricing-rate-limits#pricing) for current per-token rates.

## Structure your prompt for cache hits {#structure}

The cache matches from the start of the prompt forward, so order determines how much can be reused:

- **System prompts**: a long, stable system prompt is ideal for caching. If every request starts with the same 2,000-token system prompt, those tokens are served from cache after the first request.
- **Few-shot examples**: examples that stay constant across requests are cached as part of the prefix.
- **Conversation history**: in a multi-turn conversation the accumulated history forms a growing prefix. Each new turn only needs to compute KV state for the new user message and the latest response.

Tokens that differ from the cached prefix end the match, and everything after the first difference is computed fresh. Putting volatile content like a timestamp or the current user message early shortens the reusable prefix.

> [!NOTE] Caching is independent of store
> Prompt caching is independent of the Responses API `store` parameter. Setting `store: false` turns off response retrieval (`GET /v1/responses/{id}` returns `404`) but does not disable caching. Cached prefixes are still reused, and `cached_tokens` still reports hits.

## Group similar requests with a cache key {#prompt-cache-key}

You get caching with no key at all. At high volume across many backends, you can optionally send `prompt_cache_key` to increase hit rate. Requests that share a key route together, so a request is more likely to land on a backend that already holds its prefix. Pick a stable string that identifies the shared prefix, such as an application name or use case, not a per-user or per-request value.

`prompt_cache_key` is accepted on both Responses and Chat Completions, and replaces the deprecated `user` field.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.chat.completions.create(
    model="muse-spark-1.3",
    prompt_cache_key="my-app-system-prompt",
    messages=[
        {
            "role": "system",
            "content": "You are a senior technical support engineer for Acme Corp. You have deep knowledge of all Acme products, APIs, and billing systems. Always provide step-by-step instructions. Be concise and professional.",
        },
        {
            "role": "user",
            "content": "How do I rotate my API keys without downtime?",
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.chat.completions.create({
  model: 'muse-spark-1.3',
  prompt_cache_key: 'my-app-system-prompt',
  messages: [
    {
      role: 'system',
      content: 'You are a senior technical support engineer for Acme Corp. You have deep knowledge of all Acme products, APIs, and billing systems. Always provide step-by-step instructions. Be concise and professional.',
    },
    {
      role: 'user',
      content: 'How do I rotate my API keys without downtime?',
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "prompt_cache_key": "my-app-system-prompt",
        "messages": [
            {
                "role": "system",
                "content": "You are a senior technical support engineer for Acme Corp. You have deep knowledge of all Acme products, APIs, and billing systems. Always provide step-by-step instructions. Be concise and professional.",
            },
            {
                "role": "user",
                "content": "How do I rotate my API keys without downtime?",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "prompt_cache_key": "my-app-system-prompt",
  "messages": [
    {
      "role": "system",
      "content": "You are a senior technical support engineer for Acme Corp. You have deep knowledge of all Acme products, APIs, and billing systems. Always provide step-by-step instructions. Be concise and professional."
    },
    {
      "role": "user",
      "content": "How do I rotate my API keys without downtime?"
    }
  ]
}'
```


- **Use one stable key per shared prefix**: a good key names your app or use case, such as `"customer-support-agent"` or `"code-review-v2"`.
- **Don't over-partition**: unique keys per user or per session lower hit rates because each key routes independently. Share a key across requests that truly share a prefix.

## Extend retention on Responses {#cache-retention}

By default a cached prefix lives in memory and is evicted under pressure or after inactivity. On the Responses API, `prompt_cache_retention` optionally requests longer retention:

| Value | Behavior |
|-------|----------|
| `"in_memory"` | Keep the cache in memory (the default behavior). Fastest access; evicted under memory pressure. |
| `"24h"` | Request extended retention, keeping the cached prefix active for longer, up to 24 hours. |

```json
{
  "model": "muse-spark-1.1",
  "prompt_cache_retention": "24h",
  "input": "Summarize the incident report from this quarter."
}
```

> [!NOTE] Retention is a hint
> `prompt_cache_retention` is a hint, not a guarantee. Actual retention is managed server-side based on available resources, and the server may evict entries early under load.

## Check cache performance {#checking-cache-performance}

Read the cached-token usage field on each response to confirm caching is helping:

- **`cached_tokens` is most of `input_tokens`**: cache is working well. Only the new tokens, such as the latest user message, needed computation.
- **`cached_tokens` is zero**: no cache hit. Expected on the first request with a new prefix, or after eviction.
- **`cached_tokens` is lower than expected**: the prefix likely changed partway through, such as an edited system prompt, ending the match early.

> [!NOTE] Counts reflect the request sent
> These counts reflect the tokens in the request you actually send. On the Responses API with `previous_response_id`, the server reconstructs prior turns from stored history, so a follow-up reports only the new turn's `input_tokens` and `cached_tokens`, not the full reconstructed prefix. To see accounting across the entire prefix, manage the `input` array yourself instead of chaining with `previous_response_id`.

## Best practices {#best-practices}

- **Put stable content first**: this is the main lever. The cache matches from the beginning, so system prompts, instructions, and few-shot examples should come before dynamic content. Volatile content early shortens the reusable prefix.
- **Monitor `cached_tokens`**: track the ratio of `cached_tokens` to input tokens over time to confirm your prompt structure caches well.
- **Add a `prompt_cache_key` at scale**: optional, but it raises hit rates for high-volume workloads by keeping requests that share a prefix on the same backend.
- **Set `"24h"` retention for bursty workloads**: on Responses, if traffic arrives in bursts with idle gaps, extended retention avoids rebuilding the cache between bursts.

## Next steps

Now that prefixes are caching, put that saved budget to work:

- Use the [Responses API](/docs/protocols/responses) to carry context across turns, with stateless reasoning replay or `previous_response_id`.
- Add [tool calling](/docs/tool-calling) to a cached system prompt so tool definitions are computed once and reused across turns.
- Combine with [structured output](/docs/structured-output) for low-latency extraction pipelines that reuse the same schema instructions.