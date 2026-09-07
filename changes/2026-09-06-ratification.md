# 2026-09-06 — Ratification session: sixteen decisions, one record

Status: RATIFIED 2026-09-06.  The decided text is
`changes/2026-09-06-decisions.md` (D1–D16); this entry is the record of
what it changed and where.  Workers transcribed; nothing here was
re-decided.  Context: `changes/2026-09-06-contract-baseline-review.md`
(the gaps this session closed) and
`changes/2026-09-06-streamed-reasoning-state.md` (the MAP-7 correction
that preceded it).

## Decisions

- **D1 — AUTH-2: a `BearerToken` may travel under `x-api-key`.**  An
  `ApiKey` takes the policy's first scheme in policy order; a
  `BearerToken` takes `bearer`, else `x-api-key`, else
  `NotConfiguredError` naming the accepted schemes; `AwsCredentials` is
  `sigv4` only.  Cost, stated: a token on first-party `anthropic` gets
  the provider's 401, not a local error.  A harness wire pin lands with
  the first Bedrock Claude 200 (account-gated).  WHY: the aws-chain's env
  rung yields a `BearerToken` and the Claude doors carry it in the key
  header; the chain and the scheme table disagreed about the chain's own
  product.  Files: `spec/auth.md` (AUTH-2 rule text, footer),
  `spec/vocabularies.md` (AuthScheme `x-api-key`: `api_key`,
  `bearer_token`), `changes/2026-09-04-bedrock-bearer.md` (status).
- **D2 — AUTH-10: tenth host `bedrock-mantle-chat`.**  WHY: one provider
  string, one wire — Bedrock's Chat Completions API is two hosts.  Files:
  `spec/auth.md` (footer), `changes/2026-09-04-bedrock-mantle-chat-live.md`
  (status).
- **D3 — Live provider entries: wire facts ratified; goldens later.**  Ten
  entries flip to `RATIFIED 2026-09-06 (wire facts: cases, bodies, errors,
  receipts)`: `2026-09-03-provider-registry`, `-deepseek-live`,
  `-deepseek-anthropic-live`, `-zai-live`, `-moonshotai-live`,
  `-moonshotai-wires`, `-meta-live`, `-bedrock-chat-live`,
  `2026-09-04-azure-live`, `-azure-chat-live`.
  `2026-09-04-azure-anthropic-partial.md` stays BLOCKED.  WHY: the wire
  facts have receipts; the goldens await the re-review below.
- **D4 — `playbooks/api-family.md` ratified** with six edits: the
  Credential row returns an AUTH-2 value (a string is the `ApiKey`
  shorthand); a "Host settings" row; rule 6 (positional layout frozen at
  1.0; later fields keyword-only); rule 7 (prefer `reject` to a new
  send-as value; a compat knob needs no other way, an unreachable goal,
  and two providers); a "Marked for demotion" note for
  `OpenAIResponsesCompat.edit_image_field` and `commentary_phase`
  (Meta-only; `extensions` in the next alpha unless a second provider
  needs them); status `RATIFIED 2026-09-06`.  WHY: a person who knows
  lm15 in two languages must be at home in the third.  Files:
  `playbooks/api-family.md`, `README.md`.
- **D5 — Hidden thinking: `redacted` removed (alpha window).**
  `ThinkingPart` loses `redacted`; factory
  `thinking(content, *, continuation=None)`; new MAP-7 rule 11: hidden
  thinking is a `ThinkingPart` with empty `text` and continuation state,
  no flag, no placeholder text.  Anthropic `redacted_thinking` →
  `ThinkingPart(text="", continuation=[anthropic:redacted_thinking
  {"data": <blob>}])`; in a stream `ThinkingDelta(text="")` at
  `content_block_start`, `ContinuationDelta(part_index=i)` at
  `content_block_stop`; replay unchanged.  WHY: a Responses reasoning
  item with no summary is already "empty text + state" (MAP-7.9) — one
  concept, not two; `[redacted]` was English presentation text, not
  provider text.  Files: `spec/types.md`, `spec/invariants.md` (INV-045),
  `lm15-python/docs/mapping-rules.md`; `serde/canonical.json` and the
  goldens by the migration below (serde/golden workers).
- **D6 — FileReadiness fold.**  OpenAI-shaped `status`:
  `uploaded | pending → pending`, `error | failed → failed`,
  `processed | absent | unknown → ready`; the reference implements the
  same table in the shared OpenAI-shape file mapping.  WHY: one fold
  table, implemented once, for the OpenAI-shaped `status` field.  Files:
  `spec/vocabularies.md`.
- **D7 — Continuation namespace is the dialect.**
  `ContinuationState.provider` names the dialect that consumes the state
  (`openai`, `anthropic`, `gemini`, `xai` where xAI has its own wire),
  never the door; a Meta or Azure reasoning item is
  `openai:reasoning_item`; state replays verbatim on any door of that
  dialect and the server judges.  WHY: the dialect consumes the state;
  the door only carries it.  Files:
  `lm15-python/docs/mapping-rules.md` (MAP-7.8), `spec/types.md`
  (ContinuationState `provider` constraint).
- **D8 — Message-level id continuation dropped; INV-051 added.**  No
  dialect emits `openai:response_id`, `gemini:response_id`, or
  `anthropic:message_id`; `Response.id` and `StreamStartEvent.id` carry
  the id; chaining knobs stay `extensions` (INV-049).  INV-051
  (stream/complete parity): the Response from a stream equals the
  complete call's Response except the fields MAP-9.6 lists as withheld
  (today: chat streams carry no `id`); continuation state is never
  withheld — start-time state right after `start` as a message-level
  `ContinuationDelta`, part-end state at that end.  WHY: nothing consumed
  those states (verified: no reader in lm15-python) and the id already
  has one place.  Files: `spec/invariants.md` (INV-051),
  `lm15-python/docs/mapping-rules.md` (MAP-9.6); `serde/canonical.json`
  and the goldens by the migration below.
- **D9 — `StreamEndEvent.provider_data`: one rule, escape hatch.**  The
  wire frame that supplied `usage`, verbatim; else the frame that
  supplied `finish_reason`; bare terminators contribute nothing; the
  harness compares presence and JSON type only.  Chat: the usage chunk;
  Anthropic: `message_delta`; Responses: `response.completed` (its
  `response` object, as today); Gemini: the last chunk; xAI: same as its
  wire.  WHY: an escape hatch, not a canonical fact — one rule for every
  dialect, and the harness never pins its content.  Files:
  `lm15-python/docs/mapping-rules.md` (MAP-3); `harness/check.py`,
  `harness/PROTOCOL.md`, the `end_provider_data_dropped` selftest
  mutation, and the goldens by the tools/golden workers.
- **D10 — Never parse delimiters out of provider text.**  MAP-7 rule 12:
  thinking comes only from a typed wire field; where a server knob
  separates reasoning (Groq `reasoning_format: parsed`, MAP-7.7) the
  preset sends the knob.  Bedrock runtime gpt-oss inline tags stay
  literal text; a live cell for a parsed-reasoning knob there is a
  follow-up.  WHY: thinking is a typed wire fact; text between
  delimiters is provider text.  Files: `lm15-python/docs/mapping-rules.md`.
- **D11 — Evidence: grandfather old receipts, require hashes from now.**
  A live-capture case dated on or after 2026-09-06 carries
  `provenance.exchange` (path of the exchange receipt with
  `request_sha256` and `response_sha256` of the unredacted transport
  exchange); earlier captures stand without a hash, stated.  WHY: the
  baseline review found no contemporaneous request hash on existing live
  artifacts, and past receipts cannot be invented.  Files:
  `AUTHORITY.md` (Evidence; re-ratification footer);
  `tools/check_provenance.py` by the tools worker.
- **D12 — Golden review state uses the existing `reviewed` line.**  No
  new `source` value; `check_provenance.py` validates that a present
  `reviewed` is a non-empty string starting with a `YYYY-MM-DD` date;
  `scribe_goldens.py` keeps never rewriting a golden that has `reviewed`.
  WHY: the line exists and already means "frozen".  Files: tools only
  (tools worker).
- **D13 — Moonshot links.**  21 cases under `cases/moonshotai-responses/`
  and `cases/moonshotai-anthropic/` cite
  `changes/2026-09-03-moonshotai-wires.md`, the entry that exists.  WHY:
  mechanical; the per-door filenames were never written.  Files: cases
  (parent, on main).
- **D14 — Port playbook: module 3 splits.**  3a core auth (AUTH-1 `key`,
  `oauth`, `oauth-unless-explicit`; AUTH-2 values; AUTH-5; AUTH-7; AUTH-8
  borrowed CLI files; non-cloud `--direction auth`) gates 1.0; 3b cloud
  chains (AUTH-1 cloud chains, AUTH-11, SigV4, RS256, `--direction token`,
  cloud `--direction auth`) does not.  A port without 3b answers
  `NotConfiguredError` for cloud-chain providers and states it in its
  README.  `check.py --direction auth --auth-scope core|cloud|all`
  (default `all`); a cloud case is one whose provider's policy is
  `aws-chain`/`azure-chain`/`gcp-chain` per `spec/support-matrix.json`.
  WHY: 3a gates 1.0 and 3b does not; the harness needs a way to run only
  the non-cloud auth cases.  Files: `playbooks/port.md`;
  `harness/check.py` by the tools worker.
- **D15 — SigV4 vectors: the whole AWS suite.**  The complete botocore
  `aws4_testsuite` is frozen under
  `research/cloud-hosts/sources/aws-sigv4-suite/` with the manifest
  convention; every case with `.req`, `.creq`, `.sts`, `.authz` joins
  `auth/sigv4-vectors.json`; cases the reference fails are reported, not
  dropped.  WHY: no vector is dropped to make the reference green
  (AUTHORITY.md).  Files: research and auth vectors (tools worker).
- **D16 — Reference-only** (not contract): async adapters call a
  credential provider through `asyncio.to_thread`; `docs/cloud-hosts.md`
  states the stdlib RSA timing limit and the external-token-provider
  mitigation; the cookbook's `ThinkingPart(redacted=True)` mention becomes
  the D5 shape.  Files: lm15-python (Python worker).

## Golden migration (D5, D8, D9)

327 goldens; 110 carry a `reviewed` line (frozen).  Frozen goldens change
only by a scripted, verifiable transform with a re-review note — the
MAP-3 and MAP-4 precedent (`goldens/anthropic/streaming.json`
provenance).  `tools/migrate_goldens_2026_09_06.py` (kept as the record)
removes message-level `response_id`/`message_id` continuation entries
and their message-level `ContinuationDelta` events, removes `redacted`
keys (a `redacted: true` ThinkingPart and a `[redacted]` ThinkingDelta
get `text: ""`), and prints a per-file summary.  A re-scribe into a
scratch directory (`scribe_goldens.py --out DIR`) is diffed against the
migrated goldens; the only allowed difference is an added
`provider_data` on `end` events of chat/Anthropic/xAI-family streams
(D9); any other difference is a finding that stops the run.  Final
goldens = migrated content + that addition; frozen goldens append a
`Re-reviewed 2026-09-06 for D5/D8/D9 …` sentence to `reviewed`, drafts
to `evidence`.  Gate: `harness/check.py --shim python --direction all
--no-check-pin` all green with the two pre-existing `openai.computer_use`
skips only; `goldens/_failures.json` regenerated by the scribe.

The 88 new (2026-09-03/04) goldens stay `scribe-draft` until the
parent's independent re-review; the parent then adds their `reviewed`
line.  D3 ratifies their wire facts, not their canonical expectations.

## Files touched by this record

`AUTHORITY.md`; `spec/auth.md`, `spec/vocabularies.md`, `spec/types.md`,
`spec/invariants.md`; `playbooks/api-family.md`, `playbooks/port.md`;
`README.md`; status lines of the twelve entries named under D1–D3;
`lm15-python/docs/mapping-rules.md`.  The code, goldens, serde vectors,
harness, and tools changes land in the sibling commits of the same
ratification branch.

---

Ratified-by: Maxime Rivest, 2026-09-06 — in session ("perfect, implement it all!"); transcribed.
