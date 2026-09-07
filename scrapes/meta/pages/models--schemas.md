---
meta:
  title: Models schemas
  description: Full schema and model definitions referenced by the Models API endpoints.
  keywords: models, schemas, types, API reference, schema reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/models/schemas
  target: aidmc
---

# Models schemas

The full schema and model definitions referenced by the [Models](/docs/api-reference/models/list-models) endpoints. Each endpoint page links here for the detailed shape of its response objects.

## Schemas

```openapi-schema
kind: schema
name: ListModelsResponse
schema:
  type: object
  properties:
    object:
      type: string
      enum:
      - list
      default: list
      description: Object type; always `list`.
    data:
      type: array
      items:
        $ref: '#/components/schemas/Model'
      description: List of model objects.
  required:
  - object
  - data
  title: List models response
  description: Response containing the list of available models.
components:
  schemas: {}
page_linked_schemas:
  ListModelsResponse: '#list-models-response'
  Model: '#model'
```
```openapi-schema
kind: schema
name: Model
schema:
  type: object
  properties:
    id:
      type: string
      description: Identifier for the model.
    object:
      type: string
      enum:
      - model
      default: model
      description: Object type; always `model`.
    created:
      type: integer
      description: Unix timestamp (seconds) at which the model was created.
    owned_by:
      type: string
      description: Owner of the model.
    metadata:
      type: object
      additionalProperties: true
      nullable: true
      description: Client-specific metadata, present only when the request supplies a recognized `client` query parameter. Keyed by client type.
  required:
  - id
  - object
  - created
  - owned_by
  title: Model
  description: Describes a model available for use with the API.
components:
  schemas: {}
page_linked_schemas:
  Model: '#model'
```