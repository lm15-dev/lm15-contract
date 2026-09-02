#!/bin/bash
# Re-scrape OpenAI API docs from native .md / index.md endpoints
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://developers.openai.com"

# Format: "filename=path"
# Pages using .md suffix directly
MD_PAGES=(
  "overview.md=/api/reference/overview.md"
  "responses-overview.md=/api/reference/responses/overview.md"
  "chat-completions-overview.md=/api/reference/chat-completions/overview.md"
  # Guides (moved from /docs/guides/ to /api/docs/guides/ — the old paths 404 since 2026-09)
  "guide--error-codes.md=/api/docs/guides/error-codes.md"
  "guide--rate-limits.md=/api/docs/guides/rate-limits.md"
  "guide--latency.md=/api/docs/guides/latency-optimization.md"
  "guide--production.md=/api/docs/guides/production-best-practices.md"
  "guide--reasoning.md=/api/docs/guides/reasoning.md"
  "guide--streaming.md=/api/docs/guides/streaming-responses.md"
  "guide--function-calling.md=/api/docs/guides/function-calling.md"
  "guide--structured-output.md=/api/docs/guides/structured-outputs.md"
  "guide--text.md=/api/docs/guides/text.md"
  "guide--audio.md=/api/docs/guides/audio.md"
  "guide--embeddings.md=/api/docs/guides/embeddings.md"
)

# Pages using /index.md suffix (Stainless-generated API reference)
INDEX_PAGES=(
  # Responses API
  "responses--create.md=/api/reference/resources/responses/methods/create"
  "responses--retrieve.md=/api/reference/resources/responses/methods/retrieve"
  "responses--cancel.md=/api/reference/resources/responses/methods/cancel"
  "responses--delete.md=/api/reference/resources/responses/methods/delete"
  "responses--input-items.md=/api/reference/resources/responses/subresources/input_items/methods/list"
  "responses--count-tokens.md=/api/reference/resources/responses/subresources/input_tokens/methods/count"
  # Chat Completions
  "chat--create.md=/api/reference/resources/chat/subresources/completions/methods/create"
  # Embeddings
  "embeddings--create.md=/api/reference/resources/embeddings/methods/create"
  # Models
  "models--list.md=/api/reference/resources/models/methods/list"
  "models--retrieve.md=/api/reference/resources/models/methods/retrieve"
  # Files
  "files--create.md=/api/reference/resources/files/methods/create"
  "files--list.md=/api/reference/resources/files/methods/list"
  "files--retrieve.md=/api/reference/resources/files/methods/retrieve"
  "files--delete.md=/api/reference/resources/files/methods/delete"
  "files--content.md=/api/reference/resources/files/methods/content"
  # Batches
  "batches--create.md=/api/reference/resources/batches/methods/create"
  "batches--list.md=/api/reference/resources/batches/methods/list"
  "batches--retrieve.md=/api/reference/resources/batches/methods/retrieve"
  "batches--cancel.md=/api/reference/resources/batches/methods/cancel"
  # Images
  "images--generate.md=/api/reference/resources/images/methods/generate"
  "images--edit.md=/api/reference/resources/images/methods/edit"
  # Audio
  "audio--speech.md=/api/reference/resources/audio/subresources/speech/methods/create"
  "audio--transcription.md=/api/reference/resources/audio/subresources/transcriptions/methods/create"
  # Realtime
  "realtime--sessions.md=/api/reference/resources/realtime/subresources/sessions/methods/create"
)

for pair in "${MD_PAGES[@]}"; do
  fetch_page "${pair%%=*}" "${BASE}${pair#*=}"
done

for pair in "${INDEX_PAGES[@]}"; do
  fetch_page "${pair%%=*}" "${BASE}${pair#*=}/index.md"
done

# Streaming events page (jina fallback — JS-rendered, no native .md)
tmp="$(mktemp)"
curl -sL "https://r.jina.ai/https://developers.openai.com/api/reference/resources/chat/subresources/completions/streaming-events" \
  | awk '/^Markdown Content:/{found=1; next} found' > "$tmp"
if [[ -s "$tmp" ]]; then
  mv "$tmp" "$DIR/chat--streaming.md"
  echo "  chat--streaming.md (jina) ... $(wc -l < "$DIR/chat--streaming.md") lines"
else
  rm -f "$tmp"
  echo "  chat--streaming.md (jina) ... FAILED (empty)" >&2
  FETCH_FAILURES=$((FETCH_FAILURES + 1))
fi

fetch_summary
