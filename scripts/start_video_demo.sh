#!/usr/bin/env bash
set -euo pipefail

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
PORT="${HYDRADG_VIDEO_PORT:-3012}"
REQUESTED_MODE="${HYDRADG_VIDEO_MODE:-auto}"
PID_FILE="${HYDRADG_VIDEO_PID_FILE:-$HOME/.local/share/hydradg-video-demo.pid}"
LOG_FILE="${HYDRADG_VIDEO_LOG_FILE:-$HOME/.local/share/hydradg-video-demo.log}"
mkdir -p "$(dirname "$PID_FILE")"

case "$REQUESTED_MODE" in
  auto|live|static) ;;
  *) echo "STOP: HYDRADG_VIDEO_MODE must be auto|live|static"; exit 10 ;;
esac

stop_old() {
  if [[ -s "$PID_FILE" ]]; then
    old="$(cat "$PID_FILE")"
    kill "$old" 2>/dev/null || true
    rm -f "$PID_FILE"
  fi
}
stop_old

cd "$ROOT"

if [[ "$REQUESTED_MODE" = "live" ]] && [[ ! -f apps/hydradg-web/.next/BUILD_ID ]]; then
  echo "STOP: live mode requested but no completed Next.js build is present"
  exit 11
fi

if [[ "$REQUESTED_MODE" = "static" ]]; then
  USE_LIVE=0
elif [[ "$REQUESTED_MODE" = "live" ]]; then
  USE_LIVE=1
elif [[ -f apps/hydradg-web/.next/BUILD_ID ]]; then
  USE_LIVE=1
else
  USE_LIVE=0
fi

if [[ "$USE_LIVE" = "1" ]]; then
  cd apps/hydradg-web
  nohup npm run start -- -p "$PORT" > "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  URL="http://127.0.0.1:${PORT}/"
  MODE="LIVE_LOCAL_NEXTJS"
else
  nohup python3 -m http.server "$PORT" --bind 127.0.0.1 --directory apps/hydradg-web/public > "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  URL="http://127.0.0.1:${PORT}/backup/hydradg.html"
  MODE="STATIC_FALLBACK"
fi

for _ in $(seq 1 30); do
  curl -fsS "$URL" >/dev/null 2>&1 && break
  kill -0 "$(cat "$PID_FILE")" 2>/dev/null || { cat "$LOG_FILE"; exit 20; }
  sleep 1
done
curl -fsS "$URL" >/dev/null || { cat "$LOG_FILE"; exit 21; }

echo "VIDEO_DEMO_MODE=$MODE"
echo "VIDEO_DEMO_URL=$URL"
echo "VIDEO_DEMO_PID=$(cat "$PID_FILE")"
echo "VIDEO_DEMO_LOG=$LOG_FILE"
if [[ "$MODE" = "STATIC_FALLBACK" ]]; then
  echo "VIDEO_CLAIM_NOTE=STATIC_PRESENTATION_FALLBACK_NO_LIVE_HYDRADB_CONTROL"
else
  echo "VIDEO_CLAIM_NOTE=LOCAL_APPLICATION_SURFACE_USE_PAGE_LABELS_FOR_LIVE_VS_SYNTHETIC_STATE"
fi

if command -v open >/dev/null 2>&1; then
  open "$URL" || true
fi

echo "STOP_COMMAND=kill $(cat "$PID_FILE")"
