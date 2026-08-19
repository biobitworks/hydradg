#!/usr/bin/env bash
set -euo pipefail
REPO="${HYDRADG_REPO:-/Users/byron/projects/active/hydradg}"
BASE_COMMIT="${HYDRADG_BASE_COMMIT:-0d409c5c34f8ecb772780f95be74ef9ea59879e6}"
BRANCH="${HYDRADG_MATRIX_BRANCH:-local/daisy-seedgraph-matrix-20260819}"

cd "$REPO"

echo "== current =="
git status --short
git rev-parse HEAD
git branch --show-current

if ! git diff --quiet -- apps/hydradg-web/next-env.d.ts 2>/dev/null; then
  git stash push -m "pre-matrix next-env local state 2026-08-19" -- apps/hydradg-web/next-env.d.ts
fi

# Refuse to hide any other local work.
if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: remaining working-tree changes exist. Preserve/commit them before matrix work."
  git status --short
  exit 2
fi

git cat-file -e "${BASE_COMMIT}^{commit}"

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git switch "$BRANCH"
else
  git switch -c "$BRANCH" "$BASE_COMMIT"
fi

echo "== matrix branch =="
git rev-parse HEAD
git branch --show-current
git status --short
