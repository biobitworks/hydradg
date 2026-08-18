#!/usr/bin/env bash
set -euo pipefail

# Universal two-machine GitHub + remote-work bootstrap.
# RUN ONLY ON magicPRObox.
#
# Control plane: magicPRObox
# Execution plane: magicSTUDIObox
# Transport: ordinary SSH over Tailscale
# Model lane: Ollarma tunnel (not a shell)
# Persistence/sync: GitHub
#
# Default scope: union of top-level projects already present under
# /Users/byron/projects/active on either machine, plus LessWrong.
#
# Safe behavior:
# - no force-push
# - no history rewrite
# - no deletion of non-Git project directories
# - no pull into dirty repos
# - no assumption that every repo uses main
# - no plaintext secret/private-key admission
# - evidence is held in /tmp until the final commit, so running the script
#   cannot dirty HydraDG before its own clean/checkpoint gate.

ROOT="/Users/byron/projects/active/hydradg"
ACTIVE="/Users/byron/projects/active"
STUDIO="${STUDIO_SSH:-magicstudiobox}"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
RUN_STACK_TESTS="${RUN_STACK_TESTS:-1}"
RUN_ID="PORTFOLIO-GITHUB-$(date -u +%Y%m%dT%H%M%SZ)"
TMP_OUT="$(mktemp -d "/tmp/${RUN_ID}.XXXXXX")"
FINAL_REL="HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
FINAL_OUT="$ROOT/$FINAL_REL"
trap 'rm -rf "$TMP_OUT"' EXIT

log(){ printf '\n[%3s%%] %s\n' "$1" "$2"; }
fail(){
  local msg="$1" code="${2:-1}"
  printf 'FAIL=%s\n' "$msg" | tee -a "$TMP_OUT/final_status.txt" >&2
  exit "$code"
}
remote(){ ssh -o ConnectTimeout=12 "$STUDIO" "$@"; }

normalize_origin(){
  printf '%s' "$1" | sed -E \
    -e 's#^git@github\.com:##' \
    -e 's#^https://github\.com/##' \
    -e 's#^ssh://git@github\.com/##' \
    -e 's#/$##' -e 's#\.git$##'
}

inventory_local(){
  local out="$1"
  : > "$out"
  for d in "$ACTIVE"/*; do
    [ -d "$d" ] || continue
    local name top origin repo branch dirty
    name="$(basename "$d")"
    top="$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || true)"
    if [ "$top" = "$d" ]; then
      origin="$(git -C "$d" remote get-url origin 2>/dev/null || true)"
      repo="$(normalize_origin "$origin")"
      branch="$(git -C "$d" branch --show-current 2>/dev/null || true)"
      dirty=0; [ -n "$(git -C "$d" status --porcelain 2>/dev/null)" ] && dirty=1
      printf 'GIT\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$d" "$repo" "$origin" "$branch" "$dirty" >> "$out"
    else
      printf 'NONGIT\t%s\t%s\t\t\t\t\n' "$name" "$d" >> "$out"
    fi
  done
}

inventory_remote(){
  remote 'bash -s' <<'REMOTE_INV'
set -euo pipefail
ACTIVE="/Users/byron/projects/active"
normalize(){ printf '%s' "$1" | sed -E -e 's#^git@github\.com:##' -e 's#^https://github\.com/##' -e 's#^ssh://git@github\.com/##' -e 's#/$##' -e 's#\.git$##'; }
for d in "$ACTIVE"/*; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  top="$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ "$top" = "$d" ]; then
    origin="$(git -C "$d" remote get-url origin 2>/dev/null || true)"
    repo="$(normalize "$origin")"
    branch="$(git -C "$d" branch --show-current 2>/dev/null || true)"
    dirty=0; [ -n "$(git -C "$d" status --porcelain 2>/dev/null)" ] && dirty=1
    printf 'GIT\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$d" "$repo" "$origin" "$branch" "$dirty"
  else
    printf 'NONGIT\t%s\t%s\t\t\t\t\n' "$name" "$d"
  fi
done
REMOTE_INV
}

sync_clean_repo_local(){
  local p="$1"
  [ -d "$p/.git" ] || return 0
  if [ -n "$(git -C "$p" status --porcelain)" ]; then
    echo "DEFERRED_DIRTY LOCAL $p" | tee -a "$TMP_OUT/sync_actions.log"
    return 0
  fi
  git -C "$p" fetch origin --prune --quiet || {
    echo "FETCH_FAIL LOCAL $p" | tee -a "$TMP_OUT/sync_actions.log"; return 0;
  }
  local b up
  b="$(git -C "$p" branch --show-current || true)"
  up="$(git -C "$p" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
  if [ -n "$b" ] && [ -n "$up" ]; then
    git -C "$p" pull --ff-only >/dev/null || {
      echo "PULL_DEFERRED LOCAL $p branch=$b upstream=$up" | tee -a "$TMP_OUT/sync_actions.log"; return 0;
    }
  fi
  echo "SYNCED LOCAL $p head=$(git -C "$p" rev-parse HEAD) branch=${b:-DETACHED}" | tee -a "$TMP_OUT/sync_actions.log"
}

log 2 "verify magicPRObox control host"
CN="$(scutil --get ComputerName 2>/dev/null || true)"
LH="$(scutil --get LocalHostName 2>/dev/null || true)"
HN="$(hostname 2>/dev/null || true)"
case "$(printf '%s %s %s' "$CN" "$LH" "$HN" | tr '[:upper:]' '[:lower:]')" in
  *magicprobox*) ;;
  *) fail RUN_ON_MAGICPROBOX_ONLY 2 ;;
esac
printf 'CONTROL_COMPUTER_NAME=%s\nCONTROL_LOCAL_HOST_NAME=%s\nCONTROL_HOSTNAME=%s\n' "$CN" "$LH" "$HN" | tee "$TMP_OUT/control_identity.txt"

test -d "$ROOT/.git" || fail HYDRADG_NOT_GIT_REPO 3
command -v gh >/dev/null || fail MAGICPRO_GH_MISSING 4
command -v tailscale >/dev/null || fail MAGICPRO_TAILSCALE_MISSING 5

log 5 "synchronize HydraDG setup branch without discarding evidence"
cd "$ROOT"
git fetch origin "$BRANCH" --quiet
if [ -n "$(git status --porcelain)" ]; then
  echo "HydraDG control repo has pre-existing work; checkpointing it first."
  helper="$(mktemp /tmp/hydradg-checkpoint.XXXXXX.sh)"
  git show "origin/$BRANCH:scripts/checkpoint_dirty_worktree.sh" > "$helper"
  bash "$helper"
  rm -f "$helper"
fi
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
git pull --ff-only origin "$BRANCH"
test -z "$(git status --porcelain)" || fail HYDRADG_DIRTY_AFTER_SETUP_SYNC 6

log 10 "verify Tailscale + SSH to magicSTUDIObox"
tailscale status > "$TMP_OUT/tailscale_magicpro.txt"
ssh -o BatchMode=yes -o ConnectTimeout=12 "$STUDIO" \
  'command -v tailscale >/dev/null && tailscale status >/dev/null && printf "SSH_TAILSCALE=PASS\n"' \
  > "$TMP_OUT/studio_transport.txt" || fail STUDIO_SSH_TAILSCALE_FAILED 10
STUDIO_IDS="$(remote 'printf "%s %s %s" "$(scutil --get ComputerName 2>/dev/null || true)" "$(scutil --get LocalHostName 2>/dev/null || true)" "$(hostname 2>/dev/null || true)"' | tr '[:upper:]' '[:lower:]')"
case "$STUDIO_IDS" in *magicstudiobox*) ;; *) fail REMOTE_NOT_MAGICSTUDIO 11 ;; esac

log 14 "ensure Homebrew exists on magicSTUDIObox"
if ! remote 'test -x /opt/homebrew/bin/brew || command -v brew >/dev/null 2>&1'; then
  echo "Homebrew is missing on Studio. Launching the official installer through this PRObox terminal."
  echo "A Studio password/confirmation may be requested here."
  ssh -tt "$STUDIO" '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"' || fail HOMEBREW_INSTALL_FAILED 14
fi
remote 'test -x /opt/homebrew/bin/brew' || fail HOMEBREW_BINARY_MISSING 15

log 18 "install/verify Studio control toolchain"
remote 'bash -s' <<'REMOTE_TOOLS'
set -euo pipefail
BREW=/opt/homebrew/bin/brew
LINE='eval "$(/opt/homebrew/bin/brew shellenv)"'
touch "$HOME/.zprofile"
grep -Fqx "$LINE" "$HOME/.zprofile" || printf '%s\n' "$LINE" >> "$HOME/.zprofile"
eval "$($BREW shellenv)"
REQ=(gh gitleaks tmux uv git-lfs jq just)
MISS=()
for c in "${REQ[@]}"; do command -v "$c" >/dev/null 2>&1 || MISS+=("$c"); done
if [ "${#MISS[@]}" -gt 0 ]; then brew install "${MISS[@]}"; fi
for c in "${REQ[@]}"; do command -v "$c" >/dev/null 2>&1 || { echo "FAIL=STUDIO_TOOL_MISSING:$c"; exit 21; }; done
git lfs install --skip-repo >/dev/null
echo "STUDIO_TOOLCHAIN=PASS"
REMOTE_TOOLS

log 24 "configure GitHub auth and Git identity globally on both machines"
if ! gh auth status >/dev/null 2>&1; then
  gh auth login --hostname github.com --git-protocol https --web
fi
gh auth setup-git >/dev/null
git lfs install --skip-repo >/dev/null 2>&1 || true

if ! remote 'eval "$(/opt/homebrew/bin/brew shellenv)"; gh auth status >/dev/null 2>&1'; then
  echo "Studio GitHub auth is missing; starting its one-time browser auth through this PRObox terminal."
  ssh -tt "$STUDIO" 'eval "$(/opt/homebrew/bin/brew shellenv)"; gh auth login --hostname github.com --git-protocol https --web && gh auth setup-git' || fail STUDIO_GH_LOGIN_FAILED 24
fi
remote 'eval "$(/opt/homebrew/bin/brew shellenv)"; gh auth setup-git >/dev/null; gh auth status >/dev/null; echo STUDIO_GH_AUTH=PASS' > "$TMP_OUT/studio_github_auth.txt" || fail STUDIO_GH_AUTH_FAILED 25

NAME="$(git config --global user.name || true)"
EMAIL="$(git config --global user.email || true)"
[ -n "$NAME" ] || fail MAGICPRO_GIT_NAME_MISSING 26
[ -n "$EMAIL" ] || fail MAGICPRO_GIT_EMAIL_MISSING 27
ssh "$STUDIO" bash -s -- "$NAME" "$EMAIL" <<'REMOTE_IDENT'
set -euo pipefail
NAME="$1"; EMAIL="$2"
[ -n "$(git config --global user.name || true)" ] || git config --global user.name "$NAME"
[ -n "$(git config --global user.email || true)" ] || git config --global user.email "$EMAIL"
printf 'STUDIO_GIT_IDENTITY=%s <%s>\n' "$(git config --global user.name)" "$(git config --global user.email)"
REMOTE_IDENT

log 32 "bootstrap canonical LessWrong repository from Studio"
remote 'bash -s' <<'REMOTE_LW'
set -euo pipefail
eval "$(/opt/homebrew/bin/brew shellenv)"
LW="/Users/byron/projects/active/lesswrong"
REPO="biobitworks/lesswrong"
test -d "$LW" || { echo "FAIL=LESSWRONG_PATH_MISSING:$LW"; exit 30; }
if ! git -C "$LW" rev-parse --show-toplevel >/dev/null 2>&1; then git -C "$LW" init -b main; fi
test "$(git -C "$LW" rev-parse --show-toplevel)" = "$LW" || { echo FAIL=LESSWRONG_WRONG_ROOT; exit 31; }
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
cd "$LW"
BIG=0
while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue
  sz="$(stat -f %z "$f")"
  if [ "$sz" -gt 95000000 ]; then echo "OVER_95MB:$sz:$f"; BIG=1; fi
done < <(find "$LW" -path "$LW/.git" -prune -o -type f -print0)
[ "$BIG" -eq 0 ] || { echo FAIL=LESSWRONG_LARGE_FILE_GATE; exit 32; }
git add -A
gitleaks git --staged --redact=100 --no-banner .
if ! git rev-parse HEAD >/dev/null 2>&1; then
  git commit -m "Initialize LessWrong FCO/FCG workspace"
elif ! git diff --cached --quiet; then
  git commit -m "Checkpoint LessWrong workspace before universal GitHub bootstrap"
fi
if gh repo view "$REPO" >/dev/null 2>&1; then
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$REPO.git"
else
  gh repo create "$REPO" --private --source=. --remote=origin
fi
git fetch origin --prune || true
if git show-ref --verify --quiet refs/remotes/origin/main; then
  if ! git merge-base --is-ancestor origin/main HEAD && ! git merge-base --is-ancestor HEAD origin/main; then
    echo FAIL=LESSWRONG_UNRELATED_REMOTE_HISTORY; exit 33
  fi
fi
git branch -M main
git push -u origin main
for b in test stage; do
  git show-ref --verify --quiet "refs/heads/$b" || git branch "$b" main
  git push -u origin "$b"
done
echo "STUDIO_LESSWRONG=PASS:$(git rev-parse main)"
REMOTE_LW

log 40 "ensure LessWrong exists on magicPRObox"
LW_PRO="$ACTIVE/lesswrong"
if git -C "$LW_PRO" rev-parse --show-toplevel >/dev/null 2>&1; then
  test "$(git -C "$LW_PRO" rev-parse --show-toplevel)" = "$LW_PRO" || fail MAGICPRO_LESSWRONG_WRONG_ROOT 40
elif [ -e "$LW_PRO" ] && [ -n "$(find "$LW_PRO" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
  fail MAGICPRO_LESSWRONG_NON_GIT_CONFLICT 41
else
  rm -rf "$LW_PRO"
  gh repo clone biobitworks/lesswrong "$LW_PRO"
fi
sync_clean_repo_local "$LW_PRO"

log 48 "inventory active projects on both machines"
inventory_local "$TMP_OUT/magicpro_active.tsv"
inventory_remote > "$TMP_OUT/magicstudio_active.tsv"
awk -F '\t' '$1=="GIT" && $4 ~ /github\.com/ && $3!="" {print $3}' \
  "$TMP_OUT/magicpro_active.tsv" "$TMP_OUT/magicstudio_active.tsv" | sort -u > "$TMP_OUT/github_active_union.txt"
printf 'ACTIVE_GITHUB_REPOS=%s\n' "$(wc -l < "$TMP_OUT/github_active_union.txt" | tr -d ' ')"

log 56 "make every active GitHub repo available on both machines"
: > "$TMP_OUT/sync_actions.log"
while IFS= read -r repo; do
  [ -n "$repo" ] || continue
  name="${repo##*/}"
  lpath="$(awk -F '\t' -v r="$repo" '$1=="GIT" && $3==r {print $2; exit}' "$TMP_OUT/magicpro_active.tsv")"
  spath="$(awk -F '\t' -v r="$repo" '$1=="GIT" && $3==r {print $2; exit}' "$TMP_OUT/magicstudio_active.tsv")"
  [ -n "$lpath" ] || lpath="$ACTIVE/$name"
  [ -n "$spath" ] || spath="$ACTIVE/$name"

  if ! git -C "$lpath" rev-parse --show-toplevel >/dev/null 2>&1; then
    if [ -e "$lpath" ] && [ -n "$(find "$lpath" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
      echo "CONFLICT_NONGIT LOCAL repo=$repo path=$lpath" | tee -a "$TMP_OUT/sync_actions.log"
    else
      rm -rf "$lpath"
      gh repo clone "$repo" "$lpath" && echo "CLONED LOCAL $repo -> $lpath" | tee -a "$TMP_OUT/sync_actions.log"
    fi
  fi

  ssh "$STUDIO" bash -s -- "$repo" "$spath" <<'REMOTE_CLONE' | tee -a "$TMP_OUT/sync_actions.log"
set -euo pipefail
repo="$1"; p="$2"
eval "$(/opt/homebrew/bin/brew shellenv)"
if ! git -C "$p" rev-parse --show-toplevel >/dev/null 2>&1; then
  if [ -e "$p" ] && [ -n "$(find "$p" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
    echo "CONFLICT_NONGIT STUDIO repo=$repo path=$p"
  else
    rm -rf "$p"; gh repo clone "$repo" "$p"; echo "CLONED STUDIO $repo -> $p"
  fi
fi
REMOTE_CLONE
done < "$TMP_OUT/github_active_union.txt"

log 68 "fast-forward clean GitHub-backed active repos"
inventory_local "$TMP_OUT/magicpro_active_after_clone.tsv"
inventory_remote > "$TMP_OUT/magicstudio_active_after_clone.tsv"
while IFS=$'\t' read -r kind name path repo origin branch dirty; do
  [ "$kind" = GIT ] || continue
  case "$origin" in *github.com*) sync_clean_repo_local "$path" ;; esac
done < "$TMP_OUT/magicpro_active_after_clone.tsv"

remote 'bash -s' <<'REMOTE_SYNC_ALL' | tee -a "$TMP_OUT/sync_actions.log"
set -euo pipefail
ACTIVE="/Users/byron/projects/active"
for p in "$ACTIVE"/*; do
  [ -d "$p" ] || continue
  top="$(git -C "$p" rev-parse --show-toplevel 2>/dev/null || true)"
  [ "$top" = "$p" ] || continue
  origin="$(git -C "$p" remote get-url origin 2>/dev/null || true)"
  case "$origin" in *github.com*) ;; *) continue ;; esac
  if [ -n "$(git -C "$p" status --porcelain)" ]; then echo "DEFERRED_DIRTY STUDIO $p"; continue; fi
  git -C "$p" fetch origin --prune --quiet || { echo "FETCH_FAIL STUDIO $p"; continue; }
  b="$(git -C "$p" branch --show-current || true)"
  up="$(git -C "$p" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
  if [ -n "$b" ] && [ -n "$up" ]; then
    git -C "$p" pull --ff-only >/dev/null || { echo "PULL_DEFERRED STUDIO $p branch=$b upstream=$up"; continue; }
  fi
  echo "SYNCED STUDIO $p head=$(git -C "$p" rev-parse HEAD) branch=${b:-DETACHED}"
done
REMOTE_SYNC_ALL

log 78 "write bounded portfolio receipt"
PRO_INV_SHA="$(shasum -a 256 "$TMP_OUT/magicpro_active_after_clone.tsv" | awk '{print $1}')"
STUDIO_INV_SHA="$(shasum -a 256 "$TMP_OUT/magicstudio_active_after_clone.tsv" | awk '{print $1}')"
UNION_SHA="$(shasum -a 256 "$TMP_OUT/github_active_union.txt" | awk '{print $1}')"
ACTIONS_SHA="$(shasum -a 256 "$TMP_OUT/sync_actions.log" | awk '{print $1}')"
DEFERRED="$(grep -Ec 'DEFERRED_DIRTY|CONFLICT_NONGIT|FETCH_FAIL|PULL_DEFERRED' "$TMP_OUT/sync_actions.log" || true)"
jq -n \
  --arg run "$RUN_ID" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg pro "$PRO_INV_SHA" --arg studio "$STUDIO_INV_SHA" \
  --arg union "$UNION_SHA" --arg actions "$ACTIONS_SHA" \
  --argjson deferred "$DEFERRED" \
  '{schema:"fcofcg.two_machine_portfolio_github.v2",run_id:$run,timestamp_utc:$ts,scope:"UNION_OF_TOP_LEVEL_ACTIVE_PROJECTS_ON_BOTH_MACHINES",control_host:"magicPRObox",execution_host:"magicSTUDIObox",github_auth:{magicpro:"PASS",magicstudio:"PASS"},evidence_sha256:{magicpro_inventory:$pro,magicstudio_inventory:$studio,github_active_union:$union,sync_actions:$actions},deferred_or_conflict_count:$deferred,claim_ceiling:"GITHUB_AUTH_AND_ACTIVE_REPOSITORY_AVAILABILITY/SYNC_AUDIT_ONLY; DIRTY_OR_CONFLICTING_REPOSITORIES_ARE_NOT_CLAIMED_SYNCHRONIZED",signature_state:"NOT_SIGNED_BY_THIS_SCRIPT",public_export_state:"UNCHANGED"}' \
  > "$TMP_OUT/PORTFOLIO_GITHUB_RECEIPT.json"
printf 'DEFERRED_OR_CONFLICT_COUNT=%s\n' "$DEFERRED" | tee "$TMP_OUT/final_status.txt"

log 84 "materialize and commit run evidence only after synchronization"
cd "$ROOT"
test -z "$(git status --porcelain)" || fail HYDRADG_DIRTY_BEFORE_EVIDENCE_MATERIALIZATION 79
mkdir -p "$FINAL_OUT"
cp -a "$TMP_OUT/." "$FINAL_OUT/"
git add "$FINAL_REL"
gitleaks git --staged --redact=100 --no-banner .
git commit -m "Record universal two-machine GitHub setup $RUN_ID"
git push origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
LOCAL="$(git rev-parse HEAD)"
REMOTE_HEAD="$(git rev-parse "origin/$BRANCH")"
[ "$LOCAL" = "$REMOTE_HEAD" ] || fail POST_PUSH_DIVERGENCE 80

if [ "$RUN_STACK_TESTS" = "1" ]; then
  log 90 "run critical remote stack checks"
  STUDIO_SSH="$STUDIO" HYDRADG_BRANCH="$BRANCH" bash scripts/run_remote_stack_final_check.sh
  cd "$ROOT"
  git fetch origin "$BRANCH" --quiet
  git pull --ff-only origin "$BRANCH" >/dev/null
fi

log 100 "complete"
echo "UNIVERSAL_GITHUB_READY=YES"
echo "CONTROL_HOST=magicPRObox"
echo "EXECUTION_HOST=magicSTUDIObox"
echo "ACTIVE_SCOPE_FILE=$FINAL_OUT/github_active_union.txt"
echo "DEFERRED_OR_CONFLICT_COUNT=$DEFERRED"
echo "CHECKPOINT_COMMIT=$(git -C "$ROOT" rev-parse HEAD)"
echo "NOTE=All active GitHub-backed projects were audited for availability on both machines; dirty/conflicting projects remain explicitly deferred, never overwritten."
