#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/byron/projects/active/hydradg"
STUDIO_SSH="${STUDIO_SSH:-magicstudiobox}"
BRANCH="${HYDRADG_BRANCH:-setup/remote-work-20260818}"
PIN="6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219"
RUN_ID="HYDRADB-STUDIO-$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
mkdir -p "$OUT"

fail(){ echo "FAIL=$1" | tee -a "$OUT/final_status.txt"; exit "${2:-1}"; }
log(){ printf '[%3s%%] %s\n' "$1" "$2"; }

cd "$ROOT"
log 5 "pull HydraDG setup branch on magicPRObox"
git fetch origin "$BRANCH" --quiet
git switch "$BRANCH" >/dev/null 2>&1 || git switch -c "$BRANCH" --track "origin/$BRANCH"
test -z "$(git status --porcelain)" || fail HYDRADG_MAGICPRO_DIRTY 10
git pull --ff-only origin "$BRANCH" >/dev/null

log 15 "verify studio paths and synchronize HydraDG"
ssh -o BatchMode=yes -o ConnectTimeout=10 "$STUDIO_SSH" 'bash -s' <<'REMOTE' > "$OUT/studio_preflight.txt" || fail STUDIO_PREFLIGHT_FAILED 20
set -euo pipefail
ACTIVE="/Users/byron/projects/active"
for P in hydradb hydradg; do
  test -d "$ACTIVE/$P/.git" || { echo "MISSING_REPO:$ACTIVE/$P"; exit 21; }
done
cd "$ACTIVE/hydradg"
test -z "$(git status --porcelain)" || { echo DIRTY_HYDRADG; git status --short; exit 22; }
git fetch origin main --quiet
git switch main >/dev/null 2>&1 || true
git pull --ff-only origin main >/dev/null
L="$(git rev-parse HEAD)"; R="$(git rev-parse origin/main)"
test "$L" = "$R" || { echo "HYDRADG_DIVERGED local=$L remote=$R"; exit 23; }
echo "HYDRADG_STUDIO_HEAD=$L"
REMOTE

log 30 "verify exact HydraDB source pin on magicSTUDIObox"
ssh "$STUDIO_SSH" "bash -s" <<REMOTE > "$OUT/hydradb_source.txt" || fail HYDRADB_SOURCE_FAILED 30
set -euo pipefail
source "\$HOME/.cargo/env" 2>/dev/null || true
cd /Users/byron/projects/active/hydradb
test -z "\$(git status --porcelain)" || { echo DIRTY_HYDRADB; git status --short; exit 31; }
git fetch --all --tags --prune --quiet
git cat-file -e '${PIN}^{commit}'
git checkout --detach '$PIN' >/dev/null
HEAD="\$(git rev-parse HEAD)"
test "\$HEAD" = '$PIN' || { echo "PIN_MISMATCH:\$HEAD"; exit 32; }
echo "HYDRADB_STUDIO_HEAD=\$HEAD"
echo "HYDRADB_ORIGIN=\$(git remote get-url origin)"
REMOTE

log 45 "ensure persistent HydraDB graph-node on studio"
ssh "$STUDIO_SSH" 'bash -s' <<'REMOTE' > "$OUT/hydradb_start.txt" || fail HYDRADB_START_FAILED 40
set -euo pipefail
source "$HOME/.cargo/env" 2>/dev/null || true
H="/Users/byron/projects/active/hydradb"
cd "$H"
mkdir -p .hydradb/store .hydradb/cache
if [ ! -s .hydradb/auth-token ]; then
  umask 077
  if command -v openssl >/dev/null 2>&1; then openssl rand -hex 32 > .hydradb/auth-token; else python3 - <<'PY' > .hydradb/auth-token
import secrets
print(secrets.token_hex(32))
PY
  fi
fi
chmod 600 .hydradb/auth-token
if ! curl -fsS http://127.0.0.1:9090/readyz >/dev/null 2>&1; then
  command -v tmux >/dev/null 2>&1 || { echo MISSING_TMUX; exit 41; }
  tmux has-session -t hydradb 2>/dev/null && tmux kill-session -t hydradb || true
  BREW_PREFIX="$(brew --prefix 2>/dev/null || true)"
  CMD="cd '$H'; source \"\$HOME/.cargo/env\" 2>/dev/null || true; export CLOUD_PROVIDER=local LOCAL_PATH='$H/.hydradb/store' GRAPH_NAMESPACE=default GRAPH_ID=default GRAPH_CELL_ID=cell-0 GRAPH_CELLS=cell-0 GRAPH_NODE_ID=node-0 GRAPH_BOLT_NODE_ADDRESSES=node-0=127.0.0.1:7687 GRAPH_ADVERTISED_BOLT_ADDR=127.0.0.1:7687 GRAPH_DATA_CACHE_DIR='$H/.hydradb/cache' GRAPH_AUTH_TOKEN_FILE='$H/.hydradb/auth-token' GRAPH_ALLOW_PLAINTEXT=true RUST_MIN_STACK=33554432;"
  if [ -n "$BREW_PREFIX" ]; then CMD="$CMD export BINDGEN_EXTRA_CLANG_ARGS='-I$BREW_PREFIX/include' LIBRARY_PATH='$BREW_PREFIX/lib';"; fi
  CMD="$CMD exec cargo run --locked --features server-runtime --bin graph-node"
  tmux new-session -d -s hydradb "$CMD"
  for _ in $(seq 1 150); do
    curl -fsS http://127.0.0.1:9090/readyz >/dev/null 2>&1 && break
    sleep 2
  done
fi
curl -fsS http://127.0.0.1:9090/readyz >/dev/null || { echo READY_FAILED; exit 42; }
echo HYDRADB_READY=YES
echo HYDRADB_ROOT="$H"
echo HYDRADB_PID="$(pgrep -f 'graph-node' | head -n1 || true)"
REMOTE

log 65 "perform real HydraDB write/read on studio"
ssh "$STUDIO_SSH" 'bash -s' <<'REMOTE' > "$OUT/hydradb_roundtrip.txt" || fail HYDRADB_ROUNDTRIP_FAILED 50
set -euo pipefail
H="/Users/byron/projects/active/hydradb"
TOKEN="$(cat "$H/.hydradb/auth-token")"
ID="$(date +%s)"
CREATE="$(curl -fsS http://127.0.0.1:8443/v1/graphs/default/query -H "Authorization: Bearer $TOKEN" -H 'X-Graph-Namespace: default' -H 'Content-Type: application/json' --data "{\"cell_id\":\"cell-0\",\"query\":\"CREATE (a {id: $ID})-[:REMOTE_READY]->(b {id: $((ID+1))})\"}")"
READ="$(curl -fsS http://127.0.0.1:8443/v1/graphs/default/query -H "Authorization: Bearer $TOKEN" -H 'X-Graph-Namespace: default' -H 'Content-Type: application/json' --data "{\"cell_id\":\"cell-0\",\"query\":\"MATCH (a {id: $ID})-[:REMOTE_READY]->(b) RETURN b.id AS id\"}")"
printf '%s' "$CREATE" | shasum -a 256 | awk '{print "CREATE_RESPONSE_SHA256=" $1}'
printf '%s' "$READ" | shasum -a 256 | awk '{print "READ_RESPONSE_SHA256=" $1}'
printf '%s' "$READ" | grep -q "$((ID+1))" || { echo READ_VALUE_MISMATCH; exit 51; }
echo HYDRADB_WRITE_READ=PASS
REMOTE

log 80 "create laptop-local HydraDB tunnels"
pkill -f '127.0.0.1:18443:127.0.0.1:8443.*magicstudio' 2>/dev/null || true
ssh -fNT -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=4 \
  -L 127.0.0.1:18443:127.0.0.1:8443 \
  -L 127.0.0.1:17687:127.0.0.1:7687 \
  -L 127.0.0.1:19090:127.0.0.1:9090 \
  "$STUDIO_SSH"
curl -fsS http://127.0.0.1:19090/readyz > "$OUT/tunneled_readyz.txt" || fail HYDRADB_TUNNEL_FAILED 60

log 90 "write bounded receipt"
SOURCE_SHA="$(shasum -a 256 "$OUT/hydradb_source.txt" | awk '{print $1}')"
START_SHA="$(shasum -a 256 "$OUT/hydradb_start.txt" | awk '{print $1}')"
ROUND_SHA="$(shasum -a 256 "$OUT/hydradb_roundtrip.txt" | awk '{print $1}')"
READY_SHA="$(shasum -a 256 "$OUT/tunneled_readyz.txt" | awk '{print $1}')"
jq -n --arg run "$RUN_ID" --arg pin "$PIN" --arg source "$SOURCE_SHA" --arg start "$START_SHA" --arg round "$ROUND_SHA" --arg ready "$READY_SHA" '{schema:"hydradg.hydradb_studio_remote_check.v1",run_id:$run,execution_class:"LOCAL_AND_REMOTE_RECOMPUTED",studio_paths:{hydradb:"/Users/byron/projects/active/hydradb",hydradg:"/Users/byron/projects/active/hydradg"},hydradb_pin:$pin,service:{graph_node:"PASS",write_read_roundtrip:"PASS",admin_tunnel:"PASS"},tunnels:{http:"127.0.0.1:18443",bolt:"127.0.0.1:17687",admin:"127.0.0.1:19090"},evidence_sha256:{source:$source,start:$start,roundtrip:$round,readyz:$ready},claim_ceiling:"MAGICSTUDIO_LOCAL_HYDRADB_RUNTIME_AND_REMOTE_TUNNEL_VERIFIED_ONLY",signature_state:"NOT_SIGNED_BY_THIS_SCRIPT",mmr_state:"APPEND_PENDING"}' > "$OUT/HYDRADB_STUDIO_RECEIPT.json"
RECEIPT_SHA="$(shasum -a 256 "$OUT/HYDRADB_STUDIO_RECEIPT.json" | awk '{print $1}')"
echo PASS > "$OUT/final_status.txt"

log 95 "commit/push receipt to review branch"
cd "$ROOT"
git add "HydraDG_DaisyTrain_v0.3.7/eval/remote_work/$RUN_ID"
if command -v gitleaks >/dev/null 2>&1; then gitleaks git --staged --redact=100 --no-banner .; fi
git commit -m "Record HydraDB studio remote check $RUN_ID"
git push origin "$BRANCH"
git fetch origin "$BRANCH" --quiet
git pull --ff-only origin "$BRANCH" >/dev/null
LOCAL="$(git rev-parse HEAD)"; REMOTE="$(git rev-parse "origin/$BRANCH")"; test "$LOCAL" = "$REMOTE" || fail POST_PUSH_DIVERGENCE 70

log 100 "complete"
echo HYDRADB_REMOTE_READY=YES
echo HYDRADB_STUDIO_ROOT=/Users/byron/projects/active/hydradb
echo HYDRADG_STUDIO_ROOT=/Users/byron/projects/active/hydradg
echo HYDRADB_PIN=$PIN
echo HYDRADB_HTTP_TUNNEL=http://127.0.0.1:18443
echo HYDRADB_BOLT_TUNNEL=bolt://127.0.0.1:17687
echo HYDRADB_ADMIN_TUNNEL=http://127.0.0.1:19090
echo CHECKPOINT_COMMIT=$LOCAL
echo RECEIPT_SHA256=$RECEIPT_SHA
