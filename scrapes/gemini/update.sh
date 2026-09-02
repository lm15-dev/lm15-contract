#!/bin/bash
# Re-scrape Gemini API docs from native .md.txt endpoints
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"

declare -A PAGES=(
  ["generate-content.md"]="https://ai.google.dev/api/generate-content.md.txt"
  ["embeddings.md"]="https://ai.google.dev/api/embeddings.md.txt"
  ["models.md"]="https://ai.google.dev/api/models.md.txt"
  ["tokens.md"]="https://ai.google.dev/api/tokens.md.txt"
  ["caching.md"]="https://ai.google.dev/api/caching.md.txt"
  ["files.md"]="https://ai.google.dev/api/files.md.txt"
  ["live.md"]="https://ai.google.dev/api/live.md.txt"
  ["batch-mode.md"]="https://ai.google.dev/api/batch-mode.md.txt"
  ["interactions-api.md"]="https://ai.google.dev/api/interactions-api.md.txt"
  ["troubleshooting.md"]="https://ai.google.dev/gemini-api/docs/troubleshooting.md.txt"
  ["api-versions.md"]="https://ai.google.dev/gemini-api/docs/api-versions.md.txt"
  ["models-gemini.md"]="https://ai.google.dev/gemini-api/docs/models.md.txt"  # models/gemini 404s since 2026-09
  ["rate-limits.md"]="https://ai.google.dev/gemini-api/docs/rate-limits.md.txt"
  ["tokens-guide.md"]="https://ai.google.dev/gemini-api/docs/tokens.md.txt"
)

for file in "${!PAGES[@]}"; do
  fetch_page "$file" "${PAGES[$file]}"
done

fetch_summary
