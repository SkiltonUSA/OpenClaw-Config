#!/usr/bin/env bash
set -euo pipefail

# Usage: booking_min_price_oneway.sh <DEPART_IATA> <ARRIVAL_IATA>
# Example: booking_min_price_oneway.sh JFK LOS

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  echo "Usage: $(basename "$0") <DEPART_IATA> <ARRIVAL_IATA>"
  echo "Env vars: RAPIDAPI_KEY (required), RAPIDAPI_HOST (optional; default booking-com18.p.rapidapi.com)"
  exit 0
fi

DEPART_ID="${1:-}"
ARRIVAL_ID="${2:-}"

if [[ -z "$DEPART_ID" || -z "$ARRIVAL_ID" ]]; then
  echo "Error: Missing required args." >&2
  echo "Usage: $(basename "$0") <DEPART_IATA> <ARRIVAL_IATA>" >&2
  exit 1
fi

if [[ -z "${RAPIDAPI_KEY:-}" ]]; then
  echo "Error: RAPIDAPI_KEY is not set." >&2
  echo "Set it like: export RAPIDAPI_KEY='your_new_key'" >&2
  exit 1
fi

RAPIDAPI_HOST="${RAPIDAPI_HOST:-booking-com18.p.rapidapi.com}"
URL="https://${RAPIDAPI_HOST}/flights/v2/min-price-oneway?departId=${DEPART_ID}&arrivalId=${ARRIVAL_ID}"

curl --silent --show-error --fail \
  --request GET \
  --url "$URL" \
  --header 'Content-Type: application/json' \
  --header "x-rapidapi-host: ${RAPIDAPI_HOST}" \
  --header "x-rapidapi-key: ${RAPIDAPI_KEY}"

echo
