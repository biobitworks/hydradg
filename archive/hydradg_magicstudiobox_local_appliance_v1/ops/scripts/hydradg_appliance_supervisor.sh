#!/bin/zsh
set -euo pipefail

ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
WEB="$ROOT/apps/hydradg-web"
BEST="$ROOT/HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh"
LOGROOT="${HYDRADG_APPLIANCE_LOGROOT:-$HOME/.local/share/hydradg-appliance}"
BIND="${HYDRADG_APPLIANCE_BIND:-127.0.0.1}"
PORT="${HYDRADG_APPLIANCE_PORT:-3010}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
mkdir -p "$LOGROOT"

health() { curl -fsS --max-time 3 "$1" >/dev/null 2>&1; }

if ! health "http://127.0.0.1:8787/health"; then
  /bin/zsh "$BEST" start >>"$LOGROOT/best-use.log" 2>&1
fi

if ! health "http://127.0.0.1:11434/api/tags"; then
  echo "OLLAMA_NOT_READY: start the Ollama macOS app; raw API remains loopback-only" >&2
fi

cd "$WEB"
if [[ ! -d .next ]]; then
  echo "MISSING_NEXT_BUILD: run npm ci && npm run typecheck && npm run build first" >&2
  exit 20
fi

exec npm run start -- -H "$BIND" -p "$PORT"
