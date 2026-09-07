# Tool-result content — live matrix

239 cells, 406 inference calls, no automatic retries. Cell = did the model receive the tool's content (hidden oracle). `OK` received · `200-miss` accepted, content not received · `200-nojson` accepted, no parseable answer · `400` tool-result wire rejected · `t1-fail` first call failed · `blocked` credentials/model/loop · `err-OK` is_error acknowledged · `err-FAB` error ignored, colors fabricated.

| Binding | Model | Oracle | text | image | mixed | pair | pdf | error | control |
|---|---|---|---|---|---|---|---|---|---|
| anthropic | claude-haiku-4-5 | 64px/auto | OK | OK | OK | OK | OK | err-OK | OK |
| aws-anthropic | claude-haiku-4-5 | 64px/auto | — | — | — | blocked | — | — | — |
| azure | gpt-4.1-mini | 256px/high | — | 200-miss | 200-miss | 200-miss | — | — | OK |
| azure | gpt-4.1-mini | 64px/auto | OK | 200-miss | 200-miss | 200-nojson | OK | 400 | t1-fail |
| azure-anthropic | claude-haiku-4-5 | 64px/auto | — | — | — | t1-fail | — | — | — |
| azure-chat | gpt-4.1-mini | 64px/auto | t1-fail | t1-fail | 400 | t1-fail | t1-fail | t1-fail | t1-fail |
| bedrock-anthropic | anthropic.claude-haiku-4-5 | 64px/auto | — | — | — | t1-fail | — | — | — |
| bedrock-chat | deepseek.v3.2 | 64px/auto | OK | 400 | 400 | 400 | 400 | blocked | t1-fail |
| bedrock-mantle-chat | xai.grok-4-3 | 64px/auto | — | — | — | t1-fail | — | — | — |
| bedrock-mantle-chat | xai.grok-4.3 | 64px/auto | — | — | — | t1-fail | — | — | — |
| claude-code | claude-sonnet-5 | 64px/auto | OK | OK | OK | OK | OK | err-OK | OK |
| deepseek | deepseek-v4-flash | 256px/high | — | 200-nojson | 200-miss | — | — | — | 200-nojson |
| deepseek | deepseek-v4-flash | 64px/auto | OK | 200-nojson | 200-miss | 200-nojson | 200-nojson | err-OK | 200-nojson |
| deepseek-anthropic | deepseek-v4-flash | 64px/auto | OK | 200-miss | 200-nojson | 200-nojson | 200-miss | err-OK | 200-nojson |
| gemini | gemini-2.5-flash | 64px/auto | — | 400 | — | 400 | 400 | — | OK |
| gemini | gemini-3.7-flash | 64px/auto | OK | OK | OK | OK | OK | err-OK | OK |
| groq | meta-llama/llama-4-scout-17b-16e-instruct | 64px/auto | — | — | — | t1-fail | — | — | — |
| groq | qwen/qwen3.8-27b | 256px/high | — | 400 | 400 | — | — | — | OK |
| groq | qwen/qwen3.8-27b | 64px/auto | 200-nojson | 400 | 400 | 400 | 400 | 200-nojson | OK |
| meta | muse-spark-1.3 | 64px/auto | OK | OK | OK | OK | OK | err-OK | OK |
| meta-anthropic | muse-spark-1.3 | 64px/auto | OK | OK | OK | OK | OK | err-OK | OK |
| meta-chat | muse-spark-1.3 | 64px/auto | OK | 400 | 400 | 400 | 400 | err-OK | OK |
| moonshotai | kimi-k2.6 | 64px/auto | OK | OK | OK | OK | 400 | err-OK | OK |
| moonshotai-anthropic | kimi-k3 | 64px/auto | OK | OK | OK | OK | 400 | err-OK | OK |
| moonshotai-responses | kimi-k3 | 64px/auto | OK | OK | OK | OK | 400 | err-OK | OK |
| ollama | qwen2.5vl:7b | 64px/auto | — | — | — | t1-fail | — | — | — |
| ollama | qwen3.5:0.8b | 256px/high | — | blocked | blocked | — | — | — | blocked |
| ollama | qwen3.5:0.8b | 64px/auto | blocked | blocked | blocked | blocked | blocked | blocked | blocked |
| openai | gpt-4.1-mini | 256px/high | — | 200-miss | 200-miss | 200-miss | — | — | OK |
| openai | gpt-4.1-mini | 64px/auto | OK | 200-miss | 200-miss | 200-miss | OK | err-OK | 200-miss |
| openai | gpt-5.4 | 256px/high | — | OK | OK | OK | — | — | OK |
| openai | gpt-5.4 | 64px/auto | OK | 200-miss | 200-miss | 200-miss | OK | err-OK | 200-miss |
| openai | gpt-5.4-mini | 64px/auto | — | — | — | 200-miss | — | — | — |
| openai-chat | gpt-4.1-mini | 64px/auto | OK | 200-miss | 200-nojson | 200-nojson | 400 | err-OK | 200-miss |
| openai-chat | gpt-5.4 | 256px/high | — | 200-miss | 200-miss | 200-nojson | — | — | OK |
| openai-chat | gpt-5.4 | 64px/auto | OK | 200-miss | 200-miss | 200-nojson | 400 | err-OK | 200-miss |
| openai-chat | gpt-5.4-mini | 64px/auto | — | — | — | 200-miss | — | — | — |
| openai-codex | gpt-5.4-mini | 256px/high | OK | 200-miss | 200-miss | 200-miss | — | err-OK | 200-nojson |
| openai-codex | gpt-5.4-mini | 64px/auto | blocked | blocked | blocked | blocked | blocked | blocked | 200-nojson |
| openrouter | openai/gpt-4.1-mini | 64px/auto | — | — | — | t1-fail | — | — | — |
| sglang | Qwen/Qwen2.5-VL-7B-Instruct | 64px/auto | — | — | — | blocked | — | — | — |
| vertex | gemini-3.7-flash | 64px/auto | — | — | — | blocked | — | — | — |
| vertex-anthropic | claude-haiku-4-5 | 64px/auto | — | — | — | blocked | — | — | — |
| vertex-express | gemini-3.7-flash | 64px/auto | — | — | — | blocked | — | — | — |
| vllm | Qwen/Qwen2.5-VL-7B-Instruct | 64px/auto | — | — | — | blocked | — | — | — |
| xai | grok-4.20 | 64px/auto | OK | OK | OK | OK | 400 | err-OK | OK |
| zai | glm-4.6v | 64px/auto | OK | OK | OK | blocked | 400 | err-OK | OK |

Older runs of the same cell are kept in `20-results.json` (field `run`).
