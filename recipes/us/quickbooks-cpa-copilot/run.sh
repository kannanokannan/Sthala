#!/usr/bin/env bash
set -euo pipefail
RECIPE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR=""; PROFILE="${RECIPE_DIR}/profile.yaml"
while [[ $# -gt 0 ]]; do
  case "$1" in --data) DATA_DIR="$2"; shift 2 ;; --profile) PROFILE="$2"; shift 2 ;; *) echo "Unknown: $1"; exit 1 ;; esac
done
[[ -z "$DATA_DIR" ]] && { echo "Usage: bash run.sh --data /path"; exit 1; }
mkdir -p "${DATA_DIR}/output" "${RECIPE_DIR}/audit"
LOG="${RECIPE_DIR}/audit/run.log"
echo "[$(date -u +%FT%TZ)] run started" >> "$LOG"
for stage in ingest extract verify compute narrate; do
  echo "[sthala] → ${stage}"
  python "${RECIPE_DIR}/pipeline/${stage}.py" --profile "$PROFILE" --data "$DATA_DIR" --log "$LOG"
  echo "[$(date -u +%FT%TZ)] stage=${stage} OK" >> "$LOG"
done
echo "[sthala] Done. Report: ${DATA_DIR}/output/report.md"
