# Port — how a language implementation is built against this corpus

A port is not a translation of lm15-python. It is an implementation of
`spec/` that the harness cannot tell apart from the reference. The
reference is one more shim; it holds no authority (`AUTHORITY.md`). This
playbook is the order of work, the gates, and the rules an agent follows so
that four ports converge instead of each inventing a shape.

## Inputs the agent receives

1. `AUTHORITY.md`, `spec/*.md` (types, vocabularies, invariants, auth,
   scope), `harness/PROTOCOL.md`, `lm15-python/docs/mapping-rules.md`
   (MAP-1 to MAP-9), `lm15-python/docs/serde-rules.md`.
2. This repository at the pinned commit, read-only. The shim is run by
   `harness/check.py --shim <lang>`; the entry in `harness/shims.json`.
3. The idiom rules for the language (§ Idioms below).
4. No network. The harness sandboxes the shim; a port's unit tests must
   not need keys either (a live smoke test may exist, env-gated, and is not
   a gate).

## Order of work

Each module is a harness direction or a spec section; a module is done
when its direction is green with zero skips added, and stays green.

| # | Module | Gate |
|---|---|---|
| 1 | canonical types + serde (`spec/types.md`, `spec/vocabularies.md`, `spec/invariants.md`, `docs/serde-rules.md`) | `--direction serde` (35 kinds, 109 vectors); `validate` rejects what the invariants reject |
| 2 | errors (`spec/vocabularies.md` ErrorCode, hierarchy shape) | `--direction error` |
| 3 | auth (`spec/auth.md` AUTH-1..10: chain, doctor, credential providers, access policies) | `--direction auth`; `auth_resolution.json` |
| 4 | dialects, request side: Anthropic, OpenAI Responses, OpenAI Chat (+ compat presets), Gemini | `--direction request` (143 cases incl. build-time raises) |
| 5 | dialects, response side + stream assembly (MAP-1..4, MAP-9) | `--direction response`, `--direction stream` (incl. the pinned assembly refusal) |
| 6 | model listing | `--direction models` |
| 7 | files, batch, cache surfaces | `--direction files`, `batch`, `cache` |
| 8 | generation (image, speech) and video | `--direction generation`, `video` |
| 9 | live (websocket transcripts) | `--direction live` |

Modules 1–5 are the frozen core and gate the 1.0 tag for every language.
Modules 6–9 ship where the language's ecosystem makes them reasonable;
a port that does not implement one answers `ok: false` with
`UnsupportedFeatureError` for its ops and declares it in its README.

## Rules

1. **The corpus is read-only to the port.** A port never edits a case,
   body, golden, or vector to pass. A disagreement is either a port bug or
   a `changes/` entry in this repository with evidence — decided here, not
   in the port. The port's CI checks out this repository at its
   `CONTRACT_PIN` and fails if the working tree is dirty; the harness
   itself does not verify the hash (stated gap, 2026-09-02).
2. **Copy tables as data.** Mapping tables in the reference (reasoning
   grading table, model-class detectors, access policies, compat presets,
   finish-reason maps, error-code maps) are data. Port them as data; do
   not re-derive them from provider docs or memory.
3. **Raise where the reference raises.** Every `expect_lm15.raises` case
   is a refusal the port must make at the same op with the same class and
   ErrorCode. Never map a refused cell to "something reasonable".
4. **No silent drops.** A canonical field with no wire slot is a raise or a
   documented `extensions` door, never omission (MAP-5..8 rationale).
5. **Absent is not zero, not empty, not null.** Serde follows
   `docs/serde-rules.md` exactly; the vectors pin omit-empty per field.
6. **Skips are monotonic.** A port keeps a skip list only for directions
   it has not started; a skip added to a started direction fails review.
7. **The shim is thin.** It parses the protocol line, calls the same
   public functions users call, and serializes. No harness-only code paths.
8. **State what the language cannot express.** If an idiom forces a
   deviation (a Go interface for the credential provider, a Rust enum for
   Part), it goes in the port's README under "Stated deviations", with the
   spec line it deviates from. Absorbed deviations are bugs.

## Idioms

Shared decisions so ports look like one family:

- `Part`, `Delta`, `StreamEvent`, `LiveClientEvent`, `LiveServerEvent`
  are closed sums: Rust `enum`, TypeScript discriminated union on `type`,
  Go sealed interface with one struct per variant, Julia abstract type.
- Canonical JSON key names and the `type` discriminator are the wire
  contract; language naming (snake vs camel) applies to identifiers only.
- Every canonical type has `from_json` / `to_json` (or the idiomatic
  equivalent) obeying the omission rule; constructors validate the
  invariants (INV-*), so serde input gets the same checks.
- Credential provider: zero-arg callable (Python/TS/Julia), single-method
  interface (Go/Rust). Invoked at request-build time, never cached by the
  adapter (AUTH-2).
- Access policy (AUTH-10): a value; the dialect consults it at the named
  points; subscription "adapters" are constructors that bind a policy.
- Errors: the class hierarchy SHAPE is replicated; the mechanism is
  idiomatic (Rust enum with a `code()`, Go error types with `errors.As`).
  Messages are not pinned; class and ErrorCode are.
- Streams: adapters may emit one end event per provider terminal frame;
  a language-neutral coalescer produces exactly one final end event
  (MAP-3) and one leading start event (MAP-4). Assembly never invents a
  tool-call name (MAP-9).
- Ints stay ints, floats stay floats, `true` is not `1` (the harness
  compares with type tags; the `bool_as_int` mutation exists for this).

## Reviewing a port

1. `python3 harness/check.py --shim <lang> --direction all` at the pinned
   commit: report per direction, zero fails, skips only in unstarted
   directions.
2. README "Stated deviations" reviewed against rule 8.
3. `CONTRACT_PIN` in the port moves in the same commit as the code that
   needed it.

(`harness/selftest.py` drives only the fake shim; it proves the
comparator, not a port. A per-port mutation run is a stated gap.)

## What this playbook does not do

It does not license a port to ratify anything. A port that finds the
corpus wrong stops, records the receipt, and opens a `changes/` entry
here. That is the whole point of separating the oracle from every
implementation, the reference included.
