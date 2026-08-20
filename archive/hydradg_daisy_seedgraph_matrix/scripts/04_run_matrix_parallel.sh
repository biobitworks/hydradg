#!/usr/bin/env bash
set -euo pipefail

REPO="${HYDRADG_REPO:-/Users/byron/projects/active/hydradg}"
PKG="$REPO/HydraDG_DaisyTrain_v0.3.7"
HARNESS="${MATRIX_HARNESS:-$REPO/hydradg_daisy_seedgraph_matrix/scripts}"
if [[ ! -d "$HARNESS" && -d "$REPO/local_matrix_harness" ]]; then
  HARNESS="$REPO/local_matrix_harness"
fi
RAW="$PKG/evidence/track03/matrix-20260819/frozen/longmemeval_full500.raw.json"
SG="$PKG/evidence/track03/matrix-20260819/seedgraph"
CACHE="$SG/cache"
TOKEN="${BEST_USE_RUNTIME:-$HOME/.local/share/hydradg-best-use}/hydradb-auth-token"
OUT="${BEST_USE_RUNTIME:-$HOME/.local/share/hydradg-best-use}/eval/matrix-20260819"
ANALYZER="$PKG/scripts/analyze_best_use_ablation.py"
RUNNER="$HARNESS/03_run_matrix_cell.py"

mkdir -p "$OUT"

run_one () {
  local rep="$1" k="$2" r="$3"
  local extractor cachearg=""
  if [[ "$rep" == "raw" ]]; then
    extractor="none"
  else
    extractor="heuristic"
    cachearg="--cache-dir $CACHE"
  fi
  local ns="default"
  local stem="$OUT/${rep}_k${k}_r${r}"
  echo "START $rep k=$k r=$r stem=$stem"
  python3 "$RUNNER" "$RAW" \
    --scripts-dir "$PKG/scripts" \
    --namespace "$ns" \
    --token-file "$TOKEN" \
    --representation "$rep" \
    --extractor "$extractor" \
    $cachearg \
    --k "$k" \
    --out "$stem.jsonl" \
    > "$stem.log" 2>&1
  python3 "$ANALYZER" "$stem.jsonl" --out "$stem.stats.json" --expected-n 500 --bootstrap 5000 \
    >> "$stem.log" 2>&1
  shasum -a 256 "$stem.jsonl.canonical.jsonl" "$stem.stats.json" > "$stem.sha256"
  echo "DONE $rep k=$k r=$r"
}

export -f run_one
export REPO PKG HARNESS RAW SG CACHE TOKEN OUT ANALYZER RUNNER

# Four independent cells in parallel per replicate wave.
for r in 1 2 3; do
  run_one raw 5 "$r" &
  run_one raw 10 "$r" &
  run_one seedgraph 5 "$r" &
  run_one seedgraph 10 "$r" &
  wait
done

echo "MATRIX_RUN_COMPLETE"
