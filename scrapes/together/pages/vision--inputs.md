> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Vision input modes

> Send local images, video URLs, or multiple images to a vision model in a single request.

Beyond a single hosted image URL, vision models accept local files (base64-encoded), video URLs, and multiple images in one prompt. For the basic URL example and supported models, see the [Vision overview](/docs/inference/vision/overview).

## Local images

To query a vision model with a local image:

<CodeGroup>
  ```python Python theme={null}
  from together import Together
  import base64

  client = Together()

  getDescriptionPrompt = "what is in the image"

  imagePath = "/home/Desktop/dog.jpeg"


  def encode_image(image_path):
      with open(image_path, "rb") as image_file:
          return base64.b64encode(image_file.read()).decode("utf-8")


  base64_image = encode_image(imagePath)

  stream = client.chat.completions.create(
      model="moonshotai/Kimi-K3",
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": getDescriptionPrompt},
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": f"data:image/jpeg;base64,{base64_image}"
                      },
                  },
              ],
          }
      ],
      stream=True,
  )

  for chunk in stream:
      print(
          chunk.choices[0].delta.content or "" if chunk.choices else "",
          end="",
          flush=True,
      )
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";
  import fs from "fs/promises";

  const together = new Together();

  const getDescriptionPrompt = "what is in the image";

  const imagePath = "./dog.jpeg";

  async function main() {
    const imageUrl = await fs.readFile(imagePath, { encoding: "base64" });

    const stream = await together.chat.completions.create({
      model: "moonshotai/Kimi-K3",
      stream: true,
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: getDescriptionPrompt },
            {
              type: "image_url",
              image_url: {
                url: `data:image/jpeg;base64,${imageUrl}`,
              },
            },
          ],
        },
      ],
    });

    for await (const chunk of stream) {
      process.stdout.write(chunk.choices[0]?.delta?.content || "");
    }
  }

  main();
  ```

  ```bash cURL theme={null}
  # Replace <BASE64_IMAGE> with your base64-encoded image data.
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
         "model": "moonshotai/Kimi-K3",
         "messages": [
           {
             "role": "user",
             "content": [
               {
                 "type": "text",
                 "text": "what is in the image"
               },
               {
                 "type": "image_url",
                 "image_url": {
                   "url": "data:image/jpeg;base64,<BASE64_IMAGE>"
                 }
               }
             ]
           }
         ]
       }'
  ```
</CodeGroup>

### Output

```
The image contains two dogs sitting close to each other
```

## Video input

Video understanding (passing a `video_url` content block to a chat completion) is supported on select VLMs that run only as a [dedicated endpoint](/docs/dedicated-endpoints/overview), for example `Qwen/Qwen3-VL-8B-Instruct`. Spin up a dedicated endpoint, then pass the endpoint name as `model` and a `video_url` block alongside `text`:

```python Python theme={null}
from together import Together

client = Together()

response = client.chat.completions.create(
    model="<ACCOUNT>/Qwen/Qwen3-VL-8B-Instruct-<ENDPOINT_HASH>",  # your dedicated endpoint name
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's happening in this video?"},
                {
                    "type": "video_url",
                    "video_url": {
                        "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
                    },
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)
```

For text-to-video and image-to-video *generation* (separate from video understanding), see [Video generation](/docs/inference/videos/overview).

## Multiple images

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  # Multi-modal message with multiple images
  response = client.chat.completions.create(
      model="moonshotai/Kimi-K3",
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": "Compare these two images."},
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": "https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/yosemite.png"
                      },
                  },
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": "https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/slack.png"
                      },
                  },
              ],
          }
      ],
  )

  print(response.choices[0].message.content)
  ```

  ```typescript TypeScript theme={null}
  // Multi-modal message with multiple images

  async function main() {
    const response = await together.chat.completions.create({
      model: "moonshotai/Kimi-K3",
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: "Compare these two images." },
            {
              type: "image_url",
              image_url: {
                url: "https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/yosemite.png",
              },
            },
            {
              type: "image_url",
              image_url: {
                url: "https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/slack.png",
              },
            },
          ],
        },
      ],
    });
    
    process.stdout.write(response.choices[0]?.message?.content || "");
  }

  main();
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
         "model": "moonshotai/Kimi-K3",
         "messages": [
           {
             "role": "user",
             "content": [
               {
                 "type": "text",
                 "text": "Compare these two images."
               },
               {
                 "type": "image_url",
                 "image_url": {
                   "url": "https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/yosemite.png"
                 }
               },
               {
                 "type": "image_url",
                 "image_url": {
                   "url": "https://huggingface.co/datasets/patrickvonplaten/random_img/resolve/main/slack.png"
                 }
               }
             ]
           }
         ]
       }'
  ```
</CodeGroup>

<Accordion title="Sample model output">
  ```text theme={null}
  The first image is a collage of multiple identical landscape photos showing a natural scene with rocks, trees, and a stream under a blue sky. The second image is a screenshot of a mobile app interface, specifically the navigation menu of the Canva app, which includes icons for Home, DMs (Direct Messages), Activity, Later, Canvases, and More.

  #### Comparison:
  1. **Content**:
     - The first image focuses on a natural landscape.
     - The second image shows a digital interface from an app.

  2. **Purpose**:
     - The first image could be used for showcasing nature, design elements in graphic work, or as a background.
     - The second image represents the functionality and layout of the Canva app's navigation system.

  3. **Visual Style**:
     - The first image has vibrant colors and realistic textures typical of outdoor photography.
     - The second image uses flat design icons with a simple color palette suited for user interface design.

  4. **Context**:
     - The first image is likely intended for artistic or environmental contexts.
     - The second image is relevant to digital design and app usability discussions.
  ```
</Accordion>
