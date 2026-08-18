#!/usr/bin/env bash
set -u

echo "HYDRADG_BACKEND_PREFLIGHT_V1"
echo "pwd=$(pwd)"
echo "python=$(python --version 2>&1 || true)"
echo "modal=$(modal --version 2>&1 || true)"
echo "kaggle=$(kaggle --version 2>&1 || true)"
echo "ssh=$(ssh -V 2>&1 || true)"
echo "curl=$(curl --version 2>/dev/null | head -n1 || true)"
echo "ollama_local=$(ollama --version 2>&1 || true)"

for host in magicstudiobox magicstudiobox.local; do
  if ssh -G "$host" >/dev/null 2>&1; then
    echo "ssh_config_${host}=PRESENT"
  else
    echo "ssh_config_${host}=NOT_RESOLVED"
  fi
done

if command -v kaggle >/dev/null 2>&1; then
  if kaggle kernels list -m --page-size 1 >/dev/null 2>&1; then
    echo "kaggle_auth=PASS"
  else
    echo "kaggle_auth=FAIL_OR_NEEDS_LOGIN"
  fi
else
  echo "kaggle_auth=CLI_MISSING"
fi

if command -v modal >/dev/null 2>&1; then
  if modal volume list >/dev/null 2>&1; then
    echo "modal_auth=PASS"
  else
    echo "modal_auth=FAIL"
  fi
else
  echo "modal_auth=CLI_MISSING"
fi
