#!/usr/bin/env bash
# Gum Doctor → Studio piecewise E2E (CFOS + SGLang graph-break)
# Paste from magicPRObox:
#   bash ~/projects/active/hydradg/scripts/gum_studio_piecewise_e2e.sh
#
# Or foreground log:
#   bash ~/projects/active/hydradg/scripts/gum_studio_piecewise_e2e.sh 2>&1 | tee /tmp/gum_studio_e2e.log
set -euo pipefail

STUDIO_HOST="${STUDIO_SSH_HOST:-magicstudiobox-ip}"
HYDRADG_PRO="${HYDRADG_PRO:-$HOME/projects/active/hydradg}"
LOG="${GUM_STUDIO_E2E_LOG:-/tmp/gum_studio_piecewise_e2e.log}"

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$LOG"; }

run_pro_cfos_controller() {
  if [[ ! -d "$HYDRADG_PRO/apps/hydradg-web" ]]; then
    log "PRO CFOS skip: hydradg not at $HYDRADG_PRO"
    return 0
  fi
  log "PRO lane: CFOS-HL-001 deterministic fixtures (controller)"
  (
    cd "$HYDRADG_PRO/apps/hydradg-web"
    npx tsx scripts/cfos_hl001_bounded.mts
  ) | tee -a "$LOG"
}

run_studio_remote() {
  log "STUDIO lane: gum doctor → CFOS → SGLang (via SSH $STUDIO_HOST)"
  ssh -o BatchMode=yes "$STUDIO_HOST" 'bash -s' <<'REMOTE' | tee -a "$LOG"
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
ROOT="$HOME/projects/active/hydradg"
EXEC="$ROOT/eval/newinml_final_daisy_20260829/execution"
GPU="$EXEC/gpu_sglang_terminal"
LOG="/tmp/gum_studio_piecewise_e2e.studio.log"
mkdir -p "$GPU"

log() { printf '[studio %s] %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }

fix_keys_env() {
  local f="$HOME/.config/ai-keys/keys.env"
  [[ -f "$f" ]] || { log "keys.env missing"; return 0; }
  if zsh -n "$f" 2>/dev/null; then
    log "keys.env syntax OK"
    return 0
  fi
  cp "$f" "${f}.bak-$(date +%Y%m%dT%H%M%S)"
  perl -i -pe '
    s/^export (BAND_\w+=)<FILL_ME>/# export $1<FILL_ME>/;
    s/^export (BAND_(ACCESS_TOKEN|REFRESH_TOKEN)=)<FILL_AFTER_OAUTH>/# export $1<FILL_AFTER_OAUTH>/;
  ' "$f"
  zsh -n "$f"
  log "keys.env repaired (commented BAND placeholders)"
}

load_keys() {
  set -a
  # shellcheck source=/dev/null
  source "$HOME/.config/ai-keys/keys.env"
  set +a
}

sync_daytona_sandbox() {
  python3 - <<'PY'
import json, re, subprocess
from pathlib import Path

gpu = Path("eval/newinml_final_daisy_20260829/execution/gpu_sglang_terminal")
state_path = gpu / "ORCHESTRATOR_STATE.json"

def daytona_started_id() -> str | None:
    p = subprocess.run(
        ["/opt/homebrew/bin/daytona", "list"],
        capture_output=True, text=True, timeout=60,
    )
    if p.returncode != 0:
        return None
    for line in p.stdout.splitlines():
        if "STARTED" in line:
            m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", line)
            if m:
                return m.group(1)
    return None

sid = daytona_started_id()
state = {"provider": None, "sandbox_id": None, "stages": {"D0": "PASS"}}
if state_path.is_file():
    try:
        state = json.loads(state_path.read_text())
    except json.JSONDecodeError:
        pass
if sid:
    state["provider"] = "daytona"
    state["sandbox_id"] = sid
    state["stages"] = {"D0": "PASS", "D1": "PASS", "D2": "PASS"}
    print(f"synced sandbox_id={sid}")
else:
    state["stages"] = {"D0": "PASS"}
    print("no STARTED daytona sandbox; orchestrator will provision")
gpu.mkdir(parents=True, exist_ok=True)
state_path.write_text(json.dumps(state, indent=2) + "\n")
PY
}

cd "$ROOT"
fix_keys_env
load_keys

log "HOST=$(hostname) daytona=$(command -v daytona) python=$(command -v python3)"

log "=== Gum Doctor v2 (--repair) ==="
"$ROOT/scripts/gum_ai_stack_doctor_v2.zsh" --repair

log "=== CFOS-HL-001 on Studio ==="
if [[ -d "$ROOT/apps/hydradg-web" ]]; then
  CFOS="$HOME/projects/active/cloudflare-os"
  [[ -d "$CFOS" ]] || CFOS="$HOME/projects/external/cloudflare-os"
  if [[ -d "$CFOS" ]]; then
    code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8787/ || echo 000)
    if [[ "$code" != 200 && "$code" != 302 ]]; then
      log "starting Cloudflare OS at :8787"
      (cd "$CFOS" && nohup pnpm run-local >/tmp/cfos-run-local.log 2>&1 &)
      for _ in $(seq 1 30); do
        sleep 2
        code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8787/ || echo 000)
        [[ "$code" == 200 || "$code" == 302 ]] && break
      done
    fi
    (cd "$ROOT/apps/hydradg-web" && npx tsx scripts/cfos_hl001_bounded.mts)
  else
    log "CFOS checkout missing — skipping bounded canary"
  fi
fi

log "=== SGLANG-HL-001 (Daytona GPU) ==="
sync_daytona_sandbox
python3 "$ROOT/scripts/newinml_gpu_sglang_daisy_execute.py"

log "=== Studio receipts ==="
echo "gum:    $EXEC/lane0_gum/GUM_DOCTOR_V2_RECEIPT.json"
echo "cfos:   $EXEC/lane1_cfos/CFOS_HL001_EXECUTION_RECEIPT.json"
echo "sglang: $GPU/FINAL_GPU_SGLANG_CLOSEOUT.json"
REMOTE
}

: >"$LOG"
log "Gum Studio piecewise E2E — cockpit $(hostname -s) → $STUDIO_HOST"
run_pro_cfos_controller || log "PRO CFOS controller lane failed (non-fatal)"
run_studio_remote
log "Done. Full log: $LOG"
log "Studio remote log: /tmp/gum_studio_piecewise_e2e.studio.log (on Studio)"
