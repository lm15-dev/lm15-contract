---
meta:
  title: Images schemas
  description: Full schema and model definitions referenced by the Images API endpoints.
  keywords: images, schemas, models, types, API reference, schema reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/images/schemas
  target: aidmc
---

# Images schemas

The full schema and model definitions referenced by the [Images](/docs/api-reference/images/create-image) endpoints. Each endpoint page links here for the detailed shape of its request and response objects.

## Schemas

```openapi-schema
kind: schema
name: CreateImageEditRequest
schema:
  type: object
  properties:
    image:
      type: string
      format: binary
      description: Image to edit. PNG format.
    prompt:
      type: string
      description: Text description of the edits to apply.
    model:
      type: string
      description: Model ID.
    n:
      type: integer
      default: 1
      minimum: 1
      maximum: 10
      description: 'Number of edited images to generate. Range: 1-10. Defaults to 1.'
    size:
      type: string
      description: Requested image shape as width x height (e.g., '1024x1024'). The values set the aspect ratio; the image is produced at the generator's own resolution, so the returned pixel dimensions will not necessarily match the numbers supplied.
    response_format:
      type: string
      enum:
      - url
      - b64_json
      default: b64_json
      description: 'Format for the edited images. One of `url` or `b64_json`. Default: `b64_json`.'
    reasoning_strength:
      type: string
      enum:
      - low
      - high
      default: high
      description: How much reasoning the image generator applies before producing the edited image. One of `low` or `high`. `low` returns after a single generation pass (no self-refinement); `high` (the default) lets the generator iteratively refine.
    moderation:
      type: string
      description: Moderation level for the safety pipeline. One of `auto`, `low`, or `none`. Supported only on models that accept this parameter; other models reject it with a 400. An unrecognized value is rejected with a 400. `none` additionally requires per-application access.
    stream:
      type: boolean
      nullable: true
      default: false
      description: If true, streams the response as server-sent events. Defaults to false.
    partial_images:
      type: integer
      minimum: 0
      maximum: 3
      default: 0
      description: 'Number of partial images to generate during streaming. Range: 0-3. Accepted but ignored.'
    tool_enablement:
      description: Per-tool controls for the image generator's planner. Omit to keep the default (all tools available).
      $ref: '#/components/schemas/ImageToolEnablement'
  required:
  - prompt
  - model
components:
  schemas: {}
page_linked_schemas:
  CreateImageEditRequest: '#create-image-edit-request'
  ImageToolEnablement: '#image-tool-enablement'
```
```openapi-schema
kind: schema
name: CreateImageRequest
schema:
  type: object
  properties:
    model:
      type: string
      description: Model ID for image generation.
    prompt:
      type: string
      description: Text description of the images to generate.
    n:
      type: integer
      default: 1
      minimum: 1
      maximum: 10
      description: 'Number of images to generate. Range: 1-10. Defaults to 1.'
    size:
      type: string
      description: Requested image shape as width x height (e.g., '1024x1024'). The value is converted into an aspect ratio only; the image is produced at the generator's own fixed output resolution, so the returned pixel dimensions stay constant regardless of the numbers supplied — only the aspect ratio changes.
    response_format:
      type: string
      enum:
      - url
      - b64_json
      default: b64_json
      description: 'Format for returned images. One of: `url`, `b64_json`. Defaults to `b64_json`.'
    moderation:
      type: string
      description: Moderation level for the safety pipeline. One of `auto`, `low`, or `none`. Supported only on models that accept this parameter; other models reject it with a 400. An unrecognized value is rejected with a 400. `none` additionally requires per-application access.
    output_format:
      type: string
      description: Requested file type for the generated images. One of `png`, `jpeg`, or `webp`. Defaults to `webp` when omitted; any other value is rejected.
    reasoning_strength:
      type: string
      enum:
      - low
      - high
      default: high
      description: How much reasoning the image generator applies before producing the image. One of `low` or `high`. `low` returns after a single generation pass (no self-refinement); `high` (the default) lets the generator iteratively refine.
    user:
      type: string
      example: user_9f3a2c1d
      description: A stable end-user identifier that helps detect and mitigate abuse. Use it on the images endpoints; on the Responses and Chat Completions endpoints, use `safety_identifier` instead.
    stream:
      type: boolean
      nullable: true
      default: false
      description: If true, streams the response as server-sent events. Defaults to false.
    tool_enablement:
      description: Per-tool controls for the image generator's planner. Omit to keep the default (all tools available).
      $ref: '#/components/schemas/ImageToolEnablement'
  required:
  - model
  - prompt
components:
  schemas: {}
page_linked_schemas:
  CreateImageRequest: '#create-image-request'
  ImageToolEnablement: '#image-tool-enablement'
```
```openapi-schema
kind: schema
name: EditImageBodyJsonParam
schema:
  type: object
  properties:
    model:
      type: string
      description: Model ID.
    prompt:
      type: string
      description: Text description of the edits to apply.
    images:
      type: array
      minItems: 1
      items:
        $ref: '#/components/schemas/ImageInputItem'
      description: Images to edit.
    n:
      type: integer
      default: 1
      minimum: 1
      maximum: 10
      description: 'Number of edited images to generate. Range: 1-10. Defaults to 1.'
    size:
      type: string
      description: Requested image shape as width x height (e.g., '1024x1024'). The value is converted into an aspect ratio only; the image is produced at the generator's own fixed output resolution, so the returned pixel dimensions stay constant regardless of the numbers supplied — only the aspect ratio changes.
    response_format:
      type: string
      enum:
      - url
      - b64_json
      default: b64_json
      description: 'Format for the edited images. One of `url` or `b64_json`. Default: `b64_json`.'
    output_format:
      type: string
      description: Requested file type for the edited images. One of `png`, `jpeg`, or `webp`. Defaults to `webp` when omitted; any other value is rejected.
    reasoning_strength:
      type: string
      enum:
      - low
      - high
      default: high
      description: How much reasoning the image generator applies before producing the edited image. One of `low` or `high`. `low` returns after a single generation pass (no self-refinement); `high` (the default) lets the generator iteratively refine.
    moderation:
      type: string
      description: Moderation level for the safety pipeline. One of `auto`, `low`, or `none`. Supported only on models that accept this parameter; other models reject it with a 400. An unrecognized value is rejected with a 400. `none` additionally requires per-application access.
    stream:
      type: boolean
      nullable: true
      default: false
      description: If true, streams the response as server-sent events. Defaults to false.
    user:
      type: string
      example: user_9f3a2c1d
      description: A stable end-user identifier that helps detect and mitigate abuse. Use it on the images endpoints; on the Responses and Chat Completions endpoints, use `safety_identifier` instead.
    tool_enablement:
      description: Per-tool controls for the image generator's planner. Omit to keep the default (all tools available).
      $ref: '#/components/schemas/ImageToolEnablement'
  required:
  - model
  - prompt
  - images
components:
  schemas: {}
page_linked_schemas:
  EditImageBodyJsonParam: '#edit-image-body-json-param'
  ImageInputItem: '#image-input-item'
  ImageToolEnablement: '#image-tool-enablement'
```
```openapi-schema
kind: schema
name: ImageEditCompletedEvent
schema:
  type: object
  title: ImageEditCompletedEvent
  description: Image edit completed event.
  properties:
    type:
      type: string
      enum:
      - image_edit.completed
      description: Event type; always `image_edit.completed`.
    b64_json:
      type: string
      description: Base64-encoded edited image data.
    created_at:
      type: integer
      description: Unix timestamp (seconds) for when the event was created.
    output_index:
      type: integer
      format: int64
      description: Zero-based index of the edited image in the response.
    size:
      type: string
      description: Requested image shape as width x height. The values set the aspect ratio; the image is produced at the generator's own resolution, so the returned pixel dimensions will not necessarily match the numbers supplied.
    quality:
      type: string
      description: Quality setting for the edited images. Accepted but ignored.
    background:
      type: string
      description: Background setting for the edited images. Accepted but ignored.
    output_format:
      type: string
      description: Output format for the edited images.
    usage:
      $ref: '#/components/schemas/ImageGenUsage'
      description: Aggregate token usage for the image edit request. Present only on the final completed event.
  required:
  - type
  - b64_json
  - created_at
  - output_index
components:
  schemas: {}
page_linked_schemas:
  ImageEditCompletedEvent: '#image-edit-completed-event'
  ImageGenUsage: '#image-gen-usage'
```
```openapi-schema
kind: schema
name: ImageEditPartialImageEvent
schema:
  type: object
  title: ImageEditPartialImageEvent
  description: Image edit partial image event.
  properties:
    type:
      type: string
      enum:
      - image_edit.partial_image
      description: Event type; always `image_edit.partial_image`.
    b64_json:
      type: string
      description: Base64-encoded partial image data.
    created_at:
      type: integer
      description: Unix timestamp (seconds) for when the event was created.
    size:
      type: string
      description: Requested image shape as width x height. The values set the aspect ratio; the image is produced at the generator's own resolution, so the returned pixel dimensions will not necessarily match the numbers supplied.
    quality:
      type: string
      description: Quality setting for the edited images. Accepted but ignored.
    background:
      type: string
      description: Background setting for the edited images. Accepted but ignored.
    output_format:
      type: string
      description: Output format for the edited images. Accepted but ignored.
    partial_image_index:
      type: integer
      description: Zero-based index for the partial image.
  required:
  - type
  - b64_json
  - created_at
  - partial_image_index
components:
  schemas: {}
page_linked_schemas:
  ImageEditPartialImageEvent: '#image-edit-partial-image-event'
```
```openapi-schema
kind: schema
name: ImageEditStreamEvent
schema:
  oneOf:
  - $ref: '#/components/schemas/ImageEditPartialImageEvent'
  - $ref: '#/components/schemas/ImageEditCompletedEvent'
  discriminator:
    propertyName: type
components:
  schemas: {}
page_linked_schemas:
  ImageEditCompletedEvent: '#image-edit-completed-event'
  ImageEditPartialImageEvent: '#image-edit-partial-image-event'
  ImageEditStreamEvent: '#image-edit-stream-event'
  ImageGenUsage: '#image-gen-usage'
```
```openapi-schema
kind: schema
name: ImageGenCompletedEvent
schema:
  type: object
  title: ImageGenCompletedEvent
  description: Image generation completed event.
  properties:
    type:
      type: string
      enum:
      - image_generation.completed
      description: Event type; always `image_generation.completed`.
    b64_json:
      type: string
      description: Base64-encoded image data.
    created_at:
      type: integer
      description: Unix timestamp (seconds) for when the event was created.
    output_index:
      type: integer
      format: int64
      description: Zero-based index of the generated image in the response.
    size:
      type: string
      description: Requested image shape as width x height. The values set the aspect ratio; the image is produced at the generator's own resolution, so the returned pixel dimensions will not necessarily match the numbers supplied.
    quality:
      type: string
      description: Quality setting for the generated images. Accepted but ignored.
    background:
      type: string
      description: Background setting for the generated images. Accepted but ignored.
    output_format:
      type: string
      description: Output format for the generated images.
    usage:
      $ref: '#/components/schemas/ImageGenUsage'
      description: Aggregate token usage for the image generation request. Present only on the final completed event.
  required:
  - type
  - b64_json
  - created_at
  - output_index
components:
  schemas: {}
page_linked_schemas:
  ImageGenCompletedEvent: '#image-gen-completed-event'
  ImageGenUsage: '#image-gen-usage'
```
```openapi-schema
kind: schema
name: ImageGenPartialImageEvent
schema:
  type: object
  title: ImageGenPartialImageEvent
  description: Image generation partial image event.
  properties:
    type:
      type: string
      enum:
      - image_generation.partial_image
      description: Event type; always `image_generation.partial_image`.
    b64_json:
      type: string
      description: Base64-encoded partial image data.
    created_at:
      type: integer
      description: Unix timestamp (seconds) for when the event was created.
    size:
      type: string
      description: Requested image shape as width x height. The values set the aspect ratio; the image is produced at the generator's own resolution, so the returned pixel dimensions will not necessarily match the numbers supplied.
    quality:
      type: string
      description: Quality setting for the generated images. Accepted but ignored.
    background:
      type: string
      description: Background setting for the generated images. Accepted but ignored.
    output_format:
      type: string
      description: Output format for the generated images. Accepted but ignored.
    partial_image_index:
      type: integer
      description: Zero-based index of the partial image in the streaming sequence.
  required:
  - type
  - b64_json
  - created_at
  - partial_image_index
components:
  schemas: {}
page_linked_schemas:
  ImageGenPartialImageEvent: '#image-gen-partial-image-event'
```
```openapi-schema
kind: schema
name: ImageGenStreamEvent
schema:
  oneOf:
  - $ref: '#/components/schemas/ImageGenPartialImageEvent'
  - $ref: '#/components/schemas/ImageGenCompletedEvent'
  discriminator:
    propertyName: type
components:
  schemas: {}
page_linked_schemas:
  ImageGenCompletedEvent: '#image-gen-completed-event'
  ImageGenPartialImageEvent: '#image-gen-partial-image-event'
  ImageGenStreamEvent: '#image-gen-stream-event'
  ImageGenUsage: '#image-gen-usage'
```
```openapi-schema
kind: schema
name: ImageGenUsage
schema:
  type: object
  properties:
    input_tokens:
      type: integer
      description: Number of input tokens.
    input_tokens_details:
      type: object
      properties:
        image_tokens:
          type: integer
          description: Number of image tokens in the input.
        text_tokens:
          type: integer
          description: Number of text tokens in the input.
      description: Breakdown of input tokens by modality.
    output_tokens:
      type: integer
      description: Number of output tokens.
    total_tokens:
      type: integer
      description: Total number of tokens.
components:
  schemas: {}
page_linked_schemas:
  ImageGenUsage: '#image-gen-usage'
```
```openapi-schema
kind: schema
name: ImageInputItem
schema:
  type: object
  minProperties: 1
  maxProperties: 1
  additionalProperties: false
  properties:
    image_url:
      type: string
      description: Image URL.
    file_id:
      type: string
      description: File ID.
components:
  schemas: {}
page_linked_schemas:
  ImageInputItem: '#image-input-item'
```
```openapi-schema
kind: schema
name: ImageObject
schema:
  type: object
  properties:
    b64_json:
      type: string
      description: Base64-encoded image data.
    url:
      type: string
      description: Image URL.
    revised_prompt:
      type: string
      description: Revised prompt used for the image.
components:
  schemas: {}
page_linked_schemas:
  ImageObject: '#image-object'
```
```openapi-schema
kind: schema
name: ImageToolEnablement
schema:
  type: object
  description: Per-tool controls for the image generator's agentic planner. Omit to keep the default (all tools available); set a field to `false` to disable that tool for the request.
  properties:
    enable_image_search:
      type: boolean
      description: Whether the image generator may search the web for visual references. `false` disables it.
    enable_web_search:
      type: boolean
      description: Whether the image generator may search the web for facts. `false` disables it (also drops the browser tools).
    enable_shell:
      type: boolean
      description: Whether the image generator may run code to build layouts and charts. `false` disables it.
components:
  schemas: {}
page_linked_schemas:
  ImageToolEnablement: '#image-tool-enablement'
```
```openapi-schema
kind: schema
name: ImagesResponse
schema:
  type: object
  properties:
    created:
      type: integer
      description: Unix timestamp (seconds) for when the images were created.
    data:
      type: array
      items:
        $ref: '#/components/schemas/ImageObject'
      description: Array of generated images.
    output_format:
      type: string
      description: File type of the generated images. Echoes the requested `output_format` (`png`, `jpeg`, or `webp`); `webp` when omitted.
    background:
      type: string
      description: Background setting for the generated images. Accepted but ignored.
    usage:
      $ref: '#/components/schemas/ImageGenUsage'
      description: Token usage for the image generation request.
  required:
  - created
  - data
components:
  schemas: {}
page_linked_schemas:
  ImageGenUsage: '#image-gen-usage'
  ImageObject: '#image-object'
  ImagesResponse: '#images-response'
```