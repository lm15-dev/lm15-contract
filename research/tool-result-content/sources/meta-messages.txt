---
meta:
  title: Messages schemas
  description: Full schema and model definitions referenced by the Anthropic-compatible Messages API endpoints.
  keywords: Messages API, Anthropic Messages, schemas, models, types, API reference, schema reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/messages/schemas
  target: aidmc
---

# Messages schemas

The full schema and model definitions referenced by the [Messages](/docs/api-reference/messages/create-message) endpoints. Each endpoint page links here for the detailed shape of its request and response objects.

## Schemas

```openapi-schema
kind: schema
name: AnthropicContentBlock
schema:
  type: object
  description: Anthropic Messages content block. Supported block types are `text`, `image`, `video` (Meta extension), `document`, `tool_use`, `tool_result`, `server_tool_use`, `thinking`, and `redacted_thinking`. `cache_control` prompt-cache controls are accepted to improve cache hit rates. Unsupported block types return an `invalid_request_error`.
  properties:
    type:
      type: string
      description: Content block discriminator, such as `text`, `image`, `video`, `document`, `tool_use`, or `tool_result`.
  required:
  - type
  additionalProperties: true
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: '#anthropic-content-block'
```
```openapi-schema
kind: schema
name: AnthropicContextManagementConfig
schema:
  type: object
  description: Anthropic beta context-management config. Known edit types are accepted for compatibility; no server-side context edits are applied.
  properties:
    edits:
      type: array
      items:
        type: object
        additionalProperties: true
  additionalProperties: false
components:
  schemas: {}
page_linked_schemas:
  AnthropicContextManagementConfig: '#anthropic-context-management-config'
```
```openapi-schema
kind: schema
name: AnthropicCountTokensRequest
schema:
  allOf:
  - $ref: '#/components/schemas/AnthropicMessageRequestBase'
  - type: object
    description: Request body for Anthropic-compatible token counting.
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: '#anthropic-content-block'
  AnthropicContextManagementConfig: '#anthropic-context-management-config'
  AnthropicCountTokensRequest: '#anthropic-count-tokens-request'
  AnthropicInputMessage: '#anthropic-input-message'
  AnthropicJsonOutputFormat: '#anthropic-json-output-format'
  AnthropicMessageRequestBase: '#anthropic-message-request-base'
  AnthropicOutputConfig: '#anthropic-output-config'
  AnthropicTool: '#anthropic-tool'
  AnthropicToolChoice: '#anthropic-tool-choice'
```
```openapi-schema
kind: schema
name: AnthropicCountTokensResponse
schema:
  type: object
  properties:
    input_tokens:
      type: integer
      description: Number of input tokens in the supplied Messages request.
  required:
  - input_tokens
components:
  schemas: {}
page_linked_schemas:
  AnthropicCountTokensResponse: '#anthropic-count-tokens-response'
```
```openapi-schema
kind: schema
name: AnthropicInputMessage
schema:
  type: object
  description: Anthropic Messages input message.
  properties:
    role:
      type: string
      enum:
      - user
      - assistant
      - system
      - developer
    content:
      oneOf:
      - type: string
      - type: array
        items:
          $ref: '#/components/schemas/AnthropicContentBlock'
  required:
  - role
  - content
  additionalProperties: false
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: '#anthropic-content-block'
  AnthropicInputMessage: '#anthropic-input-message'
```
```openapi-schema
kind: schema
name: AnthropicJsonOutputFormat
schema:
  type: object
  description: Anthropic JSON structured-output format.
  properties:
    type:
      type: string
      enum:
      - json_schema
    schema:
      type: object
      additionalProperties: true
  required:
  - type
  - schema
  additionalProperties: false
components:
  schemas: {}
page_linked_schemas:
  AnthropicJsonOutputFormat: '#anthropic-json-output-format'
```
```openapi-schema
kind: schema
name: AnthropicMessage
schema:
  type: object
  description: Anthropic-compatible assistant message response.
  properties:
    id:
      type: string
    type:
      type: string
      enum:
      - message
    role:
      type: string
      enum:
      - assistant
    content:
      type: array
      items:
        $ref: '#/components/schemas/AnthropicContentBlock'
    model:
      type: string
    stop_reason:
      type: string
      enum:
      - end_turn
      - max_tokens
      - stop_sequence
      - tool_use
      - pause_turn
      - refusal
    stop_sequence:
      anyOf:
      - type: string
      - type: 'null'
    usage:
      $ref: '#/components/schemas/AnthropicUsage'
  required:
  - id
  - type
  - role
  - content
  - model
  - stop_reason
  - stop_sequence
  - usage
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: '#anthropic-content-block'
  AnthropicMessage: '#anthropic-message'
  AnthropicUsage: '#anthropic-usage'
```
```openapi-schema
kind: schema
name: AnthropicMessageRequest
schema:
  allOf:
  - $ref: '#/components/schemas/AnthropicMessageRequestBase'
  - type: object
    required:
    - max_tokens
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: '#anthropic-content-block'
  AnthropicContextManagementConfig: '#anthropic-context-management-config'
  AnthropicInputMessage: '#anthropic-input-message'
  AnthropicJsonOutputFormat: '#anthropic-json-output-format'
  AnthropicMessageRequest: '#anthropic-message-request'
  AnthropicMessageRequestBase: '#anthropic-message-request-base'
  AnthropicOutputConfig: '#anthropic-output-config'
  AnthropicTool: '#anthropic-tool'
  AnthropicToolChoice: '#anthropic-tool-choice'
```
```openapi-schema
kind: schema
name: AnthropicMessageRequestBase
schema:
  type: object
  description: Anthropic Messages request accepted at `/v1/messages`.
  properties:
    model:
      type: string
    max_tokens:
      type: integer
      minimum: 0
    messages:
      type: array
      minItems: 1
      items:
        $ref: '#/components/schemas/AnthropicInputMessage'
    system:
      oneOf:
      - type: string
      - type: array
        items:
          $ref: '#/components/schemas/AnthropicContentBlock'
    stream:
      type: boolean
      default: false
    tools:
      type: array
      items:
        $ref: '#/components/schemas/AnthropicTool'
    tool_choice:
      $ref: '#/components/schemas/AnthropicToolChoice'
    metadata:
      type: object
      additionalProperties: true
    temperature:
      type: number
      minimum: 0
      maximum: 1
    top_p:
      type: number
      minimum: 0
      maximum: 1
    top_k:
      type: integer
    thinking:
      type: object
      additionalProperties: true
    stop_sequences:
      type: array
      items:
        type: string
    service_tier:
      type: string
    cache_control:
      type: object
      properties:
        type:
          type: string
          enum:
          - ephemeral
        ttl:
          type: string
          enum:
          - 5m
      additionalProperties: false
    context_management:
      anyOf:
      - $ref: '#/components/schemas/AnthropicContextManagementConfig'
      - type: 'null'
    container:
      type: object
      additionalProperties: true
    inference_geo:
      type: string
    output_config:
      $ref: '#/components/schemas/AnthropicOutputConfig'
  required:
  - model
  - messages
  additionalProperties: false
components:
  schemas: {}
page_linked_schemas:
  AnthropicContentBlock: '#anthropic-content-block'
  AnthropicContextManagementConfig: '#anthropic-context-management-config'
  AnthropicInputMessage: '#anthropic-input-message'
  AnthropicJsonOutputFormat: '#anthropic-json-output-format'
  AnthropicMessageRequestBase: '#anthropic-message-request-base'
  AnthropicOutputConfig: '#anthropic-output-config'
  AnthropicTool: '#anthropic-tool'
  AnthropicToolChoice: '#anthropic-tool-choice'
```
```openapi-schema
kind: schema
name: AnthropicOutputConfig
schema:
  type: object
  description: Anthropic output controls. `effort` sets the reasoning effort; `max` selects the strongest available effort.
  properties:
    effort:
      type: string
      enum:
      - low
      - medium
      - high
      - xhigh
      - max
    format:
      $ref: '#/components/schemas/AnthropicJsonOutputFormat'
  additionalProperties: false
components:
  schemas: {}
page_linked_schemas:
  AnthropicJsonOutputFormat: '#anthropic-json-output-format'
  AnthropicOutputConfig: '#anthropic-output-config'
```
```openapi-schema
kind: schema
name: AnthropicStreamEvent
schema:
  type: object
  description: Anthropic Messages server-sent event. Stream event names include `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, and `error`.
  additionalProperties: true
components:
  schemas: {}
page_linked_schemas:
  AnthropicStreamEvent: '#anthropic-stream-event'
```
```openapi-schema
kind: schema
name: AnthropicTool
schema:
  type: object
  description: Anthropic tool definition. Custom (developer) tools are supported; supported hosted tools are accepted, and unsupported hosted tools return an `invalid_request_error`.
  properties:
    type:
      type: string
    name:
      type: string
    description:
      type: string
    input_schema:
      type: object
      additionalProperties: true
  additionalProperties: true
components:
  schemas: {}
page_linked_schemas:
  AnthropicTool: '#anthropic-tool'
```
```openapi-schema
kind: schema
name: AnthropicToolChoice
schema:
  type: object
  properties:
    type:
      type: string
      enum:
      - auto
      - any
      - none
      - tool
    name:
      type: string
    disable_parallel_tool_use:
      type: boolean
  required:
  - type
  additionalProperties: false
components:
  schemas: {}
page_linked_schemas:
  AnthropicToolChoice: '#anthropic-tool-choice'
```
```openapi-schema
kind: schema
name: AnthropicUsage
schema:
  type: object
  properties:
    input_tokens:
      type: integer
    output_tokens:
      type: integer
    cache_creation_input_tokens:
      type: integer
    cache_read_input_tokens:
      type: integer
    output_tokens_details:
      type: object
      properties:
        thinking_tokens:
          type: integer
  required:
  - input_tokens
  - output_tokens
components:
  schemas: {}
page_linked_schemas:
  AnthropicUsage: '#anthropic-usage'
```