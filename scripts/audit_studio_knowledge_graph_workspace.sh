#!/usr/bin/env bash
set -euo pipefail

# Run on magicPRObox. Audits the magicSTUDIObox knowledge-graph workspace
# without mutating repositories.
STUDIO="${STUDIO_SSH:-magicstudiobox}"
ROOT="${STUDIO_KG_ROOT:-/Users/byron/projects/active/hydradg-knowledge-graph}"

ssh -o ConnectTimeout=15 "$STUDIO" "ROOT='$ROOT' bash -s" <<'REMOTE'
set -euo pipefail

echo "STUDIO_HOST=$(hostname)"
echo "WORKSPACE_ROOT=$ROOT"
[ -d "$ROOT" ] || { echo "FAIL=WORKSPACE_ROOT_MISSING"; exit 2; }

echo "=== ROOT CONTENTS ==="
find "$ROOT" -mindepth 1 -maxdepth 2 -type d -print | sort

echo "=== GIT REPOSITORIES ==="
FOUND=0
while IFS= read -r dotgit; do
  repo="${dotgit%/.git}"
  top="$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null || true)"
  [ "$top" = "$repo" ] || continue
  FOUND=$((FOUND+1))
  echo
  echo "REPO_PATH=$repo"
  echo "REPO_NAME=$(basename "$repo")"
  echo "HEAD=$(git -C "$repo" rev-parse HEAD 2>/dev/null || true)"
  echo "BRANCH=$(git -C "$repo" branch --show-current 2>/dev/null || true)"
  echo "DIRTY_COUNT=$(git -C "$repo" status --porcelain | wc -l | tr -d ' ')"
  echo "REMOTES_BEGIN"
  git -C "$repo" remote -v || true
  echo "REMOTES_END"
  if git -C "$repo" remote get-url origin >/dev/null 2>&1; then
    git -C "$repo" fetch origin --prune --quiet || echo "FETCH_ORIGIN=FAIL"
    echo "ORIGIN_FETCH=ATTEMPTED"
    up="$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
    echo "UPSTREAM=${up:-NONE}"
    if [ -n "$up" ]; then
      local_sha="$(git -C "$repo" rev-parse HEAD)"
      remote_sha="$(git -C "$repo" rev-parse "$up" 2>/dev/null || true)"
      echo "LOCAL_SHA=$local_sha"
      echo "UPSTREAM_SHA=${remote_sha:-UNKNOWN}"
      if [ -n "$remote_sha" ] && [ "$local_sha" = "$remote_sha" ]; then echo "SYNC_STATE=EXACT"; else echo "SYNC_STATE=DIFF_OR_UNKNOWN"; fi
    fi
  fi
done < <(find "$ROOT" -mindepth 1 -maxdepth 4 -type d -name .git -print | sort)

echo
echo "REPO_COUNT=$FOUND"
echo "WORKSPACE_AUDIT_COMPLETE=YES"
REMOTE
