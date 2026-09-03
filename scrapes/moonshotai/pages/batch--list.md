> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# List Batches

> List the batch jobs of the current account.

List all batch tasks for your organization, with pagination support. Commonly used to review task status or manage batch operations.

<Accordion title="Usage Example">
  <CodeGroup>
    ```python Python theme={null}
    import os
    from openai import OpenAI
    from openai.pagination import SyncCursorPage
    from openai.types import Batch

    client = OpenAI(
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        base_url=os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
    )

    batches: SyncCursorPage[Batch] = client.batches.list(limit=10)
    for batch in batches.data:
        print(f"{batch.id} - {batch.status} ({batch.request_counts.completed}/{batch.request_counts.total})")
    ```

    ```bash cURL theme={null}
    curl "${MOONSHOT_BASE_URL:-https://api.moonshot.ai/v1}/batches?limit=10" \
      -H "Authorization: Bearer $MOONSHOT_API_KEY"
    ```

    ```javascript Node.js theme={null}
    const OpenAI = require("openai");

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: process.env.MOONSHOT_BASE_URL || "https://api.moonshot.ai/v1",
    });

    async function main() {
        const batches = await client.batches.list({ limit: 10 });
        for (const batch of batches.data) {
            console.log(`${batch.id} - ${batch.status} (${batch.request_counts.completed}/${batch.request_counts.total})`);
        }
    }

    main();
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Response Fields">
  The list batches endpoint returns a paginated list object containing the following fields:

  | Field      | Type           | Description                                                                                                                          |
  | ---------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
  | `object`   | string         | Object type, always `"list"`                                                                                                         |
  | `data`     | array\[object] | List of batch tasks, each element is a `BatchObject` with the same fields as [Retrieve Batch](/docs/api/batch-retrieve)                   |
  | `has_more` | boolean        | Whether there are more results. When `true`, pass the last `batch.id` from this page as the `after` parameter to fetch the next page |

  **Response Example**

  ```json theme={null}
  {
      "object": "list",
      "data": [
          {
              "id": "batch_xxx",
              "object": "batch",
              "endpoint": "/v1/chat/completions",
              "input_file_id": "file_xxx",
              "completion_window": "24h",
              "status": "completed",
              "output_file_id": "file_yyy",
              "error_file_id": null,
              "created_at": 1711475054,
              "in_progress_at": 1711475055,
              "expires_at": 1711561454,
              "finalizing_at": 1711475100,
              "completed_at": 1711475110,
              "failed_at": null,
              "cancelling_at": null,
              "cancelled_at": null,
              "request_counts": {
                  "completed": 100,
                  "failed": 0,
                  "total": 100
              },
              "metadata": null
          }
      ],
      "has_more": false
  }
  ```
</Accordion>

<Note>
  For complete usage examples and status transitions, see the [Batch API Guide](/docs/guide/use-batch-api).
</Note>

<Warning>
  When `has_more` is `true`, you must use the `after` parameter for pagination. Pass the last `batch.id` from the current page as the `after` value to retrieve the next page. Omitting `after` will always return the first page.
</Warning>


## OpenAPI

````yaml GET /v1/batches
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
    get:
      tags:
        - Batch
      summary: List Batches
      description: List batch tasks for your organization.
      parameters:
        - name: after
          in: query
          required: false
          description: >-
            Pagination cursor, pass the ID of the last batch from the previous
            page
          schema:
            type: string
        - name: limit
          in: query
          required: false
          description: Number of results per page, default 20
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: List of batch tasks
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BatchListResponse'
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
    BatchListResponse:
      type: object
      properties:
        object:
          type: string
          example: list
        data:
          type: array
          items:
            $ref: '#/components/schemas/BatchObject'
        has_more:
          type: boolean
          description: Whether there are more results
      required:
        - object
        - data
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