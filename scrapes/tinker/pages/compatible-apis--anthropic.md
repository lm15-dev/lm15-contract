# Anthropic API Compatible Inference (Beta)

Anthropic-compatible inference lets you use any model in Tinker, including base models and your own fine-tuned checkpoints, through an endpoint compatible with the [Anthropic Messages API](https://docs.anthropic.com/en/api/messages). Tools built for Claude, such as [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) and the Anthropic SDKs, work with Tinker when you change only the base URL and API key. It's designed for:

- **Trying Inkling**: Chat with [Inkling](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/index.md) from any Anthropic client, with no rendering code.
- **Claude Code on your own model**: Point `ANTHROPIC_BASE_URL` at Tinker to drive Inkling or a fine-tuned checkpoint through the `claude` CLI.
- **Fast feedback while training**: Sample from any sampler checkpoint as soon as it's saved, even while the training job continues.

You can also use Anthropic-compatible inference for production traffic. For higher or more stable throughput, or guidance on large-scale setups, [join our waitlist for production inference](https://form.typeform.com/to/CPTm26T7).

## Using Anthropic compatible inference from an Anthropic client

The interface exposes an Anthropic-compatible HTTP API. You can use any Anthropic SDK or HTTP client that lets you override the base URL.

1. Set the base URL of your Anthropic-compatible client to:

```text
https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api
```

The client appends `/v1/messages` (and `/v1/messages/count_tokens`) to this base, matching the standard Anthropic paths.

2. Set the model name. Use `thinkingmachines/Inkling` for Inkling, another base model name (for example `Qwen/Qwen3-8B`), or a Tinker sampler weight path for one of your own fine-tuned checkpoints:

```text
thinkingmachines/Inkling
```

```text
tinker://0034d8c9-0a88-52a9-b2b7-bce7cb1e6fef:train:0/sampler_weights/000080
```

Any valid Tinker sampler checkpoint path works here. You can keep training and sample from the same checkpoint simultaneously.

3. Authenticate with your Tinker API key, by passing the same key used for Tinker as the API key to the Anthropic client. The endpoint accepts the Anthropic SDK's native `x-api-key` header, so no header rewriting is needed. An `Authorization: Bearer <key>` header works too.

## Code Example

```py
from os import getenv
from anthropic import Anthropic

BASE_URL = "https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api"
MODEL = "thinkingmachines/Inkling"

client = Anthropic(
    base_url=BASE_URL,
    api_key=getenv("TINKER_API_KEY"),
)

response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    messages=[{"role": "user", "content": "The capital of France is"}],
)

print(response.content[0].text)
```

Notes:

- `BASE_URL` points to the Anthropic-compatible inference endpoint.
- `MODEL` can be a base model name (like `thinkingmachines/Inkling`) or a sampler checkpoint path from Tinker (`tinker://...:train:0/sampler_weights/000080`).
- `max_tokens` is required by the Messages API, as it is with Anthropic.
- `messages`, `system`, `temperature`, `top_p`, `top_k`, and `stop_sequences` behave as they do in the Anthropic Messages API.
- You can swap `MODEL` to any other sampler checkpoint to compare runs quickly in your evals or notebooks.

## Controlling thinking effort

Inkling and other Thinking Machines models control how much the model thinks with an **effort** value rather than Anthropic's native `thinking.budget_tokens`. Pass it as a Tinker-specific `output_config.effort` field through your client's `extra_body`:

```py
response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is 17 * 23?"}],
    extra_body={"output_config": {"effort": "high"}},
)

# The model's reasoning is returned as a leading `thinking` content block,
# followed by the answer text.
for block in response.content:
    if block.type == "thinking":
        print("Reasoning:", block.thinking)
    elif block.type == "text":
        print("Answer:", block.text)
```

To turn reasoning off entirely, use the standard Anthropic `thinking` field:

```py
response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    messages=[{"role": "user", "content": "What is 17 * 23?"}],
    thinking={"type": "disabled"},
)
```

Notes:

- `effort` accepts `"low"`, `"medium"`, `"high"`, `"xhigh"`, or `"max"` (`"max"` behaves the same as `"xhigh"`).
- Not all models support effort. Requests against a model that doesn't support it return HTTP 400.
- `thinking={"type": "disabled"}` forces reasoning off regardless of `output_config`. Anthropic's `thinking.budget_tokens` is accepted for wire compatibility but is not used; control effort with `output_config.effort` instead.
- When omitted for a model that supports effort, a default level is applied.
- For the native (non-Anthropic) way to control effort, and for effort scaling results, see [Thinking effort](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/thinking-effort/index.md).

## Tool use

The endpoint round-trips Anthropic tool use. Pass `tools` with an `input_schema`, and the model replies with `tool_use` content blocks; send the results back as `tool_result` blocks in a follow-up `user` message.

```py
response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "input_schema": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        }
    ],
)
```

`tool_choice` supports `auto`, `any`, a named tool, and `none`. When the model calls a tool, `stop_reason` is `tool_use`.

## Streaming

Set `stream=True` (or use `client.messages.stream(...)`) to receive standard Anthropic Server-Sent Events: `message_start`, then `content_block_start` / `content_block_delta` / `content_block_stop` per block, then `message_delta` and `message_stop`. Thinking blocks stream as `thinking_delta`, text as `text_delta`, and tool arguments as `input_json_delta`.

```py
with client.messages.stream(
    model=MODEL,
    max_tokens=512,
    messages=[{"role": "user", "content": "Write a haiku about the ocean."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## Counting tokens

`POST /v1/messages/count_tokens` returns the input token count for a request using the model's real tokenizer and renderer, without sampling.

```py
count = client.messages.count_tokens(
    model=MODEL,
    messages=[{"role": "user", "content": "How many tokens is this?"}],
)
print(count.input_tokens)
```

## Supported and unsupported features

Supported:

- System prompts (string or content-block list), multi-turn conversations, and streaming.
- Tool use, tool results, and `tool_choice`.
- Extended thinking, exposed as `thinking` content blocks and controlled with `output_config.effort` (see above).
- Image inputs via `base64` or `url` image sources.
- Token counting through `/v1/messages/count_tokens`.
- `temperature`, `top_p`, `top_k`, and `stop_sequences`.

Not currently supported:

- **Prompt caching**: `cache_control` is ignored, and the `cache_creation_input_tokens` / `cache_read_input_tokens` usage fields are always null.
- **Citations**.
- **Audio input**: audio content blocks are not part of the Messages API schema.
- **`thinking.budget_tokens`**: accepted for compatibility but not applied. Use `output_config.effort`.
- Thinking-block `signature` values are returned as empty strings.

## Related docs

- [Using Inkling](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/index.md)
- [OpenAI API Compatible Inference](https://tinker-docs.thinkingmachines.ai/tinker/compatible-apis/openai/index.md)
- [Getting a `TINKER_API_KEY`](https://tinker-docs.thinkingmachines.ai/tinker/quickstart/index.md)
- [SamplingClient API Reference](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/samplingclient/index.md)
