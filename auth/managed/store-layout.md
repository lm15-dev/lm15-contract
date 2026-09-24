# The managed credential store, version 1: the layout both SDKs share

**Status (2026-09-24): implementation record, binding on the second SDK.**
This is the layout lm15-python has written since 2026-09-22
(`lm15/login/store.py`, `lm15/login/manager.py`). It replaces, for the file
store, the reserved design artifact [`spec/auth-store.schema.json`](../../spec/auth-store.schema.json)
(implementation record P1 in
[changes/2026-09-22-managed-authentication-python.md](../../changes/2026-09-22-managed-authentication-python.md)).
A second implementation reads and writes exactly this, byte-compatibly enough that Python and TypeScript can
share one file under one lock. It is promoted to a normative rule (AUTH-25) only after the
mixed-language race tests pass. Until then a change needs a `changes/` entry and a matching change in both SDKs.

The guarantees are AUTH-25's; this page only says where each one lives.

## The file

- Path: `$LM15_CREDENTIALS_PATH`, else `$XDG_CONFIG_HOME/lm15/credentials.json`, else
  `~/.config/lm15/credentials.json` (AUTH-8). Read at call time; anchored to an absolute path when the store is
  constructed.
- Written privately and atomically (AUTH-4): temporary file in the same directory, mode `0600`, fsync, rename.
- Every read-modify-write happens under the AUTH-4 advisory lock on the canonical path (the lock file AUTH-4
  names, not the credentials file itself). Renewal writes twice inside one lock: the in-flight marker, then the
  result.
- Strict JSON (AUTH-25): UTF-8, one object, no duplicate member names, no non-finite numbers. A document that
  fails is left untouched and reported as `storage_unavailable`; an unknown `_lm15.version` is
  `unsupported_store_version`. Neither is ever read as empty and neither is ever overwritten.

## The document

One JSON object. Every member except `_lm15` is a provider entry keyed by provider route; `_lm15` is non-secret
bookkeeping.

```json
{
  "xai": {"type": "oauth", "access": "…", "refresh": "…", "expires": 1790000000000,
          "issued_at": 1789996400000, "lifetime_s": 3600.0},
  "openrouter": {"type": "api_key", "key": "…", "minted": true},
  "gemini": {"type": "env", "name": "GEMINI_API_KEY"},
  "claude-code": {"type": "external", "source": "claude-code-cli"},
  "_lm15": {
    "version": 1,
    "slots": {
      "xai": {
        "generation": "3", "connection_id": "cn_Z_0tEcI8Te25EmNP", "revision": "7",
        "kind": "account", "method_id": "device", "instance_id": "public",
        "label": "xAI subscription", "created_at": "2026-09-22T18:04:11Z",
        "routes": ["xai"], "settings": {}, "state": "ready", "renewal": "refresh_token",
        "previous_ids": ["cn_…"]
      },
      "gemini": {"generation": "2", "connection_id": null, "revision": "0", "kind": "api_key",
                 "method_id": "", "instance_id": "public", "label": "", "created_at": "",
                 "routes": [], "settings": {}, "state": "ready", "renewal": "none", "logged_out": true}
    }
  }
}
```

### Provider entries (secret)

The shape is the provider's private material ([profiles.json](profiles.json) `tokens.material`). The OAuth shape is
the one the legacy xAI loader and Pi already read, so one entry has one owner (R1):

| `type` | Members | Meaning |
|---|---|---|
| `oauth` | `access`, `refresh`?, `expires`?, `issued_at`?, `lifetime_s`?, provider extras | `expires` is the **actual** expiry in epoch milliseconds, never pre-skewed. `issued_at` (epoch ms) and `lifetime_s` feed the renewal lead `min(300 s, lifetime/10)` (AUTH-20). Codex adds `accountId` and `id_token`. |
| `api_key` | `key`, `minted`? | A literal key. `minted: true` means an account flow produced it (OpenRouter). |
| `env` | `name` | The variable's *name*, read at request time; never its value. |
| `external` | `source` | A source name (`claude-code-cli`, `codex-cli`, `pi-xai`); the owning tool's file is read and renewed in place, nothing is copied. |
| `local` | `base_url`, `key` | A keyless local server. |
| `cloud` | `named` | A named cloud identity (AUTH-15). |

Unknown members are preserved on rewrite. An entry that is not an object makes the whole document invalid.

### `_lm15` (not secret)

`version` is the integer `1`. `slots` maps a provider route to one slot record:

| Member | Type | Rule |
|---|---|---|
| `generation` | decimal string | Identity generation. +1 on every committed login, replacement and logout; never decreases, never reused. |
| `connection_id` | string or `null` | `cn_` + 12 random bytes base64url. `null` after logout. A legacy entry without a record reads as `legacy-<provider>`, generation `1`, revision `1`; the record is written on the first managed commit, never on read. |
| `revision` | decimal string | Credential revision. +1 on every renewal of the same connection. |
| `kind` | string | `account`, `api_key`, `cloud_identity`, `local_server`. |
| `method_id` | string | The method that created the connection. |
| `instance_id` | string | `public` unless an instance was chosen. |
| `label`, `account_label`? | string | Display text. `account_label` is untrusted provider text (AUTH-12). |
| `created_at` | RFC 3339 UTC | |
| `routes` | string array | Routes this connection authenticates. |
| `settings` | string map | Non-secret method settings (`enterprise_domain`, `oauth_host`, `base_url`). |
| `state` | string | `ready`, `needs_login` (definite rejection: material dropped), `indeterminate` (an interrupted one-use exchange). |
| `renewal` | string | `refresh_token`, `remint`, `none`, `external`, `recipe`. |
| `logged_out` | `true`? | Present after logout. Persists the R3 block: an ambient key is not used for this provider. |
| `renewal_in_flight` | object? | `{started_at, revision}`, written before a renewal exchange. Still present when read: the exchange may have spent a one-use token, so status is `indeterminate`. |
| `attempt` | object? | `{id, expected_generation, started_at_s, lifetime_s}`: the slot's single reserved login. Another attempt may take the slot once `started_at_s + lifetime_s` has passed. Any end of a login without a commit releases it (cancel included). |
| `verification` | object? | `{result, checked_at, check, detail?}` from an explicit `verify()`. |
| `previous_ids` | string array? | The last 8 connection ids this slot held. |

Units: `started_at_s` is epoch **seconds** (a JSON number; Python writes `time.time()`); `expires` and
`issued_at` are epoch **milliseconds**; `created_at`, `checked_at` and `renewal_in_flight.started_at` are RFC 3339
UTC strings. A second SDK writes the same units.

## What a second SDK must prove before claiming this store

1. It reads a Python-written document and every record above without rewriting it.
2. A login, renewal and logout it commits are read correctly by Python, and the other way round.
3. Under the shared lock, two processes of different languages renewing one connection spend the refresh token
   once (MA scenarios on renewal races; `auth/managed/scenarios.md`).
4. It refuses the invalid documents in [store-vectors.json](store-vectors.json) whose verdict does not depend on
   the reserved envelope (duplicate members, non-finite numbers, non-object entries, unknown version).

Browser pages have no such file. A browser store keeps the same entry and slot shapes in memory or in an
explicitly chosen browser store; it states that same-origin scripts can read it (AUTH-21).
