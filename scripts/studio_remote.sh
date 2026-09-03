#!/usr/bin/env bash
# Run commands on magicSTUDIObox from magicPRObox (or any SSH client).
# Non-interactive SSH omits Homebrew from PATH — this wrapper restores it.
#
# Usage (from magicPRObox):
#   ./scripts/studio_remote.sh shell
#   ./scripts/studio_remote.sh exec 'daytona list'
#   ./scripts/studio_remote.sh hydradg 'git status --short'
#   ./scripts/studio_remote.sh sglang              # foreground
#   ./scripts/studio_remote.sh sglang-bg           # nohup + log path
#   ./scripts/studio_remote.sh ollarma 'ollarma health'
set -euo pipefail

# Prefer Tailscale IPv4 alias (Wi-Fi resilient). Override with STUDIO_SSH_HOST if needed.
HOST="${STUDIO_SSH_HOST:-magicstudiobox-ip}"
REMOTE_ROOT="${STUDIO_REMOTE_ROOT:-/Users/byron/projects/active}"

remote_prelude() {
  cat <<'EOF'
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
if [ -f "$HOME/.config/ai-keys/keys.env" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$HOME/.config/ai-keys/keys.env"
  set +a
fi
EOF
}

run_remote() {
  local cmd="$1"
  ssh -o BatchMode=yes "$HOST" "$(remote_prelude)
${cmd}"
}

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
}

cmd="${1:-shell}"
shift || true

case "$cmd" in
  -h|--help|help)
    usage
    ;;
  shell)
    exec ssh "$HOST"
    ;;
  exec)
    [[ $# -ge 1 ]] || { echo "usage: $0 exec '<remote command>'" >&2; exit 2; }
    run_remote "$*"
    ;;
  hydradg)
    [[ $# -ge 1 ]] || { echo "usage: $0 hydradg '<command>'" >&2; exit 2; }
    run_remote "cd ${REMOTE_ROOT}/hydradg && $*"
    ;;
  ollarma)
    [[ $# -ge 1 ]] || { echo "usage: $0 ollarma '<command>'" >&2; exit 2; }
    run_remote "cd ${REMOTE_ROOT}/ollarma && $*"
    ;;
  smoke)
    run_remote 'echo HOST=$(hostname); which daytona python3; daytona list 2>&1 | head -3; python3 --version'
    ;;
  sglang)
    run_remote "cd ${REMOTE_ROOT}/hydradg && python3 scripts/newinml_gpu_sglang_daisy_execute.py"
    ;;
  sglang-bg)
    log="/tmp/hydradg_sglang_orchestrator.log"
    run_remote "cd ${REMOTE_ROOT}/hydradg && nohup python3 scripts/newinml_gpu_sglang_daisy_execute.py > ${log} 2>&1 & echo pid=\$! log=${log}"
    ;;
  sglang-log)
    run_remote "tail -50 /tmp/hydradg_sglang_orchestrator.log 2>/dev/null || echo 'no log yet'"
    ;;
  *)
    echo "unknown subcommand: $cmd" >&2
    usage
    exit 2
    ;;
esac
