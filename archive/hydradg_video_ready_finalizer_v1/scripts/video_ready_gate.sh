#!/bin/zsh
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
WEB="$ROOT/apps/hydradg-web"
BEST="${BEST_USE_URL:-http://127.0.0.1:8787}"
SITE="${HYDRADG_VIDEO_SITE:-http://127.0.0.1:3010}"
STATE="${HYDRADG_ICEBERG_STATE_PATH:-$HOME/.local/share/hydradg-best-use/eval/e2e-20260819/context_iceberg_state.json}"
OUTROOT="${HYDRADG_E2E_DIR:-$HOME/.local/share/hydradg-best-use/eval/e2e-20260819}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$OUTROOT/video-ready-$STAMP"
mkdir -p "$OUT"

fail() { echo "VIDEO_READY=NO"; echo "BLOCKER=$1"; exit 1; }

cd "$ROOT"
git status -sb | tee "$OUT/git-status.txt"
git rev-parse HEAD | tee "$OUT/git-head.txt"

test -s "$STATE" || fail "LIVE_ICEBERG_STATE_MISSING:$STATE"

python3 - "$STATE" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]))
assert j.get("source_state")=="LIVE_CUSTODY_ARTIFACT", j.get("source_state")
assert j.get("timeline"), "timeline empty"
assert j.get("scene",{}).get("nodes"), "scene nodes empty"
print("LIVE_ICEBERG_STATE=PASS")
PY

curl -fsS "$BEST/health" > "$OUT/best-use-health.json" || fail "BEST_USE_HEALTH"
curl -fsS "$BEST/api/iceberg/headline" > "$OUT/iceberg-headline.json" || fail "ICEBERG_HEADLINE"
curl -fsS "$BEST/api/iceberg/full" > "$OUT/iceberg-full.json" || fail "ICEBERG_FULL"
curl -fsS "$BEST/api/models/comparison" > "$OUT/model-comparison.json" || fail "MODEL_COMPARISON"
curl -fsS "$BEST/api/local-model/status" > "$OUT/local-model-status.json" || fail "LOCAL_MODEL_STATUS"
curl -fsS -X POST "$BEST/api/local-model/explain" \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Explain the current Iceberg state using only recorded evidence. Give one counterevidence item and one falsification test."}' \
  > "$OUT/local-model-explain.json" || fail "LOCAL_MODEL_EXPLAIN"

cd "$WEB"
npm ci | tee "$OUT/npm-ci.log"
npm run typecheck | tee "$OUT/typecheck.log"
npm run build | tee "$OUT/build.log"

cd "$ROOT"
"$HERE/scripts/start_video_stack.sh"

for path in / /judge /graph /evidence /api/iceberg; do
  name="$(echo "$path" | tr '/' '_' | sed 's/^_*$/_root/')"
  code="$(curl -sS -o "$OUT/route${name}.txt" -w '%{http_code}' "$SITE$path" || true)"
  [[ "$code" == "200" ]] || fail "ROUTE:$path:HTTP=$code"
done

python3 - "$STATE" "$OUT" "$SITE" <<'PY'
import hashlib,json,pathlib,subprocess,sys,time
state=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2]); site=sys.argv[3]
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
root=pathlib.Path("/Users/byron/projects/active/hydradg")
branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
status=subprocess.check_output(["git","status","--porcelain"],cwd=root,text=True)
e2e=pathlib.Path.home()/".local/share/hydradg-best-use/eval/e2e-20260819/E2E_VERIFICATION_RECEIPT.json"
ice=json.loads(state.read_text())
obj={
 "schema":"hydradg.video_ready_receipt.v1",
 "timestamp_unix":int(time.time()),
 "git_branch":branch,
 "git_commit":commit,
 "working_tree_state":"CLEAN" if not status.strip() else "DIRTY",
 "e2e_receipt_sha256":sha(e2e) if e2e.exists() else None,
 "iceberg_state_sha256":sha(state),
 "project_fcg_root":ice.get("project_fcg_root"),
 "hydradb_projection_root":ice.get("hydradb_projection_root"),
 "site_url":site,
 "source_state":ice.get("source_state"),
 "route_checks":"PASS",
 "local_model_check":"PASS",
 "claim_ceiling":"LOCAL_PRIVATE_END_TO_END_DEMO_ONLY",
 "signature_state":ice.get("signature_state","PENDING_EXTERNAL_PRIVATE_KEY_OPERATION"),
 "merkle_state":ice.get("merkle_state","NOT_MERKLE_COMMITTED"),
 "push_state":"DEFERRED_LOCAL_PRESERVED",
 "video_ready":True
}
raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
obj["receipt_root_sha256"]=hashlib.sha256(raw).hexdigest()
p=out/"VIDEO_READY_RECEIPT.json"
p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print("VIDEO_READY=YES")
print("VIDEO_RECEIPT="+str(p))
print("VIDEO_RECEIPT_SHA256="+sha(p))
print("NEXT=RECORD_VIDEO_NOW")
PY
