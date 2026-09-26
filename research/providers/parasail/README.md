# Parasail — provider dossier

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-26 | maintainer request (key added with credit) |
| researched | 2026-09-26 | this dossier; `scrapes/parasail/pages/` (17 pages); `sources/` (terms) |
| implemented | 2026-09-26 | `lm15.registry.PROVIDERS["parasail"]`, `lm15.access.PARASAIL`, compat preset `parasail` |
| offline-conformant | 2026-09-26 | auth case `parasail-env-selected`; support matrix row; `tests/test_inference_hosts.py` |
| live-verified | 2026-09-26 | 10 live cases, 1 tool-result case, 3 error envelopes (one hand-added from its receipt), probes: `changes/2026-09-26-inference-hosts-live.md`, `receipts/2026-09-26-parasail/` |
| supported | 2026-09-26 | change entry ratified |

## Identity

- Service: Parasail serverless inference (vLLM-based; `model-specific-notes.md`).
- lm15 provider string: `parasail` — Chat Completions wire only. litellm spells it `parasail/`.
- Base URL: `https://api.parasail.io/v1` (`authentication.md`).
- Console: https://www.saas.parasail.io/keys.  Env key: `PARASAIL_API_KEY`.
- Models listed under two ids (`parasail-llama-33-70b-fp8` and `meta-llama/Llama-3.3-70B-Instruct`).
- Not registered: the Responses door, batch, embeddings, dedicated-instance management.

## Wire facts, each with its receipt (receipts/2026-09-26-parasail/)

| lm15 knob | Parasail wire | Live 2026-09-26 | Compat / decision |
|---|---|---|---|
| effort | `reasoning_effort` low/medium/high (gpt-oss, Harmony) | honoured; `minimal`, `xhigh`, `max`, `bogus` → 400 | `thinking_format="reasoning_effort"` |
| reasoning off | per model: gpt-oss none → **400** "Harmony does not support reasoning_effort='none'"; DeepSeek V3.1 / Qwen3.5 use `chat_template_kwargs` | loud where refused | send; model-specific `chat_template_kwargs` go in `Config.extensions` |
| reasoning out | `message.reasoning` (gpt-oss) | parsed | thinking |
| reasoning replay | — | code word recalled via `reasoning_content` 2 of 3, via `reasoning` 3 of 3, absent 0 of 3 | `thinking_replay="native"` |
| max tokens / stream usage | `max_completion_tokens` documented | cap honoured; usage on the final chunk | as the other hosts |
| tool choice | documented | required and named honoured (named answers `finish_reason: stop` with the call, vLLM's habit); `none` on Llama wrote the call as JSON text | send |
| structured output | `response_format` and `guided_json` | honoured | send |
| images in tool results | — | Qwen3-VL-8B read the image (hidden-oracle check) | `tool_result_media="images"`; case `tool_result_image` |
| caching | automatic | `cached_tokens` reported | `cache_control="none"` |
| models | `GET /models` → `data[]` | 91 entries | `models: true` |
| errors | JSON envelopes; **401 is plain text** ("Unauthorized. Invalid token format.") under a JSON content-type | 401 → AuthError by status; 404 "Deployment … doesn't exist or isn't accessible." → pinned MAP-15 form (`spec/model-not-found.json`) | `errors/cases/parasail.json` |

## Terms-of-service verdict

Source: `sources/parasail-terms-of-service.md`.  § 2.1: access "solely for your own internal
business purposes".  § 2.2: no reselling or service-bureau use, no competing product, and **(h) no
public disclosure of "any performance information or analysis relating to the Platform"**.
California law.

**Verdict: allowed, API key only, for the key holder's own purposes.**  Because of § 2.2(h) the
corpus records wire shapes only: the tool-result runner's per-request `latency_s` was removed from
this pass's receipts, and no overload or speed observation is recorded as a finding.

## Open items

- The cases use gpt-oss-20b as the reasoning model.
- Documents in tool results: untested.
