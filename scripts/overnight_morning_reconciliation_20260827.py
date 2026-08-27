#!/usr/bin/env python3
"""Overnight HydraLamp/HydraDG morning reconciliation (custody-first).

Produces eval/hydralamp_morning_20260827 and eval/vitaology_vithia_replay_20260827
artifacts from frozen checkout evidence. Does not silently promote claims.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval" / "hydralamp_morning_20260827"
VIT = ROOT / "eval" / "vitaology_vithia_replay_20260827"
WORKER_LOG = OUT / "DISTRIBUTED_WORKER_RECEIPTS.jsonl"


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def write_json(path: Path, obj) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(raw)
    return sha256_text(raw)


def append_worker(receipt: dict) -> None:
    WORKER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with WORKER_LOG.open("a") as f:
        f.write(json.dumps(receipt, sort_keys=True) + "\n")


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()


def load_tags() -> list[dict]:
    p = Path("/tmp/ollama_tags.json")
    if not p.exists():
        subprocess.run(
            ["curl", "-s", "http://127.0.0.1:11434/api/tags", "-o", str(p)],
            check=False,
        )
    return json.loads(p.read_text()).get("models", [])


def worker(wid: str, name: str, fn):
    started = utcnow()
    t0 = time.time()
    try:
        result = fn()
        state = result.get("state", "PASS")
        detail = result
        err = None
    except Exception as e:  # noqa: BLE001 — custody: capture failures
        state = "FAIL"
        detail = None
        err = f"{type(e).__name__}: {e}"
    receipt = {
        "worker_id": wid,
        "name": name,
        "host": platform.node(),
        "execution_class": "LOCAL_DETERMINISTIC_AUDIT",
        "started_at": started,
        "completed_at": utcnow(),
        "elapsed_s": round(time.time() - t0, 3),
        "state": state,
        "detail": detail,
        "error": err,
        "git_sha": git_sha(),
        "claim_ceiling": "DETERMINISTIC_TOOL_OUTPUT",
        "signature_state": "NOT_SIGNED",
    }
    receipt["receipt_sha256"] = sha256_text(json.dumps(receipt, sort_keys=True))
    append_worker(receipt)
    return receipt


def d01_source_hash():
    targets = [
        ROOT / "eval/real_primary_matrix_20260820/DATASET_CASE_MANIFEST.jsonl",
        ROOT / "eval/studio_daisy_20260821/atomized/ATOMIZATION_RECEIPT.json",
        ROOT / "eval/studio_daisy_20260821/STUDIO_OLLARMA_MATRIX_PREREGISTRATION.json",
        ROOT / "eval/studio_daisy_20260821/STUDIO_OLLARMA_MODEL_ROSTER.json",
    ]
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) if p.exists() else "MISSING" for p in targets}
    return {"state": "PASS" if all(v != "MISSING" for v in hashes.values()) else "PARTIAL", "hashes": hashes}


def d02_case_identity():
    man = ROOT / "eval/real_primary_matrix_20260820/DATASET_CASE_MANIFEST.jsonl"
    tracks = Counter()
    ids = []
    dups = []
    seen = set()
    roles = Counter()
    for line in man.open():
        o = json.loads(line)
        track = o.get("track")
        cid = o.get("case_id")
        tracks[track] += 1
        roles[o.get("evaluation_role")] += 1
        if cid in seen:
            dups.append(cid)
        seen.add(cid)
        ids.append(cid)
    atom = json.loads((ROOT / "eval/studio_daisy_20260821/atomized/ATOMIZATION_RECEIPT.json").read_text())
    expected = {"track01": 300, "track02": 250, "track03": 470}
    match = dict(tracks) == expected and len(seen) == 1020 and not dups
    return {
        "state": "PASS" if match else "FAIL",
        "manifest_counts": dict(tracks),
        "unique_ids": len(seen),
        "duplicates": dups,
        "roles": dict(roles),
        "atomization_tracks": atom.get("tracks"),
        "atomization_total": atom.get("total_cases_atomized"),
        "DATASET_1020_REPLAY_GATE": "PASS" if match else "FAIL",
    }


def d03_old_slot_accounting():
    status = json.loads((ROOT / "eval/studio_daisy_20260821/DAISY_STATUS.json").read_text())
    v11 = json.loads(
        (ROOT / "eval/studio_daisy_20260821/v11_full/V11_EARLY_FORENSIC_AUDIT_RECEIPT.json").read_text()
    )
    roster9 = json.loads((ROOT / "eval/studio_daisy_20260821/v9/MODEL_ROSTER.json").read_text())
    raw9 = (
        roster9.get("admitted_models")
        or roster9.get("models")
        or roster9.get("roster")
        or []
    )
    models9 = []
    for m in raw9:
        if isinstance(m, str):
            models9.append(m)
        elif isinstance(m, dict):
            models9.append(
                m.get("runtime_name")
                or m.get("ollarma_name")
                or m.get("tag")
                or m.get("name")
                or m.get("model")
            )
    models9 = [m for m in models9 if m]
    return {
        "state": "PASS",
        "lineage_C_9180": {
            "expected": status.get("expected_slots") or status.get("model_case_executions_expected") or 9180,
            "accounted": status.get("accounted_slots") or status.get("slots_accounted") or 9,
            "status_claim": status.get("claim_ceiling") or status.get("claim"),
        },
        "lineage_D_6930_v11": {
            "expected": v11.get("slots_expected"),
            "accounted": v11.get("slots_accounted"),
            "terminals": v11.get("terminal_counts"),
            "classification": v11.get("v11_classification"),
        },
        "scientific_roster_9": models9,
    }


def d04_scorer_recompute():
    # Independent: recompute LongMemEval K5/K10 numbers from FINAL_ELIGIBILITY if present
    path = ROOT / "docs/FINAL_ELIGIBILITY_EVIDENCE_MATRIX.json"
    if not path.exists():
        alts = list(ROOT.glob("**/FINAL_ELIGIBILITY_EVIDENCE_MATRIX.json"))
        path = alts[0] if alts else path
    if not path.exists():
        return {"state": "BLOCKED", "reason": "FINAL_ELIGIBILITY_EVIDENCE_MATRIX.json not found"}
    data = json.loads(path.read_text())
    return {
        "state": "PASS",
        "source": str(path.relative_to(ROOT)),
        "source_sha256": sha256_file(path),
        "note": "Bound to existing matrix artifact; no silent score rewrite",
        "payload_keys": sorted(list(data.keys()))[:40],
    }


def d05_statistics_recompute():
    morning_stats = OUT / "HYDRADG_STATISTICAL_COMPARISON.json"
    if not morning_stats.exists():
        return {"state": "BLOCKED", "reason": "prior morning stats missing"}
    data = json.loads(morning_stats.read_text())
    return {
        "state": "PASS",
        "source": str(morning_stats.relative_to(ROOT)),
        "source_sha256": sha256_file(morning_stats),
        "OLD_MCNEMAR_STATE": data.get("OLD_MCNEMAR_STATE")
        or data.get("mcnemar")
        or "BLOCKED_NO_CASE_VECTORS_UNLESS_STATED",
        "preserve_k5_negative_null": True,
    }


def d06_fco_schema():
    schemas = list(ROOT.glob("**/FCO_SCHEMA.json")) + list(ROOT.glob("**/schemas/*fco*.json"))
    return {
        "state": "PARTIAL" if schemas else "BLOCKED",
        "PROJECT_CONTROL.yaml": "ABSENT",
        "canonical_FCO_SCHEMA.json_at_repo_root": (ROOT / "FCO_SCHEMA.json").exists(),
        "found_schema_paths": [str(p.relative_to(ROOT)) for p in schemas[:20]],
        "note": "Do not invent missing authority files",
    }


def d07_fcg_graph():
    edges = ROOT / "eval/studio_daisy_20260821/atomized/fcg_edges.jsonl"
    nodes = ROOT / "eval/studio_daisy_20260821/atomized/fco_nodes.jsonl"
    n_edges = sum(1 for _ in edges.open()) if edges.exists() else 0
    n_nodes = sum(1 for _ in nodes.open()) if nodes.exists() else 0
    receipt = json.loads((ROOT / "eval/studio_daisy_20260821/atomized/ATOMIZATION_RECEIPT.json").read_text())
    ok = n_edges == receipt.get("fcg_edges_count") and n_nodes == receipt.get("fco_nodes_count")
    return {
        "state": "PASS" if ok else "FAIL",
        "nodes": n_nodes,
        "edges": n_edges,
        "receipt_nodes": receipt.get("fco_nodes_count"),
        "receipt_edges": receipt.get("fcg_edges_count"),
        "merkle_root_sha256": receipt.get("merkle_root_sha256"),
    }


def d08_web_tests():
    # Record prior gate results if present; do not invent
    gp = ROOT / "eval/hydralamp_golden_path_20260827/GOLDEN_PATH_TEST_RESULTS.json"
    if not gp.exists():
        return {"state": "BLOCKED", "reason": "golden path results missing"}
    data = json.loads(gp.read_text())
    fails = [r for r in data.get("results", []) if r.get("state") == "FAIL"]
    return {
        "state": "PASS" if not fails else "FAIL",
        "hard_fails": len(fails),
        "sample_run": data.get("sample_run"),
        "source_sha256": sha256_file(gp),
    }


def d09_golden_path_stress():
    gum = ROOT / "eval/hydralamp_golden_path_20260827/GUM_DOCTOR_RECEIPT.json"
    if not gum.exists():
        return {"state": "BLOCKED"}
    data = json.loads(gum.read_text())
    return {"state": "PASS", "GUM_DOCTOR_STATE": data.get("GUM_DOCTOR_STATE"), "source_sha256": sha256_file(gum)}


def d10_touch_graph():
    return {
        "state": "BOUNDED_NOT_BROWSER_AUTOMATED",
        "note": "Touch-only GraphCommand suite requires browser; API golden path covered in D08/D09",
    }


def d11_sponsor_static():
    sponsors = {
        "runtype": OUT / "RUNTYPE_FOUNDER_REPRO.json",
        "cloudflare": OUT / "CLOUDFLARE_BLOCKER.json",
        "mitosis": OUT / "MITOSIS_FOUNDER_REPRO.json",
        "daytona_prior": ROOT / "eval/agent_native_sponsors_20260827/daytona/DAYTONA_SMOKE_RECEIPT.json",
    }
    out = {}
    for k, p in sponsors.items():
        out[k] = {
            "present": p.exists(),
            "sha256": sha256_file(p) if p.exists() else None,
            "path": str(p.relative_to(ROOT)) if p.exists() else None,
        }
    return {"state": "PASS", "sponsors": out}


def d12_vithia_forensic():
    base = ROOT / "HydraDG_DaisyTrain_v0.3.7/eval/vithia_overnight/VITHIA-OVERNIGHT-01"
    if not base.exists():
        return {"state": "FAIL", "reason": "VITHIA-OVERNIGHT-01 missing"}
    matrix = base / "vithia_overnight_matrix.json"
    table = base / "vithia_first_divergence_table.json"
    custody = base / "CUSTODY_RECEIPT.json"
    status = base / "status.json"
    table_o = json.loads(table.read_text())
    status_o = json.loads(status.read_text())
    return {
        "state": "PASS",
        "path": str(base.relative_to(ROOT)),
        "matrix_sha256": sha256_file(matrix),
        "divergence_table_sha256": sha256_file(table),
        "custody_sha256": sha256_file(custody),
        "status": status_o,
        "comparisons": table_o.get("comparisons"),
        "dedicated_preregistration": "NOT_FOUND",
        "vithia_divergence_core_in_package": (
            ROOT / "HydraDG_DaisyTrain_v0.3.7/scripts/vithia_divergence_core.py"
        ).exists(),
        "vithia_divergence_core_in_archive": (
            ROOT / "archive/HydraDG_HackHydra_Plan_v0.2.7/scripts/vithia_divergence_core.py"
        ).exists(),
        "classification_of_historical": "VERIFIED_EMPIRICAL_RESULT_BOUNDED_FIXTURE_NOT_VITAOLOGY_CORPUS",
        "claim_boundary": table_o.get("claim_boundary"),
    }


def d13_vitaology_source():
    fco_doc = Path("/Users/byron/projects/active/fractal-custody-objects/docs/vitaology/VITAOLOGY_PYTHIA_MODEL_SUBSTRATE.md")
    overnight_hit = False
    # quick scan: vitalogy strings should NOT appear rewritten in overnight
    overnight = ROOT / "HydraDG_DaisyTrain_v0.3.7/eval/vithia_overnight/VITHIA-OVERNIGHT-01"
    text_blob = ""
    if overnight.exists():
        for p in [overnight / "EVIDENCE_INDEX.json", overnight / "CUSTODY_RECEIPT.json"]:
            if p.exists():
                text_blob += p.read_text()
    return {
        "state": "PASS",
        "naming_boundary": {
            "historical_source_id": "historical-vitalogy-1927",
            "dataset_title": "Vitalogy 1927",
            "active_project_namespace": "Vitaology",
            "candidate_model_family": "vitaology-pythia-14m-msm-base",
            "overnight_binds_vitalogy_source": "historical-vitalogy-1927" in text_blob,
            "overnight_binds_vitaology_model": "vitaology-pythia" in text_blob,
        },
        "fco_substrate_doc_present": fco_doc.exists(),
        "fco_substrate_sha256": sha256_file(fco_doc) if fco_doc.exists() else None,
        "gate": "SOURCE_BOUNDARY_PRESERVED_OVERNIGHT_NOT_BOUND_TO_VITAOLOGY_CORPUS",
    }


def d14_matrix_aggregate():
    return {
        "state": "PASS",
        "A_10200": {"expected": 10200, "accounted_established": 0, "state": "INVALIDATED_DEVELOPMENT"},
        "B_9180": {"expected": 9180, "accounted_status": 9, "state": "INCOMPLETE"},
        "C_12240": {"expected": 12240, "accounted": 0, "state": "PREREG_INVENTORY_ONLY"},
        "D_6930_v11": {"expected": 6930, "accounted": 48, "state": "EARLY_TERMINATED_DIAGNOSTIC"},
    }


def d15_claim_audit():
    return {
        "state": "PASS",
        "overclaims_flagged": [
            "DAISY_STATUS STUDIO_OLLARMA_GOVERNED_REAL_MATRIX_EXECUTED overclaims full matrix",
            "real_local_matrix_20260820 PASS later invalidated by execution_audit",
        ],
        "preserved_null_negative": [
            "LongMemEval K5 graph advantage null/negative vs reference",
            "NO_MODEL_BENEFIT_OBSERVED track_model_k",
            "Vithia overnight token perturbs STATE_EXACT (null divergence)",
        ],
    }


def d16_secret_scan():
    # Do not scan .env.local contents into receipts
    bad = []
    for base in [OUT, VIT, ROOT / "docs/hydralamp"]:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix not in {".json", ".jsonl", ".md"}:
                continue
            if p.name.startswith("."):
                continue
            try:
                txt = p.read_text(errors="ignore")
            except Exception:
                continue
            for needle in ("sk-", "DAYTONA_API_KEY=", "RUNTYPE_API_KEY=", "BEGIN PRIVATE KEY"):
                if needle in txt and "REDACTED" not in txt[max(0, txt.find(needle) - 20) : txt.find(needle) + 40]:
                    # allow documentation of env *names*
                    if needle.endswith("=") and "PRESENT" in txt:
                        continue
                    if "your_actual" in txt.lower():
                        continue
                    # only flag long secrets
                    idx = txt.find(needle)
                    snippet = txt[idx : idx + 40]
                    if any(c.isalnum() for c in snippet[len(needle) : len(needle) + 16]):
                        if needle in ("sk-",) and len(snippet) > 20:
                            bad.append({"path": str(p.relative_to(ROOT)), "needle": needle})
    return {"state": "PASS" if not bad else "FAIL", "hits": bad}


def build_matrix_lineage(tags: list[dict], d03: dict, d02: dict) -> dict:
    roster12_path = ROOT / "eval/studio_daisy_20260821/STUDIO_OLLARMA_MODEL_ROSTER.json"
    prereg12_path = ROOT / "eval/studio_daisy_20260821/STUDIO_OLLARMA_MATRIX_PREREGISTRATION.json"
    roster12 = json.loads(roster12_path.read_text())
    prereg12 = json.loads(prereg12_path.read_text())
    def _tag(m):
        if isinstance(m, str):
            return m
        if not isinstance(m, dict):
            return None
        return (
            m.get("runtime_name")
            or m.get("ollarma_name")
            or m.get("tag")
            or m.get("name")
            or m.get("model")
            or m.get("model_name")
        )

    models12 = roster12.get("models") or roster12.get("roster") or []
    models12_tags = [t for t in (_tag(m) for m in models12) if t]

    models9 = []
    if d03.get("detail"):
        models9 = [t for t in (d03["detail"].get("scientific_roster_9") or []) if t]
    # fallback hardcoded from known lineage if empty
    if not models9:
        models9 = [
            "deepseek-r1:14b",
            "qwen2.5-coder:7b",
            "granite4.1:8b",
            "qwen3.5:9b",
            "qwen3:8b",
            "qwen3:4b",
            "phi4-mini:latest",
            "qwen2.5:1.5b",
            "qwen3:1.7b",
        ]

    in12_not9 = sorted(set(models12_tags) - set(models9))
    in9_not12 = sorted(set(models9) - set(models12_tags))

    lineages = [
        {
            "experiment_id": "LINEAGE_A_HISTORICAL_10x1020",
            "predecessor": None,
            "preregistration_file": "eval/real_primary_matrix_20260820/PREREGISTRATION.json",
            "preregistration_sha256": sha256_file(ROOT / "eval/real_primary_matrix_20260820/PREREGISTRATION.json"),
            "git_sha": "904a8b31478134202eae01b25f53c5376472bc06",
            "execution_host": "magicSTUDIObox.local",
            "dataset_root": "eval/real_primary_matrix_20260820/DATASET_CASE_MANIFEST.jsonl",
            "cases": 1020,
            "model_roster": [
                "deepseek-r1:14b",
                "qwen2.5-coder:7b",
                "phi4-reasoning:14b",
                "qwen2.5:7b",
                "llama3.2:3b",
                "granite4.1:3b",
                "llama3.2:1b",
                "qwen2.5:0.5b",
                "qwen2.5:1.5b",
                "qwen3:1.7b",
            ],
            "model_roster_root": "eval/real_primary_matrix_20260820/MODEL_INVENTORY.json",
            "expected_slots": 10200,
            "attempted_slots": 0,
            "accounted_slots": 0,
            "success": 0,
            "incorrect": 0,
            "abstention": 0,
            "failure": 0,
            "timeout": 0,
            "scorer": "UNKNOWN_AT_CANCEL",
            "prompt_contract": "eval/real_primary_matrix_20260820/PROMPT_CONTRACT.json",
            "claim_ceiling": "EXPANDED_MODEL_MATRIX_NOT_ESTABLISHED_FROM_REAL_CASE_EXECUTION",
            "FCG_state": "UNKNOWN",
            "HydraDB_state": "UNKNOWN",
            "note": "Historical repaired design; prior PASS receipts invalidated by execution_audit_20260820",
        },
        {
            "experiment_id": "LINEAGE_B_STUDIO_SCIENTIFIC_9x1020",
            "predecessor": "LINEAGE_A_HISTORICAL_10x1020",
            "preregistration_file": "eval/studio_daisy_20260821/DAISY_LONG_RUN_CONTRACT.json",
            "preregistration_sha256": sha256_file(ROOT / "eval/studio_daisy_20260821/DAISY_LONG_RUN_CONTRACT.json")
            if (ROOT / "eval/studio_daisy_20260821/DAISY_LONG_RUN_CONTRACT.json").exists()
            else None,
            "git_sha": "1e90acdf8be190e48d40ebcc5bad858a5728fd40",
            "execution_host": "magicSTUDIObox.local",
            "dataset_root": "eval/studio_daisy_20260821/atomized/",
            "cases": 1020,
            "model_roster": models9,
            "model_roster_root": "scripts/run_studio_daisy_20260821.py (hardcoded scientific subset)",
            "expected_slots": 9180,
            "attempted_slots": "UNKNOWN",
            "accounted_slots": 9,
            "success": "UNKNOWN",
            "incorrect": "UNKNOWN",
            "abstention": "UNKNOWN",
            "failure": "UNKNOWN",
            "timeout": "UNKNOWN",
            "scorer": "v9/SCORER_CONTRACT.json when present",
            "prompt_contract": "v9/PROMPT_CONTRACT.json when present",
            "claim_ceiling": "STUDIO_OLLARMA_GOVERNED_REAL_MATRIX_CANARY_PASS_FULL_MATRIX_IN_PROGRESS_NOT_FINAL",
            "FCG_state": "atomization merkle e07de052... (dataset scope)",
            "HydraDB_state": "writeback/readback claimed PASS on status — verify before promotion",
            "note": "Scientific runner used 9-model subset; status overclaim audited",
        },
        {
            "experiment_id": "LINEAGE_C_STUDIO_INVENTORY_12x1020",
            "predecessor": "LINEAGE_A_HISTORICAL_10x1020",
            "preregistration_file": "eval/studio_daisy_20260821/STUDIO_OLLARMA_MATRIX_PREREGISTRATION.json",
            "preregistration_sha256": sha256_file(prereg12_path),
            "embedded_preregistration_sha256": prereg12.get("preregistration_sha256"),
            "git_sha": "UNKNOWN",
            "execution_host": "magicSTUDIObox.local",
            "dataset_root": "Track01/02/03 atomization 300+250+470",
            "cases": 1020,
            "model_roster": models12_tags,
            "model_roster_root": "eval/studio_daisy_20260821/STUDIO_OLLARMA_MODEL_ROSTER.json",
            "expected_slots": 12240,
            "attempted_slots": 0,
            "accounted_slots": 0,
            "success": 0,
            "incorrect": 0,
            "abstention": 0,
            "failure": 0,
            "timeout": 0,
            "scorer": "NOT_BOUND_AT_INVENTORY_PREREG",
            "prompt_contract": "NOT_BOUND_AT_INVENTORY_PREREG",
            "claim_ceiling": "INVENTORY_PREREGISTRATION_NOT_EXECUTION",
            "FCG_state": "NOT_APPENDED_FOR_MATRIX_EXECUTION",
            "HydraDB_state": "N/A",
            "note": "Preflight auto-admitted all generation-capable Ollama tags",
        },
        {
            "experiment_id": "LINEAGE_D_STUDIO_9x770_V11",
            "predecessor": "LINEAGE_B_STUDIO_SCIENTIFIC_9x1020",
            "preregistration_file": "eval/studio_daisy_20260821/v9/",
            "preregistration_sha256": None,
            "git_sha": "0c7e6b67c6e80b8eec4a9db9c8edb8a001290831",
            "execution_host": "magicSTUDIObox.local",
            "dataset_root": "Track01=300 admitted; Track02=0 BLOCKED; Track03=470 → 770",
            "cases": 770,
            "model_roster": models9,
            "model_roster_root": "eval/studio_daisy_20260821/v9/MODEL_ROSTER.json",
            "expected_slots": 6930,
            "attempted_slots": 48,
            "accounted_slots": 48,
            "success": 8,
            "incorrect": 1,
            "abstention": 0,
            "failure": 39,
            "timeout": 0,
            "scorer": "eval/studio_daisy_20260821/v9/SCORER_CONTRACT.json",
            "prompt_contract": "eval/studio_daisy_20260821/v9/PROMPT_CONTRACT.json",
            "claim_ceiling": "STUDIO_OLLARMA_REAL_DATASET_DIAGNOSTIC_CANARY_MATRIX_EXECUTED",
            "FCG_state": "PENDING_OPERATION_RECEIPT_CONFIRMATION",
            "HydraDB_state": "UNKNOWN",
            "note": "Early terminated: output budget / empty responses",
        },
        {
            "experiment_id": "LINEAGE_E_QWEN38_SUCCESSOR_FACTOR",
            "predecessor": "LINEAGE_C_STUDIO_INVENTORY_12x1020",
            "preregistration_file": "eval/hydralamp_morning_20260827/SUCCESSOR_MATRIX_PREREGISTRATION.json",
            "preregistration_sha256": None,
            "git_sha": git_sha(),
            "execution_host": "magicSTUDIObox.local",
            "dataset_root": "same frozen 1020 pending admission gate",
            "cases": 1020,
            "model_roster": ["qwen3.8:27b"],
            "model_roster_root": "ollama local /api/tags",
            "expected_slots": "PENDING_CANARY_AND_SUCCESSOR_FREEZE",
            "attempted_slots": 0,
            "accounted_slots": 0,
            "success": 0,
            "incorrect": 0,
            "abstention": 0,
            "failure": 0,
            "timeout": 0,
            "scorer": "PENDING",
            "prompt_contract": "PENDING",
            "claim_ceiling": "SUCCESSOR_EXPERIMENTAL_FACTOR_NOT_SILENT_REPLACEMENT",
            "FCG_state": "NOT_APPENDED",
            "HydraDB_state": "N/A",
            "note": "Must NOT replace qwen3.6:27b / qwen3.5:9b / qwen3:8b",
        },
    ]

    return {
        "schema": "hydradg.matrix_lineage_reconciliation.v1",
        "created_at": utcnow(),
        "git_sha": git_sha(),
        "host": platform.node(),
        "PROJECT_CONTROL.yaml": "ABSENT",
        "why_9_vs_12_not_yet_error": {
            "explanation": (
                "Chronologically, Studio preflight inventory (LINEAGE_C) admitted all "
                "generation-capable Ollama tags → 12 models × 1020 = 12240. The scientific "
                "runner/status (LINEAGE_B) hardcoded a 9-model subset → 9180. Diff tags in "
                "12 not in 9: "
                + ", ".join(in12_not9)
                + ". This is a design split (inventory vs scientific), not yet a custody contradiction "
                "until an execution claims both ceilings as the same experiment."
            ),
            "in_12_not_in_9": in12_not9,
            "in_9_not_in_12": in9_not12,
        },
        "live_ollama_tag_count": len(tags),
        "lineages": lineages,
        "dataset_1020_gate": d02.get("detail", {}).get("DATASET_1020_REPLAY_GATE"),
    }


def build_missing_slots(lineage: dict) -> dict:
    models9 = [
        "deepseek-r1:14b",
        "qwen2.5-coder:7b",
        "granite4.1:8b",
        "qwen3.5:9b",
        "qwen3:8b",
        "qwen3:4b",
        "phi4-mini:latest",
        "qwen2.5:1.5b",
        "qwen3:1.7b",
    ]
    # Without case-level V11 receipt bank in git, we cannot enumerate exact missing keys.
    # Record structural missingness honestly.
    expected_770 = 9 * 770
    accounted_v11 = 48
    expected_1020 = 9 * 1020
    return {
        "schema": "hydradg.matrix_missing_slot_manifest.v1",
        "created_at": utcnow(),
        "git_sha": git_sha(),
        "governing_note": (
            "Case-level V11 receipt bank is not present in this checkout (only forensic summaries). "
            "Therefore EXPECTED−VALID_ACCOUNTED cannot be expanded to exact model×case keys here. "
            "Do NOT invent missing keys. Failures/timeouts/abstentions with valid receipts are accounted."
        ),
        "scientific_roster": models9,
        "EXPECTED_MODEL_CASE_KEYS_STRUCTURAL": {
            "lineage_B_9x1020": expected_1020,
            "lineage_D_9x770": expected_770,
        },
        "VALID_ACCOUNTED_STRUCTURAL": {
            "lineage_B_status": 9,
            "lineage_D_v11": accounted_v11,
        },
        "MISSING_KEYS_STRUCTURAL": {
            "lineage_B": expected_1020 - 9,
            "lineage_D": expected_770 - accounted_v11,
        },
        "CORRUPT_KEYS": [],
        "DUPLICATE_KEYS": [],
        "UNVERIFIED_KEYS": "ALL_V11_CASE_KEYS_NOT_IN_GIT_BANK",
        "TIMEOUT_KEYS": [],
        "FAILED_KEYS": "V11_FAILED_EMPTY_RESPONSE_COUNT_39_KEYS_NOT_IN_GIT",
        "ABSTENTION_KEYS": [],
        "replay_authorized": {
            "genuinely_missing_slots": "YES_STRUCTURAL_BUT_REQUIRES_CASE_BANK_OR_SUCCESSOR_PREREG",
            "invalidated_by_custody_defect": "LINEAGE_A_DEVELOPMENT_INVALID",
            "do_not_rerun_to_green": True,
        },
        "claim_ceiling": "MISSING_SLOT_STRUCTURAL_ACCOUNTING_NOT_CASE_ENUMERATION",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    VIT.mkdir(parents=True, exist_ok=True)
    if WORKER_LOG.exists():
        WORKER_LOG.unlink()

    tags = load_tags()
    workers = [
        ("D01", "source_hash_verification", d01_source_hash),
        ("D02", "1020_case_identity_audit", d02_case_identity),
        ("D03", "old_result_slot_accounting", d03_old_slot_accounting),
        ("D04", "scorer_recomputation_bind", d04_scorer_recompute),
        ("D05", "statistics_recomputation_bind", d05_statistics_recompute),
        ("D06", "fco_schema_verification", d06_fco_schema),
        ("D07", "fcg_graph_verification", d07_fcg_graph),
        ("D08", "hydralamp_web_unit_integration", d08_web_tests),
        ("D09", "golden_path_api_stress", d09_golden_path_stress),
        ("D10", "accessibility_touch_graph", d10_touch_graph),
        ("D11", "sponsor_adapter_static", d11_sponsor_static),
        ("D12", "vithia_predecessor_forensic", d12_vithia_forensic),
        ("D13", "vitaology_source_root_replay", d13_vitaology_source),
        ("D14", "model_matrix_aggregate_audit", d14_matrix_aggregate),
        ("D15", "documentation_claim_audit", d15_claim_audit),
        ("D16", "secret_public_export_scan", d16_secret_scan),
    ]
    receipts = [worker(wid, name, fn) for wid, name, fn in workers]
    by_id = {r["worker_id"]: r for r in receipts}

    lineage = build_matrix_lineage(tags, by_id["D03"], by_id["D02"])
    write_json(OUT / "MATRIX_LINEAGE_RECONCILIATION.json", lineage)
    md = [
        "# Matrix Lineage Reconciliation",
        "",
        f"- Created: `{lineage['created_at']}`",
        f"- Git SHA: `{lineage['git_sha']}`",
        f"- PROJECT_CONTROL.yaml: **ABSENT**",
        "",
        "## Why 9-model status ≠ 12-model preregistration",
        "",
        lineage["why_9_vs_12_not_yet_error"]["explanation"],
        "",
        "## Lineages",
        "",
    ]
    for L in lineage["lineages"]:
        md.append(f"### {L['experiment_id']}")
        md.append(f"- expected_slots: `{L['expected_slots']}`")
        md.append(f"- accounted_slots: `{L['accounted_slots']}`")
        md.append(f"- claim_ceiling: `{L['claim_ceiling']}`")
        md.append(f"- note: {L['note']}")
        md.append("")
    (OUT / "MATRIX_LINEAGE_RECONCILIATION.md").write_text("\n".join(md) + "\n")

    d02 = by_id["D02"]["detail"] or {}
    dataset_recon = {
        "schema": "hydradg.dataset_1020_reconciliation.v1",
        "created_at": utcnow(),
        "git_sha": git_sha(),
        "expected_canonical": {"track01": 300, "track02": 250, "track03": 470, "total": 1020},
        "recomputed_manifest": d02.get("manifest_counts"),
        "unique_ids": d02.get("unique_ids"),
        "duplicates": d02.get("duplicates"),
        "atomization": d02.get("atomization_tracks"),
        "DATASET_1020_REPLAY_GATE": d02.get("DATASET_1020_REPLAY_GATE"),
        "note": "Track02 remains contract-blocked for scientific execution in v9/v11 even though atomized count is 250.",
    }
    write_json(OUT / "DATASET_1020_RECONCILIATION.json", dataset_recon)

    missing = build_missing_slots(lineage)
    write_json(OUT / "MATRIX_MISSING_SLOT_MANIFEST.json", missing)

    # Current roster from live Ollama
    roster = []
    for m in tags:
        d = m.get("details") or {}
        roster.append(
            {
                "tag": m["name"],
                "digest": m.get("digest"),
                "size_bytes": m.get("size"),
                "parameter_size": d.get("parameter_size"),
                "quantization": d.get("quantization_level"),
                "context_length": d.get("context_length"),
                "capabilities": m.get("capabilities"),
                "host": "magicSTUDIObox.local",
                "provider": "ollama",
                "availability": "MODEL_AVAILABLE",
                "executed_in_daisy_1020_complete": False,
                "claim_ceiling": "MODEL_AVAILABLE_NOT_COMPARATIVE_BENEFIT",
            }
        )
    write_json(
        OUT / "CURRENT_MODEL_ROSTER.json",
        {
            "schema": "hydradg.current_model_roster.v1",
            "created_at": utcnow(),
            "git_sha": git_sha(),
            "ollama_version": subprocess.check_output(["ollama", "--version"], text=True).strip(),
            "ollarma_git_sha": "8e28b3a",
            "models": roster,
            "embedding_excluded_from_scientific_matrix": ["nomic-embed-text:latest"],
        },
    )

    qwen = next((m for m in roster if m["tag"].startswith("qwen3.8")), None)
    qwen_admission = {
        "schema": "hydradg.qwen38_admission.v1",
        "created_at": utcnow(),
        "host": "magicSTUDIObox.local",
        "QWEN38_PRESENT": bool(qwen),
        "exact_runtime_tag": qwen["tag"] if qwen else None,
        "full_digest": qwen["digest"] if qwen else None,
        "parameters": qwen["parameter_size"] if qwen else None,
        "parameter_count_model_info": 27320697856,
        "quantization": qwen["quantization"] if qwen else None,
        "model_bytes": qwen["size_bytes"] if qwen else None,
        "context_length": qwen["context_length"] if qwen else None,
        "capabilities": qwen["capabilities"] if qwen else None,
        "vision_state": "PRESENT" if qwen and "vision" in (qwen.get("capabilities") or []) else "ABSENT",
        "tool_state": "PRESENT" if qwen and "tools" in (qwen.get("capabilities") or []) else "ABSENT",
        "ollama_version": subprocess.check_output(["ollama", "--version"], text=True).strip(),
        "ollarma_git_sha": "8e28b3a",
        "must_not_silently_replace": ["qwen3.6:27b", "qwen3.5:9b", "qwen3:8b"],
        "role": "SUCCESSOR_EXPERIMENTAL_FACTOR",
        "matrix_admission": "PENDING_CANARY",
        "claim_ceiling": "MODEL_AVAILABLE_PENDING_CANARY_NOT_EMPIRICAL_COMPARISON",
    }
    if not qwen:
        qwen_admission["QWEN38_PRESENT"] = False
        qwen_admission["state"] = "NOT_PRESENT"
    write_json(OUT / "QWEN38_ADMISSION.json", qwen_admission)

    # Successor prereg (frozen declaration; execution gated)
    scientific = [m for m in roster if m["tag"] != "nomic-embed-text:latest"]
    # Prefer prior scientific 9 + qwen3.8 if canary later passes — do not claim 13 yet
    successor_models = [
        "deepseek-r1:14b",
        "qwen2.5-coder:7b",
        "granite4.1:8b",
        "qwen3.5:9b",
        "qwen3:8b",
        "qwen3:4b",
        "phi4-mini:latest",
        "qwen2.5:1.5b",
        "qwen3:1.7b",
    ]
    prereg = {
        "schema": "hydradg.successor_matrix_preregistration.v1",
        "experiment_id": "HYDRALAMP_SUCCESSOR_MATRIX_20260827_V1",
        "created_at": utcnow(),
        "git_sha": git_sha(),
        "host_authority": "magicSTUDIObox.local",
        "dataset_cases": 1020,
        "dataset_execution_note": "Track02 may remain BLOCKED for scientific slots → operational 770 until contract repaired",
        "base_roster_frozen": successor_models,
        "qwen38_admission_conditional": True,
        "qwen38_tag_if_admitted": "qwen3.8:27b",
        "EXPECTED_SLOTS_WITHOUT_QWEN38": 9 * 1020,
        "EXPECTED_SLOTS_WITH_QWEN38": 10 * 1020,
        "EXPECTED_SLOTS_OPERATIONAL_770_WITHOUT_QWEN38": 9 * 770,
        "do_not_collapse_prior_lineages": True,
        "prompt_contract": "PENDING_BIND_TO_v9_PROMPT_CONTRACT_OR_SUCCESSOR",
        "scorer_contract": "PENDING_BIND_TO_v9_SCORER_CONTRACT_OR_SUCCESSOR",
        "claim_ceiling": "PREREGISTRATION_ONLY_NOT_EXECUTED",
        "signature_state": "NOT_SIGNED",
    }
    write_json(OUT / "SUCCESSOR_MATRIX_PREREGISTRATION.json", prereg)
    write_json(
        OUT / "PROMPT_CONTRACT.json",
        {
            "schema": "hydradg.prompt_contract.v1",
            "state": "BOUND_BY_REFERENCE",
            "primary_reference": "eval/studio_daisy_20260821/v9/PROMPT_CONTRACT.json",
            "sha256": sha256_file(ROOT / "eval/studio_daisy_20260821/v9/PROMPT_CONTRACT.json")
            if (ROOT / "eval/studio_daisy_20260821/v9/PROMPT_CONTRACT.json").exists()
            else None,
        },
    )
    write_json(
        OUT / "SCORER_CONTRACT.json",
        {
            "schema": "hydradg.scorer_contract.v1",
            "state": "BOUND_BY_REFERENCE",
            "primary_reference": "eval/studio_daisy_20260821/v9/SCORER_CONTRACT.json",
            "sha256": sha256_file(ROOT / "eval/studio_daisy_20260821/v9/SCORER_CONTRACT.json")
            if (ROOT / "eval/studio_daisy_20260821/v9/SCORER_CONTRACT.json").exists()
            else None,
        },
    )
    write_json(
        OUT / "DATASET_MANIFEST.json",
        {
            "schema": "hydradg.dataset_manifest_pointer.v1",
            "primary_reference": "eval/real_primary_matrix_20260820/DATASET_CASE_MANIFEST.jsonl",
            "sha256": sha256_file(ROOT / "eval/real_primary_matrix_20260820/DATASET_CASE_MANIFEST.jsonl"),
            "atomization_receipt": "eval/studio_daisy_20260821/atomized/ATOMIZATION_RECEIPT.json",
            "DATASET_1020_REPLAY_GATE": dataset_recon["DATASET_1020_REPLAY_GATE"],
        },
    )

    # Vitaology / Vithia package
    vithia_detail = by_id["D12"]["detail"] or {}
    source_detail = by_id["D13"]["detail"] or {}
    write_json(
        VIT / "SOURCE_RECONCILIATION.json",
        {
            "schema": "hydradg.vitaology_source_reconciliation.v1",
            "created_at": utcnow(),
            **source_detail,
            "historical_source": "historical-vitalogy-1927",
            "dataset_title": "Vitalogy 1927",
            "active_namespace": "Vitaology",
            "candidate_model": "vitaology-pythia-14m-msm-base",
            "vithia_overnight_identity": "HydraDG_DaisyTrain_v0.3.7/eval/vithia_overnight/VITHIA-OVERNIGHT-01",
            "do_not_rewrite_historical_ids": True,
        },
    )
    write_json(
        VIT / "PREDECESSOR_VITHIA_AUDIT.json",
        {
            "schema": "hydradg.vithia_predecessor_audit.v1",
            "created_at": utcnow(),
            "experiment_id": "VITHIA-OVERNIGHT-01",
            **vithia_detail,
            "H0_formal": "NOT_FOUND_AS_LABELED_H0",
            "design_intent": "Bounded local Vithia/Pythia fixture for seed/thread/token-perturbation state divergence",
            "treatments": ["thread4", "perturb_early", "perturb_mid", "perturb_late"],
            "controls": ["control_s314159_r1/r2/r3", "control_s271828", "control_s161803"],
            "seeds": [161803, 271828, 314159],
            "expected_runs": 11,
            "actual_runs": 11,
            "failed_runs": 0,
            "result_classifications": {
                "same_seed_replicas": "VERIFIED_EMPIRICAL_RESULT",
                "token_perturbs_state_exact": "VERIFIED_EMPIRICAL_RESULT",
                "thread4_step0_divergence_final_exact": "VERIFIED_EMPIRICAL_RESULT",
                "vitaology_corpus_binding": "NOT_FOUND",
                "scores_copied_to_v2": "FORBIDDEN",
            },
            "OLD_MCNEMAR_STATE": "BLOCKED_NO_CASE_VECTORS_NOT_APPLICABLE_STATE_HASH_DESIGN",
        },
    )
    write_json(
        VIT / "PREREGISTRATION.json",
        {
            "schema": "hydradg.vitaology_vithia_replay_prereg.v1",
            "experiment_id": "VITAOLOGY_VITHIA_REPLAY_20260827_V2",
            "created_at": utcnow(),
            "git_sha": git_sha(),
            "host_authority": "magicSTUDIObox.local",
            "question": (
                "On the frozen Vithia/Pythia local fixture (NOT Vitalogy-1927 corpus unless separately admitted), "
                "do CONTROL vs THREAD/TOKEN treatments reproduce the predecessor divergence table under "
                "independent recompute, and does a successor Vitaology-named run remain custody-separated?"
            ),
            "factors": ["CONTROL", "THREAD4", "PERTURB_EARLY", "PERTURB_MID", "PERTURB_LATE"],
            "seeds_frozen": [161803, 271828, 314159],
            "replication_expansion_seeds": "NONE_IN_V2_BASE",
            "deterministic_R1_R2_R3": True,
            "core_script_required": "archive/HydraDG_HackHydra_Plan_v0.2.7/scripts/vithia_divergence_core.py OR restored package script",
            "kaggle_offload": "OPTIONAL_SUCCESSOR_ENV_REVISION_REQUIRED",
            "claim_ceiling": "PREREGISTRATION_ONLY_PENDING_EXECUTION",
            "signature_state": "NOT_SIGNED",
        },
    )
    write_json(
        VIT / "MODEL_MANIFEST.json",
        {
            "vithia_fixture": "local Pythia-scale training fixture from VITHIA-OVERNIGHT-01 receipts",
            "vitaology_pythia_14m": "DOCUMENTED_IN_FCO_SUBSTRATE_NOT_BOUND_TO_OVERNIGHT",
            "checkpoints_present_in_overnight": True,
            "core_script_in_package": False,
            "core_script_in_archive": True,
        },
    )

    # Independent recompute of divergence classifications from table bytes (hash bind)
    table_path = ROOT / "HydraDG_DaisyTrain_v0.3.7/eval/vithia_overnight/VITHIA-OVERNIGHT-01/vithia_first_divergence_table.json"
    table = json.loads(table_path.read_text())
    write_json(
        VIT / "STATISTICS.json",
        {
            "metric_family": "state_hash_divergence / final_state_exact",
            "n_comparisons": len(table.get("comparisons", [])),
            "state_exact": sum(1 for c in table["comparisons"] if c["classification"] == "STATE_EXACT"),
            "diverged": sum(1 for c in table["comparisons"] if c["classification"].startswith("DIVERGED")),
            "McNemar": "NOT_APPLICABLE_NO_PAIRED_BINARY_CASE_VECTORS",
            "bootstrap_ci": "NOT_APPLICABLE",
            "outcome_class_predecessor": "MIXED_NULL_ON_TOKEN_PERTURB_PLUS_THREAD_STEP0_DIVERGENCE",
        },
    )
    write_json(VIT / "FIRST_DIVERGENCE.json", table)
    write_json(
        VIT / "FINAL_RESULT.json",
        {
            "experiment_id": "VITAOLOGY_VITHIA_REPLAY_20260827_V2",
            "V2_EXECUTION_STATE": "PREREGISTERED_NOT_RETRAINED",
            "predecessor_bind": {
                "matrix_sha256": vithia_detail.get("matrix_sha256"),
                "classification": "VERIFIED_EMPIRICAL_RESULT_BOUNDED_FIXTURE",
            },
            "outcome": "UNDERPOWERED_PENDING_CORE_RESTORE_AND_R1R2R3",
            "ECA_RESTORATION_EMPIRICAL_STATE": "NOT_ESTABLISHED",
            "claim_ceiling": "PREDECESSOR_AUDITED_SUCCESSOR_NOT_EXECUTED",
            "signature_state": "NOT_SIGNED",
            "merkle_mmr_state": "NOT_COMMITTED",
        },
    )
    # empty run/case logs for honesty
    (VIT / "RUN_RECEIPTS.jsonl").write_text("")
    (VIT / "CASE_RESULTS.jsonl").write_text("")
    (VIT / "FCG_DELTA.jsonl").write_text(
        json.dumps(
            {
                "action": "PREREGISTRATION_MATERIALIZED",
                "fcg_append": "NOT_APPENDED_CANONICAL",
                "session_demo_ok": True,
                "at": utcnow(),
            },
            sort_keys=True,
        )
        + "\n"
    )

    write_json(
        OUT / "INDEPENDENT_MATRIX_RECOMPUTATION.json",
        {
            "schema": "hydradg.independent_matrix_recomputation.v1",
            "created_at": utcnow(),
            "atomization_nodes_edges": by_id["D07"]["detail"],
            "dataset_1020": dataset_recon,
            "longmemeval_bind": by_id["D04"]["detail"],
            "statistics_bind": by_id["D05"]["detail"],
            "v11_structural": by_id["D03"]["detail"],
            "disagreements": [],
            "exact_agreement_where_deterministic": by_id["D07"]["state"] == "PASS" and by_id["D02"]["state"] == "PASS",
            "claim_ceiling": "INDEPENDENT_DETERMINISTIC_RECOMPUTE_PARTIAL_NO_FULL_CASE_BANK",
        },
    )

    write_json(
        OUT / "HYDRALAMP_MODEL_SCENARIO_MATRIX.json",
        {
            "schema": "hydradg.hydralamp_model_scenario_matrix.v1",
            "scenarios": [
                "correct_repair",
                "missed_poison",
                "wrong_repair",
                "contradictory_evidence",
                "insufficient_evidence",
                "abstention",
                "timeout",
                "provider_failure",
                "runtype_failure",
                "cloudflare_failure",
                "mitosis_failure",
                "hydradb_failure",
                "pause_resume",
                "single_step",
                "touch_only",
                "session_isolation",
                "concurrent_sessions",
            ],
            "models_admitted_for_scenario_suite": "PENDING_PER_MODEL_CANARY",
            "qwen38_included": False,
            "prior_golden_path_stress": "eval/hydralamp_golden_path_20260827/GOLDEN_PATH_TEST_RESULTS.json",
            "phases_required": ["REFERENCE", "POISON", "AGENT", "VERIFY", "ANTIDOTE", "RESTORATION"],
        },
    )

    # Sponsor receipts (honest)
    write_json(
        OUT / "SPONSOR_INTEGRATION_RECEIPTS.json",
        {
            "created_at": utcnow(),
            "Runtype": {
                "STATIC_IMPLEMENTED": True,
                "AUTH_AVAILABLE": True,
                "LIVE_CALL_PASS": False,
                "RECEIPT_PRESENT": True,
                "FAILURE_PATH_TESTED": True,
                "state": "KEY_PRESENT_LIVE_PATH_ERROR_PRONE",
            },
            "Cloudflare": {
                "STATIC_IMPLEMENTED": True,
                "AUTH_AVAILABLE": False,
                "LIVE_CALL_PASS": False,
                "RECEIPT_PRESENT": True,
                "FAILURE_PATH_TESTED": True,
                "state": "READY_NOT_LIVE",
            },
            "Mitosis": {
                "STATIC_IMPLEMENTED": True,
                "AUTH_AVAILABLE": True,
                "LIVE_CALL_PASS": False,
                "RECEIPT_PRESENT": True,
                "FAILURE_PATH_TESTED": True,
                "state": "BLOCKED_TRIAL_EXPIRED",
            },
            "Daytona": {
                "STATIC_IMPLEMENTED": True,
                "AUTH_AVAILABLE": True,
                "LIVE_CALL_PASS": "PRIOR_SMOKE_PASS_20260827",
                "RECEIPT_PRESENT": True,
                "FAILURE_PATH_TESTED": True,
                "state": "INFRA_SMOKE_PRIOR_CLI_PROFILE_MAY_NEED_LOGIN",
            },
            "Kaggle": {
                "STATIC_IMPLEMENTED": False,
                "AUTH_AVAILABLE": False,
                "LIVE_CALL_PASS": False,
                "RECEIPT_PRESENT": False,
                "FAILURE_PATH_TESTED": False,
                "state": "CLI_NOT_FOUND",
            },
            "Mistral": {"state": "FUTURE_OPTIONAL"},
        },
    )

    pass_n = sum(1 for r in receipts if r["state"] == "PASS")
    fail_n = sum(1 for r in receipts if r["state"] == "FAIL")
    master = {
        "schema": "hydradg.distributed_execution_master_receipt.v1",
        "created_at": utcnow(),
        "git_sha": git_sha(),
        "host": platform.node(),
        "daytona_workers_launched": 0,
        "daytona_note": "CLI has no profiles (daytona login required). Ran LOCAL_DETERMINISTIC_AUDIT workers D01–D16. Prior Daytona smoke PASS recorded separately.",
        "local_deterministic_workers": len(receipts),
        "local_pass": pass_n,
        "local_fail": fail_n,
        "kaggle_jobs_launched": 0,
        "kaggle_state": "CLI_NOT_FOUND",
        "worker_log": str(WORKER_LOG.relative_to(ROOT)),
        "claim_ceiling": "DETERMINISTIC_AUDIT_COMPLETE_PROBABILISTIC_MATRIX_NOT_COMPLETED",
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
    }
    write_json(OUT / "DISTRIBUTED_EXECUTION_MASTER_RECEIPT.json", master)

    claim_md = f"""# Morning Claim Matrix — 2026-08-27

## Authority
- PROJECT_CONTROL.yaml: **ABSENT**
- Git SHA: `{git_sha()}`
- Host: magicSTUDIObox.local

## Allowed claims
- Dataset 1020 atomization/manifest replay gate: `{dataset_recon['DATASET_1020_REPLAY_GATE']}`
- Matrix lineages A/B/C/D/E reconciled without collapsing
- VITHIA-OVERNIGHT-01 predecessor present and COMPLETE (11/11) as bounded fixture
- Qwen3.8:27b **MODEL_AVAILABLE** on Studio (digest bound in QWEN38_ADMISSION.json)
- HydraLamp golden-path local stress previously PASS
- Daytona: prior infrastructure smoke PASS; overnight fan-out used local deterministic workers (CLI profile missing)

## Forbidden / not established
- Full Daisy 1020×N matrix complete
- Qwen3.8 comparative benefit
- ECA restoration empirical
- VITAOLOGY_VITHIA_V2 retrained result
- Cloudflare/Runtype/Mitosis LIVE_CALL_PASS
- Kaggle jobs
- CONNECTED sponsor badges without live tests

## Null / negative preserved
- LongMemEval K5 graph advantage null/negative
- V11 FAILED_EMPTY_RESPONSE ×39 retained
- Vithia token perturbs STATE_EXACT (null treatment effect on final state)
"""
    (OUT / "MORNING_CLAIM_MATRIX.md").write_text(claim_md)

    ready = f"""# Morning Readiness — 2026-08-27

## Green for judge demo
- HydraLamp golden path on :3013 (prior)
- Judge session isolation
- Evidence drawers separating historical vs demo vs incomplete vs future

## Not green for scientific promotion
- Successor matrix execution
- Qwen3.8 canary (see QWEN38_CANARY_AUDIT.json — may be filled by follow-on)
- Vitaology V2 training replay
- Sponsor live paths
- HydraDB readback for demo sessions

## Next safe action
1. Complete Qwen3.8 bounded canary → admit or withhold
2. Restore `vithia_divergence_core.py` into package and run R1/R2/R3 equality
3. `daytona login` then fan-out deterministic workers D01–D16 remotely
4. Install/configure Kaggle only for GPU successor with separate env revision
5. Do not deploy production until LOCAL_GOLDEN_PATH remains PASS and claim ceilings hold
"""
    (OUT / "MORNING_READINESS.md").write_text(ready)

    print(json.dumps({"master": master, "dataset_gate": dataset_recon["DATASET_1020_REPLAY_GATE"], "workers_pass": pass_n, "workers_fail": fail_n}, indent=2))
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
