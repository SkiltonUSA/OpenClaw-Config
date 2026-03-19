#!/usr/bin/env bash
set -euo pipefail

# Usage: flights_sky_details.sh "<FULL_URL_WITH_QUERY_PARAMS>"
# Example:
# flights_sky_details.sh "https://flights-sky.p.rapidapi.com/web/flights/details?itineraryId=...&adults=1"

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  echo "Usage: $(basename "$0") \"<FULL_URL_WITH_QUERY_PARAMS>\""
  echo "Env vars: RAPIDAPI_KEY (required), RAPIDAPI_HOST (optional; default flights-sky.p.rapidapi.com)"
  exit 0
fi

URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "Error: Missing URL argument." >&2
  echo "Usage: $(basename "$0") \"<FULL_URL_WITH_QUERY_PARAMS>\"" >&2
  exit 1
fi

if [[ -z "${RAPIDAPI_KEY:-}" ]]; then
  echo "Error: RAPIDAPI_KEY is not set." >&2
  echo "Set it like: export RAPIDAPI_KEY='your_new_key'" >&2
  exit 1
fi

RAPIDAPI_HOST="${RAPIDAPI_HOST:-flights-sky.p.rapidapi.com}"

curl --silent --show-error --fail \
  --request GET \
  --url "$URL" \
  --header 'Content-Type: application/json' \
  --header "x-rapidapi-host: ${RAPIDAPI_HOST}" \
  --header "x-rapidapi-key: ${RAPIDAPI_KEY}"

echo
