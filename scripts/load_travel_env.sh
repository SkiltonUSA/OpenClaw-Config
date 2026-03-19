#!/usr/bin/env bash
set -euo pipefail

# Source `.env.travel` from workspace root if present.
# shellcheck disable=SC1091
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env.travel"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi
