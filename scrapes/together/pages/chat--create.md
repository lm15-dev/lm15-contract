> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Create chat completion

> Generate a model response for a given chat conversation. Supports single queries and multi-turn conversations with system, user, and assistant messages.



## OpenAPI

````yaml openapi.yaml POST /chat/completions
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
  /chat/completions:
    post:
      tags:
        - Chat
      summary: Create chat completion
      description: >-
        Generate a model response for a given chat conversation. Supports single
        queries and multi-turn conversations with system, user, and assistant
        messages.
      operationId: chat-completions
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatCompletionRequest'
      responses:
        '200':
          description: '200'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatCompletionResponse'
            text/event-stream:
              schema:
                $ref: '#/components/schemas/ChatCompletionStream'
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
        '503':
          description: Overloaded
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

            response = client.chat.completions.create(
                model="Qwen/Qwen3.5-9B",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What are some fun things to do in New York?"},
                ],
                reasoning={"enabled": False}
            )
        - lang: TypeScript
          label: Together AI SDK (TypeScript)
          source: |
            import Together from "together-ai";

            const client = new Together({
              apiKey: process.env.TOGETHER_API_KEY,
            });

            const response = await client.chat.completions.create({
              model: "Qwen/Qwen3.5-9B",
              messages: [
                { role: "system", content: "You are a helpful assistant." },
                { role: "user", "content": "What are some fun things to do in New York?" },
              ],
              reasoning: { enabled: false },
            });

            console.log(response.choices[0].message?.content);
        - lang: JavaScript
          label: Together AI SDK (JavaScript)
          source: |
            import Together from "together-ai";

            const client = new Together({
              apiKey: process.env.TOGETHER_API_KEY,
            });

            const response = await client.chat.completions.create({
              model: "Qwen/Qwen3.5-9B",
              messages: [
                { role: "system", content: "You are a helpful assistant." },
                { role: "user", "content": "What are some fun things to do in New York?" },
              ],
              reasoning: { enabled: false },
            });

            console.log(response.choices[0].message?.content);
        - lang: Shell
          label: cURL
          source: |
            curl -X POST "https://api.together.ai/v1/chat/completions" \
                 -H "Authorization: Bearer $TOGETHER_API_KEY" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "model": "Qwen/Qwen3.5-9B",
                   "messages": [
                     {"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": "What are some fun things to do in New York?"}
                   ],
                   "reasoning": {"enabled": false}
                 }'
components:
  schemas:
    ChatCompletionRequest:
      type: object
      required:
        - model
        - messages
      properties:
        messages:
          type: array
          description: A list of messages comprising the conversation so far.
          items:
            $ref: '#/components/schemas/ChatCompletionMessageParam'
        model:
          type: string
          description: >
            The name of the model to query.<br> <br> [See all of Together AI's
            chat
            models](https://docs.together.ai/docs/serverless-models#chat-models)
        max_tokens:
          type: integer
          description: The maximum number of tokens to generate.
        stop:
          type: array
          description: >-
            A list of string sequences that truncate (stop) inference text
            output. For example, "</s>" stops generation as soon as the model
            generates the given token.
          items:
            type: string
        temperature:
          type: number
          description: >-
            A decimal number from 0-1 that determines the degree of randomness
            in the response. A temperature less than 1 favors more correctness
            and is appropriate for question answering or summarization. A value
            closer to 1 introduces more randomness in the output.
        top_p:
          type: number
          description: >-
            A percentage (also called the nucleus parameter) that's used to
            dynamically adjust the number of choices for each predicted token
            based on the cumulative probabilities. It specifies a probability
            threshold below which all less likely tokens are filtered out. This
            technique helps maintain diversity and generate more fluent and
            natural-sounding text.
        top_k:
          type: integer
          description: >-
            An integer that's used to limit the number of choices for the next
            predicted word or token. It specifies the maximum number of tokens
            to consider at each step, based on their probability of occurrence.
            This technique helps to speed up the generation process and can
            improve the quality of the generated text by focusing on the most
            likely options.
        context_length_exceeded_behavior:
          type: string
          enum:
            - truncate
            - error
          default: error
          description: >-
            Defines the behavior of the API when max_tokens exceed the maximum
            context length of the model. When set to 'error', the API returns
            400 with an appropriate error message. When set to 'truncate',
            overrides max_tokens with the maximum context length of the model.
        repetition_penalty:
          type: number
          description: >-
            A number that controls the diversity of generated text by reducing
            the likelihood of repeated sequences. Higher values decrease
            repetition.
        stream:
          type: boolean
          description: >-
            If true, stream tokens as Server-Sent Events as the model generates
            them instead of waiting for the full model response. The stream
            terminates with `data: [DONE]`. If false, return a single JSON
            object containing the results.
        logprobs:
          type: integer
          minimum: 0
          maximum: 20
          description: >-
            An integer between 0 and 20 of the top k tokens to return log
            probabilities for at each generation step, instead of only the
            sampled token. Log probabilities help assess model confidence in
            token predictions.
        echo:
          type: boolean
          description: >-
            If true, the response contains the prompt. Can be used with
            `logprobs` to return prompt logprobs.
        'n':
          type: integer
          description: The number of completions to generate for each prompt.
          minimum: 1
          maximum: 128
        min_p:
          type: number
          description: >-
            A number between 0 and 1 that can be used as an alternative to top_p
            and top-k.
        presence_penalty:
          type: number
          description: >-
            A number between -2.0 and 2.0 where a positive value increases the
            likelihood of a model talking about new topics.
        frequency_penalty:
          type: number
          description: >-
            A number between -2.0 and 2.0 where a positive value decreases the
            likelihood of repeating tokens that have already been mentioned.
        logit_bias:
          type: object
          additionalProperties:
            type: number
          description: >-
            Adjusts the likelihood of specific tokens appearing in the generated
            output.
          example:
            '105': 21.4
            '1024': -10.5
        seed:
          type: integer
          description: Seed value for reproducibility.
          example: 42
        function_call:
          oneOf:
            - type: string
              enum:
                - none
                - auto
            - type: object
              required:
                - name
              properties:
                name:
                  type: string
        response_format:
          description: >
            An object specifying the format that the model must output.


            Setting to `{ "type": "json_schema", "json_schema": {...} }` enables

            Structured Outputs which ensures the model will match your supplied
            JSON

            schema. Learn more in the [Structured Outputs

            guide](https://docs.together.ai/docs/json-mode).


            Setting to `{ "type": "json_object" }` enables the older JSON mode,
            which

            ensures the message the model generates is valid JSON. Using
            `json_schema`

            is preferred for models that support it.
          discriminator:
            propertyName: type
          anyOf:
            - $ref: '#/components/schemas/ResponseFormatText'
            - $ref: '#/components/schemas/ResponseFormatJsonSchema'
            - $ref: '#/components/schemas/ResponseFormatJsonObject'
        tools:
          type: array
          description: >-
            A list of tools the model may call. Currently, only functions are
            supported as a tool. Use this to provide a list of functions the
            model may generate JSON inputs for.
          items:
            $ref: '#/components/schemas/ToolsPart'
        tool_choice:
          description: >-
            Controls which (if any) function is called by the model. By default
            uses `auto`, which lets the model pick between generating a message
            or calling a function.
          oneOf:
            - type: string
              example: tool_name
            - $ref: '#/components/schemas/ToolChoice'
        compliance:
          const: hipaa
        chat_template_kwargs:
          description: Additional configuration to pass to model engine.
          type: object
          additional_properties: true
        safety_model:
          type: string
          description: >-
            The name of the moderation model used to validate tokens. Choose
            from the available moderation models found
            [here](https://docs.together.ai/docs/inference-models#moderation-models).
          example: safety_model_name
        reasoning_effort:
          type: string
          enum:
            - low
            - medium
            - high
          description: >-
            Controls the level of reasoning effort the model should apply when
            generating responses. Higher values may result in more thoughtful
            and detailed responses but may take longer to generate.
          example: medium
        reasoning:
          description: >-
            For models that support toggling reasoning functionality, this
            object can be used to control that functionality.
          type: object
          properties:
            enabled:
              type: boolean
    ChatCompletionResponse:
      type: object
      properties:
        id:
          type: string
        choices:
          $ref: '#/components/schemas/ChatCompletionChoicesData'
        usage:
          $ref: '#/components/schemas/UsageData'
        created:
          type: integer
        model:
          type: string
        prompt:
          $ref: '#/components/schemas/PromptPart'
          description: >-
            When `echo` is true, the prompt is included in the response.
            Additionally, when `logprobs` is also provided, log probability
            information is provided on the prompt.
        object:
          description: The object type, which is always `chat.completion`.
          const: chat.completion
        warnings:
          type: array
          items:
            $ref: '#/components/schemas/InferenceWarning'
      required:
        - choices
        - id
        - created
        - model
        - object
        - prompt
    ChatCompletionStream:
      oneOf:
        - $ref: '#/components/schemas/ChatCompletionEvent'
        - $ref: '#/components/schemas/StreamSentinel'
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
    ChatCompletionMessageParam:
      oneOf:
        - $ref: '#/components/schemas/ChatCompletionSystemMessageParam'
        - $ref: '#/components/schemas/ChatCompletionUserMessageParam'
        - $ref: '#/components/schemas/ChatCompletionAssistantMessageParam'
        - $ref: '#/components/schemas/ChatCompletionToolMessageParam'
        - $ref: '#/components/schemas/ChatCompletionFunctionMessageParam'
    ResponseFormatText:
      type: object
      title: Text
      description: |
        Default response format. Used to generate text responses.
      properties:
        type:
          type: string
          description: The type of response format being defined. Always `text`.
          enum:
            - text
          x-stainless-const: true
      required:
        - type
    ResponseFormatJsonSchema:
      type: object
      title: JSON schema
      description: >
        JSON Schema response format. Used to generate structured JSON responses.

        Learn more about [Structured
        Outputs](https://docs.together.ai/docs/json-mode).
      properties:
        type:
          type: string
          description: The type of response format being defined. Always `json_schema`.
          enum:
            - json_schema
          x-stainless-const: true
        json_schema:
          type: object
          title: JSON schema
          description: |
            Structured Outputs configuration options, including a JSON Schema.
          properties:
            description:
              type: string
              description: >
                A description of what the response format is for, used by the
                model to

                determine how to respond in the format.
            name:
              type: string
              description: >
                The name of the response format. Must be a-z, A-Z, 0-9, or
                contain

                underscores and dashes, with a maximum length of 64.
            schema:
              $ref: '#/components/schemas/ResponseFormatJsonSchemaSchema'
            strict:
              anyOf:
                - type: boolean
                  default: false
                  description: >
                    Whether to enable strict schema adherence when generating
                    the output.

                    If set to true, the model will always follow the exact
                    schema defined

                    in the `schema` field. Only a subset of JSON Schema is
                    supported when

                    `strict` is `true`. To learn more, read the [Structured
                    Outputs

                    guide](https://docs.together.ai/docs/json-mode).
                - type: 'null'
          required:
            - name
      required:
        - type
        - json_schema
    ResponseFormatJsonObject:
      type: object
      title: JSON object
      description: >
        JSON object response format. An older method of generating JSON
        responses.

        Using `json_schema` is recommended for models that support it. Note that
        the

        model will not generate JSON without a system or user message
        instructing it

        to do so.
      properties:
        type:
          type: string
          description: The type of response format being defined. Always `json_object`.
          enum:
            - json_object
          x-stainless-const: true
      required:
        - type
    ToolsPart:
      type: object
      properties:
        type:
          type: string
          example: tool_type
        function:
          type: object
          properties:
            description:
              type: string
              example: A description of the function.
            name:
              type: string
              example: function_name
            parameters:
              type: object
              additionalProperties: true
              description: A map of parameter names to their values.
    ToolChoice:
      type: object
      required:
        - id
        - type
        - function
        - index
      properties:
        index:
          type: number
        id:
          type: string
        type:
          type: string
          enum:
            - function
        function:
          type: object
          required:
            - name
            - arguments
          properties:
            name:
              type: string
              example: function_name
            arguments:
              type: string
    ChatCompletionChoicesData:
      type: array
      items:
        type: object
        properties:
          text:
            type: string
          index:
            type: integer
          seed:
            type: integer
          finish_reason:
            $ref: '#/components/schemas/FinishReason'
          message:
            $ref: '#/components/schemas/ChatCompletionMessage'
          logprobs:
            allOf:
              - nullable: true
              - $ref: '#/components/schemas/LogprobsPart'
          top_logprobs:
            $ref: '#/components/schemas/TopLogprobs'
    UsageData:
      type: object
      properties:
        prompt_tokens:
          type: integer
        completion_tokens:
          type: integer
        total_tokens:
          type: integer
      required:
        - prompt_tokens
        - completion_tokens
        - total_tokens
      nullable: true
    PromptPart:
      type: array
      items:
        type: object
        properties:
          text:
            type: string
            example: <s>[INST] What is the capital of France? [/INST]
          logprobs:
            $ref: '#/components/schemas/LogprobsPart'
    InferenceWarning:
      type: object
      required:
        - message
      properties:
        message:
          type: string
    ChatCompletionEvent:
      type: object
      required:
        - data
      properties:
        data:
          $ref: '#/components/schemas/ChatCompletionChunk'
    StreamSentinel:
      type: object
      required:
        - data
      properties:
        data:
          title: stream_signal
          type: string
          enum:
            - '[DONE]'
    ChatCompletionSystemMessageParam:
      type: object
      required:
        - content
        - role
      properties:
        content:
          type: string
        role:
          type: string
          enum:
            - system
        name:
          type: string
    ChatCompletionUserMessageParam:
      type: object
      required:
        - content
        - role
      properties:
        content:
          $ref: '#/components/schemas/ChatCompletionUserMessageContent'
        role:
          type: string
          enum:
            - user
        name:
          type: string
    ChatCompletionAssistantMessageParam:
      type: object
      required:
        - role
      properties:
        content:
          type: string
          nullable: true
        role:
          type: string
          enum:
            - assistant
        name:
          type: string
        tool_calls:
          type: array
          items:
            $ref: '#/components/schemas/ToolChoice'
        function_call:
          type: object
          deprecated: true
          required:
            - arguments
            - name
          properties:
            arguments:
              type: string
            name:
              type: string
        reasoning:
          type: string
          nullable: true
        reasoning_content:
          type: string
          nullable: true
    ChatCompletionToolMessageParam:
      type: object
      properties:
        name:
          type: string
        role:
          type: string
          enum:
            - tool
        content:
          type: string
        tool_call_id:
          type: string
      required:
        - role
        - content
        - tool_call_id
    ChatCompletionFunctionMessageParam:
      type: object
      deprecated: true
      required:
        - content
        - role
        - name
      properties:
        role:
          type: string
          enum:
            - function
        content:
          type: string
        name:
          type: string
    ResponseFormatJsonSchemaSchema:
      type: object
      title: JSON schema
      description: |
        The schema for the response format, described as a JSON Schema object.
        Learn how to build JSON schemas [here](https://json-schema.org/).
      additionalProperties: true
    FinishReason:
      type: string
      enum:
        - stop
        - eos
        - length
        - tool_calls
        - function_call
    ChatCompletionMessage:
      type: object
      required:
        - role
        - content
      properties:
        content:
          type: string
          nullable: true
        role:
          type: string
          enum:
            - assistant
        tool_calls:
          type: array
          items:
            $ref: '#/components/schemas/ToolChoice'
        function_call:
          type: object
          deprecated: true
          required:
            - arguments
            - name
          properties:
            arguments:
              type: string
            name:
              type: string
        reasoning:
          type: string
          nullable: true
        reasoning_content:
          type: string
          nullable: true
    LogprobsPart:
      type: object
      properties:
        token_ids:
          type: array
          items:
            type: number
          description: List of token IDs corresponding to the logprobs
        tokens:
          type: array
          items:
            type: string
          description: List of token strings
        token_logprobs:
          type: array
          items:
            type: number
          description: List of token log probabilities
        top_logprobs:
          $ref: '#/components/schemas/TopLogprobs'
    TopLogprobs:
      description: Top log probabilities for the tokens.
      type: object
      additionalProperties:
        type: number
    ChatCompletionChunk:
      type: object
      required:
        - id
        - object
        - created
        - choices
        - model
      properties:
        id:
          type: string
        object:
          description: The object type, which is always `chat.completion.chunk`.
          const: chat.completion.chunk
        created:
          type: integer
        system_fingerprint:
          type: string
        model:
          type: string
          example: mistralai/Mixtral-8x7B-Instruct-v0.1
        choices:
          title: ChatCompletionChoices
          type: array
          items:
            type: object
            required:
              - index
              - delta
              - finish_reason
            properties:
              index:
                type: integer
              finish_reason:
                $ref: '#/components/schemas/FinishReason'
                nullable: true
              logprobs:
                type: number
                nullable: true
              top_logprobs:
                $ref: '#/components/schemas/TopLogprobs'
              seed:
                type: integer
                nullable: true
              delta:
                title: ChatCompletionChoiceDelta
                type: object
                required:
                  - role
                properties:
                  token_id:
                    type: integer
                  role:
                    type: string
                    enum:
                      - system
                      - user
                      - assistant
                      - function
                      - tool
                  content:
                    type: string
                    nullable: true
                  reasoning:
                    type: string
                    nullable: true
                  reasoning_content:
                    type: string
                    nullable: true
                  tool_calls:
                    type: array
                    items:
                      $ref: '#/components/schemas/ToolChoice'
                  function_call:
                    type: object
                    deprecated: true
                    nullable: true
                    properties:
                      arguments:
                        type: string
                      name:
                        type: string
                    required:
                      - arguments
                      - name
        usage:
          allOf:
            - $ref: '#/components/schemas/UsageData'
            - nullable: true
        warnings:
          type: array
          items:
            $ref: '#/components/schemas/InferenceWarning'
    ChatCompletionUserMessageContent:
      description: >-
        The content of the message, which can either be a simple string or a
        structured format.
      oneOf:
        - $ref: '#/components/schemas/ChatCompletionUserMessageContentString'
        - $ref: '#/components/schemas/ChatCompletionUserMessageContentMultimodal'
    ChatCompletionUserMessageContentString:
      type: string
      description: A plain text message.
    ChatCompletionUserMessageContentMultimodal:
      type: array
      description: A structured message with mixed content types.
      items:
        type: object
        oneOf:
          - type: object
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
          - type: object
            properties:
              type:
                type: string
                enum:
                  - image_url
              image_url:
                type: object
                properties:
                  url:
                    type: string
                    description: The URL of the image
                required:
                  - url
          - type: object
            title: Video
            properties:
              type:
                type: string
                enum:
                  - video_url
              video_url:
                type: object
                properties:
                  url:
                    type: string
                    description: The URL of the video
                required:
                  - url
            required:
              - type
              - video_url
          - type: object
            title: Audio
            properties:
              type:
                type: string
                enum:
                  - audio_url
              audio_url:
                type: object
                properties:
                  url:
                    type: string
                    description: The URL of the audio
                required:
                  - url
            required:
              - type
              - audio_url
          - type: object
            title: Input Audio
            properties:
              type:
                type: string
                enum:
                  - input_audio
              input_audio:
                type: object
                properties:
                  data:
                    type: string
                    description: The base64 encoded audio data
                  format:
                    type: string
                    description: The format of the audio data
                    enum:
                      - wav
                required:
                  - data
                  - format
            required:
              - type
              - input_audio
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      x-bearer-format: bearer
      x-default: default

````