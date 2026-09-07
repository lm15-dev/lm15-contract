---
meta:
  title: Structured output
  description: Constrain model output to match a JSON schema using the response_format parameter.
  keywords: structured output, JSON schema, response_format, JSON mode, schema validation
cms:
  alias: /model-api/docs/structured-output
  target: aidmc
---

# Structured output

Ship features that need reliable JSON — extracted fields, labels, configs — without adding recovery logic. With Meta Model API you define the JSON Schema in `response_format`, and the model constrains decoding to match it exactly.

## Understand how it works {#how-it-works}

Set `response_format` to `type: "json_schema"` and provide your schema in the `json_schema` field. The model constrains token generation to produce only valid JSON matching your schema. This is not post-processing: decoding itself is constrained, so the output is guaranteed to conform.

> [!IMPORTANT] Recursive schemas aren't supported
> Recursive schemas (schemas that reference themselves, such as tree or linked-list structures) are not supported. A request containing a recursive JSON schema returns `HTTP 400`. Flatten recursive structures into a fixed-depth representation instead.

> [!NOTE] text.format vs response_format
> `text.format` is the [Responses API](/docs/protocols/responses) parameter for structured output. `response_format` is the [Chat Completions](/docs/protocols/chat-completions) equivalent for structured output. A parameter from the other endpoint does not configure structured output, even when accepted for compatibility.

Benefits:

- **Consistent format**: Output always follows your defined structure, so you can drop brittle parsing logic.
- **Reduced errors**: No unexpected variations in response shape.
- **Simpler integration**: Feed model output directly to APIs, databases, or downstream services that expect structured data.

## Choose the right use cases {#use-cases}

Structured output fits tasks where shape matters:

- **Extracting information**: Pull names, dates, locations, or product details from unstructured text.
- **Classifying data**: Categorize input into predefined labels or categories.
- **Generating function arguments**: Produce structured arguments for downstream functions or APIs from natural language.
- **Generating configurations**: Create JSON configuration files from user requirements.

## Using a JSON schema {#using-a-json-schema}

Define your schema directly in `response_format`. The schema follows standard JSON Schema syntax.

The example below extracts an address into a structured object.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "system",
            "content": "Extract the address from the user input into the specified JSON format.",
        },
        {
            "role": "user",
            "content": "Please format this address: 1 Hacker Wy Menlo Park CA 94025",
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "Address",
            "schema": {
                "type": "object",
                "properties": {
                    "street": {
                        "type": "string",
                    },
                    "city": {
                        "type": "string",
                    },
                    "state": {
                        "type": "string",
                        "description": "2-letter state abbreviation",
                    },
                    "zip": {
                        "type": "string",
                        "description": "5-digit zip code",
                    },
                },
                "required": [
                    "street",
                    "city",
                    "state",
                    "zip",
                ],
            },
        },
    },
)

print(response.model_dump_json(indent=2))
```
```typescript title="TypeScript (OpenAI SDK)"
import OpenAI from 'openai';

const apiKey = process.env.MODEL_API_KEY;
if (!apiKey) {
  throw new Error('MODEL_API_KEY is not set');
}

const client = new OpenAI({
  baseURL: 'https://api.meta.ai/v1',
  apiKey,
});

const response = await client.chat.completions.create({
  model: 'muse-spark-1.3',
  messages: [
    {
      role: 'system',
      content: 'Extract the address from the user input into the specified JSON format.',
    },
    {
      role: 'user',
      content: 'Please format this address: 1 Hacker Wy Menlo Park CA 94025',
    },
  ],
  response_format: {
    type: 'json_schema',
    json_schema: {
      name: 'Address',
      schema: {
        type: 'object',
        properties: {
          street: {
            type: 'string',
          },
          city: {
            type: 'string',
          },
          state: {
            type: 'string',
            description: '2-letter state abbreviation',
          },
          zip: {
            type: 'string',
            description: '5-digit zip code',
          },
        },
        required: [
          'street',
          'city',
          'state',
          'zip',
        ],
      },
    },
  },
});

console.log(JSON.stringify(response, null, 2));
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.post(
    "https://api.meta.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['MODEL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "muse-spark-1.3",
        "messages": [
            {
                "role": "system",
                "content": "Extract the address from the user input into the specified JSON format.",
            },
            {
                "role": "user",
                "content": "Please format this address: 1 Hacker Wy Menlo Park CA 94025",
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "Address",
                "schema": {
                    "type": "object",
                    "properties": {
                        "street": {
                            "type": "string",
                        },
                        "city": {
                            "type": "string",
                        },
                        "state": {
                            "type": "string",
                            "description": "2-letter state abbreviation",
                        },
                        "zip": {
                            "type": "string",
                            "description": "5-digit zip code",
                        },
                    },
                    "required": [
                        "street",
                        "city",
                        "state",
                        "zip",
                    ],
                },
            },
        },
    },
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "messages": [
    {
      "role": "system",
      "content": "Extract the address from the user input into the specified JSON format."
    },
    {
      "role": "user",
      "content": "Please format this address: 1 Hacker Wy Menlo Park CA 94025"
    }
  ],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "Address",
      "schema": {
        "type": "object",
        "properties": {
          "street": {
            "type": "string"
          },
          "city": {
            "type": "string"
          },
          "state": {
            "type": "string",
            "description": "2-letter state abbreviation"
          },
          "zip": {
            "type": "string",
            "description": "5-digit zip code"
          }
        },
        "required": [
          "street",
          "city",
          "state",
          "zip"
        ]
      }
    }
  }
}'
```


For all supported fields, see the [Chat Completions API reference](/docs/api-reference/chat-completions). The response contains a JSON string in `choices[0].message.content`:

```json
{
  "street": "1 Hacker Way",
  "city": "Menlo Park",
  "state": "CA",
  "zip": "94025"
}
```

Parse that string with `json.loads()` to work with it as a Python dict.

## Using Pydantic models {#using-pydantic-models}

If you use the OpenAI SDK, call `beta.chat.completions.parse()` with a Pydantic model as `response_format` and get a typed result back.

```python title="Python (OpenAI SDK)"
import os
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str


response = client.beta.chat.completions.parse(
    model="muse-spark-1.1",
    messages=[
        {
            "role": "system",
            "content": "Extract the address from the user input.",
        },
        {
            "role": "user",
            "content": "Please format this address: 1 Hacker Wy Menlo Park CA 94025",
        },
    ],
    response_format=Address,
)

address = response.choices[0].message.parsed
print(address.street)  # "1 Hacker Way"
print(address.state)   # "CA"
```

The `.parsed` attribute returns an `Address` instance with typed fields.

## Stay within schema constraints {#schema-constraints}

Model API validates schemas before decoding starts. A schema that exceeds these limits returns `HTTP 400`:

| Constraint | Limit |
|------------|-------|
| Nesting depth | 10 levels |
| Total properties | 5,000, across the whole schema |
| Total string length | 120,000 characters (property names, definition names, enum values, and `const` values combined) |
| Enum values | 1,000 by default (raisable per app), across all enum properties |
| Large string enums | A single string enum with more than 250 values is additionally capped at 15,000 combined characters |
| Expanded size | A schema that expands beyond 200,000 nodes once `$ref`s are inlined is rejected |

These limits apply to structured-output schemas (`response_format` / `text.format`) and to function-tool `parameters` schemas, on both `/v1/chat/completions` and `/v1/responses`. Recursive (`$ref`-cycle) schemas are also rejected; see the note under [How it works](#how-it-works).

## Enforce strict mode {#strict-mode}

The `strict` flag controls whether your schema must conform to the supported strict subset below. `strict` defaults to `false` on every surface. When omitted, the schema is accepted as-is (subject to the [constraints above](#schema-constraints)) and the strict-subset rules are not enforced. Set `strict: true` to require that the server validates your schema against the strict subset.

> [!NOTE] Structured output is always schema-constrained
> For structured output (`response_format` / `text.format`), the response is always constrained to your JSON Schema, so `strict: false` currently behaves the same as `strict: true` — output still conforms to the schema. The `strict` flag only controls whether the server additionally validates your schema against the strict subset below.

| Surface | Parameter | `strict` default |
|---------|-----------|------------------|
| Chat Completions structured output | `response_format.json_schema.strict` | `false` |
| Responses structured output | `text.format.strict` | `false` |
| Chat Completions function tool | `tools[].function.strict` | `false` |
| Responses function tool | `tools[].strict` | `false` |

When `strict: true`, your schema must satisfy the strict subset (modeled on OpenAI's):

- **Root must be a plain object**: no top-level `anyOf`, `oneOf`, `allOf`, `enum`, or `not`.
- **`allOf` and `oneOf`**: not supported anywhere in the schema; `anyOf` is supported below the root.
- **`additionalProperties`**: every object must set `additionalProperties: false`.
- **`required`**: an object's `required` array must list every key in its `properties`.

A schema that violates the subset returns `HTTP 400` only when `strict: true`; the same schema with `strict` omitted (or `false`) is accepted and normalized. The subset is validated inside `$defs` / `definitions` as well.

## Combine with other features {#combining-with-other-features}

Structured output works with the rest of Model API:

- **[Tool calling](/docs/tool-calling)**: Define consistent formats for tool arguments or structure data returned from tools before the model processes it.
- **[Image understanding](/docs/image-understanding)**: Extract structured data from images, such as detected objects, labels, or recognized text.
- **[Chat completion](/docs/protocols/chat-completions)**: Use validated structured output from one turn as reliable context in later turns.

## Next steps

- Now that you have JSON validation working, wire it into a [tool-calling loop](/docs/tool-calling) for reliable agent pipelines with schema-constrained arguments.
- Build the core conversation and test your schemas in [chat completion](/docs/protocols/chat-completions).
- Check the full parameter and response shapes in the [Chat Completions API reference](/docs/api-reference/chat-completions).