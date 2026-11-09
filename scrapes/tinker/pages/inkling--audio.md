# Audio

Inkling and Inkling-Small natively support audio input, which you can combine with other modalities such as text and tool calls in the same conversation. Common uses include:

- **Speech transcription (ASR)** — “Transcribe this speech exactly.”
- **Audio question answering** — “What topic are the speakers discussing?”
- **Speaking-style classification** — “Is the speaker whispering, laughing, or speaking normally?”
- **Information extraction** — “List the names and dates mentioned in this recording.”

The [Cookbook audio recipes](https://github.com/thinking-machines-lab/tinker-cookbook/tree/main/tinker_cookbook/recipes/audio) demonstrate complete ASR and speaking-style workflows, including sampling, supervised fine-tuning, reinforcement learning, and evaluation.

Use either a native `AudioPointer` or an OpenAI-compatible `input_audio` part. `tml-renderers` decodes and DMel-encodes the audio on your client before the model request.

## Native chat messages

Use `AudioPointer` to refer to a local file:

```python
from tml_renderers import chat

user = chat.Author(chat.AuthorKind.User)
audio = chat.AudioPointer(
    location="speech.wav",
    format=chat.AudioFormat.Wav,
    num_frames=48_000,
    sample_rate=16_000,
)
messages = [
    chat.Message(content=chat.Text("Transcribe this."), author=user),
    chat.Message(content=audio, author=user),
]
```

`num_frames` is the number of source audio frames—not the number of DMel tokens. `sample_rate` describes the source file.

## OpenAI-compatible Cookbook messages

For OpenAI-compatible messages, put base64-encoded audio in an `input_audio` content part:

```python
audio_base64 = "..."  # Base64-encoded WAV bytes
audio_part = {
    "type": "input_audio",
    "input_audio": {"data": audio_base64, "format": "wav"},
}
text_part = {"type": "text", "text": "Transcribe this."}
messages = [{"role": "user", "content": [text_part, audio_part]}]
```

For WAV input, `tml-renderers` reads the frame count and sample rate from the WAV header. MP3 and FLAC inputs must include `num_frames` and `sample_rate`:

```python
{
    "type": "input_audio",
    "input_audio": {
        "data": audio_base64,
        "format": "mp3",
        "num_frames": 48_000,
        "sample_rate": 24_000,
    },
}
```

The Cookbook Inkling renderer accepts these dictionaries directly.

## Accepted audio input

- **Formats:** WAV, MP3, and FLAC.
- **Locations:** Local file paths for native `AudioPointer`; base64 audio for OpenAI-compatible `input_audio`.
- **WAV metadata:** Frame count and sample rate can be read from a valid WAV header.
- **MP3 and FLAC metadata:** Provide `num_frames` and `sample_rate`.
- **Remote media:** HTTP and cloud-storage URLs are not fetched. Download the file in your application first.

The encoding is eager and client-side. By the time `build_generation_prompt(...)` returns, the audio is ready to send to Inkling.

## Client-side audio encoding

`AudioPointer` holds the source location and metadata. When you build the generation prompt, `tml-renderers`:

1. Reads the local or inline audio.
1. Decodes and resamples it.
1. Encodes it as quantized mel features (DMels).
1. Places those features into the model-ready prompt.

You do not need to compute DMels yourself. Your application supplies audio bytes plus the correct format and metadata.

> **Preparing speech input**
>
> Mono 16 kHz WAV is a simple interchange format for speech datasets. Other accepted source rates are decoded and resampled by the client encoder.

## Run the example

[`sample_audio.py`](https://github.com/thinking-machines-lab/tinker-cookbook/blob/main/tinker_cookbook/scripts/inkling/sample_audio.py) demonstrates the complete sampling flow:

```bash
uv run python -m tinker_cookbook.scripts.inkling.sample_audio
uv run python -m tinker_cookbook.scripts.inkling.sample_audio message_format=chat
```

Pass `audio_path=/path/to/audio.wav` to use your own file.

## Learn more

- **[Cookbook audio recipes](https://github.com/thinking-machines-lab/tinker-cookbook/tree/main/tinker_cookbook/recipes/audio)** — SFT, RL, and evaluation workflows.
- **[`DmelChunk` API](https://tinker-docs.thinkingmachines.ai/tinker/api-reference/types/dmelchunk/index.md)** — Optional low-level reference for client-encoded audio input.
- **[tml-renderers](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/tml-renderers/index.md)** — The common rendering and sampling flow.
- **[Rendering tutorial](https://tinker-docs.thinkingmachines.ai/tutorials/core-concepts/rendering/index.md)** — How Cookbook renderers produce model inputs.
