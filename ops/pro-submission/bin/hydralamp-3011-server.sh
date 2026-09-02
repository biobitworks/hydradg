#!/bin/bash
# User-level HydraLamp submission UI on port 3011 (magicPRObox controller lane).
set -euo pipefail

export HOME="${HOME:-/Users/byron}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
WEB="${ROOT}/apps/hydradg-web"
RUNTIME="${HYDRALAMP_RUNTIME:-$HOME/.local/share/hydralamp-3011}"
PORT="${HYDRALAMP_PORT:-3011}"
BIND="${HYDRALAMP_BIND:-127.0.0.1}"

mkdir -p "${RUNTIME}/logs" "${RUNTIME}/state"
LOG_OUT="${RUNTIME}/logs/web.out.log"
LOG_ERR="${RUNTIME}/logs/web.err.log"

if [[ ! -d "${WEB}/.next" ]]; then
  echo "BUILD_MISSING=${WEB}/.next" | tee -a "${LOG_ERR}"
  exit 1
fi

cd "${WEB}"
exec >>"${LOG_OUT}" 2>>"${LOG_ERR}"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) starting hydralamp on ${BIND}:${PORT}"
exec node ./node_modules/next/dist/bin/next start -H "${BIND}" -p "${PORT}"
