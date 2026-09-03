> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Messages API

> Call Kimi models with an Anthropic Messages API compatible format, supporting streaming, tool use, image input, thinking, and structured output.

Call Kimi models using an Anthropic Messages API compatible format. If you already use the Anthropic SDK, Claude Code, or similar tools, simply point the base URL at `https://api.moonshot.ai/anthropic` to call Kimi models directly.


## OpenAPI

````yaml POST /anthropic/v1/messages
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
  /anthropic/v1/messages:
    post:
      tags:
        - Messages
      summary: Messages API
      description: >-
        Call Kimi models with an Anthropic Messages API compatible format,
        supporting streaming, tool use, image input, thinking, and structured
        output.
      parameters:
        - name: X-Msh-Request-Nonce
          in: header
          required: false
          description: >-
            A client-generated random nonce (a UUID v4 is recommended). Sending
            it enables Request Signature: the Kimi API returns
            `Msh-Request-Timestamp` and `Msh-Request-Signature` in the response
            headers, which can later be used to prove that the request was
            handled by the Kimi API. Exactly one non-empty header value is
            allowed; if the value is invalid, the request proceeds normally but
            the headers above are not returned. See [Verify Request
            Signature](/api/signatures-verify).
          schema:
            type: string
            minLength: 1
            example: 7d929748-0ae6-41c2-ab5d-a186498ad721
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MessagesRequest'
      responses:
        '200':
          description: Message response
          headers:
            Msh-Request-Timestamp:
              description: >-
                Unix timestamp in milliseconds at which the Kimi API accepted
                this request. Only returned when the request carries a valid
                `X-Msh-Request-Nonce`.
              schema:
                type: integer
                format: int64
                example: 1786338000123
            Msh-Request-Signature:
              description: >-
                Signature token prefixed with `reqsigv1_`, issued by the Kimi
                API over the nonce, timestamp, and the request's `model`; verify
                it with `POST /v1/signatures/verify`. Only returned when the
                request carries a valid `X-Msh-Request-Nonce`.
              schema:
                type: string
                example: reqsigv1_<opaque-token>
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MessagesResponse'
            text/event-stream:
              schema:
                $ref: '#/components/schemas/MessagesStreamEvent'
        '400':
          description: Bad request - Invalid parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MessagesErrorResponse'
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
                $ref: '#/components/schemas/MessagesErrorResponse'
      security:
        - bearerAuth: []
components:
  schemas:
    MessagesRequest:
      title: kimi-k3
      type: object
      properties:
        model:
          type: string
          description: Model ID
          enum:
            - kimi-k3
          default: kimi-k3
        messages:
          type: array
          description: >-
            The conversation messages. If the last message is from the
            assistant, the model continues from that content (Partial Mode).
          items:
            $ref: '#/components/schemas/MessagesMessageParam'
        max_tokens:
          type: integer
          minimum: 1
          description: >-
            Maximum number of tokens to generate, required. If the limit is
            reached before the model finishes, `stop_reason` is `max_tokens`.
        system:
          oneOf:
            - type: string
            - type: array
              items:
                $ref: '#/components/schemas/MessagesTextBlockParam'
          description: System prompt, either a string or an array of text blocks
        stream:
          type: boolean
          default: false
          description: Whether to stream the response as Server-Sent Events, default false
        stop_sequences:
          type: array
          items:
            type: string
          maxItems: 5
          description: >-
            Stop sequences. Generation stops on an exact match; the matched
            sequence itself is not output. Up to 5 entries, each at most 32
            bytes.
        tools:
          type: array
          description: List of tools the model may call
          items:
            $ref: '#/components/schemas/MessagesTool'
        tool_choice:
          $ref: '#/components/schemas/MessagesToolChoice'
        metadata:
          type: object
          properties:
            user_id:
              type: string
              description: >-
                A stable identifier for the end user or session, used to improve
                cache hit rate and for abuse detection. Use a hashed value; do
                not send personally identifiable information. For coding agents,
                pass the session id and keep it constant for the whole session.
        output_config:
          type: object
          description: 'Output configuration: reasoning effort and structured output'
          properties:
            effort:
              type: string
              enum:
                - low
                - high
                - max
              default: max
              description: >-
                Reasoning effort: low, high, or max; default max. Changing the
                level breaks prefix-cache hits, so decide it before the session
                starts.
            format:
              type: object
              description: >-
                Structured output. When set, the model outputs JSON that
                strictly follows the given JSON Schema.
              properties:
                type:
                  type: string
                  enum:
                    - json_schema
                schema:
                  type: object
                  description: The JSON Schema the output must follow
                  additionalProperties: true
              required:
                - type
                - schema
      required:
        - model
        - messages
        - max_tokens
    MessagesResponse:
      type: object
      properties:
        id:
          type: string
          description: Unique identifier of the response
        type:
          type: string
          enum:
            - message
          example: message
        role:
          type: string
          enum:
            - assistant
        model:
          type: string
          description: The model specified in the request
        content:
          type: array
          description: Content blocks, ordered thinking → text → tool_use
          items:
            oneOf:
              - title: thinking
                type: object
                properties:
                  type:
                    type: string
                    enum:
                      - thinking
                  thinking:
                    type: string
                  signature:
                    type: string
                required:
                  - type
                  - thinking
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
              - title: tool_use
                type: object
                properties:
                  type:
                    type: string
                    enum:
                      - tool_use
                  id:
                    type: string
                  name:
                    type: string
                  input:
                    type: object
                    additionalProperties: true
                required:
                  - type
                  - id
                  - name
                  - input
        stop_reason:
          type:
            - string
            - 'null'
          enum:
            - end_turn
            - max_tokens
            - tool_use
            - refusal
            - null
          description: >-
            Stop reason. `end_turn`: finished naturally (including a
            `stop_sequences` match); `max_tokens`: reached the max_tokens limit;
            `tool_use`: the model issued a tool call; `refusal`: content safety
            review was triggered.
        stop_sequence:
          type:
            - string
            - 'null'
          description: The stop sequence that was matched
        usage:
          type: object
          description: Token usage
          properties:
            input_tokens:
              type: integer
              description: Input tokens (excluding cache hits)
            output_tokens:
              type: integer
              description: Output tokens (including reasoning tokens)
            cache_read_input_tokens:
              type: integer
              description: Input tokens served from cache
            cache_creation_input_tokens:
              type: integer
              description: Input tokens written to cache
            output_tokens_details:
              type: object
              properties:
                thinking_tokens:
                  type: integer
                  description: The portion of output tokens used for reasoning
    MessagesStreamEvent:
      oneOf:
        - title: message_start
          type: object
          properties:
            type:
              type: string
              enum:
                - message_start
            message:
              $ref: '#/components/schemas/MessagesResponse'
          required:
            - type
            - message
        - title: content_block_start
          type: object
          properties:
            type:
              type: string
              enum:
                - content_block_start
            index:
              type: integer
            content_block:
              oneOf:
                - title: thinking
                  type: object
                  properties:
                    type:
                      type: string
                      enum:
                        - thinking
                    thinking:
                      type: string
                    signature:
                      type: string
                  required:
                    - type
                    - thinking
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
                - title: tool_use
                  type: object
                  properties:
                    type:
                      type: string
                      enum:
                        - tool_use
                    id:
                      type: string
                    name:
                      type: string
                    input:
                      type: object
                      additionalProperties: true
                  required:
                    - type
                    - id
                    - name
                    - input
          required:
            - type
            - index
            - content_block
        - title: content_block_delta
          type: object
          properties:
            type:
              type: string
              enum:
                - content_block_delta
            index:
              type: integer
            delta:
              type: object
              properties:
                type:
                  type: string
                  enum:
                    - text_delta
                    - thinking_delta
                    - signature_delta
                    - input_json_delta
                text:
                  type: string
                  description: Text fragment for `text_delta`
                thinking:
                  type: string
                  description: Reasoning fragment for `thinking_delta`
                signature:
                  type: string
                  description: Signature for `signature_delta`
                partial_json:
                  type: string
                  description: >-
                    Partial JSON of the tool input for `input_json_delta`;
                    concatenate before parsing
              required:
                - type
          required:
            - type
            - index
            - delta
        - title: content_block_stop
          type: object
          properties:
            type:
              type: string
              enum:
                - content_block_stop
            index:
              type: integer
          required:
            - type
            - index
        - title: message_delta
          type: object
          properties:
            type:
              type: string
              enum:
                - message_delta
            delta:
              type: object
              properties:
                stop_reason:
                  type:
                    - string
                    - 'null'
                  enum:
                    - end_turn
                    - max_tokens
                    - tool_use
                    - refusal
                    - null
                  description: >-
                    Stop reason. `end_turn`: finished naturally (including a
                    `stop_sequences` match); `max_tokens`: reached the
                    max_tokens limit; `tool_use`: the model issued a tool call;
                    `refusal`: content safety review was triggered.
                stop_sequence:
                  type:
                    - string
                    - 'null'
            usage:
              type: object
              properties:
                input_tokens:
                  type: integer
                  description: Input tokens (excluding cache hits)
                output_tokens:
                  type: integer
                  description: Output tokens (including reasoning tokens)
                cache_read_input_tokens:
                  type: integer
                  description: Input tokens served from cache
                cache_creation_input_tokens:
                  type: integer
                  description: Input tokens written to cache
                output_tokens_details:
                  type: object
                  properties:
                    thinking_tokens:
                      type: integer
                      description: The portion of output tokens used for reasoning
          required:
            - type
            - delta
        - title: message_stop
          type: object
          properties:
            type:
              type: string
              enum:
                - message_stop
          required:
            - type
      description: >-
        Streaming events. Each SSE frame's `event` matches `data.type`; the
        order is message_start → (content_block_start → content_block_delta… →
        content_block_stop)… → message_delta → message_stop.
    MessagesErrorResponse:
      type: object
      properties:
        type:
          type: string
          enum:
            - error
        error:
          type: object
          properties:
            type:
              type: string
              description: Error type; see [Errors](/api/errors) for values
            message:
              type: string
              description: Error message describing the cause
          required:
            - type
            - message
        request_id:
          type: string
          description: Request ID; include it when reporting issues
      required:
        - type
        - error
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
    MessagesMessageParam:
      type: object
      properties:
        role:
          type: string
          enum:
            - user
            - assistant
          example: user
          description: >-
            The role of the message. Supports user and assistant. Use the
            top-level `system` field for the system prompt.
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
                        description: Text content
                    required:
                      - type
                      - text
                  - title: image
                    type: object
                    properties:
                      type:
                        type: string
                        enum:
                          - image
                      source:
                        type: object
                        description: >-
                          Image source. When `type` is `base64`, provide both
                          `media_type` and `data`; when `type` is `url`, pass an
                          `ms://<file_id>` file reference in `url`.
                        properties:
                          type:
                            type: string
                            enum:
                              - base64
                              - url
                          media_type:
                            type: string
                            enum:
                              - image/jpeg
                              - image/png
                              - image/gif
                              - image/webp
                            description: Image MIME type, required only when `type=base64`
                          data:
                            type: string
                            description: >-
                              Base64-encoded image content, required only when
                              `type=base64`
                          url:
                            type: string
                            description: >-
                              Reference to an uploaded image by file ID in the
                              form `ms://<file_id>`, required only when
                              `type=url`. See [Upload File](/api/files-upload).
                        required:
                          - type
                    required:
                      - type
                      - source
                  - title: thinking
                    type: object
                    description: >-
                      The model's reasoning. In multi-turn conversations, pass
                      the thinking block from the response (including
                      `signature`) back unchanged inside the assistant message.
                    properties:
                      type:
                        type: string
                        enum:
                          - thinking
                      thinking:
                        type: string
                        description: Reasoning content
                      signature:
                        type: string
                        description: >-
                          Signature of the reasoning content; keep it unchanged
                          when passing back
                    required:
                      - type
                      - thinking
                  - title: tool_use
                    type: object
                    description: >-
                      A tool call issued by the model (appears in assistant
                      messages)
                    properties:
                      type:
                        type: string
                        enum:
                          - tool_use
                      id:
                        type: string
                        description: >-
                          Tool call ID; must match `tool_use_id` when submitting
                          the result
                      name:
                        type: string
                        description: Tool name
                      input:
                        type: object
                        description: Tool input
                        additionalProperties: true
                    required:
                      - type
                      - id
                      - name
                      - input
                  - title: tool_result
                    type: object
                    description: The result of a tool execution (appears in user messages)
                    properties:
                      type:
                        type: string
                        enum:
                          - tool_result
                      tool_use_id:
                        type: string
                        description: The `id` of the corresponding tool_use block
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
                                      description: Text content
                                  required:
                                    - type
                                    - text
                                - title: image
                                  type: object
                                  properties:
                                    type:
                                      type: string
                                      enum:
                                        - image
                                    source:
                                      type: object
                                      description: >-
                                        Image source. When `type` is `base64`,
                                        provide both `media_type` and `data`;
                                        when `type` is `url`, pass an
                                        `ms://<file_id>` file reference in
                                        `url`.
                                      properties:
                                        type:
                                          type: string
                                          enum:
                                            - base64
                                            - url
                                        media_type:
                                          type: string
                                          enum:
                                            - image/jpeg
                                            - image/png
                                            - image/gif
                                            - image/webp
                                          description: >-
                                            Image MIME type, required only when
                                            `type=base64`
                                        data:
                                          type: string
                                          description: >-
                                            Base64-encoded image content, required
                                            only when `type=base64`
                                        url:
                                          type: string
                                          description: >-
                                            Reference to an uploaded image by file
                                            ID in the form `ms://<file_id>`,
                                            required only when `type=url`. See
                                            [Upload File](/api/files-upload).
                                      required:
                                        - type
                                  required:
                                    - type
                                    - source
                        description: >-
                          Tool output, either a string or an array of text /
                          image blocks
                    required:
                      - type
                      - tool_use_id
                      - content
          example: Hello
          description: >-
            Message content. Either a plain string or an array of content blocks
            (text / image / thinking / tool_use / tool_result).
      required:
        - role
        - content
    MessagesTextBlockParam:
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
    MessagesTool:
      type: object
      properties:
        type:
          type: string
          enum:
            - custom
          description: Tool type, may be omitted
        name:
          type: string
          description: >-
            Tool name. Must match the regular expression:
            ^[a-zA-Z_][a-zA-Z0-9-_]{0,127}$
          pattern: ^[a-zA-Z_][a-zA-Z0-9-_]{0,127}$
        description:
          type: string
          description: Description of what the tool does
        input_schema:
          type: object
          description: >-
            JSON Schema for the tool input; the top-level `type` must be
            `object`. Must conform to the [MFJS (Moonshot Flavored JSON Schema)
            specification](https://github.com/MoonshotAI/walle/blob/main/docs/mfjs-spec.md).
          additionalProperties: true
      required:
        - name
        - input_schema
    MessagesToolChoice:
      type: object
      description: >-
        Controls whether the model calls tools. `auto` (default): the model
        decides; `any`: force a call to any tool; `none`: do not call tools.
      properties:
        type:
          type: string
          enum:
            - auto
            - any
            - none
          default: auto
      required:
        - type
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````