> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Estimate Tokens

> Estimate the token count of your input before sending a request.

The input structure for `estimate-token-count` is almost identical to that of `chat completion`.

<Accordion title="Plain Text Call Example">
  ```bash theme={null}
  curl 'https://api.moonshot.ai/v1/tokenizers/estimate-token-count' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $MOONSHOT_API_KEY" \
    -d '{
      "model": "kimi-k3",
      "messages": [
          {
              "role": "system",
              "content": "You are Kimi, an AI assistant provided by Moonshot AI. You excel in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You refuse to answer any questions involving terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages."
          },
          {
              "role": "user",
              "content": "Hello, my name is Li Lei. What is 1+1?"
          }
      ]
  }'
  ```
</Accordion>

<Accordion title="Vision Call Example">
  ```python theme={null}
  import os
  import base64
  import json
  import requests

  api_key = os.environ.get("MOONSHOT_API_KEY")
  endpoint = "https://api.moonshot.ai/v1/tokenizers/estimate-token-count"
  image_path = "image.png"

  with open(image_path, "rb") as f:
      image_data = f.read()

  # Encode the image to base64 format for the image_url
  image_url = f"data:image/{os.path.splitext(image_path)[1].lstrip('.')};base64,{base64.b64encode(image_data).decode('utf-8')}"

  payload = {
      "model": "kimi-k3",
      "messages": [
          {
              "role": "system",
              "content": "You are Kimi, an AI assistant provided by Moonshot AI. You excel in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You refuse to answer any questions involving terrorism, racism, pornography, or violence. Moonshot AI is a proper noun and should not be translated into other languages."
          },
          {
              "role": "user",
              "content": [
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": image_url,
                      },
                  },
                  {
                      "type": "text",
                      "text": "Please describe the content of the image.",
                  },
              ],
          }
      ]
  }

  response = requests.post(
      endpoint,
      headers={
          "Authorization": f"Bearer {api_key}",
          "Content-Type": "application/json"
      },
      data=json.dumps(payload)
  )

  print(response.json())
  ```
</Accordion>

If there is no `error` field, you can take `data.total_tokens` as the calculation result.


## OpenAPI

````yaml POST /v1/tokenizers/estimate-token-count
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
  /v1/tokenizers/estimate-token-count:
    post:
      tags:
        - Utilities
      summary: Estimate Token Count
      description: >-
        Estimates the number of tokens that would be used for a given set of
        messages and model. The input structure is almost identical to that of
        chat completion.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EstimateTokenRequest'
      responses:
        '200':
          description: Token count estimation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EstimateTokenResponse'
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
    EstimateTokenRequest:
      type: object
      properties:
        model:
          type: string
          description: Model ID
          default: kimi-k3
          enum:
            - kimi-k3
            - kimi-k2.7-code
            - kimi-k2.7-code-highspeed
            - kimi-k2.6
        messages:
          type: array
          description: >-
            A list of messages in the conversation so far. Each element has the
            format {"role": "user", "content": "Hello"}. role supports system,
            user, assistant, or tool. content must not be empty
          items:
            $ref: '#/components/schemas/Message'
      required:
        - model
        - messages
    EstimateTokenResponse:
      type: object
      properties:
        data:
          type: object
          properties:
            total_tokens:
              type: integer
              description: Estimated total number of tokens
              example: 80
          required:
            - total_tokens
      required:
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
    Message:
      type: object
      properties:
        role:
          type: string
          enum:
            - system
            - user
            - assistant
            - tool
          example: user
          description: >-
            The role of the message sender. Supports system, user, assistant,
            tool.
        content:
          oneOf:
            - type: string
            - type: array
              items:
                oneOf:
                  - title: text
                    type: object
                    properties:
                      type:
                        type: string
                        enum:
                          - text
                      text:
                        type: string
                    required:
                      - type
                      - text
                  - title: image_url
                    type: object
                    properties:
                      type:
                        type: string
                        enum:
                          - image_url
                      image_url:
                        oneOf:
                          - type: object
                            properties:
                              url:
                                type: string
                            required:
                              - url
                          - type: string
                    required:
                      - type
                      - image_url
                  - title: video_url
                    type: object
                    properties:
                      type:
                        type: string
                        enum:
                          - video_url
                      video_url:
                        oneOf:
                          - type: object
                            properties:
                              url:
                                type: string
                            required:
                              - url
                          - type: string
                    required:
                      - type
                      - video_url
          example: Hello
          description: >-
            The content of the message. Can be a plain text string, or an array
            of objects with text/image_url/video_url types (for multimodal
            input)
        name:
          type: string
          default: null
          description: Optional name for the message sender
        partial:
          type: boolean
          default: false
          description: >-
            Enable Partial Mode by setting this to true in the last assistant
            message
      required:
        - role
        - content
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````