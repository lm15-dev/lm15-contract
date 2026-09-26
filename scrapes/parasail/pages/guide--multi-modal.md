> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/guides/multi-modal.md).

# Multi-Modal

Send images to vision-language models like Qwen2.5-VL using base64 data URLs through Parasail's OpenAI-compatible API.

**Multimodal** (or Multi-Modal) refers to systems or methods that can process or integrate **multiple types of data**, typically from different modalities such as **text, image, audio, video, and other sensory inputs**. Multi-modal systems aim to understand and generate outputs based on this diverse, merged information, mimicking human perception, where we simultaneously use different senses (for example, seeing, hearing, and reading) to interpret the world.

In machine learning and AI, multi-modal models combine data from different modalities to improve the performance of tasks like classification, generation, captioning, and more. For example, an AI model that processes both images and text could interpret and respond to visual and written information in a cohesive and context-aware manner.

## Quickstart

The simplest way to use Vision Language Model is using OpenAI-compatible API and embed image input as base64 encoded data URLs.

Below is an example using Qwen2.5-VL 72 B model with Parasail's serverless API. GLM 4.5V also works with this example.

```python
!pip install openai > /dev/null

import base64
import openai
from IPython.display import Image, display

try:
  from google.colab import userdata
  API_KEY = userdata.get('PARASAIL_API_KEY')
except:
  import os
  API_KEY = os.getenv('PARASAIL_API_KEY')

!wget https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Flower_poster_2.jpg/1540px-Flower_poster_2.jpg -O flower.jpg &> /dev/null
display(Image("flower.jpg", width=500))

def data_url(image):
    with open(image, "rb") as f:
        return f"data:image/jpeg;base64," + base64.b64encode(f.read()).decode("ascii")

oai_client = openai.OpenAI(base_url="https://api.parasail.io/v1", api_key=API_KEY)

messages = [{
    "role": "user",
    "content": [
        { "type": "image_url", "image_url": { "url": data_url("flower.jpg")}},
        {"type": "text", "text": "What's in the image?"},
    ],
}]

chat_completion = oai_client.chat.completions.create(
    model="parasail-qwen25-vl-72b-instruct", messages=messages)

print(chat_completion.choices[0].message.content)
```

```
[33mWARNING: Ignoring invalid distribution ~vidia-cufft-cu12 (/usr/local/lib/python3.11/dist-packages)[0m[33m
[0m[33mWARNING: Ignoring invalid distribution ~vidia-cufft-cu12 (/usr/local/lib/python3.11/dist-packages)[0m[33m
[0m[33mWARNING: Ignoring invalid distribution ~vidia-cufft-cu12 (/usr/local/lib/python3.11/dist-packages)[0m[33m
[0m
```

![jpeg](https://3807676826-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FLSXNQZeD4w30hUaiugTx%2Fuploads%2Fgit-blob-d870024811b990b29afde833f7c9f0184477c9a2%2Fmulti_modal_1_1.jpg?alt=media)

```
The image is a collage of twelve different types of flowers, each labeled with its common name and scientific name. Here is a list of the flowers:

1. St Bernard's Lily (Anthericum liliago)
2. Bermuda Buttercup (Oxalis pes-caprae)
3. Oleander (Nerium oleander)
4. Lantana (Lantana camara)
5. Scarlet Pimpernel (Anagallis arvensis)
6. Verbascum (Verbascum sinuatum)
7. Common Mallow (Malva sylvestris)
8. Spanish Oyster (Scolymus hispanicum)
9. Stork's bill (Erodium malacoides)
10. Bindweed (Convolvulus arvensis)
11. Blue Gem (Hebes × franciscana)
12. Calla Lily (Zantedeschia aethiopica)

Each flower is depicted with vibrant colors and detailed features, showcasing the diversity and beauty of the flora.
```

As in the output, the model shows good visual understanding and OCR ability.

## Vision Capabilities

### Limitations

Our public serverless model can support up to 8 input images for multimodal LLMs. For private dedicated deployments, the model supports 2 input images for RTX4090s and 8 input images for A100s, H100s, and H200s. If you need a different configuration than this than [please contact us](https://parasail.clickup.com/forms/9011827181/p/f/8cjb4fd-3371/JDGNCNLKS6ULEJYCHA/help-form).

### Multiple Images: Document Visual Question Answering Example

To process multiple images, you can simply add multiple `image_url`items into the content list. The images are referenced in the order they are present in the content list and in the prompt.

```python
!apt-get install -qq -y poppler-utils &> /dev/null
!pip install pdf2image &> /dev/null
import pdf2image

!wget https://arxiv.org/pdf/1706.03762 -O transformer.pdf &> /dev/null

# Use multiple images as input
messages = []
for i, page in enumerate(pdf2image.convert_from_path("transformer.pdf", last_page=4)):
    page.save(f"page_{i}.jpg", 'JPEG')
    messages.append({"type": "image_url", "image_url": { "url": data_url(f"page_{i}.jpg")}})

messages = [{
    "role": "user",
    "content": messages + [{
        "type": "text",
        "text": "How many of encoder layers were used and where in the paper it's mentioned?"
    }]
}]

chat_completion = oai_client.chat.completions.create(
    model="parasail-qwen25-vl-72b-instruct", messages=messages)

display(Image("page_0.jpg", width=500))
print(chat_completion.choices[0].message.content)
```

![jpeg](https://3807676826-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FLSXNQZeD4w30hUaiugTx%2Fuploads%2Fgit-blob-db859489cb77346424767905863782f82d45ab33%2Fmulti_modal_4_0.jpg?alt=media)

```
The paper mentions that the encoder is composed of a stack of \( N = 6 \) identical layers. This is specified in the section "3.1 Encoder and Decoder Stacks" where it states:

"Encoder: The encoder is composed of a stack of \( N = 6 \) identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position-wise fully connected feed-forward network."
```

### Video Understanding

Qwen-2-VL and Qwen-2.5-VL support the `video_url` content type, where the data URL is a series of encoded base64 PNG frames separated by a comma. The Parasail gateway supports up to 20 MB in a single API request, so care must be taken to ensure the frame count and resolution fit in this limit.

The following notebook shows how to load an MP4 video, reorder the channels correctly in a Torch format, resize the video, and compile the data URL.

```python
!pip install torch torchvision opencv-python &> /dev/null
from IPython.display import Video

import os
import cv2
import gc
import math
import openai
import textwrap
import torch
import torchvision
```

```python
FPS = 2  # Video frame sample rate
MIN_FRAMES = 4
MAX_FRAMES = 110  #
FRAME_FACTOR = 2  #

IMAGE_FACTOR = 28  # Image patch size
VIDEO_MIN_PIXELS = 128 * 28 * 28  # Min number of pixels of a single video frame
VIDEO_MAX_PIXELS = 768 * 28 * 28  # Max number of pixels of a single video frame
VIDEO_TOTAL_PIXELS = 12000 * 28 * 28  # Max number of video pixels in a request
MAX_RATIO = 200  # Aspect ratio limit
MAX_GATEWAY_STRING_LEN = 20_000_000

def round_by_factor(number: int, factor: int) -> int:
    """Returns the closest integer to 'number' that is divisible by 'factor'."""
    return round(number / factor) * factor


def ceil_by_factor(number: int, factor: int) -> int:
    """Returns the smallest integer greater than or equal to 'number' that is divisible by 'factor'."""
    return math.ceil(number / factor) * factor


def floor_by_factor(number: int, factor: int) -> int:
    """Returns the largest integer less than or equal to 'number' that is divisible by 'factor'."""
    return math.floor(number / factor) * factor


def smart_resize(
    height: int, width: int, factor, min_pixels: int, max_pixels: int
) -> tuple[int, int]:
    """
    Rescales the image so that the following conditions are met:

    1. Both dimensions (height and width) are divisible by 'factor'.

    2. The total number of pixels is within the range ['min_pixels', 'max_pixels'].

    3. The aspect ratio of the image is maintained as closely as possible.
    """
    if max(height, width) / min(height, width) > MAX_RATIO:
        raise ValueError(
            f"absolute aspect ratio must be smaller than {MAX_RATIO}, got {max(height, width) / min(height, width)}"
        )
    h_bar = max(factor, round_by_factor(height, factor))
    w_bar = max(factor, round_by_factor(width, factor))
    if h_bar * w_bar > max_pixels:
        beta = math.sqrt((height * width) / max_pixels)
        h_bar = floor_by_factor(height / beta, factor)
        w_bar = floor_by_factor(width / beta, factor)
    elif h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h_bar = ceil_by_factor(height * beta, factor)
        w_bar = ceil_by_factor(width * beta, factor)
    return h_bar, w_bar


def extract_frames_smart_sampling(
    video_path,
    min_frames=MIN_FRAMES,
    max_frames=MAX_FRAMES,
    fps_target=FPS,
    frame_factor=FRAME_FACTOR,
):
    """Extract frames from a video with smart sampling based on target FPS and frame limits."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Height: {height}, Width: {width}, Frames: {total_frames}, FPS: {video_fps}")

    # Calculate number of frames to extract
    num_frames = min(max(total_frames / video_fps * fps_target, min_frames), max_frames)
    num_frames = round_by_factor(num_frames, frame_factor)

    # Sample frames evenly
    indices = torch.linspace(0, total_frames - 1, num_frames).round().long().tolist()

    # Extract frames
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    cap.release()
    return frames, height, width, num_frames


def process_video(
    video_path,
    image_factor=IMAGE_FACTOR,
    video_min_pixels=VIDEO_MIN_PIXELS,
    video_max_pixels=VIDEO_MAX_PIXELS,
    video_total_pixels=VIDEO_TOTAL_PIXELS,
):

    # Extract frames
    print("Extracting frames")
    frames, height, width, num_frames = extract_frames_smart_sampling(video_path)

    # Calculate max pixels per frame based on total pixel budget
    max_pixels = min(
        video_max_pixels,
        max(int(video_min_pixels * 1.05), video_total_pixels / num_frames),
    )

    # Calculate target dimensions
    resized_height, resized_width = smart_resize(
        height,
        width,
        factor=image_factor,
        min_pixels=video_min_pixels,
        max_pixels=max_pixels,
    )

    print(f"Resizing {len(frames)} frames to {resized_height}x{resized_width}")

    # Convert frames to torch tensors (batch processing)
    torch_frames = torch.stack(
        [torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0 for frame in frames]
    )

    # Resize all frames at once
    resized_frames = torchvision.transforms.functional.resize(
        torch_frames,
        [resized_height, resized_width],
        interpolation=torchvision.transforms.InterpolationMode.BICUBIC,
        antialias=True,
    )

    # Convert to uint8 and encode as PNG
    print("Encoding as PNG")
    resized_frames = (resized_frames * 255).to(torch.uint8)
    encoded_frames = [
        bytes(torchvision.io.encode_jpeg(frame)) for frame in resized_frames
    ]

    # Build data URL, stopping if it gets too large
    print("Building data URL")
    video_url = "data:video/jpeg;base64"
    for frame in encoded_frames:
        encoded = "," + base64.b64encode(frame).decode("utf-8")
        if len(video_url) + len(encoded) > MAX_GATEWAY_STRING_LEN:
            print(f"Data URL reached {len(video_url)} chars, truncating video")
            break
        video_url += encoded

    print(f"Done processing video. Data URL size: {len(video_url)}")
    return video_url, encoded_frames
```

```python
!wget https://upload.wikimedia.org/wikipedia/commons/2/2f/Making_snowman_in_K%C3%B5rvemaa%2C_Estonia_%28January_2022%29.webm -O snowman.webm &> /dev/null

print(f"Processing snowman.webm...")
Video("snowman.webm", embed=True)
video_url, frames = process_video("snowman.webm")

# Generate chat completions for each model/prompt pair.
chat_response = oai_client.chat.completions.create(
    model="parasail-qwen25-vl-72b-instruct",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "video_url", "video_url": {"url": video_url}},
                {"type": "text", "text": "Describe the video in detail"},
            ],
        }
    ],
    temperature=1,
    top_p=0.001,
    max_tokens=4096,
    extra_body={"repetition_penalty": 1.05},
)
print("---------------------------")
print(textwrap.fill(f"output={chat_response.choices[0].message.content}"))
print("=============================")


```

```
Processing snowman.webm...
Extracting frames
Height: 1080, Width: 1920, Frames: 3962, FPS: 25.0
Resizing 110 frames to 224x420
Encoding as PNG
Building data URL
Done processing video. Data URL size: 3467916
---------------------------
output=The video begins with a serene winter scene, showcasing a snow-
covered landscape with a small house nestled among tall, snow-laden
trees. The sky is overcast, adding to the tranquil and chilly
atmosphere of the setting. A person dressed warmly in winter clothing
walks into the frame from the left side, carrying a shovel. They
approach a patch of undisturbed snow near the house and begin to scoop
up large handfuls of snow.  As they gather more snow, they start
shaping it into a ball, rolling it on the ground to make it larger and
more compact. Once the base of the snowman is sufficiently large, they
repeat the process to create a second, smaller ball for the middle
section. With both sections ready, they carefully stack the smaller
ball on top of the larger one, ensuring it is stable.  Next, the
person shapes another, even smaller ball of snow for the head. They
lift it and place it atop the middle section, completing the basic
structure of the snowman. To add details, they find some small twigs
and sticks nearby and use them as arms, sticking them out from the
sides of the middle section. For the face, they search for suitable
objects and eventually find two small stones or pebbles, which they
place as eyes on the head. A small piece of carrot is used for the
nose, and a stick is broken into a short segment to serve as the
mouth.  Finally, the person steps back to admire their creation. The
snowman stands proudly in front of the house, surrounded by the
peaceful winter scenery. The person then walks away, leaving the
snowman as a cheerful addition to the snowy landscape. The video ends
with a wide shot of the completed snowman, emphasizing its charm and
the beauty of the winter environment.
=============================
```

### Object Detection and Localization

Models like Qwen2.5-VL series and [PaliGemma2](https://developers.googleblog.com/en/introducing-paligemma-2-mix/) are trained with object detection and localization capabilities. Simply prompt the model with the description of the objects of interest, the models can output object bounding boxes in the specified format.

Here is an example using the same Transformer paper image:

````python
import json
import PIL
import PIL.ImageDraw

# Prompt the model to output bouding box in JSON format.
messages = [{
    "role": "user",
    "content": [
        { "type": "image_url", "image_url": { "url": data_url("page_0.jpg")}},
        {"type": "text", "text": "Locate the abstract section, output its bbox coordinates using JSON format."},
    ],
}]

chat_completion = oai_client.chat.completions.create(
    model="parasail-qwen25-vl-72b-instruct", messages=messages)
print(chat_completion.choices[0].message.content)

json_string = chat_completion.choices[0].message.content.removeprefix("```json").removesuffix("```")
data = json.loads(json_string)

img = PIL.Image.open("page_0.jpg")

for bbox in data:
  PIL.ImageDraw.Draw(img).rectangle(bbox["bbox_2d"], outline='red')

img.save("page_0_bbox.jpg")
display(Image("page_0_bbox.jpg", width=500))
````

````
```json
[
	{"bbox_2d": [396, 1152, 1314, 1607], "text_content": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English- to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data."}
]
```
````

![jpeg](https://3807676826-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FLSXNQZeD4w30hUaiugTx%2Fuploads%2Fgit-blob-676c602af320bc00107effa9f2f3ca02ce888ffa%2Fmulti_modal_10_1.jpg?alt=media)

### More resources

* <https://github.com/QwenLM/Qwen2.5-VL/tree/main/cookbooks>
* <https://ai.google.dev/gemma/docs/capabilities/vision/prompt-with-visual-data>
* <https://github.com/bytedance/UI-TARS>
* <https://docs.mistral.ai/capabilities/vision/>

## Next steps

* [Chat Completions API reference](/parasail-docs/api-reference/chat-completions.md)
* [Serverless overview](/parasail-docs/products/overview.md)
