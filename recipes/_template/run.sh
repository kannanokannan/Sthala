#!/usr/bin/env bash
# run.sh — entry point for this recipe
# Usage: bash run.sh --data /path/to/data [--profile profile.yaml]
set -euo pipefail

RECIPE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR=""
PROFILE="${RECIPE_DIR}/profile.yaml"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --data)     DATA_DIR="$2"; shift 2 ;;
    --profile)  PROFILE="$2";  shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$DATA_DIR" ]]; then
  echo "Usage: bash run.sh --data /path/to/data"
  exit 1
fi

mkdir -p "${DATA_DIR}/output" "${RECIPE_DIR}/audit"
LOG="${RECIPE_DIR}/audit/run.log"
echo "[$(date -u +%FT%TZ)] run started — data=${DATA_DIR}" >> "$LOG"

echo "[sthala] Starting recipe pipeline..."

for stage in ingest extract verify compute narrate; do
  echo "[sthala] Stage: ${stage}"
  python "${RECIPE_DIR}/pipeline/${stage}.py" \
    --profile "$PROFILE" \
    --data    "$DATA_DIR" \
    --log     "$LOG"
  echo "[$(date -u +%FT%TZ)] stage=${stage} OK" >> "$LOG"
done

echo "[sthala] Done. Output at: ${DATA_DIR}/output/"
echo "[$(date -u +%FT%TZ)] run complete" >> "$LOG"
