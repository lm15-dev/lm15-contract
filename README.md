# lm15-contract

The single source of truth for lm15 behavior across all language
implementations. See [AUTHORITY.md](AUTHORITY.md) for the rules that govern
this corpus — start there.

| Path | What |
|---|---|
| `AUTHORITY.md` | The constitution: precedence and evidence rules |
| `cases/` | Provider request fixtures (canonical case → wire request), live-validated |
| `bodies/` | Verbatim captured provider response/SSE bodies |
| `errors/` | Provider error bodies → expected canonical lm15 errors |
| `serde/canonical.json` | Canonical JSON round-trip fixtures |
| `changes/` | One entry per oracle change, with evidence |
| `tools/check_provenance.py` | CI gate: every fixture carries provenance |

Migrated 2026-06-09 from `lm15-python2/conformance` (see
`changes/2026-06-09-initial-migration.md`). The old suite keeps running
against its own copies of `cases/`, `bodies/`, and `errors/` until the Stage 2
harness cutover; until then, edits to those land in both places or not at
all. `serde/canonical.json` has no second copy since 2026-09-02: the
reference's conformance suite reads this file directly
(`changes/2026-09-02-one-copy.md`).
