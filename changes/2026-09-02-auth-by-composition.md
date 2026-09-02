# 2026-09-02 — Auth by composition: the access policy is a value (AUTH-10, proposed)

Ratification: PENDING — awaiting Maxime Rivest. Decision D from the
2026-09-01 API review ("model subscription auth as composition, not
subclassing"), accepted in principle then; the plan asked for is this
entry and the implementation. Do not push before ratification.

## What this changes

- **AUTH-10** in `spec/auth.md`: an adapter is a dialect bound to an
  `AccessPolicy` value. The field table, the seven policies, and the
  exhaustive list of `backend` branches are normative; ports copy the
  table as data and consult it at the named points.
- No fixture, golden, or wire byte changes. Harness 13/13 green on the
  same corpus; the Claude Code, Codex, and xAI request cases produce the
  same headers and bodies as before, now from policy fields.

## Why a value, and where the line is

- Go and Rust have no inheritance. `ClaudeCodeLM(AnthropicLM)` and
  `OpenAICodexLM(OpenAILM)` each overrode headers, payload defaults, error
  hints, and endpoint blocks; a port would have re-derived those from
  memory in its own shape. A frozen value with a stated consult list is a
  table lookup in every language.
- The line: **access** facts (credential path, headers, surfaces, backend
  variant, system prefix, base URL) are policy. **Provider** facts stay in
  code: xAI's image and video wire and its refusals are what xAI does,
  not how it is reached, so `XaiLM` remains a provider adapter that
  composes only its credential path. Two of the three subclasses become
  names; the third becomes honest about what it is.
- `backend` is deliberately a variant name, not more flags. The Codex
  backend differs in four places that are behaviour (error envelope,
  models endpoint shape, streaming-first, payload strips); those are
  listed exhaustively in AUTH-10 and are a `match` in any language.
  Encoding each as a boolean would have made the policy a flag soup with
  no fewer branches.

## Reference implementation (lm15-python)

- `lm15/features.py`: `AccessPolicy` (pure data; `ProviderManifest` is the
  same class). `lm15/access.py`: the table, the per-provider credential
  loaders, the stored-credential probe, `auth_header`.
- `BaseProviderLM._bind_access` resolves the credential (explicit key
  wins; stored login through the provider's loader; `key` policy with no
  key is `NotConfiguredError` naming the env keys) and records which rung
  won so the login hint applies only when a stored login did.
- Surfaces are gated in the shared drivers on `access.supports`, so a
  dialect that implements files still raises on a login that lacks them.
- `ClaudeCodeLM` / `OpenAICodexLM` hold the class-level policy and
  constructors; a test asserts they define nothing else. A second test
  asserts `AnthropicLM(access=CLAUDE_CODE)` and `ClaudeCodeLM()` produce the
  same wire. 18 new tests; 971 total.
- Async mirrors carry the same constructor (the parity test enforced it).

## Behaviour changes, stated

1. `api_key` is optional on every dialect; a `key` policy without one now
   raises `NotConfiguredError` (was `TypeError` from the dataclass).
2. `lm.supports` is the bound policy's surfaces (instance), not the
   class's. Class-level `Cls.supports` is gone; `Cls.manifest.supports`
   is the class default.
3. `provider` is no longer a constructor argument; it derives from the
   policy.
4. Header order for Claude Code changed (`anthropic-beta` now last); the
   harness compares header maps, and servers do not order headers.

## Stated trade-offs

1. `backend_options` is a string map — an escape hatch shaped like
   `extensions`. It holds exactly one knob today (`client_version`).
2. Credential loaders remain per-language code keyed by provider; the
   policy cannot carry a function portably. The table of loaders is small
   (three) and named in AUTH-10.
3. `ProviderManifest` survives as an alias rather than a rename across the
   spec and support matrix; the support-matrix audit keys on field names
   that did not change.
