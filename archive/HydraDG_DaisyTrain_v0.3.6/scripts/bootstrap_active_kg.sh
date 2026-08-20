#!/usr/bin/env bash
set -euo pipefail

KG_HOME="${HYDRADG_KG_HOME:-/Users/byron/projects/active/hydradg-knowledge-graph}"
PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

dirs=(
  graph/live graph/internal graph/anonymous
  seedgraph/review seedgraph/bridge seedgraph/exports
  hydradb/pins hydradb/receipts hydradb/exports
  agents models turns tool_actions knowledge_updates
  sources/internal sources/anonymous
  claims evidence perturbations recoveries
  submissions/hack-hydra
  submissions/newinml/internal submissions/newinml/anonymous
  schemas receipts figures exports docs logs
)

mkdir -p "$KG_HOME"
for d in "${dirs[@]}"; do
  mkdir -p "$KG_HOME/$d"
done

touch "$KG_HOME/graph/live/nodes.jsonl"
touch "$KG_HOME/graph/live/edges.jsonl"

cp "$PACKAGE_ROOT/SEEDGRAPH_SUBMISSION_REVIEW.md" \
   "$KG_HOME/seedgraph/review/SEEDGRAPH_SUBMISSION_REVIEW.md"
cp "$PACKAGE_ROOT/seedgraph/bridge_schema.json" \
   "$KG_HOME/seedgraph/bridge/bridge_schema.json"
cp "$PACKAGE_ROOT/AGENT_MODEL_TURN_FCO_POLICY.md" \
   "$KG_HOME/docs/AGENT_MODEL_TURN_FCO_POLICY.md"
cp "$PACKAGE_ROOT/hydra/schema_nodes.json" \
   "$KG_HOME/schemas/hydradg_schema_nodes.json"
cp "$PACKAGE_ROOT/hydra/schema_edges.json" \
   "$KG_HOME/schemas/hydradg_schema_edges.json"
cp "$PACKAGE_ROOT/config/kg_home.json" \
   "$KG_HOME/schemas/kg_home.json"

if [[ -f "$PACKAGE_ROOT/MANIFEST.json" ]]; then
  cp "$PACKAGE_ROOT/MANIFEST.json" "$KG_HOME/receipts/current_package_manifest.json"
fi
if [[ -f "$PACKAGE_ROOT/SHA256SUMS.txt" ]]; then
  cp "$PACKAGE_ROOT/SHA256SUMS.txt" "$KG_HOME/receipts/current_package_SHA256SUMS.txt"
fi

cat > "$KG_HOME/env.sh" <<EOF
export HYDRADG_KG_HOME="$KG_HOME"
export HYDRADG_LIVE_GRAPH_DIR="$KG_HOME/graph/live"
export HYDRADG_INTERNAL_GRAPH_DIR="$KG_HOME/graph/internal"
export HYDRADG_ANON_GRAPH_DIR="$KG_HOME/graph/anonymous"
EOF

cat > "$KG_HOME/README.md" <<EOF
# HydraDG / FCO-FCG durable knowledge-graph home

Created by HydraDG Daisy Train v0.3.6.

This directory is intentionally outside versioned HydraDG ZIP folders so agent/model
turn custody and submission evidence survive package upgrades.

Primary live append-only journal:
- graph/live/nodes.jsonl
- graph/live/edges.jsonl

Internal submission graph:
- graph/internal/

Anonymous review graph:
- graph/anonymous/

SeedGraph review/bridge:
- seedgraph/review/
- seedgraph/bridge/

HydraDB state:
- hydradb/

Source this before agent/model custody commands:
\`\`\`bash
source "$KG_HOME/env.sh"
\`\`\`

The live JSONL journal is not itself a HydraDB database. HydraDB ingestion requires a
separate successful write/read receipt.

Signature state: NOT_SIGNED unless a separate signing operation is performed.
Merkle state: NOT_MERKLE_COMMITTED unless a separate commitment operation is performed.
EOF

printf '%s\n' "$PACKAGE_ROOT" > "$KG_HOME/CURRENT_PACKAGE_PATH.txt"

echo "KG_HOME=$KG_HOME"
echo "LIVE_GRAPH=$KG_HOME/graph/live"
echo "ENV_FILE=$KG_HOME/env.sh"
echo "SEEDGRAPH_REVIEW=$KG_HOME/seedgraph/review/SEEDGRAPH_SUBMISSION_REVIEW.md"
