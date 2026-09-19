# 2026-09-19 — The capture record: what the gateway writes, and what everything else reads

Ratification: **RATIFIED** — Maxime Rivest, 2026-09-19, in session
("I think I ratify and then we go"), together with the companion
`changes/2026-09-19-gateway-boundary.md` (D5, D8, D10, D11). Revised
before ratification on the reviewer's own findings: the decoded form
moved to its own stream (C2b) instead of a second row per exchange, the
scanner's DNS match became an optional privileged helper (C4), and
secrets inside bodies got their own rule (C5b). Nothing below is
implemented.

## The problem

aiconvo could be built only because Pi and Claude Code wrote session
traces in formats aiconvo learned to read after the fact. The gateway
makes every application write the *same* trace. That trace is the
interface between capture, control, translate and share; it deserves the
rigor of the request/response contract: a versioned schema, redaction
rules that cannot be forgotten, fixtures, and a stated relationship to
the canonical types. Without it, the dashboards, the cost ledger and the
decoders would each invent their own reading of the raw bytes.

## Decisions

**C1 — Four append-only streams per day, plus content-addressed raw
bytes.** Under the gateway data directory (Linux
`$XDG_DATA_HOME/lm15/gateway`, macOS `~/Library/Application
Support/lm15/gateway`, Windows `%LOCALAPPDATA%\lm15\gateway`; mode
0700):

| path | one row per | purpose |
|---|---|---|
| `exchanges/YYYY-MM-DD.jsonl` | request | the ledger: who, what model, how many tokens, how long, how routed, decoded form when available |
| `events/YYYY-MM-DD.jsonl` | wire frame (SSE event, WebSocket message, or the single body of a non-streamed reply) | timing of streaming traffic |
| `scan/YYYY-MM-DD.jsonl` | observed connection | the coverage view (boundary D8) |
| `decoded/YYYY-MM-DD.jsonl` | decoder pass over one exchange | the canonical `Request`/`Response`, joined to `exchanges` on `id`; written later, possibly by another program (boundary D5) |
| `raw/<sha256[:2]>/<sha256>` | redacted request or response (headers + body) | verbatim evidence, deduplicated by exact content |

JSONL because a crash loses at most one line and `grep` works.
`lm15 gateway compact` rewrites closed days to Parquet under
`parquet/<stream>/YYYY-MM-DD.parquet`; DuckDB reads both directly.
Prefix deduplication of repeated system prompts is a compaction
optimisation, not part of this record.

**C2 — The exchange row.** Field order is the canonical order; omit-empty
follows `docs/serde-rules.md` (absent, never `null`, unless stated).

| field | type | presence | meaning |
|---|---|---|---|
| `v` | int | always | capture schema version; this note defines `1` |
| `id` | string (ULID) | always | exchange id; `events` and `raw` reference it |
| `t` | RFC 3339, ms | always | first byte received from the application |
| `t_end` | RFC 3339, ms | omit-empty | last byte sent to the application; absent while in flight or on abort |
| `tag` | string | omit-empty | from `/t/<tag>/…`; the cost-center / program label |
| `origin` | object | always | `user_agent` (string, omit-empty); `pid`, `exe` (loopback peer lookup; omit-empty; best effort) |
| `provider` | string | always | the upstream name the URL selected (`anthropic`, `openai`, `openai-codex`, `gemini`, `typesafe`, `ollama`, or a user-defined upstream) |
| `dialect` | string | always | wire dialect detected from path and body: `anthropic`, `openai`, `openai-chat`, `gemini`, `typesafe`, `unknown` |
| `method`, `path` | string | always | as received; `path` after the tag/provider prefix is stripped; query string with secrets removed (C5) |
| `transport` | string | always | `http`, `sse`, `websocket` |
| `upstream` | object | always | `url` (after routing), `status` (int, omit-empty), `ttfb_ms`, `latency_ms` (omit-empty until known) |
| `model` | object | always | `asked` (what the application sent), `sent` (after routing), `served` (from the response, omit-empty). Equal values are still all written: the ledger must not require a join to answer "was it rerouted?" |
| `usage` | object (Usage) | omit-empty | the canonical `Usage` type, extracted cheaply from the response or final stream frame; the same accounting caveats as `spec/types.md` "Usage" |
| `route` | object | omit-empty | `rule` (name), `lane` (`passthrough`, `rewrite`, `translate`), `experiment`, `arm`, `sticky_key` (omit-empty each). Absent means: no rule matched, pass-through |
| `adaptations` | array (Adaptation) | omit-empty | MAP-13 records from a `translate` lane; the same type as `Response.adaptations` |
| `error` | object | omit-empty | `code` (ErrorCode vocabulary), `message`; present when the gateway itself failed or refused (a provider's error is in `upstream.status` and the raw response, and is *also* summarised here with the canonical mapping) |
| `redacted` | array of string | always (may be `[]`) | header and query names whose values were replaced (C5); an auditor can see what was removed without seeing it |
| `secrets` | object | omit-empty | C5b: `found` (int), `kinds` (array of string), `action` (`marked` \| `scrubbed`); present only when the body scan matched |
| `raw` | object | always | `request`, `response` (sha256 hex; `response` omit-empty on abort) |

An exchange row is written exactly once, when the exchange ends or
aborts (the live feed, C7, additionally emits an in-flight row that is
never persisted). Nothing in this stream is ever rewritten.

**C2b — The decoded row.** `decoded/` holds one row per decoder pass
over one exchange: `{v, id, t, decoder, contract_pin, status, notes,
request, response}` — `decoder` is the SDK name and version;
`contract_pin` the contract commit it implements; `status` is `full`,
`partial` (something was not decoded; `notes` says what and why) or
`none` (dialect `unknown`, or a call on a provider host that is not a
model call, such as `/v1/models` or a login refresh); `request` and
`response` are the canonical types, omit-empty when `status` is `none`.
An exchange with no decoded row is *pending*. Two decoders may each
write a row for the same `id`; readers pick by `contract_pin` or
`decoder`, never by "last wins". The join on `id` is a single DuckDB
`LEFT JOIN`, and the ledger (`exchanges`) answers every accounting
question without it.

**C3 — The event row.** `{v, id, seq, t_offset_ms, bytes}` and, for
WebSocket, `dir` (`in` | `out`). `seq` starts at 0; `t_offset_ms` is
measured from the exchange's `t`. The frame *content* is not repeated
here — the raw response blob holds the complete stream verbatim, and a
decoder maps frames to canonical `StreamEvent`s with these timings. This
is the whole "track all the streaming traffic" requirement: what arrived
when, at what rate, and for how long, at one row per frame.

**C4 — The scan row.** `{v, t, pid, exe, cmdline (omit-empty), host,
remote, match, coverage}` where `host` is the provider hostname when
known, `remote` is `ip:port`, `match` is `ip` (address matched one of the
provider hosts the gateway resolved itself; definitive for providers
on their own address ranges, *probable* on CDN-shared ranges — the row
carries `shared_range: true` in that case) or `dns` (the optional
privileged helper of boundary D8 saw this program or the system look up
`host` just before the connection; definitive), and `coverage`
is `covered` (the connection is to the gateway itself), `observed`,
or `observed_not_coverable`; a `recipe` string (omit-empty) names the
knowledge-base entry that would cover it. This vocabulary is the
contract-owned part of boundary D8.

**C5 — Redaction is not configurable off.** Before any byte reaches
disk or the live feed: header values for `authorization`,
`proxy-authorization`, `x-api-key`, `x-goog-api-key`, `cookie`,
`set-cookie`, and any header whose name contains `token`, `secret` or
`session`, are replaced with `[redacted:<byte length>]`; query
parameters `key`, `api_key`, `access_token` are removed from `path` and
from the raw request; the gateway's own credential-store substitutions
are never written. Body content is *not* redacted by default (it is the
conversation, which is the point) — a per-tag `retention: metadata`
setting keeps the exchange row and drops `raw` and `events` for
programs whose content one does not wish to keep. Additions to the
redaction list are additive changes; removals are breaking.

**C5b — Secrets inside bodies.** Header redaction does not touch
bodies, and bodies *will* contain secrets: a coding agent that reads a
`.env` file sends its contents to the model. So before a body reaches
disk or the live feed it is scanned for known credential shapes (the
patterns of `tools/check_secrecy.py` are the seed: provider key
prefixes, `AKIA…`, JWTs, PEM blocks, `Bearer <token>` inside text,
GitHub/Slack/Stripe token shapes). Two actions, chosen per tag:
`scrubbed` (default) — each match is replaced in the stored body and in
the raw blob with `[secret:<kind>:<sha256[:8]>]`, so the record is no
longer verbatim there but repeated occurrences of one secret are still
recognisable as the same; `marked` — the body is kept verbatim and the
row says a secret is present. Either way the exchange row carries
`secrets` (C2) so an auditor can find the rows. What is forwarded to
the provider is never altered by this rule; it acts on the copy. A body
scan is heuristic and will miss some secrets and flag some
non-secrets; the documentation says so, and the data directory is
never described as safe to share. The default is `scrubbed` because the
verbatim-evidence purpose of `raw` is served for everything *except*
credentials, and a credential is the one thing evidence must not
contain.

**C6 — Relationship to the canonical types.** `usage`, `adaptations`,
`error.code`, `request` and `response` are the contract's own types,
under the contract pin named in `decode.contract_pin`; nothing is
re-spelled. A capture row therefore validates against `spec/types.md`
for those fields. A change to a canonical type shows up as a new
`contract_pin` on new rows, never as a rewrite of old ones.

**C7 — The live feed.** `GET /_lm15/live` on the gateway emits, as SSE,
the same rows as they are written — exchange rows at start (with
`t_end` absent) and end, event rows as frames pass — after C5. The
`/_lm15/` prefix is reserved for the gateway's own API and can never
collide with a provider path. This feed is what a "what is being sent
right now" panel consumes.

**C8 — Fixtures.** `gateway/schema/capture-v1.json` (JSON Schema for
the three rows) and `gateway/captures/` holding redacted example days
from real programs (Pi, Claude Code, Codex at minimum) with the receipt
discipline of AUTHORITY.md: a capture promoted to a contract fixture
carries its `raw` hashes and the gateway version. `tools/audit.py` gains
a check that every fixture row validates and contains no value matching
the C5 patterns.

**C9 — Versioning.** `v` is bumped only for a change a `v = 1` reader
would misread. New omit-empty fields are additive under `v = 1` with a
`changes/` entry. Readers ignore fields they do not know.

## Trade-offs, stated

- Storing bodies verbatim means the data directory holds one's
  conversations and code. That is the value and the risk; mode 0700, C5,
  and per-tag retention are the answer, and the documentation says so
  plainly rather than implying the directory is safe.
- The decoded form lives in a separate stream and needs a join. The
  alternatives — rewriting the exchange line in place, or appending a
  second row with the same id — would respectively forfeit crash safety
  and force a "last row wins" step into every query.
- Scrubbing secrets in bodies (C5b) makes `raw` non-verbatim exactly
  where a credential appeared. A fixture promoted from such a capture
  says so in its receipt; the alternative — verbatim credentials on disk
  — is not acceptable for a product whose data directory holds months of
  conversations.
- `usage` extracted at capture time duplicates what the decoder would
  produce. Deliberate: the ledger must work with no decoder (boundary
  D5), and the two are compared by the audit to catch decoder drift.
- Raw frames are not copied into `events`; a reader wanting frame
  content must open the raw blob. Keeps `events` small enough to hold a
  year of streaming timings in a laptop's DuckDB.

## Defaults taken at ratification

Each may change with a `changes/` entry:

- `origin.pid`/`origin.exe` are recorded by default: cheap on Linux
  (`/proc/net/tcp` peer lookup), best effort elsewhere, omitted when
  unknown. It is the difference between "tag `pi`" and "this pi, this
  binary".
- Retention: keep everything until `lm15 gateway prune` is run, or a
  per-tag `retention` says otherwise. Silent deletion of a user's own
  record is worse than a growing directory; the size is shown in the
  coverage view.
- Non-model traffic on a provider host (login refresh, `/v1/models`,
  account calls) is **kept** as an exchange row with `dialect:
  unknown` and, when decoded, `status: none`. It is part of "what left
  my machine", which is the question the product answers; the ledger
  filters it out by dialect.
