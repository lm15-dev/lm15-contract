# Fireworks AI — provider dossier

| State | Date | Evidence |
|---|---|---|
| candidate | 2026-09-26 | maintainer request (key added with credit); earlier the router guide's declared-provider example |
| researched | 2026-09-26 | this dossier; `scrapes/fireworks/pages/` (15 pages); `sources/` (terms, PDF) |
| implemented | 2026-09-26 | `lm15.registry.PROVIDERS["fireworks"]`, `lm15.access.FIREWORKS`, compat preset `fireworks` |
| offline-conformant | 2026-09-26 | auth case `fireworks-env-selected`; support matrix row; `tests/test_inference_hosts.py` |
| live-verified | 2026-09-26 | 11 live cases, 1 tool-result case, 3 error envelopes, probes: `changes/2026-09-26-inference-hosts-live.md`, `receipts/2026-09-26-fireworks/` |
| supported | — | after a reviewer ratifies the change entry |

## Identity

- Service: Fireworks AI serverless inference.
- lm15 provider string: `fireworks` — Chat Completions wire only. litellm spells it `fireworks_ai/`.
- Base URL: `https://api.fireworks.ai/inference/v1` (`openai-compatibility.md`).
- Console: https://app.fireworks.ai/settings/users/api-keys.  Env key: `FIREWORKS_API_KEY`.
- Model ids are `accounts/fireworks/models/<name>`; routers `accounts/fireworks/routers/<name>`.
- Not registered: the Responses and Anthropic Messages doors, batch, embeddings, reranking.

## Wire facts, each with its receipt (receipts/2026-09-26-fireworks/)

| lm15 knob | Fireworks wire | Live 2026-09-26 | Compat / decision |
|---|---|---|---|
| effort | `reasoning_effort`, or Anthropic-style `thinking` (never both) | low/high honoured; `minimal` and `bogus` → 400; xhigh/max ≈ high | `thinking_format="reasoning_effort"` |
| the `reasoning` object | not documented | **400 "Extra inputs are not permitted, field: reasoning"** (`probe-shape-reasoning-*`) | the OpenRouter shape is wrong here |
| reasoning off | `reasoning_effort: "none"` | DeepSeek V4.1: honoured (`reasoning_off`); **gpt-oss: 400** "Invalid reasoning effort: none"; **GLM-5.3: 400** "thinking-only model" — loud | send (MAP-5 satisfied by the server) |
| reasoning replay | `reasoning_content` required for interleaved thinking (`reasoning.md`) | code word recalled 3 of 3 via `reasoning_content`; **`reasoning` field → 400** 3 of 3 | `thinking_replay="native"` |
| max tokens / stream usage | both accepted | cap honoured; usage on the final chunk | as the other hosts |
| tool choice | documented | required, named honoured; `none` honoured | send |
| structured output | json_schema | honoured | send |
| images in tool results | — | GLM-5.3-Flash read the image (hidden-oracle check) | `tool_result_media="images"`; case `tool_result_image` |
| usage | nested details plus `output_tokens_details` | reasoning tokens reported | parsed |
| caching | automatic; session affinity via `user` or `x-session-affinity` | not exercised | `cache_control="none"` |
| models | `GET /inference/v1/models` → `data[]` with `supports_image_input`, `supports_tools` | 27 entries | `models: true` |
| errors | `{"error": {object, type, code, message}}` / `{message, code, type}` | 401 `UNAUTHORIZED`; 404 `NOT_FOUND`; 400 on a bad effort word | `errors/cases/fireworks.json` |

## Terms-of-service verdict

Source: `sources/fireworks-terms-of-service.md` (PDF, pdftotext).  § 2.1: access "solely for your
personal use or internal business purposes".  § 2.2: no use of content for ML training, no reselling
or transferring API keys, no competing products, **no benchmarking or competitive analysis**.
Delaware.  A documented-API client used by the key holder is authorized use.

**Verdict: allowed, API key only, for the key holder's own purposes.**  lm15 records wire facts,
never performance figures.

## Open items

- Documents in tool results: untested (`images` preset raises on them).
- The account was suspended (spending limit) earlier on 2026-09-26: error code `PRECONDITION_FAILED`
  on `/models`; not captured as an error case (no receipt).
