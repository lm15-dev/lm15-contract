# Parity ledger — what each implementation has, lacks, or will never have

Status: LEDGER (kept current by whoever moves a pin; not itself normative).

## 2026-10-02 — router tables pinned; provider tables generated

changes/2026-10-02-router-tables-pinned.md: 46 router cases (every built-in
rule and its byte-short boundary; every litellm prefix through the new
`resolve_openai_chat_model` op); `tables/providers.json` published, and
TypeScript, Rust and Go now generate their provider tables from it
(`tools/gen_tables.py --check` in each CI). Every SDK's main moves its pin to
`dd3d3be`, measured with `harness/check.py --direction all`, network cut:

| | Python | TypeScript | Rust | Go | Julia | R |
|---|---|---|---|---|---|---|
| Contract checks (all directions) | 1,884 / 1,884 | 1,884 / 1,884 | 1,884 / 1,884 | 1,884 / 1,884 | 1,884 / 1,884 | 1,884 / 1,884 (`tools/check-contract.py`) |
| Commit | `c84bd74` | `562fdbf` | `4a15bd0` | `c2af04c` | `ce7a1f0` | `5740f90` |
| Code change the cases asked for | none | none | rule `jev-` | none | litellm door: bare prefix kept, declared spellings read | none |

R's `PYTHON_REFERENCE` moves to lm15-python `c84bd74`; its parity probes: 30
pass, the 2 known differences unchanged; `R CMD check --as-cran`: 1 NOTE (new
submission; two README links answered 503 during the check). R gains
`provider_definition()` / `new_router(providers =)`. The website (`3545920`)
reads its provider list from the pinned SDK registry and offers xai,
deepinfra, together, fireworks and parasail. No release yet.

Not moved: Java, Ruby, .NET and Swift (still at `cfed007`).

## 2026-09-30 — the Claude Code release as a setting; Claude's default max_tokens

changes/2026-09-30-claude-code-client-version.md (AUTH-10 `backend_settings`:
`client_version` on `claude-code` and `openai-codex`, default Claude Code
2.1.285, `LM15_CLAUDE_CODE_VERSION` / `LM15_CODEX_CLIENT_VERSION`, the
minimum-version guidance, an unread settings entry refused; MAP-7 rule 6: an
unset `max_tokens` on a Claude model is its output ceiling; the harness
compares `compare_headers`). Nine new checks: two live claude-code cases,
three hand-authored `defaulted` cases (one amended), one error case pinning
its message, two auth cases. Every SDK moves its pin to `bd9586d`, measured
with `harness/check.py --direction all`, network cut:

| | Python | TypeScript | Rust | Go | Julia | R |
|---|---|---|---|---|---|---|
| Contract checks (all directions) | 1,838 / 1,838 | 1,838 / 1,838 | 1,838 / 1,838 | 1,838 / 1,838 | 1,838 / 1,838 | 1,838 / 1,838 (`tools/check-contract.py`) |
| Commit | `f1b20a7` | `c62e326` | `7282332` | `e094ce9` | `c93467c` | `2e32cd4` |

The claude-code cases now compare `user-agent`: before this pin no port
could fail on a stale Claude Code release. R's `PYTHON_REFERENCE` moves to
lm15-python `f1b20a7`; its parity probes: 30 pass, the 2 known differences
unchanged. Julia's `conformance/auth/resolution.json` and Python's
`conformance/auth_resolution.json` are re-copied from `auth/resolution.json`.

**Released 2026-09-30**, every SDK at `57e33d1` (the ratification commit;
text only, the same 1,838 of 1,838): Python 1.2.0 (PyPI), TypeScript
1.0.0-rc.4 (npm), Rust 1.0.0-rc.4 (crates.io), Go v1.1.0-rc.3, R 1.0.1
(GitHub release). Julia's pending 1.0.0 registration (General#169598, still
waiting for a maintainer to approve the name) was moved to LM15.jl `85eaaac`,
so the first Julia release carries this change. Each release was installed
fresh from its registry and called `claude-code:claude-opus-5-5` with no
settings: HTTP 200, `stop`, `max_tokens` defaulted to 128000.

Not moved: Java, Ruby, .NET and Swift, the early ports still pinned to
`cfed007` (2026-09-11). Each takes only the new default release, 2.1.285
(lm15-java `6479467`, lm15-dotnet `5a4c813`, lm15-ruby `0f223a0`, lm15-swift
`a1f53be`; a one-value change, their test suites not run here), so their
claude-code door is not refused; the setting, the guidance and the ceiling
default wait for their catch-up.

## 2026-09-29 (later) — input_audio formats in every SDK

changes/2026-09-29-input-audio-formats.md (MAP-12 rule 4: `input_audio`
reads `ogg`, `opus`, `flac`, `aac`, `aiff`, `webm` and `mpeg` as their true
media types; case `openai_chat.ingest_input_audio_ogg`). Every SDK's main
moves its pin to `307925a` (`8ee6322` merges it with an identical tree),
measured with `harness/check.py --direction all`, network cut:

| | Python | TypeScript | Rust | Go | Julia | R |
|---|---|---|---|---|---|---|
| Contract checks (all directions) | 1,829 / 1,829 | 1,829 / 1,829 | 1,829 / 1,829 | 1,829 / 1,829 | 1,829 / 1,829 | 1,829 / 1,829 (`tools/check-contract.py`) |
| Change | lm15-python#16 | lm15-ts#1 | lm15-rs#1 | lm15-go#1 | LM15.jl#1 | lm15-r#1 |

Rust and Julia also move past the member-order commit (INV-002), which they
passed unchanged. R's
`PYTHON_REFERENCE` moves to lm15-python `2a85094`, the reference at this pin;
its parity probes: 30 pass, the 2 known differences unchanged. No release
yet: the README's table still lists each SDK's released pin.

Left open, as the change record says: `m4a` / `mp4`, until a receipt shows
which spelling Gemini accepts.

## 2026-09-29 — member order JavaScript would change (INV-002)

changes/2026-09-29-index-member-names.md: 40 new checks (33 in the
`mapping` direction, `mapping/opaque-order.json`; 7 in `serde`), measured
with `harness/check.py --direction all` on this commit:

| | Python | TypeScript | Rust | Go | Julia |
|---|---|---|---|---|---|
| Contract checks (all directions) | 1,828 / 1,828 | 1,828 / 1,828 (1,788 before its fix) | 1,828 / 1,828 | 1,828 / 1,828 | 1,828 / 1,828 |
| Code change needed | none | `src/json.ts` member order record | none | none | none |

Only lm15-ts moves its pin here, with its fix (released as 1.0.0-rc.3 on
2026-09-29, pinned at `442295a`, this change plus its ratification).
Python, Rust, Go and Julia pass this commit unchanged; their pins move at
their next release.

## 2026-09-26 (evening) — Julia at parity

lm15-jl brought from pin `cfed007` (2026-09-11) to this commit and measured
with `harness/check.py --shim julia --direction all`:

| | Python | TypeScript | Rust | Go | Julia |
|---|---|---|---|---|---|
| Contract checks (all directions) | 1,788 / 1,788 | 1,788 / 1,788 | 1,788 / 1,788 | 1,788 / 1,788 | 1,788 / 1,788 |
| `managed` direction (43 sign-in runs) | 43 | 43 | 43 | 43 | 43 |
| Mixed-language store runs and concurrent renewal (`tools/managed_crossrun.py python julia typescript rust go`) | pass | pass | pass | pass | pass (40 of 40) |
| Live smoke with real keys | — | 8/8 hosts | 8/8 hosts | 16/16 | 63 ok of 69 checks on 14 key bindings and 4 saved sign-ins (`lm15-jl receipts/2026-09-26-live-smoke`); the rest: 1 adapted and 1 provider refusal as receipted, Grok declining to repeat a phrase, an OpenRouter minted key at its $1 limit |

What Julia gained, each already ratified: the four open-model hosts and
`reasoning_off`; MAP-15 forms and the router tables as copied data;
refusals naming their field (message media, cache resources); MAP-16;
judgments (DataPart, `Config.probabilities`, TypeSafe, candidate-sequence
scoring on vLLM); the Google Cloud pass (keys on `vertex`, the project from
Google's places, settings origins); named cloud credentials, provenance and
endpoint roots (2026-09-19); R3 blocking the ambient xAI key; managed
sign-in (AUTH-12–26, `connect` in `LM15.Interactive`); reply faults
INV-053/054/055; error diagnostics; the connection budget; bounded live-turn
collection. Julia's stated deviations are in its README (functions rather
than methods, ordered choices as pairs, HTTP.jl's missing pool-wait timeout).

Found live, not a Julia defect and not changed here: OpenRouter answers a
minted key that reached its spending limit with HTTP 403 ("Key limit
exceeded"), which the status mapping makes `AuthError` in every SDK; a
`BillingError` would describe it better, and would need a receipt and a
`changes/` entry.

## 2026-09-26 (later) — four open-model hosts in every SDK

Every SDK pinned to `fe5cdf9` (changes/2026-09-26-inference-hosts-live.md,
ratified the same day), measured with `harness/check.py --direction all`:

| | Python | TypeScript | Rust | Go |
|---|---|---|---|---|
| Contract checks (all directions) | 1,788 / 1,788 | 1,788 / 1,788 | 1,788 / 1,788 | 1,788 / 1,788 |
| `deepinfra`, `together`, `fireworks`, `parasail` (registry, presets, litellm prefixes, sign-in labels) | ✓ | ✓ | ✓ | ✓ |
| compat `reasoning_off` ("send" / "lowest", per model) | ✓ | ✓ | ✓ | ✓ |
| Chat `list_models`: bare array read, unknown shape → ProviderError | ✓ | ✓ | ✓ | ✓ |
| Chat usage: flat `cached_tokens` fallback | ✓ | ✓ | ✓ | ✓ |
| Live against the four hosts with real keys | capture scripts (43 cases) | live smoke 8/8 | live smoke 8/8 | live smoke 16/16 checks (`receipts/2026-09-26-inference-hosts-live-smoke`) |

The count grows by 205 over `3763eec`: the four hosts' cases, pins, error
envelopes and auth cases, and the Google Cloud cases of `4c9b6cc` (vertex,
vertex-express), which every SDK already passed. Rust has no console URLs in
its registry, as before. The TypeScript and Rust corpus tests carried
constants that moved with the pin (case counts); the TypeScript request test
now rewrites the `query-key` parameter as the harness does.

## 2026-09-26 — MAP-16 (Gemini schema fields) in every SDK

| | Python | TypeScript | Rust | Go |
|---|---|---|---|---|
| Contract checks (all directions) | 1,583 / 1,583 | 1,583 / 1,583 | 1,583 / 1,583 | 1,583 / 1,583 |

The count grows by 91: the new `mapping` direction (87 checks, 29 vectors ×
tools, response format, cached prefix) and the two live Gemini cases in
the request and response directions. Before the SDKs moved, Go failed 26
mapping checks; the reference was changed first. Each SDK also tests the
vectors on the Live setup frame, which the harness cannot build.
lm15-go's live smoke sent one strict tool schema (`additionalProperties:
false`) to OpenAI, Anthropic and Gemini and got a tool call from each
(lm15-go `receipts/2026-09-26-live-smoke-map16`).

## 2026-09-25 (later) — Go at parity; opaque key order is now checked

Measured with `harness/check.py --direction all` at this commit, every SDK
pinned to it:

| | Python | TypeScript | Rust | Go |
|---|---|---|---|---|
| Contract cases (all directions) | 1,492 / 1,492 | 1,492 / 1,492 | 1,492 / 1,492 | 1,492 / 1,492 |

Go's one stated deviation is gone: `JSONObject` is an ordered type through
Go's decoder and builders, so the 23 byte-pinned cases pass and a schema's
property order reaches the provider. The harness now checks key order
inside opaque payloads in the request and serde directions
(changes/2026-09-25-opaque-key-order.md); the earlier Go fails 179 request
and 8 serde cases under it, and all four current SDKs pass. Beyond the
check, Go's wire bodies and canonical JSON now match the reference's key
order everywhere the harness exercises, except two Go-map-typed fields
(`probabilities`, `rate_limit_headers`) and header order, which net/http
writes sorted.

## 2026-09-25 — managed sign-in in every SDK; where each SDK stands

Measured, not claimed: `harness/check.py --direction all` at each SDK's pin
and `tools/managed_crossrun.py python typescript rust go`.

| | Python | TypeScript | Rust | Go |
|---|---|---|---|---|
| Contract cases (all directions) | 1,492 / 1,492 | 1,492 / 1,492 | 1,492 / 1,492 | 1,469 / 1,492 |
| `managed` direction (43 sign-in runs) | 43 | 43 | 43 | 43 |
| Mixed-language runs on one store, concurrent renewal race | pass | pass | pass | pass |
| `Auth`, recipes, seven account flows, bound client, `connect()`, terminal UI | ✓ | ✓ | ✓ | ✓ |
| Managed router mode (AUTH-15 B), managed doctor, `kimi-code` / `github-copilot` routed | ✓ | ✓ | ✓ | ✓ |
| Loopback return listener | ✓ | Node | native | native (not `GOOS=js`) |
| Sign-in in a web page | — | ✓ (browser track, relays) | — (wasm build is the codec only) | — |
| Synchronous mirror | native sync + `AsyncAuth` | n/a (async) | `lm15::blocking::{Auth, connect}` | native (blocking + `context`) |
| `AuthOperationError`, ErrorCode `auth_operation` | ✓ | ✓ | added 2026-09-25 | added 2026-09-25 |

Go's 23 failures are one stated deviation: JSON object keys are written
sorted, so the 20 SigV4-signed Bedrock bodies, 2 batch JSONL uploads and 1
image-edit multipart differ in bytes (not in meaning). The same sorting loses
a user's JSON-schema property order, which decides the order a model fills
structured output in: a behavioral gap, not only a test artifact. The fix is
an ordered JSON object type through Go's decoder and builders.

Live evidence did not change: managed-path receipts exist for Python only
(xAI supported; Claude, ChatGPT, Copilot, OpenRouter observed but unverified
for permission and billing). The TypeScript, Rust and Go sign-ins run the
same requests, proven offline by the shared runs; none has its own live
receipt yet.

## 2026-09-20 — implementation pass, execution deliberately deferred

The maintainer requested Python, TypeScript/browser and Rust source catch-up,
with baseline/final commits and **no tests or builds in this pass**. The rows
below describe implemented source, NOT passing conformance, runtime verification,
or published packages. A CONTRACT_PIN names the target rules, not proof that an
implementation satisfies them. The September 11 results farther below are
historical evidence for different revisions.

| Area | Python | TypeScript / browser | Rust |
|---|---|---|---|
| MAP-13 records, policies, planning, promoted controls | implemented | implemented | implemented |
| Stops preserving scores and reporting incomplete coverage | implemented | implemented | implemented |
| MAP-14 data, judgment helpers, TypeSafe and candidate scoring | implemented; malformed-reply repairs | implemented; malformed-reply repairs | implemented |
| Streamed judgment answers materialize as DataPart | repaired | repaired | implemented |
| Named cloud identity, provenance, endpoint roots, JWT bearer | implemented | implemented | implemented |
| Caller-owned budgets and bounded transport concurrency | implemented | native Node implementation; explicit Fetch limitations | implemented over reqwest; backend limits stated |
| Malformed replies, compression and retained diagnostics | implemented; auxiliary faults repaired | implemented; Node codec / Fetch decoded bodies | implemented; native and host codec |
| Router-local declarations and credential-free planning | implemented | implemented | implemented |
| Bounded live collection, retained events and recovery | implemented | implemented; DEL byte charge repaired | implemented |
| Batch/video handles, cached-prefix convenience | implemented | implemented | implemented |
| Generic credential store and shared lock identity | implemented; identity repaired | implemented; optional native lock source | implemented; identity repaired |
| Blocking mirror | sync/async implementations | async language API | expanded beyond chat/model listing |
| Testing helpers and API inspection | existing helpers | existing helpers | scripted helpers and surface description added |

Source guides: `lm15-python/CHANGELOG.md`, `lm15-ts/docs/transport.md`,
`lm15-ts/docs/cloud-identity.md`, `lm15-rs/docs/catchup.md`, and each SDK's
`docs/credential-lock-identity.md`. New regression files are written, not run.
Provider fixtures and previous goldens were not rewritten to match SDK output.
`changes/2026-09-20-source-parity-repairs.md` records the additional consumer
vectors and corrections to the preliminary study.

### Boundaries that must not be mistaken for completed verification

- Browser credentials/files/cloud chains remain explicit host boundaries.
  Fetch owns decompression and socket controls; CORS can hide diagnostic or
  Content-Encoding headers. Unknown does not mean unlimited quota or identity
  coding. Browser code does not silently gain filesystem access.
- TypeScript's macOS/Windows credential-lock backend is native **source**, not
  a built or platform-verified binary. Linux's util-linux backend remains usable.
  A matching native artifact is required where that backend is selected.
- Shared credential identity has a coordinated-upgrade requirement: do not mix
  old/new Windows writers or writers using previously unresolved POSIX aliases.
  Unsupported ambiguous paths fail closed. This does not coordinate foreign
  CLIs or unify every filesystem alias.
- Transport libraries impose stated limitations. Rust's write watchdog observes
  upload-body consumption, not every socket write; Node's new native transport
  is HTTP/1.1 and does not automatically discover proxies or follow redirects.
  Configure an appropriate transport rather than assuming those capabilities.
- Platform-specific APIs, release artifacts, generated metadata, compiler/type
  compatibility, locks, cancellation and concurrency all still need the next
  authorized verification pass. No release approval is implied here.
- Existing explicit cloud-chain gaps remain shared limitations, not silently
  successful fallback: AWS login DPoP refresh, special Azure managed-identity
  environments, and unsupported GCP credential-source variants.
- Python-only introspection/catalog discovery and deprecated profile layers
  remain intentional non-goals for ports. The gateway is a separate product.

## Historical ledger — September 11 (not the current implementation status)

Started 2026-09-11 from a file-by-file comparison of `lm15-python` 8bafafa,
`lm15-ts` 17a521e (+ uncommitted browser work), `lm15-rs` c81ad74, all at
contract pin 42d8040; updated the same day after the four OPEN rows were
decided (`changes/2026-09-11-job-handles-live-turns-profiles.md`). The harness proves the rows marked *corpus*; the
rest were read from the code and the ports' READMEs ("Stated deviations",
"Not implemented, stated") and are only as true as those.

Three verdicts, one per row:

- **SAME** — present, same names, same behaviour; proven by the corpus
  where a direction covers it.
- **BEHIND** — present in Python, absent or narrower in the port, and
  meant to be closed. Says what is missing.
- **NEVER** — deliberately not in that language, with the reason and the
  place the decision is recorded. A NEVER row is a decision, not a gap.
- **OPEN** — Python has it; nobody has decided whether the ports should.

## Providers and presets

| Row | Python | TS / Node | TS / browser | Rust | Verdict |
|---|---|---|---|---|---|
| The 31 registry providers (`openai` … `sglang`) | 31 | 31 | 31 | 31 | SAME (corpus: `router`, `auth`, `models`) |
| Chat presets (15: `openai`, `ollama`, `lmstudio`, `groq`, `openrouter`, `xai`, `vllm`, `sglang`, `deepseek`, `qwen`, `bedrock`, `bedrock_mantle`, `zai`, `meta`, `moonshotai`) | 15 | 15 | 15 | 15 | SAME (corpus: `request`; TS knob-for-knob diff 0 on 2026-09-11; Rust differential 194/0) |
| Responses presets (11) and Messages presets (4) | ✓ | ✓ | ✓ | ✓ | SAME |
| Spelling aliases (`lm-studio`, `z.ai`, `dashscope_qwen`, `responses`, …) | ✓ | ✓ | ✓ | ✓ | SAME |
| Preset → address tables; refuse a named server with no address | ✓ | ✓ | ✓ | ✓ | SAME (api-family 2026-09-11, pending ratification) |
| Naming a preset on a direct adapter | `compat="groq"` | `{ compat: "groq" }` | same | `LmBuilder::preset("groq")` (2026-09-11) | SAME |
| `ProviderProfile` / `EndpointProfile` layering (`lm15/profiles.py`) | deprecated (rc2; removed 1.0.0) | ✗ | ✗ | ✗ | NEVER — a second configuration-resolution system beside the adapter's and the router's; the same facts are `compat=` + `base_url=` and the request hatch (`changes/2026-09-11-job-handles-live-turns-profiles.md` § 3) |

## Chat core and streaming

| Row | Python | TS / Node | TS / browser | Rust | Verdict |
|---|---|---|---|---|---|
| Canonical types, serde, errors, four dialects, coalescer (MAP-3/4), assembler (MAP-9) | ✓ | ✓ | ✓ | ✓ | SAME (corpus: `request`, `response`, `stream`, `error`, `serde`) |
| `ResponseStream`, strict completion, post-completion warning channel | ✓ `StreamCleanupWarning` | ✓ `process.emitWarning` | ✓ `console.warn` fallback | ✓ `log::warn!` | SAME (ratified 2026-09-11) |
| Error metadata from headers (request id, retry hints) | ✓ | ✓ | ✓ | ✓ | SAME |
| `request_from_openai_chat`, `response_from_openai_chat` (MAP-12) | ✓ | ✓ | ✓ | ✓ | SAME (corpus: `ingest`, `response`) |
| `complete_from_openai_chat` / `stream_from_openai_chat`, litellm prefixes, client-keyword refusals | ✓ (+ `stream=True`) | ✓ (+ `stream: true`) | ✓ | ✓ (two functions; no flag) | SAME — the `stream` flag is a Python amendment; TS mirrors it, Rust states two functions (README) |
| Router: prefix / catalog / rule rungs, `explain`, shared explicit keys, `base_urls`, provider-key check | ✓ | ✓ | ✓ | ✓ | SAME |
| Router rung 0 (a `provider` attribute on a `str` subclass) and catalog discovery from installed packages | ✓ | ✗ | ✗ | ✗ | NEVER — Python idiom (`str` subclass, entry points); the ports take a data catalog (`RouterConfig.catalog`, `{ registry }`). Recorded in both READMEs. |
| Tool derivation from a function signature (`tool(fn)`, `@tool`) | ✗ | ✗ | ✗ | ✗ | NEVER, in any language — removed from Python and Julia before 1.0 ([changes/2026-09-23-no-tool-derivation.md](../changes/2026-09-23-no-tool-derivation.md)). A tool is a written-out `FunctionTool`. |

## Auth

| Row | Python | TS / Node | TS / browser | Rust | Verdict |
|---|---|---|---|---|---|
| AUTH-1 chain: explicit key / callable, env keys, placeholder, stored login, cloud chain | ✓ | ✓ | explicit only (no env, no files) | ✓ | SAME on Node/Rust; browser NEVER by design (`lm15-ts/docs/browser.md`: refused by name, never guessed) |
| AUTH-7 doctor (`explain_auth`) | ✓ (+ accepts a `Resolution`) | ✓ | ✓ (reports rungs absent) | ✓ | SAME (corpus: `auth` 43/43) |
| Stored logins: Claude Code, Codex (AUTH-8), refresh under the lock (AUTH-3/4) | ✓ | ✓ | ✗ (no filesystem) | ✓ | SAME on Node/Rust; browser NEVER |
| AUTH-4 lock: platforms | POSIX `fcntl` + Windows `msvcrt` | **Linux only**, needs util-linux `flock` on PATH; elsewhere fails closed | n/a | std `File::try_lock` (cross-platform) | BEHIND (TS): macOS/Windows cannot refresh a stored login; explicit keys still work. Recorded as a stated deviation. Fix: a native lock (N-API or `fs.open` + `flock` via a small addon) or accept and document. |
| xAI device-code login (AUTH-9), PKCE S256, RFC 8628 polling | ✓ | ✓ (`login`, `loginXai`, `generatePkce`) | PKCE only | ✓ | SAME |
| `OAuthCallbackListener` (loopback redirect listener) | ✓ (`authkit`) | ✗ | ✗ (a page *is* the redirect target) | ✗ | ON DEMAND — a port ships one when a login flow it owns needs one; PKCE is the primitive every port has (§ 4). Not a gap. |
| `CredentialFileStore` (lm15-owned multi-provider store, `mutate`) | ✓ | ✓ | ✗ | partial (xAI entry only, inside `login.rs`) | BEHIND (Rust): no general store API; only the one lm15-owned login writes. Small. |
| Cloud chains: AWS (env, profile, SSO, process, STS, IMDS), Azure (env, cli, MSI, cert), GCP (ADC, SA, impersonation, metadata), SigV4, RS256 | ✓ | ✓ | ✗ (explicit `BearerToken`; SigV4 has no Web Crypto impl) | ✓ (`aws-lc-rs` RS256) | SAME on Node/Rust (corpus: `auth` cloud, `token` 43/43, SigV4 34 vectors); browser NEVER except `Platform.signSigV4` extension point |
| Cloud-chain rungs nobody has: `aws login` DPoP refresh, Azure Service Fabric MI, GCP `external_account` with AWS source, `external_account_authorized_user`, `gdch_service_account` | ✗ | ✗ | ✗ | ✗ | SAME gap — each is a typed `NotConfiguredError` naming the fix, in all three |
| JWT-looking-key guard on a key-header door (`lm15/access.py:722`) | ✓ | ✓ | ✓ | ✗ | BEHIND (Rust) — deliberately unported ("AUTH-2 states the cost as the provider's 401; no case pins the guard"). Cheap to add; decide whether it is worth a case. |
| Duplicate spellings in `api_keys` (`openai-chat` + `openai_chat`) | refused | refused | refused | last write wins (builder canonicalises on insert) | BEHIND (Rust) — cannot be detected after the fact; refuse in `RouterConfig::api_key` when the canonical key exists. Small. |

## Surfaces beyond chat (all provisional per spec/SCOPE.md)

| Row | Python | TS / Node | TS / browser | Rust | Verdict |
|---|---|---|---|---|---|
| Files, batches, caches, image, speech, video (submit/status/result/list), model listing | ✓ | ✓ | ✓ (bytes you supply; no paths) | ✓ | SAME (corpus: `files`, `batch`, `cache`, `generation`, `video`, `models`) |
| `BatchJob` / `VideoJob` handles (`batch` / `batch_job` / `batches`, `video_generate` / `video_job` / `video_jobs`; `wait` bounded, `failed` returns) | ✓ | ✓ | ✓ | ✓ | SAME (api-family § Beyond chat, 2026-09-11; wait past its deadline is each language's own timeout type by rule) |
| Live sessions (Gemini Live, OpenAI Realtime): codec, send/receive, close | ✓ | ✓ | ✓ where the provider's WebSocket needs no request header (OpenAI's does → refused by name) | ✓ (`tokio-tungstenite`) | SAME (corpus: `live` 24/24); browser limit is the platform's |
| Live `turn()` → `Turn` (LIVE-1 boundary, LIVE-2 bill) | ✓ | ✓ | ✓ | ✓ | SAME (rules written 2026-09-11; each port pins them over a scripted socket — Rust replays the recorded `openai/live_tools` transcript) |
| `aws-event-stream` framing (Bedrock Converse, "phase 2") | ✗ | ✗ | ✗ | ✗ | SAME gap — no declared door uses it; refused by name everywhere |
| Async mirror | `Async*` classes | native | native | native + `blocking` feature | SAME (api-family rule 4) |

## Tooling and evidence

| Row | Python | TS / Node | TS / browser | Rust | Verdict |
|---|---|---|---|---|---|
| `lm15-vet` shim (every harness direction) | ✓ | ✓ | n/a | ✓ | SAME |
| `surface_dump` | reflection at call time | reflection at build time (`gen_surface.ts`) | — | not implemented (README: "not a gate") | BEHIND (Rust), low value — the ratchet runs on the reference. |
| Live receipts on this machine | chat core re-run 2026-09-11 (OpenAI ×2, Anthropic, Gemini, Groq) | chat core + local servers ("first contact") | Chromium/Firefox smoke vs a fake door; OpenRouter live opt-in | chat core + sessions | SAME gap — files/batch/video/cloud chains/OAuth refresh/xAI login not exercised live in any port since 2026-09-07 |
| CI matrix | Python 3.12, Linux only | Node 22, Linux | same | stable, Linux (build server) | BEHIND (all) — roadmap item 4 (3.10–3.14 × Linux/macOS/Windows; a type gate) is unmet in every repo |

## Reading this

- Every SAME row that says *corpus* is machine-checked at the pin; the
  others are claims and rot at the rate of the code.
- A BEHIND row is small by construction: the large ones already closed
  this week (shared keys, the OpenAI-shaped door, MAP-12 rule 9, stream
  completion, error metadata, `lmstudio`). What is left is one platform
  gap (the TS lock), two Rust guards, and a store API.
- The four OPEN rows were decided 2026-09-11 (job handles and live turns:
  family surface; profiles: never, Python deprecates; the loopback
  listener: on demand). No OPEN row remains.
