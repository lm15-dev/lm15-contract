---
meta:
  title: Count input tokens
  description: API reference for counting input tokens with POST /v1/responses/input_tokens.
  keywords: Responses API, count input tokens, token counting, POST /responses input_tokens, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/responses/count-input-tokens
  target: aidmc
---

# Count input tokens

Count the tokens in the fully rendered input for a Responses request, without generating or storing a response. The count includes resolved `previous_response_id` history, current instructions and tools, media, and server-injected prompt scaffolding. Conversation resources are not supported.

```openapi-schema
method: POST
path: /responses/input_tokens
operation:
  operationId: countResponseInputTokens
  tags:
  - Responses
  summary: Count tokens in the fully rendered input for a Responses request without generating or storing a response.
  requestBody:
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CreateResponse'
  responses:
    '200':
      description: Success
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TokenCountsResource'
components:
  schemas: {}
page_linked_schemas:
  Annotation: /docs/api-reference/responses/schemas#annotation
  CompactionSummaryItemParam: /docs/api-reference/responses/schemas#compaction-summary-item-param
  ContextManagementParam: /docs/api-reference/responses/schemas#context-management-param
  CreateModelResponseProperties: /docs/api-reference/responses/schemas#create-model-response-properties
  CreateResponse: /docs/api-reference/responses/schemas#create-response
  DetailEnum: /docs/api-reference/responses/schemas#detail-enum
  EasyInputMessage: /docs/api-reference/responses/schemas#easy-input-message
  EmptyModelParam: /docs/api-reference/responses/schemas#empty-model-param
  FileCitationBody: /docs/api-reference/responses/schemas#file-citation-body
  FileDetailEnum: /docs/api-reference/responses/schemas#file-detail-enum
  FileInputDetail: /docs/api-reference/responses/schemas#file-input-detail
  FilePath: /docs/api-reference/responses/schemas#file-path
  FunctionCallItemStatus: /docs/api-reference/responses/schemas#function-call-item-status
  FunctionCallOutputContentListParam: /docs/api-reference/responses/schemas#function-call-output-content-list-param
  FunctionCallOutputItemParam: /docs/api-reference/responses/schemas#function-call-output-item-param
  FunctionCallOutputTextParam: /docs/api-reference/responses/schemas#function-call-output-text-param
  FunctionTool: /docs/api-reference/responses/schemas#function-tool
  FunctionToolCall: /docs/api-reference/responses/schemas#function-tool-call
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
  OutputMessage: /docs/api-reference/responses/schemas#output-message
  OutputMessageContent: /docs/api-reference/responses/schemas#output-message-content
  OutputTextContent: /docs/api-reference/responses/schemas#output-text-content
  Prompt: /docs/api-reference/responses/schemas#prompt
  Reasoning: /docs/api-reference/responses/schemas#reasoning
  ReasoningEffort: /docs/api-reference/responses/schemas#reasoning-effort
  ReasoningItemParam: /docs/api-reference/responses/schemas#reasoning-item-param
  ReasoningTextContent: /docs/api-reference/responses/schemas#reasoning-text-content
  RefusalContent: /docs/api-reference/responses/schemas#refusal-content
  ResponseFormatJsonObject: /docs/api-reference/responses/schemas#response-format-json-object
  ResponseFormatJsonSchemaSchema: /docs/api-reference/responses/schemas#response-format-json-schema-schema
  ResponseFormatText: /docs/api-reference/responses/schemas#response-format-text
  ResponsePromptVariables: /docs/api-reference/responses/schemas#response-prompt-variables
  ResponseProperties: /docs/api-reference/responses/schemas#response-properties
  ResponseStreamOptions: /docs/api-reference/responses/schemas#response-stream-options
  ResponseTextParam: /docs/api-reference/responses/schemas#response-text-param
  ServiceTier: /docs/api-reference/responses/schemas#service-tier
  SummaryTextContent: /docs/api-reference/responses/schemas#summary-text-content
  TextResponseFormatConfiguration: /docs/api-reference/responses/schemas#text-response-format-configuration
  TextResponseFormatJsonSchema: /docs/api-reference/responses/schemas#text-response-format-json-schema
  TokenCountsResource: /docs/api-reference/responses/schemas#token-counts-resource
  Tool: /docs/api-reference/responses/schemas#tool
  ToolChoiceOptions: /docs/api-reference/responses/schemas#tool-choice-options
  ToolChoiceParam: /docs/api-reference/responses/schemas#tool-choice-param
  ToolSearchCallItemParam: /docs/api-reference/responses/schemas#tool-search-call-item-param
  ToolSearchExecutionType: /docs/api-reference/responses/schemas#tool-search-execution-type
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

```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses/input_tokens",
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
curl -X POST "https://api.meta.ai/v1/responses/input_tokens" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "input": "What is the capital of France?"
}'
```

<!-- openapi-schemas-page: /docs/api-reference/responses/schemas -->

For usage examples and rate-limit guidance, see the [Responses](/docs/protocols/responses) feature page.