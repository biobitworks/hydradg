#!/usr/bin/env bash
set -euo pipefail

ROOT="${HYDRADG_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

echo "================================================================"
echo "HYDRADG HACK HYDRA RELEASE GATE"
echo "================================================================"
echo "ROOT=$ROOT"
cd "$ROOT"

fail() {
  echo "BLOCKER=$1"
  echo "RELEASE_READY=NO"
  exit "${2:-1}"
}

echo "--> [1/9] Required reproduction assets"
test -f README.md || fail README_MISSING 11
test -f SUBMISSION.md || fail SUBMISSION_DOC_MISSING 12
test -f docs/JUDGE_REPRODUCE_FROM_SCRATCH.md || fail JUDGE_REPRO_GUIDE_MISSING 13
test -f apps/hydradg-web/.env.example || fail ENV_EXAMPLE_MISSING 14
test -f apps/hydradg-web/package-lock.json || fail WEB_LOCKFILE_MISSING 15
test -f custody/graph/live/nodes.jsonl || fail FCG_NODES_SNAPSHOT_MISSING 16
test -f custody/graph/live/edges.jsonl || fail FCG_EDGES_SNAPSHOT_MISSING 17
test -f scripts/project_fcg_snapshot_to_hydradb.py || fail HYDRADB_IMPORTER_MISSING 18
test -f apps/hydradg-web/public/backup/hydradg.html || fail STATIC_FALLBACK_MISSING 19
test -f scripts/calculate_information_savings.py || fail INFORMATION_SAVINGS_CALCULATOR_MISSING 20
test -f eval/hosted_migration_20260820/information_savings/INPUT.json || fail INFORMATION_SAVINGS_INPUT_MISSING 21
test -f eval/hosted_migration_20260820/information_savings/INFORMATION_SAVINGS_RECEIPT_V2.json || fail INFORMATION_SAVINGS_RECEIPT_MISSING 22

echo "REPRO_ASSETS=PASS"

echo "--> [2/9] Validate canonical FCG JSONL syntax and edge closure"
python3 - <<'PY'
import json
from pathlib import Path
nodes_path = Path('custody/graph/live/nodes.jsonl')
edges_path = Path('custody/graph/live/edges.jsonl')
nodes = [json.loads(x) for x in nodes_path.read_text(encoding='utf-8').splitlines() if x.strip()]
edges = [json.loads(x) for x in edges_path.read_text(encoding='utf-8').splitlines() if x.strip()]
ids = [str(n.get('id','')) for n in nodes]
if not nodes or not edges:
    raise SystemExit('empty canonical graph snapshot')
if any(not x for x in ids):
    raise SystemExit('node without id')
if len(ids) != len(set(ids)):
    raise SystemExit('duplicate node id')
known = set(ids)
for edge in edges:
    if edge.get('source') not in known or edge.get('target') not in known:
        raise SystemExit(f"orphan edge: {edge}")
print(f"FCG_NODES={len(nodes)}")
print(f"FCG_EDGES={len(edges)}")
print('FCG_JSONL_CLOSURE=PASS')
PY

echo "--> [3/9] Deterministic information-savings calculator"
bash scripts/verify_information_savings.sh || fail INFORMATION_SAVINGS_GATE_FAILED 30

echo "--> [4/9] Web TypeScript typecheck"
(
  cd apps/hydradg-web
  npm ci
  npm run typecheck
) || fail TYPECHECK_FAILED 31

echo "--> [5/9] Web production build"
(
  cd apps/hydradg-web
  npm run build
) || fail BUILD_FAILED 41

echo "--> [6/9] Static fallback validation"
python3 scripts/check_static_fallback.py || fail STATIC_FALLBACK_VALIDATION_FAILED 51

echo "--> [7/9] Knowledge/link coverage checks"
python3 scripts/check_term_knowledge_coverage.py || fail KNOWLEDGE_COVERAGE_FAILED 61

echo "--> [8/9] Full-history Gitleaks scan"
command -v gitleaks >/dev/null 2>&1 || fail GITLEAKS_NOT_INSTALLED 71
mkdir -p custody/security/current-release
set +e
gitleaks git \
  --redact=100 \
  --no-banner \
  --report-format json \
  --report-path custody/security/current-release/gitleaks-release.json \
  .
GITLEAKS_STATUS=$?
set -e
if [ ! -f custody/security/current-release/gitleaks-release.json ]; then
  printf '[]\n' > custody/security/current-release/gitleaks-release.json
fi
if [ "$GITLEAKS_STATUS" -ne 0 ]; then
  echo "GITLEAKS_RELEASE=FAIL"
  fail GITLEAKS_FINDINGS 72
fi
echo "GITLEAKS_RELEASE=PASS"

echo "--> [9/9] Hash release reconstruction inputs"
python3 - <<'PY'
import hashlib, json
from pathlib import Path
paths = [
    Path('README.md'),
    Path('SUBMISSION.md'),
    Path('docs/JUDGE_REPRODUCE_FROM_SCRATCH.md'),
    Path('apps/hydradg-web/.env.example'),
    Path('apps/hydradg-web/package-lock.json'),
    Path('custody/graph/live/nodes.jsonl'),
    Path('custody/graph/live/edges.jsonl'),
    Path('scripts/project_fcg_snapshot_to_hydradb.py'),
    Path('scripts/calculate_information_savings.py'),
    Path('eval/hosted_migration_20260820/information_savings/INPUT.json'),
    Path('eval/hosted_migration_20260820/information_savings/INFORMATION_SAVINGS_RECEIPT_V2.json'),
]
entries = []
for path in paths:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    entries.append({'path': str(path), 'sha256': h})
out = Path('custody/REPRODUCTION_INPUT_SHA256_20260819.json')
out.write_text(json.dumps({'schema':'hydradg.reproduction_inputs.v1','files':entries}, indent=2, sort_keys=True)+'\n', encoding='utf-8')
print(f"REPRODUCTION_INPUT_MANIFEST={out}")
print(f"REPRODUCTION_INPUT_MANIFEST_SHA256={hashlib.sha256(out.read_bytes()).hexdigest()}")
PY

echo ""
echo "================================================================"
echo "REPRO_ASSETS=PASS"
echo "FCG_JSONL_CLOSURE=PASS"
echo "INFORMATION_SAVINGS_GATE=PASS"
echo "WEB_TYPECHECK=PASS"
echo "WEB_BUILD=PASS"
echo "STATIC_FALLBACK=PASS"
echo "KNOWLEDGE_COVERAGE=PASS"
echo "GITLEAKS_RELEASE=PASS"
echo "RELEASE_READY=YES"
echo "BLOCKER=NONE"
echo "================================================================"
