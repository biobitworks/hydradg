#!/usr/bin/env bash
set -euo pipefail

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
VIDEO_ROOT="${HYDRADG_VIDEO_ROOT:-/Users/byron/projects/active/hydradg-video}"
REMOTE_REF="origin/hack-hydra/context-iceberg-reconcile-20260819"

cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || { echo "STOP: wrong HydraDG root"; exit 10; }

echo "ACTIVE_WORKTREE_BRANCH=$(git branch --show-current)"
echo "ACTIVE_WORKTREE_COMMIT=$(git rev-parse HEAD)"
echo "ACTIVE_WORKTREE_MUTATION=NOT_PERFORMED"

git fetch origin hack-hydra/context-iceberg-reconcile-20260819
REMOTE_SHA="$(git rev-parse "$REMOTE_REF")"
echo "VIDEO_REMOTE_SHA=$REMOTE_SHA"

if [[ -e "$VIDEO_ROOT/.git" || -f "$VIDEO_ROOT/.git" ]]; then
  test -z "$(git -C "$VIDEO_ROOT" status --porcelain)" || {
    echo "STOP: existing video worktree is dirty: $VIDEO_ROOT"
    git -C "$VIDEO_ROOT" status --short
    exit 20
  }
  git -C "$VIDEO_ROOT" fetch origin hack-hydra/context-iceberg-reconcile-20260819
  git -C "$VIDEO_ROOT" switch --detach "$REMOTE_REF"
else
  test ! -e "$VIDEO_ROOT" || { echo "STOP: path exists but is not a Git worktree: $VIDEO_ROOT"; exit 21; }
  git worktree add --detach "$VIDEO_ROOT" "$REMOTE_REF"
fi

ACTUAL="$(git -C "$VIDEO_ROOT" rev-parse HEAD)"
test "$ACTUAL" = "$REMOTE_SHA" || { echo "STOP: video worktree SHA mismatch"; exit 22; }
test -z "$(git -C "$VIDEO_ROOT" status --porcelain)" || { echo "STOP: new video worktree is dirty"; exit 23; }

echo "VIDEO_WORKTREE_READY=YES"
echo "VIDEO_ROOT=$VIDEO_ROOT"
echo "VIDEO_COMMIT=$ACTUAL"
echo "NEXT=HYDRADG_ROOT=$VIDEO_ROOT bash $VIDEO_ROOT/scripts/video_ready_gate.sh"
