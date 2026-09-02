# Tool choice — fact sheets (2026-09-02)

141 live cells (`20-results.json`, receipts under `receipts/`) across
OpenAI Responses (gpt-5.6-sol), OpenAI Chat (gpt-5.4-mini; gpt-5.6-sol
refuses function tools on /chat/completions: "use the Responses API"),
Anthropic (Sonnet 5, Sonnet 4.5), Gemini (2.5 Flash, 3.7 Flash), xAI
(grok-4.6), Groq (gpt-oss-20b). Sources: 9 pages (manifest; xAI missing).

| Cell | OpenAI Responses | OpenAI Chat | Anthropic | Gemini 2.5 / 3.7 | xAI | Groq |
|---|---|---|---|---|---|---|
| required, no tool needed | calls lookup | calls lookup | calls lookup (`stop_reason: tool_use`) | 2.5 calls lookup; 3.7 calls BOTH | calls weather | **400 "model did not call a tool"** (server validates) |
| none, tool needed | text, no call | text | text (`end_turn`) | 2.5 `finishReason: UNEXPECTED_TOOL_CALL`, no parts; 3.7 text | text | **400 "model called a tool"** |
| force weather, prompt asks lookup | weather | weather | Sonnet 5: weather **and** lookup; 4.5: weather | weather (ANY + allowedFunctionNames) | weather | **400 "attempted to call lookup"** (model ignored the force; server validated) |
| allow {lookup}, prompt asks weather | lookup (restriction held) | lookup | no wire form (`docs :843-848`: auto/any/tool/none only) | VALIDATED: text refusal, no excluded call | **weather — allowlist silently ignored** | **400 unsupported shape** |
| parallel=false, prompt asks two | 1 call | 1 call | 1 call (`disable_parallel_tool_use`) | **2 calls — no wire knob, silently ignored** (both classes) | 1 call | 1 call (default too) |
| parallel default | 2 calls | 2 calls | 2 calls | 2 calls | 2 calls | 1 call |
| forced tool + json schema | call, schema ignored | call | call | **400 "Forced function calling (ANY) with response mime type unsupported"** | **JSON text, no call — the force silently lost** | **400 "json mode cannot be combined with tool calling"** |

Sources: OpenAI modes auto/required/forced/allowed_tools/none and
`parallel_tool_calls` (`openai-function-calling.md:972-1009`); Anthropic
auto/any/tool/none, `disable_parallel_tool_use`, and per-model
restrictions — manual thinking and Fable/Mythos 5.1 reject `any`/`tool`
(`anthropic-tool-use-implement.md:555-562, 843-848`); Gemini
AUTO/ANY/NONE/VALIDATED with `allowedFunctionNames`
(`gemini-function-calling.md:1384-1390`, generate-content reference).
