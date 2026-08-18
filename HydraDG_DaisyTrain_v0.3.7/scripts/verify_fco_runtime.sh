#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

KG_ENV="/Users/byron/projects/active/hydradg-knowledge-graph/env.sh"
if [[ -f "$KG_ENV" ]]; then
  source "$KG_ENV"
fi

echo "=== 1. FCO skill filesystem audit ==="
python scripts/audit_fco_skill.py
SKILL_RC=$?

echo
echo "=== 2. Live FCO/FCG journal verification ==="
python scripts/verify_live_custody.py \
  --require-agent \
  --require-model \
  --require-turn
GRAPH_RC=$?

echo
echo "=== 3. Runtime snapshot ==="
python scripts/snapshot_fco_runtime.py \
  --out handoff/FCO_RUNTIME_SNAPSHOT.json || true

echo
if [[ $SKILL_RC -eq 0 ]]; then
  echo "FCO_SKILL_FILESYSTEM=PASS"
else
  echo "FCO_SKILL_FILESYSTEM=FAIL"
fi
if [[ $GRAPH_RC -eq 0 ]]; then
  echo "FCO_TURN_KG=PASS"
else
  echo "FCO_TURN_KG=FAIL"
fi

echo
echo "IMPORTANT:"
echo "Filesystem skill presence does not prove Antigravity loaded/invoked it."
echo "In Antigravity run /skills and verify the exact FCO skill is listed."
echo "Run /hooks and verify any FCO enforcement hooks are active."
exit $(( SKILL_RC != 0 || GRAPH_RC != 0 ))
