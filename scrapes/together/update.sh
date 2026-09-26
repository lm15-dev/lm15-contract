#!/usr/bin/env bash
# Re-scrape Together AI inference docs (docs.together.ai, native .md
# endpoints; index at https://docs.together.ai/llms.txt).  Same
# 200-with-body guard as the others (fetch.sh).
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://docs.together.ai"

PAGES=(
  "openai-compatibility.md=/docs/inference/openai-compatibility.md"
  "chat--overview.md=/docs/inference/chat/overview.md"
  "chat--parameters.md=/docs/inference/chat/parameters.md"
  "chat--create.md=/reference/chat-completions.md"
  "structured-outputs.md=/docs/inference/chat/structured-outputs.md"
  "reasoning.md=/docs/inference/chat/reasoning.md"
  "prompt-caching.md=/docs/inference/chat/prompt-caching.md"
  "logprobs.md=/docs/inference/chat/logprobs.md"
  "function-calling--overview.md=/docs/inference/function-calling/overview.md"
  "function-calling--single-call.md=/docs/inference/function-calling/single-call.md"
  "function-calling--parallel.md=/docs/inference/function-calling/parallel.md"
  "function-calling--agentic.md=/docs/inference/function-calling/agentic.md"
  "function-calling--best-practices.md=/docs/inference/function-calling/best-practices.md"
  "vision--overview.md=/docs/inference/vision/overview.md"
  "vision--inputs.md=/docs/inference/vision/inputs.md"
  "models--list.md=/reference/models.md"
  "serverless--overview.md=/docs/serverless/overview.md"
  "serverless--models.md=/docs/serverless/models.md"
  "serverless--rate-limits.md=/docs/serverless/rate-limits.md"
  "error-codes.md=/docs/error-codes.md"
  "authentication.md=/docs/api-keys-authentication.md"
  "account-management.md=/docs/account-management.md"
  "privacy-and-security.md=/docs/privacy-and-security.md"
  "batch--overview.md=/docs/inference/batch/overview.md"
)

echo "Together AI docs -> $DIR"
for entry in "${PAGES[@]}"; do
  fetch_page "${entry%%=*}" "${BASE}${entry#*=}"
done
fetch_summary
