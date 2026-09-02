# Cookbook draft — Structured output and tool choice (as it would read under MAP-8)

## 1. Ask for JSON that matches your schema

One shape, every provider. `schema` is JSON Schema, written by you, sent
exactly as written.

```python
from lm15 import LMRouter, Request, Message, Config

router = LMRouter()
PERSON = {"type": "object",
          "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
          "required": ["name", "age"], "additionalProperties": False}

for model in ["gpt-5.6-sol", "claude-sonnet-5", "gemini-3.7-flash", "grok-4.3"]:
    response = router.complete(Request(
        model=model,
        messages=[Message.user("Extract the person: John is 34 years old.")],
        config=Config(response_format={"type": "json_schema", "schema": PERSON}),
    ))
    print(model, response.json)
```

```output
gpt-5.6-sol {'name': 'John', 'age': 34}
claude-sonnet-5 {'name': 'John', 'age': 34}
gemini-3.7-flash {'name': 'John', 'age': 34}
grok-4.3 {'name': 'John', 'age': 34}
```
(receipts: so:schema-strict on each provider, 2026-09-02)

## 2. Any JSON, no schema

```python
config=Config(response_format={"type": "json_object"})
```

Works on OpenAI, Gemini, xAI, Groq. Anthropic has no "any JSON" mode;
it always wants a schema. lm15 tells you instead of guessing one:

```output
UnsupportedFeatureError: anthropic: response_format json_object is not supported —
the Messages API has no any-JSON mode; give a json_schema (objects need
additionalProperties: false)
```
(the server's own answer to a schema-less request was HTTP 400
"'additionalProperties' must be explicitly set to false")

## 3. What if I pass the provider's own shape?

You used to be able to write OpenAI's `{"format": {...}}` or Gemini's
`{"response_mime_type": ...}` here. Now:

```python
Config(response_format={"format": {"type": "json_schema", "name": "x", "schema": PERSON}})
```

```output
ValueError: response_format must be {'type': 'json_object'} or {'type': 'json_schema',
'schema': {...}, 'name'?: str, 'strict'?: bool}; provider-native shapes go in
Config.extensions (got keys ['format'])
```

One spelling for one intent. If you really want the provider's own
field, `extensions` is the door, as for every provider-only knob.

## 4. Your schema is sent as written — and some providers will say no

lm15 never edits your schema to make a request pass. So the provider's
rules reach you unchanged, at request time, loudly:

```python
STRICT_ISH = {"type": "object",
              "properties": {"name": {"type": "string"}, "age": {"type": "integer", "minimum": 0}},
              "required": ["name"], "additionalProperties": False}
```

| model | what happens | why |
|---|---|---|
| gpt-5.6-sol | HTTP 400 `'required' is required to be supplied and to be an array including every key` | strict mode wants every property required |
| claude-sonnet-5 | HTTP 400 `properties maximum, minimum are not supported` | Anthropic's schema subset |
| gemini-3.7-flash | works | full JSON Schema |
| grok-4.3 | works | keywords enforced up to limits |

(receipts: so:schema-optional, so:schema-keywords)

If you want OpenAI to accept optional fields, say so: `"strict": False`.
It is passed verbatim where the wire has it (OpenAI, Groq, xAI) and is
simply true-by-nature on Anthropic and Gemini.

## 5. Tool choice: the same words everywhere

```python
from lm15 import ToolChoice, FunctionTool
tools = (FunctionTool(name="lookup", ...), FunctionTool(name="weather", ...))

ToolChoice(mode="auto")                               # the model decides
ToolChoice(mode="required")                           # it must call something
ToolChoice(mode="required", allowed=("weather",))     # it must call weather
ToolChoice(allowed=("lookup",))                       # only lookup is on the table
ToolChoice(parallel=False)                            # one call at a time
```

These held on every provider that can express them (receipts tc:*).

## 6. Where a provider cannot keep the promise, lm15 refuses

Three cells, each measured:

```python
# xAI: the allowlist is accepted and ignored — it called `weather` anyway
router.complete(Request(model="grok-4.6", messages=..., tools=tools,
                        config=Config(tool_choice=ToolChoice(allowed=("lookup",)))))
```
```output
UnsupportedFeatureError: xai: tool_choice.allowed subsets are silently ignored by
api.x.ai (verified live 2026-09-02); force a single tool with mode='required', or
send only the allowed tools in Request.tools
```

```python
# Gemini: no parallel knob — two calls came back regardless
config=Config(tool_choice=ToolChoice(parallel=False))     # on gemini-*
```
```output
UnsupportedFeatureError: gemini: tool_choice.parallel=False is not supported —
GenerateContent has no parallel-tool-calls knob and returns several calls regardless
(OpenAI and Anthropic carry it)
```

```python
# xAI: a forced tool next to a schema — JSON text came back, no call
config=Config(tool_choice=ToolChoice(mode="required"), response_format={"type": "json_object"})
```
```output
UnsupportedFeatureError: xai: a forced tool (mode='required') cannot be combined
with response_format — api.x.ai returns JSON text and drops the call
```

(the three error texts above are the adapter's; the underlying
behaviours are the receipts tc:allow-lookup-ask-weather, tc:parallel-false,
tc:force+schema)

## 7. `name` on a schema

OpenAI and Groq want a name for the schema; Anthropic and Gemini have no
field for it. lm15 defaults it to `"response"` where it is required and
drops it where there is no slot. A name changes nothing the model does.
