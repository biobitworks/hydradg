#!/usr/bin/env bash
set -euo pipefail

BASE="/Users/byron/projects/active/hydradg"
HIST="$BASE/HydraDG_HackHydra_Plan_v0.2.7"
PKG="$BASE/HydraDG_DaisyTrain_v0.3.7"
LAUNCHDIR="$BASE/hydradg_ollarma_overnight"
REMOTE="${REMOTE:-magicstudiobox}"
CORE_LOCAL="$HIST/scripts/vithia_divergence_core.py"
CORE_REMOTE="$PKG/scripts/vithia_divergence_core.py"
VENV_REMOTE="$PKG/.venv-hydradg"
RUN_FAMILY="${RUN_FAMILY:-VITHIA-OVERNIGHT-01}"

bar () {
  pct="$1"; stage="$2"
  width=24
  filled=$((pct * width / 100))
  empty=$((width - filled))
  printf '['
  printf '%*s' "$filled" '' | tr ' ' '#'
  printf '%*s' "$empty" '' | tr ' ' '-'
  printf '] %3s%% stage=%s\n' "$pct" "$stage"
}

bar 5 "VERIFY_STAGED_CORE"
test -f "$CORE_LOCAL"
LOCAL_CORE_SHA="$(shasum -a 256 "$CORE_LOCAL" | awk '{print $1}')"
REMOTE_CORE_SHA="$(ssh "$REMOTE" "shasum -a 256 '$CORE_REMOTE' 2>/dev/null | awk '{print \$1}'")"

echo "LOCAL_CORE_SHA=$LOCAL_CORE_SHA"
echo "REMOTE_CORE_SHA=$REMOTE_CORE_SHA"
if [ -z "$REMOTE_CORE_SHA" ] || [ "$LOCAL_CORE_SHA" != "$REMOTE_CORE_SHA" ]; then
  echo "FAIL: staged Vithia core missing or hash mismatch"
  exit 10
fi
echo "CORE_HASH_MATCH=PASS"

bar 15 "DISCOVER_REFERENCE_ENV"
LOCAL_PY=""
if [ -n "${CONDA_PREFIX:-}" ] && [ -x "$CONDA_PREFIX/bin/python" ]; then
  if "$CONDA_PREFIX/bin/python" -c 'import torch,transformers,numpy' >/dev/null 2>&1; then
    LOCAL_PY="$CONDA_PREFIX/bin/python"
  fi
fi

if [ -z "$LOCAL_PY" ]; then
  for C in \
    "$HIST/.venv/bin/python" \
    "$HIST/.venv-hydradg/bin/python" \
    /Users/byron/fco-venv/bin/python3 \
    /opt/homebrew/bin/python3 \
    /usr/bin/python3
  do
    if [ -x "$C" ] && "$C" -c 'import torch,transformers,numpy' >/dev/null 2>&1; then
      LOCAL_PY="$C"
      break
    fi
  done
fi

if [ -z "$LOCAL_PY" ]; then
  echo "FAIL: no magicPRObox Python with torch + transformers + numpy was found."
  echo "This script will not invent a Transformers version."
  exit 20
fi

REF_JSON="$("$LOCAL_PY" - <<'PY'
import json, platform, torch, transformers, numpy
print(json.dumps({
    "python": platform.python_version(),
    "torch": torch.__version__,
    "transformers": transformers.__version__,
    "numpy": numpy.__version__,
}, sort_keys=True, separators=(",", ":")))
PY
)"
TF_VER="$("$LOCAL_PY" -c 'import transformers; print(transformers.__version__)')"

echo "REFERENCE_PYTHON=$LOCAL_PY"
echo "REFERENCE_ENV=$REF_JSON"
echo "TRANSFORMERS_PIN=$TF_VER"

bar 25 "CREATE_REMOTE_ISOLATED_VENV"
ssh "$REMOTE" "PKG='$PKG' VENV_REMOTE='$VENV_REMOTE' TF_VER='$TF_VER' bash -s" <<'REMOTE_SETUP'
set -euo pipefail

BASEPY="/Users/byron/fco-venv/bin/python3"
test -x "$BASEPY"

if [ ! -x "$VENV_REMOTE/bin/python" ]; then
  "$BASEPY" -m venv --system-site-packages "$VENV_REMOTE"
fi

"$VENV_REMOTE/bin/python" -m pip install \
  "transformers==$TF_VER"

"$VENV_REMOTE/bin/python" - <<'PY'
import json, platform, torch, transformers, numpy
print("REMOTE_IMPORT_GATE=PASS")
print(json.dumps({
    "python": platform.python_version(),
    "torch": torch.__version__,
    "transformers": transformers.__version__,
    "numpy": numpy.__version__,
}, sort_keys=True, separators=(",", ":")))
PY
REMOTE_SETUP

bar 45 "WRITE_RUNTIME_RECEIPT"
ssh "$REMOTE" "PKG='$PKG' VENV_REMOTE='$VENV_REMOTE' CORE_REMOTE='$CORE_REMOTE' RUN_FAMILY='$RUN_FAMILY' bash -s" <<'REMOTE_RECEIPT'
set -euo pipefail
OUT="$PKG/eval/vithia_runtime"
mkdir -p "$OUT"

"$VENV_REMOTE/bin/python" - "$CORE_REMOTE" "$VENV_REMOTE" > "$OUT/runtime_snapshot.json" <<'PY'
import hashlib, json, platform, sys
from pathlib import Path
import torch, transformers, numpy

core = Path(sys.argv[1])
venv = sys.argv[2]
obj = {
    "schema": "hydradg.vithia_runtime_snapshot.v1",
    "host": platform.node(),
    "platform": platform.platform(),
    "python": platform.python_version(),
    "torch": torch.__version__,
    "transformers": transformers.__version__,
    "numpy": numpy.__version__,
    "venv": venv,
    "core_path": str(core),
    "core_sha256": hashlib.sha256(core.read_bytes()).hexdigest(),
    "claim_boundary": "Execution-environment snapshot only; not training reproduction or scientific validation."
}
print(json.dumps(obj, sort_keys=True, separators=(",", ":")))
PY

cat "$OUT/runtime_snapshot.json"
shasum -a 256 "$OUT/runtime_snapshot.json"
REMOTE_RECEIPT

bar 55 "VITHIA_CLI_GATE"
ssh "$REMOTE" "
  cd '$PKG'
  '$VENV_REMOTE/bin/python' scripts/vithia_divergence_core.py --help | head -100
"

bar 65 "VERIFY_OLLARMA"
ssh "$REMOTE" '
set -e
echo "OLLARMA:"
curl -sS http://127.0.0.1:8484/health | /usr/bin/python3 -c "import json,sys; x=json.load(sys.stdin); print(x.get(\"status\"), x.get(\"helper_chat\",{}).get(\"effective_model\"))"
echo "OLLAMA_MODELS:"
curl -sS http://127.0.0.1:11434/api/tags | /usr/bin/python3 -c "import json,sys; x=json.load(sys.stdin); print(\",\".join(sorted(m.get(\"name\",\"\") for m in x.get(\"models\",[]) if m.get(\"name\"))))"
'

bar 75 "LAUNCH_DAISY"
cd "$LAUNCHDIR"
chmod +x hydradg_overnight_daisy.py start_hydradg_overnight.sh
RUN_FAMILY="$RUN_FAMILY" ./start_hydradg_overnight.sh

bar 95 "VERIFY_QUEUE"
ssh "$REMOTE" "PKG='$PKG' RUN_FAMILY='$RUN_FAMILY' bash -s" <<'REMOTE_VERIFY'
set -u
OUT="$PKG/eval/vithia_overnight/$RUN_FAMILY"
sleep 3

echo "=== STATUS ==="
cat "$OUT/status.json" 2>/dev/null || echo "NO_STATUS_YET"

echo
echo "=== PROCESS ==="
PID="$(cat "$OUT/launcher_pid.txt" 2>/dev/null || true)"
echo "PID=${PID:-NONE}"
if [ -n "$PID" ]; then
  ps -p "$PID" -o pid=,ppid=,etime=,state=,command= || true
fi

echo
echo "=== LOG ==="
tail -60 "$OUT/launcher.log" 2>/dev/null || true
REMOTE_VERIFY

bar 100 "DONE"
echo "Do not start a second queue if status shows RUNNING or a live launcher PID."
