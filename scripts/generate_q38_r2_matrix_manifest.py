#!/usr/bin/env python3
"""Pre-execution MATRIX_MANIFEST generator for Q38-EXP008-R2 / Q38-EXP009-R2."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from daisy_overnight.atoms import (  # noqa: E402
    CONTEXT_CHAR_BUDGET,
    load_admissible_atoms,
    order_atoms_causal,
    order_atoms_neutral,
    render_flat_prose,
    render_ordered_context,
    render_structured_fcg,
    select_atoms,
    structured_retriever_atoms,
)
from daisy_overnight.custody import sha256_bytes  # noqa: E402
from run_qwen38_model_replay import build_prompt, N_REPLICATES, SKILL_CONDENSED, OUTPUT_SCHEMA  # noqa: E402

Q38_27B = "qwen3.8:27b"
Q38_27B_DIGEST = "22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643"
FLASH_NEXT = "qwen3.8-flash-next:125b-a6b-nvfp4"
FLASH_NEXT_DIGEST = "PENDING_DAYTONA_CANARY_FREEZE"


def cell_id(case_id: str, condition: str, replicate: int, model: str) -> str:
    model_tag = "Q38_27B" if model == Q38_27B else "FLASH_NEXT"
    return f"{case_id}|{condition}|r{replicate}|{model_tag}"


def exp008_context(case: dict, condition: str, atoms: list) -> tuple[str, list[str], str]:
    fam = case["experiment_family"]
    selected = select_atoms(atoms, fam)
    if condition == "C0":
        context, retained = render_flat_prose(selected, CONTEXT_CHAR_BUDGET)
        label = "FLAT_PROSE"
    else:
        context, retained = render_structured_fcg(selected, CONTEXT_CHAR_BUDGET)
        label = "STRUCTURED_FCG"
    return context, retained, label


def exp009_context(case: dict, condition: str, atoms_lib: list) -> tuple[str, list[str], str]:
    fam = case["experiment_family"]
    selected_atoms, retained_ids = structured_retriever_atoms(atoms_lib, fam, CONTEXT_CHAR_BUDGET)
    id_set = set(retained_ids)
    if condition == "C0":
        ordered = order_atoms_neutral([a for a in selected_atoms if a["fco_id"] in id_set])
        label = "NEUTRAL_ORDER"
    else:
        ordered = order_atoms_causal([a for a in selected_atoms if a["fco_id"] in id_set])
        label = "CAUSAL_FCG_ORDER"
    context, retained, _ = render_ordered_context(ordered, label, CONTEXT_CHAR_BUDGET)
    return context, retained, label


def build_manifest(
    experiment_id: str,
    mode: str,
    models: list[tuple[str, str]],
) -> dict:
    repo = ROOT
    cases = [
        json.loads(line)
        for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
        if line.strip()
    ]
    atoms = load_admissible_atoms(repo)
    conditions = [("C0", "FLAT_PROSE"), ("C1", "STRUCTURED_FCG")] if mode == "exp008" else [("C0", "NEUTRAL_ORDER"), ("C1", "CAUSAL_FCG_ORDER")]
    rows: list[dict] = []
    for condition, _ in conditions:
        for case in cases:
            if mode == "exp008":
                context, retained, label = exp008_context(case, condition, atoms)
            else:
                context, retained, label = exp009_context(case, condition, atoms)
            for replicate in range(1, N_REPLICATES + 1):
                prompt, proj = build_prompt(case, condition, context, retained, experiment_id)
                for model, digest in models:
                    cid = cell_id(case["case_id"], condition, replicate, model)
                    rows.append(
                        {
                            "cell_id": cid,
                            "case_id": case["case_id"],
                            "experiment_family": case["experiment_family"],
                            "condition": condition,
                            "context_mode": label,
                            "model": model,
                            "replicate": replicate,
                            "prompt_sha256": proj["prompt_sha256"],
                            "expected_model_digest": digest,
                            "state": "PENDING",
                        }
                    )
    n_cases = len(cases)
    n_conds = len(conditions)
    n_models = len(models)
    expected = n_cases * n_conds * N_REPLICATES * n_models
    return {
        "schema": "hydradg.qwen38.matrix_manifest.v1",
        "experiment_id": experiment_id,
        "formula": f"{n_cases} cases × {n_conds} conditions × {N_REPLICATES} replicates × {n_models} models = {expected}",
        "n_planned": expected,
        "cases_manifest_sha256": sha256_bytes(
            (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_bytes()
        ),
        "context_char_budget": CONTEXT_CHAR_BUDGET,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", choices=["Q38-EXP008-R2", "Q38-EXP009-R2"], required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    mode = "exp008" if args.experiment.endswith("008-R2") else "exp009"
    models = [(Q38_27B, Q38_27B_DIGEST), (FLASH_NEXT, FLASH_NEXT_DIGEST)]
    manifest = build_manifest(args.experiment, mode, models)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "MATRIX_MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    progress = {
        "schema": "hydradg.qwen38.matrix_progress.v1",
        "experiment_id": args.experiment,
        "n_planned": manifest["n_planned"],
        "n_terminal": 0,
        "MATRIX_COMPLETE": "NO",
        "updated_at_utc": None,
    }
    (args.out_dir / "MATRIX_PROGRESS.json").write_text(json.dumps(progress, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({manifest['n_planned']} cells)")


if __name__ == "__main__":
    main()
