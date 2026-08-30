#!/usr/bin/env python3
"""Verify or build HydraDG SOLO NewInML successor recovery artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/newinml2026_solo/successor_recovery"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify() -> int:
    errors = []
    required = [
        OUT / "EXPERIMENT_MASTER_LEDGER.tsv",
        OUT / "statistics/STATISTICAL_REPRODUCIBILITY_RECEIPT.json",
        OUT / "figures/FIGURE_RECEIPTS.json",
        OUT / "REPRODUCE.md",
    ]
    for p in required:
        if not p.exists():
            errors.append(f"missing: {p}")
    rec_path = OUT / "statistics/STATISTICAL_REPRODUCIBILITY_RECEIPT.json"
    if rec_path.exists():
        rec = json.loads(rec_path.read_text())
        if rec.get("REPRODUCIBILITY_GATE") != "PASS":
            errors.append("statistics R1/R2/R3 gate FAIL")
        r1 = rec.get("R1", {}).get("combined_output_sha256")
        r2 = rec.get("R2", {}).get("combined_output_sha256")
        r3 = rec.get("R3", {}).get("combined_output_sha256")
        if not (r1 and r1 == r2 == r3):
            errors.append("R1/R2/R3 hash mismatch")
    figs = list((OUT / "figures").glob("FIG-*.png")) if (OUT / "figures").exists() else []
    if len(figs) < 7:
        errors.append(f"figure count {len(figs)} < 7")
    if errors:
        print("VERIFY FAIL:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("VERIFY PASS")
    print(json.dumps({"figure_count": len(figs), "statistics_gate": "PASS"}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="Verify existing artifacts")
    ap.add_argument("--build", action="store_true", help="Build all artifacts")
    args = ap.parse_args()
    if args.verify and not args.build:
        # Re-run statistics to confirm determinism
        subprocess.run([sys.executable, str(OUT / "statistics/run_statistics.py")], cwd=ROOT, check=True)
        return verify()
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/build_successor_recovery.py")], cwd=ROOT)
    if proc.returncode != 0:
        return proc.returncode
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
