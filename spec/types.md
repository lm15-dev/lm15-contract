# lm15 canonical types

The written schema for every public canonical dataclass in the lm15 model
(`lm15-python/lm15/types.py` is the reference; this document is the spec).
Wire-format rules (omission, Number rule) are normative in
[`lm15-python/docs/serde-rules.md`](../../lm15-python/docs/serde-rules.md);
response-mapping rules in
[`lm15-python/docs/mapping-rules.md`](../../lm15-python/docs/mapping-rules.md).
Construction-time invariants are numbered in [invariants.md](invariants.md)
(cited as INV-###). Closed value sets are in
[vocabularies.md](vocabularies.md).

Conventions used in the tables:

- **JSON type** is the declared wire type per the Number rule (serde-rules.md
  "Number rule"): a float field is ALWAYS a JSON float (`1.0`), an int field
  ALWAYS a JSON int (`2`), regardless of the literal the caller typed.
- **Req** — `yes` means the constructor requires it; `shape` means the field
  is optional at construction (has a default) but is ALWAYS EMITTED on the
  wire, even when empty, because it is part of the type's shape
  (serde-rules.md: "Required fields are always emitted, even when empty").
- **Omission** — `omit-empty` means the field is dropped from this object's
  JSON when `null`/`""`/`[]`/`{}` (the one omission rule); `omit-default`
  means dropped only at its specific default (e.g. `false`); `always` means
  always emitted; `never` means never serialized (in-memory only).
- All tuples serialize as JSON arrays. All dataclasses are frozen + slotted;
  fields cannot be rebound after construction.
- `type` rows are the wire discriminator: a constant string, not a
  constructor argument, always emitted.
- `continuation` is `[ContinuationState]` on every Part and on Message:
  optional, default `[]`, emitted only when non-empty.

## Required-with-shape fields (the empty-part question, answered)

Derived from `serde.part_to_dict` / sibling serializers — these fields are
emitted even when empty:

- `TextPart.text` — an empty text part serializes as
  `{"type": "text", "text": ""}`, never `{"type": "text"}`.
- `ThinkingPart.text` — same: `{"type": "thinking", "text": ""}`.
- `RefusalPart.text` — always emitted (and non-empty by INV-016 anyway).
- `ToolCallPart.input` — always emitted, `{}` when empty (opaque payload).
- `FunctionTool.parameters` — always emitted; an explicit `{}` round-trips
  verbatim as `{}` (opaque JSON-Schema payload — INV-033).
- `ToolResultPart.id` and `ToolResultPart.content` — always emitted;
  `content` would serialize as `[]` if empty (unreachable through the
  constructor, which requires non-empty content — INV-014 — but the
  serializer's contract is `[]`, not omission).
- Media parts' `media_type` — always emitted (non-empty by INV-010).
- `Message.role` and `Message.parts` — always emitted, no cleaning.
- `Delta.part_index` — always emitted (an int, never empty).
- `Response.model`, `Response.message`, `Response.finish_reason` — always.
- `Request.model`, `Request.messages` — always.
- Live events serialized without `_clean_mapping` emit ALL their fields
  verbatim, including `LiveClientTurnEvent.turn_complete` when `false`.

Everything else follows the omission rule: omitted when empty, at the top
level of its own object only; opaque payloads are never touched.

---

## Parts

### TextPart

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"text"` | — | `"text"` | always | discriminator |
| `text` | string | shape | — (required arg) | always (even `""`) | must be a string; empty allowed (INV-015) |
| `continuation` | array of ContinuationState | no | `[]` | omit-empty | INV-005 |

Factory: `text(content, *, continuation=None) -> TextPart`.

### ThinkingPart

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"thinking"` | — | `"thinking"` | always | discriminator |
| `text` | string | shape | — (required arg) | always (even `""`) | empty allowed (INV-015) |
| `redacted` | boolean | no | `false` | omit-default (only when `true`) | exactly bool |
| `continuation` | array | no | `[]` | omit-empty | INV-005 |

Factory: `thinking(content, *, redacted=False, continuation=None)`.

### RefusalPart

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"refusal"` | — | `"refusal"` | always | discriminator |
| `text` | string | yes | — | always | NON-empty (INV-016) |
| `continuation` | array | no | `[]` | omit-empty | INV-005 |

Factory: `refusal(content, *, continuation=None)`.

### CitationPart

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"citation"` | — | `"citation"` | always | discriminator |
| `url` | string | no | `null` | omit-empty | non-empty when present |
| `title` | string | no | `null` | omit-empty | non-empty when present |
| `text` | string | no | `null` | omit-empty | non-empty when present |
| `continuation` | array | no | `[]` | omit-empty | INV-005 |

At least one of `url`/`title`/`text` required (INV-017).
Factory: `citation(*, url=None, title=None, text=None, continuation=None)`.

### ImagePart

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"image"` | — | `"image"` | always | discriminator |
| `media_type` | string | shape | `"image/png"` | always | non-empty (INV-010) |
| `data` | string | one-of | `null` | omit-empty | valid base64 / data-URI (INV-011, INV-012) |
| `url` | string | one-of | `null` | omit-empty | non-empty |
| `file_id` | string | one-of | `null` | omit-empty | non-empty |
| `path` | string (local path) | one-of | `null` | omit-empty | `pathlib.Path` in memory, string on the wire; str input coerced (INV-009) |
| `detail` | string | no | `null` | omit-empty | one of `low`/`high`/`auto` |
| `continuation` | array | no | `[]` | omit-empty | INV-005 |

Exactly one of `data`/`url`/`file_id`/`path` (INV-011).
Factory: `image(*, url=None, data=None, path=None, file_id=None, media_type=None, detail=None, continuation=None)` — bytes `data` is base64-encoded; `path` infers `media_type` via mimetypes; default media type fills when unresolved.

### AudioPart

Same fields/constraints as ImagePart minus `detail`; `type: "audio"`,
default `media_type` `"audio/wav"`.

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"audio"` | — | `"audio"` | always |
| `media_type` | string | shape | `"audio/wav"` | always |
| `data` | string | one-of | `null` | omit-empty |
| `url` | string | one-of | `null` | omit-empty |
| `file_id` | string | one-of | `null` | omit-empty |
| `path` | string | one-of | `null` | omit-empty |
| `continuation` | array | no | `[]` | omit-empty |

Factory: `audio(...)` (same signature family as `image` minus `detail`).

### VideoPart

As AudioPart with `type: "video"`, default `media_type` `"video/mp4"`.

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"video"` | — | `"video"` | always |
| `media_type` | string | shape | `"video/mp4"` | always |
| `data` | string | one-of | `null` | omit-empty |
| `url` | string | one-of | `null` | omit-empty |
| `file_id` | string | one-of | `null` | omit-empty |
| `path` | string | one-of | `null` | omit-empty |
| `continuation` | array | no | `[]` | omit-empty |

Factory: `video(...)`.

### DocumentPart

As AudioPart with `type: "document"`, default `media_type`
`"application/pdf"`.

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"document"` | — | `"document"` | always |
| `media_type` | string | shape | `"application/pdf"` | always |
| `data` | string | one-of | `null` | omit-empty |
| `url` | string | one-of | `null` | omit-empty |
| `file_id` | string | one-of | `null` | omit-empty |
| `path` | string | one-of | `null` | omit-empty |
| `continuation` | array | no | `[]` | omit-empty |

Factory: `document(...)`.

### BinaryPart

As AudioPart with `type: "binary"`, default `media_type`
`"application/octet-stream"`.

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"binary"` | — | `"binary"` | always |
| `media_type` | string | shape | `"application/octet-stream"` | always |
| `data` | string | one-of | `null` | omit-empty |
| `url` | string | one-of | `null` | omit-empty |
| `file_id` | string | one-of | `null` | omit-empty |
| `path` | string | one-of | `null` | omit-empty |
| `continuation` | array | no | `[]` | omit-empty |

Factory: `binary(...)`.

### ToolCallPart

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"tool_call"` | — | `"tool_call"` | always | discriminator |
| `id` | string | yes | — | always | non-empty |
| `name` | string | yes | — | always | non-empty |
| `input` | object (opaque) | yes | — | always (even `{}`) | strict JSON object (INV-002); named `input` everywhere, never `arguments` |
| `continuation` | array | no | `[]` | omit-empty | INV-005 |

Factory: `tool_call(id, name, input, *, continuation=None)`.

### ToolResultPart

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"tool_result"` | — | `"tool_result"` | always | discriminator |
| `id` | string | yes | — | always | non-empty |
| `content` | array of Part | yes | — | always (`[]` if ever empty) | non-empty; presentational parts only (INV-013, INV-014) |
| `name` | string | no | `null` | omit-empty | non-empty when present |
| `is_error` | boolean | no | `false` | omit-default (only when `true`) | exactly bool |
| `continuation` | array | no | `[]` | omit-empty | INV-005 |

Factory: `tool_result(id, content, *, name=None, is_error=False, continuation=None)` — `content` accepts a string, a single part, or a sequence (INV-021).

## Messages

### Message

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `role` | string (Role) | yes | — | always | closed vocabulary |
| `parts` | array of Part | yes | — | always | non-empty; role/part compatibility (INV-022..024); bare Part coerced to 1-tuple (INV-020) |
| `continuation` | array | no | `[]` | omit-empty | INV-005 |

Factories (each normalizes strings to TextPart, single part to tuple —
INV-021):

- `Message.user(content)` — prompt parts only.
- `Message.developer(content)` — prompt parts only; high-authority
  instructions; providers without a native developer role receive a prefixed
  user message (adapter concern).
- `Message.assistant(content)` — assistant parts (no ToolResultPart).
- `Message.tool(results)` — a ToolResultPart, a sequence of them, or a dict
  `{call_id: output}` where output is str/Part/list (INV-025).

Convenience: `parts_of(cls)`, `first(cls)`, `.text` (non-`null` only when
ALL parts are TextPart, joined with `\n`).

## ContinuationState

### ContinuationState

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `provider` | string | yes | — | always | non-empty |
| `kind` | string | yes | — | always | non-empty (open string namespace, NOT a closed vocabulary) |
| `data` | object (opaque) | no | `{}` | always | strict JSON object, required (may be empty) |

Helper: `continuation_data(value, provider, kind)` returns the first
matching state's `data` from a Message/Part/tuple.

## Deltas

All deltas carry `part_index` (JSON int, default `0`, `>= 0`, float-coerced
per the Number rule — INV-007). `delta_to_dict` drops only `null` fields —
empty strings ARE emitted, and `part_index` is always emitted (exception:
`ContinuationDelta.part_index` is `null`-able and omitted when `null`).

### TextDelta

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"text"` | — | `"text"` | always |
| `text` | string | yes | — | always (even `""`) |
| `part_index` | int | no | `0` | always |
| `logprobs` | array of TokenLogprob | no | `[]` | omit-empty |

`logprobs` carries the token logprobs for exactly the tokens in this
fragment, when requested via `Config.logprobs` and streamed per chunk by
the provider (verified live for OpenAI Responses 2026-09-01).
Materialization concatenates fragment logprobs in arrival order into
`Response.logprobs`.

### ThinkingDelta

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"thinking"` | — | `"thinking"` | always |
| `text` | string | yes | — | always (even `""`) |
| `part_index` | int | no | `0` | always |

### AudioDelta

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"audio"` | — | `"audio"` | always | |
| `data` | string | no | `null` | omit-null | may be UNALIGNED partial base64 (chunk, not final media) |
| `url` | string | no | `null` | omit-null | at most one of data/url/file_id (INV-018) |
| `file_id` | string | no | `null` | omit-null | |
| `part_index` | int | no | `0` | always | `>= 0` |
| `media_type` | string | no | `null` | omit-null | non-empty when present |

### ImageDelta

Same shape as AudioDelta with `type: "image"`.

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"image"` | — | `"image"` | always |
| `data` | string | no | `null` | omit-null |
| `url` | string | no | `null` | omit-null |
| `file_id` | string | no | `null` | omit-null |
| `part_index` | int | no | `0` | always |
| `media_type` | string | no | `null` | omit-null |

### ToolCallDelta

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"tool_call"` | — | `"tool_call"` | always | |
| `input` | string | yes | — | always (even `""`) | raw JSON-text fragment |
| `part_index` | int | no | `0` | always | `>= 0` |
| `id` | string | no | `null` | omit-null | non-empty when present |
| `name` | string | no | `null` | omit-null | non-empty when present |

### CitationDelta

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"citation"` | — | `"citation"` | always | |
| `text` | string | no | `null` | omit-null | at least one of text/url/title (INV-019) |
| `url` | string | no | `null` | omit-null | |
| `title` | string | no | `null` | omit-null | |
| `part_index` | int | no | `0` | always | `>= 0` |

### ContinuationDelta

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"continuation"` | — | `"continuation"` | always | |
| `provider` | string | yes | — | always | non-empty |
| `kind` | string | yes | — | always | non-empty |
| `data` | object (opaque) | no | `{}` | always | strict JSON object |
| `part_index` | int or null | no | `null` | omit-null | `null` = attaches to the Message; int = attaches to that completed part |

Method: `to_state() -> ContinuationState`.

## Stream events

### StreamStartEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"start"` | — | `"start"` | always |
| `id` | string | no | `null` | omit-empty |
| `model` | string | no | `null` | omit-empty |

### StreamDeltaEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"delta"` | — | `"delta"` | always |
| `delta` | object (Delta) | yes | — | always |

### StreamEndEvent

Exactly one per stream, final (MAP-3, mapping-rules.md).

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"end"` | — | `"end"` | always | |
| `finish_reason` | string (FinishReason) | no | `null` | omit-empty | closed vocabulary |
| `usage` | object (Usage) | no | `null` | omit-empty (also omitted when Usage serializes to `{}`) | |
| `provider_data` | object (opaque) | no | `null` | omit-empty | strict JSON object |

### StreamErrorEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"error"` | — | `"error"` | always |
| `error` | object (ErrorDetail) | yes | — | always |

### ErrorDetail

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `code` | string (ErrorCode) | yes | — | always | closed vocabulary |
| `message` | string | yes | — | omit-empty | empty allowed |
| `provider_code` | string | no | `null` | omit-empty | non-empty when present |

## Tools

### FunctionTool

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"function"` | — | `"function"` | always | discriminator |
| `name` | string | yes | — | always | non-empty |
| `description` | string | no | `null` | omit-empty | |
| `parameters` | object (opaque JSON Schema) | shape | `{"type": "object", "properties": {}}` | always (even `{}`) | strict JSON object, required; opaque payload — an explicit `{}` round-trips verbatim; absent on input deserializes to the default schema (INV-033) |

### BuiltinTool

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"builtin"` | — | `"builtin"` | always | discriminator |
| `name` | string | yes | — | always | non-empty; canonical builtin names (`web_search`, `code_execution`, ...) mapped per adapter |
| `config` | object (opaque) | no | `null` | omit-empty | strict JSON object |

Deserialization dispatch: `"type": "builtin"` → BuiltinTool; anything else
(including absent `type`) → FunctionTool (INV-034).

## Configuration

### ToolChoice

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `mode` | string (ToolChoiceMode) | no | `"auto"` | always (non-empty string) | closed vocabulary |
| `allowed` | array of string | no | `[]` | omit-empty | non-empty names; bare string coerced to 1-tuple (INV-020); must be ⊆ Request.tools names (INV-031) |
| `parallel` | boolean or null | no | `null` | omit-empty | tri-state: `null` = no preference |

`mode="none"` forbids `allowed`/`parallel` (INV-028).
Factory: `ToolChoice.from_tools(allowed, *, mode="auto", parallel=None)` —
accepts Tool objects or names.

**Kind-aware name resolution (2026-09-01).** `allowed` entries may name
tools of either kind; adapters resolve each name against `Request.tools`
(INV-031 guarantees presence, tool names are unique) and emit the
kind-correct wire form, or raise when the wire cannot express it:

- **openai (Responses)**: single name + `mode="required"` →
  `{"type": "function", "name"}` or the hosted-tool form
  `{"type": "web_search_preview"}` (live-captured 2026-09-01); any other
  allowlist (multi-name, or single with `mode="auto"`) →
  `{"type": "allowed_tools", "mode", "tools"}` — mixed kinds supported.
  A single allowed name with `mode="auto"` no longer forces the call.
- **anthropic**: single name + `mode="required"` →
  `{"type": "tool", "name"}` — works for server tools too
  (live-captured 2026-09-01; the API reference is silent). Allowlist
  covering ALL declared tools → plain `any`/`auto` (no restriction).
  Proper-subset allowlists RAISE — the wire cannot express them and
  degrading would let the model call excluded tools.
- **gemini**: function-name allowlists ride `allowedFunctionNames` with
  mode `ANY` (`required`) or `VALIDATED` (`auto` — the doc-required mode;
  `allowedFunctionNames` is illegal under `AUTO`). Builtin names RAISE —
  `googleSearch`/`codeExecution` have no tool_choice form.
- **openai_chat dialect**: function forcing and the nested
  `allowed_tools` form; builtin names RAISE — the dialect wire has no
  hosted-tool tool_choice.

### Reasoning

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `effort` | string (ReasoningEffort) | no | `"off"` | always | closed vocabulary |
| `thinking_budget` | int | no | `null` | omit-empty | `> 0`; float-coerced (INV-007) |
| `total_budget` | int | no | `null` | omit-empty | `> 0`; float-coerced |
| `summary` | string (ReasoningSummary) | no | `null` | omit-empty | closed vocabulary |

`effort="off"` forbids budgets and summary (INV-026). Tri-state at the
Config level: `reasoning` absent = no explicit preference;
`Reasoning(effort="off")` = explicitly off. Property: `is_off`.

### CacheConfig

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `mode` | string (CacheMode) | no | `"auto"` | always | closed vocabulary |
| `retention` | string (CacheRetention) | no | `null` | omit-empty | closed vocabulary |
| `key` | string | no | `null` | omit-empty | |
| `prefix_until_index` | int | no | `null` | omit-empty | `>= 0`; float-coerced |

`mode="off"` forbids `retention`/`key` (INV-027).

### Config

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `max_tokens` | int | no | `null` | omit-empty | `> 0`; float-coerced (INV-007) |
| `temperature` | float | no | `null` | omit-empty | `>= 0`; int-coerced (INV-008) |
| `top_p` | float | no | `null` | omit-empty | in `[0, 1]`; int-coerced |
| `top_k` | int | no | `null` | omit-empty | `> 0`; float-coerced |
| `stop` | array of string | no | `[]` | omit-empty | non-empty strings; bare string coerced to 1-tuple (INV-020) |
| `response_format` | object (opaque) | no | `null` | omit-empty | strict JSON object |
| `tool_choice` | object (ToolChoice) | no | `null` | omit-empty | |
| `reasoning` | object (Reasoning) | no | `null` | omit-empty | |
| `cache` | object (CacheConfig) | no | `null` | omit-empty | |
| `service_tier` | string | no | `null` | omit-empty | non-empty; OPEN namespace — the tier concept is canonical, the value vocabulary provider-owned (OpenAI `default`/`flex`/`priority`/`auto`; Anthropic `auto`/`standard_only`); Gemini RAISES |
| `user_id` | string | no | `null` | omit-empty | non-empty; opaque end-user identifier for abuse attribution — OpenAI `safety_identifier`, openai_chat dialect `user`, Anthropic `metadata.user_id`; Gemini RAISES |
| `store` | bool | no | `null` | omit-empty EXCEPT `false` (false is the opt-out, data not emptiness) | provider-side response storage opt-in/out — OpenAI and Gemini `store` verbatim; Anthropic RAISES |
| `logprobs` | int | no | `null` | omit-empty EXCEPT `0` (0 is data: chosen tokens only) | `>= 0`; float-coerced; `null` = do not request, `0` = chosen-token logprobs only, `n > 0` = also top-n alternatives per position. OpenAI Responses → `top_logprobs` + `include: ["message.output_text.logprobs"]`; openai_chat dialect → `logprobs: true` (+ `top_logprobs` when `n > 0`); Gemini → `responseLogprobs` (+ `logprobs` when `n > 0`, doc-based — every currently served model rejects it live); Anthropic RAISES. Provider caps (currently 0–20) are provider-owned, not encoded |
| `extensions` | object (opaque) | no | `null` | omit-empty | strict JSON object; `{}` normalized to `null` (INV-004) |

An all-default `Config` serializes to `{}` and is omitted from the enclosing
Request entirely. On read, a present non-object `tool_choice`/`reasoning`/
`cache` is malformed canonical JSON and raises `TypeError` (INV-042).

## Request / Response

### Request

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `model` | string | yes | — | always | non-empty |
| `messages` | array of Message | yes | — | always | non-empty; bare Message coerced to 1-tuple (INV-020) |
| `system` | string OR array of prompt Part | no | `null` | omit-empty | non-empty string; no protocol parts (INV-024); strings/parts normalized (INV-021) |
| `tools` | array of Tool | no | `[]` | omit-empty | unique names (INV-030) |
| `config` | object (Config) | no | `Config()` | omit-empty (when `{}`) | tool_choice.allowed ⊆ tool names (INV-031) |

### Usage

All counters are `int | null`; `null` means "not reported by the provider",
distinct from a reported `0`. `Usage()` serializes to `{}` and is omitted by
enclosing serializers.

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `input_tokens` | int | no | `null` | omit-empty | `>= 0`; float-coerced |
| `output_tokens` | int | no | `null` | omit-empty | `>= 0` |
| `total_tokens` | int | no | `null` (auto-computed: see INV-029) | omit-empty | `>= 0`; preserved verbatim when provider-reported |
| `cache_read_tokens` | int | no | `null` | omit-empty | `>= 0` |
| `cache_write_tokens` | int | no | `null` | omit-empty | `>= 0` |
| `reasoning_tokens` | int | no | `null` | omit-empty | `>= 0`; only when the provider reports an EXACT separate count |
| `input_audio_tokens` | int | no | `null` | omit-empty | `>= 0` |
| `output_audio_tokens` | int | no | `null` | omit-empty | `>= 0` |

### Response

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `id` | string | yes (positional, nullable) | — | omit-empty | non-empty when present |
| `model` | string | yes | — | always | non-empty |
| `message` | object (Message) | yes | — | always | role MUST be `assistant`; never empty (MAP-2) |
| `finish_reason` | string (FinishReason) | yes | — | always | closed vocabulary |
| `usage` | object (Usage) | yes | — | omit-empty (when `{}`) | |
| `logprobs` | array of TokenLogprob | no | `null` | omit-empty | `null` = provider did not report (the Usage convention); never `[]` on parse |
| `provider_data` | object (opaque) | no | `null` | never by default (`response_to_dict` emits it only with `include_provider_data=True`; the vet protocol serializes WITHOUT it, surfacing only the `_lm15_unmapped` canary) | strict JSON object |

`logprobs` is decoding telemetry — the same category as `usage` and
`finish_reason`, never re-sent in history. Per-block provider lists
(OpenAI Responses attaches them per `output_text` block) concatenate in
document order; the block boundary survives in the stream
(`TextDelta.part_index`) and in `provider_data`, not here.

Convenience: `.text` (text + citation/thinking treated as metadata),
`.tool_calls`, `.citations`, `.parse_json(default=...)`, `.json`.

### TokenLogprob

The chosen token at one decoding step, with ranked alternatives. Two flat
types instead of one recursive type: the wire never nests alternatives
inside alternatives, and the type system says so.

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `token` | string | yes | — | always (even `""`) | |
| `logprob` | float | yes | — | always (even `0.0`) | float-coerced (int input accepted) |
| `bytes` | array of int | no | `null` | omit-empty | token UTF-8 bytes when reported (OpenAI); each `>= 0` |
| `token_id` | int | no | `null` | omit-empty | vocabulary id when reported (Gemini) |
| `top` | array of TopLogprob | no | `[]` | omit-empty | provider-reported ranked list, descending logprob |

No guarantee the chosen token appears in `top`. Providers also differ on
whether the requested alternative count includes the chosen token (Gemini
documents that it does; OpenAI counts alternatives only) — the reported
list is preserved as-is, never adjusted.

### TopLogprob

One scored alternative token at a decoding step — `TokenLogprob` without
the nested `top`.

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `token` | string | yes | — | always (even `""`) | |
| `logprob` | float | yes | — | always (even `0.0`) | float-coerced |
| `bytes` | array of int | no | `null` | omit-empty | each `>= 0` |
| `token_id` | int | no | `null` | omit-empty | |

## Other endpoints

### FileUploadRequest

Files are an ACCOUNT-scoped resource on every provider — there is no
`model` field. OpenAI's `purpose` storage classification is NOT part of
the portable surface: the reference defaults to `user_data`, sets
`batch` itself for batch inputs, and honors `extensions["purpose"]`.

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `filename` | string | yes | — | always | non-empty |
| `bytes_data` | string (base64 on the wire; raw bytes in memory) | one-of | `null` | omit-empty | non-empty; bytearray coerced to bytes |
| `media_type` | string | no | `"application/octet-stream"` | always (truthy) | non-empty |
| `extensions` | object | no | `null` | omit-empty | `{}` → `null` |
| `path` | string (local path) | one-of | `null` | omit-empty | str coerced to Path (INV-009); lazy read; serialized as a plain string per the media-part precedent (meaningful only where the filesystem is shared) |

Exactly one of `bytes_data`/`path` (INV-011 family).

### FileInfo

The snapshot of one provider-side stored file; replaces the former
`FileUploadResponse` and is returned by upload, get, and list. `id` is
the canonical reference to place in a media Part's `file_id`: OpenAI
and Anthropic file ids verbatim; Gemini the file URI VERBATIM (model
requests address files by URI, not resource name — verified live
2026-08-31; adapters derive the REST resource from the URI).

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `id` | string | yes | — | always | non-empty; provider reference verbatim |
| `filename` | string | no | `null` | omit-empty | non-empty when present |
| `media_type` | string | no | `null` | omit-empty | OpenAI reports no MIME type → `null` |
| `size_bytes` | int | no | `null` | omit-empty | `>= 0`; Gemini's int64-as-string normalized |
| `created_at` | string | no | `null` | omit-empty | ISO-8601 UTC `YYYY-MM-DDTHH:MM:SSZ`, normalized from epoch/ISO forms |
| `expires_at` | string | no | `null` | omit-empty | same normalization; Gemini always (~48h), OpenAI on some purposes, Anthropic when set |
| `readiness` | string (FileReadiness) | no | `"ready"` | always (truthy) | closed vocabulary |
| `downloadable` | bool | no | `null` | omit-empty EXCEPT `false` (false is data, not emptiness) | tri-state: provider-stated capability or `null` when unreported |
| `provider_data` | object (opaque) | no | `null` | omit-empty | raw file object verbatim |

Convenience: `.ready` (`readiness == "ready"`).

### FilePage

One page of stored files. Listing is a CORE operation (the provider is
the system of record; a lost id is recovered by listing). `next_cursor`
is provider-issued and opaque (OpenAI `last_id` when `has_more`;
Anthropic `next_page` token; Gemini `nextPageToken`); pass it back to
`file_list`, `null` means the listing is complete.

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `items` | array of FileInfo | no | `[]` | omit-empty | |
| `next_cursor` | string | no | `null` | omit-empty | non-empty when present; opaque |

### BatchRequest

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `model` | string | no | `null` → inferred from `requests[0].model` (INV-032) | always after inference | routing convenience only |
| `requests` | array of Request | yes | `[]` (but empty rejected) | always | non-empty |
| `label` | string | no | `null` | omit-empty | non-empty when present; providers without a wire label field REJECT labeled submits (no silent drop) |
| `extensions` | object (opaque) | no | `null` | omit-empty | |

### BatchJobInfo

The ticket: a snapshot of one provider-side batch job. `id` is a plain
string — store it anywhere; enumerability (`batch_list`) is the recovery
path for a lost id, never client-side care.

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `id` | string | yes | — | always | non-empty; the provider's job identifier verbatim |
| `status` | string (BatchStatus) | yes | — | always | closed vocabulary |
| `label` | string | no | `null` | omit-empty | non-empty when present |
| `created_at` | string | no | `null` | omit-empty | ISO-8601 UTC `YYYY-MM-DDTHH:MM:SSZ`, normalized from the provider's epoch/ISO form |
| `provider_data` | object (opaque) | no | `null` | omit-empty | raw job object verbatim |

### BatchEntry

The fate of one request, in submission order. Partial failure is a
first-class outcome: a `completed` job may mix `succeeded` and `errored`
entries. Implementations re-sort provider results so entry order always
equals submission order (providers return results out of order —
observed live, Anthropic, 2026-08-31).

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `index` | int | yes | — | always | non-negative; submission position |
| `outcome` | string (BatchOutcome) | yes | — | always | closed vocabulary |
| `response` | object (Response) | outcome-dependent | `null` | omit-empty | required iff `outcome="succeeded"`; parsed by the frozen chat response mapping |
| `error` | object (ErrorDetail) | outcome-dependent | `null` | omit-empty | required iff `outcome="errored"`; `cancelled`/`expired` carry neither |

### ImageGenerationRequest

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `model` | string | yes | — | always | non-empty |
| `prompt` | string | yes | — | always | non-empty |
| `size` | string | no | `null` | omit-empty | non-empty when present; provider's own sizing vocabulary (OpenAI pixels, Gemini aspect ratios); raises where no wire slot exists (xAI) |
| `images` | array of ImagePart | no | `()` | omit-empty | input images for edits; any Part addressing mode; adapters route to the provider's edit door and raise where none exists |
| `extensions` | object (opaque) | no | `null` | omit-empty | |

### ImageGenerationResponse

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `images` | array of ImagePart | yes | — | always | non-empty; `media_type` from the wire, never assumed |
| `text` | string | no | `null` | omit-empty | narration returned next to images (Gemini); never fabricated |
| `id` | string | no | `null` | omit-empty | non-empty when present |
| `model` | string | no | `null` | omit-empty | non-empty when present |
| `usage` | object (Usage) | no | `Usage()` | omit-empty | |
| `provider_data` | object (opaque) | no | `null` | omit-empty | |

### SpeechGenerationRequest

Renamed from `AudioGenerationRequest` (2026-09-01): both wires that
implement the endpoint sell text-to-speech and nothing more; "audio
generation" promised music and sound effects no wire offers.  Omitted
`voice`/`format` mean the SERVER's defaults — the reference
implementation injects none of its own.  `format` raises on providers
whose wire has no slot for it (Gemini: always PCM).

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `model` | string | yes | — | always | non-empty |
| `prompt` | string | yes | — | always | non-empty |
| `voice` | string | no | `null` | omit-empty | non-empty when present; provider's own voice vocabulary |
| `format` | string | no | `null` | omit-empty | non-empty when present; raises where no wire slot exists |
| `extensions` | object (opaque) | no | `null` | omit-empty | |

### SpeechGenerationResponse

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `audio` | object (AudioPart) | yes | — | always | `media_type` from the wire verbatim, including parameterized MIME (`audio/L16;codec=pcm;rate=24000`) |
| `id` | string | no | `null` | omit-empty | |
| `model` | string | no | `null` | omit-empty | |
| `usage` | object (Usage) | no | `Usage()` | omit-empty | |
| `provider_data` | object (opaque) | no | `null` | omit-empty | |

### VideoGenerationRequest

Video is job-shaped on every wire that sells it (Sora, Veo,
grok-imagine): submission returns a ticket (`VideoJobInfo`), not bytes.

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `model` | string | yes | — | always | non-empty |
| `prompt` | string | yes | — | always | non-empty |
| `seconds` | int | no | `null` | omit-empty | `> 0`; maps Sora `seconds` (string enum) and Veo `durationSeconds`; raises where no wire slot exists (xAI) |
| `images` | array of ImagePart | no | `()` | omit-empty | input frames (image-to-video); raises until the provider mapping is live-receipted |
| `extensions` | object (opaque) | no | `null` | omit-empty | |

### VideoJobInfo

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `id` | string | yes | — | always | non-empty; the ticket (on xAI the only copy — no list endpoint) |
| `status` | string (VideoStatus) | yes | — | always | closed vocabulary: `queued`/`running`/`completed`/`failed`/`cancelled`; provider wire words stay in provider_data |
| `progress` | int | no | `null` | omit-empty | 0–100 when the provider reports one |
| `created_at` | string | no | `null` | omit-empty | ISO-8601 UTC normalized |
| `model` | string | no | `null` | omit-empty | |
| `provider_data` | object (opaque) | no | `null` | omit-empty | verbatim job state |

The result of a completed job is a `VideoPart` in the provider's own
delivery mode: bytes for Sora (content endpoint) and Veo (the file URI
is key-bound — 403 without the header, verified live), a public URL for
xAI.

## Audio / Live (realtime)

### AudioFormat

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `encoding` | string (AudioEncoding) | yes | — | always | closed vocabulary |
| `sample_rate` | int | yes | — | always | `> 0`; float-coerced |
| `channels` | int | no | `1` | always (truthy int) | `> 0`; float-coerced |

### LiveConfig

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `model` | string | yes | — | always | non-empty |
| `system` | string OR array of prompt Part | no | `null` | omit-empty | as Request.system |
| `tools` | array of Tool | no | `[]` | omit-empty | unique names |
| `voice` | string | no | `null` | omit-empty | non-empty when present |
| `input_format` | object (AudioFormat) | no | `null` | omit-empty | |
| `output_format` | object (AudioFormat) | no | `null` | omit-empty | |
| `extensions` | object (opaque) | no | `null` | omit-empty | |

### LiveClientTurnEvent

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"turn"` | — | `"turn"` | always | |
| `parts` | array of prompt Part | yes | — | always | non-empty; no protocol parts; bare Part coerced |
| `turn_complete` | boolean | no | `true` | always (even `false`) | exactly bool |

### LiveClientAudioEvent

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"audio"` | — | `"audio"` | always | |
| `data` | string | yes | — | always | non-empty valid base64 |
| `media_type` | string | no | `"audio/pcm;rate=16000"` | always | must start with `audio/` |

### LiveClientImageEvent

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"image"` | — | `"image"` | always | |
| `data` | string | yes | — | always | non-empty valid base64 |
| `media_type` | string | no | `"image/jpeg"` | always | must start with `image/` |

### LiveClientTextEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"text"` | — | `"text"` | always |
| `text` | string | yes | — | always (even `""`) |

### LiveClientToolResultEvent

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"tool_result"` | — | `"tool_result"` | always | |
| `id` | string | yes | — | always | non-empty |
| `content` | array of Part | yes | — | always | non-empty; presentational parts only (as ToolResultPart) |

### LiveClientInterruptEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"interrupt"` | — | `"interrupt"` | always |

### LiveClientEndAudioEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"end_audio"` | — | `"end_audio"` | always |

### LiveServerAudioEvent

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"audio"` | — | `"audio"` | always | |
| `data` | string | yes | — | always | non-empty valid base64 |
| `media_type` | string | no | `null` | omit-empty | starts with `audio/` when present |

### LiveServerTextEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"text"` | — | `"text"` | always |
| `text` | string | yes | — | always (even `""`) |

### LiveServerToolCallEvent

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"tool_call"` | — | `"tool_call"` | always | |
| `id` | string | yes | — | always | non-empty |
| `name` | string | yes | — | always | non-empty |
| `input` | object (opaque) | yes | — | always (even `{}`) | strict JSON object |

### LiveServerToolCallDeltaEvent

| Field | JSON type | Req | Default | Omission | Constraints |
|---|---|---|---|---|---|
| `type` | string `"tool_call_delta"` | — | `"tool_call_delta"` | always | |
| `input_delta` | string | yes | — | omit-empty | empty allowed |
| `id` | string | no | `null` | omit-empty | non-empty when present |
| `name` | string | no | `null` | omit-empty | non-empty when present |

### LiveServerInterruptedEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"interrupted"` | — | `"interrupted"` | always |

### LiveServerTurnEndEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"turn_end"` | — | `"turn_end"` | always |
| `usage` | object (Usage) | yes | — | omit-empty (when `{}`) |

### LiveServerErrorEvent

| Field | JSON type | Req | Default | Omission |
|---|---|---|---|---|
| `type` | string `"error"` | — | `"error"` | always |
| `error` | object (ErrorDetail) | yes | — | always |

## Callback view

### ToolCallInfo

In-memory callback payload — same identity/input shape as ToolCallPart
without the `type` discriminator; no canonical JSON serializer.

| Field | JSON type | Req | Default | Constraints |
|---|---|---|---|---|
| `id` | string | yes | — | non-empty |
| `name` | string | yes | — | non-empty |
| `input` | object (opaque) | yes | — | strict JSON object |

Factories: `ToolCallInfo.from_part(part)`, `to_part()`.

---

Status: RATIFIED — Maxime Rivest, 2026-06-11 (session assent, transcribed; canonical-facts authority now includes spec/ per AUTHORITY.md).
Amended 2026-06-11 by maintainer delegation: FunctionTool.parameters is
required-with-shape (INV-033 resolution); Config read-side nest rule noted
(INV-042 resolution). See changes/2026-06-11-inv033-parameters-always-emitted.md
and changes/2026-06-11-inv042-config-nests-reject.md.
