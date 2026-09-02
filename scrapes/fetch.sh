#!/bin/bash
# Shared fetch step for the three update.sh scrapers.
#
# fetch_page FILE URL
#   Downloads URL into a temp file and moves it over pages/FILE only when the
#   server answered 200 with a non-empty body.  A 404, an empty body, or a
#   transport error leaves the cached copy untouched, prints the failure,
#   and is counted so the caller can exit non-zero.  The old `curl -sL >`
#   form wrote the literal "Not Found" over 17 good pages and reported
#   success (found 2026-09-02).
fetch_page() {
  local file="$1" url="$2" tmp code
  tmp="$(mktemp)"
  code="$(curl -sL -o "$tmp" -w '%{http_code}' "$url" || echo "000")"
  if [[ "$code" == "200" && -s "$tmp" ]]; then
    mv "$tmp" "$DIR/$file"
    echo "  ${file} ... $(wc -l < "$DIR/$file") lines"
  else
    rm -f "$tmp"
    echo "  ${file} ... FAILED (HTTP ${code}) ${url}" >&2
    FETCH_FAILURES=$((FETCH_FAILURES + 1))
  fi
  sleep 0.3
}

fetch_summary() {
  echo "---"
  echo "$(ls "$DIR"/*.md | wc -l) pages, $(du -sh "$DIR" | cut -f1)"
  if (( FETCH_FAILURES > 0 )); then
    echo "${FETCH_FAILURES} page(s) failed; cached copies kept. Fix the URL, do not commit a dead page." >&2
    exit 1
  fi
}

FETCH_FAILURES=0
