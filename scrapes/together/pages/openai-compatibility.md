> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# OpenAI compatibility

> Point your OpenAI Python or TypeScript client at Together AI to call open-source models without rewriting your app.

<Note>
  The full OpenAPI spec is available at [openapi.yaml](https://docs.together.ai/openapi.yaml).
</Note>

Together's API is compatible with the OpenAI REST API and SDKs across chat, completions, vision, image generation, text-to-speech, and embeddings. If you have an application that uses the OpenAI Python or TypeScript client (or cURL against `api.openai.com`), you can point it at models hosted on Together with two changes: the API key and base URL.

This page is a configuration reference for the Together AI OpenAI compatibility layer. For end-to-end examples of each capability, follow the links to the dedicated capability pages.

## Drop-in client setup

Set `api_key` to your [Together API key](/docs/api-keys-authentication) (or pull it from an environment variable) and `base_url` to `https://api.together.ai/v1`:

<CodeGroup>
  ```python Python theme={null}
  import os
  import openai

  client = openai.OpenAI(
      api_key=os.environ.get("TOGETHER_API_KEY"),
      base_url="https://api.together.ai/v1",
  )

  response = client.chat.completions.create(
      model="MiniMaxAI/MiniMax-M3",
      messages=[{"role": "user", "content": "Hello!"}],
  )

  print(response.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  import OpenAI from "openai";

  const client = new OpenAI({
    apiKey: process.env.TOGETHER_API_KEY,
    baseURL: "https://api.together.ai/v1",
  });

  const response = await client.chat.completions.create({
    model: "MiniMaxAI/MiniMax-M3",
    messages: [{ role: "user", content: "Hello!" }],
  });

  console.log(response.choices[0].message.content);
  ```

  ```bash cURL theme={null}
  curl https://api.together.ai/v1/chat/completions \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "MiniMaxAI/MiniMax-M3",
      "messages": [{"role": "user", "content": "Hello!"}]
    }'
  ```
</CodeGroup>

You can find your API key in [your settings page](https://api.together.ai/settings/projects/~current/api-keys). If you don't have an account, you can [register for free](https://api.together.ai/).

<Tip>
  Substitute the `model` field with any [Together model ID](/docs/serverless/models). Model names follow the `<provider>/<model_name>` convention rather than OpenAI's flat namespace.
</Tip>

## Endpoint compatibility matrix

The following OpenAI SDK methods route to Together-native endpoints when the base URL is set to `https://api.together.ai/v1`.

| OpenAI SDK call                               | Together endpoint               | Status        | Capability page                                                                                                                                            |
| --------------------------------------------- | ------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `chat.completions.create`                     | `POST /v1/chat/completions`     | Supported     | [Chat overview](/docs/inference/chat/overview), [Streaming](/docs/inference/chat/overview#stream-responses), [Parameters](/docs/inference/chat/parameters) |
| `chat.completions.create` (vision input)      | `POST /v1/chat/completions`     | Supported     | [Vision](/docs/inference/vision/overview)                                                                                                                  |
| `chat.completions.create` (tools)             | `POST /v1/chat/completions`     | Supported     | [Function calling](/docs/inference/function-calling/overview)                                                                                              |
| `chat.completions.create` (`response_format`) | `POST /v1/chat/completions`     | Supported     | [Structured outputs](/docs/inference/chat/structured-outputs)                                                                                              |
| `completions.create`                          | `POST /v1/completions`          | Supported     | Legacy text completions, see [Parameters](/docs/inference/chat/parameters)                                                                                 |
| `embeddings.create`                           | `POST /v1/embeddings`           | Supported     | [Embeddings](/reference/embeddings-2)                                                                                                                      |
| `images.generate`                             | `POST /v1/images/generations`   | Supported     | [Image generation](/docs/inference/images/overview)                                                                                                        |
| `audio.speech.create`                         | `POST /v1/audio/speech`         | Supported     | [Text-to-speech](/docs/inference/text-to-speech/overview)                                                                                                  |
| `audio.transcriptions.create`                 | `POST /v1/audio/transcriptions` | Supported     | [Speech-to-text](/docs/inference/transcription/overview)                                                                                                   |
| `audio.translations.create`                   | `POST /v1/audio/translations`   | Supported     | [Speech-to-text](/docs/inference/transcription/overview)                                                                                                   |
| `models.list`, `models.retrieve`              | `GET /v1/models`                | Supported     | [Model list](/docs/serverless/models)                                                                                                                      |
| `assistants.*`, `threads.*`, `runs.*`         | n/a                             | Not supported | Build agent loops on top of chat completions and [function calling](/docs/inference/function-calling/overview)                                             |
| `fine_tuning.jobs.*` (OpenAI shape)           | n/a                             | Not supported | Use the Together-native [fine-tuning API](/docs/fine-tuning/quickstart)                                                                                    |
| `files.*` (OpenAI shape)                      | n/a                             | Partial       | Together has its own [Files API](/reference/upload-file) for fine-tuning datasets and batch jobs                                                           |
| `batches.*` (OpenAI shape)                    | n/a                             | Not supported | Use the Together-native [Batch API](/docs/inference/batch/overview)                                                                                        |
| `moderations.create`                          | n/a                             | Not supported | See [moderation models](/docs/serverless/models#moderation-models) using Llama Guard via chat completions                                                  |

Together-native endpoints not exposed by the OpenAI SDKs (call them with `requests`, `fetch`, or the Together SDK):

* Video generation, see [Video generation](/docs/inference/videos/overview).
* Image edits and inpainting beyond `images.generate`, see [Image generation](/docs/inference/images/overview).
* Reasoning controls and `reasoning_content`, see [Reasoning](/docs/inference/chat/reasoning).
* Logprobs surface, see [Logprobs](/docs/inference/chat/logprobs).

## Drop-in compatibility

These capabilities work without code changes beyond the API key and base URL. Each row maps a Together capability to the OpenAI SDK method that drives it.

| Capability                        | OpenAI SDK method                                          | Capability page                                               |
| --------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------- |
| Chat completions (with streaming) | `chat.completions.create`                                  | [Chat overview](/docs/inference/chat/overview)                |
| Vision (image inputs)             | `chat.completions.create` with image content parts         | [Vision](/docs/inference/vision/overview)                     |
| Function calling                  | `chat.completions.create` with `tools` and `tool_choice`   | [Function calling](/docs/inference/function-calling/overview) |
| Structured outputs                | `chat.completions.create` with `response_format`           | [Structured outputs](/docs/inference/chat/structured-outputs) |
| Embeddings                        | `embeddings.create`                                        | [Embeddings](/reference/embeddings-2)                         |
| Image generation                  | `images.generate`                                          | [Image generation](/docs/inference/images/overview)           |
| Text-to-speech                    | `audio.speech.create`                                      | [Text-to-speech](/docs/inference/text-to-speech/overview)     |
| Speech-to-text and translation    | `audio.transcriptions.create`, `audio.translations.create` | [Speech-to-text](/docs/inference/transcription/overview)      |

[Video generation](/docs/inference/videos/overview) is Together-native and isn't exposed through the OpenAI SDK.

## Known incompatibilities

### Model identifiers

Together model IDs are namespaced (`openai/gpt-oss-120b`, `meta-llama/Llama-3.3-70B-Instruct-Turbo`, `black-forest-labs/FLUX.2-dev`). OpenAI model strings like `gpt-4o` or `text-embedding-3-large` return a 404. Browse the full list at [Available models](/docs/serverless/models).

### Endpoints not implemented

* Assistants, Threads, and Runs are not implemented. Build the agent loop yourself with [function calling](/docs/inference/function-calling/overview).
* The OpenAI-shaped Batch API and Files API are not exposed through `/v1`. Together has separate equivalents, see [Batch processing](/docs/inference/batch/overview) and [Files](/reference/upload-file).
* `moderations.create` is not implemented. Use Llama Guard via chat completions, see [Moderation models](/docs/serverless/models#moderation-models).

### Parameter quirks

* `logprobs` returns Together's own shape, which is richer than OpenAI's. See [Logprobs](/docs/inference/chat/logprobs).
* `seed` is best-effort. Determinism is not guaranteed across replicas, model versions, or load conditions.
* `n` (multiple completions per request) is supported on most chat models but not on every model. Loop client-side if a model rejects it.
* `logit_bias` is not supported on most models.
* `service_tier`, `store`, `metadata`, and `prediction` are accepted but ignored.
* `reasoning_effort` works on GPT-OSS models (`"low"`, `"medium"`, `"high"`). Other reasoning controls (Together's `reasoning={"enabled": ...}` toggle, `chat_template_kwargs`) are not part of OpenAI's API surface. See [Reasoning](/docs/inference/chat/reasoning).
* Vision models accept `image_url` with both remote URLs and base64 data URIs. The `detail` field is accepted but ignored.

### Response shape differences

* `usage` always includes `prompt_tokens`, `completion_tokens`, and `total_tokens`. Extra token counts vary in **location** by model, so read both shapes defensively:

  * Reasoning models (for example `zai-org/GLM-5.2`, `deepseek-ai/DeepSeek-V4-Pro-0813`, `Qwen/Qwen3.6-Plus`) nest them OpenAI-style: cached prompt tokens under `usage.prompt_tokens_details.cached_tokens` and reasoning tokens under `usage.completion_tokens_details.reasoning_tokens`.
  * Some non-reasoning models (for example `meta-llama/Llama-3.3-70B-Instruct-Turbo`) return `cached_tokens` flat at the top level of `usage`, with no `*_details` objects.

  A client configured for only one shape will return `0` for all others (with no error message). Fall back across both locations, for example `(usage.prompt_tokens_details or {}).get("cached_tokens") or usage.get("cached_tokens", 0)`.
* Reasoning models return the chain of thought in a `reasoning` or `reasoning_content` field on the assistant message (not OpenAI's nested `reasoning` object). The field name depends on the model. Pass it back under the same key when you send a prior turn to the API for preserved thinking or multi-turn tool calling. See [Reasoning](/docs/inference/chat/reasoning#handle-reasoning-tokens) for details.
* `id` and `system_fingerprint` are present but use Together's formats. Don't parse them as OpenAI IDs.
* `images.generate` returns `url` or `b64_json` per the `response_format` param, matching OpenAI. Some image models also return Together-specific metadata fields (for example `seed`).

### Errors

Together returns OpenAI-shaped error objects (`{ "error": { "message", "type", "code" } }`), but `type` and `code` values are Together's. Match on HTTP status (400, 401, 404, 429, 500, 503) for portable handling.

## Community libraries

The Together API is also supported by most [OpenAI libraries built by the community](https://platform.openai.com/docs/libraries).

If you come across unexpected behavior, [reach out to support](https://www.together.ai/contact).
