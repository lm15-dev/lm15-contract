---
meta:
  title: Responses API
  description: Run agentic and multi-turn workloads on the Responses API with cross-turn reasoning replay, tool loops, search grounding, and file inputs.
  keywords: Responses API, agentic, reasoning replay, multi-turn, tool calling, previous_response_id
cms:
  alias: /model-api/docs/protocols/responses
  target: aidmc
---

# Responses API

Build multi-step agents that keep reasoning intact across turns. The Responses API is the only endpoint that carries the model's chain of thought between calls, which keeps tool loops accurate and performant. It also powers [search grounding](/docs/search-grounding), [file inputs](/docs/file-handling), and background execution.

Choose how context travels. Use [stateless encrypted reasoning replay](#reasoning-items) when you want full control and no server state. Use `previous_response_id` when you want the server to manage history. For single-shot or straightforward turns that plug into existing OpenAI code without reasoning continuity, [Chat Completions](/docs/protocols/chat-completions) is simpler.

The Responses API serves [Muse Spark](/docs/models#muse-spark) (text) and [Muse Image](/docs/models#muse-image) for image generation. For which models run on which endpoint, see [model availability](/docs/models#model-availability).

## How it works {#how-it-works}

With [chat completion](/docs/protocols/chat-completions), you manage history client-side: you resend the full `messages` array each turn and the payload grows as the conversation grows.

The Responses API takes an `input` as a string or an array of typed items and offers two context modes:

- **Stateless encrypted replay** (recommended): resend the conversation each turn. Reasoning travels as encrypted [reasoning items](#reasoning-items). Nothing is stored server-side.
- **Server-managed history**: the server stores each response and you continue from `previous_response_id`. Send only new input each turn.

Both modes preserve chain of thought across turns. A plain `messages` array cannot.

When you build the `input` array yourself, it carries typed items instead of plain `{role, content}` messages:

- **Messages** with a `role` (`developer`, `system`, `user`, or `assistant`) and typed content blocks such as `input_text`, `input_image`, `input_file`, `input_video`, and `output_text` for replayed assistant turns. See [Input content types](#input-content-types).
- **`reasoning`** items that replay the model's chain of thought across turns. See [Reasoning items in multi-turn input](#reasoning-items).
- **`function_call` and `function_call_output`** items that drive [tool calling](/docs/tool-calling).

Use the Responses API when you want reasoning continuity across turns for tool loops, cleaner multi-turn code, server-managed context, or Model API features that run through this endpoint like [search grounding](/docs/search-grounding) and [file references](/docs/file-handling).

## Basic usage {#basic-usage}

Call `POST /v1/responses` with a `model` and `input`.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="What is the capital of France?",
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
  input: 'What is the capital of France?',
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
        "input": "What is the capital of France?",
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
  "input": "What is the capital of France?"
}'
```


#### Example response

```json
{
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1714502400,
  "status": "completed",
  "model": "muse-spark-1.1",
  "store": true,
  "temperature": 1.0,
  "top_p": 1.0,
  "max_output_tokens": null,
  "tools": [],
  "tool_choice": "auto",
  "parallel_tool_calls": true,
  "service_tier": "auto",
  "output": [
    {
      "id": "msg_abc123:456",
      "type": "message",
      "role": "assistant",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "text": "The capital of France is **Paris**.",
          "annotations": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 69,
    "output_tokens": 163,
    "total_tokens": 232
  }
}
```

The response returns an `id`. Pass that `id` as `previous_response_id` to continue the conversation.

## Multi-turn conversations {#multi-turn}

Chain turns with `previous_response_id`. The server appends your new input to stored history, so you send only what changed.

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

# First turn
response = client.responses.create(
    model="muse-spark-1.1",
    input="What is the capital of France?",
)
print(response.output_text)

# Second turn -- continues the conversation
response = client.responses.create(
    model="muse-spark-1.1",
    input="What is the population of that city?",
    previous_response_id=response.id,
)
print(response.output_text)

# Third turn -- the server still has the full context
response = client.responses.create(
    model="muse-spark-1.1",
    input="How does that compare to London?",
    previous_response_id=response.id,
)
print(response.output_text)
```

Each call sends only the new user input. The server reconstructs the full conversation from the chain of response IDs.

> [!NOTE] previous_response_id scope
> `previous_response_id` carries conversation turns only (user and assistant messages), not request-level parameters. Top-level `instructions` does not persist across turns, so resend `instructions` on every request where you want it applied. The same applies to other per-request settings such as `tools` and `reasoning.effort`.

### Setting instructions {#instructions}

Use `instructions` to set tone, persona, and output rules for the current request. It is developer-level: the server inserts it at the top of the model's context, it takes priority over `input`, and it is equivalent to sending a `developer`-role message. Use whichever fits your code, you do not need both. `instructions` applies to the current request only and is not carried across `previous_response_id`, so resend it on each turn where you want it applied.

### Input content types {#input-content-types}

When you manage history yourself by building the `input` array instead of chaining with `previous_response_id`, the array is flexible. It accepts multiple `system` messages, a `developer`-role message (recommended for behavior instructions; `system`-role content is applied at the same level), and multiple content blocks within a single message. User blocks include `input_text`, `input_image`, `input_file`, and `input_video` (see [video understanding](/docs/video-understanding)). Replay prior assistant turns with `output_text` so the model sees its earlier responses accurately. Assistant messages also accept an optional `phase` field, see [Message phase](#message-phase).

The example below builds a short multi-turn conversation as an `input` array:

```json
{
  "model": "muse-spark-1.1",
  "input": [
    {"role": "developer", "content": [{"type": "input_text", "text": "You are a helpful geography assistant."}]},
    {"role": "user", "content": [{"type": "input_text", "text": "What is the capital of France?"}]},
    {"role": "assistant", "content": [{"type": "output_text", "text": "The capital of France is Paris."}]},
    {"role": "user", "content": [{"type": "input_text", "text": "What is its population?"}]}
  ]
}
```

> [!NOTE] Replaying web_search_call items
> You can also replay `web_search_call` output items from prior turns in the `input` array. Their `id` field is optional: if you omit it or set it to `null`, the server auto-assigns a unique ID before validation, so you do not need to store server-assigned `web_search_call` IDs. See [search grounding constraints](/docs/search-grounding#constraints).

### Reasoning items in multi-turn input {#reasoning-items}

Muse Spark reasons internally, see [reasoning](/docs/reasoning) for controls. To preserve that reasoning across turns, return `reasoning` items from a response's `output` as part of the next `input`. You can mix reasoning items with other types such as messages and `function_call_output` when you construct multi-turn input.

> [!NOTE] Reasoning items vs reasoning_content
> In the Responses API, chain of thought is surfaced as `reasoning` items in the `output` array and replayed as `reasoning` input items as shown below. Responses output messages do not carry a `reasoning_content` field. That field belongs to [Chat Completions](/docs/protocols/chat-completions), which does not preserve reasoning across turns. To keep chain of thought, use the Responses `reasoning` items shown here.

> [!IMPORTANT] Reasoning item ordering
> Every `reasoning` item in the `input` array must be followed by an assistant message or a `function_call` before the next `user`, `system`, or `developer` message. A `reasoning` item placed directly before a `user`, `system`, or `developer` message returns `HTTP 400` (`invalid_request_error`, `param: "input"`), see [Conversation structure](#conversation-structure). If the model produces a reasoning-only turn (`reasoning` with no text output), insert a minimal assistant message between the `reasoning` item and your next `user` message.

Reasoning replay is encrypted-only: `encrypted_content` is omitted by default. To receive it, set `include: ["reasoning.encrypted_content"]` on the request. This works whether or not the response is stored. You can request encrypted content with `store: true` or `store: false`. For stateless replay, pair it with `store: false` so the server keeps no copy of the conversation:

```json
{
  "model": "muse-spark-1.1",
  "input": "...",
  "store": false,
  "include": ["reasoning.encrypted_content"]
}
```

> [!IMPORTANT] Encrypted replay vs previous_response_id
> `include: ["reasoning.encrypted_content"]` cannot be combined with `previous_response_id` in the same request. Doing so returns `HTTP 400` (`param: "include"`). Choose one source of prior reasoning context: server-managed history via `previous_response_id`, or stateless replay via encrypted content.

Then pass the reasoning item back on the next turn with its `encrypted_content`. Every reasoning input item must include a `summary` field (send `summary: []` when you have no summary). The `id` field (an `rs_`-prefixed ID returned in the prior response) is optional on input. Include it when available, but clients doing stateless replay can omit it since `encrypted_content` carries the full state:

```json
{
  "type": "reasoning",
  "id": "rs_abc123",
  "summary": [],
  "encrypted_content": "..."
}
```

> [!NOTE] id is optional on replay
> The `id` field is required on reasoning items in the response _output_ (the server always generates it), but optional when you replay a reasoning item as _input_. Omitting `id` on input is valid when the `encrypted_content` is present.

Replay reasoning items in multi-step or agentic workflows. Without replay, the model loses chain-of-thought context across turns. For multi-turn and agentic use, stateless encrypted replay (`store: false` with `include: ["reasoning.encrypted_content"]`) is the recommended path. It keeps no state on the server and works across OpenAI-compatible tooling.

### Compacting conversations with reasoning {#compacting}

Long agent loops can approach the context window. Model API does not trim for you: `truncation: "auto"` is rejected (`HTTP 400`, only the default `"disabled"` is accepted) and an over-context request fails with `HTTP 400`. You compact history yourself, and encrypted reasoning items shape how you do it.

Encrypted reasoning items are opaque: you cannot summarize or rewrite one, only keep it whole or drop it. Compact at the level of whole turns.

- **Keep recent reasoning, drop old**: retain reasoning items for turns still in play (the current tool loop) and drop reasoning from older, settled turns. The server does not require a reasoning item to travel with its message or tool call, so dropping one is allowed. You lose that turn's chain of thought.
- **Replay what you keep, intact**: every retained item must carry its `encrypted_content`. Replaying a bare `rs_` id without it returns `HTTP 400` ("Referenced reasoning item ... was not found or has expired"). Ids must be unique and you must preserve `function_call` / `function_call_output` pairing and valid [conversation structure](#conversation-structure).
- **Measure before you send**: call [`POST /v1/responses/input_tokens`](/docs/api-reference/responses) with your trimmed input to confirm it fits before generating.

If you prefer not to manage this, use `store: true` with `previous_response_id` and let the server reconstruct history (see [Multi-turn conversations](#multi-turn)). The trade-off is server-side state instead of stateless replay.

### Message phase {#message-phase}

Assistant messages carry an optional `phase` field that labels what the content is:

- **`phase: "commentary"`**: intermediate assistant content, such as a preamble the model emits before calling a tool.
- **`phase: "final_answer"`**: the model's final answer content. This value is accepted on input only. The model does not stamp it on responses.

When the model emits intermediate commentary before a tool call, it tags those messages with `phase: "commentary"`. Final-answer messages return with no `phase` field. The model does not emit `phase: "final_answer"`, so do not expect it in responses. When the model returns a `phase` on an assistant message, preserve and resend it as you replay turns by building the `input` array yourself. Dropping it can degrade quality. If a message has no `phase`, there is nothing to preserve. Treat it as a final answer. `phase` is not used on `user` messages.

`phase` also matters for [conversation structure](#conversation-structure). Intermediate assistant text that precedes a `function_call` must be tagged `phase: "commentary"`. Replaying that text as an ordinary final answer immediately before a `function_call` returns `HTTP 400`. The server does not silently reinterpret a final answer as commentary.

```json
{
  "type": "message",
  "role": "assistant",
  "phase": "commentary",
  "content": [{"type": "output_text", "text": "Let me check the weather first."}]
}
```

### Conversation structure {#conversation-structure}

When you build `input` arrays manually, the server validates structure and rejects sequences it cannot interpret safely with `HTTP 400` instead of guessing. Keep these rules in mind:

- **Pair `function_call` with `function_call_output`**: when a request contains `function_call` items and no `previous_response_id`, every `function_call_output.call_id` must match a `function_call.call_id` in the same request. A mismatch returns `HTTP 400` (`param: "call_id"`). Every `call_id` must also be 1–64 characters, an empty or overlength value returns `HTTP 400` (`param: "call_id"`).
- **Order reasoning replay correctly**: a replayed `reasoning` item must be followed by an assistant message or a `function_call` before any new `user`, `system`, or `developer` message, otherwise the request returns `HTTP 400` (`param: "input"`).
- **Tag intermediate assistant text as commentary**: see [Message phase](#message-phase).

When you pass `previous_response_id`, the server reconstructs ordering from stored history, so these checks are relaxed and you send only new input. See [error handling](/docs/error-handling#invalid-conversation-structure) for error shapes.

## Retrieving a response {#retrieve}

Responses are stored when `store: true` (the default). Fetch a stored response by its `id`:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.retrieve("resp_abc123")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/responses/resp_abc123",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/responses/resp_abc123" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```


A retrieved response carries the same self-describing fields as the original POST. It echoes request-derived parameters (`store`, `tools`, `tool_choice`, `text`, `temperature`, `top_p`, `max_output_tokens`, `service_tier`, `background`, `instructions`, `previous_response_id`, `truncation`, `metadata`, and `parallel_tool_calls`), plus `incomplete_details`, `completed_at`, `created_at`, and the full `usage` breakdown (`output_tokens_details.reasoning_tokens` and `input_tokens_details.cached_tokens`). Storing a response and reading it back later to inspect a background response or audit an earlier turn returns those fields intact instead of null or zeroed. `completed_at` is the exception: it is set only once the response reaches `status: "completed"` and is `null` for responses that haven't completed (such as `in_progress`, `failed`, or `cancelled`).

`output_tokens_details.reasoning_tokens` counts chain-of-thought tokens. User-visible commentary such as a preamble before a tool call (see [Message phase](#message-phase)) counts toward `output_tokens` but is not included in `reasoning_tokens`.

### Streaming retrieval for background responses {#streaming-retrieval}

For background responses, retrieve with `stream=true` to receive an SSE stream instead of a JSON body:

```bash title="curl"
curl "https://api.meta.ai/v1/responses/resp_abc123?stream=true" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

The stream delivers lifecycle events as the background response progresses:

1. `response.created`: emitted immediately with the response identity.
2. A terminal event (`response.completed`, `response.failed`, or `response.incomplete`): emitted once the response reaches a terminal state, carrying the full final response.
3. `[DONE]`: signals the end of the stream.

If the response is still in progress, the stream live-tails until it reaches a terminal state. Use `starting_after` to resume from a sequence number. Events with `sequence_number` at or below it are skipped.

> [!NOTE] Retrieval streams lifecycle only
> Streaming retrieval delivers lifecycle and terminal events only. It does not replay incremental token deltas. For token-by-token streaming, set `stream: true` on the initial `POST` request.

## Streaming {#streaming}

Set `stream=True` to receive tokens as they are generated.

> Streaming is also the way to run long generations. Non-streaming requests are subject to a server-side time limit and return [`HTTP 504` (`gateway_timeout`)](/docs/error-handling#504) if they run too long; streaming requests are exempt because they return output incrementally. For long or large workloads, stream the response or run it in the [background](#using-with-other-features).

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

with client.responses.stream(
    model="muse-spark-1.3",
    input="Explain how neural networks learn.",
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
print()
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

const stream = client.responses.stream({
  model: 'muse-spark-1.3',
  input: 'Explain how neural networks learn.',
});

for await (const event of stream) {
  if (event.type === 'response.output_text.delta') {
    process.stdout.write(event.delta);
  }
}
process.stdout.write('\n');
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
        "Accept": "text/event-stream",
    },
    json={
        "model": "muse-spark-1.3",
        "input": "Explain how neural networks learn.",
        "stream": True,
    },
    stream=True,
)
response.raise_for_status()

for raw_line in response.iter_lines(decode_unicode=False):
    if not raw_line:
        continue
    line = raw_line.decode("utf-8", errors="replace")
    if not line.startswith("data: "):
        continue
    data = line.removeprefix("data: ")
    if data == "[DONE]":
        break
    event = json.loads(data)
    if event.get("type") == "response.output_text.delta":
        delta = event.get("delta")
        if delta:
            print(delta, end="", flush=True)
print()
```
```shell title="curl"
curl -N -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "Explain how neural networks learn.",
  "stream": true
}'
```


You can stream with `previous_response_id` for multi-turn. The streamed response still returns an `id` you can chain into subsequent turns.

The stream delivers typed server-sent events. Common types include `response.created`, `response.in_progress`, `response.output_item.added` / `response.output_item.done`, `response.content_part.added` / `response.content_part.done`, `response.output_text.delta`, and `response.completed`. When the model invokes tools, arguments stream as `response.function_call_arguments.delta` events and finalize with `response.function_call_arguments.done`. The model's raw reasoning is not streamed as text: Muse Spark emits no `response.reasoning_text.*` events and the `reasoning` output item carries no visible content. If you request a [reasoning summary](/docs/reasoning#summaries) (`reasoning.summary`), the summary streams as `response.reasoning_summary_text.delta` / `.done` events. The raw chain of thought is available only in encrypted form for [replay across turns](#reasoning-items), via `include: ["reasoning.encrypted_content"]`. If the response fails during streaming, the terminal event is `response.failed` instead of `response.completed`. It carries the response object with `status: "failed"` and a non-null `error` object with a `code` such as `server_error` and a sanitized `message`. See [Error handling → Streaming errors](/docs/error-handling#streaming-errors).

Output items carry a `status` that transitions during the stream: `"in_progress"` on `output_item.added`, then `"completed"` on `output_item.done`. This applies to both `message` and `function_call` items. Third-party SDKs such as the Vercel AI SDK rely on `status: "completed"` as a terminal signal. Do not discard items before they reach this state.

### Persistence guarantees

When `store=true` (the default), streaming responses are persisted even if the client disconnects mid-stream. The server continues processing after disconnect and stores the final result. You can safely use `previous_response_id` to reference a streamed response even after a network interruption. The response remains available for subsequent turns.

The server persists the response **before** it emits the terminal `response.completed` event, so once you have observed completion you can immediately retrieve the response or chain it with `previous_response_id`. In rare cases — server under heavy load, a rolling deploy, or a slow storage write — persistence can briefly lag the terminal event; an immediate `GET /v1/responses/{id}` may then return `HTTP 404` (or a chained `previous_response_id` may return `HTTP 400`) for a few seconds. If you fetch or chain a just-completed response and hit that, retry once or twice with a short backoff.

## Canceling a response {#canceling}

Cancel an in-progress background response by posting to the cancel endpoint with its `id`.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.cancel("resp_abc123")

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

const response = await client.responses.cancel('resp_abc123');

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses/resp_abc123/cancel",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses/resp_abc123/cancel" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```


```json
{
  "id": "resp_abc123",
  "object": "response",
  "status": "cancelled",
  "model": "muse-spark-1.1",
  "output": []
}
```

The cancel endpoint handles races gracefully. If the response completes at the same moment a cancel arrives, the server returns the completed response instead of an error. The same applies when the response has already failed or been cancelled. You always get the current state back. If the response has been deleted, the cancel endpoint returns `HTTP 404` (not-found).

> [!NOTE] Cancelling a completed response
> If the response had already completed, the cancel response comes back with `status: "completed"` but an empty `output[]`. Fetch the response with `GET /v1/responses/{id}` to read its output.

## Deleting a response {#deleting}

Delete a response by its ID with `DELETE /v1/responses/{response_id}`. The response is soft-deleted and can no longer be retrieved or referenced by `previous_response_id`.

A repeat DELETE on an already-deleted response returns `HTTP 404`. This is not idempotent. Once deleted, subsequent DELETE calls will not return `200`.

## Using with other features {#using-with-other-features}

Several Model API features work through the Responses API:

- **Search grounding**: Add `tools=[{"type": "web_search"}]` to ground responses with real-time web results and inline citations. See [Search grounding](/docs/search-grounding).
- **File references**: Upload files via the [Files API](/docs/file-handling) and reference them by ID in your `input` using `input_file` content blocks. See [Files](/docs/file-handling).
- **Image understanding**: Send images as base64 data URLs or uploaded file references for visual analysis. See [Image understanding](/docs/image-understanding).
- **Log probabilities**: Not supported. Muse Spark is a reasoning model, so requesting them via `include: ["message.output_text.logprobs"]` returns `HTTP 400`. The Responses API does not accept a top-level `logprobs` parameter.
- **Reasoning effort**: Control how much reasoning the model performs by setting `reasoning.effort`. Accepted values: `"none"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`. When omitted, the model reasons by default. Set `reasoning.effort` to control how much. `"none"` (disable reasoning) is not supported by Muse Spark and returns `HTTP 400`. The Chat Completions equivalent is the top-level `reasoning_effort` parameter.
- **Prompt cache retention**: Set `prompt_cache_retention` to `"in_memory"` or `"24h"` as a hint for the server's prompt cache. Actual retention is managed server-side.
- **Safety identifiers**: Set `safety_identifier` to a stable, privacy-preserving identifier for the end user behind a request, so enforcement can be targeted at that user rather than your whole application. See [Safety identifiers](#safety-identifiers).
- **Sampling**: `temperature` and `top_p` are accepted (mirroring [Chat Completions](/docs/protocols/chat-completions#parameters)), but Muse Spark is tuned to run at the defaults (`temperature=1.0`, `top_p=1.0`) and performs best there. Leave both unset for most workloads. Adjust `temperature` or `top_p`, not both. To make output more focused or repeatable, prefer clearer instructions over lowering `temperature`.
- **Sampling penalties**: Set `frequency_penalty` or `presence_penalty` (number, -2 to 2, default `0`) to reduce verbatim repetition or nudge the model toward new topics. Both mirror their [Chat Completions](/docs/protocols/chat-completions#parameters) behavior.
- **Include fields**: Use `include` to request optional output fields such as logprob details. Accepted values mirror OpenAI's. Sending an unknown value returns `HTTP 400`.
- **Streaming usage**: With `stream: true`, the final streamed response always includes usage. `stream_options.include_usage` is a Chat Completions option and has no effect on the Responses API. You do not need to set it.
- **Background responses**: Set `background: true` to run a response asynchronously, then poll, [stream-retrieve](#streaming-retrieval), or [cancel](#canceling) it by `id`. The immediate acknowledgement includes `"background": true` and `"status": "queued"` so you can confirm acceptance before polling. The creation request cannot combine `background: true` with `stream: true` (returns `HTTP 400`), but you can retrieve a background response as an SSE stream with `GET /v1/responses/{id}?stream=true`. Starting background responses is additionally rate-limited per team, see [Rate limits](/docs/pricing-rate-limits#background-rate-limit). A background creation body is also capped at **1 MiB** (1,048,576 bytes). A larger body returns `HTTP 413` (`payload_too_large`). This is much smaller than the 50 MB inline-media limit, so if you inline large base64 content, reference it by `file_id` from the [Files API](/docs/file-handling) instead once you switch a request to background. See [Error handling → 413](/docs/error-handling#413).
- **Output-token limit**: `max_output_tokens` bounds tokens generated (reasoning plus visible output) and has a minimum of 16. It shares the model's context window with input: `input_tokens + max_output_tokens` must fit within the context window. Requesting more than the model's configured maximum returns `HTTP 400`. Do not set it to the full context window when the request has any input because the two share one budget.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="Who won the most recent Formula 1 race?",
    tools=[
        {
            "type": "web_search",
        },
    ],
)

print(response.model_dump_json(indent=2))
```

## Safety identifiers {#safety-identifiers}

A safety identifier attributes a request to the end user behind it, so harmful behavior can be traced to an individual rather than your whole application. Adding a safety identifier is optional but highly recommended if your application handles requests from end users you can identify.

Set `safety_identifier` to a stable value that uniquely identifies the user in your system, up to 64 characters. Use a privacy-preserving value, such as a hash of an internal user ID, so you do not send usernames, emails, or other identifying information.

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.1",
    input="Hello!",
    safety_identifier="a1b2c3d4",  # e.g. a hash of your internal user ID
)
```

`safety_identifier` supersedes the deprecated `user` field. If you send both, `safety_identifier` takes precedence. Use `prompt_cache_key` to group requests for cache efficiency, which the `user` field previously handled. This applies equally to [Chat Completions](/docs/protocols/chat-completions); on the [Messages API](/docs/protocols/messages) the Anthropic-native equivalent is `metadata.user_id`.

## OpenAI compatibility notes {#openai-compatibility}

The Responses API uses `text.format` for structured output, not `response_format`. Compatibility parsing may accept OpenAI-only top-level fields such as `response_format`, but they do not configure structured output on Responses. See [structured output](/docs/structured-output).

Some OpenAI parameters (`stop`, `verbosity`, `logit_bias`, `prediction`, `n` > 1, audio modalities, and `web_search_options`) are not implemented on the Responses endpoint. Omit them. Where accepted for compatibility, they have no effect. See [Chat completion → OpenAI compatibility notes](/docs/protocols/chat-completions#openai-compatibility) for related Chat Completions behavior.

## Next steps

Now that you can carry reasoning across turns, layer on more building blocks. Control depth and summaries with [reasoning](/docs/reasoning), add cited real-time results with [search grounding](/docs/search-grounding), and wire multi-step tool loops with [tool calling](/docs/tool-calling). When you are ready, check the [Responses API reference](/docs/api-reference/responses) for the full schema.