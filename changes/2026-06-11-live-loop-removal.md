# 2026-06-11 — Live-session tool loop removed from the Python implementation

Maintainer positioning ruling (2026-06-11): "no loop... remove anything
that's not coherent." lm15 never executes tools or retries on the user's
behalf; it transforms and transports. Result's built-in tool loop was
removed on 2026-06-10/11; live sessions carried their own copy and it is
now removed as well.

Removed from `lm15-python2` (none of it was in the spec tables, so no
spec rows change and `tools/spec_drift.py` stays green):

- `WebSocketLiveSession(callable_registry=..., on_tool_call=...)`
  constructor parameters and `set_on_tool_call()`.
- Internal auto-execution helpers `_maybe_auto_execute_tool` and
  `_invoke_tool` in `lm15/live.py`.
- `ToolRegistry` type alias in `lm15/types.py` (a `dict[str, Callable]`
  whose only consumer was the live loop).

Unchanged, deliberately: `LiveServerToolCallEvent`,
`LiveClientToolResultEvent`, `ToolCallInfo` (typed views / transport
data), and `RETRYABLE_ERRORS` (classification data for the caller's own
retry policy — the comment now says so).
