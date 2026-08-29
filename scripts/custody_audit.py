#!/usr/bin/env python3
"""HydraDG thin adapter for gsigmad custody auditor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GSD = Path("/Users/byron/projects/active/gettingsciencedone")
SEEDGRAPH = Path("/Users/byron/projects/active/seedgraph")
DEFAULT_OUT = ROOT / "eval/custody_audit_20260829"


def main() -> int:
    parser = argparse.ArgumentParser(description="HydraDG custody audit adapter")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seedgraph-root", type=Path, default=SEEDGRAPH)
    parser.add_argument("--no-repro", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(GSD / "src"))
    from gsigmad.custody_audit.runner import run_custody_audit

    receipt = run_custody_audit(
        out_dir=args.out_dir,
        hydradg_root=ROOT,
        seedgraph_root=args.seedgraph_root,
        run_reproducibility=not args.no_repro,
    )
    print(json.dumps({
        "ok": True,
        "out_dir": str(args.out_dir),
        "reproducibility_gate": receipt.get("reproducibility", {}).get("REPRODUCIBILITY_GATE"),
        "counts_by_audit_state": receipt.get("counts_by_audit_state"),
        "store_fail_count": receipt.get("store_audit", {}).get("fail_count"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
