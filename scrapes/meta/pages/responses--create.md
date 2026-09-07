---
meta:
  title: Create a response
  description: API reference for creating a model response with POST /v1/responses.
  keywords: Responses API, create response, POST /responses, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/responses/create-response
  target: aidmc
---

# Create a response

Create a model response. Optionally reference a previous response by ID to continue a multi-turn conversation with server-managed state, instead of resending the full message history.

```openapi-schema
method: POST
path: /responses
operation:
  operationId: createResponse
  tags:
  - Responses
  summary: Generate a model response.
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CreateResponse'
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Response'
        text/event-stream:
          schema:
            $ref: '#/components/schemas/ResponseStreamEvent'
components:
  schemas: {}
page_linked_schemas:
  Annotation: /docs/api-reference/responses/schemas#annotation
  CompactionBody: /docs/api-reference/responses/schemas#compaction-body
  CompactionSummaryItemParam: /docs/api-reference/responses/schemas#compaction-summary-item-param
  ContextManagementParam: /docs/api-reference/responses/schemas#context-management-param
  Conversation-2: /docs/api-reference/responses/schemas#conversation-2
  CreateModelResponseProperties: /docs/api-reference/responses/schemas#create-model-response-properties
  CreateResponse: /docs/api-reference/responses/schemas#create-response
  DetailEnum: /docs/api-reference/responses/schemas#detail-enum
  EasyInputMessage: /docs/api-reference/responses/schemas#easy-input-message
  EmptyModelParam: /docs/api-reference/responses/schemas#empty-model-param
  FileCitationBody: /docs/api-reference/responses/schemas#file-citation-body
  FileDetailEnum: /docs/api-reference/responses/schemas#file-detail-enum
  FileInputDetail: /docs/api-reference/responses/schemas#file-input-detail
  FilePath: /docs/api-reference/responses/schemas#file-path
  FunctionAndCustomToolCallOutput: /docs/api-reference/responses/schemas#function-and-custom-tool-call-output
  FunctionCallItemStatus: /docs/api-reference/responses/schemas#function-call-item-status
  FunctionCallOutputContentListParam: /docs/api-reference/responses/schemas#function-call-output-content-list-param
  FunctionCallOutputItemParam: /docs/api-reference/responses/schemas#function-call-output-item-param
  FunctionCallOutputStatusEnum: /docs/api-reference/responses/schemas#function-call-output-status-enum
  FunctionCallOutputTextParam: /docs/api-reference/responses/schemas#function-call-output-text-param
  FunctionCallStatus: /docs/api-reference/responses/schemas#function-call-status
  FunctionTool: /docs/api-reference/responses/schemas#function-tool
  FunctionToolCall: /docs/api-reference/responses/schemas#function-tool-call
  FunctionToolCallOutput: /docs/api-reference/responses/schemas#function-tool-call-output
  FunctionToolCallOutputResource: /docs/api-reference/responses/schemas#function-tool-call-output-resource
  ImageDetail: /docs/api-reference/responses/schemas#image-detail
  IncludeEnum: /docs/api-reference/responses/schemas#include-enum
  InputAudioContent: /docs/api-reference/responses/schemas#input-audio-content
  InputContent: /docs/api-reference/responses/schemas#input-content
  InputFileContent: /docs/api-reference/responses/schemas#input-file-content
  InputFileContentParam: /docs/api-reference/responses/schemas#input-file-content-param
  InputImageContent: /docs/api-reference/responses/schemas#input-image-content
  InputImageContentParamAutoParam: /docs/api-reference/responses/schemas#input-image-content-param-auto-param
  InputItem: /docs/api-reference/responses/schemas#input-item
  InputMessage: /docs/api-reference/responses/schemas#input-message
  InputMessageContentList: /docs/api-reference/responses/schemas#input-message-content-list
  InputParam: /docs/api-reference/responses/schemas#input-param
  InputTextContent: /docs/api-reference/responses/schemas#input-text-content
  InputTextContentParam: /docs/api-reference/responses/schemas#input-text-content-param
  InputVideoContent: /docs/api-reference/responses/schemas#input-video-content
  Item: /docs/api-reference/responses/schemas#item
  ItemReferenceParam: /docs/api-reference/responses/schemas#item-reference-param
  LogProb: /docs/api-reference/responses/schemas#log-prob
  MessagePhase: /docs/api-reference/responses/schemas#message-phase
  Metadata: /docs/api-reference/responses/schemas#metadata
  ModelResponseProperties: /docs/api-reference/responses/schemas#model-response-properties
  OutputContent: /docs/api-reference/responses/schemas#output-content
  OutputItem: /docs/api-reference/responses/schemas#output-item
  OutputMessage: /docs/api-reference/responses/schemas#output-message
  OutputMessageContent: /docs/api-reference/responses/schemas#output-message-content
  OutputTextContent: /docs/api-reference/responses/schemas#output-text-content
  Prompt: /docs/api-reference/responses/schemas#prompt
  Reasoning: /docs/api-reference/responses/schemas#reasoning
  ReasoningEffort: /docs/api-reference/responses/schemas#reasoning-effort
  ReasoningItem: /docs/api-reference/responses/schemas#reasoning-item
  ReasoningItemParam: /docs/api-reference/responses/schemas#reasoning-item-param
  ReasoningTextContent: /docs/api-reference/responses/schemas#reasoning-text-content
  RefusalContent: /docs/api-reference/responses/schemas#refusal-content
  Response: /docs/api-reference/responses/schemas#response
  ResponseCompletedEvent: /docs/api-reference/responses/schemas#response-completed-event
  ResponseContentPartAddedEvent: /docs/api-reference/responses/schemas#response-content-part-added-event
  ResponseContentPartDoneEvent: /docs/api-reference/responses/schemas#response-content-part-done-event
  ResponseCreatedEvent: /docs/api-reference/responses/schemas#response-created-event
  ResponseError: /docs/api-reference/responses/schemas#response-error
  ResponseErrorCode: /docs/api-reference/responses/schemas#response-error-code
  ResponseErrorEvent: /docs/api-reference/responses/schemas#response-error-event
  ResponseFailedEvent: /docs/api-reference/responses/schemas#response-failed-event
  ResponseFormatJsonObject: /docs/api-reference/responses/schemas#response-format-json-object
  ResponseFormatJsonSchemaSchema: /docs/api-reference/responses/schemas#response-format-json-schema-schema
  ResponseFormatText: /docs/api-reference/responses/schemas#response-format-text
  ResponseFunctionCallArgumentsDeltaEvent: /docs/api-reference/responses/schemas#response-function-call-arguments-delta-event
  ResponseFunctionCallArgumentsDoneEvent: /docs/api-reference/responses/schemas#response-function-call-arguments-done-event
  ResponseInProgressEvent: /docs/api-reference/responses/schemas#response-in-progress-event
  ResponseIncompleteEvent: /docs/api-reference/responses/schemas#response-incomplete-event
  ResponseLogProb: /docs/api-reference/responses/schemas#response-log-prob
  ResponseOutputItemAddedEvent: /docs/api-reference/responses/schemas#response-output-item-added-event
  ResponseOutputItemDoneEvent: /docs/api-reference/responses/schemas#response-output-item-done-event
  ResponseOutputTextAnnotationAddedEvent: /docs/api-reference/responses/schemas#response-output-text-annotation-added-event
  ResponsePromptVariables: /docs/api-reference/responses/schemas#response-prompt-variables
  ResponseProperties: /docs/api-reference/responses/schemas#response-properties
  ResponseQueuedEvent: /docs/api-reference/responses/schemas#response-queued-event
  ResponseReasoningSummaryPartAddedEvent: /docs/api-reference/responses/schemas#response-reasoning-summary-part-added-event
  ResponseReasoningSummaryPartDoneEvent: /docs/api-reference/responses/schemas#response-reasoning-summary-part-done-event
  ResponseReasoningSummaryTextDeltaEvent: /docs/api-reference/responses/schemas#response-reasoning-summary-text-delta-event
  ResponseReasoningSummaryTextDoneEvent: /docs/api-reference/responses/schemas#response-reasoning-summary-text-done-event
  ResponseReasoningTextDeltaEvent: /docs/api-reference/responses/schemas#response-reasoning-text-delta-event
  ResponseReasoningTextDoneEvent: /docs/api-reference/responses/schemas#response-reasoning-text-done-event
  ResponseRefusalDeltaEvent: /docs/api-reference/responses/schemas#response-refusal-delta-event
  ResponseRefusalDoneEvent: /docs/api-reference/responses/schemas#response-refusal-done-event
  ResponseStreamEvent: /docs/api-reference/responses/schemas#response-stream-event
  ResponseStreamOptions: /docs/api-reference/responses/schemas#response-stream-options
  ResponseTextDeltaEvent: /docs/api-reference/responses/schemas#response-text-delta-event
  ResponseTextDoneEvent: /docs/api-reference/responses/schemas#response-text-done-event
  ResponseTextParam: /docs/api-reference/responses/schemas#response-text-param
  ResponseUsage: /docs/api-reference/responses/schemas#response-usage
  ResponseWebSearchCallCompletedEvent: /docs/api-reference/responses/schemas#response-web-search-call-completed-event
  ResponseWebSearchCallInProgressEvent: /docs/api-reference/responses/schemas#response-web-search-call-in-progress-event
  ResponseWebSearchCallSearchingEvent: /docs/api-reference/responses/schemas#response-web-search-call-searching-event
  ServiceTier: /docs/api-reference/responses/schemas#service-tier
  SummaryTextContent: /docs/api-reference/responses/schemas#summary-text-content
  TextResponseFormatConfiguration: /docs/api-reference/responses/schemas#text-response-format-configuration
  TextResponseFormatJsonSchema: /docs/api-reference/responses/schemas#text-response-format-json-schema
  Tool: /docs/api-reference/responses/schemas#tool
  ToolChoiceOptions: /docs/api-reference/responses/schemas#tool-choice-options
  ToolChoiceParam: /docs/api-reference/responses/schemas#tool-choice-param
  ToolSearchCall: /docs/api-reference/responses/schemas#tool-search-call
  ToolSearchCallItemParam: /docs/api-reference/responses/schemas#tool-search-call-item-param
  ToolSearchExecutionType: /docs/api-reference/responses/schemas#tool-search-execution-type
  ToolSearchOutput: /docs/api-reference/responses/schemas#tool-search-output
  ToolSearchOutputItemParam: /docs/api-reference/responses/schemas#tool-search-output-item-param
  ToolSearchToolParam: /docs/api-reference/responses/schemas#tool-search-tool-param
  ToolsArray: /docs/api-reference/responses/schemas#tools-array
  TopLogProb: /docs/api-reference/responses/schemas#top-log-prob
  UrlCitationBody: /docs/api-reference/responses/schemas#url-citation-body
  WebSearchActionFind: /docs/api-reference/responses/schemas#web-search-action-find
  WebSearchActionOpenPage: /docs/api-reference/responses/schemas#web-search-action-open-page
  WebSearchActionSearch: /docs/api-reference/responses/schemas#web-search-action-search
  WebSearchApproximateLocation: /docs/api-reference/responses/schemas#web-search-approximate-location
  WebSearchResultItem: /docs/api-reference/responses/schemas#web-search-result-item
  WebSearchTool: /docs/api-reference/responses/schemas#web-search-tool
  WebSearchToolCall: /docs/api-reference/responses/schemas#web-search-tool-call
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input="What is the capital of France?",
)

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "input": "What is the capital of France?",
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "What is the capital of France?"
}'
```

<!-- openapi-schemas-page: /docs/api-reference/responses/schemas -->

For usage examples, `previous_response_id` patterns, and guidance on when to use the Responses API versus Chat Completions, see the [Responses](/docs/protocols/responses) feature page.