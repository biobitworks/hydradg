#!/usr/bin/env bash
set -euo pipefail
ATOM_ROOT=""
SEEDGRAPH_ROOT="${SEEDGRAPH_ROOT:-/Users/byron/projects/active/seedgraph}"
OPERATOR=""
EXPECTED_BRANCH="hack-hydra/dataset-atom-bundle-20260819"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --atom-root) ATOM_ROOT="${2:-}"; shift 2 ;;
    --seedgraph-root) SEEDGRAPH_ROOT="${2:-}"; shift 2 ;;
    --operator) OPERATOR="${2:-}"; shift 2 ;;
    *) echo "ERROR: unknown argument $1" >&2; exit 2 ;;
  esac
done
[[ -n "$ATOM_ROOT" && -d "$ATOM_ROOT" ]] || { echo "ERROR: --atom-root directory required" >&2; exit 2; }
[[ -n "$OPERATOR" ]] || { echo "ERROR: --operator required" >&2; exit 2; }
[[ -d "$SEEDGRAPH_ROOT/.git" ]] || { echo "ERROR: SeedGraph repo missing: $SEEDGRAPH_ROOT" >&2; exit 3; }
[[ "$(git -C "$SEEDGRAPH_ROOT" branch --show-current)" == "$EXPECTED_BRANCH" ]] || {
  echo "ERROR: SeedGraph must be on $EXPECTED_BRANCH" >&2; exit 4;
}
[[ -f "$HOME/.config/seedgraph/signing_key.pem" ]] || {
  echo "ERROR: SeedGraph signing key is not initialized. Review locally, then run 'uv run seedgraph init' from SeedGraph if appropriate." >&2
  exit 5
}
command -v uv >/dev/null 2>&1 || { echo "ERROR: uv required" >&2; exit 6; }

OUT="$ATOM_ROOT/seedgraph_admission"
mkdir -p "$OUT/imports" "$OUT/reingest_gate_receipts"
LIST="$OUT/objects.txt"
find "$ATOM_ROOT" -type f \( \
    -name 'fco_nodes.jsonl' -o \
    -name 'fcg_edges.jsonl' -o \
    -name 'ATOMIZATION_RECEIPT.json' -o \
    -name 'FULL_ATOMIZATION_BATCH_RECEIPT.json' \
  \) ! -path "$OUT/*" -print | LC_ALL=C sort > "$LIST"
[[ -s "$LIST" ]] || { echo "ERROR: no atom-bundle files found" >&2; exit 7; }

index=0
while IFS= read -r source; do
  index=$((index+1))
  base="$(basename "$source")"
  tag="$(printf '%04d' "$index")-$(echo "$source" | shasum -a 256 | awk '{print substr($1,1,16)}')-$base"
  result="$OUT/imports/$tag.import.json"
  gate="$OUT/reingest_gate_receipts/$tag.gate.json"
  (
    cd "$SEEDGRAPH_ROOT"
    uv run seedgraph import "$source" \
      --type evidence \
      --json \
      --no-require-publication-reingest-gate \
      --publication-reingest-not-applicable "Hack Hydra deterministic dataset FCO/FCG atom bundle; not a publication-family reingest" \
      --publication-reingest-operator "$OPERATOR" \
      --publication-reingest-receipt "$gate"
  ) > "$result"
  python3 - "$result" <<'PY'
import json,sys
p=sys.argv[1]
j=json.load(open(p))
if not isinstance(j,list) or not j:
    raise SystemExit(f"invalid SeedGraph import result: {p}")
for row in j:
    if row.get("status") not in {"created","duplicate"}:
        raise SystemExit(f"SeedGraph atom-bundle admission failed: {row}")
print("SEEDGRAPH_ATOM_BUNDLE_OBJECT_ADMITTED",p)
PY
done < "$LIST"

python3 - "$ATOM_ROOT" "$OUT" "$SEEDGRAPH_ROOT" <<'PY'
import hashlib,json,pathlib,subprocess,sys
atom=pathlib.Path(sys.argv[1]).resolve(); out=pathlib.Path(sys.argv[2]).resolve(); sg=pathlib.Path(sys.argv[3]).resolve()
def sh(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
imports=[]
for p in sorted((out/'imports').glob('*.json')):
 rows=json.load(open(p))
 imports.append({"path":str(p),"sha256":sh(p),"results":rows})
obj={
 "schema":"hydradg.seedgraph_atom_bundle_admission.v1",
 "atom_root":str(atom),
 "seedgraph_commit":subprocess.check_output(['git','-C',str(sg),'rev-parse','HEAD'],text=True).strip(),
 "seedgraph_branch":subprocess.check_output(['git','-C',str(sg),'branch','--show-current'],text=True).strip(),
 "objects":imports,
 "object_count":len(imports),
 "claim_ceiling":"SEEDGRAPH_CONTENT_ADDRESSED_ATOM_BUNDLE_ADMISSION_ONLY_NOT_NATIVE_PER_ATOM_SEEDGRAPH_GRAPH_MATERIALIZATION",
 "signature_state":"SEEDGRAPH_LEDGER_ENTRY_STATE_RECORDED_PER_IMPORT_HYDRADG_AUTHOR_SIGNATURE_NOT_CLAIMED",
 "hydradb_merkle_state":"NOT_APPLICABLE_TO_THIS_ADMISSION",
}
raw=json.dumps(obj,sort_keys=True,separators=(',',':')).encode();obj['receipt_sha256']=hashlib.sha256(raw).hexdigest()
p=out/'SEEDGRAPH_ATOM_BUNDLE_ADMISSION_RECEIPT.json';p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
print(json.dumps(obj,indent=2,sort_keys=True))
print('SEEDGRAPH_ATOM_BUNDLE_ADMISSION_COMPLETE=YES')
print('RECEIPT='+str(p))
print('RECEIPT_FILE_SHA256='+sh(p))
PY
