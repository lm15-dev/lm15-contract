# 2026-09-26 — Gemini: a schema goes in the field that can carry it (MAP-16)

**Status: DECISION (maintainer request, 2026-09-26) + normative rule
MAP-16, not yet ratified. Wire evidence: live receipts below.**

## The finding

lm15-go's first live smoke (lm15-go `receipts/2026-09-26-live-smoke`) sent a
function tool whose parameters carry `"additionalProperties": false` to
Gemini and got a 400: `Unknown name "additionalProperties" at
'tools[0].function_declarations[0].parameters'`. Every SDK sends a tool's
parameters in `functionDeclarations[].parameters`, which is Gemini's
OpenAPI Schema object; the reference built the identical body offline. For
structured output lm15 already switched fields (`responseJsonSchema`
when the schema contains `additionalProperties`, since 2026-09-02); tools
never did. OpenAI strict mode requires `additionalProperties: false`, so
a schema written for one provider broke on another — the opposite of what
lm15 is for.

## What the provider does (receipts/2026-09-26-gemini)

`research/providers/gemini/capture_schema_fields.py` sent 29 schemas,
verbatim, in all four fields (`responseSchema`, `responseJsonSchema`,
`parameters`, `parametersJsonSchema`) to gemini-2.5-flash:

- The OpenAPI fields refuse an unknown key anywhere in a schema node
  (`additionalProperties`, `const`, `$ref`/`$defs`), a list `type`, an
  `enum` with a non-string element, and a boolean sub-schema. The JSON
  Schema fields accept all of them.
- The JSON Schema fields refuse spellings the OpenAPI fields accept: a
  count or bound as a string (`"maxItems": "3"`, `"minimum": "1"`), `null`
  for a field, one string where a list is expected (`"required": "v"`,
  `"enum": "x"`, `anyOf` as one object), `nullable` that is not a boolean.
- Both accept Gemini's own spellings (uppercase `type`, `nullable`,
  `propertyOrdering`, `example`) and plain schemas; both refuse some
  malformed schemas (`items` as a list, a non-string `description`).
- A property named `additionalProperties` or `$ref`, and an `example` that
  contains keywords, are accepted by both: names and values are not read
  as keywords.

So neither field is always right. Moving every schema to the JSON Schema
field would break the second group, which works today.

Gemini Live accepted `parametersJsonSchema` in its setup frame and called
the tool (`receipts/2026-09-26-gemini/live-parametersJsonSchema.md`). A
cached prefix's tools use the same FunctionDeclaration type (API
reference, `scrapes/gemini/pages/generate-content.md`); not probed live
(a cache needs a prefix of at least 1,024 tokens).

## Decision

MAP-16 (`docs/mapping-rules.md`): the JSON Schema field exactly when a
schema node uses something only JSON Schema can say (a key outside
Gemini's Schema object, a list `type`, a non-string `enum` element, a
boolean schema); the OpenAPI field otherwise. The same rule for response
formats and for tool parameters, on generateContent, cached prefixes and
Live. The schema is verbatim either way (INV-002).

For response formats this widens the old `additionalProperties` rule: a
Pydantic-shaped schema (`$defs`/`$ref`), `const`, an integer `enum` or a
`["string", "null"]` type used to be sent to `responseSchema` and refused;
they now go to `responseJsonSchema` and work. Two kinds of schema move
the other way, from `responseJsonSchema` to `responseSchema`: one with a
property *named* `additionalProperties`, and one whose `example` contains
that key (the old rule matched the key anywhere). Both fields accept
those (receipted), so nothing that worked stops working. Every existing
case builds the same body as before.

## Pinned by

- `mapping/gemini-schema-field.json`: 29 vectors; the harness's new
  `mapping` direction builds each as tool parameters, as a response
  format and as a cached prefix's tool (87 checks; PROTOCOL.md).
  `tools/test_mapping_vectors.py` checks every vector against its four
  receipts: where only one kind of field accepted a schema, the vector
  names it. `harness/selftest.py`: mutation `gemini_schema_field_flip`.
- Two live wire cases: `gemini.tool_parameters_json_schema` (the model
  called the tool) and `gemini.response_json_schema_defs` (a `$defs`/`$ref`
  schema answered as JSON), with drafted goldens.

## Measured before the SDKs moved

At this commit with the pre-MAP-16 SDKs: lm15-go fails 26 of the 87
mapping checks: the 9 vectors that need the JSON Schema field, as tools
and as cached tools (18), and 8 response formats where the old rule
differs (6 it sent to `responseSchema`, which refuses them; the 2 above).
The reference, changed first, passes all.
