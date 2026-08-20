#!/bin/zsh
set -euo pipefail

SITE="${HYDRADG_VIDEO_SITE:-http://127.0.0.1:3010}"
OUT="${HYDRADG_SCREENSHOT_DIR:-$HOME/.local/share/hydradg-video/screenshots-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT"

for path in / /judge /graph /evidence; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' "$SITE$path" || true)"
  [[ "$code" == "200" ]] || { echo "STOP route=$path http=$code"; exit 20; }
done

echo "=== deterministic browser captures ==="
if command -v agent-browser >/dev/null 2>&1; then
  agent-browser --session hydradg-video open "$SITE/"
  agent-browser --session hydradg-video wait --load networkidle
  agent-browser --session hydradg-video screenshot --full "$OUT/home-full.png"

  agent-browser --session hydradg-video open "$SITE/judge"
  agent-browser --session hydradg-video wait --load networkidle
  agent-browser --session hydradg-video screenshot --full "$OUT/judge-full.png"

  agent-browser --session hydradg-video open "$SITE/graph"
  agent-browser --session hydradg-video wait --load networkidle
  agent-browser --session hydradg-video screenshot --full "$OUT/graph-full.png"

  agent-browser --session hydradg-video open "$SITE/evidence"
  agent-browser --session hydradg-video wait --load networkidle
  agent-browser --session hydradg-video screenshot --full "$OUT/evidence-full.png"

  agent-browser --session hydradg-video close || true
else
  echo "AGENT_BROWSER=PENDING_NOT_INSTALLED" | tee "$OUT/agent-browser-state.txt"
fi

echo "=== actual Google Chrome captures ==="
if [[ -d "/Applications/Google Chrome.app" ]]; then
  open -a "Google Chrome" "$SITE/"
  sleep 2
  osascript <<'APPLESCRIPT'
tell application "Google Chrome"
  activate
  if (count of windows) = 0 then make new window
  set bounds of front window to {0, 25, 1440, 1025}
end tell
APPLESCRIPT

  function chrome_capture() {
    local url="$1"
    local name="$2"
    osascript - "$url" <<'APPLESCRIPT'
on run argv
  tell application "Google Chrome"
    activate
    set URL of active tab of front window to item 1 of argv
  end tell
end run
APPLESCRIPT
    sleep 2
    screencapture -x -R0,25,1440,1000 "$OUT/$name"
  }

  chrome_capture "$SITE/" "chrome-home.png"
  chrome_capture "$SITE/judge" "chrome-judge.png"
  chrome_capture "$SITE/graph" "chrome-graph.png"
  chrome_capture "$SITE/evidence" "chrome-evidence.png"
else
  echo "GOOGLE_CHROME=PENDING_NOT_INSTALLED" | tee "$OUT/google-chrome-state.txt"
fi

(
  cd "$OUT"
  find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256
) > "$OUT/SCREENSHOT_SHA256SUMS.txt"

echo "SCREENSHOT_DIR=$OUT"
echo "SCREENSHOT_MANIFEST=$OUT/SCREENSHOT_SHA256SUMS.txt"
