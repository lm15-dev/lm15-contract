# Provider — adding a provider or model knowledge to lm15

Status: RATIFIED 2026-10-02 (maintainer, in session; from the study
`research/providers/ADDING.md`; change entry
`changes/2026-10-02-router-tables-pinned.md`). Companions: `port.md` (how a
port carries what lands here), `parity.md` (the ledger), `design-pass.md`
(when the provider needs a decision the rules do not settle).

The worked example is `changes/2026-09-26-inference-hosts-live.md`: four
providers on a known wire, one shared capture declaration, one change entry,
one ratification. Do the same.

## 1. Which kind is it

| Kind | What changes | Example |
|---|---|---|
| **0. Declare** | Nothing in lm15. A user describes the server for one router: `ProviderDefinition.chat/.responses/.anthropic(...)` in `RouterConfig(providers=...)` (R: `provider_definition()` in `new_router(providers =)`). It routes and says `declared` — no receipt. | Nebius in `docs/using-the-router.md` |
| **A. Same wire, new server** | A registry row, an access policy and a compat preset in the reference; data everywhere else. | groq, deepseek, the four hosts |
| **A′. New compat knob** | Dialect code in every SDK. Only when the wire has no other way, the goal is unreachable without it, and two providers need it (`api-family.md` rule 7); otherwise `extensions`. | `reasoning_off` |
| **B. Cloud door** | An existing dialect behind a host template and an auth chain (`AccessPolicy.host`, AUTH-10). | azure-chat, bedrock-chat |
| **C. New wire** | A new adapter in every SDK, MAP rules, harness cases. | Bedrock Converse, Mistral Conversations |
| **D. Subscription login** | An adapter-owned class or a managed-login flow (AUTH-12–26); the provider's terms decide first. | claude-code, kimi-code |

Model knowledge, cheapest first: **nothing** (`provider:new-model` works the
day it ships); a **bare-name rule** (`DEFAULT_RULES`, only for a family whose
name no other provider uses); a **per-model override**
(`OpenAIChatCompat.model_overrides`, with the receipt that shows the family
differs); a **model-class detector** in the adapter (Claude output ceilings,
adaptive thinking); a **not-found form** (`spec/model-not-found.json`, MAP-15);
**metadata** through a catalog package (advisory only). lm15 keeps no model
list.

## 2. States a dossier may claim

`research/providers/<p>/README.md` opens with this table and claims no state
whose evidence it cannot cite:

| State | Evidence |
|---|---|
| candidate | who asked, and why |
| researched | `scrapes/<p>/`; terms and privacy frozen with sha256 under `sources/`; the terms verdict written |
| implemented | registry row, access policy, compat preset in lm15-python |
| offline-conformant | support-matrix row; auth case; tables exported; every SDK green at the pin |
| live-verified | `receipts/<date>-<p>/`, cases, error envelopes, the change entry's receipt table |
| supported | the change entry ratified |

A row in `spec/support-matrix.json` is a support claim (AUTH-26). A provider
with no live receipt is a declaration (kind 0) or a documentation-only row the
change entry flags as such, never silently supported.

## 3. Kind A, in order

**Terms first.** Read the terms of service before writing code: what they
forbid recording (Parasail § 2.2(h): no published performance data, so its
receipts carry no latency), whether a subscription may be used by a third
party, where data is stored. Freeze them. A verdict "not allowed" ends here.

**Reference (lm15-python)**

1. `lm15/compat.py`: the preset, every knob commented with its receipt or
   documentation line; the base URL in the preset's base-URL table.
2. `lm15/access.py`: the access policy (surfaces, auth modes, env keys, the
   base URL read from the compat table: one copy of each URL).
3. `lm15/registry.py`: the row (console URL, note). The dataclass refuses
   drift at import.
4. `lm15/router.py`: a `LITELLM_PROVIDER_PREFIXES` entry when litellm spells
   the provider differently; a `DEFAULT_RULES` entry only for a bare-name
   family.
5. `lm15/login/flows/__init__.py`: the service label (AUTH-12).
6. Tests (`tests/test_registry.py` agreements, a provider test file) and
   `docs/providers-and-models.md`.

**Contract**

7. Capture: `research/providers/<p>/capture.py` (a chat host: a `Models`
   declaration over `_inference_hosts.py`; `--dry-run` first) → `cases/<p>/`,
   `bodies/`, `receipts/<date>-<p>/`, `errors/cases/<p>.json`; goldens from
   `tools/scribe_goldens.py`, reviewed.
8. `spec/support-matrix.json` row (`tools/audit.py` compares it with the
   reference, both ways).
9. `python3 tools/export_provider_tables.py` → `tables/providers.json`
   (`tools/audit.py` fails while it differs from the reference).
10. `auth/resolution.json` `<p>-env-selected`, mirrored to
    `lm15-python/conformance/auth_resolution.json` and
    `lm15-jl/conformance/auth/resolution.json`; the discovery list in
    `auth/managed/runs/core.json`.
11. A new litellm prefix or rule gets its `router/resolution.json` case in
    the same change (a rule: one positive case and one a byte short of the
    prefix; a prefix: a `resolve_openai_chat_model` case). Unpinned routing
    data is how lm15-rs's `jev` rule drifted (2026-10-02).
12. `tools/check_secrecy.py`: the key's shape (or, for a key with no prefix,
    a search of every capture for the literal key before commit).
13. `tools/check_content_coverage.py`: a `tool_result_image` case, a refusal
    case, or an `OPEN` entry with the reason (MAP-10).
14. `spec/model-not-found.json` when the not-found wording is new.
15. `changes/<date>-<p>-live.md`: the receipt table, every decision with its
    options and the one taken, the trade-offs, ratification.
16. `research/landscape/classification.json`: the entry moves to
    `supported`; `tools/provider_landscape.py check` fails until it does.

**Ports** — never hand-edited tables:

17. TypeScript, Rust, Go: move `CONTRACT_PIN`, run `python3
    tools/gen_tables.py` (each port's CI runs it with `--check`). Julia:
    `tools/import_tables.py`. R: `tools/copy-provider-tables.py`. Then the
    harness, every direction, at the pin; a live smoke receipt; a row in
    `parity.md`.
18. Only what is not a table is written by hand: a new knob's dialect code
    (A′), a new adapter (C), a login flow (D).

**Website**

19. `src/playground/connections.ts`: the provider is offered (a label and a
    default model a receipt used) or listed in `NOT_OFFERED` with the reason;
    `tests/connections.test.ts` fails until one is true. A model-picker source
    in `src/data/model-catalog.ts` (`CATALOG_PROVIDERS`, or
    `NOT_ON_MODELS_DEV`). A provider that refuses browser origins needs the
    relay's allow-list (`relay/`) before it is offered. Then
    `src/content/docs/compatibility/providers/<p>.md` and `navigation.mjs`.

## 4. Decisions the rules already make

- A server that silently ignores a knob (HTTP 200, the knob had no effect)
  raises client-side (MAP-8): `"reject"` for that knob, per model when only
  some models ignore it. A server that refuses loudly needs nothing.
- A setting with an obvious nearest value is adapted and recorded (MAP-13):
  the lowest effort level for an "off" a model cannot honour, a clamp for an
  effort word the server lacks.
- A per-model rule names exact model ids as prefixes, measured; an unmeasured
  sibling gets the host default until a receipt adds it. State that the
  table rots.
- One provider string, one wire: the same service on a second wire is a
  second row (`moonshotai-anthropic`), never a mode of the first.
- Anything these do not settle is a design pass (`design-pass.md`) with the
  options written down before the maintainer is asked.
