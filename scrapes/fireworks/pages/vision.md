> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Vision Models

> Query vision-language models to analyze images and visual content

Vision-language models (VLMs) process both text and images in a single request, enabling image captioning, visual question answering, document analysis, chart interpretation, OCR, and content moderation. Use VLMs via serverless inference or [dedicated deployments](/getting-started/ondemand-quickstart).

[Browse available vision models →](https://app.fireworks.ai/models?filter=Vision)

## Chat Completions API

Provide images via URL or base64 encoding. The request structure is identical to OpenAI's vision API.

<Tabs>
  <Tab title="Python">
    ```python theme={null}
    from fireworks import Fireworks

    client = Fireworks()

    response = client.chat.completions.create(
        model="accounts/fireworks/models/kimi-k2p5",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Can you describe this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://images.unsplash.com/photo-1582538885592-e70a5d7ab3d3?w=800"
                        }
                    }
                ]
            }
        ]
    )

    print(response.choices[0].message.content)
    ```

    <Tip>
      You can also use the [OpenAI SDK](/tools-sdks/openai-compatibility) with Fireworks by changing the base URL and API key.
    </Tip>
  </Tab>

  <Tab title="JavaScript">
    ```javascript theme={null}
    import OpenAI from "openai";

    const client = new OpenAI({
      apiKey: process.env.FIREWORKS_API_KEY,
      baseURL: "https://api.fireworks.ai/inference/v1",
    });

    const response = await client.chat.completions.create({
      model: "accounts/fireworks/models/kimi-k2p5",
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: "Can you describe this image?" },
            {
              type: "image_url",
              image_url: {
                url: "https://images.unsplash.com/photo-1582538885592-e70a5d7ab3d3?w=800"
              }
            }
          ]
        }
      ]
    });

    console.log(response.choices[0].message.content);
    ```
  </Tab>

  <Tab title="curl">
    ```bash theme={null}
    curl https://api.fireworks.ai/inference/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $FIREWORKS_API_KEY" \
      -d '{
        "model": "accounts/fireworks/models/kimi-k2p5",
        "messages": [
          {
            "role": "user",
            "content": [
              {"type": "text", "text": "Can you describe this image?"},
              {
                "type": "image_url",
                "image_url": {
                  "url": "https://images.unsplash.com/photo-1582538885592-e70a5d7ab3d3?w=800"
                }
              }
            ]
          }
        ]
      }'
    ```
  </Tab>
</Tabs>

### Using base64-encoded images

For local files, encode them as base64 with the appropriate MIME type prefix:

<Tabs>
  <Tab title="Python">
    ```python theme={null}
    import base64
    from fireworks import Fireworks

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    image_base64 = encode_image("your_image.jpg")

    client = Fireworks()

    response = client.chat.completions.create(
        model="accounts/fireworks/models/kimi-k2p5",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Can you describe this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    )

    print(response.choices[0].message.content)
    ```
  </Tab>

  <Tab title="JavaScript">
    ```javascript theme={null}
    import OpenAI from "openai";
    import fs from "fs";

    const client = new OpenAI({
      apiKey: process.env.FIREWORKS_API_KEY,
      baseURL: "https://api.fireworks.ai/inference/v1",
    });

    const imageBase64 = fs.readFileSync("your_image.jpg").toString("base64");

    const response = await client.chat.completions.create({
      model: "accounts/fireworks/models/kimi-k2p5",
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: "Can you describe this image?" },
            {
              type: "image_url",
              image_url: {
                url: `data:image/jpeg;base64,${imageBase64}`
              }
            }
          ]
        }
      ]
    });

    console.log(response.choices[0].message.content);
    ```
  </Tab>
</Tabs>

## Working with images

Vision-language models support [prompt caching](/guides/prompt-caching) to improve performance for requests with repeated content. Both text and image portions can benefit from caching to reduce time to first token by up to 80%.

**Tips for optimal performance:**

* **Use URLs for long conversations** – Reduces latency compared to base64 encoding
* **Downsize images** – Smaller images use fewer tokens and process faster
* **Structure prompts for caching** – Place static instructions at the beginning, variable content at the end
* **Include metadata in prompts** – Add context about the image directly in your text prompt

## Working with PDFs

VLMs do not natively accept PDF files as input. To analyze PDF documents, convert each page to an image and pass the images to the model using base64 encoding.

<Note>
  Remember the [30-image limit per request](#known-limitations). For long documents, process pages in batches or select only the relevant pages.
</Note>

<Tabs>
  <Tab title="Python">
    Install [PyMuPDF](https://pymupdf.readthedocs.io/):

    ```bash theme={null}
    pip install pymupdf fireworks-ai
    ```

    ```python theme={null}
    import base64
    import fitz
    from fireworks.client import Fireworks


    def pdf_pages_to_base64(pdf_path, dpi=200):
        doc = fitz.open(pdf_path)
        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            images.append(base64.b64encode(pix.tobytes("png")).decode("utf-8"))
        doc.close()
        return images


    page_images = pdf_pages_to_base64("document.pdf")

    client = Fireworks()

    content = [{"type": "text", "text": "Summarize this document."}]
    for img in page_images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}"}
        })

    response = client.chat.completions.create(
        model="accounts/fireworks/models/kimi-k2p5",
        messages=[{"role": "user", "content": content}]
    )

    print(response.choices[0].message.content)
    ```
  </Tab>

  <Tab title="JavaScript">
    Install [pdf-to-img](https://www.npmjs.com/package/pdf-to-img) and [openai](https://www.npmjs.com/package/openai):

    ```bash theme={null}
    npm install pdf-to-img openai
    ```

    ```javascript theme={null}
    import { pdf } from "pdf-to-img";
    import OpenAI from "openai";

    const client = new OpenAI({
      apiKey: process.env.FIREWORKS_API_KEY,
      baseURL: "https://api.fireworks.ai/inference/v1",
    });

    const pages = [];
    for await (const page of await pdf("document.pdf", { scale: 2.0 })) {
      pages.push(Buffer.from(page).toString("base64"));
    }

    const content = [
      { type: "text", text: "Summarize this document." },
      ...pages.map((base64) => ({
        type: "image_url",
        image_url: { url: `data:image/png;base64,${base64}` },
      })),
    ];

    const response = await client.chat.completions.create({
      model: "accounts/fireworks/models/kimi-k2p5",
      messages: [{ role: "user", content }],
    });

    console.log(response.choices[0].message.content);
    ```
  </Tab>
</Tabs>

## Advanced capabilities

<CardGroup cols={2}>
  <Card title="Vision training" href="/fine-tuning/fine-tuning-models#vision-training" icon="sliders">
    Train VLMs for specialized visual tasks
  </Card>

  <Card title="LoRA adapters" href="/models/uploading-custom-models" icon="layer-group">
    Deploy custom LoRA adapters for vision models
  </Card>

  <Card title="Dedicated deployments" href="/getting-started/ondemand-quickstart" icon="server">
    Deploy VLMs on dedicated GPUs for better performance
  </Card>

  <Card title="Video & audio inputs" href="/guides/video-audio-inputs" icon="video">
    Process video and audio content with multimodal models
  </Card>
</CardGroup>

## Alternative query methods

For the Completions API, manually insert the image token `<image>` in your prompt and supply images as an ordered list:

```python theme={null}
response = client.completions.create(
    model="accounts/fireworks/models/kimi-k2p5",
    prompt="SYSTEM: Hello\n\nUSER:<image>\ntell me about the image\n\nASSISTANT:",
    extra_body={
        "images": ["https://images.unsplash.com/photo-1582538885592-e70a5d7ab3d3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1770&q=80"]
    }
)

print(response.choices[0].text)
```

## Known limitations

1. **Maximum images per request**: 30 images maximum, regardless of format (base64 or URL)
2. **Base64 size limit**: Total base64-encoded images must be less than 10MB
3. **URL size and timeout**: Each image URL must be smaller than 5MB and download within 1.5 seconds
4. **Supported formats**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.ppm`
5. **Llama 3.2 Vision models**: Pass images before text in the content field to avoid refusals (temporary limitation)
