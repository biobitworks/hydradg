#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
REPO="${HYDRADG_REPO:-/Users/byron/projects/active/hydradg}"
DEST="$REPO/local_matrix_harness"
mkdir -p "$DEST"
cp "$SRC"/scripts/* "$DEST"/
chmod +x "$DEST"/*
echo "Installed local harness: $DEST"
echo "No GitHub Actions used."
