---
meta:
  title: Retrieve file content
  description: API reference for downloading a file's contents with GET /v1/files/{file_id}/content.
  keywords: files, file content, download file, GET /files content, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/files/retrieve-file-content
  target: aidmc
---

# Retrieve file content

Download the raw contents of a previously uploaded file by its ID.

```openapi-schema
method: GET
path: /files/{file_id}/content
operation:
  operationId: downloadFile
  tags:
  - Files
  summary: Download the contents of an uploaded file.
  description: Returns the raw bytes of the uploaded file.
  parameters:
  - in: path
    name: file_id
    required: true
    schema:
      type: string
    description: Identifier of the file to act on.
  responses:
    '200':
      description: The file content as raw bytes.
      content:
        application/octet-stream:
          schema:
            type: string
            format: binary
components:
  schemas: {}
```

```shell title="curl"
curl -X GET "https://api.meta.ai/v1/files/file_abc123/content" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/files/schemas -->

For file metadata, see [Retrieve a file](/docs/api-reference/files/retrieve-file).