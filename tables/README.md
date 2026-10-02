# tables/ — the reference's provider tables, published as data

`providers.json` is the output of the reference shim's `provider_tables` op
(`harness/PROTOCOL.md`), written by `tools/export_provider_tables.py`.
`tools/audit.py` fails when the file and the reference differ, value for
value and member order for member order.

**What it is for.** `playbooks/port.md` rule 2: tables are data, copied,
never re-derived. Ports generate their registry, access-policy,
compat-preset, router and service-label tables from this file, at their
`CONTRACT_PIN`, so a port's tables are exactly the reference's at the
contract commit it names, and its CI can prove the generated code is
current. Change entry: `changes/2026-10-02-router-tables-pinned.md`.

**What it is not.** Not an oracle. The corpus (`cases/`, `bodies/`,
`errors/`, `serde/`, `router/`, `auth/`) decides behavior; this file only
carries the reference's tables to the ports without hand copying. A table
value with no case behind it is still unpinned behavior; adding a case is
how it becomes a fact (`playbooks/provider.md`).

## Shape (`schema: 1`)

| Key | Content |
|---|---|
| `providers` | registry rows in declaration order (presentation order): `id`, `dialect`, `kind` (`adapter-owned` \| `bound` \| `hosted`), `compat` (a preset name, a compat object, or null), `access` (the whole access policy), `aliases`, `placeholder_key`, `console_url`, `note` |
| `declared_login` | the managed-login declared providers (`kimi-code`, `github-copilot`; AUTH-26: no registry row), same row shape |
| `compat.chat`, `compat.responses`, `compat.anthropic` | preset name → the knobs it sets |
| `compat.*_base_urls` | preset name → the server root the preset supplies |
| `compat.preset_aliases` | input spelling → preset name, after the key rule below |
| `routing.default_rules` | the router's built-in prefix rules, in match order: `prefix`, `provider`, `note` |
| `routing.litellm_prefixes` | litellm's `provider/` spelling → lm15 provider, for the OpenAI-SDK/litellm door |
| `login.service_labels` | provider → the AUTH-12 service label |

Value rules, so a generator never guesses:

- A compat object lists only the knobs it sets: an absent knob inherits.
  `model_overrides` is `[prefix, {knob: value}]` pairs in match order.
- An access policy, its `host` and its `supports` are written whole, every
  field, so a port never depends on its own defaults matching these.
- Arrays keep the reference's order; objects keep its member order;
  `supports.extra` is sorted. Field names are the reference's snake_case; a
  generator renames them to the language's casing.
- Preset keys: a preset name is looked up after lowercasing and replacing
  `-`, `.` and spaces with `_`, then through `preset_aliases`
  (`bedrock-mantle` → `bedrock_mantle`).
- `xai` is adapter-owned with `compat: null`: its class binds the `xai`
  chat preset itself (`lm15/providers/xai.py`). Ports that model it as a
  row with a preset do so in their adapter code, not from this file.

## The port rule

A generated file starts with a "generated from lm15-contract
tables/providers.json — do not edit" line and is produced by the port's
`tools/gen_tables.py`. The port's CI runs `tools/gen_tables.py --check`
against the contract checkout at `CONTRACT_PIN` and fails when the
committed file is stale. A port fixes a table by changing the reference
and re-exporting here, never by editing generated code.

| Port | Generated file | Generator |
|---|---|---|
| TypeScript | `src/generated/tables.ts` | `tools/gen_tables.py` |
| Rust | `src/generated/tables.rs` | `tools/gen_tables.py` |
| Go | `tables_generated.go` | `tools/gen_tables.py` |
| Julia | `src/data/*.json` | `tools/import_tables.py` (imports the reference directly; moving it to this file is follow-up work) |
| R | `R/provider-data.R` | `tools/copy-provider-tables.py` (parses the reference directly; likewise) |
