# 2026-06-11 — INV-033 resolved: FunctionTool.parameters is required-with-shape

Decision (maintainer delegation, standing instruction to resolve the two
honest spec inconsistencies found during extraction): `FunctionTool.parameters`
becomes ALWAYS-EMITTED, like `ToolCallPart.input` and `ToolResultPart.content`.

- An explicit `{}` round-trips verbatim as `{}` — `parameters` is an opaque
  JSON-Schema payload, and opaque payload contents are user data
  (serde-rules.md omission rule 3, INV-002). The old behavior (the omission
  rule dropped the serializer's own top-level `{}`, which then read back as
  the DEFAULT schema) silently rewrote user data on the round-trip.
- Absent on input still deserializes to the default schema
  `{"type": "object", "properties": {}}` (INV-045 round-trip identity).

Spec rows changed: spec/types.md FunctionTool (`parameters` Req `no`→`shape`,
Omission `omit-empty`→`always (even {})`), required-with-shape list;
spec/invariants.md INV-033 rewritten.

Implementation: lm15-python2 `lm15/serde.py::tool_to_dict` emits `parameters`
unconditionally; red-first tests in
`lm15-python2/tests/test_spec_decisions_1_0.py`.

Fixture change (canonical fact, spec citation per AUTHORITY.md): added serde
vector `tool.function.empty_parameters`
(`{"type": "function", "name": "noop", "parameters": {}}`, round-trips
verbatim) to `serde/canonical.json` and the lm15-python2
`conformance/serde/canonical.json` copy, citing INV-033 + serde-rules.md
omission rule 3. No existing vector was affected: every canonical fixture
tool carries a non-empty `parameters` (verified by corpus scan + harness
`--direction all`, zero fails). Wire fixtures untouched.
