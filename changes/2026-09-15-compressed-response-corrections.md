# Compressed-response decoder corrections

Python implementation correction authorized by Maxime Rivest on 2026-09-15
following review of DSPy PR #10409. No provider request mapping or canonical
value changes. This does not ratify the broader per-port codec-support proposal
A2 in `2026-09-14-gauntlet-connection-budget-and-reply-faults.md`.

## Basis

- RFC 1950 §2.2 defines the two-byte zlib header (compression method/window,
  header check modulo 31). A transport read boundary does not end that header.
- RFC 1952 §2.2 defines gzip as a sequence of members; the decoder must not
  stop at the first member. Every member has its own integrity trailer.
- HTTP message framing separates body bytes from any next message. Content
  decoding applies only to the framed bytes, in reverse Content-Encoding order.

The previous inflater marked deflate decoding started after one byte, disabling
its fallback before it had enough bytes to recognize a wrapped header. It also
ignored zlib.unused_data, which contains later gzip members. This could return
only part of a valid body and ignore corrupt/truncated subsequent members.

## Correction and boundaries

Python waits for two deflate bytes, selects the RFC zlib wrapper when the header
is valid, and otherwise uses the existing legacy raw-deflate compatibility path.
A valid wrapper header wins in ambiguous cases; the decoder never retries a
later checksum failure as a different format after delivering output. This is
bounded header recognition, not an unbounded buffer for guessing two formats.

For gzip/x-gzip, bytes after one completed member feed a new member decoder,
across any number of input chunks. Zero padding between/after members is
accepted, like Python's standard gzip reader. Other trailing bytes must form a
valid member, otherwise they raise ProtocolError. Empty members are valid.
Truncation, corrupt trailers, and trailing bytes after a deflate stream also
raise ProtocolError. Body framing and connection ownership are unchanged.

Trade-offs: a malformed reply that previously appeared to succeed by dropping
its suffix now fails clearly. Legacy raw deflate is a compatibility convention,
not the RFC-defined HTTP deflate encoding; ambiguous zlib-looking headers are
interpreted as zlib. No new dependency, retry, response-size policy or provider
call was added.

## Verification

Before the fix, new regression tests produced 38 failures and 6 passes.
After the fix, the combined compression suites produced 63 passes. Tests cover
all single splits and bytewise delivery of short reference bodies across
Content-Length, chunked and EOF framing; stacked codings; multiple/empty gzip
members; padding; corrupt and truncated later members; and sync/async transport
connection reuse and release after failure. Bodies are synthesized with Python's
standard zlib/gzip compressors, not generated from the decoder being checked.
No provider wire fixtures or goldens were rewritten.
