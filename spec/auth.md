# spec/auth.md — credential resolution, refresh, storage, secrecy

**STATUS: RATIFIED 2026-08-31.** These rules are normative for every lm15
implementation. The reference implementation (lm15-python `auth.py`,
`authkit.py`, `doctor.py`) implements them; `auth/resolution.json` pins the
AUTH-1/AUTH-7 behavior as fixtures; ports are held to them.

Scope: how an lm15 implementation finds, refreshes, stores, and explains
credentials. lm15 does not own interactive login: applications do. These
rules cover everything around that boundary.

## AUTH-1 — Credential policy and resolution order

Every provider declares exactly one credential policy in its manifest
(`credential_policy`). Routers, doctors, and shims derive their behavior
from the declaration — never from a hardcoded provider-name list, which is
a second copy of the same fact and will drift (amended 2026-09-01):

- **`key`** — the ordinary chain below supplies the credential.
- **`oauth`** (`claude-code`, `openai-codex`) — the provider resolves
  **only** its local CLI credential file; the chain below never runs. In
  particular (stored-credential-owns-provider): a failed OAuth load or
  refresh never falls back to an environment variable silently. An `oauth`
  manifest declares no environment keys.
- **`key-then-oauth`** (`xai`) — the ordinary chain first; when it yields
  nothing, the stored local OAuth credential is the final rung. Stated
  trade-off: a configured key silently beats a stored subscription login,
  which can move billing from subscription (prepaid) to per-token.
  Explicit-beats-ambient is the rule everywhere in lm15; the doctor
  (AUTH-7) makes the winning rung visible.

For a `key` or `key-then-oauth` provider constructed through the router,
the credential resolves in exactly this order; the first hit wins and later
rungs are dead:

1. an explicit `api_keys` entry for the provider (static value or
   credential-provider callable);
2. the provider's declared environment keys, in declared order, first
   non-empty value;
3. for local-server presets only: the preset's placeholder key;
4. for `key-then-oauth` providers only: the stored local OAuth credential
   (AUTH-8 store paths), usable when fresh or refreshable.

## AUTH-2 — Credential providers

Every implementation exposes a credential-provider shape native to its
language (zero-arg callable in Python/TS/Julia, single-method interface in
Go/Rust). The adapter invokes it once per request at request-build time and
never caches the returned value; caching belongs to the provider itself.

## AUTH-3 — Refresh state machine

For refreshable OAuth credentials:

- an expiry skew of five minutes: a token inside the skew window counts as
  expired for refresh purposes;
- refresh is double-checked: acquire the cross-process lock, re-read the
  stored credential, and skip the network refresh when the re-read
  credential is fresh (another process refreshed while we waited);
- the network refresh executes while holding the lock. Trade-off, stated:
  one slow refresh stalls sibling processes up to the lock timeout; the
  alternative double-spends rotated refresh tokens, which forces re-login;
- an expired credential without a refresh token, or a failed refresh,
  raises the typed auth error carrying the provider id and a re-login hint
  naming the exact command. Never a raw traceback, never a silent fallback.

## AUTH-4 — Storage semantics

- Credential files are written atomically: temp file created private,
  fsynced, renamed over the target. A reader observes a complete old file or
  a complete new file, never a partial one.
- Credential files and their temp files carry mode 0600 where the platform
  supports it.
- Writes are serialized by an advisory cross-process lock scoped to the
  credential file's canonical path.
- Lock files live in an lm15-owned directory, never inside another tool's
  directory (`~/.claude`, `~/.codex` are foreign territory).
- Stated limitation: the lock is cooperative among lm15 processes. Foreign
  writers do not take it; AUTH-3's double-checked re-read is the mitigation.

## AUTH-5 — Secrecy invariant

Token and key material never appears in: reprs, exception messages,
exception reprs, doctor reports, log output produced by lm15, or any fixture
expectation in this corpus. Fixtures plant the sentinel
`SECRET-SENTINEL-DO-NOT-PRINT` as credential values and assert its absence
from every rendered surface. `tools/check_secrecy.py` enforces the corpus
side; each implementation enforces the runtime side in its test suite.

## AUTH-6 — Error taxonomy

- Missing/unreadable/malformed credential sources → the implementation's
  `NotConfiguredError` equivalent, carrying `provider` and a
  `credential_hint` that names the fix (`export GROQ_API_KEY=...`,
  ``run `codex login` ``).
- Expired-and-unrefreshable or provider-rejected credentials → `AuthError`
  equivalent, same hint discipline.
- Lock contention → a local timeout error type, deliberately **not** an
  `AuthError`: nothing is wrong with the credential.

## AUTH-7 — Explainability (doctor)

Every implementation ships an `explain_auth` equivalent that:

- walks exactly the AUTH-1 chain (divergence from real construction is a
  bug, testable against `auth/resolution.json`);
- performs no network I/O;
- reports each rung as `selected`, `shadowed` (usable but beaten by an
  earlier rung), or `absent`;
- never includes secret values in its output. Presence checks may read
  values into memory; they must not retain or render them.

## AUTH-8 — Well-known paths

- lm15-owned credential store: `$LM15_CREDENTIALS_PATH`, else
  `$XDG_CONFIG_HOME/lm15/credentials.json`, else
  `~/.config/lm15/credentials.json`.
- Lock directory: `$LM15_LOCK_DIR`, else `$XDG_CACHE_HOME/lm15/locks`, else
  `~/.cache/lm15/locks`.
- Borrowed files: `~/.claude/.credentials.json` (Claude Code),
  `~/.codex/auth.json` (Codex CLI), and `~/.pi/agent/auth.json` (Pi agent
  store, read for xAI when present). These formats are wire-fact-like:
  owned by foreign tools, revalidated against reality, never "cleaned".
- The lm15-owned store's xAI entry is
  `{"xai": {"type": "oauth", "access", "expires" (ms), "refresh"?}}`;
  refreshes write back to whichever file the credential came from, because
  xAI rotates refresh tokens.

## AUTH-9 — Login-flow primitives

Every implementation exposes one uniform login entry point
(`login(provider)` or the language's idiomatic equivalent; added
2026-09-01). It runs the login flow lm15 owns for that provider (today:
xAI's device-code flow) and returns the stored credential. For every other
provider it fails with the implementation's unsupported-feature error
naming the exact fix: the foreign CLI command that owns the flow
(`claude` `/login`, `codex login`) or the console URL where an API key is
created. Console URLs are guidance strings, not wire facts: drift costs a
stale hint, never broken inference. The entry point must not prompt, open
a browser, or spend money except in the one flow explicitly requested.
Provider-named login functions may exist as the concrete flows underneath;
the uniform door dispatches to them.

Implementations that ship login primitives (PKCE, RFC 8628 device polling,
loopback callback listener, credential store) follow:

- PKCE: S256 only; the RFC 7636 Appendix B vector is a required test.
- Device polling: `slow_down` grows the interval by 5 seconds unless the
  server names an interval; expiry is a typed error distinct from denial.
- Loopback listener: binds `127.0.0.1` only; wrong path or wrong state gets
  an error page and the wait continues; a provider `error` parameter ends
  the wait as a typed failure; authorization codes are repr-suppressed.

---

Ratified-by: Maxime Rivest, 2026-08-31 — assented in session ("I ratify");
transcribed.

Amended 2026-09-01 (AUTH-1 credential policy declaration; AUTH-9 uniform
login entry point; xai key-then-oauth fixtures) — ratified in session
("implement all three!"); see changes/2026-09-01-credential-policy.md.
