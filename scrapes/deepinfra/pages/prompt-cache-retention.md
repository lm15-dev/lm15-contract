> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Prompt Cache Retention

> Retain a prompt prefix for 5 minutes or 1 hour so reuse skips prefill and bills at the cache-read rate.

[Prompt caching](/chat/prompt-caching) reuses the KV cache from a recent request when the beginning of your prompt matches — automatically, and best-effort. **Prompt cache retention** goes further: it lets you explicitly keep a prompt prefix cached for a fixed window — **5 minutes** or **1 hour** — so reuse is guaranteed for that window instead of depending on whether the prefix happens to still be warm.

While a prefix is retained, every request that reuses it **skips prefill** for a faster time to first token and is billed at the discounted **cache-read** rate. Opening the window costs a small **cache-write** premium upfront.

## Quick start

Send `prompt_cache_key` with every request in a session. Add `prompt_cache_options` on the first one to open the window.

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ["DEEPINFRA_API_KEY"],
      base_url="https://api.deepinfra.com/v1/openai",
  )

  resp = client.chat.completions.create(
      model="nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B",
      messages=messages,  # your large, reused context
      extra_body={
          "prompt_cache_key": "agent-session-123",
          "prompt_cache_options": {"mode": "explicit", "ttl": "1h"},
      },
  )

  print(resp.usage.prompt_tokens_details)
  ```

  ```javascript JavaScript theme={null}
  import OpenAI from "openai";

  const openai = new OpenAI({
    apiKey: process.env.DEEPINFRA_API_KEY,
    baseURL: "https://api.deepinfra.com/v1/openai",
  });

  const resp = await openai.chat.completions.create({
    model: "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B",
    messages, // your large, reused context
    prompt_cache_key: "agent-session-123",
    prompt_cache_options: { mode: "explicit", ttl: "1h" },
  });
  ```

  ```bash cURL theme={null}
  curl "https://api.deepinfra.com/v1/openai/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
    -d '{
        "model": "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B",
        "messages": [{"role": "system", "content": "..."}],
        "prompt_cache_key": "agent-session-123",
        "prompt_cache_options": {"mode": "explicit", "ttl": "1h"}
      }'
  ```
</CodeGroup>

## Request parameters

| Parameter                      | Type             | Description                                                                                                                                                           |
| ------------------------------ | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt_cache_key`             | `string`         | A stable identifier for the context you're caching (for example a session or agent id). Required for retention; reuse is matched on this key plus the prompt content. |
| `prompt_cache_options.mode`    | `string`         | Currently `"explicit"`.                                                                                                                                               |
| `prompt_cache_options.ttl`     | `"5m"` \| `"1h"` | Retention window. Sending it opens the window, or extends an open one. Omit it on reuse requests.                                                                     |
| `prompt_cache_breakpoint.mode` | `string`         | Set to `"explicit"` on a message content part to end the retained prefix there. See [Cache breakpoints](#cache-breakpoints).                                          |

## Window lifecycle

| Request                              | Effect                                                                                                 |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| First request with a `ttl`           | Writes the cache and starts the clock. Still prefills; billed the write premium on the cached portion. |
| Same key, no `ttl`                   | Reuses the retained prefix at the cache-read rate. Does not move the deadline.                         |
| Same key, with a `ttl`               | Reuses the cache *and* pushes the deadline out. Billed the write premium again.                        |
| Shorter `ttl` inside a longer window | Never shortens the window.                                                                             |
| After expiry                         | Reuse falls back to standard input pricing — no silent charges.                                        |

Retention is scoped to your account **and** `prompt_cache_key`. It works with streaming and non-streaming, chat and text-completions.

<Warning>
  You're charged a cache write each time a request writes new blocks **or extends the window** — not just on the first request. For example, send the same prompt with a `ttl` twice and the second call extends the window, so it's charged as another cache write. Send a `ttl` only to open the window or when you deliberately want to extend it; for ordinary reuse, omit `ttl` and pay the cheaper cache-read rate.
</Warning>

## Cache breakpoints

Most prompts are a stable prefix (system instructions, tools, a document) followed by a variable tail. Mark where the reusable prefix ends with a `prompt_cache_breakpoint` on a message content part — retention then applies to everything up to and including that part, and ignores the variable remainder, so the retained cache stays stable across requests even as the question changes.

```json theme={null}
{
  "messages": [
    { "role": "system", "content": [
        { "type": "text",
          "text": "... large stable system prompt, tools, and reference context ...",
          "prompt_cache_breakpoint": { "mode": "explicit" } }
    ]},
    { "role": "user", "content": "... the variable question — not retained ..." }
  ],
  "prompt_cache_key": "agent-session-123",
  "prompt_cache_options": { "mode": "explicit", "ttl": "1h" }
}
```

<Note>
  Put anything that changes between calls (timestamps, user ids, retrieved chunks) **after** the breakpoint, so the prefix before it stays identical and matches in full. Changing a token inside the retained prefix only recomputes from the point of divergence onward — you still get the cache-read rate on the portion that still matches.
</Note>

## Cache granularity

Caches are written in fixed increments, so the retained portion is always **rounded down** to a whole multiple of the model's cache granularity. Whatever is left over is billed as standard input.

The granularity differs per model. On Nemotron-3-Ultra it is **8,192 tokens**: a 20,000-token prompt retains 16,384 tokens (two increments), and the remaining 3,616 are billed as standard input. A breakpoint shorter than one increment retains nothing.

<Note>
  Check the model page for the granularity of the model you're using — it determines how much of your prompt is actually cacheable.
</Note>

## Reading the response

Every response reports what happened in `usage.prompt_tokens_details`.

| Field                | Type      | Description                                                                                             |
| -------------------- | --------- | ------------------------------------------------------------------------------------------------------- |
| `cache_write_tokens` | `integer` | Tokens written to cache, billed at the retention write rate. The remainder is billed as standard input. |
| `cached_tokens`      | `integer` | Tokens reused from a retained prefix, billed at the cache-read rate.                                    |

<CodeGroup>
  ```json Write (first request) theme={null}
  "usage": {
    "prompt_tokens": 34375,
    "total_tokens": 34495,
    "completion_tokens": 120,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "cache_write_tokens": 32768
    }
  }
  ```

  ```json Reuse (later request) theme={null}
  "usage": {
    "prompt_tokens": 34380,
    "total_tokens": 34475,
    "completion_tokens": 95,
    "prompt_tokens_details": {
      "cached_tokens": 32768,
      "cache_write_tokens": 0
    }
  }
  ```
</CodeGroup>

## Pricing

Relative to the model's standard input price:

| Action                                     | Rate                                                               |
| ------------------------------------------ | ------------------------------------------------------------------ |
| Reuse a retained prefix (cache **read**)   | model's cache-read rate (e.g. **0.2×** input for Nemotron-3-Ultra) |
| Retain for **5 minutes** (cache **write**) | **1.25×** input                                                    |
| Retain for **1 hour** (cache **write**)    | **2.0×** input                                                     |
| Non-retained input                         | 1× (standard)                                                      |

Only whole cacheable blocks count as cache read/write; any remainder is billed as standard input. The write premium applies only when a request actually **creates or extends** the retention window — reuse inside a window you've already paid for is billed at the read rate.

## Model support

| Model                                      | Retention |
| ------------------------------------------ | --------- |
| `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B` | 5m, 1h    |
| `moonshotai/Kimi-K2.7-Code`                | 5m, 1h    |

More models to follow. On a model without retention support, `prompt_cache_options` is ignored and the request is billed as standard input.
