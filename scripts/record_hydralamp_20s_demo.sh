#!/usr/bin/env bash
# Bounded HydraLamp 20s demo recorder.
# Prefer existing Chrome/ffmpeg path; do not claim Playwright if absent.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_ROOT="$ROOT/artifacts/hydralamp"
mkdir -p "$OUT_ROOT"
RUN_ID="rec_$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$OUT_ROOT/$RUN_ID"
mkdir -p "$OUT"

PORT="${HYDRALAMP_PORT:-3000}"
URL="http://127.0.0.1:${PORT}/hydralamp?demo=20s"

echo "RECORD_TARGET=$URL"
echo "OUT=$OUT"

if ! curl -fsS "http://127.0.0.1:${PORT}/api/hydralamp/run" >/dev/null 2>&1; then
  echo "SERVER_STATE=NOT_REACHABLE — start apps/hydradg-web (npm run dev/start) first"
  echo "VIDEO_CAPTURE=SKIPPED" | tee "$OUT/CAPTURE_STATUS.txt"
  exit 0
fi

CHROME=""
for c in google-chrome chromium chromium-browser "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do
  if command -v "$c" >/dev/null 2>&1 || [[ -x "$c" ]]; then
    CHROME="$c"
    break
  fi
done

if [[ -z "$CHROME" ]]; then
  echo "CHROME_STATE=NOT_FOUND"
  echo "VIDEO_CAPTURE=SKIPPED" | tee "$OUT/CAPTURE_STATUS.txt"
  exit 0
fi

# Screenshot timeline (not fabricated events) — 20 frames over ~20s
for i in $(seq 0 19); do
  "$CHROME" --headless --disable-gpu --window-size=1280,720 \
    --screenshot="$OUT/frame_$(printf '%02d' "$i").png" "$URL" >/dev/null 2>&1 || true
  sleep 1
done

if command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg -y -framerate 1 -i "$OUT/frame_%02d.png" -c:v libx264 -pix_fmt yuv420p "$OUT/hydralamp_20s.mp4" >/dev/null 2>&1 || true
  if [[ -f "$OUT/hydralamp_20s.mp4" ]]; then
    shasum -a 256 "$OUT/hydralamp_20s.mp4" | awk '{print $1}' > "$OUT/VIDEO_SHA256.txt"
    echo "VIDEO_CAPTURE=PASS path=$OUT/hydralamp_20s.mp4"
  else
    echo "VIDEO_CAPTURE=FAIL_FFMPEG" | tee "$OUT/CAPTURE_STATUS.txt"
  fi
else
  echo "VIDEO_CAPTURE=FRAMES_ONLY_NO_FFMPEG" | tee "$OUT/CAPTURE_STATUS.txt"
fi
