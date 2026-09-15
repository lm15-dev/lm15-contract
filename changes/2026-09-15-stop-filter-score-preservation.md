# Stop filtering preserves original events and token scores

Status: RATIFIED — Maxime Rivest, 2026-09-15, in session after the test report
listed the score-coverage rule and shared timeout defaults as the two items
requiring approval: “I'm seeing the two items that you're mentioning. Yeah,
this is fine.” Python implementation was requested earlier in the same session.
Shared score vectors and spec/types.md now record this rule. Contract pins and
other language implementations have not yet been updated.

## Existing obligations

- `spec/types.md`, TextDelta: materialization preserves and concatenates
  provider-reported token scores.
- `docs/mapping-rules.md`, MAP-13.3: client-side stop closes at the cut,
  including when a caller requested complete(). Usage is not reported after
  an early cut; provider generation/billing after disconnection is not promised.
- MAP-13.6: silent policy hides adaptation records, not execution behavior.

The former text-only stop buffer discarded every TextDelta.logprobs, even
when no stop was matched. That is an implementation defect, not a permitted
adaptation. Passing original events through unchanged fixes that omission.

## Ratified boundary rule and canonical addition

A stop may begin inside a provider token. That token's probability describes
its entire original byte sequence, not the shortened text returned to the
caller. Never split, rescale, rename, or invent a token probability.

- Retain original scores for whole tokens entirely before the cut.
- Exclude scores for the removed suffix, including a token crossing the cut.
- Keep the requested visible-text prefix exactly, including an unscored partial
  token when necessary. Do not move the stop boundary to a token boundary.
- Use provider-reported token bytes to establish alignment. Fall back to token
  spellings only when their UTF-8 bytes exactly reconstruct the original text.
  Tokens can themselves split a Unicode character. If alignment is uncertain,
  omit scores for the shortened event instead of attaching guesses.
- Add `logprobs_complete: bool` to TextDelta and Response, default true,
  omitted from canonical JSON when true; false must be serialized.
  Python constructors make this field keyword-only.
- False means local editing left retained text without corresponding original
  scores. True means no such local loss is known, NOT that the provider supplied
  scores for every token or supplied any scores at all. A false flag can
  accompany empty/absent logprobs. This qualifies the existing Response rule
  that absent logprobs means the provider did not report them.
- Materialization ANDs the flag across text events. A later true cannot erase
  a previous false. Response-to-events conversion carries false on the first
  text event, even when the score array is empty. If no TextPart exists to
  carry it, conversion refuses rather than silently losing the flag.
- Unmatched stops preserve all original events, scores, usage, and provider
  metadata. Intervening non-text events remain in order; events after a matched
  cut are not released merely because they contain no text.

## Why a field, not optional provider diagnostics

Default canonical response serialization omits provider_data. Hiding incomplete
coverage there would lose the warning when responses are cached or saved.
The explicit boolean makes the distinction durable without inventing probabilities.
Older readers that ignore new fields cannot preserve this distinction: update
consumers/ports before relying on it across versions. No port parity is claimed.

## Trade-offs

- Holding original events can delay delivery until an event's entire text is
  safe (or the stream ends), instead of releasing character-sized prefixes.
  Intervening events also wait to preserve order. There is no arbitrary event
  size or pending-memory cap added in this patch.
- A boundary token loses its score, not its retained text. Keeping that score
  would falsely suggest a probability for the shortened token.
- The shared representation gains one optional boolean in two types. This
  needs propagation; the fix is not complete cross-language merely because
  Python implements it.

## Evidence and verification status

The original no-hit score loss was reproduced during the PR review. New local
regression tests cover original event identity/order, all split positions of a
stop sequence across events/parts, aligned and partial-token cuts, Unicode byte
boundaries, unalignable token metadata, complete-value clipping, JSON round trips,
and provider-shaped SSE through sync/async complete/stream calls.

The Python suite passed after authorization: 2,434 passed, 5 skipped,
with paid subscription smoke tests excluded. The new score-preservation tests
were included. These are synthetic local tests, not new live-provider receipts
or replacement goldens.
