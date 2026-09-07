# azure-chat — dossier

Azure OpenAI v1 over the Chat Completions wire, same resource and key as
`azure` (`research/providers/azure/README.md` has the lab and the host
facts).

- Capture: `python3 research/providers/azure-chat/capture.py`.
- Live 2026-09-04: `changes/2026-09-04-azure-chat-live.md`,
  `receipts/2026-09-04-azure-chat/`. Compat preset `openai` holds:
  forced `tool_choice`, strict `json_schema`, low/high reasoning, warm
  prompt caching, both content-filter paths, stream usage and async.
- Account surfaces live on the `azure` Responses adapter, not this chat
  adapter. Open cells: a context-length envelope (the 200K TPM quota
  rate-limits a 400K-token request first); Foundry-sold non-OpenAI
  models (DeepSeek, Grok) on this path.
