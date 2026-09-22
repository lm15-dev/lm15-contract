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
- 43 identity-selection vectors have valid structure and unique identities.
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

## Post-ratification alignment checks

```bash
python3 tools/spec_drift.py
```

Passed after R1–R3/R10 alignment: 70 reflected types / 313 fields and
57 enums / 282 values are covered. The earlier draft's four missing `oauth` /
`oauth-unless-explicit` entries are no longer missing: their retirement was
rejected, not hidden by aliases or a checker bypass.

This is a surface-coverage check, not behavioral conformance. The one legacy
canonical fallback fixture is intentionally corrected under AUTH-1/AUTH-15 R3
(`xai-unusable-login-blocks-env`); existing SDKs may fail it until repaired.
No SDK runtime tests or live flows were run in this alignment pass. No pins,
support rows, provider wire fixtures or runtime snapshots were changed.

The managed checker also passed its five deliberate bad-artifact tests, and
provenance, secrecy and `git diff --check` passed. `python3 harness/selftest.py`
also passed its baseline and caught all 40 comparator mutations; this uses a fake
shim, not SDK execution. The private-store schema and vectors remain reserved
layout designs; validating them does not ratify them.

## Still required before claiming the feature works

- Implement and run the managed harness against Python and TypeScript first.
- Repair any SDK behavior still allowing key fallback from a failed subscription;
  preserve existing subscription access until R1's replacement gates pass.
- Exercise semantic store invariants, private-to-public projection and request
  source selection, not just JSON Schema.
- Mixed-language, separate-process lock/renew/logout/replacement and crash tests.
- Native/real-browser/mobile/server integration and packaging tests.
- Provider-specific approved flow profiles and authorized, redacted live receipts.
- Explicit promotion of reserved details when their use cases arrive; core
  ratification does not promote server/relay/database features automatically.
