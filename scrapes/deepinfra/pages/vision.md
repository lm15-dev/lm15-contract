> ## Documentation Index
> Fetch the complete documentation index at: https://docs.deepinfra.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Vision & OCR

> Send images to multimodal models for visual understanding and text extraction.

DeepInfra hosts multimodal models that accept both images and text as input and produce text output. These models use the standard OpenAI vision API format and cover two major use cases:

* **Visual understanding** — describe images, answer questions about visual content, compare images, analyze charts
* **OCR (Optical Character Recognition)** — extract text from scanned documents, receipts, invoices, screenshots, handwritten notes, and PDFs

## Available vision models

Browse [all vision models](https://deepinfra.com/models/ocr).

## Available OCR models

We host a growing set of OCR-specialized models for high-accuracy text extraction. Browse the [full OCR model catalog](https://deepinfra.com/models/ocr/).

OCR models currently use the same vision API format below. A dedicated OCR endpoint optimized for document processing is coming soon.

## Quick start

Images are passed in two ways:

1. **URL** — pass a link to a publicly accessible image
2. **Base64** — encode the image and include it directly in the request

### Image URL

```bash theme={null}
curl "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
  -d '{
    "model": "Qwen/Qwen3-VL-235B-A22B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
              "url": "https://shared.deepinfra.com/models/Qwen/Qwen3-VL-235B-A22B-Instruct/cover_image.188ae740a50d6f2f48bed81f834ffbe2fe5a0f38bd96dbd312ef804c18aad0c4.webp"
            }
          },
          {
            "type": "text",
            "text": "What'\''s in this image?"
          }
        ]
      }
    ]
  }'
```

### Base64 encoded image

```python theme={null}
import os

from openai import OpenAI
import base64
import requests

openai = OpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)

image_url = "https://shared.deepinfra.com/models/Qwen/Qwen3-VL-235B-A22B-Instruct/cover_image.188ae740a50d6f2f48bed81f834ffbe2fe5a0f38bd96dbd312ef804c18aad0c4.webp"
base64_image = base64.b64encode(requests.get(image_url).content).decode("utf-8")

chat_completion = openai.chat.completions.create(
    model="Qwen/Qwen3-VL-235B-A22B-Instruct",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                },
                {
                    "type": "text",
                    "text": "What's in this image?"
                }
            ]
        }
    ]
)

print(chat_completion.choices[0].message.content)
```

## OCR example

Extract all text from a document image:

```python theme={null}
import os

from openai import OpenAI
import base64

openai = OpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)

with open("invoice.png", "rb") as f:
    base64_image = base64.b64encode(f.read()).decode("utf-8")

response = openai.chat.completions.create(
    model="Qwen/Qwen3-VL-235B-A22B-Instruct",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                },
                {
                    "type": "text",
                    "text": "Extract all text from this document. Preserve the structure and layout as much as possible."
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

Common OCR prompts:

* `"Extract all text from this image."` — basic extraction
* `"Extract all text and return it as structured JSON with field names and values."` — structured extraction (e.g. invoices, forms)
* `"Transcribe the handwritten text in this image."` — handwriting recognition
* `"List all line items, quantities, and prices from this receipt."` — targeted extraction

## Multiple images

You can pass multiple images in a single request by including multiple `image_url` content items:

```bash theme={null}
curl "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
  -d '{
    "model": "Qwen/Qwen3-VL-235B-A22B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {"url": "https://example.com/page1.jpg"}
          },
          {
            "type": "image_url",
            "image_url": {"url": "https://example.com/page2.jpg"}
          },
          {
            "type": "text",
            "text": "Extract all text from both pages."
          }
        ]
      }
    ]
  }'
```

## Pricing and token counting

Images are tokenized and billed as input tokens. The number of tokens consumed by an image is reported in the response under `"usage": {"prompt_tokens": ...}`.

Different models work with different image resolutions. You can still pass images of any resolution — the model will rescale them automatically. Check the model's documentation page for supported resolutions.

## Limitations

* Supported image formats: **jpg**, **png**, **webp**
* Maximum image size: **20MB**
* The `detail` parameter (image fidelity) is not currently supported
