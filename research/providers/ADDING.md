# Adding providers and models to lm15 — a study

Status: STUDY, 2026-10-02. Not ratified, binds nobody. A candidate for
`playbooks/provider.md`. Every claim below cites the file it was read from;
the worked example throughout is `changes/2026-09-26-inference-hosts-live.md`
(DeepInfra, Together, Fireworks, Parasail: four providers in one day).

## 1. The model in one paragraph

A **provider** is a string (`groq`) naming one row of
`lm15-python/lm15/registry.py` `PROVIDERS`: a **dialect** (the wire lm15
speaks: `openai-responses`, `openai-chat`, `anthropic`, `gemini`,
`typesafe`), an **access policy** (`lm15/access.py`: env keys, auth modes,
base URL or cloud host template, which surfaces it serves) and, for the
three re-usable dialects, a **compat preset** (`lm15/compat.py`: the
server's quirks as data, e.g. `max_tokens` vs `max_completion_tokens`,
where reasoning goes, what a forced tool choice does). One provider
string means one wire: the same vendor on two wires is two rows
(`moonshotai`, `moonshotai-responses`, `moonshotai-anthropic`). A **model**
is not a row anywhere. It is the text after `provider:`, sent to the
server verbatim. lm15 keeps no model list (by design, since April). What
it keeps is *knowledge about model families* where a wire forces a
client-side decision.

## 2. How the router turns a string into a call

`lm15/router.py` `_resolve`, four rungs, fixed order:

| Rung | Input | Example | Where the table lives |
|---|---|---|---|
| 0 object | a model value carrying `.provider` (catalog packages) | aimo model objects | the catalog package |
| 1 prefix | `provider:model`, split on the **first** colon | `groq:llama-3.3-70b-versatile`, `bedrock-chat:openai.gpt-oss-20b-1:0` | `PROVIDERS` + aliases + `RouterConfig.providers` |
| 2 catalog | a bare id or alias, only if `RouterConfig(registry=ModelRegistry.discover())` | `sonnet` | entry-point group `lm15.model_catalogs` (`docs/model-hydration.md`; advisory, never changes the wire) |
| 3 rule | a bare id by prefix | `claude-…` → anthropic, `grok-…` → xai | `DEFAULT_RULES` (13 rules) |

The LiteLLM/OpenAI-SDK migration path (`complete_from_openai_chat`,
`openai_chat_model_string`) also reads `provider/model`, mapping the
first segment through `LITELLM_PROVIDER_PREFIXES` (16 entries) or a
declared provider's spellings. The plain router does not read `/`.

What a user can configure (`RouterConfig`): `api_keys`, `base_urls`,
`settings` (cloud host values), `credentials` (named cloud identity),
`rules` (prepend to override), `registry` (catalog), `providers`
(declared providers), `adaptations`, `auth` (managed login), and the
transport knobs.

## 3. Which kind of addition is it?

| Kind | What it is | Code? | Example | Cost seen |
|---|---|---|---|---|
| **0. Declare** | User-side: `ProviderDefinition.chat/.responses/.anthropic(access, compat=…)` in `RouterConfig(providers=…)`. `Resolution.declared` is true and says "no lm15 receipts". | none in lm15 | Nebius example in `docs/using-the-router.md` | minutes |
| **A. Same wire, new server** | A registry row + access policy + compat preset. Pure data in Python (`registry.py` docstring: "a declaration in this file plus a live receipt, never a new class"). | data in 6 SDKs | groq, deepseek, the four hosts | ~1 day for 4 (2026-09-26) |
| **A′. New compat knob** | A server needs a behavior no knob expresses. `playbooks/api-family.md` rule 7: a knob only when the wire has no other way, the goal is unreachable without it, and two providers need it. | dialect code in 6 SDKs | `reasoning_off` (2026-09-26), `forced_tool_choice`, `json_schema` (Z.AI) | one ratified decision + every port |
| **B. Cloud door** | An existing dialect behind a host template, a signing/auth chain and small body rewrites (`ProviderDefinition.hosted`, `AccessPolicy.host`). | auth + URL code, mostly shared | azure-chat, bedrock-chat, vertex-anthropic | days per cloud (2026-09-03…26) |
| **C. New wire** | A dialect lm15 does not speak: new request builder, parser, stream decoder, error map, MAP rules, harness cases. | a new adapter in 6 SDKs | Bedrock Converse (`bedrock`, "phase 2" in `spec/auth.md`), Mistral conversations, Cohere native, Pi's `pi-messages` | weeks |
| **D. Subscription / OAuth** | A key-less account login. A declared provider must be key-based (`ProviderDefinition.__post_init__`), so this is either an adapter-owned class (`claude-code`, `openai-codex`) or a managed-login declared provider (`lm15/login/declared.py`: `kimi-code`, `github-copilot`). Terms must allow it (Gemini CLI and Antigravity do not). | adapter or login flow | claude-code, kimi-code | varies; terms first |

And for models:

| Kind | When | Where |
|---|---|---|
| **M0. Nothing** | Almost always. A new model on a supported provider works the day it ships: `provider:new-model`. | — |
| **M1. Bare-name rule** | A new *family* should route without a prefix. Only for families whose name is unambiguous across providers. | `DEFAULT_RULES` |
| **M2. Per-model quirk** | One model family on one server behaves differently (silently ignores a knob). Needs a receipt; rots when hosts add families (stated trade-off, 2026-09-26). | `OpenAIChatCompat.model_overrides` (prefix match) |
| **M3. Model-class detector** | The wire itself changes by model: Claude adaptive thinking (`_ADAPTIVE_CLASS_MARKERS`), Claude output ceilings (`_CLAUDE_OUTPUT_CEILINGS`), GPT ≥ 5.6 cache options (`openai_model_has_cache_options`), Gemini 3 thinking levels. | the adapter module; copied as data (port rule 2) |
| **M4. Not-found wording** | A provider says "no such model" without a model-specific code. | `spec/model-not-found.json` (MAP-15), only with a live receipt |
| **M5. Metadata** | Prices, context windows, aliases. Advisory only. | a catalog package via `lm15.model_catalogs` |

## 4. The Kind A checklist (what 2026-09-26 actually touched)

The dossier lifecycle every provider in `research/providers/*/README.md`
follows: **candidate → researched → implemented → offline-conformant →
live-verified → supported**.

**Research (contract)**
1. `scrapes/<p>/update.sh` + pages; `research/providers/<p>/sources/` the
   terms of service and privacy policy, frozen with sha256.
2. `research/providers/<p>/README.md` dossier: identity, wire facts table,
   **terms verdict** (DeepSeek, Parasail examples). Terms decide what may be
   recorded: Parasail § 2.2(h) forbids publishing performance data, so its
   receipts carry no latency.

**Reference (lm15-python)**
3. `lm15/compat.py`: preset in `OPENAI_CHAT_PRESETS` (or the Responses /
   Anthropic table), base URL in `OPENAI_CHAT_PRESET_BASE_URLS`, each value
   commented with its receipt or doc line.
4. `lm15/access.py`: the `AccessPolicy` (surfaces, auth modes, env keys,
   `base_url` read from the compat table — one copy of each URL).
5. `lm15/registry.py`: the row (`_chat_bound(...)`, console URL, note). The
   dataclass refuses drift at import (`base_url` must equal the compat
   table, keyless means no env keys, ids hyphenated).
6. `lm15/router.py`: a `LITELLM_PROVIDER_PREFIXES` entry if LiteLLM spells
   it differently; a `DEFAULT_RULES` entry only for M1.
7. `lm15/login/flows/__init__.py`: the service display name (AUTH-12).
8. Tests: `tests/test_registry.py` (views, doctor, surface dump agree) plus a
   provider test file (`tests/test_inference_hosts.py`).
9. `docs/providers-and-models.md` table row and notes.

**Evidence (contract)**
10. `research/providers/<p>/capture.py` (for a chat host: a `Models`
    declaration over `_inference_hosts.py`; `--dry-run` prints every wire).
    Run it live → `cases/<p>/`, `bodies/`, `receipts/<date>-<p>/`,
    `errors/cases/<p>.json`.
11. Goldens via `tools/scribe_goldens.py` (drafts until reviewed).
12. `spec/support-matrix.json` row (`tools/audit.py` fails until it equals
    the reference, both ways).
13. `auth/resolution.json` case `<p>-env-selected`, mirrored to
    `lm15-python/conformance/auth_resolution.json` and
    `lm15-jl/conformance/auth/resolution.json`.
14. `auth/managed/runs/core.json` discovery list.
15. `tools/check_secrecy.py` key-shape pattern (or a manual search when keys
    have no prefix, as DeepInfra).
16. `tools/check_content_coverage.py`: a `tool_result_image` case, a refusal
    case, or an `OPEN` entry with the reason (MAP-10).
17. `spec/model-not-found.json` if the not-found wording is new (M4).
18. `changes/<date>-<p>-live.md`: receipts table, every decision with
    options, **ratification**.
19. `research/landscape/classification.json`: flip the entry to
    `supported`; `tools/provider_landscape.py check` fails with SUSPECT
    until you do, then run `report`.

**Ports** (`playbooks/port.md` rule 2: copy tables as data)

| SDK | Files | How the table arrives |
|---|---|---|
| TypeScript | `src/registry.ts`, `src/auth/policy.ts`, `src/compat.ts`, `src/router.ts`, `src/login/table.ts` | by hand |
| Rust | `src/registry.rs`, `src/auth/policy.rs`, `src/compat/openai_chat.rs`, `src/router.rs`, `src/login/table.rs` | by hand |
| Go | `registry.go`, `access.go`, `compat.go`, `router.go`, `login_table.go` | by hand |
| Julia | `src/data/{providers,compat,routing}.json` | `tools/import_tables.py` (imports the reference) |
| R | `R/provider-data.R` | `tools/copy-provider-tables.py` (parses the reference) |

Then each port: `CONTRACT_PIN` → the new contract commit, `harness/check.py
--direction all` green, a row in `playbooks/parity.md`, a live smoke receipt
(`tools/live_smoke.*`), release.

**Website**: `src/content/docs/compatibility/providers/<p>.md`,
`navigation.mjs`, `src/playground/connections.ts`,
`src/data/model-catalog.ts` (`CATALOG_PROVIDERS`), and the relay allowlist
(`relay/`) if the provider blocks browsers (CORS); then a runtime build.

## 5. What a user does today for a provider lm15 lacks

1. **Its wire is one lm15 speaks** (the landscape report's *lm15 wire*
   column): declare it (Kind 0). Pick `compat=OpenAIChatCompat()` and set
   knobs from the server's docs, or start from a near preset
   (`docs/connecting-openai-compatible-servers.md`). Works in Python,
   TypeScript, Go, Rust and Julia; **not in R** (finding F3).
2. **Same server as a preset, another address**:
   `RouterConfig(base_urls={"vllm": "http://gpu-box:8000/v1"})`.
3. **Several differently configured instances**: build the LM directly
   (`OpenAIChatLM(api_key=…, compat=…, base_url=…)`); the router is one
   instance per provider.
4. **A wire lm15 does not speak**: nothing, until Kind C.

## 6. Findings

**F1 — There is no provider playbook.** The lifecycle and the 19-step
contract checklist above exist only as a convention repeated across
dossiers and two change entries. Everything else that is hard (ports,
parity, design passes) has a playbook.

**F2 — The tables the harness does not pin can drift, and one has.** The
`router` direction pins 4 of the 13 `DEFAULT_RULES` (claude, gpt, gemini,
grok) and none of the 16 `LITELLM_PROVIDER_PREFIXES`. TypeScript, Rust and
Go copy them by hand. Found by reading the code: Rust's rule is `"jev"`
(lm15-rs `src/router.rs`), every other SDK's is `"jev-"`, so in Rust a
model named `jevons-1` routes to TypeSafe while the other five raise
`UnknownModelError`. R writes its rule list inline in `new_router`
(`R/client.R`) instead of copying it. Preset knob values are exposed the
same way: a value no case exercises can differ silently.

**F3 — R cannot declare a provider.** `new_router()` has no `providers`
argument; the only declared providers in R are the two managed-login ones.
Every other SDK has it.

**F4 — The website keeps its own provider lists, and they are behind.**
`src/playground/connections.ts` and `src/data/model-catalog.ts` lack
DeepInfra, Together, Fireworks and Parasail (added to the SDKs 2026-09-26),
though the compatibility pages have them.

**F5 — The 2026-09-03 proposal to move the provider table into the
contract** (`spec/providers.json` plus a harness check that each SDK's
embedded copy equals it; recorded in session 01a06702, 2026-09-03) was
never decided. Julia and R later solved the copy mechanically from Python;
TypeScript, Rust and Go did not.

**F6 — Most of the gap is cheap.** All 10 services that both Pi and
LiteLLM carry and lm15 lacks (`research/landscape/REPORT.md`, 2026-10-02:
Vercel AI Gateway, Mistral, Hugging Face, GitHub Copilot, Cloudflare
Workers AI, Baseten, NVIDIA, MiniMax, Cerebras, Xiaomi) speak a wire lm15
already speaks (Chat Completions or Anthropic Messages): Kind A, the
2026-09-26 path, except GitHub Copilot (Kind D). The expensive ones are
Kind C: Bedrock Converse (Pi's only Bedrock wire), Mistral's Conversations
API (its Chat Completions API is the Kind A door), Cohere's native API, and
Pi's own `pi-messages` gateway.

## 7. Recommendations, in order

1. **Pin the router tables in the harness** (closes F2). Add one
   `router/resolution.json` case per `DEFAULT_RULES` entry, including a
   negative for each prefix boundary (`jevons-1` → unknown), and add an
   ingest-direction case per `LITELLM_PROVIDER_PREFIXES` entry. About 30
   cases, no ratification needed beyond the corpus change. Fix Rust's
   `jev` rule in the same change. Trade-off: rules become frozen data;
   adding a rule then costs a case, which is the point.
2. **Write `playbooks/provider.md`** from §3–§4 (closes F1), with the
   lifecycle as the only states a dossier may claim.
3. **Generate the TypeScript, Rust and Go tables from the reference**
   the way Julia and R do, with a CI check that the generated file is
   current. This is F5's goal without moving the authority: the contract
   already pins behavior through cases; the generator removes hand
   copying. Trade-off: the reference stays the table's source, so a table
   bug still propagates everywhere — but identically, where the harness and
   `differential.py` can see it. The alternative, `spec/providers.json` as
   the authority, is cleaner in principle and needs an AUTHORITY.md
   amendment and a rewrite of how Python loads its tables; I would only
   take it if a seventh SDK is planned.
4. **Add `providers =` to R's `new_router`** (closes F3).
5. **Drive the website lists from the registry** (closes F4): the
   playground connections and catalog providers read the TypeScript SDK's
   `PROVIDERS` instead of a fourth copy.
6. **Then add providers in batches of the same wire**, as 2026-09-26 did:
   one shared capture declaration, one change entry, one ratification.
   The landscape report ranks them.

None of the above was implemented in this study.
