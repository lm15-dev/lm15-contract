# Concurrency surface declared out of contract scope, 2026-06-10

Adds a "Concurrency" section to `harness/PROTOCOL.md`. No cases, goldens,
or comparison semantics change.

The contract pins pure transformations (build/parse/map). Concurrency and
transport surface are per-language idiom and are out of contract scope:
Python ships sync + mirror Async* classes (lm15-python2 `AsyncOpenAILM`,
`AsyncAnthropicLM`, `AsyncGeminiLM`, `AsyncOpenAIChatLM`, landed
2026-06-10); Go uses context; TypeScript is async-only; Julia uses tasks.

The binding requirement on ports: every concurrency surface MUST share the
pure core (request building, response/stream parsing, error mapping) so
that shim conformance over the pure core covers all of a port's
concurrency surfaces. Python's async classes satisfy this by composition —
they delegate all mapping to an inner sync adapter whose transport can
never be used.
