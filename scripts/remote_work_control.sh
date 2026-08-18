#!/usr/bin/env bash
set -euo pipefail

# Final remote-work controller. Run on magicPRObox only.
#
# Usage:
#   bash scripts/remote_work_control.sh up
#   bash scripts/remote_work_control.sh status
#   bash scripts/remote_work_control.sh down
#
# Scope:
# - verifies GitHub auth on both Macs
# - verifies/safely fast-forwards LessWrong main on both Macs to GitHub main
# - audits HydraDG on both Macs without rewriting active work
# - verifies HydraDB pin in HydraDG on both Macs
# - establishes one SSH master with local forwards for Ollarma, Watchtower, HydraDB
# - verifies remote and tunneled service health where available
# - emits a local bounded readiness receipt with SHA-256
#
# Claim ceiling: transport, Git-head conformance, configured pin, and service-health
# checks only. This script does not claim scientific/model validation.

MODE="${1:-status}"
case "$MODE" in up|status|down) ;; *) echo "USAGE: $0 {up|status|down}"; exit 2;; esac

ROOT="/Users/byron/projects/active/hydradg"
PRO_LW="/Users/byron/projects/active/lesswrong"
STUDIO="${STUDIO_SSH:-magicstudiobox}"
STUDIO_LW="/Users/byron/projects/active/lesswrong"
STUDIO_HDG="/Users/byron/projects/active/hydradg"
LW_REMOTE="https://github.com/biobitworks/lesswrong.git"
HDG_REMOTE="https://github.com/biobitworks/hydradg.git"
SETUP_BRANCH="setup/remote-work-20260818"
HYDRADB_PIN_EXPECTED="6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219"
PIN_REL="HydraDG_DaisyTrain_v0.3.7/config/hydradb_pin.json"
SOCK="/tmp/fco-rw-${UID}.sock"
RUN_ID="REMOTE-WORK-$(date -u +%Y%m%dT%H%M%SZ)"
RECEIPT="/tmp/${RUN_ID}.json"

fail(){ echo "FAIL=$1" >&2; exit "${2:-1}"; }
section(){ printf '\n=== %s ===\n' "$1"; }
remote(){ ssh -o BatchMode=yes -o ConnectTimeout=12 "$STUDIO" "$@"; }
normalize_origin(){ printf '%s' "$1" | sed -E -e 's#^git@github\.com:##' -e 's#^https://github\.com/##' -e 's#^ssh://git@github\.com/##' -e 's#/$##' -e 's#\.git$##'; }

section "CONTROL HOST"
CN="$(scutil --get ComputerName 2>/dev/null || true)"
LH="$(scutil --get LocalHostName 2>/dev/null || true)"
HN="$(hostname 2>/dev/null || true)"
printf 'COMPUTER_NAME=%s\nLOCAL_HOST_NAME=%s\nHOSTNAME=%s\n' "$CN" "$LH" "$HN"
case "$(printf '%s %s %s' "$CN" "$LH" "$HN" | tr '[:upper:]' '[:lower:]')" in *magicprobox*) ;; *) fail RUN_ON_MAGICPROBOX_ONLY 2;; esac

if [ "$MODE" = down ]; then
  section "STOP SSH TUNNEL"
  if ssh -S "$SOCK" -O check "$STUDIO" >/dev/null 2>&1; then
    ssh -S "$SOCK" -O exit "$STUDIO" >/dev/null 2>&1 || true
    echo "REMOTE_WORK_TUNNEL=DOWN"
  else
    echo "REMOTE_WORK_TUNNEL=ALREADY_DOWN"
  fi
  exit 0
fi

for c in git gh ssh curl python3 shasum; do command -v "$c" >/dev/null 2>&1 || fail "MAGICPRO_TOOL_MISSING:$c" 3; done
gh auth status >/dev/null 2>&1 || fail MAGICPRO_GH_AUTH_MISSING 4

section "SSH / TAILSCALE TRANSPORT"
command -v tailscale >/dev/null 2>&1 || fail MAGICPRO_TAILSCALE_MISSING 5
tailscale status >/dev/null || fail MAGICPRO_TAILSCALE_NOT_READY 6
remote 'command -v tailscale >/dev/null 2>&1 && tailscale status >/dev/null && echo STUDIO_TAILSCALE=PASS' || fail STUDIO_SSH_OR_TAILSCALE_FAILED 7
IDS="$(remote 'printf "%s %s %s" "$(scutil --get ComputerName 2>/dev/null || true)" "$(scutil --get LocalHostName 2>/dev/null || true)" "$(hostname 2>/dev/null || true)"' | tr '[:upper:]' '[:lower:]')"
case "$IDS" in *magicstudiobox*) echo "STUDIO_IDENTITY=PASS" ;; *) fail REMOTE_NOT_MAGICSTUDIO 8;; esac

section "GITHUB AUTH BOTH MACHINES"
echo "MAGICPRO_GH_AUTH=PASS"
remote 'if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi; gh auth status >/dev/null 2>&1 && echo MAGICSTUDIO_GH_AUTH=PASS' || fail MAGICSTUDIO_GH_AUTH_MISSING 9

sync_lesswrong_local(){
  [ -d "$PRO_LW/.git" ] || fail MAGICPRO_LESSWRONG_NOT_GIT 10
  ORIGIN="$(git -C "$PRO_LW" remote get-url origin 2>/dev/null || true)"
  [ "$(normalize_origin "$ORIGIN")" = "biobitworks/lesswrong" ] || fail "MAGICPRO_LESSWRONG_BAD_ORIGIN:$ORIGIN" 11
  git -C "$PRO_LW" fetch origin --prune --quiet
  [ -z "$(git -C "$PRO_LW" status --porcelain)" ] || fail MAGICPRO_LESSWRONG_DIRTY 12
  HEAD="$(git -C "$PRO_LW" rev-parse HEAD)"
  REM="$(git -C "$PRO_LW" rev-parse origin/main)"
  if [ "$HEAD" != "$REM" ]; then
    if git -C "$PRO_LW" merge-base --is-ancestor HEAD origin/main; then
      [ "$MODE" = up ] || fail MAGICPRO_LESSWRONG_BEHIND 13
      git -C "$PRO_LW" pull --ff-only origin main >/dev/null
      HEAD="$(git -C "$PRO_LW" rev-parse HEAD)"
    elif git -C "$PRO_LW" merge-base --is-ancestor origin/main HEAD; then
      fail MAGICPRO_LESSWRONG_LOCAL_AHEAD_NOT_PUSHED 14
    else
      fail MAGICPRO_LESSWRONG_DIVERGED 15
    fi
  fi
  printf '%s' "$HEAD"
}

section "LESSWRONG THREE-WAY CONFORMANCE"
PRO_LW_HEAD="$(sync_lesswrong_local)"
STUDIO_LW_HEAD="$(ssh -o BatchMode=yes -o ConnectTimeout=12 "$STUDIO" bash -s -- "$MODE" <<'REMOTE_LW'
set -euo pipefail
MODE="$1"
P="/Users/byron/projects/active/lesswrong"
[ -d "$P/.git" ] || { echo FAIL=STUDIO_LESSWRONG_NOT_GIT >&2; exit 20; }
O="$(git -C "$P" remote get-url origin 2>/dev/null || true)"
case "$O" in https://github.com/biobitworks/lesswrong.git|git@github.com:biobitworks/lesswrong.git) ;; *) echo "FAIL=STUDIO_LESSWRONG_BAD_ORIGIN:$O" >&2; exit 21;; esac
git -C "$P" fetch origin --prune --quiet
[ -z "$(git -C "$P" status --porcelain)" ] || { echo FAIL=STUDIO_LESSWRONG_DIRTY >&2; exit 22; }
H="$(git -C "$P" rev-parse HEAD)"; R="$(git -C "$P" rev-parse origin/main)"
if [ "$H" != "$R" ]; then
  if git -C "$P" merge-base --is-ancestor HEAD origin/main; then
    [ "$MODE" = up ] || { echo FAIL=STUDIO_LESSWRONG_BEHIND >&2; exit 23; }
    git -C "$P" pull --ff-only origin main >/dev/null
    H="$(git -C "$P" rev-parse HEAD)"
  elif git -C "$P" merge-base --is-ancestor origin/main HEAD; then
    echo FAIL=STUDIO_LESSWRONG_LOCAL_AHEAD_NOT_PUSHED >&2; exit 24
  else
    echo FAIL=STUDIO_LESSWRONG_DIVERGED >&2; exit 25
  fi
fi
printf '%s' "$H"
REMOTE_LW
)" || fail STUDIO_LESSWRONG_SYNC_FAILED 16
GITHUB_LW_HEAD="$(git ls-remote "$LW_REMOTE" refs/heads/main | awk '{print $1}')"
[ -n "$GITHUB_LW_HEAD" ] || fail GITHUB_LESSWRONG_MAIN_MISSING 17
printf 'MAGICPRO_LESSWRONG=%s\nGITHUB_LESSWRONG=%s\nMAGICSTUDIO_LESSWRONG=%s\n' "$PRO_LW_HEAD" "$GITHUB_LW_HEAD" "$STUDIO_LW_HEAD"
[ "$PRO_LW_HEAD" = "$GITHUB_LW_HEAD" ] || fail MAGICPRO_LESSWRONG_NOT_GITHUB_MAIN 18
[ "$STUDIO_LW_HEAD" = "$GITHUB_LW_HEAD" ] || fail MAGICSTUDIO_LESSWRONG_NOT_GITHUB_MAIN 19
echo "LESSWRONG_TWO_MACHINE=PASS"

section "HYDRADG AUDIT"
[ -d "$ROOT/.git" ] || fail MAGICPRO_HYDRADG_NOT_GIT 30
PORIGIN="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
[ "$(normalize_origin "$PORIGIN")" = "biobitworks/hydradg" ] || fail "MAGICPRO_HYDRADG_BAD_ORIGIN:$PORIGIN" 31
git -C "$ROOT" fetch origin --prune --quiet
PRO_HDG_HEAD="$(git -C "$ROOT" rev-parse HEAD)"
PRO_HDG_BRANCH="$(git -C "$ROOT" branch --show-current || true)"
PRO_HDG_DIRTY="$(git -C "$ROOT" status --porcelain | wc -l | tr -d ' ')"
printf 'MAGICPRO_HYDRADG_HEAD=%s\nMAGICPRO_HYDRADG_BRANCH=%s\nMAGICPRO_HYDRADG_DIRTY_COUNT=%s\n' "$PRO_HDG_HEAD" "$PRO_HDG_BRANCH" "$PRO_HDG_DIRTY"

STUDIO_HDG_INFO="$(remote 'bash -s' <<'REMOTE_HDG'
set -euo pipefail
P="/Users/byron/projects/active/hydradg"
[ -d "$P/.git" ] || { echo FAIL=STUDIO_HYDRADG_NOT_GIT; exit 30; }
O="$(git -C "$P" remote get-url origin 2>/dev/null || true)"
case "$O" in https://github.com/biobitworks/hydradg.git|git@github.com:biobitworks/hydradg.git) ;; *) echo "FAIL=STUDIO_HYDRADG_BAD_ORIGIN:$O"; exit 31;; esac
git -C "$P" fetch origin --prune --quiet
printf 'STUDIO_HYDRADG_HEAD=%s\nSTUDIO_HYDRADG_BRANCH=%s\nSTUDIO_HYDRADG_DIRTY_COUNT=%s\n' "$(git -C "$P" rev-parse HEAD)" "$(git -C "$P" branch --show-current || true)" "$(git -C "$P" status --porcelain | wc -l | tr -d ' ')"
REMOTE_HDG
)" || fail STUDIO_HYDRADG_AUDIT_FAILED 32
printf '%s\n' "$STUDIO_HDG_INFO"
SETUP_REMOTE="$(git -C "$ROOT" rev-parse "origin/$SETUP_BRANCH" 2>/dev/null || true)"
printf 'HYDRADG_SETUP_REMOTE=%s\n' "$SETUP_REMOTE"

section "HYDRADB PIN BOTH MACHINES"
PIN_FILE="$ROOT/$PIN_REL"
[ -f "$PIN_FILE" ] || fail MAGICPRO_HYDRADB_PIN_MISSING 40
PRO_PIN="$(python3 - "$PIN_FILE" <<'PY'
import json,sys
with open(sys.argv[1]) as f: print(json.load(f).get('commit_sha',''))
PY
)"
[ "$PRO_PIN" = "$HYDRADB_PIN_EXPECTED" ] || fail "MAGICPRO_HYDRADB_PIN_MISMATCH:$PRO_PIN" 41
STUDIO_PIN="$(remote "python3 - '$STUDIO_HDG/$PIN_REL'" <<'PY'
import json,sys
with open(sys.argv[1]) as f: print(json.load(f).get('commit_sha',''))
PY
)" || fail STUDIO_HYDRADB_PIN_READ_FAILED 42
[ "$STUDIO_PIN" = "$HYDRADB_PIN_EXPECTED" ] || fail "STUDIO_HYDRADB_PIN_MISMATCH:$STUDIO_PIN" 43
printf 'MAGICPRO_HYDRADB_PIN=%s\nMAGICSTUDIO_HYDRADB_PIN=%s\n' "$PRO_PIN" "$STUDIO_PIN"
echo "HYDRADB_PIN_TWO_MACHINE=PASS"

if [ "$MODE" = up ]; then
  section "SSH MASTER + FORWARDS"
  if ssh -S "$SOCK" -O check "$STUDIO" >/dev/null 2>&1; then
    echo "SSH_MASTER=ALREADY_UP"
  else
    rm -f "$SOCK"
    ssh -M -S "$SOCK" -fNT \
      -o ExitOnForwardFailure=yes \
      -o ServerAliveInterval=30 \
      -o ServerAliveCountMax=3 \
      -L 18484:127.0.0.1:8484 \
      -L 18000:127.0.0.1:8000 \
      -L 18443:127.0.0.1:8443 \
      -L 17687:127.0.0.1:7687 \
      -L 19090:127.0.0.1:9090 \
      "$STUDIO"
    echo "SSH_MASTER=STARTED"
  fi
fi

section "SERVICE HEALTH"
if [ "$MODE" = status ] && ! ssh -S "$SOCK" -O check "$STUDIO" >/dev/null 2>&1; then
  echo "SSH_MASTER=DOWN"
  echo "RUN=bash scripts/remote_work_control.sh up"
fi

check_remote_http(){ local name="$1" url="$2"; if remote "curl -fsS '$url' >/dev/null"; then echo "$name=UP"; return 0; else echo "$name=DOWN"; return 1; fi; }
check_remote_tcp(){ local name="$1" port="$2"; if remote "python3 - '$port'" <<'PY'
import socket,sys
s=socket.socket(); s.settimeout(2)
try: s.connect(('127.0.0.1',int(sys.argv[1]))); print('ok')
finally: s.close()
PY
then echo "$name=UP"; return 0; else echo "$name=DOWN"; return 1; fi; }

SERVICE_FAIL=0
check_remote_http STUDIO_OLLARMA http://127.0.0.1:8484/health || SERVICE_FAIL=1
check_remote_http STUDIO_WATCHTOWER http://127.0.0.1:8000/ || SERVICE_FAIL=1
check_remote_http STUDIO_HYDRADB_ADMIN http://127.0.0.1:9090/readyz || SERVICE_FAIL=1
check_remote_tcp STUDIO_HYDRADB_HTTP 8443 || SERVICE_FAIL=1
check_remote_tcp STUDIO_HYDRADB_BOLT 7687 || SERVICE_FAIL=1

TUNNEL_UP=NO
if ssh -S "$SOCK" -O check "$STUDIO" >/dev/null 2>&1; then TUNNEL_UP=YES; fi
if [ "$TUNNEL_UP" = YES ]; then
  curl -fsS http://127.0.0.1:18484/health >/dev/null && echo PRO_TUNNEL_OLLARMA=UP || { echo PRO_TUNNEL_OLLARMA=DOWN; SERVICE_FAIL=1; }
  curl -fsS http://127.0.0.1:18000/ >/dev/null && echo PRO_TUNNEL_WATCHTOWER=UP || { echo PRO_TUNNEL_WATCHTOWER=DOWN; SERVICE_FAIL=1; }
  curl -fsS http://127.0.0.1:19090/readyz >/dev/null && echo PRO_TUNNEL_HYDRADB_ADMIN=UP || { echo PRO_TUNNEL_HYDRADB_ADMIN=DOWN; SERVICE_FAIL=1; }
  python3 - <<'PY' && echo PRO_TUNNEL_HYDRADB_HTTP=UP || { echo PRO_TUNNEL_HYDRADB_HTTP=DOWN; SERVICE_FAIL=1; }
import socket
s=socket.create_connection(('127.0.0.1',18443),2); s.close()
PY
  python3 - <<'PY' && echo PRO_TUNNEL_HYDRADB_BOLT=UP || { echo PRO_TUNNEL_HYDRADB_BOLT=DOWN; SERVICE_FAIL=1; }
import socket
s=socket.create_connection(('127.0.0.1',17687),2); s.close()
PY
fi

section "READINESS RECEIPT"
READY=YES
[ "$TUNNEL_UP" = YES ] || READY=NO
[ "$SERVICE_FAIL" -eq 0 ] || READY=NO
cat > "$RECEIPT" <<EOF
{
  "schema": "fcofcg.remote_work_readiness.v1",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "control_host": "magicPRObox",
  "execution_host": "magicSTUDIObox",
  "lesswrong_main_sha": "$GITHUB_LW_HEAD",
  "hydradg_magicpro_head": "$PRO_HDG_HEAD",
  "hydradg_setup_remote": "$SETUP_REMOTE",
  "hydradb_pin": "$PRO_PIN",
  "ssh_tunnel_up": "$TUNNEL_UP",
  "core_services_healthy": "$([ "$SERVICE_FAIL" -eq 0 ] && echo YES || echo NO)",
  "remote_work_ready": "$READY",
  "claim_ceiling": "TRANSPORT_GIT_HEAD_CONFORMANCE_CONFIGURED_HYDRADB_PIN_AND_SERVICE_HEALTH_ONLY",
  "signature_state": "NOT_SIGNED",
  "merkle_state": "NOT_MERKLE_COMMITTED"
}
EOF
RSH="$(shasum -a 256 "$RECEIPT" | awk '{print $1}')"
printf 'RECEIPT=%s\nRECEIPT_SHA256=%s\n' "$RECEIPT" "$RSH"

echo
echo "REMOTE_WORK_READY=$READY"
echo "LESSWRONG_TWO_MACHINE=PASS"
echo "HYDRADB_PIN_TWO_MACHINE=PASS"
echo "OLLARMA_URL=http://127.0.0.1:18484"
echo "WATCHTOWER_URL=http://127.0.0.1:18000"
echo "HYDRADB_HTTP=http://127.0.0.1:18443"
echo "HYDRADB_BOLT=bolt://127.0.0.1:17687"
echo "HYDRADB_ADMIN=http://127.0.0.1:19090"

[ "$READY" = YES ] || exit 50
