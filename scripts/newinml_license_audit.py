#!/usr/bin/env python3
"""HydraDG wrapper for deterministic NewInML license + Anticube audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GSD = Path("/Users/byron/projects/active/gettingsciencedone")
DEFAULT_OUT = ROOT / "paper/newinml2026_solo/license_audit"


def main() -> int:
    parser = argparse.ArgumentParser(description="NewInML license audit wrapper")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    sys.path.insert(0, str(GSD / "src"))
    from gsigmad.license_audit import run_license_audit

    receipt = run_license_audit(hydradg_root=ROOT, out_dir=args.out_dir)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
