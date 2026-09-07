---
meta:
  title: API reference — Meta Model API
  description: The Meta Model API HTTP reference — base URL, authentication, and the Responses, Chat Completions, Messages, Files, Models, and Status resources.
  keywords: Meta Model API, API reference, base URL, authentication, endpoints, Muse Spark
cms:
  layout: large
  alias: /model-api/docs/api-reference
  target: aidmc
---

# API reference

Meta Model API is an HTTP API served at `https://api.meta.ai/v1` and authenticated with a bearer token. This reference documents each resource's request and response schema. For a task-oriented introduction, start with the [Quickstart](/docs/quickstart); to choose a request format, see [Choosing an API](/docs/protocols).

## Base URL and authentication {#base-url-and-authentication}

| | |
| --- | --- |
| **Base URL** | `https://api.meta.ai/v1` |
| **Auth header** | `Authorization: Bearer $MODEL_API_KEY` |
| **Env var** | `MODEL_API_KEY` |

Create and manage keys in the [Model API dashboard](/); see the [Authentication guide](/docs/authentication) for storage and rotation.

## Resources {#resources}

- **[Responses](/docs/api-reference/responses)**: `POST /v1/responses` and related endpoints — server-managed, agentic generation with reasoning replay. OpenAI-compatible.
- **[Chat completions](/docs/api-reference/chat-completions)**: `POST /v1/chat/completions` — the OpenAI-compatible messages-array endpoint.
- **[Messages](/docs/api-reference/messages)**: `POST /v1/messages` — the Anthropic Messages-compatible endpoint.
- **[Files](/docs/api-reference/files)**: `POST /v1/files` (upload), `GET /v1/files` (list), `GET`/`DELETE /v1/files/{file_id}` (retrieve/delete a single file) — upload and manage files referenced in requests.
- **[Models](/docs/api-reference/models)**: `GET /v1/models` — list available models and retrieve model details.
- **[Status](/docs/api-reference/status)**: `GET /v1/status` — unauthenticated service-health endpoint.

## Errors and rate limits {#errors-and-rate-limits}

Errors use an OpenAI-style envelope — `{ "error": { "message", "type", "param", "code" } }`. Branch on `type` and `message`. See [Error handling](/docs/error-handling) for the full list of types, status codes, and retry guidance.

Rate limits apply per team. See [Pricing and rate limits](/docs/pricing-rate-limits) for the current tiers and headers.