#!/usr/bin/env bash
set -euo pipefail

# One command wrapper for travel API calls + concise summaries.
# Requires: RAPIDAPI_KEY env var
#
# Usage:
#   travel_api_assist.sh details-summary "https://flights-sky.p.rapidapi.com/web/flights/details?..."
#   travel_api_assist.sh min-price-summary JFK LOS

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$ROOT_DIR/scripts"
SUMMARIZER="$SCRIPTS_DIR/travel_summarize.py"

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -lt 1 ]]; then
  cat <<USAGE
Usage:
  $(basename "$0") details-summary "<FULL_DETAILS_URL>"
  $(basename "$0") min-price-summary <DEPART_IATA> <ARRIVAL_IATA>

Environment:
  RAPIDAPI_KEY (required)
USAGE
  exit 0
fi

CMD="$1"
shift

TMP_JSON="$(mktemp)"
cleanup() { rm -f "$TMP_JSON"; }
trap cleanup EXIT

case "$CMD" in
  details-summary)
    URL="${1:-}"
    if [[ -z "$URL" ]]; then
      echo "Error: details-summary requires full URL argument." >&2
      exit 1
    fi
    "$SCRIPTS_DIR/flights_sky_details.sh" "$URL" > "$TMP_JSON"
    python3 "$SUMMARIZER" details "$TMP_JSON"
    ;;

  min-price-summary)
    DEPART="${1:-}"
    ARRIVAL="${2:-}"
    if [[ -z "$DEPART" || -z "$ARRIVAL" ]]; then
      echo "Error: min-price-summary requires <DEPART_IATA> <ARRIVAL_IATA>." >&2
      exit 1
    fi
    "$SCRIPTS_DIR/booking_min_price_oneway.sh" "$DEPART" "$ARRIVAL" > "$TMP_JSON"
    python3 "$SUMMARIZER" min-price "$TMP_JSON"
    ;;

  *)
    echo "Error: unknown command '$CMD'" >&2
    echo "Run with --help for usage." >&2
    exit 1
    ;;
esac
