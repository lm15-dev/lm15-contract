> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Cancel Batch

> Cancel an in-progress batch job.

Cancel an in-progress batch task. After cancellation, the task status will change to `cancelling` and then to `cancelled`. Only tasks in `validating`, `in_progress`, or `finalizing` status can be cancelled.

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

    batch: Batch = client.batches.cancel("your_batch_id")
    print(f"Status: {batch.status}")  # cancelling
    ```

    ```bash cURL theme={null}
    curl -X POST ${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/batches/your_batch_id/cancel \
      -H "Authorization: Bearer $MOONSHOT_API_KEY"
    ```

    ```javascript Node.js theme={null}
    const OpenAI = require("openai");

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
    });

    async function main() {
        const batch = await client.batches.cancel("your_batch_id");
        console.log(`Status: ${batch.status}`);  // cancelling
    }

    main();
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Response Fields">
  On success, the endpoint returns a `BatchObject` containing the following fields:

  | Field               | Type            | Description                                                                                                                |
  | ------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------- |
  | `id`                | string          | Unique identifier for the batch task                                                                                       |
  | `object`            | string          | Object type, always `batch`                                                                                                |
  | `endpoint`          | string          | Request endpoint                                                                                                           |
  | `input_file_id`     | string          | Input file ID                                                                                                              |
  | `completion_window` | string          | Processing time window                                                                                                     |
  | `status`            | string          | Current status. After a successful cancellation request this is typically `cancelling`, and eventually becomes `cancelled` |
  | `output_file_id`    | string \| null  | Output file ID for successful results                                                                                      |
  | `error_file_id`     | string \| null  | Error file ID for failed results                                                                                           |
  | `created_at`        | integer         | Creation timestamp (Unix)                                                                                                  |
  | `in_progress_at`    | integer \| null | Execution start timestamp (Unix)                                                                                           |
  | `expires_at`        | integer \| null | Expiration timestamp (Unix)                                                                                                |
  | `finalizing_at`     | integer \| null | Result preparation start timestamp (Unix)                                                                                  |
  | `completed_at`      | integer \| null | Completion timestamp (Unix)                                                                                                |
  | `failed_at`         | integer \| null | Validation failure timestamp (Unix)                                                                                        |
  | `cancelling_at`     | integer \| null | Cancellation request timestamp (Unix)                                                                                      |
  | `cancelled_at`      | integer \| null | Cancellation completion timestamp (Unix)                                                                                   |
  | `request_counts`    | object          | Request counts, including `completed`, `failed`, and `total`                                                               |
  | `metadata`          | object \| null  | Custom metadata                                                                                                            |
</Accordion>

<Warning>
  Only tasks in `validating`, `in_progress`, or `finalizing` status can be cancelled. If the task is already `completed`, `failed`, `expired`, or `cancelled`, calling this endpoint will return a 400 error.
</Warning>

<Note>
  **Common Errors**

  * **400 Bad Request**: The task status does not allow cancellation, or the request parameters are invalid. Please verify the task status before attempting cancellation.
  * **401 Unauthorized**: Invalid or missing API key. Check that `Authorization: Bearer <key>` is correct.
  * **404 Not Found**: The specified `batch_id` does not exist. Verify the ID is correct and the task belongs to your organization.
  * **500 Server Error**: Internal server error. Please retry later; if the issue persists, contact support with the `request_id`.

  For more details, see [Error Codes](/docs/api/errors).
</Note>

For complete usage examples and status transitions, see the [Batch API Guide](/docs/guide/use-batch-api).


## OpenAPI

````yaml POST /v1/batches/{batch_id}/cancel
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
  /v1/batches/{batch_id}/cancel:
    post:
      tags:
        - Batch
      summary: Cancel Batch
      description: >-
        Cancel an in-progress batch task. The status will change to cancelling
        and then to cancelled. Only tasks in validating, in_progress, or
        finalizing status can be cancelled.
      parameters:
        - name: batch_id
          in: path
          required: true
          description: The ID of the batch task
          schema:
            type: string
      responses:
        '200':
          description: The cancelled batch task
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchObject'
        '400':
          description: Bad request - Task status does not allow cancellation
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