> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Configure Kimi Vision Models

> Build image and video inputs for Kimi multimodal models using base64, URLs, file uploads, and multi-image conversations.

The Kimi Vision Model (including `kimi-k3` / `kimi-k2.6` / `kimi-k2.7-code` / `kimi-k2.7-code-highspeed` and so on) can understand visual content, including text in the image, colors, and the shapes of objects. The `kimi-k3`, `kimi-k2.6`, `kimi-k2.7-code` and `kimi-k2.7-code-highspeed` models can also understand video content. When you need the model to recognize images or videos, build multimodal requests as described on this page.

## Upload images directly with base64

The following example encodes a local image as base64, passes it to Kimi as an `image_url` message part, and asks a question about the image:

```python theme={null}
import os
import base64

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1",
)

# Replace kimi.png with the path to the image you want Kimi to recognize
image_path = "kimi.png"

with open(image_path, "rb") as f:
    image_data = f.read()

# We use the built-in base64.b64encode function to encode the image into a base64 formatted image_url
image_url = f"data:image/{os.path.splitext(image_path)[1].lstrip('.')};base64,{base64.b64encode(image_data).decode('utf-8')}"


completion = client.chat.completions.create(
    model="kimi-k3",
    messages=[
        {"role": "system", "content": "You are Kimi."},
        {
            "role": "user",
            # Note here, the content has changed from the original str type to a list. This list contains multiple parts, with the image (image_url) being one part and the text (text) being another part.
            "content": [
                {
                    "type": "image_url", # <-- Use the image_url type to upload the image, the content is the base64 encoded image
                    "image_url": {
                        "url": image_url,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe the content of the image.", # <-- Use the text type to provide text instructions, such as "Describe the content of the image"
                },
            ],
        },
    ],
)

print(completion.choices[0].message.content)
```

When using a Vision model, `message.content` must be an `array[object]` (that is, a JSON array). **Do not** serialize the JSON array and put it into `message.content` as a `string`. This is a non-standard format and is not guaranteed to be processed as visual input; behavior may vary across models or versions. Always use the array format shown below.

The correct format — `content` is a JSON array of multiple parts:

```json theme={null}
{
    "model": "kimi-k3",
    "messages":
    [
        {
            "role": "system",
            "content": "You are Kimi, an AI assistant provided by Moonshot AI, who excels in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will reject any questions related to terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated into other languages."
        },
        {
            "role": "user",
            "content":
            [
                {
                    "type": "image_url",
                    "image_url":
                    {
                        "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABhCAYAAAApxKSdAAAACXBIWXMAACE4AAAhOAFFljFgAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAUUSURBVHgB7Z29bhtHFIWPHQN2J7lKqnhYpYvpIukCbJEAKQJEegLReYFIT0DrCSI9QEDqCSIDaQIEIOukiJwyza5SJWlId3FFz+HuGmuSSw6p+dlZ3g84luhdUeI9M3fmziyXgBCUe/DHYY0Wj/tgWmjV42zFcWe4MIBBPNJ6qqW0uvAbXFvQgKzQK62bQhkaCIPc10q1Zi3XH1o/IG9cwUm0RogrgDY1KmLgHYX9DvyiBvDYI77XmiD+oLlQHw7hIDoCMBOt1U9w0BsU9mOAtaUUFk3oQoIfzAQFCf5dNMEdTFCQ4NtQih1NSIGgf3ibxOJt5UrAB1gNK72vIdjiI61HWr+YnNxDXK0rJiULsV65GJeiIescLSTTeobKSutiCuojX8kU3MBx4I3WeNVBBRl4fWiCyoB8v2JAAkk9PmDwT8sH1TEghRjgC27scCx41wO43KAg+ILxTvhNaUACwTc04Z0B30LwzTzm5Rjw3sgseIG1wGMawMBPIOQcqvzrNIMHOg9Q5KK953O90/rFC+BhJRH8PQZ+fu7SjC7HAIV95yu99vjlxfvBJx8nwHd6IfNJAkccOjHg6OgIs9lsra6vr2GTNE03/k7q8HAhyJ/2gM9O65/4kT7/mwEcoZwYsPQiV3BwcABb9Ho9KKU2njccDjGdLlxx+InBBPBAAR86ydRPaIC9SASi3+8bnXd+fr78nw8NJ39uDJjXAVFPP7dp/VmWLR9g6w6Huo/IOTk5MTpvZesn/93AiP/dXCwd9SyILT9Jko3n1bZ+8s8rGPGvoVHbEXcPMM39V1dX9Qd/19PPNxta959D4HUGF0RrAFs/8/8mxuPxXLUwtfx2WX+cxdivZ3DFA0SKldZPuPTAKrikbOlMOX+9zFu/Q2iAQoSY5H7mfeb/tXCT8MdneU9wNNCuQUXZA0ynnrUznyqOcrspUY4BJunHqPU3gOgMsNr6G0B0BpgUXrG0fhKVAaaF1/HxMWIhKgNMcj9Tz82Nk6rVGdav/tJ5eraJ0Wi01XPq1r/xOS8uLkJc6XYnRTMNXdf62eIvLy+jyftVghnQ7Xahe8FW59fBTRYOzosDNI1hJdz0lBQkBflkMBjMU5iL13pXRb8fYAJrB/a2db0oFHthAOEUliaYFHE+aaUBdZsvvFhApyM0idYZwOCvW4JmIWdSzPmidQaYrAGZ7iX4oFUGnJ2dGdUCTRqMozeANQCLsE6nA10JG/0Mx4KmDMbBCjEWR2yxu8LAM98vXelmCA2ovVLCI8EMYODWbpbvCXtTBzQVMSAwYkBgxIDAtNKAXWdGIRADAiMpKDA0IIMQikx6QGDEgMCIAYGRMSAsMgaEhgbcQgjFa+kBYZnIGBCWWzEgLPNBOJ6Fk/aR8Y5ZCvktKwX/PJZ7xoVjfs+4chYU11tK2sE85qUBLyH4Zh5z6QHhGPOf6r2j+TEbcgdFP2RaHX5TrYQlDflj5RXE5Q1cG/lWnhYpReUGKdUewGnRmhvnCJbgmxey8sHiZ8iwF3AsUBBckKHI/SWLq6HsBc8huML4DiK80D6WnBqLzN68UFCmopheYJOVYgcU5FOVbAVfYUcUZGoaLPglCtITdg2+tZUFBTFh2+ArWEYh/7z0WIIQSiM43lt5AWAmWhLHylN4QmkNEXfAbGqEQKsHSfHLYwiSq8AnaAAKeaW3D8VbijwNW5nh3IN9FPI/jnpaPKZi2/SfFuJu4W3x9RqWL+N5C+7ruKpBAgLkAAAAAElFTkSuQmCC"
                    }
                },
                {
                    "type": "text",
                    "text": "Please describe this image."
                }
            ]
        }
    ]
}
```

The invalid format — the array is serialized into a string:

```json theme={null}
{
    "model": "kimi-k3",
    "messages":
    [
        {
            "role": "system",
            "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are proficient in Chinese and English conversations. You provide users with safe, helpful, and accurate responses. You will refuse to answer any questions involving terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated into other languages."
        },
        {
            "role": "user",
            "content": "[{\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABhCAYAAAApxKSdAAAACXBIWXMAACE4AAAhOAFFljFgAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAUUSURBVHgB7Z29bhtHFIWPHQN2J7lKqnhYpYvpIukCbJEAKQJEegLReYFIT0DrCSI9QEDqCSIDaQIEIOukiJwyza5SJWlId3FFz+HuGmuSSw6p+dlZ3g84luhdUeI9M3fmziyXgBCUe/DHYY0Wj/tgWmjV42zFcWe4MIBBPNJ6qqW0uvAbXFvQgKzQK62bQhkaCIPc10q1Zi3XH1o/IG9cwUm0RogrgDY1KmLgHYX9DvyiBvDYI77XmiD+oLlQHw7hIDoCMBOt1U9w0BsU9mOAtaUUFk3oQoIfzAQFCf5dNMEdTFCQ4NtQih1NSIGgf3ibxOJt5UrAB1gNK72vIdjiI61HWr+YnNxDXK0rJiULsV65GJeiIescLSTTeobKSutiCuojX8kU3MBx4I3WeNVBBRl4fWiCyoB8v2JAAkk9PmDwT8sH1TEghRjgC27scCx41wO43KAg+ILxTvhNaUACwTc04Z0B30LwzTzm5Rjw3sgseIG1wGMawMBPIOQcqvzrNIMHOg9Q5KK953O90/rFC+BhJRH8PQZ+fu7SjC7HAIV95yu99vjlxfvBJx8nwHd6IfNJAkccOjHg6OgIs9lsra6vr2GTNE03/k7q8HAhyJ/2gM9O65/4kT7/mwEcoZwYsPQiV3BwcABb9Ho9KKU2njccDjGdLlxx+InBBPBAAR86ydRPaIC9SASi3+8bnXd+fr78nw8NJ39uDJjXAVFPP7dp/VmWLR9g6w6Huo/IOTk5MTpvZesn/93AiP/dXCwd9SyILT9Jko3n1bZ+8s8rGPGvoVHbEXcPMM39V1dX9Qd/19PPNxta959D4HUGF0RrAFs/8/8mxuPxXLUwtfx2WX+cxdivZ3DFA0SKldZPuPTAKrikbOlMOX+9zFu/Q2iAQoSY5H7mfeb/tXCT8MdneU9wNNCuQUXZA0ynnrUznyqOcrspUY4BJunHqPU3gOgMsNr6G0B0BpgUXrG0fhKVAaaF1/HxMWIhKgNMcj9Tz82Nk6rVGdav/tJ5eraJ0Wi01XPq1r/xOS8uLkJc6XYnRTMNXdf62eIvLy+jyftVghnQ7Xahe8FW59fBTRYOzosDNI1hJdz0lBQkBflkMBjMU5iL13pXRb8fYAJrB/a2db0oFHthAOEUliaYFHE+aaUBdZsvvFhApyM0idYZwOCvW4JmIWdSzPmidQaYrAGZ7iX4oFUGnJ2dGdUCTRqMozeANQCLsE6nA10JG/0Mx4KmDMbBCjEWR2yxu8LAM98vXelmCA2ovVLCI8EMYODWbpbvCXtTBzQVMSAwYkBgxIDAtNKAXWdGIRADAiMpKDA0IIMQikx6QGDEgMCIAYGRMSAsMgaEhgbcQgjFa+kBYZnIGBCWWzEgLPNBOJ6Fk/aR8Y5ZCvktKwX/PJZ7xoVjfs+4chYU11tK2sE85qUBLyH4Zh5z6QHhGPOf6r2j+TEbcgdFP2RaHX5TrYQlDflj5RXE5Q1cG/lWnhYpReUGKdUewGnRmhvnCJbgmxey8sHiZ8iwF3AsUBBckKHI/SWLq6HsBc8huML4DiK80D6WnBqLzN68UFCmopheYJOVYgcU5FOVbAVfYUcUZGoaLPglCtITdg2+tZUFBTFh2+ArWEYh/7z0WIIQSiM43lt5AWAmWhLHylN4QmkNEXfAbGqEQKsHSfHLYwiSq8AnaAAKeaW3D8VbijwNW5nh3IN9FPI/jnpaPKZi2/SfFuJu4W3x9RqWL+N5C+7ruKpBAgLkAAAAAElFTkSuQmCC\"}}, {\"type\": \"text\", \"text\": \"Please describe this image\"}]"
        }
    ]
}
```

## Reference uploaded images or videos by file ID

Since video files are often larger, you can first upload images or videos to Moonshot and then reference them via file ID — see [Image Understanding Upload](/docs/api/files-upload) for the upload API. The following example uploads a video file and asks the model to describe it through a `video_url` using the `ms://` protocol:

```python theme={null}
import os
from pathlib import Path

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1",
)

# Here, you need to replace video.mp4 with the path to the image or video you want Kimi to recognize
video_path = "video.mp4"

file_object = client.files.create(file=Path(video_path), purpose="video")  # Upload video to Moonshot

completion = client.chat.completions.create(
    model="kimi-k3",
    messages=[
        {
            "role": "system",
            "content": "You are Kimi, an AI assistant provided by Moonshot AI, who excels in Chinese and English conversations. You provide users with safe, helpful, and accurate answers. You will refuse to answer any questions involving terrorism, racism, or explicit content. Moonshot AI is a proper noun and should not be translated into other languages."
        },
        {
            "role": "user",
            "content":
            [
                {
                    "type": "video_url",
                    "video_url":
                    {
                        "url": f"ms://{file_object.id}"  # Note this is ms:// instead of base64-encoded image
                    }
                },
                {
                    "type": "text",
                    "text": "Please describe this video"
                }
            ]
        }
    ]
)

print(completion.choices[0].message.content)
```

Note that in the above example, the format of `video_url.url` is `ms://<file-id>`, where ms is short for moonshot storage — Moonshot's internal protocol for referencing files.

## Supported image and video formats

### Images

Images support the following formats (MIME types):

* image/jpeg
* image/png
* image/gif
* image/webp
* image/bmp
* image/heic
* image/heif

Animated GIF and WebP images are also passed in via `image_url`, but the underlying system may decode them as videos, and token consumption is calculated as video accordingly.

### SVG

SVG is not supported as image input: uploading an SVG with `purpose="image"`, or passing one through `image_url` (including base64-encoded), will be rejected. To have the model interpret SVG content, include the SVG source (XML text) directly as text in `messages`.

### Videos

Videos support the following formats (MIME types):

* video/mp4
* video/mpeg
* video/mov
* video/avi
* video/x-flv
* video/mpg
* video/webm
* video/wmv
* video/3gpp

## Estimate token usage and costs

* Images and videos use dynamic token calculation: you can obtain the token consumption of a request containing images or videos through the [estimate tokens API](/docs/api/estimate) before starting the understanding process;
* Generally speaking, the higher the image resolution, the more tokens it consumes. Videos are composed of several key frames — the more key frames and the higher the resolution, the more tokens are consumed;
* The Vision model is billed based on the total tokens used for model inference. For token pricing, see [Model Inference Pricing](/docs/pricing/chat-k27-code).

## Keep image and video resolution within limits

We recommend that image resolution does not exceed 4k (4096×2160), and video resolution does not exceed FHD (1920×1080). Resolutions higher than recommended will only cost more time processing the input without improving model understanding performance.

## Choose between base64 and file upload

* Due to our overall request body size limitations, very large videos must be processed using the file upload method for visual understanding;
* For images or videos that need to be referenced multiple times, we recommend using the file upload method for visual understanding;
* Regarding file upload limitations, please refer to the [File Upload](/docs/api/files-upload) documentation.

## Feature support and limitations

The Vision model supports the following features:

* Multi-turn conversations
* Streaming output
* Tool invocation
* JSON Mode
* Partial Mode

The following features are not supported or only partially supported:

* URL-formatted images: Not supported, currently only supports base64-encoded image content and images/videos uploaded via file ID

Other limitations:

* Image quantity: The Vision model has no limit on the number of images, but ensure that the request body size does not exceed 100M.

Different models enforce different constraints on parameters such as `temperature`, `top_p`, and `n`; we recommend using the defaults instead of setting them manually. See [Model Parameter Differences](/docs/api/models-overview) for details.
