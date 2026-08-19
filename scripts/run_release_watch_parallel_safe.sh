#!/usr/bin/env bash
set -euo pipefail

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
WEB_PORT="${HYDRADG_RELEASE_WATCH_PORT:-3011}"
WEB_URL="http://127.0.0.1:$WEB_PORT"
OUT_ROOT="${HYDRADG_RELEASE_WATCH_RUNTIME:-$HOME/.local/share/hydradg-release-watch}"
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
echo "RELEASE_WATCH_MODE=PARALLEL_SAFE_READ_ONLY"
echo "BRANCH=$(git branch --show-current)"
echo "COMMIT=$(git rev-parse HEAD)"

git diff --quiet || { echo "STOP: unstaged changes"; exit 10; }
git diff --cached --quiet || { echo "STOP: staged changes"; exit 11; }
test -z "$(git ls-files --others --exclude-standard)" || { echo "STOP: untracked files"; git status --short; exit 12; }

# Explicitly no HydraDB, SeedGraph, dataset acquisition, canary, golden-path or training writes here.
echo "SCIENTIFIC_MUTATION=PROHIBITED"
echo "HYDRADB_WRITE=NOT_PERFORMED"
echo "SEEDGRAPH_WRITE=NOT_PERFORMED"
echo "DATASET_PULL=NOT_PERFORMED"

python3 -m py_compile \
  scripts/check_hydradg_web_links.py \
  scripts/check_static_fallback.py \
  scripts/check_term_knowledge_coverage.py \
  scripts/hash_release_artifacts.py

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
python3 scripts/check_hydradg_web_links.py --base "$WEB_URL" --out "$OUT/web_link_audit.json"

for path in \
  / \
  /demo \
  /graph \
  /knowledge \
  /evidence \
  /eligibility \
  /track01 \
  /track02 \
  /track03 \
  /api/iceberg \
  /api/knowledge \
  /api/site-fcg \
  /api/release-status
  do
    code="$(curl -sS -o /dev/null -w '%{http_code}' "$WEB_URL$path")"
    printf '%s %s\n' "$code" "$path" | tee -a "$OUT/route_smoke.txt"
    test "$code" = "200" || { echo "STOP: route failed $path=$code"; exit 22; }
  done

curl -fsS "$WEB_URL/api/iceberg" > "$OUT/context_iceberg.json"
curl -fsS "$WEB_URL/api/knowledge" > "$OUT/knowledge_projection.json"
curl -fsS "$WEB_URL/api/site-fcg" > "$OUT/site_fcg.json"
curl -fsS "$WEB_URL/api/release-status" > "$OUT/release_status.json"

python3 - "$OUT/context_iceberg.json" "$OUT/knowledge_projection.json" "$OUT/site_fcg.json" <<'PY'
import json,math,re,sys
ice=json.load(open(sys.argv[1])); kb=json.load(open(sys.argv[2])); site=json.load(open(sys.argv[3]))
assert ice.get("source_state") == "DETERMINISTIC_SYNTHETIC_TEST_FIXTURE", ice
assert ice.get("claim_ceiling") == "SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY", ice
assert ice.get("signature_state") == "NOT_SIGNED", ice
assert ice.get("merkle_state") == "NOT_MERKLE_COMMITTED", ice
for state in ice["timeline"]:
    js=float(state["js_divergence"]); drift=float(state["cloud_drift_0_100"])
    assert 0 <= js <= 1 and 0 <= drift <= 100
    assert abs(drift - 100*js) < 1e-8
assert kb["schema"] == "hydradg.website_knowledge_projection.v1"
assert re.fullmatch(r"fco:[0-9a-f]{64}",kb["root"]["id"])
assert kb["hydradb_projection_state"] == "PENDING_SAFE_ISOLATED_DAISY_HANDOFF"
assert site["schema"] in {"hydradg.site_fcg.v1","hydradg.site_fcg.v2"}
assert site["merkle_state"] == "NOT_MERKLE_COMMITTED"
print("RELEASE_WATCH_API_CONTRACT=PASS")
print("SCIENTIFIC_LIVE_SCORE=NOT_ESTABLISHED_BY_THIS_RUN")
PY

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "STOP: gitleaks required for Release Watch security gate"
  exit 30
fi
gitleaks dir --redact=100 --no-banner --report-format json --report-path "$OUT/gitleaks.json" .

echo "RELEASE_WATCH_PARALLEL_SAFE=PASS" | tee "$OUT/status.txt"
echo "SCIENTIFIC_MUTATION=NOT_PERFORMED" | tee -a "$OUT/status.txt"
echo "RESULT_DIR=$OUT"
