#!/usr/bin/env bash
# Start HydraDG production server for submission recording (loopback, persistent).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEB="$ROOT/apps/hydradg-web"
PORT="${HYDRADG_SUBMISSION_WEB_PORT:-3011}"
HOST="127.0.0.1"
STATE_DIR="$ROOT/eval/ollarma_measurement_review_20260827"
PID_FILE="$STATE_DIR/LOCAL_SERVER.pid"
LOG_FILE="$STATE_DIR/LOCAL_SERVER.log"
HEALTH_FILE="$STATE_DIR/LOCAL_SERVER_HEALTH.json"

mkdir -p "$STATE_DIR"
cd "$ROOT"
npm run build >/dev/null 2>&1 || npm run build

if [[ -f "$PID_FILE" ]]; then
  old_pid="$(cat "$PID_FILE")"
  if kill -0 "$old_pid" 2>/dev/null; then
    echo "LOCAL_SERVER_ALREADY_RUNNING pid=$old_pid port=$PORT"
    exit 0
  fi
fi

cd "$WEB"
nohup npx next start -H "$HOST" -p "$PORT" >>"$LOG_FILE" 2>&1 &
pid=$!
echo "$pid" >"$PID_FILE"
sleep 2
code=$(curl -s -o /dev/null -w "%{http_code}" "http://${HOST}:${PORT}/" || echo "000")
started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat >"$HEALTH_FILE" <<EOF
{
  "schema": "hydradg.local_server_health.v1",
  "LOCAL_URL": "http://${HOST}:${PORT}/",
  "LOCAL_SERVER_PID": $pid,
  "LOCAL_SERVER_START": "$started",
  "LOCAL_SERVER_HEALTH": "${code}",
  "port": $PORT
}
EOF
echo "LOCAL_URL=http://${HOST}:${PORT}/"
echo "LOCAL_SERVER_PID=$pid"
echo "LOCAL_SERVER_HEALTH=$code"
