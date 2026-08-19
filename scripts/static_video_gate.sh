#!/usr/bin/env bash
set -euo pipefail

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
OUT_ROOT="${HYDRADG_STATIC_VIDEO_RUNTIME:-$HOME/.local/share/hydradg-static-video-gate}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$OUT_ROOT/$RUN_ID"
mkdir -p "$OUT"

cd "$ROOT"
test -f apps/hydradg-web/public/backup/hydradg.html || { echo "STOP: static fallback missing"; exit 10; }

python3 scripts/check_static_fallback.py | tee "$OUT/static_fallback.log"

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "STOP: gitleaks required: brew install gitleaks"
  exit 20
fi
gitleaks dir --redact=100 --no-banner --report-format json --report-path "$OUT/gitleaks-public.json" apps/hydradg-web/public

FALLBACK_SHA="$(shasum -a 256 apps/hydradg-web/public/backup/hydradg.html | awk '{print $1}')"
cat > "$OUT/STATIC_VIDEO_READY_RECEIPT.json" <<EOF
{
  "schema": "hydradg.static_video_ready_gate.v1",
  "state": "PASS",
  "artifact": "apps/hydradg-web/public/backup/hydradg.html",
  "artifact_sha256": "$FALLBACK_SHA",
  "scientific_mutation": "NOT_PERFORMED",
  "claim_ceiling": "STATIC_PRESENTATION_FALLBACK_ONLY_NO_LIVE_HYDRADB_CONTROL",
  "signature_state": "NOT_SIGNED",
  "merkle_state": "NOT_PROJECT_COMMITTED"
}
EOF
RECEIPT_SHA="$(shasum -a 256 "$OUT/STATIC_VIDEO_READY_RECEIPT.json" | awk '{print $1}')"

echo "STATIC_VIDEO_READY=YES"
echo "STATIC_FALLBACK_SHA256=$FALLBACK_SHA"
echo "STATIC_VIDEO_RECEIPT=$OUT/STATIC_VIDEO_READY_RECEIPT.json"
echo "STATIC_VIDEO_RECEIPT_SHA256=$RECEIPT_SHA"
echo "NEXT=HYDRADG_ROOT=$ROOT HYDRADG_VIDEO_MODE=static bash $ROOT/scripts/start_video_demo.sh"
