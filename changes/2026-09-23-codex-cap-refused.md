# Codex: an output cap or store=true is refused, never stripped

**Applied 2026-09-23 (a bug against MAP-13 rule 4, not a new rule).**

The ChatGPT Codex backend (`openai-codex`) accepts no max-token field and
cannot store a response. Four SDKs (Python, TypeScript, Go, Julia) removed
`config.max_tokens` and overrode `store=true` from the wire without recording
anything: `plan()` and `response.adaptations` were empty and the caller's
spending limit was silently not applied. Found while capturing the docs'
first-request answers (a 16-token cap came back as 367 tokens).

[MAP-13](2026-09-14-adapt-visibly.md) rule 4 already decides it: dropping
`max_tokens` means unbounded spend, so it is refused. Rust and R already
refused. All six now raise `UnsupportedFeatureError` at build time, with the
same message:

- `openai-codex: config.max_tokens: this backend has no output cap; dropping it risks unbounded paid generation`
- `openai-codex: config.store: this backend cannot store a retrievable response; the program may depend on retrieval`

(`feature` is `config.max_tokens` / `config.store` where the SDK's error
carries one.) A request without a cap is unchanged.

Follow-up: a shared case (`cases/openai-codex/…`, raising at `build_request`)
so the SDKs' copied corpora pin it; each SDK has its own test until then.
