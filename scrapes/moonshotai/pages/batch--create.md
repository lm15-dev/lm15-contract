> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Create Batch

> Create a batch job to process requests asynchronously at a lower price.

<Note>
  **Limits:**

  | Limit              | Description                                                  |
  | ------------------ | ------------------------------------------------------------ |
  | File format        | Must have `.jsonl` extension                                 |
  | File size          | Must be non-empty, max 100MB                                 |
  | Organization quota | Up to 1000 batch-purpose files per organization              |
  | Model consistency  | All requests in a batch must use the same model              |
  | `custom_id`        | Must be unique within the file                               |
  | Model access       | The specified model must exist and the user must have access |
</Note>

For complete usage examples, see the [Batch API Guide](/docs/guide/use-batch-api).


## OpenAPI

````yaml POST /v1/batches
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
  /v1/batches:
    post:
      tags:
        - Batch
      summary: Create Batch
      description: >-
        Create a batch task. You need to first upload a JSONL file with
        purpose="batch" via the Files API, then use the returned file_id to
        create the task.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BatchCreateRequest'
      responses:
        '200':
          description: The created batch task
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchObject'
        '400':
          description: Bad request - Invalid parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized - Invalid or missing API key
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
    BatchCreateRequest:
      type: object
      properties:
        input_file_id:
          type: string
          description: >-
            ID of the input file, must be a .jsonl file uploaded with
            purpose="batch"
        endpoint:
          type: string
          description: Request endpoint, currently only /v1/chat/completions is supported
          enum:
            - /v1/chat/completions
        completion_window:
          type: string
          description: >-
            Time window for task processing, supports formats like 12h, 1d, 3d,
            minimum 12h, maximum 7d
        metadata:
          type: object
          description: >-
            Custom metadata, up to 16 key-value pairs, key max 64 chars, value
            max 512 chars
          additionalProperties:
            type: string
            maxLength: 512
      required:
        - input_file_id
        - endpoint
        - completion_window
    BatchObject:
      type: object
      properties:
        id:
          type: string
          description: Unique identifier for the batch task
        object:
          type: string
          description: Object type, always batch
          example: batch
        endpoint:
          type: string
          description: Request endpoint
        input_file_id:
          type: string
          description: Input file ID
        completion_window:
          type: string
          description: Processing time window
        status:
          type: string
          description: >-
            Current status: validating, failed, in_progress, finalizing,
            completed, expired, cancelling, cancelled
          enum:
            - validating
            - failed
            - in_progress
            - finalizing
            - completed
            - expired
            - cancelling
            - cancelled
        output_file_id:
          type:
            - string
            - 'null'
          description: Output file ID for successful results
        error_file_id:
          type:
            - string
            - 'null'
          description: Error file ID for failed results
        created_at:
          type: integer
          description: Creation timestamp (Unix)
        in_progress_at:
          type:
            - integer
            - 'null'
          description: Execution start timestamp (Unix)
        expires_at:
          type:
            - integer
            - 'null'
          description: Expiration timestamp (Unix)
        finalizing_at:
          type:
            - integer
            - 'null'
          description: Result preparation start timestamp (Unix)
        completed_at:
          type:
            - integer
            - 'null'
          description: Completion timestamp (Unix)
        failed_at:
          type:
            - integer
            - 'null'
          description: Validation failure timestamp (Unix)
        cancelling_at:
          type:
            - integer
            - 'null'
          description: Cancellation request timestamp (Unix)
        cancelled_at:
          type:
            - integer
            - 'null'
          description: Cancellation completion timestamp (Unix)
        request_counts:
          $ref: '#/components/schemas/BatchRequestCounts'
        metadata:
          type:
            - object
            - 'null'
          description: Custom metadata
          additionalProperties:
            type: string
      required:
        - id
        - object
        - endpoint
        - input_file_id
        - completion_window
        - status
        - created_at
        - request_counts
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
    BatchRequestCounts:
      type: object
      properties:
        completed:
          type: integer
          description: Number of completed requests
        failed:
          type: integer
          description: Number of failed requests
        total:
          type: integer
          description: Total number of requests
      required:
        - completed
        - failed
        - total
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````