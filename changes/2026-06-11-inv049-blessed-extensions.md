# 2026-06-11 — INV-049: the 4 extensions-passthrough keepers are blessed permanent

Decision (maintainer delegation): the four `config.extensions` passthrough
cases kept by the 2026-06-10 burn-down
(changes/2026-06-10-passthrough-rewrites.md) are PERMANENT provider-only
knobs, not debt. New invariant INV-049 in spec/invariants.md lists them with
rationales:

- `anthropic.thinking` / `anthropic.thinking_budget` — the wire `thinking`
  object's `"display"` field has no canonical Reasoning knob; no other
  provider exposes a thinking-display selector.
- `openai.max_tool_calls` — the Responses per-response tool-invocation cap is
  neither `max_tokens` nor a ToolChoice constraint; no canonical loop-budget
  concept exists.
- `openai.code_interpreter` — Responses `include`
  (`code_interpreter_call.outputs`) tunes provider-executed tool trace
  verbosity, which MAP-1 keeps out of canonical parts.

The audit's extensions-passthrough ratchet floor is 4 (these four cases).
Promoting any knob to a canonical key later is an additive spec change with
its own changes/ entry. No fixtures or code changed.
