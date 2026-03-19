#!/usr/bin/env bash
set -euo pipefail

# Tourist Attraction photos endpoint (RapidAPI)
# Usage:
#   tourist_attraction_photos.sh <location_id> [offset] [language] [currency]
# Example:
#   tourist_attraction_photos.sh 8797440 0 en_US USD

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/load_travel_env.sh"

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  echo "Usage: $(basename "$0") <location_id> [offset] [language] [currency]"
  echo "Env vars: RAPIDAPI_KEY (required), TOURIST_ATTRACTION_RAPIDAPI_HOST (optional; default tourist-attraction.p.rapidapi.com)"
  exit 0
fi

LOCATION_ID="${1:-}"
OFFSET="${2:-0}"
LANGUAGE="${3:-en_US}"
CURRENCY="${4:-USD}"

if [[ -z "$LOCATION_ID" ]]; then
  echo "Error: location_id is required." >&2
  exit 1
fi

if [[ -z "${RAPIDAPI_KEY:-}" ]]; then
  echo "Error: RAPIDAPI_KEY is not set." >&2
  echo "Set it in .env.travel or export RAPIDAPI_KEY='your_key'" >&2
  exit 1
fi

RAPIDAPI_HOST="${TOURIST_ATTRACTION_RAPIDAPI_HOST:-tourist-attraction.p.rapidapi.com}"
URL="https://${RAPIDAPI_HOST}/photos"

PAYLOAD=$(cat <<JSON
{"location_id":"${LOCATION_ID}","language":"${LANGUAGE}","currency":"${CURRENCY}","offset":"${OFFSET}"}
JSON
)

curl --silent --show-error --fail \
  --request POST \
  --url "$URL" \
  --header 'Content-Type: application/json' \
  --header "x-rapidapi-host: ${RAPIDAPI_HOST}" \
  --header "x-rapidapi-key: ${RAPIDAPI_KEY}" \
  --data "$PAYLOAD"

echo
