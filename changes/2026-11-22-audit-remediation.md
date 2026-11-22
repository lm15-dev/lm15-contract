# 2026-11-22 — Contract grader hardening, secret-leak fixes, and rulebook reconciliation

**Status: verified implementation of existing rules in `lm15-contract`,
`lm15-python`, and `lm15-ts` on 2026-11-22. Review/live-capture backlog and
other ports remain deferred; this is not closure of every audit finding.**

## Why

A full audit of `lm15-contract`, `THEORY.md`, `lm15-python`, and `lm15-ts`
against lm15's stated principles (`AUTHORITY.md`, `spec/auth.md` AUTH-5,
`docs/mapping-rules.md` MAP-13, `spec/invariants.md`) turned up five concrete
gaps despite all existing checks reporting green:

1. **AUTH-5 secrecy leaks:** TypeScript `ProviderLM`, `LMRouter` (including
   `config.apiKeys` and `config.env`), `TransportRequest`, `PkcePair`, and
   `XaiDeviceAuthorization` exposed secret values via `util.inspect`,
   `toString`, or `JSON.stringify`; Python's `ProxyRoute.basic_auth`,
   `parse_proxy_url` errors, and `RouterConfig.env` could leak credentials.
2. **Silent behavior drift in Python & TypeScript:** `reasoning_format="none"`
   silently dropped `config.reasoning` on the Responses dialect; boolean-only
   thinking switches (`qwen`, `zai`, `qwen_chat_template`) dropped the effort
   level without recording `substituted`; Gemini trailing usage-only SSE frames
   fabricated `finish_reason="stop"` (overwriting earlier `"length"` /
   `"tool_call"`); TypeScript's `gpt-5.6+` cache breakpoint check ran twice;
   Anthropic `structured_output="reject"` bypassed `probabilities="required"`;
   Python's `AsyncBaseProviderLM` omitted `_require(...)` gates and
   `batch_submit` adaptation collection; Python's transport retried
   `WriteTimeout` on reused sockets.
3. **Harness and tool loopholes:** `tools/check_provenance.py` checked only
   that receipt hashes were non-empty instead of hashing `pinned_body`;
   `harness/check.py` never ran `auth/named-credentials.json`, never called
   `validate` on invalid canonical inputs, and skipped `provider`, `status`,
   and `request_id` on `normalize_error`; `tools/audit.py` lacked the promised
   MAP-13 rule 7 "no receipt" refusal check.
4. **Unreviewed goldens backlog:** 340 of 538 `goldens/` lacked
   `provenance.reviewed` with no ratchet preventing new unreviewed goldens.
5. **Stale rulebooks:** pre-MAP-13 "RAISES" prose remained in MAP-5..8, MAP-12
   disagreed with `tools/openai-chat-ingest-verdicts.json` on 7 keys, two
   contract files inverted `AUTHORITY.md` wording, and `SCOPE.md` / `THEORY.md`
   carried outdated counts and already-resolved findings.

## What

- **Harness & protocol (`harness/check.py`, `harness/PROTOCOL.md`, `harness/fake_shim.py`, `harness/selftest.py`):**
  - Added `serde/reject.json` (27 spec-cited invalid canonical values) and
    wired `validate` into `run_serde_direction`.
  - Wired `auth/named-credentials.json` (22 cases, including AUTH-5 sentinel
    checks on refusal replies) into `run_auth_direction`; documented optional
    `credential`, `base_url`, and `settings_error` on `explain_auth`.
  - Enabled comparison of `provider`, `status`, and `request_id` in
    `run_error_direction` and updated `normalize_error` in `PROTOCOL.md` plus
    the Python and TypeScript vet shims.
  - Added five mutations (`validate_accepts_invalid`, `validate_unrelated_error`,
    `validate_rejects_valid`, `auth_named_error_sentinel_leak`,
    `error_provider_drift`) to `harness/selftest.py` (68/68 caught red).
  - Positive controls run `validate` on all 138 valid canonical inputs;
    invalid inputs must produce validation errors, not unrelated exceptions.
    Required fixture files cannot silently disappear.
  - Cloud/core auth scope uses the contract's credential-policy table, so
    refusals before a cloud rung are still classified correctly.
  - Eight Gemini stream variants repeat final usage without a finish reason;
    counts and the earlier finish reason must survive unchanged.
- **Provenance & audit tools (`tools/check_provenance.py`, `tools/audit.py`):**
  - `check_provenance.py` hashes every receipted `pinned_body` against
    `provenance.response_exchange or provenance.exchange`'s `response_sha256`
    (allowing a single trailing `\n` from capture serialization; pinning the 7
    documented redacted/JSONL bodies in `tools/receipt-hash-allowlist.json` by
    `body_sha256`).
  - Added `tools/unreviewed-goldens-ratchet.json` (340 grandfathered entries)
    so zero new unreviewed goldens can land and the list only shrinks.
  - `audit.py` checks MAP-13 rule 7 on refusal cases (`check_refusal_receipts`);
    it is not a proof of every possible runtime refusal.
  - CI checks out a pinned Python reference for reflection and runs audit in
    `--require-reference` mode and spec drift in strict mode: missing cross-repo
    checks fail rather than silently skip.
  - Offline tooling tests cover receipt tampering, separate response receipts,
    exact redaction exceptions, missing registries, review-ratchet changes,
    invalid-input error classes, and strict missing-reference failures.
- **Transport:** both Python transports now propagate all failed writes, not
  just timeouts. `sendall`/buffered writes cannot prove that a broken pipe sent
  no bytes. Stale connections are still discarded before writing; a race after
  that check produces a visible error instead of an automatic paid replay.
- **Rulebooks:** Reconciled `docs/mapping-rules.md` (MAP-5, MAP-6, MAP-7,
  MAP-8, MAP-12), `spec/SCOPE.md`, `spec/auth-managed.md`,
  `tools/openai-chat-ingest-verdicts.json`, `spec/types.md`,
  `spec/vocabularies.md`, and `THEORY.md`.

## Trade-offs stated

- **Port scope:** `lm15-python` and `lm15-ts` implement all changes and pass
  4,466/4,466 harness checks (50 inapplicable cases skipped); `lm15-rs`, `lm15-go`, `lm15-jl`, and `lm15-r`
  stay cleanly at their current `CONTRACT_PIN` until synced in a follow-up.
- **No paid live API calls:** The 12 pre-2026-09-06 wire cases whose bodies
  were updated on 2026-09-14 and the 340 grandfathered unreviewed goldens are
  tracked for dedicated review / live re-capture passes. Only the unreviewed
  golden list is ratcheted; the 12 old wire cases have not been repaired.
- **Trailing newline tolerance:** `check_provenance.py` accepts a single
  trailing `\n` on `pinned_body` when `sha256(body[:-1]) == response_sha256`
  (covering 54 existing capture files without rewriting verbatim body bytes).
