---
meta:
  title: Video and audio understanding
  description: Analyze video and audio with text prompts—summarize clips, answer questions about footage, and transcribe speech—on the Responses API and Chat Completions.
  keywords: video understanding, video analysis, audio understanding, speech transcription, multimodal, mp4, wav, mp3, file upload, audio
cms:
  alias: /model-api/docs/video-understanding
  target: aidmc
---

# Video and audio understanding

[Muse Spark](/docs/models#muse-spark) reads both moving pictures and sound. Summarize a clip, ask what happened when, extract structured details you can use downstream, or transcribe speech from a recording. Upload the media once (or pass a URL), add a text prompt, and the model returns text. Video and audio both work on the [Responses API](/docs/protocols/responses) and [Chat Completions](/docs/protocols/chat-completions).

## Video {#video}

Muse Spark reads a video's visual sequence and any embedded audio together, so one upload can both describe the footage and transcribe its speech.

### How it works {#how-it-works}

Video understanding takes two steps:

1. **Upload** the video through the [Files API](/docs/file-handling) with `purpose` set to `"user_data"`.
2. **Reference** the uploaded file by ID in a [Responses API](/docs/protocols/responses) request using an `input_file` content block.

The model processes the video alongside your prompt and returns a text response.

> [!NOTE] Works on both APIs
> Video works on both the [Responses API](/docs/protocols/responses) and [Chat Completions](/docs/protocols/chat-completions). This page shows the Responses + Files API workflow: upload, then reference by `file_id`, which we recommend for uploaded videos. Chat Completions accepts video through a `video_url` content part.

> [!NOTE] Reads embedded audio too
> Muse Spark reads a video's embedded audio too, not just its frames — a single upload can return both a visual description and a transcript of any speech in one call. See [Audio](#audio) below. Videos without an audio track (such as screen recordings or animated renders) are also valid input.

### Basic usage {#basic-usage}

Upload a file, then ask Muse Spark to describe what it sees. Reference the uploaded video by `file_id` with an `input_file` content block.

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
                    "text": "Describe what happens in this video.",
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
          text: 'Describe what happens in this video.',
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
                        "text": "Describe what happens in this video.",
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
          "text": "Describe what happens in this video."
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


### Reference a video by URL {#video-url}

If the video is already hosted where the API can reach it, skip the upload and pass it directly. An `input_video` block accepts `video_url`—a public or base64 data URL—or a `file_id` for a video uploaded through the [Files API](/docs/file-handling).

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
                    "text": "Describe what happens in this video.",
                },
                {
                    "type": "input_video",
                    "video_url": "https://example.com/clip.mp4",
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
          text: 'Describe what happens in this video.',
        },
        {
          type: 'input_video',
          video_url: 'https://example.com/clip.mp4',
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
                        "text": "Describe what happens in this video.",
                    },
                    {
                        "type": "input_video",
                        "video_url": "https://example.com/clip.mp4",
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
          "text": "Describe what happens in this video."
        },
        {
          "type": "input_video",
          "video_url": "https://example.com/clip.mp4"
        }
      ]
    }
  ]
}'
```


Use `input_file` or `input_video` with `file_id` for videos you upload through the Files API; use `input_video` with `video_url` for a video at a public URL.

## Audio {#audio}

> [!WARNING]
> Audio understanding in Muse Spark 1.3 is currently not fully supported, and response quality for requests including audio content may be degraded. These examples use Muse Spark 1.2 instead.

Muse Spark transcribes spoken audio to text, whether it arrives as a standalone file or as the soundtrack of a video.

### Transcribe a standalone audio file {#speech}

Send the audio as an `input_audio` content part on [Chat Completions](/docs/protocols/chat-completions) or the [Responses API](/docs/protocols/responses) (`audio/mpeg` or `audio/wav`, uploaded or inline base64). An example for each endpoint follows. First, read the file and base64-encode it; both request examples below reference this `audio_b64` variable:

```python title="Python"
import base64

with open("speech.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()
```
```typescript title="TypeScript"
import fs from 'fs';

const audio_b64 = fs.readFileSync('speech.wav').toString('base64');
```


On Chat Completions, `input_audio` goes in the message content:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.chat.completions.create(
    model="muse-spark-1.2",
    max_tokens=4000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Transcribe this audio. Return only the transcript.",
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_b64,
                        "format": "wav",
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
        "model": "muse-spark-1.2",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe this audio. Return only the transcript.",
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": "wav",
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
  model: 'muse-spark-1.2',
  max_tokens: 4000,
  messages: [
    {
      role: 'user',
      content: [
        {
          type: 'text',
          text: 'Transcribe this audio. Return only the transcript.',
        },
        {
          type: 'input_audio',
          input_audio: {
            data: audio_b64,
            format: 'wav',
          },
        },
      ],
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```


The [Responses API](/docs/protocols/responses) accepts the same `input_audio` content part — send inline `input_audio` (`{data, format}`), an `audio_url` data URI, or a `file_id` for an uploaded audio file:

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.responses.create(
    model="muse-spark-1.2",
    max_output_tokens=4000,
    input=[
        {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Transcribe this audio. Return only the transcript.",
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_b64,
                        "format": "wav",
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
    "https://api.meta.ai/v1/responses",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.2",
        "max_output_tokens": 4000,
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Transcribe this audio. Return only the transcript.",
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": "wav",
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

const response = await client.responses.create({
  model: 'muse-spark-1.2',
  max_output_tokens: 4000,
  input: [
    {
      type: 'message',
      role: 'user',
      content: [
        {
          type: 'input_text',
          text: 'Transcribe this audio. Return only the transcript.',
        },
        {
          type: 'input_audio',
          input_audio: {
            data: audio_b64,
            format: 'wav',
          },
        },
      ],
    },
  ],
});

console.log(JSON.stringify(response, null, 2));
```


### Speech from a video {#video-audio}

A video part on either endpoint also carries its embedded audio, so a single video upload can transcribe its speech alongside visual understanding. See [Video](#video) above.

### Transcription tips {#transcription-tips}

Two things to get right for transcription:

- **Give the response room.** Muse Spark is a reasoning model and reasoning shares the output budget — set `max_tokens` (or `max_output_tokens`) to at least `4000`, or a transcript can come back empty with `finish_reason: length`.
- **Stream long audio.** High reasoning effort on a long clip can take a while before the first token; set `stream: true` and/or lower `reasoning_effort` to avoid an idle-timeout disconnect.

## Supported formats {#supported-formats}

Video understanding supports mp4 files; audio understanding supports MP3 and WAV.

| MIME type | Extension |
| :---- | :---- |
| `video/mp4` | `.mp4` |
| `audio/mpeg` | `.mp3` |
| `audio/wav` | `.wav` |

## Next steps

- Add still-image analysis with [image understanding](/docs/image-understanding).
- Manage uploads and reuse files with the [Files API](/docs/file-handling).
- Check the full request schema in the [Responses API reference](/docs/api-reference/responses).