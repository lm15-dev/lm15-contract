# Live tool-result image probes

Derived from append-only receipts; no automatic retries.

| Provider | Model | Result | HTTP turns | Cells correct | Current Python body matches | Receipt |
|---|---|---|---|---|---|---|
| anthropic | claude-haiku-4-5 | visual_match | 200 / 200 | 12 | False | [receipt](2026-09-07T18-24-23Z-fd33a66c/anthropic/result.json) |
| gemini | gemini-3.7-flash | visual_match | 200 / 200 | 12 | False | [receipt](2026-09-07T18-24-23Z-fd33a66c/gemini/result.json) |
| openai | gpt-4.1-mini | accepted_but_visual_check_failed | 200 / 200 | — | — | [receipt](2026-09-07T18-24-23Z-fd33a66c/openai/result.json) |
| aws-anthropic | claude-haiku-4-5 | blocked_or_inconclusive | — / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/aws-anthropic/result.json) |
| azure | gpt-4.1-mini | accepted_but_visual_check_failed | 200 / 200 | 4 | — | [receipt](2026-09-07T18-25-27Z-0ac76375/azure/result.json) |
| azure-anthropic | claude-haiku-4-5 | first_call_rejected | 404 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/azure-anthropic/result.json) |
| azure-chat | gpt-4.1-mini | accepted_but_visual_check_failed | 200 / 200 | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/azure-chat/result.json) |
| bedrock-anthropic | anthropic.claude-haiku-4-5 | first_call_rejected | 403 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/bedrock-anthropic/result.json) |
| bedrock-chat | deepseek.v3.2 | image_result_rejected | 200 / 400 | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/bedrock-chat/result.json) |
| bedrock-mantle-chat | xai.grok-4-3 | first_call_rejected | 404 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/bedrock-mantle-chat/result.json) |
| claude-code | claude-sonnet-5 | visual_match | 200 / 200 | 12 | False | [receipt](2026-09-07T18-25-27Z-0ac76375/claude-code/result.json) |
| deepseek | deepseek-v4-flash | accepted_but_visual_check_failed | 200 / 200 | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/deepseek/result.json) |
| deepseek-anthropic | deepseek-v4-flash | accepted_but_visual_check_failed | 200 / 200 | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/deepseek-anthropic/result.json) |
| groq | meta-llama/llama-4-scout-17b-16e-instruct | first_call_rejected | 404 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/groq/result.json) |
| meta | muse-spark-1.3 | visual_match | 200 / 200 | 12 | False | [receipt](2026-09-07T18-25-27Z-0ac76375/meta/result.json) |
| meta-anthropic | muse-spark-1.3 | accepted_but_visual_check_failed | 200 / 200 | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/meta-anthropic/result.json) |
| meta-chat | muse-spark-1.3 | image_result_rejected | 200 / 400 | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/meta-chat/result.json) |
| moonshotai | kimi-k2.6 | visual_match | 200 / 200 | 12 | False | [receipt](2026-09-07T18-25-27Z-0ac76375/moonshotai/result.json) |
| moonshotai-anthropic | kimi-k3 | visual_match | 200 / 200 | 12 | True | [receipt](2026-09-07T18-25-27Z-0ac76375/moonshotai-anthropic/result.json) |
| moonshotai-responses | kimi-k3 | visual_match | 200 / 200 | 12 | False | [receipt](2026-09-07T18-25-27Z-0ac76375/moonshotai-responses/result.json) |
| ollama | qwen2.5vl:7b | first_call_rejected | 404 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/ollama/result.json) |
| openai-chat | gpt-4.1-mini | accepted_but_visual_check_failed | 200 / 200 | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/openai-chat/result.json) |
| openai-codex | gpt-5.4-mini | blocked_or_inconclusive | 200 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/openai-codex/result.json) |
| openrouter | openai/gpt-4.1-mini | first_call_rejected | 401 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/openrouter/result.json) |
| sglang | Qwen/Qwen2.5-VL-7B-Instruct | blocked_or_inconclusive | — / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/sglang/result.json) |
| vertex | gemini-3.7-flash | blocked_or_inconclusive | — / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/vertex/result.json) |
| vertex-anthropic | claude-haiku-4-5 | blocked_or_inconclusive | — / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/vertex-anthropic/result.json) |
| vertex-express | gemini-3.7-flash | blocked_or_inconclusive | — / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/vertex-express/result.json) |
| vllm | Qwen/Qwen2.5-VL-7B-Instruct | blocked_or_inconclusive | — / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/vllm/result.json) |
| xai | grok-4.20 | visual_match | 200 / 200 | 12 | False | [receipt](2026-09-07T18-25-27Z-0ac76375/xai/result.json) |
| zai | glm-4.6v | blocked_or_inconclusive | 200 / — | — | — | [receipt](2026-09-07T18-25-27Z-0ac76375/zai/result.json) |
| openai-chat | gpt-5.4-mini | accepted_but_visual_check_failed | 200 / 200 | 0 | — | [receipt](2026-09-07T18-26-37Z-16c336c4/openai-chat/result.json) |
| openai | gpt-5.4-mini | accepted_but_visual_check_failed | 200 / 200 | 8 | — | [receipt](2026-09-07T18-26-37Z-80ddea3e/openai/result.json) |
| bedrock-mantle-chat | xai.grok-4.3 | first_call_rejected | 400 / — | — | — | [receipt](2026-09-07T18-29-22Z-095ed9c9/bedrock-mantle-chat/result.json) |
| groq | qwen/qwen3.8-27b | image_result_rejected | 200 / 400 | — | — | [receipt](2026-09-07T18-29-22Z-095ed9c9/groq/result.json) |
| ollama | qwen3.5:0.8b | accepted_but_visual_check_failed | 200 / 200 | — | — | [receipt](2026-09-07T18-29-22Z-095ed9c9/ollama/result.json) |
