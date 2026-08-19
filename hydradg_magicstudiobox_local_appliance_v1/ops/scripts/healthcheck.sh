#!/bin/zsh
set -euo pipefail
for url in \
  http://127.0.0.1:11434/api/tags \
  http://127.0.0.1:8787/health \
  http://127.0.0.1:3010/ \
  http://127.0.0.1:3010/api/iceberg
do
  if curl -fsS --max-time 5 "$url" >/dev/null; then
    echo "PASS $url"
  else
    echo "FAIL $url"
  fi
done
HOST="$(scutil --get LocalHostName 2>/dev/null || true)"
[[ -n "$HOST" ]] && echo "BONJOUR=http://$HOST.local:3010"
