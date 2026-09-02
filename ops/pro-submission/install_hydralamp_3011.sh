#!/bin/bash
# Install HydraLamp submission UI persistence on magicPRObox (port 3011).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BIN_DIR="${REPO_ROOT}/ops/pro-submission/bin"
RUNTIME="${HOME}/.local/share/hydralamp-3011"
PORT="${HYDRALAMP_PORT:-3011}"
UID_NUM="$(id -u)"
PLIST_SRC="${REPO_ROOT}/ops/pro-submission/com.biobitworks.hydralamp-3011.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.biobitworks.hydralamp-3011.plist"

mkdir -p "${RUNTIME}/logs" "${RUNTIME}/state" "${HOME}/Library/LaunchAgents"
chmod +x "${BIN_DIR}/"*.sh

echo "Building hydradg-web (required once)..."
cd "${REPO_ROOT}/apps/hydradg-web"
if [[ ! -d node_modules ]]; then
  npm ci
fi
npm run build

# Stop any prior listener on 3011
pkill -f "next start.*-p ${PORT}" 2>/dev/null || true
launchctl bootout "gui/${UID_NUM}/com.biobitworks.hydralamp-3011" 2>/dev/null || true
sleep 1

cp "${PLIST_SRC}" "${PLIST_DST}"
launchctl bootstrap "gui/${UID_NUM}" "${PLIST_DST}" || launchctl load "${PLIST_DST}"

for _ in $(seq 1 90); do
  if curl -fsS "http://127.0.0.1:${PORT}/hydralamp" >/dev/null 2>&1; then
    echo "HYDRALAMP_3011_STATE=UP"
    curl -fsS -o /dev/null -w "HYDRALAMP_HEALTH_HTTP=%{http_code}\n" "http://127.0.0.1:${PORT}/hydralamp"
    launchctl print "gui/${UID_NUM}/com.biobitworks.hydralamp-3011" 2>/dev/null | grep -E 'state =|pid =' || true
    exit 0
  fi
  sleep 1
done

echo "HYDRALAMP_3011_STATE=START_FAILED" >&2
exit 1
