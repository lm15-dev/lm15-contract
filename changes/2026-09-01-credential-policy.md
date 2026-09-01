# 2026-09-01 — Credential policy is declared, not name-listed; one login door

Ratified: Maxime Rivest, 2026-09-01 — assented in session
("implement all three!") after the review "is xAI special in the right or
wrong way?".

## The finding

The rule was already homogeneous but unwritten: **a provider string means
"how the wire behaves", not "where the token comes from"**. Claude Code and
Codex are separate providers because their wire surface differs (headers,
forced system prompt, blocked endpoints, different backend). xAI is one
provider because subscription and key auth hit identical endpoints. That
stays.

Three things were heterogeneous in the wrong way:

1. The router hardcoded `_OAUTH_PROVIDERS` / `_OAUTH_FALLBACK_PROVIDERS`
   frozensets, and the doctor imported one of them — the same fact as the
   manifests' `auth_modes`, stated twice, free to drift. The doctor also
   omitted xAI's OAuth-fallback rung entirely, diverging from `lm()`
   (its own docstring calls that a bug).
2. `login_xai()` was a provider-named one-off with no uniform entry point.
3. The key-beats-subscription billing consequence for xAI was absorbed,
   not stated.

## Spec amendments

- **AUTH-1**: every provider manifest declares `credential_policy` —
  `key`, `oauth`, or `key-then-oauth`. Routers, doctors, and shims derive
  behavior from the declaration; hardcoded provider-name lists are
  forbidden as second copies of the same fact. The chain gains an explicit
  final rung for `key-then-oauth` providers. The billing trade-off is
  stated normatively.
- **AUTH-8**: the Pi agent store (`~/.pi/agent/auth.json`) and the
  lm15-owned store's xAI entry format are pinned.
- **AUTH-9**: one uniform `login(provider)` entry point per
  implementation; flows lm15 does not own fail typed, naming the exact
  fix (CLI command or console URL). Console URLs are guidance strings,
  not wire facts.

## Fixture additions (`auth/resolution.json`, hand-authored per AUTH-1/7)

- `xai-key-shadows-oauth` — env key selected, fresh stored login shadowed.
- `xai-oauth-fallback` — no key anywhere, stored login selected.
- `xai-oauth-expired-no-refresh` — stored login unusable, not configured.
- `xai-nothing-configured` — all rungs absent.

The fixture field `borrowed_file` now covers both AUTH-8 formats: the
borrowed Claude Code store and the lm15-owned xAI store. The field name is
kept (trade-off, stated): renaming it would churn the harness, both fake
and real shims, and the dual-landed copy for a purity gain with no
semantic content; the description defines the meaning instead.

## Harness

`check.materialize_borrowed_file` materializes both formats;
`fake_shim._borrowed_state` classifies both. The harness still owns every
input; shims never write credential files.

## Reference implementation (lm15-python, same commit series)

`ProviderManifest.credential_policy` added; router frozensets deleted and
derived via `_credential_policy()`; doctor walks the xAI fallback rung and
takes `xai_credentials_path`; vet shim routes `credentials_path` by
provider; `lm15.auth.login(provider)` dispatches; `Resolution.describe()`
names the fallback; billing trade-off documented in the adapter and
`docs/authentication.md`.
