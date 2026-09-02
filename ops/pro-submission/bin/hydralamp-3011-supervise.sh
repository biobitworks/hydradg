#!/bin/bash
# Restart loop for HydraLamp 3011 — launchd KeepAlive equivalent.
set -euo pipefail

export HOME="${HOME:-/Users/byron}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="${HYDRALAMP_RUNTIME:-$HOME/.local/share/hydralamp-3011}"

mkdir -p "${RUNTIME}/logs" "${RUNTIME}/state"
echo $$ >"${RUNTIME}/state/supervise.pid"

while true; do
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) supervise start" >>"${RUNTIME}/logs/supervise.log"
  if bash "${SCRIPT_DIR}/hydralamp-3011-server.sh"; then
    rc=0
  else
    rc=$?
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) exit=${rc}" >>"${RUNTIME}/logs/supervise.log"
  sleep 2
done
