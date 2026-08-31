# 2026-08-31 — auth fixtures: port mirrors registered

All four ports rebuilt their first post-removal module against the auth
contract (spec/auth.md, ratified 2026-08-31) and now carry mirrors of
`auth/resolution.json`, verified by their own test suites:

| repo | mirror | runner |
|---|---|---|
| lm15-python | `conformance/auth_resolution.json` | `tests/test_auth_resolution_contract.py` |
| lm15-go | `conformance/auth_resolution.json` | `auth/contract_test.go` |
| lm15-rs | `conformance/auth_resolution.json` | `tests/auth_resolution_contract.rs` |
| lm15-ts | `conformance/auth_resolution.json` | `tests/auth_resolution_contract.test.ts` |
| lm15-jl | `conformance/auth_resolution.json` | `test/runtests.jl` |

Dual-landing rule, extended: an edit to `auth/resolution.json` lands in
this repo and in ALL five mirrors in the same change set, or not at all.
This is the same discipline as the 2026-06-09 migration entry, with more
copies; the Stage-2 harness cutover remains the path to removing the
mirrors entirely.

Port scope at this landing (stated in each port's README and commit):
AUTH-1/2/5/7 plus the AUTH-8 read side are implemented and
fixture-verified; the AUTH-3/4 write side (locked double-checked refresh,
atomic 0600 writes) and the AUTH-9 login primitives remain owed by every
port except the reference implementation.
