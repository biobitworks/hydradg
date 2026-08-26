#!/bin/bash
# Install machine-local launchd agents for HydraDG studio-test + deploy watcher.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUNTIME="/Volumes/magicBLACKbox/hydradg/services/hydradg-test"
LAUNCH_DIR="${HOME}/Library/LaunchAgents"
UID_NUM="$(id -u)"

mkdir -p "${RUNTIME}/logs" "${RUNTIME}/launchd" "${LAUNCH_DIR}"
chmod +x "${REPO_ROOT}/ops/studio-test/run_web.sh"
chmod +x "${REPO_ROOT}/ops/studio-test/deploy.py"
chmod +x "${REPO_ROOT}/ops/studio-test/healthcheck.py"

# Copy wrappers onto BLACKBOX so launchd does not depend on mutable worktree path for the runner itself
cp "${REPO_ROOT}/ops/studio-test/run_web.sh" "${RUNTIME}/bin/run_web.sh"
cp "${REPO_ROOT}/ops/studio-test/deploy.py" "${RUNTIME}/bin/deploy.py"
cp "${REPO_ROOT}/ops/studio-test/healthcheck.py" "${RUNTIME}/bin/healthcheck.py"
chmod +x "${RUNTIME}/bin/"*

WEB_PLIST="${LAUNCH_DIR}/com.biobitworks.hydradg-test.plist"
WATCH_PLIST="${LAUNCH_DIR}/com.biobitworks.hydradg-deploy-watcher.plist"

cat >"${WEB_PLIST}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.biobitworks.hydradg-test</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${RUNTIME}/bin/run_web.sh</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${RUNTIME}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/bin:/bin</string>
    <key>npm_config_cache</key>
    <string>${RUNTIME}/cache/npm</string>
    <key>TMPDIR</key>
    <string>${RUNTIME}/tmp</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${RUNTIME}/logs/hydradg-test.out.log</string>
  <key>StandardErrorPath</key>
  <string>${RUNTIME}/logs/hydradg-test.err.log</string>
  <key>ProcessType</key>
  <string>Background</string>
</dict>
</plist>
EOF

cat >"${WATCH_PLIST}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.biobitworks.hydradg-deploy-watcher</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/python3</string>
    <string>${RUNTIME}/bin/deploy.py</string>
    <string>--repo</string>
    <string>${REPO_ROOT}</string>
    <string>--once</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${REPO_ROOT}</string>
  <key>StartInterval</key>
  <integer>60</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/bin:/bin</string>
    <key>npm_config_cache</key>
    <string>${RUNTIME}/cache/npm</string>
    <key>TMPDIR</key>
    <string>${RUNTIME}/tmp</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${RUNTIME}/logs/deploy-watcher.out.log</string>
  <key>StandardErrorPath</key>
  <string>${RUNTIME}/logs/deploy-watcher.err.log</string>
  <key>ProcessType</key>
  <string>Background</string>
</dict>
</plist>
EOF

# Keep templates in repo for version control
cp "${WEB_PLIST}" "${REPO_ROOT}/ops/studio-test/com.biobitworks.hydradg-test.plist.template"
cp "${WATCH_PLIST}" "${REPO_ROOT}/ops/studio-test/com.biobitworks.hydradg-deploy-watcher.plist.template"
# Also store machine copies under runtime
cp "${WEB_PLIST}" "${RUNTIME}/launchd/"
cp "${WATCH_PLIST}" "${RUNTIME}/launchd/"

boot() {
  local label="$1"
  local plist="$2"
  launchctl bootout "gui/${UID_NUM}/${label}" 2>/dev/null || true
  launchctl bootstrap "gui/${UID_NUM}" "${plist}"
  launchctl enable "gui/${UID_NUM}/${label}" || true
}

boot "com.biobitworks.hydradg-test" "${WEB_PLIST}"
boot "com.biobitworks.hydradg-deploy-watcher" "${WATCH_PLIST}"

echo "INSTALLED ${WEB_PLIST}"
echo "INSTALLED ${WATCH_PLIST}"
echo "NOTE: hydradg-test requires ${RUNTIME}/current to point at a built release before it can serve."
