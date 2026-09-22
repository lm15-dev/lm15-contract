# Specification validation — 2026-09-22

This records **artifact checks only**, not successful authentication or SDK
conformance. No real account login, model call, token renewal, credential-file read,
relay deployment or SDK implementation was performed.

## Passed

Command (from contract root):

```bash
uv run --no-project --with 'jsonschema[format]>=4.18,<5' python tools/check_managed_auth.py --self-test
```

- Both JSON Schemas are valid Draft 2020-12 schemas.
- 24 private-store vectors give the expected structural valid/invalid verdicts.
- 34 identity-selection vectors have valid structure and unique identities.
  Their selection expectations have **not** been executed against SDKs.
- 64 acceptance scenarios have unique contiguous IDs; AUTH-12–26 headings and
  local document links are present; code fences are balanced.
- Five bad-artifact mutations are detected by the checker. These are not the
  planned runtime mutation tests for auth safety/concurrency.
- Date-time checking is proved active by rejecting an impossible calendar date.
  An initial run with plain `jsonschema` exposed that optional format validation
  was absent; using `jsonschema[format]` and adding the guard prevents false passes.

Also passed:

```bash
python3 tools/check_provenance.py
python3 tools/check_secrecy.py
git diff --check
```

New private fixture inputs contain only artificial sentinel values; expected
public outputs contain none. Existing provider wire fixtures were not edited.

## Expected source/spec mismatch — not hidden or bypassed

```bash
python3 tools/spec_drift.py
```

This reports four missing reflected entries: the two retired values `oauth` and
`oauth-unless-explicit`, each exposed by the current reference's two vocabulary
reflections (`CREDENTIAL_POLICIES` and `CredentialPolicy`). The reviewed proposal
replaces them with `connection` for account-only routes, and ordinary `key` for
unmanaged key-capable routes. The runtime has deliberately **not** been changed.

This mismatch is expected for a specification-only draft, not a green runtime
gate. No checker was weakened, no SDK snapshot/pin was advanced, and no aliases or
compatibility wrappers were introduced to conceal it. See README's explicit
transition list of ten old implicit-login source-policy cases.

## Still required before claiming the feature works

- Implement and run the managed harness against all ten SDKs.
- Exercise semantic store invariants, private-to-public projection and request
  source selection, not just JSON Schema.
- Mixed-language, separate-process lock/renew/logout/replacement and crash tests.
- Native/real-browser/mobile/server integration and packaging tests.
- Provider-specific approved flow profiles and authorized, redacted live receipts.
- Maintainer review/ratification of the detailed amendment.
