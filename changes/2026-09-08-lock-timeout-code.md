# 2026-09-08 — ErrorCode `lock_timeout`: the credential-lock timeout joins the family

Ratification: RATIFIED 2026-09-08 — Maxime Rivest, in session ("i ratify,
go!", second session of the day), after the finding was explained with the
three options (keep as is / reuse `timeout` / add a code) and "add a
root-level retryable class" accepted. Transcribed. Drafted from the Rust
AUTH-3/4 implementation (`lm15-rs` 05de988), which had to choose a class
for a failure the vocabulary did not name.

## What this changes

One code, one class, one AUTH-6 sentence, two implementation edits:

1. **The vocabulary.** `spec/vocabularies.md` § ErrorCode gains
   `lock_timeout` → `LockTimeoutError`, a root-level class beside
   `TransportError` (not under `ProviderError`: no provider was asked;
   not under `ConfigurationError`: nothing is misconfigured; never an
   `AuthError`: nothing is wrong with the credential). It joins the
   retryable set and carries `path` (the guarded file) and `lock_path`.
2. **AUTH-6.** `spec/auth.md` names the class instead of "a local timeout
   error type", and allows a language with a native timeout type to
   subtype it additionally, never instead.
3. **The reference.** `lm15/errors.py` `LockTimeoutError`;
   `lm15/_authlock.py` `CredentialLockTimeout(LockTimeoutError,
   TimeoutError)` — inside the family for `except LM15Error`, still a
   builtin `TimeoutError` for code written before the code existed;
   `ErrorCode` in `lm15/types.py`; `RETRYABLE_ERRORS`.
4. **The Rust port.** `Lm15Error::LockTimeoutError(LockTimeout)`;
   `AuthError::LockTimeout` maps to it (it had mapped to `TimeoutError`,
   a stated misfit).

## Why

- The family's promise is that every failure lm15 produces is an
  `LM15Error` with a code a caller can switch on. The reference's
  `CredentialLockTimeout` was a bare builtin `TimeoutError`: a caller's
  `except LM15Error:` missed it and crashed. The gap was in the contract,
  so the fix is here, not per port.
- Where the class sits is the substance. A lock wait and a provider 504
  have different fixes (clear a stale lock; nothing you can do), so they
  need different codes; reusing `timeout` would have a dashboard counting
  lock waits as provider timeouts. It is local and transient like
  `TransportError`, so it is that class's sibling, and retryable so a
  caller that only does "if retryable, back off" handles it unnamed.
- Rarity is not the criterion for a code; whether a caller must tell it
  apart is.

## Considered and rejected

- Keep as is: Python outside the family, Rust misstating a provider
  timeout, the two ports disagreeing.
- Reuse `timeout` officially: redefines a provider-side code (408/504) as
  also meaning a local one.
- A generic `local_timeout`: a code names a failure the caller can act
  on; "the credential lock timed out; retry, or clear a stale lock" is
  that failure. Specific wins.

## Evidence

- No harness direction can drive lock contention (it is not a wire
  exchange); each implementation pins it in its test suite
  (`lm15-python/tests/test_errors.py`, `test_auth_hardening.py`;
  `lm15-rs/src/auth/lock.rs`, `tests/login_refresh.rs`).
  `tools/spec_drift.py` keeps `ERROR_CODES` and the spec in step.

## Trade-offs, stated

- One more code and class in every port. Small, and the alternative was a
  promise broken in one language and a lie in another.
