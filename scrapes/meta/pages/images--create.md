---
meta:
  title: Generate an image
  description: API reference for generating an image with POST /v1/images/generations.
  keywords: images, generate image, text-to-image, POST /images/generations, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/images/create-image
  target: aidmc
---

# Generate an image

Generate one or more images from a text prompt.

```openapi-schema
method: POST
path: /images/generations
operation:
  operationId: createImage
  tags:
  - Images
  summary: Generate one or more images from a text prompt.
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CreateImageRequest'
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ImagesResponse'
        text/event-stream:
          schema:
            $ref: '#/components/schemas/ImageGenStreamEvent'
components:
  schemas: {}
page_linked_schemas:
  CreateImageRequest: /docs/api-reference/images/schemas#create-image-request
  ImageGenCompletedEvent: /docs/api-reference/images/schemas#image-gen-completed-event
  ImageGenPartialImageEvent: /docs/api-reference/images/schemas#image-gen-partial-image-event
  ImageGenStreamEvent: /docs/api-reference/images/schemas#image-gen-stream-event
  ImageGenUsage: /docs/api-reference/images/schemas#image-gen-usage
  ImageObject: /docs/api-reference/images/schemas#image-object
  ImageToolEnablement: /docs/api-reference/images/schemas#image-tool-enablement
  ImagesResponse: /docs/api-reference/images/schemas#images-response
```

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.images.generate(
    model="muse-image-1.0",
    prompt="a watercolor painting of a red fox sitting in a snowy pine forest, soft golden morning light",
    n=1,
)

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/images/generations",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-image-1.0",
        "prompt": "a watercolor painting of a red fox sitting in a snowy pine forest, soft golden morning light",
        "n": 1,
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/images/generations" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-image-1.0",
  "prompt": "a watercolor painting of a red fox sitting in a snowy pine forest, soft golden morning light",
  "n": 1
}'
```

<!-- openapi-schemas-page: /docs/api-reference/images/schemas -->

For prompts, sizing, and worked examples, see the [Image generation](/docs/image-generation) feature page.