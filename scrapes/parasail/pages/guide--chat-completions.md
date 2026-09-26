> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/guides/chat-completions.md).

# Chat Completions

Send chat messages to instruct-tuned models with Parasail's OpenAI-compatible Chat Completions API.

A Chat Completion is the typical method to interact with an *instruct-tuned* large language model. The user sends chat messages to the model, and the model responds with a message of its own. The chat may continue: user may append another message to the list and the model responds with the full context of the entire chat.

Let's start with an example.

## Example Chat Completion

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of New York?"},
]

chat_completion = client.chat.completions.create(
    model="parasail-llama-33-70b-fp8",
    messages=messages,
    max_completion_tokens=1024,
)

response_message = chat_completion.choices[0].message
print(
    {
        "role": response_message.role,
        "content": response_message.content,
    }
)
```

Response message:

```python
{'role': 'assistant', 'content': 'The capital of New York is Albany.'}
```

## Messages

At its core, chat completions are based on messages. Each message has a role and content. The role defines who wrote the message: the *user*, the *assistant* (that is, the model), or the *system* prompt. The *content* is the user text or model output.

Roles are defined by the model. The ones show here are typical, such as used by the LLama 3 family. Some models have the same concepts under a different name. Check the model card or the model's chat template of you're having issues.

## Models: Base vs Instruct

Not all models are intended to work with chat completions. The notable distinction is *Base* vs *Instruct-tuned* models. Base models contain the raw knowledge of the model, but are not tuned to respond in a chat fashion. Instead the base model is additionally tuned to respond to chats. We call that the *Instruct* variant. Usually this is clear in the model name, such as `meta-llama/Llama-3.3-70B`vs `meta-llama/Llama-3.3-70B-Instruct`. Note the `Instruct` in the name, though some models use `chat`.

On the technical level, an instruct model will include a *chat template*, while a base model does not.

## What is a Chat Template?

LLMs fundamentally work on a token stream. The user provides input tokens (here in the form of text), and the model generates output tokens (here also presented as text). This is a basic *completion*. Notice this does not mention messages.

The way a model converts the input messages into the raw input tokens needed by the model is by applying a *chat template*. Models typically use the popular Jinja2 template system, and the chat template is simply a Jinja2 template that converts the messages to a string of text.

The chat template is model-specific. It must match the format of the training data used to train the model. The user is able to make some tweaks, but one cannot assume that the template used for one model will work with another.

The simplest example is one that simply concatenates the messages together:

```django
{% for message in messages %}{{ message.content }}{% endfor %}
```

However real chat templates tend to include special handling for `"role": "system"` messages, and they include special tags or tokens to identify message starts and stops. These tags or tokens will match the format of the training data used by the model author.

To explore further, the chat template is usually part of the model's tokenizer definition, often in the file `tokenizer_config.json`.

## Next steps

* [Structured output guide](/parasail-docs/guides/structured-output.md)
* [Tool and function calling guide](/parasail-docs/guides/tool-function-calling.md)
* [Chat Completions API reference](/parasail-docs/api-reference/chat-completions.md)
* [Chat and text generation use case](/parasail-docs/use-cases/chat-text-generation.md)
* [Model selection](/parasail-docs/guides/model-recommendations.md)
