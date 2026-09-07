---
meta:
  title: Messages API reference
  description: API reference for the Anthropic-compatible /v1/messages endpoints.
  keywords: Messages API, Anthropic Messages, API reference, /v1/messages, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/messages
  target: aidmc
  in_page_nav: false
---

# Messages (Anthropic-compatible)

The messages endpoints provide an Anthropic Messages-compatible surface over Meta Model API. Supply requests in the Anthropic wire format — `POST /v1/messages` generates an assistant message and `POST /v1/messages/count_tokens` counts input tokens without generating. Authentication, rate limits, and billing match the other Model API endpoints; supported tools are developer-defined (`custom`) functions and built-in `web_search`.

- [Create a message](/docs/api-reference/messages/create-message)
- [Count tokens](/docs/api-reference/messages/count-tokens)
- [Schemas](/docs/api-reference/messages/schemas)

For guidance on reasoning replay, tool calling, and structured output that also applies to the shared inference pipeline, see the [Responses](/docs/protocols/responses) feature page.