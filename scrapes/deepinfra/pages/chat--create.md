> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Openai Chat Completions



## OpenAPI

````yaml https://api.deepinfra.com/openapi.json post /v1/chat/completions
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
  /v1/chat/completions:
    post:
      tags:
        - Chat Completions
      summary: Openai Chat Completions
      operationId: openai_chat_completions_v1_chat_completions_post
      parameters:
        - name: x-deepinfra-source
          in: header
          required: false
          schema:
            anyOf:
              - type: string
              - type: 'null'
            title: X-Deepinfra-Source
        - name: x-deepinfra-service-tier
          in: header
          required: false
          schema:
            anyOf:
              - type: string
              - type: 'null'
            description: >-
              Per-request service tier (`priority` or `flex`) for clients that
              cannot set the `service_tier` body field. The body field wins when
              both are present; unrecognized values ride the default tier.
            title: X-Deepinfra-Service-Tier
          description: >-
            Per-request service tier (`priority` or `flex`) for clients that
            cannot set the `service_tier` body field. The body field wins when
            both are present; unrecognized values ride the default tier.
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
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OpenAIChatCompletionsIn'
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema: {}
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
    OpenAIChatCompletionsIn:
      properties:
        service_tier:
          anyOf:
            - $ref: '#/components/schemas/ServiceTier'
            - type: 'null'
          description: >-
            The service tier used for processing the request. 'priority'
            processes the request with higher priority (premium rate); 'flex'
            processes it at lower priority for a discount, served only when
            spare capacity exists and may be retried/timed out under load. Both
            apply only to models that support the respective tier. For
            compatibility, 'auto' is treated as 'priority' and 'standard_only'
            as 'default'.
        fail_fast:
          type: boolean
          title: Fail Fast
          description: >-
            If true, the request is rejected immediately with HTTP 429 when the
            model has no spare capacity, instead of waiting in the queue.
            Opt-in; the default (false) keeps standard queueing behavior.
          default: false
        models:
          anyOf:
            - items:
                type: string
              type: array
              maxItems: 4
              minItems: 1
            - type: 'null'
          title: Models
          description: >-
            Ordered list of up to 4 fallback models. The request is attempted on
            each model in order: when a model rejects it for lack of capacity
            (HTTP 429 model-busy / flex no-capacity), the next model is tried
            server-side. The first model that accepts serves the request; the
            response's model field and billing reflect that model, at that
            model's pricing. Models before the last are attempted without
            queueing (as if fail_fast were set); the last model honors the
            request's own fail_fast value. When models is set, the model field
            is ignored. Entries must be plain model names (no deploy_id:,
            custom_hostport, or :revision specifiers); duplicate entries are
            ignored, keeping the first occurrence.
        model:
          type: string
          title: Model
          description: model name
          examples:
            - meta-llama/Llama-2-70b-chat-hf
        messages:
          items:
            oneOf:
              - $ref: '#/components/schemas/ChatCompletionToolMessage'
              - $ref: '#/components/schemas/ChatCompletionAssistantMessage'
              - $ref: '#/components/schemas/ChatCompletionUserMessage'
              - $ref: '#/components/schemas/ChatCompletionSystemMessage'
          type: array
          title: Messages
          description: >-
            conversation messages: (user,assistant,tool)*,user including one
            system message anywhere
        stream:
          type: boolean
          title: Stream
          description: whether to stream the output via SSE or return the full response
          default: false
        temperature:
          type: number
          maximum: 2
          minimum: 0
          title: Temperature
          description: >-
            What sampling temperature to use, between 0 and 2. Higher values
            like 0.8 will make the output more random, while lower values like
            0.2 will make it more focused and deterministic
          default: 1
        top_p:
          type: number
          maximum: 1
          exclusiveMinimum: 0
          title: Top P
          description: >-
            An alternative to sampling with temperature, called nucleus
            sampling, where the model considers the results of the tokens with
            top_p probability mass. So 0.1 means only the tokens comprising the
            top 10% probability mass are considered.
          default: 1
        min_p:
          type: number
          maximum: 1
          minimum: 0
          title: Min P
          description: >-
            Float that represents the minimum probability for a token to be
            considered, relative to the probability of the most likely token.
            Must be in [0, 1]. Set to 0 to disable this.
          default: 0
        top_k:
          type: integer
          exclusiveMaximum: 1000
          minimum: 0
          title: Top K
          description: Sample from the best k (number of) tokens. 0 means off
          default: 0
        max_tokens:
          anyOf:
            - type: integer
              maximum: 10000000
              exclusiveMinimum: 0
            - type: 'null'
          title: Max Tokens
          description: >-
            The maximum number of tokens to generate in the chat completion.


            The total length of input tokens and generated tokens is limited by
            the model's context length. If explicitly set to None it will be the
            model's max context length minus input length or 65536, whichever is
            smaller.
        stop:
          anyOf:
            - type: string
            - items:
                type: string
              type: array
            - type: 'null'
          title: Stop
          description: up to 16 sequences where the API will stop generating further tokens
        stop_token_ids:
          anyOf:
            - items:
                type: integer
              type: array
            - type: 'null'
          title: Stop Token Ids
          description: >-
            Up to 16 token IDs where the API will stop generating further
            tokens. Merged with the model's built-in stop tokens. Intended for
            private deployments.
        'n':
          type: integer
          maximum: 4
          minimum: 1
          title: 'N'
          description: number of sequences to return
          default: 1
        presence_penalty:
          type: number
          maximum: 2
          minimum: -2
          title: Presence Penalty
          description: >-
            Positive values penalize new tokens based on whether they appear in
            the text so far, increasing the model's likelihood to talk about new
            topics.
          default: 0
        frequency_penalty:
          type: number
          maximum: 2
          minimum: -2
          title: Frequency Penalty
          description: >-
            Positive values penalize new tokens based on how many times they
            appear in the text so far, increasing the model's likelihood to talk
            about new topics.
          default: 0
        tools:
          anyOf:
            - items:
                $ref: '#/components/schemas/FunctionTool'
              type: array
            - type: 'null'
          title: Tools
          description: >-
            A list of tools the model may call. Currently, only functions are
            supported as a tool.
        tool_choice:
          anyOf:
            - type: string
              enum:
                - none
                - auto
                - required
            - $ref: '#/components/schemas/FunctionTool'
            - type: 'null'
          title: Tool Choice
          description: >-
            Controls which (if any) function is called by the model. none means
            the model will not call a function and instead generates a message.
            auto means the model can pick between generating a message or
            calling a function. required means the model must call a function.
            defined tool means the model must call that specific tool. none is
            the default when no functions are present. auto is the default if
            functions are present.
        response_format:
          anyOf:
            - $ref: '#/components/schemas/TextResponseFormat'
            - $ref: '#/components/schemas/JsonObjectResponseFormat'
            - $ref: '#/components/schemas/JsonSchemaResponseFormat'
            - $ref: '#/components/schemas/RegexResponseFormat'
            - type: 'null'
          title: Response Format
          description: The format of the response. Currently, only json is supported.
        repetition_penalty:
          type: number
          maximum: 5
          minimum: 0.01
          title: Repetition Penalty
          description: >-
            Alternative penalty for repetition, but multiplicative instead of
            additive (> 1 penalize, < 1 encourage)
          default: 1
        user:
          anyOf:
            - type: string
            - type: 'null'
          title: User
          description: >-
            A unique identifier representing your end-user, which can help
            monitor and detect abuse. Avoid sending us any identifying
            information. We recommend hashing user identifiers.
        seed:
          anyOf:
            - type: integer
              exclusiveMaximum: 18446744073709552000
              minimum: -9223372036854776000
            - type: 'null'
          title: Seed
          description: >-
            Seed for random number generator. If not provided, a random seed is
            used. Determinism is not guaranteed.
        logprobs:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Logprobs
          description: >-
            Whether to return log probabilities of the output tokens or not.If
            true, returns the log probabilities of each output token returned in
            the `content` of `message`.
        stream_options:
          anyOf:
            - $ref: '#/components/schemas/StreamOptions'
            - type: 'null'
          description: streaming options
        reasoning_effort:
          anyOf:
            - type: string
              enum:
                - none
                - minimal
                - low
                - medium
                - high
                - xhigh
                - max
            - type: 'null'
          title: Reasoning Effort
          description: >-
            Constrains effort on reasoning for reasoning models. Currently
            supported values are none, minimal, low, medium, high, xhigh, and
            max. Reducing reasoning effort can result in faster responses and
            fewer tokens used on reasoning in a response. Setting to none
            disables reasoning entirely if the model supports.
        reasoning:
          anyOf:
            - $ref: '#/components/schemas/ChatReasoningSettings'
            - type: 'null'
          description: Reasoning configuration.
        prompt_cache_key:
          anyOf:
            - type: string
            - type: 'null'
          title: Prompt Cache Key
          description: >-
            A key to identify prompt cache for reuse across requests. If
            provided, the prompt will be cached and can be reused in subsequent
            requests with the same key.
        prompt_cache_options:
          anyOf:
            - $ref: '#/components/schemas/PromptCacheOptions'
            - type: 'null'
          description: 'Prompt cache options for this request''s prefix, e.g. {"ttl": "1h"}.'
        chat_template_kwargs:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Chat Template Kwargs
          description: Chat template kwargs.
        continue_final_message:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Continue Final Message
          description: >-
            If set, the final assistant message is used as a prefix for the
            model to continue generating from, rather than starting a new turn.
            Only applicable when the last message in the conversation is an
            assistant message.
        ignore_eos:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Ignore Eos
          description: >-
            Keep generating until max_tokens instead of stopping at the
            end-of-sequence token. Only honoured on models tagged with the
            allow_ignore_eos feature flag; ignored otherwise. Intended for
            benchmarking, where a fixed output length is needed.
      type: object
      required:
        - model
        - messages
      title: OpenAIChatCompletionsIn
    HTTPValidationError:
      properties:
        detail:
          items:
            $ref: '#/components/schemas/ValidationError'
          type: array
          title: Detail
      type: object
      title: HTTPValidationError
    ServiceTier:
      type: string
      enum:
        - default
        - priority
        - flex
      title: ServiceTier
    ChatCompletionToolMessage:
      properties:
        cache_control:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Cache Control
          description: Cache control for prompt caching
        role:
          type: string
          const: tool
          title: Role
          description: the role of the author of this message
          default: tool
        content:
          anyOf:
            - type: string
            - items:
                $ref: '#/components/schemas/ChatCompletionContentPartText'
              type: array
          title: Content
          description: the message content
        tool_call_id:
          type: string
          title: Tool Call Id
      type: object
      required:
        - content
        - tool_call_id
      title: ChatCompletionToolMessage
    ChatCompletionAssistantMessage:
      properties:
        cache_control:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Cache Control
          description: Cache control for prompt caching
        role:
          type: string
          const: assistant
          title: Role
          description: the role of the author of this message
          default: assistant
        content:
          anyOf:
            - type: string
            - items:
                $ref: '#/components/schemas/ChatCompletionContentPartText'
              type: array
            - type: 'null'
          title: Content
          description: the message content
        reasoning_content:
          anyOf:
            - type: string
            - type: 'null'
          title: Reasoning Content
          description: the reasoning content
        name:
          anyOf:
            - type: string
            - type: 'null'
          title: Name
        tool_calls:
          anyOf:
            - items:
                $ref: '#/components/schemas/ChatCompletionMessageToolCall'
              type: array
            - type: 'null'
          title: Tool Calls
          description: the tool calls generated by the mode
      type: object
      title: ChatCompletionAssistantMessage
    ChatCompletionUserMessage:
      properties:
        cache_control:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Cache Control
          description: Cache control for prompt caching
        role:
          type: string
          const: user
          title: Role
          description: the role of the author of this message
          default: user
        content:
          anyOf:
            - type: string
            - items:
                anyOf:
                  - $ref: '#/components/schemas/ChatCompletionContentPartText'
                  - $ref: '#/components/schemas/ChatCompletionContentPartImage'
                  - $ref: '#/components/schemas/ChatCompletionContentPartAudio'
                  - $ref: '#/components/schemas/ChatCompletionContentPartVideo'
                  - $ref: '#/components/schemas/ChatCompletionContentPartFile'
              type: array
          title: Content
          description: the message content
        name:
          anyOf:
            - type: string
            - type: 'null'
          title: Name
      type: object
      required:
        - content
      title: ChatCompletionUserMessage
    ChatCompletionSystemMessage:
      properties:
        cache_control:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Cache Control
          description: Cache control for prompt caching
        role:
          type: string
          const: system
          title: Role
          description: the role of the author of this message
          default: system
        content:
          anyOf:
            - type: string
            - items:
                $ref: '#/components/schemas/ChatCompletionContentPartText'
              type: array
          title: Content
          description: the message content
        name:
          anyOf:
            - type: string
            - type: 'null'
          title: Name
      type: object
      required:
        - content
      title: ChatCompletionSystemMessage
    FunctionTool:
      properties:
        cache_control:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Cache Control
          description: Cache control for prompt caching
        type:
          type: string
          title: Type
          default: function
        function:
          $ref: '#/components/schemas/FunctionDefinition'
      type: object
      required:
        - function
      title: FunctionTool
    TextResponseFormat:
      properties:
        type:
          type: string
          const: text
          title: Type
          default: text
      type: object
      title: TextResponseFormat
    JsonObjectResponseFormat:
      properties:
        type:
          type: string
          const: json_object
          title: Type
          default: json_object
      type: object
      title: JsonObjectResponseFormat
    JsonSchemaResponseFormat:
      properties:
        type:
          type: string
          const: json_schema
          title: Type
          default: json_schema
        json_schema:
          $ref: '#/components/schemas/JsonSchema'
          description: JSON schema for structured output when type is 'json_schema'
      type: object
      required:
        - json_schema
      title: JsonSchemaResponseFormat
    RegexResponseFormat:
      properties:
        type:
          type: string
          const: regex
          title: Type
          default: regex
        regex:
          type: string
          title: Regex
          description: Regex pattern for structured output when type is 'regex'
      type: object
      required:
        - regex
      title: RegexResponseFormat
    StreamOptions:
      properties:
        include_usage:
          type: boolean
          title: Include Usage
          description: whether to include usage data
          default: true
        continuous_usage_stats:
          type: boolean
          title: Continuous Usage Stats
          description: >-
            whether to include usage stats continuously with each streaming
            event
          default: false
      type: object
      title: StreamOptions
    ChatReasoningSettings:
      properties:
        effort:
          anyOf:
            - type: string
              enum:
                - none
                - minimal
                - low
                - medium
                - high
                - xhigh
                - max
            - type: 'null'
          title: Effort
          description: >-
            Constrains effort on reasoning for reasoning models. Set to none to
            disable reasoning entirely if the model supports it.
        enabled:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Enabled
          description: Enable or disable reasoning with default parameters.
      type: object
      title: ChatReasoningSettings
    PromptCacheOptions:
      properties:
        mode:
          anyOf:
            - type: string
              enum:
                - explicit
                - implicit
            - type: 'null'
          title: Mode
          description: Prompt caching mode; 'explicit' requests explicit caching.
        ttl:
          anyOf:
            - type: string
              enum:
                - 5m
                - 1h
            - type: 'null'
          title: Ttl
          description: Requested cache retention for this request's prefix.
      type: object
      title: PromptCacheOptions
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
    ChatCompletionContentPartText:
      properties:
        type:
          type: string
          const: text
          title: Type
        text:
          type: string
          title: Text
        prompt_cache_breakpoint:
          anyOf:
            - $ref: '#/components/schemas/PromptCacheBreakpoint'
            - type: 'null'
          description: >-
            Marks the end of the prefix that prompt_cache_options retention
            applies to.
      type: object
      required:
        - type
        - text
      title: ChatCompletionContentPartText
    ChatCompletionMessageToolCall:
      properties:
        id:
          type: string
          title: Id
          description: the id of the tool call
        type:
          type: string
          title: Type
          description: the type of the tool call. only function is supported currently
        function:
          $ref: '#/components/schemas/Function'
          description: the function that the model called
        extra_content:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Extra Content
          description: >-
            provider metadata returned with this tool call; send it back
            unchanged in history
      type: object
      required:
        - id
        - type
        - function
      title: ChatCompletionMessageToolCall
    ChatCompletionContentPartImage:
      properties:
        type:
          type: string
          const: image_url
          title: Type
        image_url:
          $ref: '#/components/schemas/ImageURL'
      type: object
      required:
        - type
        - image_url
      title: ChatCompletionContentPartImage
    ChatCompletionContentPartAudio:
      properties:
        type:
          type: string
          const: input_audio
          title: Type
        input_audio:
          $ref: '#/components/schemas/InputAudio'
      type: object
      required:
        - type
        - input_audio
      title: ChatCompletionContentPartAudio
    ChatCompletionContentPartVideo:
      properties:
        type:
          type: string
          const: video_url
          title: Type
        video_url:
          $ref: '#/components/schemas/VideoURL'
      type: object
      required:
        - type
        - video_url
      title: ChatCompletionContentPartVideo
    ChatCompletionContentPartFile:
      properties:
        type:
          type: string
          const: file
          title: Type
        file:
          $ref: '#/components/schemas/FileData'
      type: object
      required:
        - type
        - file
      title: ChatCompletionContentPartFile
    FunctionDefinition:
      properties:
        name:
          type: string
          title: Name
        description:
          anyOf:
            - type: string
            - type: 'null'
          title: Description
        parameters:
          anyOf:
            - additionalProperties: true
              type: object
            - type: 'null'
          title: Parameters
      type: object
      required:
        - name
      title: FunctionDefinition
    JsonSchema:
      properties:
        name:
          type: string
          title: Name
          description: Name identifier for the JSON schema
        schema:
          additionalProperties: true
          type: object
          title: Schema
          description: The actual JSON schema definition
      type: object
      required:
        - name
        - schema
      title: JsonSchema
    PromptCacheBreakpoint:
      properties:
        mode:
          anyOf:
            - type: string
              const: explicit
            - type: 'null'
          title: Mode
          description: >-
            Breakpoint mode; 'explicit' bounds cache retention to the prompt
            prefix ending at this content part.
      type: object
      title: PromptCacheBreakpoint
    Function:
      properties:
        name:
          type: string
          title: Name
          description: the name of the function to call
        arguments:
          type: string
          title: Arguments
          description: >-
            the function arguments, generated by the model in JSON format. the
            model does not always generate valid JSON, and may hallucinate
            parameters not defined by your function schema
      type: object
      required:
        - name
        - arguments
      title: Function
    ImageURL:
      properties:
        url:
          type: string
          title: Url
        detail:
          type: string
          enum:
            - auto
            - low
            - high
          title: Detail
          default: auto
      type: object
      required:
        - url
      title: ImageURL
    InputAudio:
      properties:
        data:
          type: string
          title: Data
        format:
          type: string
          enum:
            - wav
            - mp3
          title: Format
          default: wav
      type: object
      required:
        - data
      title: InputAudio
    VideoURL:
      properties:
        url:
          type: string
          title: Url
      type: object
      required:
        - url
      title: VideoURL
    FileData:
      properties:
        file_data:
          anyOf:
            - type: string
            - type: 'null'
          title: File Data
        file_id:
          anyOf:
            - type: string
            - type: 'null'
          title: File Id
        filename:
          anyOf:
            - type: string
            - type: 'null'
          title: Filename
      type: object
      title: FileData
  securitySchemes:
    HTTPBearer:
      type: http
      scheme: bearer

````