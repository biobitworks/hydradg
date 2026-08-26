#!/bin/bash
# Sample HydraDG studio-test health for a bounded observation window.
set -euo pipefail
RUNTIME=/Volumes/magicBLACKbox/hydradg/services/hydradg-test
SAMPLES=${1:-12}
SLEEP=${2:-5}
OUT="${RUNTIME}/receipts/observe_$(date -u +%Y%m%dT%H%M%SZ).tsv"
mkdir -p "${RUNTIME}/receipts"
printf 'ts\tlocal\tts\tpid\tdeployed_sha\tlock_busy\tdeploy_py\n' >"$OUT"
fail=0
for i in $(seq 1 "$SAMPLES"); do
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local_code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:3000/ || echo 000)
  ts_code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 https://magicstudiobox.tail0cf9bb.ts.net/ || echo 000)
  pid=$(lsof -nP -iTCP:3000 -sTCP:LISTEN -t 2>/dev/null | head -1 || echo NONE)
  deployed=$(cat "$RUNTIME/state/deployed_sha" 2>/dev/null | tr -d '\n' || echo NONE)
  if [[ -f "$RUNTIME/state/deploy.lock" ]] && lsof "$RUNTIME/state/deploy.lock" >/dev/null 2>&1; then
    lock=HELD
  else
    lock=FREE
  fi
  dep=0
  if pgrep -af 'ops/studio-test/deploy.py' >/tmp/hydradg_observe_deployers.txt 2>/dev/null; then
    dep=$(grep -cvE 'pgrep|observe_health' /tmp/hydradg_observe_deployers.txt || true)
  fi
  line=$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' "$ts" "$local_code" "$ts_code" "$pid" "$deployed" "$lock" "$dep")
  printf '%s\n' "$line" | tee -a "$OUT" >/dev/null
  printf '%s\n' "$line"
  if [[ "$local_code" != "200" || "$ts_code" != "200" ]]; then fail=1; fi
  if [[ "$pid" == "NONE" ]]; then fail=1; fi
  sleep "$SLEEP"
done
echo "OBSERVE_FILE=$OUT"
# PID churn check
pids=$(awk 'NR>1 {print $4}' "$OUT" | sort -u | tr '\n' ' ')
echo "LISTENER_PIDS=$pids"
uniq_pids=$(awk 'NR>1 {print $4}' "$OUT" | sort -u | wc -l | tr -d ' ')
if [[ "$fail" -eq 0 && "$uniq_pids" -eq 1 ]]; then
  echo "SERVER_FLAP=NO"
  exit 0
fi
echo "SERVER_FLAP=YES"
exit 1
