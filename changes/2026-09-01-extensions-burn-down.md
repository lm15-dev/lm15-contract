# 2026-09-01 — extensions burn-down: every passthrough case gets a verdict

Ratified: Maxime Rivest, 2026-09-01 (session assent "yes!" over the
announced pass: promote / bless / drop each of the 22 undecided
config.extensions cases, with named reasons). The June 2026 burn-down
(INV-049) had settled 4 cases; the August–September capture campaigns
added 22 more through the escape hatch with no decision. All 26 are now
decided, and the audit lens grows teeth: an extensions-carrying case
without an explicit verdict is a HARD violation
(tools/extensions-verdicts.json, enforced two-way — stale entries fail
too).

## Promoted (8 cases → canonical; wire requests UNCHANGED, proven)

Three new Config fields, each a concept two providers sell:

- **`service_tier`** (open string namespace — the tier concept is
  canonical, the value vocabulary provider-owned, the `voice`
  precedent): OpenAI + Anthropic map verbatim; Gemini RAISES.
  Cases `openai.service_tier`, `anthropic.service_tier`.
- **`user_id`** (opaque end-user identifier for abuse attribution):
  OpenAI → `safety_identifier` (the current field; `user` is the
  deprecated legacy spelling), openai_chat dialect → `user`,
  Anthropic → `metadata.user_id`; Gemini RAISES.
  Cases `openai.safety_identifier`, `anthropic.metadata`.
- **`store`** (provider-side response storage opt-in/out; `false` is
  data and always serializes): OpenAI + Gemini verbatim (same wire
  key, both live-captured); Anthropic RAISES.
  Cases `openai.store`, `gemini.store`.

Two cases needed NO new surface — the canonical concept already
existed and the fixtures were the only debt:
`openai.prompt_cache_key` / `openai.prompt_cache_retention` rewritten
onto CacheConfig (`key`, `retention: "long"`), whose OpenAI mapping was
already shipping.

All 8 canonical_requests were rewritten (provenance notes appended);
the pinned wire bodies are untouched and the request direction proves
build equality (113 green). Extensions still win on collision with a
promoted field — passthrough precedence is the existing rule.

## Blessed permanent (15 cases, INV-049 — reasons in the registry)

The founding 4, plus: `gemini.safety_settings` (no other provider has a
request-side safety dial), `anthropic.inference_geo` (data-residency
routing), `openai.metadata` (free-form tags for OpenAI's stored-response
dashboard — NOT the user-attribution concept, which promoted),
`openai.user` (deprecated legacy spelling, kept as the passthrough
mechanism's own pinned exemplar — the escape hatch needs one case
proving arbitrary keys flow), and the seven-case OpenAI server-state
family (`previous_response_id`, `conversation`, `background`,
`truncation`, `context_management`, `stream_options`,
`reasoning_encrypted`) under one reason: lm15's canonical conversation
model deliberately resends the transcript instead of modeling OpenAI's
server-side response state.

## Deferred (3 cases — still debt, now explicit and named)

- `openai.top_logprobs` + `openai.include` → the **logprobs design
  pass**: cross-provider (Gemini `responseLogprobs`) but blocked on a
  canonical OUTPUT surface for token probabilities. The two cases are
  duplicates; fold or drop when the pass lands.
- `openai.file_search` → the **builtin-tool-forcing design pass**:
  ToolChoice cannot yet express "force this builtin", and each provider
  forces builtins differently.

## Enforcement

`tools/audit.py` replaces the report-only passthrough lens with a hard
two-way check against the registry: undecided case → violation; stale
registry entry → violation. Current state: 18 passthrough cases = 15
blessed + 3 deferred + 0 undecided. spec/invariants.md INV-049 now
points at the registry as the normative enumeration.

## Evidence at landing time

- Contract: request direction 113 pass (rewritten cases build their
  frozen wire bodies byte-identically); all directions green; audit
  OK with the new hard lens.
- Reference: mapping + raise tests per provider (7 new tests), serde
  round trip incl. `store: false` survival, 803 tests green.
- Config spec table updated with the three rows and their per-provider
  mapping/raise notes.
