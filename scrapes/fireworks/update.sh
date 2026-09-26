#!/usr/bin/env bash
# Re-scrape Fireworks AI inference docs (docs.fireworks.ai, native .md
# endpoints; index at https://docs.fireworks.ai/llms.txt).
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://docs.fireworks.ai"

PAGES=(
  "openai-compatibility.md=/tools-sdks/openai-compatibility.md"
  "querying-text-models.md=/guides/querying-text-models.md"
  "chat--create.md=/api-reference/post-chatcompletions.md"
  "function-calling.md=/guides/function-calling.md"
  "reasoning.md=/guides/reasoning.md"
  "structured-outputs.md=/structured-responses/structured-response-formatting.md"
  "vision.md=/guides/querying-vision-language-models.md"
  "prompt-caching.md=/guides/prompt-caching.md"
  "inference-error-codes.md=/guides/inference-error-codes.md"
  "reliability.md=/guides/reliability.md"
  "serverless--overview.md=/serverless/overview.md"
  "serverless--pricing.md=/serverless/pricing.md"
  "serverless--rate-limits.md=/serverless/rate-limits.md"
  "concepts.md=/getting-started/concepts.md"
  "batch.md=/guides/batch-inference.md"
)

echo "Fireworks docs -> $DIR"
for entry in "${PAGES[@]}"; do
  fetch_page "${entry%%=*}" "${BASE}${entry#*=}"
done
fetch_summary
