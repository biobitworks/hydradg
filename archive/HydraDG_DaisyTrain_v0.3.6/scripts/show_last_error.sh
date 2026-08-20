#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${HYDRADG_LOG_DIR:-$(pwd)/logs}"
ERR="$LOG_DIR/LAST_ERROR_FOR_CHAT.txt"

if [[ -f "$ERR" ]]; then
  cat "$ERR"
else
  echo "No LAST_ERROR_FOR_CHAT.txt exists in $LOG_DIR"
  echo "Recent logs:"
  ls -1t "$LOG_DIR" 2>/dev/null | head -n 20 || true
fi
