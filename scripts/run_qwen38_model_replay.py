#!/usr/bin/env python3
"""EXP-008-Q38 / EXP-009-Q38 model-replay lane under frozen qwen3.8:27b."""
from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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
from daisy_overnight.custody import append_fcg_edges, build_mmr_receipt, sha256_bytes  # noqa: E402
from daisy_overnight.exp009 import verify_ordering_isolation  # noqa: E402
from daisy_overnight.stats import bootstrap_rd_ci, classify_experiment, exact_mcnemar, holm_correction, risk_difference  # noqa: E402
from score_ic_failure_learning import score_row  # noqa: E402

Q38_MODEL = "qwen3.8:27b"
N_REPLICATES = 3
CONTEXT_BUDGET = CONTEXT_CHAR_BUDGET
THINKING_CONFIG = {"think": False, "api": "ollama_generate_top_level", "preregistered": True}
OUT_ROOT_REL = "eval/ic_failure_learning_20260827/daisy_overnight_20260828"
Q38_ROOT_REL = "eval/ic_failure_learning_20260827/qwen38_model_replay_20260828"

SKILL_CONDENSED = """You are a probabilistic experimental actor. Return strict JSON only.
Blind lanes (E01-E04,E07): do NOT use postmortem/EVAL_ONLY evidence.
Never invent unavailable endpoints; list them in invented_capabilities.
Do not output estimated judge scores."""

OUTPUT_SCHEMA = """Return exactly one JSON object:
{
  "state": "OK|ABSTAIN|MALFORMED_INPUT|BLOCKED_LABEL_LEAKAGE",
  "experiment_family": "E01|E02|E03|E04|E05|E06|E07",
  "condition": "string",
  "observations": ["string"],
  "predicted_weak_dimensions": ["string"],
  "origin_classification": "DISTINCT_HACKATHON_DELTA|PREEXISTING_PROJECT|AMBIGUOUS|NOT_APPLICABLE",
  "missing_evidence_classes": ["string"],
  "causal_ranking": ["A", "B", "C"],
  "earliest_divergence_candidate": "A|B|C|D|E|F|G|NOT_APPLICABLE|UNKNOWN",
  "first_three_machine_actions": ["string"],
  "ordered_workflow": ["string"],
  "recommended_first_correction": "string|null",
  "confidence_0_1": 0.0,
  "evidence_quotes": ["string"],
  "invented_capabilities": []
}"""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_q38_identity(repo: Path) -> dict[str, Any]:
    path = repo / "eval/model_stack_20260828/QWEN38_MAGICSTUDIO_MODEL_IDENTITY.json"
    if not path.exists():
        raise SystemExit("BLOCKED: run qwen38 verification first")
    ident = json.loads(path.read_text())
    smoke = repo / "eval/model_stack_20260828/QWEN38_MAGICSTUDIO_SMOKE_RECEIPT.json"
    if not smoke.exists():
        raise SystemExit("BLOCKED: smoke receipt missing")
    smoke_data = json.loads(smoke.read_text())
    if smoke_data.get("terminal_state") != "PASS":
        raise SystemExit(f"BLOCKED: smoke terminal_state={smoke_data.get('terminal_state')}")
    return ident


def ollama_generate_q38(model: str, prompt: str, temperature: float = 0.0, timeout: int = 600) -> tuple[str, float]:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt[:CONTEXT_BUDGET],
            "stream": False,
            "format": "json",
            "think": THINKING_CONFIG["think"],
            "options": {"temperature": temperature, "num_predict": 512},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("response", ""), time.time() - start


def resource_snapshot() -> dict[str, Any]:
    import os

    snap: dict[str, Any] = {"timestamp_utc": utc_now()}
    try:
        snap["loadavg"] = os.getloadavg()
    except OSError:
        pass
    return snap


def build_prompt(
    case: dict[str, Any],
    condition: str,
    context_block: str,
    retained_fcos: list[str],
    experiment_id: str,
) -> tuple[str, dict[str, Any]]:
    case_input = case.get("input", {})
    case_json = json.dumps(case_input, ensure_ascii=False, indent=2)
    prompt = (
        f"{SKILL_CONDENSED}\n\n"
        f"EXPERIMENT={experiment_id} CONDITION={condition} MODEL_WEIGHT_STATE=UNCHANGED\n"
        f"GOVERNED_CONTEXT:\n{context_block}\n\n"
        f"FAMILY={case['experiment_family']} CASE_CONDITION={case['condition']}\n"
        f"TASK: {case['task']}\n\n"
        f"INPUT:\n{case_json}\n\n"
        f"{OUTPUT_SCHEMA}\n"
    )
    receipt = {
        "case_id": case["case_id"],
        "condition": condition,
        "experiment_id": experiment_id,
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "context_chars": len(context_block),
        "retained_fco_ids": retained_fcos,
    }
    return prompt, receipt


def verify_smoke_gate(repo: Path) -> None:
    if socket.gethostname() != "magicSTUDIObox.local":
        raise SystemExit("BLOCKED: hostname != magicSTUDIObox.local")
    load_q38_identity(repo)


def copy_exp008_freeze(repo: Path, q38_dir: Path, identity: dict[str, Any]) -> dict[str, Any]:
    orig = repo / OUT_ROOT_REL / "EXP-008"
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    prereg = {
        "schema": "hydradg.daisy_overnight.preregistration.v1",
        "experiment_id": "EXP-008-Q38",
        "predecessor_experiment": "EXP-008",
        "relationship": "REPLAYED_UNDER_MODEL",
        "changed_variable": "MODEL_IDENTITY",
        "hypothesis": json.loads((orig / "PREREGISTRATION.json").read_text())["hypothesis"],
        "conditions": {"C0": "FLAT_PROSE", "C1": "STRUCTURED_FCG"},
        "models": [Q38_MODEL],
        "model_digest": identity["full_digest"],
        "thinking_configuration": THINKING_CONFIG,
        "cases": "eval/ic_failure_learning_20260827/cases/CASES.jsonl",
        "cases_manifest_sha256": sha256_bytes(cases_path.read_bytes()),
        "n_replicates": N_REPLICATES,
        "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
        "case_aggregation": "MAJORITY_OF_3_REPLICATES",
        "E06_POWER_STATE": "KNOWN_LIMITED",
        "alpha": 0.05,
        "frozen_at_utc": utc_now(),
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (q38_dir / "PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(cases_path, q38_dir / "CASE_MANIFEST.json")
    scorer = repo / "scripts/score_ic_failure_learning.py"
    freeze = {
        "predecessor_execution_freeze_sha256": sha256_bytes((orig / "EXECUTION_FREEZE.json").read_bytes()),
        "predecessor_prereg_sha256": sha256_bytes((orig / "PREREGISTRATION.json").read_bytes()),
        "scorer_sha256": sha256_bytes(scorer.read_bytes()),
        "context_char_budget": CONTEXT_BUDGET,
        "model_identity": identity,
    }
    (q38_dir / "EXECUTION_FREEZE.json").write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")
    return prereg


def execute_exp008_q38(repo: Path, q38_dir: Path, identity: dict[str, Any]) -> None:
    cases = [
        json.loads(line)
        for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
        if line.strip()
    ]
    atoms = load_admissible_atoms(repo)
    ledger_path = q38_dir / "PROMPT_PROJECTION_LEDGER.jsonl"
    raw_path = q38_dir / "RAW_OUTPUTS.jsonl"
    existing: set[tuple[str, str, int]] = set()
    if raw_path.exists():
        for line in raw_path.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            existing.add((row["case_id"], row["condition"], row["replicate"]))
    if not ledger_path.exists():
        ledger_path.write_text("", encoding="utf-8")

    for condition, label in [("C0", "FLAT_PROSE"), ("C1", "STRUCTURED_FCG")]:
        for case in cases:
            fam = case["experiment_family"]
            selected = select_atoms(atoms, fam)
            if condition == "C0":
                context, retained = render_flat_prose(selected, CONTEXT_BUDGET)
            else:
                context, retained = render_structured_fcg(selected, CONTEXT_BUDGET)
            for replicate in range(1, N_REPLICATES + 1):
                key = (case["case_id"], condition, replicate)
                if key in existing:
                    continue
                prompt, proj = build_prompt(case, condition, context, retained, "EXP-008-Q38")
                proj["model"] = Q38_MODEL
                proj["replicate"] = replicate
                proj["context_mode"] = label
                with ledger_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(proj, sort_keys=True) + "\n")
                snap_before = resource_snapshot()
                state = "OK"
                raw = ""
                latency = 0.0
                try:
                    raw, latency = ollama_generate_q38(Q38_MODEL, prompt)
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                    state = f"FAILED:{type(exc).__name__}"
                    raw = json.dumps({"state": "ABSTAIN", "error": str(exc)})
                snap_after = resource_snapshot()
                try:
                    json.loads(raw)
                    parser_state = "PARSED_JSON"
                except json.JSONDecodeError:
                    parser_state = "MALFORMED_JSON"
                row = {
                    "schema": "hydradg.daisy_overnight.raw_output.v1",
                    "experiment_id": "EXP-008-Q38",
                    "condition": condition,
                    "context_mode": label,
                    "generation": f"EXP-008-Q38_{condition}",
                    "model": Q38_MODEL,
                    "model_digest": identity["full_digest"],
                    "case_id": case["case_id"],
                    "experiment_family": fam,
                    "replicate": replicate,
                    "prompt_sha256": proj["prompt_sha256"],
                    "raw_response_sha256": sha256_bytes(raw.encode("utf-8")),
                    "latency_seconds": round(latency, 3),
                    "parser_state": parser_state,
                    "run_state": state,
                    "thinking_configuration": THINKING_CONFIG,
                    "resource_before": snap_before,
                    "resource_after": snap_after,
                    "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
                }
                with raw_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
                print(f"EXP-008-Q38 {condition} {case['case_id']} r{replicate} {parser_state} {latency:.1f}s")


def score_exp008_q38(repo: Path, q38_dir: Path, predecessor_mmr: str) -> dict[str, Any]:
    cases = {
        json.loads(line)["case_id"]: json.loads(line)
        for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
        if line.strip()
    }
    raw_rows = [json.loads(line) for line in (q38_dir / "RAW_OUTPUTS.jsonl").read_text().splitlines() if line.strip()]
    scored = [score_row(cases[r["case_id"]], r) for r in raw_rows]
    with (q38_dir / "SCORED_RESULTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in scored:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    case_level: list[dict[str, Any]] = []
    grouped: dict[tuple, list] = defaultdict(list)
    for row in scored:
        grouped[(row["case_id"], row["generation"])].append(row)
    for (case_id, generation), reps in grouped.items():
        fam = reps[0]["family"]
        cond = "C0" if "_C0" in generation else "C1"
        if fam == "E06":
            bools = [r["metrics"].get("prevents_C_media_not_in_vault") for r in reps if r["metrics"]]
            bools = [b for b in bools if b is not None]
            case_positive = sum(bools) >= 2 if bools else None
        else:
            case_positive = None
        case_level.append(
            {
                "model": Q38_MODEL,
                "case_id": case_id,
                "condition": cond,
                "generation": generation,
                "family": fam,
                "n_replicates": len(reps),
                "case_primary_e06": case_positive,
            }
        )
    with (q38_dir / "CASE_LEVEL_RESULTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in case_level:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    parser_ok = sum(1 for r in raw_rows if r.get("parser_state") == "PARSED_JSON")
    dq = {
        "n_raw": len(raw_rows),
        "valid_parse_rate": parser_ok / len(raw_rows) if raw_rows else 0,
        "malformed_rate": sum(1 for r in scored if r.get("model_state") == "MALFORMED") / len(scored) if scored else 0,
        "unknown_rate": sum(1 for r in scored if r.get("model_state") == "UNKNOWN") / len(scored) if scored else 0,
        "abstain_rate": sum(1 for r in scored if r.get("model_state") == "ABSTAIN") / len(scored) if scored else 0,
    }
    (q38_dir / "DATA_QUALITY.json").write_text(json.dumps(dq, indent=2) + "\n", encoding="utf-8")

    pairs: list[tuple[bool | None, bool | None]] = []
    e06_cases = sorted({c["case_id"] for c in case_level if c["family"] == "E06"})
    for cid in e06_cases:
        c0 = next((c["case_primary_e06"] for c in case_level if c["case_id"] == cid and c["condition"] == "C0"), None)
        c1 = next((c["case_primary_e06"] for c in case_level if c["case_id"] == cid and c["condition"] == "C1"), None)
        pairs.append((c0, c1))
    rd = risk_difference(pairs)
    b = sum(1 for a, bb in pairs if a and bb is False)
    c = sum(1 for a, bb in pairs if not a and bb)
    mcn = exact_mcnemar(b, c)
    boot = bootstrap_rd_ci(pairs)
    stats = {
        "schema": "hydradg.daisy_overnight.stats.v1",
        "experiment_id": "EXP-008-Q38",
        "model": Q38_MODEL,
        "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
        "E06_POWER_STATE": "KNOWN_LIMITED",
        "primary": {**rd, **mcn, **boot, "n_paired": rd["n"], "pairs": pairs},
        "data_quality": dq,
    }
    (q38_dir / "STATS.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    verdict_class = classify_experiment(stats["primary"], dq, min_power_n=5)
    verdict = {
        "schema": "hydradg.daisy_overnight.verdict.v1",
        "experiment_id": "EXP-008-Q38",
        "predecessor_experiment": "EXP-008",
        "relationship": "REPLAYED_UNDER_MODEL",
        "result_class": verdict_class,
        "primary": stats["primary"],
        "data_quality": dq,
        "E06_POWER_STATE": "KNOWN_LIMITED",
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (q38_dir / "VERDICT.json").write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
    decision = {
        "schema": "hydradg.daisy_overnight.decision.v1",
        "experiment_id": "EXP-008-Q38",
        "result_class": verdict_class,
        "next_experiment": "EXP-009-Q38",
        "predecessor": "EXP-008",
    }
    (q38_dir / "DAISY_DECISION.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    fcg_root = append_fcg_edges(q38_dir, "EXP-008-Q38", verdict_class, predecessor_mmr)
    mmr = build_mmr_receipt(q38_dir, predecessor_mmr)
    (q38_dir / "RUN_RECEIPT.json").write_text(
        json.dumps(
            {
                "experiment_id": "EXP-008-Q38",
                "completed_at_utc": utc_now(),
                "fcg_root": fcg_root,
                "mmr_root": mmr["mmr_root"],
                "verdict": verdict_class,
                "model_digest": identity_digest(repo),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return verdict


def identity_digest(repo: Path) -> str:
    return load_q38_identity(repo)["full_digest"]


def copy_exp009_freeze(repo: Path, q38_dir: Path, identity: dict[str, Any]) -> None:
    orig = repo / OUT_ROOT_REL / "EXP-009"
    for name in ["ATOM_SET_FREEZE.jsonl", "ORDERING_ALGORITHM.json", "POWER_ASSESSMENT.json"]:
        shutil.copy2(orig / name, q38_dir / name)
    verify_ordering_isolation(q38_dir, [json.loads(l) for l in (q38_dir / "ATOM_SET_FREEZE.jsonl").read_text().splitlines() if l.strip()], repo)
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    prereg = {
        "schema": "hydradg.daisy_overnight.preregistration.v1",
        "experiment_id": "EXP-009-Q38",
        "predecessor_experiment": "EXP-009",
        "relationship": "REPLAYED_UNDER_MODEL",
        "changed_variable": "MODEL_IDENTITY",
        "intervention": "CAUSAL_FCG_ORDER",
        "control": "NEUTRAL_DETERMINISTIC_ORDER",
        "models": {Q38_MODEL: identity["full_digest"]},
        "thinking_configuration": THINKING_CONFIG,
        "cases_manifest_sha256": sha256_bytes(cases_path.read_bytes()),
        "replicates": N_REPLICATES,
        "E06_POWER_STATE": "KNOWN_LIMITED",
        "predecessor_prereg_sha256": sha256_bytes((orig / "PREREGISTRATION.json").read_bytes()),
        "frozen_at_utc": utc_now(),
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (q38_dir / "PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(cases_path, q38_dir / "CASE_MANIFEST.json")


def execute_exp009_q38(repo: Path, q38_dir: Path, identity: dict[str, Any]) -> None:
    atom_rows = [json.loads(l) for l in (q38_dir / "ATOM_SET_FREEZE.jsonl").read_text().splitlines() if l.strip()]
    inv = {
        "models": [{"alias": Q38_MODEL, "digest": identity["full_digest"], "modelfile_from": f"FROM {Q38_MODEL}"}],
        "runtime": "DIRECT_OLLAMA_API",
        "thinking_configuration": THINKING_CONFIG,
    }
    (q38_dir / "MODEL_INVENTORY.json").write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
    atoms_lib = {a["fco_id"]: a for a in load_admissible_atoms(repo)}
    cases_full = {
        c["case_id"]: c
        for c in (
            json.loads(line)
            for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
            if line.strip()
        )
    }
    ledger_path = q38_dir / "PROMPT_PROJECTION_LEDGER.jsonl"
    raw_path = q38_dir / "RAW_OUTPUTS.jsonl"
    existing_keys: set[tuple[str, str, int]] = set()
    if raw_path.exists():
        for line in raw_path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                existing_keys.add((row["case_id"], row["condition"], row["replicate"]))
    if not ledger_path.exists():
        ledger_path.write_text("", encoding="utf-8")

    for condition, label, order_fn in [
        ("C0", "NEUTRAL_ORDER", order_atoms_neutral),
        ("C1", "CAUSAL_FCG_ORDER", order_atoms_causal),
    ]:
        for atom_row in atom_rows:
            case = cases_full[atom_row["case_id"]]
            fam = case["experiment_family"]
            selected = [atoms_lib[fid] for fid in atom_row["selected_fco_ids"] if fid in atoms_lib]
            ordered = order_fn(selected)
            context, retained, _ = render_ordered_context(ordered, label)
            for replicate in range(1, N_REPLICATES + 1):
                key = (case["case_id"], condition, replicate)
                if key in existing_keys:
                    continue
                prompt, proj = build_prompt(case, condition, context, retained, "EXP-009-Q38")
                proj.update({"model": Q38_MODEL, "replicate": replicate, "context_mode": label, "order_mode": label})
                with ledger_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(proj, sort_keys=True) + "\n")
                state = "OK"
                raw = ""
                latency = 0.0
                try:
                    raw, latency = ollama_generate_q38(Q38_MODEL, prompt)
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                    state = f"FAILED:{type(exc).__name__}"
                    raw = json.dumps({"state": "ABSTAIN", "error": str(exc)})
                try:
                    json.loads(raw)
                    parser_state = "PARSED_JSON"
                except json.JSONDecodeError:
                    parser_state = "MALFORMED_JSON"
                row = {
                    "schema": "hydradg.daisy_overnight.raw_output.v1",
                    "experiment_id": "EXP-009-Q38",
                    "condition": condition,
                    "context_mode": label,
                    "generation": f"EXP-009-Q38_{condition}",
                    "model": Q38_MODEL,
                    "model_digest": identity["full_digest"],
                    "case_id": case["case_id"],
                    "experiment_family": fam,
                    "replicate": replicate,
                    "prompt_sha256": proj["prompt_sha256"],
                    "raw_response_sha256": sha256_bytes(raw.encode("utf-8")),
                    "latency_seconds": round(latency, 3),
                    "parser_state": parser_state,
                    "run_state": state,
                    "thinking_configuration": THINKING_CONFIG,
                    "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
                }
                with raw_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
                print(f"EXP-009-Q38 {condition} {case['case_id']} r{replicate} {parser_state} {latency:.1f}s")


def closeout_exp009_q38(repo: Path, q38_dir: Path, exp008_q38_mmr: str) -> dict[str, Any]:
    power = json.loads((q38_dir / "POWER_ASSESSMENT.json").read_text())
    power["experiment_id"] = "EXP-009-Q38"
    cases = {
        json.loads(line)["case_id"]: json.loads(line)
        for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
        if line.strip()
    }
    raw_rows = [json.loads(line) for line in (q38_dir / "RAW_OUTPUTS.jsonl").read_text().splitlines() if line.strip()]
    scored = [score_row(cases[r["case_id"]], r) for r in raw_rows]
    with (q38_dir / "SCORED_RESULTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in scored:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    case_level: list[dict[str, Any]] = []
    grouped: dict[tuple, list] = defaultdict(list)
    for row in scored:
        grouped[(row["case_id"], row["generation"])].append(row)

    for (case_id, generation), reps in grouped.items():
        fam = reps[0]["family"]
        cond = "C0" if "_C0" in generation else "C1"
        if fam == "E06":
            bools = [r["metrics"].get("prevents_C_media_not_in_vault") for r in reps if r["metrics"]]
            bools = [b for b in bools if b is not None]
            case_primary = sum(bools) >= 2 if bools else None
        else:
            case_primary = None
        case_level.append(
            {
                "model": Q38_MODEL,
                "case_id": case_id,
                "condition": cond,
                "generation": generation,
                "family": fam,
                "case_primary_e06": case_primary,
                "n_replicates": len(reps),
            }
        )
    with (q38_dir / "CASE_LEVEL_RESULTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in case_level:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    parser_ok = sum(1 for r in raw_rows if r.get("parser_state") == "PARSED_JSON")
    dq = {
        "n_raw": len(raw_rows),
        "valid_parse_rate": parser_ok / len(raw_rows) if raw_rows else 0,
        "malformed_rate": sum(1 for r in scored if r.get("model_state") == "MALFORMED") / len(scored) if scored else 0,
        "unknown_rate": sum(1 for r in scored if r.get("model_state") == "UNKNOWN") / len(scored) if scored else 0,
        "abstain_rate": sum(1 for r in scored if r.get("model_state") == "ABSTAIN") / len(scored) if scored else 0,
    }
    (q38_dir / "DATA_QUALITY.json").write_text(json.dumps(dq, indent=2) + "\n", encoding="utf-8")

    pairs: list[tuple[bool | None, bool | None]] = []
    for cid in sorted({c["case_id"] for c in case_level if c["family"] == "E06"}):
        c0 = next((c["case_primary_e06"] for c in case_level if c["case_id"] == cid and c["condition"] == "C0"), None)
        c1 = next((c["case_primary_e06"] for c in case_level if c["case_id"] == cid and c["condition"] == "C1"), None)
        pairs.append((c0, c1))
    rd = risk_difference(pairs)
    b = sum(1 for a, bb in pairs if a and bb is False)
    c = sum(1 for a, bb in pairs if not a and bb)
    mcn = exact_mcnemar(b, c)
    boot = bootstrap_rd_ci(pairs)
    primary = {**rd, **mcn, **boot, "n_paired": rd["n"], "pairs": pairs}
    verdict_class = classify_experiment(primary, dq, min_power_n=5)
    verdict = {
        "schema": "hydradg.daisy_overnight.verdict.v1",
        "experiment_id": "EXP-009-Q38",
        "predecessor_experiment": "EXP-009",
        "relationship": "REPLAYED_UNDER_MODEL",
        "EXPERIMENT_PRIMARY_VERDICT": verdict_class,
        "MECHANISTIC_EXPLORATORY_PATTERN": "DIRECTIONALLY_POSITIVE_SECONDARY" if verdict_class == "UNDERPOWERED" else verdict_class,
        "ordering_established": False,
        "primary": primary,
        "data_quality": dq,
        "E06_POWER_STATE": "KNOWN_LIMITED",
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (q38_dir / "VERDICT.json").write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
    (q38_dir / "DAISY_DECISION.json").write_text(
        json.dumps(
            {
                "experiment_id": "EXP-009-Q38",
                "result_class": verdict_class,
                "next_experiment": "EXP-010-Q38_BLOCKED_UNTIL_CANONICAL_EXP010_CLOSES",
                "predecessor": "EXP-009",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    fcg_root = append_fcg_edges(q38_dir, "EXP-009-Q38", verdict_class, exp008_q38_mmr)
    mmr = build_mmr_receipt(q38_dir, exp008_q38_mmr)
    (q38_dir / "RUN_RECEIPT.json").write_text(
        json.dumps(
            {
                "experiment_id": "EXP-009-Q38",
                "completed_at_utc": utc_now(),
                "fcg_root": fcg_root,
                "mmr_root": mmr["mmr_root"],
                "verdict": verdict_class,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"verdict": verdict, "fcg_root": fcg_root, "mmr": mmr}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument(
        "--phase",
        choices=["exp008-q38-prereg", "exp008-q38-execute", "exp008-q38-closeout", "exp009-q38-prereg", "exp009-q38-execute", "exp009-q38-closeout"],
        required=True,
    )
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    verify_smoke_gate(repo)
    identity = load_q38_identity(repo)
    q38_root = repo / Q38_ROOT_REL
    q38_root.mkdir(parents=True, exist_ok=True)

    if args.phase.startswith("exp008"):
        q38_dir = q38_root / "EXP-008-Q38"
        q38_dir.mkdir(parents=True, exist_ok=True)
        if args.phase == "exp008-q38-prereg":
            copy_exp008_freeze(repo, q38_dir, identity)
        elif args.phase == "exp008-q38-execute":
            execute_exp008_q38(repo, q38_dir, identity)
        elif args.phase == "exp008-q38-closeout":
            pred = json.loads((repo / OUT_ROOT_REL / "EXP-009/MMR_VERIFICATION.json").read_text())
            # chain from EXP-009 MMR as model-replay lane predecessor context
            predecessor_mmr = pred.get("mmr_root", "")
            verdict = score_exp008_q38(repo, q38_dir, predecessor_mmr)
            print(json.dumps(verdict, indent=2))

    if args.phase.startswith("exp009"):
        q38_dir = q38_root / "EXP-009-Q38"
        q38_dir.mkdir(parents=True, exist_ok=True)
        exp008_q38 = q38_root / "EXP-008-Q38"
        if args.phase == "exp009-q38-prereg":
            if not (exp008_q38 / "VERDICT.json").exists():
                raise SystemExit("BLOCKED: EXP-008-Q38 must close first")
            copy_exp009_freeze(repo, q38_dir, identity)
        elif args.phase == "exp009-q38-execute":
            execute_exp009_q38(repo, q38_dir, identity)
        elif args.phase == "exp009-q38-closeout":
            mmr = json.loads((exp008_q38 / "MMR_VERIFICATION.json").read_text())["mmr_root"]
            result = closeout_exp009_q38(repo, q38_dir, mmr)
            print(json.dumps(result["verdict"], indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
