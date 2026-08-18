#!/bin/bash

PKG="/Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7"
PY="/Users/byron/fco-venv/bin/python3"
OUT="$PKG/eval/xeno_magicstudiobox"
DEPS="$OUT/deps"

export PYTHONPATH="$DEPS${PYTHONPATH:+:$PYTHONPATH}"

"$PY" "$PKG/inputs/xeno/cafa6_governed_eval.py" \
  --table "$PKG/inputs/xeno/residual_table.jsonl" \
  --ckpt "$PKG/inputs/xeno/ckpt_latest.pt" \
  --out "$OUT/outputs" \
  --report-name cafa6_governed_eval_report.json \
  --seed 20260710 \
  >"$OUT/stdout.log" \
  2>"$OUT/stderr.log"

rc=$?

printf "%s\n" "$rc" > "$OUT/returncode.txt"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$OUT/finished_utc.txt"

exit "$rc"
