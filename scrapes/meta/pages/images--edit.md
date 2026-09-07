---
meta:
  title: Edit an image
  description: API reference for editing or composing images with POST /v1/images/edits.
  keywords: images, edit image, image-to-image, compose images, POST /images/edits, API reference, endpoint reference
cms:
  layout: large
  alias: /model-api/docs/api-reference/images/edit-image
  target: aidmc
---

# Edit an image

Edit, transform, or compose one or more input images, guided by a text prompt.

With the OpenAI SDK, upload the input image(s) as `multipart/form-data` — `client.images.edit(image=..., prompt=..., model=...)`, passing a list of files to compose several inputs. Over raw HTTP you can instead send a JSON body with an `images` array of `image_url`/`file_id` items (shown below); the OpenAI SDK does not send this JSON shape.

```openapi-schema
method: POST
path: /images/edits
operation:
  operationId: createImageEdit
  tags:
  - Images
  summary: Edit one or more input images from a text prompt.
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/EditImageBodyJsonParam'
      multipart/form-data:
        schema:
          $ref: '#/components/schemas/CreateImageEditRequest'
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ImagesResponse'
        text/event-stream:
          schema:
            $ref: '#/components/schemas/ImageEditStreamEvent'
components:
  schemas: {}
page_linked_schemas:
  CreateImageEditRequest: /docs/api-reference/images/schemas#create-image-edit-request
  EditImageBodyJsonParam: /docs/api-reference/images/schemas#edit-image-body-json-param
  ImageEditCompletedEvent: /docs/api-reference/images/schemas#image-edit-completed-event
  ImageEditPartialImageEvent: /docs/api-reference/images/schemas#image-edit-partial-image-event
  ImageEditStreamEvent: /docs/api-reference/images/schemas#image-edit-stream-event
  ImageGenUsage: /docs/api-reference/images/schemas#image-gen-usage
  ImageInputItem: /docs/api-reference/images/schemas#image-input-item
  ImageObject: /docs/api-reference/images/schemas#image-object
  ImageToolEnablement: /docs/api-reference/images/schemas#image-tool-enablement
  ImagesResponse: /docs/api-reference/images/schemas#images-response
```

```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/images/edits",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-image-1.0",
        "prompt": "add a small red wool hat on the fox's head, keep the snowy forest background",
        "images": [
            {
                "image_url": "data:image/webp;base64,UklGR...",
            },
        ],
        "n": 1,
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/images/edits" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-image-1.0",
  "prompt": "add a small red wool hat on the fox'\''s head, keep the snowy forest background",
  "images": [
    {
      "image_url": "data:image/webp;base64,UklGR..."
    }
  ],
  "n": 1
}'
```

<!-- openapi-schemas-page: /docs/api-reference/images/schemas -->

For reference images, multi-image composition, and worked examples, see the [Image generation](/docs/image-generation) feature page.