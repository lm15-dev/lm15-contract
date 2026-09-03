> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Use response_format to control model output format

> Use `response_format` for JSON Mode or Structured Output and handle schema, structure, and Partial Mode constraints.

The Kimi API constrains the output format of chat completions via the `response_format` parameter. It supports two modes:

| Mode                  | `type` value  | Description                                                                | Use case                                                               |
| --------------------- | ------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **JSON Mode**         | `json_object` | Guarantees a valid JSON Object, but does not constrain specific fields     | Simple JSON output, flexible-field scenarios                           |
| **Structured Output** | `json_schema` | Precisely defines field names, types, and nested structure via JSON Schema | Scenarios requiring strict structure and downstream-system integration |

This document focuses on the **`json_schema` mode of `response_format` (i.e., Structured Output)**, including parameter usage, model differences, common issues, and error handling. For the basics of JSON Mode, see [JSON Mode](/docs/guide/use-json-mode-feature-of-kimi-api).

## response\_format basic structure

```python theme={null}
response_format={
    "type": "json_schema",           # or "json_object"
    "json_schema": {                 # required for json_schema mode
        "name": "schema_name",
        "strict": True,
        "schema": { ... }            # your JSON Schema
    }
}
```

* When `type` is `json_object`, the `json_schema` field is not required.
* When `type` is `json_schema`, both `json_schema.name` and `json_schema.schema` are required.

## Advantages of Structured Output

Compared to JSON Mode, Structured Output offers the following advantages:

* **Strictly controlled structure**: The model output must fully follow the JSON Schema you define, with field names, types, and nesting levels matching one-to-one.
* **No need to repeatedly describe the format in the prompt**: Decouple format requirements from the schema, reducing prompt-engineering complexity.
* **More reliable downstream integration**: Output can be directly parsed by `json.loads` into strongly-typed objects without extra fault-tolerance handling.

> **Model-difference note**: Different models have different levels of JSON Schema support.
>
> * `kimi-k3` reliably supports Structured Output, including nested objects, arrays, and `anyOf`.
> * `kimi-k2.7-code` has the most stable Structured Output support, including nested objects, arrays, `anyOf` / `oneOf` / `$ref` / `additionalProperties: true`, etc.
> * `kimi-k2.6` occasionally behaves unstably with complex schemas; for example, `$ref` may return a Markdown code block, `oneOf` may be ignored, and `partial=true` may output fields outside the schema. When using `kimi-k2.6`, prefer simple schemas and add a second validation layer in your business logic.

## Quick start

### Basic usage

Set `type` to `"json_schema"` in `response_format`, and pass the `json_schema` object:

```python theme={null}
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.ai/v1",
)

completion = client.chat.completions.create(
    model="kimi-k3",
    messages=[
        {
            "role": "system",
            "content": "You are a news summarization assistant."
        },
        {
            "role": "user",
            "content": "Please summarize the following news: Today, the field of artificial intelligence technology has welcomed a major breakthrough..."
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "news_summary",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "News headline"},
                    "author": {"type": "string", "description": "Author or source"},
                    "publish_time": {"type": "string", "description": "Publication time in ISO 8601 format"},
                    "summary": {"type": "string", "description": "Summary within 200 characters"},
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "3-5 keywords"
                    }
                },
                "required": ["title", "author", "summary", "keywords"]
            }
        }
    }
)

import json
result = json.loads(completion.choices[0].message.content)
print(result["title"])
print(result["keywords"])
```

### Example output

```json theme={null}
{
  "title": "Major Breakthrough in Artificial Intelligence Technology",
  "author": "Tech Daily",
  "publish_time": "2024-06-19",
  "summary": "Researchers have made new progress in deep learning model efficiency optimization...",
  "keywords": ["artificial intelligence", "deep learning", "model optimization", "breakthrough"]
}
```

### About reasoning\_content

Thinking models such as `kimi-k3` and `kimi-k2.7-code` may return `reasoning_content` in addition to `content`. Only parse `choices[0].message.content` as the final JSON; do not call `json.loads` on the entire response object.

```python theme={null}
content = completion.choices[0].message.content
result = json.loads(content)
```

## Parameter description

| Parameter            | Type                               | Description                                                                     |
| -------------------- | ---------------------------------- | ------------------------------------------------------------------------------- |
| `type`               | `"json_schema"` \| `"json_object"` | Must be set; choose one                                                         |
| `json_schema.name`   | string                             | Identifier name for the schema, used for logging and debugging                  |
| `json_schema.strict` | boolean                            | Whether to strictly enforce the schema. Recommended to explicitly set to `true` |
| `json_schema.schema` | object                             | JSON Schema object defining the output structure                                |

> **Note**: Whether `strict` is `true`, `false`, or omitted, `kimi-k2.7-code` generally adheres to the schema well; `kimi-k2.6` is more likely to output fields outside the schema when `strict=false` or omitted. Always explicitly set `strict: true`.

## `strict` mode

`json_schema.strict` is recommended to be set to `true`, meaning the model output **must** fully match the schema definition. In this case, your schema must comply with the **MFJS (Moonshot Flavored JSON Schema)** specification.

> **MFJS model differences**:
>
> * `kimi-k2.7-code` already has relatively complete support for features such as `anyOf` / `oneOf` / `$ref` / `additionalProperties: true`, and usually will not trigger MFJS errors.
> * `kimi-k2.6` is more likely to hit MFJS limits with complex schemas; keep schemas simple.

If `strict` is set to `false`, the API only guarantees that the output is a valid JSON object, but does not strictly enforce the internal field structure. This can be used when the schema is complex or you want to give the model more flexibility.

### How to validate schema compliance with MFJS

You can use the `walle` CLI tool to quickly self-check schema compatibility:

```bash theme={null}
# Install the walle tool
go install github.com/moonshotai/walle/cmd/walle@latest

# Validate your schema
walle -schema 'your_schema_json' -level strict
```

> Even if the schema contains `anyOf` / `oneOf` / `$ref`, the API often returns `200`, and the response **does not contain a `warning` field**. Therefore, `walle` is better suited as a static-check entry point; actual compatibility should be verified via live calls against the target model.

## Nested objects and arrays example

Structured Output supports arbitrarily deep nested objects and arrays, which is stable on `kimi-k2.7-code`:

```python theme={null}
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "meeting_minutes",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "meeting_title": {"type": "string"},
                "date": {"type": "string"},
                "attendees": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "present": {"type": "boolean"}
                        },
                        "required": ["name", "role", "present"]
                    }
                },
                "agenda_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "discussion": {"type": "string"},
                            "action_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "assignee": {"type": "string"},
                                        "task": {"type": "string"},
                                        "deadline": {"type": "string"}
                                    },
                                    "required": ["assignee", "task"]
                                }
                            }
                        },
                        "required": ["topic", "discussion"]
                    }
                }
            },
            "required": ["meeting_title", "date", "attendees", "agenda_items"]
        }
    }
}
```

## Comparison with JSON Mode

| Feature           | `json_object`                            | `json_schema` + `strict: true`                                                   |
| ----------------- | ---------------------------------------- | -------------------------------------------------------------------------------- |
| Output validity   | Guaranteed valid JSON Object             | Guaranteed valid JSON Object                                                     |
| Field names       | Not guaranteed — the model may improvise | Strictly fixed                                                                   |
| Field type        | Not enforced                             | Enforced to match                                                                |
| Extra fields      | May be added at will                     | Forbidden (`additionalProperties: false`)                                        |
| Missing fields    | May be omitted                           | `required` fields always appear; declare union types to allow `null`             |
| Mechanism         | Prompt guidance                          | Token-level constrained decoding (CFG), filtering illegal tokens during sampling |
| Use case          | Rapid prototyping, non-critical paths    | Production, API integration, data ingestion                                      |
| strict validation | None                                     | Yes (MFJS specification)                                                         |

The structural guarantee of constrained decoding holds when the schema complies with the MFJS specification; complex schemas may still be unstable on models such as `kimi-k2.6` — see the model-difference note above. For structured data consumed downstream, always use `json_schema` with `strict: true` to avoid writing extensive defensive code in the business layer.

## Notes

1. **Schema must comply with MFJS**: When `strict=true`, use the `walle` CLI tool to pre-validate the schema. Common MFJS constraints are greatly relaxed on `kimi-k2.7-code`, but may still trigger on `kimi-k2.6`.

2. **Prompt still needs context**: Although the format is constrained by the schema, the model still needs to understand the **business content**. Please clearly describe the task objective and data source in the system prompt or user prompt.

3. **`additionalProperties`**:
   * When set to `false`, the model will not output fields not defined in the schema.
   * When set to `true` or omitted, `kimi-k2.7-code` allows extra fields; `kimi-k2.6` may also output extra fields, but with less stability than `kimi-k2.7-code`.

4. **Use nullable union types for missing information**: Fields declared in `required` always appear in the output. When the input lacks the corresponding information, a field declared with a single type (e.g. `"integer"`) may lead the model to fabricate content or return an empty string. Prefer a union type that allows `null` (e.g. `"type": ["integer", "null"]`), so the model can use `null` to explicitly mean "information missing" instead of the string `"unknown"` or a disappearing field — downstream code can then `json.loads` and cast to typed objects without defensive handling. Note that `kimi-k2.6` may still return empty strings (e.g. `"employee_id": ""`), so keep a null-value check in the business layer.

5. **Error handling**: When the schema is too complex or the prompt contradicts the schema, the model may output incomplete JSON (`finish_reason="length"`). We recommend checking `finish_reason` and appropriately increasing `max_tokens`.

6. **Compatibility with Partial Mode**:
   * `kimi-k2.7-code` usually works with `partial=true` on simple schemas, but complex schemas may still break structural constraints.
   * `kimi-k2.6` is more likely to output fields outside the schema with `partial=true`, so **it is not recommended** to mix them on this model.

7. **Prefix cache**: setting `response_format` (or not setting it) **does not invalidate the prefix cache**, so you can adjust it on a per-request basis without hurting cache hit rates.

## Common errors

### `invalid_request_error`

When the schema format itself is invalid (for example, `json_schema.schema` is not an object), the API returns `400` with error type `invalid_request_error`:

```json theme={null}
{
  "error": {
    "message": "Invalid request: the `response_format.json_schema.schema` field in the request (expected type dict[string,interface]) is illegal...",
    "type": "invalid_request_error"
  }
}
```

Please check that the schema is a valid JSON Schema object.

### Output truncated (`finish_reason="length"`)

The model reached the `max_tokens` limit before outputting the complete JSON. We recommend:

* Increasing `max_tokens` (e.g., 4096 or higher)
* Simplifying the nesting depth of the schema
* Shortening the input text length

### Field type mismatch / Markdown code block output

On older models such as `kimi-k2.6`, the following may occur:

* The returned `content` contains a Markdown code block (e.g., `json ... `), causing `json.loads` to fail.
* Complex schemas such as `oneOf` / `$ref` are not strictly followed.

Recommendations:

* Use `kimi-k2.7-code` for Structured Output calls.
* If you must use `kimi-k2.6`, strip Markdown markers in the business layer first, then validate the parsed result against the schema fields.
