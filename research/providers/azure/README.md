# azure — dossier

Azure OpenAI v1 over the Responses wire:
`https://{resource}.openai.azure.com/openai/v1`, `api-key` header or an
Entra bearer (`azure-chain`).  Sources: `research/cloud-hosts/sources/
azure-openai-api-lifecycle.md`, `azure-openai-managed-identity.md`; fact
sheet `research/cloud-hosts/10-facts-azure.md`.

- Lab: `bash research/cloud-hosts/azure/provision.sh` after `az login`
  (writes `~/.config/lm15/azure-lab.env`; `--teardown` deletes it all).
- Capture: `python3 research/providers/azure/capture.py` (reads the lab
  env; the `entra-*` probes need `az` on PATH, the `entra-sp-*` probes
  need only the env file).
- Live 2026-09-04: `changes/2026-09-04-azure-live.md`,
  `receipts/2026-09-04-azure/`.  Deployment `gpt-4.1-mini` (nano has 0
  quota on a fresh subscription).
- Live surfaces: complete/stream, tools, reasoning, prompt caching,
  content filtering, models, Files, Batch, speech and Realtime text.
  Sync/async and every practical auth path also ran live.
- Facts learned live: `/openai/v1/models` answers 200 (the resource's
  catalog, not its deployments); both Entra scopes accepted; `x-api-key`
  refused; an `OpenAI`-kind resource has no `services.ai.azure.com`
  name; `max_output_tokens` floor 16; 404 `DeploymentNotFound` is the
  door's "unknown model"; Azure Files uses 201 + pending then 204/200.
- Exact pending item on this door: image generation waits on
  `gpt-image-1-mini` quota. Certificate refresh passed live by forced
  expiry; its natural-expiry soak is supplementary. Video is deliberately
  excluded. See the change entry for the post-quota command.
