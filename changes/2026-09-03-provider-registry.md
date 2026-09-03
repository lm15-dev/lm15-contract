# 2026-09-03 — One provider registry; DeepSeek is its first data-only provider

Status: DRAFT, pending ratification.  The DeepSeek wire rows are declared
from provider documentation (AUTHORITY.md precedence 2) and await the
live receipt; see § What is not yet evidenced.

## Why

The provider-expansion plan (2026-09-01) starts from one architectural
change: provider knowledge lived in five places in the reference
(`ADAPTERS`, `CHAT_PRESET_ROUTES`, the `preset()` if-chain in
`compat.py`, `OPENAI_CHAT_PRESET_BASE_URLS`, the vet shim's
`adapter_for_provider` if-chain) plus the docs tables, and a sixth in
every port's auth table.  Forty providers on that layout drift.  This
entry lands the registry with the twelve existing providers unchanged
and pushes one new provider through it to prove the path is a
declaration plus a receipt, never a class.

## Reference changes (lm15-python)

- `lm15/registry.py`: `ProviderDefinition` (id, dialect, adapter,
  async_adapter, access policy, compat preset, placeholder key, console
  URL, note) and `PROVIDERS`, the one table.  Two kinds of entry share
  the shape: adapter-owned (the class manifest IS the access policy) and
  chat-bound (`OpenAIChatLM` with an `lm15.access` policy and a compat
  preset bound at construction).  The dataclass rejects drift at import
  time: an id that is not hyphenated, an access policy naming another
  provider, a bound entry whose `base_url` differs from the compat
  table, a keyless server with env keys.
- `lm15/access.py`: policies `GROQ`, `OPENROUTER`, `DEEPSEEK`, `OLLAMA`,
  `VLLM`, `SGLANG` (surfaces complete/stream/models, bearer, the
  provider's own env key, `base_url` from the compat table).
- `lm15/compat.py`: `OPENAI_CHAT_PRESETS` table replaces the if-chain;
  `preset()` reads it through the alias map.  `deepseek` preset gains
  `thinking_replay="native"` and `assistant_reasoning_content=
  "include_empty"` (docs: `reasoning_content` must come back on every
  assistant turn when `tools` is present, else 400).  `deepseek` base
  URL `https://api.deepseek.com` added.
- `lm15/router.py`: `ADAPTERS`, `ASYNC_ADAPTERS`, `CHAT_PRESET_ROUTES`
  are read-only views (`MappingProxyType`) of the registry; same keys,
  same values.  `_build_lm` binds `access=` and `compat=` for chat-bound
  entries.
- `lm15/vet.py`: `adapter_for_provider` and `_reflect_providers` walk the
  registry.  The surface dump now reflects every routable provider.
- Tests: `tests/test_registry.py` (13) pin the rules above and that every
  view, the doctor, and the surface dump agree with the table.

Behavior change, stated: a router-built chat preset LM now names its
provider.  `router.lm("groq:…").provider == "groq"` (was `"openai_chat"`),
so errors, `ModelInfo.provider` from `list_models()`, and
`lm.access.env_keys` say groq.  `OpenAIChatLM(compat="groq")` built
directly is unchanged (its manifest stays `openai_chat`).  No pinned
fixture depended on the old name (the harness is green: request 147,
response 129, stream 14, error 18, serde 110, auth 15, models 14 …).

## Contract changes (this repository)

- `spec/support-matrix.json`: six rows added — `groq`, `openrouter`,
  `deepseek`, `ollama`, `vllm`, `sglang` — reflecting the registry.
  `tools/audit.py` compares 13 providers both ways: pinned and matching.
  Evidence per row:
  - `groq`: `changes/2026-06-10-openai-chat-live-cases.md` (ten live
    cases, `/models` listing used to pick the model),
    `receipts/2026-09-01-chat-builtin-tools/groq-*.json`.
  - `openrouter`: `receipts/2026-09-01-chat-builtin-tools/openrouter-*.json`.
  - `vllm`, `sglang`: `changes/2026-06-10-vllm-sglang-live-cases.md`
    (`cases/openai_chat/*_vllm.json`, `*_sglang.json`).
  - `ollama`: no capture in this corpus; the row pins what the class
    already did for it (the chat dialect's `models: true`).  Flagged.
  - `deepseek`: **documentation only** (below).
- `auth/resolution.json`: case `deepseek-env-selected` (plain AUTH-1 key
  chain; the fixture's third key-only provider after groq and ollama).
  Mirrored to `lm15-python/conformance/auth_resolution.json`.  Ports:
  one table line each (Go, Rust, TypeScript, Julia), all four suites
  green.  The ports' fixture copies predate xai and were not resynced
  here; that is the port playbook's job, not this entry's.
- `tools/check_secrecy.py`: a DeepSeek key pattern (`sk-` + 32 hex) and
  `.sse` files in the scan, before any capture can leak one.
- `scrapes/deepseek/`: `update.sh` + `html2text.py` (Docusaurus has no
  Markdown endpoint), 15 pages fetched 2026-09-03.
- `research/providers/deepseek/`: the dossier (`README.md`), frozen
  terms-of-service and privacy sources with sha256, and `capture.py` —
  the controlled validator: adapter-built wires, verbatim bodies, cases
  in the corpus shape, probes for the six open decisions, `--dry-run`
  prints every wire without sending.

## Terms verdict (DeepSeek)

Allowed, API key only.  § 1.1 grants downstream application use for
internal and external end users; § 4.2 allows derivative products and
distillation; § 6 is prepaid balance (HTTP 402 when drained — no
surprise bill); § 10.1 PRC law; personal data stored in the PRC.  No
OAuth client to borrow, no coding-plan restriction.  Sources frozen
under `research/providers/deepseek/sources/`.

## What is not yet evidenced

`deepseek` has **no live receipt**.  Its support-matrix row, its compat
preset, and its docs table line come from `scrapes/deepseek/pages/`
(2026-09-03).  The dossier lists six decisions that need a wire
sighting: `user` vs `user_id`; `temperature` ignored in thinking mode;
`minimal` effort; `json_schema` response_format; the cache-usage
spelling (`prompt_cache_hit_tokens` vs `prompt_tokens_details`);
`insufficient_system_resource` finish reason.  Running

```
DEEPSEEK_API_KEY=… python3 research/providers/deepseek/capture.py
```

lands `cases/deepseek/` (10), `bodies/deepseek.*`, `errors/cases/
deepseek.json`, and `receipts/2026-09-03-deepseek/`; a follow-up entry
`changes/<date>-deepseek-live.md` records the receipt table and
resolves the six decisions.  Until then the ledger in the dossier reads
"implemented, offline-conformant, not live-verified", and a reviewer
should treat the row as a claim, not a fact.

Ratified-by: (pending)
