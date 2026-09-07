---
meta:
  title: Responses API reference
  description: API reference for the /v1/responses endpoints.
  keywords: Responses API, API reference, /v1/responses, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/responses
  target: aidmc
  in_page_nav: false
---

# Responses

The responses endpoints create and manage model responses for agentic and multi-turn workloads. Carry the model's reasoning across turns with stateless encrypted reasoning replay or with server-managed state (`previous_response_id`), alongside tool calling, search grounding, and file inputs.

- [Create a response](/docs/api-reference/responses/create-response)
- [Retrieve a response](/docs/api-reference/responses/retrieve-response)
- [Delete a response](/docs/api-reference/responses/delete-response)
- [Cancel a response](/docs/api-reference/responses/cancel-response)
- [Count input tokens](/docs/api-reference/responses/count-input-tokens)
- [Schemas](/docs/api-reference/responses/schemas)

For usage examples, `previous_response_id` patterns, and guidance on when to use the Responses API versus Chat Completions, see the [Responses](/docs/protocols/responses) feature page.