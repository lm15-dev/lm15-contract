---
meta:
  title: Files schemas
  description: Full schema and model definitions referenced by the Files API endpoints.
  keywords: files, schemas, models, types, API reference, schema reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/files/schemas
  target: aidmc
---

# Files schemas

The full schema and model definitions referenced by the [Files](/docs/api-reference/files/upload-file) endpoints. Each endpoint page links here for the detailed shape of its request and response objects.

## Schemas

```openapi-schema
kind: schema
name: CreateFileRequest
schema:
  title: Create file request
  description: Request body for uploading a file.
  type: object
  properties:
    file:
      type: string
      format: binary
      description: The file to upload.
    purpose:
      type: string
      description: The intended purpose of the uploaded file. Only `user_data` and `batch` are supported by this endpoint; other values are rejected with a 400 error.
      enum:
      - user_data
      - batch
    expires_after:
      $ref: '#/components/schemas/FileExpiresAfter'
  required:
  - file
  - purpose
components:
  schemas: {}
page_linked_schemas:
  CreateFileRequest: '#create-file-request'
  FileExpiresAfter: '#file-expires-after'
```
```openapi-schema
kind: schema
name: DeleteFileResponse
schema:
  type: object
  properties:
    id:
      type: string
    object:
      type: string
      enum:
      - file
    deleted:
      type: boolean
  required:
  - id
  - object
  - deleted
components:
  schemas: {}
page_linked_schemas:
  DeleteFileResponse: '#delete-file-response'
```
```openapi-schema
kind: schema
name: FileExpiresAfter
schema:
  title: File expiration policy
  description: The expiration policy for an uploaded file.
  type: object
  properties:
    anchor:
      type: string
      description: The timestamp anchor for the expiration policy.
      enum:
      - created_at
    seconds:
      type: integer
      format: int64
      minimum: 3600
      maximum: 2592000
      description: The number of seconds after the anchor time when the file expires.
  required:
  - anchor
  - seconds
components:
  schemas: {}
page_linked_schemas:
  FileExpiresAfter: '#file-expires-after'
```
```openapi-schema
kind: schema
name: FileObject
schema:
  title: File object
  description: Represents a file uploaded to the Files API.
  type: object
  properties:
    id:
      type: string
      description: Identifier for the file. Format is `file-<numeric>`.
    bytes:
      type: integer
      format: int64
      description: Size of the file in bytes.
    created_at:
      type: integer
      format: int64
      description: Unix timestamp (seconds) for when the file was created.
    expires_at:
      anyOf:
      - type: integer
        format: int64
      - type: 'null'
      description: Unix timestamp (seconds) at which the file expires, or null when no expiration was requested. Set to `created_at + expires_after.seconds` when `expires_after` is supplied at upload. Always present in the response — null rather than omitted for non-expiring files.
    filename:
      type: string
      description: Name of the file.
    object:
      type: string
      description: Object type; always `file`.
      enum:
      - file
    purpose:
      type: string
      description: The intended purpose of the file.
      enum:
      - batch
      - fine-tune
      - evals
      - user_data
    status:
      type: string
      deprecated: true
      description: Deprecated. The current status of the file, which can be either `uploaded`, `processed`, or `error`.
      enum:
      - uploaded
      - processed
      - error
    status_details:
      type: string
      deprecated: true
      description: Deprecated. Details about why the file failed validation.
  required:
  - id
  - object
  - bytes
  - created_at
  - expires_at
  - filename
  - purpose
  - status
components:
  schemas: {}
page_linked_schemas:
  FileObject: '#file-object'
```
```openapi-schema
kind: schema
name: ListFilesResponse
schema:
  type: object
  properties:
    object:
      type: string
      example: list
      enum:
      - list
    data:
      type: array
      items:
        $ref: '#/components/schemas/FileObject'
    first_id:
      type: string
      example: file-417829365540192
    last_id:
      type: string
      example: file-417829365538107
    has_more:
      type: boolean
      example: false
  required:
  - object
  - data
  - first_id
  - last_id
  - has_more
components:
  schemas: {}
page_linked_schemas:
  FileObject: '#file-object'
  ListFilesResponse: '#list-files-response'
```