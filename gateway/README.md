# gateway/ — the capture record

What the lm15 gateway writes to disk, defined here because it is an
interface other programs read: dashboards, DuckDB queries, aiconvo, the
decoders in every SDK, the routing rules. Ratified 2026-09-19 in
`changes/2026-09-19-capture-record.md` (the rules) and
`changes/2026-09-19-gateway-boundary.md` (the product). The gateway itself
lives in the `lm15-gateway` repository and names the contract commit it
writes in its `CONTRACT_PIN`.

```
gateway/
  schema/capture-v1.json     the four row shapes, JSON Schema 2020-12 — the artifact
  examples/<day>/            a synthetic day, derived from pinned provider bodies
  examples/build.py          regenerates it deterministically
  captures/<day>/            real days promoted from a running gateway (none yet)
```

`python3 tools/check_gateway.py` validates everything here (CI runs it).
`python3 -m unittest tools.test_check_gateway` proves the checker catches
each way a row or blob can be wrong.

## The day directory

A day is one directory, four streams, one raw store:

```
2026-09-19/
  exchanges/2026-09-19.jsonl   one row per request       — the ledger
  events/2026-09-19.jsonl      one row per wire frame    — streaming timing
  scan/2026-09-19.jsonl        one row per observed program→provider connection
  decoded/2026-09-19.jsonl     one row per decoder pass  — canonical Request/Response, joined on id
  raw/<sha256[:2]>/<sha256>.http     stored request or response message
  raw/<sha256[:2]>/<sha256>.jsonl    websocket frame log
  _provenance.json  (examples)  |  _receipt.json  (captures)
```

Every row carries `v: 1`. Field meanings are in the schema's
`description`s; the rules are in the changes entry. Three that decide
most questions:

- **The ledger needs no join.** `exchanges` answers who / which model /
  how many tokens / how long / how routed on its own. `decoded` is a
  `LEFT JOIN` on `id` for anyone who wants the canonical form.
- **Nothing is rewritten.** Streams are append-only; an exchange row is
  written once, when the exchange ends or aborts. A decoder adds a row to
  `decoded`, never edits `exchanges`.
- **Bodies are verbatim.** Transport credentials (`authorization`,
  `x-api-key`, …) are replaced with `[redacted:<byte length>]` before
  anything touches disk; the body is stored exactly as sent, and a body
  that looks like it carries a credential is *marked* in
  `exchanges.secrets` so it can be found (C5, C5b).

## Raw blobs

A blob is content-addressed: its file name is the SHA-256 of its bytes, so
the same response body stored twice is one file (the example day shows
this: two exchanges share one response blob).

`.http` — an HTTP/1.1 message, exactly the shape any HTTP library parses:

```
POST /v1/messages HTTP/1.1\r\n
host: api.anthropic.com\r\n
x-api-key: [redacted:108]\r\n
content-length: 173\r\n
\r\n
{"model":"claude-sonnet-4-5", ...}
```

- Request: the request line is the path as sent upstream (after routing),
  never a full URL, never a secret query parameter.
- Response: the status line, then headers, then the body. For an SSE
  reply the body is the complete stream text.
- Headers are as received, lower-cased names, except: redacted values
  (above), and framing. The body is stored as the **decoded entity** — the
  JSON or SSE text, not gzip bytes — so `content-encoding` and
  `transfer-encoding` are omitted from the stored headers,
  `content-length` equals the stored body length, and the wire's original
  encoding is recorded in the row (`raw.<which>.content_encoding`). This
  is the one place the stored message is not byte-for-byte the wire; the
  reason is that a compressed blob is unreadable and un-greppable, and the
  encoding is recoverable from the row. `wire_sha256` (below) still
  covers the true wire bytes.

`.jsonl` (websocket only) — one frame per line:
`{"seq":0,"dir":"out","t_offset_ms":12,"opcode":"text","data":"..."}`;
binary frames carry `"opcode":"binary","data_b64":"..."`. The handshake
request and response are ordinary `.http` blobs.

## Examples vs captures

`examples/` is **synthetic**: no gateway ran. Response bodies are pinned
bodies from `bodies/`; canonical forms are the reviewed goldens for the
same cases; timings, pids, ids and headers are invented and
`_provenance.json` says so per row. `build.py` regenerates the day
byte-for-byte. Synthetic rows carry no `wire_sha256` and can never move
to `captures/`.

`captures/` is **real**: a day recorded by a running gateway on a named
machine, redacted by the gateway (never by hand), with every blob carrying
`wire_sha256` — the hash of the unredacted transport message, which the
gateway computes and discards — and a `_receipt.json` naming the gateway
version, the host, the date and the reviewer. That is the AUTHORITY.md
receipt discipline applied to captures; the checker enforces it. A capture
becomes contract evidence for a wire fact only through the ordinary route
(a case under `cases/` citing it), never by sitting here.

## Reading a day with DuckDB

```sql
-- spend and latency by tag, no join
SELECT tag, count(*) AS calls,
       sum(usage.input_tokens) AS input_tokens,
       sum(usage.output_tokens) AS output_tokens,
       quantile_cont(upstream.latency_ms, 0.5) AS p50_ms
FROM read_json_auto('gateway/examples/*/exchanges/*.jsonl')
GROUP BY tag ORDER BY calls DESC;

-- what was rerouted
SELECT id, tag, model.asked, model.sent, route.rule
FROM read_json_auto('gateway/examples/*/exchanges/*.jsonl')
WHERE model.asked <> model.sent;

-- time to first content token per streamed exchange
SELECT e.id, min(ev.t_offset_ms) AS first_content_ms
FROM read_json_auto('gateway/examples/*/exchanges/*.jsonl') e
JOIN read_json_auto('gateway/examples/*/events/*.jsonl') ev USING (id)
WHERE ev.event = 'content_block_delta'
GROUP BY e.id;

-- the canonical form, when a decoder has run
SELECT e.id, e.tag, d.status, d.response.finish_reason
FROM read_json_auto('gateway/examples/*/exchanges/*.jsonl') e
LEFT JOIN read_json_auto('gateway/examples/*/decoded/*.jsonl') d USING (id);
```

## Changing the record

- A new **omit-empty** field is additive under `v: 1`: a `changes/` entry,
  the schema, the example day (`build.py`), and `check_gateway.py` if the
  field has an invariant. Readers ignore fields they do not know.
- A change a `v: 1` reader would **misread** bumps `v` and adds
  `capture-v2.json` beside this one; old days are never rewritten.
- The redaction list and the C5 header rule only grow. Removing a name is
  a breaking change.
- The checker refuses schema keywords it does not implement: to use a
  new keyword, teach the checker first, and re-run the `jsonschema`
  cross-check (`tools/test_check_gateway.py`, under
  `nix-shell -p 'python3.withPackages (p: [p.jsonschema])'`).
