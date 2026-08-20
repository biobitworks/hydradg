#!/usr/bin/env bash
set -euo pipefail

# Run a named sequence of commands through run_logged.sh.
# Usage:
#   bash scripts/run_sequence.sh LABEL command_file.txt
#
# command_file.txt: one shell command per non-empty, non-comment line.
# Stops on first failure and leaves logs/LAST_ERROR_FOR_CHAT.txt.

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 LABEL command_file.txt" >&2
  exit 64
fi

LABEL="$1"
FILE="$2"

if [[ ! -f "$FILE" ]]; then
  echo "Command file not found: $FILE" >&2
  exit 66
fi

N=0
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "${line//[[:space:]]/}" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  N=$((N+1))
  bash scripts/run_logged.sh "${LABEL}_${N}" -- bash -lc "$line"
done < "$FILE"
