#!/bin/zsh
set -euo pipefail
ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
LABEL="com.biobitworks.hydradg.appliance"
SRC="$ROOT/ops/magicstudiobox/launchd/$LABEL.plist"
DST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/.local/share/hydradg-appliance"
cp "$SRC" "$DST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$DST"
launchctl enable "gui/$(id -u)/$LABEL"
launchctl kickstart -k "gui/$(id -u)/$LABEL"
echo "LAUNCHAGENT=$DST"
echo "LOCAL=http://127.0.0.1:3010"
HOST="$(scutil --get LocalHostName 2>/dev/null || true)"
[[ -n "$HOST" ]] && echo "BONJOUR=http://$HOST.local:3010"
