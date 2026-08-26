#!/usr/bin/env bash
# Unattended Kaggle watcher: poll >=60s, collect on terminal, hash, receipt, stop.
# No LLM calls. No parameter-changing retries.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
EXP="$ROOT/eval/sglang_bcg_kaggle_20260826"
TOOL_KAGGLE="${HYDRADG_KAGGLE_CLI:-$ROOT/.tools/kaggle_venv/bin/kaggle}"
KERNEL_REF="biobitworks/hydradg-sglang-bcg-stress-20260826"
POLL_S="${POLL_S:-60}"
# Max watcher lifetime: 75 GPU min + 30 min install/queue + 20 min collect slack
MAX_WATCH_S="${MAX_WATCH_S:-7500}"
WATCH_LOG="$EXP/receipts/watcher.log"
mkdir -p "$EXP/receipts" "$EXP/results"

export KAGGLE_USERNAME
export KAGGLE_KEY
KAGGLE_USERNAME="$(python3 -c "import json; d=json.load(open('$HOME/.kaggle/kaggle.json')); print(d.get('KAGGLE_USERNAME') or d.get('username') or '')")"
KAGGLE_KEY="$(python3 -c "import json; d=json.load(open('$HOME/.kaggle/kaggle.json')); print(d.get('KAGGLE_KEY') or d.get('key') or '')")"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] $*" | tee -a "$WATCH_LOG"; }

log "WATCHER_START kernel=$KERNEL_REF poll_s=$POLL_S max_watch_s=$MAX_WATCH_S"
START=$(date +%s)
TERMINAL=""
STATUS_RAW=""

while true; do
  NOW=$(date +%s)
  ELAPSED=$((NOW - START))
  if (( ELAPSED > MAX_WATCH_S )); then
    log "WATCHER_TIMEOUT elapsed_s=$ELAPSED"
    TERMINAL="WATCHER_TIMEOUT"
    break
  fi
  STATUS_RAW=$("$TOOL_KAGGLE" kernels status "$KERNEL_REF" 2>/dev/null || echo "STATUS_ERROR")
  log "status_raw=$STATUS_RAW"
  STATE=$(STATUS_RAW_ENV="$STATUS_RAW" python3 -c 'import re,os; raw=os.environ.get("STATUS_RAW_ENV",""); m=re.search(r"KernelWorkerStatus\.([A-Za-z]+)", raw); print((m.group(1) if m else ("STATUS_ERROR" if "STATUS_ERROR" in raw else "UNKNOWN")).upper())')
  log "parsed_state=$STATE"
  case "$STATE" in
    COMPLETE|COMPLETED) TERMINAL="COMPLETE"; break ;;
    ERROR|CANCEL|CANCELLED|CANCELED|FAILED) TERMINAL="FAILED"; break ;;
    RUNNING|QUEUED|PENDING|STARTING|UNKNOWN|STATUS_ERROR) ;;
    *) log "UNRECOGNIZED_STATE=$STATE" ;;
  esac
  sleep "$POLL_S"
done

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)_${TERMINAL}"
OUT="$EXP/results/$RUN_ID"
mkdir -p "$OUT"
log "COLLECT_BEGIN out=$OUT terminal=$TERMINAL"

set +e
"$TOOL_KAGGLE" kernels output "$KERNEL_REF" -p "$OUT" >"$OUT/kaggle_output_pull.log" 2>&1
PULL_RC=$?
set -e
log "COLLECT_PULL_RC=$PULL_RC"
ls -la "$OUT" | tee -a "$WATCH_LOG" || true

# Hash bounded artifacts (exclude model caches if any)
python3 - "$OUT" "$TERMINAL" "$KERNEL_REF" "$EXP" <<'PY'
import hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(sys.argv[1])
terminal = sys.argv[2]
kernel = sys.argv[3]
exp = Path(sys.argv[4])
skip_parts = {"hf_cache", ".cache", "model_cache", "blobs"}
hashes = {}
for p in sorted(out.rglob("*")):
    if not p.is_file():
        continue
    if any(s in p.parts for s in skip_parts):
        continue
    if p.stat().st_size > 50_000_000:
        hashes[str(p.relative_to(out))] = {"skipped": "TOO_LARGE", "size": p.stat().st_size}
        continue
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    hashes[str(p.relative_to(out))] = h.hexdigest()

required = [
    "environment.json", "condition_manifest.json", "metrics.jsonl",
    "summary.json", "failures.jsonl", "receipt.json", "gpu_telemetry.csv",
]
present = {r: (out / r).exists() or any((out / r).exists() for _ in [0]) for r in required}
# also accept nested
for r in list(required):
    if not (out / r).exists():
        found = list(out.rglob(r))
        present[r] = bool(found)

receipt = {
    "schema": "hydradg.kaggle_collection_receipt.v1",
    "experiment_id": "SGLANG-BCG-KAGGLE-20260826",
    "work_unit_id": "HYDRADG_SGLANG_KAGGLE_BCG_STRESS_20260826",
    "kaggle_kernel_ref": kernel,
    "kaggle_run_state": terminal,
    "collected_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "output_dir": str(out),
    "required_artifacts_present": present,
    "artifact_sha256": hashes,
    "signature_state": "NOT_SIGNED",
    "claim_ceiling": "ONE_MODEL_ONE_KAGGLE_GPU_RUNTIME_STRESS_ONLY",
}
(out / "COLLECTION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
(exp / "receipts" / "COLLECTION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps({"terminal": terminal, "present": present, "n_hashed": len(hashes)}, indent=2))
PY

# Local recompute + recommendation if metrics present
if [[ -f "$OUT/metrics.jsonl" ]] || ls "$OUT"/**/metrics.jsonl >/dev/null 2>&1; then
  python3 "$EXP/scripts/recompute_summary.py" --results-dir "$OUT" || log "RECOMPUTE_FAILED"
  python3 "$EXP/scripts/daisy_recommendation.py" --results-dir "$OUT" || log "RECOMMEND_FAILED"
fi

log "WATCHER_STOP terminal=$TERMINAL out=$OUT"
echo "$OUT" > "$EXP/receipts/LATEST_RESULTS_DIR.txt"
unset KAGGLE_KEY
# Exit 0 even on FAILED kernel so collection receipt is preserved; state is in receipt
exit 0
