# 2026-09-04 — Claude in Microsoft Foundry (`azure-anthropic`), quota-blocked partial live verification

Status: **BLOCKED for successful inference**, not a live-verified door.
Dossier: `research/providers/azure-anthropic/README.md`. Receipts:
`receipts/2026-09-04-azure-anthropic/`.

## What is proven on the real Azure host without a deployment

Resource `lm15-fdy-29d280ed6f8e` (kind `AIServices`, eastus2) answers at
`https://lm15-fdy-29d280ed6f8e.services.ai.azure.com/anthropic/v1`.
A request with a valid identity reaches deployment lookup and returns the
model-specific 404, which separates accepted authentication from a bad
key's 401.

| cell | live result |
|---|---|
| API key under `x-api-key` | 404 `DeploymentNotFound`: authentication accepted |
| API key under documented `api-key` | 401: refused; lm15 policy corrected to `x-api-key` only |
| Entra, `https://ai.azure.com/.default` | 404 `DeploymentNotFound`: accepted |
| Entra, `https://cognitiveservices.azure.com/.default` | 404: accepted |
| lm15 `azure-chain`, client secret | 404: accepted |
| lm15 `azure-chain`, certificate / standard-library RS256 assertion | 404: accepted |
| `GET /anthropic/v1/models` | 404 `api_not_supported`, as documented |
| unknown deployment | top-level `{code: DeploymentNotFound, message: …}`; maps to `UnsupportedModelError` |
| malformed body before deployment exists | deployment lookup wins; body validation cannot be tested yet |

The quota-free work found two real bugs. `AZURE_ANTHROPIC` preferred the
wrong `api-key` header, and Anthropic error parsing ignored Azure's
top-level `{code,message}` gateway shape. Both are fixed and harness-
pinned. The ordinary Anthropic request, response and stream codecs remain
covered by their live first-party cases and all harness vectors.

## Exact blocker

`AIServices.GlobalStandard.claude-haiku-4-5` quota is 0. The user
requested 10 capacity units (10K TPM), Hosted on Anthropic
Infrastructure, Global Standard, eastus2. Microsoft denied it because
**eastus2 had no capacity**, not because of IAM, billing, policy, or the
application. Microsoft asks for another region or a retry after 30 days.
The user chose not to submit another tedious request now.

Therefore these cells have no Azure proof: HTTP 200 response, SSE stream,
Azure usage additions, thinking, tools, forced tool choice, structured
output, beta headers, and the documented web-search refusal.

## Runbook after Azure grants quota

Use the granted region (example `westus3`). The provisioner creates a
second Foundry resource there; it does not move the eastus2 Azure OpenAI
resource. Version `20251001` explicitly selects the Anthropic-
infrastructure offer, not version `2` (Hosted on Azure).

```bash
cd lm15-contract
FDY_LOC=westus3 \
LM15_LAB_ORG='lm15-dev (open-source project, Maxime Rivest)' \
LM15_LAB_INDUSTRY='Software & Internet' \
LM15_LAB_COUNTRY=CA \
bash research/cloud-hosts/azure/provision.sh

python3 research/providers/azure-anthropic/capture.py --force
python3 tools/scribe_goldens.py
python3 harness/check.py --shim python --direction all --no-check-pin
python3 tools/check_secrecy.py
python3 tools/check_provenance.py
python3 tools/audit.py
```

Then review every generated case and golden, update this entry from
BLOCKED to DRAFT/live-verified, and ratify it. No lm15 design work should
be needed after quota; only deployment, capture, review, and any real
wire differences the successful calls reveal.
