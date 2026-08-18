#!/usr/bin/env bash
set -euo pipefail

# Run on magicPRObox. Bootstraps Homebrew on magicSTUDIObox over ordinary SSH/Tailscale.
# It intentionally uses an interactive TTY for Homebrew's initial sudo/confirmation step.
# After Homebrew exists, package installation remains handled by magicstudio_homebrew_audit.sh.

STUDIO_SSH="${STUDIO_SSH:-magicstudiobox}"

fail(){ echo "FAIL=$1"; exit "${2:-1}"; }

CONTROL_HOST="$(hostname 2>/dev/null || true)"
echo "CONTROL_HOST=$CONTROL_HOST"
echo "STUDIO_SSH=$STUDIO_SSH"

command -v ssh >/dev/null 2>&1 || fail MISSING_SSH 10

# Verify the remote identity and Apple Silicon architecture before changing anything.
ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO_SSH" 'bash -s' <<'REMOTE_PREFLIGHT' || fail STUDIO_PREFLIGHT 11
set -euo pipefail
CN="$(scutil --get ComputerName 2>/dev/null || true)"
LH="$(scutil --get LocalHostName 2>/dev/null || true)"
HN="$(hostname 2>/dev/null || true)"
ARCH="$(uname -m)"
printf 'COMPUTER_NAME=%s\nLOCAL_HOST_NAME=%s\nHOSTNAME=%s\nARCH=%s\n' "$CN" "$LH" "$HN" "$ARCH"
case "$(printf '%s %s %s' "$CN" "$LH" "$HN" | tr '[:upper:]' '[:lower:]')" in
  *magicstudiobox*) ;;
  *) echo 'FAIL=REMOTE_NOT_MAGICSTUDIO'; exit 21 ;;
esac
[ "$ARCH" = "arm64" ] || { echo "FAIL=UNEXPECTED_ARCH:$ARCH"; exit 22; }
if xcode-select -p >/dev/null 2>&1; then
  echo "XCODE_CLT=PASS"
else
  echo "XCODE_CLT=MISS"
  echo "ACTION=Install Apple Command Line Tools before Homebrew."
  exit 23
fi
if command -v brew >/dev/null 2>&1 || [ -x /opt/homebrew/bin/brew ]; then
  echo "BREW_ALREADY_PRESENT=YES"
else
  echo "BREW_ALREADY_PRESENT=NO"
fi
REMOTE_PREFLIGHT

# If already installed, skip the installer and just normalize shellenv.
if ssh "$STUDIO_SSH" 'test -x /opt/homebrew/bin/brew || command -v brew >/dev/null 2>&1'; then
  echo "BREW_INSTALL=SKIPPED_ALREADY_PRESENT"
else
  echo "BREW_INSTALL=BEGIN"
  echo "Homebrew may ask for the Studio user's password/confirmation in this remote TTY."
  ssh -t "$STUDIO_SSH" '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
fi

# Persist the supported Apple Silicon shell environment idempotently.
ssh "$STUDIO_SSH" 'bash -s' <<'REMOTE_POST' || fail HOMEBREW_POSTINSTALL 30
set -euo pipefail
BREW=/opt/homebrew/bin/brew
[ -x "$BREW" ] || { echo "FAIL=BREW_BINARY_MISSING_AFTER_INSTALL"; exit 31; }
LINE='eval "$(/opt/homebrew/bin/brew shellenv)"'
touch "$HOME/.zprofile"
grep -Fqx "$LINE" "$HOME/.zprofile" || printf '%s\n' "$LINE" >> "$HOME/.zprofile"
eval "$($BREW shellenv)"
echo "BREW_PREFIX=$($BREW --prefix)"
echo "BREW_VERSION=$($BREW --version | head -n1)"
echo "BREW_SHELLENV=PASS"
REMOTE_POST

echo "MAGICSTUDIO_HOMEBREW_BOOTSTRAP=YES"
echo "NEXT=bash scripts/magicstudio_homebrew_audit.sh audit"
