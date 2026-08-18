#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:?usage: locate_historical_eca_source.sh /path/to/fractal-custody-objects}"
printf 'Searching %s\n' "$ROOT"
find "$ROOT" -type f \( \
  -iname '*eca*' -o \
  -iname '*rule30*' -o \
  -iname '*rule_30*' -o \
  -iname '*PREREG_eca_demo.json' -o \
  -iname '*RESULTS_eca_demo.json' -o \
  -iname '*STATS_eca_demo.json' \
\) -print | sort

printf '\nText references:\n'
if command -v rg >/dev/null 2>&1; then
  rg -n --hidden --glob '!*.git/*' \
    'FMO-EXP-ECA-DEMO-01|PREREG_eca_demo|RESULTS_eca_demo|STATS_eca_demo|Rule 30|Rule 90|Rule 110|Rule 184' \
    "$ROOT" || true
else
  grep -RInE \
    'FMO-EXP-ECA-DEMO-01|PREREG_eca_demo|RESULTS_eca_demo|STATS_eca_demo|Rule 30|Rule 90|Rule 110|Rule 184' \
    "$ROOT" || true
fi
