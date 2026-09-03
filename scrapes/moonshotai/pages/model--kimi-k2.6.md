> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Kimi K2.6

> Explore Kimi K2.6 text, image, and video understanding, thinking mode, tool calling, and its 256K-token context window.

## Overview of Kimi K2.6 Model

Kimi K2.6 is Kimi's general-purpose model, possessing stronger and more stable long-term code writing capabilities, significantly improved instruction compliance and self-correction capabilities, and the ability to handle more complex software engineering tasks. It also significantly enhances the autonomous execution capabilities of the Agent. It supports text, image, and video input, thinking and non-thinking modes, and dialogue and Agent tasks. [Tech Blog](https://www.kimi.com/blog/kimi-k2-6)

<img src="https://mintcdn.com/moonshotai/QKwipWA7W5wxQ2Oa/assets/pics/k26.png?fit=max&auto=format&n=QKwipWA7W5wxQ2Oa&q=85&s=f17a118a63d40478a0336ff296a3e0fb" alt="kimi-k2.6" width="1920" height="1080" data-path="assets/pics/k26.png" />

### Long-horizon coding capability breakthrough

* K2.6 has achieved a breakthrough in long-horizon coding tasks, demonstrating more reliable generalization across diverse programming languages (such as Rust, Go, and Python) and task scenarios (including frontend development, DevOps, and performance optimization).

### Ultra-Long Context Support

* `kimi-k2.7-code` and `kimi-k2.6` models both provide a 256K context window.

### Long-Thinking Capabilities

* Kimi K2.6 still has strong reasoning capabilities, supporting multi-step tool invocation and reasoning, excelling at solving complex problems, such as complex logical reasoning, mathematical problems, and code writing.

## Example Usage

Here is a complete usage example to help you quickly get started with the Kimi K2.6 model.

### Install the OpenAI SDK

Kimi API is fully compatible with OpenAI's API format. You can install the OpenAI SDK as follows:

```bash theme={null}
pip install --upgrade 'openai>=1.0'
```

### Verify the Installation

```bash theme={null}
python -c 'import openai; print("version =",openai.__version__)'

# The output may be version = 1.10.0, indicating the OpenAI SDK was installed successfully and your Python environment is using OpenAI SDK v1.10.0.
```

## Quick Start

* [Try it now](https://platform.kimi.ai/playground): Test model performance in your business scenarios through interactive operations in the Dev Workbench
* [Apply for API Key](https://platform.kimi.ai/console/api-keys): Test via API call immediately

### Image Understanding Code Example

```python theme={null}
import os
import base64

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1",
)

# Replace kimi.png with the path to the image you want Kimi to analyze
image_path = "kimi.png"

with open(image_path, "rb") as f:
    image_data = f.read()

# Use the standard library base64.b64encode function to encode the image into base64 format
image_url = f"data:image/{os.path.splitext(image_path)[1].lstrip('.')};base64,{base64.b64encode(image_data).decode('utf-8')}"


completion = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[
        {"role": "system", "content": "You are Kimi."},
        {
            "role": "user",
            # Note: content is changed from str type to a list containing multiple content parts.
            # Image (image_url) is one part, and text is another part.
            "content": [
                {
                    "type": "image_url",  # <-- Use image_url type to upload images, with content as base64-encoded image data
                    "image_url": {
                        "url": image_url,
                    },
                },
                {
                    "type": "text",
                    "text": "Please describe the content of the image.",  # <-- Use text type to provide text instructions
                },
            ],
        },
    ],
)

print(completion.choices[0].message.content)
```

If your code runs successfully with no errors, you will see output similar to the following:

```text theme={null}
[Image description output]
```

### Video Understanding Code Example

```python theme={null}
import os
import base64

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1",
)

# Replace kimi.mp4 with the path to the video you want Kimi to analyze
video_path = "kimi.mp4"

with open(video_path, "rb") as f:
    video_data = f.read()

# Use the standard library base64.b64encode function to encode the video into base64 format
video_url = f"data:video/{os.path.splitext(video_path)[1].lstrip('.')};base64,{base64.b64encode(video_data).decode('utf-8')}"


completion = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[
        {"role": "system", "content": "You are Kimi."},
        {
            "role": "user",
            # Note: content is changed from str type to a list containing multiple content parts.
            # Video (video_url) is one part, and text is another part.
            "content": [
                {
                    "type": "video_url",  # <-- Use video_url type to upload videos, with content as base64-encoded video data
                    "video_url": {
                        "url": video_url,
                    },
                },
                {
                    "type": "text",
                    "text": "Please describe the content of the video.",  # <-- Use text type to provide text instructions
                },
            ],
        },
    ],
)

print(completion.choices[0].message.content)
```

### Multimodal Tool Capability Example

Kimi K2.6 model combines multiple capabilities. The following example demonstrates K2.6's visual understanding + tool calling capabilities.

First, download this sample video to your local machine, such as `~/Download/test_video.mp4`

<Frame>
  <video controls style={{ width: '100%', height: 'auto' }}>
    <source src="https://mintcdn.com/moonshotai/AP772Is8kVTEjpLL/assets/pics/test_video.mp4?fit=max&auto=format&n=AP772Is8kVTEjpLL&q=85&s=b316516bf71c00a59a1be4d0e9d9b9e0" type="video/mp4" data-path="assets/pics/test_video.mp4" />
  </video>
</Frame>

Then run the following code:

```python theme={null}
import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path
from openai import OpenAI

tools = [{
    "type": "function",
    "function": {
        "name": "watch_video_clip",
        "description": "Watch a video file or a sub-clip of it. If start_time and end_time are not provided, the entire video will be returned.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string", 
                    "description": "The path to the video file to watch"
                },
                "start_time": {
                    "type": "number",
                    "description": "The start time of the clip in seconds (optional, defaults to 0)"
                },
                "end_time": {
                    "type": "number",
                    "description": "The end time of the clip in seconds (optional, defaults to end of video)"
                }
            },
            "required": ["path"]
        }
    }
}]

def watch_video_clip(path: str, start_time: float | None = None, end_time: float | None = None) -> list[dict]:
    """
    Watch a video file or a sub-clip of it.

    Args:
        path: The path to the video file to watch
        start_time: The start time in seconds (optional, defaults to 0)
        end_time: The end time in seconds (optional, defaults to end of video)

    Returns:
        A list of content blocks in MultiModal Tool API format
    """

    video_path = Path(path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {path}")

    # Get video duration if needed
    if start_time is None and end_time is None:
        # Return entire video
        with open(path, "rb") as f:
            video_base64 = base64.b64encode(f.read()).decode("utf-8")
        return [
            {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{video_base64}"}},
            {"type": "text", "text": f"Full video: {video_path.name}"}
        ]

    # Get video duration for defaults
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True
    )
    duration = float(json.loads(probe.stdout)["format"]["duration"])

    start_time = start_time or 0
    end_time = end_time or duration
    clip_duration = end_time - start_time

    # Extract clip
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(start_time), "-i", path,
            "-t", str(clip_duration), "-c:v", "libx264", "-c:a", "aac",
            "-preset", "fast", "-crf", "23", "-movflags", "+faststart",
            "-loglevel", "error", tmp_path
        ], check=True)

        with open(tmp_path, "rb") as f:
            video_base64 = base64.b64encode(f.read()).decode("utf-8")

        return [
            {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{video_base64}"}},
            {"type": "text", "text": f"Clip from {video_path.name}: {start_time}s - {end_time}s"}
        ]
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1"
)

def agent_loop(user_message: str):
    """Simple agent loop with multimodal tool support."""

    messages = [
        {"role": "system", "content": "You are a video analysis assistant. Use watch_video_clip to examine specific portions of videos."},
        {"role": "user", "content": user_message}
    ]

    while True:
        response = client.chat.completions.create(
            model="kimi-k2.6",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        message = response.choices[0].message
        messages.append(message.model_dump())

        # No tool calls = done
        if not message.tool_calls:
            return message.content

        # Execute tool calls
        for tool_call in message.tool_calls:
            if tool_call.function.name == "watch_video_clip":
                args = json.loads(tool_call.function.arguments)
                result = watch_video_clip(
                    path=args["path"],
                    start_time=args.get("start_time"),
                    end_time=args.get("end_time")
                )
                # Multimodal tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

# Usage
answer = agent_loop("Analyze what happens between seconds 8-13 in ~/Download/test_video.mp4")
print(answer)
```

## Best Practices

### Supported Formats

Images are supported in formats: png, jpeg, webp, gif.\
Videos are supported in formats: mp4, mpeg, mov, avi, x-flv, mpg, webm, wmv, 3gpp.

### Token Calculation and Billing

Image and video token usage is dynamically calculated. You can use the [token estimation API](/docs/api/estimate) to check the expected token consumption for a request containing images or video before processing.

Generally, the higher the resolution of an image, the more tokens it will consume. For videos, the number of tokens depends on the number of keyframes and their resolution—the more keyframes and the higher their resolution, the greater the token consumption.

The Vision model is billed based on the total number of tokens processed. For more information, see:

For token pricing details, refer to [Model Pricing](/docs/pricing/chat-k26).

### Recommended Resolution

We recommend that image resolution should not exceed 4k (4096×2160), and video resolution should not exceed FHD (1920×1080). Higher resolutions will only increase processing time and will not improve the model’s understanding.

### Upload File or Base64?

Due to the limitation on the overall size of the request body, for very large videos you **must** use the file upload method to utilize vision capabilities.For images or videos that will be referenced multiple times, it is recommended to use the file upload method. Regarding file upload limitations, please refer to the [File Upload documentation](/docs/api/files-upload).

Image quantity limit: The Vision model has no limit on the number of images, but ensure that the request body size does not exceed 100M

URL-formatted images: Not supported, currently only supports base64-encoded image content

## Parameters Differences in Request Body

Parameters are listed in [chat](/docs/api/chat). However, behaviour of some parameters may be different in k2.6 models.

**We recommend using the default values instead of manually configuring these parameters.**

Differences are listed below.

| Field              | Required | Description                                                                  | Type   | Values                                                                                                                       |
| ------------------ | -------- | ---------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------- |
| max\_tokens        | optional | The maximum number of tokens to generate for the chat completion.            | int    | Default to be 32k aka 32768                                                                                                  |
| thinking           | optional | **New!** This parameter controls if the thinking is enabled for this request | object | Default to be `{"type": "enabled"}`. Value can only be one of `{"type": "enabled"}` or `{"type": "disabled"}`                |
| temperature        | optional | The sampling temperature to use                                              | float  | k2.6 model will use a fixed value 1.0, non-thinking mode will use a fixed value 0.6. Any other value will result in an error |
| top\_p             | optional | A sampling method                                                            | float  | k2.6 model will use a fixed value 0.95. Any other value will result in an error                                              |
| n                  | optional | The number of results to generate for each input message                     | int    | k2.6 model will use a fixed value 1. Any other value will result in an error                                                 |
| presence\_penalty  | optional | Penalizing new tokens based on whether they appear in the text               | float  | k2.6 model will use a fixed value 0.0. Any other value will result in an error                                               |
| frequency\_penalty | optional | Penalizing new tokens based on their existing frequency in the text          | float  | k2.6 model will use a fixed value 0.0. Any other value will result in an error                                               |

## Tool Use Compatibility

When using tools, if the thinking parameter is set to `{"type": "enabled"}`, please note the following constraints to ensure model performance:

* `tool_choice` can only be set to "auto" or "none" (default is "auto") to avoid conflicts between reasoning content and the specified tool\_choice. Any other value will result in an error;
* During multi-step tool calling, we recommend keeping the `reasoning_content` from the assistant message in the current turn's tool call within the context; omitting it does not cause an error, but may degrade reasoning continuity and tool-call quality;
* The official builtin `$web_search` tool is temporarily incompatible with Kimi K2.6 thinking mode, you can choose to disable thinking mode first and then use the `$web_search` tool.

You can refer to [Use Thinking Mode](/docs/guide/use-thinking-models) for correct usage of tool calling.

### Disable Thinking Capability Example

For the `kimi-k2.6` model, you can disable thinking by specifying `"thinking": {"type": "disabled"}` in the request body:

<Tabs>
  <Tab title="curl">
    ```bash theme={null}
    $ curl https://api.moonshot.ai/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $MOONSHOT_API_KEY" \
        -d '{
            "model": "kimi-k2.6",
            "messages": [
                {"role": "user", "content": "hello"}
            ],
            "thinking": {"type": "disabled"}
       }'
    ```
  </Tab>

  <Tab title="python">
    ```python theme={null}
    import os
    import openai

    client = openai.Client(
        base_url="https://api.moonshot.ai/v1",
        api_key=os.getenv("MOONSHOT_API_KEY"),
    )

    response = client.chat.completions.create(
        model="kimi-k2.6",
        messages=[
            {"role": "user", "content": "hello"}
        ],
        extra_body={
            "thinking": {"type": "disabled"}
        },  # Pass additional request body via extra_body parameter to disable thinking
        max_tokens=1024*32
        # No need to set temperature
    )

    print(response.choices[0].message.content)
    print(response)
    ```
  </Tab>
</Tabs>

## Model Pricing

For token pricing details, refer to [Model Pricing](/docs/pricing/chat-k26).

## Learn More

* For the benchmark testing with Kimi K2.6, please refer to this [benchmark best practice](/docs/guide/benchmark-best-practice)
* For the most detailed API usage example of Kimi K2.6, see: [Vision Input](/docs/guide/use-kimi-vision-model)
* See how to use Kimi K2 in [Claude Code](/docs/guide/claude-code-kimi)
* Learn how to configure and use the [Thinking Mode](/docs/guide/use-thinking-models)

<Warning>
  The web search (`web_search`) is currently being updated. We do not recommend using this functionality in the near term. This documentation is outdated; please follow subsequent content updates.
</Warning>

* Web search is a powerful official tool provided by the Kimi API. See how to use [Web Search](/docs/guide/use-web-search) and other [official tools](/docs/guide/use-official-tools).
* For all model pricing see [here](/docs/pricing/chat), [Billing & Rate Limit details](/docs/pricing/limits), and [Web Search Pricing](/docs/pricing/tools)
