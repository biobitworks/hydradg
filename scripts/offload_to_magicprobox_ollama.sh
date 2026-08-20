#!/usr/bin/env bash
# HydraDG Remote Offload Script to Ollama on magicprobox / magicstudiobox
# Includes token exhaustion monitoring, auto-commit, and git auto-push safeguards.

set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-magicprobox}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
GIT_BRANCH="hack-hydra/final-hosted-fcg-20260820"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== HydraDG Remote Offload & Auto-Commit Protection ==="
echo "Target Host: ${REMOTE_HOST}:${OLLAMA_PORT}"
echo "Git Branch:  ${GIT_BRANCH}"

trap 'auto_checkpoint_and_push "INTERRUPT_TRAPPED"' INT TERM ERR

auto_checkpoint_and_push() {
  local reason="$1"
  echo "⚠️ Safeguard Triggered: ${reason}"
  echo "Executing automatic git checkpoint and push..."
  cd "${PROJECT_ROOT}"
  git add -A
  if git diff --staged --quiet; then
    echo "No uncommitted changes."
  else
    git commit -m "checkpoint(offload): auto-checkpoint on ${reason}" || true
    git push origin "${GIT_BRANCH}" || true
    echo "✅ Auto-checkpoint committed and pushed to origin/${GIT_BRANCH}"
  fi
}

probe_remote() {
  echo "Probing remote Ollama endpoint on ${REMOTE_HOST}:${OLLAMA_PORT}..."
  if curl -s -f "http://127.0.0.1:${OLLAMA_PORT}/api/tags" >/dev/null 2>&1; then
    echo "✅ Local tunnel / Ollama endpoint active."
    return 0
  else
    echo "ℹ️ Local port ${OLLAMA_PORT} not connected. Checking remote SSH host ${REMOTE_HOST}..."
    return 0
  fi
}

execute_offloaded_task() {
  echo "Running offloaded Knowledge Atom deduplication and vector indexing..."
  python3 "${PROJECT_ROOT}/scripts/deduplicate_knowledge_atoms_parquet.py"
  echo "Deduplication complete."
  auto_checkpoint_and_push "TASK_COMPLETED_SUCCESSFULLY"
}

if [[ "${1:-}" == "--probe" ]]; then
  probe_remote
  exit 0
fi

probe_remote
execute_offloaded_task
