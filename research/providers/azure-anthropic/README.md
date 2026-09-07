# azure-anthropic — dossier

Claude in Microsoft Foundry over the Anthropic Messages wire:
`https://{resource}.services.ai.azure.com/anthropic/v1`.

- Partial live verification: `changes/2026-09-04-azure-anthropic-partial.md`.
- Receipts: `receipts/2026-09-04-azure-anthropic/`.
- Capture after quota: `python3 research/providers/azure-anthropic/capture.py --force`.
- Proven without quota: real host; `x-api-key`; both Entra scopes; lm15's
  secret and certificate rungs; `/models` refusal; top-level Azure error
  shape. The documented `api-key` header is refused (401).
- Blocker: quota 0. Microsoft's eastus2 request denial says regional
  capacity, not account or permission. No HTTP 200/SSE proof exists.
- Exact post-quota commands and the remaining cells are in the partial
  change entry. Do not call this door live-verified before they land.
