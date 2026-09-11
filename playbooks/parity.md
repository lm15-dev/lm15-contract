# Parity ledger — what each implementation has, lacks, or will never have

Status: LEDGER (kept current by whoever moves a pin; not itself normative).
Started 2026-09-11 from a file-by-file comparison of `lm15-python` 8bafafa,
`lm15-ts` 17a521e (+ uncommitted browser work), `lm15-rs` c81ad74, all at
contract pin 42d8040. The harness proves the rows marked *corpus*; the
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
| `ProviderProfile` / `EndpointProfile` layering (`lm15/profiles.py`) | ✓ | ✗ | ✗ | ✗ | OPEN — Python ergonomic layer over compat; Rust README lists it under "not implemented, stated"; no api-family row. Decide: port, or declare Python-only. |

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
| `lm15.tool` / `derive_tool` (JSON Schema from a function signature) | ✓ | ✗ | ✗ | ✗ | NEVER — api-family § Tools: `tool(name, { parameters })` takes the schema you write, "stated once for all three non-Python ports". |

## Auth

| Row | Python | TS / Node | TS / browser | Rust | Verdict |
|---|---|---|---|---|---|
| AUTH-1 chain: explicit key / callable, env keys, placeholder, stored login, cloud chain | ✓ | ✓ | explicit only (no env, no files) | ✓ | SAME on Node/Rust; browser NEVER by design (`lm15-ts/docs/browser.md`: refused by name, never guessed) |
| AUTH-7 doctor (`explain_auth`) | ✓ (+ accepts a `Resolution`) | ✓ | ✓ (reports rungs absent) | ✓ | SAME (corpus: `auth` 43/43) |
| Stored logins: Claude Code, Codex (AUTH-8), refresh under the lock (AUTH-3/4) | ✓ | ✓ | ✗ (no filesystem) | ✓ | SAME on Node/Rust; browser NEVER |
| AUTH-4 lock: platforms | POSIX `fcntl` + Windows `msvcrt` | **Linux only**, needs util-linux `flock` on PATH; elsewhere fails closed | n/a | std `File::try_lock` (cross-platform) | BEHIND (TS): macOS/Windows cannot refresh a stored login; explicit keys still work. Recorded as a stated deviation. Fix: a native lock (N-API or `fs.open` + `flock` via a small addon) or accept and document. |
| xAI device-code login (AUTH-9), PKCE S256, RFC 8628 polling | ✓ | ✓ (`login`, `loginXai`, `generatePkce`) | PKCE only | ✓ | SAME |
| `OAuthCallbackListener` (loopback redirect listener) | ✓ (`authkit`) | ✗ | ✗ (a page *is* the redirect target) | ✗ | OPEN — Rust README: "built when a flow needs it; a listener is a server with its own attack surface". No flow lm15 owns uses it today. Decide: port on demand, or declare Python-only. |
| `CredentialFileStore` (lm15-owned multi-provider store, `mutate`) | ✓ | ✓ | ✗ | partial (xAI entry only, inside `login.rs`) | BEHIND (Rust): no general store API; only the one lm15-owned login writes. Small. |
| Cloud chains: AWS (env, profile, SSO, process, STS, IMDS), Azure (env, cli, MSI, cert), GCP (ADC, SA, impersonation, metadata), SigV4, RS256 | ✓ | ✓ | ✗ (explicit `BearerToken`; SigV4 has no Web Crypto impl) | ✓ (`aws-lc-rs` RS256) | SAME on Node/Rust (corpus: `auth` cloud, `token` 43/43, SigV4 34 vectors); browser NEVER except `Platform.signSigV4` extension point |
| Cloud-chain rungs nobody has: `aws login` DPoP refresh, Azure Service Fabric MI, GCP `external_account` with AWS source, `external_account_authorized_user`, `gdch_service_account` | ✗ | ✗ | ✗ | ✗ | SAME gap — each is a typed `NotConfiguredError` naming the fix, in all three |
| JWT-looking-key guard on a key-header door (`lm15/access.py:722`) | ✓ | ✓ | ✓ | ✗ | BEHIND (Rust) — deliberately unported ("AUTH-2 states the cost as the provider's 401; no case pins the guard"). Cheap to add; decide whether it is worth a case. |
| Duplicate spellings in `api_keys` (`openai-chat` + `openai_chat`) | refused | refused | refused | last write wins (builder canonicalises on insert) | BEHIND (Rust) — cannot be detected after the fact; refuse in `RouterConfig::api_key` when the canonical key exists. Small. |

## Surfaces beyond chat (all provisional per spec/SCOPE.md)

| Row | Python | TS / Node | TS / browser | Rust | Verdict |
|---|---|---|---|---|---|
| Files, batches, caches, image, speech, video (submit/status/result/list), model listing | ✓ | ✓ | ✓ (bytes you supply; no paths) | ✓ | SAME (corpus: `files`, `batch`, `cache`, `generation`, `video`, `models`) |
| `VideoJob` handle sugar (`video_generate` → poll → result on one object) | ✓ | ✗ (four verbs) | ✗ | ✗ (four verbs; README: "out of contract scope") | OPEN — api-family names no row for it. Decide: sugar in every port, or Python-only. |
| Live sessions (Gemini Live, OpenAI Realtime): codec, send/receive, close | ✓ | ✓ | ✓ where the provider's WebSocket needs no request header (OpenAI's does → refused by name) | ✓ (`tokio-tungstenite`) | SAME (corpus: `live` 24/24); browser limit is the platform's |
| Live `turn()` view / pending-queue mechanics | ✓ | ✗ | ✗ | ✗ (README: not reproduced) | OPEN — same decision as `VideoJob`. |
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
- The OPEN rows are one decision, not four: *does the family mirror
  Python's ergonomic sugar* (`ProviderProfile`, `VideoJob`, live `turn()`,
  the loopback listener) *or is that sugar Python's alone?* The
  api-family playbook is silent; it should say.
