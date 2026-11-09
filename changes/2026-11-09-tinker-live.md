# 2026-11-09 — Tinker (Thinking Machines): two doors, checkpoints by path, the reasoning switch per family

Status: DECIDED IN SESSION 2026-11-09, TO RATIFY. The maintainer approved the
study's recommendations ("i approve all that you recommended … support tinker
fully and most excellently"): the URI naming rule, the ids `tinker` and
`tinker-anthropic` with the alias `thinkingmachines`, the catalog's fine-tune
origin, Tinker's own price tables in the catalog package, and the survey spend.
The decisions the study did not foresee are listed under § Decisions with
their options; each follows the expert reading stated there and waits for
ratification. Dossier: `research/providers/tinker/README.md`; survey report
`research/providers/tinker/SURVEY.md`.

## Why

Quiver (bigspin) wanted to call models trained with FunctAI's Tinker trainer
and found no Tinker in lm15's table; the lm15 intent record of 2026-08-31
already asks for inference on Thinking Machines fine-tunes. Tinker trains
models and also answers chat requests for its base models and for any sampler
checkpoint, by its path, through an OpenAI-compatible door and an
Anthropic-compatible door (both "beta"). Training stays out of lm15 (FunctAI
owns it).

## What was measured (receipts)

| Evidence | What it shows |
|---|---|
| `receipts/2026-11-09-tinker-survey/probe-reasoning-*` (`reasoning_survey.py`: 23 models × 12 values on the chat door, × 10 on the Messages door, and three checkpoints) | `reasoning_effort` is answered **per base family**, loudly: Inkling takes `none`…`max` and floats; Qwen 3/3.5/3.6, Kimi K2.6, Nemotron 3/3.5 take `true`/`false` only; Qwen 3.8 and DeepSeek V4.1 take some words and `true`/`false`; gpt-oss, Kimi K3.1, GLM 5.3 take some words and have no off. Every model reasons by default. A checkpoint answers as its base ("resolved base 'Qwen/Qwen3.5-4B'"). On the Messages door the switch families refuse `thinking: disabled` and every effort word |
| survey kit (`survey.py run/sweep`, 614 receipts) | developer role 422; `max_completion_tokens` honoured; usage on the last stream chunk; replay through `reasoning_content` 3/3, `reasoning` 0/3; `response_format` json_schema **and** json_object ignored (200, free text) on every family; a forced tool choice is checked after sampling (422 "model returned no tool call…"), never ignored; cached tokens counted (512 on a repeat) |
| `chat_extra_probes.py`, `anthropic_survey.py` | the stop sequence is returned in the text on both doors; `parallel_tool_calls: false` and `disable_parallel_tool_use` honoured; `n: 2` silently returns one choice (lm15 has no `n`); logprobs returned; Messages door: `output_config.format` ignored, `cache_control` ignored, usage counts cache reads and reports the uncached prompt as `cache_creation_input_tokens`, unsigned thinking replays 3/3 |
| `receipts/2026-11-09-tool-result-media/` | images in tool results received on both doors; a PDF is a 422 (chat) and accepted-but-not-received (Messages) |
| `receipts/2026-11-09-tinker/` (capture.py, 21 chat + 15 Messages cases) | every case below, built by lm15's adapters, HTTP 200 |
| prompt-token counts vs the published Qwen3.5-4B template | the chat door with `reasoning_effort: false` renders exactly `enable_thinking=False` (27/15 tokens), absent or `true` renders `enable_thinking=True` (25/13) |

Terms (`research/providers/tinker/sources/thinkingmachines-terms.md`, § 1(e)
no benchmarking): receipts record wire shapes only, no latency.

## Registry and presets (lm15-python)

- `tinker` — Chat Completions, bearer `TINKER_API_KEY`, base
  `https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1`,
  complete/stream/models; alias `thinkingmachines`.
- `tinker-anthropic` — Messages, `x-api-key` (bearer also accepted), base
  `…/anthropic/api/v1`, complete/stream (its `/models` is a 404).
- Chat preset: system role, `max_completion_tokens`, stream usage,
  `thinking_format="reasoning_effort"` with `reasoning_off="switch"` (host
  default), `thinking_replay="native"`, `json_schema="none"`,
  `cache_control="none"`, `tool_result_media="images"`,
  `stop_in_text="included"`; `model_overrides`: `thinkingmachines/` →
  `reasoning_off="send"`; `Qwen/Qwen3-`, `Qwen/Qwen3.5-`, `Qwen/Qwen3.6-`,
  `moonshotai/Kimi-K2`, `nvidia/NVIDIA-Nemotron-3` →
  `thinking_format="reasoning_effort_switch"`.
- Messages preset: `thinking_format="effort"`, `thinking_replay="unsigned"`,
  `cache_control="none"`, `structured_output="reject"`,
  `parallel_tool_calls="send"`, `tool_result_media="images"`,
  `stop_in_text="included"`.

## New behaviour every SDK carries

1. **A URI is one name** (router rung 1, its hint, and the adapter's own
   prefix strip): `scheme://…` is never `provider:model`. Rule
   `tinker://` → `tinker`. Router cases `rule-tinker-checkpoint-uri`,
   `rule-boundary-tinker-uri`, `prefix-tinker-explicit-uri`,
   `prefix-tinker-anthropic-uri`, `uri-never-a-prefix`.
2. **Registry aliases route** (`registry-alias-thinkingmachines`,
   `openai-chat-litellm-registry-alias`); a declared provider may not take
   one.
3. **`RouterConfig(base_models=…)` and the chat adapter's `base_models`**:
   `model_overrides` match the model id, then its base model. PROTOCOL.md
   `base_models`; case `tinker.checkpoint_base_model`.
4. **Chat compat values**: `thinking_format="reasoning_effort_switch"` (off
   → `false`; an effort word → `true`, recorded `config.reasoning.effort`
   substituted, applied `"on"`); `reasoning_off="switch"` (off → `false`
   under `reasoning_effort`); `json_schema="none"` (either response_format
   type dropped and recorded). Ingest reads `false` back as off and refuses
   `true` (no level). Cases `tinker.reasoning_off_switch`,
   `tinker.reasoning_effort_switch`, `tinker.reasoning_off_words`,
   `tinker.checkpoint`, `tinker.response_format_json_schema`.
5. **MAP-21** — `{"detail": …}` error bodies carry the message
   (`errors/cases/tinker*.json`, messages pinned).
6. **MAP-15** — forms may name `code: null`; four Tinker forms.
7. **MAP-22** — `stop_in_text` on chat and Messages compat; the cut in
   `parse_response` and the stream reader (`*.stop_sequence`,
   `*.streaming_stop_sequence`).
8. **MAP-23** — a catalog entry naming `base_model` is a fine-tune
   (`tinker.models`).

## Decisions

1. **How a checkpoint learns its family.** Its name does not say; the
   server answers per family. Options: (a) the adapter asks Tinker
   (`/api/v1/weights_info` or `/models`) — hidden I/O and hidden state in a
   library whose adapters are pure build/parse, rejected; (b) the catalog
   (`ModelRegistry`) changes the wire — `docs/model-hydration.md` says
   hydrated data never changes what `build_request` produces, rejected;
   (c) retry on the 400 with the value its message names — hidden retries,
   control flow from error text, rejected; (d) **the caller declares it,
   `RouterConfig(base_models=…)`, fed from the provider's own catalog
   (MAP-23) or from what the caller trained** — taken. Trade-off: a
   `RouterConfig` is frozen; an application that learns new checkpoints at
   run time builds a new router (cheap: LMs are built lazily) or passes
   `base_models` to the adapter it builds.
2. **The default for a checkpoint whose base is not named.** Options:
   Tinker's documented spelling (words, off `none`: only Inkling's family
   turns off) or **the spelling most families take (words verbatim, off
   `false`: Qwen 3/3.5/3.6/3.8, Kimi K2.6, Nemotron, DeepSeek V4.1)** —
   taken, because off is the setting a fine-tune most needs (FunctAI trains
   Qwen without thinking) and Qwen is most of the catalog. Trade-off: an
   unnamed Inkling checkpoint cannot turn thinking off (Tinker's 400 names
   the base and the accepted values), and an effort word on an unnamed
   Qwen checkpoint is refused the same way, where a named one would be
   adapted to "on".
3. **An effort word on an on/off model.** Options: refuse; send it and let
   Tinker refuse (400); **send `true` and record the substitution (MAP-13:
   the nearest value to a level is "on")** — taken.
4. **`response_format`.** Tinker ignores both types silently. Options:
   refuse; **drop with a record (`json_schema="none"`, as Z.AI's
   `reject` drops json_schema)** — taken; the existing `reject` would have
   sent json_object to be ignored.
5. **The stop sequence in the text.** Options: leave it (a silent semantic
   difference from every other provider); refuse `stop` (the server does
   stop, so the feature works); **cut it (MAP-22), keep sending it** —
   taken; idempotent if Tinker fixes the bug.
6. **`thinkingmachines` names the chat door**, though models.dev binds its
   `thinkingmachines` provider to the Messages door: the chat door is the
   one with a catalog, every reasoning switch and the cached-token count.
7. **The Messages door's reasoning on switch families** is left loud: both
   off and effort words are Tinker 400s there. lm15 does not add
   per-model rules to `AnthropicCompat` for a server bug; the docs say
   "use `tinker`".

## Stated trade-offs and gaps

- **Context-length errors on the chat door** are `InvalidRequestError`, not
  `ContextLengthError`: the chat dialect classifies them by code only and
  Tinker sends none; the Messages door's message rule catches the same
  text. A pinned context-length form table (like MAP-15's) would close it;
  not done here.
- **A forced tool choice the model did not follow** is a 422,
  `InvalidRequestError`, not retryable by class, though a new sample may
  succeed.
- **The family table rots** as Tinker adds models; a new family gets the
  host default until a receipt adds it.
- **Pricing is the catalog's** (lm15 keeps no prices): aimo reads Tinker's
  own `models.json`/`serverless.json`, bills a cache write at the input rate,
  and prices a checkpoint at its base model's rates.
- **Checkpoints for the captures** live on the maintainer's Tinker account
  (three untrained LoRA, ~0.37 GB, about $0.04 a month, no expiry); the
  first survey's FunctAI checkpoint was deleted during the run.
- **Beta.** Tinker calls both doors beta; production throughput is a
  waitlist.

## For the ports (TypeScript, Go, Rust, Julia, R)

Tables (`tools/gen_tables.py`, `import_tables.py`,
`copy-provider-tables.py`) carry the presets, aliases, rule and base URLs.
By hand: items 1–8 above. Then the harness at the pin and a row in
`playbooks/parity.md`.
