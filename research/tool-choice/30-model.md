# Tool choice + structured output — the model and the mapping (proposal, 2026-09-02)

## Tool choice

`ToolChoice(mode, allowed, parallel)` is already the right shape; the
2026-09-01 kind-aware mapping holds. Three silent cells found:

| Intent | OpenAI (both) | Anthropic | Gemini | xAI | Groq/compat |
|---|---|---|---|---|---|
| `mode=none/auto/required` | verbatim | none/auto/any | NONE/AUTO/ANY | verbatim | verbatim (server validates the outcome) |
| single name + required | forced function / hosted tool | `{type: tool, name}` | ANY + `allowedFunctionNames` | forced function | forced function |
| allowlist (subset, or single + auto) | `allowed_tools` (restriction held) | RAISE (unchanged) | VALIDATED + `allowedFunctionNames` (held) | **RAISE** (was: `allowed_tools` sent and silently ignored — receipt) | server 400 (loud) |
| `parallel=false` | `parallel_tool_calls: false` | `disable_parallel_tool_use` | **RAISE** (was: silently ignored — receipt: 2 calls) | `parallel_tool_calls: false` (held) | `parallel_tool_calls: false` |
| forced tool + `response_format` | call wins, format ignored | call wins | server 400 | **RAISE** (was: JSON text returned, the force silently lost — receipt) | server 400 |

Provider behaviours recorded, not lm15's to fix: Anthropic Sonnet 5 may
add calls beside a forced one; Gemini 2.5 `NONE` with a tool-needing
prompt ends `UNEXPECTED_TOOL_CALL` (lm15 raises in-band, loud); Groq
validates required/none/forced server-side and 400s when the model
disobeys.

## Structured output

Today `Config.response_format` is an opaque object with four per-adapter
heuristics that accept provider-native shapes (`{"format": ...}`,
`{"response_mime_type": ...}`, `{"json_schema": {...}}`, bare schemas).
Two canonical spellings for one intent, and the wire decides which. The
frame forbids that.

**Canonical shape (INV-050, proposed):** `response_format` is one of

- `{"type": "json_object"}` — any valid JSON;
- `{"type": "json_schema", "schema": <JSON Schema>, "name"?: str, "strict"?: bool}`.

Any other object RAISES at `Config` construction. Provider-native shapes
belong in `extensions` (the passthrough door), never in `response_format`.
`schema` stays opaque and verbatim (INV-002): lm15 never rewrites a
keyword, drops `minimum`, or flips `additionalProperties` to make a
request pass — the provider's 400 is the contract.

| Intent | OpenAI Responses | OpenAI Chat / xAI / Groq / compat | Anthropic | Gemini |
|---|---|---|---|---|
| `json_object` | `text.format.type: json_object` | `response_format.type: json_object` | **RAISE** (no any-JSON form; was: a `{type: object}` schema the server rejects) | `responseMimeType: application/json` |
| `json_schema` | `text.format: {type: json_schema, name, schema, strict?}` (`name` defaults to `"response"`) | `response_format: {type: json_schema, json_schema: {name, schema, strict?}}` | `output_config.format: {type: json_schema, schema}`; `name`/`strict` have no slot — `strict` is satisfied (always constrained), `name` dropped? no: RAISE if `name` set? | `responseMimeType` + `responseJsonSchema` (JSON Schema) or `responseSchema` (OpenAPI subset) — chosen by the existing `additionalProperties` rule |
| `strict: true` | verbatim (server enforces all-required) | verbatim | satisfied (always enforced) | satisfied |
| `strict: false` | verbatim | verbatim | satisfied (enforcement is stronger than asked) | satisfied |
| `name` | verbatim | verbatim | dropped silently? → keep as a label: no wire slot, but a name is not a control — accepted | same |

Decision on `name`: it is a label, not a control (it changes nothing the
model does on the providers that take it). Dropping it where there is no
slot is not a silent behaviour change. Stated.
