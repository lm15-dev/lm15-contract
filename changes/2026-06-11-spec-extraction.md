# 2026-06-11 — Written spec extraction (the porter's data-model catalog)

## What

The canonical model now has a written specification in `spec/`, extracted
from the reference implementation (`lm15-python2/lm15/types.py`, `serde.py`,
`errors.py`) and the already-normative docs (`docs/serde-rules.md`,
`docs/mapping-rules.md`, linked rather than duplicated):

- `spec/types.md` — field tables for every public canonical dataclass (61
  types, 249 fields): JSON type per the Number rule, required/optional,
  defaults, omission behavior, constraints, factory methods. The
  required-with-shape cases are called out explicitly (an empty text part is
  `{"type":"text","text":""}`, never `{"type":"text"}`; `ToolResultPart.content`
  contract is `[]` when empty; `ToolCallPart.input` always emitted).
- `spec/vocabularies.md` — every closed vocabulary (25 reflected enums /
  146 values) plus the FORWARD-COMPAT POLICY as a written rule:
  vocabularies are closed; adapters map unknown provider values to the
  closest canonical value (existing fallbacks documented, e.g. unknown
  finish_reason → `"stop"` + `_lm15_unmapped` record) and preserve the raw
  value in provider_data; new values are additive spec changes requiring a
  `changes/` entry. Also: the full error class hierarchy ↔ ErrorCode table.
- `spec/invariants.md` — numbered INV-001…INV-048 covering every
  `__post_init__` rule and every serde from_dict leniency, each with a WHY
  (rationales that had to be inferred are marked "(inferred)"). Constructor
  coercions (list→tuple, bare-Message, number coercions, `{}`-extensions
  normalization) are named invariants ports must replicate at their API
  boundary or document the idiomatic equivalent. Known wire pitfall pinned:
  `FunctionTool.parameters == {}` is omitted and deserializes to the default
  schema (INV-033).

## PROTOCOL.md gap fills (additive)

- **Unmapped recorder**: defined what counts as unmapped (provider response
  content the adapter cannot map; the exact inspected paths per provider),
  the element shape `{"path": str, "type": str}`, the `"<missing>"`
  convention, and the `provider_data["_lm15_unmapped"]` → `unmapped`
  transport.
- **validate**: `normalized` is ALWAYS present on `ok: true` — verified
  against `lm15.vet.op_validate`, which returns it unconditionally.
- **Volatile path syntax**: exact-match grammar of `check.py`'s matcher
  (`$.`-prefix optional, `canonical_response.` root optional, `[i]`
  indices, no wildcards, closed class set, unknown class ≠ match).
- **Serde kinds**: the 19 kind strings are enumerated in the protocol
  itself; `KIND_SERDE` is now required to match the document, not vice
  versa.
- **Query parameter encoding**: shims return DECODED params; encoding is
  the transport's job (out of contract); repeated query params are
  unsupported (both sides collapse via `dict(parse_qsl)`, last wins).

## The gate

`tools/spec_drift.py` runs the python shim's `surface_dump` (reflection) and
hard-fails when any reflected type/field/enum value is missing from the spec
tables; extra spec prose is report-only. Wired into `contract.yml` after the
audit step. Teeth proven by deleting a field row and a vocabulary value from
a `/tmp` copy (`LM15_SPEC_DIR` override): 3 drift failures, exit 1. When
lm15-python2 is not a sibling checkout the gate skips with a notice
(`LM15_SPEC_DRIFT_STRICT=1` to forbid skipping) — same convention as the
python2 CI vet smoke test.

## Authority

Every spec file carries: "Status: DRAFT — pending maintainer ratification
(AUTHORITY.md canonical-facts authority transfers to spec/ upon
ratification)." AUTHORITY.md itself is NOT amended by this change —
amendments require the maintainer's re-ratification. **Pending maintainer
action:** ratify spec/ and amend AUTHORITY.md "Canonical facts" precedence
item 1 to point at `lm15-contract/spec/` (with re-ratification), replacing
the lm15-python2 docs pointer.

## Evidence

- Source-of-truth reading: `lm15/types.py` (all dataclasses +
  `__post_init__`), `lm15/serde.py` (all to/from_dict pairs),
  `lm15/errors.py`, `lm15/vet.py`, `harness/check.py`
  (`_volatile_class`, `split_url`), provider `_record_unmapped` call sites.
- `surface_dump` run against the live shim on 2026-06-10: 61 types / 249
  fields, 25 enums / 146 values — all covered (spec_drift OK).
- check_provenance + audit + selftest re-run green; harness fixtures
  untouched.
