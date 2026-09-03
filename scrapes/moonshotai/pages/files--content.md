> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Get File Content

> Retrieve the extracted text content of a file uploaded with purpose file-extract.

<Accordion title="Usage Example">
  <Tabs>
    <Tab title="python">
      ```python theme={null}
      # Note: retrieve_content is marked with a warning in the latest version. Use the line below instead.
      # If you are using an older version, you can use retrieve_content.
      file_content = client.files.content(file_id=file_object.id).text
      ```
    </Tab>

    <Tab title="curl">
      ```bash theme={null}
      curl https://api.moonshot.ai/v1/files/{file_id}/content \
        -H "Authorization: Bearer $MOONSHOT_API_KEY"
      ```
    </Tab>
  </Tabs>
</Accordion>


## OpenAPI

````yaml GET /v1/files/{file_id}/content
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
  /v1/files/{file_id}/content:
    get:
      tags:
        - Files
      summary: Get File Content
      description: >-
        Retrieves extracted text content for files uploaded with purpose
        `file-extract`.
      parameters:
        - name: file_id
          in: path
          required: true
          description: The file identifier
          schema:
            type: string
      responses:
        '200':
          description: Extracted file content
          content:
            text/plain:
              schema:
                type: string
                description: Extracted file content as plain text
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