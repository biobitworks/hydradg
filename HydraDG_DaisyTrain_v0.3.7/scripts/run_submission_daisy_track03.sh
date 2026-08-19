#!/usr/bin/env bash
set -euo pipefail
[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"

# Hack Hydra submission-critical Daisy: Track 03 real-data evidence.
# Scope is frozen to LongMemEval-S full500 after the live HydraDB structural gate.
# Data hydration is from the public upstream dataset, not an older participant
# package directory, so the final Hack Hydra tree can remain eligibility-clean.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO="$(cd "$PKG/.." && pwd)"
RUNTIME="${BEST_USE_RUNTIME:-$HOME/.local/share/hydradg-best-use}"
EVALDIR="$RUNTIME/eval/submission_track03"
RECEIPTDIR="$RUNTIME/receipts"
DATA="$RUNTIME/data/longmemeval_s_cleaned.json"
AUTH="$RUNTIME/hydradb-auth-token"
EXTRACTOR="${BEST_USE_EXTRACTOR:-heuristic}"
K="${BEST_USE_K:-5}"
BOOTSTRAP="$SCRIPT_DIR/bootstrap_best_use_magicstudio.sh"
RUNNER="$SCRIPT_DIR/run_best_use_typed_longmemeval.py"
ANALYZER="$SCRIPT_DIR/analyze_best_use_ablation.py"
OUT="$EVALDIR/longmemeval_full500_k${K}_${EXTRACTOR}.jsonl"
STATS="$EVALDIR/longmemeval_full500_k${K}_${EXTRACTOR}_stats.json"
RECEIPT="$RECEIPTDIR/submission_track03_full500_receipt.json"
LOG="$EVALDIR/submission_track03.log"
EXPECTED_SHA="d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
HF_REPO="xiaowu0162/longmemeval-cleaned"
HF_FILE="longmemeval_s_cleaned.json"
HF_REVISION="${LONGMEMEVAL_HF_REVISION:-main}"

mkdir -p "$EVALDIR" "$RECEIPTDIR" "$RUNTIME/data"

say() { printf '%s\n' "$*" | tee -a "$LOG"; }
fail() { printf 'ERROR: %s\n' "$*" | tee -a "$LOG" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }
sha256_file() {
  if have shasum; then shasum -a 256 "$1" | awk '{print $1}';
  else python3 - "$1" <<'PY'
import hashlib,sys
h=hashlib.sha256()
with open(sys.argv[1],'rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
print(h.hexdigest())
PY
  fi
}

hydrate_full_data() {
  if [[ -s "$DATA" ]] && [[ "$(sha256_file "$DATA")" == "$EXPECTED_SHA" ]]; then
    say "[daisy] full500 data already hydrated: $DATA"
    return 0
  fi

  TMP="$DATA.tmp.$$"
  rm -f "$TMP"
  say "[daisy] hydrating LongMemEval full500 from Hugging Face repo=$HF_REPO revision=$HF_REVISION"

  if have hf; then
    HFDIR="$RUNTIME/data/hf-longmemeval-cleaned"
    mkdir -p "$HFDIR"
    hf download "$HF_REPO" --repo-type dataset --revision "$HF_REVISION" --local-dir "$HFDIR" "$HF_FILE" 2>&1 | tee -a "$LOG"
    cp "$HFDIR/$HF_FILE" "$TMP"
  elif have uvx; then
    HFDIR="$RUNTIME/data/hf-longmemeval-cleaned"
    mkdir -p "$HFDIR"
    uvx --from huggingface_hub hf download "$HF_REPO" --repo-type dataset --revision "$HF_REVISION" --local-dir "$HFDIR" "$HF_FILE" 2>&1 | tee -a "$LOG"
    cp "$HFDIR/$HF_FILE" "$TMP"
  elif have curl; then
    # Hugging Face resolve URL; final SHA gate prevents silent source drift.
    curl -fL --retry 4 --retry-delay 2 \
      "https://huggingface.co/datasets/${HF_REPO}/resolve/${HF_REVISION}/${HF_FILE}?download=true" \
      -o "$TMP" 2>&1 | tee -a "$LOG"
  else
    fail "need hf, uvx, or curl to hydrate LongMemEval"
  fi

  [[ -s "$TMP" ]] || fail "downloaded LongMemEval object is empty"
  GOT="$(sha256_file "$TMP")"
  [[ "$GOT" == "$EXPECTED_SHA" ]] || fail "LongMemEval source SHA mismatch: got=$GOT expected=$EXPECTED_SHA"
  mv "$TMP" "$DATA"
  say "[daisy] full500 data hydrated sha256=$GOT bytes=$(wc -c < "$DATA" | tr -d ' ')"
}

: > "$LOG"
say "[daisy] Track 03 submission train"
say "[daisy] extractor=$EXTRACTOR k=$K"
say "[daisy] claim ceiling during execution: EXECUTION_IN_PROGRESS"

[[ -x "$BOOTSTRAP" || -f "$BOOTSTRAP" ]] || fail "missing bootstrap: $BOOTSTRAP"
[[ -f "$RUNNER" ]] || fail "missing runner: $RUNNER"
[[ -f "$ANALYZER" ]] || fail "missing analyzer: $ANALYZER"

say "[daisy] CAR 5/structural gate: starting pinned HydraDB"
bash "$BOOTSTRAP" start 2>&1 | tee -a "$LOG"

hydrate_full_data

[[ -f "$DATA" ]] || fail "full LongMemEval data not found after hydration: $DATA"
[[ -s "$AUTH" ]] || fail "HydraDB token file missing after bootstrap"

FULL_SHA="$(sha256_file "$DATA")"
[[ "$FULL_SHA" == "$EXPECTED_SHA" ]] || fail "LongMemEval full source SHA mismatch: $FULL_SHA"

say "[daisy] CAR 7: LongMemEval-S full500 A/B/C/D"
python3 "$RUNNER" "$DATA" \
  --token-file "$AUTH" \
  --extractor "$EXTRACTOR" \
  --k "$K" \
  --out "$OUT" 2>&1 | tee -a "$LOG"

[[ -s "$OUT" ]] || fail "full500 output missing or empty"

say "[daisy] CAR 8: paired statistics / bootstrap report"
python3 "$ANALYZER" "$OUT" \
  --out "$STATS" \
  --expected-n 500 \
  --bootstrap 5000 2>&1 | tee -a "$LOG"

[[ -s "$STATS" ]] || fail "statistics output missing or empty"

OUT_SHA="$(sha256_file "$OUT")"
STATS_SHA="$(sha256_file "$STATS")"
STRUCT="$RUNTIME/eval/structural_suite.json"
STRUCT_SHA="UNRESOLVED"
[[ -s "$STRUCT" ]] && STRUCT_SHA="$(sha256_file "$STRUCT")"

python3 - "$RECEIPT" "$REPO" "$FULL_SHA" "$OUT" "$OUT_SHA" "$STATS" "$STATS_SHA" "$STRUCT_SHA" "$EXTRACTOR" "$K" "$HF_REPO" "$HF_REVISION" <<'PY'
import hashlib,json,subprocess,sys,time
(out,repo,data_sha,result_path,result_sha,stats_path,stats_sha,struct_sha,extractor,k,hf_repo,hf_revision)=sys.argv[1:]
def git(*args):
    try:
        return subprocess.check_output(["git","-C",repo,*args],text=True).strip()
    except Exception:
        return "UNRESOLVED"
obj={
  "schema":"hydradg.submission_track03_full500.v2",
  "timestamp_unix":int(time.time()),
  "hydradg_commit":git("rev-parse","HEAD"),
  "hydradg_branch":git("branch","--show-current"),
  "longmemeval_source":"HUGGING_FACE_DATASET_REPOSITORY",
  "longmemeval_repo_id":hf_repo,
  "longmemeval_requested_revision":hf_revision,
  "longmemeval_source_sha256":data_sha,
  "extractor":extractor,
  "k":int(k),
  "result_path":result_path,
  "result_sha256":result_sha,
  "stats_path":stats_path,
  "stats_sha256":stats_sha,
  "structural_suite_sha256":struct_sha,
  "evidence_class":"RECOMPUTED_LIVE_HYDRADB_RETRIEVAL_ABLATION",
  "claim_ceiling":"LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
  "signature_state":"NOT_SIGNED",
  "merkle_state":"NOT_MERKLE_COMMITTED",
  "independent_replication_state":"NOT_ESTABLISHED_BY_THIS_RUN"
}
raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
obj["receipt_sha256"]=hashlib.sha256(raw).hexdigest()
with open(out,"w") as f: json.dump(obj,f,indent=2,sort_keys=True); f.write("\n")
print(json.dumps(obj,indent=2,sort_keys=True))
PY

say "[daisy] FULL500_COMPLETE"
say "[daisy] result=$OUT"
say "[daisy] result_sha256=$OUT_SHA"
say "[daisy] stats=$STATS"
say "[daisy] stats_sha256=$STATS_SHA"
say "[daisy] receipt=$RECEIPT"
say "[daisy] next: review stats before any claim promotion or optional K=10 run"