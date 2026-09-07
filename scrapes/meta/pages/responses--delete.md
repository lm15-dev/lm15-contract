---
meta:
  title: Delete a response
  description: API reference for deleting a model response with DELETE /v1/responses/{response_id}.
  keywords: Responses API, delete response, DELETE /responses, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/responses/delete-response
  target: aidmc
---

# Delete a response

Delete a previously created response by its ID.

```openapi-schema
method: DELETE
path: /responses/{response_id}
operation:
  operationId: deleteResponse
  tags:
  - Responses
  summary: Delete a stored model response by ID.
  parameters:
  - in: path
    name: response_id
    required: true
    schema:
      type: string
    description: The ID of the response to delete.
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/DeleteResponseResponse'
components:
  schemas: {}
page_linked_schemas:
  DeleteResponseResponse: /docs/api-reference/responses/schemas#delete-response-response
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.delete("resp_abc123")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.delete(
    "https://api.meta.ai/v1/responses/resp_abc123",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X DELETE "https://api.meta.ai/v1/responses/resp_abc123" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/responses/schemas -->

For usage examples and guidance on managing server-side conversation state, see the [Responses](/docs/protocols/responses) feature page.