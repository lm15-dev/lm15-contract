---
meta:
  title: Chat completions API reference
  description: API reference for the POST /v1/chat/completions endpoint.
  keywords: chat completions, API reference, /v1/chat/completions, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/chat-completions
  target: aidmc
  in_page_nav: false
---

# Chat completions

The chat completions endpoint generates a model response from a conversation supplied as a list of messages. Reasoning is not carried across turns on this endpoint; for agentic and multi-step workloads that need reasoning continuity, use the [Responses API](/docs/api-reference/responses).

- [Create a chat completion](/docs/api-reference/chat-completions/create-chat-completion)
- [Schemas](/docs/api-reference/chat-completions/schemas)

For usage examples, streaming, multi-turn conversations, and parameter guidance, see the [Chat completion](/docs/protocols/chat-completions) feature page.