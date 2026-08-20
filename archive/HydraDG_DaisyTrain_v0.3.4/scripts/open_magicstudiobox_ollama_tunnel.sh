#!/usr/bin/env bash
set -euo pipefail
HOST="${1:-magicstudiobox}"
LOCAL_PORT="${2:-11434}"

echo "Opening loopback-only Ollama tunnel:"
echo "127.0.0.1:${LOCAL_PORT} -> ${HOST}:127.0.0.1:11434"
exec ssh -N \
  -o ExitOnForwardFailure=yes \
  -L "127.0.0.1:${LOCAL_PORT}:127.0.0.1:11434" \
  "$HOST"
