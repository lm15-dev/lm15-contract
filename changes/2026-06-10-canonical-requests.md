# 2026-06-10 — canonical requests + pinned bodies

Tool: `tools/attach_canonical_requests.py` (committed, rerunnable; re-running
is a no-op on an attached corpus).

## What was attached

- **`canonical_request`** on the 69 case files that have a logical case in
  `lm15-python2/conformance/cross_sdk/test_cases.json`: the canonical Request
  built by the reference's own interpretation (`request_for_case` in
  `conformance/cross_sdk/dump_request.py`, imported by path) and serialized
  with `lm15.serde.request_to_dict`.
- **`canonical_request_provenance`** alongside each one:
  `{"source": "derived-from-reference", "date": "2026-06-10", "evidence":
  "request_for_case @ lm15-python2 HEAD; DRAFT pending human review — see
  AUTHORITY.md canonical-facts rule"}`. This is a separate field; the existing
  `provenance` blocks (wire-fact provenance, enforced by
  `tools/check_provenance.py`) are untouched.
- **`stream: true`** on the 3 cases whose logical case streams:
  `openai.streaming`, `anthropic.streaming`, `gemini.streaming`.
- **`pinned_body`** on all 96 case files: the newest body file BY NAME in the
  matching `bodies/<provider>.<feature>/` directory. The harness must use ONLY
  the pinned body — this kills the self-selecting oracle where any body in the
  directory could be picked to make a run pass. Every body directory had a
  matching case file; none were orphaned, none invented.

## DRAFT status (AUTHORITY.md, canonical facts)

`canonical_request` is a canonical fact derived from lm15-python2, which holds
**no oracle authority** (canonical-facts precedence: normative rules >
contract fixture > reference > ports). These values are DRAFTs pending human
review against `docs/serde-rules.md` and the forthcoming numbered invariants;
the `canonical_request_provenance` blocks say so explicitly. Promoting a
DRAFT to an authoritative canonical fixture requires a spec citation per
AUTHORITY.md.

## Orphan case files (27) — no logical case, no canonical_request

These wire fixtures exist in `cases/` (with bodies, now pinned) but have no
counterpart in the 69 logical cross-SDK cases, so no canonical request was
derived for them:

- anthropic.cache_control
- anthropic.inference_geo
- anthropic.metadata
- anthropic.service_tier
- anthropic.system_content_blocks
- gemini.cached_content
- gemini.safety_settings
- gemini.store
- openai.background
- openai.computer_use
- openai.context_management
- openai.conversation
- openai.file_search
- openai.include
- openai.metadata
- openai.previous_response_id
- openai.prompt
- openai.prompt_cache_key
- openai.prompt_cache_retention
- openai.reasoning_encrypted
- openai.safety_identifier
- openai.service_tier
- openai.store
- openai.stream_options
- openai.top_logprobs
- openai.truncation
- openai.user

## Gates run

- `tools/attach_canonical_requests.py`: 69/69 attached, 27 orphans, 96 pinned.
- `tools/check_provenance.py`: OK (100 files scanned).
- `lm15-python2/conformance/run_all.py --strict`: all OK (its copies were not
  modified).
- `lm15-python2` pytest suite: 244 passed.
