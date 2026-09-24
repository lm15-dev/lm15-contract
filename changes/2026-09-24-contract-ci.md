# 2026-09-24 — Contract CI ran nothing from 2026-09-07 to today

Status: repair (no normative rule changes).

## What was wrong

`.github/workflows/contract.yml` gained a step on 2026-09-07 (commit 8cb228b)
named `Content coverage (MAP-10: every binding …)`. Unquoted, the `: ` inside
the name makes the file invalid YAML. GitHub rejected the workflow before any
job started, so every push since then shows a failed run with zero jobs, and
none of the gates ran: provenance, secrecy, audit, spec drift, MAP-10
coverage, the gateway record, the tooling tests or the mutation self-test.

## What the gates found once they ran again

Both were real drift the broken CI had hidden:

1. **MAP-10: TypeSafe's tool-result cell was blank** since TypeSafe joined the
   registry (2026-09-17). Systemone has no tools, so a tool result can never
   reach its wire. Pinned as a refusal:
   `cases/typesafe/tool_result_image_raise.json` (Python, TypeScript, Go and
   Rust each refuse it at `build_request`, `feature: tools`).
2. **Audit: `NamedCredential` / `NAMED_CREDENTIALS`** (AUTH-1 named credentials,
   2026-09-19) was reported as a serde gap. It is a RouterConfig input, never
   serialized, and `spec/vocabularies.md` already documents it; it joins the
   audit's policy vocabularies, which are checked value-for-value against that
   table.

## Repair

The step name is quoted. All eight steps pass locally with a bare Python 3,
as the runner has.
