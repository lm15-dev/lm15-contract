> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# OpenAI compatibility

You can use the [OpenAI Python client library](https://github.com/openai/openai-python) to interact with Fireworks. This makes migration of existing applications already using OpenAI particularly easy.

For Anthropic SDK support, see [Anthropic compatibility](/tools-sdks/anthropic-compatibility). For NVIDIA NIM / vLLM request fields such as `chat_template_kwargs`, see [NIM compatibility](/tools-sdks/nim-compatibility).

## Specify endpoint and API key

### Using the OpenAI client

You can use the OpenAI client by initializing it with your Fireworks configuration:

```python theme={null}
from openai import OpenAI

# Initialize with Fireworks parameters
client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<YOUR_FIREWORKS_API_KEY>",
)
```

You can also use environment variables with the client:

```python theme={null}
import os
from openai import OpenAI

# Initialize using environment variables
client = OpenAI(
    base_url=os.environ.get("OPENAI_API_BASE", "https://api.fireworks.ai/inference/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),  # Set to your Fireworks API key
)
```

### Using environment variables

```shell theme={null}
export OPENAI_API_BASE="https://api.fireworks.ai/inference/v1"
export OPENAI_API_KEY="<YOUR_FIREWORKS_API_KEY>"
```

### Alternative approach

```python theme={null}
import openai

# warning: it has a process-wide effect
openai.api_base = "https://api.fireworks.ai/inference/v1"
openai.api_key = "<YOUR_FIREWORKS_API_KEY>"
```

## Usage

Use OpenAI's SDK how you'd normally would. Just ensure that the `model` parameter refers to one of [Fireworks models](https://fireworks.ai/models).

### Completion

Simple completion API that doesn't modify provided prompt in any way:

```python theme={null}
from openai import OpenAI

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<YOUR_FIREWORKS_API_KEY>",
)

completion = client.completions.create(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    prompt="The quick brown fox",
)
print(completion.choices[0].text)
```

### Chat Completion

Works best for models trained for conversation (e.g. llama\*-chat variants):

```python theme={null}
from openai import OpenAI

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key="<YOUR_FIREWORKS_API_KEY>",
)

chat_completion = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "Say this is a test",
        },
    ],
)
print(chat_completion.choices[0].message.content)
```

<h2 id="training-compatibility">
  Training compatibility
</h2>

Fireworks training uses the same **OpenAI-compatible chat completion format** for training data. If you have datasets formatted for OpenAI SFT, they work on Fireworks with no conversion required — the same `messages` array with `role`, `content`, `tool_calls`, and `weight` fields.

Fireworks also supports additional features in the training schema:

* **Thinking traces** via `reasoning_content` on assistant messages (for models like DeepSeek R1 and Qwen3)
* **Per-message weights** to control which turns the model learns from
* **Per-sample weights** for weighted training
* **Vision inputs** using the same OpenAI-compatible multimodal content format

To get started with training, see the [Supervised Fine-Tuning guide](/fine-tuning/fine-tuning-models) or the [Training overview](/fine-tuning/finetuning-intro).

## API compatibility

### Differences

The following options have minor differences:

* `max_tokens`: behaves differently if the model context length is exceeded. If the length of `prompt` or `messages` plus `max_tokens` is higher than the model's context window, `max_tokens` will be adjusted lower accordingly. OpenAI returns an invalid request error in this situation. Control this behavior with the `context_length_exceeded_behavior` parameter:
  * `truncate` (default): Automatically adjusts `max_tokens` to fit within the context window
  * `error`: Returns an error like OpenAI does

### Token usage for streaming responses

OpenAI API returns usage stats (number of tokens in prompt and completion) for non-streaming responses but doesn't for the streaming ones (see [forum post](https://community.openai.com/t/chat-completion-stream-api-token-usage/352964)).

Fireworks API returns usage stats in both cases. For streaming responses, the `usage` field is returned in the very last chunk on the response (i.e. the one having `finish_reason` set). For example:

```bash cURL theme={null}
curl --request POST \
     --url https://api.fireworks.ai/inference/v1/completions \
     --header "accept: application/json" \
     --header "authorization: Bearer $API_KEY" \
     --header "content-type: application/json" \
     --data '{"model": "accounts/fireworks/models/starcoder-16b-w8a16", "prompt": "def say_hello_world():", "max_tokens": 100, "stream": true}'
```

```
data: {..., "choices":[{"text":"\n  print('Hello,","index":0,"finish_reason":null,"logprobs":null}],"usage":null}

data: {..., "choices":[{"text":" World!')\n\n\n","index":0,"finish_reason":null,"logprobs":null}],"usage":null}

data: {..., "choices":[{"text":"say_hello_","index":0,"finish_reason":null,"logprobs":null}],"usage":null}

data: {..., "choices":[{"text":"world()\n","index":0,"finish_reason":"stop","logprobs":null}],"usage":{"prompt_tokens":7,"total_tokens":24,"completion_tokens":17}}

data: [DONE]
```

<Note>
  Note, that if you're using OpenAI SDK, they `usage` field won't be listed in the SDK's structure definition. But it can be accessed directly. For example:

  <CodeGroup>
    ```python Python theme={null}
    for chunk in client.chat.completions.create(stream=True, ...):
        if chunk.usage:  # Available in final chunk
            print(f"Tokens: {chunk.usage.total_tokens}")
    ```

    ```typescript TypeScript theme={null}
    for await (const chunk of await openai.chat.completions.create(...)) {
        console.log((chunk as any).usage);
    }
    ```
  </CodeGroup>
</Note>
