> ## Documentation Index
> Fetch the complete documentation index at: https://docs.together.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Use image inputs

> Run vision-language models on Together: pass images alongside text and get structured replies, transcripts, comparisons, or extracted data.

Vision-language models accept images alongside text and reply in natural language, structured JSON, or tool calls. For the current list of vision-capable models, see the [serverless catalog](/docs/serverless/models) or the [dedicated model inference catalog](/docs/dedicated-endpoints/models).

## Basic example

Pass a `messages` array where the user content is a list mixing `text` and `image_url` blocks. The model treats them as a single multimodal prompt and replies with text in `choices[0].message.content`. The example below points the model at an image of a Trello board and asks it to describe the UI in detail; the response streams back token-by-token.

<CodeGroup>
  ```python Python theme={null}
  from together import Together

  client = Together()

  getDescriptionPrompt = "You are a UX/UI designer. Describe the attached screenshot or UI mockup in detail. I will feed in the output you give me to a coding model that will attempt to recreate this mockup, so please think step by step and describe the UI in detail. Pay close attention to background color, text color, font size, font family, padding, margin, border, etc. Match the colors and sizes exactly. Make sure to mention every part of the screenshot including any headers, footers, etc. Use the exact text from the screenshot."

  imageUrl = "https://napkinsdev.s3.us-east-1.amazonaws.com/next-s3-uploads/d96a3145-472d-423a-8b79-bca3ad7978dd/trello-board.png"

  stream = client.chat.completions.create(
      model="moonshotai/Kimi-K3",
      max_tokens=2048,
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": getDescriptionPrompt},
                  {"type": "image_url", "image_url": {"url": imageUrl}},
              ],
          }
      ],
      stream=True,
  )

  # Kimi K3 is reasoning-default. Reasoning tokens stream first, then content.
  for chunk in stream:
      if not chunk.choices:
          continue
      delta = chunk.choices[0].delta
      if getattr(delta, "reasoning", None):
          print(delta.reasoning, end="", flush=True)
      if getattr(delta, "content", None):
          print(delta.content, end="", flush=True)
  ```

  ```typescript TypeScript theme={null}
  import Together from "together-ai";

  const together = new Together();

  let getDescriptionPrompt = `You are a UX/UI designer. Describe the attached screenshot or UI mockup in detail. I will feed in the output you give me to a coding model that will attempt to recreate this mockup, so please think step by step and describe the UI in detail.

  - Pay close attention to background color, text color, font size, font family, padding, margin, border, etc. Match the colors and sizes exactly.
  - Make sure to mention every part of the screenshot including any headers, footers, etc.
  - Use the exact text from the screenshot.
  `;
  let imageUrl =
    "https://napkinsdev.s3.us-east-1.amazonaws.com/next-s3-uploads/d96a3145-472d-423a-8b79-bca3ad7978dd/trello-board.png";

  async function main() {
    const stream = await together.chat.completions.create({
      model: "moonshotai/Kimi-K3",
      temperature: 0.2,
      stream: true,
      max_tokens: 2048,
      messages: [
        {
          role: "user",
          // @ts-expect-error Need to fix the TypeScript library type
          content: [
            { type: "text", text: getDescriptionPrompt },
            {
              type: "image_url",
              image_url: {
                url: imageUrl,
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
  curl -X POST "https://api.together.ai/v1/chat/completions" \
       -H "Authorization: Bearer $TOGETHER_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{
         "model": "moonshotai/Kimi-K3",
         "max_tokens": 2048,
         "messages": [
           {
             "role": "user",
             "content": [
               {
                 "type": "text",
                 "text": "You are a UX/UI designer. Describe the attached screenshot or UI mockup in detail. I will feed in the output you give me to a coding model that will attempt to recreate this mockup, so please think step by step and describe the UI in detail. Pay close attention to background color, text color, font size, font family, padding, margin, border, etc. Match the colors and sizes exactly. Make sure to mention every part of the screenshot including any headers, footers, etc. Use the exact text from the screenshot."
               },
               {
                 "type": "image_url",
                 "image_url": {
                   "url": "https://napkinsdev.s3.us-east-1.amazonaws.com/next-s3-uploads/d96a3145-472d-423a-8b79-bca3ad7978dd/trello-board.png"
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
  The attached screenshot appears to be a Trello board, a project management tool used for organizing tasks and projects into boards. Below is a detailed breakdown of the UI:

  **Header**
  -----------------

  * A blue bar spanning the top of the page
  * White text reading "Trello" in the top-left corner
  * White text reading "Workspaces", "Recent", "Starred", "Templates", and "Create" in the top-right corner, separated by small white dots
  * A white box with a blue triangle and the word "Board" inside it

  **Top Navigation Bar**
  ----------------------

  * A blue bar with white text reading "Project A"
  * A dropdown menu with options "Workspace visible" and "Board"
  * A search bar with a magnifying glass icon

  **Main Content**
  -----------------

  * Three columns of cards with various tasks and projects
  * Each column has a header with a title
  * Cards are white with gray text and a blue border
  * Each card has a checkbox, a title, and a description
  * Some cards have additional details such as a yellow or green status indicator, a due date, and comments

  **Footer**
  ------------

  * A blue bar with white text reading "Add a card"
  * A button to add a new card to the board

  **Color Scheme**
  -----------------

  * Blue and white are the primary colors used in the UI
  * Yellow and green are used as status indicators
  * Gray is used for text and borders

  **Font Family**
  ----------------

  * The font family used throughout the UI is clean and modern, with a sans-serif font

  **Iconography**
  ----------------

  * The UI features several icons, including:
          + A magnifying glass icon for the search bar
          + A triangle icon for the "Board" dropdown menu
          + A checkbox icon for each card
          + A status indicator icon (yellow or green)
          + A comment icon (a speech bubble)

  **Layout**
  ------------

  * The UI is divided into three columns: "To Do", "In Progress", and "Done"
  * Each column has a header with a title
  * Cards are arranged in a vertical list within each column
  * The cards are spaced evenly apart, with a small gap between each card

  **Overall Design**
  -------------------

  * The UI is clean and modern, with a focus on simplicity and ease of use
  * The use of blue and white creates a sense of calmness and professionalism
  * The icons and graphics are simple and intuitive, making it easy to navigate the UI

  This detailed breakdown provides a comprehensive understanding of the UI mockup, including its layout, color scheme, and components.
  ```
</Accordion>

## Pricing

Vision models bill images as **input tokens**. Each image breaks into a tile grid (capped at 2×2 of 560-pixel tiles) and you pay **1,601 tokens per tile**. There are only four possible image bills:

| Image size (W × H)                     | Tile grid | Image tokens |
| -------------------------------------- | :-------: | -----------: |
| Up to 559 × 559                        |   1 × 1   |        1,601 |
| Up to 559 tall, wider than 560         |   1 × 2   |        3,202 |
| Taller than 560, up to 559 wide        |   2 × 1   |        3,202 |
| Wider than 560 **and** taller than 560 |   2 × 2   |        6,404 |

A 4K screenshot and a 1280×720 photo are billed the same (both are 2×2). The image tokens are added to your prompt's text tokens; output tokens are billed separately at the model's standard rate.

The exact formula:

```python theme={null}
image_tokens = (
    min(2, max(width // 560, 1)) * min(2, max(height // 560, 1)) * 1601
)
```
