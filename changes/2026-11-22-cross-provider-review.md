# 2026-11-22 — Cross-provider review and nameless live-call refusal

## Evidence review

[Seven-case review](../goldens/REVIEW-2026-11-22-cross-provider.md): xAI usage,
Gemini chunked parallel calls/signatures, unnamed Chat assembly, Codex final
copies, two Tinker adaptations, and Gemini Live. All existing canonical values
and traces agree with saved wire and the written rules. Review metadata is added;
no expected answers, captured requests, bodies, or receipts are rewritten.
Original scribe provenance remains. The active unreviewed backlog falls 334 → 327.

The review is reproducible without importing any SDK in
`tools/test_reviewed_cross_provider_goldens.py`. It compares complete projections,
including numeric JSON types and exact state/input values. Separate Tinker survey
receipts substantiate the switch-only and ignored-schema policies; the already
adapted request alone would not prove either claim.

## Boundary defect

Gemini Live previously replaced missing/empty tool names with `"tool"` and
coerced non-string names to strings, in both Python and TypeScript. Python's
live-completion path also emitted that fabricated name. Failing SDK regression
tests were recorded before changes. Per MAP-1/MAP-9, completed live calls now
raise ProviderError if no non-empty string name exists. Completion-stream
fragments preserve absence and assembly raises StreamAssemblyError, retaining
partial text/usage. Valid calls, including an explicitly named `"tool"`, keep
IDs, names and inputs verbatim.

`mapping/live-tool-names.json` adds eight synthetic negative controls derived
from the recorded named Gemini Live call: missing/null/empty/numeric name under
both existing decoder envelopes. The live harness exercises them through the
same `replay_live` operation, comparing the typed refusal, not just any failure.
A mutation self-test proves accepting a nameless call is caught. These controls
are not new wire facts or claims of observed bad provider replies.

Trade-off: malformed completed frames now fail rather than dispatching a guessed
function; earlier delivered frames remain delivered, but that completed frame is
refused as a unit. Live missing-ID policy and general live Config coverage are
not redesigned here. Python and TypeScript move pins with their fixes; other
ports remain on their existing pins. No paid API calls or package release.

## Verification targets

The shared harness gains eight live checks and retires four history-replay
checks generated from the archived, withdrawn TypeSafe golden: 4,470 checks per
updated SDK, 69 mutation controls. The removed IDs are
`history-replay.typesafe.conversation_state[openai|openai_chat|anthropic|gemini]`;
other DataPart history-replay cases remain. No failing check was weakened or
skipped to achieve a pass. SDK tests additionally cover strict Tinker refusal before network access
and Python streaming salvage. Provenance, strict audit, spec drift, secrecy,
local tests/type checks and GitHub CI must pass before merging/publishing commits.
