#!/usr/bin/env bash
set -euo pipefail

# Universal GitHub bootstrap/reconciliation for magicPRObox + magicSTUDIObox.
# Run ONLY on magicPRObox.
#
# Modes:
#   audit      : inventory only; no repository or package mutation
#   apply      : bootstrap Studio Homebrew/tooling/GitHub auth, normalize Git
#                identity/LFS, reconcile every existing project that already
#                maps to an accessible GitHub repository, and create the
#                canonical private LessWrong repo if required.
#   apply-all  : same as apply; additionally create a PRIVATE biobitworks repo
#                for a project-like local-only directory ONLY when it exists on
#                exactly one machine and passes size + Gitleaks gates.
#
# Important boundaries:
# - magicPRObox is the control plane.
# - ordinary SSH over Tailscale is the machine-control channel.
# - Ollarma is the governed model-inference channel, NOT a remote shell.
# - private keys / live credentials are never intentionally committed.
# - dirty Git worktrees are reported and skipped; they are never reset/cleaned.
# - non-Git non-empty directories are never overwritten by clone.
# - upstream/external origins (e.g. hydra-db/hydradb) are preserved.

MODE="${1:-audit}"
case "$MODE" in
  audit) APPLY=0; CREATE_UNMAPPED=0 ;;
  apply) APPLY=1; CREATE_UNMAPPED=0 ;;
  apply-all) APPLY=1; CREATE_UNMAPPED=1 ;;
  *) echo "USAGE: $0 [audit|apply|apply-all]"; exit 2 ;;
esac

ACTIVE="/Users/byron/projects/active"
STUDIO="${STUDIO_SSH:-magicstudiobox}"
OWNER="${GITHUB_OWNER:-biobitworks}"
ROOT="$ACTIVE/hydradg"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT_DIR="$ROOT/HydraDG_DaisyTrain_v0.3.7/eval/remote_work/UNIVERSAL-GITHUB-$STAMP"
mkdir -p "$REPORT_DIR"

log(){ printf '[%3s%%] %s\n' "$1" "$2"; }
fail(){ echo "FAIL=$1"; exit "${2:-1}"; }
remote(){ ssh -o ConnectTimeout=15 "$STUDIO" "$@"; }

host_identity(){
  scutil --get LocalHostName 2>/dev/null || hostname
}

is_magicpro(){
  local ids
  ids="$(printf '%s %s %s' "$(scutil --get ComputerName 2>/dev/null || true)" "$(scutil --get LocalHostName 2>/dev/null || true)" "$(hostname 2>/dev/null || true)" | tr '[:upper:]' '[:lower:]')"
  case "$ids" in *magicprobox*) return 0;; *) return 1;; esac
}

brew_env_local(){
  if command -v brew >/dev/null 2>&1; then eval "$(brew shellenv)";
  elif [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)";
  elif [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)";
  else return 1; fi
}

install_local_tools(){
  brew_env_local || fail "MAGICPRO_HOMEBREW_MISSING" 10
  local missing=""
  local spec cmd formula
  for spec in 'gh|gh' 'gitleaks|gitleaks' 'git-lfs|git-lfs' 'jq|jq' 'tmux|tmux' 'uv|uv' 'just|just'; do
    cmd="${spec%%|*}"; formula="${spec#*|}"
    command -v "$cmd" >/dev/null 2>&1 || missing="$missing $formula"
  done
  if [ -n "${missing// /}" ]; then
    if [ "$APPLY" -eq 1 ]; then
      # shellcheck disable=SC2086
      brew install $missing
    else
      echo "MAGICPRO_MISSING_FORMULAE=$missing"
    fi
  fi
}

studio_bootstrap_tools(){
  if remote 'test -x /opt/homebrew/bin/brew || command -v brew >/dev/null 2>&1'; then
    echo "STUDIO_BREW=PASS"
  else
    echo "STUDIO_BREW=MISS"
    [ "$APPLY" -eq 1 ] || return 0
    echo "STUDIO_HOMEBREW_INSTALL=BEGIN"
    # Homebrew's initial install may require sudo/password confirmation.
    ssh -tt "$STUDIO" '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  fi

  remote "APPLY=$APPLY bash -s" <<'REMOTE_TOOLS'
set -euo pipefail
if [ -x /opt/homebrew/bin/brew ]; then BREW=/opt/homebrew/bin/brew
elif command -v brew >/dev/null 2>&1; then BREW="$(command -v brew)"
elif [ -x /usr/local/bin/brew ]; then BREW=/usr/local/bin/brew
else echo STUDIO_BREW_STILL_MISSING; exit 20; fi
LINE='eval "$(/opt/homebrew/bin/brew shellenv)"'
if [ "$BREW" = /opt/homebrew/bin/brew ]; then
  touch "$HOME/.zprofile"
  grep -Fqx "$LINE" "$HOME/.zprofile" || printf '%s\n' "$LINE" >> "$HOME/.zprofile"
fi
eval "$($BREW shellenv)"
missing=""
for spec in 'gh|gh' 'gitleaks|gitleaks' 'git-lfs|git-lfs' 'jq|jq' 'tmux|tmux' 'uv|uv' 'just|just'; do
  cmd="${spec%%|*}"; formula="${spec#*|}"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "STUDIO_TOOL_PASS=$cmd:$(command -v "$cmd")"
  else
    echo "STUDIO_TOOL_MISS=$cmd:$formula"
    missing="$missing $formula"
  fi
done
if [ "$APPLY" = 1 ] && [ -n "${missing// /}" ]; then
  # shellcheck disable=SC2086
  brew install $missing
fi
command -v git-lfs >/dev/null 2>&1 && git lfs install --skip-repo >/dev/null || true
REMOTE_TOOLS
}

ensure_gh_auth(){
  if gh auth status >/dev/null 2>&1; then
    echo "MAGICPRO_GH_AUTH=PASS"
  elif [ "$APPLY" -eq 1 ]; then
    gh auth login --hostname github.com --git-protocol https --web
    gh auth setup-git
  else
    echo "MAGICPRO_GH_AUTH=MISS"
  fi

  if remote 'eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || true)"; command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1'; then
    echo "MAGICSTUDIO_GH_AUTH=PASS"
  elif [ "$APPLY" -eq 1 ]; then
    echo "MAGICSTUDIO_GH_AUTH=INTERACTIVE_LOGIN"
    ssh -tt "$STUDIO" 'eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || true)"; gh auth login --hostname github.com --git-protocol https --web && gh auth setup-git'
  else
    echo "MAGICSTUDIO_GH_AUTH=MISS"
  fi
}

normalize_git_identity(){
  local name email
  name="$(git config --global user.name || true)"
  email="$(git config --global user.email || true)"
  [ -n "$name" ] && [ -n "$email" ] || fail "MAGICPRO_GIT_IDENTITY_MISSING" 30
  echo "MAGICPRO_GIT_NAME=$name"
  echo "MAGICPRO_GIT_EMAIL=$email"
  if [ "$APPLY" -eq 1 ]; then
    git lfs install --skip-repo >/dev/null 2>&1 || true
    remote "NAME=$(printf %q "$name") EMAIL=$(printf %q "$email") bash -s" <<'REMOTE_ID'
set -euo pipefail
git config --global user.name "$NAME"
git config --global user.email "$EMAIL"
eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || true)"
command -v gh >/dev/null 2>&1 && gh auth setup-git >/dev/null || true
command -v git-lfs >/dev/null 2>&1 && git lfs install --skip-repo >/dev/null || true
REMOTE_ID
  fi
}

inventory_local(){
  local host="$1" out="$2" d name origin branch dirty head top
  : > "$out"
  while IFS= read -r -d '' d; do
    name="$(basename "$d")"
    if git -C "$d" rev-parse --show-toplevel >/dev/null 2>&1; then
      top="$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || true)"
      if [ "$top" != "$d" ]; then
        printf '%s\t%s\t%s\tNESTED_IN_OTHER_GIT\t%s\t\t\t\n' "$host" "$name" "$d" "$top" >> "$out"
        continue
      fi
      origin="$(git -C "$d" remote get-url origin 2>/dev/null || true)"
      branch="$(git -C "$d" branch --show-current 2>/dev/null || true)"
      dirty=0; [ -z "$(git -C "$d" status --porcelain 2>/dev/null)" ] || dirty=1
      head="$(git -C "$d" rev-parse HEAD 2>/dev/null || true)"
      printf '%s\t%s\t%s\tGIT\t%s\t%s\t%s\t%s\n' "$host" "$name" "$d" "$origin" "$branch" "$dirty" "$head" >> "$out"
    else
      printf '%s\t%s\t%s\tNON_GIT\t\t\t\t\n' "$host" "$name" "$d" >> "$out"
    fi
  done < <(find "$ACTIVE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
}

inventory_studio(){
  remote 'bash -s' > "$REPORT_DIR/studio_projects.tsv" <<'REMOTE_INV'
set -euo pipefail
ACTIVE=/Users/byron/projects/active
HOST=magicSTUDIObox
while IFS= read -r -d '' d; do
  name="$(basename "$d")"
  if git -C "$d" rev-parse --show-toplevel >/dev/null 2>&1; then
    top="$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || true)"
    if [ "$top" != "$d" ]; then
      printf '%s\t%s\t%s\tNESTED_IN_OTHER_GIT\t%s\t\t\t\n' "$HOST" "$name" "$d" "$top"
      continue
    fi
    origin="$(git -C "$d" remote get-url origin 2>/dev/null || true)"
    branch="$(git -C "$d" branch --show-current 2>/dev/null || true)"
    dirty=0; [ -z "$(git -C "$d" status --porcelain 2>/dev/null)" ] || dirty=1
    head="$(git -C "$d" rev-parse HEAD 2>/dev/null || true)"
    printf '%s\t%s\t%s\tGIT\t%s\t%s\t%s\t%s\n' "$HOST" "$name" "$d" "$origin" "$branch" "$dirty" "$head"
  else
    printf '%s\t%s\t%s\tNON_GIT\t\t\t\t\n' "$HOST" "$name" "$d"
  fi
done < <(find "$ACTIVE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
REMOTE_INV
}

github_catalog(){
  gh repo list "$OWNER" --limit 200 --json name,nameWithOwner,defaultBranchRef,visibility \
    --jq '.[] | [.name,.nameWithOwner,(.defaultBranchRef.name // ""),.visibility] | @tsv' \
    > "$REPORT_DIR/github_catalog.tsv"
}

repo_record(){
  local name="$1"
  awk -F '\t' -v n="$name" '$1==n {print; exit}' "$REPORT_DIR/github_catalog.tsv"
}

repo_record_ci(){
  local name="$1"
  awk -F '\t' -v n="$name" 'tolower($1)==tolower(n) {print; exit}' "$REPORT_DIR/github_catalog.tsv"
}

sync_existing_local_repo(){
  local path="$1" label="$2"
  local dirty branch origin
  dirty="$(git -C "$path" status --porcelain)"
  origin="$(git -C "$path" remote get-url origin 2>/dev/null || true)"
  branch="$(git -C "$path" branch --show-current 2>/dev/null || true)"
  if [ -n "$dirty" ]; then
    echo "SKIP_DIRTY=$label:$path"
    return 0
  fi
  [ "$APPLY" -eq 1 ] || { echo "AUDIT_CLEAN_GIT=$label:$path:$origin:$branch"; return 0; }
  [ -n "$origin" ] || { echo "SKIP_NO_ORIGIN=$label:$path"; return 0; }
  git -C "$path" fetch origin --prune --quiet || { echo "FETCH_FAILED=$label:$path:$origin"; return 0; }
  if [ -n "$branch" ] && git -C "$path" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
    git -C "$path" pull --ff-only origin "$branch" >/dev/null || { echo "PULL_BLOCKED=$label:$path:$branch"; return 0; }
  fi
  git -C "$path" lfs install --local >/dev/null 2>&1 || true
  echo "SYNCED_GIT=$label:$path:$(git -C "$path" rev-parse HEAD)"
}

sync_existing_remote_repo(){
  local path="$1" label="$2"
  [ "$APPLY" -eq 1 ] || { echo "AUDIT_REMOTE_GIT=$label:$path"; return 0; }
  remote "P=$(printf %q "$path") LABEL=$(printf %q "$label") bash -s" <<'REMOTE_SYNC_REPO'
set -euo pipefail
if [ -n "$(git -C "$P" status --porcelain)" ]; then echo "SKIP_DIRTY=$LABEL:$P"; exit 0; fi
origin="$(git -C "$P" remote get-url origin 2>/dev/null || true)"
branch="$(git -C "$P" branch --show-current 2>/dev/null || true)"
[ -n "$origin" ] || { echo "SKIP_NO_ORIGIN=$LABEL:$P"; exit 0; }
git -C "$P" fetch origin --prune --quiet || { echo "FETCH_FAILED=$LABEL:$P:$origin"; exit 0; }
if [ -n "$branch" ] && git -C "$P" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
  git -C "$P" pull --ff-only origin "$branch" >/dev/null || { echo "PULL_BLOCKED=$LABEL:$P:$branch"; exit 0; }
fi
git -C "$P" lfs install --local >/dev/null 2>&1 || true
echo "SYNCED_GIT=$LABEL:$P:$(git -C "$P" rev-parse HEAD)"
REMOTE_SYNC_REPO
}

safe_publish_non_git_dir(){
  # Args: host(pro|studio) path repo_full_name
  local host="$1" path="$2" repo="$3"
  [ "$APPLY" -eq 1 ] || { echo "WOULD_CREATE_PRIVATE=$host:$path:$repo"; return 0; }

  local runner_prefix=()
  if [ "$host" = pro ]; then
    (
      cd "$path"
      command -v gitleaks >/dev/null 2>&1 || { echo "BLOCK_CREATE_MISSING_GITLEAKS=$path"; exit 0; }
      big="$(find . -path './.git' -prune -o -type f -size +95M -print -quit 2>/dev/null || true)"
      [ -z "$big" ] || { echo "BLOCK_CREATE_LARGE_FILE=$path:$big"; exit 0; }
      [ -d .git ] || git init -b main
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
      git add -A
      gitleaks git --staged --redact=100 --no-banner . || { echo "BLOCK_CREATE_GITLEAKS=$path"; git reset >/dev/null; exit 0; }
      if ! git rev-parse HEAD >/dev/null 2>&1; then git commit -m "Initialize private project repository";
      elif ! git diff --cached --quiet; then git commit -m "Checkpoint project before GitHub bootstrap"; fi
      gh repo view "$repo" >/dev/null 2>&1 || gh repo create "$repo" --private --source=. --remote=origin
      git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$repo.git"
      git push -u origin "$(git branch --show-current)"
      echo "CREATED_PRIVATE=$path:$repo"
    )
  else
    remote "P=$(printf %q "$path") REPO=$(printf %q "$repo") bash -s" <<'REMOTE_PUBLISH'
set -euo pipefail
eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || true)"
cd "$P"
command -v gitleaks >/dev/null 2>&1 || { echo "BLOCK_CREATE_MISSING_GITLEAKS=$P"; exit 0; }
big="$(find . -path './.git' -prune -o -type f -size +95M -print -quit 2>/dev/null || true)"
[ -z "$big" ] || { echo "BLOCK_CREATE_LARGE_FILE=$P:$big"; exit 0; }
[ -d .git ] || git init -b main
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
git add -A
gitleaks git --staged --redact=100 --no-banner . || { echo "BLOCK_CREATE_GITLEAKS=$P"; git reset >/dev/null; exit 0; }
if ! git rev-parse HEAD >/dev/null 2>&1; then git commit -m "Initialize private project repository";
elif ! git diff --cached --quiet; then git commit -m "Checkpoint project before GitHub bootstrap"; fi
gh repo view "$REPO" >/dev/null 2>&1 || gh repo create "$REPO" --private --source=. --remote=origin
git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$REPO.git"
git push -u origin "$(git branch --show-current)"
echo "CREATED_PRIVATE=$P:$REPO"
REMOTE_PUBLISH
  fi
}

clone_if_absent(){
  local host="$1" path="$2" repo="$3"
  if [ "$host" = pro ]; then
    if [ -e "$path" ]; then
      [ -d "$path/.git" ] || { echo "BLOCK_CLONE_NON_GIT_EXISTS=pro:$path:$repo"; return 0; }
      sync_existing_local_repo "$path" pro
    elif [ "$APPLY" -eq 1 ]; then
      gh repo clone "$repo" "$path"
      echo "CLONED=pro:$repo:$path"
    else echo "WOULD_CLONE=pro:$repo:$path"; fi
  else
    if remote "test -e $(printf %q "$path")"; then
      if remote "test -d $(printf %q "$path/.git")"; then sync_existing_remote_repo "$path" studio
      else echo "BLOCK_CLONE_NON_GIT_EXISTS=studio:$path:$repo"; fi
    elif [ "$APPLY" -eq 1 ]; then
      remote "eval \"\$(/opt/homebrew/bin/brew shellenv 2>/dev/null || true)\"; mkdir -p $(printf %q "$ACTIVE"); gh repo clone $(printf %q "$repo") $(printf %q "$path")"
      echo "CLONED=studio:$repo:$path"
    else echo "WOULD_CLONE=studio:$repo:$path"; fi
  fi
}

log 2 "verify control host + SSH/Tailscale"
is_magicpro || fail "RUN_THIS_SCRIPT_ON_MAGICPROBOX" 3
command -v ssh >/dev/null 2>&1 || fail "MAGICPRO_SSH_MISSING" 4
ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO" 'printf "STUDIO_SSH=PASS\n"; hostname' > "$REPORT_DIR/studio_ssh.txt" || fail "STUDIO_SSH_FAILED" 5

log 8 "toolchain audit/bootstrap"
install_local_tools
studio_bootstrap_tools

log 18 "GitHub authentication + global Git identity"
if command -v gh >/dev/null 2>&1; then ensure_gh_auth; fi
if [ "$APPLY" -eq 1 ] || gh auth status >/dev/null 2>&1; then normalize_git_identity; fi

log 28 "inventory projects on both machines"
inventory_local magicPRObox "$REPORT_DIR/magicpro_projects.tsv"
inventory_studio
github_catalog
cat "$REPORT_DIR/magicpro_projects.tsv" "$REPORT_DIR/studio_projects.tsv" > "$REPORT_DIR/all_projects.tsv"
cut -f2 "$REPORT_DIR/all_projects.tsv" | sort -fu > "$REPORT_DIR/project_names.txt"

log 38 "reconcile existing Git projects and matching GitHub repos"
while IFS= read -r name; do
  [ -n "$name" ] || continue
  pro_line="$(awk -F '\t' -v n="$name" '$1=="magicPRObox" && $2==n {print; exit}' "$REPORT_DIR/all_projects.tsv")"
  studio_line="$(awk -F '\t' -v n="$name" '$1=="magicSTUDIObox" && $2==n {print; exit}' "$REPORT_DIR/all_projects.tsv")"
  rec="$(repo_record "$name")"; [ -n "$rec" ] || rec="$(repo_record_ci "$name")"
  repo="$(printf '%s' "$rec" | awk -F '\t' '{print $2}')"

  pro_state="$(printf '%s' "$pro_line" | awk -F '\t' '{print $4}')"
  studio_state="$(printf '%s' "$studio_line" | awk -F '\t' '{print $4}')"
  pro_path="$(printf '%s' "$pro_line" | awk -F '\t' '{print $3}')"
  studio_path="$(printf '%s' "$studio_line" | awk -F '\t' '{print $3}')"

  if [ "$pro_state" = GIT ]; then sync_existing_local_repo "$pro_path" pro; fi
  if [ "$studio_state" = GIT ]; then sync_existing_remote_repo "$studio_path" studio; fi

  # A matching biobitworks repo may be cloned to the other machine only when
  # this project already exists on at least one machine.
  if [ -n "$repo" ]; then
    if [ -n "$pro_line" ] && [ -z "$studio_line" ]; then clone_if_absent studio "$ACTIVE/$name" "$repo"; fi
    if [ -n "$studio_line" ] && [ -z "$pro_line" ]; then clone_if_absent pro "$ACTIVE/$name" "$repo"; fi
  fi

done < "$REPORT_DIR/project_names.txt"

log 62 "canonical LessWrong publication boundary"
# LessWrong is explicitly Studio-canonical. If no GitHub repo exists yet, create
# it from Studio with secret/size gates, then clone/sync on PRObox.
LW_REPO="$OWNER/lesswrong"
LW_STUDIO="$ACTIVE/lesswrong"
LW_PRO="$ACTIVE/lesswrong"
if gh repo view "$LW_REPO" >/dev/null 2>&1; then
  clone_if_absent studio "$LW_STUDIO" "$LW_REPO"
  clone_if_absent pro "$LW_PRO" "$LW_REPO"
elif remote "test -d $(printf %q "$LW_STUDIO")"; then
  echo "LESSWRONG_REMOTE=ABSENT_STUDIO_SOURCE_PRESENT"
  safe_publish_non_git_dir studio "$LW_STUDIO" "$LW_REPO"
  if [ "$APPLY" -eq 1 ] && gh repo view "$LW_REPO" >/dev/null 2>&1; then clone_if_absent pro "$LW_PRO" "$LW_REPO"; fi
else
  echo "LESSWRONG_BLOCKED=STUDIO_SOURCE_MISSING"
fi

log 72 "local-only project report / optional private promotion"
: > "$REPORT_DIR/unmapped_projects.tsv"
while IFS= read -r name; do
  [ -n "$name" ] || continue
  rec="$(repo_record "$name")"; [ -n "$rec" ] || rec="$(repo_record_ci "$name")"
  [ -z "$rec" ] || continue
  pro_line="$(awk -F '\t' -v n="$name" '$1=="magicPRObox" && $2==n {print; exit}' "$REPORT_DIR/all_projects.tsv")"
  studio_line="$(awk -F '\t' -v n="$name" '$1=="magicSTUDIObox" && $2==n {print; exit}' "$REPORT_DIR/all_projects.tsv")"
  printf '%s\t%s\t%s\n' "$name" "${pro_line:-ABSENT}" "${studio_line:-ABSENT}" >> "$REPORT_DIR/unmapped_projects.tsv"

  [ "$CREATE_UNMAPPED" -eq 1 ] || continue
  pro_state="$(printf '%s' "$pro_line" | awk -F '\t' '{print $4}')"
  studio_state="$(printf '%s' "$studio_line" | awk -F '\t' '{print $4}')"
  pro_path="$(printf '%s' "$pro_line" | awk -F '\t' '{print $3}')"
  studio_path="$(printf '%s' "$studio_line" | awk -F '\t' '{print $3}')"

  # Never remap an existing Git repo with an external/upstream origin.
  if [ "$pro_state" = GIT ] || [ "$studio_state" = GIT ]; then
    echo "UNMAPPED_GIT_PRESERVED=$name"
    continue
  fi

  # Only auto-promote a non-Git project if it exists on exactly one machine.
  if [ "$pro_state" = NON_GIT ] && [ -z "$studio_line" ]; then
    safe_publish_non_git_dir pro "$pro_path" "$OWNER/$name"
    clone_if_absent studio "$ACTIVE/$name" "$OWNER/$name"
  elif [ "$studio_state" = NON_GIT ] && [ -z "$pro_line" ]; then
    safe_publish_non_git_dir studio "$studio_path" "$OWNER/$name"
    clone_if_absent pro "$ACTIVE/$name" "$OWNER/$name"
  elif [ "$pro_state" = NON_GIT ] && [ "$studio_state" = NON_GIT ]; then
    echo "AMBIGUOUS_TWO_NON_GIT_COPIES=$name"
  fi
done < "$REPORT_DIR/project_names.txt"

log 86 "refresh final inventory"
inventory_local magicPRObox "$REPORT_DIR/magicpro_projects_final.tsv"
inventory_studio > /dev/null 2>&1 || true
# Re-run Studio inventory into a final file without replacing the first evidence.
remote 'bash -s' > "$REPORT_DIR/studio_projects_final.tsv" <<'REMOTE_FINAL_INV'
set -euo pipefail
ACTIVE=/Users/byron/projects/active
HOST=magicSTUDIObox
while IFS= read -r -d '' d; do
  name="$(basename "$d")"
  if git -C "$d" rev-parse --show-toplevel >/dev/null 2>&1; then
    top="$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || true)"
    origin="$(git -C "$d" remote get-url origin 2>/dev/null || true)"
    branch="$(git -C "$d" branch --show-current 2>/dev/null || true)"
    dirty=0; [ -z "$(git -C "$d" status --porcelain 2>/dev/null)" ] || dirty=1
    head="$(git -C "$d" rev-parse HEAD 2>/dev/null || true)"
    printf '%s\t%s\t%s\tGIT\t%s\t%s\t%s\t%s\n' "$HOST" "$name" "$d" "$origin" "$branch" "$dirty" "$head"
  else
    printf '%s\t%s\t%s\tNON_GIT\t\t\t\t\n' "$HOST" "$name" "$d"
  fi
done < <(find "$ACTIVE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
REMOTE_FINAL_INV

log 92 "write bounded readiness summary"
PRO_GIT="$(awk -F '\t' '$4=="GIT"{n++} END{print n+0}' "$REPORT_DIR/magicpro_projects_final.tsv")"
STUDIO_GIT="$(awk -F '\t' '$4=="GIT"{n++} END{print n+0}' "$REPORT_DIR/studio_projects_final.tsv")"
UNMAPPED="$(wc -l < "$REPORT_DIR/unmapped_projects.tsv" | tr -d ' ')"
cat > "$REPORT_DIR/final_status.txt" <<EOF
UNIVERSAL_GITHUB_SETUP_MODE=$MODE
CONTROL_HOST=$(host_identity)
STUDIO_SSH=$STUDIO
MAGICPRO_GIT_PROJECTS=$PRO_GIT
MAGICSTUDIO_GIT_PROJECTS=$STUDIO_GIT
UNMAPPED_PROJECT_ROWS=$UNMAPPED
PRIVATE_KEY_POLICY=LOCAL_ONLY
DIRTY_WORKTREE_POLICY=SKIP_NOT_RESET
OLLARMA_ROLE=MODEL_INFERENCE_NOT_SHELL
EOF

log 96 "optional HydraDG custody checkpoint"
if [ "$APPLY" -eq 1 ]; then
  cd "$ROOT"
  git add "HydraDG_DaisyTrain_v0.3.7/eval/remote_work/UNIVERSAL-GITHUB-$STAMP"
  if command -v gitleaks >/dev/null 2>&1; then gitleaks git --staged --redact=100 --no-banner .; fi
  if ! git diff --cached --quiet; then
    git commit -m "Record universal two-machine GitHub setup $STAMP"
    branch="$(git branch --show-current)"
    git push origin "$branch"
    git fetch origin "$branch" --quiet
    test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$branch")" || fail "HYDRADG_REPORT_PUSH_DIVERGENCE" 80
  fi
fi

log 100 "complete"
echo "UNIVERSAL_GITHUB_SETUP=COMPLETE"
echo "MODE=$MODE"
echo "REPORT_DIR=$REPORT_DIR"
echo "MAGICPRO_GIT_PROJECTS=$PRO_GIT"
echo "MAGICSTUDIO_GIT_PROJECTS=$STUDIO_GIT"
echo "UNMAPPED_PROJECT_ROWS=$UNMAPPED"
echo "NEXT=Review unmapped_projects.tsv before using apply-all if any local-only projects remain."
