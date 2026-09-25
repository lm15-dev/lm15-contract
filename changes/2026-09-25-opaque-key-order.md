# 2026-09-25 — Opaque payloads keep their key order, and the harness checks it

**Status: HARNESS (enforces an existing normative rule; no fixture, golden
or spec rule changes).**

## The rule was already written

INV-002: opaque objects "must round-trip byte-exact". serde-rules.md
omission rule 3: opaque payloads (tool `input`, FunctionTool `parameters`,
`extensions`, `response_format`, builtin tool `config`, `provider_data`,
continuation `data`) "round-trip exactly". Key order is part of "exactly".
It is not cosmetic:

- A JSON Schema's property order is the order a model fills structured
  output in. OpenAI documents it ("outputs will be produced in the same
  order as the ordering of keys in the schema"); Gemini exposes it as
  `propertyOrdering`. A schema that lists `reasoning` before `answer` asks
  the model to reason first; sorted, `answer` comes first and the
  reasoning is written after the answer it was meant to produce.
- A SigV4 signature, a JSONL batch upload and a multipart field cover the
  exact bytes.

## Why nothing caught it

The harness compares JSON as parsed JSON, so key order never differed.
Only the byte-pinned cases could see a port that re-ordered objects. Go
wrote every JSON object as a Go map, sorted; its 23 failures at the
2026-09-25 pin (20 Bedrock SigV4 requests, 2 batch uploads, 1 image-edit
multipart) were the only visible symptom of a gap that touched every
structured-output request.

## What the harness now checks

`harness/check.py`, `opaque_key_orders` / `opaque_order_difference`
(PROTOCOL.md, "Comparison semantics"): in the `request` direction, every
object of the built body that equals, up to key order, an object inside
an opaque payload of the case's `canonical_request` must list its keys in
that order; in the `serde` direction the round-tripped value is checked
the same way against the case `value`. Typed objects stay order-free
(serde-rules.md: byte-identical "after key sorting"). An object an adapter
rewrites (INV-050's judgment exception) no longer equals an input object
and is not checked.

`harness/selftest.py` gains the mutation `opaque_keys_sorted` (the fake
shim writes the body with sorted keys); it is caught on
`anthropic.data_part_text`.

## Measured

| | request cases failing the new check | serde cases |
|---|---|---|
| Go before the ordered `JSONObject` (lm15-go `main`, 2026-09-25) | 179 of 398 | 8 of 129 |
| Python, TypeScript, Rust, Go (ordered `JSONObject`) | 0 | 0 |

The recorded fixtures agree with their canonical requests in all 370
comparable cases, so the fake shim's echo stays green: no fixture changes.

## Not covered

- A case written to show the behavioral consequence (`reasoning` before
  `answer`) would be a new wire fixture and needs a live receipt
  (AUTHORITY.md); the 177 existing cases that carry an unsorted opaque
  object already give the check its teeth.
- `harness/selftest.py` was red from the managed direction's arrival
  (0872d6e): its baseline ran that direction against the fake shim, which
  had no `managed_run` op. Fixed in the next commit (the fake shim echoes
  each run's recorded expectation; two managed mutations added).
