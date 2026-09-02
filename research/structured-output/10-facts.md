# Structured output — fact sheets (2026-09-02)

Same 141-cell run (`../tool-choice/20-results.json`). Sources: 10 pages.

| Cell | OpenAI Responses / Chat | Anthropic (Sonnet 5 and 4.5) | Gemini 2.5 / 3.7 | xAI | Groq |
|---|---|---|---|---|---|
| any JSON (`json_object` / mime) | ok | **no form**: `format.schema` requires `additionalProperties: false` on objects (400) | ok (`responseMimeType`) | ok | ok |
| schema, strict (all required, no extra props) | ok | ok (always constrained) | ok | ok | ok |
| schema with an optional field | **400** strict needs every property in `required` | ok | ok | ok | **400** same as OpenAI |
| minimum/maximum, `format: email`, `pattern` | ok (5.6) | **400 "maximum, minimum are not supported"** | ok | ok (docs: enforced up to limits, `format` best-effort `xai-structured-outputs.md:59-84`) | ok |
| `$ref`/`$defs` | ok | ok | ok | ok | ok |
| `anyOf` with null | ok | ok | ok | ok | ok |
| schema + tools offered | ok | ok | **2.5: 400 "Function calling with a response mime type unsupported"**; 3.7 ok | ok | **400 "json mode cannot be combined with tool calling"** |
| schema + thinking | ok | ok (adaptive) | ok | ok | ok |
| `strict: false` | ok, best-effort | n/a (no knob) | n/a | ok (same output) | ok, best-effort (`groq-structured-outputs.md:19-20`) |

Guarantees: OpenAI strict = constrained decoding (`openai-structured-outputs.md:326-338`);
Anthropic always constrained, supported-model list (`anthropic-structured-outputs.md:9,33-36`);
Gemini `responseJsonSchema` accepts JSON Schema keywords, `responseSchema`
is the OpenAPI subset (generate-content reference); xAI "guaranteed to match
your schema" for supported keywords, `additionalProperties` defaults to
false (`xai-structured-outputs.md:12,49`); Groq strict = constrained, needs
all-required + `additionalProperties: false`, no streaming, no tools
(`groq-structured-outputs.md:5-9,44`).
