---
meta:
  title: Create a message
  description: API reference for generating an Anthropic-compatible message with POST /v1/messages.
  keywords: Messages API, Anthropic Messages, create message, POST /messages, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/messages/create-message
  target: aidmc
---

# Create a message

Generate an Anthropic Messages-compatible assistant message. Requests are supplied in the Anthropic wire format and run through the same inference pipeline as the [Responses API](/docs/api-reference/responses). Supported tools are developer-defined (`custom`) functions and built-in `web_search`.

```openapi-schema
method: POST
path: /messages
operation:
  operationId: createAnthropicMessage
  tags:
  - Anthropic
  summary: Generate an Anthropic-compatible assistant message.
  parameters:
  - name: anthropic-version
    in: header
    required: false
    schema:
      type: string
    description: Anthropic API version header. Accepted for SDK compatibility.
  - name: x-api-key
    in: header
    required: false
    schema:
      type: string
    description: 'API key header used by Anthropic SDKs. `Authorization: Bearer` is also accepted.'
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AnthropicMessageRequest'
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AnthropicMessage'
        text/event-stream:
          schema:
            $ref: '#/components/schemas/AnthropicStreamEvent'
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: /docs/api-reference/messages/schemas#anthropic-content-block
  AnthropicContextManagementConfig: /docs/api-reference/messages/schemas#anthropic-context-management-config
  AnthropicInputMessage: /docs/api-reference/messages/schemas#anthropic-input-message
  AnthropicJsonOutputFormat: /docs/api-reference/messages/schemas#anthropic-json-output-format
  AnthropicMessage: /docs/api-reference/messages/schemas#anthropic-message
  AnthropicMessageRequest: /docs/api-reference/messages/schemas#anthropic-message-request
  AnthropicMessageRequestBase: /docs/api-reference/messages/schemas#anthropic-message-request-base
  AnthropicOutputConfig: /docs/api-reference/messages/schemas#anthropic-output-config
  AnthropicStreamEvent: /docs/api-reference/messages/schemas#anthropic-stream-event
  AnthropicTool: /docs/api-reference/messages/schemas#anthropic-tool
  AnthropicToolChoice: /docs/api-reference/messages/schemas#anthropic-tool-choice
  AnthropicUsage: /docs/api-reference/messages/schemas#anthropic-usage
```

```python title="Python (Anthropic SDK)"
import os

from anthropic import Anthropic

client = Anthropic(
    base_url="https://api.meta.ai",
    auth_token=os.environ["MODEL_API_KEY"],
)

message = client.messages.create(
    model="muse-spark-1.3",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        },
    ],
)

print(message.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/messages",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/messages" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ]
}'
```

<!-- openapi-schemas-page: /docs/api-reference/messages/schemas -->

For reasoning replay, tool calling, and structured output guidance that applies to the shared inference pipeline, see the [Responses](/docs/protocols/responses) feature page.