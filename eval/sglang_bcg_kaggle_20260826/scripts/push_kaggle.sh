#!/usr/bin/env bash
# Push exactly one private Kaggle GPU kernel for SGLang BCG stress.
# Credentials: ~/.kaggle/kaggle.json via env (never echoed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
EXP="$ROOT/eval/sglang_bcg_kaggle_20260826"
KAGGLE_DIR="$EXP/kaggle"
TOOL_KAGGLE="${HYDRADG_KAGGLE_CLI:-$ROOT/.tools/kaggle_venv/bin/kaggle}"

if [[ ! -x "$TOOL_KAGGLE" ]]; then
  echo "KAGGLE_CLI_MISSING path=$TOOL_KAGGLE" >&2
  exit 1
fi

export KAGGLE_USERNAME
export KAGGLE_KEY
KAGGLE_USERNAME="$(python3 -c "import json; d=json.load(open('$HOME/.kaggle/kaggle.json')); print(d.get('KAGGLE_USERNAME') or d.get('username') or '')")"
KAGGLE_KEY="$(python3 -c "import json; d=json.load(open('$HOME/.kaggle/kaggle.json')); print(d.get('KAGGLE_KEY') or d.get('key') or '')")"

KERNEL_REF="biobitworks/hydradg-sglang-bcg-stress-20260826"
echo "KAGGLE_CLI=$TOOL_KAGGLE"
echo "KAGGLE_KERNEL_REF=$KERNEL_REF"
echo "[push] pushing private GPU kernel from $KAGGLE_DIR"
"$TOOL_KAGGLE" kernels push -p "$KAGGLE_DIR"
echo "[push] done"
echo "KAGGLE_KERNEL_REF=$KERNEL_REF" | tee "$EXP/receipts/KAGGLE_PUSH_REF.txt"
unset KAGGLE_KEY
