#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:?usage: locate_xeno_command.sh /path/to/fractal-custody-objects}"
echo "Candidate repository references to cafa6_governed_eval.py:"
if command -v rg >/dev/null 2>&1; then
  rg -n --hidden --glob '!*.git/*' 'cafa6_governed_eval\.py|ckpt_latest\.pt|residual_table\.jsonl' "$ROOT" || true
else
  grep -RInE 'cafa6_governed_eval\.py|ckpt_latest\.pt|residual_table\.jsonl' "$ROOT" || true
fi
echo
echo "Candidate shell-history lines (local only; not copied into package):"
if [[ -f "$HOME/.zsh_history" ]]; then
  grep -n 'cafa6_governed_eval.py' "$HOME/.zsh_history" | tail -50 || true
fi
echo
echo "Freeze a chosen exact invocation into inputs/xeno/run_contract.json."
