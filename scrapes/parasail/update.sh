#!/usr/bin/env bash
# Re-scrape Parasail docs (docs.parasail.io, GitBook native .md endpoints;
# index at https://docs.parasail.io/llms.txt).
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://docs.parasail.io/parasail-docs"

PAGES=(
  "serverless-quickstart.md=/quickstart/serverless.md"
  "serverless--overview.md=/products/overview.md"
  "serverless--models.md=/products/overview/models.md"
  "model-specific-notes.md=/products/overview/model-specific-notes.md"
  "authentication.md=/api-reference/authentication.md"
  "chat--create.md=/api-reference/chat-completions.md"
  "parameters.md=/api-reference/parameters.md"
  "models-endpoint.md=/api-reference/models-endpoint.md"
  "guide--chat-completions.md=/guides/chat-completions.md"
  "guide--structured-output.md=/guides/structured-output.md"
  "guide--tool-function-calling.md=/guides/tool-function-calling.md"
  "guide--multi-modal.md=/guides/multi-modal.md"
  "retries-and-idempotency.md=/operate-in-production/retries-and-idempotency.md"
  "limits-and-quotas.md=/operate-in-production/limits-and-quotas.md"
  "security--overview.md=/security-and-account-management/overview.md"
  "account-api-keys.md=/security-and-account-management/account-api-keys.md"
  "pricing.md=/billing/pricing.md"
)

echo "Parasail docs -> $DIR"
for entry in "${PAGES[@]}"; do
  fetch_page "${entry%%=*}" "${BASE}${entry#*=}"
done
fetch_summary
