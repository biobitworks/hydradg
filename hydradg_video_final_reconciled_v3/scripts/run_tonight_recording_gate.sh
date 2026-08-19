#!/bin/zsh
set -euo pipefail

ROOT=/Users/byron/projects/active/hydradg
BRANCH=hack-hydra/context-iceberg-reconcile-20260819
VIDEO_ROOT=/Users/byron/projects/active/hydradg-video

cd "$ROOT"
git fetch origin "$BRANCH"

git show "origin/${BRANCH}:scripts/prepare_video_worktree.sh" | bash

command -v gitleaks >/dev/null 2>&1 || {
  echo "BLOCKER=GITLEAKS_MISSING"
  echo "Install with: brew install gitleaks"
  exit 20
}

set +e
HYDRADG_ROOT="$VIDEO_ROOT" bash "$VIDEO_ROOT/scripts/video_ready_gate.sh" > /tmp/hydradg-video-live-gate.log 2>&1
LIVE_RC=$?
set -e
cat /tmp/hydradg-video-live-gate.log

if grep -q '^VIDEO_READY_LIVE=YES$' /tmp/hydradg-video-live-gate.log; then
  echo "VIDEO_PATH=LIVE"
  HYDRADG_ROOT="$VIDEO_ROOT" HYDRADG_VIDEO_MODE=live \
    bash "$VIDEO_ROOT/scripts/start_video_demo.sh"
  echo "NEXT=CAPTURE_SCREENSHOTS_AND_RECORD"
  exit 0
fi

echo "=== STATIC FALLBACK GATE ==="
HYDRADG_ROOT="$VIDEO_ROOT" bash "$VIDEO_ROOT/scripts/static_video_gate.sh" | tee /tmp/hydradg-video-static-gate.log

if grep -q '^STATIC_VIDEO_READY=YES$' /tmp/hydradg-video-static-gate.log; then
  echo "VIDEO_PATH=STATIC_FALLBACK"
  HYDRADG_ROOT="$VIDEO_ROOT" HYDRADG_VIDEO_MODE=static \
    bash "$VIDEO_ROOT/scripts/start_video_demo.sh"
  echo "NEXT=CAPTURE_SCREENSHOTS_AND_RECORD_AS_OFFLINE_FALLBACK"
  exit 0
fi

echo "VIDEO_READY=NO"
echo "BLOCKER=NEITHER_LIVE_NOR_STATIC_GATE_PASSED"
exit 30
