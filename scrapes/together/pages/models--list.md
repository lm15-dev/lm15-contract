> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# List all models

> Lists all of Together's open-source models and metadata including pricing, chat template, and context.



## OpenAPI

````yaml openapi.yaml GET /models
openapi: 3.1.0
info:
  title: Together APIs
  description: The Together REST API. See https://docs.together.ai for more details.
  version: 2.0.0
  termsOfService: https://www.together.ai/terms-of-service
  contact:
    name: Together Support
    url: https://www.together.ai/contact
  license:
    name: MIT
    url: https://github.com/togethercomputer/openapi/blob/main/LICENSE
servers:
  - url: https://api.together.ai/v1
    description: Default environment for APIs
  - url: https://api-inference.together.ai/v2
    description: Optimized environment for inference
security:
  - bearerAuth: []
paths:
  /models:
    get:
      tags:
        - Models
      summary: List all models
      description: >-
        Lists all of Together's open-source models and metadata including
        pricing, chat template, and context.
      operationId: models
      parameters:
        - name: dedicated
          in: query
          schema:
            description: Filter models to only return dedicated models
            type: boolean
      responses:
        '200':
          description: '200'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ModelInfoList'
        '400':
          description: BadRequest
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorData'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorData'
        '404':
          description: NotFound
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorData'
        '429':
          description: RateLimit
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorData'
        '504':
          description: Timeout
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorData'
      deprecated: false
      x-codeSamples:
        - lang: Python
          label: Together AI SDK (Python)
          source: |
            from together import Together
            import os

            client = Together(
                api_key=os.environ.get("TOGETHER_API_KEY"),
            )

            models = client.models.list()

            for model in models:
                print(model.id)
        - lang: TypeScript
          label: Together AI SDK (TypeScript)
          source: |
            import Together from "together-ai";

            const client = new Together({
              apiKey: process.env.TOGETHER_API_KEY,
            });

            const models = await client.models.list();

            for (const model of models) {
              console.log(model.id);
            }
        - lang: JavaScript
          label: Together AI SDK (JavaScript)
          source: |
            import Together from "together-ai";

            const client = new Together({
              apiKey: process.env.TOGETHER_API_KEY,
            });

            const models = await client.models.list();

            for (const model of models) {
              console.log(model.id);
            }
        - lang: Shell
          label: cURL
          source: |
            curl "https://api.together.ai/v1/models" \
                 -H "Authorization: Bearer $TOGETHER_API_KEY" \
                 -H "Content-Type: application/json"
components:
  schemas:
    ModelInfoList:
      type: array
      items:
        $ref: '#/components/schemas/ModelInfo'
    ErrorData:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          properties:
            message:
              type: string
              nullable: false
            type:
              type: string
              nullable: false
            param:
              type: string
              nullable: true
              default: null
            code:
              type: string
              nullable: true
              default: null
          required:
            - type
            - message
    ModelInfo:
      type: object
      required:
        - id
        - object
        - created
        - type
      properties:
        id:
          type: string
          example: Austism/chronos-hermes-13b
        object:
          description: The object type, which is always `model`.
          const: model
        created:
          type: integer
          example: 1692896905
        type:
          enum:
            - chat
            - language
            - code
            - image
            - embedding
            - moderation
            - rerank
          example: chat
        display_name:
          type: string
          example: Chronos Hermes (13B)
        organization:
          type: string
          example: Austism
        link:
          type: string
        license:
          type: string
          example: other
        context_length:
          type: integer
          example: 2048
        pricing:
          $ref: '#/components/schemas/Pricing'
    Pricing:
      type: object
      required:
        - hourly
        - input
        - output
        - base
        - finetune
      properties:
        base:
          type: number
          example: 0
        finetune:
          type: number
          example: 0
        hourly:
          type: number
          example: 0
        input:
          type: number
          example: 0.3
        output:
          type: number
          example: 0.3
        cached_input:
          type: number
          example: 0.2
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      x-bearer-format: bearer
      x-default: default

````