---
meta:
  title: File handling
  description: Send files to the model inline in a Responses or chat completion request, or upload them once with the Files API and reference them by ID.
  keywords: file handling, file upload, files API, inline files, input_file, multimodal inputs
cms:
  alias: /model-api/docs/file-handling
  target: aidmc
---

# File handling

Bring your own files to the model and build with your own data. Include bytes inline in a single [Responses API](/docs/protocols/responses) or [chat completion](/docs/protocols/chat-completions) request, or upload once with the Files API and reuse the ID across calls. Both paths work for images, video, and PDFs.

## How it works {#how-it-works}

Pick the path that fits your call:

- **Send it inline**: include the file directly in a Responses or chat completion request, as base64 bytes (`file_data`) or a public URL (`file_url`). No storage to manage and nothing to clean up. Best for one-off calls. Limited to the 50 MB inline limit.
- **Upload it once**: `POST` the file to the Files API, get a `file-` ID back, and reference that ID in as many requests as you need. Best for reuse and for large files up to 1 GiB.

See the [Files API reference](/docs/api-reference/files) for full endpoint details.

## Supported file types {#supported-file-types}

The API accepts the following MIME types whether you send the file inline or upload it:

| Media type | MIME types | Notes |
|------------|-----------|-------|
| Image | `image/png`, `image/jpeg` (or `image/jpg`), `image/gif`, `image/webp`, `image/x-icon` | `image/jpg` is an alias for `image/jpeg` |
| Video | `video/mp4` | Visual frames plus embedded-audio transcription. See [video and audio understanding](/docs/video-understanding). |
| Audio | `audio/mpeg`, `audio/wav` | MP3 and WAV audio input. See [video and audio understanding](/docs/video-understanding#speech). |
| Document | `application/pdf` | Converted to text plus per-page images. See [PDF handling](#pdf-handling). |
| Text | `text/plain`, `application/json`, `application/jsonl` | `application/jsonl` is used for `batch` uploads (`purpose=batch`) |

Images, MP4 video, audio, and PDFs can be referenced in inference requests for [image understanding](/docs/image-understanding), [video and audio understanding](/docs/video-understanding), and document understanding. Audio files can be uploaded via `/v1/files` or sent inline using `input_audio`; see [video and audio understanding](/docs/video-understanding#speech). Text, JSON, and JSONL files are accepted for other purposes, such as `batch` datasets uploaded with `purpose=batch`.

### PDF handling {#pdf-handling}

PDFs are converted in parallel to **text** and per-page raster **images**, then sent together to the inference layer:

- **Text** is extracted from the **first 100 pages**; pages beyond 100 contribute no text. The extracted text is then bounded by the model's context window.
- Only the **first 50 page-images** are retained for visual understanding. These page-images count toward the per-request image budget (up to 50 images per request; see [Image understanding](/docs/image-understanding#multiple-images)).

A PDF with up to 50 pages is fully covered for both text and images. For a longer PDF, the model receives text from the first 100 pages and images from the first 50. It cannot see text beyond 100 pages or visual content beyond 50 pages.

## Size limits {#size-limits}

| Send method | Maximum file size |
|-------------|-------------------|
| Inline (`file_data` base64 or `file_url` in the request body) | 50 MB (50,000,000 bytes) |
| Files API upload (`POST /v1/files`) | 1 GiB (1,073,741,824 bytes) |

Files larger than these limits are rejected.

### Team storage limit {#team-storage-limit}

Uploaded files also count toward a per-team total storage limit of **100 GiB (107,374,182,400 bytes)**, shared across all API keys in your team. Only files stored through the Files API count toward this limit; inline files (`file_data` / `file_url`) do not.

Uploaded files don't expire, so stored data only grows until you remove it. When your team reaches the limit, further uploads to `POST /v1/files` are rejected with `HTTP 400`. Delete files you no longer need with [`DELETE /v1/files/{file_id}`](/docs/api-reference/files/delete-file) to free space.

## Send a file inline {#inline}

Send a file directly in the request body with no upload step. Chat Completions and the Responses API each carry an inline file in a content block:

- **Chat Completions**: a `file` content block whose nested `file` object carries `file_data` (base64 bytes, optionally as a `data:` URL) and a `filename`.
- **Responses API**: an `input_file` content block carrying `file_data` (with an optional `filename`), or a `file_url` the server fetches for you. Send inline video with an `input_video` block carrying `video_url` as a public URL or base64 data URL.

Inline files are bounded by the 50 MB [inline limit](#size-limits). For anything larger, or for a file you will reuse, [upload it](#upload) instead.

First, read the file and base64-encode it into a `data:` URL. The request examples below reference this `file_data` variable:

```python title="Python"
import base64

with open("document.pdf", "rb") as f:
    raw = f.read()

encoded = base64.b64encode(raw).decode()
file_data = f"data:application/pdf;base64,{encoded}"
```
```typescript title="TypeScript"
import fs from 'fs';

const bytes = fs.readFileSync('document.pdf');
const encoded = bytes.toString('base64');
const file_data = `data:application/pdf;base64,${encoded}`;
```


### In a chat completion {#inline-chat}

Pass the data URL in a `file` content block alongside your text.

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
                    "text": "Summarize this document.",
                },
                {
                    "type": "file",
                    "file": {
                        "filename": "document.pdf",
                        "file_data": file_data,
                    },
                },
            ],
        },
    ],
)

print(response.model_dump_json(indent=2))
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
                        "text": "Summarize this document.",
                    },
                    {
                        "type": "file",
                        "file": {
                            "filename": "document.pdf",
                            "file_data": file_data,
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
          text: 'Summarize this document.',
        },
        {
          type: 'file',
          file: {
            filename: 'document.pdf',
            file_data: file_data,
          },
        },
      ],
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```


### In a Responses request {#inline-responses}

On the Responses API, carry the data URL in an `input_file` block's `file_data` field.

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
                    "text": "Summarize this document.",
                },
                {
                    "type": "input_file",
                    "filename": "document.pdf",
                    "file_data": file_data,
                },
            ],
        },
    ],
)

print(response.model_dump_json(indent=2))
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
                        "text": "Summarize this document.",
                    },
                    {
                        "type": "input_file",
                        "filename": "document.pdf",
                        "file_data": file_data,
                    },
                ],
            },
        ],
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
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
          text: 'Summarize this document.',
        },
        {
          type: 'input_file',
          filename: 'document.pdf',
          file_data: file_data,
        },
      ],
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```


### Reference a file by URL {#file-url}

Skip uploading and encoding; pass a public URL in an `input_file` block's `file_url` field on the Responses API. The server fetches the URL, detects the file type, and processes it. PDFs are parsed as described in [PDF handling](#pdf-handling). Use this when the document is already hosted somewhere the API can reach over `http` or `https`. Other URL schemes return `HTTP 400`.

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
                    "text": "Summarize this document.",
                },
                {
                    "type": "input_file",
                    "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
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
          text: 'Summarize this document.',
        },
        {
          type: 'input_file',
          file_url: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
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
                        "text": "Summarize this document.",
                    },
                    {
                        "type": "input_file",
                        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
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
          "text": "Summarize this document."
        },
        {
          "type": "input_file",
          "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        }
      ]
    }
  ]
}'
```


## Upload and reference a file {#upload}

Upload a file once, then reference its ID across requests. Upload with `POST /v1/files` and set `purpose` to `user_data` for files you plan to reference in inference calls. To make a file expire automatically, include an optional `expires_after` object (see [File expiration](#expiration)).

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

with open("/path/to/image.png", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="user_data",
    )

print(file.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import fs from 'fs';
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const file = await client.files.create({
  file: fs.createReadStream('/path/to/image.png'),
  purpose: 'user_data',
});

console.log(JSON.stringify(file, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

with open("/path/to/image.png", "rb") as f:
    response = requests.post(
        "https://api.meta.ai/v1/files",
        headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
        files={"file": f},
        data={
            "purpose": "user_data",
        },
    )
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/files" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -F "file=@/path/to/image.png" \
  -F "purpose=user_data"
```


#### Example response {#upload-response}

```json
{
  "id": "file-842549258569145",
  "object": "file",
  "bytes": 245832,
  "created_at": 1714502400,
  "filename": "document.pdf",
  "purpose": "user_data",
  "status": "uploaded"
}
```

The response includes an `id`: a `file-` prefix followed by a numeric identifier, such as `file-842549258569145`. Use that ID to reference the file in later requests.

### Reference an uploaded file {#reference-uploaded}

Pass the file ID in an `input_file` block's `file_id` field on a Responses API request. This works for images, videos, and PDFs. You can also reference uploaded images and videos with the typed `input_image` and `input_video` blocks.

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
                    "text": "Summarize this document.",
                },
                {
                    "type": "input_file",
                    "file_id": "file-abc123",
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
          text: 'Summarize this document.',
        },
        {
          type: 'input_file',
          file_id: 'file-abc123',
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
                        "text": "Summarize this document.",
                    },
                    {
                        "type": "input_file",
                        "file_id": "file-abc123",
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
          "text": "Summarize this document."
        },
        {
          "type": "input_file",
          "file_id": "file-abc123"
        }
      ]
    }
  ]
}'
```


### File expiration {#expiration}

By default, uploaded files do not expire. If you do not set `expires_after`, the response omits `expires_at`. To set an expiration, include an `expires_after` object in the upload request with two fields:

- **`anchor`**: the reference point the lifetime is measured from. The only supported value is `created_at`.
- **`seconds`**: the lifetime in seconds, from `3600` (1 hour) to `2592000` (30 days).

Both fields are required when `expires_after` is present. Omitting either, or using any anchor other than `created_at`, returns `HTTP 400`. When set, `expires_at` is `created_at + seconds` in Unix seconds.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

with open("/path/to/document.pdf", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="user_data",
        expires_after={
            "anchor": "created_at",
            "seconds": 2592000,
        },
    )

print(file.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import fs from 'fs';
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const file = await client.files.create({
  file: fs.createReadStream('/path/to/document.pdf'),
  purpose: 'user_data',
  expires_after: {
    anchor: 'created_at',
    seconds: 2592000,
  },
});

console.log(JSON.stringify(file, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

with open("/path/to/document.pdf", "rb") as f:
    response = requests.post(
        "https://api.meta.ai/v1/files",
        headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
        files={"file": f},
        data={
            "purpose": "user_data",
            "expires_after[anchor]": "created_at",
            "expires_after[seconds]": 2592000,
        },
    )
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/files" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -F "file=@/path/to/document.pdf" \
  -F "purpose=user_data" \
  -F "expires_after[anchor]=created_at" \
  -F "expires_after[seconds]=2592000"
```


### List files {#list}

Retrieve a list of your uploaded files with `GET /v1/files`. Filter by purpose with the `purpose` query parameter, such as `?purpose=user_data`.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.files.list()

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/files",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/files" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```


### Retrieve a file {#retrieve}

Get metadata for a specific file with `GET /v1/files/{file_id}`.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.files.retrieve("file_abc123")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/files/file_abc123",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/files/file_abc123" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```


### Delete a file {#delete}

Remove a file with `DELETE /v1/files/{file_id}`.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.files.delete("file_abc123")

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.delete(
    "https://api.meta.ai/v1/files/file_abc123",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X DELETE "https://api.meta.ai/v1/files/file_abc123" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```


## Next steps

Now that you can get files to the model, put them to work:

- Analyze images you uploaded with [image understanding](/docs/image-understanding).
- Reference files in multi-turn workflows with the [Responses API](/docs/protocols/responses).
- See the [Files API reference](/docs/api-reference/files) for the complete upload, list, retrieve, and delete endpoints.