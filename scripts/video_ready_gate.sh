#!/usr/bin/env bash
set -euo pipefail

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
WEB_PORT="${HYDRADG_VIDEO_GATE_PORT:-3012}"
WEB_URL="http://127.0.0.1:${WEB_PORT}"
OUT_ROOT="${HYDRADG_VIDEO_GATE_RUNTIME:-$HOME/.local/share/hydradg-video-gate}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$OUT_ROOT/$RUN_ID"
mkdir -p "$OUT"

cleanup() {
  if [[ -s "$OUT/web.pid" ]]; then
    kill "$(cat "$OUT/web.pid")" 2>/dev/null || true
  fi
}
trap cleanup EXIT

cd "$ROOT"
printf 'VIDEO_GATE_MODE=READ_ONLY_RELEASE_VERIFICATION\n'
printf 'BRANCH=%s\n' "$(git branch --show-current)"
printf 'COMMIT=%s\n' "$(git rev-parse HEAD)"

git diff --quiet || { echo "STOP: unstaged changes"; exit 10; }
git diff --cached --quiet || { echo "STOP: staged changes"; exit 11; }
test -z "$(git ls-files --others --exclude-standard)" || { echo "STOP: untracked files"; git status --short; exit 12; }

echo "SCIENTIFIC_MUTATION=NOT_PERFORMED"
echo "HYDRADB_WRITE=NOT_PERFORMED"
echo "SEEDGRAPH_WRITE=NOT_PERFORMED"
echo "DATASET_PULL=NOT_PERFORMED"
echo "SCIENTIFIC_CANARY=NOT_PERFORMED"

python3 scripts/check_term_knowledge_coverage.py | tee "$OUT/term_coverage.log"
python3 scripts/check_static_fallback.py | tee "$OUT/static_fallback.log"
python3 scripts/hash_release_artifacts.py --out "$OUT/release_artifact_hashes.json"

cd apps/hydradg-web
npm ci
npm run typecheck
npm run build

nohup npm run start -- -p "$WEB_PORT" > "$OUT/web.log" 2>&1 &
echo $! > "$OUT/web.pid"
for _ in $(seq 1 60); do
  curl -fsS "$WEB_URL/" >/dev/null 2>&1 && break
  kill -0 "$(cat "$OUT/web.pid")" 2>/dev/null || { cat "$OUT/web.log"; exit 20; }
  sleep 1
done
curl -fsS "$WEB_URL/" >/dev/null || { cat "$OUT/web.log"; exit 21; }

cd "$ROOT"
for path in / /judge /graph /knowledge /evidence /eligibility /track01 /track02 /track03 /api/iceberg /api/knowledge /api/site-fcg /api/release-status; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' "$WEB_URL$path")"
  printf '%s %s\n' "$code" "$path" | tee -a "$OUT/route_smoke.txt"
  test "$code" = "200" || { echo "STOP: route failed $path=$code"; exit 22; }
done

curl -fsS "$WEB_URL/api/iceberg" > "$OUT/context_iceberg.json"
python3 - "$OUT/context_iceberg.json" <<'PY'
import json, math, sys
j=json.load(open(sys.argv[1]))
assert j.get("timeline"), j
assert j.get("scene",{}).get("nodes"), j
for state in j["timeline"]:
    js=float(state["js_divergence"])
    drift=float(state["cloud_drift_0_100"])
    assert math.isfinite(js) and 0 <= js <= 1, state
    assert math.isfinite(drift) and 0 <= drift <= 100, state
    assert abs(drift - 100*js) < 1e-8, state
print("CONTEXT_ICEBERG_CONTRACT=PASS")
print("ICEBERG_SOURCE_STATE=" + str(j.get("source_state","UNKNOWN")))
print("ICEBERG_CLAIM_CEILING=" + str(j.get("claim_ceiling","UNKNOWN")))
PY

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "STOP: gitleaks required: brew install gitleaks"
  exit 30
fi
gitleaks dir --redact=100 --no-banner --report-format json --report-path "$OUT/gitleaks.json" .

python3 - "$OUT" "$WEB_URL" <<'PY'
import hashlib, json, pathlib, sys, time
out=pathlib.Path(sys.argv[1]); url=sys.argv[2]
body={
  "schema":"hydradg.video_ready_gate.v1",
  "state":"PASS",
  "video_url":url,
  "scientific_mutation":"NOT_PERFORMED",
  "hydradb_write":"NOT_PERFORMED",
  "seedgraph_write":"NOT_PERFORMED",
  "claim_ceiling":"LOCAL_VIDEO_SURFACE_BUILD_ROUTE_AND_SECURITY_GATE_ONLY",
  "signature_state":"NOT_SIGNED",
  "merkle_state":"NOT_PROJECT_COMMITTED",
  "timestamp_unix":int(time.time()),
}
canon=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
body["payload_sha256"]=hashlib.sha256(canon).hexdigest()
p=out/"VIDEO_READY_RECEIPT.json"; p.write_text(json.dumps(body,indent=2,sort_keys=True)+"\n")
print("VIDEO_READY_LIVE=YES")
print("VIDEO_URL="+url)
print("VIDEO_READY_RECEIPT="+str(p))
print("VIDEO_READY_RECEIPT_SHA256="+hashlib.sha256(p.read_bytes()).hexdigest())
PY

echo "NEXT=bash scripts/start_video_demo.sh"
