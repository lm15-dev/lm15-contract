---
meta:
  title: Upload a file
  description: API reference for uploading a file with POST /v1/files.
  keywords: files, upload file, POST /files, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/files/upload-file
  target: aidmc
---

# Upload a file

Upload a file for use in inference requests.

```openapi-schema
method: POST
path: /files
operation:
  operationId: createFile
  tags:
  - Files
  summary: Upload a file for batch or user-data use.
  requestBody:
    required: true
    content:
      multipart/form-data:
        schema:
          $ref: '#/components/schemas/CreateFileRequest'
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
  CreateFileRequest: /docs/api-reference/files/schemas#create-file-request
  FileExpiresAfter: /docs/api-reference/files/schemas#file-expires-after
  FileObject: /docs/api-reference/files/schemas#file-object
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

with open("/path/to/image.png", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="user_data",
    )

print(file.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

with open("/path/to/image.png", "rb") as f:
    response = requests.post(
        "https://api.meta.ai/v1/files",
        headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
        files={"file": f},
        data={
            "purpose": "user_data",
        },
    )
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/files" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -F "file=@/path/to/image.png" \
  -F "purpose=user_data"
```

<!-- openapi-schemas-page: /docs/api-reference/files/schemas -->

For supported file types, upload examples, and how to reference files in requests, see the [Files](/docs/file-handling) feature page.