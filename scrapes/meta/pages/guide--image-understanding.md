---
meta:
  title: Image understanding
  description: Analyze images with text prompts using URLs, base64 encoding, or uploaded files.
  keywords: image understanding, vision, multimodal, image analysis, image_url, base64, perception grounding, localization, bounding box, coordinates
cms:
  alias: /model-api/docs/image-understanding
  target: aidmc
---

# Image understanding

Add vision to your workflow. Send images alongside a text prompt and get grounded text back you can crop, measure, or render on.

> [!NOTE] Responses API is recommended
> The [Responses API](/docs/protocols/responses) is the recommended way to send images. If your product or agent harness is built on [Chat Completions](/docs/protocols/chat-completions), image understanding is fully supported there too — see [Image understanding with Chat Completions](#chat-completions). The only difference is how the image is wrapped in the request; the model and its capabilities are identical.

## How it works {#how-it-works}

Send one or more images alongside text in a [Responses API](/docs/protocols/responses) or [chat completion](/docs/protocols/chat-completions) request. [Muse Spark](/docs/models#muse-spark) reads the visuals and returns text. Provide each image one of three ways:

- **Public URL** — a fully qualified `http`/`https` image link.
- **Base64 data URL** — the image bytes inline, no hosting required.
- **Uploaded file** — a `file_id` from the [Files API](/docs/file-handling).

> [!NOTE] Images only in user messages
> Only include images in `user`-role messages. The model does not process images attached to other roles.

Use it for:

* **Describing scenes**: generate detailed descriptions of what appears in an image.
* **Answering questions**: respond to specific queries about objects, people, or actions in an image.
* **Extracting information**: pull text, data, or key elements from charts, diagrams, or documents.
* **Analyzing content**: identify objects, understand relationships, and categorize visual information.
* **Localizing objects**: report *where* objects are as coordinates you can crop, measure, or draw overlays with. See [perception grounding](#perception-grounding).

## Image understanding with the Responses API {#responses-api}

Send images as `input_image` content blocks inside a `user` message. The `image_url` field is a plain string — a public URL or a base64 `data:` URL — or set `file_id` to reference an image uploaded through the [Files API](/docs/file-handling).

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.3",
    input=[
        {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "What is in this image?",
                },
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg",
                },
            ],
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.responses.create({
  model: 'muse-spark-1.3',
  input: [
    {
      type: 'message',
      role: 'user',
      content: [
        {
          type: 'input_text',
          text: 'What is in this image?',
        },
        {
          type: 'input_image',
          image_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg',
        },
      ],
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
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
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "What is in this image?",
                    },
                    {
                        "type": "input_image",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg",
                    },
                ],
            },
        ],
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
  "input": [
    {
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "What is in this image?"
        },
        {
          "type": "input_image",
          "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg"
        }
      ]
    }
  ]
}'
```


To send a local image without hosting it, pass a base64 `data:` URL as the same `image_url` string (for example, `"data:image/jpeg;base64,<encoded bytes>"`).

### Reference an uploaded file {#uploaded-files}

Upload an image through the [Files API](/docs/file-handling), then reference it by ID with an `input_file` (or `input_image`) block.

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

# Upload the image
with open("photo.png", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="user_data",
    )

# Reference the uploaded file in a responses request
response = client.responses.create(
    model="muse-spark-1.1",
    input=[
        {
            "type": "message",
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What is in this image?"},
                {"type": "input_file", "file_id": file.id},
            ],
        }
    ],
)

print(response.output_text)
```

> [!NOTE] input_file vs input_image
> You can reference an uploaded image with either an `input_file` block (shown above) or an `input_image` block that carries a `file_id` instead of an `image_url` (for example `{"type": "input_image", "file_id": file.id}`). Both point to the same uploaded file; use `input_image` when you want the block typed explicitly as an image.

> [!NOTE] Reference an image by URL
> To use a publicly hosted image on the Responses API without uploading first, pass its URL in an `input_file` block's `file_url` field (for example `{"type": "input_file", "file_url": "https://example.com/photo.png"}`). The server fetches the URL for you. See [Files API: reference a file by URL](/docs/file-handling#file-url).

## Image understanding with Chat Completions {#chat-completions}

If your application or agent harness is built on [Chat Completions](/docs/protocols/chat-completions), image understanding is fully supported. The only structural difference from the Responses API is that Chat Completions wraps the image in an `image_url` **object** (whose `url` is a public URL or a base64 data URL), rather than the plain string the Responses API uses.

Include the image in the `content` array of a `user` message:

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
            "content": [
                {
                    "type": "text",
                    "text": "Describe what you see in this image.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg",
                    },
                },
            ],
        },
    ],
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.chat.completions.create({
  model: 'muse-spark-1.3',
  messages: [
    {
      role: 'user',
      content: [
        {
          type: 'text',
          text: 'Describe what you see in this image.',
        },
        {
          type: 'image_url',
          image_url: {
            url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg',
          },
        },
      ],
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
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
                "content": [
                    {
                        "type": "text",
                        "text": "Describe what you see in this image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg",
                        },
                    },
                ],
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
      "content": [
        {
          "type": "text",
          "text": "Describe what you see in this image."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg"
          }
        }
      ]
    }
  ]
}'
```


#### Example response

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1714502400,
  "model": "muse-spark-1.1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "A whole dark-skinned avocado is placed next to a halved avocado showing its green flesh and brown pit on a white reflective surface."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 272,
    "completion_tokens": 22,
    "total_tokens": 294
  }
}
```

To send a local image, base64-encode it and pass it as the `url` inside the `image_url` object:

```python title="Python (OpenAI SDK)"
import os
import base64
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

def image_to_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

base64_image = image_to_base64("photo.jpg")

response = client.chat.completions.create(
    model="muse-spark-1.1",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What does this image contain?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)
```

## Multiple images {#multiple-images}

Send multiple images in one request by adding several image content blocks — `input_image` blocks on the Responses API, or `image_url` items on Chat Completions. You can include up to **50 images**; more than 50 returns `HTTP 400` (`request contains <n> images, exceeding the maximum of 50 allowed per request`). Requests are also bounded by payload size and the context window. A PDF upload contributes at most its first 50 page-images toward this budget; see [Files API: PDF handling](/docs/file-handling#pdf-handling).

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
            "content": [
                {
                    "type": "text",
                    "text": "What do these two images have in common?",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image1.jpg",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image2.jpg",
                    },
                },
            ],
        },
    ],
)

print(response.model_dump_json(indent=2))
```

## Localize objects with perception grounding {#perception-grounding}

Perception grounding adds location to understanding. Alongside describing an image, Muse Spark reports where objects are. Name the objects you care about, ask for coordinates, and use the positions to crop regions, measure layouts, seed a downstream detector, or draw labeled overlays on the original image.

### Coordinate system {#coordinate-system}

Muse Spark reports positions on a normalized **0–1000** grid based on the image you sent:

* `(0, 0)` is the top-left corner; `(1000, 1000)` is the bottom-right.
* The first axis (`x`) increases left to right; the second (`y`) increases top to bottom.
* The grid is resolution-independent: it applies whether you sent a 640px or a 4000px image, so output stays stable if you resize.

Convert normalized values back to pixels using the dimensions of the exact image you sent:

```python
def to_pixels(x_norm, y_norm, width, height):
    x = round(x_norm * width / 1000)
    y = round(y_norm * height / 1000)
    return x, y
```

> [!WARNING] Coordinates match the sent image
> Coordinates are relative to the image the model actually received. If you crop, pad, or resize before sending, map the response back to that same image, then to the original. Keep one basis for the whole task.

### Prompt for structured coordinates {#structured-coordinates}

Muse Spark fills the coordinate schema you define. State the exact fields and axis order in your prompt and ask for JSON. Pair the instruction with [structured output](/docs/structured-output) when you need the response to parse on the first try.

```python title="Python (OpenAI SDK)"
import os
import base64
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

def image_to_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

base64_image = image_to_base64("kitchen.jpg")

prompt = (
    "Locate every piece of fruit in the image. Return a JSON array where each "
    'element has "label" (the object name) and "box", a bounding box as '
    "[x_min, y_min, x_max, y_max] on a normalized 0-1000 grid with (0,0) at the "
    "top-left. Return only the JSON."
)

response = client.chat.completions.create(
    model="muse-spark-1.1",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)
```

```json
[
  {"label": "avocado", "box": [412, 530, 588, 690]},
  {"label": "lemon", "box": [640, 486, 742, 604]}
]
```

Parse the array, then run each box through the `to_pixels` helper to crop or annotate the region. Points work the same way: ask for a single `[x, y]` per object when you need a location rather than an extent.

### Some grounding modes: point, box, and count {#grounding-modes}

Muse Spark grounds most reliably when your prompt asks for **one specific output shape** and lists the objects to find. Three shapes worth reaching for first are point, box, and count — they cover most tasks, but they aren't the only options; you can define your own output shape the same way (see [Prompt for structured coordinates](#structured-coordinates) above). In each of these, coordinates use the normalized **0–1000** grid described above, the model returns a JSON array with one entry per object, and any object it can't find is omitted from the results.

Pick the shape from what you need to do with the result:

| Mode | Use when | Returns per object |
|------|----------|--------------------|
| **Point** | You need a location, not an extent — "where is", "point to", "find", "show me where" | `{"x": int, "y": int}` |
| **Box** | You want to highlight, outline, detect, or crop a region or a large object | `{"bbox": [{"x_min": int, "y_min": int, "x_max": int, "y_max": int}]}` |
| **Count** | You need "how many" — dense crowds, repeated or small items, overlapping or occluded instances | `{"points": [{"x": int, "y": int}, ...], "count": int}` |

**Point.** Ask the model to point at each object and reply as a JSON array:

```text title="Point prompt"
Point to each of the following objects in the image: "the power button", "the water tank". For each object, answer in the format {"object_name": "<name>", "x": <int>, "y": <int>}. The coordinates should be in the 0-1000 range. Return a JSON array of results. If you cannot find an object, omit it from the results.
```

**Box.** For regions and larger objects, ask for bounding boxes. Leading with "You are an object grounding expert" and telling the model not to miss any objects measurably improves recall:

```text title="Bounding-box prompt"
You are an object grounding expert. Provide the bounding box coordinates of the objects in the image: "the coffee mug", "the laptop". Ensure the objects accurately match the request and do not miss any objects. For each object, answer in the format {"object_name": "<name>", "bbox": [{"x_min": <int>, "y_min": <int>, "x_max": <int>, "y_max": <int>}]}. The coordinates should be in the 0-1000 range. Return a JSON array of results. If you cannot find an object, omit it from the results.
```

**Count.** To count instances, ask the model to point at *every* instance and return the total. Pointing at each one before counting handles overlapping, clustered, and partially occluded objects far better than asking for a bare number:

```text title="Count prompt"
Point to every instance of each of the following objects in the image and count them: "person", "car". For each object, answer in the format {"object_name": "<name>", "points": [{"x": <int>, "y": <int>}, ...], "count": <int>}. The coordinates should be in the 0-1000 range. Return a JSON array of results. If you cannot find any instances of an object, omit it from the results.
```

> [!TIP] Keep grounding prompts direct
> Keep the request direct: put the grounding instruction in the user message next to the image and leave the system prompt minimal — the model grounds best from an uncluttered prompt. Pair any mode with [structured output](/docs/structured-output) to guarantee the JSON parses on the first try, and convert the 0–1000 values to pixels with the `to_pixels` helper above before you crop or draw. The model may emit a value slightly outside the range (for example `1001`) for an object touching the edge, so clamp to the image bounds.

### Render annotation overlays {#annotation-overlays}

Normalized coordinates map directly to the image at display time, so you can ask for a ready-to-view annotation instead of raw numbers. Ask for a self-contained HTML page that draws each labeled box over the image, and you get the overlay without writing rendering code:

```python
prompt = (
    "Locate every piece of fruit in the image. Return a complete, self-contained "
    "HTML page that displays the image and overlays a labeled box on each item. "
    "Position each box with CSS percentages by dividing the normalized 0-1000 "
    "coordinates by 10. Return only the HTML."
)

# Send prompt + image as in the previous example, then save the result:
with open("annotated.html", "w") as f:
    f.write(response.choices[0].message.content)
```

Dividing normalized coordinates by 10 yields CSS percentages, so a box positioned with percentage `left` / `top` / `width` / `height` lines up at any display size. Embed the same base64 data URL you sent, or point the page's `<img>` at your hosted image.

## Supported formats and limits {#supported-formats}

| Constraint | Value |
|---|---|
| Max file size per image (inline `image_url`) | 50 MB (50,000,000 bytes) |
| Max file size per image (`input_file` via Files API) | 1 GiB (1,073,741,824 bytes) |
| Max images per request | **50**, enforced. More than 50 returns `HTTP 400`. Also bounded by payload size and the context window. |
| PDF page-images retained | First 50 per PDF |
| Supported MIME types | `image/jpeg`, `image/jpg`, `image/png`, `image/gif`, `image/webp`, `image/x-icon` |

> [!NOTE] Undecodable images return 400
> If an image's bytes can't be decoded (for example, a corrupt or truncated file), the request fails with `HTTP 400` (`type: invalid_request_error`, `code: null`). The error message identifies the affected image. Re-upload or re-encode the image and retry.

## Estimating token usage {#token-estimation}

For an exact count of any request (including images and files), call [`POST /v1/responses/input_tokens`](/docs/api-reference/responses) with the same `input`. It returns the input token total without generating a response, and is the authoritative way to estimate cost.

Image cost scales with resolution, not a fixed per-image amount. Measured via `input_tokens`:

* A very small image adds only a few tokens (a 1x1 image ≈ 3 tokens).
* Cost rises with resolution: a ~1280px image adds roughly **1,300–1,500 tokens**.

> [!NOTE] Token counts vary; use the endpoint
> Requests also carry a fixed prompt-formatting overhead (a short text-only request is ~110 input tokens) and the model may resize images, so counts vary. An older estimate based on a flat 336x336-pixel tile formula (≈147 tokens per single-tile image) significantly over-estimates small images; rely on the `input_tokens` endpoint instead.

## Next steps

- **Upload images efficiently**: use the [Files API](/docs/file-handling) to reference images by `file_id` instead of base64 or public URLs.
- **Go multimodal and multi-turn**: use the [Responses API](/docs/protocols/responses) for multimodal, multi-turn interactions.
- **Make localization reliable**: enforce your coordinate schema with [structured output](/docs/structured-output) so responses parse on the first try.
- **Wire up the rest of the call**: explore generation controls in [chat completion](/docs/protocols/chat-completions) and see the [Responses API reference](/docs/api-reference/responses) for the full parameter schema.