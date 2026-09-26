> For the complete documentation index, see [llms.txt](https://docs.parasail.io/parasail-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parasail.io/parasail-docs/guides/structured-output.md).

# Structured Output

Get reliable, schema-conformant JSON from Parasail models using guided\_json and response\_format.

## Overview

Parasail's OpenAI-compatible endpoint can return structured, machine-parseable output so you don't have to scrape JSON out of free-form text. There are two distinct ways to do this:

* **Prompt-only JSON**—you *ask* the model for JSON in the prompt. Simple, but the model can still drift (extra prose, missing keys, invalid JSON).
* **Server-enforced schemas**—you pass a schema with the request and the server constrains decoding so the output is guaranteed to match. On Parasail this is done with `guided_json` or `response_format` (JSON Schema).

Use server-enforced schemas whenever you need to parse the result programmatically.

## Prompt-only JSON vs. server-enforced schemas

| Approach                        | How                                                 | Guarantee                           |
| ------------------------------- | --------------------------------------------------- | ----------------------------------- |
| Prompt-only JSON                | Describe the desired JSON in the prompt             | None—best-effort                    |
| `guided_json`                   | Pass a JSON Schema in `extra_body`                  | Output is constrained to the schema |
| `response_format` (JSON Schema) | Pass `response_format={"type": "json_schema", ...}` | Output is constrained to the schema |

Both server-enforced approaches use the same Parasail base URL:

```
https://api.parasail.io/v1
```

## Supported models

The following models support guided/structured decoding as of June 2026. Capabilities change over time—use the [models endpoint](/parasail-docs/api-reference/models-endpoint.md) to check model availability, then validate structured-output support with a small test request.

Treat this table as a starting point for testing. Before relying on a constraint in production, send a small request with the same model and constraint type you plan to use.

| Model                                  | Guided JSON / JSON Schema | Regex | Choice |
| -------------------------------------- | ------------------------- | ----- | ------ |
| parasail-llama-33-70b-fp8              | Y                         | Y     | Y      |
| parasail-llama-4-scout-instruct        | Y                         | Y     | Y      |
| parasail-llama-4-maverick-instruct-fp8 | Y                         | Y     | Y      |
| parasail-qwen3-30b-a3b                 | Y                         |       | Y      |
| parasail-qwen3-235b-a22b               | Y                         |       | Y      |
| parasail-qwen3-32b                     | Y                         |       | Y      |
| parasail-gemma3-27b-it                 | Y                         | Y     | Y      |
| parasail-mistral-devstral-small        | Y                         | Y     | Y      |

## Server-enforced JSON with `guided_json`

Pass a JSON Schema via the OpenAI SDK's `extra_body` parameter. The server uses guided decoding to ensure the response matches your schema.

```python
import json
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>",
)

schema = {
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "date": {"type": "string", "format": "date"},
    },
    "required": ["location", "date"],
    "additionalProperties": False,
}

completion = client.chat.completions.create(
    model="parasail-qwen3-32b",
    messages=[
        {"role": "user", "content": "What's the weather like in Manhattan Beach on 2025-06-03?"}
    ],
    extra_body={"guided_json": schema},
)

# The content is already constrained to match the schema
data = json.loads(completion.choices[0].message.content)
print(json.dumps(data, indent=2))
```

Expected output:

```json
{
  "location": "Manhattan Beach",
  "date": "2025-06-03"
}
```

## Server-enforced JSON with `response_format`

Parasail also accepts the OpenAI `response_format` field with `type: "json_schema"`—the same shape OpenAI uses. Combine `strict: true` with `additionalProperties: false` for the tightest output.

```python
import json
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>",
)

schema = {
    "type": "object",
    "properties": {
        "capital": {"type": "string"},
        "country": {"type": "string"},
    },
    "required": ["capital", "country"],
    "additionalProperties": False,
}

resp = client.chat.completions.create(
    model="parasail-qwen3-32b",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "capital_lookup", "strict": True, "schema": schema},
    },
)

data = json.loads(resp.choices[0].message.content)
print(json.dumps(data, indent=2))
```

Expected output:

```json
{
  "capital": "Paris",
  "country": "France"
}
```

## Prompt-only JSON

If you don't need a hard guarantee, you can simply ask the model for JSON. This works with any model but is best-effort—always validate and `json.loads()` the result before relying on it.

```python
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.parasail.io/v1",
    api_key="<PARASAIL_API_KEY>",
)

resp = client.chat.completions.create(
    model="parasail-qwen3-32b",
    messages=[
        {
            "role": "user",
            "content": (
                "Return ONLY a JSON object with keys 'location' and 'date' "
                "for the weather in Manhattan Beach on 2025-06-03. No prose."
            ),
        }
    ],
)

print(resp.choices[0].message.content)
```

## Other guided decoding constraints (regex and choice)

For models listed with regex or choice support in the table above, guided decoding can also constrain output to a regular expression or a fixed set of choices via `extra_body`:

```python
# Constrain to an ISO date
extra_body = {"guided_regex": r"\d{4}-\d{2}-\d{2}"}

# Constrain to one of a fixed set of values
extra_body = {"guided_choice": ["red", "green", "blue"]}
```

## cURL example

```bash
curl https://api.parasail.io/v1/chat/completions \
  -H "Authorization: Bearer $PARASAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "parasail-qwen3-32b",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
        "guided_json": {
          "type": "object",
          "properties": {
            "capital": {"type": "string"},
            "country": {"type": "string"}
          },
          "required": ["capital", "country"],
          "additionalProperties": false
        }
      }'
```

## Troubleshooting

| Symptom                              | Likely cause                   | Fix                                                                                           |
| ------------------------------------ | ------------------------------ | --------------------------------------------------------------------------------------------- |
| Model ignores the constraint         | Using prompt-only JSON         | Switch to `guided_json` or `response_format` for server-enforced schemas.                     |
| Valid JSON but unexpected extra keys | `additionalProperties` not set | Add `"additionalProperties": false` to your schema.                                           |
| Need to stream large JSON            | Output too large for one chunk | Set `stream=True`; constraints still apply. Concatenate `delta.content` and parse at the end. |

## Next steps

* [Chat completions guide](/parasail-docs/guides/chat-completions.md)
* [Tool/function calling guide](/parasail-docs/guides/tool-function-calling.md)
* [Chat Completions API reference](/parasail-docs/api-reference/chat-completions.md)
* [Models endpoint](/parasail-docs/api-reference/models-endpoint.md)
