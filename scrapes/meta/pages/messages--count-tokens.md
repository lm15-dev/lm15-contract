---
meta:
  title: Count tokens
  description: API reference for counting input tokens with POST /v1/messages/count_tokens.
  keywords: Messages API, Anthropic Messages, count tokens, token counting, POST /messages count_tokens, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/messages/count-tokens
  target: aidmc
---

# Count tokens

Count the number of input tokens an Anthropic-format Messages request would consume, without generating a message.

```openapi-schema
method: POST
path: /messages/count_tokens
operation:
  operationId: countAnthropicMessageTokens
  tags:
  - Anthropic
  summary: Count input tokens for an Anthropic-compatible Messages request.
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
          $ref: '#/components/schemas/AnthropicCountTokensRequest'
  responses:
    '200':
      description: Success
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AnthropicCountTokensResponse'
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: /docs/api-reference/messages/schemas#anthropic-content-block
  AnthropicContextManagementConfig: /docs/api-reference/messages/schemas#anthropic-context-management-config
  AnthropicCountTokensRequest: /docs/api-reference/messages/schemas#anthropic-count-tokens-request
  AnthropicCountTokensResponse: /docs/api-reference/messages/schemas#anthropic-count-tokens-response
  AnthropicInputMessage: /docs/api-reference/messages/schemas#anthropic-input-message
  AnthropicJsonOutputFormat: /docs/api-reference/messages/schemas#anthropic-json-output-format
  AnthropicMessageRequestBase: /docs/api-reference/messages/schemas#anthropic-message-request-base
  AnthropicOutputConfig: /docs/api-reference/messages/schemas#anthropic-output-config
  AnthropicTool: /docs/api-reference/messages/schemas#anthropic-tool
  AnthropicToolChoice: /docs/api-reference/messages/schemas#anthropic-tool-choice
```

```python title="Python (Anthropic SDK)"
import os

from anthropic import Anthropic

client = Anthropic(
    base_url="https://api.meta.ai",
    auth_token=os.environ["MODEL_API_KEY"],
)

message = client.messages.count_tokens(
    model="muse-spark-1.3",
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
    "https://api.meta.ai/v1/messages/count_tokens",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
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
curl -X POST "https://api.meta.ai/v1/messages/count_tokens" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ]
}'
```

<!-- openapi-schemas-page: /docs/api-reference/messages/schemas -->

For usage examples and rate-limit guidance that applies to the shared inference pipeline, see the [Responses](/docs/protocols/responses) feature page.