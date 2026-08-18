#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/byron/projects/active/hydradg"
cd "$ROOT"

test "$(git rev-parse --show-toplevel)" = "$ROOT" || {
  echo "FAIL=WRONG_GIT_ROOT"
  exit 2
}

if [ -z "$(git status --porcelain)" ]; then
  echo "WORKTREE_ALREADY_CLEAN=YES"
  exit 0
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
HOST_LABEL="$(scutil --get ComputerName 2>/dev/null || hostname)"
HOST_SAFE="$(printf '%s' "$HOST_LABEL" | tr '[:upper:] ' '[:lower:]_')"
BRANCH="checkpoint/${HOST_SAFE}-pre-bootstrap-${STAMP}"
BASE="$(git branch --show-current)"

echo "BASE_BRANCH=$BASE"
echo "CHECKPOINT_BRANCH=$BRANCH"
echo "=== DIRTY STATE ==="
git status --short

# Refuse unexpected large files before staging. Use LFS deliberately rather than
# accidentally embedding a >95 MB research object in ordinary Git history.
BIG=0
while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue
  size="$(stat -f %z "$f")"
  if [ "$size" -gt 95000000 ]; then
    echo "OVER_95MB size=$size file=$f"
    BIG=1
  fi
done < <(git ls-files --others --modified --exclude-standard -z)
[ "$BIG" -eq 0 ] || {
  echo "FAIL=LARGE_FILE_REQUIRES_EXPLICIT_LFS_REVIEW"
  exit 20
}

command -v gitleaks >/dev/null 2>&1 || {
  echo "FAIL=MISSING_GITLEAKS"
  echo "Install once: brew install gitleaks"
  exit 21
}

git switch -c "$BRANCH"
git add -A

gitleaks git --staged --redact=100 --no-banner . || {
  echo "FAIL=GITLEAKS_STAGED"
  echo "No commit was created. Review staged findings before continuing."
  exit 22
}

if git diff --cached --quiet; then
  echo "NOTHING_TO_COMMIT"
else
  git commit -m "Checkpoint ${HOST_LABEL} pre-bootstrap worktree ${STAMP}"
fi

COMMIT="$(git rev-parse HEAD)"
git push -u origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
REMOTE="$(git rev-parse "origin/$BRANCH")"
test "$COMMIT" = "$REMOTE" || {
  echo "FAIL=CHECKPOINT_PUSH_DIVERGENCE"
  exit 23
}

echo "CHECKPOINT_PUSHED=YES"
echo "CHECKPOINT_COMMIT=$COMMIT"
echo "CHECKPOINT_BRANCH=$BRANCH"
echo "RETURN_TO_BASE_WITH: git switch '$BASE'"
