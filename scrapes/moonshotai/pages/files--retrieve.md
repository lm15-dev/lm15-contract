> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Get File Information

> Get metadata for a specific file.

<Accordion title="Usage Example">
  ```python theme={null}
  client.files.retrieve(file_id=file_id)
  # FileObject(
  #     id='file_clg681objj8g9m7n4je0',
  #     bytes=761790,
  #     created_at=1700815879,
  #     filename='xlnet.pdf',
  #     object='file',
  #     purpose='file-extract',
  #     status='ok',
  #     status_details=''
  # )
  ```
</Accordion>


## OpenAPI

````yaml GET /v1/files/{file_id}
openapi: 3.1.0
info:
  title: Moonshot AI API
  version: 1.0.0
  description: API for Moonshot AI / Kimi large language model services
servers:
  - url: https://api.moonshot.ai
    description: Production
security: []
paths:
  /v1/files/{file_id}:
    get:
      tags:
        - Files
      summary: Get File Information
      description: Retrieves metadata for a specific uploaded file.
      parameters:
        - name: file_id
          in: path
          required: true
          description: The file identifier
          schema:
            type: string
      responses:
        '200':
          description: File metadata
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileObject'
        '401':
          description: Unauthorized - Invalid or missing API key
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: File not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      security:
        - bearerAuth: []
components:
  schemas:
    FileObject:
      type: object
      properties:
        id:
          type: string
          description: Unique file identifier
        object:
          type: string
          description: Object type
          example: file
        bytes:
          type: integer
          description: File size in bytes
        created_at:
          type: integer
          description: Unix timestamp when the file was created
        filename:
          type: string
          description: Original file name
        purpose:
          type: string
          description: >-
            Purpose used when uploading the file. file-extract: extract content
            from text-based files (such as pdf, doc, txt); images are not
            supported; image: upload images for vision understanding; video:
            upload videos for video understanding; batch: upload JSONL files for
            batch processing
          enum:
            - file-extract
            - image
            - video
            - batch
        status:
          type: string
          description: Processing status of the file
          example: ready
        status_details:
          type: string
          description: Additional status details when processing fails or returns warnings
      required:
        - id
        - object
        - bytes
        - created_at
        - filename
        - purpose
        - status
    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            message:
              type: string
              description: Error message describing what went wrong
            type:
              type: string
              description: Error type
            code:
              type: string
              description: Error code
          required:
            - message
      required:
        - error
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````