# 2026-09-01 — xAI: stored subscription beats environment keys

Ratified: Maxime Rivest, 2026-09-01 — assented in session ("we always want
to use subscriptions before billing... the only time we will use API before
subscriptions should be if it's specifically in the request, in the client
creation, in the session, in the process").

Supersedes, same day, the `key-then-oauth` ordering ratified this morning
(changes/2026-09-01-credential-policy.md) — before any port consumed it.

## The decision

The morning's order let `XAI_API_KEY` beat the stored subscription login.
That order carried a stated billing trade-off: a stray env var silently
moves the user from prepaid subscription to per-token billing. On review
that trade-off loses to a durable constraint: **normal inference must not
unexpectedly spend money.**

The corrected reasoning: an env var is not "explicit" in the sense that
matters — it is stored shell state, often written by other projects. The
subscription login is stored state too, created just as deliberately. When
two kinds of stored state compete, the one that spends no money wins.
Truly in-process configuration (an `api_keys` entry, an `api_key`
constructor argument) still beats everything: deliberate instructions must
always win, or no setting can be trusted.

## AUTH-1

The third credential policy is renamed `key-then-oauth` →
`oauth-unless-explicit` and reordered:

1. explicit `api_keys` entry (or constructor argument) — always wins;
2. usable stored local OAuth credential (fresh, or refreshable);
3. declared environment keys;
4. typed not-configured error with the login hint.

Adapters declaring this policy expose an offline stored-credential probe
(file reads only) so routers walk the chain without network I/O.

Residual trade-off, stated: with a subscription stored, a set env key is
silently ignored. That surprise costs zero dollars; the doctor (AUTH-7)
shows the shadowed rung. It also diverges from the common SDK convention
that an env var always wins — accepted deliberately, for xAI only, because
the alternative bills people by accident.

## Fixtures (`auth/resolution.json`)

The four morning xai cases are replaced by five pinning the new chain:

- `xai-explicit-key-shadows-subscription` — config entry wins, fresh login
  shadowed.
- `xai-subscription-shadows-env` — fresh login wins, env key shadowed
  (the case this change exists for).
- `xai-subscription-only` — login selected with nothing else set.
- `xai-env-rescues-unusable-login` — expired-no-refresh login is dead; the
  env key is used rather than failing.
- `xai-nothing-configured` — all rungs absent.

Step order in every xai case is the chain order: `api_keys`, `oauth-file`,
`env:XAI_API_KEY`. Harness and shims need no mechanical changes; the fake
shim matches cases by planted inputs.

## Reference implementation (lm15-python, same commit series)

`CredentialPolicy` literal renamed; `XaiLM.has_stored_credential()` /
`usable_xai_credential()` added as the offline probe; router builds the
new chain; doctor walks rungs in chain order; `Resolution.describe()`
prints the chain (resolve() stays pure, so it names the chain, not a
winner); docs rewritten around the new order.
