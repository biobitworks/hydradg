#!/usr/bin/env bash
# Sync magicSTUDIObox → magicPRObox local rebuild bundle.
# Includes: citations, experiments, lab notebooks, atom sources, eval JSON, datasets.
# Does NOT copy live OrbStack DB volumes (query Studio via SSH/tunnel instead).
set -euo pipefail

STUDIO="${STUDIO:-magicSTUDIObox.local}"
PRO="${PRO:-/Users/byron/projects}"
BUNDLE="${BUNDLE:-$PRO/active/hydradg/.pro-local-rebuild}"
SYNC_DATASETS="${SYNC_DATASETS:-1}"
SYNC_RESEARCH_PDFS="${SYNC_RESEARCH_PDFS:-0}"

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }

mkdir -p "$BUNDLE"/{overwatch/data,overwatch/experiments,overwatch/docs/notebooks,seedgraph/data,gettingsciencedone,hydradg-runtime/{eval,best-use,datasets},atoms,research_hub/literature/papers,watchtower}

log "=== Git fast-forward (integration arbiter) ==="
for r in hydradg overwatch watchtower gettingsciencedone; do
  git -C "$PRO/active/$r" fetch origin
  git -C "$PRO/active/$r" pull --ff-only origin main || log "WARN: $r main not ff-only — resolve manually"
done
# seedgraph may diverge; fetch only
git -C "$PRO/active/seedgraph" fetch origin || true

log "=== Tier 1: Citations & ingest JSONL ==="
rsync -az "$STUDIO:$PRO/active/overwatch/data/ingest/" "$BUNDLE/overwatch/data/ingest/"
rsync -az "$STUDIO:$PRO/active/overwatch/data/references/" "$BUNDLE/overwatch/data/references/"
rsync -az "$STUDIO:$PRO/active/seedgraph/data/intake/" "$BUNDLE/seedgraph/data/intake/"

log "=== Tier 2: Experiments & lab notebooks ==="
rsync -az "$STUDIO:$PRO/active/overwatch/experiments/" "$BUNDLE/overwatch/experiments/"
rsync -az "$STUDIO:$PRO/active/gettingsciencedone/experiments/" "$BUNDLE/gettingsciencedone/experiments/"
rsync -az "$STUDIO:$PRO/active/hydradg/eval/" "$BUNDLE/hydradg-runtime/eval/"
rsync -az "$STUDIO:$PRO/active/overwatch/docs/notebooks/" "$BUNDLE/overwatch/docs/notebooks/" 2>/dev/null || true
rsync -az "$STUDIO:$PRO/active/watchtower/LAB_NOTEBOOK.md" "$BUNDLE/watchtower/" 2>/dev/null || true

log "=== Tier 3: Atom sources ==="
rsync -az "$STUDIO:$PRO/active/hydradg/custody/graph/live/" "$BUNDLE/atoms/hydradg-fcg-live/"
rsync -az "$STUDIO:$HOME/.config/seedgraph/store/" "$BUNDLE/atoms/seedgraph-store/"
rsync -az "$STUDIO:/Volumes/magicLABbox/databases/seedgraph/sources/" "$BUNDLE/atoms/seedgraph-sources/" 2>/dev/null || log "WARN: magicLABbox sources unavailable"

log "=== Tier 4: HydraDG runtime eval (no secrets) ==="
rsync -az "$STUDIO:$HOME/.local/share/hydradg-best-use/eval/" "$BUNDLE/hydradg-runtime/best-use/eval/"
rsync -az "$STUDIO:$HOME/.local/share/hydradg-best-use/receipts/" "$BUNDLE/hydradg-runtime/best-use/receipts/"
rsync -az "$STUDIO:$HOME/.local/share/hydradg-best-use/data/" "$BUNDLE/hydradg-runtime/best-use/data/"
# NEVER rsync hydradb-auth-token

if [ "$SYNC_DATASETS" = "1" ]; then
  log "=== Tier 5: Dataset bytes (~2.8GB) ==="
  rsync -az "$STUDIO:$HOME/.local/share/hydradg-datasets/" "$BUNDLE/hydradg-runtime/datasets/"
fi

log "=== Tier 6: Research hub citations ==="
if [ "$SYNC_RESEARCH_PDFS" = "1" ]; then
  rsync -az "$STUDIO:$PRO/research_hub/literature/papers/" "$BUNDLE/research_hub/literature/papers/"
else
  rsync -az --include='*/' --include='metadata.json' --include='*.json' --include='*.jsonl' --include='*.bib' --exclude='*' \
    "$STUDIO:$PRO/research_hub/literature/papers/" "$BUNDLE/research_hub/literature/papers/"
fi

log "=== Receipt ==="
python3 "$PRO/active/hydradg/scripts/emit_pro_studio_sync_receipt.py" --bundle "$BUNDLE" --studio "$STUDIO"
log "DONE. Bundle: $BUNDLE"
