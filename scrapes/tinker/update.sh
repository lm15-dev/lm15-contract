#!/usr/bin/env bash
# Re-scrape the Tinker docs that bear on inference through lm15
# (tinker-docs.thinkingmachines.ai, native .md pages; index at
# https://tinker-docs.thinkingmachines.ai/llms.txt). Training pages are out of
# lm15's scope and not kept. models.json and serverless.json are the price
# tables Thinking Machines publishes as "the stable interface for scripts".
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://tinker-docs.thinkingmachines.ai"

PAGES=(
  "compatible-apis--openai.md=/tinker/compatible-apis/openai/index.md"
  "compatible-apis--anthropic.md=/tinker/compatible-apis/anthropic/index.md"
  "opencode.md=/tinker/opencode/index.md"
  "models-and-pricing.md=/tinker/models/models_and_pricing/index.md"
  "model-deprecations.md=/tinker/model-deprecations/index.md"
  "checkpoints.md=/tinker/howto/checkpoints/index.md"
  "data-model.md=/tinker/data-model/index.md"
  "under-the-hood.md=/tinker/under-the-hood/index.md"
  "restclient.md=/tinker/api-reference/restclient/index.md"
  "samplingclient.md=/tinker/api-reference/samplingclient/index.md"
  "cli--billing.md=/tinker/cli/billing/index.md"
  "types--billingusageevent.md=/tinker/api-reference/types/billingusageevent/index.md"
  "inkling.md=/cookbook/inkling/index.md"
  "inkling--thinking-effort.md=/cookbook/inkling/thinking-effort/index.md"
  "inkling--images.md=/cookbook/inkling/images/index.md"
  "inkling--audio.md=/cookbook/inkling/audio/index.md"
  "inkling--tml-renderers.md=/cookbook/inkling/tml-renderers/index.md"
  "deployment-basics.md=/cookbook/deployment/basics/index.md"
  "models.json=/tinker/models.json"
  "serverless.json=/tinker/serverless.json"
)

echo "Tinker docs -> $DIR"
for entry in "${PAGES[@]}"; do
  fetch_page "${entry%%=*}" "${BASE}${entry#*=}"
done
fetch_summary
