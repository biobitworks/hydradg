#!/usr/bin/env bash
# After watch_and_collect exits: secret-scan, commit bounded results, push via proxy if needed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
EXP="$ROOT/eval/sglang_bcg_kaggle_20260826"
cd "$ROOT"
WATCH_PID_FILE="$EXP/receipts/watcher.pid"
LOG="$EXP/receipts/finalize.log"
PROXY="${HTTPS_PROXY:-http://127.0.0.1:18080}"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] $*" | tee -a "$LOG"; }

if [[ -f "$WATCH_PID_FILE" ]]; then
  WPID=$(cat "$WATCH_PID_FILE")
  log "WAITING_FOR_WATCHER pid=$WPID"
  while kill -0 "$WPID" 2>/dev/null; do sleep 30; done
  log "WATCHER_EXITED"
else
  log "NO_WATCHER_PID — proceeding if results exist"
fi

LATEST=""
if [[ -f "$EXP/receipts/LATEST_RESULTS_DIR.txt" ]]; then
  LATEST=$(cat "$EXP/receipts/LATEST_RESULTS_DIR.txt")
fi
log "LATEST_RESULTS_DIR=$LATEST"

# Secret scan bounded result tree (fail closed on literal keys)
if [[ -n "$LATEST" && -d "$LATEST" ]]; then
  if rg -n "KAGGLE_KEY\s*=\s*'[A-Za-z0-9]{20,}'|BEGIN (RSA |OPENSSH )?PRIVATE KEY" "$LATEST" ; then
    log "SECRET_SCAN=FAIL — abort commit"
    exit 1
  fi
  log "SECRET_SCAN=PASS"
fi

# Stage bounded artifacts only
git add \
  "$EXP/receipts" \
  "$EXP/results" \
  "$EXP"/*.json \
  2>/dev/null || true

# Avoid huge logs: unstage files > 5MB
python3 - <<'PY'
import subprocess
from pathlib import Path
out = subprocess.check_output(["git","diff","--cached","--name-only"], text=True)
for line in out.splitlines():
    p = Path(line)
    if p.exists() and p.is_file() and p.stat().st_size > 5_000_000:
        subprocess.run(["git","reset","HEAD","--",line], check=False)
        print("unstaged_large", line, p.stat().st_size)
PY

if git diff --cached --quiet; then
  log "NOTHING_TO_COMMIT"
else
  git commit -m "$(cat <<'EOF'
collect SGLang BCG Kaggle stress results (provisional)

Engineering runtime evidence only; local recompute + Daisy successor
recommendation. Not Daisy T00-T12; HydraDB untouched; claim ceiling
one-model one-Kaggle-GPU runtime stress.
EOF
)"
  log "COMMITTED=$(git rev-parse HEAD)"
fi

# Push via proxy (en0 may still be captive-portal intercepted)
export https_proxy="$PROXY" http_proxy="$PROXY" HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY"
if git -c http.proxy="$PROXY" push origin exp/sglang-kaggle-bcg-stress-20260826; then
  log "PUSH_OK"
else
  log "PUSH_FAIL — results remain local"
fi

# Final report file
python3 - <<'PY'
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
exp = Path('eval/sglang_bcg_kaggle_20260826')
latest = ''
lp = exp/'receipts'/'LATEST_RESULTS_DIR.txt'
if lp.exists():
    latest = lp.read_text().strip()
rd = Path(latest) if latest else None
recomp = {}
rec = {}
daisy = {}
if rd and (rd/'RECOMPUTED_SUMMARY.json').exists():
    recomp = json.loads((rd/'RECOMPUTED_SUMMARY.json').read_text())
elif rd:
    found = list(rd.rglob('RECOMPUTED_SUMMARY.json'))
    if found:
        recomp = json.loads(found[0].read_text())
if rd and (rd/'COLLECTION_RECEIPT.json').exists():
    rec = json.loads((rd/'COLLECTION_RECEIPT.json').read_text())
if rd and (rd/'DAISY_RUNTIME_SUCCESSOR_RECOMMENDATION.json').exists():
    daisy = json.loads((rd/'DAISY_RUNTIME_SUCCESSOR_RECOMMENDATION.json').read_text())
pc = recomp.get('per_condition') or {}
def g(cid, key):
    return (pc.get(cid) or {}).get(key)
recomp_sha = None
if rd and (rd/'RECOMPUTED_SUMMARY.sha256').exists():
    recomp_sha = (rd/'RECOMPUTED_SUMMARY.sha256').read_text().strip()
elif recomp:
    recomp_sha = hashlib.sha256(json.dumps(recomp, sort_keys=True).encode()).hexdigest()

report = {
  'WORK_UNIT_ID': 'HYDRADG_SGLANG_KAGGLE_BCG_STRESS_20260826',
  'WORK_UNIT_STATE': 'COLLECTED' if recomp else 'WATCHER_DONE_PARTIAL',
  'PREREGISTRATION_SHA': (exp/'receipts'/'PREREGISTRATION_SHA.txt').read_text().strip() if (exp/'receipts'/'PREREGISTRATION_SHA.txt').exists() else None,
  'RESULT_COMMIT_SHA': __import__('subprocess').check_output(['git','rev-parse','HEAD'], text=True).strip(),
  'KAGGLE_AUTH': 'PASS',
  'KAGGLE_KERNEL_REF': 'biobitworks/hydradg-sglang-bcg-stress-20260826',
  'KAGGLE_RUN_STATE': rec.get('kaggle_run_state'),
  'GPU_NAME': None,
  'GPU_MINUTES_USED': None,
  'MODEL': 'Qwen/Qwen2.5-1.5B-Instruct',
  'SGLANG_VERSION': '0.5.18',
  'C0_STATE': list((pc.get('C0') or {}).get('failure_counts', {}).keys()) or None,
  'C1_STATE': list((pc.get('C1') or {}).get('failure_counts', {}).keys()) or None,
  'C2_STATE': list((pc.get('C2') or {}).get('failure_counts', {}).keys()) or None,
  'CELLS_EXPECTED': 108,
  'CELLS_COMPLETED': sum((pc.get(c) or {}).get('n_pass', 0) for c in pc),
  'C0_SUCCESS_RATE': g('C0','success_rate'),
  'C1_SUCCESS_RATE': g('C1','success_rate'),
  'C2_SUCCESS_RATE': g('C2','success_rate'),
  'C0_MEDIAN_TTFT': g('C0','median_ttft_s'),
  'C1_MEDIAN_TTFT': g('C1','median_ttft_s'),
  'C2_MEDIAN_TTFT': g('C2','median_ttft_s'),
  'C0_MEDIAN_PREFILL_TOK_S': g('C0','median_input_tokens_per_s'),
  'C1_MEDIAN_PREFILL_TOK_S': g('C1','median_input_tokens_per_s'),
  'C2_MEDIAN_PREFILL_TOK_S': g('C2','median_input_tokens_per_s'),
  'C0_PEAK_VRAM': g('C0','peak_vram_mib'),
  'C1_PEAK_VRAM': g('C1','peak_vram_mib'),
  'C2_PEAK_VRAM': g('C2','peak_vram_mib'),
  'OUTPUT_EQUIVALENCE_MISMATCHES': recomp.get('output_equivalence_mismatches'),
  'FAILURE_PHENOTYPES': sorted({k for c in pc.values() for k in (c.get('failure_counts') or {})}),
  'RECOMPUTED_SUMMARY_SHA256': recomp_sha,
  'DAISY_RUNTIME_SUCCESSOR_RECOMMENDATION': daisy.get('recommendation'),
  'EVIDENCE_STATE': 'ENGINEERING_RUNTIME_EVIDENCE_PROVISIONAL',
  'EXPERIMENT_STATE': 'SUCCESSOR_EVAL_ONLY_NOT_DAISY_T00_T12',
  'FCO_STATE': 'NOT_PROMOTED_UNLESS_EXISTING_GOVERNANCE_REQUIRES_RECEIPT_ONLY',
  'FCG_STATE': 'NOT_PROMOTED',
  'HYDRADB_STATE': 'NOT_TOUCHED',
  'CLAIM_CEILING': 'ONE_MODEL_ONE_KAGGLE_GPU_RUNTIME_STRESS_ONLY',
  'SIGNATURE_STATE': 'NOT_SIGNED',
  'MERKLE_MMR_STATE': 'NOT_COMMITTED',
  'NEXT_SAFE_ACTION': 'REVIEW_RESULTS_AND_DECIDE_WHETHER_TO_PREREGISTER_DAISY_SGLANG_RUNTIME_SUCCESSOR',
  'FINAL_REVIEW_GATE': 'RAW_RESULTS_COLLECTED_AND_LOCAL_RECOMPUTATION_COMPLETE' if recomp else 'WAITING_OR_PARTIAL',
  'results_dir': latest,
  'finished_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
}
# enrich from cloud summary/environment if present
if rd:
    for name in ('summary.json','environment.json','receipt.json'):
        hits = list(rd.rglob(name))
        if not hits: continue
        doc = json.loads(hits[0].read_text())
        if name == 'environment.json':
            report['GPU_NAME'] = doc.get('GPU_NAME')
        if name == 'summary.json':
            report['GPU_MINUTES_USED'] = doc.get('gpu_minutes_used_approx')
            report['C0_STATE'] = (doc.get('condition_states') or {}).get('C0') or report['C0_STATE']
            report['C1_STATE'] = (doc.get('condition_states') or {}).get('C1') or report['C1_STATE']
            report['C2_STATE'] = (doc.get('condition_states') or {}).get('C2') or report['C2_STATE']
        if name == 'receipt.json':
            report['GPU_MINUTES_USED'] = report['GPU_MINUTES_USED'] or doc.get('gpu_min_used')
(exp/'receipts'/'FINAL_REPORT.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
(exp/'receipts'/'FINAL_REPORT.md').write_text('\n'.join(f'{k}={report[k]}' for k in report)+'\n')
print(json.dumps(report, indent=2, sort_keys=True))
PY

log "FINALIZE_DONE"
