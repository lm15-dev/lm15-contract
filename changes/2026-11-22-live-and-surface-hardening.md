# 2026-11-22 — OpenAI Realtime nameless-call refusal, non-chat unmapped enforcement, and expanded reject vectors

**Status: implemented across `lm15-contract`, `lm15-python`, and `lm15-ts` on 2026-11-22.**

## Summary

Closes the remaining shared contract and Python/TypeScript gaps identified in the 2026-11-22 audit:

1. **MAP-9 on OpenAI Realtime (`mapping/live-tool-names.json`, `harness/check.py`):**
   Extends the synthetic live negative controls from Gemini Live to OpenAI Realtime `response.output_item.done` `function_call` items (`missing`, `null`, `empty`, `number`), derived from the recorded `openai.live_tool_no_description` call. Both `lm15-python` and `lm15-ts` now raise `ProviderError` (`provider`) instead of fabricating `"tool"` or stringifying non-string names.
2. **Non-chat `_lm15_unmapped` checks (`harness/check.py`):**
   `run_generation_direction` (before stripping `provider_data`), `run_batch_direction`, `run_files_direction`, `run_cache_direction`, `run_video_direction`, and `run_models_direction` now fail whenever any parsed object or nested `provider_data` carries a non-empty `_lm15_unmapped` list. OpenAI and xAI image-generation parsers also record unmapped `data[i]` items instead of silently skipping them.
3. **Expanded `serde/reject.json` and selftest controls (`serde/reject.json`, `harness/fake_shim.py`, `harness/selftest.py`):**
   Adds 11 invalid canonical inputs covering `ModelInfo` / `InferencePricing`, `TokenLogprob`, and `Adaptation` (via `stream_event`), plus three new harness self-test mutations (`live_guessed_openai_tool_name`, `gen_unmapped_ignored`, `batch_unmapped_ignored` — 72 mutations total).
