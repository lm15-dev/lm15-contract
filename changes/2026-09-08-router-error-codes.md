# 2026-09-08 — Router failures join the ErrorCode vocabulary: `unknown_model`, `ambiguous_model`; no `router` code

Ratification: RATIFIED 2026-09-08 — Maxime Rivest, in session ("i ratify,
go!"), after the finding was laid out with the three-way table (what went
wrong → what the user must do) and the recommendation "add two codes,
delete one" accepted. Transcribed. Drafted from the Rust module 5c review
(`lm15-rs/README.md` § Module 5, "Router errors stay inside the ratified
vocabulary"): the reference raised codes the vocabulary did not list; the
port refused to invent them and collapsed both to `ConfigurationError`.

## What this changes

Two codes, one deletion, one harness direction, two implementation edits:

1. **The vocabulary.** `spec/vocabularies.md` § ErrorCode gains
   `unknown_model` → `UnknownModelError` and `ambiguous_model` →
   `AmbiguousModelError`, both subclasses of `ConfigurationError`
   (local, pre-network, "your setup is wrong" — the family
   `not_configured` already lives in). Payload: `model` on both;
   `providers` (every candidate, catalog order, deduplicated) on
   `AmbiguousModelError`. The hierarchy diagram and the metadata paragraph
   say so.
2. **The deletion.** There is no `router` code and no `RouterError`
   class. The vocabulary names failures a caller can act on, not the
   component that raised them. The reference's `RouterError` base (code
   `router`) is removed; `MissingCredentialError` stays a
   `NotConfiguredError` (code `not_configured`, unchanged) and loses the
   second parent.
3. **The harness.** `PROTOCOL.md` gains `resolve_model`;
   `router/resolution.json` pins 22 cases (the three rungs, their
   precedence, the underscore alias as input-only, and every refusal);
   `harness/check.py --direction router` drives them. Both ports answer
   the same class, code and payload for the same input.
4. **The reference.** `lm15/errors.py` owns the two classes;
   `lm15/router.py` raises them and re-exports; `ErrorCode` in
   `lm15/types.py` lists the codes (before this entry
   `ErrorDetail(code="unknown_model")` raised `ValueError` — the reference
   could not even serialize its own router errors).
5. **The Rust port.** Two `ErrorCode` / `ErrorClass` / `Lm15Error`
   entries; `resolve` raises them instead of `ConfigurationError`.

## Why

- The three failures demand three different fixes: `unknown_model` — fix
  the model string, add a prefix or a rule; `ambiguous_model` — add a
  prefix to pick one; `not_configured` — set a credential. Collapsing the
  first two into the parent class is safe (it invents nothing) but throws
  away a machine-readable distinction and pushes a consumer (DSPy) toward
  parsing message text — the thing a smaller contract exists to prevent.
- They are not `unsupported_model`. That code is a `ProviderError`: the
  provider replied 404. These never reached the network. Merging them
  would misstate whether a call was made.
- `router` named a module, not a failure. Nobody can act on "something in
  the router went wrong"; the message already says which. A code per
  component does not scale and would have been ratifying an accident of
  the reference's class layout.
- The `RouterError` + `NotConfiguredError` double parent was a Python
  convenience no port could copy; removing it costs nothing (every
  `except NotConfiguredError` still catches the credential case).

## Considered and rejected

- Make the reference drop the codes (the cheapest fix): matches the
  stricter port by making the contract poorer. The port was right to
  refuse to invent codes; it was not right about which outcome is best.
- Ratify all three as they were: see `router` above.
- Keep the router out of the harness and trust the differential probe
  (130 comparisons, `lm15-rs/receipts/2026-09-07-differential/`): the
  whole point of the codes is that every language raises the same one for
  the same input; that is a fixture, not a probe.
- Pin `rules_tried` / `catalog_searched` on `UnknownModelError`: the
  reference carries them as diagnostics; they describe the router's
  configuration, not the failure, and a port without discoverable
  catalogs has nothing truthful to put in the second. Left to each
  language.

## Evidence

- Reference: `--direction router` 22 / 0; the full pytest suite green.
- Rust: `--direction router` 22 / 0 after the two-variant change; every
  other direction unchanged.
- `tools/audit.py`, `tools/spec_drift.py`, `tools/check_provenance.py`:
  clean.

## Trade-offs, stated

- A consumer that caught `RouterError` by name breaks. Pre-1.0; the base
  class was never in the contract; `ConfigurationError` catches the same
  set (minus nothing: `MissingCredentialError` was already a
  `NotConfiguredError`).
- The harness now has an opinion about rung precedence (prefix > catalog
  > rule) and about alias-vs-exact-id in the catalog. Those were already
  the reference's documented rules (`docs/using-the-router.md`) and the
  port's copy of them; pinning them is the intent.
