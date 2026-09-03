> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Responses API

> Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call the function tools you define, or use server-side web search.

<Accordion title="Examples">
  <CodeGroup>
    ```python Python theme={null}
    import os

    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["MOONSHOT_API_KEY"],
        base_url="https://api.moonshot.ai/v1",
    )

    response = client.responses.create(
        model="kimi-k3",
        instructions="You are Kimi, an AI assistant provided by Moonshot AI.",
        input="Explain context caching in one sentence.",
    )

    print(response.output_text)
    ```

    ```javascript Node.js theme={null}
    import OpenAI from "openai";

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: "https://api.moonshot.ai/v1",
    });

    const response = await client.responses.create({
        model: "kimi-k3",
        instructions: "You are Kimi, an AI assistant provided by Moonshot AI.",
        input: "Explain context caching in one sentence.",
    });

    console.log(response.output_text);
    ```

    ```bash cURL theme={null}
    curl https://api.moonshot.ai/v1/responses \
        --header "Content-Type: application/json" \
        --header "Authorization: Bearer $MOONSHOT_API_KEY" \
        --data '{
            "model": "kimi-k3",
            "instructions": "You are Kimi, an AI assistant provided by Moonshot AI.",
            "input": "Explain context caching in one sentence."
        }'
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Tool Use">
  `tools` supports four tool types: `function`, `namespace`, `custom` (only `apply_patch`), and `web_search`. Other types are not supported. The first three run on your side: the model returns a call request, you execute it and send the result back. `web_search` runs on the server side, with nothing for you to handle.

  **Function calling**

  Pass functions defined with JSON Schema through `tools`, and the model decides when to call them:

  ```json theme={null}
  {
    "model": "kimi-k3",
    "input": "What is the weather in Beijing today?",
    "tools": [
      {
        "type": "function",
        "name": "get_weather",
        "description": "Get the weather for a city",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string", "description": "City name"}
          },
          "required": ["city"]
        }
      }
    ]
  }
  ```

  When the model decides to call a function, `output` contains a `function_call` item whose `arguments` is a JSON string:

  ```json theme={null}
  {
    "type": "function_call",
    "id": "fc_IrcmDq5JNO0JhWdEpsuZnL9J",
    "status": "completed",
    "call_id": "get_weather_0",
    "name": "get_weather",
    "arguments": "{\"city\":\"Beijing\"}"
  }
  ```

  After running it locally, append the previous `output` to `input` as is, followed by a `function_call_output` item (its `call_id` must match the `function_call`), and send the next request:

  ```json theme={null}
  {
    "model": "kimi-k3",
    "input": [
      {"type": "message", "role": "user", "content": "What is the weather in Beijing today?"},
      {"type": "function_call", "call_id": "get_weather_0", "name": "get_weather", "arguments": "{\"city\":\"Beijing\"}"},
      {"type": "function_call_output", "call_id": "get_weather_0", "output": "Sunny, 25°C"}
    ],
    "tools": [
      {
        "type": "function",
        "name": "get_weather",
        "description": "Get the weather for a city",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string", "description": "City name"}
          },
          "required": ["city"]
        }
      }
    ]
  }
  ```

  **Web search**

  Add `{"type": "web_search"}` to `tools`. The server first decides from the input whether a search is needed, then runs it and injects the results into the model context, and the model answers from those results:

  ```json theme={null}
  {
    "model": "kimi-k3",
    "input": "What are the top news stories today?",
    "tools": [
      {"type": "web_search"}
    ]
  }
  ```

  When a search ran, a `web_search_call` item appears at the front of `output`. Add `web_search_call.action.sources` to `include` to get the web pages the search hit:

  ```json theme={null}
  {
    "type": "web_search_call",
    "id": "ws_dackjbcdo9rs73fo3oig",
    "status": "completed",
    "action": {
      "type": "search",
      "query": "top news September 3 2026",
      "sources": [
        {"type": "url", "url": "https://example.com/news/1", "title": "News headline"}
      ]
    }
  }
  ```
</Accordion>


## OpenAPI

````yaml POST /v1/responses
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
  /v1/responses:
    post:
      tags:
        - Responses
      summary: Create a model response
      description: >-
        Creates a model response. Provide text or image inputs to generate text
        or JSON outputs. Have the model call the function tools you define. When
        `stream` is `true`, the response is delivered as a stream of SSE events.
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
              $ref: '#/components/schemas/ResponsesRequest'
      responses:
        '200':
          description: The response was created
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
                $ref: '#/components/schemas/ResponsesResponse'
            text/event-stream:
              schema:
                $ref: '#/components/schemas/ResponsesStreamEvent'
        '400':
          description: Bad request - invalid parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: Unauthorized - the API key is invalid or missing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '403':
          description: Access to the resource is forbidden
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '429':
          description: Rate limited or out of quota
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
    ResponsesRequest:
      type: object
      required:
        - model
        - input
      properties:
        model:
          type: string
          description: ID of the model to use. This endpoint currently supports `kimi-k3`.
          example: kimi-k3
        input:
          description: >-
            Input for this request. A string is equivalent to a single user
            message. An array holds ordered typed items and may contain
            conversation history, tool calls, and tool results.
          oneOf:
            - type: string
            - type: array
              items:
                $ref: '#/components/schemas/ResponsesInputItem'
        instructions:
          type: string
          description: Top-level system instructions, applied ahead of every input item.
        stream:
          type: boolean
          default: false
          description: When true, the response is delivered as a stream of SSE events.
        max_output_tokens:
          type: integer
          description: >-
            Maximum number of tokens to generate for this response. For
            `kimi-k3` it defaults to 131072 and can be set up to 1048576. This
            refers to the length of tokens you expect us to return, not the
            total length of input plus output. When the limit is reached,
            `status` is `incomplete` and `incomplete_details.reason` is
            `max_output_tokens`.
        reasoning:
          type: object
          description: Reasoning configuration.
          properties:
            effort:
              type: string
              enum:
                - low
                - high
                - max
              default: max
              description: >-
                Reasoning depth. Higher levels reason more thoroughly, which
                usually also increases latency and reasoning token usage.
        text:
          type: object
          description: Output text configuration.
          properties:
            format:
              type: object
              required:
                - type
                - schema
              description: Constrains the output structure with a JSON Schema.
              properties:
                type:
                  type: string
                  enum:
                    - json_schema
                name:
                  type: string
                  description: Schema name. Defaults to `output`.
                schema:
                  type: object
                  description: JSON Schema describing the output structure.
                strict:
                  type: boolean
                  description: Whether the output must strictly conform to the schema.
        tools:
          type: array
          description: List of tools the model may call.
          items:
            $ref: '#/components/schemas/ResponsesTool'
        tool_choice:
          $ref: '#/components/schemas/ResponsesToolChoice'
        include:
          type: array
          items:
            type: string
            enum:
              - web_search_call.results
              - web_search_call.action.sources
          description: >-
            Additional fields to return. Only effective when the `web_search`
            tool is used. `web_search_call.action.sources` returns the web pages
            the search hit; `web_search_call.results` returns image search
            results.
        prompt_cache_key:
          type: string
          description: >-
            Context cache identifier. Reusing the same value across a session
            improves cache hit rate.
        safety_identifier:
          type: string
          description: >-
            A stable identifier used to help detect users of your application
            that may be violating usage policies. The ID should be a string that
            uniquely identifies each user. It is recommended to hash the
            username or email address to avoid sending any identifying
            information
    ResponsesResponse:
      type: object
      description: A single model response.
      properties:
        id:
          type: string
          description: Unique identifier of the response.
          example: resp_68f0c1c2d3e4f5a6b7c8d9e0
        object:
          type: string
          enum:
            - response
        created_at:
          type: integer
          description: Unix timestamp of when the response was created.
        completed_at:
          type:
            - integer
            - 'null'
          description: >-
            Unix timestamp of when the response finished. Present when `status`
            is `completed` or `incomplete`; `null` when `status` is
            `in_progress` or `failed`.
        status:
          type: string
          enum:
            - in_progress
            - completed
            - incomplete
            - failed
          description: Response status. The opening snapshot of a stream is `in_progress`.
        model:
          type: string
          description: Model that produced the response.
        output:
          type: array
          description: >-
            The output item array, ordered as web_search_call (if any),
            reasoning, message, tool calls.
          items:
            $ref: '#/components/schemas/ResponsesOutputItem'
        usage:
          oneOf:
            - $ref: '#/components/schemas/ResponsesUsage'
            - type: 'null'
        incomplete_details:
          type:
            - object
            - 'null'
          description: Reason the response is `incomplete`.
          properties:
            reason:
              type: string
              enum:
                - max_output_tokens
                - content_filter
        error:
          type:
            - object
            - 'null'
          description: Error information when `status` is `failed`.
          properties:
            code:
              type: string
            message:
              type: string
        instructions:
          type:
            - string
            - 'null'
        reasoning:
          type:
            - object
            - 'null'
        text:
          type:
            - object
            - 'null'
        tools:
          type:
            - array
            - 'null'
          items:
            $ref: '#/components/schemas/ResponsesTool'
        tool_choice:
          oneOf:
            - $ref: '#/components/schemas/ResponsesToolChoice'
            - type: 'null'
        max_output_tokens:
          type:
            - integer
            - 'null'
        temperature:
          type:
            - number
            - 'null'
        top_p:
          type:
            - number
            - 'null'
        metadata:
          type:
            - object
            - 'null'
        parallel_tool_calls:
          type: boolean
        service_tier:
          type:
            - string
            - 'null'
        store:
          type: boolean
          description: Always `false`.
        background:
          type:
            - boolean
            - 'null'
          description: Always `false`.
        previous_response_id:
          type:
            - string
            - 'null'
          description: Always `null`.
        conversation:
          type:
            - object
            - 'null'
          description: Always `null`.
    ResponsesStreamEvent:
      type: object
      description: >-
        A single SSE event returned when `stream: true`. Each frame is `event:
        <type>` followed by `data: <json>`, and the remaining fields of the
        event body vary by `type`.
      required:
        - type
        - sequence_number
      properties:
        type:
          type: string
          enum:
            - response.created
            - response.in_progress
            - response.output_item.added
            - response.output_item.done
            - response.content_part.added
            - response.content_part.done
            - response.output_text.delta
            - response.output_text.done
            - response.reasoning_summary_part.added
            - response.reasoning_summary_part.done
            - response.reasoning_summary_text.delta
            - response.reasoning_summary_text.done
            - response.function_call_arguments.delta
            - response.function_call_arguments.done
            - response.custom_tool_call_input.delta
            - response.custom_tool_call_input.done
            - response.web_search_call.in_progress
            - response.web_search_call.searching
            - response.web_search_call.completed
            - response.completed
            - response.incomplete
            - response.failed
            - error
        sequence_number:
          type: integer
          description: Event sequence number, increasing monotonically from 0.
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
    ResponsesInputItem:
      description: >-
        An element of the input array, discriminated by `type`. When `type` is
        omitted the item is treated as `message`.
      oneOf:
        - $ref: '#/components/schemas/ResponsesMessageItem'
        - $ref: '#/components/schemas/ResponsesReasoningItem'
        - $ref: '#/components/schemas/ResponsesFunctionCallItem'
        - $ref: '#/components/schemas/ResponsesFunctionCallOutputItem'
        - $ref: '#/components/schemas/ResponsesCustomToolCallItem'
        - $ref: '#/components/schemas/ResponsesCustomToolCallOutputItem'
        - $ref: '#/components/schemas/ResponsesWebSearchCallItem'
        - $ref: '#/components/schemas/ResponsesAdditionalToolsItem'
    ResponsesTool:
      description: >-
        A tool definition, discriminated by `type`. Supported types are
        `function`, `custom` (only `apply_patch`), `namespace`, and
        `web_search`; other tool types are not supported.
      oneOf:
        - $ref: '#/components/schemas/ResponsesFunctionTool'
        - $ref: '#/components/schemas/ResponsesCustomTool'
        - $ref: '#/components/schemas/ResponsesNamespaceTool'
        - $ref: '#/components/schemas/ResponsesWebSearchTool'
      discriminator:
        propertyName: type
        mapping:
          function:
            $ref: '#/components/schemas/ResponsesFunctionTool'
          custom:
            $ref: '#/components/schemas/ResponsesCustomTool'
          namespace:
            $ref: '#/components/schemas/ResponsesNamespaceTool'
          web_search:
            $ref: '#/components/schemas/ResponsesWebSearchTool'
    ResponsesToolChoice:
      type: string
      enum:
        - auto
      description: >-
        Controls tool-calling behavior. With `auto`, the model decides whether
        to call a tool.
    ResponsesOutputItem:
      description: An element of the output array, discriminated by `type`.
      oneOf:
        - $ref: '#/components/schemas/ResponsesOutputReasoningItem'
        - $ref: '#/components/schemas/ResponsesOutputMessageItem'
        - $ref: '#/components/schemas/ResponsesOutputFunctionCallItem'
        - $ref: '#/components/schemas/ResponsesOutputCustomToolCallItem'
        - $ref: '#/components/schemas/ResponsesOutputWebSearchCallItem'
      discriminator:
        propertyName: type
        mapping:
          reasoning:
            $ref: '#/components/schemas/ResponsesOutputReasoningItem'
          message:
            $ref: '#/components/schemas/ResponsesOutputMessageItem'
          function_call:
            $ref: '#/components/schemas/ResponsesOutputFunctionCallItem'
          custom_tool_call:
            $ref: '#/components/schemas/ResponsesOutputCustomToolCallItem'
          web_search_call:
            $ref: '#/components/schemas/ResponsesOutputWebSearchCallItem'
    ResponsesUsage:
      type: object
      description: Token usage for this response.
      properties:
        input_tokens:
          type: integer
          description: Number of input tokens, including cached tokens.
        input_tokens_details:
          type: object
          properties:
            cached_tokens:
              type: integer
              description: Number of tokens served from the context cache.
            cache_write_tokens:
              type: integer
              description: Number of tokens written to the context cache.
        output_tokens:
          type: integer
          description: Number of output tokens, including reasoning tokens.
        output_tokens_details:
          type: object
          properties:
            reasoning_tokens:
              type: integer
              description: Number of tokens spent on reasoning.
        total_tokens:
          type: integer
          description: Total number of tokens.
    ResponsesMessageItem:
      type: object
      title: Message
      description: A conversation message. `type` may be omitted.
      required:
        - role
        - content
      properties:
        type:
          type: string
          enum:
            - message
        role:
          type: string
          enum:
            - user
            - assistant
            - developer
          description: Message role. `developer` is handled as a system instruction.
        content:
          description: Message content, either a string or an array of content parts.
          oneOf:
            - type: string
            - type: array
              items:
                $ref: '#/components/schemas/ResponsesInputContentPart'
        status:
          type: string
          enum:
            - completed
    ResponsesReasoningItem:
      type: object
      title: Reasoning
      description: >-
        Replays reasoning content from a previous turn. `content` takes
        precedence over `summary`.
      required:
        - type
      properties:
        type:
          type: string
          enum:
            - reasoning
        id:
          type: string
        summary:
          type: array
          items:
            type: object
            required:
              - type
              - text
            properties:
              type:
                type: string
                enum:
                  - summary_text
              text:
                type: string
        content:
          type: array
          items:
            type: object
            required:
              - type
              - text
            properties:
              type:
                type: string
                enum:
                  - reasoning_text
              text:
                type: string
        status:
          type: string
          enum:
            - completed
    ResponsesFunctionCallItem:
      type: object
      title: Function call
      description: Replays a function call.
      required:
        - type
        - call_id
        - name
        - arguments
      properties:
        type:
          type: string
          enum:
            - function_call
        id:
          type: string
        call_id:
          type: string
          description: Call ID paired with the matching `function_call_output`.
        name:
          type: string
        namespace:
          type: string
          description: Namespace the tool belongs to, returned for namespace tool calls.
        arguments:
          type: string
          description: JSON string of the function arguments.
        status:
          type: string
          enum:
            - completed
    ResponsesFunctionCallOutputItem:
      type: object
      title: Function call output
      description: Result of executing a function call.
      required:
        - type
        - call_id
        - output
      properties:
        type:
          type: string
          enum:
            - function_call_output
        call_id:
          type: string
          description: Same call ID as the matching `function_call`.
        output:
          description: Content returned by the tool.
          oneOf:
            - type: string
            - type: array
              items:
                $ref: '#/components/schemas/ResponsesInputContentPart'
        status:
          type: string
          enum:
            - completed
    ResponsesCustomToolCallItem:
      type: object
      title: Custom tool call
      description: Replays a custom tool call.
      required:
        - type
        - call_id
        - name
        - input
      properties:
        type:
          type: string
          enum:
            - custom_tool_call
        id:
          type: string
        call_id:
          type: string
          description: Call ID paired with the matching `custom_tool_call_output`.
        name:
          type: string
        namespace:
          type: string
          description: Namespace the tool belongs to, returned for namespace tool calls.
        input:
          type: string
          description: Free-form text input generated by the model.
        status:
          type: string
          enum:
            - completed
    ResponsesCustomToolCallOutputItem:
      type: object
      title: Custom tool call output
      description: Result of executing a custom tool call.
      required:
        - type
        - call_id
        - output
      properties:
        type:
          type: string
          enum:
            - custom_tool_call_output
        call_id:
          type: string
          description: Same call ID as the matching `custom_tool_call`.
        output:
          description: Content returned by the tool.
          oneOf:
            - type: string
            - type: array
              items:
                $ref: '#/components/schemas/ResponsesInputContentPart'
        status:
          type: string
          enum:
            - completed
    ResponsesWebSearchCallItem:
      type: object
      title: Web search call
      description: >-
        Replays a previous web search call. Kept for history only and ignored
        during conversion; the search results are already carried by the
        assistant message that follows.
      required:
        - type
      properties:
        type:
          type: string
          enum:
            - web_search_call
        id:
          type: string
        status:
          type: string
          enum:
            - completed
        action:
          type: object
          properties:
            type:
              type: string
              enum:
                - search
            query:
              type: string
    ResponsesAdditionalToolsItem:
      type: object
      title: Additional tools
      description: >-
        Adds callable tools partway through a conversation, effective from the
        position of this item.
      required:
        - type
        - role
        - tools
      properties:
        type:
          type: string
          enum:
            - additional_tools
        id:
          type: string
        role:
          type: string
          enum:
            - developer
        tools:
          type: array
          items:
            $ref: '#/components/schemas/ResponsesTool'
    ResponsesFunctionTool:
      type: object
      title: Function tool
      description: A function tool whose arguments are described by a JSON Schema.
      required:
        - type
        - name
      properties:
        type:
          type: string
          enum:
            - function
        name:
          type: string
          description: >-
            Function name. Must follow the regex:
            ^[a-zA-Z_][a-zA-Z0-9-_]{0,127}$
          pattern: ^[a-zA-Z_][a-zA-Z0-9-_]{0,127}$
        description:
          type: string
        parameters:
          type: object
          description: JSON Schema describing the function arguments.
        strict:
          type: boolean
    ResponsesCustomTool:
      type: object
      title: Custom tool
      description: >-
        A custom tool that takes free-form text input. Only the custom tool
        named `apply_patch` is supported, and it must define a `grammar` +
        `lark` format; when the model calls it, a `custom_tool_call` item is
        returned in the output.
      required:
        - type
        - name
        - format
      properties:
        type:
          type: string
          enum:
            - custom
        name:
          type: string
          enum:
            - apply_patch
          description: Tool name. Only `apply_patch` is supported.
        description:
          type: string
        format:
          type: object
          description: >-
            Input format constraint. Only the `grammar` type with `lark` syntax
            is supported.
          required:
            - type
            - syntax
            - definition
          properties:
            type:
              type: string
              enum:
                - grammar
            syntax:
              type: string
              enum:
                - lark
            definition:
              type: string
              description: The Lark grammar definition.
    ResponsesNamespaceTool:
      type: object
      title: Namespace tool
      description: Groups a set of function or custom tools under one namespace.
      required:
        - type
        - name
        - description
        - tools
      properties:
        type:
          type: string
          enum:
            - namespace
        name:
          type: string
        description:
          type: string
        tools:
          type: array
          items:
            oneOf:
              - $ref: '#/components/schemas/ResponsesFunctionTool'
              - $ref: '#/components/schemas/ResponsesCustomTool'
    ResponsesWebSearchTool:
      type: object
      title: Web search tool
      description: >-
        A web search tool executed on the server side. When present, the server
        first decides from the input whether a search is needed; if so, it runs
        the search, injects the results into the model context, and returns a
        `web_search_call` item in the output. At most one `web_search` tool is
        allowed per request. `search_context_size`, `blocked_domains`, and
        `filters.blocked_domains` are not supported and return
        `invalid_request_error`; `user_location`, `external_web_access`, and
        `indexed_web_access` are ignored.
      required:
        - type
      properties:
        type:
          type: string
          enum:
            - web_search
        filters:
          type: object
          description: Search scope filters.
          properties:
            allowed_domains:
              type: array
              items:
                type: string
              maxItems: 100
              description: Restrict the search to these domains, up to 100.
        search_content_types:
          type: array
          items:
            type: string
            enum:
              - text
              - image
          default:
            - text
          description: >-
            Result types to search for. Defaults to `text` only. Including
            `image` additionally runs an image search.
        image_settings:
          type: object
          description: >-
            Image search settings. Only effective when `search_content_types`
            includes `image`.
          properties:
            max_results:
              type: integer
              minimum: 1
              maximum: 10
              default: 3
              description: Maximum number of images to return.
            caption:
              type: boolean
              default: false
              description: Whether to generate a caption for each image.
    ResponsesOutputReasoningItem:
      type: object
      title: Reasoning
      description: Reasoning content produced by the model.
      properties:
        type:
          type: string
          enum:
            - reasoning
        id:
          type: string
          example: rs_68f0c1c2d3e4f5a6b7c8d9e0
        summary:
          type: array
          description: The reasoning content.
          items:
            type: object
            properties:
              type:
                type: string
                enum:
                  - summary_text
              text:
                type: string
        encrypted_content:
          type:
            - string
            - 'null'
          description: Always `null`.
        status:
          type: string
          enum:
            - in_progress
            - completed
    ResponsesOutputMessageItem:
      type: object
      title: Message
      description: Text reply produced by the model.
      properties:
        type:
          type: string
          enum:
            - message
        id:
          type: string
          example: msg_68f0c1c2d3e4f5a6b7c8d9e0
        role:
          type: string
          enum:
            - assistant
        content:
          type: array
          items:
            type: object
            properties:
              type:
                type: string
                enum:
                  - output_text
              text:
                type: string
              annotations:
                type: array
                items: {}
        status:
          type: string
          enum:
            - in_progress
            - completed
    ResponsesOutputFunctionCallItem:
      type: object
      title: Function call
      description: A function call initiated by the model.
      properties:
        type:
          type: string
          enum:
            - function_call
        id:
          type: string
          example: fc_68f0c1c2d3e4f5a6b7c8d9e0
        call_id:
          type: string
          description: Use this value in `function_call_output` when returning the result.
        name:
          type: string
        namespace:
          type: string
          description: Returned for namespace tool calls.
        arguments:
          type: string
          description: JSON string of the function arguments.
        status:
          type: string
          enum:
            - in_progress
            - completed
    ResponsesOutputCustomToolCallItem:
      type: object
      title: Custom tool call
      description: A custom tool call initiated by the model.
      properties:
        type:
          type: string
          enum:
            - custom_tool_call
        id:
          type: string
          example: ctc_68f0c1c2d3e4f5a6b7c8d9e0
        call_id:
          type: string
          description: >-
            Use this value in `custom_tool_call_output` when returning the
            result.
        name:
          type: string
        namespace:
          type: string
          description: Returned for namespace tool calls.
        input:
          type: string
          description: Free-form text input generated by the model.
        status:
          type: string
          enum:
            - in_progress
            - completed
    ResponsesOutputWebSearchCallItem:
      type: object
      title: Web search call
      description: >-
        A web search call executed on the server side. Returned only when the
        request includes the `web_search` tool and the server decides a search
        is needed. It appears first in the output array.
      properties:
        type:
          type: string
          enum:
            - web_search_call
        id:
          type: string
          example: ws_68f0c1c2d3e4f5a6b7c8d9e0
        status:
          type: string
          enum:
            - in_progress
            - completed
        action:
          type: object
          description: The action performed by this search.
          properties:
            type:
              type: string
              enum:
                - search
            query:
              type: string
              description: The search query actually used.
            sources:
              type: array
              description: >-
                Web pages the search hit. Returned only when `include` contains
                `web_search_call.action.sources`.
              items:
                type: object
                properties:
                  type:
                    type: string
                    enum:
                      - url
                  url:
                    type: string
                  title:
                    type: string
        results:
          type: array
          description: >-
            Image search results. Returned only when `include` contains
            `web_search_call.results` and `search_content_types` includes
            `image`.
          items:
            type: object
            properties:
              type:
                type: string
                enum:
                  - image_result
              image_url:
                type: string
              thumbnail_url:
                type: string
              source_website_url:
                type: string
              caption:
                type: string
                description: >-
                  Image caption. Returned only when `image_settings.caption` is
                  enabled.
    ResponsesInputContentPart:
      description: An element of a content array, discriminated by `type`.
      oneOf:
        - type: object
          title: Input text
          required:
            - type
            - text
          properties:
            type:
              type: string
              enum:
                - input_text
            text:
              type: string
        - type: object
          title: Input image
          required:
            - type
            - image_url
          properties:
            type:
              type: string
              enum:
                - input_image
            image_url:
              type: string
              description: >-
                Data URL of the image, for example
                `data:image/png;base64,<base64>`. Public http(s) URLs are not
                supported.
            detail:
              type: string
              enum:
                - auto
                - low
                - high
                - original
        - type: object
          title: Output text
          description: Used when replaying assistant text from history.
          required:
            - type
            - text
          properties:
            type:
              type: string
              enum:
                - output_text
            text:
              type: string
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````