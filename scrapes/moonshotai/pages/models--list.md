> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# List Models

> List currently available models and their IDs.

List all currently available models, including model ID, context length, and capability flags. We recommend querying this endpoint before creating a chat completion to verify the target model is available and supports the required capabilities.

<Accordion title="Usage Example">
  <CodeGroup>
    ```python python expandable theme={null}
    import os
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        base_url="https://api.moonshot.ai/v1",
    )

    models = client.models.list()
    print(models.data)
    ```

    ```bash curl expandable theme={null}
    curl https://api.moonshot.ai/v1/models \
        -H "Authorization: Bearer $MOONSHOT_API_KEY"
    ```

    ```javascript node.js expandable theme={null}
    const OpenAI = require("openai");

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: "https://api.moonshot.ai/v1",
    });

    async function main() {
        const models = await client.models.list();
        console.log(models.data);
    }

    main();
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Response Fields">
  The response is an object containing the following fields:

  | Field    | Type           | Description                                    |
  | -------- | -------------- | ---------------------------------------------- |
  | `object` | string         | Object type, always `"list"`                   |
  | `data`   | array\[object] | List of models, each element is a model object |

  Each model object in the `data` array has the following fields:

  | Field                | Type    | Description                                            |
  | -------------------- | ------- | ------------------------------------------------------ |
  | `id`                 | string  | Model ID, e.g. `kimi-k3`                               |
  | `object`             | string  | Object type, always `"model"`                          |
  | `created`            | integer | Unix timestamp when the model was created              |
  | `owned_by`           | string  | Model owner identifier, e.g. `"moonshot"`              |
  | `context_length`     | integer | Maximum context length supported by the model (tokens) |
  | `supports_image_in`  | boolean | Whether the model supports image input                 |
  | `supports_video_in`  | boolean | Whether the model supports video input                 |
  | `supports_reasoning` | boolean | Whether the model supports deep thinking               |
</Accordion>

<Note>
  The model list and capability flags may change as the platform is updated. If you receive a `resource_not_found_error` (404) when creating a chat completion, the model does not exist or your account does not have access to it. Check the `model` parameter spelling and confirm your account tier.
</Note>

<Warning>
  This endpoint requires a valid API Key for authentication. If you receive a 401 error, verify that the `Authorization` header is `Bearer <MOONSHOT_API_KEY>` and that the API Key matches the platform endpoint (Keys from `platform.kimi.ai` and `platform.kimi.com` are not interchangeable).
</Warning>


## OpenAPI

````yaml GET /v1/models
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
  /v1/models:
    get:
      tags:
        - Models
      summary: List Models
      description: List all currently available models.
      responses:
        '200':
          description: Model list
          content:
            application/json:
              schema:
                type: object
                properties:
                  object:
                    type: string
                    example: list
                  data:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          description: Model ID
                          example: kimi-k3
                        object:
                          type: string
                          example: model
                        created:
                          type: integer
                          description: Creation timestamp
                        owned_by:
                          type: string
                          example: moonshot
                        context_length:
                          type: integer
                          description: Maximum context length (tokens)
                        supports_image_in:
                          type: boolean
                          description: Whether the model supports image input
                        supports_video_in:
                          type: boolean
                          description: Whether the model supports video input
                        supports_reasoning:
                          type: boolean
                          description: Whether the model supports deep thinking
        '401':
          description: Unauthorized - Invalid or missing API key
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