# Managed authentication — what needs your yes or no

**2026-09-22. One page. Answer each line; everything not listed here has one
obvious answer and was decided for you (see the
[decision log](2026-09-22-managed-authentication.md)).**

The draft is split in two: [core](../spec/auth-managed.md) (ratify now, gates the
first two implementations) and [reserved](../spec/auth-managed-reserved.md)
(design notes; each says what must exist before it binds anyone). This page is
about the core.

## Decisions that change what LM15 does today

| # | Decision | What you give up | Yes / No |
|---|---|---|---|
| **R1** | **Python stops borrowing Claude Code and Codex CLI logins.** Today `claude-code` and `openai-codex` read `~/.claude/.credentials.json` / `~/.codex/auth.json`. The draft retires that: LM15 runs its own login and keeps its own store. No importer. | Those two routes stop working until LM15's own Claude/Codex login ships (stages 3–4). A later "import from CLI" is a separate design, if ever. | |
| **R2** | **xAI's existing device-code login is migrated, not kept.** Same user experience, new machinery underneath; the `oauth-unless-explicit` policy (stored login beats env key) is retired. With managed Auth attached: explicit key > saved connection, and **no** fall-through to env keys. Without it: ordinary key rules. | The "subscription beats ambient key" convenience for xAI users who set both. They now choose by attaching Auth or passing the key. | |
| **R3** | **Attaching managed Auth turns off ambient fallback entirely.** After logout or a failed renewal, a managed router fails `login_required`; it never picks up an env key or the machine's cloud identity. API-key/Azure users who never attach Auth are untouched. | Some availability: a stale login means an error, not a silent switch to a paid key. | |

## Decisions that shape the new API

| # | Decision | Alternative rejected | Yes / No |
|---|---|---|---|
| **R4** | **`connect()` returns a client pinned to one connection ID + one model.** Replacing the account later makes the old client fail `connection_changed`; it never follows the new identity. | Client follows "current account" — a CSV job could change who pays mid-run. | |
| **R5** | **One active connection per (scope, provider instance, binding) in v1.** Personal + work on the same provider = two scopes or two configured instances. No account picker inside one slot. | Multi-account arbitration now, before the basic contract is proven. | |
| **R6** | **A finished login is saved before the model picker runs.** Cancel the picker and the login stays; `connect()` is not one atomic wizard. | Roll back the login — throws away a grant the user just approved, and can't really revoke it remotely anyway. | |
| **R7** | **Cancel cannot undo a commit; an uncertain token exchange is never retried blind.** If a crash/timeout happens after a one-use code was sent, the user signs in again. | Retry on network error — can spend a rotated refresh token twice and break the account for good. | |
| **R8** | **New error type `AuthOperationError` (`code="auth_operation"`) with 15 closed reasons**, separate from HTTP 401s and never auto-retried. | Reuse existing auth errors — mixes "store unreadable" with "provider rejected you" and inherits retry behavior. | |

## Numbers (defaults; change them if you disagree, they are not load-bearing)

| # | Value | Yes / No |
|---|---|---|
| **R9** | Login attempt lifetime **15 min**; device poll interval provider's or **5 s**, `slow_down` adds ≥5 s; network exchange and lock wait **30 s** each; renewal due at `expires_at − min(5 min, lifetime/10)`. | |

## Scope questions the draft assumed but you never said

| # | Question | Draft assumed | Yes / No |
|---|---|---|---|
| **R10** | **Which SDKs must implement this?** The draft says all ten: Python, TypeScript, Rust, Go, R, Julia, Java, .NET, Ruby, Swift. Your project memory lists "which language ports are committed deliverables" as still open. | All ten. | |
| **R11** | **Which provider logins are the initial inventory?** Draft: Claude, Codex, Copilot, xAI, Kimi Code, Meta, OpenRouter, Radius. Gemini CLI and Antigravity excluded. | Those eight. | |
| **R12** | **Sequencing.** Core is ratified now; the reserved file binds nobody until its trigger is met. Implementation order: xAI migration → Claude browser login → then the rest. The spec is corrected wherever those two contradict it. | Yes. | |

## What was decided for you (no action)

Explicit scope, no global current account; login returns metadata not tokens;
UI is an adapter with `prompt`/`notify`; PKCE S256 + state, loopback-only
listeners, no client secret in public apps, TLS mandatory; secrets never in
repr/logs/errors; stores are versioned (v1), decimal-string revisions, atomic
commit and atomic logout; keys typed in a form are literal text; `verify` is
explicit and can be metered; descriptors are data, not authority; four evidence
levels before any "supported" claim.

## Deferred on purpose (reserved file — no decision needed now)

Resuming a login across processes/requests (web servers); database and
lease-based stores and their invariants; relay consent; per-environment profile
table (SSH, GUI, mobile, serverless); remote provider definitions and instance
security revisions; serialized `ModelSelection` for rebinding in another process.
