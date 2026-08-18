#!/usr/bin/env bash
set -euo pipefail

# Run on magicPRObox. Reconciles the canonical LessWrong workspace on
# magicSTUDIObox with biobitworks/lesswrong, then synchronizes magicPRObox.
#
# Modes:
#   audit  - inspect Studio, Pro, and GitHub only
#   apply  - promote Studio as canonical source, then synchronize Pro
#
# Safety:
# - magicSTUDIObox is the canonical source for the initial import.
# - the existing GitHub stub commit is preserved on pre-studio-import-20260818.
# - dirty worktrees fail closed; nothing is reset or deleted.
# - staged content is scanned with Gitleaks before first publication.

MODE="${1:-audit}"
case "$MODE" in audit|apply) ;; *) echo "USAGE: $0 [audit|apply]"; exit 2;; esac

ACTIVE="/Users/byron/projects/active"
PRO_LW="$ACTIVE/lesswrong"
STUDIO="${STUDIO_SSH:-magicstudiobox}"
STUDIO_LW="$ACTIVE/lesswrong"
REPO="biobitworks/lesswrong"
REMOTE_URL="https://github.com/$REPO.git"
STUB="67d0d071845e26e1cd4d7f60252e2efa67afae3c"
BACKUP_BRANCH="pre-studio-import-20260818"

fail(){ echo "FAIL=$1"; exit "${2:-1}"; }
remote(){ ssh -o ConnectTimeout=15 "$STUDIO" "$@"; }

echo "CONTROL_HOST=$(hostname)"
echo "STUDIO_SSH=$STUDIO"
echo "MODE=$MODE"

audit_one(){
  local label="$1" path="$2"
  echo "=== $label ==="
  if [ ! -d "$path" ]; then echo "PATH=MISSING:$path"; return; fi
  echo "PATH=$path"
  echo "FILE_COUNT=$(find "$path" -path "$path/.git" -prune -o -type f -print | wc -l | tr -d ' ')"
  if git -C "$path" rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "GIT_ROOT=$(git -C "$path" rev-parse --show-toplevel)"
    echo "BRANCH=$(git -C "$path" branch --show-current || true)"
    echo "HEAD=$(git -C "$path" rev-parse HEAD 2>/dev/null || true)"
    echo "ORIGIN=$(git -C "$path" remote get-url origin 2>/dev/null || true)"
    echo "DIRTY_COUNT=$(git -C "$path" status --porcelain | wc -l | tr -d ' ')"
  else
    echo "GIT_ROOT=NONE"
  fi
  POST="$path/mechanical-scientific-method-for-solving-aging"
  if [ -d "$POST" ]; then
    echo "MSM_POST=FOUND"
    echo "MSM_FILE_COUNT=$(find "$POST" -type f | wc -l | tr -d ' ')"
  else
    echo "MSM_POST=MISSING"
  fi
}

echo "=== GITHUB ==="
gh repo view "$REPO" --json nameWithOwner,isPrivate,defaultBranchRef >/dev/null || fail GITHUB_REPO_NOT_ACCESSIBLE 10
REMOTE_MAIN="$(git ls-remote "$REMOTE_URL" refs/heads/main | awk '{print $1}')"
REMOTE_BACKUP="$(git ls-remote "$REMOTE_URL" "refs/heads/$BACKUP_BRANCH" | awk '{print $1}')"
echo "REMOTE_MAIN=$REMOTE_MAIN"
echo "REMOTE_BACKUP=$REMOTE_BACKUP"

# Local audit
audit_one MAGICPRO "$PRO_LW"

# Remote audit
remote 'bash -s' <<'REMOTE_AUDIT'
set -euo pipefail
path="/Users/byron/projects/active/lesswrong"
echo "=== MAGICSTUDIO ==="
if [ ! -d "$path" ]; then echo "PATH=MISSING:$path"; exit 0; fi
echo "PATH=$path"
echo "FILE_COUNT=$(find "$path" -path "$path/.git" -prune -o -type f -print | wc -l | tr -d ' ')"
if git -C "$path" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "GIT_ROOT=$(git -C "$path" rev-parse --show-toplevel)"
  echo "BRANCH=$(git -C "$path" branch --show-current || true)"
  echo "HEAD=$(git -C "$path" rev-parse HEAD 2>/dev/null || true)"
  echo "ORIGIN=$(git -C "$path" remote get-url origin 2>/dev/null || true)"
  echo "DIRTY_COUNT=$(git -C "$path" status --porcelain | wc -l | tr -d ' ')"
else
  echo "GIT_ROOT=NONE"
fi
POST="$path/mechanical-scientific-method-for-solving-aging"
if [ -d "$POST" ]; then
  echo "MSM_POST=FOUND"
  echo "MSM_FILE_COUNT=$(find "$POST" -type f | wc -l | tr -d ' ')"
else
  echo "MSM_POST=MISSING"
fi
REMOTE_AUDIT

[ "$MODE" = "audit" ] && { echo "LESSWRONG_RECONCILE_AUDIT=COMPLETE"; exit 0; }

echo "=== APPLY: MAGICSTUDIO CANONICAL IMPORT ==="
# Backup branch must preserve the pre-import GitHub object if main is still the stub.
if [ "$REMOTE_MAIN" = "$STUB" ]; then
  [ "$REMOTE_BACKUP" = "$STUB" ] || fail STUB_BACKUP_BRANCH_MISSING 20
fi

remote "REPO='$REPO' REMOTE_URL='$REMOTE_URL' STUB='$STUB' BACKUP_BRANCH='$BACKUP_BRANCH' bash -s" <<'REMOTE_APPLY'
set -euo pipefail
LW="/Users/byron/projects/active/lesswrong"
[ -d "$LW" ] || { echo "FAIL=STUDIO_LESSWRONG_MISSING"; exit 30; }
[ -n "$(find "$LW" -mindepth 1 -maxdepth 1 -print -quit)" ] || { echo "FAIL=STUDIO_LESSWRONG_EMPTY"; exit 31; }
command -v git >/dev/null || { echo "FAIL=STUDIO_GIT_MISSING"; exit 32; }
command -v gh >/dev/null || { echo "FAIL=STUDIO_GH_MISSING"; exit 33; }
gh auth status >/dev/null 2>&1 || { echo "FAIL=STUDIO_GH_AUTH_MISSING"; exit 34; }
command -v gitleaks >/dev/null || { echo "FAIL=STUDIO_GITLEAKS_MISSING"; exit 35; }

if ! git -C "$LW" rev-parse --show-toplevel >/dev/null 2>&1; then
  git -C "$LW" init -b main
fi
[ "$(git -C "$LW" rev-parse --show-toplevel)" = "$LW" ] || { echo "FAIL=STUDIO_WRONG_GIT_ROOT"; exit 36; }

cd "$LW"
if [ ! -f .gitignore ]; then
cat > .gitignore <<'EOF'
.DS_Store
__pycache__/
*.pyc
.venv/
.venv-*/
**/.venv/
.env
.env.*
*.pem
*.key
*.p12
*.pfx
*.secret
secrets/
private_keys/
*.pid
*.tmp
EOF
fi

# Refuse any pre-existing tracked/untracked delta only after staging it for a
# bounded secret scan; initial import itself is expected to be untracked.
git add -A
gitleaks git --staged --redact=100 --no-banner .

if ! git rev-parse HEAD >/dev/null 2>&1; then
  git commit -m "Import canonical LessWrong workspace from magicSTUDIObox"
elif ! git diff --cached --quiet; then
  git commit -m "Sync canonical LessWrong workspace from magicSTUDIObox"
fi

if git remote get-url origin >/dev/null 2>&1; then
  ORIGIN="$(git remote get-url origin)"
  case "$ORIGIN" in *biobitworks/lesswrong*) ;; *) echo "FAIL=STUDIO_WRONG_ORIGIN:$ORIGIN"; exit 37;; esac
else
  git remote add origin "$REMOTE_URL"
fi

git fetch origin --prune
LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse origin/main)"

echo "STUDIO_LOCAL_PRE_RECONCILE=$LOCAL"
echo "REMOTE_MAIN_PRE_RECONCILE=$REMOTE"

if git merge-base --is-ancestor "$REMOTE" "$LOCAL" 2>/dev/null; then
  git branch -M main
  git push -u origin main
elif git merge-base --is-ancestor "$LOCAL" "$REMOTE" 2>/dev/null; then
  git branch -M main
  git pull --ff-only origin main
elif [ "$REMOTE" = "$STUB" ]; then
  # The remote stub is preserved on BACKUP_BRANCH before this script is allowed
  # to replace main. This is the only permitted non-fast-forward initial import.
  BACKUP="$(git rev-parse "origin/$BACKUP_BRANCH" 2>/dev/null || true)"
  [ "$BACKUP" = "$STUB" ] || { echo "FAIL=REMOTE_STUB_NOT_BACKED_UP"; exit 38; }
  git branch -M main
  git push --force-with-lease=refs/heads/main:"$STUB" -u origin main
else
  echo "FAIL=UNRELATED_NONSTUB_HISTORY"
  exit 39
fi

git fetch origin --prune
MAIN="$(git rev-parse origin/main)"
for b in test stage; do
  if ! git show-ref --verify --quiet "refs/remotes/origin/$b"; then
    git branch -f "$b" "$MAIN"
    git push -u origin "$b"
  fi
done

git switch main >/dev/null 2>&1
[ -z "$(git status --porcelain)" ] || { echo "FAIL=STUDIO_DIRTY_AFTER_IMPORT"; exit 40; }
L="$(git rev-parse HEAD)"; R="$(git rev-parse origin/main)"
[ "$L" = "$R" ] || { echo "FAIL=STUDIO_POST_IMPORT_DIVERGENCE"; exit 41; }
echo "STUDIO_LESSWRONG_READY=YES"
echo "STUDIO_MAIN=$L"
REMOTE_APPLY

echo "=== APPLY: MAGICPRO SYNCHRONIZATION ==="
if [ -d "$PRO_LW/.git" ]; then
  [ "$(git -C "$PRO_LW" rev-parse --show-toplevel)" = "$PRO_LW" ] || fail PRO_WRONG_GIT_ROOT 50
  [ -z "$(git -C "$PRO_LW" status --porcelain)" ] || fail PRO_LESSWRONG_DIRTY 51
  ORIGIN="$(git -C "$PRO_LW" remote get-url origin 2>/dev/null || true)"
  case "$ORIGIN" in *biobitworks/lesswrong*) ;; *) fail PRO_WRONG_ORIGIN 52;; esac
  git -C "$PRO_LW" fetch origin --prune
  git -C "$PRO_LW" switch main >/dev/null 2>&1 || true
  git -C "$PRO_LW" reset --keep origin/main
elif [ -e "$PRO_LW" ] && [ -n "$(find "$PRO_LW" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
  fail PRO_NON_GIT_NONEMPTY_REQUIRES_REVIEW 53
else
  rm -rf "$PRO_LW"
  gh repo clone "$REPO" "$PRO_LW"
fi

# Create local tracking branches if the remotes exist.
for b in main test stage; do
  git -C "$PRO_LW" fetch origin "$b" --quiet
  if [ "$b" != main ] && ! git -C "$PRO_LW" show-ref --verify --quiet "refs/heads/$b"; then
    git -C "$PRO_LW" branch --track "$b" "origin/$b" >/dev/null
  fi
done
git -C "$PRO_LW" switch main >/dev/null 2>&1
[ -z "$(git -C "$PRO_LW" status --porcelain)" ] || fail PRO_DIRTY_AFTER_SYNC 54

PRO_HEAD="$(git -C "$PRO_LW" rev-parse HEAD)"
REMOTE_HEAD="$(git -C "$PRO_LW" rev-parse origin/main)"
STUDIO_HEAD="$(remote "git -C '$STUDIO_LW' rev-parse HEAD")"
[ "$PRO_HEAD" = "$REMOTE_HEAD" ] || fail PRO_REMOTE_DIVERGENCE 55
[ "$STUDIO_HEAD" = "$REMOTE_HEAD" ] || fail STUDIO_REMOTE_DIVERGENCE 56

echo "LESSWRONG_TWO_MACHINE_READY=YES"
echo "MAIN_SHA=$REMOTE_HEAD"
echo "MAGICPRO_PATH=$PRO_LW"
echo "MAGICSTUDIO_PATH=$STUDIO_LW"
echo "REMOTE=$REPO"
echo "BRANCHES=main,test,stage"
echo "STUB_PRESERVED_AS=$BACKUP_BRANCH"
