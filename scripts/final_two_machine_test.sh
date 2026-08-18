#!/usr/bin/env bash
set -euo pipefail

# Final bounded remote-work smoke test.
# Control host: magicPRObox
# Execution host: magicSTUDIObox
# This script does NOT launch the frozen VITHIA-OVERNIGHT-01 queue.

ROOT="/Users/byron/projects/active/hydradg"
PKG="$ROOT/HydraDG_DaisyTrain_v0.3.7"
STUDIO="${STUDIO_SSH:-magicstudiobox}"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
STUDIO_ACTIVE="/Users/byron/projects/active"
STUDIO_LESSWRONG="$STUDIO_ACTIVE/lesswrong"
STUDIO_HYDRADG="$STUDIO_ACTIVE/hydradg"
STUDIO_OLLARMA="$STUDIO_ACTIVE/ollarma"
RUN_ID="TWO-MACHINE-SMOKE-$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$PKG/eval/remote_work/$RUN_ID"
mkdir -p "$OUT"

log(){ printf '[%3s%%] %s\n' "$1" "$2"; }
fail(){ echo "FAIL=$1" | tee -a "$OUT/final_status.txt"; exit "${2:-1}"; }
remote(){ ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO" "$@"; }
sha(){ shasum -a 256 "$1" | awk '{print $1}'; }

log 5 "control-plane Git synchronization"
cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || fail WRONG_HYDRADG_ROOT 10
git fetch origin "$BRANCH" --quiet
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
test -z "$(git status --porcelain)" || fail MAGICPRO_HYDRADG_DIRTY 11
git pull --ff-only origin "$BRANCH" >/dev/null
CONTROL_HEAD="$(git rev-parse HEAD)"

log 12 "Tailscale + SSH"
command -v tailscale >/dev/null || fail MAGICPRO_TAILSCALE_MISSING 12
tailscale status > "$OUT/tailscale_magicpro.txt"
remote 'command -v tailscale >/dev/null && tailscale status' > "$OUT/tailscale_magicstudio.txt" || fail STUDIO_TAILSCALE_OR_SSH 13
remote 'hostname; whoami; sw_vers 2>/dev/null || uname -a' > "$OUT/studio_identity.txt"

log 22 "magicSTUDIObox repository state"
remote "bash -s" <<'REMOTE_REPOS' > "$OUT/studio_repos.txt"
set -euo pipefail
for P in /Users/byron/projects/active/hydradg /Users/byron/projects/active/ollarma; do
  test -d "$P/.git" || { echo "MISSING_GIT_REPO:$P"; exit 21; }
  cd "$P"
  test -z "$(git status --porcelain)" || { echo "DIRTY:$P"; git status --short; exit 22; }
  git fetch origin main --quiet
  git switch main >/dev/null 2>&1 || true
  git pull --ff-only origin main >/dev/null
  L="$(git rev-parse HEAD)"; R="$(git rev-parse origin/main)"
  test "$L" = "$R" || { echo "DIVERGED:$P local=$L origin=$R"; exit 23; }
  echo "SYNCED:$P:$L"
done
REMOTE_REPOS

log 32 "LessWrong workspace gate on magicSTUDIObox"
remote "bash -s" <<'REMOTE_LW' > "$OUT/lesswrong_workspace.txt"
set -euo pipefail
LW="/Users/byron/projects/active/lesswrong"
test -d "$LW" || { echo "LESSWRONG_PATH_MISSING:$LW"; exit 31; }

echo "LESSWRONG_PATH=$LW"
if git -C "$LW" rev-parse --show-toplevel >/dev/null 2>&1; then
  TOP="$(git -C "$LW" rev-parse --show-toplevel)"
  echo "LESSWRONG_GIT_TOPLEVEL=$TOP"
  test "$TOP" = "$LW" || { echo "LESSWRONG_WRONG_GIT_ROOT:$TOP"; exit 32; }
  test -z "$(git -C "$LW" status --porcelain)" || { echo "LESSWRONG_DIRTY"; git -C "$LW" status --short; exit 33; }
  REMOTE_URL="$(git -C "$LW" remote get-url origin 2>/dev/null || true)"
  test -n "$REMOTE_URL" || { echo "LESSWRONG_ORIGIN_MISSING"; exit 34; }
  echo "LESSWRONG_ORIGIN=$REMOTE_URL"
  BR="$(git -C "$LW" branch --show-current)"
  test -n "$BR" || { echo "LESSWRONG_DETACHED_HEAD"; exit 35; }
  git -C "$LW" fetch origin "$BR" --quiet
  git -C "$LW" pull --ff-only origin "$BR" >/dev/null
  L="$(git -C "$LW" rev-parse HEAD)"; R="$(git -C "$LW" rev-parse "origin/$BR")"
  test "$L" = "$R" || { echo "LESSWRONG_DIVERGED local=$L origin=$R"; exit 36; }
  echo "LESSWRONG_SYNCED:$BR:$L"
else
  echo "LESSWRONG_NOT_GIT_REPO"
  exit 37
fi

POST="$LW/mechanical-scientific-method-for-solving-aging"
if [ -d "$POST" ]; then
  echo "POST_SUBFOLDER=FOUND"
  for F in \
    backbone/ARTICLE_BACKBONE_v0.7.json \
    widgets/LESSWRONG_WIDGET_ANTICUBE_FCO.html \
    widgets/LESSWRONG_WIDGET_MSM_PIPELINE.html \
    fcg/custody/POST_PACKAGE_MANIFEST.json
  do
    test -f "$POST/$F" || { echo "POST_REQUIRED_FILE_MISSING:$F"; exit 38; }
  done
  if [ -f "$POST/scripts/verify_post_package.py" ]; then
    python3 "$POST/scripts/verify_post_package.py"
  fi
  echo "LESSWRONG_POST_TEST=PASS"
else
  echo "POST_SUBFOLDER_MISSING:$POST"
  exit 39
fi
REMOTE_LW

log 47 "Ollarma service + local model on magicSTUDIObox"
remote "bash -s" <<'REMOTE_OLLARMA' > "$OUT/ollarma_service.txt"
set -euo pipefail
cd /Users/byron/projects/active/ollarma
if ! curl -fsS http://127.0.0.1:8484/health >/dev/null 2>&1; then
  command -v tmux >/dev/null 2>&1 || { echo MISSING_TMUX; exit 41; }
  tmux has-session -t ollarma 2>/dev/null && tmux kill-session -t ollarma || true
  tmux new-session -d -s ollarma 'cd /Users/byron/projects/active/ollarma && exec uv run ollarma serve'
  for _ in $(seq 1 45); do
    curl -fsS http://127.0.0.1:8484/health >/dev/null 2>&1 && break
    sleep 2
  done
fi
curl -fsS http://127.0.0.1:8484/health
curl -fsS -X POST http://127.0.0.1:8484/chat \
  -H 'Content-Type: application/json' \
  --data-binary '{"message":"Two-machine readiness smoke. Reply briefly that the local governed model path is responsive."}'
REMOTE_OLLARMA

log 62 "bounded Vithia training smoke on magicSTUDIObox"
remote "bash -s" <<'REMOTE_TRAIN' > "$OUT/vithia_smoke.txt"
set -euo pipefail
PKG="/Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7"
TMP="$(mktemp -d /tmp/hydradg-two-machine-smoke.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
PY=""
for C in "$PKG/.venv-hydradg/bin/python" /Users/byron/fco-venv/bin/python3 /opt/homebrew/bin/python3; do
  if [ -x "$C" ] && "$C" -c 'import torch,transformers,numpy' >/dev/null 2>&1; then PY="$C"; break; fi
done
test -n "$PY" || { echo "VITHIA_PYTHON_ENV_MISSING"; exit 51; }
cd "$PKG"
"$PY" scripts/vithia_divergence_core.py \
  --run-id two_machine_smoke \
  --outdir "$TMP" \
  --seed 20260818 \
  --steps 2 \
  --batch 1 \
  --seq 32 \
  --lr 0.0003
RP="$TMP/two_machine_smoke.receipt.json"
CK="$TMP/two_machine_smoke.pt"
test -s "$RP" || { echo "SMOKE_RECEIPT_MISSING"; exit 52; }
test -s "$CK" || { echo "SMOKE_CHECKPOINT_MISSING"; exit 53; }
echo "SMOKE_RECEIPT_SHA256=$(shasum -a 256 "$RP" | awk '{print $1}')"
echo "SMOKE_CHECKPOINT_SHA256=$(shasum -a 256 "$CK" | awk '{print $1}')"
python3 - "$RP" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
print("SMOKE_FINAL_STATE_HASH="+x["final_state_hash"])
print("SMOKE_DEVICE="+("cuda" if x.get("environment",{}).get("cuda_available") else "cpu"))
print("SMOKE_DETERMINISTIC_REQUESTED="+str(x.get("deterministic_requested")))
PY
REMOTE_TRAIN

log 76 "laptop-local tunnel test"
pkill -f '127.0.0.1:18484:127.0.0.1:8484.*magicstudiobox' 2>/dev/null || true
ssh -fNT -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=4 \
  -L 127.0.0.1:18484:127.0.0.1:8484 "$STUDIO"
curl -fsS http://127.0.0.1:18484/health > "$OUT/ollarma_tunnel_health.json" || fail OLLARMA_TUNNEL_FAILED 61
curl -fsS -X POST http://127.0.0.1:18484/chat \
  -H 'Content-Type: application/json' \
  --data-binary '{"message":"Tunneled readiness smoke from magicPRObox. Reply briefly."}' \
  > "$OUT/ollarma_tunnel_chat.json" || fail OLLARMA_TUNNEL_CHAT_FAILED 62

log 88 "write bounded FCO-style readiness receipt"
PRO_TS_SHA="$(sha "$OUT/tailscale_magicpro.txt")"
STUDIO_TS_SHA="$(sha "$OUT/tailscale_magicstudio.txt")"
LW_SHA="$(sha "$OUT/lesswrong_workspace.txt")"
TRAIN_SHA="$(sha "$OUT/vithia_smoke.txt")"
CHAT_SHA="$(sha "$OUT/ollarma_tunnel_chat.json")"

jq -n \
  --arg run_id "$RUN_ID" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg control_head "$CONTROL_HEAD" \
  --arg pro_ts "$PRO_TS_SHA" \
  --arg studio_ts "$STUDIO_TS_SHA" \
  --arg lw "$LW_SHA" \
  --arg train "$TRAIN_SHA" \
  --arg chat "$CHAT_SHA" \
  '{
    schema:"hydradg.two_machine_remote_readiness.v1",
    run_id:$run_id,
    timestamp_utc:$timestamp,
    control_branch:"setup/remote-work-20260818",
    control_commit:$control_head,
    transport:{tailscale_magicpro_sha256:$pro_ts,tailscale_magicstudio_sha256:$studio_ts,ssh:"PASS"},
    magicstudio:{lesswrong_workspace_receipt_sha256:$lw,ollarma:"PASS",bounded_vithia_smoke_sha256:$train},
    magicpro:{ollarma_tunnel:"PASS",tunneled_chat_sha256:$chat},
    training_claim:"A two-step synthetic Vithia/Pythia fixture executed on magicSTUDIObox; no full Daisy-training or scientific-validation claim.",
    claim_ceiling:"REMOTE_WORKSPACE_TRANSPORT_SERVICE_AND_BOUNDED_TRAINING_SMOKE_ONLY",
    signature_state:"NOT_SIGNED_BY_THIS_TEST",
    public_release_state:"NOT_PROMOTED"
  }' > "$OUT/TWO_MACHINE_READINESS_RECEIPT.json"
RECEIPT_SHA="$(sha "$OUT/TWO_MACHINE_READINESS_RECEIPT.json")"
echo PASS > "$OUT/final_status.txt"

log 94 "commit + push readiness receipt"
cd "$ROOT"
git add "HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks git --staged --redact=100 --no-banner .
fi
git commit -m "Record two-machine remote readiness smoke $RUN_ID"
git push origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
LOCAL="$(git rev-parse HEAD)"; REMOTE_HEAD="$(git rev-parse "origin/$BRANCH")"
test "$LOCAL" = "$REMOTE_HEAD" || fail POST_PUSH_DIVERGENCE 70

log 100 "complete"
echo "TWO_MACHINE_READY=YES"
echo "RUN_ID=$RUN_ID"
echo "CHECKPOINT_COMMIT=$LOCAL"
echo "RECEIPT_SHA256=$RECEIPT_SHA"
echo "LESSWRONG_WORKSPACE=$STUDIO_LESSWRONG"
echo "OLLARMA_TUNNEL=http://127.0.0.1:18484"
