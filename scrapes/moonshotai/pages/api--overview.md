> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# API Overview

> Review Kimi API base URLs, authentication, request conventions, compatibility, and links to the main API endpoints.

## Service Address

```
https://api.moonshot.ai
```

The `base_url` differs by compatible protocol; see "Protocol Compatibility" below.

## Protocol Compatibility

The Kimi API is compatible with three API formats, so you can reuse the corresponding official SDKs and tools:

| Compatible API          | base\_url                           | Endpoint                         | SDKs / Tools                                                                                                     |
| ----------------------- | ----------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| OpenAI Chat Completions | `https://api.moonshot.ai/v1`        | [`/chat/completions`](/docs/api/chat) | Official OpenAI SDKs (Python / Node.js), plus third-party tools and frameworks such as LangChain, Dify, and Coze |
| OpenAI Responses        | `https://api.moonshot.ai/v1`        | [`/responses`](/docs/api/responses)   | Official OpenAI SDKs (Python / Node.js)                                                                          |
| Anthropic Messages      | `https://api.moonshot.ai/anthropic` | [`/messages`](/docs/api/messages)     | Official Anthropic SDKs, Claude Code, and similar tools                                                          |

If your project already uses the official OpenAI or Anthropic APIs, simply replace `base_url` and the API Key with your Kimi configuration to migrate — no other code changes are needed.

<Note>
  When using the OpenAI-compatible endpoints, some parameters are Kimi-specific extensions: the `thinking` parameter needs to be passed via the SDK's `extra_body`; `partial` is a field on assistant messages within the messages array (`"partial": true`), not a top-level request parameter. See [Tool Use](/docs/api/tool-use) and [Partial Mode](/docs/api/partial) for details.
</Note>

## Authentication

All API requests require an API Key in the HTTP header:

```
Authorization: Bearer $MOONSHOT_API_KEY
```

API Keys can be created and managed in the [Kimi Open Platform Console](https://platform.kimi.ai/console/api-keys).

<Warning>
  Your API Key is sensitive. Do not expose it in client-side code, public repositories, or logs. Use environment variables to manage it.
</Warning>

When using an official SDK, pass your API Key and the protocol-specific `base_url` at initialization.

OpenAI-compatible endpoints:

<CodeGroup>
  ```python Python theme={null}
  import os

  from openai import OpenAI

  client = OpenAI(
      api_key=os.environ["MOONSHOT_API_KEY"],
      base_url="https://api.moonshot.ai/v1",
  )
  ```

  ```javascript Node.js theme={null}
  const OpenAI = require("openai");

  const client = new OpenAI({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: "https://api.moonshot.ai/v1",
  });
  ```
</CodeGroup>

Anthropic-compatible endpoints:

<CodeGroup>
  ```python Python theme={null}
  import os

  from anthropic import Anthropic

  client = Anthropic(
      api_key=os.environ["MOONSHOT_API_KEY"],
      base_url="https://api.moonshot.ai/anthropic",
  )
  ```

  ```javascript Node.js theme={null}
  const Anthropic = require("@anthropic-ai/sdk");

  const client = new Anthropic({
      apiKey: process.env.MOONSHOT_API_KEY,
      baseURL: "https://api.moonshot.ai/anthropic",
  });
  ```
</CodeGroup>

## Error Handling

Failed requests return a JSON error response with `error.type` and `error.message` fields. For the full list of error types, messages, and troubleshooting tips, see [Errors](/docs/api/errors).

## API Endpoints

| Endpoint                              | Method | Protocol  | Description                              |
| ------------------------------------- | ------ | --------- | ---------------------------------------- |
| `/v1/chat/completions`                | POST   | OpenAI    | [Create Chat Completion](/docs/api/chat)      |
| `/v1/responses`                       | POST   | OpenAI    | [Responses API](/docs/api/responses)          |
| `/anthropic/v1/messages`              | POST   | Anthropic | [Messages API](/docs/api/messages)            |
| `/v1/models`                          | GET    | OpenAI    | [List Models](/docs/api/list-models)          |
| `/v1/tokenizers/estimate-token-count` | POST   | OpenAI    | [Estimate Tokens](/docs/api/estimate)         |
| `/v1/users/me/balance`                | GET    | OpenAI    | [Check Balance](/docs/api/balance)            |
| `/v1/files`                           | POST   | OpenAI    | [Upload File](/docs/api/files-upload)         |
| `/v1/files`                           | GET    | OpenAI    | [List Files](/docs/api/files-list)            |
| `/v1/files/{file_id}`                 | GET    | OpenAI    | [Get File Info](/docs/api/files-retrieve)     |
| `/v1/files/{file_id}`                 | DELETE | OpenAI    | [Delete File](/docs/api/files-delete)         |
| `/v1/files/{file_id}/content`         | GET    | OpenAI    | [Get File Content](/docs/api/files-content)   |
| `/v1/batches`                         | POST   | OpenAI    | [Create Batch](/docs/api/batch-create)        |
| `/v1/batches`                         | GET    | OpenAI    | [List Batches](/docs/api/batch-list)          |
| `/v1/batches/{batch_id}`              | GET    | OpenAI    | [Get Batch Details](/docs/api/batch-retrieve) |
| `/v1/batches/{batch_id}/cancel`       | POST   | OpenAI    | [Cancel Batch](/docs/api/batch-cancel)        |

## Next Steps

<CardGroup cols={2}>
  <Card title="Quickstart" icon="rocket" href="/docs/api/quickstart">
    Send your first API request
  </Card>

  <Card title="Responses API" icon="code" href="/docs/api/responses">
    OpenAI Responses-compatible endpoint
  </Card>

  <Card title="Messages API" icon="message" href="/docs/api/messages">
    Anthropic Messages-compatible endpoint
  </Card>

  <Card title="List Models" icon="list" href="/docs/api/list-models">
    See the currently available models
  </Card>
</CardGroup>
