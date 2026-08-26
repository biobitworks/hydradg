#!/bin/bash
# launchd wrapper: serve current HydraDG web release on 127.0.0.1:3000 only
set -euo pipefail
RUNTIME="/Volumes/magicBLACKbox/hydradg/services/hydradg-test"
CURRENT="${RUNTIME}/current"
WEB="${CURRENT}/apps/hydradg-web"
export PATH="/opt/homebrew/bin:/usr/bin:/bin"
export npm_config_cache="${RUNTIME}/cache/npm"
export TMPDIR="${RUNTIME}/tmp"
export TMP="${TMPDIR}"
export TEMP="${TMPDIR}"
export PORT=3000
export HOSTNAME=127.0.0.1

if [[ ! -d "$WEB" ]]; then
  echo "WEB_MISSING=$WEB" >&2
  exit 1
fi
if [[ ! -d "$WEB/.next" ]]; then
  echo "BUILD_MISSING=$WEB/.next" >&2
  exit 1
fi
cd "$WEB"
exec /opt/homebrew/bin/npm run start -- -H 127.0.0.1 -p 3000
