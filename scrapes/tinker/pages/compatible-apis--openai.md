# OpenAI API Compatible Inference (Beta)

OpenAI-compatible inference lets you interact with any model checkpoint in Tinker, using an endpoint compatible with the [OpenAI Completions API](https://platform.openai.com/docs/api-reference/chat). It’s designed to let you easily “poke at” your model while you're training it:

- **Fast feedback while training**: Start sampling very quickly from any sampler checkpoint obtained during training.
- **Sampling while training continues**: Sample even while the training job is still running on that experiment.
- **Developer & internal workflows**: Intended for testing, evaluation, and internal tools.

You can also use OpenAI-compatible inference for production traffic. For higher or more stable throughput, or guidance on large-scale setups, [join our waitlist for production inference](https://form.typeform.com/to/CPTm26T7).

## Using OpenAI compatible inference from an OpenAI client

The new interface exposes an OpenAI-compatible HTTP API. You can use any OpenAI SDK or HTTP client that lets you override the base URL.

1. Set the base URL of your OpenAI-compatible client to:

```text
https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1
```

2. Use a Tinker sampler weight path as the model name. For example:

```text
tinker://0034d8c9-0a88-52a9-b2b7-bce7cb1e6fef:train:0/sampler_weights/000080
```

Any valid Tinker sampler checkpoint path works here. You can keep training and sample from the same checkpoint simultaneously.

3. Authenticate with your Tinker API key, by passing the same key used for Tinker as the API key to the OpenAI client.

**Note:** We support both `/completions` and `/chat/completions` endpoints. For most use cases we recommend `/chat/completions`. Here's how to decide which one to use:

- **`/chat/completions`** — for chat-formatted prompts. You pass `messages` and the server renders them with the model’s default Hugging Face chat template, so it works out-of-the-box for checkpoints that use that template.
- **`/completions`** — for raw text continuation. You pass plain text and the model continues it, with no chat template applied. This is the usual way to sample from base (pretrained) models, or for completion-style prompting.
- If your checkpoint expects a different renderer, render the prompt to token IDs yourself (see the [Rendering tutorial](https://tinker-docs.thinkingmachines.ai/tutorials/core-concepts/rendering/index.md)) and sample with the native [`SamplingClient`](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/samplingclient/index.md) (`ModelInput.from_ints(...)`), which uses your exact tokens.

## Code Example

```py
from os import getenv
from openai import OpenAI

BASE_URL = "https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1"
MODEL_PATH = "tinker://0034d8c9-0a88-52a9-b2b7-bce7cb1e6fef:train:0/sampler_weights/000080"

api_key = getenv("TINKER_API_KEY")

client = OpenAI(
    base_url=BASE_URL,
    api_key=api_key,
)

response = client.completions.create(
    model=MODEL_PATH,
    prompt="The capital of France is",
    max_tokens=50,
    temperature=0.7,  # example value, not a recommended default
    top_p=0.9,  # example value, not a recommended default
)

print(f"{response.choices[0].text}")
```

Notes:

- `BASE_URL` points to the OpenAI compatible inference endpoint.
- `MODEL_PATH` is a sampler checkpoint path from Tinker (`tinker://0034d8c9-0a88-52a9-b2b7-bce7cb1e6fef:train:0/sampler_weights/000080`).
- The rest of the arguments (`prompt`, `max_tokens`, `temperature`, `top_p`) behave like they do in the OpenAI Completions API.
- The `temperature` and `top_p` values above are only there to show how you pass these parameters. They are not suggested defaults, so pick values that fit your use case.
- You can swap `MODEL_PATH` to any other sampler checkpoint to compare runs quickly in your evals or notebooks.

## Separating reasoning from response content

For reasoning models that emit chain-of-thought alongside their final answer, the `/chat/completions` endpoint accepts a non-standard `separate_reasoning` flag. When set to `true`, the server parses out the reasoning portion and returns it on a dedicated `reasoning_content` field rather than inlining it into `content`.

```py
response = client.chat.completions.create(
    model=MODEL_PATH,
    messages=[{"role": "user", "content": "What is 17 * 23?"}],
    extra_body={"separate_reasoning": True},
)

message = response.choices[0].message
print("Reasoning:", message.reasoning_content)
print("Answer:", message.content)
```

Notes:

- `separate_reasoning` defaults to `true`; set it to `false` to keep the reasoning trace inlined in `content`.
  - The default was changed from `false` to `true` in June 2026.
- Only available on `/chat/completions` (not `/completions`).
- In streaming mode, `reasoning_content` and `content` arrive on separate SSE events — the reasoning chunks come first, followed by the answer chunks.
- The flag is a no-op for models that don't produce a separable reasoning trace.

## Controlling thinking effort

For models that support it, the `/chat/completions` endpoint accepts the standard OpenAI `reasoning_effort` parameter to bias how much the model thinks before answering. Set it to one of the OpenAI strings — `"none"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"` — or pass a raw float in `[0.0, 0.99]` for finer control.

```py
response = client.chat.completions.create(
    model=MODEL_PATH,
    messages=[{"role": "user", "content": "What is 17 * 23?"}],
    reasoning_effort="high",
)
```

You can also pass a float via `extra_body`:

```py
response = client.chat.completions.create(
    model=MODEL_PATH,
    messages=[{"role": "user", "content": "What is 17 * 23?"}],
    extra_body={"reasoning_effort": 0.8},
)
```

Notes:

- Not all models support this parameter. Requests against a model that doesn't support it return HTTP 400.
- The OpenAI strings map to fixed floats internally: `"none"` → `0.0`, `"minimal"` → `0.1`, `"low"` → `0.2`, `"medium"` → `0.7`, `"high"` → `0.9`, and `"xhigh"` → `0.99`.
- When omitted, reasoning effort defaults to `0.9`.
- Only available on `/chat/completions` (not `/completions`).

## Related docs

- [Getting a `TINKER_API_KEY`](https://tinker-docs.thinkingmachines.ai/tinker/quickstart/index.md)
- [Security and Privacy](https://thinkingmachines.ai/legal/terms/)
- [SamplingClient API Reference](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/samplingclient/index.md)
