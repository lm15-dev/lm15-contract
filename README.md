# lm15-contract

This repository defines shared lm15 behavior. Read [AUTHORITY.md](AUTHORITY.md)
first. Implementations must follow the contract, not change fixtures to pass.

| Path | Purpose |
|---|---|
| `AUTHORITY.md` | Evidence rules and source precedence |
| `spec/` | Canonical types, invariants, vocabularies, scope, and authentication |
| `docs/` | Normative serde rules and mapping rules (MAP-1..MAP-10); moved here from lm15-python on 2026-09-07 |
| `cases/`, `bodies/`, `errors/` | Provider requests and captured responses |
| `goldens/` | Expected canonical responses and stream events |
| `serde/canonical.json` | Canonical JSON vectors |
| `auth/` | Credential resolution, signing, and token-exchange vectors |
| `receipts/`, `changes/` | Capture evidence and change records |
| `spec/support-matrix.json` | Provider support and evidence status |
| `harness/` | Shared test protocol, runner, and comparator tests |
| `tools/` | Provenance, secrecy, coverage, and spec checks; the verdict registries (`extensions-verdicts.json`, INV-049; `openai-chat-ingest-verdicts.json`, MAP-12) |
| `playbooks/port.md` | Port order, test gates, and review rules |
| `playbooks/api-family.md` | Public API guide (ratified 2026-09-06) |

## Check the contract

Run these commands from this repository:

```bash
python3 tools/check_provenance.py
python3 tools/check_secrecy.py
python3 tools/audit.py
python3 tools/spec_drift.py
python3 tools/check_content_coverage.py
python3 harness/selftest.py
```

`spec_drift.py` needs the Python reference at `../lm15-python` for its full check.
The comparator self-test does not prove that any implementation passes.

## Check the Python reference

Install `../lm15-python` in its `.venv`, then run:

```bash
python3 harness/check.py --shim python --direction all
```

The harness checks `lm15-python/CONTRACT_PIN` against this repository's HEAD.
Use a clean contract checkout at that commit for a reproducible result.
`--no-check-pin` supports local development only; it is not a release gate.

Land reviewed contract changes first. Update the Python pin with the matching
implementation changes. Publish the contract commit before dependent CI runs.

## Readiness boundaries

- A passing reference suite does not prove that a language port passes.
- Each port must pass its own gates against its declared contract version.
- Keep failing port tests visible. Do not remove new fixtures to claim parity.
- Documentation evidence is not a successful live capture. Check each provider's
  support row and change record, including partial captures.
- The public API guide (`playbooks/api-family.md`) and the two
  authentication amendments (`changes/2026-09-04-bedrock-bearer.md`,
  `changes/2026-09-04-bedrock-mantle-chat-live.md`) were ratified
  2026-09-06. See `changes/2026-09-06-ratification.md`.
- The 88 new goldens (2026-09-03/04) stay `scribe-draft` until the
  independent re-review adds their `reviewed` line. A green harness run
  does not approve them.

## Migration history

The corpus moved from `lm15-python2/conformance` on 2026-06-09. See
`changes/2026-06-09-initial-migration.md`. Some legacy Python checks still use
local fixtures. The shared harness reads this repository directly.

The Python serialization suite reads `serde/canonical.json` directly since
2026-09-02. See `changes/2026-09-02-one-copy.md`.
