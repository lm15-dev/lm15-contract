> ## Documentation Index
> Fetch the complete documentation index at: https://docs.fireworks.ai/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> For Fireworks Nexus, start at https://docs.fireworks.ai/nexus.
> Use https://docs.fireworks.ai/nexus/quickstart for coding harnesses, custom agents, APIs, SDKs, and LLM gateways.
> Use https://docs.fireworks.ai/nexus/firerouter for model router types, composition, and pricing.
> Prefer canonical short model IDs such as firerouter/opus. In LiteLLM, use the fireworks_ai/ provider prefix.
> Family names such as opus track the latest evaluated family version; do not describe them as fixed model versions.

# Structured Outputs

> Enforce output formats using JSON schemas or custom grammars

Structured outputs ensure model responses conform to your specified format, making them easy to parse and integrate into your application. Fireworks supports two methods: **JSON mode** (using JSON schemas) and **Grammar mode** (using custom BNF grammars).

<Info>
  New to structured outputs? Check out the [Serverless Quickstart](/getting-started/quickstart#structured-outputs-json-mode) for a quick introduction.
</Info>

## Quick Start

Force model output to conform to a [JSON schema](https://json-schema.org/):

```python theme={null}
import os
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(
    api_key=os.environ.get("FIREWORKS_API_KEY"),
    base_url="https://api.fireworks.ai/inference/v1"
)

# Define your schema
class Result(BaseModel):
    winner: str

# Make the request
response = client.chat.completions.create(
    model="accounts/fireworks/models/kimi-k2p5",
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "Result",
            "schema": Result.model_json_schema()
        }
    },
    messages=[{
        "role": "user",
        "content": "Who won the US presidential election in 2012? Reply in JSON format."
    }]
)

print(response.choices[0].message.content)
# Output: {"winner": "Barack Obama"}
```

<Tip>
  Include the schema in **both** your prompt and the `response_format` for best results. The model doesn't automatically "see" the schema—it's enforced during generation.
</Tip>

## Response Format Options

Fireworks supports two JSON mode variants:

* **`json_object`** – Force any valid JSON output (no specific schema)
* **`json_schema`** – Enforce a specific JSON schema (recommended)

<Warning>
  Always instruct the model to produce JSON in your prompt. Without this, the model may generate whitespace indefinitely until hitting token limits.
</Warning>

<AccordionGroup>
  <Accordion title="Using arbitrary JSON mode">
    To force JSON output without a specific schema:

    ```python theme={null}
    response = client.chat.completions.create(
        model="accounts/fireworks/models/kimi-k2p5",
        response_format={"type": "json_object"},
        messages=[{
            "role": "user",
            "content": "List the top 3 programming languages in JSON format."
        }]
    )
    ```

    This is similar to [OpenAI's JSON mode](https://platform.openai.com/docs/guides/text-generation/json-mode).
  </Accordion>

  <Accordion title="Important notes and limitations">
    **Token limits:** If `finish_reason="length"`, the response may be truncated and invalid JSON. Increase `max_tokens` if needed.

    **Completions API:** JSON mode works with both Chat Completions and Completions APIs.

    **Function calling:** When using [Tool Calling](/guides/function-calling), JSON mode is enabled automatically—these guidelines don't apply.
  </Accordion>
</AccordionGroup>

## JSON Schema Support

Fireworks supports most [JSON Schema 2020-12](https://json-schema.org/specification) constructs, and also accepts Draft-7 keyword aliases (`definitions`) for backward compatibility:

**Supported:**

* Types: `string`, `number`, `integer`, `boolean`, `object`, `array`, `null`
* Object constraints: `properties`, `required`, `additionalProperties`
* Array constraints: `items`
* Length/size constraints: `minLength`, `maxLength`, `minItems`, `maxItems`
* Regular expressions: `pattern`
* Composition: `anyOf`, `allOf`, `oneOf`
* Reuse: `$defs` (Draft 2020-12) and `definitions` (Draft 7), referenced via `$ref`
* Annotations: `$id`, `$schema`, `description`, `title`, `default`
* Recursive references (self-recursive `$ref`, mutually recursive `$defs`)

**Not yet supported:**

* External `$ref` URIs (HTTP/file). Only in-document JSON Pointer fragments are resolved.

<Tip>
  Fireworks automatically prevents hallucinated fields by treating schemas with `properties` as if `"unevaluatedProperties": false` is set.
</Tip>

<Note>
  `pattern` is enforced on a best-effort basis: regexes that can be compiled into the underlying grammar are enforced, and constructs that can't (e.g. lookahead/lookbehind) are safely ignored — the field falls back to an unconstrained string and the request still succeeds.
</Note>

### JSON Pointer references (`$ref`)

`$ref` follows the [RFC 6901 JSON Pointer](https://datatracker.ietf.org/doc/html/rfc6901) syntax used by JSON Schema 2020-12. Fireworks supports two pointer forms in the same document:

1. **Fully-qualified pointer (strict-spec).** A `$ref` whose fragment is a complete JSON Pointer to the definition's actual location, e.g. `#/properties/A/$defs/Foo`. Always resolves to that exact location, regardless of any other definitions in the document. This is fully portable across any conformant JSON Schema 2020-12 implementation.

2. **Bare shorthand `#/$defs/Foo` (Fireworks extension).** When `Foo` is placed inside a nested subschema (e.g. `properties.A.$defs.Foo`) instead of at the document root, Fireworks lifts every nested `$defs` / `definitions` entry into a root pool so that the bare pointer resolves. Most converters (OpenAPI, Instructor, LangChain `TypeAdapter`, pydantic v2) emit this shape, so the shorthand keeps them working without rewrites. **This shorthand is not portable** — strict validators will return `PointerToNowhere` for the same pointer.

**Name-collision precedence for the bare shorthand:**

* **Root-level `$defs[Foo]` always wins.** If `Foo` exists at both the document root and a nested location, `#/$defs/Foo` resolves to the root entry. The fully-qualified pointer to the nested entry continues to work and addresses the nested definition.
* **Nested vs. nested:** if `Foo` appears at multiple nested locations and there is no root entry, the first occurrence in document order wins (and the server logs a warning). If you need both, give them distinct names or hoist the shared definition to the root.
* **`$defs` and `definitions` are independent pools** — `#/$defs/Foo` and `#/definitions/Foo` address two different schemas, exactly as the spec defines.

<Tip>
  For maximum portability, place all `$defs` at the document root and reference them with `#/$defs/<Name>`. This is the shape OpenAI, pydantic v2, and the JSON Schema spec recommend, and works on every conformant validator.
</Tip>

<Accordion title="Example: recursive schema (linked list)">
  Self-recursive and mutually recursive schemas are supported. The example below is the canonical linked-list shape and works in both `response_format` and tool calling parameters:

  ```json theme={null}
  {
    "$defs": {
      "linked_list_node": {
        "type": "object",
        "properties": {
          "value": {"type": "integer"},
          "next": {
            "anyOf": [
              {"$ref": "#/$defs/linked_list_node"},
              {"type": "null"}
            ]
          }
        },
        "required": ["value"]
      }
    },
    "$ref": "#/$defs/linked_list_node"
  }
  ```
</Accordion>

<Accordion title="Example: pydantic v2 schemas with `$id`">
  Schemas emitted by `pydantic.BaseModel.model_json_schema()` typically carry a root `$id` annotation. This is treated as an identity annotation only — Fireworks never attempts to fetch the URI — and `#/$defs/...` references resolve correctly within the document:

  ```python theme={null}
  from pydantic import BaseModel

  class Person(BaseModel):
      name: str
      age: int

  class Response(BaseModel):
      person: Person

  # Response.model_json_schema() returns a schema with `$id`, `$defs`, and `$ref`.
  # Pass it directly into `response_format={"type": "json_schema", ...}`.
  ```
</Accordion>

<Accordion title="Advanced: Reasoning Model JSON Mode">
  Some models support generating structured JSON outputs alongside their reasoning process. The [Fireworks Python SDK](/tools-sdks/python-sdk) exposes the model's reasoning via the `reasoning_content` field, keeping it separate from the JSON output in the `content` field.

  <Warning>
    Using `response_format` with `json_schema` disables reasoning output. To get **both** reasoning and structured JSON, include the schema in your prompt instead and omit the `response_format` parameter.
  </Warning>

  #### Example Usage

  ````python theme={null}
  import json
  from fireworks import Fireworks
  from pydantic import BaseModel

  client = Fireworks()

  # Define the output schema
  class QAResult(BaseModel):
      question: str
      answer: str

  # Include the schema in the prompt to preserve reasoning
  schema = QAResult.model_json_schema()

  response = client.chat.completions.create(
      model="accounts/fireworks/models/kimi-k2p5",
      messages=[{
          "role": "user",
          "content": (
              "Who wrote 'Pride and Prejudice'?\n\n"
              f"Reply in JSON matching this schema:\n{json.dumps(schema, indent=2)}"
          )
      }],
      max_tokens=1000
  )

  # The Fireworks SDK separates reasoning into its own field
  reasoning = response.choices[0].message.reasoning_content
  content = response.choices[0].message.content

  # Strip markdown code fences if the model wraps the JSON
  json_str = content.strip()
  if json_str.startswith("```"):
      json_str = json_str.split("\n", 1)[1].rsplit("```", 1)[0].strip()

  # Parse into Pydantic model
  qa_result = QAResult.model_validate_json(json_str)

  if reasoning:
      print("Reasoning:", reasoning)
  print("Result:", qa_result.model_dump_json(indent=2))
  ````

  <Tip>
    If you don't need reasoning and just want guaranteed schema-conformant JSON, use the `response_format` parameter as shown in the [Quick Start](#quick-start) above. The `response_format` approach enforces the schema during generation, eliminating the need to parse the JSON yourself.
  </Tip>

  #### Use Cases

  Reasoning mode is useful for:

  * **Debugging**: Understanding why the model generated specific outputs
  * **Auditing**: Documenting the decision-making process
  * **Complex tasks**: Scenarios where the reasoning is as valuable as the final answer

  See the [Reasoning guide](/guides/reasoning) for more on working with reasoning models.
</Accordion>

## Grammar Mode

For advanced use cases where JSON isn't sufficient, use [Grammar mode](/structured-responses/structured-output-grammar-based) to constrain outputs using custom BNF grammars. Grammar mode is ideal for:

* **Classification tasks** – Limit output to a predefined list of options
* **Language-specific output** – Force output in specific languages or character sets
* **Custom formats** – Define arbitrary output structures beyond JSON

[Learn more about Grammar mode →](/structured-responses/structured-output-grammar-based)

## Related features

Check out [Tool Calling](/guides/function-calling) for multi-turn capabilities and routing across multiple schemas.
