#!/bin/bash
# Chain EXP-008-Q38 closeout → EXP-009-Q38 after execute completes.
set -euo pipefail
REPO="/Users/byron/projects/active/hydradg-qwen38-model-replay-20260828"
RAW="$REPO/eval/ic_failure_learning_20260827/qwen38_model_replay_20260828/EXP-008-Q38/RAW_OUTPUTS.jsonl"
TARGET=150
cd "$REPO"
echo "[q38-chain] waiting for $TARGET rows in EXP-008-Q38..."
while [[ $(wc -l < "$RAW" 2>/dev/null || echo 0) -lt $TARGET ]]; do
  n=$(wc -l < "$RAW" 2>/dev/null || echo 0)
  echo "[q38-chain] EXP-008-Q38 progress: $n/$TARGET $(date -u +%H:%M:%S)"
  sleep 120
done
echo "[q38-chain] EXP-008-Q38 execute complete; closeout..."
python3 scripts/run_qwen38_model_replay.py --phase exp008-q38-closeout
git add eval/ic_failure_learning_20260827/qwen38_model_replay_20260828/EXP-008-Q38/
git commit -m "$(cat <<'EOF'
exp008-q38: replay structured retrieval under qwen3.8

Successor replay of EXP-008 flat-prose vs structured-FCG under frozen
qwen3.8:27b digest; E06_POWER_STATE=KNOWN_LIMITED preserved.

EOF
)"
git push origin hack-hydra/qwen38-model-replay-20260828
python3 scripts/run_qwen38_model_replay.py --phase exp009-q38-prereg
python3 scripts/run_qwen38_model_replay.py --phase exp009-q38-execute
python3 scripts/run_qwen38_model_replay.py --phase exp009-q38-closeout
git add eval/ic_failure_learning_20260827/qwen38_model_replay_20260828/EXP-009-Q38/
git commit -m "$(cat <<'EOF'
exp009-q38: replay causal ordering under qwen3.8

Successor replay of EXP-009 atom-ordering contract under qwen3.8:27b;
canonical EXP-008/009/010 mechanistic lane unchanged.

EOF
)"
git push origin hack-hydra/qwen38-model-replay-20260828
echo "[q38-chain] complete $(git rev-parse HEAD)"
