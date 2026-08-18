#!/usr/bin/env bash
set -euo pipefail

# Reconcile LessWrong so magicPRObox is canonical, GitHub main is the exchange
# point, and magicSTUDIObox is reset to the canonical GitHub main.
#
# RUN ONLY ON magicPRObox.
#
# This script deliberately performs one non-fast-forward replacement of GitHub
# main when the existing remote main belongs to the accidental Studio bootstrap
# history. It uses --force-with-lease against the exact observed remote SHA and
# first preserves that remote SHA on a timestamped backup branch.
#
# Safety invariants:
# - never deletes either working directory
# - preserves the old GitHub main on a backup branch before replacement
# - preserves Studio's pre-reconciliation HEAD on a local backup branch
# - stashes dirty worktrees instead of discarding them
# - requires Gitleaks on the canonical PRObox repository
# - refuses an unexpected origin URL
# - refuses a remote-main race via --force-with-lease
# - verifies PRObox == GitHub main == Studio at the end

PRO_LW="/Users/byron/projects/active/lesswrong"
STUDIO="${STUDIO_SSH:-magicstudiobox}"
STUDIO_LW="/Users/byron/projects/active/lesswrong"
REMOTE_URL="https://github.com/biobitworks/lesswrong.git"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
REMOTE_BACKUP="pre-magicpro-canonical-${RUN_ID}"
STUDIO_BACKUP="backup/studio-pre-magicpro-canonical-${RUN_ID}"
RECEIPT="/tmp/lesswrong-reconcile-${RUN_ID}.json"

fail(){ echo "FAIL=$1" >&2; exit "${2:-1}"; }
section(){ printf '\n=== %s ===\n' "$1"; }

section "VERIFY CONTROL HOST"
CN="$(scutil --get ComputerName 2>/dev/null || true)"
LH="$(scutil --get LocalHostName 2>/dev/null || true)"
HN="$(hostname 2>/dev/null || true)"
printf 'COMPUTER_NAME=%s\nLOCAL_HOST_NAME=%s\nHOSTNAME=%s\n' "$CN" "$LH" "$HN"
case "$(printf '%s %s %s' "$CN" "$LH" "$HN" | tr '[:upper:]' '[:lower:]')" in
  *magicprobox*) ;;
  *) fail RUN_ON_MAGICPROBOX_ONLY 2 ;;
esac

command -v git >/dev/null 2>&1 || fail MAGICPRO_GIT_MISSING 3
command -v gh >/dev/null 2>&1 || fail MAGICPRO_GH_MISSING 4
command -v gitleaks >/dev/null 2>&1 || fail MAGICPRO_GITLEAKS_MISSING 5
command -v ssh >/dev/null 2>&1 || fail MAGICPRO_SSH_MISSING 6
gh auth status >/dev/null 2>&1 || fail MAGICPRO_GH_AUTH_MISSING 7

[ -d "$PRO_LW" ] || fail MAGICPRO_LESSWRONG_PATH_MISSING 8
PRO_ROOT="$(git -C "$PRO_LW" rev-parse --show-toplevel 2>/dev/null || true)"
[ "$PRO_ROOT" = "$PRO_LW" ] || fail MAGICPRO_LESSWRONG_WRONG_GIT_ROOT 9

section "PRESERVE MAGICPRO DIRTY STATE"
PRO_STATUS_BEFORE="$(git -C "$PRO_LW" status --porcelain)"
PRO_STASHED=NO
if [ -n "$PRO_STATUS_BEFORE" ]; then
  printf '%s\n' "$PRO_STATUS_BEFORE"
  git -C "$PRO_LW" stash push -u -m "LessWrong pre-canonical-reconcile ${RUN_ID}" >/dev/null
  PRO_STASHED=YES
fi
[ -z "$(git -C "$PRO_LW" status --porcelain)" ] || fail MAGICPRO_STILL_DIRTY_AFTER_STASH 10

PRO_HEAD="$(git -C "$PRO_LW" rev-parse HEAD)"
PRO_BRANCH="$(git -C "$PRO_LW" branch --show-current)"
[ -n "$PRO_BRANCH" ] || fail MAGICPRO_DETACHED_HEAD 11
printf 'MAGICPRO_HEAD=%s\nMAGICPRO_BRANCH=%s\nMAGICPRO_STASHED=%s\n' "$PRO_HEAD" "$PRO_BRANCH" "$PRO_STASHED"

section "ATTACH / VERIFY ORIGIN"
if git -C "$PRO_LW" remote get-url origin >/dev/null 2>&1; then
  ORIGIN="$(git -C "$PRO_LW" remote get-url origin)"
  [ "$ORIGIN" = "$REMOTE_URL" ] || fail "UNEXPECTED_MAGICPRO_ORIGIN:$ORIGIN" 12
else
  git -C "$PRO_LW" remote add origin "$REMOTE_URL"
fi
git -C "$PRO_LW" fetch origin --prune
REMOTE_MAIN="$(git -C "$PRO_LW" rev-parse origin/main 2>/dev/null || true)"
[ -n "$REMOTE_MAIN" ] || fail GITHUB_MAIN_MISSING 13
printf 'REMOTE_MAIN_BEFORE=%s\n' "$REMOTE_MAIN"

section "PRESERVE CURRENT GITHUB MAIN"
if git -C "$PRO_LW" show-ref --verify --quiet "refs/heads/$REMOTE_BACKUP"; then
  fail "LOCAL_BACKUP_BRANCH_ALREADY_EXISTS:$REMOTE_BACKUP" 14
fi
git -C "$PRO_LW" branch "$REMOTE_BACKUP" "$REMOTE_MAIN"
git -C "$PRO_LW" push origin "$REMOTE_BACKUP:$REMOTE_BACKUP"
printf 'REMOTE_BACKUP_BRANCH=%s\nREMOTE_BACKUP_SHA=%s\n' "$REMOTE_BACKUP" "$REMOTE_MAIN"

section "CANONICAL MAGICPRO ADMISSION GATES"
# Scan the canonical repository history/current reachable objects for secrets.
(
  cd "$PRO_LW"
  gitleaks git --redact=100 --no-banner .
)

# Current-tree GitHub large-object guard. Historical oversized objects will also
# be rejected by GitHub during push; this gate catches the common current-tree case.
BIG=0
while IFS= read -r -d '' rel; do
  [ -f "$PRO_LW/$rel" ] || continue
  sz="$(stat -f %z "$PRO_LW/$rel")"
  if [ "$sz" -gt 95000000 ]; then
    printf 'OVER_95MB=%s:%s\n' "$sz" "$rel"
    BIG=1
  fi
done < <(git -C "$PRO_LW" ls-files -z)
[ "$BIG" -eq 0 ] || fail MAGICPRO_CURRENT_TREE_LARGE_FILE_GATE 15

section "PUBLISH MAGICPRO AS GITHUB MAIN"
# This is the only history-replacing operation. The lease makes it fail if
# GitHub main changed after REMOTE_MAIN was observed.
git -C "$PRO_LW" push \
  --force-with-lease="refs/heads/main:${REMOTE_MAIN}" \
  origin "${PRO_HEAD}:refs/heads/main"

git -C "$PRO_LW" fetch origin --prune
REMOTE_MAIN_AFTER="$(git -C "$PRO_LW" rev-parse origin/main)"
[ "$REMOTE_MAIN_AFTER" = "$PRO_HEAD" ] || fail GITHUB_MAIN_NOT_MAGICPRO_HEAD 16

# Normalize local branch name/upstream to main without rewriting the commit.
if [ "$PRO_BRANCH" != "main" ]; then
  git -C "$PRO_LW" branch -M main
fi
git -C "$PRO_LW" branch --set-upstream-to=origin/main main >/dev/null

# Create test/stage only if absent; do not rewrite existing branch histories.
for b in test stage; do
  if git -C "$PRO_LW" ls-remote --exit-code --heads origin "$b" >/dev/null 2>&1; then
    echo "BRANCH_EXISTS_UNCHANGED=$b"
  else
    git -C "$PRO_LW" push origin "${PRO_HEAD}:refs/heads/$b"
    echo "BRANCH_CREATED=$b:$PRO_HEAD"
  fi
done

section "RECONCILE MAGICSTUDIO TO GITHUB MAIN"
ssh -o ConnectTimeout=15 "$STUDIO" bash -s -- \
  "$STUDIO_LW" "$REMOTE_URL" "$STUDIO_BACKUP" "$PRO_HEAD" <<'REMOTE'
set -euo pipefail
LW="$1"
REMOTE_URL="$2"
BACKUP="$3"
EXPECTED="$4"

[ -d "$LW" ] || { echo FAIL=STUDIO_LESSWRONG_PATH_MISSING; exit 30; }
ROOT="$(git -C "$LW" rev-parse --show-toplevel 2>/dev/null || true)"
[ "$ROOT" = "$LW" ] || { echo FAIL=STUDIO_LESSWRONG_WRONG_GIT_ROOT; exit 31; }

if git -C "$LW" remote get-url origin >/dev/null 2>&1; then
  ORIGIN="$(git -C "$LW" remote get-url origin)"
  [ "$ORIGIN" = "$REMOTE_URL" ] || { echo "FAIL=UNEXPECTED_STUDIO_ORIGIN:$ORIGIN"; exit 32; }
else
  git -C "$LW" remote add origin "$REMOTE_URL"
fi

STUDIO_STATUS="$(git -C "$LW" status --porcelain)"
STASHED=NO
if [ -n "$STUDIO_STATUS" ]; then
  printf '%s\n' "$STUDIO_STATUS"
  git -C "$LW" stash push -u -m "LessWrong Studio pre-canonical-reconcile $(date -u +%Y%m%dT%H%M%SZ)" >/dev/null
  STASHED=YES
fi
[ -z "$(git -C "$LW" status --porcelain)" ] || { echo FAIL=STUDIO_STILL_DIRTY_AFTER_STASH; exit 33; }

OLD_HEAD="$(git -C "$LW" rev-parse HEAD)"
if git -C "$LW" show-ref --verify --quiet "refs/heads/$BACKUP"; then
  echo "FAIL=STUDIO_BACKUP_BRANCH_ALREADY_EXISTS:$BACKUP"; exit 34
fi
git -C "$LW" branch "$BACKUP" "$OLD_HEAD"

git -C "$LW" fetch origin --prune
REMOTE_HEAD="$(git -C "$LW" rev-parse origin/main)"
[ "$REMOTE_HEAD" = "$EXPECTED" ] || { echo "FAIL=STUDIO_FETCHED_UNEXPECTED_MAIN:$REMOTE_HEAD"; exit 35; }

git -C "$LW" switch -C main origin/main >/dev/null
git -C "$LW" branch --set-upstream-to=origin/main main >/dev/null
NEW_HEAD="$(git -C "$LW" rev-parse HEAD)"
[ "$NEW_HEAD" = "$EXPECTED" ] || { echo "FAIL=STUDIO_HEAD_MISMATCH:$NEW_HEAD"; exit 36; }
[ -z "$(git -C "$LW" status --porcelain)" ] || { echo FAIL=STUDIO_DIRTY_AFTER_RECONCILE; exit 37; }

printf 'STUDIO_OLD_HEAD=%s\nSTUDIO_BACKUP=%s\nSTUDIO_STASHED=%s\nSTUDIO_NEW_HEAD=%s\n' "$OLD_HEAD" "$BACKUP" "$STASHED" "$NEW_HEAD"
REMOTE

section "FINAL THREE-WAY VERIFICATION"
PRO_FINAL="$(git -C "$PRO_LW" rev-parse HEAD)"
GITHUB_FINAL="$(git -C "$PRO_LW" ls-remote "$REMOTE_URL" refs/heads/main | awk '{print $1}')"
STUDIO_FINAL="$(ssh -o ConnectTimeout=15 "$STUDIO" "git -C '$STUDIO_LW' rev-parse HEAD")"

printf 'MAGICPRO_FINAL=%s\nGITHUB_FINAL=%s\nMAGICSTUDIO_FINAL=%s\n' "$PRO_FINAL" "$GITHUB_FINAL" "$STUDIO_FINAL"
[ "$PRO_FINAL" = "$GITHUB_FINAL" ] || fail FINAL_MAGICPRO_GITHUB_MISMATCH 40
[ "$PRO_FINAL" = "$STUDIO_FINAL" ] || fail FINAL_MAGICPRO_STUDIO_MISMATCH 41

cat > "$RECEIPT" <<EOF
{
  "schema": "fcofcg.lesswrong_two_machine_reconcile.v1",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "canonical_source": "magicPRObox",
  "repository": "biobitworks/lesswrong",
  "canonical_sha": "$PRO_FINAL",
  "github_main_before": "$REMOTE_MAIN",
  "github_backup_branch": "$REMOTE_BACKUP",
  "magicstudio_backup_branch": "$STUDIO_BACKUP",
  "magicpro_dirty_state_stashed": "$PRO_STASHED",
  "final_state": "MAGICPRO_EQUALS_GITHUB_MAIN_EQUALS_MAGICSTUDIO",
  "claim_ceiling": "GIT_CONTENT_AND_HEAD_CONFORMANCE_ONLY",
  "signature_state": "NOT_SIGNED",
  "merkle_state": "NOT_MERKLE_COMMITTED"
}
EOF
RECEIPT_SHA="$(shasum -a 256 "$RECEIPT" | awk '{print $1}')"
printf 'RECEIPT=%s\nRECEIPT_SHA256=%s\n' "$RECEIPT" "$RECEIPT_SHA"

echo
echo "LESSWRONG_TWO_MACHINE_READY=YES"
echo "CANONICAL_SHA=$PRO_FINAL"
echo "REMOTE_BACKUP_BRANCH=$REMOTE_BACKUP"
echo "STUDIO_BACKUP_BRANCH=$STUDIO_BACKUP"
echo "NOTE=Any pre-reconciliation dirty files were preserved in Git stash entries and were not reapplied automatically."
