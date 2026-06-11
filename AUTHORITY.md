# AUTHORITY — the lm15 contract constitution

This document defines which artifact wins when artifacts disagree. It exists
because the alternative was demonstrated not to work: on 2026-04-29, fixtures
were edited to match SDK output to reach a green coverage number
(curl-fixtures commit `ea208b0`), inverting the oracle. Under this document,
that move is a violation unless accompanied by the evidence specified below.

The corpus in this repository — `cases/`, `bodies/`, `errors/`,
`serde/canonical.json` — is the single source of truth for lm15 behavior.
`lm15-python` is the reference implementation: changes land there first, but
it holds **no oracle authority**. Implementations never win by default.

## Wire facts

A wire fact is a claim about the bytes exchanged with a provider: the HTTP
request an lm15 case must produce, and the raw response/SSE bodies a provider
returns.

Precedence (highest wins):

1. **Live provider behavior** — a fresh, verbatim capture from the real API,
   with a receipt (timestamp, model, request hash).
2. **Provider documentation** — the scraped snapshots under api-references.
3. **The contract fixture** (`cases/*/`, `bodies/`).
4. **Any implementation** — including the reference.

When live behavior contradicts a fixture, the fixture is wrong: re-capture,
re-validate, update the fixture with the receipt attached. When an
implementation contradicts a fixture and there is no new live evidence, the
implementation is wrong — fix the code, never the fixture.

## Canonical facts

A canonical fact is a claim about the lm15 representation itself: what the
canonical JSON for a value is, which fields exist, what an invariant requires,
how provider output maps into canonical types.

Precedence (highest wins):

1. **Normative rules** — the written spec for the representation:
   `spec/types.md`, `spec/vocabularies.md`, `spec/invariants.md` in this
   repository (ratified 2026-06-11), together with
   `lm15-python/docs/serde-rules.md` and `docs/mapping-rules.md`.
2. **The contract fixture** (`serde/canonical.json`, `expect_lm15` blocks).
3. **lm15-python** (the reference implementation).
4. **The ports** (Go, Rust, TypeScript, Julia).

A canonical fixture changes only with a citation of the normative rule that
justifies the new expected value. A normative rule changes only with a
`changes/` entry explaining why, in the same commit.

## Evidence

No fixture changes without evidence, and the evidence must be of the right
kind for the fact:

- A **wire fixture** (`cases/`, `bodies/`) changes only with a
  **live-validation receipt**: the captured request/response, timestamp, and
  model, recorded in a `changes/` entry committed together with the fixture
  edit.
- A **canonical fixture** (`serde/`, `expect_lm15`) changes only with a
  **spec citation**: the numbered rule (or `docs/serde-rules.md` section) that
  makes the new value correct, recorded the same way.
- An agent (LLM or human-in-a-hurry) making an implementation pass by editing
  a fixture, weakening an assertion, or adding a skip is the failure mode this
  repo exists to prevent. Repair loops fix implementations; only reviewed,
  evidenced commits change the oracle.

Provenance is machine-enforced: `tools/check_provenance.py` fails CI when any
fixture lacks its provenance block (source, date, evidence).

## Scope and amendments

These rules bind every repository in the lm15 organization, every agent
work-order, and the maintainer. Amendments to this document require a
`changes/` entry and re-ratification below.

Ratified-by: Maxime Rivest, 2026-06-10 — rules read and assented to in session; transcribed at his request.
Re-ratified: Maxime Rivest, 2026-06-11 — canonical-facts precedence amended to name the ratified spec/ files (session assent: "I ratified the spec"); transcribed.
