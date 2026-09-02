# lm15 canonical invariants

Numbered catalog of every construction-time (`__post_init__`) rule and every
serde leniency behavior in the canonical model. Ports MUST replicate each
invariant at their API boundary, or document the idiomatic equivalent (e.g. a
language whose type system makes INV-020 unrepresentable simply doesn't need
the coercion — but must accept the same canonical JSON).

Rationale provenance: rationales citing a docstring, code comment, error
message, changes/ entry, or recorded review are primary-sourced. Rationales
that were originally marked "(inferred)" were re-derived from code and
history on 2026-06-11; where no primary source exists they are marked
**(design intent, confirmed by maintainer ratification 2026-06-11)** — the
rationale is the designed reason, ratified, not a guess.

## JSON value discipline

- **INV-001 — Strict JSON values only.** Opaque payload fields (`input`,
  `parameters`, `config`, `extensions`, `response_format`, `provider_data`,
  continuation `data`) accept only `null`/bool/int/finite float/str and
  list/dict-of-string-keys compositions thereof; non-finite floats and
  non-string dict keys are rejected at construction.
  WHY: anything else has no JSON wire form; validating at the boundary keeps
  every later serialization infallible (types.py module docstring, principle 5).
- **INV-002 — Opaque objects are validated, never copied or mutated.**
  Validation is iterative and non-coercing; the caller's container is stored
  as-is. WHY: opaque payloads must round-trip byte-exact (serde-rules.md
  omission rule 3); copying/coercing would create second wire forms.
- **INV-003 — bool is never a number.** `True` is rejected wherever an
  int/float is expected and never coerces under the Number rule.
  WHY: Python's `bool subclasses int` is a Python accident, not a canonical
  fact; `true != 1` is also the harness comparison rule (PROTOCOL.md).
- **INV-004 — Empty `extensions` normalizes to absent.** `extensions={}` is
  stored as `None` on every type carrying extensions.
  WHY (design intent, confirmed by maintainer ratification 2026-06-11): `{}` and absent would otherwise be two wire forms of "no
  extensions" — the omission rule already treats a type's own empty optional
  field as absent.

## Number rule coercions

- **INV-005 — Continuation normalization.** `continuation` accepts `None`
  (→ `()`), a single `ContinuationState` (→ 1-tuple), or a sequence (→
  tuple); strings and non-ContinuationState elements are rejected.
  WHY (design intent, confirmed by maintainer ratification 2026-06-11): ergonomic single-state attach with one in-memory shape.
- **INV-006 — `part_index` is an int `>= 0`.** Applies to every Delta.
  WHY: indexes address parts positionally during stream assembly; negatives
  are meaningless.
- **INV-007 — Int fields coerce same-valued floats and reject the rest.**
  `2.0 → 2`; `2.5` raises; applies to `max_tokens`, `top_k`,
  `thinking_budget`, `prefix_until_index`, every Usage
  counter, `sample_rate`, `channels`, every `part_index`.
  WHY: each numeric field has ONE declared wire form (serde-rules.md Number
  rule); rounding would silently change meaning.
- **INV-008 — Float fields coerce same-valued ints.** `1 → 1.0`; applies to
  `temperature`, `top_p`, pricing
  fields, error `retry_after`. WHY: same Number rule; before 2026-06-10 the
  wire form depended on the caller's Python literal, which other languages
  cannot reproduce.
- **INV-009 — Path coercion.** Path-typed fields (`*Part.path`,
  `FileUploadRequest.path`) accept strings and coerce to `pathlib.Path`;
  empty path strings are rejected. On the wire a path serializes as its
  string. WHY (design intent, confirmed by maintainer ratification 2026-06-11): ergonomics; empty path is always a bug.

## Media parts

- **INV-010 — `media_type` is required and non-empty** on every media part.
  WHY (design intent, confirmed by maintainer ratification 2026-06-11): receivers (providers, renderers) cannot interpret bytes
  without it; defaults per part type fill it at construction.
- **INV-011 — Exactly one media source.** Each media part (and the media
  factory functions, and FileUploadRequest with its `bytes_data`/`path`
  pair) requires exactly one of `data`/`url`/`file_id`/`path`, non-empty.
  WHY: "one representation per concept" — two addresses would make
  precedence ambiguous in every consumer.
- **INV-012 — Inline `data` must be base64-shaped.** Data-URI prefixes
  (`data:...;base64,`) are stripped to the payload; embedded whitespace is
  collapsed; the payload must match `^[A-Za-z0-9+/]*={0,2}$` with length
  % 4 == 0. Validation never eagerly decodes large payloads.
  WHY: catches corruption at construction without paying a decode
  (`_validate_base64_data` docstring: "without eagerly decoding large
  payloads"); whitespace-tolerant because providers and shells wrap base64
  (design intent, confirmed by maintainer ratification 2026-06-11).

## Part-level content rules

- **INV-013 — Tool results contain presentational parts only.**
  `ToolResultPart.content` (and `LiveClientToolResultEvent.content`) may not
  contain ToolCallPart, ToolResultPart, ThinkingPart, or RefusalPart.
  WHY: tool results are data returned TO the model; protocol parts inside
  them would re-enter agent loops (docstring; same logic as MAP-1).
- **INV-014 — Tool result content is non-empty.** An empty OUTPUT is
  expressed explicitly as one empty TextPart — `tool_result(id, "")`
  produces `(TextPart(""),)` via INV-021 and is valid — but a content tuple
  with zero parts is rejected. WHY (design intent, confirmed by maintainer ratification 2026-06-11): mirrors Message's never-empty
  guarantee; "no content at all" is indistinguishable from a bug.
- **INV-015 — `TextPart.text` and `ThinkingPart.text` MAY be empty.**
  WHY: streaming reassembly and provider redaction produce legitimately
  empty fragments (RefusalPart docstring); MAP-2 also requires an empty
  TextPart as the never-empty-message placeholder.
- **INV-016 — `RefusalPart.text` is non-empty.** WHY: a refusal is final
  semantic content; an empty refusal communicates nothing (docstring).
- **INV-017 — CitationPart requires at least one of `url`/`title`/`text`.**
  WHY (design intent, confirmed by maintainer ratification 2026-06-11): an all-empty citation cites nothing.
- **INV-018 — Media deltas carry AT MOST one address** (`data`/`url`/
  `file_id`), possibly none (metadata-only chunk); final media validation
  happens at stream assembly, not per chunk. WHY: chunks are partial; a
  chunk's base64 may be unaligned (AudioDelta docstring).
- **INV-019 — CitationDelta requires at least one of `text`/`url`/`title`.**
  WHY (design intent, confirmed by maintainer ratification 2026-06-11): same as INV-017.

## Constructor coercions (API-boundary sugar — replicate or document)

- **INV-020 — Bare-value and list→tuple coercion.** Sequences are stored as
  tuples; a bare element coerces to a 1-tuple: `Message.parts` (bare Part),
  `Request.messages` (bare Message), `Config.stop` (bare str),
  `ToolChoice.allowed` (bare str),
  `LiveClientTurnEvent.parts` (bare Part), continuation everywhere
  (INV-005). A bare STRING for `Message.parts` is rejected with guidance to
  use `Message.user(...)`. WHY: shallow immutability requires tuples;
  the bare-Message coercion was an explicit 2026-06-10 API-regret fix.
  Ports replicate at their boundary or document the idiomatic equivalent
  (e.g. variadics / overloads).
- **INV-021 — Content normalization.** Factory inputs (`Message.user/...`,
  `tool_result`, `system`) accept a string (→ one TextPart), a single Part,
  or a sequence of strings/Parts; empty sequences are rejected; non-Part
  non-str elements are rejected. WHY: the 90% case is plain text; one
  normalizer means one behavior everywhere (design intent, confirmed by
  maintainer ratification 2026-06-11).
- **INV-022 — Tool messages contain only ToolResultPart.**
- **INV-023 — Assistant messages never contain ToolResultPart.**
- **INV-024 — User/developer messages and `system` never contain
  protocol/artifact parts** (ToolCallPart, ToolResultPart, ThinkingPart,
  RefusalPart, CitationPart). Also: a string `system` must be non-empty.
  WHY (022–024): roles are a protocol; parts that the model or tool runtime
  produces cannot be authored by the caller, and tool output belongs only to
  tool turns (types.py comments).
- **INV-025 — `Message.tool` dict form.** A `{call_id: output}` dict maps
  each entry through `tool_result(call_id, output)` preserving dict order.
  WHY: the tool-result round-trip in one line — flagged by the 2026-06-10
  fresh-eyes panel as elegant-but-undocumented, then promoted to the README's
  flagship tool round-trip example
  (`messages = (*messages, response.message, Message.tool({call.id: result}))`).

## Config-family consistency rules

- **INV-026 — `Reasoning(effort="off")` forbids `thinking_budget` and
  `summary`.** (`total_budget` was removed 2026-09-02, MAP-7 rule 6.) WHY:
  a budget with reasoning off would be silently dead configuration
  (docstring: raises "instead of silently discarding").
- **INV-027 — `CacheConfig(mode="off")` forbids `retention`, `key`,
  `prefix`, `prefix_until_index`, and `resource`; `prefix` and
  `prefix_until_index` are mutually exclusive.** (Widened 2026-09-02 with
  MAP-6; the text lagged until the independent review.) WHY: same
  dead-knob logic as INV-026 — `__post_init__` raises
  `"CacheConfig(mode='off') cannot specify retention, key, prefix,
  prefix_until_index, or resource"` instead of silently discarding.
- **INV-028 — `ToolChoice(mode="none")` forbids `allowed` and `parallel`.**
  WHY: same — `__post_init__` raises `"ToolChoice(mode='none') cannot
  specify allowed or parallel"`; `none` means tools are not used at all.
- **INV-029 — Usage semantics.** Every counter is int-or-absent and
  `>= 0`; absent (`null`) means "not reported", DISTINCT from reported `0`.
  `total_tokens`, when not provided, auto-computes as
  `input_tokens + output_tokens` only when BOTH are present; an explicit
  total is preserved verbatim (provider telemetry). Arithmetic must treat
  absent as unknown, never zero. WHY: providers report different token
  taxonomies; conflating unknown with zero corrupted pricing/telemetry
  (Usage docstring; usage-none-vs-zero changes entry).
- **INV-030 — `Request.tools` / `LiveConfig.tools` names are unique.**
  WHY: tool dispatch is by name; duplicates make calls ambiguous
  (`__post_init__` raises `"... cannot contain duplicate tool names"`;
  design intent, confirmed by maintainer ratification 2026-06-11).
- **INV-031 — `tool_choice.allowed` ⊆ request tool names.** Checked on
  Request, not on ToolChoice alone. WHY (design intent, confirmed by maintainer ratification 2026-06-11): an allowed tool that is
  not offered can never be chosen — always a caller bug.
- **INV-032 — `BatchRequest.model` infers from `requests[0].model`** when
  omitted; it is routing convenience only and constrains nothing.
  WHY: each nested Request carries its own model (docstring).
- **INV-033 — `FunctionTool.parameters` is required-with-shape.** It
  defaults to `{"type": "object", "properties": {}}` and is ALWAYS EMITTED
  on the wire, like `ToolCallPart.input` / `ToolResultPart.content`: the
  field is an opaque JSON-Schema payload, so a caller-provided literal `{}`
  round-trips verbatim as `{}` — it is never subject to the omission rule
  (serde-rules.md omission rule 3). Absent on input still deserializes to
  the default schema (INV-045 round-trip identity).
  WHY: most provider APIs require `parameters`, so the empty-schema default
  keeps no-arg tools valid; and an opaque payload's contents are user data —
  the pre-2026-06-11 behavior (a literal `{}` dropped by the omission rule,
  then read back as the default schema) silently rewrote user data on the
  round-trip, contradicting INV-002. Resolved by maintainer delegation
  2026-06-11; see changes/2026-06-11-inv033-parameters-always-emitted.md.
- **INV-034 — Tool deserialization dispatch.** `"type": "builtin"` →
  BuiltinTool; ANY other or missing `type` → FunctionTool.
  WHY (design intent, confirmed by maintainer ratification 2026-06-11): forward-lenient reading of older payloads that omitted
  `type`.

## Model-wide structural checks

- **INV-035 — Vocabulary/partition self-checks at import.** The Literal
  vocabularies must equal their runtime mirrors; StreamablePart ∪
  NonStreamablePart must equal Part exactly with no overlap; Delta variants
  must equal the streamable part types (plus the state-only `continuation`
  delta). Ports should encode the same partition statically or test it.
  WHY: adding a Part variant has one source of truth; a missed delta or
  dispatch entry fails at import, not in production.
- **INV-036 — A Response message has role `assistant` and is never
  empty** (MAP-2: an otherwise-empty response materializes one
  `TextPart("")`). `finish_reason` is required and canonical.
- **INV-037 — Roles are closed.** Unknown `Message.role` rejects; same for
  every vocabulary-typed field (`finish_reason`, `code`, `status`,
  `encoding`, `effort`, `summary`, `mode`, ...). WHY: closed vocabularies
  (vocabularies.md forward-compat policy) — normalization to canonical
  values happens in adapters, before construction.

## Serde leniency (from_dict rules — exact, normative)

- **INV-040 — Missing text defaults to `""`** on `part_from_dict` for
  `text`/`thinking`/`refusal` (refusal then rejects via INV-016), on
  text-bearing deltas, and on live text events. WHY (design intent, confirmed by maintainer ratification 2026-06-11): tolerate
  hand-written and older fixtures; the constructor still validates.
- **INV-041 — Lenient `tool_result.content` reading.** A string value
  becomes one TextPart (empty string → empty content → rejected); a list may
  mix part objects and scalars (scalars → `TextPart(str(x))`); any other
  shape → empty content → rejected. WHY (design intent, confirmed by maintainer ratification 2026-06-11): tolerance for provider-
  shaped and legacy payloads at the read boundary only — the write side has
  exactly one form.
- **INV-042 — Malformed caller-authored config nests are an error; telemetry
  nests stay lenient.** `config_from_dict` raises `TypeError` when
  `tool_choice`/`reasoning`/`cache` is present but not a JSON object
  (`null` still reads as absent): malformed canonical input is an error,
  never silent data loss. The telemetry/metadata nests — `response.usage`,
  `stream end.usage`, `model_info.origin/inference`,
  `live_config.input_format/output_format` — keep treating a non-dict value
  as absent (`None`/default). WHY: a config nest is the caller's own request;
  silently dropping a mistyped `tool_choice` changes what the request asks
  for (the pre-2026-06-11 behavior). Telemetry nests describe what a
  provider reported — leniency there loses nothing the caller authored.
  Resolved by maintainer delegation 2026-06-11; see
  changes/2026-06-11-inv042-config-nests-reject.md. Ports must match both
  halves exactly.
- **INV-043 — Legacy Reasoning keys.** `reasoning_from_dict` honors
  `{"enabled": false}` (→ effort `off`) and `"budget"` (fallback for
  `thinking_budget`); when effort is `off`, budgets/summary in the payload
  are DISCARDED rather than rejected. Default effort when only legacy keys
  present: `medium`. WHY: pre-effort payloads must keep parsing (code
  comment).
- **INV-044 — Unknown discriminators reject.** Unknown part `type`, delta
  `type`, stream/live event `type`, serde `kind`, cache `mode`/`retention`
  raise (`ValueError`). WHY: closed vocabularies; silent skipping would
  destroy content.
- **INV-045 — from_dict restores defaults for omitted optional fields.**
  `part_index` → 0, `is_error` → false, `redacted` → false, `turn_complete`
  → true, ToolChoice `mode` → `"auto"`, `channels` → 1,
  `media_type` on live client audio/image → their constructor defaults,
  ErrorDetail `message` → `""`, continuation/`data` → `{}`,
  tool_call `input` → `{}`, request `tools` → `[]`, request `config` →
  `{}` → `Config()`, response `usage` → `{}` → `Usage()`. This is the
  inverse of the omission rule: omitted-on-write must reconstruct equal
  values on read (round-trip identity).
- **INV-046 — from_dict delegates validation to constructors.** Serde does
  no type checking of its own beyond shape dispatch; every value flows
  through `__post_init__`, so wire input gets the same invariants (and
  number coercions) as in-memory construction. WHY: one validation surface
  (design intent, confirmed by maintainer ratification 2026-06-11).
- **INV-047 — Lenient message parts.** `message_from_dict` converts non-dict
  part entries to `TextPart(str(x))`; an empty/missing `parts` array is
  rejected before Message construction with a role-naming error.
- **INV-048 — Empty `tool_choice.allowed`, `stop`, `aliases`, etc. read as
  empty tuples**, equal to the omitted form (round-trip identity with the
  omission rule).

## Structured output shape

- **INV-050 — `response_format` has exactly two shapes.**
  `{"type": "json_object"}` (any valid JSON) or `{"type": "json_schema",
  "schema": <JSON Schema>, "name"?: str, "strict"?: bool}`. Any other
  object is rejected at `Config` construction; provider-native spellings
  (`{"format": ...}`, `{"response_mime_type": ...}`, `{"json_schema":
  {...}}`, a bare schema) belong in `extensions`. `schema` is an opaque
  payload (INV-002): adapters never rewrite a keyword, drop `minimum`, or
  flip `additionalProperties` to make a request pass — the provider's
  400 is the contract. WHY: the 2026-09-02 pass found four adapter
  heuristics accepting several spellings for one intent, with the wire
  deciding which; two canonical spellings for one intent violates
  principle 2 of types.py (MAP-8, changes/2026-09-02-tool-choice-structured-output.md).

## Blessed provider-only extension knobs

- **INV-049 — Blessed provider-only extension knobs.** Some
  `config.extensions` passthrough keys are PERMANENT, not burn-down debt.
  Each is provider syntax for a capability no canonical key can express
  without inventing semantics the other providers don't have. The
  NORMATIVE enumeration lives in `tools/extensions-verdicts.json`
  ("blessed" bucket, one reason per case), enforced two-way by
  `tools/audit.py`: an extensions-carrying case without a verdict is a
  hard violation, and so is a stale registry entry. Since the 2026-09-01
  burn-down (changes/2026-09-01-extensions-burn-down.md) the registry
  holds 15 blessed cases — the four founding knobs below, plus Gemini's
  safety-settings dial, Anthropic's inference-geo routing, OpenAI's
  free-form request metadata, OpenAI's seven server-side
  response-state knobs (previous_response_id / conversation / background /
  truncation / context_management / stream_options / reasoning_encrypted —
  the canonical conversation model deliberately resends the transcript
  instead of modeling server state), and `openai.user` kept as the
  passthrough mechanism's own pinned exemplar. A separate "deferred"
  bucket names cross-provider concepts awaiting their own design pass
  (logprobs output surface; builtin-tool forcing) — still debt, made
  explicit. The founding four:
  - **anthropic thinking display** (cases `anthropic.thinking`,
    `anthropic.thinking_budget`): the wire `thinking` object's `"display"`
    field (e.g. `"summarized"`) selects how thinking is surfaced; canonical
    `Reasoning` deliberately maps only to `{type, budget_tokens}` and has no
    display knob, because no other provider exposes one.
  - **openai `max_tool_calls`** (case `openai.max_tool_calls`): the
    Responses API's cap on total tool invocations per response is neither a
    token limit (`max_tokens`) nor a tool-selection constraint
    (`ToolChoice`) — there is no canonical "loop budget" concept.
  - **openai `include` / code-interpreter outputs** (case
    `openai.code_interpreter`): `include: ["code_interpreter_call.outputs"]`
    tunes the verbosity of provider-executed tool traces, which MAP-1 keeps
    out of canonical parts entirely (they live in `provider_data`).
  These keys stay spelled in provider syntax inside `extensions` by design.
  Promoting any blessed knob to a canonical key later is an additive spec
  change (registry entry deleted in the same commit — the audit enforces
  staleness). Promoted so far (2026-09-01): `service_tier`, `user_id`,
  `store` as Config fields; `prompt_cache_key`/`prompt_cache_retention`
  rewritten onto the pre-existing CacheConfig.
  Blessed by maintainer delegation 2026-06-11; see
  changes/2026-06-11-inv049-blessed-extensions.md and
  changes/2026-06-10-passthrough-rewrites.md (the original keep analysis).

The serde kind strings accepted by the vet `serde_roundtrip`/`validate` ops
are enumerated in harness/PROTOCOL.md (§ "Serde kinds").

---

Status: RATIFIED — Maxime Rivest, 2026-06-11 (session assent, transcribed; canonical-facts authority now includes spec/ per AUTHORITY.md).
Amended 2026-06-11 by maintainer delegation (standing instruction to resolve
1.0 spec decisions): INV-033 resolved (parameters required-with-shape),
INV-042 resolved (config nests reject), INV-049 added (blessed extension
knobs), inferred rationales re-derived/confirmed. See
changes/2026-06-11-inv033-parameters-always-emitted.md,
changes/2026-06-11-inv042-config-nests-reject.md,
changes/2026-06-11-inv049-blessed-extensions.md.
