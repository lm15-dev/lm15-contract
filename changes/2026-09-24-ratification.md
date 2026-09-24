# 2026-09-24 — Ratification: MAP-15, the INV-053 browser amendment, relay consent

**RATIFIED 2026-09-24.** Asked which proposals were waiting, the maintainer
answered: "I approve the for [four] rule change." The four items put to him
were the three proposals below and the adaptation-parity record, which needed
no approval (it brings the SDKs to an already ratified rule, MAP-13).

## What is now binding

| Rule | Where | Proposal |
|---|---|---|
| **MAP-15** — a provider's "no such model" is `unsupported_model`, whatever its status; pinned forms only from live receipts | `docs/mapping-rules.md`, `spec/model-not-found.json` | `changes/2026-09-24-model-not-found.md` |
| **INV-053, browser Fetch** — where the platform forbids `Accept-Encoding`, a transport accepts the `br`/`zstd` the platform negotiated and decoded; detected by a feature test | `spec/invariants.md` | `changes/2026-09-24-inv-053-browser-fetch.md` |
| **AUTH-21, relay consent** — promoted from reserved to core: scoped per relay origin, route and stage; an explicit act after a plain disclosure; no automatic fallback; per-stage configuration; session memory by default; an allow-listed, log-free relay | `spec/auth-managed.md` § Relay consent | `changes/2026-09-24-managed-auth-profiles-and-browser-track.md` §6 |

## What this does not decide

- **Lighter consent for an encrypted relay** (the §6 addendum's open question).
  The core text states what an encrypted relay sees and that its allow-list
  names hosts, not paths; consent stays the same explicit, scoped act.
- **§7 items 2 and 3** of the browser-track record (the §3 identification and
  AUTH-24 diagnostics clarifications; store-layout.md's status) were not put
  to the maintainer and stay as that record describes them.
- **Provider permission and billing** for subscription traffic from a page, or
  through a relay, remain unverified for every provider but xAI. Ratifying how
  consent is asked is not a claim that a provider allows the traffic.
- **Server-side egress policy** for relays stays reserved (AUTH-20 reserved).

## Pins

A port that already implements a rule does not change behavior on this
record. MAP-15 is implemented in all six ports; the INV-053 amendment in
lm15-ts (the only port with a browser Fetch transport in the playground whose
behavior was observed; the Python, Rust and Go playground runtimes are checked
separately); relay consent in lm15-ts `loginAdapter` and the playground's
sign-in lab.

## Pins moved to this record's contract (same day)

`harness/check.py --direction all` against this contract, every direction:

| Port | Pass | Fail | Was pinned at | Notes |
|---|---|---|---|---|
| lm15-python | 1440 | 0 | ec989ba | |
| lm15-ts | 1440 | 0 | b721ce4 (09-20) | `xai-unusable-login-blocks-env` fixed (R3 ported to router and doctor), the gate `changes/2026-09-24-managed-auth-profiles-and-browser-track.md` named for moving this pin |
| lm15-rs | 1440 | 0 | b721ce4 (09-20) | R3 ported; the TypeSafe listing's content type |
| lm15-go | 1416 | 24 | 18dad7b (09-19) | R3 ported. Known, visible, and also failing at its old pin: **23** cases where Go serializes JSON keys alphabetically while the recorded bytes keep insertion order: 20 Bedrock Chat / Mantle SigV4 signatures (the signature covers the body bytes), 2 batch JSONL uploads, 1 image-edit multipart field order. Providers accept either order; the harness compares bodies as parsed JSON but a signature or an uploaded file pins bytes. **1**: `cached_prefix.routed` (the 2026-09-20 `CachedPrefix.provider` field, itself still awaiting review, is not ported). At its old pin Go failed 28, including the five MAP-15 cases it now implements. |

lm15-jl and lm15-r stay at cfed007 (2026-09-11): R3 and several later rules
are not ported there, and their harness runs were not repeated today.
