---
meta:
  title: Create a chat completion
  description: API reference for generating a model response with POST /v1/chat/completions.
  keywords: chat completions, create chat completion, POST /chat/completions, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/chat-completions/create-chat-completion
  target: aidmc
---

# Create a chat completion

Generate a model response from a conversation supplied as a list of messages.

```openapi-schema
method: POST
path: /chat/completions
operation:
  operationId: createChatCompletion
  tags:
  - Chat
  summary: Generate a chat completion.
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CreateChatCompletionRequest'
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CreateChatCompletionResponse'
        text/event-stream:
          schema:
            $ref: '#/components/schemas/CreateChatCompletionStreamResponse'
components:
  schemas: {}
page_linked_schemas:
  ChatCompletionMessageToolCall: /docs/api-reference/chat-completions/schemas#chat-completion-message-tool-call
  ChatCompletionMessageToolCallChunk: /docs/api-reference/chat-completions/schemas#chat-completion-message-tool-call-chunk
  ChatCompletionMessageToolCalls: /docs/api-reference/chat-completions/schemas#chat-completion-message-tool-calls
  ChatCompletionRequestAssistantMessage: /docs/api-reference/chat-completions/schemas#chat-completion-request-assistant-message
  ChatCompletionRequestAssistantMessageContentPart: /docs/api-reference/chat-completions/schemas#chat-completion-request-assistant-message-content-part
  ChatCompletionRequestDeveloperMessage: /docs/api-reference/chat-completions/schemas#chat-completion-request-developer-message
  ChatCompletionRequestMessage: /docs/api-reference/chat-completions/schemas#chat-completion-request-message
  ChatCompletionRequestMessageContentPartAudio: /docs/api-reference/chat-completions/schemas#chat-completion-request-message-content-part-audio
  ChatCompletionRequestMessageContentPartFile: /docs/api-reference/chat-completions/schemas#chat-completion-request-message-content-part-file
  ChatCompletionRequestMessageContentPartImage: /docs/api-reference/chat-completions/schemas#chat-completion-request-message-content-part-image
  ChatCompletionRequestMessageContentPartRefusal: /docs/api-reference/chat-completions/schemas#chat-completion-request-message-content-part-refusal
  ChatCompletionRequestMessageContentPartText: /docs/api-reference/chat-completions/schemas#chat-completion-request-message-content-part-text
  ChatCompletionRequestMessageContentPartVideo: /docs/api-reference/chat-completions/schemas#chat-completion-request-message-content-part-video
  ChatCompletionRequestSystemMessage: /docs/api-reference/chat-completions/schemas#chat-completion-request-system-message
  ChatCompletionRequestSystemMessageContentPart: /docs/api-reference/chat-completions/schemas#chat-completion-request-system-message-content-part
  ChatCompletionRequestToolMessage: /docs/api-reference/chat-completions/schemas#chat-completion-request-tool-message
  ChatCompletionRequestToolMessageContentPart: /docs/api-reference/chat-completions/schemas#chat-completion-request-tool-message-content-part
  ChatCompletionRequestUserMessage: /docs/api-reference/chat-completions/schemas#chat-completion-request-user-message
  ChatCompletionRequestUserMessageContentPart: /docs/api-reference/chat-completions/schemas#chat-completion-request-user-message-content-part
  ChatCompletionResponseMessage: /docs/api-reference/chat-completions/schemas#chat-completion-response-message
  ChatCompletionStreamOptions: /docs/api-reference/chat-completions/schemas#chat-completion-stream-options
  ChatCompletionStreamResponseDelta: /docs/api-reference/chat-completions/schemas#chat-completion-stream-response-delta
  ChatCompletionTokenLogprob: /docs/api-reference/chat-completions/schemas#chat-completion-token-logprob
  ChatCompletionTool: /docs/api-reference/chat-completions/schemas#chat-completion-tool
  ChatCompletionToolChoiceOption: /docs/api-reference/chat-completions/schemas#chat-completion-tool-choice-option
  CompletionUsage: /docs/api-reference/chat-completions/schemas#completion-usage
  CreateChatCompletionRequest: /docs/api-reference/chat-completions/schemas#create-chat-completion-request
  CreateChatCompletionResponse: /docs/api-reference/chat-completions/schemas#create-chat-completion-response
  CreateChatCompletionStreamResponse: /docs/api-reference/chat-completions/schemas#create-chat-completion-stream-response
  CreateModelResponseProperties: /docs/api-reference/chat-completions/schemas#create-model-response-properties
  FunctionObject: /docs/api-reference/chat-completions/schemas#function-object
  FunctionParameters: /docs/api-reference/chat-completions/schemas#function-parameters
  Metadata: /docs/api-reference/chat-completions/schemas#metadata
  ModelResponseProperties: /docs/api-reference/chat-completions/schemas#model-response-properties
  ParallelToolCalls: /docs/api-reference/chat-completions/schemas#parallel-tool-calls
  ReasoningEffort: /docs/api-reference/chat-completions/schemas#reasoning-effort
  ResponseFormatJsonObject: /docs/api-reference/chat-completions/schemas#response-format-json-object
  ResponseFormatJsonSchema: /docs/api-reference/chat-completions/schemas#response-format-json-schema
  ResponseFormatJsonSchemaSchema: /docs/api-reference/chat-completions/schemas#response-format-json-schema-schema
  ResponseFormatText: /docs/api-reference/chat-completions/schemas#response-format-text
  ResponseModalities: /docs/api-reference/chat-completions/schemas#response-modalities
  ServiceTier: /docs/api-reference/chat-completions/schemas#service-tier
  StopConfiguration: /docs/api-reference/chat-completions/schemas#stop-configuration
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "user",
            "content": "What are three differences between TCP and UDP?",
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "messages": [
            {
                "role": "user",
                "content": "What are three differences between TCP and UDP?",
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "messages": [
    {
      "role": "user",
      "content": "What are three differences between TCP and UDP?"
    }
  ]
}'
```

<!-- openapi-schemas-page: /docs/api-reference/chat-completions/schemas -->

For usage examples, streaming, multi-turn conversations, and parameter guidance, see the [Chat completion](/docs/protocols/chat-completions) feature page.