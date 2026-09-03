> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Chat Completions API

> Create a chat completion: send messages to Kimi models and get replies, with streaming, tool calling, and vision input.

Create a chat completion request. The model generates a response based on the provided message list.

<Accordion title="Content Field Description">
  The `content` field supports the following two forms:

  **Plain text string**

  ```json theme={null}
  { "content": "Hello" }
  ```

  **Array of objects** (for multimodal input)

  Each element in the array is distinguished by the `type` field:

  ```json theme={null}
  {
      "content": [
          { "type": "text", "text": "Describe this image" },
          { "type": "image_url", "image_url": { "url": "data:image/png;base64,..." } },
          { "type": "video_url", "video_url": { "url": "data:video/mp4;base64,..." } }
      ]
  }
  ```

  `image_url` and `video_url` also support passing a string directly, equivalent to the `url` field in object form:

  ```json theme={null}
  { "type": "image_url", "image_url": "data:image/png;base64,..." }
  ```

  #### Parameter Description

  Each element in the array has the following fields:

  | Parameter   | Required                       | Description                                                                             | Type                                       |
  | ----------- | ------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------ |
  | `type`      | required                       | Content type                                                                            | `"text"` \| `"image_url"` \| `"video_url"` |
  | `text`      | required when `type=text`      | Text content                                                                            | string                                     |
  | `image_url` | required when `type=image_url` | For transmitting images. Supports object form `{"url": "..."}` or a URL string directly | object \| string                           |
  | `video_url` | required when `type=video_url` | For transmitting videos. Supports object form `{"url": "..."}` or a URL string directly | object \| string                           |

  When `image_url` is passed as an object, its fields are:

  | Parameter | Required | Description                                            | Type   |
  | --------- | -------- | ------------------------------------------------------ | ------ |
  | `url`     | required | Image content specified via base64 encoding or file id | string |

  When `video_url` is passed as an object, its fields are:

  | Parameter | Required | Description                                                                                     | Type   |
  | --------- | -------- | ----------------------------------------------------------------------------------------------- | ------ |
  | `url`     | required | Video content specified via base64 encoding or file id, for example `data:video/mp4;base64,...` | string |

  <Note>
    Both the object form (`url` field) and the string shorthand support the following formats:

    * Base64 encoding: `data:image/png;base64,...` or `data:video/mp4;base64,...`
    * File reference: `ms://<file_id>`

    See [Use the Kimi Vision Model](/docs/guide/use-kimi-vision-model).
  </Note>

  #### Usage Example

  <CodeGroup>
    ```python python expandable theme={null}
    import os
    import base64

    from openai import OpenAI
    from openai.types.chat import ChatCompletion

    client: OpenAI = OpenAI(
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        base_url="https://api.moonshot.ai/v1",
    )

    # Encode the image to base64
    with open("your_image_path", "rb") as f:
        img_base: str = base64.b64encode(f.read()).decode("utf-8")

    response: ChatCompletion = client.chat.completions.create(
        model="kimi-k2.6",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base}",
                        },
                    },
                    {
                        "type": "text",
                        "text": "Describe this image",
                    },
                ],
            }
        ],
    )
    print(response.choices[0].message.content)
    ```

    ```bash curl expandable theme={null}
    curl https://api.moonshot.ai/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -d '{
            "model": "kimi-k2.6",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/jpeg;base64,/9j/4AAQ..."
                            }
                        },
                        {
                            "type": "text",
                            "text": "Describe this image"
                        }
                    ]
                }
            ]
        }'
    ```

    ```javascript node.js expandable theme={null}
    const fs = require("fs");
    const OpenAI = require("openai");

    const client = new OpenAI({
        apiKey: process.env.MOONSHOT_API_KEY,
        baseURL: "https://api.moonshot.ai/v1",
    });

    async function main() {
        // Encode the image to base64
        const imgBase = fs.readFileSync("your_image_path").toString("base64");

        const response = await client.chat.completions.create({
            model: "kimi-k2.6",
            messages: [
                {
                    role: "user",
                    content: [
                        {
                            type: "image_url",
                            image_url: {
                                url: `data:image/jpeg;base64,${imgBase}`,
                            },
                        },
                        {
                            type: "text",
                            text: "Describe this image",
                        },
                    ],
                },
            ],
        });
        console.log(response.choices[0].message.content);
    }

    main();
    ```
  </CodeGroup>
</Accordion>

<Accordion title="Response Format">
  ### Non-streaming Response

  ```json theme={null}
  {
      "id": "cmpl-04ea926191a14749b7f2c7a48a68abc6",
      "object": "chat.completion",
      "created": 1698999496,
      "model": "kimi-k2.6",
      "choices": [
          {
              "index": 0,
              "message": {
                  "role": "assistant",
                  "content": "Hello, Li Lei! 1+1 equals 2. If you have any other questions, feel free to ask!"
              },
              "finish_reason": "stop"
          }
      ],
      "usage": {
          "prompt_tokens": 19,
          "completion_tokens": 21,
          "total_tokens": 40,
          "cached_tokens": 10
      }
  }
  ```

  ### Streaming Response

  ```text theme={null}
  data: {"id":"cmpl-xxx","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k2.6","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

  data: {"id":"cmpl-xxx","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k2.6","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

  ...

  data: {"id":"cmpl-xxx","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k2.6","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":19,"completion_tokens":13,"total_tokens":32,"cached_tokens":12}}

  data: [DONE]
  ```

  <Note>
    The model name in the response example will be returned based on the model parameter in the request. When using the `kimi-k2.6` model, the `"model"` field in the response will show `"kimi-k2.6"`.
  </Note>
</Accordion>

<Accordion title="Multi-turn Conversations">
  The Kimi API is stateless and does not retain conversation history. To implement multi-turn dialogue, append the previous assistant reply (and any tool results, if applicable) back into the `messages` array before sending the next request.

  ```python theme={null}
  messages = [
      {"role": "system", "content": "You are Kimi."},
      {"role": "user", "content": "Hello, my name is Li Lei."}
  ]

  completion = client.chat.completions.create(model="kimi-k2.6", messages=messages)
  reply = completion.choices[0].message

  # Append the assistant reply back into messages for the next turn
  messages.append({"role": "assistant", "content": reply.content})
  messages.append({"role": "user", "content": "What is 1+1?"})
  ```

  When the conversation history grows too long, retain only the most recent messages or compress earlier turns to avoid exceeding the model's context limit.

  <Note>
    See [Engage in Multi-turn Conversations](/docs/guide/engage-in-multi-turn-conversations-using-kimi-api) for details.
  </Note>
</Accordion>

<Accordion title="JSON Mode">
  Use the `response_format` parameter to constrain the model output format:

  * `{"type": "text"}` (default): plain text output
  * `{"type": "json_object"}`: forces a valid JSON Object output
  * `{"type": "json_schema", "json_schema": {...}}`: outputs structured data according to the given JSON Schema (Structured Output)

  When using `json_object`, **you must explicitly describe the expected JSON fields and types in the system prompt or user prompt**, otherwise the model may produce unexpected results.

  ```json theme={null}
  {
    "model": "kimi-k2.6",
    "messages": [
      {"role": "system", "content": "Please output JSON containing title, author, and summary fields."},
      {"role": "user", "content": "Summarize this article..."}
    ],
    "response_format": {"type": "json_object"}
  }
  ```

  <Note>
    See [Use the JSON Mode Feature of Kimi API](/docs/guide/use-json-mode-feature-of-kimi-api) for details.
  </Note>
</Accordion>

<Accordion title="Tool Use">
  Pass external tools defined as JSON Schema via the `tools` parameter. The model can decide to invoke them when appropriate.

  **Request example**

  ```json theme={null}
  {
    "model": "kimi-k2.6",
    "messages": [{"role": "user", "content": "What is the weather in Beijing today?"}],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get the weather for a given city",
          "parameters": {
            "type": "object",
            "properties": {
              "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
          }
        }
      }
    ]
  }
  ```

  **`tool_calls` in the response**

  When `finish_reason` is `"tool_calls"`, the model returns a `tool_calls` array containing `id`, `function.name`, and `function.arguments`:

  ```json theme={null}
  {
    "choices": [{
      "message": {
        "role": "assistant",
        "content": "",
        "tool_calls": [{
          "id": "call_xxx",
          "type": "function",
          "function": {
            "name": "get_weather",
            "arguments": "{\"city\":\"Beijing\"}"
          }
        }]
      },
      "finish_reason": "tool_calls"
    }]
  }
  ```

  **Submitting tool execution results**

  After executing the tool locally, append the result back into `messages` using `role="tool"`. The `tool_call_id` must match the `id` from the request:

  ```json theme={null}
  {"role": "tool", "tool_call_id": "call_xxx", "content": "Sunny, 25°C"}
  ```

  <Note>
    See [Use the Kimi API to Complete Tool Calls](/docs/guide/use-kimi-api-to-complete-tool-calls) for details.
  </Note>
</Accordion>

<Accordion title="Thinking Mode and Preserved Thinking">
  `kimi-k3` always reasons and uses the top-level `reasoning_effort` field (`"low"`, `"high"`, or `"max"`; default `"max"`). `kimi-k2.6` and `kimi-k2.7-code` support thinking mode: the model first outputs its reasoning process (`reasoning_content`) before producing the final answer.

  **K2.x request parameters**

  | Field           | Type                        | Description                                                                                                                                                                                                               |
  | --------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `thinking.type` | `"enabled"` \| `"disabled"` | Thinking switch (`kimi-k2.7-code` is always `enabled` and cannot be disabled)                                                                                                                                             |
  | `thinking.keep` | `null` \| `"all"`           | Preserved Thinking: whether to retain historical `reasoning_content` in context. `kimi-k2.6` defaults to `null` (not kept) and accepts `"all"`; `kimi-k2.7-code` is fixed at `"all"` (kept), other values return an error |

  **Response fields**

  In non-streaming responses, `choices[0].message` contains:

  | Field               | Description                                                     |
  | ------------------- | --------------------------------------------------------------- |
  | `content`           | Final answer                                                    |
  | `reasoning_content` | Reasoning process (returned only when thinking mode is enabled) |

  ```json theme={null}
  {
    "choices": [{
      "message": {
        "role": "assistant",
        "content": "1+1 equals 2.",
        "reasoning_content": "The user asked a basic math question, simply add the numbers."
      }
    }]
  }
  ```

  <Warning>
    When using a thinking model in multi-turn conversations, always preserve the `reasoning_content` of each historical assistant message in `messages`, otherwise the model may lose reasoning context.
  </Warning>

  <Note>
    See [Use the Kimi K2 Thinking Mode](/docs/guide/use-thinking-models) for details.
  </Note>
</Accordion>

<Accordion title="Streaming">
  Set `stream: true` to enable streaming output. The model returns content incrementally in Server-Sent Events (SSE) format. Recommended for scenarios requiring real-time feedback, such as chat, code generation, and long text output.

  ```python theme={null}
  completion = client.chat.completions.create(
      model="kimi-k2.6",
      messages=[{"role": "user", "content": "Explain what recursion is."}],
      stream=True
  )

  for chunk in completion:
      if chunk.choices[0].delta.content:
          print(chunk.choices[0].delta.content, end="")
  ```

  **SSE Response Format**

  Each line starts with `data:`, followed by a JSON object. When `finish_reason` is `null`, content accumulates in `delta.content`; when `finish_reason` is not `null`, the output is complete:

  ```text theme={null}
  data: {"id":"cmpl-xxx","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k2.6","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

  data: {"id":"cmpl-xxx","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k2.6","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

  data: {"id":"cmpl-xxx","object":"chat.completion.chunk","created":1698999575,"model":"kimi-k2.6","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":19,"completion_tokens":13,"total_tokens":32,"cached_tokens":12}}

  data: [DONE]
  ```

  **`stream_options`**

  Use `stream_options: {"include_usage": true}` to receive an additional `usage` field in the last chunk (before `data: [DONE]`), showing the token consumption of the request:

  ```python theme={null}
  stream=True,
  stream_options={"include_usage": True}
  ```

  <Note>
    See [Utilize the Streaming Output Feature of Kimi API](/docs/guide/utilize-the-streaming-output-feature-of-kimi-api) for details.
  </Note>
</Accordion>

<Accordion title="Partial Mode">
  Partial Mode (Prefill) allows you to prefill an output prefix in the last assistant message of `messages`, guiding the model to continue generation in the format or direction you expect.

  **How to Enable**

  Append an `role="assistant"` message at the end of the `messages` array, and set `partial: true`:

  ````python theme={null}
  completion = client.chat.completions.create(
      model="kimi-k2.6",
      messages=[
          {"role": "user", "content": "Implement quicksort in Python."},
          {"role": "assistant", "content": "```python\n", "partial": True}
      ]
  )
  ````

  The model will continue generating code from \`\`\`\`python\n\` instead of outputting explanatory text first.

  **Common Use Cases**

  * Force the model to start with a specific format (e.g., JSON's `{`, a code block's \`\`\`\`python\`)
  * Maintain role name prefixes in role-play scenarios (combined with the `name` field)
  * When `finish_reason="length"`, use the same prefix to continue truncated content

  <Warning>
    Do not mix Partial Mode with `response_format={"type": "json_object"}`, as this may lead to unexpected model responses. To guide JSON output, use [Structured Output](/docs/guide/response_format) directly, or set `partial: true` and prefill `{` separately.
  </Warning>

  <Note>
    See [Use the Partial Mode Feature of Kimi API](/docs/guide/use-partial-mode-feature-of-kimi-api) for details.
  </Note>
</Accordion>


## OpenAPI

````yaml POST /v1/chat/completions
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
  /v1/chat/completions:
    post:
      tags:
        - Chat
      summary: Create Chat Completion
      description: >-
        Creates a completion for the chat message. Supports standard chat,
        Partial Mode, and Tool Use (Function Calling).
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
              oneOf:
                - $ref: '#/components/schemas/KimiK3ChatRequest'
                - $ref: '#/components/schemas/KimiK27CodeChatRequest'
                - $ref: '#/components/schemas/KimiK26ChatRequest'
              discriminator:
                propertyName: model
                mapping:
                  kimi-k3:
                    $ref: '#/components/schemas/KimiK3ChatRequest'
                  kimi-k2.7-code:
                    $ref: '#/components/schemas/KimiK27CodeChatRequest'
                  kimi-k2.7-code-highspeed:
                    $ref: '#/components/schemas/KimiK27CodeChatRequest'
                  kimi-k2.6:
                    $ref: '#/components/schemas/KimiK26ChatRequest'
      responses:
        '200':
          description: Chat completion response
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
                $ref: '#/components/schemas/ChatCompletionResponse'
            text/event-stream:
              schema:
                $ref: '#/components/schemas/ChatCompletionChunk'
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
    KimiK3ChatRequest:
      title: kimi-k3
      allOf:
        - $ref: '#/components/schemas/ChatRequestCommon'
        - type: object
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
                A list of Kimi K3 conversation messages. In addition to standard
                messages, you can insert a {"role": "system", "tools": [...]}
                message at any conversation position to dynamically load tools.
                A dynamic tool message omits content and only affects subsequent
                conversation turns.
              items:
                $ref: '#/components/schemas/KimiK3Message'
            reasoning_effort:
              type: string
              enum:
                - low
                - high
                - max
              default: max
              description: >-
                Kimi K3 always enables thinking with Preserved Thinking.
                Reasoning effort supports low, high, and max, with max as the
                default.
          required:
            - model
            - messages
    KimiK27CodeChatRequest:
      title: kimi-k2.7-code
      allOf:
        - $ref: '#/components/schemas/ChatRequestBase'
        - type: object
          properties:
            model:
              type: string
              description: >-
                Model ID. Either `kimi-k2.7-code` or its high-speed variant
                `kimi-k2.7-code-highspeed`; the two are the same model with
                identical parameters, while the high-speed variant outputs at
                approximately 180 Tokens/s (up to 260 Tokens/s in short-context
                scenarios).
              enum:
                - kimi-k2.7-code
                - kimi-k2.7-code-highspeed
              default: kimi-k2.7-code
            thinking:
              type: object
              description: >-
                Controls thinking for the kimi-k2.7-code model, and whether to
                fully preserve reasoning_content across multi-turn
                conversations. Optional parameter. Default value is {"type":
                "enabled", "keep": "all"}.


                Differences from kimi-k2.6:

                - `type` only accepts `"enabled"`. Unlike kimi-k2.6,
                `"disabled"` is NOT supported — passing it returns an error.
                Thinking is always on for this model.

                - `keep` only accepts the valid value `"all"`; omitting it or
                passing `"all"` is treated as `"all"` on the server, while any
                other invalid value returns an error. Preserved Thinking is
                therefore always enabled for this model.
              properties:
                type:
                  type: string
                  enum:
                    - enabled
                  description: >-
                    Enable thinking capability. For kimi-k2.7-code, only
                    `"enabled"` is accepted; passing `"disabled"` returns an
                    error. This differs from kimi-k2.6, which also supports
                    `"disabled"`.
                keep:
                  type:
                    - string
                    - 'null'
                  enum:
                    - all
                    - null
                  description: >-
                    Controls whether reasoning_content from previous turns is
                    preserved across a multi-turn conversation, i.e. whether to
                    enable Preserved Thinking.


                    - For kimi-k2.7-code this parameter only accepts the valid
                    value `"all"`: passing `"all"`, passing `null`, or omitting
                    it all behave identically and are treated as `"all"` on the
                    server — reasoning_content from historical turns is always
                    preserved; passing any other invalid value returns an error.
                    This differs from kimi-k2.6, whose default is `null`
                    (historical thinking NOT preserved unless you explicitly set
                    `"all"`).

                    - Because Preserved Thinking is always on, keep the
                    reasoning_content from every historical assistant message in
                    messages as-is.

                    - Note: This parameter only affects reasoning_content from
                    historical turns; it does not change whether the model
                    produces/outputs thinking within the current turn (that is
                    controlled by `type`). For best practices, see [Preserved
                    Thinking](/guide/use-thinking-models#preserved-thinking).
              required:
                - type
              additionalProperties: false
          required:
            - model
    KimiK26ChatRequest:
      title: kimi-k2.6
      allOf:
        - $ref: '#/components/schemas/ChatRequestBase'
        - type: object
          properties:
            model:
              type: string
              description: Model ID
              enum:
                - kimi-k2.6
              default: kimi-k2.6
            thinking:
              type: object
              description: >-
                Controls whether thinking is enabled for the kimi-k2.6 model,
                and whether to fully preserve reasoning_content across
                multi-turn conversations. Optional parameter. Default value is
                {"type": "enabled"}.
              properties:
                type:
                  type: string
                  enum:
                    - enabled
                    - disabled
                  description: Enable or disable thinking capability
                keep:
                  type:
                    - string
                    - 'null'
                  enum:
                    - all
                    - null
                  description: >-
                    Controls whether reasoning_content from previous turns is
                    preserved across a multi-turn conversation, i.e. whether to
                    enable Preserved Thinking. Defaults to `null`, meaning
                    historical thinking is NOT preserved.


                    - `null` (default) or omitted: The server ignores
                    reasoning_content from historical turns.

                    - `"all"`: Preserves reasoning_content from historical turns
                    and provides it to the model as part of the context,
                    enabling Preserved Thinking. When using this, keep the
                    reasoning_content from every historical assistant message in
                    messages as-is. Recommended to use together with `type:
                    "enabled"`.

                    - Note: This parameter only affects reasoning_content from
                    historical turns; it does not change whether the model
                    produces/outputs thinking within the current turn (that is
                    controlled by `type`). For best practices, see [Preserved
                    Thinking](/guide/use-thinking-models#preserved-thinking).
              required:
                - type
              additionalProperties: false
          required:
            - model
    ChatCompletionResponse:
      type: object
      properties:
        id:
          type: string
          description: Unique identifier for the completion
        object:
          type: string
          description: Object type
          example: chat.completion
        created:
          type: integer
          description: Unix timestamp of when the completion was created
        model:
          type: string
          description: Model used for the completion
        choices:
          type: array
          description: List of completion choices
          items:
            type: object
            properties:
              index:
                type: integer
              message:
                type: object
                properties:
                  role:
                    type: string
                    enum:
                      - assistant
                  content:
                    type:
                      - string
                      - 'null'
                    description: The assistant's message content
                  tool_calls:
                    type: array
                    description: Tool calls made by the model
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        type:
                          type: string
                          enum:
                            - function
                        function:
                          type: object
                          properties:
                            name:
                              type: string
                            arguments:
                              type: string
                              description: JSON string of function arguments
                  reasoning_content:
                    type:
                      - string
                      - 'null'
                    description: >-
                      Reasoning process (returned only when thinking mode is
                      enabled)
              finish_reason:
                type: string
                enum:
                  - stop
                  - length
                  - tool_calls
        usage:
          type: object
          properties:
            prompt_tokens:
              type: integer
              description: Number of tokens in the prompt
            completion_tokens:
              type: integer
              description: Number of tokens in the completion
            total_tokens:
              type: integer
              description: Total number of tokens used
            cached_tokens:
              type: integer
              description: Number of tokens served from cache
    ChatCompletionChunk:
      type: object
      properties:
        id:
          type: string
          description: Unique identifier for the completion
        object:
          type: string
          description: Object type
          example: chat.completion.chunk
        created:
          type: integer
          description: Unix timestamp of when the completion was created
        model:
          type: string
          description: Model used for the completion
        choices:
          type: array
          description: List of completion choices
          items:
            $ref: '#/components/schemas/ChoiceDelta'
        usage:
          type:
            - object
            - 'null'
          description: >-
            Token usage statistics. Object in the final chunk with usage, null
            in ordinary chunks
          properties:
            prompt_tokens:
              type: integer
              description: Number of tokens in the prompt
            completion_tokens:
              type: integer
              description: Number of tokens in the completion
            total_tokens:
              type: integer
              description: Total number of tokens used
            cached_tokens:
              type: integer
              description: Number of tokens served from cache
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
    ChatRequestCommon:
      type: object
      properties:
        logprobs:
          type: boolean
          default: false
          description: >-
            Whether to return log probabilities of the output tokens. If true,
            the log probability of each output token is returned in the logprobs
            field of the response message.
        top_logprobs:
          type: integer
          minimum: 0
          maximum: 20
          description: >-
            An integer between 0 and 20 specifying the number of most likely
            tokens to return at each token position, each with an associated log
            probability. logprobs must be set to true when this parameter is
            used.
        prediction:
          type: object
          description: >-
            Configuration for a Predicted Output, which can greatly improve
            response times when large parts of the model response are known
            ahead of time (for example, regenerating a file with only minor
            changes).
          properties:
            type:
              type: string
              enum:
                - content
              description: >-
                The type of the predicted content. Currently only content is
                supported.
            content:
              oneOf:
                - type: string
                - type: array
                  items:
                    type: object
              description: >-
                The static predicted output content that should be matched when
                generating the model response, such as the content of a text
                file being regenerated. Accepts a string or an array of content
                parts (text parts only).
        max_tokens:
          type: integer
          deprecated: true
          description: Deprecated, please refer to max_completion_tokens
        max_completion_tokens:
          type: integer
          description: >-
            The maximum number of tokens to generate for the chat completion.
            The default varies by model: for Kimi K3 it defaults to 131072 and
            can be set up to 1048576. If the result reaches the maximum number
            of tokens without ending, the finish reason will be "length";
            otherwise, it will be "stop". This refers to the length of tokens
            you expect us to return, not the total length of input plus output.
            If input plus max_completion_tokens exceeds the model context
            window, the API returns invalid_request_error.
        response_format:
          type: object
          description: >-
            Controls the model output format. Default is {"type": "text"} for
            plain text output. Set to {"type": "json_object"} to enable JSON
            mode, ensuring output is a valid JSON object (you must guide the
            model to output JSON in the prompt). Set to {"type": "json_schema"}
            to enable Structured Output, constraining output to match a
            specified JSON Schema (recommended, requires the json_schema field).
            If you encounter schema validation issues, please submit feedback at
            walle GitHub Issues (https://github.com/MoonshotAI/walle/issues).
          properties:
            type:
              type: string
              enum:
                - text
                - json_object
                - json_schema
              description: >-
                Output format type. text: default, plain text output;
                json_object: ensures output is a valid JSON object; json_schema:
                constrains output to match a specified JSON Schema (recommended,
                requires the json_schema field)
            json_schema:
              type: object
              description: >-
                Used when type is json_schema. Defines the JSON Schema that the
                output should conform to.
              properties:
                name:
                  type: string
                  description: Schema name for identification
                strict:
                  type: boolean
                  default: true
                  description: >-
                    Whether to strictly constrain output according to the
                    schema. Defaults to true. When true, the schema must conform
                    to the MFJS specification; non-conforming schemas will
                    return errors or warnings. When false, only guarantees the
                    output is a valid JSON object without enforcing internal
                    structure.
                schema:
                  type: object
                  description: >-
                    The JSON Schema object defining the structure the output
                    should conform to. Must conform to MFJS (Moonshot Flavored
                    JSON Schema) specification. You can use the walle CLI tool
                    to validate: go install
                    github.com/moonshotai/walle/cmd/walle@latest && walle
                    -schema 'your_schema' -level strict
                  additionalProperties: true
              required:
                - name
                - schema
        stop:
          oneOf:
            - type: string
            - type: array
              items:
                type: string
              maxItems: 5
          default: null
          description: >-
            Stop words, which will halt the output when a full match is found.
            The matched words themselves will not be output. A maximum of 5
            strings is allowed, and each string must not exceed 32 bytes
        stream:
          type: boolean
          default: false
          description: >-
            Whether to return the response in a streaming fashion. Default is
            false.
        stream_options:
          type: object
          description: Options for streaming responses
          properties:
            include_usage:
              type: boolean
              default: false
              description: >-
                If set, an additional chunk will be streamed before the data:
                [DONE] message. The usage field on this chunk shows the token
                usage statistics for the entire request, and the choices field
                will always be an empty array. All other chunks will also
                include a usage field, but with a null value. NOTE: If the
                stream is interrupted, you may not receive the final usage chunk
                which contains the total token usage for the request
        tools:
          type: array
          description: A list of tools the model may call
          items:
            $ref: '#/components/schemas/ToolDefinition'
        prompt_cache_key:
          type: string
          default: null
          description: >-
            Used to cache responses for similar requests to optimize cache hit
            rates. For Coding Agents, this is typically a session id or task id
            representing a single session; if the session is exited and later
            resumed, this value should remain the same. For Kimi Code Plan, this
            field is required to improve cache hit rates. For other agents
            involving multi-turn conversations, it is also recommended to
            implement this field
        safety_identifier:
          type: string
          description: >-
            A stable identifier used to help detect users of your application
            that may be violating usage policies. The ID should be a string that
            uniquely identifies each user. It is recommended to hash the
            username or email address to avoid sending any identifying
            information
        tool_choice:
          oneOf:
            - type: string
              enum:
                - auto
                - none
                - required
              description: >-
                auto: the model decides whether to call tools; none: no tool
                calls; required: force a tool call
            - type: object
              description: Force a specific tool call
              properties:
                type:
                  type: string
                  enum:
                    - function
                function:
                  type: object
                  properties:
                    name:
                      type: string
                      description: The name of the function to call
                  required:
                    - name
              required:
                - type
                - function
          description: >-
            Controls whether the model calls tools. `auto` (default): the model
            decides whether to call tools; `none`: no tool calls; `required`:
            force a tool call; or pass an object specifying a particular
            function to force that tool call.
    KimiK3Message:
      oneOf:
        - $ref: '#/components/schemas/Message'
          title: Standard message
        - $ref: '#/components/schemas/KimiK3DynamicToolMessage'
          title: Dynamic tool message
      description: >-
        A Kimi K3 conversation message. Supports both standard messages and
        system messages that omit content and declare dynamically loaded tools
        through tools.
    ChatRequestBase:
      type: object
      properties:
        logprobs:
          type: boolean
          default: false
          description: >-
            Whether to return log probabilities of the output tokens. If true,
            the log probability of each output token is returned in the logprobs
            field of the response message.
        top_logprobs:
          type: integer
          minimum: 0
          maximum: 20
          description: >-
            An integer between 0 and 20 specifying the number of most likely
            tokens to return at each token position, each with an associated log
            probability. logprobs must be set to true when this parameter is
            used.
        prediction:
          type: object
          description: >-
            Configuration for a Predicted Output, which can greatly improve
            response times when large parts of the model response are known
            ahead of time (for example, regenerating a file with only minor
            changes).
          properties:
            type:
              type: string
              enum:
                - content
              description: >-
                The type of the predicted content. Currently only content is
                supported.
            content:
              oneOf:
                - type: string
                - type: array
                  items:
                    type: object
              description: >-
                The static predicted output content that should be matched when
                generating the model response, such as the content of a text
                file being regenerated. Accepts a string or an array of content
                parts (text parts only).
        messages:
          type: array
          description: >-
            A list of messages in the conversation so far. Each element has the
            format {"role": "user", "content": "Hello"}. role supports system,
            user, assistant, or tool. content must not be empty. The content
            field can be a string or an array[object] (for multimodal input).
          items:
            $ref: '#/components/schemas/Message'
        max_tokens:
          type: integer
          deprecated: true
          description: Deprecated, please refer to max_completion_tokens
        max_completion_tokens:
          type: integer
          description: >-
            The maximum number of tokens to generate for the chat completion.
            The default varies by model: for Kimi K3 it defaults to 131072 and
            can be set up to 1048576. If the result reaches the maximum number
            of tokens without ending, the finish reason will be "length";
            otherwise, it will be "stop". This refers to the length of tokens
            you expect us to return, not the total length of input plus output.
            If input plus max_completion_tokens exceeds the model context
            window, the API returns invalid_request_error.
        response_format:
          type: object
          description: >-
            Controls the model output format. Default is {"type": "text"} for
            plain text output. Set to {"type": "json_object"} to enable JSON
            mode, ensuring output is a valid JSON object (you must guide the
            model to output JSON in the prompt). Set to {"type": "json_schema"}
            to enable Structured Output, constraining output to match a
            specified JSON Schema (recommended, requires the json_schema field).
            If you encounter schema validation issues, please submit feedback at
            walle GitHub Issues (https://github.com/MoonshotAI/walle/issues).
          properties:
            type:
              type: string
              enum:
                - text
                - json_object
                - json_schema
              description: >-
                Output format type. text: default, plain text output;
                json_object: ensures output is a valid JSON object; json_schema:
                constrains output to match a specified JSON Schema (recommended,
                requires the json_schema field)
            json_schema:
              type: object
              description: >-
                Used when type is json_schema. Defines the JSON Schema that the
                output should conform to.
              properties:
                name:
                  type: string
                  description: Schema name for identification
                strict:
                  type: boolean
                  default: true
                  description: >-
                    Whether to strictly constrain output according to the
                    schema. Defaults to true. When true, the schema must conform
                    to the MFJS specification; non-conforming schemas will
                    return errors or warnings. When false, only guarantees the
                    output is a valid JSON object without enforcing internal
                    structure.
                schema:
                  type: object
                  description: >-
                    The JSON Schema object defining the structure the output
                    should conform to. Must conform to MFJS (Moonshot Flavored
                    JSON Schema) specification. You can use the walle CLI tool
                    to validate: go install
                    github.com/moonshotai/walle/cmd/walle@latest && walle
                    -schema 'your_schema' -level strict
                  additionalProperties: true
              required:
                - name
                - schema
        stop:
          oneOf:
            - type: string
            - type: array
              items:
                type: string
              maxItems: 5
          default: null
          description: >-
            Stop words, which will halt the output when a full match is found.
            The matched words themselves will not be output. A maximum of 5
            strings is allowed, and each string must not exceed 32 bytes
        stream:
          type: boolean
          default: false
          description: >-
            Whether to return the response in a streaming fashion. Default is
            false.
        stream_options:
          type: object
          description: Options for streaming responses
          properties:
            include_usage:
              type: boolean
              default: false
              description: >-
                If set, an additional chunk will be streamed before the data:
                [DONE] message. The usage field on this chunk shows the token
                usage statistics for the entire request, and the choices field
                will always be an empty array. All other chunks will also
                include a usage field, but with a null value. NOTE: If the
                stream is interrupted, you may not receive the final usage chunk
                which contains the total token usage for the request
        tools:
          type: array
          description: A list of tools the model may call
          items:
            $ref: '#/components/schemas/ToolDefinition'
        prompt_cache_key:
          type: string
          default: null
          description: >-
            Used to cache responses for similar requests to optimize cache hit
            rates. For Coding Agents, this is typically a session id or task id
            representing a single session; if the session is exited and later
            resumed, this value should remain the same. For Kimi Code Plan, this
            field is required to improve cache hit rates. For other agents
            involving multi-turn conversations, it is also recommended to
            implement this field
        safety_identifier:
          type: string
          description: >-
            A stable identifier used to help detect users of your application
            that may be violating usage policies. The ID should be a string that
            uniquely identifies each user. It is recommended to hash the
            username or email address to avoid sending any identifying
            information
        tool_choice:
          oneOf:
            - type: string
              enum:
                - auto
                - none
                - required
              description: >-
                auto: the model decides whether to call tools; none: no tool
                calls; required: force a tool call
            - type: object
              description: Force a specific tool call
              properties:
                type:
                  type: string
                  enum:
                    - function
                function:
                  type: object
                  properties:
                    name:
                      type: string
                      description: The name of the function to call
                  required:
                    - name
              required:
                - type
                - function
          description: >-
            Controls whether the model calls tools. `auto` (default): the model
            decides whether to call tools; `none`: no tool calls; `required`:
            force a tool call; or pass an object specifying a particular
            function to force that tool call.
      required:
        - messages
    ChoiceDelta:
      type: object
      properties:
        index:
          type: integer
          description: Choice index
        delta:
          type: object
          description: Incremental content object
          properties:
            role:
              type: string
              description: Message role (only present in the first chunk)
            content:
              type: string
              description: Message content fragment
            tool_calls:
              type: array
              description: Tool calls initiated by the model
              items:
                type: object
                properties:
                  id:
                    type: string
                  type:
                    type: string
                    enum:
                      - function
                  function:
                    type: object
                    properties:
                      name:
                        type: string
                      arguments:
                        type: string
                        description: JSON string of function arguments
        finish_reason:
          type:
            - string
            - 'null'
          enum:
            - stop
            - length
            - tool_calls
            - null
          description: Stop reason, only present in the final chunk
        usage:
          type: object
          description: Token usage statistics (optional)
          properties:
            prompt_tokens:
              type: integer
              description: Number of tokens in the prompt
            completion_tokens:
              type: integer
              description: Number of tokens in the completion
            total_tokens:
              type: integer
              description: Total number of tokens used
    ToolDefinition:
      type: object
      properties:
        type:
          type: string
          enum:
            - function
        function:
          type: object
          properties:
            name:
              type: string
              description: >-
                Function name. Must follow the regex:
                ^[a-zA-Z_][a-zA-Z0-9-_]{0,127}$
              pattern: ^[a-zA-Z_][a-zA-Z0-9-_]{0,127}$
            description:
              type: string
              description: Description of what the function does
            parameters:
              type: object
              description: >-
                Function parameters as JSON Schema. Must conform to the [MFJS
                (Moonshot Flavored JSON Schema)
                specification](https://github.com/MoonshotAI/walle/blob/main/docs/mfjs-spec.md).
              additionalProperties: true
            strict:
              type: boolean
              default: true
              description: >-
                Whether to strictly constrain tool call arguments according to
                the parameters schema. Defaults to true. When false, only
                guarantees the output is a valid JSON object without enforcing
                internal structure.
          required:
            - name
            - parameters
      required:
        - type
        - function
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
    KimiK3DynamicToolMessage:
      type: object
      description: >-
        A Kimi K3 dynamic tool loading message. This message must use the system
        role, declares tools available to subsequent conversation turns from its
        position, and does not include a content field.
      properties:
        role:
          type: string
          enum:
            - system
          description: The role of a dynamic tool loading message. Always system.
        tools:
          type: array
          description: Tools available for the model to call from this message onward
          items:
            $ref: '#/components/schemas/ToolDefinition'
      required:
        - role
        - tools
      additionalProperties: false
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        The Authorization header expects a Bearer token. Use an MOONSHOT_API_KEY
        as the token. This is a server-side secret key. Generate one on the [API
        keys page](https://platform.kimi.ai/console/api-keys) in your dashboard.

````