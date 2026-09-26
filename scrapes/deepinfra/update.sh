#!/usr/bin/env bash
# Re-scrape DeepInfra docs (docs.deepinfra.com, native .md endpoints; index
# at https://docs.deepinfra.com/llms.txt — deepinfra.com/docs/* answers
# 200 with the HTML app for every path, so it is not the source).
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://docs.deepinfra.com"

PAGES=(
  "index.md=/index.md"
  "chat--overview.md=/chat/overview.md"
  "chat--create.md=/api-reference/chat-completions/openai-chat-completions.md"
  "streaming.md=/chat/streaming.md"
  "tool-calling.md=/chat/tool-calling.md"
  "structured-outputs.md=/chat/structured-outputs.md"
  "reasoning.md=/chat/reasoning.md"
  "prompt-caching.md=/chat/prompt-caching.md"
  "prompt-cache-retention.md=/chat/prompt-cache-retention.md"
  "log-probs.md=/chat/log-probs.md"
  "vision.md=/chat/vision.md"
  "models--openai.md=/api-reference/models/openai-models.md"
  "authentication.md=/account/authentication.md"
  "rate-limits.md=/account/rate-limits.md"
  "data-privacy.md=/account/data-privacy.md"
  "batch--introduction.md=/batch/introduction.md"
)

echo "DeepInfra docs -> $DIR"
for entry in "${PAGES[@]}"; do
  fetch_page "${entry%%=*}" "${BASE}${entry#*=}"
done
fetch_summary
