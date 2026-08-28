#!/usr/bin/env python3
"""EXP-010 prereg pipeline and optional execute (lease-gated)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from daisy_overnight.exp010 import run_prereg_pipeline  # noqa: E402


def validate_work_units(exp_dir: Path) -> None:
    checker = ROOT / "scripts/check_orchestration_work_unit.py"
    for path in sorted((exp_dir / "work_units").glob("T010-*.json")):
        code = subprocess.call(["python3", str(checker), str(path)])
        if code != 0:
            raise SystemExit(f"orchestration check failed: {path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--phase", choices=["exp010-prereg", "exp010-lease-check"], default="exp010-prereg")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()

    if args.phase == "exp010-prereg":
        result = run_prereg_pipeline(repo)
        exp_dir = repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP-010"
        validate_work_units(exp_dir)
        print(
            json.dumps(
                {
                    "EXP-010": "PREREG_FROZEN",
                    "required_paired_n": result["power"]["required_paired_n_worst_case_mde_grid"],
                    "e06_cases": result["bank_manifest"]["e06_primary_cases"],
                    "power_gate": result["bank_manifest"]["power_gate_satisfied"],
                    "plan_check": result["review"]["terminal_state"],
                    "runtime_lease": result["lease"]["terminal_state"],
                    "execute_permitted": result["lease"]["exp010_execute_permitted"],
                },
                indent=2,
            )
        )
        if not result["lease"]["exp010_execute_permitted"]:
            print(json.dumps({"T010-F": "BLOCKED_RUNTIME_LEASE", "reason": "Q38 replay active on shared Ollama"}, indent=2))
            return 0
    if args.phase == "exp010-lease-check":
        from daisy_overnight.exp010 import check_runtime_lease

        lease = check_runtime_lease()
        print(json.dumps(lease, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
