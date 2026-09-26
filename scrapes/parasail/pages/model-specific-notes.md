> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/products/overview/model-specific-notes.md).

# Model-specific Notes

Model-specific Serverless parameters for DeepSeek V3.1, Qwen3.5, and GPT-OSS models on Parasail.

Most Serverless models work with the standard [Chat Completions API](/parasail-docs/api-reference/chat-completions.md) and [sampling parameters](/parasail-docs/api-reference/parameters.md). Some models expose extra controls through `extra_body`, `custom_params`, or `chat_template_kwargs`.

## DeepSeek V3.1 thinking mode

Use `chat_template_kwargs.thinking` to turn thinking mode on or off. Pass a JSON boolean, not a string.

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)

chat_completion = client.chat.completions.create(
    model="parasail-deepseek-31",
    messages=[{"role": "user", "content": "What is the capital of New York?"}],
    extra_body={"chat_template_kwargs": {"thinking": True}},
)

print(chat_completion.choices[0].message.content)
```

```bash
curl -X POST https://api.parasail.io/v1/chat/completions \
  -H "Authorization: Bearer $PARASAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "parasail-deepseek-31",
    "chat_template_kwargs": {"thinking": false},
    "messages": [{"role": "user", "content": "What is the capital of New York?"}]
  }'
```

## Qwen3.5 thinking mode

Use `chat_template_kwargs.enable_thinking` to turn Qwen3.5 thinking mode on or off. Qwen-specific sampling settings such as `top_k` belong in `extra_body`.

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)

chat_response = client.chat.completions.create(
    model="Qwen/Qwen3.5-35B-A3B",
    messages=[{"role": "user", "content": "What is the capital of New York?"}],
    max_tokens=32768,
    temperature=0.7,
    top_p=0.8,
    presence_penalty=1.5,
    extra_body={
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},
    },
)

print(chat_response.choices[0].message.content)
```

## GPT-OSS reasoning control

GPT-OSS models support explicit reasoning controls that trade depth for latency and cost.

| Parameter          | Type                       | Description                                                  |
| ------------------ | -------------------------- | ------------------------------------------------------------ |
| `thinking_budget`  | integer                    | Upper bound on internal reasoning tokens.                    |
| `reasoning_effort` | `low`, `medium`, or `high` | Qualitative control over how deliberately the model reasons. |

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)

resp = client.chat.completions.create(
    model="parasail-gpt-oss-20b-fast",
    messages=[{"role": "user", "content": "Explain why the sky is blue."}],
    extra_body={
        "custom_params": {"thinking_budget": 40},
        "chat_template_kwargs": {"reasoning_effort": "high"},
    },
)

print(resp.choices[0].message.content)
```

```bash
curl https://api.parasail.io/v1/chat/completions \
  -H "Authorization: Bearer $PARASAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "parasail-gpt-oss-20b-fast",
    "messages": [{"role": "user", "content": "Explain why the sky is blue."}],
    "custom_params": {"thinking_budget": 40},
    "chat_template_kwargs": {"reasoning_effort": "high"}
  }'
```

### Practical defaults

| Goal                | `thinking_budget` | `reasoning_effort` |
| ------------------- | ----------------- | ------------------ |
| Fast and lower cost | `10`              | `low`              |
| Balanced default    | `25`              | `medium`           |
| Deeper reasoning    | `40` or higher    | `high`             |

## Structured outputs with GPT-OSS

Use `response_format.type = "json_schema"` with GPT-OSS models when the response must be valid JSON that matches a schema. You can combine structured output with GPT-OSS reasoning controls in the same request: put `response_format` at the top level, and put `thinking_budget` and `reasoning_effort` in `extra_body`.

```python
import json
import os

from openai import OpenAI

MODEL = "parasail-gpt-oss-20b-fast"

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key=os.environ["PARASAIL_API_KEY"],
)

product_review_schema = {
    "type": "object",
    "properties": {
        "rating": {"type": "integer", "minimum": 1, "maximum": 5},
        "pros": {"type": "array", "items": {"type": "string"}},
        "cons": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
    "required": ["rating", "pros", "cons", "summary"],
    "additionalProperties": False,
}

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "Write a short review of a flagship smartphone.",
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "product_review",
            "strict": True,
            "schema": product_review_schema,
        },
    },
    extra_body={
        "custom_params": {"thinking_budget": 50},
        "chat_template_kwargs": {"reasoning_effort": "medium"},
    },
)

data = json.loads(resp.choices[0].message.content)
print(data)
```

Parsing and strictness notes:

* Use `strict: True` with `additionalProperties: False` to keep the response limited to the schema.
* Parse `resp.choices[0].message.content` with `json.loads()` and use the parsed object as the source of truth.
* For streaming responses, concatenate the JSON text from `delta.content` chunks and parse it after the stream ends.

For full schema guidance, see [Structured Output](/parasail-docs/guides/structured-output.md).

## Next steps

* [Serverless overview](/parasail-docs/products/overview.md)
* [Chat Completions API](/parasail-docs/api-reference/chat-completions.md)
* [Parameters reference](/parasail-docs/api-reference/parameters.md)
* [Structured Output](/parasail-docs/guides/structured-output.md)
