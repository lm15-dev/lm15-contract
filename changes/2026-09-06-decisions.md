# Ratification decisions — 2026-09-06

Maxime Rivest ratified these decisions in session on 2026-09-06 ("perfect,
implement it all!"), after review of the proposals and the simplification
pass. This file is the single statement of the decided rules (copied from the maintainer's working notes into the contract on 2026-09-06). Workers
implement exactly this text; they do not re-decide. Where a rule below
changes a normative file, the worker cites this file and the ratification
date in the `changes/` entry.

Repositories: `lm15-contract` (the oracle), `lm15-python` (reference;
`docs/mapping-rules.md` and `docs/serde-rules.md` are normative per
AUTHORITY.md). Dates: use 2026-09-06.

## D1 — AUTH-2: a BearerToken may travel under `x-api-key`. RATIFIED.

Rule (replaces the 2026-09-04 draft wording, same substance):
- An `ApiKey` uses the policy's first header-carrying scheme in policy order
  (`bearer`, `x-api-key`, `api-key`, `query-key`).
- A `BearerToken` uses `bearer` if the policy lists it; else `x-api-key` if
  the policy lists it; else the adapter raises `NotConfiguredError`
  naming the accepted schemes.
- `AwsCredentials` uses `sigv4` only; any other scheme raises.
- Cost, stated: a token given to a key-header-only door that does not take
  tokens (first-party `anthropic`) gets the provider's 401, not a local
  error.
- `spec/vocabularies.md` `AuthScheme` row `x-api-key`: credential kinds
  become `api_key`, `bearer_token`.
- `spec/auth.md` footer: the 2026-09-04 AUTH-2 amendment is ratified
  2026-09-06. `changes/2026-09-04-bedrock-bearer.md` status → RATIFIED.
- A harness wire pin lands with the first Bedrock Claude HTTP 200 (account
  gated today; stated, not absorbed).

## D2 — AUTH-10: tenth host `bedrock-mantle-chat`. RATIFIED.

Footer and `changes/2026-09-04-bedrock-mantle-chat-live.md` → RATIFIED
2026-09-06. One provider string, one wire.

## D3 — Live provider entries: wire facts ratified; goldens ratified later.

These entries flip to `Status: RATIFIED 2026-09-06 (wire facts: cases,
bodies, errors, receipts). Goldens: see changes/2026-09-06-ratification.md.`:
`2026-09-03-provider-registry`, `-deepseek-live`, `-deepseek-anthropic-live`,
`-zai-live`, `-moonshotai-live`, `-moonshotai-wires`, `-meta-live`,
`-bedrock-chat-live`, `2026-09-04-azure-live`, `-azure-chat-live`.
`2026-09-04-azure-anthropic-partial.md` stays BLOCKED.

## D4 — `playbooks/api-family.md`: ratified after these edits.

1. Credential row: a credential provider returns a credential value
   (`ApiKey`, `BearerToken`, `AwsCredentials`); a plain string is the
   `ApiKey` shorthand. Python/TS/Julia zero-arg callable, Go/Rust single-
   method interface returning the value. Same in all four.
2. New row "Host settings": `settings=` on every provider constructor and
   `RouterConfig.settings` (Python), `settings` option object (TS),
   `lm15.WithSettings(map)` (Go), `HostSettings` builder field (Rust).
3. Rule 6: **Positional layout is frozen at 1.0. Every field added later is
   keyword-only (or the language's equivalent: options struct / builder).**
4. Rule 7: **Prefer `reject` to a new send-as value. A compat knob exists
   only when the wire has no other way, the goal is unreachable without it,
   and at least two providers need it. Otherwise it is an `extensions`
   passthrough.**
5. A "Marked for demotion" note: `OpenAIResponsesCompat.edit_image_field`
   and `commentary_phase` are single-provider knobs (Meta). They stay in
   1.0.0a; they move to `extensions` in the next alpha unless a second
   provider needs them. (Note only; no code change now.)
6. Status line → `RATIFIED 2026-09-06`.

## D5 — Hidden thinking: remove `redacted`. RATIFIED (alpha window).

- `ThinkingPart` loses the `redacted` field. Factory:
  `thinking(content, *, continuation=None)`.
- `ThinkingDelta` gains nothing.
- New MAP-7 rule 11: **Hidden thinking is a `ThinkingPart` with empty `text`
  and continuation state. There is no flag and no placeholder text.**
  Anthropic `redacted_thinking` → `ThinkingPart(text="",
  continuation=[anthropic:redacted_thinking {"data": <blob>}])`. In a
  stream: `ThinkingDelta(text="")` at `content_block_start`,
  `ContinuationDelta(part_index=i)` at `content_block_stop`. Replay is
  unchanged (the blob goes back as `redacted_thinking`).
- Why: a Responses reasoning item with no summary is already "empty text +
  state" (MAP-7.9). One concept, not two. `[redacted]` was English
  presentation text, not provider text.
- `spec/types.md` ThinkingPart table: drop the `redacted` row; `spec/
  invariants.md` INV-045 example list: drop `redacted → false`.
- `serde/canonical.json`: any ThinkingPart vector carrying `redacted` is
  rewritten to the new shape with a provenance citation of this decision.

## D6 — FileReadiness fold. RATIFIED.

`spec/vocabularies.md` FileReadiness, OpenAI-shaped `status`:
`uploaded | pending → pending`, `error | failed → failed`,
`processed | absent | unknown → ready`. The reference implements the same
table in the shared OpenAI-shape file mapping.

## D7 — Continuation namespace is the dialect. RATIFIED.

- MAP-7.8 gains: **`ContinuationState.provider` names the dialect that
  consumes the state (`openai`, `anthropic`, `gemini`, `xai` where xAI has
  its own wire), never the door. A Meta or Azure reasoning item is
  `openai:reasoning_item`. State replays verbatim on any door of that
  dialect; the server judges.**
- `spec/types.md` ContinuationState `provider` constraints column: "dialect
  id, not the access-route provider string (MAP-7.8)".

## D8 — Message-level id continuation is dropped. RATIFIED.

- No dialect emits `openai:response_id`, `gemini:response_id`, or
  `anthropic:message_id` continuation. `Response.id` (and
  `StreamStartEvent.id`) carry the id. Nothing consumed those states
  (verified: no reader in lm15-python). Server-side chaining knobs
  (`previous_response_id`, `conversation`) stay `extensions` per INV-049.
- New invariant **INV-051 — Stream/complete parity.** The Response
  materialized from a stream's events equals the Response the complete call
  produces for the same body, except fields the wire withholds on one path.
  The withheld fields are listed per dialect in MAP-9.6 (today: chat
  streams carry no `id`). Continuation state is never withheld: state known
  at start is emitted immediately after `start` as a message-level
  `ContinuationDelta`; state known at a part's end is emitted at that end.
- MAP-9.6 gains the per-dialect withheld list and the sentence above.
- `serde/canonical.json`: the two vectors carrying `response_id`
  continuation are rewritten to a `reasoning_item` example (same shape,
  different kind/data), provenance cites this decision.
- Goldens: every message-level `response_id` / `message_id` continuation
  entry and its message-level `ContinuationDelta` event are removed. See
  "Golden migration" below.

## D9 — `StreamEndEvent.provider_data`: one rule, escape hatch. RATIFIED.

- MAP-3 gains: **`StreamEndEvent.provider_data` is the wire frame that
  supplied `usage`, verbatim (the JSON object of that frame); if no frame
  supplied usage, the frame that supplied `finish_reason`. Bare terminators
  contribute nothing. It is an escape hatch, not a canonical fact: the
  harness compares it for presence and JSON type only.** Chat: the usage
  chunk. Anthropic: the `message_delta` frame. Responses:
  `response.completed` (the event payload's `response` object, as today).
  Gemini: the last chunk. xAI: same as its wire.
- `harness/check.py`: `$.events[*].provider_data` on `end` events is
  compared by presence + type (like a volatile path), never by content.
  `harness/PROTOCOL.md` says so. A selftest mutation `end_provider_data_dropped`
  (drop the field) must be caught.
- Goldens: end events on chat and Anthropic-family streams gain
  `provider_data` per the rule.

## D10 — Never parse delimiters out of provider text. RATIFIED.

New MAP-7 rule 12: **Thinking comes only from a typed wire field. lm15
never parses delimiters (`<think>`, `<reasoning>`, …) out of provider text.
Where a server knob separates reasoning (Groq `reasoning_format: parsed`,
MAP-7.7), the preset sends the knob.** Bedrock runtime gpt-oss inline tags
stay literal text; a live cell (does the runtime accept a parsed-reasoning
knob?) is a follow-up, not done here.

## D11 — Evidence: grandfather old receipts, require hashes from now.

`AUTHORITY.md` Evidence section gains: **A live-capture case dated on or
after 2026-09-06 carries `provenance.exchange`: the path (relative to the
contract root) of the exchange receipt written by the capture tool, which
records `request_sha256` and `response_sha256` of the unredacted transport
exchange. Captures dated earlier stand as live evidence without a hash
(grandfathered, stated).** `tools/check_provenance.py` enforces it: for
`source: live-capture` with `date >= 2026-09-06`, `exchange` must exist,
the file must exist, and it must contain both hashes. Re-ratification
footer: "Re-ratified: Maxime Rivest, 2026-09-06 — evidence hashes; transcribed."

## D12 — Golden review state uses the existing `reviewed` line.

No new `source` value. A frozen golden has `provenance.reviewed` (a dated
sentence naming the review and approver), as today. `check_provenance.py`
validates that when `reviewed` is present it is a non-empty string starting
with a `YYYY-MM-DD` date. `tools/scribe_goldens.py` keeps never rewriting a
golden that has `reviewed`.

## D13 — Moonshot links. Mechanical.

21 cases under `cases/moonshotai-responses/` and `cases/moonshotai-anthropic/`
cite `changes/2026-09-03-moonshotai-responses-live.md` /
`-moonshotai-anthropic-live.md`, which do not exist. They cite
`changes/2026-09-03-moonshotai-wires.md`. (Parent does this on main.)

## D14 — Port playbook: module 3 splits.

`playbooks/port.md`: module 3 becomes **3a — core auth** (AUTH-1 `key`,
`oauth`, `oauth-unless-explicit`; AUTH-2 credential values; AUTH-5; AUTH-7
doctor; AUTH-8 borrowed CLI files; `--direction auth` for non-cloud cases)
and **3b — cloud chains** (AUTH-1 cloud chains, AUTH-11 rung kinds, SigV4,
RS256, `--direction token`, the cloud cases of `--direction auth`). 3a gates
1.0; 3b does not. A port without 3b answers `NotConfiguredError` for
cloud-chain providers and states it in its README. The harness needs a way
to run only the non-cloud auth cases: `check.py --direction auth
--auth-scope core|cloud|all` (default `all`); a cloud case is one whose
provider's policy is a cloud chain (`aws-chain`, `azure-chain`,
`gcp-chain`) — determined from `spec/support-matrix.json`. Idioms section:
credential provider returns the AUTH-2 value (already stated).

## D15 — SigV4 vectors: the whole AWS suite.

Freeze the complete AWS SigV4 test suite (botocore
`tests/unit/auth/aws4_testsuite/`, upstream GitHub, main branch at fetch
time) under `research/cloud-hosts/sources/aws-sigv4-suite/` with the
manifest convention already used there (original-response and saved-byte
hashes, source URL, fetch date). Add every case that has `.req`, `.creq`,
`.sts`, `.authz` files to `auth/sigv4-vectors.json` in the existing vector
shape. Cases the reference signer fails are reported, not hidden: no vector
is dropped to make the reference green (AUTHORITY.md). Known-to-be-thin
areas: percent-encoded paths, dot segments, `+` in query, space in path.

## D16 — Reference-only decisions (not contract).

- Async adapters call a credential provider through `asyncio.to_thread`
  so a chain refresh does not block the event loop.
- `docs/cloud-hosts.md` states the stdlib RSA timing limit and names the
  mitigation: an external token provider (`BearerToken` from your own
  signer or the cloud CLI) for high-value keys.
- `docs/cookbooks/10-audio-video-reasoning.md`: replace the
  `ThinkingPart(redacted=True)` mention with the D5 shape.

## Golden migration (D5, D8, D9 together)

327 goldens exist; 110 carry a `reviewed` line (frozen). Frozen goldens
change only by a scripted, verifiable transform with a re-review note, as
the MAP-3 and MAP-4 precedents did (see `goldens/anthropic/streaming.json`
provenance). Pipeline:

1. `tools/migrate_goldens_2026_09_06.py` (new, kept in the repo as the
   record): for every golden, (a) remove message-level continuation
   entries whose kind is `response_id` or `message_id`, and message-level
   `ContinuationDelta` events (no `part_index`) of those kinds; (b) remove
   `redacted` keys; for a ThinkingPart that had `redacted: true`, set
   `text` to `""`; for a ThinkingDelta whose text is exactly `[redacted]`,
   set `text` to `""`. It prints a per-file summary of what it removed.
2. Re-scribe every golden with the fixed reference into a scratch directory
   (`tools/scribe_goldens.py` gains `--out DIR`, and never touches
   provenance when `--out` is used). Diff scratch against the migrated
   goldens: the ONLY allowed differences are (c) an added `provider_data`
   on `end` events of chat/Anthropic/xAI-family streams (D9). Any other
   difference is a finding: print it and stop; do not overwrite.
3. Write final goldens = migrated content + (c). Provenance: keep every
   existing key; for frozen goldens append to `reviewed`: ` Re-reviewed
   2026-09-06 for D5/D8/D9 (changes/2026-09-06-decisions.md,
   changes/2026-09-06-ratification.md): change verified by
   tools/migrate_goldens_2026_09_06.py to be exactly {what changed}.` For
   draft goldens append the same sentence to `evidence`.
4. `python3 harness/check.py --shim python --direction all --no-check-pin`
   must be all green with the two pre-existing `openai.computer_use` skips
   only. `goldens/_failures.json` is regenerated by the scribe.

The 88 new (2026-09-03/04) goldens stay `scribe-draft` until the parent's
independent re-review; the parent then adds their `reviewed` line.
