# lm15 vet protocol

Every lm15 implementation ships one entrypoint (the "vet shim") speaking
newline-delimited JSON on stdin/stdout. The harness in this repository drives
shims as subprocesses and performs ALL comparison itself — shims only
transform. A shim must never touch the network: the harness runs it inside a
no-network sandbox, and any connection attempt is a hard failure.

Entrypoints:

| Language | Command |
|---|---|
| Python (reference) | `python -m lm15.vet` (cwd: lm15-python2) |
| Rust | `cargo run --quiet --bin lm15-vet` |
| Go | `go run ./cmd/lm15-vet` |
| TypeScript | `node dist/vet.js` |
| Julia | `julia bin/vet.jl` |

## Framing

One JSON object per line on stdin; one JSON object per line on stdout, same
order, one output per input. On EOF, exit 0. A shim crash mid-stream is a
harness error for the remaining ops.

Request: `{"op": <string>, "id": <string>, ...op-specific fields}`
Success: `{"id": <string>, "ok": true, "result": {...}}`
Failure: `{"id": <string>, "ok": false, "error": {"type": <string>, "message": <string>}}`

`ok: false` is a *result*, not a protocol failure — reject vectors expect it.
The `error.type` for lm15-typed errors is the canonical error class name
(e.g. `InvalidRequestError`); for unexpected exceptions, the native exception
name.

## Ops

All canonical JSON uses the canonical serde forms (see
`lm15-python2/docs/serde-rules.md`): one omission rule, opaque payloads
verbatim.

### capabilities
In: `{}` → Out: `{"language": str, "ops": [str], "impl_version": str}`

### build_request
In: `{"provider": "openai"|"openai_chat"|"anthropic"|"gemini", "canonical_request": <Request JSON>, "stream": bool, "api_key": str, "base_url"?: str}`
Out: `{"method": str, "url": str, "params": {str: str}, "headers": {str: str}, "body": <JSON|null>}`
- `url` carries no query string — query params go in `params`.
- Header names lowercased; values VERBATIM (the harness asserts exact auth
  formatting against the provided `api_key`, e.g. `Bearer test-key-123`).
- The shim must construct the adapter with the given `api_key` and must not
  read environment keys.

`base_url` (additive, optional, 2026-06-10): when present on `build_request`,
`parse_response`, `replay_stream`, or `normalize_error`, the shim MUST
construct the adapter against that base URL instead of the provider's
default. This exists for dialect adapters that speak to many servers —
provider `openai_chat` (OpenAI Chat Completions dialect: OpenAI, ollama,
Groq, OpenRouter, vLLM, SGLang, …) — where the case fixture pins the server
it was captured against. The harness forwards a case's top-level
`"base_url"` field verbatim on every op; absence means the adapter default.
Shims that predate this field treat unknown fields per JSON convention
(ignore), so the addition is backward compatible only for cases that do not
declare it — cases that DO declare `base_url` require a shim that honors it.

### parse_response
In: `{"provider": str, "canonical_request": <Request JSON>, "status": int, "body_b64": str}`
Out: `{"canonical_response": <Response JSON>}`
- Response serialized WITHOUT provider_data, except the `_lm15_unmapped`
  canary: if the parser recorded unmapped fields, include them as
  `{"canonical_response": ..., "unmapped": [...]}` — the harness fails any
  case with a non-empty `unmapped`.

### replay_stream
In: `{"provider": str, "canonical_request": <Request JSON>, "body_b64": str}`
Out: `{"events": [<StreamEvent JSON>], "canonical_response": <Response JSON>}`
- `events` is the full canonical event trace, in order, serialized with the
  canonical stream-event serde. `canonical_response` is the materialized
  final Response (same rules as parse_response).

### normalize_error
In: `{"provider": str, "status": int, "body_text": str}`
Out: `{"class": str, "code": str, "provider_code": str|null, "message": str}`
- `class` is the canonical lm15 error class name; `code` the canonical
  ErrorCode literal.

### serde_roundtrip
In: `{"kind": str, "value": <JSON>}`  (kinds as in serde KIND_SERDE)
Out: `{"value": <JSON>}` — `to_dict(from_dict(value))`, NO cleaning, no
normalization. The harness does strict comparison; the shim must not "help".

### validate
In: `{"kind": str, "value": <JSON>}`
Out: `{"ok": true}` if accepted, else `ok: false` with the canonical error
type — used by reject vectors (invalid input MUST be rejected) and accept
vectors (sloppy input MUST normalize to an exact expected output, returned as
`{"ok": true, "normalized": <JSON>}`).

### surface_dump
In: `{}`
Out: `{"types": {<TypeName>: {"fields": [str]}}, "enums": {<EnumName>: [str]}}`
- MUST be produced by reflection (e.g. dataclasses.fields), never a
  hand-maintained list — this feeds the coverage ratchet.

## Comparison semantics (harness-side)

- Strict typed deep-equality. `true != 1`, `1 != 1.0` (exception: a float
  with zero fractional part compares equal to the same-valued int ONLY in
  `usage` token fields, normalized at the harness boundary — JS/Julia JSON
  emitters; scope fixed, never widened).
- Absent, null, `""`, `[]`, `{}` are FIVE DIFFERENT VALUES everywhere.
- Volatile paths: a case may declare `"volatile": {"<json-path>": "<class>"}`
  with classes `id`, `timestamp`, `usage-count`, `duration`. Volatile paths
  compare by presence + type only. The audit lints volatile maps: text
  content, tool names, and tool inputs may NEVER be volatile; max 6 volatile
  paths per case.
- Auth header values are compared EXACTLY against the api_key the harness
  injected (never redacted on the shim side).

## Concurrency

The contract pins pure transformations (build/parse/map). Concurrency and
transport surface are per-language idiom and are OUT of contract scope:
Python ships sync + mirror Async* classes; Go uses context; TypeScript is
async-only; Julia uses tasks. Ports MUST share the pure core across their
concurrency surfaces so conformance covers all of them.
