# Tinker (Thinking Machines) — provider dossier

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-11-09 | maintainer request: Quiver (bigspin) needs to call models trained with FunctAI's Tinker trainer; the lm15 intent record of 2026-08-31 already asks for inference on Thinking Machines fine-tunes |
| researched | 2026-11-09 | this dossier; `scrapes/tinker/pages/` (18 pages + the two price tables); `sources/` (terms) |
| surveyed | 2026-11-09 | `receipts/2026-11-09-tinker-survey/` (survey kit, `reasoning_survey.py`, `anthropic_survey.py`, `chat_extra_probes.py`); `SURVEY.md` |
| implemented | 2026-11-09 | `lm15.registry.PROVIDERS["tinker"]`, `["tinker-anthropic"]`, `lm15.access.TINKER*`, compat presets `tinker` (chat and Messages) |
| offline-conformant | 2026-11-09 | support-matrix rows; auth cases `tinker-env-selected`, `tinker-anthropic-env-selected`; tables exported; router cases; Python green at the harness |
| live-verified | 2026-11-09 | `receipts/2026-11-09-tinker/` (36 cases), error envelopes, `changes/2026-11-09-tinker-live.md` |
| supported | — | the change entry ratified |

## Identity

- Service: Tinker, Thinking Machines' training API. It also serves inference on base models and
  on the user's own checkpoints through two compatible doors (both "Beta").
- Doors (same key, same models):
  - OpenAI Chat Completions: `https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1`
    (`/chat/completions`, `/completions`, `/models`). Bearer auth.
    (`compatible-apis--openai.md`)
  - Anthropic Messages: `https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api`
    (`/v1/messages`, `/v1/messages/count_tokens`). `x-api-key` or Bearer.
    (`compatible-apis--anthropic.md`)
- Env key: `TINKER_API_KEY` (models.dev, OpenCode and the SDK all read it). Console:
  https://tinker.thinkingmachines.ai/keys.
- models.dev lists it as provider `thinkingmachines`, bound to the **Anthropic** door, with prices
  for 36 model ids (checked 2026-11-09: every listed price equals Tinker's own table; models.dev
  lacks the two newest models, `Inkling-2-Small` and `Kimi-K3.1-Pro`).
- Out of lm15's scope, and why:
  - training, checkpoint management (TTL, delete, publish, download): lm15 does no training
    (intent, 2026-08-31); FunctAI owns it;
  - the native `SamplingClient` (token ids in, token ids out, futures polled over Tinker's own
    protocol): it takes rendered tokens, not messages, so it is not a model call in lm15's sense;
  - the org billing API (`/api/v1/billing/usage/events`): hourly, lags hours, needs billing
    access. Useful to a platform reconciling spend (Quiver), not per call.

## Model names (the routing problem)

Three forms, all valid on both doors (Anthropic page; for the OpenAI door, `opencode.md` uses a
base model, `moonshotai/Kimi-K2.6`, and the OpenAI page a checkpoint):

| Form | Example | Notes |
|---|---|---|
| base model | `Qwen/Qwen3-8B`, `thinkingmachines/Inkling` | `/` inside; many hosts serve the same name, so no bare-name rule |
| base model variant | `thinkingmachines/Inkling:peft:262144:sampling-nvfp4` | colons inside; `:peft:N` = long context, `:sampling-nvfp4` = the serverless, cheaper copy |
| user checkpoint | `tinker://<run-uuid>:train:0/sampler_weights/<name>` | a URI: scheme, colons, slashes |

lm15's router splits a model string at its **first colon** (router rung 1). With a `tinker`
provider registered, the bare checkpoint string `tinker://…` would route to Tinker and send
`//…:train:0/…` as the model: a broken request. `tinker:tinker://…` works today. Fix options are
in "Decisions" below.

## Read-only probes, 2026-11-09 (no sampling, nothing billed)

Run with the maintainer's key; raw bodies kept out of the corpus because they carry the account's
organisation-user id.

| Request | Result |
|---|---|
| `GET …/oai/api/v1/models` | 200. Lists the account's **sampler checkpoints only** (not base models), each with `id` (the `tinker://` path), `owned_by`, `created`, and a non-standard **`base_model`** (`"Qwen/Qwen3.5-4B"`) |
| `GET …/anthropic/api/v1/models` | 404 `{"detail":"Not Found"}`: the Anthropic door has no catalog |
| `GET …/oai/api/v1/models`, wrong key | 401 `{"detail":"Unable to validate api-key"}` (FastAPI envelope; MAP-18 bad-key form) |
| `GET …/api/v1/get_server_capabilities` (SDK REST, `X-API-Key`) | 200. 38 models with `max_context_length`, `trainable`, `sampleable`; the `sampling-nvfp4` ids are sampleable only |
| `GET …/api/v1/checkpoints?limit=5` (SDK REST) | 200. Each checkpoint carries `base_model`, `checkpoint_type` (`sampler` / `training`), `size_bytes`, `expires_at` |
| `POST …/api/v1/weights_info {"tinker_path"}` (SDK REST) | not called; documented to return `base_model`, `is_lora`, `lora_rank` for any path, including published checkpoints of other users |

## Price facts

- Sampling is billed per token in three buckets: prefill, **cached prefill** (automatic prompt
  cache, discounted, about 20% of prefill; 10% on Inkling 2 Small), and sample (output)
  (`models-and-pricing.md`, "Pricing Terms"). There is no cache-write charge: a write is billed as
  plain prefill. aimo should add `thinkingmachines` to `_WRITES_BILLED_AS_INPUT`.
- A checkpoint is billed **at its base model's rates**: billing events carry `base_model` and no
  checkpoint id (`types--billingusageevent.md`); `:peft:` long-context variants cost the same as
  the base for sampling ("Extended context costs more for training only").
- The serverless copies (`…:sampling-nvfp4`) have their own, lower prices (`serverless.json`).
- Prices are published as JSON, "the stable interface for scripts": `models.json` (prefill,
  cached_prefill, sample, train) and `serverless.json` (input, cached_input, output).
- Checkpoint storage ($0.10 per GB-month) is not a per-call cost.

What this means for lm15's cost estimate (MAP-19, exact or unknown):

1. For a checkpoint, the price lookup needs its base model. The `/models` catalog gives it.
   lm15 already has the slot: `ModelOrigin(type="fine-tune", base_model=…)`. Today
   `model_infos_from_entries` writes every entry as `type="provider"` and leaves `base_model` in
   `provider_data`.
2. The estimate is exact only if the reply counts cached tokens, because cached prefill has its
   own rate (`InferencePricing.estimate` returns None when the cache count is unknown and the rates
   differ). The Anthropic door documents `cache_read_input_tokens` as **always null**: through it,
   cost is unknown on every call. Whether the OpenAI door reports
   `prompt_tokens_details.cached_tokens` is unknown (survey item 1).

## Rendering facts (silent quality risk)

- OpenAI door, `/chat/completions`: "the server renders them with the model's default Hugging Face
  chat template". The docs tell users whose checkpoint expects another renderer to use the native
  sampler instead.
- Anthropic door: "no rendering code" for Inkling; `count_tokens` uses "the model's real tokenizer
  and renderer". It is unclear whether this is the same template as the OpenAI door (survey item 4).
- FunctAI trains on the model's published Hugging Face chat template (`design/21`, "Rendering"),
  the one the OpenAI door uses. The **template options** must match too: FunctAI trains Qwen with
  `enable_thinking=False` and Inkling with `reasoning_effort=0.0`. The doors default to thinking
  (OpenAI door: `reasoning_effort` defaults to 0.9, `separate_reasoning` true). A FunctAI model
  called through lm15 with no reasoning setting would therefore get a prompt unlike its training
  prompts, and no error.

## Reasoning knobs

| Door | Wire | Values | Off |
|---|---|---|---|
| OpenAI | `reasoning_effort` | `none` `minimal` `low` `medium` `high` `xhigh` (mapped to 0.0, 0.1, 0.2, 0.7, 0.9, 0.99) or a float in [0, 0.99] | `none` |
| OpenAI | `separate_reasoning` (non-standard, default true since June 2026) | reasoning in `reasoning_content` | — |
| Anthropic | `output_config.effort` | `low` `medium` `high` `xhigh` `max` (= xhigh) | `thinking: {"type": "disabled"}` |

Both doors return 400 for a model without effort support. Anthropic `thinking.budget_tokens` is
accepted and ignored; thinking `signature` is an empty string.

## Feature matrix (documented; ? = survey)

| Feature | OpenAI door | Anthropic door |
|---|---|---|
| text, system, multi-turn, stream | yes | yes |
| tools, tool results | ? | yes; `tool_choice` auto/any/named/none |
| structured output (json_schema) | ? | not documented |
| images in | ? | yes, base64 or url |
| images in tool results | ? | ? |
| audio in | no (Inkling audio is native-sampler only) | no ("not part of the Messages API schema") |
| prompt-cache usage counts | ? | always null |
| explicit cache control | — | `cache_control` ignored |
| citations | — | no |
| logprobs | ? | no |
| model catalog | yes, checkpoints only, with `base_model` | 404 |
| token counting | — | `count_tokens` |
| raw completion (`/completions`) | yes (lm15 has no surface for it) | — |

## Terms-of-service verdict

Source: `sources/thinkingmachines-terms.md` (last updated January 10, 2026).

- § 1(d): Hosted and fine-tuned models may be used "for your lawful purposes, including lawful
  commercial or production purposes"; some hosted models are beta.
- § 1(e): no use "for benchmarking or competitive analysis of the Service".
- § 3(c): Customer Content (prompts, outputs, datasets) is not used to train or improve their
  technology and is not shared for that purpose.
- § 3(d): diagnostic and usage data belongs to Thinking Machines.

**Verdict: allowed, API key only, for the key holder's own purposes.** Because of § 1(e) the
receipts record wire shapes only (as for Parasail § 2.2(h)): no latency, throughput or quality
comparison is recorded as a finding.

## Survey results (2026-11-09)

Every question below was answered by the survey; the answers and the
decisions taken from them are in `changes/2026-11-09-tinker-live.md` § What
was measured. In short: (1) the chat door counts cached tokens, and so does
the Messages door despite its docs; (2) tools, forced tool choice (checked
after sampling, 422 when unmet), images, tool-result images, reasoning per
family, replay through `reasoning_content`; `response_format` and
`output_config.format` are ignored; (3) the reply's `model` is the
checkpoint path; (4) both doors count the same prompt tokens; (5)
`chat_template_kwargs.enable_thinking` is accepted and IGNORED (the switch is
`reasoning_effort: false`); (6) error envelopes in `errors/cases/tinker*.json`.

## Survey plan as written before the survey

1. OpenAI door: does usage carry `prompt_tokens_details.cached_tokens`? (send one long prompt twice)
2. Both doors on a checkpoint and on a base model: text, stream (usage on the last chunk?), tools,
   forced tool choice, json_schema, image in, image in a tool result, reasoning words and off,
   reasoning replay (does `reasoning_content` sent back help?).
3. What does `model` in the reply hold for a checkpoint: the path or the base model?
4. Same prompt through both doors to `count_tokens` / reply usage: same template, same token count?
5. Chat-template options on the OpenAI door: is `chat_template_kwargs` (`enable_thinking`)
   accepted, like vLLM?
6. Error envelopes: unknown checkpoint, malformed path, a training (not sampler) checkpoint, an
   expired or deleted checkpoint, effort on a non-reasoning model, over-long prompt (MAP-15/18).

## Decisions for the maintainer (approved 2026-11-09: "i approve all that you recommended")

1. **The `tinker://` name.** Options: (a) users write `tinker:tinker://…` (no change, easy to get
   wrong); (b) a general router rule: a model string whose first colon begins `://` is a URI,
   never `provider:model`, plus a data rule routing the `tinker://` scheme to Tinker. (b) is
   proposed: it is one general rule in all SDKs, and it keeps the string Tinker's own docs,
   console and SDK print working when pasted.
2. **Ids and doors.** Proposed: `tinker` (OpenAI Chat door: the only one with a catalog and the
   only one that may count cached tokens) and `tinker-anthropic` (Messages door), with alias
   `thinkingmachines` (models.dev's id) on `tinker-anthropic` or on both. This follows the
   existing pairs (`deepseek`/`deepseek-anthropic`, `moonshotai`/`moonshotai-anthropic`). Which
   door is the default depends on survey items 1, 2 and 4.
3. **Fine-tune origin in catalogs.** A general rule: a catalog entry that names its `base_model`
   becomes `ModelOrigin(type="fine-tune", base_model=…)`. It is data, applies to any host that
   reports a base model, and lets a catalog price a checkpoint at its base model's rates where the
   provider documents that billing (Tinker does).
4. **Where checkpoint prices come from.** lm15 keeps no prices. aimo (the catalog package) can
   read Tinker's `models.json` / `serverless.json` directly (fresher than models.dev) and mark that
   Tinker checkpoints are billed at base rates.
