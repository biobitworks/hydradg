#!/usr/bin/env bash
set -euo pipefail

# Repair/synchronize HydraDB across magicPRObox and magicSTUDIObox.
# RUN ONLY ON magicPRObox.
#
# Intended topology:
#   hydra-db/hydradb                  = authoritative public upstream
#   biobitworks/hydradb-hackhydra     = private Hack Hydra mirror / origin
#   /Users/byron/projects/active/hydradb on both Macs = working checkout
#
# biobitworks/hydradb is intentionally NOT used. It is an unrelated placeholder
# repository created during the universal GitHub bootstrap/app setup.
#
# Modes:
#   audit  - no filesystem or GitHub mutations
#   apply  - fast-forward the private mirror main from upstream when safe,
#            preserve existing local checkouts, then make both machines conform.
#
# Safety:
# - no force push
# - no deletion of project data
# - no history rewrite on GitHub
# - existing wrong/non-Git local folders are moved to timestamped backups
# - existing Git repositories are bundled before their main checkout is replaced
# - upstream->mirror synchronization must be a fast-forward
# - final verification requires both machines == private mirror main == upstream main

MODE="${1:-audit}"
case "$MODE" in audit|apply) ;; *) echo "USAGE: $0 [audit|apply]"; exit 2;; esac

STUDIO="${STUDIO_SSH:-magicstudiobox}"
ACTIVE="/Users/byron/projects/active"
LOCAL_PATH="$ACTIVE/hydradb"
STUDIO_PATH="$ACTIVE/hydradb"
MIRROR_REPO="biobitworks/hydradb-hackhydra"
MIRROR_URL="https://github.com/${MIRROR_REPO}.git"
UPSTREAM_URL="https://github.com/hydra-db/hydradb.git"
ACCIDENTAL_REPO="biobitworks/hydradb"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_ROOT="$ACTIVE/.hydradb-reconcile-$RUN_ID"

fail(){ echo "FAIL=$1" >&2; exit "${2:-1}"; }
section(){ printf '\n=== %s ===\n' "$1"; }
remote(){ ssh -o ConnectTimeout=15 "$STUDIO" "$@"; }

host_ok(){
  local s
  s="$(printf '%s %s %s' "$(scutil --get ComputerName 2>/dev/null || true)" "$(scutil --get LocalHostName 2>/dev/null || true)" "$(hostname 2>/dev/null || true)" | tr '[:upper:]' '[:lower:]')"
  case "$s" in *magicprobox*) return 0;; *) return 1;; esac
}

repo_audit_local(){
  local label="$1" p="$2"
  echo "--- $label ---"
  if [ ! -e "$p" ]; then echo "PATH=MISSING:$p"; return 0; fi
  echo "PATH=$p"
  if top="$(git -C "$p" rev-parse --show-toplevel 2>/dev/null)" && [ "$top" = "$p" ]; then
    echo "GIT=YES"
    echo "HEAD=$(git -C "$p" rev-parse HEAD 2>/dev/null || true)"
    echo "BRANCH=$(git -C "$p" branch --show-current 2>/dev/null || true)"
    echo "ORIGIN=$(git -C "$p" remote get-url origin 2>/dev/null || true)"
    echo "UPSTREAM_REMOTE=$(git -C "$p" remote get-url upstream 2>/dev/null || true)"
    echo "DIRTY_COUNT=$(git -C "$p" status --porcelain | wc -l | tr -d ' ')"
  else
    echo "GIT=NO"
    echo "ENTRY_COUNT=$(find "$p" -mindepth 1 -maxdepth 1 -print 2>/dev/null | wc -l | tr -d ' ')"
  fi
}

repo_audit_remote(){
  remote 'bash -s' <<'EOS'
set -euo pipefail
p="/Users/byron/projects/active/hydradb"
echo "--- MAGICSTUDIO ---"
if [ ! -e "$p" ]; then echo "PATH=MISSING:$p"; exit 0; fi
echo "PATH=$p"
if top="$(git -C "$p" rev-parse --show-toplevel 2>/dev/null)" && [ "$top" = "$p" ]; then
  echo "GIT=YES"
  echo "HEAD=$(git -C "$p" rev-parse HEAD 2>/dev/null || true)"
  echo "BRANCH=$(git -C "$p" branch --show-current 2>/dev/null || true)"
  echo "ORIGIN=$(git -C "$p" remote get-url origin 2>/dev/null || true)"
  echo "UPSTREAM_REMOTE=$(git -C "$p" remote get-url upstream 2>/dev/null || true)"
  echo "DIRTY_COUNT=$(git -C "$p" status --porcelain | wc -l | tr -d ' ')"
else
  echo "GIT=NO"
  echo "ENTRY_COUNT=$(find "$p" -mindepth 1 -maxdepth 1 -print 2>/dev/null | wc -l | tr -d ' ')"
fi
EOS
}

section "CONTROL HOST"
host_ok || fail RUN_ON_MAGICPROBOX_ONLY 3
command -v git >/dev/null || fail MAGICPRO_GIT_MISSING 4
command -v gh >/dev/null || fail MAGICPRO_GH_MISSING 5
gh auth status >/dev/null 2>&1 || fail MAGICPRO_GH_AUTH_MISSING 6
ssh -o BatchMode=yes -o ConnectTimeout=15 "$STUDIO" 'true' || fail STUDIO_SSH_FAILED 7

echo "MODE=$MODE"
echo "CONTROL_HOST=$(hostname)"
echo "STUDIO=$STUDIO"

section "REMOTE HEADS"
UPSTREAM_MAIN="$(git ls-remote "$UPSTREAM_URL" refs/heads/main | awk '{print $1}')"
MIRROR_MAIN="$(git ls-remote "$MIRROR_URL" refs/heads/main | awk '{print $1}')"
[ -n "$UPSTREAM_MAIN" ] || fail UPSTREAM_MAIN_MISSING 10
[ -n "$MIRROR_MAIN" ] || fail MIRROR_MAIN_MISSING 11
printf 'UPSTREAM_MAIN=%s\nMIRROR_MAIN=%s\n' "$UPSTREAM_MAIN" "$MIRROR_MAIN"

# Report the accidental repo but never use it as a source.
if gh repo view "$ACCIDENTAL_REPO" >/dev/null 2>&1; then
  ACC_MAIN="$(git ls-remote "https://github.com/${ACCIDENTAL_REPO}.git" refs/heads/main | awk '{print $1}')"
  echo "ACCIDENTAL_PLACEHOLDER_REPO=$ACCIDENTAL_REPO"
  echo "ACCIDENTAL_PLACEHOLDER_MAIN=${ACC_MAIN:-MISSING}"
fi

section "LOCAL CHECKOUT AUDIT"
repo_audit_local MAGICPRO "$LOCAL_PATH"
repo_audit_remote

if [ "$MODE" = audit ]; then
  if [ "$UPSTREAM_MAIN" = "$MIRROR_MAIN" ]; then
    echo "MIRROR_VS_UPSTREAM=CONTENT_EXACT_AT_MAIN"
  else
    echo "MIRROR_VS_UPSTREAM=DIVERGED_OR_BEHIND"
  fi
  echo "HYDRADB_TWO_MACHINE_AUDIT=COMPLETE"
  exit 0
fi

section "FAST-FORWARD PRIVATE MIRROR FROM UPSTREAM"
if [ "$MIRROR_MAIN" != "$UPSTREAM_MAIN" ]; then
  TMP="$(mktemp -d /tmp/hydradb-mirror-sync.XXXXXX)"
  trap 'rm -rf "${TMP:-}"' EXIT
  git clone --quiet "$MIRROR_URL" "$TMP/repo"
  git -C "$TMP/repo" remote add upstream "$UPSTREAM_URL"
  git -C "$TMP/repo" fetch --quiet upstream main
  git -C "$TMP/repo" fetch --quiet origin main

  # Only permit upstream to advance mirror main by fast-forward.
  if ! git -C "$TMP/repo" merge-base --is-ancestor origin/main upstream/main; then
    fail MIRROR_MAIN_HAS_NON_UPSTREAM_HISTORY_REVIEW_REQUIRED 20
  fi
  git -C "$TMP/repo" push origin "upstream/main:refs/heads/main"
  MIRROR_MAIN="$(git ls-remote "$MIRROR_URL" refs/heads/main | awk '{print $1}')"
  [ "$MIRROR_MAIN" = "$UPSTREAM_MAIN" ] || fail MIRROR_FAST_FORWARD_FAILED 21
fi

echo "MIRROR_SYNC=PASS:$MIRROR_MAIN"

# Keep hack work off main. Create private test/stage branches if absent.
for b in test stage; do
  if ! git ls-remote --exit-code --heads "$MIRROR_URL" "$b" >/dev/null 2>&1; then
    git push "$MIRROR_URL" "$MIRROR_MAIN:refs/heads/$b"
    echo "MIRROR_BRANCH_CREATED=$b:$MIRROR_MAIN"
  else
    echo "MIRROR_BRANCH_EXISTS=$b"
  fi
done

section "RECONCILE MAGICPRO CHECKOUT"
mkdir -p "$BACKUP_ROOT"
if top="$(git -C "$LOCAL_PATH" rev-parse --show-toplevel 2>/dev/null)" && [ "$top" = "$LOCAL_PATH" ]; then
  OLD_HEAD="$(git -C "$LOCAL_PATH" rev-parse HEAD)"
  OLD_ORIGIN="$(git -C "$LOCAL_PATH" remote get-url origin 2>/dev/null || true)"
  git -C "$LOCAL_PATH" bundle create "$BACKUP_ROOT/magicpro-before.bundle" --all
  echo "MAGICPRO_BUNDLE=$BACKUP_ROOT/magicpro-before.bundle"
  echo "MAGICPRO_OLD_HEAD=$OLD_HEAD"
  echo "MAGICPRO_OLD_ORIGIN=$OLD_ORIGIN"
  if [ -n "$(git -C "$LOCAL_PATH" status --porcelain)" ]; then
    git -C "$LOCAL_PATH" stash push -u -m "HydraDB pre-reconcile $RUN_ID" >/dev/null
    echo "MAGICPRO_STASHED=YES"
  fi
  if git -C "$LOCAL_PATH" remote get-url origin >/dev/null 2>&1; then
    git -C "$LOCAL_PATH" remote set-url origin "$MIRROR_URL"
  else
    git -C "$LOCAL_PATH" remote add origin "$MIRROR_URL"
  fi
  if git -C "$LOCAL_PATH" remote get-url upstream >/dev/null 2>&1; then
    git -C "$LOCAL_PATH" remote set-url upstream "$UPSTREAM_URL"
  else
    git -C "$LOCAL_PATH" remote add upstream "$UPSTREAM_URL"
  fi
  git -C "$LOCAL_PATH" fetch origin --prune
  git -C "$LOCAL_PATH" fetch upstream --prune
  git -C "$LOCAL_PATH" branch "backup/pre-hydradb-reconcile-$RUN_ID" "$OLD_HEAD" 2>/dev/null || true
  git -C "$LOCAL_PATH" switch -C main origin/main >/dev/null
else
  if [ -e "$LOCAL_PATH" ]; then
    mv "$LOCAL_PATH" "$BACKUP_ROOT/magicpro-nongit"
    echo "MAGICPRO_NONGIT_MOVED=$BACKUP_ROOT/magicpro-nongit"
  fi
  gh repo clone "$MIRROR_REPO" "$LOCAL_PATH"
  git -C "$LOCAL_PATH" remote add upstream "$UPSTREAM_URL"
fi

section "RECONCILE MAGICSTUDIO CHECKOUT"
ssh -o ConnectTimeout=15 "$STUDIO" bash -s -- "$MIRROR_URL" "$UPSTREAM_URL" "$RUN_ID" <<'EOS'
set -euo pipefail
MIRROR_URL="$1"; UPSTREAM_URL="$2"; RUN_ID="$3"
ACTIVE="/Users/byron/projects/active"
p="$ACTIVE/hydradb"
backup="$ACTIVE/.hydradb-reconcile-$RUN_ID"
mkdir -p "$backup"

if top="$(git -C "$p" rev-parse --show-toplevel 2>/dev/null)" && [ "$top" = "$p" ]; then
  old="$(git -C "$p" rev-parse HEAD)"
  old_origin="$(git -C "$p" remote get-url origin 2>/dev/null || true)"
  git -C "$p" bundle create "$backup/magicstudio-before.bundle" --all
  echo "MAGICSTUDIO_BUNDLE=$backup/magicstudio-before.bundle"
  echo "MAGICSTUDIO_OLD_HEAD=$old"
  echo "MAGICSTUDIO_OLD_ORIGIN=$old_origin"
  if [ -n "$(git -C "$p" status --porcelain)" ]; then
    git -C "$p" stash push -u -m "HydraDB pre-reconcile $RUN_ID" >/dev/null
    echo "MAGICSTUDIO_STASHED=YES"
  fi
  if git -C "$p" remote get-url origin >/dev/null 2>&1; then git -C "$p" remote set-url origin "$MIRROR_URL"; else git -C "$p" remote add origin "$MIRROR_URL"; fi
  if git -C "$p" remote get-url upstream >/dev/null 2>&1; then git -C "$p" remote set-url upstream "$UPSTREAM_URL"; else git -C "$p" remote add upstream "$UPSTREAM_URL"; fi
  git -C "$p" fetch origin --prune
  git -C "$p" fetch upstream --prune
  git -C "$p" branch "backup/pre-hydradb-reconcile-$RUN_ID" "$old" 2>/dev/null || true
  git -C "$p" switch -C main origin/main >/dev/null
else
  if [ -e "$p" ]; then mv "$p" "$backup/magicstudio-nongit"; echo "MAGICSTUDIO_NONGIT_MOVED=$backup/magicstudio-nongit"; fi
  git clone "$MIRROR_URL" "$p"
  git -C "$p" remote add upstream "$UPSTREAM_URL"
fi
EOS

section "FINAL CONFORMANCE"
PRO_HEAD="$(git -C "$LOCAL_PATH" rev-parse HEAD)"
PRO_ORIGIN="$(git -C "$LOCAL_PATH" remote get-url origin)"
PRO_UPSTREAM="$(git -C "$LOCAL_PATH" remote get-url upstream)"
STUDIO_HEAD="$(remote "git -C '$STUDIO_PATH' rev-parse HEAD")"
STUDIO_ORIGIN="$(remote "git -C '$STUDIO_PATH' remote get-url origin")"
STUDIO_UPSTREAM="$(remote "git -C '$STUDIO_PATH' remote get-url upstream")"
MIRROR_FINAL="$(git ls-remote "$MIRROR_URL" refs/heads/main | awk '{print $1}')"
UPSTREAM_FINAL="$(git ls-remote "$UPSTREAM_URL" refs/heads/main | awk '{print $1}')"

printf 'MAGICPRO_HEAD=%s\nMAGICSTUDIO_HEAD=%s\nMIRROR_MAIN=%s\nUPSTREAM_MAIN=%s\n' "$PRO_HEAD" "$STUDIO_HEAD" "$MIRROR_FINAL" "$UPSTREAM_FINAL"
printf 'MAGICPRO_ORIGIN=%s\nMAGICPRO_UPSTREAM=%s\nMAGICSTUDIO_ORIGIN=%s\nMAGICSTUDIO_UPSTREAM=%s\n' "$PRO_ORIGIN" "$PRO_UPSTREAM" "$STUDIO_ORIGIN" "$STUDIO_UPSTREAM"

[ "$PRO_HEAD" = "$MIRROR_FINAL" ] || fail MAGICPRO_HEAD_MISMATCH 40
[ "$STUDIO_HEAD" = "$MIRROR_FINAL" ] || fail MAGICSTUDIO_HEAD_MISMATCH 41
[ "$MIRROR_FINAL" = "$UPSTREAM_FINAL" ] || fail MIRROR_UPSTREAM_MISMATCH 42
[ "$PRO_ORIGIN" = "$MIRROR_URL" ] || fail MAGICPRO_ORIGIN_WRONG 43
[ "$STUDIO_ORIGIN" = "$MIRROR_URL" ] || fail MAGICSTUDIO_ORIGIN_WRONG 44
[ "$PRO_UPSTREAM" = "$UPSTREAM_URL" ] || fail MAGICPRO_UPSTREAM_WRONG 45
[ "$STUDIO_UPSTREAM" = "$UPSTREAM_URL" ] || fail MAGICSTUDIO_UPSTREAM_WRONG 46

# Optional HydraDG vendor/submodule visibility. This does not alter the pinned source.
for host in pro studio; do
  if [ "$host" = pro ]; then
    V="/Users/byron/projects/active/hydradg/vendor/hydradb"
    if git -C "$V" rev-parse HEAD >/dev/null 2>&1; then echo "HYDRADG_VENDOR_PRO=$(git -C "$V" rev-parse HEAD)"; fi
  else
    remote 'V=/Users/byron/projects/active/hydradg/vendor/hydradb; if git -C "$V" rev-parse HEAD >/dev/null 2>&1; then echo "HYDRADG_VENDOR_STUDIO=$(git -C "$V" rev-parse HEAD)"; fi'
  fi
done

echo "HYDRADB_TWO_MACHINE_READY=YES"
echo "CANONICAL_MAIN=$MIRROR_FINAL"
echo "ORIGIN_REPO=$MIRROR_REPO"
echo "UPSTREAM_REPO=hydra-db/hydradb"
echo "IGNORED_PLACEHOLDER_REPO=$ACCIDENTAL_REPO"
echo "CLAIM_CEILING=GIT_HEAD_AND_REMOTE_CONFORMANCE_ONLY"
echo "SIGNATURE_STATE=NOT_PROJECT_SIGNED"
echo "MMR_STATE=NOT_COMMITTED_BY_THIS_SCRIPT"
