---
meta:
  title: Retrieve a model
  description: API reference for retrieving a single model's metadata with GET /v1/models/{model}.
  keywords: models, retrieve model, GET /models, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/models/retrieve-model
  target: aidmc
---

# Retrieve a model

Retrieve metadata for a single model by its ID.

```openapi-schema
method: GET
path: /models/{model}
operation:
  operationId: retrieveModel
  tags:
  - Models
  summary: Retrieve metadata for a model.
  parameters:
  - in: path
    name: model
    required: true
    schema:
      type: string
    description: The ID of the model to retrieve.
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Model'
components:
  schemas: {}
page_linked_schemas:
  Model: /docs/api-reference/models/schemas#model
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.models.retrieve("muse-spark-1.3")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/models/muse-spark-1.3",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/models/muse-spark-1.3" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/models/schemas -->

For a catalog of available models, capabilities, and context windows, see the [Models](/docs/models) page.