#!/usr/bin/env bash
set -euo pipefail

# Execute the release-critical Hack Hydra batches on magicSTUDIObox.
# This script does not publish GitHub/Vercel or submit the hackathon form.
# It writes local evidence under ~/.local/share/hydradg-release and fails closed.

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
BRANCH="hack-hydra/submission-eligible-20260819"
PKG="$ROOT/HydraDG_DaisyTrain_v0.3.7"
RUNTIME="${HYDRADG_RELEASE_RUNTIME:-$HOME/.local/share/hydradg-release}"
BEST_RUNTIME="${BEST_USE_RUNTIME:-$HOME/.local/share/hydradg-best-use}"
TOKEN_FILE="$BEST_RUNTIME/hydradb-auth-token"
HYDRA_ENDPOINT="http://127.0.0.1:8443/v1/graphs/default/query"
BEST_URL="http://127.0.0.1:${BEST_USE_PORT:-8787}"
WEB_PORT="${HYDRADG_RELEASE_WEB_PORT:-3010}"
WEB_URL="http://127.0.0.1:$WEB_PORT"
PULL_DATASETS="${HYDRADG_RELEASE_PULL_DATASETS:-1}"
EXTERNAL_LINKS="${HYDRADG_RELEASE_EXTERNAL_LINKS:-0}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$RUNTIME/$RUN_ID"
mkdir -p "$RUN_DIR"

progress() { printf '[%-24s] %3s%% stage=%s\n' "$(printf '%*s' $(( $1 * 24 / 100 )) '' | tr ' ' '#')" "$1" "$2"; }
sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }

cleanup() {
  if [[ -f "$RUN_DIR/web.pid" ]]; then
    kill "$(cat "$RUN_DIR/web.pid")" 2>/dev/null || true
    rm -f "$RUN_DIR/web.pid"
  fi
}
trap cleanup EXIT

progress 3 VERIFY_RELEASE_BRANCH
cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || { echo "STOP: wrong repo root"; exit 10; }
test "$(git branch --show-current)" = "$BRANCH" || { echo "STOP: expected $BRANCH"; exit 11; }
git diff --quiet || { echo "STOP: unstaged changes exist"; exit 12; }
git diff --cached --quiet || { echo "STOP: staged changes exist"; exit 13; }
test -z "$(git ls-files --others --exclude-standard)" || { echo "STOP: untracked files exist"; git status --short; exit 14; }

git fetch origin "$BRANCH"
git pull --ff-only origin "$BRANCH"
SOURCE_SHA="$(git rev-parse HEAD)"
echo "SOURCE_SHA=$SOURCE_SHA"

progress 9 STATIC_CHECKS
python3 -m py_compile \
  "$PKG/scripts/best_use_typed_graph.py" \
  "$PKG/scripts/best_use_structural_suite.py" \
  "$PKG/scripts/best_use_local_server.py" \
  "$PKG/scripts/best_use_local_server_hackhydra.py" \
  "$PKG/scripts/track01_hydraontology_canary.py" \
  "$PKG/scripts/track02_hydrablast_canary.py" \
  "$PKG/scripts/run_track03_live_golden_path.py" \
  "$ROOT/scripts/check_hydradg_web_links.py"
bash -n "$PKG/scripts/best_use_magicstudio.sh"
bash -n "$PKG/scripts/bootstrap_best_use_magicstudio.sh"
bash -n "$PKG/scripts/pull_track01_track03_datasets.sh"
bash -n "$ROOT/scripts/build_hackhydra_public_export.sh"

echo "STATIC_CHECKS=PASS"

progress 18 START_PINNED_HYDRADB_AND_BEST_USE
bash "$PKG/scripts/bootstrap_best_use_magicstudio.sh" start | tee "$RUN_DIR/bootstrap.log"
test -s "$TOKEN_FILE" || { echo "STOP: local HydraDB token file missing"; exit 20; }
curl -fsS "$BEST_URL/health" | tee "$RUN_DIR/best_use_health.json" | python3 -m json.tool

progress 28 DATASETS
if [[ "$PULL_DATASETS" = "1" ]]; then
  bash "$PKG/scripts/pull_track01_track03_datasets.sh" --track all --tier core | tee "$RUN_DIR/dataset_pull.log"
  LATEST_DATASET_RECEIPT="$(find "$HOME/.local/share/hydradg-datasets/receipts" -type f -name 'dataset_pull_*.json' -print 2>/dev/null | LC_ALL=C sort | tail -1)"
  test -n "$LATEST_DATASET_RECEIPT" && test -s "$LATEST_DATASET_RECEIPT" || { echo "STOP: dataset pull receipt missing"; exit 21; }
  cp "$LATEST_DATASET_RECEIPT" "$RUN_DIR/dataset_pull_receipt.json"
else
  echo "DATASET_PULL=SKIPPED_BY_OPERATOR" | tee "$RUN_DIR/dataset_pull.log"
fi

progress 40 TRACK01_CANARY
python3 "$PKG/scripts/track01_hydraontology_canary.py" \
  --endpoint "$HYDRA_ENDPOINT" \
  --token-file "$TOKEN_FILE" \
  --out "$RUN_DIR/track01_hydraontology_canary.json"
python3 - "$RUN_DIR/track01_hydraontology_canary.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]))
assert j["status"]=="PASS", j
assert j["claim_ceiling"]=="SYNTHETIC_TRACK01_STRUCTURAL_CANARY_ONLY_NOT_ENTERPRISERAG_OR_HERB_PERFORMANCE"
print("TRACK01_CANARY=PASS",j["result_sha256"])
PY

progress 50 TRACK02_CANARY
python3 "$PKG/scripts/track02_hydrablast_canary.py" \
  --endpoint "$HYDRA_ENDPOINT" \
  --token-file "$TOKEN_FILE" \
  --out "$RUN_DIR/track02_hydrablast_canary.json"
python3 - "$RUN_DIR/track02_hydrablast_canary.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]))
assert j["status"]=="PASS", j
assert j["claim_ceiling"]=="SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY_NOT_REAL_NPM_EXPOSURE"
print("TRACK02_CANARY=PASS",j["result_sha256"])
PY

progress 61 TRACK03_LIVE_GOLDEN_PATH
python3 "$PKG/scripts/run_track03_live_golden_path.py" \
  --server "$BEST_URL" \
  --endpoint "$HYDRA_ENDPOINT" \
  --token-file "$TOKEN_FILE" \
  --out "$RUN_DIR/track03_live_golden_path.json"
python3 - "$RUN_DIR/track03_live_golden_path.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]))
assert j["status"]=="PASS", j
print("TRACK03_LIVE_GOLDEN_PATH=PASS",j["result_sha256"])
PY

progress 70 WEB_BUILD
cd "$ROOT/apps/hydradg-web"
npm ci
npm run typecheck
npm run build

progress 78 WEB_START
nohup npm run start -- -p "$WEB_PORT" > "$RUN_DIR/web.log" 2>&1 &
echo $! > "$RUN_DIR/web.pid"
for _ in $(seq 1 60); do
  if curl -fsS "$WEB_URL/" >/dev/null 2>&1; then break; fi
  kill -0 "$(cat "$RUN_DIR/web.pid")" 2>/dev/null || { cat "$RUN_DIR/web.log"; exit 30; }
  sleep 1
done
curl -fsS "$WEB_URL/" >/dev/null || { cat "$RUN_DIR/web.log"; echo "STOP: web server health timeout"; exit 31; }

progress 84 WEB_ROUTE_AND_LINK_AUDIT
LINK_ARGS=(--base "$WEB_URL" --out "$RUN_DIR/web_link_audit.json")
[[ "$EXTERNAL_LINKS" = "1" ]] && LINK_ARGS+=(--external)
python3 "$ROOT/scripts/check_hydradg_web_links.py" "${LINK_ARGS[@]}"

curl -fsS "$WEB_URL/api/site-fcg" > "$RUN_DIR/site_fcg.json"
curl -fsS "$WEB_URL/api/custody" > "$RUN_DIR/fixture_custody.json"
python3 - "$RUN_DIR/site_fcg.json" "$RUN_DIR/fixture_custody.json" <<'PY'
import json,re,sys
site=json.load(open(sys.argv[1])); custody=json.load(open(sys.argv[2]))
assert site["schema"]=="hydradg.site_fcg.v1"
assert len(site["nodes"])>=9 and len(site["edges"])>=10
assert all(re.fullmatch(r"fco:[0-9a-f]{64}",n["id"]) for n in site["nodes"])
assert site["merkle_state"]=="NOT_MERKLE_COMMITTED"
assert custody["claim_ceiling"]=="DETERMINISTIC_FIXTURE_MERKLE_CHECKPOINT_ONLY"
assert custody["live_merkle_state"]=="NOT_ESTABLISHED_BY_THIS_ROUTE"
print("WEBSITE_FCG=PASS",site["artifact"]["id"])
PY

progress 90 SECURITY_GATE
cd "$ROOT"
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks dir --redact=100 --no-banner \
    --report-format json --report-path "$RUN_DIR/gitleaks.json" .
  echo "GITLEAKS=PASS"
else
  echo "STOP: gitleaks is required for release gate" >&2
  exit 40
fi

progress 95 WRITE_RELEASE_RECEIPT
python3 - "$RUN_DIR" "$SOURCE_SHA" "$PULL_DATASETS" <<'PY'
import hashlib,json,pathlib,sys,time
run=pathlib.Path(sys.argv[1]); source_sha=sys.argv[2]; dataset_mode=sys.argv[3]
files={}
for p in sorted(run.iterdir()):
    if p.is_file() and p.name not in {"RELEASE_BATCH_RECEIPT.json"}:
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        files[p.name]={"sha256":h,"bytes":p.stat().st_size}
obj={
 "schema":"hydradg.release_batch_receipt.v1",
 "timestamp_unix":int(time.time()),
 "source_commit":source_sha,
 "dataset_pull_requested":dataset_mode=="1",
 "artifacts":files,
 "gates":{
   "static_checks":"PASS",
   "pinned_local_hydradb_and_best_use":"PASS",
   "track01_synthetic_canary":"PASS",
   "track02_synthetic_canary":"PASS",
   "track03_live_golden_path":"PASS",
   "web_build":"PASS",
   "internal_link_audit":"PASS",
   "website_fcg":"PASS",
   "secret_scan":"PASS"
 },
 "claim_ceiling":"LOCAL_RELEASE_EXECUTION_GATES_ONLY",
 "signature_state":"NOT_SIGNED",
 "merkle_state":"NOT_MERKLE_COMMITTED"
}
raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
obj["receipt_sha256"]=hashlib.sha256(raw).hexdigest()
out=run/"RELEASE_BATCH_RECEIPT.json"
out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(obj,indent=2,sort_keys=True))
PY

progress 100 COMPLETE
RECEIPT="$RUN_DIR/RELEASE_BATCH_RECEIPT.json"
echo "RELEASE_BATCH_COMPLETE=YES"
echo "RUN_DIR=$RUN_DIR"
echo "RECEIPT=$RECEIPT"
echo "RECEIPT_FILE_SHA256=$(sha256_file "$RECEIPT")"
echo "NOTE=This proves only the gates actually executed here. Public GitHub/Vercel/video/form remain separate gates."
