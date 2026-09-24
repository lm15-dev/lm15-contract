# 2026-09-24 — INV-053 in a browser: a coding the platform negotiated is already decoded

**Status: amendment PROPOSED, implemented in lm15-ts, awaiting ratification.**

## What happened

From the playground sign-in lab (a real page, Chromium on XPSwhite), a Claude
subscription signed in, then its model list and a model call to
`api.anthropic.com` failed inside lm15 with
`ProtocolError: unsupported Content-Encoding: "br"`. Anthropic never refused
anything.

## Why

INV-053 has two halves: encoded bytes never reach a parser, and requests
advertise `Accept-Encoding: identity` so SSE is not buffered. A page cannot do
the second: `Accept-Encoding` is a forbidden request header, the browser drops
it and sends its own list (`gzip, deflate, br, zstd` in Chromium 152). The
server compresses; the browser decodes before the page reads a byte (Fetch
Standard, "handle content codings"). The first half therefore already holds,
and refusing `br` refused a correct, already-decoded reply.

Checked 2026-09-24:

- `api.anthropic.com` answers `content-encoding: br` to a browser-style
  `Accept-Encoding`, and exposes the header to pages (the SDK saw it).
- `api.openai.com` and `api.x.ai` did not compress the small replies probed;
  OpenRouter compresses with `gzip` (already accepted). That is why no browser
  call hit this before: the rule applied since 2026-09-18 and the playground's
  earlier Anthropic traffic was streamed.
- Chromium: `new Request(url, {headers: {"accept-encoding": "identity"}})`
  drops the header; Node 24's keeps it.

## The amendment

Where the platform forbids setting `Accept-Encoding`, a Fetch transport
accepts `br` and `zstd` (the codings browsers negotiate themselves) and never
decodes them again. Anything else is still refused. Everywhere a transport can
ask for `identity`, nothing changes: `br`/`zstd` stay a `ProtocolError`.

Rejected alternatives:

- *Accept every coding under Fetch.* A coding the platform did not decode would
  reach the parser as bytes; only the ones browsers negotiate are safe.
- *Detect "browser" by globals.* Workers, Deno and embedded runtimes differ;
  the forbidden-header behavior is the property that matters, so it is tested.
- *Route Anthropic through the relay to strip compression.* Adds a party that
  sees credentials and prompts to work around an SDK bug.

What the browser still cannot guarantee (stated, not fixed): a compressed SSE
stream may be buffered by an intermediary; the page cannot ask otherwise.

## Other SDKs

The playground's Python, Rust and Go runtimes also speak through the browser's
fetch; each needs the same check before its Anthropic calls from a page are
trusted. Native transports are unaffected.
