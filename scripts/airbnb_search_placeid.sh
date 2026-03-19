#!/usr/bin/env bash
set -euo pipefail

# Airbnb search by placeId (RapidAPI)
# Usage:
#   airbnb_search_placeid.sh <placeId> [adults] [currency]
# Example:
#   airbnb_search_placeid.sh ChIJ7cv00DwsDogRAMDACa2m4K8 4 USD

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/load_travel_env.sh"

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  echo "Usage: $(basename "$0") <placeId> [adults] [currency]"
  echo "Env vars: RAPIDAPI_KEY (required), AIRBNB_RAPIDAPI_HOST (optional; default airbnb19.p.rapidapi.com)"
  exit 0
fi

PLACE_ID="${1:-}"
ADULTS="${2:-1}"
CURRENCY="${3:-USD}"

if [[ -z "$PLACE_ID" ]]; then
  echo "Error: placeId is required." >&2
  exit 1
fi

if [[ -z "${RAPIDAPI_KEY:-}" ]]; then
  echo "Error: RAPIDAPI_KEY is not set." >&2
  echo "Set it in .env.travel or export RAPIDAPI_KEY='your_key'" >&2
  exit 1
fi

RAPIDAPI_HOST="${AIRBNB_RAPIDAPI_HOST:-airbnb19.p.rapidapi.com}"

URL="https://${RAPIDAPI_HOST}/api/v2/searchPropertyByPlaceId?placeId=${PLACE_ID}&adults=${ADULTS}&guestFavorite=false&ib=false&currency=${CURRENCY}"

curl --silent --show-error --fail \
  --request GET \
  --url "$URL" \
  --header 'Content-Type: application/json' \
  --header "x-rapidapi-host: ${RAPIDAPI_HOST}" \
  --header "x-rapidapi-key: ${RAPIDAPI_KEY}"

echo
