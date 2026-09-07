---
meta:
  title: Cancel a response
  description: API reference for cancelling an in-progress model response with POST /v1/responses/{response_id}/cancel.
  keywords: Responses API, cancel response, POST /responses cancel, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/responses/cancel-response
  target: aidmc
---

# Cancel a response

Cancel an in-progress response. Only responses created for background processing can be cancelled.

```openapi-schema
method: POST
path: /responses/{response_id}/cancel
operation:
  operationId: cancelResponse
  tags:
  - Responses
  summary: Cancel a background model response by ID.
  description: 'Only responses created with `background: true` can be cancelled. Returns the cancelled response.'
  parameters:
  - in: path
    name: response_id
    required: true
    schema:
      type: string
    description: The ID of the response to cancel.
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CancelResponseResponse'
components:
  schemas: {}
page_linked_schemas:
  Annotation: /docs/api-reference/responses/schemas#annotation
  CancelResponseResponse: /docs/api-reference/responses/schemas#cancel-response-response
  CompactionBody: /docs/api-reference/responses/schemas#compaction-body
  EmptyModelParam: /docs/api-reference/responses/schemas#empty-model-param
  FileCitationBody: /docs/api-reference/responses/schemas#file-citation-body
  FileInputDetail: /docs/api-reference/responses/schemas#file-input-detail
  FilePath: /docs/api-reference/responses/schemas#file-path
  FunctionAndCustomToolCallOutput: /docs/api-reference/responses/schemas#function-and-custom-tool-call-output
  FunctionCallOutputStatusEnum: /docs/api-reference/responses/schemas#function-call-output-status-enum
  FunctionCallStatus: /docs/api-reference/responses/schemas#function-call-status
  FunctionTool: /docs/api-reference/responses/schemas#function-tool
  FunctionToolCall: /docs/api-reference/responses/schemas#function-tool-call
  FunctionToolCallOutput: /docs/api-reference/responses/schemas#function-tool-call-output
  FunctionToolCallOutputResource: /docs/api-reference/responses/schemas#function-tool-call-output-resource
  ImageDetail: /docs/api-reference/responses/schemas#image-detail
  InputFileContent: /docs/api-reference/responses/schemas#input-file-content
  InputImageContent: /docs/api-reference/responses/schemas#input-image-content
  InputTextContent: /docs/api-reference/responses/schemas#input-text-content
  LogProb: /docs/api-reference/responses/schemas#log-prob
  MessagePhase: /docs/api-reference/responses/schemas#message-phase
  OutputItem: /docs/api-reference/responses/schemas#output-item
  OutputMessage: /docs/api-reference/responses/schemas#output-message
  OutputMessageContent: /docs/api-reference/responses/schemas#output-message-content
  OutputTextContent: /docs/api-reference/responses/schemas#output-text-content
  ReasoningItem: /docs/api-reference/responses/schemas#reasoning-item
  ReasoningTextContent: /docs/api-reference/responses/schemas#reasoning-text-content
  RefusalContent: /docs/api-reference/responses/schemas#refusal-content
  SummaryTextContent: /docs/api-reference/responses/schemas#summary-text-content
  Tool: /docs/api-reference/responses/schemas#tool
  ToolSearchCall: /docs/api-reference/responses/schemas#tool-search-call
  ToolSearchExecutionType: /docs/api-reference/responses/schemas#tool-search-execution-type
  ToolSearchOutput: /docs/api-reference/responses/schemas#tool-search-output
  ToolSearchToolParam: /docs/api-reference/responses/schemas#tool-search-tool-param
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

response = client.responses.cancel("resp_abc123")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/responses/resp_abc123/cancel",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/responses/resp_abc123/cancel" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```

<!-- openapi-schemas-page: /docs/api-reference/responses/schemas -->

For usage examples and background-processing guidance, see the [Responses](/docs/protocols/responses) feature page.