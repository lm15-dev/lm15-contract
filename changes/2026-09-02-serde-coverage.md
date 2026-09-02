# 2026-09-02 — Serde coverage closed and ratcheted; porting playbook

Ratification: not required. Additive vectors for types already in the
spec, a report-only audit promoted to a hard check now that it is at zero,
a stale protocol list synced, and a playbook. No rule, golden, or wire
byte changes.

## What changed

- `serde/canonical.json`: 11 vectors closing the reported gaps —
  `cache_info` (2), `cache_page` (2), `cached_prefix` (2),
  `token_logprob` (2, covering `TopLogprob`), and `cache_config` with
  `prefix` / `resource` (3, covering the `CachePrefix` vocabulary). The
  `cache_page.empty` vector is `{}`: `items` is omit-empty per
  `spec/types.md`, and the first draft with `"items": []` was correctly
  refused by the harness as non-canonical.
- `harness/PROTOCOL.md` "Serde kinds": the list called itself normative and
  had drifted to 25 while the reference had 35 (`token_logprob` is new
  today; the generation, video, and cache kinds were never listed). Synced.
- `tools/audit.py`: surface coverage is HARD (0 types, 0 enums uncovered)
  and the PROTOCOL kind list must equal the kinds present in the vector
  file, both directions. `ToolCallInfo` is declared a non-wire type
  (callback view of a ToolCallPart) rather than left as a permanent gap.
- `playbooks/port.md`: the order of work, gates, rules, and shared idioms
  for a language port, so four ports converge on one shape. Two gaps it
  names rather than hides: the harness does not verify the checkout hash
  (the port's CI must), and the mutation self-test drives only the fake
  shim.

## Evidence

serde direction 109/109; audit green with the new hard checks; 13/13
directions; lm15-python 971 tests.
