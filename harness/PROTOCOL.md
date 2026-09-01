# lm15 vet protocol

Every lm15 implementation ships one entrypoint (the "vet shim") speaking
newline-delimited JSON on stdin/stdout. The harness in this repository drives
shims as subprocesses and performs ALL comparison itself — shims only
transform. A shim must never touch the network: the harness runs it inside a
no-network sandbox, and any connection attempt is a hard failure.

Entrypoints:

| Language | Command |
|---|---|
| Python (reference) | `python -m lm15.vet` (cwd: lm15-python) |
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
`lm15-python/docs/serde-rules.md`): one omission rule, opaque payloads
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
In: `{"kind": str, "value": <JSON>}`  (kinds enumerated in "Serde kinds" below)
Out: `{"value": <JSON>}` — `to_dict(from_dict(value))`, NO cleaning, no
normalization. The harness does strict comparison; the shim must not "help".

### validate
In: `{"kind": str, "value": <JSON>}`
Out: on acceptance, `{"ok": true, "normalized": <JSON>}` — `normalized` is
ALWAYS present on `ok: true` (verified against the reference shim:
`lm15.vet.op_validate` unconditionally returns
`{"ok": True, "normalized": to_dict(obj)}`). On rejection, `ok: false` with
the canonical error type. Used by reject vectors (invalid input MUST be
rejected) and accept vectors (sloppy input MUST normalize to an exact
expected output, compared against `normalized`).

### surface_dump
In: `{}`
Out: `{"types": {<TypeName>: {"fields": [str]}}, "enums": {<EnumName>: [str]}}`
- MUST be produced by reflection (e.g. dataclasses.fields), never a
  hand-maintained list — this feeds the coverage ratchet.

### explain_auth
In: `{"provider": str, "sentinel": str, "env": {str: str}, "api_keys_providers": [str], "credentials_path"?: str}`
Out: `{"configured": bool, "steps": [{"kind": str, "state": str}], "report_text": str}`
- Drives the AUTH-7 explain surface over the AUTH-1 chain
  (`auth/resolution.json`; spec/auth.md). The harness owns EVERY input:
  - `env` is the complete environment for resolution. It is always present
    (possibly empty); the shim must never consult its real process
    environment or real home-directory credential stores.
  - `api_keys_providers` lists providers for which an explicit api_keys
    entry exists; the shim plants `sentinel` as each entry's value.
  - `credentials_path`, when present, is a harness-materialized borrowed
    OAuth credential file (or a deliberately nonexistent path). The harness
    writes the file — never the shim — in the AUTH-8 wire format, with the
    sentinel as every secret value.
- `steps` carries the language-neutral `kind` vocabulary of the fixture
  (`api_keys`, `env:<VAR>`, `placeholder`, `oauth-file`) and the AUTH-7
  states (`selected`, `shadowed`, `absent`), in chain order.
- `report_text` is the implementation's full human rendering of the report
  (every rendered surface concatenated). It must be a non-empty string: the
  harness enforces AUTH-5 by asserting the sentinel appears nowhere in the
  ENTIRE reply, and an empty rendering would give that check nothing to
  inspect.
- The op performs no network I/O and no writes; reading the harness-given
  `credentials_path` is the only file access.

### build_models_request
In: `{"provider": str, "api_key": str, "base_url"?: str}`
Out: same shape as `build_request` (`method`/`url`/`params`/`headers`/`body`)
- The wire GET request for the provider's model catalog (the `models`
  direction; mapping table in
  `changes/2026-08-31-list-models-provisional.md`). `body` is null.
- Subscription dialects are constructible with the injected key: for
  provider `openai-codex` the shim MUST construct the adapter with account
  id `test-account` (the ctor cannot derive one from a non-JWT key, and the
  `chatgpt-account-id` header is compared verbatim); for `claude-code` the
  injected key stands in for the OAuth access token.

### parse_models_response
In: `{"provider": str, "status": int, "body_b64": str, "base_url"?: str}`
Out: `{"models": [<ModelInfo JSON>]}`
- Canonical `model_info` serde, INCLUDING `origin.provider_data` (unlike
  parse_response): the listing mapping embeds each wire entry verbatim, and
  the harness verifies that mechanically — the returned `provider_data`
  values must be an order-preserving subsequence of the pinned body's
  entries under the case's `entries_key` (entries without a usable id are
  skipped, never invented). For the golden comparison the harness strips
  `origin.provider_data` and drops an origin left as exactly
  `{"type": "provider"}` (mirroring the serde collapse); goldens pin the
  mapped surface only.
- A `status >= 400` input must surface the adapter's normalized error as an
  `ok: false` reply.

### replay_live
In: `{"provider": "openai"|"gemini", "live_config": <LiveConfig JSON>, "client_events": [<LiveClientEvent JSON>], "server_frames_b64": [str], "base_url"?: str}`
Out: `{"setup_frames": [<wire JSON>], "client_frames": [[<wire JSON>]], "events": [[<LiveServerEvent JSON>]]}`
- Recorded-transcript replay of the live websocket CODEC — three pure
  transformations, no socket:
  - `setup_frames`: the frames the implementation would send at connect
    time for this LiveConfig, in send order (OpenAI: the GA
    `session.update`; Gemini: the `setup` frame).
  - `client_frames`: one wire-frame LIST per canonical client event, in
    order — the grouping is contract (e.g. OpenAI `end_audio` →
    `input_audio_buffer.commit` + `response.create`).
  - `events`: one canonical-event LIST per server frame (decoded from the
    verbatim recorded bytes), in order. An EMPTY list is a real assertion:
    this housekeeping frame is deliberately ignored (e.g. Gemini
    `setupComplete`, OpenAI `conversation.item.added`, the benign
    `response_cancel_not_active` barge-in race error).
- Wire frames are compared as parsed JSON (key order and whitespace
  irrelevant), the same standard as request bodies. Server frame input is
  b64 for byte fidelity; text frames are utf-8.
- Session mechanics — locking, pending queues, iteration, `turn()` sugar,
  reconnection — are per-language idiom, OUT of contract scope. The codec
  (config → setup, client event → frames, frame → events) IS the contract.
- Live cases carry `surface: "live"`, a canonical `live_config`, and a
  `pinned_body` transcript (JSONL of directed entries:
  `{"dir":"client","kind":"setup"|"event",...}` with recorded frames, and
  `{"dir":"server","frame"|"frame_b64":...}` verbatim). Goldens pin the
  canonical decode (`{"events": [[...]]}`) only; setup/encode expectations
  come from the transcript itself (wire truth).

### file_op_build
In: `{"provider": str, "file_op": "upload"|"get"|"list"|"delete"|"download", "api_key": str, "upload_request"?: <FileUploadRequest JSON>, "file_id"?: str, "limit"?: int, "cursor"?: str|null, "base_url"?: str}`
Out: the wire request, `build_request`-shaped.
- One op per files-lifecycle wire request, discriminated by `file_op` —
  the same seam as the reference implementation's pure build hooks.
  `upload` takes the canonical FileUploadRequest (bytes as base64);
  `get`/`delete`/`download` take `file_id`; `list` takes `limit` and an
  optional opaque `cursor`.

### file_op_parse
In: `{"provider": str, "kind": "info"|"page", "status": int, "body_b64": str, "base_url"?: str}`
Out: `{"file": <FileInfo JSON>}` or `{"page": <FilePage JSON>}`.
- Canonical snapshot from a pinned wire body. A `status >= 400` raises
  through the provider's error normalization (typed error out).

### batch_op_build
In: `{"provider": str, "action": "upload"|"submit"|"status"|"cancel"|"list"|"result_fetches", "api_key": str, "batch_request"?: <BatchRequest JSON>, "batch_id"?: str, "limit"?: int, "upload_body"?: <JSON>, "status_body"?: <JSON>, "base_url"?: str}`
Out: `{"requests": [<wire request>...]}`.
- ALWAYS a list: `upload` is zero requests on single-step providers
  (Anthropic, Gemini) and one (the JSONL multipart) on OpenAI;
  `result_fetches` is zero on Gemini (results are inlined in the
  terminal operation) and one-or-more on OpenAI (output + error files).
  `submit` receives the parsed `upload_body` when an upload step
  preceded it (OpenAI's file object), else null/absent.

### batch_op_parse
In: `{"provider": str, "kind": "job"|"list"|"entries", "status"?: int, "body_b64"?: str, "status_body"?: <JSON>, "fetched_b64"?: [str], "base_url"?: str}`
Out: `{"job": <BatchJobInfo JSON>}`, `{"jobs": [...]}`, or `{"entries": [<BatchEntry JSON>...]}`.
- `entries` takes the terminal status body plus the fetched result texts
  and returns entries in SUBMISSION order — re-sorting is contract
  (Anthropic returned results out of order in live capture 2026-08-31).
  Statuses are the canonical vocabulary, never provider wire words.

### generation_build
In: `{"provider": str, "kind": "image"|"speech", "api_key": str, "generation_request": <ImageGenerationRequest|SpeechGenerationRequest JSON>, "base_url"?: str}`
Out: the wire request, `build_request`-shaped.
- Image requests with input `images` must route to the provider's real
  edit door (OpenAI `/images/edits` multipart; Gemini the same chat
  call; xAI `/images/edits` with `image:{url|file_id}`) — never to an
  endpoint that silently ignores them. Fields with no wire slot raise
  (Gemini speech `format`, xAI `size`, >1 input image on xAI).

### generation_parse
In: `{"provider": str, "kind": "image"|"speech", "generation_request": <JSON>, "status": int, "headers"?: {str: str}, "body_b64": str, "base_url"?: str}`
Out: `<ImageGenerationResponse|SpeechGenerationResponse JSON>`.
- `headers` matter: OpenAI speech bodies are raw media bytes whose
  media type exists only in the `content-type` header. Media types come
  from the wire verbatim (parameterized MIME included); `provider_data`
  must be present (the harness asserts presence, then strips it before
  golden comparison, digesting media payloads >= 512 chars as
  `sha256:<hex>` on both sides).
- Endpoint-surface cases carry `surface: "files"|"batch"|"generation"`.
  Files/batch cases hold a `steps` list (each step pins its wire
  request block and optional pinned body + golden key); generation
  cases hold one `generation_request`/`request`/`pinned_body` triple.
  Multipart wire bodies compare with the boundary token normalized to
  `BOUNDARY` on both sides — the boundary is the only legitimately
  random byte.

## Serde kinds

The closed set of `kind` strings for `serde_roundtrip` and `validate`
(normative enumeration; the reference's `lm15.vet.KIND_SERDE` table must
match this list, not the other way around). An unknown kind is an
`ok: false` ValueError.

`part`, `message`, `tool`, `tool_choice`, `reasoning`, `config`,
`cache_config`, `continuation_state`, `error_detail`, `delta`, `usage`,
`stream_event`, `request`, `response`, `model_info`, `audio_format`,
`live_config`, `live_client_event`, `live_server_event`,
`batch_request`, `batch_job`, `batch_entry`,
`file_upload_request`, `file_info`, `file_page`

Adding a kind is an additive spec change requiring a `changes/` entry.

## Unmapped recorder (`_lm15_unmapped`)

What "an unmapped field" means, derived from the reference `_record_unmapped`
call sites (openai.py, openai_chat.py, anthropic.py, gemini.py):

- **What counts as unmapped:** a provider RESPONSE CONTENT element the
  adapter could not map to any canonical part or value. Concretely, the
  inspected paths are the provider's content containers and terminal values:
  - openai (Responses API): `output[i]` items and
    `output[i].content[j]` entries of unknown type/shape;
  - openai_chat: `choices[0]` (non-object), `choices[0].message.content`
    array entries and non-string/non-array content,
    `choices[0].message.tool_calls[i]` of unknown type, and
    `choices[0].finish_reason` values outside the known map;
  - anthropic: `content[i]` blocks of unknown type/shape;
  - gemini: `candidates[0].content.parts[i]` entries with no recognized
    key (the recorded type is the `+`-joined sorted key set, or `<empty>`).

  Request-side passthrough (`extensions`) and known-but-ignored metadata are
  NOT unmapped; only response content the user would silently lose is.
- **Element shape:** each entry is exactly
  `{"path": <str>, "type": <str>}` — `path` is a JSON-path-like string
  relative to the provider response body root (object keys dotted, array
  indices bracketed, e.g. `output[2].content[0]`); `type` is the provider's
  discriminator string (or the value itself for `finish_reason`, or a
  native type name for shape failures), stringified, with falsy values
  recorded as `"<missing>"`.
- **Transport:** the recorder list is attached to
  `Response.provider_data["_lm15_unmapped"]` only when non-empty. The shim's
  `parse_response`/`replay_stream` surface it as the top-level `"unmapped"`
  array (the rest of provider_data is not serialized), and the harness fails
  any case with a non-empty `unmapped`.

## Volatile path syntax

A case's `"volatile"` map keys are JSON paths matched EXACTLY (string
equality, no wildcards, no slicing) against the harness's rendered diff
path. The grammar accepted by `harness/check.py::_volatile_class`:

- Rendered form: `$` is the comparison root; object keys append `.<key>`;
  array indices append `[<int>]`. Example:
  `$.canonical_response.message.parts[0].id`.
- The `$.` prefix is OPTIONAL in case files: `a.b[0]` and `$.a.b[0]` match
  the same path.
- For response/stream directions, the `canonical_response.` root segment is
  also optional: `message.parts[0].id` matches
  `$.canonical_response.message.parts[0].id`.
- Keys containing dots or brackets are not escapable — such paths cannot be
  declared volatile (no canonical field needs them).
- The class value must be one of `id`, `timestamp`, `usage-count`,
  `duration`; a key with an unknown class does NOT match (the diff stays a
  failure). Volatile matches compare presence + JSON type only.
- Audit lint (tools/audit.py): text content, tool names, and tool inputs may
  never be volatile; max 6 volatile paths per case.

## Query parameter encoding

Responsibility split, normative (derived from `check.py::split_url` and
`lm15.vet.normalize_transport_request`):

- The shim returns `params` as DECODED key/value strings: the reference
  splits the adapter's URL with `urlparse` + `parse_qsl(keep_blank_values=
  True)` and strips the query from `url`. `?key=` (blank value) is
  preserved as `"key": ""`.
- The harness decodes the fixture URL the same way and merges the fixture's
  explicit `params` map (stringified) over it, then compares the decoded
  maps strictly. Percent-encoding therefore never reaches the comparison:
  ENCODING IS THE TRANSPORT'S RESPONSIBILITY at send time, out of contract
  scope; the contract pins decoded parameter names and values only.
- **Repeated query parameters are unsupported.** Both sides collapse
  duplicates via `dict(parse_qsl(...))` (last occurrence wins), so an
  adapter MUST NOT emit the same parameter name twice; a provider API that
  required repeats would need a protocol extension (changes/ entry) first.

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
