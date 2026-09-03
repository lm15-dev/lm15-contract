> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Retrieve Batch

> Get the details and progress of a specific batch job.

Retrieve the current status, progress statistics, and detailed metadata of a specific batch task. Typically used to poll whether a task has completed after creation.

<Accordion title="Usage Example">
  <CodeGroup>
    ```python Python theme={null}
    import os
    from openai import OpenAI
    from openai.types import Batch

    client = OpenAI(
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
    )

    batch: Batch = client.batches.retrieve("your_batch_id")
    print(f"Status: {batch.status}")
    print(f"Progress: {batch.request_counts.completed}/{batch.request_counts.total}")
    ```

    ```bash cURL theme={null}
    curl ${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/batches/your_batch_id \
      -H "Authorization: Bearer $MOONSHOT_API_KEY"
    ```

    ```javascript Node.js theme={null}
    const OpenAI = require("openai");

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
    });

    async function main() {
        const batch = await client.batches.retrieve("your_batch_id");
        console.log(`Status: ${batch.status}`);
        console.log(`Progress: ${batch.request_counts.completed}/${batch.request_counts.total}`);
    }

    main();
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Response Fields">
  | Field               | Type            | Description                                                                                                            |
  | ------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------- |
  | `id`                | string          | Unique identifier for the batch task                                                                                   |
  | `object`            | string          | Object type, always `batch`                                                                                            |
  | `endpoint`          | string          | Request endpoint                                                                                                       |
  | `input_file_id`     | string          | Input file ID                                                                                                          |
  | `completion_window` | string          | Processing time window                                                                                                 |
  | `status`            | string          | Current status: `validating`, `failed`, `in_progress`, `finalizing`, `completed`, `expired`, `cancelling`, `cancelled` |
  | `output_file_id`    | string \| null  | Output file ID for successful results                                                                                  |
  | `error_file_id`     | string \| null  | Error file ID for failed results                                                                                       |
  | `created_at`        | integer         | Creation timestamp (Unix)                                                                                              |
  | `in_progress_at`    | integer \| null | Execution start timestamp (Unix)                                                                                       |
  | `expires_at`        | integer \| null | Expiration timestamp (Unix)                                                                                            |
  | `finalizing_at`     | integer \| null | Result preparation start timestamp (Unix)                                                                              |
  | `completed_at`      | integer \| null | Completion timestamp (Unix)                                                                                            |
  | `failed_at`         | integer \| null | Validation failure timestamp (Unix)                                                                                    |
  | `cancelling_at`     | integer \| null | Cancellation request timestamp (Unix)                                                                                  |
  | `cancelled_at`      | integer \| null | Cancellation completion timestamp (Unix)                                                                               |
  | `request_counts`    | object          | Request count statistics, containing `completed`, `failed`, and `total`                                                |
  | `metadata`          | object \| null  | Custom metadata                                                                                                        |
</Accordion>

<Note>
  For complete usage examples and polling scripts, see the [Batch API Guide](/docs/guide/use-batch-api).
</Note>

<Warning>
  When `status` is `completed`, `output_file_id` contains the results file ID. When `status` is `failed`, check `error_file_id` for error details. If the specified `batch_id` does not exist, the API returns a `404` error (`resource_not_found_error`).
</Warning>


## OpenAPI

````yaml GET /v1/batches/{batch_id}
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
  /v1/batches/{batch_id}:
    get:
      tags:
        - Batch
      summary: Retrieve Batch
      description: Retrieve the status and details of a specific batch task.
      parameters:
        - name: batch_id
          in: path
          required: true
          description: The ID of the batch task
          schema:
            type: string
      responses:
        '200':
          description: Batch task details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchObject'
        '401':
          description: Unauthorized - Invalid or missing API key
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: Batch task not found
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