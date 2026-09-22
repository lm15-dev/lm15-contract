# Managed authentication — what needs your yes or no

**RATIFIED 2026-09-22. The maintainer edited R10–R12, then confirmed:
“ok, i just changed that but otherwise i ratify.” R1–R12 and the supporting
core recommendations are accepted. Reserved details are not ratified.**

The specification is split in two: [core](../spec/auth-managed.md) (ratified, gates the
first two implementations) and [reserved](../spec/auth-managed-reserved.md)
(design notes; each says what must exist before it binds anyone). This page is
about the core.

## Subscription access comes first

- An explicitly selected key or named cloud identity is deliberate authority;
  use it, never replace it with a discovered account.
- Otherwise prefer subscription access over ambient API keys. If several accounts
  are eligible, ask rather than guess whose account to use.
- Failed renewal, expiry or logout must not silently switch to a metered key.
  With no subscription available, the connection helper offers API-key use as an
  explicit choice. Existing API-key/Azure-only callers remain supported.
- Login success alone does not prove subscription entitlement, included usage or
  freedom from extra charges. Provider permission and actual billing behavior
  require separate evidence.

**This correction supersedes the earlier R1/R2 retirement proposal**, including
conflicting statements in the linked core, decision log and fixture-transition
notes. The companion specification, decision log and scenarios have been aligned
with this correction; none authorizes removing current subscription access
before R1's evidence gate passes.

## Protect existing access while improving login

| # | Decision | What you give up | Yes / No |
|---|---|---|---|
| **R1** | **Keep existing Claude Code/Codex subscription access until a replacement is demonstrated.** LM15-owned login remains a goal, not a proven substitute. Before retiring either existing path, establish provider-permitted use and demonstrate login → inference → renewal with the intended account access and billing behavior, separately for Claude and Codex. | Temporary coexistence and provider-specific work. Do not copy rotating refresh tokens into independent stores or claim LM15's locks coordinate foreign tools. If safe coexistence cannot be established, stop and review—not remove access or claim certainty. | Confirmed direction |
| **R2** | **Preserve subscription-first selection, including xAI.** An explicitly selected key wins; otherwise subscription access wins over ambient keys. Migrating xAI's device flow must preserve that behavior, regardless of internal policy names. | An environment key alone does not override an available subscription. Choosing API-key use explicitly still works. | Confirmed direction |
| **R3** | **Never silently switch billing sources after subscription failure or logout.** Report the actual problem and offer deliberate recovery or explicit key selection; do not silently charge an ambient key or use the machine's cloud identity. | A request may stop rather than use a different billing source. Existing API-key/Azure-only callers remain supported. | Confirmed direction |

## Ratified decisions that shape the new API

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
| **R10** | **Which SDKs must implement this?** The draft says all ten: Python, TypeScript, Rust, Go, R, Julia, Java, .NET, Ruby, Swift. Your project memory lists "which language ports are committed deliverables" as still open. | Starting with python and typescript. | yes |
| **R11** | **Which provider logins are the initial inventory?** Draft: Claude, Codex, Copilot, xAI, Kimi Code, Meta, OpenRouter, Radius. Gemini CLI and Antigravity excluded. | Those eight. | yes |
| **R12** | **Sequencing proposal.** Review the core first; reserved details need explicit promotion. Preserve existing access while proving xAI migration and Claude/Codex-owned login, then expand. Correct the spec when provider evidence contradicts it; no cutover before R1's evidence gate. | Ratified sequence; reserved details still need promotion. | yes |

## Supporting recommendations (ratified for the core)

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
