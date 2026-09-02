# lm15 closed vocabularies

Every closed string vocabulary in the canonical model. Reference:
`lm15-python/lm15/types.py` Literal aliases plus their runtime mirrors
(frozensets / dispatch tables), which `surface_dump` reflects and
`tools/spec_drift.py` checks against this file.

## Forward-compatibility policy (normative)

1. **Vocabularies are CLOSED.** A canonical value not listed here does not
   exist. Constructors reject unknown values (`ValueError`); deserializers do
   not invent values.
2. **Adapters map unknown provider values to the closest canonical value**
   and never crash on a new provider token. The existing fallbacks are
   normative precedent:
   - openai_chat `finish_reason`: `stop`→`stop`, `length`→`length`,
     `tool_calls`/`function_call`→`tool_call`,
     `content_filter`→`content_filter`; any UNKNOWN value → `"stop"` AND the
     raw value is recorded in the `_lm15_unmapped` canary
     (path `choices[0].finish_reason`).
   - anthropic `stop_reason`: `max_tokens`/`model_context_window_exceeded`
     → `length`; `tool_use`/`pause_turn` → `tool_call`;
     `refusal`/`safety`/`content_filter` → `content_filter`; anything else
     (including `end_turn`, absent) → `stop`.
   - gemini `finishReason`: `MAX_TOKENS` → `length`;
     `SAFETY`/`RECITATION`/`BLOCKLIST`/`PROHIBITED_CONTENT`/`SPII` →
     `content_filter`; anything else → `stop`.
   - batch statuses: provider statuses fold into the canonical BatchStatus
     set (`in_progress`/`processing` → `running`, `validating` → `queued`,
     ...).
   - A present tool call always wins: `has_tool_call` forces
     `finish_reason="tool_call"` regardless of the provider token.
3. **The raw provider value is preserved.** The verbatim provider payload
   stays in `provider_data` (responses embed the raw body / terminal frames),
   so no information is destroyed by the fallback. Where the adapter could
   not even classify the value, it additionally lands in the
   `_lm15_unmapped` recorder (see harness/PROTOCOL.md "Unmapped recorder").
4. **New canonical values are additive spec changes.** Adding a value to any
   vocabulary below requires a `changes/` entry in this repo (and updated
   fixtures citing it), never a silent code edit. Removing or renaming a
   value is a breaking change to every port and requires maintainer
   ratification.

## Role

Runtime mirror: `ROLE_VALUES`.

| Value | Meaning |
|---|---|
| `user` | end-user input |
| `assistant` | model output |
| `tool` | tool execution results (ToolResultPart only) |
| `developer` | high-authority application instructions; native on OpenAI, prefixed user message elsewhere |

## PartType

Runtime mirror: `PART_TYPES` (dispatch table, value → Part class).

| Value |
|---|
| `text` |
| `image` |
| `audio` |
| `video` |
| `document` |
| `binary` |
| `tool_call` |
| `tool_result` |
| `thinking` |
| `refusal` |
| `citation` |

Streamable partition (must stay exact — INV-035): streamable = `text`,
`thinking`, `image`, `audio`, `tool_call`, `citation`; non-streamable =
`video`, `document`, `binary`, `tool_result`, `refusal`.

## DeltaType

Runtime mirror: `DELTA_TYPES` (dispatch table). Equals the streamable part
types plus the state-only `continuation` delta.

| Value |
|---|
| `text` |
| `thinking` |
| `audio` |
| `image` |
| `tool_call` |
| `citation` |
| `continuation` |

## FinishReason

Runtime mirror: `FINISH_REASONS`. A separate namespace from PartType even
where a token (`tool_call`) appears in both.

| Value | Meaning |
|---|---|
| `stop` | natural completion (also the unknown-value fallback) |
| `length` | output/token limit reached |
| `tool_call` | the model requests client tool execution |
| `content_filter` | provider safety/refusal stop |
| `error` | the stream/response ended in error |

## ReasoningEffort

Runtime mirror: `REASONING_EFFORTS`.

| Value |
|---|
| `off` |
| `adaptive` |
| `minimal` |
| `low` |
| `medium` |
| `high` |
| `xhigh` |

## ReasoningSummary

Runtime mirror: `REASONING_SUMMARIES`.

| Value |
|---|
| `auto` |
| `concise` |
| `detailed` |

## ErrorCode

Runtime mirror: `ERROR_CODES`. Bidirectional with the error class hierarchy
(`lm15-python/lm15/errors.py`); `error.type` on the vet protocol is the
CLASS name, `code` is the ErrorCode literal.

| Value | Canonical class | Notes |
|---|---|---|
| `auth` | `AuthError` | 401/403 |
| `billing` | `BillingError` | 402 |
| `rate_limit` | `RateLimitError` | 429 |
| `invalid_request` | `InvalidRequestError` | 400/404/409/413/422 |
| `context_length` | `ContextLengthError` | subclass of InvalidRequestError |
| `timeout` | `TimeoutError` (`RequestTimeoutError` alias) | 408/504; also subclasses the builtin TimeoutError |
| `server` | `ServerError` | 5xx |
| `unsupported_model` | `UnsupportedModelError` | subclass of InvalidRequestError |
| `unsupported_feature` | `UnsupportedFeatureError` (and base `CapabilityError`) | local adapter capability |
| `not_configured` | `NotConfiguredError` (and base `ConfigurationError`) | missing key/config |
| `transport` | `TransportError` | network failure at the LM layer |
| `provider` | `ProviderError` | catch-all; the code fallback |

Class hierarchy (ports must replicate the SHAPE; idiomatic error mechanisms
allowed):

```
LM15Error
├── TransportError
├── ConfigurationError
│   └── NotConfiguredError
├── CapabilityError
│   └── UnsupportedFeatureError
└── ProviderError
    ├── AuthError
    ├── BillingError
    ├── RateLimitError
    ├── InvalidRequestError
    │   ├── ContextLengthError
    │   └── UnsupportedModelError
    ├── TimeoutError
    └── ServerError
```

Error metadata fields (every class): `message`, `code`, `provider`,
`provider_code`, `status`, `request_id`, `retry_after` (float-typed; int
coerces per the Number rule). Retryable set: RateLimitError, TimeoutError,
ServerError, TransportError. HTTP mapping: unmatched status → `ProviderError`.
Code mapping is most-specific-class-first; unknown code →
`ProviderError`.

## StreamEventType

| Value |
|---|
| `start` |
| `delta` |
| `end` |
| `error` |

## BatchStatus

Runtime mirror: `BATCH_STATUSES`. The job lifecycle only — per-entry
fates live in BatchOutcome; conflating the two dimensions is how batch
APIs usually hurt people. Terminal subset mirror:
`BATCH_TERMINAL_STATUSES` (`completed`/`failed`/`cancelled`/`expired`).
Provider folds: `validating` → `queued`; `in_progress`/`finalizing`/
`BATCH_STATE_RUNNING` → `running`; `canceling` → `cancelling`;
Anthropic's `ended` splits on request_counts (all-cancelled →
`cancelled`, all-expired → `expired`, else `completed`).

| Value |
|---|
| `queued` |
| `running` |
| `cancelling` |
| `completed` |
| `failed` |
| `cancelled` |
| `expired` |

## BATCH_TERMINAL_STATUSES

Derived subset of BatchStatus: the states in which a job will make no
further progress (`BatchJobInfo.done`). Not a separate vocabulary — a
named convenience mirror.

| Value |
|---|
| `completed` |
| `failed` |
| `cancelled` |
| `expired` |

## BatchOutcome

Runtime mirror: `BATCH_OUTCOMES`. The fate of one entry (adopted from
Anthropic's result types, US spelling normalized to `cancelled`).
`succeeded` carries a full canonical Response; `errored` a canonical
ErrorDetail; `cancelled`/`expired` neither.

| Value |
|---|
| `succeeded` |
| `errored` |
| `cancelled` |
| `expired` |

## VideoStatus

Runtime mirror: `VIDEO_STATUSES`. The video job lifecycle (ticket
pattern, changes/2026-09-01-video-generation.md). Reuses batch's words
where meanings match; no `cancelling`/`expired` — no probed video wire
exposes either state. Terminal subset mirror: `VIDEO_TERMINAL_STATUSES`
(`completed`/`failed`/`cancelled`).
Provider folds: openai `in_progress` → `running` (other tokens map
verbatim); xai `pending` → `running`, `done` → `completed`; gemini
operations carry only `done` + `error` — done with error → `failed`,
done → `completed`, not done → `running` (the wire exposes no
queued/running distinction; the submit acknowledgement alone is
`queued` on xai).
Stated exception to forward-compatibility rule 2: the video adapters
RAISE `ProviderError` on an unknown wire status instead of folding to
a fallback. Ratified with the surface (the harness status-drift
selftest mutation guards it, changes/2026-09-01-video-generation.md):
a job status steers a polling loop, and a wrong fallback such as
`running` would poll a dead job forever — failing loudly is the honest
move here.

| Value |
|---|
| `queued` |
| `running` |
| `completed` |
| `failed` |
| `cancelled` |

## VIDEO_TERMINAL_STATUSES

Derived subset of VideoStatus: the states in which a job will make no
further progress (`VideoJobInfo.done`). Not a separate vocabulary — a
named convenience mirror, parallel to BATCH_TERMINAL_STATUSES.

| Value |
|---|
| `completed` |
| `failed` |
| `cancelled` |

## FileReadiness

Runtime mirror: `FILE_READINESS_VALUES`. Whether a stored file can be
used in a model request yet. Deliberately NOT the provider wire words
(Gemini says `ACTIVE`; OpenAI's deprecated `status` says `processed`).
Provider folds (verified live 2026-08-31): Gemini `*PROCESSING` →
`pending`, `*FAILED` → `failed`, `ACTIVE`/absent/unknown → `ready`
(suffix match — the `BATCH_STATE_*`-vs-`JOB_STATE_*` drift precedent);
OpenAI deprecated `status`: `uploaded` → `pending`, `error` → `failed`,
`processed`/absent/unknown → `ready`; Anthropic reports no state →
always `ready`.

| Value | Meaning |
|---|---|
| `pending` | still processing; not yet usable in requests |
| `ready` | usable in model requests (also the unknown-value fallback) |
| `failed` | processing failed; unusable |

## AudioEncoding

Runtime mirror: `AUDIO_ENCODINGS`.

| Value |
|---|
| `pcm16` |
| `opus` |
| `mp3` |
| `aac` |

## ToolChoiceMode

Runtime mirror: `TOOL_CHOICE_MODES`.

| Value |
|---|
| `auto` |
| `required` |
| `none` |

## CacheMode

Runtime mirror: `CACHE_MODES` (added 2026-09-01; the vocabulary is unchanged).

| Value |
|---|
| `auto` |
| `off` |

## CacheRetention

Runtime mirror: `CACHE_RETENTIONS` (added 2026-09-01; the vocabulary is unchanged).

| Value |
|---|
| `short` |
| `long` |

## CachePrefix

Runtime mirror: `CACHE_PREFIXES`. Added 2026-09-01 (MAP-6, changes/2026-09-01-caching-design.md A2): the two prefix INTENTS a caller can name without counting messages.

| Value |
|---|
| `stable` |
| `history` |

## LiveClientEventType

| Value |
|---|
| `turn` |
| `audio` |
| `image` |
| `text` |
| `tool_result` |
| `interrupt` |
| `end_audio` |

## LiveServerEventType

| Value |
|---|
| `audio` |
| `text` |
| `tool_call` |
| `tool_call_delta` |
| `interrupted` |
| `turn_end` |
| `error` |

## Open string namespaces (NOT vocabularies)

- `ContinuationKind` — provider-owned, opaque, any non-empty string.
- `ImagePart.detail` — constrained to `low`/`high`/`auto` but defined inline
  on the field (no module-level vocabulary).
- Media `media_type` — MIME strings, open.
- `BuiltinTool.name` — canonical names exist per adapter mapping tables, but
  unknown names pass through.

---

Status: RATIFIED — Maxime Rivest, 2026-06-11 (session assent, transcribed; canonical-facts authority now includes spec/ per AUTHORITY.md).
