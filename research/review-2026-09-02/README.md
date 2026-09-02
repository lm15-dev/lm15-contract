# review-2026-09-02 — live probes settling the independent review

Seven probes the independent review (`goldens/REVIEW-2026-09-02-independent.md`
§5) said could not be judged offline. `10-probes.py` is the exact code;
`receipts/<tag>/<ts>.txt` the verbatim bodies with the redacted request
beside each; `20-results.json` the table. `30-recapture.py` then
re-captured the four OpenAI cache cases whose wire changed and captured
the four streaming tool-call cases, all with adapter-built wires.
Total spend: about 8 cents.

| # | Question | Result | Consequence |
|---|---|---|---|
| 1 | Does the Gemini 3.x text-part `thoughtSignature` matter on replay? | Both variants 200. Without it: `thoughtsTokenCount` absent (no thinking on turn 2). With it: 145 thought tokens. | The fix landed in `2026-09-02-review-followup.md` is meaningful: the signature carries the thinking context forward. |
| 2 | Does gpt-5.6-sol reject `prompt_cache_retention: "24h"`? | 200; echoes `"24h"`. Every pinned 5.6 body already echoes 24h as default. | MAP-6 rule 5 amended: no raise; send 24h on every class. |
| 3 | Does `prompt_cache_options.mode=explicit` next to a breakpoint stop the suffix write? | Cold: write 3066. Warm: read 3066, write 0. Before: warm wrote 18. | MAP-6 rule 4 amended: a placed mark travels with explicit mode on 5.6+. Four cases re-captured. |
| 4 | Groq `reasoning_format: parsed` (MAP-7 rule 7, no receipt) | Default: `<think>` leaks into content, no `reasoning` key. Parsed: `message.reasoning` 694 chars, content `3861`. | Rule receipted. |
| 5 | xAI allowlist (MAP-8 rule 1, one sample) | 5/5 called the disallowed `weather`. | Rule confirmed systematic. |
| 6 | Sonnet 5 `effort: minimal` (MAP-7 rule 2) | 400: "Input should be 'low', 'medium', 'high', 'xhigh' or 'max'". | Rule confirmed. |
| 7 | Does every dialect name a streamed tool call on its first fragment? (MAP-9 premise) | Yes on all four. Pinned as `openai/openai_chat/anthropic/gemini.streaming_tool_call`. | Premise pinned — and the Anthropic pin caught a reference bug: `content_block_start.input: {}` was glued in front of the `input_json_delta` fragments. Fixed; red-first test. |
