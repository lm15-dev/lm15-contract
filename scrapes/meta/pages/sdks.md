---
meta:
  title: SDKs and libraries
  description: Use the OpenAI SDK (Python or TypeScript) or the Anthropic SDK with Meta Model API. No custom client required.
  keywords: SDKs, OpenAI SDK, Anthropic SDK, Python SDK, TypeScript SDK, Messages API, libraries
cms:
  alias: /model-api/docs/sdks
  target: aidmc
---

# SDKs and libraries

Build with the tools you already run. **Meta Model API** works with the OpenAI SDK and the Anthropic SDK — no custom client to learn. Point the OpenAI SDK at the Model API base URL for [Responses](/docs/protocols/responses) and [Chat Completions](/docs/protocols/chat-completions), or point the Anthropic SDK at Model API for the [Messages](/docs/protocols/messages) format. Any OpenAI-compatible SDK, HTTP client, or framework — such as LangChain, LlamaIndex, or Vercel AI SDK — works with Model API too.

## Supported features {#supported-features}

Through the OpenAI SDK you can call:

- [Responses API](/docs/protocols/responses) (`client.responses.create()`)
- [Chat completions](/docs/protocols/chat-completions) (`client.chat.completions.create()`)
- [Search grounding](/docs/search-grounding) (via Responses API)
- [Image understanding](/docs/image-understanding) (vision)
- [Video and audio understanding](/docs/video-understanding) (Responses API and Chat Completions)
- [Structured output](/docs/structured-output) (`response_format`)
- [Function calling / tool use](/docs/tool-calling)
- [File uploads](/docs/file-handling) (`client.files.create()`)
- [Streaming](/docs/protocols/chat-completions#streaming)
- [Temperature and sampling parameters](/docs/protocols/chat-completions#parameters)
- [Model selection](/docs/protocols/chat-completions#parameters)

## Python {#python}

Install the package:

```shell
pip install openai
```

Send a request:

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MODEL_API_KEY"],
    base_url="https://api.meta.ai/v1",
)

response = client.responses.create(
    model="muse-spark-1.1",
    input="Explain mixture-of-experts in two sentences.",
)
print(response.output_text)
```

## TypeScript {#typescript}

Install the package:

```shell
npm install openai
```

Send a request:

```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.MODEL_API_KEY,
  baseURL: "https://api.meta.ai/v1",
});

const response = await client.responses.create({
  model: "muse-spark-1.1",
  input: "Explain mixture-of-experts in two sentences.",
});
console.log(response.output_text);
```

## Anthropic SDK {#anthropic}

Use the Anthropic SDK for Model API's [Messages API](/docs/protocols/messages). Set the base host to `https://api.meta.ai` — the SDK appends `/v1/messages` — and pass your Model API key as a bearer token:

```python title="Python (Anthropic SDK)"
import os
from anthropic import Anthropic

client = Anthropic(
    base_url="https://api.meta.ai",
    auth_token=os.environ["MODEL_API_KEY"],
)

message = client.messages.create(
    model="muse-spark-1.1",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain mixture-of-experts in two sentences."}],
)
print(message.content[0].text)
```

See the [Messages API guide](/docs/protocols/messages) for the full request and response shape.

## Authentication {#authentication}

The OpenAI SDK looks for `OPENAI_API_KEY` by default, not `MODEL_API_KEY`. Pass your Model API key explicitly when you create the client:

```python title="Python (OpenAI SDK)"
client = OpenAI(
    api_key=os.environ["MODEL_API_KEY"],
    base_url="https://api.meta.ai/v1",
)
```

See [Authentication](/docs/authentication) for details on creating and managing API keys.