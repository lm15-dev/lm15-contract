# 2026-08-31 — auth contract: spec, resolution fixtures, secrecy gate

Adds the credential-resolution/refresh/storage/secrecy domain to the
contract. `spec/auth.md` landed as DRAFT and was **ratified the same day**
(session assent: "I ratify"; transcribed in spec/auth.md and in the
AUTHORITY.md re-ratification line, which now names spec/auth.md in the
canonical-facts precedence). The filename keeps its original `-draft`
suffix as honest history of how it landed.

## What lands

- `spec/auth.md` (ratified 2026-08-31) — rules AUTH-1..AUTH-9: resolution order,
  credential-provider interface shape, double-checked locked refresh,
  atomic 0600 storage, the secrecy invariant, error taxonomy, the
  explain_auth ("doctor") requirement, well-known paths, login-flow
  primitive semantics (PKCE S256, RFC 8628 polling, loopback listener).
- `auth/resolution.json` — hand-authored, language-neutral fixtures for the
  AUTH-1 chain as observed through AUTH-7 explain output. Canonical facts;
  spec citation: AUTH-1/AUTH-7. Also mirrored (per the Stage-2
  dual-landing rule from the 2026-06-09 migration entry) at
  `lm15-python/conformance/auth_resolution.json`.
- `tools/check_provenance.py` — now also scans `auth/`.
- `tools/check_secrecy.py` — new CI gate for AUTH-5: the planted sentinel
  may never appear inside an expectation block, and no corpus file may
  contain material matching known live-credential shapes. Verified clean
  against the existing corpus (703 files) at landing time.

## Reference implementation (lm15-python), same date

- `lm15/_authlock.py` — advisory cross-process lock (lm15-owned lock dir,
  never inside foreign tool directories) + atomic private JSON writes.
- `lm15/auth.py` — refresh now runs under the lock with a double-checked
  re-read; public writers lock; all writes atomic; lock contention raises
  `CredentialLockTimeout` (a TimeoutError, deliberately not AuthError).
- `lm15/authkit.py` — PKCE (S256, RFC 7636 Appendix B vector pinned),
  device-code poller (RFC 8628 slow_down/expiry semantics), loopback
  callback listener (127.0.0.1 only), `CredentialFileStore` (locked,
  atomic, 0600, serialized `mutate`).
- `lm15/doctor.py` — `explain_auth`: the AUTH-7 report.
- `tests/test_auth_hardening.py` — 42 tests, hermetic; runs the mirrored
  fixture file via `tests/test_auth_resolution_contract.py`.

## Evidence class

Everything here is a **canonical fact** (no provider wire behavior is
claimed), so the required evidence is a spec citation: the rules in
`spec/auth.md`, authored and ratified in the same commit. The two borrowed credential
file formats (`~/.claude/.credentials.json`, `~/.codex/auth.json`) were
already read by the reference implementation before this entry; their
shapes are treated as wire-fact-like and revalidated there, not here.

## Explicit trade-offs (recorded so they are never absorbed silently)

1. Refresh holds the lock across the network call: a slow refresh can stall
   sibling lm15 processes up to the lock timeout. Rejected alternative
   (refresh outside the lock) double-spends rotated refresh tokens and
   forces re-login, which is worse.
2. The lock is advisory and lm15-cooperative only; the Claude Code and
   Codex CLIs do not take it. Mitigation is the double-checked re-read,
   not mutual exclusion.
3. `explain_auth` tests env vars for presence, so secret values transit
   process memory (the router's `resolve()` never reads values). They are
   never retained or rendered.
4. The live-secret scan uses specific prefixes, not entropy heuristics:
   fewer catches, near-zero false positives. A gate that cries wolf gets
   ignored.
5. Ports (Go, Rust, TypeScript, Julia) are NOT updated by this entry. With
   the spec now ratified, the ports are formally behind the contract on
   this surface until they implement AUTH-1..AUTH-9 against
   `auth/resolution.json`.
