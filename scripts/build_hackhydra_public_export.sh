#!/usr/bin/env bash
set -euo pipefail

# Build a fresh-history Hack Hydra public export from the private working repo.
# This script intentionally uses an explicit allowlist. It does not publish,
# change repository visibility, or infer content-origin eligibility from commit
# timestamps alone.

SOURCE_ROOT="${HYDRADG_SOURCE_ROOT:-/Users/byron/projects/active/hydradg}"
SOURCE_BRANCH="hack-hydra/submission-eligible-20260819"
EXPORT_ROOT="${HYDRAG_PUBLIC_EXPORT_ROOT:-/Users/byron/projects/active/hydradg-public-export}"

progress() { printf '[%-24s] %3s%% stage=%s\n' "$(printf '%*s' $(( $1 * 24 / 100 )) '' | tr ' ' '#')" "$1" "$2"; }

progress 5 VERIFY_SOURCE
cd "$SOURCE_ROOT"

test "$(git rev-parse --show-toplevel)" = "$SOURCE_ROOT" || { echo "STOP: wrong source Git root"; exit 10; }
CURRENT_BRANCH="$(git branch --show-current)"
test "$CURRENT_BRANCH" = "$SOURCE_BRANCH" || { echo "STOP: expected branch $SOURCE_BRANCH, got $CURRENT_BRANCH"; exit 11; }

git diff --quiet || { echo "STOP: unstaged changes exist"; exit 12; }
git diff --cached --quiet || { echo "STOP: staged changes exist"; exit 13; }
test -z "$(git ls-files --others --exclude-standard)" || { echo "STOP: untracked files exist in source worktree"; git status --short; exit 14; }

SOURCE_SHA="$(git rev-parse HEAD)"
echo "SOURCE_COMMIT=$SOURCE_SHA"

progress 12 PREPARE_EXPORT
rm -rf "$EXPORT_ROOT"
mkdir -p "$EXPORT_ROOT"

copy_file() {
  local rel="$1"
  test -f "$SOURCE_ROOT/$rel" || { echo "STOP: missing allowlisted file $rel"; exit 20; }
  mkdir -p "$EXPORT_ROOT/$(dirname "$rel")"
  cp -p "$SOURCE_ROOT/$rel" "$EXPORT_ROOT/$rel"
}

copy_tree() {
  local rel="$1"
  test -d "$SOURCE_ROOT/$rel" || { echo "STOP: missing allowlisted directory $rel"; exit 21; }
  mkdir -p "$EXPORT_ROOT/$rel"
  rsync -a --delete \
    --exclude '.git/' \
    --exclude '.next/' \
    --exclude 'node_modules/' \
    --exclude '.env' \
    --exclude '.env.local' \
    --exclude '*.pem' \
    --exclude '*.key' \
    --exclude '*.p12' \
    --exclude '*.pfx' \
    --exclude '*.secret' \
    "$SOURCE_ROOT/$rel/" "$EXPORT_ROOT/$rel/"
}

progress 25 COPY_PROJECT
for f in \
  README.md \
  LICENSE \
  THIRD_PARTY_NOTICES.md \
  docs/HACK_HYDRA_ELIGIBILITY_AUDIT_20260819.md \
  docs/PUBLIC_EXPORT_MANIFEST_20260819.md \
  handoff/SUBMISSION_TASKS_20260819.md \
  handoff/RELEASE_EXECUTION_LEDGER_20260819.md
  do copy_file "$f"; done

copy_tree apps/hydradg-web

progress 36 COPY_RELEASE_TOOLS
for f in \
  scripts/check_hydradg_web_links.py \
  scripts/run_hackhydra_release_batches_magicstudio.sh \
  scripts/build_hackhydra_public_export.sh
  do copy_file "$f"; done

progress 45 COPY_TRACK_CODE
PKG="HydraDG_DaisyTrain_v0.3.7"
for f in \
  "$PKG/BEST_USE_MAGICSTUDIO.md" \
  "$PKG/docs/DATASETS_TRACK01_TRACK03.md" \
  "$PKG/eval/best_use_reference/HYDRADB_CI_FAILURE_20260819.md" \
  "$PKG/eval/best_use_reference/REFERENCE_SMOKE80_20260818.md" \
  "$PKG/scripts/analyze_best_use_ablation.py" \
  "$PKG/scripts/best_use_local_server.py" \
  "$PKG/scripts/best_use_local_server_hackhydra.py" \
  "$PKG/scripts/best_use_magicstudio.sh" \
  "$PKG/scripts/best_use_structural_suite.py" \
  "$PKG/scripts/best_use_typed_graph.py" \
  "$PKG/scripts/bootstrap_best_use_magicstudio.sh" \
  "$PKG/scripts/pull_track01_track03_datasets.sh" \
  "$PKG/scripts/run_best_use_longmemeval.py" \
  "$PKG/scripts/run_best_use_typed_longmemeval.py" \
  "$PKG/scripts/run_submission_daisy_track03.sh" \
  "$PKG/scripts/run_track03_live_golden_path.py" \
  "$PKG/scripts/track01_hydraontology_canary.py" \
  "$PKG/scripts/track02_hydrablast_canary.py"
  do copy_file "$f"; done

progress 55 COPY_CI
for f in \
  .github/workflows/hackhydra-best-use-v2-structural.yml \
  .github/workflows/hackhydra-judge-lab.yml \
  .github/workflows/hackhydra-track01-canary.yml \
  .github/workflows/hackhydra-track02-canary.yml
  do copy_file "$f"; done

progress 61 WRITE_EXPORT_METADATA
cat > "$EXPORT_ROOT/PUBLIC_EXPORT_RECEIPT.json" <<EOF
{
  "schema": "hydradg.public_export_receipt.v1",
  "source_repository": "biobitworks/hydradg",
  "source_branch": "$SOURCE_BRANCH",
  "source_commit": "$SOURCE_SHA",
  "transform": "PUBLIC_EXPORT_v1_EXPLICIT_ALLOWLIST",
  "evidence_class": "DETERMINISTIC_LOCAL_FILE_SELECTION_PENDING_FINAL_REVIEW",
  "claim_ceiling": "FRESH_HISTORY_EXPORT_IDENTITY_AND_SELECTION_ONLY",
  "signature_state": "NOT_SIGNED",
  "merkle_state": "NOT_MERKLE_COMMITTED"
}
EOF

cat > "$EXPORT_ROOT/.gitignore" <<'EOF'
.DS_Store
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
*.secret
secrets/
private_keys/
node_modules/
.next/
__pycache__/
*.pyc
.venv/
.venv-*/
*.pt
*.bin
*.safetensors
EOF

progress 68 HARD_EXCLUSION_GATE
BAD_PATHS="$(find "$EXPORT_ROOT" -type f \( \
  -name '.env' -o -name '.env.local' -o -name '*.pem' -o -name '*.key' -o \
  -name '*.p12' -o -name '*.pfx' -o -name '*.secret' -o -name '*.pt' -o \
  -name '*.bin' -o -name '*.safetensors' \) -print)"
if [ -n "$BAD_PATHS" ]; then
  echo "STOP: forbidden file entered export"
  printf '%s\n' "$BAD_PATHS"
  exit 30
fi

find "$EXPORT_ROOT" -type d -name .git -print | grep -q . && { echo "STOP: nested .git copied"; exit 31; } || true

progress 74 SIZE_GATE
while IFS= read -r -d '' f; do
  bytes="$(stat -f %z "$f" 2>/dev/null || stat -c %s "$f")"
  if [ "$bytes" -gt 50000000 ]; then
    echo "STOP: public export file exceeds 50MB: $bytes $f"
    exit 32
  fi
done < <(find "$EXPORT_ROOT" -type f -print0)

progress 80 SECRET_SCAN
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "STOP: gitleaks is required before public publication"
  echo "Install on macOS: brew install gitleaks"
  exit 40
fi
(
  cd "$EXPORT_ROOT"
  gitleaks dir --redact=100 --no-banner .
)

progress 86 HASH_EXPORT
(
  cd "$EXPORT_ROOT"
  find . -type f ! -path './.git/*' ! -name 'PUBLIC_EXPORT_SHA256SUMS.txt' ! -name 'PUBLIC_EXPORT_MANIFEST_SHA256.txt' -print0 \
    | LC_ALL=C sort -z \
    | xargs -0 shasum -a 256 > PUBLIC_EXPORT_SHA256SUMS.txt
  shasum -a 256 PUBLIC_EXPORT_SHA256SUMS.txt | tee PUBLIC_EXPORT_MANIFEST_SHA256.txt
)

progress 92 FRESH_GIT
cd "$EXPORT_ROOT"
git init -b main
git add -A
git status --short

# Final content-origin admission remains human-reviewed; this commit is created
# only after deterministic export/secret/size gates pass.
git commit -m "Hack Hydra 2026 submission export"

progress 97 VERIFY_HISTORY
COUNT="$(git rev-list --count HEAD)"
test "$COUNT" = "1" || { echo "STOP: export history is not fresh"; exit 50; }
EXPORT_SHA="$(git rev-parse HEAD)"
echo "FRESH_HISTORY=YES"
echo "EXPORT_COMMIT=$EXPORT_SHA"
echo "EXPORT_ROOT=$EXPORT_ROOT"

echo
progress 100 READY_FOR_HUMAN_ADMISSION
echo "PUBLIC_EXPORT_BUILT=YES"
echo "PUBLICATION_NOT_YET_PERFORMED=YES"
echo "NEXT=Review content-origin eligibility, then create/push a NEW public GitHub repository."
echo "Example after review: gh repo create biobitworks/hydradg-hackhydra --public --source=. --remote=origin --push"
