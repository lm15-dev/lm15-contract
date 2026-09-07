---
meta:
  title: List models
  description: API reference for listing available models with GET /v1/models.
  keywords: models, list models, GET /models, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/models/list-models
  target: aidmc
---

# List models

List the models available through the Meta Model API.

```openapi-schema
method: GET
path: /models
operation:
  operationId: listModels
  tags:
  - Models
  summary: List the available models.
  parameters:
  - name: client
    in: query
    required: false
    schema:
      type: string
    description: Optional client-specific model catalog view.
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ListModelsResponse'
components:
  schemas: {}
page_linked_schemas:
  ListModelsResponse: /docs/api-reference/models/schemas#list-models-response
  Model: /docs/api-reference/models/schemas#model
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.models.list()

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/models",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/models" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/models/schemas -->

For a catalog of available models, capabilities, and context windows, see the [Models](/docs/models) page.