#!/bin/bash
# Install HydraDG studio-test persistence + deploy watcher.
#
# Observed on magicSTUDIObox (2026-08-26):
#   - launchd ProgramArguments/stdio on /Volumes/magicBLACKbox → exit 78 EX_CONFIG
#   - Cursor agent cannot write ~/Library/LaunchAgents or ~/.local/bin (TCC)
#   - launchd-managed `next start` can hang without binding :3000; nohup supervise works
#
# Therefore:
#   1) Wrappers live in-repo: ops/studio-test/bin/ (boot volume)
#   2) Web persistence default = nohup supervise loop (KeepAlive-equivalent)
#   3) Deploy watcher = launchd StartInterval (outbound git pull only)
#   4) Optional: from Terminal.app, copy plist templates into LaunchAgents for login
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUNTIME="/Volumes/magicBLACKbox/hydradg/services/hydradg-test"
BIN_DIR="${REPO_ROOT}/ops/studio-test/bin"
LOG_DIR="${HOME}/Library/Logs/hydradg-test"
LAUNCH_DIR="${HOME}/Library/LaunchAgents"
UID_NUM="$(id -u)"

if [[ ! -d /Volumes/magicBLACKbox ]]; then
  echo "MAGICBLACKBOX_NOT_MOUNTED" >&2
  exit 1
fi

mkdir -p \
  "${RUNTIME}/"{repo,releases,logs,receipts,state,cache/npm,tmp,bin,launchd} \
  "${BIN_DIR}" "${LOG_DIR}"
mkdir -p /Users/byron/services
if [[ ! -e /Users/byron/services/hydradg-test ]]; then
  ln -s "${RUNTIME}" /Users/byron/services/hydradg-test
fi

chmod +x "${REPO_ROOT}/ops/studio-test/"*.py "${REPO_ROOT}/ops/studio-test/run_web.sh" || true
cp "${REPO_ROOT}/ops/studio-test/deploy.py" "${RUNTIME}/bin/deploy.py"
cp "${REPO_ROOT}/ops/studio-test/healthcheck.py" "${RUNTIME}/bin/healthcheck.py"

# --- boot-volume wrappers ---
cat >"${BIN_DIR}/hydradg-test-supervise-loop.sh" <<'EOF'
#!/bin/bash
export HOME=/Users/byron
export PATH=/opt/homebrew/bin:/usr/bin:/bin
RUNTIME=/Volumes/magicBLACKbox/hydradg/services/hydradg-test
export npm_config_cache=$RUNTIME/cache/npm
export TMPDIR=$RUNTIME/tmp
mkdir -p $RUNTIME/logs $RUNTIME/state $RUNTIME/tmp
echo $$ > $RUNTIME/state/supervise.pid
while true; do
  WEB=$RUNTIME/current/apps/hydradg-web
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) supervise start" >> $RUNTIME/logs/supervise_web.log
  if [[ -d $WEB/.next ]]; then
    cd $WEB
    /opt/homebrew/bin/node ./node_modules/next/dist/bin/next start -H 127.0.0.1 -p 3000 \
      >>$RUNTIME/logs/web.out.log 2>>$RUNTIME/logs/web.err.log
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) exit=$?" >> $RUNTIME/logs/supervise_web.log
  else
    echo "missing build" >> $RUNTIME/logs/supervise_web.log
  fi
  sleep 2
done
EOF

cat >"${BIN_DIR}/hydradg-test-server.sh" <<'EOF'
#!/bin/bash
set -euo pipefail
export HOME="/Users/byron"
export PATH="/opt/homebrew/bin:/usr/bin:/bin"
RUNTIME="/Volumes/magicBLACKbox/hydradg/services/hydradg-test"
export npm_config_cache="$RUNTIME/cache/npm"
export TMPDIR="$RUNTIME/tmp"
WEB="$RUNTIME/current/apps/hydradg-web"
cd "$WEB"
exec /opt/homebrew/bin/node ./node_modules/next/dist/bin/next start -H 127.0.0.1 -p 3000
EOF

cat >"${BIN_DIR}/hydradg-deploy-once.sh" <<EOF
#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/bin:/bin"
export HOME="/Users/byron"
RUNTIME="/Volumes/magicBLACKbox/hydradg/services/hydradg-test"
export npm_config_cache="\$RUNTIME/cache/npm"
export TMPDIR="\$RUNTIME/tmp"
exec /opt/homebrew/bin/python3 "${REPO_ROOT}/ops/studio-test/deploy.py" --repo "${REPO_ROOT}" --once
EOF
chmod +x "${BIN_DIR}/"*

# --- plist templates (repo + optional LaunchAgents) ---
WEB_PLIST_TMP=/tmp/com.biobitworks.hydradg-test.plist
WATCH_PLIST_TMP=/tmp/com.biobitworks.hydradg-deploy-watcher.plist

cat >"${WATCH_PLIST_TMP}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.biobitworks.hydradg-deploy-watcher</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${BIN_DIR}/hydradg-deploy-once.sh</string>
  </array>
  <key>StartInterval</key>
  <integer>60</integer>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/deploy-watcher.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/deploy-watcher.err.log</string>
</dict>
</plist>
EOF

# Web plist kept for Terminal-based experiments; default path is nohup.
cat >"${WEB_PLIST_TMP}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.biobitworks.hydradg-test</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${BIN_DIR}/hydradg-test-supervise-loop.sh</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>/Users/byron</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/bin:/bin</string>
  </dict>
</dict>
</plist>
EOF

cp "${WEB_PLIST_TMP}" "${REPO_ROOT}/ops/studio-test/com.biobitworks.hydradg-test.plist.template"
cp "${WATCH_PLIST_TMP}" "${REPO_ROOT}/ops/studio-test/com.biobitworks.hydradg-deploy-watcher.plist.template"

# Stop conflicting listeners
pkill -f 'next start -H 127.0.0.1 -p 3000' 2>/dev/null || true
if [[ -f "${RUNTIME}/state/supervise.pid" ]]; then
  kill "$(cat "${RUNTIME}/state/supervise.pid")" 2>/dev/null || true
fi
sleep 1

# Default web persistence: nohup supervise
nohup "${BIN_DIR}/hydradg-test-supervise-loop.sh" >/dev/null 2>&1 &
echo $! >"${RUNTIME}/state/supervise.pid"
echo "WEB_SUPERVISE_PID=$(cat "${RUNTIME}/state/supervise.pid")"

# Deploy watcher via launchd (outbound only)
launchctl bootout "gui/${UID_NUM}/com.biobitworks.hydradg-deploy-watcher" 2>/dev/null || true
launchctl bootstrap "gui/${UID_NUM}" "${WATCH_PLIST_TMP}"
# Best-effort copy for login persistence (may fail under Cursor TCC)
cp "${WATCH_PLIST_TMP}" "${LAUNCH_DIR}/com.biobitworks.hydradg-deploy-watcher.plist" 2>/dev/null || \
  echo "NOTE: could not write ${LAUNCH_DIR} (use Terminal.app to copy plist templates for login persistence)"

echo "INSTALLED_WATCHER gui/${UID_NUM}/com.biobitworks.hydradg-deploy-watcher"
echo "WEB_MODE=nohup_supervise (launchd next-start observed hang on this host)"
echo "RUNTIME=${RUNTIME}"
echo "Verify: curl -fsS http://127.0.0.1:3000/"
