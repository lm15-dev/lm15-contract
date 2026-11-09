# Images

Add PNG or JPEG images and text to the same Inkling conversation. Common uses include:

- **Image captioning** — “Describe this image.”
- **Visual question answering** — “How many people are in the image?”
- **Document understanding** — “Extract the totals from this receipt.”
- **Image classification** — “Which product category best matches this image?”

Use either a native `ImagePointer`, an OpenAI-compatible `image_url` part, or a Cookbook `ImagePart`.

`ImagePointer` carries the image location, format, width, and height. `tml-renderers` uses those dimensions to calculate how many image tokens the model input needs.

## Native chat messages

Use `ImagePointer` when you know the local path and dimensions:

```python
from tml_renderers import chat

user = chat.Author(chat.AuthorKind.User)
image = chat.ImagePointer(
    location="photo.png",
    format=chat.ImageFormat.Png,
    width=512,
    height=384,
)
messages = [
    chat.Message(content=chat.Text("Describe this image."), author=user),
    chat.Message(content=image, author=user),
]
```

The dimensions determine the expected number of image tokens.

## OpenAI-compatible Cookbook messages

Use an OpenAI-compatible `image_url` content part with a base64 data URI:

```python
data_uri = "data:image/png;base64,..."
text_part = {"type": "text", "text": "Describe this image."}
image_part = {"type": "image_url", "image_url": {"url": data_uri}}
messages = [{"role": "user", "content": [text_part, image_part]}]
```

When given a decodable data URI, `tml-renderers` derives the image format and dimensions. The Cookbook Inkling renderer accepts these dictionaries directly.

Cookbook-native image parts are supported too:

```python
image_part = {"type": "image", "image": "photo.png"}
```

The renderer reads the image and constructs the same image input.

## Accepted image input

- **Formats:** PNG and JPEG.
- **Locations:** Local paths, `file://` URIs, and base64 data URIs.
- **Native pointers:** Provide `width` and `height`.
- **OpenAI-compatible data URIs:** Dimensions and format are decoded from the image bytes.
- **Cookbook image parts:** Accept a local path, data URI, or PIL image.
- **Remote media:** HTTP and cloud-storage URLs are not fetched. Download the image in your application first.

## Client-side image handling

`ImagePointer` holds the image location, format, and dimensions. When you build the generation prompt, `tml-renderers` validates this information and prepares the image input expected by Inkling.

You do not need to generate image patches yourself. Your application supplies valid PNG or JPEG bytes and, for native pointers, the correct width and height.

## Run the example

[`sample_vision.py`](https://github.com/thinking-machines-lab/tinker-cookbook/blob/main/tinker_cookbook/scripts/inkling/sample_vision.py) demonstrates the complete sampling flow:

```bash
uv run python -m tinker_cookbook.scripts.inkling.sample_vision
uv run python -m tinker_cookbook.scripts.inkling.sample_vision message_format=chat
```

Pass `image_path=/path/to/image.png` to use your own image.

For a complete image-training workflow, including dataset loading, supervised training, and evaluation, use the [VLM classifier recipe](https://tinker-docs.thinkingmachines.ai/cookbook/recipes/vlm-classifier/index.md).

## Learn more

- **[VLM classifier recipe](https://tinker-docs.thinkingmachines.ai/cookbook/recipes/vlm-classifier/index.md)** — End-to-end supervised image classification.
- **[Rendering tutorial](https://tinker-docs.thinkingmachines.ai/tutorials/core-concepts/rendering/index.md)** — Cookbook renderers and `ImagePart`.
- **[tml-renderers](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/tml-renderers/index.md)** — The common rendering and sampling flow.
