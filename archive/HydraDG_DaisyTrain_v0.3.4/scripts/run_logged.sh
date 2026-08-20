#!/usr/bin/env bash
set -uo pipefail

# Usage:
#   bash scripts/run_logged.sh LABEL -- command arg1 arg2 ...
#
# Outputs:
#   logs/<timestamp>_<label>.log              full stdout/stderr
#   logs/<timestamp>_<label>.meta.txt         command + environment metadata
#   logs/<timestamp>_<label>.ERROR.txt        compact failure bundle if nonzero
#   logs/LAST_ERROR_FOR_CHAT.txt              latest compact failure bundle
#   logs/LAST_SUCCESS.txt                     latest successful run summary
#
# The wrapper redacts common token/secret environment variable VALUES from metadata.
# It does not attempt to scrub secrets emitted by the wrapped command itself.

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 LABEL -- command [args...]" >&2
  exit 64
fi

LABEL="$1"
shift
if [[ "$1" != "--" ]]; then
  echo "Expected -- after LABEL" >&2
  exit 64
fi
shift

ROOT="${HYDRADG_ROOT:-$(pwd)}"
LOG_DIR="${HYDRADG_LOG_DIR:-$ROOT/logs}"
mkdir -p "$LOG_DIR"

TS="$(date '+%Y%m%d_%H%M%S')"
SAFE_LABEL="$(printf '%s' "$LABEL" | tr -cs 'A-Za-z0-9._-' '_')"
BASE="$LOG_DIR/${TS}_${SAFE_LABEL}"
LOG="${BASE}.log"
META="${BASE}.meta.txt"
ERR="${BASE}.ERROR.txt"

# Human-readable shell-escaped command.
CMD_ESCAPED=""
for arg in "$@"; do
  printf -v q '%q' "$arg"
  CMD_ESCAPED+="${q} "
done

{
  echo "label=$LABEL"
  echo "timestamp=$(date -Iseconds)"
  echo "pwd=$(pwd)"
  echo "command=$CMD_ESCAPED"
  echo "shell=${SHELL:-unknown}"
  echo "uname=$(uname -a 2>/dev/null || true)"
  echo "python=$(python --version 2>&1 || true)"
  echo "modal=$(modal --version 2>&1 || true)"
  echo "git_head=$(git rev-parse HEAD 2>/dev/null || true)"
  echo "git_branch=$(git branch --show-current 2>/dev/null || true)"
  echo "host=$(hostname 2>/dev/null || true)"
  echo "env_flags:"
  for k in PYTHONHASHSEED OMP_NUM_THREADS MKL_NUM_THREADS CUBLAS_WORKSPACE_CONFIG CUDA_VISIBLE_DEVICES; do
    printf '  %s=%s\n' "$k" "${!k-}"
  done
  # Never print values for common credential variables.
  for k in MODAL_TOKEN_ID MODAL_TOKEN_SECRET HF_TOKEN HUGGINGFACE_TOKEN GITHUB_TOKEN KAGGLE_KEY KAGGLE_USERNAME; do
    if [[ -n "${!k-}" ]]; then
      printf '  %s=<SET_REDACTED>\n' "$k"
    else
      printf '  %s=<UNSET>\n' "$k"
    fi
  done
} > "$META"

echo "=== HydraDG logged run ==="
echo "label:   $LABEL"
echo "log:     $LOG"
echo "meta:    $META"
echo "command: $CMD_ESCAPED"
echo

set +e
"$@" 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e

if [[ $RC -eq 0 ]]; then
  {
    echo "STATUS=SUCCESS"
    echo "LABEL=$LABEL"
    echo "EXIT_CODE=0"
    echo "LOG=$LOG"
    echo "META=$META"
    echo "COMMAND=$CMD_ESCAPED"
  } > "$LOG_DIR/LAST_SUCCESS.txt"
  echo
  echo "SUCCESS: $LABEL"
  echo "Full log: $LOG"
  exit 0
fi

# Compact failure bundle: metadata + high-signal grep + tail.
{
  echo "HYDRADG_ERROR_BUNDLE_V1"
  echo "STATUS=FAILED"
  echo "LABEL=$LABEL"
  echo "EXIT_CODE=$RC"
  echo "LOG=$LOG"
  echo "META=$META"
  echo
  echo "=== COMMAND ==="
  echo "$CMD_ESCAPED"
  echo
  echo "=== METADATA ==="
  cat "$META"
  echo
  echo "=== HIGH-SIGNAL ERROR LINES ==="
  grep -Ein \
    'error|exception|traceback|failed|failure|not found|no such file|modified during build|permission denied|mismatch|refus|invalid|timeout|killed|oom|out of memory|404|403|500|502|503' \
    "$LOG" | tail -n 80 || true
  echo
  echo "=== LAST 120 LOG LINES ==="
  tail -n 120 "$LOG" || true
} > "$ERR"

cp "$ERR" "$LOG_DIR/LAST_ERROR_FOR_CHAT.txt"

echo
echo "FAILED: $LABEL (exit $RC)"
echo "Compact error bundle:"
echo "  $ERR"
echo
echo "For ChatGPT, paste only:"
echo "  cat \"$LOG_DIR/LAST_ERROR_FOR_CHAT.txt\""
exit "$RC"
