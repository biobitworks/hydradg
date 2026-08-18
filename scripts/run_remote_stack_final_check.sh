#!/usr/bin/env bash
set -euo pipefail

# Clean-gated wrapper for the two existing readiness harnesses.
# Run with: bash scripts/run_remote_stack_final_check.sh
#
# Why this wrapper exists:
# remote_final_check.sh and hydradb_studio_check.sh intentionally write their
# evidence under the HydraDG repository, but their current implementations
# create the run directory before their internal `git status --porcelain` gate.
# That makes a genuinely clean checkout appear dirty. This wrapper performs the
# real clean-worktree gate first, then temporarily hides only newly-created
# untracked run artifacts from the child scripts' redundant status checks.
# Tracked modifications remain visible and fail closed.

ROOT="/Users/byron/projects/active/hydradg"
ACTIVE="/Users/byron/projects/active"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
STUDIO_SSH="${STUDIO_SSH:-magicstudiobox}"
PIN="6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219"

log(){ printf '[%3s%%] %s\n' "$1" "$2"; }
fail(){ echo "FAIL=$1"; exit "${2:-1}"; }

restore_status_config(){
  if [ "${STATUS_CONFIG_WAS_SET:-0}" = "1" ]; then
    git -C "$ROOT" config status.showUntrackedFiles "$STATUS_CONFIG_OLD"
  else
    git -C "$ROOT" config --unset status.showUntrackedFiles >/dev/null 2>&1 || true
  fi
}
trap restore_status_config EXIT

log 5 "synchronize HydraDG setup branch on magicPRObox"
cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || fail WRONG_HYDRADG_ROOT 10

# Undo a mode-only chmod on scripts if a prior attempt used `chmod +x`.
# Contents are restored only to the current branch version.
git restore -- scripts/remote_final_check.sh scripts/hydradb_studio_check.sh 2>/dev/null || true

# Preserve failed run evidence rather than deleting it. If a previous failed
# run exists untracked, stop and tell the operator to checkpoint it first.
DIRTY="$(git status --porcelain)"
if [ -n "$DIRTY" ]; then
  echo "=== PRE-EXISTING HYDRADG DELTA ==="
  printf '%s\n' "$DIRTY"
  fail HYDRADG_DIRTY_BEFORE_WRAPPER 11
fi

git fetch origin "$BRANCH" --quiet
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
git pull --ff-only origin "$BRANCH" >/dev/null

test -z "$(git status --porcelain)" || fail HYDRADG_DIRTY_AFTER_PULL 12

log 12 "verify MagicPro local HydraDB source checkout"
LOCAL_HYDRA="$ACTIVE/hydradb"
test -d "$LOCAL_HYDRA/.git" || fail MAGICPRO_HYDRADB_REPO_MISSING 13
git -C "$LOCAL_HYDRA" fetch --all --tags --prune --quiet
git -C "$LOCAL_HYDRA" cat-file -e "${PIN}^{commit}" || fail MAGICPRO_HYDRADB_PIN_MISSING 14
echo "MAGICPRO_HYDRADB_HEAD=$(git -C "$LOCAL_HYDRA" rev-parse HEAD)"
echo "HYDRADB_REQUIRED_PIN=$PIN"

log 18 "verify Tailscale/SSH path before creating evidence"
command -v tailscale >/dev/null || fail TAILSCALE_MISSING_ON_MAGICPRO 15
tailscale status >/dev/null
ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO_SSH" 'command -v tailscale >/dev/null && tailscale status >/dev/null && printf "STUDIO_SSH_TAILSCALE=PASS\n"' || fail STUDIO_SSH_TAILSCALE_FAILED 16

# Save user's repository status configuration, then hide untracked files only
# from the child scripts' redundant internal gate. This does NOT hide tracked
# modifications and does not change what `git add` later records.
if STATUS_CONFIG_OLD="$(git config --get status.showUntrackedFiles 2>/dev/null)"; then
  STATUS_CONFIG_WAS_SET=1
else
  STATUS_CONFIG_WAS_SET=0
  STATUS_CONFIG_OLD=""
fi
git config status.showUntrackedFiles no

log 25 "run Ollarma + Watchtower + repository readiness harness"
STUDIO_SSH="$STUDIO_SSH" HYDRADG_BRANCH="$BRANCH" bash scripts/remote_final_check.sh

# The child must commit/push its evidence and return the tree to clean state.
restore_status_config
STATUS_CONFIG_WAS_SET=0
test -z "$(git status --porcelain)" || fail DIRTY_AFTER_REMOTE_FINAL_CHECK 20

git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")" || fail DIVERGED_AFTER_REMOTE_FINAL_CHECK 21

# Repeat the workaround for the HydraDB-specific harness.
if STATUS_CONFIG_OLD="$(git config --get status.showUntrackedFiles 2>/dev/null)"; then
  STATUS_CONFIG_WAS_SET=1
else
  STATUS_CONFIG_WAS_SET=0
  STATUS_CONFIG_OLD=""
fi
git config status.showUntrackedFiles no

log 62 "run persistent HydraDB studio runtime + write/read + tunnel test"
STUDIO_SSH="$STUDIO_SSH" HYDRADG_BRANCH="$BRANCH" bash scripts/hydradb_studio_check.sh

restore_status_config
STATUS_CONFIG_WAS_SET=0

log 92 "final repository synchronization check"
cd "$ROOT"
test -z "$(git status --porcelain)" || fail HYDRADG_DIRTY_AT_END 30
git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse "origin/$BRANCH")"
test "$LOCAL" = "$REMOTE" || fail HYDRADG_FINAL_DIVERGENCE 31

log 96 "verify all tunneled operator endpoints"
curl -fsS http://127.0.0.1:18484/health >/dev/null || fail FINAL_OLLARMA_TUNNEL_FAILED 32
curl -fsSI http://127.0.0.1:18000/ >/dev/null || fail FINAL_WATCHTOWER_TUNNEL_FAILED 33
curl -fsS http://127.0.0.1:19090/readyz >/dev/null || fail FINAL_HYDRADB_ADMIN_TUNNEL_FAILED 34

log 100 "remote stack ready"
echo "REMOTE_STACK_READY=YES"
echo "HYDRADG_BRANCH=$BRANCH"
echo "HYDRADG_CHECKPOINT_COMMIT=$LOCAL"
echo "MAGICSTUDIO_HYDRADG=/Users/byron/projects/active/hydradg"
echo "MAGICSTUDIO_HYDRADB=/Users/byron/projects/active/hydradb"
echo "OLLARMA_REMOTE_URL=http://127.0.0.1:18484"
echo "WATCHTOWER_REMOTE_URL=http://127.0.0.1:18000"
echo "HYDRADB_HTTP_TUNNEL=http://127.0.0.1:18443"
echo "HYDRADB_BOLT_TUNNEL=bolt://127.0.0.1:17687"
echo "HYDRADB_ADMIN_TUNNEL=http://127.0.0.1:19090"
