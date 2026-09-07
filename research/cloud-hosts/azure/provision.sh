#!/usr/bin/env bash
# Provision the Azure lab for the cloud-hosts capture campaign (phase 3 of
# changes/2026-09-03-cloud-hosts.md).  Idempotent: rerun after any failure.
#
# Creates, in one resource group:
#   - an Azure OpenAI resource (kind OpenAI, S0, custom subdomain — required
#     for Entra tokens) with one gpt-4.1-nano deployment (GlobalStandard);
#   - a Foundry resource (kind AIServices, S0, custom subdomain) and a
#     claude-haiku-4-5 deployment.  Anthropic deployments need a one-time
#     "model provider data" form (industry, organisation, country) that the
#     `az cognitiveservices` command cannot send, so the deployment goes
#     through `az rest` (api-version 2025-10-01-preview).  Set LM15_LAB_ORG,
#     LM15_LAB_INDUSTRY and LM15_LAB_COUNTRY (ISO 3166-1 alpha-2) or the
#     script skips it and says so.  A fresh subscription also has ZERO Claude
#     quota in every region; the script detects that and names the portal
#     page where quota is requested;
#   - an app registration + service principal with a client SECRET and a
#     client CERTIFICATE (generated here), and the data-plane roles on both
#     resources for the service principal and for you;
# and writes every value the capture scripts read to $ENV_FILE (mode 600,
# outside every repository).  Nothing here has a fixed monthly cost: S0
# accounts and GlobalStandard deployments bill per token.
#
# Usage:  bash research/cloud-hosts/azure/provision.sh      (after `az login`)
#         bash research/cloud-hosts/azure/provision.sh --teardown
set -euo pipefail
umask 077

# Reject mistyped/dry-run flags before touching state or provisioning anything.
case "${1:-}" in
  ""|--teardown) ;;
  --help|-h) echo 'Usage: provision.sh [--teardown] (live operations; no dry-run mode)'; exit 0 ;;
  *) echo 'Unsupported argument; use --help. No operations performed.' >&2; exit 2 ;;
esac
if (( $# > 1 )); then
  echo 'Unexpected extra arguments. No operations performed.' >&2
  exit 2
fi

# `command az` so the function does not call itself when az is on PATH.
if command -v az >/dev/null 2>&1; then
  az() { command az "$@"; }
else
  az() { nix run nixpkgs#azure-cli -- "$@"; }
fi

STATE_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/lm15"
ENV_FILE="$STATE_DIR/azure-lab.env"
CERT_DIR="$STATE_DIR/azure-lab"
mkdir -p "$STATE_DIR" "$CERT_DIR"
chmod 700 "$STATE_DIR" "$CERT_DIR"

RG=${RG:-lm15-lab}
LOC=${LOC:-eastus2}
# Claude quota can be granted in a different region from Azure OpenAI.
FDY_LOC=${FDY_LOC:-$LOC}
# gpt-4.1-mini, not nano: a fresh subscription has 0 TPM quota for nano and
# 200K for mini (observed 2026-09-04, eastus2).  Same API surface, same date.
OPENAI_MODEL=${OPENAI_MODEL:-gpt-4.1-mini}
OPENAI_MODEL_VERSION=${OPENAI_MODEL_VERSION:-2025-04-14}
CLAUDE_MODEL=${CLAUDE_MODEL:-claude-haiku-4-5}
# 20251001 is the Anthropic-infrastructure offer requested in the form;
# version 2 is the separate "Hosted on Azure" offer and quota row.
CLAUDE_MODEL_VERSION=${CLAUDE_MODEL_VERSION:-20251001}
APP_NAME=${APP_NAME:-lm15-lab-sp}

# A stable suffix so reruns find the same resources (names must be globally
# unique).  Saved to its own file BEFORE anything is created, so a run that
# dies halfway does not leave orphans under a name the next run cannot find.
SUFFIX_FILE="$STATE_DIR/azure-lab.suffix"
if [[ -f "$SUFFIX_FILE" ]]; then
  SUFFIX=$(cat "$SUFFIX_FILE")
elif [[ -f "$ENV_FILE" ]] && grep -q '^LM15_LAB_SUFFIX=' "$ENV_FILE"; then
  SUFFIX=$(grep '^LM15_LAB_SUFFIX=' "$ENV_FILE" | cut -d= -f2)
  echo "$SUFFIX" > "$SUFFIX_FILE"
else
  SUFFIX=$(head -c 6 /dev/urandom | od -An -tx1 | tr -d ' \n')
  echo "$SUFFIX" > "$SUFFIX_FILE"
fi
OAI="lm15-oai-$SUFFIX"
if [[ "$FDY_LOC" == "$LOC" ]]; then
  FDY="lm15-fdy-$SUFFIX"  # keep the original name on ordinary reruns
else
  FDY="lm15-fdy-${FDY_LOC//-/}-$SUFFIX"
fi

say() { printf '\n== %s\n' "$*"; }

if [[ "${1:-}" == "--teardown" ]]; then
  say "deleting resource group $RG (all resources, all deployments)"
  az group delete -n "$RG" --yes --no-wait
  if [[ -f "$ENV_FILE" ]] && grep -q '^AZURE_CLIENT_ID=' "$ENV_FILE"; then
    APPID=$(grep '^AZURE_CLIENT_ID=' "$ENV_FILE" | cut -d= -f2)
    say "deleting app registration $APPID"
    az ad app delete --id "$APPID"
  fi
  rm -f "$ENV_FILE" "$SUFFIX_FILE"
  rm -rf "$CERT_DIR"
  echo "done; the group deletes in the background (az group show -n $RG to check)"
  exit 0
fi

say "subscription"
SUB=$(az account show --query id -o tsv)
TENANT=$(az account show --query tenantId -o tsv)
ME=$(az ad signed-in-user show --query id -o tsv)
echo "subscription $SUB, tenant $TENANT, user object $ME"

say "resource provider Microsoft.CognitiveServices"
az provider register -n Microsoft.CognitiveServices --wait >/dev/null

say "resource group $RG in $LOC"
az group create -n "$RG" -l "$LOC" -o none

say "Azure OpenAI resource $OAI"
if ! az cognitiveservices account show -n "$OAI" -g "$RG" -o none 2>/dev/null; then
  az cognitiveservices account create -n "$OAI" -g "$RG" -l "$LOC" --kind OpenAI --sku S0 --custom-domain "$OAI" --yes -o none
fi
OAI_ID=$(az cognitiveservices account show -n "$OAI" -g "$RG" --query id -o tsv)

say "deployment $OPENAI_MODEL on $OAI"
if ! az cognitiveservices account deployment show -n "$OAI" -g "$RG" --deployment-name "$OPENAI_MODEL" -o none 2>/dev/null; then
  az cognitiveservices account deployment create -n "$OAI" -g "$RG" \
    --deployment-name "$OPENAI_MODEL" --model-name "$OPENAI_MODEL" --model-version "$OPENAI_MODEL_VERSION" \
    --model-format OpenAI --sku-name GlobalStandard --sku-capacity 10 -o none
fi

# Extra deployments for the account surfaces and the reasoning cells, on the
# same Azure OpenAI resource.  name|model|version|sku|capacity.  Every one is
# pay-per-use; a fresh subscription has quota for all of these (2026-09-04,
# eastus2) but NONE for image generation (gpt-image-1, dall-e-3): that one
# is requested in the portal and added here when it lands.
EXTRA_DEPLOYMENTS=${EXTRA_DEPLOYMENTS:-"gpt-5-mini|gpt-5-mini|2025-08-07|GlobalStandard|10
gpt-4.1-mini-batch|gpt-4.1-mini|2025-04-14|GlobalBatch|50
text-embedding-3-small|text-embedding-3-small|1|GlobalStandard|10
gpt-4o-mini-transcribe|gpt-4o-mini-transcribe|2025-03-20|GlobalStandard|1
gpt-4o-mini-tts|gpt-4o-mini-tts|2025-03-20|GlobalStandard|1
gpt-realtime-mini|gpt-realtime-mini|2025-12-15|GlobalStandard|1
gpt-image-1-mini|gpt-image-1-mini|2025-10-06|GlobalStandard|1"}
say "extra deployments on $OAI"
while IFS='|' read -r DNAME MNAME MVER SKU CAP; do
  [[ -z "$DNAME" ]] && continue
  if az cognitiveservices account deployment show -n "$OAI" -g "$RG" --deployment-name "$DNAME" -o none 2>/dev/null; then
    echo "  $DNAME: exists"
  elif az cognitiveservices account deployment create -n "$OAI" -g "$RG" --deployment-name "$DNAME" \
        --model-name "$MNAME" --model-version "$MVER" --model-format OpenAI --sku-name "$SKU" --sku-capacity "$CAP" -o none 2>/tmp/lm15-deploy.err; then
    echo "  $DNAME: created ($MNAME $MVER, $SKU $CAP)"
  else
    echo "  $DNAME: FAILED — $(grep -m1 -oE '\([A-Za-z]+\)[^.]*' /tmp/lm15-deploy.err || head -c 200 /tmp/lm15-deploy.err)"
  fi
done <<< "$EXTRA_DEPLOYMENTS"

say "Foundry resource $FDY in $FDY_LOC"
if ! az cognitiveservices account show -n "$FDY" -g "$RG" -o none 2>/dev/null; then
  az cognitiveservices account create -n "$FDY" -g "$RG" -l "$FDY_LOC" --kind AIServices --sku S0 --custom-domain "$FDY" --yes -o none
fi
FDY_ID=$(az cognitiveservices account show -n "$FDY" -g "$RG" --query id -o tsv)

say "Claude quota for $CLAUDE_MODEL in $FDY_LOC (tokens/minute, thousands)"
CLAUDE_QUOTA=$(az cognitiveservices usage list -l "$FDY_LOC" --query "[?name.value=='AIServices.GlobalStandard.$CLAUDE_MODEL'].limit | [0]" -o tsv 2>/dev/null || echo 0)
CLAUDE_QUOTA=${CLAUDE_QUOTA:-0}
echo "limit: $CLAUDE_QUOTA"

say "Claude deployment $CLAUDE_MODEL on $FDY"
CLAUDE_OK=0
if az cognitiveservices account deployment show -n "$FDY" -g "$RG" --deployment-name "$CLAUDE_MODEL" -o none 2>/dev/null; then
  CLAUDE_OK=1
elif [[ "${CLAUDE_QUOTA%.*}" == 0 ]]; then
  cat <<EOF

!! Claude quota is 0 for this subscription.  New subscriptions get none; it
!! must be requested once (Microsoft reviews it, usually within a day):
!!   https://ai.azure.com -> Management center -> Quota -> "Request quota"
!!   model "$CLAUDE_MODEL", region $FDY_LOC, 10 (thousand TPM) is enough.
!! Rerun this script when the limit above is > 0.
EOF
elif [[ -z "${LM15_LAB_ORG:-}" || -z "${LM15_LAB_INDUSTRY:-}" || -z "${LM15_LAB_COUNTRY:-}" ]]; then
  cat <<EOF

!! Anthropic deployments need a one-time form (industry, organisation,
!! country) that Azure forwards to the model provider.  Rerun with:
!!   LM15_LAB_ORG='<organisation name>' LM15_LAB_INDUSTRY='<industry>' LM15_LAB_COUNTRY='<ISO-2, e.g. FR>' \\
!!   bash research/cloud-hosts/azure/provision.sh
EOF
else
  VER=$(az cognitiveservices model list -l "$FDY_LOC" --query "[?model.name=='$CLAUDE_MODEL' && model.format=='Anthropic' && model.version=='$CLAUDE_MODEL_VERSION'].model.version | [0]" -o tsv)
  if [[ -z "$VER" ]]; then
    echo "!! $CLAUDE_MODEL version $CLAUDE_MODEL_VERSION is not listed in $FDY_LOC" >&2
    exit 1
  fi
  # `az cognitiveservices account deployment create` has no flag for
  # modelProviderData; the ARM API (2025-10-01-preview) takes it flat.
  BODY=$(python3 - "$CLAUDE_MODEL" "$VER" <<'PY'
import json, os, sys
print(json.dumps({
  "sku": {"name": "GlobalStandard", "capacity": 1},
  "properties": {
    "model": {"format": "Anthropic", "name": sys.argv[1], "version": sys.argv[2]},
    "modelProviderData": {
      "industry": os.environ["LM15_LAB_INDUSTRY"],
      "organizationName": os.environ["LM15_LAB_ORG"],
      "countryCode": os.environ["LM15_LAB_COUNTRY"],
    },
  },
}))
PY
)
  if az rest --method PUT -o none \
      --url "https://management.azure.com$FDY_ID/deployments/$CLAUDE_MODEL?api-version=2025-10-01-preview" \
      --body "$BODY"; then
    CLAUDE_OK=1
  fi
fi

say "app registration $APP_NAME (service principal)"
APPID=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv)
if [[ -z "$APPID" ]]; then
  APPID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
fi
if ! az ad sp show --id "$APPID" -o none 2>/dev/null; then
  az ad sp create --id "$APPID" -o none
fi
SPOBJ=$(az ad sp show --id "$APPID" --query id -o tsv)

say "client secret"
if [[ -f "$ENV_FILE" ]] && grep -q '^AZURE_CLIENT_SECRET=' "$ENV_FILE"; then
  SECRET=$(grep '^AZURE_CLIENT_SECRET=' "$ENV_FILE" | cut -d= -f2-)
else
  SECRET=$(az ad app credential reset --id "$APPID" --append --display-name lm15-lab-secret --years 1 --query password -o tsv)
fi

say "client certificate (RSA 2048, self-signed, 1 year)"
KEYPEM="$CERT_DIR/sp-key-and-cert.pem"
if [[ ! -f "$KEYPEM" ]]; then
  openssl req -x509 -newkey rsa:2048 -nodes -keyout "$CERT_DIR/sp.key" -out "$CERT_DIR/sp.crt" -days 365 -subj "/CN=lm15-lab-sp" 2>/dev/null
  cat "$CERT_DIR/sp.key" "$CERT_DIR/sp.crt" > "$KEYPEM"
  chmod 600 "$CERT_DIR"/*
  az ad app credential reset --id "$APPID" --cert "@$CERT_DIR/sp.crt" --append -o none
fi

say "data-plane roles (service principal and you)"
for SCOPE in "$OAI_ID" "$FDY_ID"; do
  for ROLE in "Cognitive Services OpenAI User" "Cognitive Services User" "Azure AI User"; do
    az role assignment create --assignee-object-id "$SPOBJ" --assignee-principal-type ServicePrincipal --role "$ROLE" --scope "$SCOPE" -o none 2>/dev/null || true
    az role assignment create --assignee-object-id "$ME" --assignee-principal-type User --role "$ROLE" --scope "$SCOPE" -o none 2>/dev/null || true
  done
done

say "keys"
OAI_KEY=$(az cognitiveservices account keys list -n "$OAI" -g "$RG" --query key1 -o tsv)
FDY_KEY=$(az cognitiveservices account keys list -n "$FDY" -g "$RG" --query key1 -o tsv)

umask 077
cat > "$ENV_FILE" <<EOF
# lm15 Azure lab — written by research/cloud-hosts/azure/provision.sh. Secrets: never commit, never paste.
LM15_LAB_SUFFIX=$SUFFIX
AZURE_SUBSCRIPTION_ID=$SUB
AZURE_TENANT_ID=$TENANT
AZURE_CLIENT_ID=$APPID
AZURE_CLIENT_SECRET=$SECRET
AZURE_CLIENT_CERTIFICATE_PATH=$KEYPEM
AZURE_OPENAI_RESOURCE=$OAI
AZURE_OPENAI_API_KEY=$OAI_KEY
AZURE_OPENAI_DEPLOYMENT=$OPENAI_MODEL
ANTHROPIC_FOUNDRY_RESOURCE=$FDY
ANTHROPIC_FOUNDRY_LOCATION=$FDY_LOC
ANTHROPIC_FOUNDRY_API_KEY=$FDY_KEY
ANTHROPIC_FOUNDRY_MODEL=$CLAUDE_MODEL
EOF
chmod 600 "$ENV_FILE"

say "done"
echo "env file: $ENV_FILE  (source it: set -a; . $ENV_FILE; set +a)"
echo "Azure OpenAI: https://$OAI.openai.azure.com/openai/v1/  deployment $OPENAI_MODEL"
echo "Foundry:      https://$FDY.services.ai.azure.com/anthropic/v1/  claude deployment: $([[ $CLAUDE_OK == 1 ]] && echo yes || echo 'NOT YET (portal step above)')"
echo "Service principal $APPID with secret + certificate; roles assigned (propagation can take up to 5 minutes)."
