# `tml-renderers`

[`tml-renderers`](https://pypi.org/project/tml-renderers/) is Thinking Machines Lab's high-performance rendering package to ensure reliable sampling and post-training. It converts chat messages, tool calls, images, and audio into the token and media representation Inkling expects. It accepts native, typed `tml_renderers.chat` objects as well as the OpenAI-compatible message dictionaries used by Cookbook datasets.

> **Installation**
>
> Install a compatible release of the SDK, Cookbook, and [`tml-renderers`](https://pypi.org/project/tml-renderers/):
>
> ```bash
> pip install tinker tinker-cookbook tml-renderers
> ```
>
> `tml-renderers` is a standard Cookbook dependency, so `pip install tinker-cookbook` alone also pulls it in.
>
> Requirements:
>
> - **PyTorch >= 2.10**, installed before importing `tml_renderers` (libtorch is not bundled).
> - **Supported platforms:** x86_64 and ARM (aarch64) Linux and macOS.
> - **CPython 3.11+.**

## Native chat messages

Native messages make media pointers and TMLv0-specific content explicit:

```python
from tinker_cookbook import model_info
from tinker_cookbook.renderers import get_renderer
from tinker_cookbook.tokenizer_utils import get_tokenizer
from tml_renderers import chat

model_name = "thinkingmachines/Inkling-2-Small"
renderer = get_renderer(
    model_info.get_recommended_renderer_name(model_name),
    get_tokenizer(model_name),
)

message = chat.Message(
    content=chat.Text("What is 2 + 2?"),
    author=chat.Author(chat.AuthorKind.User),
)
prompt = renderer.build_generation_prompt([message])
```

Use native messages when you want typed `ImagePointer` or `AudioPointer` objects.

## OpenAI-compatible Cookbook messages

Use ordinary Cookbook messages when your dataset or application already follows the OpenAI-compatible role/content schema:

```python
messages = [
    {"role": "system", "content": "Answer concisely."},
    {"role": "user", "content": "What is 2 + 2?"},
]
prompt = renderer.build_generation_prompt(messages)
```

`build_generation_prompt(...)` returns the `tinker.ModelInput` you feed to Inkling.

To inspect or round-trip the message conversion directly:

```python
from tml_renderers import chat

tml_messages = chat.OpenAIMessage.from_openai_chat_dicts(messages)
openai_messages = chat.OpenAIMessage.to_openai_chat_dicts(tml_messages)
```

This is compatibility with the **message format used by the Cookbook**.

## Feed the input to Inkling

`renderer.build_generation_prompt(messages)` produces a model-ready prompt containing the text, media, and tool context from the conversation. Pass it to a sampling client:

```python
import tinker

client = await tinker.ServiceClient().create_sampling_client(
    base_model=model_name
)
response = await client.sample(
    prompt=prompt,
    num_samples=1,
    sampling_params=tinker.SamplingParams(
        max_tokens=128, stop=renderer.get_stop_sequences()
    ),
)
message, termination = renderer.parse_response(response.sequences[0].tokens)
```

The stop sequences and parser come from the same TMLv0 renderer, so structured output such as tool calls can be recovered as Cookbook messages. See [Thinking effort](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/thinking-effort/index.md) to control how much Inkling reasons.

## Tool calls

Declare tools with the standard Cookbook `ToolSpec`, then render the resulting prefix together with the user's message:

```python
from tinker_cookbook.renderers import Message, ToolSpec

tool = ToolSpec(
    name="get_weather",
    description="Get weather for a city.",
    parameters={"type": "object", "properties": {"city": {"type": "string"}}},
)
messages = renderer.create_conversation_prefix_with_tools(
    [tool], system_prompt="Use tools when needed."
)
messages.append(Message(role="user", content="What is the weather in Tokyo?"))
prompt = renderer.build_generation_prompt(messages)
```

After sampling, `renderer.parse_response(...)` returns a Cookbook assistant message. If Inkling invoked a tool, inspect its `tool_calls`, execute the function in your application, append a `role="tool"` result, and sample again.

Append tool results using the OpenAI-compatible Cookbook format:

```python
messages.append({
    "role": "tool",
    "tool_call_id": "call_weather_001",
    "name": "get_weather",
    "content": '{"temperature_c":28}',
})
```

## Training

The same renderer supports supervised examples. Use the same value you chose for generation; see [Thinking effort](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/thinking-effort/index.md).

```python
model_input, weights = renderer.build_supervised_example(
    [
        {"role": "user", "content": "What is 2 + 2?"},
        {"role": "assistant", "content": "4"},
    ],
    effort=0.9,
)
```

`build_generation_prompt(...)` uses `render_for_completion(...)`; supervised construction uses `render_for_sft(...)` and returns aligned model input and loss weights.

## `tml_renderers` API reference

The Cookbook renderer wraps the lower-level `tml_renderers` package. Use the Cookbook renderer for the common path; call `tml_renderers` directly when you want raw token spans, the streaming parser, or your own Tinker integration.

Create the renderer for your model. Each class selects the model's tokenizer:

```python
from tml_renderers import renderers

tml_renderer = renderers.Inkling2()  # thinkingmachines/Inkling-2-Small
# renderers.Inkling() for thinkingmachines/Inkling and thinkingmachines/Inkling-Small
```

### `renderers.Inkling2` and `renderers.Inkling`

All methods accept a `MessageList`, `list[Message]`, or `list[OpenAIMessage]`.

| Method                                                | Purpose                                                                                  |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `render_for_completion(messages)`                     | Render a generation prompt; returns `(spans, parser)`.                                   |
| `render_for_completion_with_effort(messages, effort)` | Same, with a thinking-effort system message (`effort` in `[0, 1)`).                      |
| `render_for_sft(messages)`                            | Render supervised examples with per-token loss weights; returns `list[TrainingExample]`. |
| `stop()`                                              | Stop token IDs for sampling.                                                             |

```python
spans, parser = tml_renderer.render_for_completion(messages)
training_examples = tml_renderer.render_for_sft(messages)
```

### Parser

`render_for_completion(...)` returns a parser for turning sampled tokens back into messages.

| Method                 | Purpose                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------- |
| `parse_tokens(tokens)` | Parse sampled token IDs; returns a `ParseResult` with `messages` and per-message `token_counts`.    |
| `parse(spans)`         | Parse rendered token spans; returns a `ParseResult`.                                                |
| `parse_stream()`       | Streaming: a context manager whose `feed(tokens)` and `finish()` return incremental `ParseUpdate`s. |

```python
messages = parser.parse_tokens(sampled_token_ids).messages

with parser.parse_stream() as stream:
    updates = stream.feed(sampled_token_ids) + stream.finish()
```

### SFT with native messages and `ModelEndSampling`

`ModelEndSampling` is the model's end-of-turn signal. The parser treats it as the stop and drops it from returned messages, so do **not** add it to a generation prompt.

If you are already working directly with native `tml_renderers.chat` types, those pass through the Cookbook renderer too, and `build_supervised_example` terminates model turns with `ModelEndSampling` automatically (adding it yourself is a no-op). When calling a `tml_renderers` renderer's `render_for_sft(...)` directly, you own the exact message sequence, so include `ModelEndSampling` after model turns:

```python
from tml_renderers import chat

tml_messages = [
    chat.Message(
        author=chat.Author(chat.AuthorKind.User),
        content=chat.Text("What is 2+2?"),
    ),
    chat.Message(
        author=chat.Author(chat.AuthorKind.Model),
        content=chat.Text("4."),
    ),
    chat.Message(
        author=chat.Author(chat.AuthorKind.Model),
        content=chat.ModelEndSampling(),
    ),
]

training_examples = tml_renderer.render_for_sft(tml_messages)
```

This is the intended boundary: datasets and environments produce ordinary chat-completion-shaped messages, and both the Cookbook renderer and `from_openai_chat_dicts(...)` add these end-of-turn boundaries automatically; only direct `render_for_sft(...)` callers add them explicitly.

### Message conversion

`chat.OpenAIMessage` bridges OpenAI-compatible dictionaries and native messages.

| Method                                         | Purpose                                          |
| ---------------------------------------------- | ------------------------------------------------ |
| `OpenAIMessage.from_openai_chat_dicts(dicts)`  | OpenAI-compatible dicts → `list[OpenAIMessage]`. |
| `OpenAIMessage.to_openai_chat_dicts(messages)` | `OpenAIMessage`s → OpenAI-compatible dicts.      |
| `OpenAIMessage.from_messages(parsed)`          | Native `Message`s → `list[OpenAIMessage]`.       |

### Tinker adapters

`tml_renderers.tinker` converts rendered output into Tinker SDK objects.

| Function                                                      | Purpose                                        |
| ------------------------------------------------------------- | ---------------------------------------------- |
| `token_spans_to_tinker_model_input(spans)`                    | Rendered spans → `tinker.ModelInput`.          |
| `training_example_to_tinker_model_input_and_weights(example)` | A `TrainingExample` → `(ModelInput, weights)`. |

```python
from tml_renderers.tinker import token_spans_to_tinker_model_input

model_input = token_spans_to_tinker_model_input(spans)
```

## Current constraints

- Inkling generates complete assistant messages; it does not continue from a partially written assistant message.
- `tml-renderers` renders whole conversations rather than individual messages.
- Native `tml_renderers.chat` inputs support training on all assistant messages. Selective Cookbook training modes require Cookbook/OpenAI-compatible dictionaries.

## Next steps

- **[Audio](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/audio/index.md)** — Add `AudioPointer` or `input_audio` content.
- **[Images](https://tinker-docs.thinkingmachines.ai/cookbook/inkling/images/index.md)** — Add `ImagePointer` or `image_url` content.
- **[Rendering tutorial](https://tinker-docs.thinkingmachines.ai/tutorials/core-concepts/rendering/index.md)** — Learn the general Cookbook rendering model.
