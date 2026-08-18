#!/usr/bin/env bash
set -euo pipefail

# HydraDG local/private-first Hack Hydra MVP bootstrap.
# Designed for magicstudiobox or another Docker-capable host.
# It binds HydraDB and Next.js to loopback by default. Put a reviewed secure
# reverse proxy/tunnel in front of the web app if remote access is needed.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEB="$ROOT/apps/hydradg-web"
RUNTIME="${HYDRADG_RUNTIME_DIR:-$HOME/.hydradg-hackhydra}"
DATA="$RUNTIME/hydradb"
TOKEN_FILE="$DATA/auth-token"
ENV_FILE="$RUNTIME/hydradg.env"
HYDRA_IMAGE="${HYDRADB_IMAGE:-ghcr.io/hydra-db/hydradb:latest}"
WEB_PORT="${HYDRADG_WEB_PORT:-3000}"

command -v docker >/dev/null || { echo "docker is required" >&2; exit 2; }
command -v node >/dev/null || { echo "node is required" >&2; exit 2; }
command -v npm >/dev/null || { echo "npm is required" >&2; exit 2; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 2; }

mkdir -p "$DATA/store" "$DATA/cache" "$RUNTIME/logs"
chmod 700 "$RUNTIME" "$DATA"

if [[ ! -s "$TOKEN_FILE" ]]; then
  python3 - "$TOKEN_FILE" <<'PY'
import secrets,sys
from pathlib import Path
p=Path(sys.argv[1])
p.write_text(secrets.token_urlsafe(32)+'\n')
p.chmod(0o600)
PY
fi
TOKEN="$(tr -d '\r\n' < "$TOKEN_FILE")"

cat > "$ENV_FILE" <<EOF
GRAPH_BACKEND=hydradb-http
HYDRADB_HTTP_URL=http://127.0.0.1:8443
HYDRADB_GRAPH_ID=default
HYDRADB_GRAPH_NAMESPACE=default
HYDRADB_CELL_ID=cell-0
HYDRADB_AUTH_TOKEN=$TOKEN
EOF
chmod 600 "$ENV_FILE"

if docker ps -a --format '{{.Names}}' | grep -qx hydradg-hydradb; then
  docker rm -f hydradg-hydradb >/dev/null 2>&1 || true
fi

docker pull "$HYDRA_IMAGE"
docker image inspect "$HYDRA_IMAGE" --format '{{json .RepoDigests}}' > "$RUNTIME/hydradb-image-digest.json"
docker run -d --name hydradg-hydradb \
  --restart unless-stopped \
  --user "$(id -u):$(id -g)" \
  -p 127.0.0.1:7687:7687 \
  -p 127.0.0.1:8443:8443 \
  -p 127.0.0.1:9090:9090 \
  -v "$DATA:/data" \
  -e CLOUD_PROVIDER=local \
  -e LOCAL_PATH=/data/store \
  -e GRAPH_NAMESPACE=default \
  -e GRAPH_ID=default \
  -e GRAPH_CELL_ID=cell-0 \
  -e GRAPH_CELLS=cell-0 \
  -e GRAPH_NODE_ID=node-0 \
  -e GRAPH_BOLT_NODE_ADDRESSES=node-0=127.0.0.1:7687 \
  -e GRAPH_ADVERTISED_BOLT_ADDR=127.0.0.1:7687 \
  -e GRAPH_DATA_CACHE_DIR=/data/cache \
  -e GRAPH_AUTH_TOKEN_FILE=/data/auth-token \
  -e GRAPH_ALLOW_PLAINTEXT=true \
  -e RUST_MIN_STACK=33554432 \
  "$HYDRA_IMAGE" >/dev/null

for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:9090/readyz > "$RUNTIME/hydradb-ready.txt" 2>/dev/null; then
    break
  fi
  sleep 2
done
curl -fsS http://127.0.0.1:9090/readyz >/dev/null || {
  docker logs hydradg-hydradb >&2
  exit 3
}

# Direct HydraDB round trip. Mutation and read are separate because HydraDB's
# supported OpenCypher subset accepts one statement per request.
curl -fsS http://127.0.0.1:8443/v1/graphs/default/query \
  -H "Authorization: Bearer $TOKEN" \
  -H 'X-Graph-Namespace: default' \
  -H 'Content-Type: application/json' \
  --data '{"cell_id":"cell-0","query":"MERGE (a:HostProbe {id: 91001})-[:ROUND_TRIP]->(b:HostProbe {id: 91002})"}' \
  > "$RUNTIME/direct-write.json"
curl -fsS http://127.0.0.1:8443/v1/graphs/default/query \
  -H "Authorization: Bearer $TOKEN" \
  -H 'X-Graph-Namespace: default' \
  -H 'Content-Type: application/json' \
  --data '{"cell_id":"cell-0","query":"MATCH (a:HostProbe {id: 91001})-[:ROUND_TRIP]->(b) RETURN b.id AS id"}' \
  > "$RUNTIME/direct-read.json"
python3 - "$RUNTIME/direct-read.json" <<'PY'
import json,sys
obj=json.load(open(sys.argv[1]))
assert obj.get('rows'), obj
PY

cd "$WEB"
npm install --no-audit --no-fund
npm run typecheck
npm run build

if [[ -f "$RUNTIME/web.pid" ]] && kill -0 "$(cat "$RUNTIME/web.pid")" 2>/dev/null; then
  kill "$(cat "$RUNTIME/web.pid")" || true
fi
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
nohup npm run start -- -H 127.0.0.1 -p "$WEB_PORT" > "$RUNTIME/logs/web.log" 2>&1 &
echo $! > "$RUNTIME/web.pid"

for _ in $(seq 1 40); do
  if curl -fsS "http://127.0.0.1:$WEB_PORT/api/status" > "$RUNTIME/status.json" 2>/dev/null; then
    break
  fi
  sleep 1
done
curl -fsS "http://127.0.0.1:$WEB_PORT/api/status" > "$RUNTIME/status.json"
curl -fsS -X POST "http://127.0.0.1:$WEB_PORT/api/query" \
  -H 'Content-Type: application/json' --data '{"action":"fixture"}' > "$RUNTIME/fixture.json"

python3 - "$RUNTIME/status.json" "$RUNTIME/fixture.json" "$RUNTIME" "$WEB_PORT" <<'PY'
import json,sys,subprocess,pathlib
status=json.load(open(sys.argv[1]))
fixture=json.load(open(sys.argv[2]))['fixture']
runtime=pathlib.Path(sys.argv[3]); port=sys.argv[4]
assert status['graph']['reachable'] is True, status
assert len(fixture['timeline']) == 3, fixture
assert [x['label'] for x in fixture['timeline']] == ['reference','mutation','restoration']
ids=fixture['ids']; subject=fixture['subject_key']
def post(payload,name):
    raw=subprocess.check_output([
        'curl','-fsS','-X','POST',f'http://127.0.0.1:{port}/api/query',
        '-H','Content-Type: application/json','--data',json.dumps(payload)
    ])
    (runtime/name).write_bytes(raw)
    return json.loads(raw)
current=post({'action':'current','subject_key':subject},'current.json')
history=post({'action':'history','id':ids['seed_v1']},'history.json')
provenance=post({'action':'provenance','id':ids['seed_v2']},'provenance.json')
assert any('beta' in str(row.get('payload','')).lower() for row in current.get('rows',[])), current
assert any(row.get('relation') == 'SUPERSEDED_BY' for row in history.get('rows',[])), history
relations={hop.get('relation') for hop in provenance.get('hops',[])}
assert {'SUPPORTED_BY','DERIVED_FROM'} <= relations, provenance
PY

curl -fsS "http://127.0.0.1:$WEB_PORT/" >/dev/null
curl -fsS "http://127.0.0.1:$WEB_PORT/demo" >/dev/null
curl -fsS "http://127.0.0.1:$WEB_PORT/graph" >/dev/null
curl -fsS "http://127.0.0.1:$WEB_PORT/eligibility" >/dev/null

cd "$ROOT"
python3 scripts/build_fcg_root.py

cat <<EOF
HYDRADG_MAGICSTUDIOBOX_SMOKE=PASS
web=http://127.0.0.1:$WEB_PORT
runtime=$RUNTIME
hydradb_image_digest=$(cat "$RUNTIME/hydradb-image-digest.json")
author_signature_state=$(python3 -c 'import json; print(json.load(open("custody/live/manifest.json"))["author_signature_state"])')
NOTE: services are loopback-only. Configure reviewed remote access separately.
EOF
