> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Openai Models



## OpenAPI

````yaml https://api.deepinfra.com/openapi.json get /v1/models
openapi: 3.1.0
info:
  title: DeepInfra API
  description: >-
    The DeepInfra API provides serverless AI inference, custom model
    deployments, and GPU rentals.
  version: 1.0.0
servers:
  - url: https://api.deepinfra.com
security: []
tags:
  - name: Chat Completions
    description: OpenAI and Anthropic-compatible chat completion endpoints for LLMs.
  - name: Text Completions
    description: OpenAI-compatible text completion endpoints.
  - name: Embeddings
    description: Generate text embeddings for search and RAG.
  - name: Image Generation
    description: Generate, edit, and create variations of images.
  - name: Audio
    description: OpenAI-compatible speech synthesis, transcription, and translation.
  - name: Text to Speech
    description: ElevenLabs-compatible TTS endpoints and voice management.
  - name: Inference
    description: Native DeepInfra inference API for models and deployments.
  - name: Dedicated Models
    description: Deploy and manage private model instances with autoscaling.
  - name: GPU Rentals
    description: Rent dedicated GPU containers.
  - name: Models
    description: Browse, search, and manage AI models.
  - name: Files & Batches
    description: File uploads and batch processing.
  - name: LoRA Adapters
    description: Create, manage, and query LoRA adapter models.
  - name: Agents
    description: Manage agent-framework instances (OpenClaw and friends).
  - name: Sandboxes
    description: Create and manage isolated sandbox environments.
  - name: Account
    description: User profile, team management, rate limits, and GPU pool limits.
  - name: Authentication
    description: API tokens, SSH keys, scoped JWTs, and login flows.
  - name: Billing
    description: Payment methods, usage tracking, and billing.
  - name: Logs & Metrics
    description: Query inference logs, deployment logs, and usage metrics.
  - name: Utilities
    description: Feedback submission and CLI version.
paths:
  /v1/models:
    get:
      tags:
        - Models
      summary: Openai Models
      operationId: openai_models_v1_models_get
      parameters:
        - name: sort_by
          in: query
          required: false
          schema:
            anyOf:
              - type: string
              - type: 'null'
            title: Sort By
        - name: filter
          in: query
          required: false
          schema:
            anyOf:
              - type: string
              - type: 'null'
            title: Filter
        - name: xi-api-key
          in: header
          required: false
          schema:
            anyOf:
              - type: string
              - type: 'null'
            title: Xi-Api-Key
        - name: x-api-key
          in: header
          required: false
          schema:
            anyOf:
              - type: string
              - type: 'null'
            title: X-Api-Key
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OpenAIModelsOut'
        '422':
          description: Validation Error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
      security:
        - HTTPBearer: []
components:
  schemas:
    OpenAIModelsOut:
      properties:
        object:
          type: string
          title: Object
          default: list
        data:
          items:
            $ref: '#/components/schemas/OpenAIModelOut'
          type: array
          title: Data
      type: object
      title: OpenAIModelsOut
    HTTPValidationError:
      properties:
        detail:
          items:
            $ref: '#/components/schemas/ValidationError'
          type: array
          title: Detail
      type: object
      title: HTTPValidationError
    OpenAIModelOut:
      properties:
        id:
          type: string
          title: Id
        object:
          type: string
          title: Object
          default: model
        created:
          type: integer
          title: Created
        owned_by:
          type: string
          title: Owned By
        root:
          type: string
          title: Root
        parent:
          type: 'null'
          title: Parent
        metadata:
          anyOf:
            - $ref: '#/components/schemas/ModelMetadata'
            - type: 'null'
      type: object
      required:
        - id
        - created
        - owned_by
        - root
      title: OpenAIModelOut
    ValidationError:
      properties:
        loc:
          items:
            anyOf:
              - type: string
              - type: integer
          type: array
          title: Location
        msg:
          type: string
          title: Message
        type:
          type: string
          title: Error Type
      type: object
      required:
        - loc
        - msg
        - type
      title: ValidationError
    ModelMetadata:
      properties:
        description:
          type: string
          title: Description
        context_length:
          anyOf:
            - type: integer
            - type: 'null'
          title: Context Length
        max_tokens:
          anyOf:
            - type: integer
            - type: 'null'
          title: Max Tokens
        pricing:
          additionalProperties:
            type: number
          type: object
          title: Pricing
        discount:
          anyOf:
            - type: number
            - type: 'null'
          title: Discount
        tags:
          items:
            type: string
          type: array
          title: Tags
        default_width:
          anyOf:
            - type: integer
            - type: 'null'
          title: Default Width
        default_height:
          anyOf:
            - type: integer
            - type: 'null'
          title: Default Height
        default_iterations:
          anyOf:
            - type: integer
            - type: 'null'
          title: Default Iterations
      type: object
      required:
        - description
        - pricing
        - tags
      title: ModelMetadata
      description: >-
        Per-model metadata exposed by ``/v1/openai/models``.


        Pricing key names are surface-specific:


        - chat / vlm:  {"input_tokens", "output_tokens", "cache_read_tokens"} 
        ($/1M tokens)

        - embed:       {"input_tokens"}                                       
        ($/1M tokens)

        - image-gen:   {"per_image_unit"}                                     
        ($/image at default geometry)

        - video-gen:   {"output_seconds"}                                     
        ($/sec generated)

        - tts:         {"input_characters"}                                   
        ($/1M input chars)

        - stt:         {"input_seconds"}                                      
        ($/sec input audio)


        ``tags`` always carries the surface short alias (e.g. ``'chat'``,

        ``'image-gen'``) and, for chat models, any of ``'vision'``,

        ``'prompt_cache'``, ``'reasoning_effort'``, ``'reasoning'``.
  securitySchemes:
    HTTPBearer:
      type: http
      scheme: bearer

````