---
meta:
  title: Delete a file
  description: API reference for deleting an uploaded file with DELETE /v1/files/{file_id}.
  keywords: files, delete file, DELETE /files, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/files/delete-file
  target: aidmc
---

# Delete a file

Delete a previously uploaded file by its ID.

```openapi-schema
method: DELETE
path: /files/{file_id}
operation:
  operationId: deleteFile
  tags:
  - Files
  summary: Delete an uploaded file.
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
            $ref: '#/components/schemas/DeleteFileResponse'
components:
  schemas: {}
page_linked_schemas:
  DeleteFileResponse: /docs/api-reference/files/schemas#delete-file-response
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.files.delete("file_abc123")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.delete(
    "https://api.meta.ai/v1/files/file_abc123",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X DELETE "https://api.meta.ai/v1/files/file_abc123" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/files/schemas -->

For supported file types and how to reference files in requests, see the [Files](/docs/file-handling) feature page.