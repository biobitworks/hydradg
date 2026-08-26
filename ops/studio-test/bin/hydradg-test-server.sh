#!/bin/bash
set -euo pipefail
export HOME="/Users/byron"
export PATH="/opt/homebrew/bin:/usr/bin:/bin"
RUNTIME="/Volumes/magicBLACKbox/hydradg/services/hydradg-test"
export npm_config_cache="$RUNTIME/cache/npm"
export TMPDIR="$RUNTIME/tmp"
export TMP="$TMPDIR"
export TEMP="$TMPDIR"
# Avoid inherited HOSTNAME quirks
unset HOSTNAME || true
mkdir -p "$RUNTIME/logs" "$RUNTIME/tmp" "$RUNTIME/cache/npm"
WEB="$RUNTIME/current/apps/hydradg-web"
LOG_OUT="$RUNTIME/logs/web.out.log"
LOG_ERR="$RUNTIME/logs/web.err.log"
if [[ ! -d "$WEB/.next" ]]; then
  echo "BUILD_MISSING=$WEB/.next" >>"$LOG_ERR"
  exit 1
fi
cd "$WEB"
exec >>"$LOG_OUT" 2>>"$LOG_ERR"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) starting"
exec /opt/homebrew/bin/node ./node_modules/next/dist/bin/next start -H 127.0.0.1 -p 3000
