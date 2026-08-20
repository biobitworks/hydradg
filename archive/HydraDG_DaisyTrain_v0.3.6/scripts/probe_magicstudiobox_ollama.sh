#!/usr/bin/env bash
set -euo pipefail
HOST="${1:-magicstudiobox}"

echo "OLLAMA_REMOTE_PROBE_V1"
echo "host=$HOST"

ssh -o BatchMode=yes -o ConnectTimeout=8 "$HOST" '
  set -e
  echo "remote_host=$(hostname)"
  echo "ollama_version=$(ollama --version 2>&1 || true)"
  echo "disk:"
  df -h . | tail -n 1
  echo "models:"
  ollama list 2>&1 || true
  echo "api_tags:"
  curl -fsS http://127.0.0.1:11434/api/tags
'
