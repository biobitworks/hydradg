#!/bin/zsh
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
MODE="verify"
if [[ "${1:-}" == "--mock" ]]; then MODE="mock"; shift; fi
if [[ "${1:-}" == "--verify" ]]; then MODE="verify"; shift; fi
if [[ "${1:-}" == "--full" ]]; then MODE="full"; shift; fi

OUTROOT="${HYDRADG_E2E_OUT:-$HERE/e2e-output-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUTROOT"

echo "STATE=RUNNING STAGE=PACKAGE_TESTS MODE=$MODE"
python3 -m pytest -q "$HERE/tests" | tee "$OUTROOT/package-tests.txt"

if [[ "$MODE" == "mock" ]]; then
  echo "STATE=RUNNING STAGE=MOCK_OLLARMA"
  python3 "$HERE/mock/mock_ollama_server.py" 18434 >"$OUTROOT/mock-server.log" 2>&1 &
  MPID=$!
  trap 'kill "$MPID" 2>/dev/null || true' EXIT
  sleep 0.4
  python3 "$HERE/scripts/run_approved_models.py" \
    --base-url http://127.0.0.1:18434 \
    --packet "$HERE/mock/sample_diagnostic_packet.json" \
    --out "$OUTROOT/model-replay.json"
  python3 "$HERE/scripts/verify_local_apis.py" \
    --best-use http://127.0.0.1:18434 \
    --web http://127.0.0.1:18434 \
    --out "$OUTROOT/api-verify.json" || true
  echo "STATE=PASS STAGE=MOCK_E2E CLAIM_CEILING=HARNESS_ONLY OUTPUT=$OUTROOT"
  exit 0
fi

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
echo "STATE=RUNNING STAGE=PREFLIGHT"
"$HERE/scripts/00_preflight.zsh" "$OUTROOT/preflight.txt"

echo "STATE=RUNNING STAGE=APPROVED_MODEL_REPLAY"
PACKET="${HYDRADG_DIAGNOSTIC_PACKET:-$HERE/mock/sample_diagnostic_packet.json}"
python3 "$HERE/scripts/run_approved_models.py" \
  --base-url "${OLLARMA_BASE_URL:-http://127.0.0.1:11434}" \
  --packet "$PACKET" \
  --out "$OUTROOT/model-replay.json"

echo "STATE=RUNNING STAGE=LOCAL_API_VERIFY"
python3 "$HERE/scripts/verify_local_apis.py" \
  --best-use "${BEST_USE_URL:-http://127.0.0.1:8787}" \
  --web "${HYDRADG_WEB_URL:-http://127.0.0.1:3010}" \
  --out "$OUTROOT/api-verify.json"

if [[ "$MODE" == "verify" ]]; then
  echo "STATE=PASS STAGE=VERIFY_ONLY NEXT=REVIEW_PREFLIGHT_AND_RUN_FULL OUTPUT=$OUTROOT"
  exit 0
fi

echo "STATE=RUNNING STAGE=WEB_BUILD"
cd "$ROOT/apps/hydradg-web"
npm ci
npm run typecheck
npm run build

echo "STATE=RUNNING STAGE=RELEASE_BATCH"
cd "$ROOT"
python3 scripts/check_term_knowledge_coverage.py
python3 scripts/check_static_fallback.py
python3 scripts/hash_release_artifacts.py --out "$OUTROOT/release-artifact-hashes.json"

if [[ "${HYDRADG_RUN_RELEASE_BATCH:-1}" == "1" ]]; then
  bash scripts/run_hackhydra_release_batches_magicstudio.sh | tee "$OUTROOT/release-batch.log"
else
  echo "RELEASE_BATCH=SKIPPED_BY_OPERATOR" | tee "$OUTROOT/release-batch.log"
fi

echo "STATE=PASS STAGE=FULL_LOCAL_EXECUTION_COMPLETED CLAIM_CEILING=LOCAL_E2E_GATES_ONLY OUTPUT=$OUTROOT"
echo "NEXT=APPEND_E2E_RECEIPT_TO_CANONICAL_FCG_AND_SIGN_IF_AUTHORIZED"
