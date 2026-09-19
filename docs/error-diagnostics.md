# Provider error diagnostics

Normative amendment: changes/2026-09-19-rate-limit-diagnostics.md.

## HTTP evidence, not a retry engine

Every raised lm15 error exposes `rate_limit_headers` (Python),
`rateLimitHeaders` (TypeScript): an immutable mapping of lowercase header
names to ordered arrays of original string values. Empty means no retained
evidence, not unlimited quota. Apply this on complete, stream failures and
auxiliary endpoint HTTP errors, regardless of status or error subclass.

Retain only these exact case-insensitive names:

- `retry-after`, `retry-after-ms`, `x-ms-retry-after-ms`
- `x-ratelimit-type`, `x-ratelimit-abusepenalty-active`
- `x-ratelimit-{limit,remaining,reset,renewalperiod}-{requests,tokens}`
- `anthropic-ratelimit-{requests,tokens,input-tokens,output-tokens}-{limit,remaining,reset}`

The brace notation enumerates a CLOSED set, not a wildcard. Never retain
Authorization, api-key, cookies, arbitrary x-* headers, or x-ratelimit-key
(which can identify an account/deployment). Request IDs retain their own
existing metadata field.

Preserve duplicates, negative counters, contradictory values, and reset
units exactly; no case/value normalization beyond lowercasing header names.
A snapshot accepts at most four values per name, each 1–256 printable ASCII
characters (0x20–0x7e). Reject other values rather than clipping them into
plausible numbers. This is a bounded diagnostic snapshot, NOT a full HTTP
capture. Duplicate values retain arrival order. Sorting names for display
is allowed. SDK constructors copy/freeze snapshots so later mutations of the
input cannot rewrite an error's evidence. No snapshot calls credentials,
performs I/O, or triggers a retry.

A name allowlist avoids importing unrelated secrets; it is not a promise
that an upstream server can never put sensitive data in a diagnostic field.
Applications must handle provider errors according to their own logging policy.

## Useful wait hints

Existing `retry_after` / `retryAfter` precedence remains: a finite nonnegative
body-derived number of seconds, otherwise the FIRST `Retry-After` header
(delta-seconds or HTTP-date). If neither gives a valid hint, try the FIRST
`retry-after-ms`, then the FIRST `x-ms-retry-after-ms`, each a finite
nonnegative decimal number of milliseconds divided by 1000. Millisecond
headers are numbers, never dates. Unknown/negative/nonfinite waits stay absent.
Do not derive retry_after from a rate-limit reset header, remaining balance,
error text, or the maximum of contradictory hints. Raw snapshots preserve
conflicting advice separately. Retry advice is never a success guarantee.

Request-id fallback order: existing x-request-id, request-id,
x-amzn-requestid, x-amz-request-id, x-ms-request-id, then apim-request-id,
then x-typesafe-request-id. A body request ID wins. Additional diagnostics
must still be attached when an error already has a request ID.

## Display

Preserve the provider's message/code/status. ProviderError string rendering adds a
compact diagnostics paragraph when headers or a retry hint are available,
labelled raw/advisory, with a bounded preview (2048 characters plus a
truncation notice; full retained values remain on the error). Escape values
for display. `no_capacity` may be described as rate/capacity limiting, but
MUST NOT be described as proof of an unsupported model/endpoint or as proof
that buying provisioned capacity is necessary. Do not append diagnostics
repeatedly or mutate the underlying `message` when formatting.

## Errors inside a successful HTTP stream

On canonical error events emitted by an HTTP stream driver, store transport
evidence in the optional `ErrorDetail.http_response` object (TypeScript
`httpResponse`), default `{}`. The object accepts only the following keys;
unknown keys are rejected:

```
{"request_id": "...", "retry_after": 39.0,
 "rate_limit_headers": {"x-ratelimit-limit-requests": ["1"]}}
```

Omit absent/empty fields and omit the block when empty. `request_id` is a
non-empty string, `retry_after` finite nonnegative seconds (int coerces to
float), and `rate_limit_headers` is normalized by the same bounded snapshot
rules as exceptions. Null is not an object. The HTTP driver's block replaces
only this field; the error's code/message/provider_code are preserved.
Pure dialect parsing (no transport headers) does not invent this block.
When materializing the stream as a Response raises the error, propagate the
block into exception metadata. Do NOT give an in-stream error HTTP status
200 merely because the handshake succeeded. A ProviderError raised during
stream parsing also receives the handshake diagnostics.

This is diagnostic evidence from the HTTP response, not proof of quota
balances at the later moment an in-stream error occurred. Never infer 429
from quota headers alone. Azure Responses' explicit `no_capacity` and
`too_many_requests` codes classify as `rate_limit` even inside HTTP 200
(documented by Microsoft's Responses guide, streaming error example);
retain the original `provider_code`. Other codes retain their existing mapping.

## Browser restriction

Snapshots preserve duplicates as exposed by the transport; a Fetch Headers
object may already have combined duplicate fields. Do not split such values
on commas (HTTP dates themselves contain commas).

Browser TypeScript sees only headers exposed by CORS. If Azure or a gateway
does not expose a header, leave it absent: do not proxy a request merely to
collect diagnostics and do not imply an empty snapshot means no throttling.
