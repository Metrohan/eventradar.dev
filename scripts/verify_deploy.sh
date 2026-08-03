#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-12}"
RETRY_DELAY="${RETRY_DELAY:-5}"

endpoints=(
  "/health"
  "/api/events?active_only=true"
  "/api/sources"
)

for endpoint in "${endpoints[@]}"; do
  url="${BASE_URL}${endpoint}"
  healthy=false

  for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do
    if curl --fail --silent --show-error --max-time 10 "$url" >/dev/null; then
      echo "Health check passed: $endpoint"
      healthy=true
      break
    fi

    echo "Health check attempt $attempt/$MAX_ATTEMPTS failed: $endpoint"
    sleep "$RETRY_DELAY"
  done

  if [[ "$healthy" != "true" ]]; then
    echo "Deploy verification failed: $endpoint" >&2
    exit 1
  fi
done

echo "Deploy verification passed."
