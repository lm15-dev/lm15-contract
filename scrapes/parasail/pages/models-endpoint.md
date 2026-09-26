> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/api-reference/models-endpoint.md).

# Models Endpoint

List available models on the Parasail platform using the /v1/models endpoint.

List all available models on the Parasail platform. This endpoint works on the standard gateway and serves both the chat completions and Responses APIs.

## Endpoint

```
GET https://api.parasail.io/v1/models
```

## Authentication

Pass your API key in the `Authorization` header:

```
Authorization: Bearer <PARASAIL_API_KEY>
```

See [Authentication](/parasail-docs/api-reference/authentication.md) for how to create and store a key.

## Request

### cURL

```bash
curl https://api.parasail.io/v1/models \
  -H "Authorization: Bearer $PARASAIL_API_KEY"
```

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>"
)

models = client.models.list()
for model in models.data:
    print(model.id)
```

## Response

A successful request returns a list of model objects:

```json
{
  "object": "list",
  "data": [
    {
      "id": "parasail-deepseek-r1",
      "object": "model",
      "created": 1727900000,
      "owned_by": "parasail"
    }
  ]
}
```

| Field             | Description                                   |
| ----------------- | --------------------------------------------- |
| `data[].id`       | Model ID to pass as `model` in other requests |
| `data[].object`   | Always `model`                                |
| `data[].owned_by` | Owner of the model                            |

The list is returned in full in a single response—this endpoint is not paginated. See the [OpenAI models reference](https://platform.openai.com/docs/api-reference/models) for field semantics.

## Model types

Parasail supports several types of models:

* **Serverless models**—prefixed with `parasail-` (for example, `parasail-deepseek-r1`). Available on the serverless tier with token-based pricing.
* **Dedicated deployments**—use the deployment name as the model ID. Available on dedicated instances.
* **HuggingFace models**—any HuggingFace transformer can be used with batch or dedicated endpoints by specifying the full HuggingFace ID (for example, `NousResearch/DeepHermes-3-Mistral-24B-Preview`).

## Error responses

Errors use OpenAI-compatible status codes and a JSON body with an `error` object (`message`, `type`, `code`).

| Status Code | Description                                          |
| ----------- | ---------------------------------------------------- |
| `401`       | Missing or invalid API key                           |
| `403`       | API key lacks access to list models                  |
| `429`       | Rate limit or quota exceeded—back off and retry      |
| `500`       | Internal server error—retry with exponential backoff |

## Next steps

* [Chat completions API](/parasail-docs/api-reference/chat-completions.md)—use a model ID to run inference
* [Serverless overview](/parasail-docs/products/overview.md)—list of available serverless models
* [Model selection](/parasail-docs/guides/model-recommendations.md)—choose models by workload and check availability
* [Pricing](/parasail-docs/billing/pricing.md)—pricing by model parameter count
