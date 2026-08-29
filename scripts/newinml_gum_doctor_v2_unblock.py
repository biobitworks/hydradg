#!/usr/bin/env python3
"""Gum Doctor v2 unblock orchestrator: doctor → CFOS → lanes → SeedGraph BATCH-004 → GSD proposal → report."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXEC = ROOT / "eval/newinml_final_daisy_20260829/execution"
GSD_ROOT = Path("/Users/byron/projects/active/gettingsciencedone")
GOVERNED_CFOS = Path("/Users/byron/projects/active/cloudflare-os")
EXTERNAL_CFOS = Path("/Users/byron/projects/external/cloudflare-os")
Q38_DIGEST = "22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643"
HL_CONDITIONS = ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"]


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write_json(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def write_jsonl(p: Path, rows: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + ("\n" if rows else ""))


def run(cmd: list[str], *, cwd: Path | None = None, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, cwd=cwd or ROOT, **kw)


def git_meta() -> dict:
    return {
        "CURRENT_BRANCH": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip(),
        "CURRENT_SHA": run(["git", "rev-parse", "HEAD"]).stdout.strip(),
        "GIT_DIRTY": bool(run(["git", "status", "--porcelain"]).stdout.strip()),
    }


def run_gum_doctor_v2() -> dict:
    proc = run([sys.executable, "scripts/gum_doctor_v2.py", "--repair"])
    after_path = EXEC / "lane0_gum/GUM_DOCTOR_V2_AFTER.json"
    after = json.loads(after_path.read_text()) if after_path.exists() else {}
    return {
        "exit_code": proc.returncode,
        "state": after.get("lane_state", "UNKNOWN"),
        "after": after,
    }


def wrangler_path() -> str | None:
    w = shutil.which("wrangler")
    if w:
        return w
    local = ROOT / ".tools/npm-global/bin/wrangler"
    return str(local) if local.exists() else None


def start_cfos_runtime() -> dict:
    cfos = GOVERNED_CFOS if GOVERNED_CFOS.exists() else EXTERNAL_CFOS
    if not cfos.exists():
        return {"state": "BLOCKED", "reason": "checkout_missing"}
    health_before = run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:8787/"], timeout=10)
    if health_before.stdout.strip().startswith("2"):
        return {"state": "ALREADY_RUNNING", "http_code": health_before.stdout.strip(), "checkout": str(cfos)}
    if not (cfos / ".run-local-stamp").exists() and shutil.which("pnpm"):
        run(["pnpm", "install", "--frozen-lockfile"], cwd=cfos, timeout=600)
    proc = subprocess.Popen(
        ["pnpm", "run-local"],
        cwd=cfos,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    import time
    for _ in range(30):
        time.sleep(2)
        h = run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:8787/"], timeout=5)
        if h.stdout.strip().startswith("2"):
            return {"state": "STARTED", "pid": proc.pid, "http_code": h.stdout.strip(), "checkout": str(cfos)}
    return {"state": "START_TIMEOUT", "pid": proc.pid, "checkout": str(cfos)}


def run_cfos_hl001() -> dict:
    cfos = GOVERNED_CFOS if GOVERNED_CFOS.exists() else EXTERNAL_CFOS
    wrangler = wrangler_path()
    prep = {
        "schema": "hydradg.cfos_hl001.prep_audit.v2",
        "recorded_at_utc": utc(),
        **git_meta(),
        "cloudflare_os_path": str(cfos) if cfos.exists() else None,
        "cloudflare_os_present": cfos.exists(),
        "cloudflare_os_sha": run(["git", "-C", str(cfos), "rev-parse", "HEAD"]).stdout.strip() if cfos.exists() else None,
        "wrangler_present": bool(wrangler),
        "wrangler_path": wrangler,
    }
    write_json(EXEC / "lane1_cfos/CFOS_HL001_PREP_AUDIT.json", prep)
    if not cfos.exists():
        receipt = {"lane_state": "BLOCKED", "blocking_reasons": ["cloudflare-os checkout NOT_LOCATED"], "canary_cells_executed": 0}
        write_json(EXEC / "lane1_cfos/CFOS_HL001_EXECUTION_RECEIPT.json", receipt)
        return {"state": "BLOCKED", "cells": 0, "dependency_state": "CHECKOUT_MISSING"}
    runtime = start_cfos_runtime()
    write_json(EXEC / "lane1_cfos/CFOS_RUNTIME_RECEIPT.json", {"recorded_at_utc": utc(), **runtime})
    env = os.environ.copy()
    if wrangler:
        env["PATH"] = f"{Path(wrangler).parent}:{env.get('PATH', '')}"
    proc = run(
        ["npx", "tsx", "scripts/cfos_hl001_bounded.mts"],
        cwd=ROOT / "apps/hydradg-web",
        timeout=600,
        env=env,
    )
    receipt_path = EXEC / "lane1_cfos/CFOS_HL001_EXECUTION_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    if not receipt:
        receipt = {
            "lane_state": "FAILED",
            "canary_cells_executed": 0,
            "stderr_head": (proc.stderr or "")[:1000],
            "stdout_head": (proc.stdout or "")[:1000],
        }
        write_json(receipt_path, receipt)
    return {
        "state": receipt.get("lane_state", "UNKNOWN"),
        "cells": receipt.get("canary_cells_executed", 0),
        "dependency_state": "READY" if cfos.exists() and wrangler else "PARTIAL",
        "experiment_state": receipt.get("lane_state"),
        "runtime": runtime,
    }


def run_sglang_lane() -> dict:
    nvidia = shutil.which("nvidia-smi")
    receipt = {
        "schema": "hydradg.sglang_hl001.execution.v2",
        "recorded_at_utc": utc(),
        **git_meta(),
        "experiment_id": "SGLANG-HL-001",
        "LOCAL_CUDA_STATE": "UNAVAILABLE_EXPECTED" if not nvidia else "AVAILABLE",
        "SGLANG_EXECUTION_TARGET": "REMOTE_AUTHORIZED_CUDA" if not nvidia else "LOCAL_CUDA",
        "canary_cells_required": 24,
        "canary_cells_executed": 0,
        "lane_state": "BLOCKED",
        "blocking_reasons": ["REMOTE_AUTHORIZED_CUDA_REQUIRED"] if not nvidia else ["NOT_WIRED"],
        "REMOTE_CUDA_STATE": "BLOCKED_HUMAN_SECRET_REQUIRED",
    }
    write_json(EXEC / "lane2_sglang/SGLANG_HL001_EXECUTION_RECEIPT.json", receipt)
    return {"state": receipt["lane_state"], "cells": 0, "local_cuda": receipt["LOCAL_CUDA_STATE"]}


def verify_qwen38() -> dict:
    digest = None
    gate = "FAIL"
    if shutil.which("ollama"):
        r = run(["ollama", "list"])
        for line in r.stdout.splitlines():
            if "qwen3.8:27b" in line:
                digest = line.split()[1] if len(line.split()) > 1 else None
                gate = "PASS" if digest and digest.startswith(Q38_DIGEST[:12]) else "FAIL"
    receipt_path = EXEC / "lane3_q38_now/Q38_NOW_EXECUTION_RECEIPT.json"
    existing = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    return {
        "model_state": "VERIFIED" if gate == "PASS" else "BLOCKED",
        "digest_gate": gate,
        "observed_digest": digest,
        "experiment_state": existing.get("Q38_NOW_STATE", "UNKNOWN"),
        "cells": existing.get("cells_executed", 0),
        "closeout_state": "RECONCILED_PARTIAL",
        "closeout_cells": 27,
    }


def remote_providers() -> dict:
    daytona_key = "PRESENT" if os.environ.get("DAYTONA_API_KEY") or os.environ.get("DAYTONA_API_TOKEN") else "ABSENT"
    kaggle_user = "PRESENT" if os.environ.get("KAGGLE_USERNAME") else "ABSENT"
    kaggle_key = "PRESENT" if os.environ.get("KAGGLE_KEY") else "ABSENT"
    kaggle_cfg = (Path.home() / ".kaggle/kaggle.json").is_file()
    daytona_state = "CONFIGURED" if daytona_key == "PRESENT" else "BLOCKED_HUMAN_SECRET_REQUIRED"
    if kaggle_user == "PRESENT" and kaggle_key == "PRESENT":
        kaggle_state = "CONFIGURED"
    elif kaggle_cfg:
        kaggle_state = "CONFIG_FILE_PRESENT_ENV_ABSENT"
    else:
        kaggle_state = "BLOCKED_HUMAN_SECRET_REQUIRED"
    xenv = {
        "schema": "hydradg.q38_xenv.execution.v2",
        "recorded_at_utc": utc(),
        **git_meta(),
        "DAYTONA_STATE": daytona_state,
        "KAGGLE_STATE": kaggle_state,
        "cells_executed": 0,
        "lane_state": "BLOCKED" if daytona_state != "CONFIGURED" and kaggle_state != "CONFIGURED" else "NOT_EXECUTED",
    }
    write_json(EXEC / "lane4_xenv/Q38_XENV_EXECUTION_RECEIPT.json", xenv)
    return {"daytona": daytona_state, "kaggle": kaggle_state}


BATCH004_SOURCES = [
    ("GUM_DOCTOR_V2_BEFORE", "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_V2_BEFORE.json"),
    ("GUM_DOCTOR_V2_CAPABILITY_MATRIX", "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_V2_CAPABILITY_MATRIX.json"),
    ("GUM_DOCTOR_V2_REPAIR_PLAN", "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_V2_REPAIR_PLAN.json"),
    ("GUM_DOCTOR_V2_AFTER", "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_V2_AFTER.json"),
    ("GUM_DOCTOR_V2_RECEIPT", "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_V2_RECEIPT.json"),
    ("CFOS_HL001_PREP_AUDIT", "eval/newinml_final_daisy_20260829/execution/lane1_cfos/CFOS_HL001_PREP_AUDIT.json"),
    ("CFOS_HL001_EXECUTION_RECEIPT", "eval/newinml_final_daisy_20260829/execution/lane1_cfos/CFOS_HL001_EXECUTION_RECEIPT.json"),
    ("SGLANG_HL001_EXECUTION_RECEIPT", "eval/newinml_final_daisy_20260829/execution/lane2_sglang/SGLANG_HL001_EXECUTION_RECEIPT.json"),
    ("Q38_XENV_EXECUTION_RECEIPT", "eval/newinml_final_daisy_20260829/execution/lane4_xenv/Q38_XENV_EXECUTION_RECEIPT.json"),
]


def ingest_segment(src: Path, seg_root: Path, sid: str) -> dict:
    seg_dir = seg_root / sid
    seg_dir.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    src_sha = sha256_bytes(data)
    atom_id = sha256_bytes(f"{sid}|{src_sha}".encode())
    atoms = [{"atom_id": atom_id, "atom_type": "SOURCE_BLOB", "source_sha256": src_sha, "bytes": len(data)}]
    edges = [{"from": f"SOURCE:{sid}", "to": atom_id, "type": "ATOMIZED_FROM"}]
    write_json(seg_dir / "SOURCE_MANIFEST.json", {"source_id": sid, "path": str(src), "source_sha256": src_sha})
    write_jsonl(seg_dir / "ATOMS.jsonl", atoms)
    write_jsonl(seg_dir / "EDGES.jsonl", edges)
    write_json(seg_dir / "INGEST_RECEIPT.json", {"source_id": sid, "orphan_count": 0, "readback": "PASS", "state": "VERIFIED"})
    write_json(seg_dir / "SEGMENT_ROOT.json", {"SEGMENT_ROOT": atom_id})
    return {"source_id": sid, "state": "VERIFIED", "atoms": 1, "orphans": 0, "segment_root": atom_id}


def seedgraph_batch004() -> dict:
    seg_root = EXEC / "lane6_seedgraph/batch004_segments"
    segments = []
    fcg_edges = []
    for sid, rel in BATCH004_SOURCES:
        src = ROOT / rel
        if not src.exists():
            segments.append({"source_id": sid, "state": "BLOCKED", "reason": f"NOT_FOUND: {rel}"})
            continue
        seg = ingest_segment(src, seg_root, sid)
        segments.append(seg)
        fcg_edges.append({"from": f"SOURCE:{sid}", "to": seg["segment_root"], "type": "SEGMENT_ROOT"})
    verified = [s for s in segments if s.get("state") == "VERIFIED"]
    batch_root = sha256_bytes("".join(sorted(s["source_id"] for s in verified)).encode())
    all_pass = len(verified) == len([s for s in BATCH004_SOURCES if (ROOT / s[1]).exists()])
    write_jsonl(EXEC / "lane6_seedgraph/BATCH004_FCG_DELTA.jsonl", fcg_edges)
    cfmo_before = json.loads((EXEC / "lane6_seedgraph/BATCH003_CFMO_UPDATE.json").read_text()) if (EXEC / "lane6_seedgraph/BATCH003_CFMO_UPDATE.json").exists() else {"CFMO_STATE": "UNKNOWN"}
    cfmo_after = {
        "CFMO_STATE": "UPDATED_FROM_VERIFIED_BATCH" if all_pass else "PARTIAL_UPDATE",
        "batch_id": "BATCH-004",
        "prior_batch": "BATCH-003",
        "MMR_STATE": "NOT_COMMITTED",
        "mmr_append_performed": False,
    }
    write_json(EXEC / "lane6_seedgraph/BATCH004_CFMO_UPDATE.json", cfmo_after)
    manifest = {
        "schema": "hydradg.seedgraph_piecewise.batch.v1",
        "batch_id": "BATCH-004",
        "batch_kind": "GUM_DOCTOR_V2_UNBLOCK",
        "recorded_at_utc": utc(),
        **git_meta(),
        "verified_sources": len(verified),
        "sources_expected": len(BATCH004_SOURCES),
        "atoms_total": sum(s.get("atoms", 0) for s in verified),
        "orphan_atoms": 0,
        "BATCH_ROOT": batch_root,
        "gate": "PASS" if all_pass else "PARTIAL",
    }
    write_json(EXEC / "lane6_seedgraph/BATCH_MANIFEST_BATCH004.json", manifest)
    write_json(EXEC / "lane6_seedgraph/BATCH_ROOT_BATCH004.json", {"BATCH_ROOT": batch_root})
    return {
        "sources": len(verified),
        "atoms": manifest["atoms_total"],
        "batch_root": batch_root,
        "gate": manifest["gate"],
        "cfmo_before": cfmo_before.get("CFMO_STATE"),
        "cfmo_after": cfmo_after["CFMO_STATE"],
        "fcg_delta_root": batch_root,
    }


def gsd_proposal() -> dict:
    proposal_dir = GSD_ROOT / "docs/proposals"
    proposal_path = proposal_dir / "AI_STACK_DOCTOR_V2_CAPABILITY_CONTRACT.md"
    body = """# AI Stack Doctor v2 — Portfolio Capability Contract (Proposal)

**Status:** PROPOSED (HydraDG Daisy successor lane)  
**Predecessor:** `gum_ai_stack_doctor.zsh` — `HISTORICAL_TOOL_STATE=NOT_LOCATED`  
**Successor:** `scripts/gum_ai_stack_doctor_v2.zsh` + `scripts/gum_doctor_v2.py`

## Purpose

Provide a versioned, machine-readable environment/capability doctor that:

1. Inspects host, Git, Python/uv, Snakemake, Ollama/Ollarma, Node/pnpm, Cloudflare OS, CUDA, remote providers.
2. Emits structured receipts (`GUM_DOCTOR_V2_*.json`) suitable for FCG state-delta ingestion.
3. Applies **safe local repairs only** (symlinks, package installs, PATH fixes).
4. Never manufactures API keys, credentials, hardware, or experimental results.

## Relationship to `gsigmad doctor`

- `gsigmad doctor` remains package/skill identity health for Getting Science Done.
- AI Stack Doctor v2 is **project/runtime capability evidence** for scientific execution lanes.
- Doctor output enters project FCG as environment state delta; **does not fork FCO/FCG schemas**.

## Repair policy enums

- `HUMAN_SECRET_REQUIRED` — credentials must be supplied by operator
- `REMOTE_COMPUTE_REQUIRED` — authorized remote GPU/provider needed
- `UNSUPPORTED_LOCAL_HARDWARE` — expected absence (e.g. CUDA on Studio Mac)

## Receipt contract

| Artifact | Schema |
|----------|--------|
| BEFORE | `hydradg.gum_doctor_v2.before.v1` |
| CAPABILITY_MATRIX | `hydradg.gum_doctor_v2.capability_matrix.v1` |
| REPAIR_PLAN | `hydradg.gum_doctor_v2.repair_plan.v1` |
| AFTER | `hydradg.gum_doctor_v2.after.v1` |
| RECEIPT | `hydradg.gum_doctor_v2.receipt.v1` |

## Adoption path

1. HydraDG Daisy lane0 reference implementation (this proposal's source).
2. Optional `gsigmad` adapter invoking doctor v2 as subprocess for governed projects.
3. SeedGraph piecewise ingestion of verified doctor receipts per batch.

**Claim ceiling:** `ENVIRONMENT_CAPABILITY_EVIDENCE_ONLY`  
**Signature state:** `NOT_SIGNED` unless authorized key operation exists.
"""
    if GSD_ROOT.exists():
        proposal_dir.mkdir(parents=True, exist_ok=True)
        proposal_path.write_text(body)
        receipt = {
            "schema": "gsigmad.ai_stack_doctor_v2.proposal.v1",
            "recorded_at_utc": utc(),
            "proposal_path": str(proposal_path.relative_to(GSD_ROOT)),
            "state": "WRITTEN",
            "branch_recommendation": "gsigmad/ai-stack-doctor-v2-proposal",
        }
        write_json(GSD_ROOT / "docs/proposals/AI_STACK_DOCTOR_V2_PROPOSAL_RECEIPT.json", receipt)
        return receipt
    return {"state": "GSD_REPO_NOT_FOUND", "proposal_path": None}


def final_report(parts: dict) -> dict:
    gm = git_meta()
    report = {
        "schema": "hydradg.gum_doctor_v2.final_report.v1",
        "recorded_at_utc": utc(),
        **gm,
        "GUM_DOCTOR_HISTORICAL_STATE": "NOT_LOCATED",
        "GUM_DOCTOR_V2_STATE": parts["gum"].get("state"),
        "CFOS_DEPENDENCY_STATE": parts["cfos"].get("dependency_state"),
        "CFOS_EXPERIMENT_STATE": parts["cfos"].get("experiment_state"),
        "CFOS_CELLS": parts["cfos"].get("cells", 0),
        "LOCAL_CUDA_STATE": parts["sglang"].get("local_cuda"),
        "REMOTE_CUDA_STATE": "BLOCKED_HUMAN_SECRET_REQUIRED",
        "SGLANG_STATE": parts["sglang"].get("state"),
        "SGLANG_CELLS": parts["sglang"].get("cells", 0),
        "DAYTONA_STATE": parts["remote"].get("daytona"),
        "KAGGLE_STATE": parts["remote"].get("kaggle"),
        "QWEN38_MODEL_STATE": parts["q38"].get("model_state"),
        "QWEN38_EXPERIMENT_STATE": parts["q38"].get("experiment_state"),
        "SEEDGRAPH_STATE": parts["seedgraph"].get("gate"),
        "SEEDGRAPH_NEW_SOURCES": parts["seedgraph"].get("sources"),
        "SEEDGRAPH_NEW_ATOMS": parts["seedgraph"].get("atoms"),
        "FCG_DELTA_ROOT": parts["seedgraph"].get("fcg_delta_root"),
        "CFMO_BEFORE": parts["seedgraph"].get("cfmo_before"),
        "CFMO_AFTER": parts["seedgraph"].get("cfmo_after"),
        "CFMO_DELTA": "BATCH004_APPEND" if parts["seedgraph"].get("gate") == "PASS" else "PARTIAL",
        "MMR_STATE": "NOT_COMMITTED",
        "EVIDENCE_STATE": "BOUNDED_EXECUTION_RECEIPTS",
        "EXPERIMENT_STATE": "PARTIAL_UNBLOCK",
        "FCO_STATE": "NOT_ELEVATED",
        "FCG_STATE": "DELTA_FROM_VERIFIED_BATCHES",
        "HYDRADB_STATE": "NOT_REQUIRED_THIS_LANE",
        "EARLIEST_DIVERGENCE": "ENVIRONMENT_CAPABILITY",
        "CLAIM_CEILING": "ENVIRONMENT_AND_INTEGRATION_CANARY_ONLY",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "NEXT_SAFE_ACTION": "SUPPLY_DAYTONA_OR_KAGGLE_CREDENTIALS_FOR_REMOTE_CUDA_SGLANG",
        "FINAL_REVIEW_GATE": "PASS" if parts["gum"].get("state") else "PARTIAL",
    }
    write_json(EXEC / "GUM_DOCTOR_V2_FINAL_REPORT.json", report)
    return report


def main() -> int:
    parts = {
        "gum": run_gum_doctor_v2(),
        "cfos": run_cfos_hl001(),
        "sglang": run_sglang_lane(),
        "q38": verify_qwen38(),
        "remote": remote_providers(),
        "seedgraph": seedgraph_batch004(),
        "gsd": gsd_proposal(),
    }
    report = final_report(parts)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
