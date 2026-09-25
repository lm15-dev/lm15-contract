# 2026-09-25 — Managed authentication in every SDK, and one test for all of them

**Status: DECISION (maintainer, 2026-09-25) + harness direction. Amends the
R10 scope in AUTH-26.**

## Decision

The maintainer asked for full feature parity between Python, TypeScript,
Rust and Go, sign-in included. R10 made Python and TypeScript the first
implementations and left the others as "follow-up decisions"; this is that
decision. Every SDK implements the ratified managed-authentication core
(AUTH-12–26): the store of store-layout.md, `Auth` (discovery, login,
configure, status, logout, cancel, verify, request-time resolution with
renewal), the provider flows of the inventory, bound clients and model
choices, the managed router mode (AUTH-15 mode B) and doctor, and the
interactive `connect()` with a terminal UI.

Nothing else changes: the rules, the store layout and each method's
availability (`supported` / `unverified` / `unavailable`) are the same in
every language. A port does not promote a method because it was written;
AUTH-26's evidence levels apply per SDK and per platform.

## Why a harness direction first

Three re-implementations of a state machine with durable markers,
generations and uncertain exchanges drift unless the same cases grade all
of them. `auth/managed/README.md` already required a separately reported
managed direction before support could be claimed; `harness/managed.py`
is that direction and `auth/managed/runs/core.json` its first 42 cases:

- the xAI device flow (pacing, slow_down, denial, provider expiry, the
  attempt deadline), renewal (success, rejection, timeout → indeterminate,
  5xx and refused → kept), legacy entries (read-only, renewed, replaced);
- slots: connection_exists, connection_changed, replacement, logout with
  the R3 marker, logout by an old id, pinned selections;
- recipes: API key, environment variable (set and unset), local server,
  named cloud identity, missing fields;
- store integrity: not JSON, unknown version, duplicate members, a
  non-object entry — never read as empty, never overwritten;
- Claude's hosted return (PKCE, state, paste validation, rejected
  exchange, cancellation), ChatGPT device login, GitHub Copilot (device,
  token exchange, host validation, re-mint), Kimi Code (a 429 renewal keeps
  the credential), Meta (key mint, permanent mint rejection);
- the managed doctor, `cancel_login`, discovery of every provider's
  methods.

Loopback-callback flows are not in the direction: whether a sandbox can
bind 127.0.0.1 is the machine's property, not the SDK's. Each SDK tests its
listener in its own suite (real sockets), as Python's does.

Expectations were captured from lm15-python and reviewed case by case
against AUTH-12–26. Where a port disagrees, the port is wrong unless a
`changes/` entry shows the reference was.

## What a case compares

One outcome per step, the ordered trace (prompts, notices, auth HTTP
requests with their bodies and headers, waits), and the store file
afterwards. Before comparing, the harness fails the case if the sentinel
reaches a public outcome, prompt or notice, if PKCE's challenge is not the
S256 of the verifier sent, or if the state sent to the token endpoint is
not the authorization URL's. It then renames random ids by first
appearance, masks random OAuth values and compares numbers by value (the
store is written by four languages; JavaScript has one number type).

## Stated limits

- Mixed-language races on one store file (AUTH-26 level 2) are separate
  process tests, not this direction.
- Descriptor prose (labels of methods, notice text) is not compared;
  connection labels are, because they are stored and shown.
- No live receipt follows from this. Live evidence remains per provider,
  per platform, with a person at the browser.

## Reference corrected while writing the cases

- **An invalid pasted return no longer ends the sign-in (Python).** AUTH-18
  says a wrong return "receives a generic rejection and does not terminate
  the legitimate wait", and AUTH-24 describes `invalid_login_state` as
  "reject input, preserve legitimate wait". lm15-python ended the attempt
  with `invalid_login_state` on a pasted return with the wrong state, a
  wrong URL, or a bare code the profile refuses; lm15-ts already told the
  person and asked again. Python now does the same (the listener, when
  there is one, keeps listening). `claude-wrong-state` pins the recovery;
  `claude-bare-code-refused` pins the second prompt.
