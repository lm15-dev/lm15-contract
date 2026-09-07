---
meta:
  title: Retrieve a file
  description: API reference for retrieving a file's metadata with GET /v1/files/{file_id}.
  keywords: files, retrieve file, GET /files, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/files/retrieve-file
  target: aidmc
---

# Retrieve a file

Retrieve metadata for a previously uploaded file by its ID.

```openapi-schema
method: GET
path: /files/{file_id}
operation:
  operationId: retrieveFile
  tags:
  - Files
  summary: Retrieve metadata for an uploaded file.
  parameters:
  - in: path
    name: file_id
    required: true
    schema:
      type: string
    description: Identifier of the file to act on.
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/FileObject'
components:
  schemas: {}
page_linked_schemas:
  FileObject: /docs/api-reference/files/schemas#file-object
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.files.retrieve("file_abc123")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/files/file_abc123",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/files/file_abc123" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/files/schemas -->

To download the file's contents, see [Retrieve file content](/docs/api-reference/files/retrieve-file-content).