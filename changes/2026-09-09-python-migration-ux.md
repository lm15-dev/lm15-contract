# Shared explicit credentials and Python migration streaming

Ratified by Maxime Rivest in this conversation, 2026-09-09: “ok yes, do
these”, plus the explicit request to use
`router.complete_from_openai_chat(..., stream=True)` for streaming.
Rollout narrowed by the maintainer: “we focus on python first”.

## Problem

An OpenAI account key worked for both APIs through OPENAI_API_KEY, but an
explicit `api_keys={"openai": ...}` applied only to Responses. Migrating
Chat Completions could therefore select a different ambient account.
The tutorial also made users manually connect the stream assembler.

## Decisions

- AUTH-1: exact provider entry first, else the single entry with an identical
  non-empty ordered env-key declaration. No overlap-based or empty-list
  sharing. Multiple shared candidates raise `not_configured`, even when
  values look equal. Credential callables are not invoked during lookup.
- Duplicate provider spellings and empty explicit credentials are refused
  rather than silently falling back or choosing by dictionary order.
- AUTH-7: the same selection rule powers the doctor, which identifies the
  source key without showing the credential. Python accepts a Resolution
  directly; the router config remains an explicit argument.
- Python migration helper: `stream=True` returns ResponseStream; omitted or
  false returns Response. Async mirrors this with an awaited helper and
  AsyncResponseStream. Non-booleans raise TypeError. Native complete and
  raw-event stream methods retain their existing API.
- Stream wrappers expose close/context-manager support, propagate source
  closure through the coalescer, preserve cancellation/errors, and refuse
  completed-response access after an unfinished stream is closed.

## Evidence and bounds

These are canonical policy/API choices, not new provider wire facts. No live
provider receipt is needed to establish how the local SDK selects a supplied
credential or wraps its existing stream. New hand-authored auth cases cite
AUTH-1; Python tests exercise actual routing and dialects using fake HTTP,
including callable renewal, overrides, ambiguity, isolation, usage assembly,
errors, closing, and async cancellation.

## Trade-offs

- A key entry reaches sibling endpoints, not merely its literal endpoint.
  Exact entries still permit different accounts. URL and host settings do
  not inherit, and this rule does not prove that two hosts accept the key.
- Ambiguity is an error instead of an arbitrary account choice.
- The migration helper has two return types; boolean-literal overloads help
  static callers, while a runtime boolean requires handling the union.
- Assembly retains the response in memory. Use raw events if this is not
  wanted. Closing releases local resources; it does not guarantee an
  immediate end to provider generation or billing.
- Python is the first implementation. Rust and TypeScript propagation is
  explicitly deferred. Passing Python tests is not cross-language parity.
