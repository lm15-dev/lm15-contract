---
meta:
  title: Status API reference
  description: API reference for the unauthenticated /v1/status service-health endpoint.
  keywords: status, health, service status, model availability, /v1/status, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/status
  target: aidmc
---

# Status

Report overall API status and per-model availability. This endpoint is unauthenticated: no API key is required. Check it for service disruptions before retrying failed requests; see [error handling](/docs/error-handling) for retry guidance.

```openapi-schema
method: GET
path: /status
operation:
  operationId: getStatus
  tags:
  - Status
  summary: Get API status.
  description: Returns overall API status and public model health. Does not require authentication.
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/StatusResponse'
components:
  schemas:
    IncidentHistoryItem:
      type: object
      properties:
        date:
          type: string
          description: ISO-8601 date of the incident.
        title:
          type: string
          description: Short title of the incident.
        status:
          type: string
          description: Current status of the incident.
        message:
          type: string
          nullable: true
          description: Optional detailed message about the incident.
      required:
      - date
      - title
      - status
      title: Incident history item
      description: A single incident in the service incident history.
    ModelStatusItem:
      type: object
      properties:
        id:
          type: string
          description: Identifier of the model.
        status:
          type: string
          enum:
          - operational
          - degraded
          - outage
          description: Current status of the model.
        message:
          type: string
          nullable: true
          description: Optional human-readable message describing the model status.
      required:
      - id
      - status
      title: Model status item
      description: Status for a single public model.
    StatusResponse:
      type: object
      properties:
        is_alive:
          type: boolean
          description: Whether the API is currently serving requests.
        service_status:
          type: string
          enum:
          - operational
          - degraded
          - outage
          default: operational
          description: Overall status of the service.
        service_message:
          type: string
          nullable: true
          description: Optional human-readable message describing the current service status.
        updated_at:
          type: string
          nullable: true
          description: ISO-8601 timestamp of when the status was last updated.
        incident_history:
          type: array
          nullable: true
          items:
            $ref: '#/components/schemas/IncidentHistoryItem'
          description: Recent incident history, most recent first.
        model_statuses:
          type: array
          nullable: true
          items:
            $ref: '#/components/schemas/ModelStatusItem'
          description: Per-model status for public models.
      required:
      - is_alive
      - service_status
      title: Status response
      description: Overall API status and public model health.
```

```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/status",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/status" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```