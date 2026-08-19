#!/usr/bin/env bash
set -euo pipefail

# HydraDG Hack Hydra dataset acquisition for Track 01 + Track 03.
#
# Canonical intent:
#   Track 01: EnterpriseRAG-Bench + HERB
#   Track 03: LongMemEval-S cleaned + LongMemEval-V2 + BEAM
#
# Data is stored OUTSIDE the Git repository by default. This script records the
# exact Hugging Face repository revision resolved at acquisition time and
# computes per-file SHA-256 manifests after download. It does not claim dataset
# correctness, independent verification, or license permission beyond the
# upstream license metadata declared below.
#
# Usage:
#   bash pull_track01_track03_datasets.sh --track all --tier core
#   bash pull_track01_track03_datasets.sh --track 1 --tier core
#   bash pull_track01_track03_datasets.sh --track 3 --tier full
#
# core:
#   - full EnterpriseRAG-Bench
#   - full HERB
#   - LongMemEval-S cleaned
#   - LongMemEval-V2 without large trajectory screenshot archives
#   - BEAM 100K/500K/1M repository
# full additionally:
#   - LongMemEval-V2 trajectory screenshot archives
#   - BEAM-10M

TRACK="all"
TIER="core"
DATA_ROOT="${HYDRADG_DATASET_ROOT:-$HOME/.local/share/hydradg-datasets}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --track) TRACK="${2:-}"; shift 2 ;;
    --tier) TIER="${2:-}"; shift 2 ;;
    --data-root) DATA_ROOT="${2:-}"; shift 2 ;;
    -h|--help)
      sed -n '1,45p' "$0"
      exit 0
      ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ "$TRACK" =~ ^(1|3|all)$ ]] || { echo "ERROR: --track must be 1, 3, or all" >&2; exit 2; }
[[ "$TIER" =~ ^(core|full)$ ]] || { echo "ERROR: --tier must be core or full" >&2; exit 2; }

for cmd in curl jq python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "ERROR: missing required command: $cmd" >&2; exit 10; }
done

hf_cli() {
  if command -v hf >/dev/null 2>&1; then
    hf "$@"
  elif command -v uvx >/dev/null 2>&1; then
    uvx --from huggingface_hub hf "$@"
  else
    echo "ERROR: Hugging Face CLI not found. Install huggingface_hub or uv, then rerun." >&2
    echo "Example: uv tool install huggingface_hub" >&2
    return 127
  fi
}

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    python3 - "$1" <<'PY'
import hashlib,sys
h=hashlib.sha256()
with open(sys.argv[1],"rb") as f:
    for b in iter(lambda:f.read(1024*1024),b""):
        h.update(b)
print(h.hexdigest())
PY
  fi
}

repo_revision() {
  local repo="$1"
  curl -fsSL --retry 3 "https://huggingface.co/api/datasets/$repo" | jq -er '.sha'
}

hash_tree() {
  local dir="$1"
  local sums="$dir/SHA256SUMS.txt"
  local tmp="$dir/.SHA256SUMS.tmp.$$"
  : > "$tmp"
  (
    cd "$dir"
    find . -type f \
      ! -path './.cache/*' \
      ! -name 'SHA256SUMS.txt' \
      ! -name '.SHA256SUMS.tmp.*' \
      -print0 \
      | LC_ALL=C sort -z \
      | while IFS= read -r -d '' rel; do
          clean="${rel#./}"
          printf '%s  %s\n' "$(sha256_file "$clean")" "$clean"
        done
  ) > "$tmp"
  mv "$tmp" "$sums"
  sha256_file "$sums"
}

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RECEIPT_DIR="$DATA_ROOT/receipts"
CATALOG_TSV="$RECEIPT_DIR/dataset_catalog_${RUN_ID}.tsv"
RECEIPT_JSON="$RECEIPT_DIR/dataset_pull_${RUN_ID}.json"
mkdir -p "$DATA_ROOT" "$RECEIPT_DIR"
: > "$CATALOG_TSV"

export HF_XET_HIGH_PERFORMANCE="${HF_XET_HIGH_PERFORMANCE:-1}"

pull_dataset() {
  local track="$1"
  local repo="$2"
  local slug="$3"
  local license="$4"
  shift 4
  local dest="$DATA_ROOT/track${track}/${slug}"
  local rev
  rev="$(repo_revision "$repo")"
  mkdir -p "$dest"

  echo
  echo "[dataset] track=$track repo=$repo"
  echo "[dataset] revision=$rev"
  echo "[dataset] license=$license"
  echo "[dataset] destination=$dest"

  hf_cli download "$repo" --repo-type dataset --revision "$rev" --local-dir "$dest" "$@"

  local tree_sha
  tree_sha="$(hash_tree "$dest")"
  local bytes
  bytes="$(du -sk "$dest" | awk '{print $1 * 1024}')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$track" "$repo" "$rev" "$license" "$dest" "$tree_sha" >> "$CATALOG_TSV"
  echo "[dataset] tree_manifest_sha256=$tree_sha"
  echo "[dataset] approximate_bytes=$bytes"
}

if [[ "$TRACK" == "1" || "$TRACK" == "all" ]]; then
  # MIT. Synthetic enterprise corpus; benchmark canary means evaluation data
  # must not be used as training corpus.
  pull_dataset "01" "onyx-dot-app/EnterpriseRAG-Bench" "enterprise-rag-bench" "MIT"

  # CC-BY-NC-4.0. Keep private by default; do not redistribute in a public
  # release without an explicit license review for the intended use.
  pull_dataset "01" "Salesforce/HERB" "herb" "CC-BY-NC-4.0"
fi

if [[ "$TRACK" == "3" || "$TRACK" == "all" ]]; then
  # Existing Track 03 primary benchmark object.
  pull_dataset "03" "xiaowu0162/longmemeval-cleaned" "longmemeval-cleaned" "MIT" \
    longmemeval_s_cleaned.json README.md

  if [[ "$TIER" == "core" ]]; then
    pull_dataset "03" "xiaowu0162/longmemeval-v2" "longmemeval-v2" "Apache-2.0" \
      --exclude "trajectory_screenshots/*"
  else
    pull_dataset "03" "xiaowu0162/longmemeval-v2" "longmemeval-v2" "Apache-2.0"
  fi

  pull_dataset "03" "Mohammadta/BEAM" "beam" "CC-BY-SA-4.0"

  if [[ "$TIER" == "full" ]]; then
    pull_dataset "03" "Mohammadta/BEAM-10M" "beam-10m" "CC-BY-SA-4.0"
  fi
fi

python3 - "$CATALOG_TSV" "$RECEIPT_JSON" "$RUN_ID" "$TRACK" "$TIER" <<'PY'
import csv,hashlib,json,sys,time
catalog,out,run_id,track,tier=sys.argv[1:]
items=[]
with open(catalog,newline='') as f:
    for row in csv.reader(f,delimiter='\t'):
        if not row: continue
        tr,repo,revision,license_name,path,tree_sha=row
        items.append({
            "track":tr,
            "source":"HUGGING_FACE_DATASET_REPOSITORY",
            "repo_id":repo,
            "revision":revision,
            "license_declared_upstream":license_name,
            "local_path":path,
            "sha256_manifest":f"{path}/SHA256SUMS.txt",
            "sha256_manifest_sha256":tree_sha,
            "evidence_class":"EXTERNALLY_RETRIEVED_DATASET_BYTES",
            "claim_ceiling":"LOCAL_DATASET_BYTE_IDENTITIES_AFTER_DOWNLOAD_ONLY",
        })
obj={
    "schema":"hydradg.dataset_pull_receipt.v1",
    "run_id":run_id,
    "timestamp_unix":int(time.time()),
    "requested_track":track,
    "tier":tier,
    "datasets":items,
    "license_state":"UPSTREAM_LICENSE_METADATA_RECORDED_NOT_LEGAL_OPINION",
    "signature_state":"NOT_SIGNED",
    "merkle_state":"NOT_MERKLE_COMMITTED",
    "independent_verification_state":"NOT_ESTABLISHED_BY_THIS_PULL",
}
raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
obj["receipt_sha256"]=hashlib.sha256(raw).hexdigest()
with open(out,"w") as f:
    json.dump(obj,f,indent=2,sort_keys=True);f.write("\n")
print(json.dumps(obj,indent=2,sort_keys=True))
PY

echo
echo "DATASET_PULL_COMPLETE=YES"
echo "DATA_ROOT=$DATA_ROOT"
echo "RECEIPT=$RECEIPT_JSON"
echo "RECEIPT_SHA256=$(sha256_file "$RECEIPT_JSON")"
echo "NOTE=HERB is CC-BY-NC-4.0; keep it out of public redistribution until release-license review."
