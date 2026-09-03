#!/bin/bash
# Re-scrape DeepSeek API docs (api-docs.deepseek.com).  The site is
# Docusaurus HTML with no Markdown endpoint; html2text.py keeps the
# <article> text only.  Same 200-with-body guard as the other scrapers.
set -e
DIR="$(cd "$(dirname "$0")/pages" && pwd)"
source "$(dirname "$0")/../fetch.sh"
BASE="https://api-docs.deepseek.com"
HERE="$(cd "$(dirname "$0")" && pwd)"

PAGES=(
  "first-call.md=/"
  "chat--create.md=/api/create-chat-completion"
  "models--list.md=/api/list-models"
  "guide--thinking-mode.md=/guides/thinking_mode"
  "guide--reasoning-model.md=/guides/reasoning_model"
  "guide--json-mode.md=/guides/json_mode"
  "guide--function-calling.md=/guides/function_calling"
  "guide--chat-prefix-completion.md=/guides/chat_prefix_completion"
  "guide--kv-cache.md=/guides/kv_cache"
  "guide--anthropic-api.md=/guides/anthropic_api"
  "pricing.md=/quick_start/pricing"
  "error-codes.md=/quick_start/error_codes"
  "parameter-settings.md=/quick_start/parameter_settings"
  "rate-limit.md=/quick_start/rate_limit"
  "updates.md=/updates"
)

fetch_article() {
  local file="$1" url="$2" tmp code
  tmp="$(mktemp)"
  code="$(curl -sL -o "$tmp" -w '%{http_code}' "$url" || echo "000")"
  if [[ "$code" == "200" && -s "$tmp" ]]; then
    python3 "$HERE/html2text.py" < "$tmp" > "$DIR/$file"
    rm -f "$tmp"
    echo "  ${file} ... $(wc -l < "$DIR/$file") lines"
  else
    rm -f "$tmp"
    echo "  ${file} ... FAILED (HTTP ${code}) ${url}" >&2
    FETCH_FAILURES=$((FETCH_FAILURES + 1))
  fi
  sleep 0.3
}

echo "DeepSeek docs -> $DIR"
for entry in "${PAGES[@]}"; do
  fetch_article "${entry%%=*}" "${BASE}${entry#*=}"
done
fetch_summary
