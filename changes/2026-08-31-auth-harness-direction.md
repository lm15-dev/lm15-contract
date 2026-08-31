# 2026-08-31 — auth becomes a harness direction (explain_auth op)

Ratified: Maxime Rivest, 2026-08-31 (session assent: "i ratify"); transcribed.

Additive protocol change: the AUTH-1/AUTH-7 resolution fixtures in
`auth/resolution.json` (ratified 2026-08-31) are now executable through the
vet harness, not only through each implementation's in-repo test suite. A
port can no longer be "harness-green" while lacking the credential-resolution
surface.

## What lands

- `harness/PROTOCOL.md` — new op `explain_auth`. The harness owns every
  input: the full `env` map (always sent, possibly empty, so the shim never
  reads its real environment), `api_keys_providers` planted with the fixture
  sentinel, and `credentials_path` pointing at a harness-materialized
  borrowed credential file in the AUTH-8 wire format. The shim returns
  `configured`, the `steps` kind/state chain, and `report_text` (its full
  human rendering).
- `harness/check.py` — new direction `auth` (in `--direction all`):
  - strict comparison of `configured` and `steps` against each fixture
    `expect` block;
  - AUTH-5 enforced harness-side: the planted sentinel must not appear
    anywhere in the shim reply, and `report_text` must be a non-empty
    string so the secrecy check has a rendered surface to inspect;
  - `materialize_borrowed_file` writes the Claude Code
    `{"claudeAiOauth": {...}}` file itself — never the shim — so an
    implementation cannot pass with a file only its own parser accepts.
- `harness/fake_shim.py` + `harness/selftest.py` — two new mutations, both
  proven caught: `auth_state_flip` (chain-state drift) and
  `auth_sentinel_leak` (sentinel in `report_text`). The sentinel check is a
  substring gate, not deep-equality, so it needs its own mutation to prove
  it has teeth.

## Reference implementation (lm15-python), same date

- `lm15/doctor.py` — `AuthStep` gains a structured `kind` field carrying the
  fixture's language-neutral vocabulary (`api_keys`, `env:<VAR>`,
  `placeholder`, `oauth-file`). Conformance no longer parses display
  strings.
- `lm15/vet.py` — implements `explain_auth` per the protocol.
- `tests/test_auth_resolution_contract.py` — compares `step.kind`
  structurally; the display-string mapper is gone.

## Evidence at landing time

- `harness/check.py --shim python --direction auth`: pass 9 / fail 0 / skip 0.
- `harness/selftest.py`: baseline green in all six directions; all 8
  mutations caught red.

## Stated trade-offs

- The harness duplicates the borrowed-file materialization that
  lm15-python's in-repo test also performs. Accepted: the harness must own
  fixture materialization to stay oracle-grade, and the in-repo test must
  keep running without the contract harness. Divergence is caught because
  both are exercised in CI.
- `report_text` concatenates renderings into one string instead of
  structured fields. Accepted: AUTH-5 is a substring invariant over ALL
  rendered surfaces; one opaque blob is exactly the right shape for it and
  over-specifying the rendering would freeze human-facing text into the
  contract.
- Fixtures currently exercise borrowed files for `claude-code` only. The
  materializer fails loudly for any other provider, so adding e.g. Codex
  fixtures forces a deliberate materializer addition rather than silent
  reuse of the wrong file format.
