#!/bin/zsh
set -euo pipefail
ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
WEB="$ROOT/apps/hydradg-web"
STATE="${HYDRADG_ICEBERG_STATE_PATH:-$HOME/.local/share/hydradg-best-use/eval/e2e-20260819/context_iceberg_state.json}"
PORT="${HYDRADG_VIDEO_PORT:-3010}"
LOGDIR="${HYDRADG_VIDEO_LOGDIR:-$HOME/.local/share/hydradg-video}"
mkdir -p "$LOGDIR"

test -s "$STATE" || { echo "STOP: missing live Iceberg state $STATE"; exit 20; }
export HYDRADG_ICEBERG_STATE_PATH="$STATE"

if ! curl -fsS http://127.0.0.1:8787/health >/dev/null 2>&1; then
  bash "$ROOT/HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh" start
fi

if curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
  echo "SITE_ALREADY_RUNNING=http://127.0.0.1:$PORT"
  exit 0
fi

cd "$WEB"
test -d .next || { echo "STOP: .next missing; run npm run build"; exit 21; }

nohup npm run start -- -H 127.0.0.1 -p "$PORT" >"$LOGDIR/web.log" 2>&1 &
echo $! > "$LOGDIR/web.pid"

for _ in $(seq 1 40); do
  if curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
    echo "SITE_READY=http://127.0.0.1:$PORT"
    echo "WEB_PID=$(cat "$LOGDIR/web.pid")"
    exit 0
  fi
  sleep 0.5
done

cat "$LOGDIR/web.log"
exit 22
