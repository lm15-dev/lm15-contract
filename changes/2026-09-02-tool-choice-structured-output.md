# 2026-09-02 — Tool choice and structured output: three silent cells, one canonical shape (MAP-8, proposed)

Ratification: PENDING — awaiting Maxime Rivest. Third and fourth design
passes (`playbooks/design-pass.md`), run together; records under
`research/tool-choice/` and `research/structured-output/`. Do not push
before ratification.

## What the passes established (141 live cells, 19 sources)

- The 2026-09-01 kind-aware `ToolChoice` mapping holds on OpenAI (both
  dialects), Anthropic, Gemini, and Groq. Three cells were silent:
  1. xAI ignores `allowed_tools`: with `{lookup}` allowed and weather
     requested it called **weather**.
  2. Gemini has no parallel knob: `parallel=false` still returned two
     calls on 2.5 and 3.7.
  3. xAI with a forced tool **and** a `response_format` returned JSON
     text and no call — the force lost silently.
- `response_format` had no canonical shape: four adapter heuristics
  accepted provider-native spellings and two corpus cases pinned them.
- Anthropic has no any-JSON mode (`format.schema` needs
  `additionalProperties: false`, 400 otherwise) and rejects
  `minimum`/`maximum` (400); OpenAI and Groq strict mode need every
  property in `required` (400 otherwise); Gemini 2.5 rejects a schema
  next to tools (3.x accepts); Groq rejects JSON mode with tools.
  All loud — the contract leaves them to the server.

## The rule — MAP-8

**Tool choice** (amends the 2026-09-01 mapping in spec/types.md):

1. `allowed` on xAI RAISES (any allowlist form; a single name with
   `required` still maps to the forced-function form, which held).
2. `parallel=false` on Gemini RAISES (no wire knob; the outcome is not
   observable from usage, so the MAP-6 fallback exception does not apply).
3. `tool_choice` `required`/forced together with `response_format` on xAI
   RAISES (the force is silently lost). Elsewhere the server decides
   (Gemini and Groq 400; OpenAI and Anthropic let the call win).

**Structured output:**

4. **INV-050 — `response_format` has exactly two shapes**:
   `{"type": "json_object"}` and `{"type": "json_schema", "schema":
   <JSON Schema>, "name"?: str, "strict"?: bool}`. Any other object
   RAISES at `Config` construction with both shapes and the `extensions`
   door in the message. `schema` is opaque and verbatim (INV-002): lm15
   never rewrites a keyword to make a request pass.
5. Mapping: OpenAI Responses `text.format` (`name` defaults to
   `"response"`, `strict` verbatim); Chat dialect, xAI, Groq, compat
   `response_format.json_schema {name, schema, strict}`; Anthropic
   `output_config.format {type: json_schema, schema}`; Gemini
   `responseMimeType` + `responseJsonSchema` or `responseSchema` (the
   existing `additionalProperties` rule picks the field).
6. `json_object` on Anthropic RAISES (no any-JSON form).
7. `strict` is verbatim where the wire has it (OpenAI, Chat dialect,
   Groq, xAI) and satisfied where enforcement is always on (Anthropic,
   Gemini). `name` is a label, not a control: dropped where there is no
   slot, stated.
8. Provider-native shapes (`{"format": ...}`, `{"response_mime_type":
   ...}`, `{"json_schema": {...}}`, bare schemas) are no longer accepted
   in `response_format`; they belong in `extensions`.

## Behaviour changes (stated)

- Three new raises (rules 1–3, 6).
- `Config(response_format=<native shape>)` now raises; two corpus cases
  (`gemini.response_schema`, `openai.structured_output`) rewrite their
  canonical request to the canonical shape with the wire unchanged.
- The four adapter heuristics shrink to the two shapes.

## Open questions for the maintainer

1. `name` dropped silently on Anthropic/Gemini (a label, proposed) or
   raise.
2. Whether Gemini `parallel=false` should raise (proposed) or fall back
   like prefix intents (the outcome is visible to the caller as a second
   tool call, arguably "observable").

## Implementation landed (2026-09-02, awaiting ratification)

Reference: INV-050 at `Config` construction; the four adapter heuristics
replaced by the two shapes; Anthropic `json_object` raise; Gemini
`parallel=False` raise; xAI allowlist and forced-tool-with-format raises;
MAP-8 in docs/mapping-rules.md; 937 tests (7 new).

Contract: `openai.structured_output` and `gemini.response_schema`
canonical requests rewritten to the canonical shape (wires byte-identical,
harness green); three new live cases `openai_chat.structured_output`,
`gemini.response_json_schema` (3.7 Flash, `responseJsonSchema`),
`xai.structured_output` with drafted goldens; INV-050 in
spec/invariants.md; Config row and the ToolChoice resolution notes in
spec/types.md.

Open questions 1 (`name` dropped as a label) and 2 (Gemini `parallel`
raise) stand as proposed.
