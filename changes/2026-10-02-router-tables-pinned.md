# 2026-10-02 — Router tables pinned; provider tables published and generated in every port

Status: RATIFIED 2026-10-02 (maintainer, in session: "do 1 to 5", the five
recommendations of `research/providers/ADDING.md` § 7). No wire fact
changes: no case, body or golden is touched; 46 router cases are added.

## Why

The study `research/providers/ADDING.md` found the routing tables
(`DEFAULT_RULES`, `LITELLM_PROVIDER_PREFIXES`) mostly unpinned — the `router`
direction pinned 4 of 13 rules and no litellm prefix — while TypeScript, Rust
and Go copied every provider table by hand (`port.md` rule 2). One copy had
already drifted: lm15-rs's TypeSafe rule was `"jev"`, so `jevons-1` routed to
TypeSafe in Rust and was `UnknownModelError` in the other five SDKs. R could
not declare a provider; the website kept its own provider lists and lacked the
four hosts of 2026-09-26.

## 1. Router tables pinned

- `router/resolution.json`: 46 cases. One per built-in rule not pinned
  before (9) and the wide two-letter form `o1`; one a byte short of each
  delimited rule (`claudette-1`, `gpt4all`, `gemini`, `gemma3`, `grok`,
  `sora2`, `veo3`, `jevons-1`); case sensitivity (`Claude-haiku-4-5`); an
  ollama-style `gemma3:4b`. Through the new op: one case per litellm prefix
  (16), first-segment-only (`groq/openai/gpt-oss-20b`), a bare OpenAI name to
  `openai-chat`, a bare name by rule, an lm15 string passed through, an
  explicit `openai:` kept, the deliberately absent `bedrock/` and
  `vertex_ai/`, a hyphenated non-litellm spelling, an unknown prefix, and a
  prefix with nothing after it. Expected values written by hand from the
  tables, then run through every shim.
- `harness/PROTOCOL.md`: op `resolve_openai_chat_model` (the router's
  OpenAI-SDK/litellm door, `resolve_openai_chat` in every port). A case names
  it with `"op"`; `harness/check.py` refuses an op it does not know.
- `harness/fake_shim.py`: two mutations, both caught by `selftest.py` (51 of
  51): `router_rule_delimiter_dropped` (the lm15-rs bug) and
  `router_litellm_prefix_kept`.

**Decision — a new op, not a `form` field on `resolve_model`.** A shim that
ignored an unknown field would answer through the plain door, silently; an
unknown op fails by name. Rejected: the field (smaller diff, silent
misreading by old shims).

Findings, both fixed in this change:

- **lm15-rs**: rule `"jev"` → `"jev-"` (`rule-boundary-jev`).
- **LM15.jl**: `openai_chat_model_string("groq/")` rewrote the string to
  `groq:` before refusing, so `error.model` named a string the caller never
  wrote (`openai-chat-litellm-empty-rest`); and it ignored a declared
  provider's spellings, which the reference reads (`providers=`). Both now as
  the reference.

## 2. Provider tables published; TypeScript, Rust and Go generate theirs

- `tables/providers.json`: the reference shim's new `provider_tables` op
  (reference only; `lm15-python/lm15/_vet_tables.py`): registry rows with
  whole access policies, the two managed-login declared providers, the three
  dialects' compat presets with base-URL and alias tables, `DEFAULT_RULES`,
  `LITELLM_PROVIDER_PREFIXES`, the AUTH-12 service labels. Written by
  `tools/export_provider_tables.py`; `tools/audit.py` fails when it differs
  from the reference, member order included. `tables/README.md` states the
  shape and the port rule.
- Each of lm15-ts, lm15-rs, lm15-go: `tools/gen_tables.py` writes
  `src/generated/tables.ts`, `src/generated/tables.rs`, `tables_generated.go`
  from the file at the port's `CONTRACT_PIN`; CI runs it with `--check`. The
  hand-written tables are gone; every public name stays (`access.GROQ`,
  `lm15::auth::GROQ`, `lm15.Groq`, `DEEPINFRA_FORCED_TOOL_CHOICE`, …), its
  value read from the generated data. Rust's scalar constants are computed
  from the table at compile time; Go's stay literal constants (Go cannot
  compute a constant from a variable) and `TestTableConstants` pins each to
  the table.

**Decision — publish in the contract, generate from the pin.** Rejected:
generate from an lm15-python checkout (a second pin per port; Julia's import
has none); move the tables' authority into the contract (an AUTHORITY.md
amendment and a rewrite of how Python loads its tables, for no gain while the
reference stays the place a table is changed). The file mirrors the
reference exactly as `spec/support-matrix.json` does, and is not an oracle.

What generation changed, stated:

- Rows now carry the reference's notes and order. TypeScript's and Rust's
  notes had drifted (Rust's shortened; TypeScript's Azure note lacked
  `AZURE_OPENAI_ENDPOINT`); rule and row order follow the reference. No
  harness check moved (the order of non-overlapping prefixes has no effect).
- TypeScript: `OPENAI_RESPONSES_PRESETS.lmstudio` was a getter returning the
  `ollama` object; it is now the reference's own (equal) entry. One test
  asserted object identity; it asserts the same policy by value.
- **xai's preset.** The reference's `xai` row has no compat: the `XaiLM`
  class binds the `xai` preset in its constructor (adapter code). Rust built
  xai from the row's compat; it now reads it from
  `ProviderDefinition::preset()`, the one adapter-owned binding written by
  hand with its citation. TypeScript and Go bind it in their xai classes, as
  before.
- **A login hint is language text.** The table's xai hint names the
  reference's Python function (`lm15.auth.login_xai()`); Rust keeps its own
  (`lm15::auth::login("xai")`) as an explicit override of the generated
  policy. TypeScript and Go already used the reference's wording.
- Julia and R keep their own copy tools, which read the reference directly
  (`tools/import_tables.py` imports it; `tools/copy-provider-tables.py`
  parses it). R's tool now also copies `DEFAULT_RULES` (its rule list was
  written inline in `new_router`) and each dialect's compat field names.
  Moving both to `tables/providers.json` is follow-up work, not done here.

## 3. R declares providers

`provider_definition()` and `new_router(providers =)`, as the reference's
`RouterConfig(providers=...)`: router-local, routed by id and alias,
`api_keys`/`base_urls` keyed by the id, `resolve()` answering
`declared = TRUE` (now present on every resolution), the litellm door reading
declared spellings, a spelling a built-in provider, a litellm prefix, a
managed-login route or another declaration uses refused; an unknown compat
knob refused by name (the reference's field list, copied). Key-based servers
only, as the reference: no cloud door, no subscription. `new_lm()` takes a
definition directly. 37 testthat expectations.

## 4. The website reads the registry

`src/playground/connections.ts` takes each provider's id and key variable
from the SDK registry (`PROVIDERS`, the pinned runtime package); the page adds
a label and a default model (the model the 2026-09-26 receipts used). Every
other registry provider is in `NOT_OFFERED` with its reason;
`tests/connections.test.ts` fails when the SDK has a provider the site has not
placed. `keyless()` and `judgmentsOnly()` read the registry instead of naming
providers. Now offered: xai, deepinfra, together, fireworks, parasail (each
answers a browser preflight with `access-control-allow-origin: *`, checked
2026-10-02, so no relay entry). Model pickers: models.dev ids for xai,
deepinfra, together, fireworks; parasail is `NOT_ON_MODELS_DEV` and its picker
shows the curated models.

Finding, fixed: the page wrote xai's Python client with the dialect's class
(`AsyncOpenAIChatLM`), whose request went to api.openai.com; it now writes
`AsyncXaiLM`. Caught by the existing provider-examples test once xai was
offered.

## Results (`harness/check.py --direction all`, network cut, on this commit)

| | Python | TypeScript | Rust | Go | Julia | R |
|---|---|---|---|---|---|---|
| Contract checks | 1,884 / 1,884 | 1,884 / 1,884 | 1,884 / 1,884 | 1,884 / 1,884 | 1,884 / 1,884 | see `playbooks/parity.md` |

Before this change: every SDK 1,838 of 1,838 at `57e33d1`. The 46 new checks
are the router cases.

## Stated trade-offs

- Pinned routing data is frozen data: a new built-in rule or litellm prefix
  costs a router case. That is the point.
- The published table is a mirror the audit keeps equal to the reference only
  where lm15-python is checked out (as for the support matrix); the contract's
  own CI skips the comparison without it.
- The generated files are large (Rust's is 2,300 lines after `rustfmt`) and
  carry no per-value receipt comments; the receipts stay cited at the
  reference's tables, which is where a value is changed.
- `allow(dead_code)` on Rust's generated module: the `wasm` codec build reads
  a subset (no managed login). Hand-written code keeps every lint.
- A browser preflight proves the browser may send the call, not that every
  reply carries the header; the hosts' replies are not re-checked live here.
- The models.dev snapshot was refreshed for all providers, not only the new
  ones, as any refresh does.

Ratified-by: Maxime Rivest, 2026-10-02 (in session)
