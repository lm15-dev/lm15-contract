---
meta:
  title: List files
  description: API reference for listing uploaded files with GET /v1/files.
  keywords: files, list files, GET /files, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/files/list-files
  target: aidmc
---

# List files

List previously uploaded files.

```openapi-schema
method: GET
path: /files
operation:
  operationId: listFiles
  tags:
  - Files
  summary: List uploaded files.
  parameters:
  - in: query
    name: purpose
    required: false
    schema:
      type: string
    description: Return only files with this purpose.
  - in: query
    name: limit
    required: false
    description: Maximum number of files to return, from 1 to 10,000. Defaults to 10,000.
    schema:
      type: integer
      default: 10000
      minimum: 1
      maximum: 10000
  - in: query
    name: order
    required: false
    description: 'Sort direction by `created_at`: `asc` for oldest first, `desc` for newest first.'
    schema:
      type: string
      default: desc
      enum:
      - asc
      - desc
  - in: query
    name: after
    required: false
    description: A cursor for use in pagination. `after` is a file ID that defines your place in the list.
    schema:
      type: string
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ListFilesResponse'
components:
  schemas: {}
page_linked_schemas:
  FileObject: /docs/api-reference/files/schemas#file-object
  ListFilesResponse: /docs/api-reference/files/schemas#list-files-response
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.files.list()

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/files",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/files" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/files/schemas -->

For supported file types and how to reference files in requests, see the [Files](/docs/file-handling) feature page.