API Reference
Lists Models
Lists Models

GET /models

Lists the currently available models, and provides basic information about each one such as the owner and availability. Check Models & Pricing for our currently supported models.

Responses​
200

OK, returns A list of models

application/json

Schema
Example (from schema)
Example

Schema

object stringrequiredPossible values: [list]

data
Model[]
required
Array [

id stringrequiredThe model identifier, which can be referenced in the API endpoints.

object stringrequiredPossible values: [model]

The object type, which is always "model".

owned_by stringrequiredThe organization that owns the model.

]

{
  "object": "list",
  "data": [
    {
      "id": "string",
      "object": "model",
      "owned_by": "string"
    }
  ]
}

{
  "object": "list",
  "data": [
    {
      "id": "deepseek-v4-flash",
      "object": "model",
      "owned_by": "deepseek"
    },
    {
      "id": "deepseek-v4-pro",
      "object": "model",
      "owned_by": "deepseek"
    }
  ]
}

Loading...
