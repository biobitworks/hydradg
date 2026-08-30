#!/usr/bin/env bash
# Render HydraLamp replay video from frames
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMES_DIR="${REPO_ROOT}/eval/hydralamp_20260826/replay/frames"
OUTPUT="${REPO_ROOT}/eval/hydralamp_20260826/replay/HYDRALAMP_REPLAY.mp4"
RECEIPT="${REPO_ROOT}/eval/hydralamp_20260826/replay/VIDEO_RECEIPT.json"
FPS="${HYDRALAMP_FPS:-2}"

if [[ ! -d "$FRAMES_DIR" ]] || [[ -z "$(ls -A "$FRAMES_DIR"/*.png 2>/dev/null)" ]]; then
  echo "No frames found; running render_hydralamp_frames.py first"
  "${REPO_ROOT}/.venv-hydralamp/bin/python" "${REPO_ROOT}/scripts/render_hydralamp_frames.py"
fi

FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -1)
ffmpeg -y -framerate "$FPS" -pattern_type glob -i "${FRAMES_DIR}/frame_*.png" \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$OUTPUT"

VIDEO_SHA=$(shasum -a 256 "$OUTPUT" | awk '{print $1}')
FRAME_MANIFEST="${REPO_ROOT}/eval/hydralamp_20260826/replay/FRAME_SHA256SUMS.txt"

cat > "$RECEIPT" <<EOF
{
  "schema": "hydradg.hydralamp.video_receipt.v1",
  "video_path": "eval/hydralamp_20260826/replay/HYDRALAMP_REPLAY.mp4",
  "video_sha256": "${VIDEO_SHA}",
  "ffmpeg_version": "${FFMPEG_VERSION}",
  "fps": ${FPS},
  "encoding": "libx264 yuv420p",
  "frame_manifest": "eval/hydralamp_20260826/replay/FRAME_SHA256SUMS.txt",
  "deterministic_claim": "FRAME_HASH_MANIFEST_PRIMARY",
  "mp4_byte_identical_claim": "PENDING_INDEPENDENT_RERENDER"
}
EOF

echo "Video: $OUTPUT"
echo "SHA256: $VIDEO_SHA"
cat "$RECEIPT"
