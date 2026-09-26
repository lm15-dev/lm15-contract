# 2026-09-26 — Four open-model hosts: DeepInfra, Together AI, Fireworks AI, Parasail

Status: RATIFIED 2026-09-26 (§ Ratification).  Wire facts are live receipts.
Provider pathway: `changes/2026-09-03-provider-registry.md`.  Dossiers:
`research/providers/{deepinfra,together,fireworks,parasail}/README.md`.

## Why

The maintainer asked for the four as built-in providers.  Hand-declared
through `RouterConfig(providers=...)` with the dialect's default policy they
already answered text, streams and tools, but three things were wrong for a
user and invisible: the default `thinking_replay="as_text"` pasted a model's
reasoning into the visible text of the next turn; Together's model listing
returned zero models with no error; Together's cached-token count read as
"not reported".  Measuring the four also turned up silent server behaviour
the presets must answer for.

## Registry and presets (lm15-python)

- `registry.py`, `access.py`: `deepinfra`, `together`, `fireworks`,
  `parasail` — chat-bound entries, bearer key, the provider's own documented
  env variable, surfaces complete/stream/models.
- `compat.py`: one policy for the four — `thinking_format="reasoning_effort"`,
  `thinking_replay="native"`, `max_completion_tokens`, stream usage on,
  `cache_control="none"` — plus the per-model rules below.  Base URLs are the
  documented OpenAI-compatible roots.
- `router.py`: litellm prefixes `deepinfra/`, `together_ai/`, `fireworks_ai/`,
  `parasail/`.

## Why one policy fits the four

| knob | receipt | decision |
|---|---|---|
| effort | all four honour top-level `reasoning_effort`; Fireworks answers 400 "Extra inputs" to the `reasoning` object (`probe-shape-reasoning-*`) | `reasoning_effort`, not the OpenRouter shape |
| replay | a code word planted in a replayed trace, three tries per field (`probe-replay-field-*`): recalled through `reasoning_content` on all four (DeepInfra 1/3, Together 2/3, Fireworks 3/3, Parasail 2/3), never with no trace (0/3 everywhere); the `reasoning` field is 400 on Fireworks | `thinking_replay="native"` (`reasoning_content`) |
| cap | `max_completion_tokens: 8` → `finish_reason: length` on all four (`probe-max-tokens-cap`) | `max_completion_tokens` |
| stream usage | usage on the final chunk on all four (`streaming` cases) | include |
| caching | automatic everywhere; no host takes the key/retention pair in this dialect's shape | `cache_control="none"`: a key or long retention is dropped with a record |

## Per-model rules, each pinned by a consumer-side case

| rule | receipt | follows | pin |
|---|---|---|---|
| DeepInfra sends a forced tool choice only to 14 receipted models, refuses it elsewhere | survey of 24 models (`research/providers/deepinfra/tool_choice_survey.py`, `receipts/2026-09-26-deepinfra/survey-tool-choice.json`): required twice, named, none, and an unprompted-call control. Honour all: DeepSeek V3.2, V4-Flash, V4.1-Flash, GLM-5.3-Flash, Kimi-K2.6, Llama-4-Scout, Qwen3.6-27B, Qwen3-Next-80B, Nemotron-3.5-Lightning, granite-4.2-8b, MiMo-V2.6-Flash, Hy3, gemini-3.1-flash-lite, claude-haiku-4-5. Ignore: Llama 3.3, Qwen3-235B-2507, Qwen3-Coder-480B, Qwen3-30B/14B, Mistral-Small-3.2, gemma-4-26B, gpt-oss. Qwen3.8-Flash: 500. MiniMax-M2.7, GLM-4.7, Seed-2.0-mini: `none` ignored. Llama 3.1 8B: calls unprompted (no evidence either way) | MAP-8 (a silent cell raises), as Z.AI | `deepinfra.tool_choice_required`, `deepinfra.tool_choice_required_deepseek`, `deepinfra.tool_choice_required_glm` |
| Together refuses a forced tool choice on gpt-oss | HTTP 500 every time (`probe-tool-choice-required-reasoner`); a 500 is retryable | MAP-8 | `together.tool_choice_required_gpt_oss` |
| Together clamps gpt-oss effort to low\|medium\|high | xhigh, max and `bogus` all accepted and run at the default (medium) — `max` got fewer reasoning tokens than `high` | MAP-13, as Moonshot kimi-k3 | `together.reasoning_effort_max_gpt_oss` |
| reasoning off → the lowest level, recorded (Together gpt-oss and GLM-5.3, DeepInfra gpt-oss) | Together gpt-oss accepts `none`, hides the trace, bills ~60 reasoning tokens; Together GLM-5.3 ignores it; DeepInfra gpt-oss runs it as low | MAP-13 decision 2026-09-14 §4.2 (xAI's rule: no off switch → lowest level, recorded) | `together.reasoning_off_gpt_oss`, `together.reasoning_off_glm`, `deepinfra.reasoning_off_gpt_oss` |

Fireworks and Parasail refuse `none` loudly where a model cannot stop
reasoning (gpt-oss, GLM-5.3): MAP-5 is met by the server and nothing is
added.

New compat knob for the fourth rule: `OpenAIChatCompat.reasoning_off`,
`"send"` (default) or `"lowest"`, keyword-only, overridable per model.
"lowest" sends `reasoning_efforts[0]`, else `"low"`, and records
`config.reasoning.effort: substituted`.  It is the xAI adapter's rule made
data, so a chat preset can carry it per model family.

## Live cases (receipts/2026-09-26-<host>/)

Each host: `basic_text`, `streaming`, `reasoning_low`, `reasoning_off`
(DeepSeek V4.1; none for Parasail, whose documented thinking switches are
per-model `chat_template_kwargs`, and whose gpt-oss refuses `none` loudly), `tools`,
`streaming_tool_call`, `multi_turn_tool_result` (the model's own turn
replayed with `reasoning_content`), `response_format_json_schema` (every
reply had exactly the schema's keys), `system_prompt` (with the
`leading_developer_as_system` ingest block), `user_id`, `models`.  Plus
`fireworks.tool_result_image`, `parasail.tool_result_image` and
`deepinfra.tool_result_image_raise` from the tool-result matrix
(`receipts/2026-09-26-tool-result-media/`).  Goldens are scribe drafts.
Error envelopes: `errors/cases/{deepinfra,together,fireworks,parasail}.json`.

## Dialect and harness changes

- **Bare-array catalogs.**  Together's `GET /models` is a JSON array.  The
  chat adapter read `data` only and returned `()` without an error.  It now
  reads `{"data": [...]}` or an array, and anything else is a malformed reply
  (`ProviderError`), never an empty catalog.  Harness: a models case's
  `entries_key: null` means the body is the array (`harness/check.py
  models_entries`, `fake_shim.py`, PROTOCOL.md § parse_models_response).
  The capture tool writes `entries_key` from the body and now records the
  exchange receipt on models cases (it never had; `check_provenance.py` D11
  flagged the four new ones).
- **Flat cached tokens.**  Together's non-reasoning models report
  `usage.cached_tokens` with no `prompt_tokens_details`.
  `cache_read_tokens` reads the nested count first, then the flat one.
  Pinned by `together.basic_text` (golden `cache_read_tokens: 0`).
- **MAP-15 form.**  Parasail's "no such model" is 404 `invalid_request_error`
  "Deployment <id> doesn't exist or isn't accessible." — no word "model" for
  the marker test.  Pinned as a form in `spec/model-not-found.json`.
- **Error bodies that are not JSON.**  Parasail's 401 is plain text under a
  JSON content-type; `parasail.unauthenticated` carries it as a string body
  (the error direction already accepted one; the capture tool's fold did not).

## Corpus bookkeeping

`spec/support-matrix.json` (four rows); `auth/resolution.json`
`<host>-env-selected` ×4 (mirrored to lm15-python/conformance);
`auth/managed/runs/core.json` discovery list (+4 providers);
`tools/check_secrecy.py` key shapes for Together (`tgp_v1_`), Fireworks
(`fw_`), Parasail (`psk-`) — DeepInfra keys have no prefix, so its captures
were searched for the literal key before commit instead;
`tools/check_content_coverage.py`: fireworks and parasail are images-only,
together is OPEN (credit limit during the pass); scrapes and frozen terms for
the four; capture scripts `research/providers/<host>/capture.py` over the
shared `_inference_hosts.py`; pins by `_inference_hosts_pins.py`.

## Terms

Allowed with the user's own key on all four.  Parasail § 2.2(h) forbids
publicly disclosing performance information, and Together, DeepInfra and
Fireworks forbid benchmarking or competitive analysis: this pass records wire
shapes only, and the tool-result runner's per-request `latency_s` was removed
from its receipts for these four.

## Stated trade-offs

- **DeepInfra allow-list.**  A forced tool call goes only to the 14
  receipted models; every other model, including ones never measured, is
  refused.  The list is exact model ids used as prefixes, so a suffixed
  variant (`-0731`, `-Turbo`) inherits its entry, but a sibling does not:
  DeepSeek V4-Pro, allowed by the first draft's `DeepSeek-V4` prefix, is
  refused until measured.  MiniMax M2.7 and Seed 2.0 honour `required` but
  not `none`; they sit with the refused, so `none` is done client-side
  (tools not sent, recorded) and `required` raises.  A user who knows better
  keeps the preset and sets `forced_tool_choice="send"` on a copy.
- **Model-name knowledge in presets.**  The Together and DeepInfra rules name
  model families (`openai/gpt-oss`, `zai-org/GLM-5.3`, `deepseek-ai/DeepSeek-V4`).
  They rot when hosts add families; a new family gets the host default until a
  receipt adds it.  Bedrock's preset set this precedent (2026-09-03).
- **Caching.**  DeepInfra documents retention (`prompt_cache_options.ttl`
  5m|1h, breakpoints); lm15 drops `retention="long"` with a record rather
  than map it without a design pass.
- **Together gpt-oss tool loops** stay broken (server side); not worked
  around, documented for users.

## For the ports (TypeScript, Go, Rust, Julia, R)

Done in TypeScript (`56dba9a`), Go (`2bb9f95`) and Rust (`9105daf`), each at
1,788 of 1,788 (playbooks/parity.md); Julia and R not yet.

1. The four registry entries, access policies, compat presets (with
   `model_overrides`), base URLs, litellm prefixes.
2. The compat knob `reasoning_off` ("send" | "lowest"), overridable, applied
   before the effort is written.
3. Chat `list_models`: bare array or `data`, else a malformed-reply error.
4. Chat usage: flat `cached_tokens` fallback.
5. The Parasail MAP-15 form in the model-not-found table.

The harness then pins all of it: 54 new cases (43 live captures, 8
consumer-side pins, 3 from the tool-result matrix), 11 error envelopes, 4
auth cases, and the discovery list.

## Ratification

**RATIFIED 2026-09-26.**  Two decisions were put to the maintainer, each with
options and a recommendation; he answered "yes, 1 c, 2 c".

1. **Reasoning off on a model that cannot stop reasoning, on a server that
   accepts `none` and reasons anyway** — option C: send the lowest level and
   record the substitution (MAP-13 §4.2, the rule already binding for xAI),
   carried by the new compat knob `OpenAIChatCompat.reasoning_off`
   ("send" | "lowest", overridable per model).  Rejected: A, send `none`
   (a paid, silent no-op); B, refuse (every caller that says "off" would
   special-case these models).
2. **Forced tool choice on DeepInfra** — option C: send it to the 14 models
   the survey showed honour it, refuse it everywhere else.  Rejected: A, the
   first draft (refuse all but DeepSeek V4, which the survey showed would
   refuse 13 working models); B, send everywhere (silent on at least 9).
   The survey was run after the first draft and before the decision.

Everything else in this entry follows already-ratified rules with receipts.

Ratified-by: Maxime Rivest, 2026-09-26 (in session)
