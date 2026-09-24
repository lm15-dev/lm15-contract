# 2026-09-24 — Managed auth: provider profiles, the shared store layout, the 09-23 Python changes, and the browser track

**Status: records and clarifications applied; the relay-consent promotion (§6) is
PROPOSED and awaits ratification. No support-matrix promotion.**

## Why

Before TypeScript implements managed login (R10), three things that existed only
inside lm15-python had to move into the contract, because a port that copies them
from Python makes Python the oracle, which AUTHORITY.md forbids:

1. every provider's client id, URLs, parameters and return rules;
2. the exact file layout two languages must share under one lock;
3. what changed in Python on 2026-09-22/23 after the implementation record was
   written, and what was observed live.

A fourth reason: the next step is exploring which logins work from a web page (the
playground), including through the playground relay. The relay's reserved consent
rule names that exact extension as its promotion trigger.

## 1. Provider profiles — `auth/managed/profiles.json`

One entry per provider route, one method per way of signing in, with the wire
parameters, PKCE/state sizes, return-URI rules, device-poll vocabulary, token
material, inference binding and dated native evidence. Values are what
lm15-python@365cbca sends. The Claude client id is the corrected one (see §3).
AUTH-18 now points at this file (§ Provider profiles and identification).

Every value was copied from the Python flows and read back against them; the
Python flows themselves are the implementation, not the authority, from now on.

## 2. The shared store layout — `auth/managed/store-layout.md`

The v1 document Python writes: provider entries in the legacy/Pi shape plus the
non-secret `_lm15.slots` records (generation, connection id, revision, state,
renewal marker, attempt reservation, logout marker, verification, previous ids),
with units and legacy-entry rules. It is binding on the second implementation
and becomes a normative AUTH-25 rule after mixed-language race tests pass. It
supersedes the reserved `auth-store.schema.json` for the file store, as
implementation record P1 already said. AUTH-25 now points at it.

## 3. Python changes after the 2026-09-22 implementation record

| Commit | Change | Contract effect |
|---|---|---|
| ff26085 | Any exit from `login()` without a commit releases the slot's attempt reservation (Ctrl-C at a prompt used to leave it reserved for 15 minutes) | Conformance fix to AUTH-19 as written; recorded in store-layout.md (`attempt`) |
| 365cbca | Claude client id corrected from `…-44d5-…` to `…-44d9-…` (transcription error) | profiles.json. **lm15-ts still carries the wrong id** in `src/auth/stores.ts` (external Claude Code renewal): a port bug to fix |
| 365cbca | Claude `browser` now uses Claude's hosted code page (`claude.com/cai/oauth/authorize` → `platform.claude.com/oauth/code/callback`), paste `code#state`; no listener, so the browser may be on another machine. The localhost flow stays as method `loopback` | profiles.json (two methods) |
| 365cbca | Pasted returns: a full URL must match the registered URI's scheme, host, effective port and path; no userinfo or fragment; duplicate parameters, code+error together, wrong or missing state are rejected; a wrong-state error never ends the legitimate attempt as denied | Already required by AUTH-18 § Browser and OAuth protections; Python now conforms |
| 365cbca | Auth HTTP sends `User-Agent: lm15/<version>` | AUTH-18 identification paragraph (clarification) |
| 365cbca | Failed exchanges report status, response-format category, recognized OAuth code, explicit challenge flag; never provider text | AUTH-24 diagnostics paragraph (clarification of AUTH-21's existing boundary) |
| 365cbca | Method descriptions record the 09-22/23 live observations | §4 |
| 9100305, 6c081a1, 3f86e3d | Tool derivation removed; Codex cap refused | Already recorded (2026-09-23 changes) |

## 4. Evidence levels now reached (native, lm15-python)

Observed by a person on 2026-09-22/23; redacted notebook lm15-python
`docs/cookbooks/21-managed-login-live.md`. These are level-4 observations for the
native terminal platform. They are not yet contract receipts (no exchange hashes)
and move no method to `supported`: provider permission and billing are unanswered
for every account method except xAI.

| Provider / method | Observed | Still open |
|---|---|---|
| xAI device | managed login, inference, streaming, logout blocking the env key, fresh-process persistence, one early renewal | — (`supported`) |
| Claude browser (hosted) | login, inference, fresh-process persistence, one early renewal | permission, billing; unattended full expiry |
| Claude loopback | nothing | everything |
| Codex browser | login, catalog, inference, fresh-process persistence, one early renewal | permission, billing |
| Codex device | login, inference (memory-only) | persistence, renewal, permission, billing |
| OpenRouter browser | key issuance, limit inspection, catalog, inference, fresh-process reuse | broader review |
| Copilot device | login, Copilot token, catalog (59 models), inference, persistence, one early renewal | permission, billing |
| Kimi Code, Meta | nothing | everything |

This supersedes the "not done for any managed-path method" row of the
2026-09-22 Python record's evidence table.

## 5. The browser track — `auth/managed/browser.json`

AUTH-22: a native pass is not a browser pass. `tools/probe_auth_cors.py` sends,
with `Origin: https://lm15.dev`, what a page would send to every endpoint a
browser flow touches (preflight, then an invalid harmless request) and records
whether the reply is readable. First run, 2026-09-24:

| Provider | Sign-in / renewal | Catalog | Inference |
|---|---|---|---|
| xAI | relay (auth.x.ai sends no CORS) | direct | direct |
| Claude | relay (token endpoint: no CORS) | direct | direct |
| Codex | **direct** (auth.openai.com: `*`, device and token) | relay | relay (chatgpt.com) |
| Copilot | relay (github.com device/token); Copilot token direct only without the Editor-* headers | direct | direct |
| OpenRouter | direct (known live since 2026-09-11) | direct | direct |
| Kimi Code | **direct** (auth.kimi.com: `*`) | — | relay (api.kimi.com/coding) |
| Meta | relay (auth.meta.com, key mint) | — | direct |

What a page can do per delivery mode (AUTH-22 reserved "Web page" row): no loopback
listener; manual return works (Claude hosted page; Codex's failed `localhost:1455`
page, whose address bar holds the return URL); page redirect works where the
provider accepts an arbitrary return (OpenRouter); every device flow works.

Known platform limits: a page cannot send `User-Agent` (Claude Code's
`claude-cli/<v>` inference header, Copilot's `GitHubCopilotChat/…`); whether a
provider requires it is exactly what the page receipts must establish.

This table is a hypothesis for the page exploration, not a support claim.
Receipts from the real page are appended to `browser.json` `receipts`.

## 6. Relay consent — PROPOSED promotion of AUTH-21 (reserved)

Trigger met: the playground relay is to forward managed-login and subscription
traffic, not only TypeSafe. Proposed core text, re-read against that
implementation:

1. **Consent is scoped** to (relay origin, provider route, stage). Stages:
   `auth` (authorization, device start and polling, code exchange, renewal, key
   mint), `catalog`, `inference`. Consent to one stage never covers another; a
   changed relay origin needs new consent.
2. **Consent is a person's explicit act** in the application's UI, given after the
   UI says, in words: who operates the relay; that it keeps no logs; and what
   crosses it. For `auth`: authorization codes, PKCE verifiers, device codes,
   access and refresh tokens, which let the operator act as the user until
   sign-out or revocation. For `inference`: the access token or key, prompts and
   replies. For `catalog`: the token.
3. **No automatic fallback.** An SDK never reroutes through a relay on its own. A
   direct request that fails the way a CORS refusal looks is reported as a
   transport failure; the application may then ask for consent.
4. **Configuration is explicit per stage.** An SDK takes the relay as a
   per-stage routing choice in its configuration; the auth path and the
   inference path are configured separately.
5. **Memory by default.** Consent lasts for the page session unless the person
   also chooses to remember it on the device; it is revocable, and revoking
   stops future use without claiming to undo what already crossed.
6. **The relay** forwards only to allow-listed upstream hosts, only for
   allow-listed page origins, adds no credential of its own, keeps no logs or
   state, and is not an open proxy. Origin allow-listing is not authentication
   of non-browser callers; since the relay only carries the caller's own
   credentials, that is acceptable and must be stated.

Until ratified, the exploration follows this text and says so on screen.

## 7. What needs a decision

1. Ratify §6 (relay consent) as core, amend it, or keep it reserved.
2. Confirm the two clarifications (§3 identification, AUTH-24 diagnostics).
   They restate the ratified secrecy boundary in testable form.
3. Confirm store-layout.md's status: binding on TypeScript, normative after the
   race tests.

## Pins

lm15-python's CONTRACT_PIN moves to this commit (no behavior change; its auth
harness is 43/43). lm15-ts stays pinned at b721ce4 until its managed-auth port
passes the auth harness, including `xai-unusable-login-blocks-env` (fails today).
