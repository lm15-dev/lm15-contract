# 2026-09-19 — The gateway: a second lm15 product, and where its boundary sits

Ratification: **RATIFIED** — Maxime Rivest, 2026-09-19, in session
("I think I ratify and then we go"), after setting the direction ("use
LM15 everywhere in your company … you can start by having it as a
gateway"; "we do that all through first step capturing the traffic")
and reviewing the four flagged uncertainties: the boundary revision
(D2, "that wasn't a very big decision … but it should not remove it
from being a delightful library also"), the translate lane (D4, "doesn't
scare me … handle it with care and professionalism"), subscription and
corporate logins (D11, "our architecture is supposed to anyway be
general enough to do that well"), and secrets inside bodies (companion
C5b). Revises an in-session decision of 2026-09-15 (aiconvo
`01a0a6e4`). Companion: `changes/2026-09-19-capture-record.md` (the
record the gateway writes). Nothing below is implemented.

## The problem

A person running Pi, Claude Code, Codex, OpenCode and an IDE plugin
cannot see what leaves their machine for a model, when, or under which
account — and cannot change it without editing each program. aiconvo
exists only because two of those programs happened to write traces to
disk; every other program is dark. The same blindness scales up: a
company cannot attribute model spend to teams, cannot reroute a vendor
tool to its own backend, cannot run an experiment across tools, and
today buys a server-side gateway (Cloudflare AI Gateway, Azure APIM,
LiteLLM Proxy, Portkey) that sees only the traffic someone remembered to
point at it, and translates between providers with per-vendor
special-casing and no oracle.

lm15 already owns the two halves such a gateway needs: a ratified
request/response contract with conformance fixtures, and adapters in
several languages. What it lacks is the product that puts that contract
in the path of traffic the application did not write with lm15.

## Decisions

**D1 — Scope.** The gateway is a second lm15 product, distinct from the
SDK: a local HTTP service that applications reach through a base URL,
which forwards to providers, records every exchange in the capture
record (companion note), and optionally routes. It is the entry point of
the adoption path *capture → control → translate → share*; each later
stage reads only what the earlier stage wrote. The membership test of
`spec/SCOPE.md` is unchanged: the gateway carries the same Parts and
Requests as the SDK; it adds no canonical type.

**D2 — The boundary, revised.** On 2026-09-15 the boundary was drawn
"lm15 executes explicit connections; cmpnd owns named resources,
permissions, budgets, credential storage." That decision was made about
the *library* and stands for the library (`THEORY.md` §3.10: no retries,
no fallback, no cost ledger, no registry — a ten-line script must never
need one). It does **not** stand for the gateway. The gateway product
owns: route rules, tags and cost-center attribution, budgets and
allowlists, retention, redaction rules, and a credential store (apps hold
a local URL; the gateway holds the keys). cmpnd becomes a consumer of the
gateway — its trusted egress points at one — not the owner of these
concepts. Reason: for a service the routing table and the ledger *are*
the product; leaving them to a downstream platform would make the
consumer tier (D9) impossible. Two things this revision does **not**
do: it does not demote the library — the SDK remains a first-class,
delightful product in every language, and the gateway is built *from*
it, never the other way round; and it does not withdraw support for
cmpnd — the explicit-connection composition the 2026-09-15 session
asked for is still wanted, at lower priority than the gateway.

**D3 — Language and foundation.** Go, built on `lm15-go`. Reasons, each
one a stranger's-laptop requirement: one static binary per OS/arch,
cross-compiled from one machine; `net/http` + `httputil.ReverseProxy`
already do streaming, HTTP/2 and WebSocket hijack; the HTTP client
trusts the operating-system certificate store and honours
`HTTPS_PROXY`/`NO_PROXY` by default (D7); process↔connection mapping for
the scanner (D8) is portable through `gopsutil`. Rejected: Rust
(`lm15-rs` is the least complete port, and rustls's root-store choice is
the classic enterprise failure), Python (a daemon, not a script; the
decoders can still run in Python over the record — D5).

**D4 — Two lanes, chosen per rule; pass-through is the default.**
*Pass-through*: bytes forwarded untouched — headers, beta flags, SSE,
WebSocket — so an application using a feature the contract has not met
yet keeps working. *Rewrite*: same dialect, host and/or model string
substituted (an OpenAI-shaped app to a local vLLM; `sonnet` → `opus`);
no decode needed. *Translate*: the request is decoded into a canonical
Request, built for another wire, and the response is re-encoded into the
dialect the application spoke, so the application does not notice. Only
a rule selects rewrite or translate. Translation obeys MAP-13 exactly:
adapt what is unambiguous, record every `Adaptation` on the exchange,
refuse — with an error in the application's own dialect — when a guess
could hurt. No silent downgrade, ever; this is the single behaviour that
distinguishes the product from the incumbents.

The cost of this lane, stated plainly: today the contract maps canonical
types OUT to a wire request and a wire response IN; the only foreign
reader is MAP-12 (a Chat Completions request body). Translate needs the
other two directions — every dialect's *request* read into a canonical
`Request` (MAP-12 generalised to Anthropic, Responses, Gemini, and to
the `chatgpt.com/backend-api` variant), and a canonical `Response` /
event trace *written* as that dialect's body and stream, including tool
calls, thinking blocks and the end-of-stream shapes. That is a new axis
of the corpus with its own fixtures and verdict tables, carried with
the same discipline as MAP-1..14. It is stage 3 (D9) and nothing before
it waits on it.

**D5 — Capture never depends on decoding.** The forwarding path writes
the raw record and cheap metadata (model, tokens, latency, first-byte
time, status) and is complete on its own. Decoding wire bytes into
canonical Request/Response is a separate pass that any SDK may run over
the record (Python first, as the reference; Go second) and may finish
later or partially. A decoder that cannot handle an exchange marks it
`decode.status = partial` with the raw bytes still present; it never
fails or delays a request. Corollary: the gateway is a continuous source
of live captures for the contract corpus — real Claude Code, Codex and
Pi traffic exercising features nobody reproduced by hand — subject to
AUTHORITY.md's receipt rule when promoted to a fixture.

**D6 — Reach the gateway by base URL, not by certificate.** Every
program in scope overrides its endpoint: `ANTHROPIC_BASE_URL`,
`OPENAI_BASE_URL`, `GOOGLE_GEMINI_BASE_URL` (Claude Code, Pi, the
official SDKs in every language), `~/.pi/agent/models.json`,
`~/.codex/config.toml` (`chatgpt_base_url`), OpenCode's
`provider.*.options.baseURL`. `lm15 gateway setup` writes these once
(Home Manager / launchd / Windows user environment) and appends
`127.0.0.1,localhost` to `NO_PROXY` (D7). The URL carries attribution:
`http://127.0.0.1:4315/t/<tag>/<provider>/…`; untagged
`/<provider>/…` falls back to User-Agent. When the gateway is down,
programs fail loudly instead of bypassing it — that is the point.
Certificate interception (`HTTPS_PROXY` + installed CA) is shipped only
as an explicit opt-in (`lm15 gateway intercept`) that prints its
limits at install time; it is never default, because it recreates the
"something invisible altered my machine" feeling the product exists to
remove, and Rust/Go programs with bundled roots ignore it anyway.

**D7 — Enterprise network behaviour.** Because every application now
talks plain HTTP to loopback, the gateway is the only process that must
be a good corporate citizen, and it is: honours `HTTPS_PROXY`,
`HTTP_PROXY`, `NO_PROXY` and Basic proxy auth; trusts the OS store (so
Zscaler-style corporate CAs work with no configuration, and programs
that individually failed behind them start working); per-provider
`upstream` (base URL + fixed headers) so it chains in front of an
existing Cloudflare/APIM/LiteLLM deployment instead of competing;
listens on loopback only by default with no auth (a shared-host mode
with a token is not v1). Not doing: PAC files, NTLM/Kerberos proxy auth —
stated in docs, not half-built.

**D8 — The scanner and the coverage view.** Independently of routing,
the gateway periodically lists established connections with their
owning process (`ss`/`lsof`/`Get-NetTCPConnection` via gopsutil; no
root, no certificate) and matches remote addresses against the
provider hosts it resolves itself. Address matching is definitive for
providers on their own ranges (Anthropic, Google) and *probable* for
providers behind a shared CDN (api.openai.com and chatgpt.com sit on
Cloudflare addresses shared with much of the web). Confirming those
requires seeing the program's DNS lookups, which on Linux
(`resolvectl monitor`) and macOS is a privileged operation — checked
2026-09-19 on lambda: the monitor returns nothing to an unprivileged
user. So DNS confirmation ships as an **optional** small privileged
helper the user installs knowingly; without it the view says
"probably OpenAI" and says why. Result, per program: **covered** (goes through the gateway; fully recorded),
**observed** (talked to provider Z at time T; not recorded), or
**observed, not coverable**. For observed programs the view offers the
recipe: a known-app knowledge base (Cursor, Zed, Aider, Continue, Cline,
… with the exact setting and value), `lm15 gateway run -- <cmd>` for
anything using a standard SDK, or the honest "no override exists". The
boundary is stated, not hidden: one can always see *that* a program
talks to a model; one can only read *what* it says if it is routed.

**D9 — Order of work follows the free-tier-first model.** (1) *See*:
capture, live feed, scanner, coverage menu — useful alone, solves the
feeling. (2) *Control*: rewrite lane, key store, allowlist, kill switch,
per-tag spend. (3) *Translate*: cross-dialect routing, weighted A/B with
a sticky key per conversation, fallbacks — where the contract becomes
visibly superior. (4) *Share*: hosted team dashboards, cost centers,
multiplayer conversations, memory — the paid tier. Stages 1–2 ship with
no decoder; the capture record is the interface between all four.

**D11 — Credentials and logins: one general design, policy decides.**
A gateway *connection* is what the 2026-09-15 session defined —
destination, protocol, authentication source, compatibility settings —
and the authentication source may be an API key, a bearer/OAuth token
with refresh, or a subscription login (OpenAI Codex, xAI, Anthropic
Claude subscriptions, all of which lm15's AUTH-1 chain already knows how
to find). Three cases, one mechanism: (a) the application carries its
own credential (a developer's personal Codex login) — pass-through
forwards the headers untouched and the ledger attributes the spend to
the tag; (b) the gateway *holds* the credential and the application has
none (a corporate key, or a corporate subscription login shared by a
team) — the gateway's store substitutes it, the application sees only
the local URL; (c) both exist and a rule says which wins. Whether a
given tag may use a subscription, a personal key, or only the corporate
connection is an **allowlist setting per tag**, not an architectural
limit; the default allows everything the application already did. The
provider's terms for subscription use are the user's or company's to
respect, and the docs say so; the gateway neither enables nor forbids
anything the application could not do alone. `openai-codex`
(`chatgpt.com/backend-api`) is therefore a first-class provider name in
the default upstream table, alongside `xai`.

**D10 — What the contract repository owns.** The capture record schema
and its fixtures (`gateway/` in this repository, per the companion
note); the semantics of lanes, adaptations and refusals on a translated
exchange (MAP-13 applies unchanged); the coverage vocabulary of D8. The
gateway's own configuration format, route-rule language, key store and
UI are product surfaces outside the contract, versioned with the
binary.

## Trade-offs, stated

- A rewrite or translate rule can break an application when the rule is
  wrong. Mitigated, not removed: rules are opt-in per tag, pass-through
  is default, and every rewritten exchange keeps the original bytes.
- A local key store concentrates secrets that today sit in `.env` files
  and `~/.claude`. No worse in kind; worse in concentration. File mode
  0600, OS keychain as a backend from the first release.
- Translation quality is capped by decoders that do not exist yet. That
  is why stages 1–2 are defined to need none.
- Go over Rust costs ~10 MB of resident memory and garbage-collector
  pauses, neither observable for a local proxy; it buys portability and
  correct-by-default TLS and proxy behaviour.
- Base-URL redirect is one setup step, not zero. Zero is only reachable
  through the certificate path, which was rejected on the product's own
  principle.

## Defaults taken at ratification

Resolved in session or by the maintainer's standing preference for
expert defaults over further questions; each may change with a
`changes/` entry:

- D2 confirmed as written, with the library-stays-first-class clause.
- `openai-codex` and `xai` are first-class upstreams (D11).
- Default port `4315`; URL shape `/t/<tag>/<provider>/<provider path>`;
  untagged `/<provider>/<provider path>` accepted.
- The binary lives at `lm15-go/cmd/lm15-gateway` until it needs
  dependencies the SDK module should not carry (the scanner's
  `gopsutil` is the first candidate); at that point it moves to its own
  repository depending on `lm15-go`.
