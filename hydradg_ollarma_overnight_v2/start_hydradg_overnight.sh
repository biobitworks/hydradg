#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-magicstudiobox}"
PKG="${PKG:-/Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7}"
RUN_FAMILY="${RUN_FAMILY:-VITHIA-OVERNIGHT-01}"
CUTOFF="${CUTOFF:-08:00}"
HERE="$(cd "$(dirname "$0")" && pwd)"

bar() {
  local pct="$1" stage="$2"
  local width=24 filled empty
  filled=$((pct * width / 100))
  empty=$((width - filled))
  printf '['
  printf '%*s' "$filled" '' | tr ' ' '#'
  printf '%*s' "$empty" '' | tr ' ' '-'
  printf '] %3s%% stage=%s\n' "$pct" "$stage"
}

bar 5 "SSH_CONNECT"
ssh -o BatchMode=yes -o ConnectTimeout=10 "$REMOTE_HOST" 'printf "SSH_OK host=%s\n" "$(hostname)"'

bar 10 "REMOTE_PREFLIGHT"
ssh "$REMOTE_HOST" "PKG='$PKG' bash -s" <<'REMOTE'
set -u
FAIL=0

echo "--- package ---"
if [ -d "$PKG" ]; then
  echo "PACKAGE_OK=$PKG"
else
  echo "PACKAGE_MISSING=$PKG"
  FAIL=1
fi

echo "--- vithia core ---"
CORE="$PKG/scripts/vithia_divergence_core.py"
if [ -f "$CORE" ]; then
  echo "VITHIA_CORE_OK=$CORE"
  shasum -a 256 "$CORE"
else
  echo "VITHIA_CORE_MISSING=$CORE"
  FAIL=1
fi

echo "--- ollarma localhost ---"
TMP="/tmp/hydradg_ollarma_health.$$"
HTTP_CODE="$(curl -sS -o "$TMP" -w '%{http_code}' http://127.0.0.1:8484/health 2>/dev/null || printf '000')"
echo "OLLARMA_HTTP_CODE=$HTTP_CODE"
if [ -s "$TMP" ]; then
  cat "$TMP"
  echo
fi
rm -f "$TMP"
# Do not require HTTP 2xx here: the Ollarma client intentionally accepts a
# valid JSON body from non-2xx degraded health responses.
if [ "$HTTP_CODE" = "000" ]; then
  echo "OLLARMA_UNREACHABLE"
  FAIL=1
else
  echo "OLLARMA_REACHABLE"
fi

echo "--- ollama localhost ---"
TMP="/tmp/hydradg_ollama_tags.$$"
OLLAMA_CODE="$(curl -sS -o "$TMP" -w '%{http_code}' http://127.0.0.1:11434/api/tags 2>/dev/null || printf '000')"
echo "OLLAMA_HTTP_CODE=$OLLAMA_CODE"
if [ -s "$TMP" ]; then
  /usr/bin/python3 - "$TMP" <<'PY' 2>/dev/null || cat "$TMP"
import json, sys
with open(sys.argv[1]) as f:
    x=json.load(f)
print("OLLAMA_MODELS=" + ",".join(sorted(m.get("name","") for m in x.get("models",[]) if m.get("name"))))
PY
fi
rm -f "$TMP"
if [ "$OLLAMA_CODE" = "000" ]; then
  echo "OLLAMA_UNREACHABLE"
  FAIL=1
else
  echo "OLLAMA_REACHABLE"
fi

echo "--- ollarma client candidates ---"
for p in \
  /Users/byron/projects/active/ollarma/clients/ollarma_client.py \
  /Users/byron/projects/ollarma/clients/ollarma_client.py
do
  [ -f "$p" ] && echo "OLLARMA_CLIENT_FOUND=$p"
done

exit "$FAIL"
REMOTE

bar 25 "UPLOAD_ORCHESTRATOR"
scp -q "$HERE/hydradg_overnight_daisy.py" "$REMOTE_HOST:$PKG/scripts/hydradg_overnight_daisy.py"

bar 45 "REMOTE_DRY_RUN"
ssh "$REMOTE_HOST" "
set -e
cd '$PKG'
export OLLARMA_URL='http://127.0.0.1:8484'
export OLLAMA_URL='http://127.0.0.1:11434'
/Users/byron/fco-venv/bin/python3 scripts/hydradg_overnight_daisy.py \
  --run-family '$RUN_FAMILY' \
  --cutoff-local '$CUTOFF' \
  --resume \
  --dry-run
"

bar 65 "START_BACKGROUND_QUEUE"
ssh "$REMOTE_HOST" "
set -eu
cd '$PKG'
OUT='eval/vithia_overnight/$RUN_FAMILY'
mkdir -p \"\$OUT\"

if [ -f \"\$OUT/launcher_pid.txt\" ]; then
  OLD=\$(cat \"\$OUT/launcher_pid.txt\" 2>/dev/null || true)
  if [ -n \"\$OLD\" ] && kill -0 \"\$OLD\" 2>/dev/null; then
    echo \"STOP: overnight queue already running pid=\$OLD\"
    exit 2
  fi
fi

RUNNER=(/Users/byron/fco-venv/bin/python3 scripts/hydradg_overnight_daisy.py --run-family '$RUN_FAMILY' --cutoff-local '$CUTOFF' --resume)

if command -v caffeinate >/dev/null 2>&1; then
  nohup env OLLARMA_URL=http://127.0.0.1:8484 OLLAMA_URL=http://127.0.0.1:11434 \
    caffeinate -s \"\${RUNNER[@]}\" >\"\$OUT/launcher.log\" 2>&1 </dev/null &
else
  nohup env OLLARMA_URL=http://127.0.0.1:8484 OLLAMA_URL=http://127.0.0.1:11434 \
    \"\${RUNNER[@]}\" >\"\$OUT/launcher.log\" 2>&1 </dev/null &
fi

PID=\$!
echo \"\$PID\" > \"\$OUT/launcher_pid.txt\"
echo \"STARTED pid=\$PID\"
"

bar 85 "VERIFY_STARTED"
ssh "$REMOTE_HOST" "
PKG='$PKG'
OUT=\"\$PKG/eval/vithia_overnight/$RUN_FAMILY\"
sleep 3
PID=\$(cat \"\$OUT/launcher_pid.txt\" 2>/dev/null || true)
echo \"PID=\${PID:-NONE}\"
if [ -n \"\$PID\" ]; then
  ps -p \"\$PID\" -o pid=,etime=,state=,command= || true
fi
echo '--- status ---'
cat \"\$OUT/status.json\" 2>/dev/null || echo NO_STATUS_YET
echo '--- log ---'
tail -30 \"\$OUT/launcher.log\" 2>/dev/null || true
"

bar 100 "DAISY_QUEUE_LAUNCHED"
echo
echo "Monitor:"
echo "ssh $REMOTE_HOST 'cd $PKG && OUT=eval/vithia_overnight/$RUN_FAMILY; cat \$OUT/status.json; tail -40 \$OUT/launcher.log'"
