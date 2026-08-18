#!/usr/bin/env bash
set -euo pipefail

# One-time/fail-closed GitHub bootstrap for the two-machine research setup.
# Usage:
#   bash scripts/setup_github_both_machines.sh studio
#   bash scripts/setup_github_both_machines.sh pro
#
# Canonical machine paths:
#   /Users/byron/projects/active/hydradg
#   /Users/byron/projects/active/lesswrong
#
# Repository policy:
#   biobitworks/hydradg  = private canonical HydraDG history
#   biobitworks/lesswrong = private canonical LessWrong/article history
#   branches main/test/stage are private custody domains; public export remains a separate repository.

ROLE="${1:-}"
case "$ROLE" in
  studio|pro) ;;
  *) echo "USAGE: $0 {studio|pro}"; exit 2 ;;
esac

ACTIVE="/Users/byron/projects/active"
HYDRA="$ACTIVE/hydradg"
LW="$ACTIVE/lesswrong"
HYDRA_REPO="biobitworks/hydradg"
LW_REPO="biobitworks/lesswrong"

log(){ printf '[%3s%%] %s\n' "$1" "$2"; }
fail(){ echo "FAIL=$1"; exit "${2:-1}"; }

require(){ command -v "$1" >/dev/null 2>&1 || fail "MISSING_$1" 10; }
require git
require gh

log 5 "GitHub authentication"
if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated on this machine."
  echo "Run once: gh auth login --hostname github.com --git-protocol https --web"
  exit 11
fi
gh auth setup-git >/dev/null

NAME="$(git config --global user.name || true)"
EMAIL="$(git config --global user.email || true)"
if [ -z "$NAME" ] || [ -z "$EMAIL" ]; then
  echo "Git identity is incomplete. Configure it once on this machine, then rerun:"
  echo "  git config --global user.name 'YOUR NAME'"
  echo "  git config --global user.email 'YOUR GITHUB EMAIL OR NOREPLY EMAIL'"
  exit 12
fi

echo "GIT_IDENTITY_NAME=$NAME"
echo "GIT_IDENTITY_EMAIL=$EMAIL"

sync_branches(){
  local root="$1"
  local repo="$2"
  cd "$root"

  test -z "$(git status --porcelain)" || {
    git status --short
    fail "DIRTY_WORKTREE:$root" 20
  }

  local origin
  origin="$(git remote get-url origin 2>/dev/null || true)"
  test -n "$origin" || fail "ORIGIN_MISSING:$root" 21
  case "$origin" in
    *"$repo"*) ;;
    *) echo "ORIGIN=$origin"; fail "WRONG_ORIGIN:$root" 22 ;;
  esac

  git fetch origin --prune
  git switch main >/dev/null 2>&1 || fail "MAIN_BRANCH_MISSING:$root" 23
  git pull --ff-only origin main

  for b in test stage; do
    if git show-ref --verify --quiet "refs/remotes/origin/$b"; then
      if ! git show-ref --verify --quiet "refs/heads/$b"; then
        git branch --track "$b" "origin/$b" >/dev/null
      fi
    else
      git branch "$b" main
      git push -u origin "$b"
    fi
  done

  local l r
  l="$(git rev-parse main)"
  r="$(git rev-parse origin/main)"
  test "$l" = "$r" || fail "MAIN_DIVERGED:$root" 24
  echo "SYNCED=$root:$l"
}

log 15 "HydraDG GitHub synchronization"
test -d "$HYDRA/.git" || fail "HYDRADG_NOT_GIT_REPO:$HYDRA" 30
test "$(git -C "$HYDRA" rev-parse --show-toplevel)" = "$HYDRA" || fail "HYDRADG_WRONG_ROOT" 31
sync_branches "$HYDRA" "$HYDRA_REPO"

if [ "$ROLE" = "studio" ]; then
  log 35 "Bootstrap canonical LessWrong repository from magicSTUDIObox"
  test -d "$LW" || fail "LESSWRONG_PATH_MISSING:$LW" 40

  if [ ! -d "$LW/.git" ]; then
    git -C "$LW" init -b main
  fi
  test "$(git -C "$LW" rev-parse --show-toplevel)" = "$LW" || fail "LESSWRONG_WRONG_GIT_ROOT" 41

  # Never overwrite an existing ignore policy. Create a conservative baseline only if absent.
  if [ ! -f "$LW/.gitignore" ]; then
    cat > "$LW/.gitignore" <<'EOF'
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

  # Initial publication to GitHub requires the actual secret-scanner gate.
  if ! command -v gitleaks >/dev/null 2>&1; then
    echo "gitleaks is required before the first LessWrong repository push."
    echo "Install once (Homebrew): brew install gitleaks"
    exit 42
  fi

  # Refuse unexpectedly large objects; use Git LFS deliberately if a real artifact needs it.
  BIG=0
  while IFS= read -r -d '' f; do
    [ -f "$f" ] || continue
    size="$(stat -f %z "$f")"
    if [ "$size" -gt 95000000 ]; then
      echo "OVER_95MB size=$size file=$f"
      BIG=1
    fi
  done < <(find "$LW" -path "$LW/.git" -prune -o -type f -print0)
  [ "$BIG" -eq 0 ] || fail "LESSWRONG_LARGE_FILE_GATE" 43

  cd "$LW"
  git add -A
  gitleaks git --staged --redact=100 --no-banner .

  if ! git rev-parse HEAD >/dev/null 2>&1; then
    git commit -m "Initialize LessWrong FCO/FCG workspace"
  elif ! git diff --cached --quiet; then
    git commit -m "Sync LessWrong FCO/FCG workspace before two-machine bootstrap"
  fi

  if gh repo view "$LW_REPO" >/dev/null 2>&1; then
    if ! git remote get-url origin >/dev/null 2>&1; then
      git remote add origin "https://github.com/$LW_REPO.git"
    fi
    git fetch origin --prune || true
    if git show-ref --verify --quiet refs/remotes/origin/main; then
      # Never merge unrelated histories during bootstrap.
      if ! git merge-base --is-ancestor origin/main main && ! git merge-base --is-ancestor main origin/main; then
        fail "LESSWRONG_REMOTE_HAS_UNRELATED_HISTORY" 44
      fi
      git pull --ff-only origin main
    fi
  else
    gh repo create "$LW_REPO" --private --source=. --remote=origin
  fi

  git push -u origin main
  for b in test stage; do
    if ! git show-ref --verify --quiet "refs/heads/$b"; then git branch "$b" main; fi
    git push -u origin "$b"
  done
  git fetch origin --prune

  L="$(git rev-parse main)"
  R="$(git rev-parse origin/main)"
  test "$L" = "$R" || fail "LESSWRONG_POST_PUSH_DIVERGENCE" 45
  echo "LESSWRONG_CANONICAL_REPO=$LW_REPO"
  echo "LESSWRONG_MAIN=$L"

else
  log 35 "Clone/synchronize LessWrong repository on magicPRObox"

  gh repo view "$LW_REPO" >/dev/null 2>&1 || fail "LESSWRONG_REMOTE_NOT_CREATED_YET:run_studio_first" 50

  if [ -d "$LW/.git" ]; then
    test "$(git -C "$LW" rev-parse --show-toplevel)" = "$LW" || fail "LESSWRONG_WRONG_GIT_ROOT" 51
  elif [ -e "$LW" ] && [ -n "$(find "$LW" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
    echo "Existing non-Git LessWrong directory will not be overwritten automatically: $LW"
    echo "Review it, then move it aside, e.g.:"
    echo "  mv '$LW' '${LW}.pre-github-$(date +%Y%m%dT%H%M%S)'"
    echo "Then rerun this script with role=pro."
    exit 52
  else
    rm -rf "$LW"
    mkdir -p "$ACTIVE"
    gh repo clone "$LW_REPO" "$LW"
  fi

  sync_branches "$LW" "$LW_REPO"
fi

log 75 "Cross-repository local state"
for P in "$HYDRA" "$LW"; do
  cd "$P"
  echo "REPO=$P"
  echo "ORIGIN=$(git remote get-url origin)"
  echo "MAIN_LOCAL=$(git rev-parse main)"
  echo "MAIN_REMOTE=$(git rev-parse origin/main)"
  echo "TEST_REMOTE=$(git rev-parse origin/test)"
  echo "STAGE_REMOTE=$(git rev-parse origin/stage)"
done

log 90 "GitHub CLI repository access"
gh repo view "$HYDRA_REPO" --json nameWithOwner,isPrivate,defaultBranchRef
gh repo view "$LW_REPO" --json nameWithOwner,isPrivate,defaultBranchRef

log 100 "complete"
echo "GITHUB_MACHINE_READY=YES"
echo "ROLE=$ROLE"
echo "HYDRADG=$HYDRA_REPO"
echo "LESSWRONG=$LW_REPO"
echo "PUBLIC_EXPORT=SEPARATE_REPOSITORY_NOT_CREATED_BY_THIS_SCRIPT"
