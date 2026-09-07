---
meta:
  title: Image generation with Muse Image
  description: 'Generate and edit images with Muse Image through a conversation: interleave text and reference images and refine across turns on the Responses API, or make one-off calls with the OpenAI-compatible images endpoints.'
  keywords: image generation, Muse Image, conversational image generation, interleaved text and image, multi-turn editing, text-to-image, image editing, image-to-image, images/generations, images/edits, reference images, Responses API
cms:
  alias: /model-api/docs/image-generation
  target: aidmc
---

# Image generation with Muse Image

[Muse Image](/docs/models#muse-image) generates and edits images from a conversation. Send interleaved text and reference images, get an image back, then keep refining it turn by turn, all through the same [Responses API](/docs/protocols/responses) you already use for text. One model handles both generation and editing, and plain text-to-image and one-off edits are just special cases of the same conversational interface.

## How it works {#how-it-works}

Muse Image takes text and, optionally, reference images, and returns an image. One model covers the whole workflow:

- **Generate**: describe an image and get it back.
- **Edit**: send an existing image with an instruction, and it changes only what you ask for while keeping the rest intact.
- **Refine**: keep going in the same conversation, and each turn builds on the last.

The main interface is the conversational **[Responses API](/docs/protocols/responses)**. It accepts arbitrary interleaved text and image input and keeps conversation state across turns, so you can generate an image and then steer it toward the result you want. This interleaved, multi-turn flow is what Muse Image is built around.

For a one-off generation or edit with no conversation state, the **single-shot images endpoints** ([`/v1/images/generations`](#generate) and [`/v1/images/edits`](#edit)) are compatible with the OpenAI Images API, so an OpenAI client works by pointing `base_url` at `https://api.meta.ai/v1`.

### Automatic grounding {#grounding}

Muse Image is agentic. Before it renders, it can look things up and use what it finds as references, so results stay accurate for real places, products, brands, styles, and current events:

- **Visual references**: for a real landmark, product, logo, or style, it can pull reference imagery from the web and match likeness, composition, and detail.
- **Current facts**: when a prompt depends on real-world information such as recent results, prices, or dates, it can look them up so any text or data in the image is right.
- **Generated layouts**: for infographics, charts, or other structured graphics, it can compute and arrange the elements before rendering.

This all happens on its own. You don't configure it, and this built-in search is part of the per-image price, so it carries no extra search-grounding charge. The intermediate lookups aren't surfaced as separate tool-call items, so you just get the finished image. On the Responses API you also get a short summary of what the model did in a `reasoning` item (see [Read the response](#read-the-response)); the images endpoints return the finished image only. If you'd rather constrain it, you can turn specific tools off or cap refinement on the [Responses API](#tool-controls) or the [images endpoints](#tool-controls-images).

> [!NOTE] Search is built in, not a tool
> Muse Image runs web and image search itself. This differs from a text model's [search grounding](/docs/search-grounding), where you add a `web_search` tool: with Muse Image, search is built in and on by default, and passing a `web_search` tool returns an error (see [Control the tools and reasoning](#tool-controls) on the Responses API, or [the images endpoints](#tool-controls-images)).

## Conversational generation {#responses-api}

Use the [Responses API](/docs/protocols/responses) to generate an image and then refine it across turns. Pass a text prompt (and optional reference images) as `input`; the response's `output` array carries the result.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-image-1.0",
    input="a red fox trotting through fresh snow, golden hour",
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
  model: 'muse-image-1.0',
  input: 'a red fox trotting through fresh snow, golden hour',
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
        "model": "muse-image-1.0",
        "input": "a red fox trotting through fresh snow, golden hour",
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
  "model": "muse-image-1.0",
  "input": "a red fox trotting through fresh snow, golden hour"
}'
```


### Read the response {#read-the-response}

A successful response's `output` array holds up to three items, in order:

- a **`reasoning`** item: a short summary of what the model planned and looked up. It's a summary only, never the raw chain of thought, and it appears when the model produces one.
- a **`message`** item: the assistant turn.
- one **`image_generation_call`** item per image: the base64-encoded image is in `result`, and its `id` is a signed handle you use to keep editing in a later turn.

```json
{
  "id": "resp_abc123",
  "status": "completed",
  "output": [
    {
      "type": "reasoning",
      "id": "rs_xxx",
      "summary": [
        { "type": "summary_text", "text": "Looked up the current table and each crest, then laid out the panel." }
      ],
      "status": "completed"
    },
    { "type": "message", "id": "msg_xxx", "role": "assistant", "content": [], "status": "completed" },
    { "type": "image_generation_call", "id": "ig_xxx", "status": "completed", "result": "UklGR..." }
  ]
}
```

Pick the image item by type rather than by position, then save it:

```python title="Python (OpenAI SDK)"
import base64

image_b64 = next(
    o.result for o in response.output if o.type == "image_generation_call"
)
with open("fox.webp", "wb") as f:
    f.write(base64.b64decode(image_b64))
```

### Iterate across turns {#multi-turn}

Refine an image over several turns. By default the API tracks the conversation for you (`store` defaults to `true`): chain each turn by passing the previous response's `id` as `previous_response_id` and sending only your new instruction.

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

# Turn 1: generate
t1 = client.responses.create(
    model="muse-image-1.0",
    input="a red fox trotting through fresh snow, golden hour",
)

# Turn 2: refine, chaining from the previous response
t2 = client.responses.create(
    model="muse-image-1.0",
    previous_response_id=t1.id,
    input="now make it night, with the aurora overhead",
)
```

Each turn keeps the coherence of the last, so you can move toward a target result without starting over. You don't resend the image: the `image_generation_call.id` from the prior turn carries what's needed.

### Guide generation with reference images {#reference-images}

To steer generation with one or more reference images, pass `input` as a list of content parts. Mix `input_text` and `input_image` parts in any order: they're read in the order you provide them, so you can caption each image inline. Each `input_image` takes an `image_url` (a public URL or a base64 data URL) or a `file_id` from the [Files API](/docs/file-handling).

```python title="Python (OpenAI SDK)"
response = client.responses.create(
    model="muse-image-1.0",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Use the pose from this image:"},
                {"type": "input_image", "image_url": "https://example.com/pose.png"},
                {"type": "input_text", "text": "and the color palette of this one:"},
                {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0KGgo..."},
                {"type": "input_text", "text": "Produce a single painterly portrait."},
            ],
        }
    ],
)
```

You can pass multiple reference images in a single turn, and add new ones on later turns to bring in fresh references as you iterate.

### Manage state yourself {#stateless}

If you'd rather manage the conversation yourself, or don't want responses persisted, set `store: false`. On each new turn, replay the previous `image_generation_call` item in the `input` list, followed by your new instruction. Add `input_image` parts to that instruction to bring in new reference images.

```json
{
  "model": "muse-image-1.0",
  "store": false,
  "input": [
    {
      "type": "image_generation_call",
      "id": "ig_xxx_from_prior_turn",
      "status": "completed",
      "result": null
    },
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "now make it night, with the aurora overhead"}
      ]
    }
  ]
}
```

### Control the tools and reasoning {#tool-controls}

By default, Muse Image decides when to search or run code, refines its output over several passes, and picks the output shape and format. To control any of that on the Responses API, include an `image_generation` tool in `tools` and set its fields:

- **`enable_image_search`**, **`enable_web_search`**, **`enable_shell`**: per-tool switches, all `true` by default. Set one to `false` to turn that tool off for the request. `enable_image_search` pulls visual references such as real places, products, logos, and styles; `enable_web_search` looks up current facts (turning it off also drops the browser tools); `enable_shell` runs code to build charts, tables, or structured layouts.
- **`reasoning_strength`**: `"high"` (the default) refines the output over several passes for more polished results. `"low"` returns after a single pass, trading some of that refinement for faster generation. It doesn't change the price: you're billed [per image](#usage) either way.
- **`size`**: a `"WxH"` string such as `"1024x1536"` that sets the aspect ratio, not the exact pixel size: the image is produced at the generator's own resolution, so the returned dimensions won't match the numbers exactly. Omit it or pass `"auto"` for the default aspect ratio.
- **`output_format`**: `"webp"` (the default), `"png"`, or `"jpeg"` — the encoding of the returned image.

```json
{
  "model": "muse-image-1.0",
  "input": "an infographic of the current Premier League top four, with each club's crest",
  "tools": [
    {
      "type": "image_generation",
      "enable_web_search": false,
      "enable_shell": false,
      "reasoning_strength": "low",
      "size": "1536x1024",
      "output_format": "png"
    }
  ]
}
```

Muse Image accepts only the `image_generation` tool. Because it runs web and image search internally, you don't add a `web_search` tool the way you would for a text model: passing `web_search`, a function tool, or any other tool returns `HTTP 400` with the message "image models only support the `image_generation` tool".

## One-off generation {#images-endpoints}

For a one-off generation or edit with no conversation state, use the OpenAI-compatible images endpoints. Point the OpenAI SDK at `https://api.meta.ai/v1` and call `client.images.generate(...)` and `client.images.edit(...)`, the same paths and methods as the OpenAI Images API.

- `POST /v1/images/generations`: text-to-image.
- `POST /v1/images/edits`: image-to-image and editing. The OpenAI SDK uploads the input image(s) as `multipart/form-data` (the `image` field). The endpoint also accepts a Meta-specific JSON body, an `images` array of URLs or `file_id`s, for callers using raw HTTP.

> [!NOTE] Identify end users
> Pass an optional `user` field — a stable end-user identifier — to help detect and mitigate abuse. It's supported on the images endpoints; on the [Responses API](/docs/protocols/responses) and Chat Completions, use `safety_identifier` instead.

### Generate from a prompt {#generate}

Send a text prompt to `images/generations`.

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

const response = await client.images.generate({
  model: 'muse-image-1.0',
  prompt: 'a watercolor painting of a red fox sitting in a snowy pine forest, soft golden morning light',
  n: 1,
});

console.log(JSON.stringify(response, null, 2));
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


Useful parameters:

- **`n`**: number of images to return, 1 to 10 (default 1). `data` has one entry per image.
- **`size`**: a `"WxH"` string such as `"1792x1024"`. It sets the aspect ratio, not the exact pixel size: the image is produced at the generator's own resolution, so the returned dimensions won't match the numbers exactly. Omit it for the default aspect ratio.
- **`response_format`**: `"b64_json"` (default) returns base64 bytes in `data[].b64_json`; `"url"` returns a temporary signed URL in `data[].url` instead.
- **`output_format`**: `"webp"` (default), `"png"`, or `"jpeg"`. The response echoes the format in `output_format`.

### Edit an image {#edit}

Send an input image to `images/edits` with a text prompt describing the change. With the OpenAI SDK, pass the image bytes as `image`, exactly like OpenAI's `images.edit`:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

with open("fox.png", "rb") as image:
    response = client.images.edit(
        model="muse-image-1.0",
        prompt="add a small red wool hat on the fox's head, keep the snowy forest background",
        image=image,
        n=1,
    )

print(response.model_dump_json(indent=2))
```

Over raw HTTP, send a JSON body instead: an `images` array where each item is an `image_url` (a public URL or a base64 data URL) or a pre-uploaded `file_id` from the [Files API](/docs/file-handling). This JSON shape is Meta-specific: the OpenAI SDK always sends multipart, so use `requests` or curl for the JSON body.

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


### Compose multiple images {#compose}

Pass multiple input images to fuse them into a single scene, for example to place a subject from one image into the setting of another. With the OpenAI SDK, pass a list of files as `image`:

```python title="Python (OpenAI SDK)"
with open("fox.webp", "rb") as fox, open("mug.webp", "rb") as mug:
    response = client.images.edit(
        model="muse-image-1.0",
        prompt="place the watercolor fox sitting next to the ceramic coffee mug on the wooden table",
        image=[fox, mug],
    )
```

Over raw HTTP, pass the same inputs as `images` array items:

```json
{
  "model": "muse-image-1.0",
  "prompt": "place the watercolor fox sitting next to the ceramic coffee mug on the wooden table",
  "images": [
    { "image_url": "data:image/webp;base64,...fox..." },
    { "image_url": "data:image/webp;base64,...mug..." }
  ]
}
```

### Control the tools and reasoning on the images endpoints {#tool-controls-images}

The images endpoints expose the same controls as top-level request fields: a `tool_enablement` object (with `enable_image_search`, `enable_web_search`, and `enable_shell`) and a `reasoning_strength` string. Omit `tool_enablement` to keep every tool available, or set a field to `false` to turn that tool off.

```json
{
  "model": "muse-image-1.0",
  "prompt": "a watercolor red fox in a snowy forest",
  "reasoning_strength": "low",
  "tool_enablement": { "enable_web_search": false, "enable_shell": false }
}
```

With the OpenAI SDK, pass them through `extra_body` (they're Meta extensions, not part of the OpenAI Images types). This example generates an infographic, a case where grounding helps: the model searches for each club's crest and looks up the current table before it renders.

```python title="Python (OpenAI SDK)"
import base64
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.images.generate(
    model="muse-image-1.0",
    prompt="An infographic of the current Premier League top four, with each club's crest",
    extra_body={
        "reasoning_strength": "high",
        # These tools are on by default; shown here to make the shape explicit.
        "tool_enablement": {
            "enable_image_search": True,
            "enable_web_search": True,
            "enable_shell": True,
        },
    },
)

image_b64 = response.data[0].b64_json
with open("standings.png", "wb") as image_file:
    image_file.write(base64.b64decode(image_b64))
```

Disabling tools trades some grounding accuracy for speed: for prompts that don't rely on real-world references or current facts, turning them off can speed up generation.

### Response shape {#images-response}

Both images endpoints return the same shape:

```json
{
  "created": 1784584435,
  "data": [
    { "b64_json": "UklGR..." }
  ],
  "output_format": "webp",
  "background": "opaque",
  "usage": { "input_tokens": 9831, "output_tokens": 749, "total_tokens": 10580 }
}
```

- **`created`**: Unix timestamp (seconds).
- **`data`**: one entry per image. Each carries `b64_json` (when `response_format` is `b64_json`, the default) or `url` (when `response_format` is `url`).
- **`output_format`**: the format of the returned images.
- **`background`**: echoed for OpenAI compatibility; always `opaque`.
- **`usage`**: token counts. See [Pricing](#usage).

### Stream results {#images-stream}

Set `stream: true` to receive the result as a server-sent event stream. The endpoint emits a completed event carrying the finished image:

- `/v1/images/generations`: an `image_generation.completed` event.
- `/v1/images/edits`: an `image_edit.completed` event.

```
event: image_generation.completed
data: {"type": "image_generation.completed", "b64_json": "UklGR...", "created_at": 1784584435}
```

## Pricing {#usage}

Muse Image is billed at a flat **$0.01 per generated image**. The price is the same whether you set `reasoning_strength` to `high` or the model uses tools during generation, and a request that returns `n` images is billed for `n` images. You're billed only for images the model successfully generates and returns: images that fail to generate, or that are removed by safety filtering before they're returned, aren't counted. See [Pricing and rate limits](/docs/pricing-rate-limits#image-generation) for the full breakdown.

> [!NOTE] Built-in search is included
> Muse Image's built-in web and image search is part of the per-image price, so it carries no separate [search-grounding](/docs/pricing-rate-limits#image-generation) charge.

Every response still includes a `usage` object with token counts for reference, but Muse Image isn't priced per token.

## Errors {#errors}

Requests that fail validation return an HTTP `400` with an OpenAI-style error envelope:

```json
{
  "error": {
    "type": "invalid_request_error",
    "param": "n",
    "message": "`n` The number must be `<= 10`."
  }
}
```

Common cases:

- **Missing `prompt`**: `prompt` is required on both endpoints.
- **`n` out of range**: `n` must be between 1 and 10.
- **Invalid `response_format` or `output_format`**: each must be one of its supported values.
- **Empty or malformed `images`**: an edit needs at least one item, and each item must contain exactly one of `image_url` or `file_id`.
- **Unsupported tool on the Responses API**: Muse Image accepts only the `image_generation` tool; sending `web_search`, a function tool, or any other tool returns "image models only support the `image_generation` tool".
- **Restricted `moderation`**: `auto` and `low` are accepted; `none` requires per-application access and otherwise returns an `unsupported_parameter` error.

## Next steps

- **Upload reference images once**: use the [Files API](/docs/file-handling) to reference images by `file_id` instead of resending base64 on every edit.
- **Iterate in a conversation**: use the [Responses API](/docs/protocols/responses) to refine an image across turns with server-managed state.
- **See the full schema**: the [Images API reference](/docs/api-reference/images) has the complete request and response shapes for every parameter.