---
meta:
  title: Reasoning
  description: Control how much the model thinks before responding using the reasoning_effort parameter.
  keywords: reasoning, chain of thought, reasoning_effort, thinking, reasoning effort
cms:
  alias: /model-api/docs/reasoning
  target: aidmc
---

# Reasoning

Solve harder problems by giving the model more time to think. [Muse Spark](/docs/models#muse-spark) is a reasoning model: it generates internal reasoning tokens before visible output, and you control how much with `reasoning_effort`.

## How it works {#how-it-works}

When you send a request, the model works through the problem internally first. That reasoning stays private and does not appear in the response body. Reasoning tokens count toward your output-token budget (`max_tokens` on Chat Completions, `max_output_tokens` on the Responses API) and toward billed completion tokens.

Set `reasoning_effort` to choose depth:

| Value | Behavior |
|-------|----------|
| `"none"` | Disables reasoning. **Not supported by Muse Spark**: returns `HTTP 400`. |
| `"minimal"` | Shortest reasoning pass. |
| `"low"` | Light reasoning. |
| `"medium"` | Moderate depth. |
| `"high"` | Deep reasoning. |
| `"xhigh"` | Maximum reasoning depth. |

Higher effort means more reasoning — and more reasoning tokens, latency, and cost. `"none"` disables reasoning entirely, which Muse Spark does not support.

When you omit the parameter, the model still reasons at a model-determined level.

> [!NOTE] Where to set reasoning effort
> On [Chat Completions](/docs/protocols/chat-completions), use the top-level `reasoning_effort` parameter. On the [Responses API](/docs/protocols/responses), nest it as `reasoning.effort`.

## Usage {#usage}

### Chat Completions

Send `reasoning_effort` at the top level of a chat completion request:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.chat.completions.create(
    model="muse-spark-1.3",
    reasoning_effort="high",
    messages=[
        {
            "role": "user",
            "content": "Prove that the square root of 2 is irrational.",
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
  reasoning_effort: 'high',
  messages: [
    {
      role: 'user',
      content: 'Prove that the square root of 2 is irrational.',
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
        "reasoning_effort": "high",
        "messages": [
            {
                "role": "user",
                "content": "Prove that the square root of 2 is irrational.",
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
  "reasoning_effort": "high",
  "messages": [
    {
      "role": "user",
      "content": "Prove that the square root of 2 is irrational."
    }
  ]
}'
```


### Responses API

On the Responses API, nest the same control as `reasoning.effort`:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    reasoning={
        "effort": "high",
    },
    input="Prove that the square root of 2 is irrational.",
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

const response = await client.responses.create({
  model: 'muse-spark-1.3',
  reasoning: {
    effort: 'high',
  },
  input: 'Prove that the square root of 2 is irrational.',
});

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "reasoning": {
            "effort": "high",
        },
        "input": "Prove that the square root of 2 is irrational.",
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "reasoning": {
    "effort": "high"
  },
  "input": "Prove that the square root of 2 is irrational."
}'
```


### Log probabilities {#logprobs}

Muse Spark is a reasoning model, so `logprobs` is not supported. `logprobs: true` (Chat Completions) and `include: ["message.output_text.logprobs"]` (Responses API) both return `HTTP 400`.

## Multi-turn reasoning {#multi-turn}

You can carry reasoning context across turns so follow-ups build on earlier thinking. How you preserve it depends on the endpoint.

### Responses API

Chain turns with `previous_response_id`. The server keeps reasoning context for you:

```json
{
  "model": "muse-spark-1.1",
  "reasoning": {"effort": "high"},
  "input": "Now extend the proof to show that the square root of 3 is also irrational.",
  "previous_response_id": "resp_abc123"
}
```

For stateless replay, where you manage history yourself instead of chaining response IDs, request the model's encrypted reasoning with `include: ["reasoning.encrypted_content"]` and replay it as a `reasoning` input item on the next turn. See [reasoning items in multi-turn input](/docs/protocols/responses#reasoning-items) for the full pattern.

### Chat Completions

Chat Completions cannot carry reasoning across turns for external API keys. Assistant messages expose a `reasoning_content` field, but it holds the model's **private** chain of thought and is **redacted to empty** before the response reaches an external caller, so there is nothing to replay and each turn reasons from scratch. It is populated only for internal callers holding the `internal:private_cot` attribute. Do not rely on `reasoning_content` for multi-turn continuity on this endpoint. For multi-step and agentic workloads where preserving chain of thought matters, use the Responses API above, which replays reasoning through encrypted content or `previous_response_id`.

## Reasoning summaries {#summaries}

The raw chain of thought stays private, but on the [Responses API](/docs/protocols/responses) you can request a natural-language **summary** of it. Set `reasoning.summary` to `"auto"`, `"concise"`, or `"detailed"`:

```json
{
  "model": "muse-spark-1.1",
  "reasoning": {"effort": "high", "summary": "auto"},
  "input": "Prove that the square root of 2 is irrational."
}
```

Each profile controls how much reasoning the summary captures:

| Profile | Behavior |
|---------|----------|
| `"auto"` | Compact summary, typically about one sentence. Best for most use cases. |
| `"concise"` | Brief multi-sentence summary focused on the key reasoning steps. |
| `"detailed"` | Longer summary that preserves more of the reasoning chain's structure. |

Summary length varies with reasoning complexity; these are targets, not guarantees.

When a summary is generated, it is returned in the `summary` array of the response's `reasoning` output item, and in [streaming](/docs/protocols/responses#streaming) mode it is delivered as `response.reasoning_summary_text.delta` / `response.reasoning_summary_text.done` events.

> [!NOTE] Summaries aren't guaranteed
> A summary is not guaranteed on every response. If the model does little or no private reasoning for a turn, or no summary is produced, the `summary` array is empty (`[]`). Treat the summary as optional output.

Request summaries with the `reasoning.summary` field; the older `generate_summary` alias is deprecated and does not request one. A summary is human-readable explanatory text, distinct from the opaque `encrypted_content` used for [multi-turn replay](#multi-turn). Reasoning summaries are a Responses API feature. Chat Completions does not expose `reasoning.summary`.

## Token usage {#token-usage}

Reasoning tokens count toward both your output-token limit and billed completion tokens:

- **Output-token limit**: `max_tokens` (Chat Completions) and `max_output_tokens` (Responses API) cap reasoning tokens plus visible output tokens combined. If the model spends most of the budget on reasoning, the visible response may be truncated. Set the limit high enough to accommodate both.
- **Billing**: Reasoning tokens are billed at the same rate as visible output tokens. The `usage` breakdown reports them separately as `completion_tokens_details.reasoning_tokens` (Chat Completions) or `output_tokens_details.reasoning_tokens` (Responses API).

Higher `reasoning_effort` produces more reasoning tokens, which means longer latency and higher cost. Use the lowest level that gives you acceptable results.

## When to reach for reasoning {#when-to-use}

Higher reasoning effort helps with multi-step problem solving: proofs and calculations, complex code generation, architecture trade-off analysis, and task planning and sequencing.

For direct-answer tasks, such as lookups, formatting, and translation, set `reasoning_effort` to `"low"` for faster responses at lower cost. (Muse Spark does not support `"none"`; see [How it works](#how-it-works).)

## Constraints {#constraints}

- **Log probabilities**: Not supported. Muse Spark is a reasoning model, so `logprobs: true` returns `HTTP 400`. See [Log probabilities](#logprobs).
- **Raw reasoning is not exposed as text**: The model's chain of thought is private. The raw reasoning is not returned as readable text in the response body and is not emitted as stream events; only the visible output and, if you request one, a [reasoning summary](#summaries), is streamed. On the Responses API, the raw reasoning is available solely as encrypted content for [replay](/docs/protocols/responses#reasoning-items) via `include: ["reasoning.encrypted_content"]`. During built-in tool loops (for example, when the model runs `web_search`), reasoning output items appear with empty `content` so output indices stay stable, and no visible reasoning text is exposed. When you set `include: ["reasoning.encrypted_content"]`, those items still carry `encrypted_content`, so stateless replay works across tool-loop turns.
- **Streaming**: Because the model reasons before producing visible output, expect an initial latency before the first visible content chunk in streaming mode.
- **Output-token limit**: Covers reasoning plus visible output. Set it high enough to accommodate both.

## Next steps

- Ship a reasoning conversation with [Responses API](/docs/protocols/responses), or keep it stateless with [chat completion](/docs/protocols/chat-completions).
- Constrain a reasoned answer to a schema with [structured output](/docs/structured-output).
- Build multi-step agents that replay reasoning across turns with [tool calling](/docs/tool-calling).