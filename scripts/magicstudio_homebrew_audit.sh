#!/usr/bin/env bash
set -euo pipefail

# Run on magicPRObox. Audits magicSTUDIObox through ordinary SSH over the
# existing Tailscale path. With --install, installs only missing Homebrew
# formulae required by the current HydraDG remote-work harnesses.
# Ollarma remains the governed model-inference lane, not a shell/control channel.

STUDIO="${STUDIO_SSH:-magicstudiobox}"
MODE="${1:-audit}"
case "$MODE" in
  audit|--audit) INSTALL=0 ;;
  install|--install) INSTALL=1 ;;
  *) echo "USAGE: $0 [audit|--install]"; exit 2 ;;
esac

remote(){ ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO" "$@"; }

printf 'CONTROL_HOST=%s\n' "$(hostname)"
printf 'STUDIO_SSH=%s\n' "$STUDIO"

remote "INSTALL=$INSTALL bash -s" <<'REMOTE'
set -euo pipefail

echo "=== MAGICSTUDIO IDENTITY ==="
echo "COMPUTER_NAME=$(scutil --get ComputerName 2>/dev/null || true)"
echo "LOCAL_HOST_NAME=$(scutil --get LocalHostName 2>/dev/null || true)"
echo "HOSTNAME=$(hostname)"
echo "ARCH=$(uname -m)"

echo
echo "=== HOMEBREW ==="
# Non-login SSH shells on Apple Silicon may not inherit /opt/homebrew/bin.
# Detect the supported Homebrew prefix explicitly and activate shellenv before
# auditing command availability.
if command -v brew >/dev/null 2>&1; then
  BREW_BIN="$(command -v brew)"
elif [ -x /opt/homebrew/bin/brew ]; then
  BREW_BIN=/opt/homebrew/bin/brew
elif [ -x /usr/local/bin/brew ]; then
  BREW_BIN=/usr/local/bin/brew
else
  echo "BREW=MISS"
  echo "ACTION=Install Homebrew on magicSTUDIObox, then rerun this audit."
  exit 20
fi

eval "$($BREW_BIN shellenv)"
BREW_PREFIX="$(brew --prefix)"
echo "BREW=PASS"
echo "BREW_BIN=$(command -v brew)"
echo "BREW_PREFIX=$BREW_PREFIX"
brew --version | head -n1

REQS='gh|gh|GitHub bootstrap/clone
gitleaks|gitleaks|staged secret admission gate
tmux|tmux|persistent Ollarma/Watchtower/HydraDB services
uv|uv|Ollarma and Watchtower Python execution
git-lfs|git-lfs|HydraDG large Git/LFS objects
jq|jq|receipt/JSON tooling
just|just|HydraDB build/check harness'

MISSING_FORMULAE=""
echo
echo "=== REQUIRED HOMEBREW-CAPABLE TOOLS ==="
while IFS='|' read -r cmd formula why; do
  [ -n "$cmd" ] || continue
  if command -v "$cmd" >/dev/null 2>&1; then
    path="$(command -v "$cmd")"
    printf 'PASS  %-10s %-28s %s\n' "$cmd" "$path" "$why"
  else
    printf 'MISS  %-10s formula=%-15s %s\n' "$cmd" "$formula" "$why"
    MISSING_FORMULAE="$MISSING_FORMULAE $formula"
  fi
done <<EOF
$REQS
EOF

echo
echo "=== REQUIRED COMMANDS / NON-FORMULA-SPECIFIC ==="
for cmd in git curl ssh shasum openssl python3 tailscale rustc cargo; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "PASS  $cmd=$(command -v "$cmd")"
  else
    echo "MISS  $cmd"
  fi
done

echo
echo "=== VITHIA PYTHON ENVIRONMENT ==="
PY=""
for C in \
  /Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7/.venv-hydradg/bin/python \
  /Users/byron/fco-venv/bin/python3 \
  /opt/homebrew/bin/python3
 do
  if [ -x "$C" ] && "$C" -c 'import torch,transformers,numpy' >/dev/null 2>&1; then
    PY="$C"; break
  fi
done
if [ -n "$PY" ]; then
  echo "VITHIA_PYTHON=PASS:$PY"
else
  echo "VITHIA_PYTHON=MISS:need python environment with torch transformers numpy"
fi

if [ "$INSTALL" = "1" ]; then
  if [ -n "${MISSING_FORMULAE// /}" ]; then
    echo
    echo "=== INSTALL MISSING FORMULAE ==="
    # shellcheck disable=SC2086
    brew install $MISSING_FORMULAE
  else
    echo "NO_HOMEBREW_FORMULAE_MISSING"
  fi
  if command -v git-lfs >/dev/null 2>&1; then
    git lfs install --skip-repo >/dev/null
    echo "GIT_LFS_GLOBAL=CONFIGURED"
  fi
fi

echo
echo "=== GITHUB AUTH ==="
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    echo "GH_AUTH=PASS"
  else
    echo "GH_AUTH=MISS_OR_EXPIRED"
    echo "ACTION_FROM_MAGICPRO=ssh -t magicstudiobox 'eval \"$(/opt/homebrew/bin/brew shellenv)\"; gh auth login --hostname github.com --git-protocol https --web && gh auth setup-git'"
  fi
fi

echo
echo "=== SERVICES ==="
for spec in \
  'Ollarma|http://127.0.0.1:8484/health' \
  'Watchtower|http://127.0.0.1:8000/' \
  'HydraDB-admin|http://127.0.0.1:9090/readyz'
 do
  name="${spec%%|*}"; url="${spec#*|}"
  if curl -fsS "$url" >/dev/null 2>&1; then echo "$name=UP"; else echo "$name=DOWN_OR_NOT_STARTED"; fi
done

echo "MAGICSTUDIO_AUDIT_COMPLETE=YES"
REMOTE
