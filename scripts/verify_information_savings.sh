#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail

ROOT="${HYDRADG_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

INPUT="eval/hosted_migration_20260820/information_savings/INPUT.json"
OUTPUT="eval/hosted_migration_20260820/information_savings/INFORMATION_SAVINGS_RECEIPT_V2.json"
CALCULATOR="scripts/calculate_information_savings.py"

echo "--> Verify deterministic retained information-savings receipt"
python3 "$CALCULATOR" --input "$INPUT" --output "$OUTPUT" --verify

TMPDIR_PATH="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_PATH"' EXIT

python3 - "$INPUT" "$TMPDIR_PATH/conflicting.json" <<'PY'
import json, sys
from pathlib import Path
src = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
src["download_files"] = [
    {"path": "a.bin", "size_bytes": 10, "sha256": "a" * 64},
    {"path": "b.bin", "size_bytes": 11, "sha256": "a" * 64},
]
Path(sys.argv[2]).write_text(json.dumps(src, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

set +e
python3 "$CALCULATOR" \
  --input "$TMPDIR_PATH/conflicting.json" \
  --output "$TMPDIR_PATH/should-not-exist.json" \
  >"$TMPDIR_PATH/negative.stdout" 2>"$TMPDIR_PATH/negative.stderr"
NEGATIVE_STATUS=$?
set -e

if [ "$NEGATIVE_STATUS" -eq 0 ]; then
  echo "INFORMATION_SAVINGS_NEGATIVE_TEST=FAIL"
  echo "Calculator accepted same SHA-256 with conflicting byte sizes."
  exit 1
fi

if ! grep -q "same SHA-256 has conflicting sizes" "$TMPDIR_PATH/negative.stderr"; then
  echo "INFORMATION_SAVINGS_NEGATIVE_TEST=FAIL"
  cat "$TMPDIR_PATH/negative.stderr"
  exit 1
fi

echo "INFORMATION_SAVINGS_NEGATIVE_TEST=PASS"
echo "INFORMATION_SAVINGS_GATE=PASS"
