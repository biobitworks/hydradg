#!/usr/bin/env bash
set -euo pipefail
[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"

# Hack Hydra Best Use v2 — MagicStudio local launcher.
# Keeps all mutable runtime/data under ~/.local/share/hydradg-best-use.
# Does not print or commit the local HydraDB bearer token.

HYDRADB_PIN="6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO="$(cd "$PKG/.." && pwd)"
RUNTIME="${BEST_USE_RUNTIME:-$HOME/.local/share/hydradg-best-use}"
HYDRA_SRC="$RUNTIME/hydradb-src"
STORE="$RUNTIME/hydradb-store"
CACHE="$RUNTIME/hydradb-cache"
AUTH="$RUNTIME/hydradb-auth-token"
LOGDIR="$RUNTIME/logs"
EVALDIR="$RUNTIME/eval"
DATADIR="$RUNTIME/data"
RECEIPTDIR="$RUNTIME/receipts"
SERVER_PORT="${BEST_USE_PORT:-8787}"
SERVER_BIND="${BEST_USE_BIND:-127.0.0.1}"
OLLARMA_URL="${OLLARMA_URL:-http://127.0.0.1:8484}"
DEFAULT_EXTRACTOR="${BEST_USE_EXTRACTOR:-heuristic}"
MODEL="${BEST_USE_MODEL:-}"
HYDRA_ENDPOINT="http://127.0.0.1:8443/v1/graphs/default/query"
HYDRA_HEALTH="http://127.0.0.1:8443/healthz"
HYDRA_PID="$RUNTIME/hydradb.pid"
SERVER_PID="$RUNTIME/best_use_server.pid"

mkdir -p "$RUNTIME" "$STORE" "$CACHE" "$LOGDIR" "$EVALDIR" "$DATADIR" "$RECEIPTDIR"

say() { printf '%s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }
pid_alive() { [[ -f "$1" ]] && kill -0 "$(cat "$1")" 2>/dev/null; }

sha256_file() {
  if have shasum; then shasum -a 256 "$1" | awk '{print $1}';
  else python3 - "$1" <<'PY'
import hashlib,sys
h=hashlib.sha256()
with open(sys.argv[1],'rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
print(h.hexdigest())
PY
  fi
}

preflight() {
  local missing=()
  for cmd in git python3 curl cargo; do have "$cmd" || missing+=("$cmd"); done
  ((${#missing[@]}==0)) || fail "missing commands: ${missing[*]}"
  if [[ "$(uname -s)" == "Darwin" ]]; then
    have cmake || fail "cmake missing. Install: brew install cmake"
    have pkg-config || fail "pkg-config missing. Install: brew install pkg-config"
    pkg-config --exists cypher-parser 2>/dev/null || pkg-config --exists libcypher-parser 2>/dev/null || \
      fail "libcypher-parser missing. Install: brew install cleishm/neo4j/libcypher-parser"
    pkg-config --exists graphblas 2>/dev/null || pkg-config --exists GraphBLAS 2>/dev/null || \
      fail "SuiteSparse GraphBLAS missing. Install: brew install suite-sparse"
  fi
}

prepare_hydradb() {
  if [[ ! -d "$HYDRA_SRC/.git" ]]; then
    say "[hydradb] cloning public upstream into runtime"
    git clone https://github.com/hydra-db/hydradb.git "$HYDRA_SRC"
  fi
  if ! git -C "$HYDRA_SRC" cat-file -e "$HYDRADB_PIN^{commit}" 2>/dev/null; then
    say "[hydradb] fetching pinned commit"
    git -C "$HYDRA_SRC" fetch origin "$HYDRADB_PIN"
  fi
  git -C "$HYDRA_SRC" checkout --detach "$HYDRADB_PIN" >/dev/null
  [[ "$(git -C "$HYDRA_SRC" rev-parse HEAD)" == "$HYDRADB_PIN" ]] || fail "HydraDB pin mismatch"
  if [[ ! -x "$HYDRA_SRC/target/debug/graph-node" ]]; then
    say "[hydradb] first build; this compiles the pinned Rust server"
    (cd "$HYDRA_SRC" && env BINDGEN_EXTRA_CLANG_ARGS="-I/opt/homebrew/include" CPATH="/opt/homebrew/include" LIBRARY_PATH="/opt/homebrew/lib" cargo build --locked --features server-runtime --bin graph-node)
  fi
}

prepare_token() {
  if [[ ! -s "$AUTH" ]]; then
    umask 077
    python3 - <<'PY' > "$AUTH"
import secrets
print(secrets.token_urlsafe(36))
PY
    chmod 600 "$AUTH"
  fi
}

start_hydra() {
  if pid_alive "$HYDRA_PID"; then
    curl -fsS "$HYDRA_HEALTH" >/dev/null || fail "HydraDB pid exists but health probe failed"
    say "[hydradb] already running pid=$(cat "$HYDRA_PID")"
    return
  fi
  if curl -fsS --max-time 1 "$HYDRA_HEALTH" >/dev/null 2>&1; then
    fail "something is already serving HydraDB port 8443 but is not managed by $HYDRA_PID"
  fi
  say "[hydradb] starting localhost-only development node"
  (
    cd "$HYDRA_SRC"
    nohup env \
      CLOUD_PROVIDER=local \
      LOCAL_PATH="$STORE" \
      GRAPH_NAMESPACE=default \
      GRAPH_ID=default \
      GRAPH_CELL_ID=cell-0 \
      GRAPH_CELLS=cell-0 \
      GRAPH_NODE_ID=node-0 \
      GRAPH_BOLT_ADDR=127.0.0.1:17687 \
      GRAPH_BOLT_NODE_ADDRESSES=node-0=127.0.0.1:17687 \
      GRAPH_ADVERTISED_BOLT_ADDR=127.0.0.1:17687 \
      GRAPH_DATA_CACHE_DIR="$CACHE" \
      GRAPH_AUTH_TOKEN_FILE="$AUTH" \
      GRAPH_ALLOW_PLAINTEXT=true \
      RUST_MIN_STACK=33554432 \
      ./target/debug/graph-node > "$LOGDIR/hydradb.log" 2>&1 &
    echo $! > "$HYDRA_PID"
  )
  for _ in $(seq 1 90); do
    if curl -fsS "$HYDRA_HEALTH" >/dev/null 2>&1; then say "[hydradb] health PASS"; return; fi
    pid_alive "$HYDRA_PID" || { tail -100 "$LOGDIR/hydradb.log" >&2; fail "HydraDB exited"; }
    sleep 1
  done
  tail -100 "$LOGDIR/hydradb.log" >&2
  fail "HydraDB health timeout"
}

resolve_dataset() {
  FULL_DATA="${LONGMEMEVAL_DATA:-}"
  if [[ -n "$FULL_DATA" && ! -f "$FULL_DATA" ]]; then fail "LONGMEMEVAL_DATA not found: $FULL_DATA"; fi
  if [[ -z "$FULL_DATA" ]]; then
    local candidate="$REPO/HydraDG_DaisyTrain_v0.3.6/data/longmemeval_s_cleaned.json"
    if [[ -f "$candidate" && $(wc -c < "$candidate") -gt 200000000 ]]; then FULL_DATA="$candidate"; fi
  fi
  if [[ -z "$FULL_DATA" ]]; then
    FULL_DATA="$DATADIR/longmemeval_s_cleaned.json"
    if [[ ! -f "$FULL_DATA" || $(wc -c < "$FULL_DATA") -lt 200000000 ]]; then
      say "[data] downloading official cleaned LongMemEval-S"
      curl -fL --retry 3 \
        https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json \
        -o "$FULL_DATA.tmp"
      mv "$FULL_DATA.tmp" "$FULL_DATA"
    fi
  fi
  FULL_SHA="$(sha256_file "$FULL_DATA")"
  local expected="d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
  [[ "$FULL_SHA" == "$expected" ]] || fail "LongMemEval source SHA mismatch: $FULL_SHA"
  SMOKE_DATA="$DATADIR/longmemeval_smoke80.json"
  SMOKE_MANIFEST="$EVALDIR/longmemeval_smoke80_manifest.json"
  if [[ ! -f "$SMOKE_DATA" ]]; then
    say "[data] building deterministic smoke80"
    python3 "$PKG/scripts/build_longmemeval_smoke80.py" "$FULL_DATA" \
      --out "$SMOKE_DATA" --manifest "$SMOKE_MANIFEST" --n 80
  fi
  SMOKE_SHA="$(sha256_file "$SMOKE_DATA")"
}

run_structural() {
  say "[conformance] running synthetic typed-graph structural suite"
  python3 "$SCRIPT_DIR/best_use_structural_suite.py" \
    --endpoint "$HYDRA_ENDPOINT" --token-file "$AUTH" \
    --out "$EVALDIR/structural_suite.json"
}

ollarma_health() {
  if curl -fsS --max-time 3 "$OLLARMA_URL/health" >/dev/null 2>&1; then echo PASS; else echo UNAVAILABLE; fi
}

start_server() {
  if pid_alive "$SERVER_PID"; then
    say "[server] already running pid=$(cat "$SERVER_PID")"
    return
  fi
  local args=(
    "$SCRIPT_DIR/best_use_local_server.py"
    --data "$SMOKE_DATA"
    --token-file "$AUTH"
    --endpoint "$HYDRA_ENDPOINT"
    --ollarma-url "$OLLARMA_URL"
    --extractor "$DEFAULT_EXTRACTOR"
    --cache-dir "$RUNTIME/extraction-cache"
    --receipts "$RECEIPTDIR/server_receipts.jsonl"
    --bind "$SERVER_BIND"
    --port "$SERVER_PORT"
  )
  [[ -n "$MODEL" ]] && args+=(--model "$MODEL")
  say "[server] starting http://$SERVER_BIND:$SERVER_PORT"
  nohup python3 "${args[@]}" > "$LOGDIR/best_use_server.log" 2>&1 &
  echo $! > "$SERVER_PID"
  for _ in $(seq 1 30); do
    if curl -fsS "http://127.0.0.1:$SERVER_PORT/health" >/dev/null 2>&1; then return; fi
    pid_alive "$SERVER_PID" || { tail -100 "$LOGDIR/best_use_server.log" >&2; fail "local test server exited"; }
    sleep 1
  done
  tail -100 "$LOGDIR/best_use_server.log" >&2
  fail "local test server health timeout"
}

write_start_receipt() {
  python3 - "$RECEIPTDIR/startup_receipt.json" "$HYDRADB_PIN" "$FULL_SHA" "$SMOKE_SHA" "$SERVER_PORT" "$(ollarma_health)" "$DEFAULT_EXTRACTOR" "$REPO" <<'PY'
import hashlib,json,subprocess,sys,time
out,pin,full_sha,smoke_sha,port,ollarma,extractor,repo=sys.argv[1:]
def git(*a):
    try:return subprocess.check_output(["git","-C",repo,*a],text=True).strip()
    except Exception:return "UNRESOLVED"
obj={
 "schema":"hydradg.best_use_magicstudio_startup.v2",
 "timestamp_unix":int(time.time()),
 "hydradg_commit":git("rev-parse","HEAD"),
 "hydradg_branch":git("branch","--show-current"),
 "hydradb_pin":pin,
 "longmemeval_source_sha256":full_sha,
 "smoke80_sha256":smoke_sha,
 "server_url":f"http://127.0.0.1:{port}",
 "ollarma_health":ollarma,
 "default_extractor":extractor,
 "token_disclosure":"NOT_INCLUDED",
 "claim_ceiling":"LOCAL_TEST_SURFACE_READY",
 "signature_state":"NOT_SIGNED",
 "merkle_state":"NOT_MERKLE_COMMITTED"
}
raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode();obj["receipt_sha256"]=hashlib.sha256(raw).hexdigest()
open(out,"w").write(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(obj,indent=2,sort_keys=True))
PY
}

status() {
  say "HydraDB: $(curl -fsS --max-time 2 "$HYDRA_HEALTH" >/dev/null 2>&1 && echo UP || echo DOWN)"
  say "Best Use server: $(curl -fsS --max-time 2 "http://127.0.0.1:$SERVER_PORT/health" >/dev/null 2>&1 && echo UP || echo DOWN)"
  say "Ollarma: $(ollarma_health)"
  [[ -f "$HYDRA_PID" ]] && say "HydraDB PID file: $(cat "$HYDRA_PID")"
  [[ -f "$SERVER_PID" ]] && say "Server PID file: $(cat "$SERVER_PID")"
  say "Runtime: $RUNTIME"
}

stop() {
  if pid_alive "$SERVER_PID"; then kill "$(cat "$SERVER_PID")" || true; fi
  if pid_alive "$HYDRA_PID"; then kill "$(cat "$HYDRA_PID")" || true; fi
  rm -f "$SERVER_PID" "$HYDRA_PID"
  say "Stopped managed Best Use server and HydraDB. Runtime data preserved at $RUNTIME"
}

smoke() {
  curl -fsS "http://127.0.0.1:$SERVER_PORT/health" | python3 -m json.tool
  curl -fsS "http://127.0.0.1:$SERVER_PORT/cases?limit=3" | python3 -m json.tool
}

start_all() {
  preflight
  prepare_hydradb
  prepare_token
  start_hydra
  resolve_dataset
  run_structural
  start_server
  write_start_receipt
  say ""
  say "READY: http://127.0.0.1:$SERVER_PORT/"
  say "Default extractor: $DEFAULT_EXTRACTOR"
  say "Ollarma: $(ollarma_health) (optional; choose extractor=ollarma in UI/API when PASS)"
  say "Logs: $LOGDIR"
  say "Receipts: $RECEIPTDIR"
  say "From magicPRObox: ssh -N -L 18787:127.0.0.1:$SERVER_PORT magicstudio"
}

case "${1:-start}" in
  start) start_all ;;
  status) status ;;
  stop) stop ;;
  smoke) smoke ;;
  structural) preflight; prepare_hydradb; prepare_token; start_hydra; run_structural ;;
  restart) stop; start_all ;;
  *) echo "usage: $0 {start|status|stop|smoke|structural|restart}" >&2; exit 2 ;;
esac
