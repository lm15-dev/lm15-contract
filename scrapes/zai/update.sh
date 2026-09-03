#!/bin/bash
# Re-scrape Z.AI API docs (docs.z.ai, native .md endpoints; index at
# https://docs.z.ai/llms.txt).  Same 200-with-body guard as the others.
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://docs.z.ai"

PAGES=(
  "introduction.md=/api-reference/introduction.md"
  "chat--create.md=/api-reference/llm/chat-completion.md"
  "api-code.md=/api-reference/api-code.md"
  "overview.md=/guides/overview/overview.md"
  "quick-start.md=/guides/overview/quick-start.md"
  "concept-param.md=/guides/overview/concept-param.md"
  "migrate-to-glm-new.md=/guides/overview/migrate-to-glm-new.md"
  "model--glm-5.3.md=/guides/llm/glm-5.3.md"
  "model--glm-5.2.md=/guides/llm/glm-5.2.md"
  "model--glm-5.3-flash.md=/guides/vlm/glm-5.3-flash.md"
  "guide--thinking.md=/guides/capabilities/thinking.md"
  "guide--thinking-mode.md=/guides/capabilities/thinking-mode.md"
  "guide--streaming.md=/guides/capabilities/streaming.md"
  "guide--stream-tool.md=/guides/capabilities/stream-tool.md"
  "guide--function-calling.md=/guides/capabilities/function-calling.md"
  "guide--struct-output.md=/guides/capabilities/struct-output.md"
  "guide--cache.md=/guides/capabilities/cache.md"
  "guide--http.md=/guides/develop/http/introduction.md"
  "guide--openai-sdk.md=/guides/develop/openai/python.md"
  "devpack--overview.md=/devpack/overview.md"
  "devpack--usage-policy.md=/devpack/usage-policy.md"
  "release-notes.md=/release-notes/new-released.md"
)

echo "Z.AI docs -> $DIR"
for entry in "${PAGES[@]}"; do
  fetch_page "${entry%%=*}" "${BASE}${entry#*=}"
done
fetch_summary
