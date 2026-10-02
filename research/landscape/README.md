# Provider landscape

Which providers and models Pi and LiteLLM support, and where lm15 stands
against them. Start with [REPORT.md](REPORT.md).

| File | Kind | What it holds |
|---|---|---|
| `classification.json` | **reviewed by hand** | every upstream provider → `supported` / `partial` (with the lm15 provider strings) / `missing` / `out-of-scope` / `not-a-provider`, with notes |
| `snapshot.json` | generated | the upstream extract: Pi and LiteLLM versions and hashes, every provider, every model (one line each) |
| `REPORT.md` | generated | summary, ranked gaps, surface gaps on supported providers, Claude output-ceiling comparison |
| `models.tsv` | generated | one row per upstream model: does it reach a model through lm15, and through which provider string |

Tool: [`tools/provider_landscape.py`](../../tools/provider_landscape.py).
Stdlib only; reads `spec/support-matrix.json` and never writes it.

## Where the data comes from

- **Pi**: the published `@earendil-works/pi-ai` npm package. The tarball's
  sha512 is checked against the registry's integrity field. Read: the
  model catalogs in `dist/providers/data/*.json`, the `KnownProvider` union,
  and each provider module's id, display name, auth labels and env keys.
- **LiteLLM**: the release tag `v<version>` on GitHub, version from PyPI.
  Read: the `LlmProviders` enum, `provider_endpoints_support_backup.json`,
  `llms/openai_like/providers.json`, `openai_compatible_providers` and the
  model price/context table. Each file's sha256 is recorded.
- **lm15**: `spec/support-matrix.json` on every run, plus the Python
  reference's Claude output-ceiling table at update time.

## The maintenance loop

```sh
python3 tools/provider_landscape.py update     # network: fetch latest, print what changed
python3 tools/provider_landscape.py suggest    # stubs for new upstream providers
# edit classification.json: review each stub
python3 tools/provider_landscape.py report     # regenerate REPORT.md / models.tsv
python3 tools/provider_landscape.py check      # offline gate, also run in CI
```

`check` fails when an upstream provider is unclassified, an entry names a
provider upstream dropped, an entry names an lm15 string the matrix lacks,
a `missing` entry shares its name with a provider lm15 now ships, or the
generated files are stale. Editing the support matrix therefore needs a
`report` run in the same change.

Pin a version with `--pi-version` / `--litellm-version`; read installed
packages offline with `--pi-package DIR` / `--litellm-dir DIR`.

## How to read it

- Upstream listing a provider is not evidence it works, for them or for
  lm15. Support claims stay in the support matrix, backed by receipts.
- LiteLLM marks `messages`, `responses`, `a2a` and `interactions` true for
  most providers because LiteLLM translates them to chat. The tool drops
  every endpoint the upstream file flags `bridges_to_chat_completion`.
- *lm15 wire* in the gap table means lm15 already speaks that provider's
  wire, so a declared provider (`RouterConfig(providers=...)`) reaches it
  today; registering it is a registry entry plus live receipts.
- Automatic `out-of-scope`: a provider whose every offering is ruled out
  (embeddings, vector stores, web search, guardrails, fine-tuning). Speech
  to text, rerank, moderation and OCR are *no lm15 surface*, not ruled out:
  the contract has not decided them.
