> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Delete File

> Delete a specific uploaded file.

Deletes a previously uploaded file. Once deleted, the file no longer counts against your storage quota and cannot be used in chat completions or Batch requests.

<Accordion title="Usage Example">
  <Tabs>
    <Tab title="python">
      ```python showLineNumbers expandable theme={null}
      import os
      from openai import OpenAI

      client = OpenAI(
          api_key=os.environ.get("MOONSHOT_API_KEY"),
          base_url="https://api.moonshot.ai/v1",
      )

      # Delete a specific file
      delete_result = client.files.delete(file_id="file_xxx")
      print(delete_result)
      ```
    </Tab>

    <Tab title="curl">
      ```bash showLineNumbers theme={null}
      curl -X DELETE https://api.moonshot.ai/v1/files/file_xxx \
        -H "Authorization: Bearer $MOONSHOT_API_KEY"
      ```
    </Tab>

    <Tab title="node.js">
      ```js showLineNumbers expandable theme={null}
      const OpenAI = require("openai");

      const client = new OpenAI({
          apiKey: process.env.MOONSHOT_API_KEY,
          baseURL: "https://api.moonshot.ai/v1",
      });

      async function main() {
          const deleteResult = await client.files.delete({
              file_id: "file_xxx",
          });
          console.log(deleteResult);
      }

      main();
      ```
    </Tab>
  </Tabs>
</Accordion>

<Accordion title="Response Fields">
  The delete file endpoint returns a JSON object with the following fields:

  | Field     | Type    | Description                               |
  | --------- | ------- | ----------------------------------------- |
  | `id`      | string  | Deleted file identifier                   |
  | `object`  | string  | Always `"file"`                           |
  | `deleted` | boolean | Whether the file was deleted successfully |

  **Response Example**

  ```json theme={null}
  {
      "id": "file_xxx",
      "object": "file",
      "deleted": true
  }
  ```
</Accordion>

<Note>
  Deletion is permanent. Each user can upload a maximum of 1,000 files. When the total file count reaches the limit, you must delete unused files before uploading new ones.
</Note>

<Warning>
  If the file does not exist or has already been deleted, the endpoint returns a `404` error. Please verify that the `file_id` is correct.
</Warning>


## OpenAPI

````yaml DELETE /v1/files/{file_id}
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
    delete:
      tags:
        - Files
      summary: Delete File
      description: Deletes a previously uploaded file.
      parameters:
        - name: file_id
          in: path
          required: true
          description: The file identifier
          schema:
            type: string
      responses:
        '200':
          description: Deletion result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FileDeleteResponse'
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
    FileDeleteResponse:
      type: object
      properties:
        id:
          type: string
          description: Deleted file identifier
        object:
          type: string
          example: file
        deleted:
          type: boolean
          description: Whether the file was deleted successfully
      required:
        - id
        - object
        - deleted
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