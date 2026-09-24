# 2026-09-22 — Managed authentication: Python implementation record

**Status: implementation of the ratified core (AUTH-12–26, R1–R12) in
lm15-python. Offline conformance green; live receipts still owed per
provider. No support-matrix promotion.**

lm15-python (see its CONTRACT_PIN for the contract revision) implements the core
in `lm15/login/` (`Auth`, `AsyncAuth`, store, engine, flows, `TerminalUI`,
`BoundClient`, `model_choices`), `lm15/interactive.py` (`connect()`),
`RouterConfig(auth=...)` (AUTH-15 mode B), the doctor's managed walk, and
`AuthOperationError` (AUTH-24). `lm15.auth.login_xai` now runs the managed
xAI flow: one implementation, one store entry (R12's xAI migration).

## Decisions taken while implementing (each with the objection it answers)

| # | Decision | Rejected alternative and why |
|---|---|---|
| P1 | **One store file.** The managed store is AUTH-8's `~/.config/lm15/credentials.json`, provider entries in the shape the legacy xAI login and Pi already use, plus one non-secret `_lm15` block (version, per-slot generation, revision, renewal marker, logout marker, display metadata). | A second file would have forced either a copy of xAI's rotating refresh token (two owners — forbidden by R1) or a plain `LMRouter()` that cannot see a `connect()` login. The reserved `auth-store.schema.json` describes a different layout; it is a design artifact and is **superseded** by this one for Python. It must be re-derived from what two implementations needed before promotion (AUTH-25 reserved), not the other way round. |
| P2 | **Legacy entries read as connections.** An entry without a slot record is generation `1`, id `legacy-<provider>`; the record is written on the first managed commit. | Rewriting untouched files on read would violate "unknown formats are never overwritten". |
| P3 | **Claude Code / Codex CLI logins are external-source connections** (`external:claude-code-cli`, `external:codex-cli`, `external:pi-xai`): the material stores a source *name*; the request path calls the legacy locked loaders; logout removes the recipe and never touches the CLI file. | Copying tokens (forbidden). Refusing to offer the proven path in `connect()` (would make R1's preservation invisible to the user). |
| P4 | **LM15-owned Claude/Codex/OpenRouter/Meta/Kimi/Copilot logins are `unverified`**: implemented, excluded from the default picker, explicit `allow_unverified=True` to try. xAI device login is `supported` on the strength of the 2026-09-01 live validation of the identical protocol through `lm15.auth`; a managed-path receipt is still owed. | Marking them supported from code alone is the registration-table support claim AUTH-26 forbids. |
| P5 | **`kimi-code` and `github-copilot` are declared providers, not registry rows.** They route only when a managed `Auth` is attached (the only way to hold their credential) and answer `Resolution.declared = True`. | A registry row is a receipted support claim; neither has a wire receipt. |
| P6 | **Radius: descriptor only, `unavailable`.** | Its gateway wire protocol is not in lm15-python; login without inference would advertise a model connection that cannot make a request. |
| P7 | **Copilot model-policy enablement is not performed during login** (Pi does it). | AUTH-17/D17: login must not change account settings. A future explicit operation may. |
| P8 | **Sync `Auth`; `AsyncAuth` runs each operation in a worker thread.** | A coroutine that does blocking network I/O on the loop would be a lie; a full async re-implementation doubles the surface before the first receipt exists. The adapters' per-request credential callable is sync, as the existing subscription adapters already are. |
| P9 | **Uncertainty classification** (AUTH-20.6): a refused connection or DNS failure never reached the provider (safe: credentials kept); a timeout or a dropped connection after sending is `indeterminate` (durable marker kept; `commit_state=unknown`; user signs in again). | Treating every network error as retryable can spend a rotated refresh token twice. |
| P10 | **R3 in the legacy chain.** `oauth-unless-explicit` now has four stored states: `usable` (login wins), `unusable` / `logged_out` (the env key is **blocked**; the error names the login and says the key is used only when passed explicitly), `absent` (env chain as before). Third-party adapters that only implement the older boolean probe still work. | The old rule rescued an expired login with the env key — the exact silent billing switch R3 forbids. |
| P11 | **Renewal lead** = `min(300 s, lifetime/10)` computed from actual expiry + `issued_at`/`lifetime_s` written by managed flows; the legacy reader applies the same lead when it sees `issued_at`, so both paths agree on "due" for one entry. | Storing a pre-skewed expiry (the old habit) double-counts skew and makes short tokens perpetually due. |

## What the fixture changes were

- `lm15-python/conformance/auth_resolution.json` mirrors the corrected contract
  fixture (`xai-unusable-login-blocks-env`). Python now passes it.
- `CONTRACT_PIN` advanced to the ratified contract commit; `harness/check.py
  --shim python --direction all` is green (auth 43/43).

## Evidence levels reached (AUTH-26)

| Level | State |
|---|---|
| 1. Specification and artifact checks | done (this repository) |
| 2. Deterministic fake-provider/store/clock tests | done for Python: `tests/test_login.py`, 36 scenarios (MA-001–007, 011–014, 016, 019, 025–029, 032–033, 036–037, 040–041, 043–044, 054–055, 058–060, plus the R3 legacy boundary and the doctor) |
| 3. Real browser/native UI integration | **not done** — the loopback listener is exercised with real sockets; no real browser round-trip |
| 4. Authorized live login → inference → renewal receipts | **not done for any managed-path method.** xAI's protocol has the 2026-09-01 receipt through the legacy entry point only |

Nothing here moves a provider row to "supported" in the support matrix.

## Still owed

- Live receipts, per provider, with a person at the browser: xAI (managed
  path), then Claude and Codex LM15-owned logins — each also needs the
  provider-permission question answered before promotion (R1).
- Mixed-language shared-store race tests (once TypeScript exists).
- The reserved store schema and its vectors: re-derive from the Python layout
  and the TypeScript one, then promote or retire.
- TypeScript implementation (R10).

## Update 2026-09-24

The evidence table above describes 2026-09-22. Level-4 native observations made
on 2026-09-22/23, the later Python changes (hosted Claude login, the corrected
Claude client id, auth identification and diagnostics, reservation release on
interrupt) and the provider profiles now moved into the contract are recorded in
[2026-09-24-managed-auth-profiles-and-browser-track.md](2026-09-24-managed-auth-profiles-and-browser-track.md).
