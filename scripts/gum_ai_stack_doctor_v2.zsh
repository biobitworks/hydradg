#!/usr/bin/env zsh
# Gum AI Stack Doctor v2 — successor to NOT_LOCATED gum_ai_stack_doctor.zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${GUM_DOCTOR_OUT:-$ROOT/eval/newinml_final_daisy_20260829/execution/lane0_gum}"
REPAIR=0
for arg in "$@"; do
  case "$arg" in
    --repair) REPAIR=1 ;;
    --read-only) REPAIR=0 ;;
  esac
done
ARGS=(--out-dir "$OUT")
if (( REPAIR )); then
  ARGS+=(--repair)
fi
exec python3 "$ROOT/scripts/gum_doctor_v2.py" "${ARGS[@]}"
