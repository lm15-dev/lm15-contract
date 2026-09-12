# 2026-09-11 — Job handles and live turns are family surface; profiles are not; the loopback listener is on demand

Ratification: PENDING — drafted 2026-09-11 in session after the parity
ledger (`playbooks/parity.md`) surfaced four pieces of Python-only
ergonomics with no recorded decision, and the maintainer chose, in
session: "port job handles; specify and port live turns; simplify
profiles first; keep callback listeners optional — not never" ("Good
nice go implemented excellently and fully"). This entry writes the four
decisions down and the two rules the ports needed before they could
mirror the reference faithfully. Python, Rust and TypeScript implement
it in the commits that cite this file.

The principle behind all four: **share the conveniences that prevent
mistakes; do not standardize the ones that obscure what the library
does.** A convenience earns a family row when a user without it would
re-derive a rule and get it wrong.

## 1. Job handles (`BatchJob`, `VideoJob`) — family surface

A batch and a video are tickets on every wire that sells them: submit,
poll, wait, fetch. Two things users get wrong without a handle — what
counts as terminal, and the forgot-to-reassign-a-stale-status bug — are
exactly what the handle owns. `ResponseStream` is the same idea for
streams and is already a family row; these are its siblings.

Rule, all languages (`playbooks/api-family.md` § Beyond chat):

- The four pure operations stay public and are the wire truth
  (`batch_submit` / `batch_status` / `batch_results` / `batch_cancel` /
  `batch_list`; `video_submit` / `video_status` / `video_result` /
  `video_list`). The handle is sugar over them, never a second reader.
- `batch(request)` / `video_generate(request)` submit and return a
  handle; `batch_job(id)` / `video_job(id)` re-attach by id alone (the
  primary pattern for real workloads: store the id); `batches()` /
  `video_jobs()` list as handles where the wire lists.
- The handle holds one frozen snapshot (`info`) and exposes `id`,
  `status`, `done` (video: `progress`). `refresh()` and `wait()` replace
  the snapshot in place and return the handle.
- **`wait` is explicit and bounded.** `wait(poll_every, timeout)` polls
  until `done`. Reading a property never waits and never contacts the
  provider. A `failed` job **returns** from `wait` (the status says so;
  the batch precedent's entry-level honesty); it does not raise.
- **A deadline that elapses is loud, at `wait`.** It is the caller's own
  deadline, not a provider or lm15 failure, so it carries no ErrorCode:
  each language raises its *own* timeout type — Python the builtin
  `TimeoutError` (the `asyncio.wait_for` convention), TypeScript a
  `DOMException` named `TimeoutError` (the `AbortSignal.timeout`
  convention), Rust a `WaitError::Elapsed` beside `WaitError::Lm15`.
  Returning silently before `done` was rejected: `wait(...).result()`
  would then fail one step later with a message about the wrong thing.
- Default poll cadence is the reference's: batch 30 s, video 5 s.

## 2. Live `turn()` — a rule first, then family surface

A live session is full-duplex and open indefinitely; "give me one turn"
is what every scripted recipe and turn-based voice app needs, and
without it each application invents its own stop condition — and gets
the bill wrong. Two of the turn's behaviours are rules, not
convenience, so they are written here before any port copies them:

**LIVE-1 — Turn boundary.** A turn's event iterator yields server
events until it has yielded one of `turn_end`, `interrupted`, `error`,
then ends itself (the `stream()` self-ending idiom). A `tool_call`
event is yielded mid-turn and does **not** end iteration: the caller
holds the session and can answer with `send_tool_result` and keep
iterating. `result()` (the materialized turn) **returns at a
`tool_call`** instead: it cannot answer for the caller, and waiting past
it would deadlock against a model that is waiting for the result.
`Turn.ended_by` is therefore one of `turn_end` / `interrupted` / `error`
/ `tool_call`; `ok` is `ended_by == turn_end`.

**LIVE-2 — A turn's bill.** `Turn.usage` is the field-wise sum of every
`usage` and `turn_end` event the turn saw; a counter absent on either
side is unknown in the sum, never zero (INV-029). A tool-call response's
tokens arrive as a `usage` event after the `tool_call` that ended the
previous `result()`, i.e. at the start of the continuation turn: the
semantic turn stayed open, so that is where they belong. A cancelled
response's tokens precede its `interrupted` and stay on the interrupted
turn. (Already stated for the reference in
`changes/2026-09-02-live-usage-event.md`; promoted here to a rule every
port follows.)

**Materialization** concatenates `text` events, concatenates decoded
`audio` bytes (media type from the first audio event that names one),
collects `tool_call` events as `ToolCallInfo`, keeps the last `error`,
and keeps the raw `events`. It buffers the whole turn in memory: for
latency-sensitive playback, iterate the events instead — that path is
unchanged and primary.

The transcript harness pins the event stream, not the turn; LIVE-1 and
LIVE-2 are pinned by each implementation's tests over a scripted socket.

## 3. `ProviderProfile` / `EndpointProfile` — not family surface; Python simplifies

What profiles express that nothing else does was checked and is small:

- a base URL and a compat for an endpoint — `compat=` + `base_url=` on
  the adapter say the same, shorter, and after the 2026-09-11 address
  rule a preset name supplies its own URL;
- a per-model compat on the Responses dialect — the chat dialect has
  `model_overrides` on its compat; the Responses dialect keeps the
  request-level escape hatch (`Config.extensions["openai_responses_compat"]`),
  which is per request and therefore per model;
- a default compat chosen by **sniffing the base URL** for
  `openrouter.ai` / `api.meta.ai` — a guess about the server, the kind
  the family refuses elsewhere; `compat="openrouter"` is the explicit
  spelling.

So the layering (bound < endpoint < model < request) is a second
configuration-resolution system beside the router's, and two systems is
how a user ends up not knowing which one picked the URL.

Decision: **NEVER for the ports**; the reference deprecates
`lm15.profiles.ProviderProfile` / `EndpointProfile`, `OpenAILM.from_profile`,
the `profile=` field, and the URL-sniffed default (a `DeprecationWarning`
naming `compat=`), in the next release candidate, and removes them in
1.0.0. They are not in `spec/SCOPE.md`'s frozen list. What survives, in
`lm15.compat` where it belongs: the partial-compat semantics (`None` =
inherit, `"auto"` = adapter default), `merge_*_compat`, and the
request-level extension hatch.

## 4. Loopback OAuth callback listener — on demand, not never

`OAuthCallbackListener` is a one-shot local HTTP server for an
authorization-code redirect: infrastructure for desktop/CLI login flows,
with a listener's attack surface. No flow lm15 owns uses it (xAI is
device-code; a browser page *is* the redirect target). Rust's stance is
adopted family-wide: a port ships one **when a flow it owns needs one**,
and PKCE (`generate_pkce`) is the primitive every port already has.
Neither mandatory parity nor "never". Python's stays.

## Considered and rejected

- Port everything ("parity"): standardizes the profile layering, the one
  piece that obscures rather than prevents.
- Port nothing ("sugar is Python's"): leaves the bill rule (LIVE-2) as
  one language's habit; a Rust or TS user materializing a turn by hand
  would drop the tool-call response's tokens.
- `wait` returning at the deadline without raising: see § 1.
- A family ErrorCode for the wait deadline: a code names a failure the
  caller can act on; the caller set the deadline. The language's own
  timeout type is the honest class.

## Trade-offs, stated

- Handles add mutable state and polling loops to maintain in three
  languages; the pure verbs remain the truth and the harness pins only
  them.
- Materializing a turn buffers audio; the event path stays primary.
- Deprecating profiles costs any rc1 user of `from_profile` a two-line
  change; the URL-sniffing removal changes behaviour for
  `OpenAILM(base_url="https://openrouter.ai/…")` without `compat=` —
  warned now, refused in 1.0.
- The wait deadline is a different type in each language. Deliberate:
  it is not an lm15 failure.
