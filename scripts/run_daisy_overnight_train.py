#!/usr/bin/env python3
"""Daisy falsification overnight train — governed local Ollama experiments."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from daisy_overnight.atoms import (  # noqa: E402
    CONTEXT_CHAR_BUDGET,
    load_admissible_atoms,
    render_flat_prose,
    render_structured_fcg,
    select_atoms,
)
from daisy_overnight.custody import append_fcg_edges, build_mmr_receipt, sha256_bytes  # noqa: E402
from daisy_overnight.exp009 import (  # noqa: E402
    CHECKPOINT_SHA,
    build_atom_set_freeze,
    build_ordering_algorithm,
    build_power_assessment,
    build_preregistration,
    execute_exp009,
    score_and_closeout_exp009,
    verify_exp008_closed,
    verify_ordering_isolation,
)
from daisy_overnight.stats import (  # noqa: E402
    bootstrap_rd_ci,
    classify_experiment,
    exact_mcnemar,
    holm_correction,
    risk_difference,
)

# Import scorer logic from existing script
from score_ic_failure_learning import score_row  # noqa: E402

PARENT_SHA = "d8166ae41f68c2d082eaf3d5380af0ea4e9b6bda"
STAGE2_MODELS = ["qwen3:1.7b", "qwen2.5-coder:7b"]
N_REPLICATES = 3
CONTEXT_BUDGET = CONTEXT_CHAR_BUDGET
PREDECESSOR_MMR = "c1134aa670e0cb5fcd1602f055223619ea8afa0d539087618bcaaebbed3b01bf"

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


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def resource_snapshot() -> dict[str, Any]:
    snap: dict[str, Any] = {"timestamp_utc": utc_now()}
    try:
        snap["loadavg"] = os.getloadavg()
    except OSError:
        snap["loadavg"] = None
    try:
        du = shutil.disk_usage("/")
        snap["disk_free_gb"] = round(du.free / (1024**3), 2)
    except OSError:
        pass
    try:
        out = subprocess.check_output(["vm_stat"], text=True)
        snap["vm_stat_head"] = out.splitlines()[:5]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return snap


def ollama_generate(model: str, prompt: str, temperature: float = 0.0, timeout: int = 300) -> tuple[str, float]:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
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


def model_digest(model: str) -> dict[str, Any]:
    info: dict[str, Any] = {"alias": model}
    try:
        tags = json.loads(
            urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10).read().decode()
        )
        exact = None
        prefix = None
        for m in tags.get("models", []):
            name = m.get("name", "")
            if name == model or name.startswith(model + "-"):
                exact = m
                break
            if name.split(":")[0] == model.split(":")[0]:
                prefix = m
        chosen = exact or prefix
        if chosen:
            info["model_id"] = chosen.get("name")
            info["digest"] = chosen.get("digest")
            info["size"] = chosen.get("size")
            if exact is None and prefix is not None:
                info["MODEL_IDENTITY_DRIFT"] = "PREFIX_MATCH_ONLY"
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        info["digest"] = "UNRESOLVED"
    try:
        show = subprocess.check_output(["ollama", "show", model, "--modelfile"], text=True, stderr=subprocess.DEVNULL)
        for line in show.splitlines():
            if line.startswith("FROM "):
                info["modelfile_from"] = line.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return info


def freeze_model_inventory(repo: Path, out_root: Path) -> dict[str, Any]:
    try:
        ollama_ver = subprocess.check_output(["ollama", "--version"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        ollama_ver = "unknown"
    ollarma_ver = "NOT_IN_PATH"
    which = shutil.which("ollarma")
    if which:
        try:
            ollarma_ver = subprocess.check_output([which, "--version"], text=True).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            ollarma_ver = which
    inv = {
        "schema": "hydradg.daisy_overnight.model_inventory_freeze.v1",
        "frozen_at_utc": utc_now(),
        "host": socket.gethostname(),
        "ollama_version": ollama_ver,
        "ollarma_version": ollarma_ver,
        "runtime": "DIRECT_OLLAMA_API",
        "ollarma_note": "Ollarma not in PATH; governed local execution via Ollama HTTP API with receipts",
        "models": [model_digest(m) for m in STAGE2_MODELS],
        "temperature": 0.0,
        "num_predict": 512,
    }
    path = out_root / "MODEL_INVENTORY_FREEZE.json"
    path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
    return inv


def write_gate_receipt(repo: Path, out_root: Path) -> dict[str, Any]:
    code, head = run_cmd(["git", "rev-parse", "HEAD"], repo)
    code_o, origin = run_cmd(["git", "rev-parse", "origin/hack-hydra/daisy-exp008-overnight-20260828"], repo)
    origin_sha = origin.strip() if code_o == 0 else None
    dirty_main = []
    main_repo = repo.parent / "hydradg"
    if main_repo.exists():
        _, st = run_cmd(["git", "status", "--short"], main_repo)
        dirty_main = [l.strip() for l in st.splitlines() if l.strip()][:20]
    gate = {
        "schema": "hydradg.daisy_overnight.worktree_gate.v1",
        "hostname": socket.gethostname(),
        "hostname_ok": socket.gethostname() == "magicSTUDIObox.local",
        "branch": "hack-hydra/daisy-exp008-overnight-20260828",
        "parent_sha": PARENT_SHA,
        "head_sha": head.strip() if code == 0 else None,
        "origin_sha": origin_sha,
        "origin_sha_ok": origin_sha == PARENT_SHA if origin_sha else head.strip() == PARENT_SHA,
        "worktree_path": str(repo),
        "dirty_paths_main_worktree": dirty_main,
        "PROJECT_CONTROL.yaml": "NOT_PRESENT_IN_CHECKOUT",
        "PROJECT_CONTROL_decision": "USE_ISOLATED_SUCCESSOR_WORKTREE",
        "timestamp_utc": utc_now(),
    }
    (out_root / "WORKTREE_GATE.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    if not gate["hostname_ok"]:
        raise SystemExit("BLOCKED: hostname != magicSTUDIObox.local")
    if gate["head_sha"] != PARENT_SHA:
        raise SystemExit(f"BLOCKED: head {gate['head_sha']} != required {PARENT_SHA}")
    return gate


def build_common_freeze(repo: Path, out_root: Path) -> dict[str, Any]:
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    scorer_path = repo / "scripts/score_ic_failure_learning.py"
    inv = json.loads((out_root / "MODEL_INVENTORY_FREEZE.json").read_text())
    freeze = {
        "schema": "hydradg.daisy_overnight.common_freeze.v1",
        "case_manifest_sha256": sha256_bytes(cases_path.read_bytes()),
        "scorer_sha256": sha256_bytes(scorer_path.read_bytes()),
        "models": STAGE2_MODELS,
        "model_digests": {m["alias"]: m.get("digest") for m in inv["models"]},
        "n_replicates": N_REPLICATES,
        "context_char_budget": CONTEXT_BUDGET,
        "temperature": 0.0,
        "num_predict": 512,
        "fcg_predecessor_root": PREDECESSOR_MMR,
        "prohibited_eval_only_fields": ["expected_answer", "judge_label", "scorer_label", "case_outcome"],
        "deterministic_seed_control": "UNAVAILABLE_OLLAMA",
        "case_aggregation_rule": "MAJORITY_OF_REPLICATES",
        "host": socket.gethostname(),
    }
    (out_root / "DAISY_COMMON_FREEZE.json").write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")
    return freeze


def build_prompt(
    case: dict[str, Any],
    condition: str,
    context_block: str,
    retained_fcos: list[str],
    experiment_id: str,
) -> tuple[str, dict[str, Any]]:
    case_input = case.get("input", {})
    if isinstance(case_input, dict) and "readme_poison_fixture" in case_input:
        case_input = {**case_input}
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
        "omitted_fco_ids": [],
    }
    return prompt, receipt


def execute_experiment(
    repo: Path,
    exp_dir: Path,
    experiment_id: str,
    c0_label: str,
    c1_label: str,
    hypothesis: str,
) -> None:
    if not (exp_dir / "PREREGISTRATION.json").exists():
        prereg = {
            "schema": "hydradg.daisy_overnight.preregistration.v1",
            "experiment_id": experiment_id,
            "hypothesis": hypothesis,
            "conditions": {"C0": c0_label, "C1": c1_label},
            "models": STAGE2_MODELS,
            "cases": "eval/ic_failure_learning_20260827/cases/CASES.jsonl",
            "n_replicates": N_REPLICATES,
            "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
            "case_aggregation": "MAJORITY_OF_3_REPLICATES",
            "alpha": 0.05,
            "prereg_sha": PARENT_SHA,
            "frozen_at_utc": utc_now(),
        }
        (exp_dir / "PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2) + "\n", encoding="utf-8")
    common = json.loads((repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/DAISY_COMMON_FREEZE.json").read_text())
    inv = json.loads((repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/MODEL_INVENTORY_FREEZE.json").read_text())
    if not (exp_dir / "EXECUTION_FREEZE.json").exists():
        (exp_dir / "EXECUTION_FREEZE.json").write_text(
            json.dumps({"common_freeze": common, "model_inventory_sha256": sha256_bytes(json.dumps(inv, sort_keys=True).encode())}, indent=2)
            + "\n",
            encoding="utf-8",
        )
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    manifest = exp_dir / "CASE_MANIFEST.json"
    if not manifest.exists():
        shutil.copy2(cases_path, manifest)
    cases = [json.loads(line) for line in cases_path.read_text().splitlines() if line.strip()]
    atoms = load_admissible_atoms(repo)
    ledger_path = exp_dir / "PROMPT_PROJECTION_LEDGER.jsonl"
    raw_path = exp_dir / "RAW_OUTPUTS.jsonl"
    existing_keys: set[tuple[str, str, str, int]] = set()
    if raw_path.exists():
        for line in raw_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            existing_keys.add((row["model"], row["case_id"], row["condition"], row["replicate"]))
    if not ledger_path.exists():
        ledger_path.write_text("", encoding="utf-8")

    for model in STAGE2_MODELS:
        for condition, label in [("C0", c0_label), ("C1", c1_label)]:
            for case in cases:
                fam = case["experiment_family"]
                selected = select_atoms(atoms, fam)
                if condition == "C0":
                    context, retained = render_flat_prose(selected, CONTEXT_BUDGET)
                else:
                    context, retained = render_structured_fcg(selected, CONTEXT_BUDGET)
                for replicate in range(1, N_REPLICATES + 1):
                    key = (model, case["case_id"], condition, replicate)
                    if key in existing_keys:
                        continue
                    prompt, proj = build_prompt(case, condition, context, retained, experiment_id)
                    proj["model"] = model
                    proj["replicate"] = replicate
                    proj["context_mode"] = label
                    with ledger_path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(proj, sort_keys=True) + "\n")
                    snap_before = resource_snapshot()
                    state = "OK"
                    raw = ""
                    latency = 0.0
                    try:
                        raw, latency = ollama_generate(model, prompt)
                    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                        try:
                            time.sleep(2)
                            raw, latency = ollama_generate(model, prompt, timeout=600)
                        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc2:
                            state = f"FAILED:{type(exc2).__name__}"
                            raw = json.dumps({"state": "ABSTAIN", "error": str(exc2)})
                    snap_after = resource_snapshot()
                    try:
                        parsed = json.loads(raw)
                        parser_state = "PARSED_JSON"
                    except json.JSONDecodeError:
                        parsed = None
                        parser_state = "MALFORMED_JSON"
                    row = {
                        "schema": "hydradg.daisy_overnight.raw_output.v1",
                        "experiment_id": experiment_id,
                        "condition": condition,
                        "context_mode": label,
                        "generation": f"{experiment_id}_{condition}",
                        "model": model,
                        "model_identity": inv["models"][STAGE2_MODELS.index(model)].get("modelfile_from", model),
                        "case_id": case["case_id"],
                        "experiment_family": fam,
                        "case_condition": case["condition"],
                        "replicate": replicate,
                        "prompt_sha256": proj["prompt_sha256"],
                        "raw_response_sha256": sha256_bytes(raw.encode("utf-8")),
                        "latency_seconds": round(latency, 3),
                        "parser_state": parser_state,
                        "parsed": parsed,
                        "run_state": state,
                        "resource_before": snap_before,
                        "resource_after": snap_after,
                        "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
                        "model_weight_state": "UNCHANGED",
                    }
                    with raw_path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
                    print(f"{experiment_id} {condition} {model} {case['case_id']} r{replicate} {parser_state} {latency:.1f}s")


def score_and_analyze(repo: Path, exp_dir: Path, experiment_id: str) -> dict[str, Any]:
    cases = {
        row["case_id"]: row
        for row in (
            json.loads(line)
            for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
            if line.strip()
        )
    }
    raw_rows = [
        json.loads(line) for line in (exp_dir / "RAW_OUTPUTS.jsonl").read_text().splitlines() if line.strip()
    ]
    scored: list[dict[str, Any]] = []
    for row in raw_rows:
        case = cases[row["case_id"]]
        scored.append(score_row(case, row))

    scored_path = exp_dir / "SCORED_RESULTS.jsonl"
    with scored_path.open("w", encoding="utf-8") as fh:
        for row in scored:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    # Case-level majority aggregation for E06 primary
    case_level: list[dict[str, Any]] = []
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in scored:
        key = (row["model"], row["case_id"], row["generation"])
        grouped[key].append(row)

    for key, reps in grouped.items():
        model, case_id, generation = key
        fam = reps[0]["family"]
        cond = "C0" if "_C0" in generation else "C1"
        if fam == "E06":
            vals = [r["metrics"].get("prevents_C_media_not_in_vault") for r in reps if r["metrics"]]
            bools = [v for v in vals if v is not None]
            if bools:
                case_positive = sum(bools) >= 2
            else:
                case_positive = None
        else:
            case_positive = None
        case_level.append(
            {
                "model": model,
                "case_id": case_id,
                "condition": cond,
                "generation": generation,
                "family": fam,
                "n_replicates": len(reps),
                "case_primary_e06": case_positive,
                "replicate_states": [r.get("model_state") for r in reps],
            }
        )
    with (exp_dir / "CASE_LEVEL_RESULTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in case_level:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    # Data quality
    parser_ok = sum(1 for r in raw_rows if r.get("parser_state") == "PARSED_JSON")
    dq = {
        "n_raw": len(raw_rows),
        "valid_parse_rate": parser_ok / len(raw_rows) if raw_rows else 0,
        "malformed_rate": sum(1 for r in scored if r.get("model_state") == "MALFORMED") / len(scored) if scored else 0,
        "unknown_rate": sum(1 for r in scored if r.get("model_state") == "UNKNOWN") / len(scored) if scored else 0,
        "abstain_rate": sum(1 for r in scored if r.get("model_state") == "ABSTAIN") / len(scored) if scored else 0,
    }
    (exp_dir / "DATA_QUALITY.json").write_text(json.dumps(dq, indent=2) + "\n", encoding="utf-8")

    # Per-model primary McNemar on E06 cases
    stats_by_model: dict[str, Any] = {}
    for model in STAGE2_MODELS:
        pairs: list[tuple[bool | None, bool | None]] = []
        e06_cases = sorted({c["case_id"] for c in case_level if c["family"] == "E06" and c["model"] == model})
        for cid in e06_cases:
            c0 = next((c["case_primary_e06"] for c in case_level if c["model"] == model and c["case_id"] == cid and c["condition"] == "C0"), None)
            c1 = next((c["case_primary_e06"] for c in case_level if c["model"] == model and c["case_id"] == cid and c["condition"] == "C1"), None)
            pairs.append((c0, c1))
        rd = risk_difference(pairs)
        b = sum(1 for a, bb in pairs if a and bb is False)
        c = sum(1 for a, bb in pairs if not a and bb)
        mcn = exact_mcnemar(b, c)
        boot = bootstrap_rd_ci(pairs)
        stats_by_model[model] = {**rd, **mcn, **boot, "n_paired": rd["n"], "pairs": pairs}

    # Secondary endpoints (descriptive + Holm where applicable)
    secondary_tests: list[dict[str, Any]] = []
    for metric, family, field in [
        ("E05_top1", "E05", "top1_correct"),
        ("E01_cold_start", "E01", "detects_cold_start_gap"),
        ("E01_vault_media", "E01", "detects_vault_media_gap"),
    ]:
        for model in STAGE2_MODELS:
            pairs = []
            case_ids = sorted({r["case_id"] for r in scored if r["family"] == family and r["model"] == model})
            for cid in case_ids:
                c0_reps = [r for r in scored if r["model"] == model and r["case_id"] == cid and "_C0" in r["generation"]]
                c1_reps = [r for r in scored if r["model"] == model and r["case_id"] == cid and "_C1" in r["generation"]]
                if not c0_reps or not c1_reps:
                    continue
                c0_maj = sum(r["metrics"].get(field) is True for r in c0_reps) >= 2
                c1_maj = sum(r["metrics"].get(field) is True for r in c1_reps) >= 2
                pairs.append((c0_maj, c1_maj))
            rd = risk_difference(pairs)
            b = sum(1 for a, bb in pairs if a and not bb)
            c = sum(1 for a, bb in pairs if not a and bb)
            mcn = exact_mcnemar(b, c)
            secondary_tests.append({"metric": metric, "model": model, **rd, **mcn})
    secondary_tests = holm_correction(secondary_tests)

    macro_n = sum(s["n_paired"] for s in stats_by_model.values())
    macro_rd = sum((s["rd"] or 0) * s["n_paired"] for s in stats_by_model.values()) / macro_n if macro_n else None

    stats = {
        "schema": "hydradg.daisy_overnight.stats.v1",
        "experiment_id": experiment_id,
        "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
        "by_model": stats_by_model,
        "macro_descriptive": {"n_paired_total": macro_n, "weighted_rd": macro_rd},
        "secondary_tests": secondary_tests,
        "alpha": 0.05,
    }
    (exp_dir / "STATS.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    # Verdict — use worst-case across models for classification
    primary_pooled = stats_by_model[STAGE2_MODELS[0]]
    for m in STAGE2_MODELS[1:]:
        if (stats_by_model[m].get("p_exact") or 1) < (primary_pooled.get("p_exact") or 1):
            primary_pooled = stats_by_model[m]
    verdict_class = classify_experiment(primary_pooled, dq, min_power_n=5)
    verdict = {
        "schema": "hydradg.daisy_overnight.verdict.v1",
        "experiment_id": experiment_id,
        "result_class": verdict_class,
        "primary": primary_pooled,
        "data_quality": dq,
        "conclusion_bounded": (
            "structured retrieval improved measured failure-prevention endpoint under this frozen experiment"
            if verdict_class == "SUPPORTED_POSITIVE"
            else "effect not established"
            if verdict_class in ("RETAINED_NULL", "UNDERPOWERED", "MIXED")
            else verdict_class
        ),
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (exp_dir / "VERDICT.json").write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")

    # Daisy decision
    next_map = {
        "SUPPORTED_POSITIVE": "EXP-008R_CONFIRMATION",
        "RETAINED_NULL": "EXP-009",
        "MIXED": "EXP-009",
        "SUPPORTED_NEGATIVE": "EXP-009",
        "UNDERPOWERED": "EXP-009",
        "INCONCLUSIVE_DATA_QUALITY": "STOP_IMPLEMENTATION_REPAIR",
        "ABORTED_EXECUTION_SETUP": "STOP",
        "FAILED_IMPLEMENTATION": "STOP",
        "TIMEOUT": "STOP",
    }
    decision = {
        "schema": "hydradg.daisy_overnight.decision.v1",
        "experiment_id": experiment_id,
        "result_class": verdict_class,
        "next_experiment": next_map.get(verdict_class, "STOP"),
        "reason": f"primary E06 n_paired={primary_pooled.get('n_paired')} p={primary_pooled.get('p_report')}",
    }
    (exp_dir / "DAISY_DECISION.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")

    md = [
        f"# {experiment_id} Statistics",
        "",
        f"**Result class:** {verdict_class}",
        "",
        "## Primary (E06 prevents-C)",
        json.dumps(stats_by_model, indent=2),
        "",
        "## Data quality",
        json.dumps(dq, indent=2),
    ]
    (exp_dir / "STATS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return verdict


def git_checkpoint(repo: Path, experiment_id: str, message: str) -> str:
    rel = f"eval/ic_failure_learning_20260827/daisy_overnight_20260828/{experiment_id}"
    run_cmd(["git", "add", rel, "scripts/daisy_overnight", "scripts/run_daisy_overnight_train.py"], repo)
    code, _ = run_cmd(
        [
            "git",
            "commit",
            "-m",
            message,
        ],
        repo,
    )
    if code != 0:
        return "NO_COMMIT"
    _, sha = run_cmd(["git", "rev-parse", "HEAD"], repo)
    run_cmd(["git", "push", "-u", "origin", "HEAD"], repo)
    return sha.strip()


def append_train_log(out_root: Path, record: dict[str, Any]) -> None:
    with (out_root / "DAISY_TRAIN.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def run_exp008(repo: Path, out_root: Path, execute_only: bool = False) -> dict[str, Any]:
    exp_dir = out_root / "EXP-008"
    exp_dir.mkdir(parents=True, exist_ok=True)
    if not (exp_dir / "PREREGISTRATION.json").exists():
        prereg = {
            "schema": "hydradg.daisy_overnight.preregistration.v1",
            "experiment_id": "EXP-008",
            "hypothesis": "H0_EXP008: Structured FCG retrieval/composition does not improve failure-prevention vs flat prose.",
            "conditions": {"C0": "FLAT_PROSE", "C1": "STRUCTURED_FCG"},
            "models": STAGE2_MODELS,
            "cases": "eval/ic_failure_learning_20260827/cases/CASES.jsonl",
            "n_replicates": N_REPLICATES,
            "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
            "case_aggregation": "MAJORITY_OF_3_REPLICATES",
            "alpha": 0.05,
            "prereg_sha": PARENT_SHA,
            "frozen_at_utc": utc_now(),
        }
        (exp_dir / "PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2) + "\n", encoding="utf-8")
    execute_experiment(
        repo,
        exp_dir,
        "EXP-008",
        "FLAT_PROSE",
        "STRUCTURED_FCG",
        "H0_EXP008: Structured FCG retrieval/composition does not improve failure-prevention vs flat prose.",
    )
    if execute_only:
        return {"result_class": "EXECUTION_IN_PROGRESS"}
    verdict = score_and_analyze(repo, exp_dir, "EXP-008")
    fcg_root = append_fcg_edges(exp_dir, "EXP-008", verdict["result_class"], PREDECESSOR_MMR)
    mmr = build_mmr_receipt(exp_dir, PREDECESSOR_MMR)
    run_receipt = {
        "schema": "hydradg.daisy_overnight.run_receipt.v1",
        "experiment_id": "EXP-008",
        "completed_at_utc": utc_now(),
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "fcg_root": fcg_root,
        "mmr_root": mmr["mmr_root"],
        "verdict": verdict["result_class"],
    }
    (exp_dir / "RUN_RECEIPT.json").write_text(json.dumps(run_receipt, indent=2) + "\n", encoding="utf-8")
    sha = git_checkpoint(repo, "EXP-008", "exp008: test structured FCG retrieval against flat context")
    append_train_log(
        out_root,
        {
            "experiment_id": "EXP-008",
            "parent": "STAGE2_POST_MODEL",
            "prereg_sha": PARENT_SHA,
            "execution_sha": sha,
            "result_class": verdict["result_class"],
            "fcg_root": fcg_root,
            "mmr_root": mmr["mmr_root"],
            "SIGNATURE_STATE": "NOT_SIGNED",
        },
    )
    return verdict


def verify_checkpoint_gate(repo: Path) -> None:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    if head != CHECKPOINT_SHA:
        raise SystemExit(f"BLOCKED: HEAD {head} != checkpoint {CHECKPOINT_SHA}")
    if socket.gethostname() != "magicSTUDIObox.local":
        raise SystemExit("BLOCKED: hostname != magicSTUDIObox.local")


def run_exp009_prereg(repo: Path, out_root: Path) -> dict[str, Any]:
    verify_checkpoint_gate(repo)
    closed = verify_exp008_closed(out_root)
    exp_dir = out_root / "EXP-009"
    exp_dir.mkdir(parents=True, exist_ok=True)
    power = build_power_assessment(repo, exp_dir)
    atom_rows = build_atom_set_freeze(repo, exp_dir)
    build_ordering_algorithm(exp_dir)
    verify_ordering_isolation(exp_dir, atom_rows, repo)
    prereg = build_preregistration(repo, exp_dir, power)
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    shutil.copy2(cases_path, exp_dir / "CASE_MANIFEST.json")
    inv = json.loads((out_root / "MODEL_INVENTORY_FREEZE.json").read_text())
    (exp_dir / "MODEL_INVENTORY.json").write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
    common = json.loads((out_root / "DAISY_COMMON_FREEZE.json").read_text())
    (exp_dir / "EXECUTION_FREEZE.json").write_text(
        json.dumps(
            {
                "common_freeze": common,
                "power_assessment_sha256": sha256_bytes((exp_dir / "POWER_ASSESSMENT.json").read_bytes()),
                "atom_set_freeze_sha256": sha256_bytes((exp_dir / "ATOM_SET_FREEZE.jsonl").read_bytes()),
                "predecessor_mmr": closed["predecessor_mmr"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"prereg": prereg, "power": power, "atom_rows": atom_rows, "predecessor_mmr": closed["predecessor_mmr"]}


def run_exp009_execute(repo: Path, out_root: Path) -> None:
    verify_checkpoint_gate(repo)
    verify_exp008_closed(out_root)
    exp_dir = out_root / "EXP-009"
    if not (exp_dir / "PREREGISTRATION.json").exists():
        raise SystemExit("BLOCKED: run exp009-prereg first")
    atom_rows = [json.loads(line) for line in (exp_dir / "ATOM_SET_FREEZE.jsonl").read_text().splitlines() if line.strip()]
    inv = json.loads((exp_dir / "MODEL_INVENTORY.json").read_text())
    execute_exp009(repo, exp_dir, atom_rows, ollama_generate, build_prompt, resource_snapshot, inv)


def run_exp009_closeout(repo: Path, out_root: Path) -> dict[str, Any]:
    verify_checkpoint_gate(repo)
    exp_dir = out_root / "EXP-009"
    power = json.loads((exp_dir / "POWER_ASSESSMENT.json").read_text())
    closed = verify_exp008_closed(out_root)
    result = score_and_closeout_exp009(repo, exp_dir, closed["predecessor_mmr"], power)
    run_receipt = {
        "schema": "hydradg.daisy_overnight.run_receipt.v1",
        "experiment_id": "EXP-009",
        "completed_at_utc": utc_now(),
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "fcg_root": result["fcg_root"],
        "mmr_root": result["mmr"]["mmr_root"],
        "verdict": result["verdict"]["EXPERIMENT_PRIMARY_VERDICT"],
        "predecessor_experiment": "EXP-008",
    }
    (exp_dir / "RUN_RECEIPT.json").write_text(json.dumps(run_receipt, indent=2) + "\n", encoding="utf-8")
    sha = git_checkpoint(repo, "EXP-009", "exp009: test causal FCG ordering after EXP-008 power limit")
    append_train_log(
        out_root,
        {
            "experiment_id": "EXP-009",
            "parent": "EXP-008",
            "parent_verdict": "UNDERPOWERED",
            "prereg_sha": sha256_bytes((exp_dir / "PREREGISTRATION.json").read_bytes()),
            "execution_sha": sha,
            "result_class": result["verdict"]["EXPERIMENT_PRIMARY_VERDICT"],
            "MECHANISTIC_EXPLORATORY_PATTERN": result["verdict"]["MECHANISTIC_EXPLORATORY_PATTERN"],
            "E06_n_paired": result["verdict"]["primary"].get("n_paired"),
            "next_experiment": result["decision"]["next_experiment"],
            "fcg_root": result["fcg_root"],
            "mmr_root": result["mmr"]["mmr_root"],
            "SIGNATURE_STATE": "NOT_SIGNED",
        },
    )
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument(
        "--phase",
        choices=[
            "bootstrap",
            "exp008",
            "exp008-execute",
            "exp008-closeout",
            "exp009-prereg",
            "exp009-execute",
            "exp009-closeout",
            "train",
        ],
        default="train",
    )
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out_root = repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828"
    out_root.mkdir(parents=True, exist_ok=True)

    if args.phase in ("bootstrap", "train"):
        write_gate_receipt(repo, out_root)
        freeze_model_inventory(repo, out_root)
        build_common_freeze(repo, out_root)

    if args.phase in ("exp008", "exp008-execute", "train"):
        verdict = run_exp008(repo, out_root, execute_only=args.phase == "exp008-execute")
        if args.phase != "exp008-execute":
            print(json.dumps({"EXP-008": verdict["result_class"], "next": json.loads((out_root / "EXP-008/DAISY_DECISION.json").read_text())["next_experiment"]}, indent=2))

    if args.phase == "exp008-closeout":
        exp_dir = out_root / "EXP-008"
        verdict = score_and_analyze(repo, exp_dir, "EXP-008")
        fcg_root = append_fcg_edges(exp_dir, "EXP-008", verdict["result_class"], PREDECESSOR_MMR)
        mmr = build_mmr_receipt(exp_dir, PREDECESSOR_MMR)
        run_receipt = {
            "schema": "hydradg.daisy_overnight.run_receipt.v1",
            "experiment_id": "EXP-008",
            "completed_at_utc": utc_now(),
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
            "fcg_root": fcg_root,
            "mmr_root": mmr["mmr_root"],
            "verdict": verdict["result_class"],
        }
        (exp_dir / "RUN_RECEIPT.json").write_text(json.dumps(run_receipt, indent=2) + "\n", encoding="utf-8")
        sha = git_checkpoint(repo, "EXP-008", "exp008: test structured FCG retrieval against flat context")
        append_train_log(
            out_root,
            {
                "experiment_id": "EXP-008",
                "parent": "STAGE2_POST_MODEL",
                "prereg_sha": PARENT_SHA,
                "execution_sha": sha,
                "result_class": verdict["result_class"],
                "fcg_root": fcg_root,
                "mmr_root": mmr["mmr_root"],
                "SIGNATURE_STATE": "NOT_SIGNED",
            },
        )
        print(json.dumps(verdict, indent=2))

    if args.phase == "exp009-prereg":
        result = run_exp009_prereg(repo, out_root)
        print(json.dumps({"EXP-009": "PREREG_FROZEN", "E06_POWER_STATE": result["power"]["E06_POWER_STATE"]}, indent=2))

    if args.phase == "exp009-execute":
        run_exp009_execute(repo, out_root)
        n = sum(1 for _ in (out_root / "EXP-009/RAW_OUTPUTS.jsonl").open() if _.strip())
        print(json.dumps({"EXP-009": "EXECUTION_COMPLETE", "raw_rows": n}, indent=2))

    if args.phase == "exp009-closeout":
        result = run_exp009_closeout(repo, out_root)
        print(json.dumps(result["verdict"], indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
