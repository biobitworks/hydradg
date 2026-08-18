#!/usr/bin/env bash
set -euo pipefail

# True one-command remote-work bootstrap.
# RUN ONLY ON magicPRObox.
#
# Sequence:
# 1. Verify PRObox control identity + SSH/Tailscale path to Studio.
# 2. Bootstrap Homebrew on Studio if absent (interactive SSH TTY only if needed).
# 3. Pull the current HydraDG remote-work branch.
# 4. Run universal two-machine GitHub/toolchain/repository synchronization.
# 5. Run the critical remote stack checks unless RUN_STACK_TESTS=0.

ROOT="/Users/byron/projects/active/hydradg"
STUDIO="${STUDIO_SSH:-magicstudiobox}"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"

fail(){ echo "FAIL=$1"; exit "${2:-1}"; }
log(){ printf '\n[%3s%%] %s\n' "$1" "$2"; }

log 2 "verify magicPRObox control host"
IDS="$(printf '%s %s %s' "$(scutil --get ComputerName 2>/dev/null || true)" "$(scutil --get LocalHostName 2>/dev/null || true)" "$(hostname 2>/dev/null || true)" | tr '[:upper:]' '[:lower:]')"
case "$IDS" in *magicprobox*) ;; *) fail RUN_ON_MAGICPROBOX_ONLY 2 ;; esac

test -d "$ROOT/.git" || fail HYDRADG_NOT_GIT_REPO 3
command -v tailscale >/dev/null || fail MAGICPRO_TAILSCALE_MISSING 4
command -v ssh >/dev/null || fail MAGICPRO_SSH_MISSING 5

tailscale status >/dev/null
ssh -o BatchMode=yes -o ConnectTimeout=12 "$STUDIO" 'command -v tailscale >/dev/null && tailscale status >/dev/null' || fail STUDIO_SSH_TAILSCALE_FAILED 6

log 10 "synchronize bootstrap scripts from GitHub"
cd "$ROOT"
git fetch origin "$BRANCH"
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
# Do not pull across an unrelated dirty worktree. The universal controller will
# checkpoint evidence, but this wrapper must be able to obtain its own helpers.
if [ -n "$(git status --porcelain)" ]; then
  TMP="$(mktemp /tmp/hydradg-wrapper-checkpoint.XXXXXX.sh)"
  git show "origin/$BRANCH:scripts/checkpoint_dirty_worktree.sh" > "$TMP"
  bash "$TMP"
  rm -f "$TMP"
  git switch "$BRANCH"
fi
git pull --ff-only origin "$BRANCH"

log 20 "bootstrap Homebrew on magicSTUDIObox if needed"
if ssh "$STUDIO" 'test -x /opt/homebrew/bin/brew || command -v brew >/dev/null 2>&1'; then
  echo "STUDIO_HOMEBREW=ALREADY_PRESENT"
else
  echo "STUDIO_HOMEBREW=MISSING"
  echo "Starting the one-time Homebrew installer through an interactive Studio SSH TTY."
  bash "$ROOT/scripts/bootstrap_magicstudio_homebrew_from_magicpro.sh"
fi

ssh "$STUDIO" 'test -x /opt/homebrew/bin/brew || command -v brew >/dev/null 2>&1' || fail STUDIO_HOMEBREW_BOOTSTRAP_FAILED 20

log 30 "run universal GitHub + active-project synchronization"
cd "$ROOT"
STUDIO_SSH="$STUDIO" HYDRADG_BRANCH="$BRANCH" RUN_STACK_TESTS="${RUN_STACK_TESTS:-1}" \
  bash scripts/magicpro_universal_github_setup.sh

log 100 "all-in-one remote work bootstrap complete"
echo "REMOTE_WORK_ALL_IN_ONE=PASS"
echo "CONTROL_HOST=magicPRObox"
echo "EXECUTION_HOST=magicSTUDIObox"
echo "NEXT=Use SSH/Tailscale for machine control; Ollarma/HydraDB via localhost tunnels; GitHub for persistent source/evidence sync."
