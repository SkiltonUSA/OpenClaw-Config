#!/usr/bin/env bash
set -euo pipefail

# Yahoo Weather via RapidAPI
# Usage:
#   weather_yahoo_forecast.sh "Washington,DC"
#   weather_yahoo_forecast.sh "Key West,FL" c

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/load_travel_env.sh"

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  echo "Usage: $(basename "$0") <location> [unit]"
  echo "  location: city/region string (e.g., 'Washington,DC')"
  echo "  unit: f or c (default: f)"
  echo "Env vars: RAPIDAPI_KEY (required), YAHOO_WEATHER_RAPIDAPI_HOST (optional; default yahoo-weather5.p.rapidapi.com)"
  exit 0
fi

LOCATION="${1:-}"
UNIT="${2:-f}"

if [[ -z "$LOCATION" ]]; then
  echo "Error: location is required." >&2
  exit 1
fi

if [[ "$UNIT" != "f" && "$UNIT" != "c" ]]; then
  echo "Error: unit must be 'f' or 'c'." >&2
  exit 1
fi

if [[ -z "${RAPIDAPI_KEY:-}" ]]; then
  echo "Error: RAPIDAPI_KEY is not set." >&2
  echo "Set it in .env.travel or export RAPIDAPI_KEY='your_key'" >&2
  exit 1
fi

RAPIDAPI_HOST="${YAHOO_WEATHER_RAPIDAPI_HOST:-yahoo-weather5.p.rapidapi.com}"
ENC_LOCATION="$(python3 - <<'PY' "$LOCATION"
import urllib.parse, sys
print(urllib.parse.quote(sys.argv[1]))
PY
)"

URL="https://${RAPIDAPI_HOST}/weather?location=${ENC_LOCATION}&format=json&u=${UNIT}"

curl --silent --show-error --fail \
  --request GET \
  --url "$URL" \
  --header 'Content-Type: application/json' \
  --header "x-rapidapi-host: ${RAPIDAPI_HOST}" \
  --header "x-rapidapi-key: ${RAPIDAPI_KEY}"

echo
