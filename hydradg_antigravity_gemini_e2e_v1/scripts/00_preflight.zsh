#!/bin/zsh
set -euo pipefail
ROOT="${HYDRADG_ROOT:-/Users/byron/projects/active/hydradg}"
EXPECTED="${HYDRADG_EXPECTED_LONGMEM_SHA:-d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442}"
OUT="${1:-/tmp/hydradg-e2e-preflight.txt}"

{
  echo "TIMESTAMP_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "ROOT=$ROOT"
  cd "$ROOT"
  echo "BRANCH=$(git branch --show-current)"
  echo "HEAD=$(git rev-parse HEAD)"
  echo "STATUS_BEGIN"
  git status --short
  echo "STATUS_END"
  git fetch origin >/dev/null 2>&1 || true
  echo "DIVERGENCE_BEGIN"
  git log --left-right --graph --oneline HEAD...origin/hack-hydra/submission-eligible-20260819 2>/dev/null | head -80 || true
  echo "DIVERGENCE_END"
  echo "TOOLS"
  for c in python3 node npm ollama ollarma git shasum curl; do
    printf "%s=" "$c"; command -v "$c" || true
  done
  echo "MODELS_BEGIN"
  ollama list 2>/dev/null || true
  echo "MODELS_END"
  echo "LISTENERS_BEGIN"
  lsof -nP -iTCP:11434 -iTCP:8787 -iTCP:3010 -sTCP:LISTEN 2>/dev/null || true
  echo "LISTENERS_END"
} | tee "$OUT"

echo "PREFLIGHT_RECEIPT=$OUT"
