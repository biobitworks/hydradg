#!/usr/bin/env bash
set -euo pipefail

# Final remote-work readiness test for magicPRObox -> magicSTUDIObox.
# Run on magicPRObox from the HydraDG repository.

ROOT="/Users/byron/projects/active/hydradg"
ACTIVE="/Users/byron/projects/active"
STUDIO_SSH="${STUDIO_SSH:-magicstudiobox}"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
RUN_ID="REMOTE-READY-$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
mkdir -p "$OUT"

log(){ printf '[%3s%%] %s\n' "$1" "$2"; }
fail(){ echo "FAIL=$1" | tee -a "$OUT/final_status.txt"; exit "${2:-1}"; }

repo_sync_local(){
  local name="$1" path="$ACTIVE/$1"
  test -d "$path/.git" || fail "LOCAL_REPO_MISSING:$name" 20
  cd "$path"
  test -z "$(git status --porcelain)" || fail "LOCAL_REPO_DIRTY:$name" 21
  git fetch origin main --quiet
  git pull --ff-only origin main >/dev/null
  local l r
  l="$(git rev-parse HEAD)"; r="$(git rev-parse origin/main)"
  test "$l" = "$r" || fail "LOCAL_REPO_DIVERGED:$name" 22
  printf '%s\t%s\n' "$name" "$l" >> "$OUT/local_repos.tsv"
}

remote(){ ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO_SSH" "$@"; }

log 5 "verify control-plane repository"
cd "$ROOT"
test "$(git rev-parse --show-toplevel)" = "$ROOT" || fail WRONG_HYDRADG_ROOT 10

# The setup branch itself is synchronized first.
git fetch origin "$BRANCH" --quiet
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
test -z "$(git status --porcelain)" || fail HYDRADG_SETUP_BRANCH_DIRTY 11
git pull --ff-only origin "$BRANCH" >/dev/null

log 12 "verify Tailscale and SSH transport"
command -v tailscale >/dev/null || fail TAILSCALE_MISSING_ON_MAGICPRO 12
tailscale status > "$OUT/tailscale_magicpro.txt"
remote 'command -v tailscale >/dev/null && tailscale status' > "$OUT/tailscale_magicstudio.txt" || fail TAILSCALE_OR_SSH_FAILED 13
remote 'hostname; whoami' > "$OUT/studio_identity.txt"

log 20 "synchronize canonical repos on magicPRObox"
# Ollarma and Watchtower are canonical main repos. HydraDG setup branch is handled above.
repo_sync_local ollarma
repo_sync_local watchtower

log 30 "ensure and synchronize repos on magicSTUDIObox"
remote 'bash -s' <<'REMOTE_SYNC' > "$OUT/studio_repo_sync.txt"
set -euo pipefail
ACTIVE="/Users/byron/projects/active"
mkdir -p "$ACTIVE"
for NAME in hydradg ollarma watchtower; do
  PATH_="$ACTIVE/$NAME"
  if [ ! -d "$PATH_/.git" ]; then
    command -v gh >/dev/null 2>&1 || { echo "MISSING_GH:$NAME"; exit 31; }
    gh repo clone "biobitworks/$NAME" "$PATH_"
  fi
  cd "$PATH_"
  if [ -n "$(git status --porcelain)" ]; then
    echo "DIRTY:$NAME"
    git status --short
    exit 32
  fi
  git fetch origin main --quiet
  git switch main >/dev/null 2>&1 || true
  git pull --ff-only origin main >/dev/null
  L="$(git rev-parse HEAD)"; R="$(git rev-parse origin/main)"
  [ "$L" = "$R" ] || { echo "DIVERGED:$NAME local=$L remote=$R"; exit 33; }
  echo "SYNCED:$NAME:$L"
done
REMOTE_SYNC

log 45 "ensure persistent Ollarma service"
remote 'bash -s' <<'REMOTE_OLLARMA' > "$OUT/ollarma_start.txt"
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
REMOTE_OLLARMA

log 58 "execute Ollarma live model test"
remote 'curl -fsS -X POST http://127.0.0.1:8484/chat -H "Content-Type: application/json" --data-binary '\''{"message":"Remote readiness test. Reply with a short confirmation that the local model is responsive."}'\''' > "$OUT/ollarma_chat.json" || fail OLLARMA_MODEL_TEST_FAILED 42
test -s "$OUT/ollarma_chat.json" || fail OLLARMA_EMPTY_RESPONSE 43

log 68 "ensure Watchtower dashboard service"
remote 'bash -s' <<'REMOTE_WATCH' > "$OUT/watchtower_start.txt"
set -euo pipefail
cd /Users/byron/projects/active/watchtower
if ! curl -fsS http://127.0.0.1:8000/ >/dev/null 2>&1; then
  command -v tmux >/dev/null 2>&1 || { echo MISSING_TMUX; exit 51; }
  tmux has-session -t watchtower 2>/dev/null && tmux kill-session -t watchtower || true
  tmux new-session -d -s watchtower 'cd /Users/byron/projects/active/watchtower && exec uv run --no-project --python 3.13 --with fastapi --with httpx --with jinja2 --with pydantic --with uvicorn uvicorn watchtower.api:app --host 127.0.0.1 --port 8000'
  for _ in $(seq 1 45); do
    curl -fsS http://127.0.0.1:8000/ >/dev/null 2>&1 && break
    sleep 2
  done
fi
curl -fsSI http://127.0.0.1:8000/ | head
REMOTE_WATCH

log 78 "create laptop-local SSH tunnels"
# Remove only our old forwarding masters if present. These commands do not alter studio services.
pkill -f '127.0.0.1:18484:127.0.0.1:8484.*magicstudiobox' 2>/dev/null || true
pkill -f '127.0.0.1:18000:127.0.0.1:8000.*magicstudiobox' 2>/dev/null || true
ssh -fNT -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=4 \
  -L 127.0.0.1:18484:127.0.0.1:8484 \
  -L 127.0.0.1:18000:127.0.0.1:8000 \
  "$STUDIO_SSH"

curl -fsS http://127.0.0.1:18484/health > "$OUT/ollarma_tunnel_health.json" || fail OLLARMA_TUNNEL_FAILED 61
curl -fsSI http://127.0.0.1:18000/ > "$OUT/watchtower_tunnel_headers.txt" || fail WATCHTOWER_TUNNEL_FAILED 62

log 86 "bounded cross-machine test run"
# Exercise Ollarma through the same tunnel the mobile laptop will use.
curl -fsS -X POST http://127.0.0.1:18484/chat \
  -H 'Content-Type: application/json' \
  --data-binary '{"message":"HydraDG remote-work test through SSH/Tailscale tunnel. Confirm the model path is responsive."}' \
  > "$OUT/ollarma_tunnel_chat.json" || fail TUNNELED_MODEL_TEST_FAILED 63

log 90 "write FCO-style receipt"
PRO_HOST="$(hostname)"
STUDIO_ID="$(tr '\n' ' ' < "$OUT/studio_identity.txt" | sed 's/[[:space:]]*$//')"
PRO_TS_SHA="$(shasum -a 256 "$OUT/tailscale_magicpro.txt" | awk '{print $1}')"
STUDIO_TS_SHA="$(shasum -a 256 "$OUT/tailscale_magicstudio.txt" | awk '{print $1}')"
CHAT_SHA="$(shasum -a 256 "$OUT/ollarma_tunnel_chat.json" | awk '{print $1}')"
WATCH_SHA="$(shasum -a 256 "$OUT/watchtower_tunnel_headers.txt" | awk '{print $1}')"

jq -n \
  --arg run_id "$RUN_ID" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg magicpro "$PRO_HOST" \
  --arg magicstudio "$STUDIO_ID" \
  --arg ssh_alias "$STUDIO_SSH" \
  --arg pro_ts_sha "$PRO_TS_SHA" \
  --arg studio_ts_sha "$STUDIO_TS_SHA" \
  --arg chat_sha "$CHAT_SHA" \
  --arg watch_sha "$WATCH_SHA" \
  '{
    schema:"hydradg.remote_readiness_receipt.v1",
    run_id:$run_id,
    timestamp_utc:$timestamp,
    execution_class:"LOCAL_AND_REMOTE_RECOMPUTED",
    hosts:{magicpro:$magicpro,magicstudio:$magicstudio,ssh_alias:$ssh_alias},
    transport:{tailscale_magicpro_status_sha256:$pro_ts_sha,tailscale_magicstudio_status_sha256:$studio_ts_sha,ssh:"PASS"},
    repositories:{magicpro:"SYNCED_OR_FAIL_CLOSED",magicstudio:"SYNCED_OR_FAIL_CLOSED"},
    ollarma:{studio_service:"PASS",tunneled_endpoint:"http://127.0.0.1:18484",live_model_response_sha256:$chat_sha},
    watchtower:{studio_service:"PASS",tunneled_endpoint:"http://127.0.0.1:18000",http_headers_sha256:$watch_sha},
    daisy_training_posture:"magicSTUDIObox persistent tmux/host-service lane available; no training claim made by this readiness test",
    claim_ceiling:"REMOTE_TRANSPORT_SERVICE_AND_MODEL_READINESS_ONLY",
    signature_state:"NOT_SIGNED_BY_THIS_SCRIPT",
    mmr_state:"APPEND_PENDING"
  }' > "$OUT/REMOTE_READINESS_RECEIPT.json"

RECEIPT_SHA="$(shasum -a 256 "$OUT/REMOTE_READINESS_RECEIPT.json" | awk '{print $1}')"

echo "PASS" > "$OUT/final_status.txt"

log 94 "commit and push receipt checkpoint"
cd "$ROOT"
git add "HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks git --staged --redact=100 --no-banner .
fi
git commit -m "Record remote work readiness test $RUN_ID"
git push origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
LOCAL="$(git rev-parse HEAD)"; REMOTE="$(git rev-parse "origin/$BRANCH")"
test "$LOCAL" = "$REMOTE" || fail POST_PUSH_DIVERGENCE 70

log 100 "complete"
echo "REMOTE_READY=YES"
echo "RUN_ID=$RUN_ID"
echo "CHECKPOINT_COMMIT=$LOCAL"
echo "RECEIPT_SHA256=$RECEIPT_SHA"
echo "OLLARMA_REMOTE_URL=http://127.0.0.1:18484"
echo "WATCHTOWER_REMOTE_URL=http://127.0.0.1:18000"
echo "NOTE=These URLs are reachable on magicPRObox while the SSH tunnel is alive."
