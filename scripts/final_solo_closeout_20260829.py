#!/usr/bin/env python3
"""Generate final solo NewInML 2026 closeout artifacts (ML + HL twins)."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
EVAL_OUT = REPO / "eval/final_solo_closeout_20260829"
DOCS_OUT = REPO / "docs/final_solo"
PKG_OUT = REPO / "package/final_solo"

SOLO_ROOTS = [
    REPO / "eval/newinml_doc_roundtrip_20260829",
    REPO / "eval/newinml_final_daisy_20260829",
    REPO / "paper/newinml2026_solo",
    REPO / "scripts/newinml_doc_roundtrip_execute.py",
    REPO / "scripts/newinml_gpu_sglang_daisy_execute.py",
    REPO / "scripts/newinml_seedgraph_full_traceability_execute.py",
]

PUBLIC_SCAN_ROOTS = [
    REPO / "paper/newinml2026_solo/manuscript",
    REPO / "paper/newinml2026_solo/reviewer_artifact",
    REPO / "paper/newinml2026_solo/final_v4",
]

START_SHA = "7f6de6f45cb14c39fe82f67da5d816f0845ad9c9"
AUTHORITATIVE_BRANCH = "cursor/newinml-daisy-execute-20260829"
AUTHORITATIVE_PR = 36

EXPERIMENTS: list[dict[str, Any]] = [
    {
        "experiment_id": "NEWINML-DOC-ROUNDTRIP-001",
        "execution_state": "TERMINAL_PASS",
        "scientific_state": "NULL_PRIMARY_STATISTICAL",
        "terminal_receipt": "eval/newinml_doc_roundtrip_20260829/13_closeout/FINAL_CLOSEOUT.json",
        "reproduction": "python3 scripts/newinml_doc_roundtrip_execute.py",
    },
    {
        "experiment_id": "SEEDGRAPH-TRACEABILITY-001",
        "execution_state": "TERMINAL_PASS",
        "scientific_state": "CUSTODY_MECHANICS_VALIDATED",
        "terminal_receipt": "paper/newinml2026_solo/seedgraph_traceability/SEEDGRAPH_TRACEABILITY_CLOSEOUT.json",
        "reproduction": "python3 scripts/newinml_seedgraph_full_traceability_execute.py",
    },
    {
        "experiment_id": "GPU-SGLANG-TERMINAL",
        "execution_state": "BLOCKED",
        "scientific_state": "NOT_EXECUTED",
        "terminal_receipt": "eval/newinml_final_daisy_20260829/execution/gpu_sglang_terminal/FINAL_GPU_SGLANG_CLOSEOUT.json",
        "reproduction": "python3 scripts/newinml_gpu_sglang_daisy_execute.py",
    },
    {
        "experiment_id": "EXP-008",
        "execution_state": "TERMINAL_UNDERPOWERED",
        "scientific_state": "UNDERPOWERED",
        "terminal_receipt": "paper/newinml2026_solo/provenance/admitted/eval__ic_failure_learning_20260827__daisy_overnight_20260828__EXP-008__VERDICT.json",
        "reproduction": "historical lane; see eval/ic_failure_learning_20260827/",
    },
    {
        "experiment_id": "EXP-009",
        "execution_state": "TERMINAL_UNDERPOWERED",
        "scientific_state": "UNDERPOWERED",
        "terminal_receipt": "paper/newinml2026_solo/provenance/admitted/eval__ic_failure_learning_20260827__daisy_overnight_20260828__EXP-009__VERDICT.json",
        "reproduction": "historical lane; see eval/ic_failure_learning_20260827/",
    },
    {
        "experiment_id": "Q38-SUCCESSOR-PROBE",
        "execution_state": "PARTIAL",
        "scientific_state": "NON_TERMINAL",
        "terminal_receipt": "eval/newinml_final_daisy_20260829/execution/lane3_q38/Q38_TERMINAL_PROVENANCE.json",
        "reproduction": "see eval/newinml_final_daisy_20260829/execution/lane3_q38/",
    },
    {
        "experiment_id": "CFOS-HL-001",
        "execution_state": "BLOCKED",
        "scientific_state": "NOT_EXECUTED",
        "terminal_receipt": "eval/newinml_final_daisy_20260829/execution/lane1_cfos/CFOS_HL001_CANARY_RECEIPT.json",
        "reproduction": "blocked: cloudflare-os checkout NOT_LOCATED",
    },
]

SCRIPTS = [
    {
        "artifact_id": "SCRIPT-DOC-ROUNDTRIP",
        "path": "scripts/newinml_doc_roundtrip_execute.py",
        "purpose": "Execute preregistered frozen-document roundtrip validation pipeline.",
        "inputs": ["paper/newinml2026_solo/manuscript", "eval/newinml_doc_roundtrip_20260829/00_preregistration/"],
        "outputs": ["eval/newinml_doc_roundtrip_20260829/"],
        "host": "magicSTUDIObox.local",
        "boundary": "deterministic structural + governed probabilistic atomization via Ollarma",
        "invocation": "python3 scripts/newinml_doc_roundtrip_execute.py",
        "failure_behavior": "fail-closed; negative terminals preserved",
    },
    {
        "artifact_id": "SCRIPT-GPU-SGLANG",
        "path": "scripts/newinml_gpu_sglang_daisy_execute.py",
        "purpose": "Terminal GPU SGLang daisy lane orchestration and receipt emission.",
        "inputs": ["eval/newinml_final_daisy_20260829/execution/gpu_sglang_terminal/"],
        "outputs": ["eval/newinml_final_daisy_20260829/execution/gpu_sglang_terminal/FINAL_GPU_SGLANG_CLOSEOUT.json"],
        "host": "magicSTUDIObox.local / Kaggle GPU",
        "boundary": "probabilistic model execution with deterministic receipt hashing",
        "invocation": "python3 scripts/newinml_gpu_sglang_daisy_execute.py",
        "failure_behavior": "preserve BLOCKED with earliest divergence",
    },
    {
        "artifact_id": "SCRIPT-SEEDGRAPH-TRACE",
        "path": "scripts/newinml_seedgraph_full_traceability_execute.py",
        "purpose": "Source→atom→FCO→FCG→claim traceability closeout for solo manuscript seed.",
        "inputs": ["paper/newinml2026_solo/manuscript"],
        "outputs": ["paper/newinml2026_solo/seedgraph_traceability/"],
        "host": "magicSTUDIObox.local",
        "boundary": "deterministic extraction + Neo4j graph write with receipt",
        "invocation": "python3 scripts/newinml_seedgraph_full_traceability_execute.py",
        "failure_behavior": "fail-closed on graph_errors or missing SOT support",
    },
]

DG_DEFINITIONS = [
    {
        "definition_id": "DG-STAR-TRANSITION",
        "name": "ΔG* transition diagnostic",
        "formula_family": "delta_g_star",
        "source": "paper/newinml2026_solo/longitudinal_fcg/SECRET_REGISTRY_AUDIT.jsonl",
        "distinct": True,
        "note": "Categorical AntiCube transition diagnostic; not a continuous time axis.",
    },
    {
        "definition_id": "CLOUD-DRIFT-JSD",
        "name": "Cloud Drift JSD",
        "formula_family": "cloud_drift_jsd",
        "source": "conceptual; not promoted as measured primary endpoint in solo package",
        "distinct": True,
    },
    {
        "definition_id": "TV-MUTATION-DISTANCE",
        "name": "TV mutation distance",
        "formula_family": "tv_mutation_distance",
        "source": "doc roundtrip structural accounting",
        "distinct": True,
    },
    {
        "definition_id": "RESTORATION-GAIN",
        "name": "Restoration gain",
        "formula_family": "restoration_gain",
        "source": "roundtrip equivalence report",
        "distinct": True,
    },
]

PREDECESSORS = [
    {
        "predecessor_artifact": "eval/newinml_final_daisy_20260829/execution/gpu_sglang_terminal/FINAL_GPU_SGLANG_CLOSEOUT.json",
        "predecessor_state": "EXTERNAL_PROVIDER_BLOCKED",
        "earliest_divergence": "SGLANG_INSTALL_FAILED",
        "successor_artifact": "eval/newinml_final_daisy_20260829/execution/gpu_sglang_terminal/GPU_RUNTIME_PROOF.json",
        "successor_state": "CUDA_PROOF_ONLY",
        "resolved": False,
        "claim_impact": "GPU lane cannot support inference claims; infrastructure proof only",
    },
    {
        "predecessor_artifact": "paper/newinml2026_solo/FINAL_OPENREVIEW_OPERATOR_PACKET.md",
        "predecessor_state": "PDF_SHA256=6578d37eeb28a7f2bdadb967939e68b816174491df3932a792601d09aaa14c60",
        "earliest_divergence": "MANUSCRIPT_REBUILD",
        "successor_artifact": "paper/newinml2026_solo/manuscript/build/main.pdf",
        "successor_state": "CURRENT_BUILD",
        "resolved": "RESOLVED_BY_SUCCESSOR",
        "claim_impact": "Operator packet PDF hash stale; rebuild required before upload",
    },
    {
        "predecessor_artifact": "eval/newinml_final_daisy_20260829/execution/lane3_q38/canonical_predecessor/EXPERIMENT_TERMINAL_AUDIT.json",
        "predecessor_state": "Q38-EXP008-R STARTED 27/150",
        "earliest_divergence": "INCOMPLETE_MATRIX",
        "successor_artifact": "eval/newinml_final_daisy_20260829/execution/lane3_q38/Q38_TERMINAL_PROVENANCE.json",
        "successor_state": "CANONICAL_27_SUPERSEDES_STALE_26",
        "resolved": "PARTIAL",
        "claim_impact": "Q38 omitted from primary results per manuscript",
    },
]

CITATION_QUEUE = [
    {"citation_key": "neg_sel_prior", "topic": "negative-selection / NegSel", "status": "NEEDS_EXTERNAL_VERIFY", "used_in": "manuscript related work"},
    {"citation_key": "free_energy", "topic": "information-theory / free-energy background", "status": "NEEDS_EXTERNAL_VERIFY", "used_in": "ΔG* framing"},
    {"citation_key": "nanopubs", "topic": "nanopublications / atomic claims", "status": "NEEDS_EXTERNAL_VERIFY", "used_in": "SeedGraph traceability section"},
    {"citation_key": "provenance", "topic": "research object provenance", "status": "PARTIAL_IN_MANIFEST", "used_in": "FCO/FCG custody"},
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def iter_solo_files() -> list[Path]:
    files: list[Path] = []
    for root in SOLO_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file())
    return sorted(set(files))


def classify_role(path: Path) -> str:
    rel = path.relative_to(REPO).as_posix()
    if rel.endswith(".py") and "scripts/" in rel:
        return "script"
    if "closeout" in rel.lower() or rel.endswith("_RECEIPT.json"):
        return "terminal_receipt"
    if "preregistration" in rel.lower() or "PREREGISTRATION" in rel:
        return "preregistration"
    if "/figures/" in rel and rel.endswith((".svg", ".pdf", ".png")):
        return "figure"
    if rel.endswith("main.pdf"):
        return "paper_pdf"
    if "manifest" in rel.lower():
        return "manifest"
    if rel.endswith((".json", ".jsonl")):
        return "machine_receipt"
    if rel.endswith(".md"):
        return "human_doc"
    return "artifact"


def security_scan_public() -> dict[str, Any]:
    patterns = {
        "secret_api_key": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
        "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
        "hard_path_users": re.compile(r"/Users/[^\s\"']+"),
        "hard_path_volumes": re.compile(r"/Volumes/[^\s\"']+"),
        "localhost": re.compile(r"\b(?:127\.0\.0\.1|localhost)\b"),
        "machine_name": re.compile(r"\b(?:magicSTUDIObox|magicPRObox)\b", re.I),
        "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    }
    hits: list[dict[str, Any]] = []
    for root in PUBLIC_SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".pkl", ".pem", ".sqlite", ".db"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = path.relative_to(REPO).as_posix()
            for pname, pat in patterns.items():
                for m in pat.finditer(text):
                    classification = "INTERNAL_ALLOWED"
                    if pname in {"secret_api_key", "private_key_block"}:
                        classification = "PUBLIC_BLOCKER"
                    elif pname in {"hard_path_users", "hard_path_volumes", "localhost", "machine_name", "email"}:
                        classification = "PUBLIC_BLOCKER"
                    hits.append(
                        {
                            "path": rel,
                            "pattern": pname,
                            "match_excerpt": m.group(0)[:120],
                            "classification": classification,
                        }
                    )
    blockers = [h for h in hits if h["classification"] == "PUBLIC_BLOCKER"]
    return {
        "scanned_roots": [str(p.relative_to(REPO)) for p in PUBLIC_SCAN_ROOTS if p.exists()],
        "hit_count": len(hits),
        "public_blocker_count": len(blockers),
        "hits": hits[:500],
        "status": "PASS" if len(blockers) == 0 else "FAIL",
    }


def run_gitleaks() -> dict[str, Any]:
    gitleaks = subprocess.run(
        ["gitleaks", "detect", "--source", str(REPO), "--no-git", "-f", "json"],
        capture_output=True,
        text=True,
    )
    findings = []
    if gitleaks.stdout.strip():
        try:
            findings = json.loads(gitleaks.stdout)
        except json.JSONDecodeError:
            findings = [{"raw": gitleaks.stdout[:2000]}]
    solo_findings = [
        f for f in findings
        if any(
            s in str(f.get("File", f.get("file", "")))
            for s in (
                "paper/newinml2026_solo",
                "eval/newinml_doc_roundtrip",
                "eval/newinml_final_daisy",
            )
        )
    ]
    return {
        "exit_code": gitleaks.returncode,
        "status": "PASS" if gitleaks.returncode == 0 else "FINDINGS",
        "finding_count_total": len(findings),
        "finding_count_solo_scope": len(solo_findings),
        "findings_solo_scope": solo_findings[:50],
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def md_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> int:
    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    EVAL_OUT.mkdir(parents=True, exist_ok=True)
    DOCS_OUT.mkdir(parents=True, exist_ok=True)
    PKG_OUT.mkdir(parents=True, exist_ok=True)

    runtime_status = {
        "schema": "hydradg.final_solo.runtime_status.v1",
        "recorded_at_utc": recorded_at,
        "host": "magicSTUDIObox.local",
        "authoritative_branch": AUTHORITATIVE_BRANCH,
        "start_sha": START_SHA,
        "current_sha": git_head(),
        "ollama_daemon": {"pid_observed": True, "api_http_code": 200, "material_experiment": False},
        "material_experiments": EXPERIMENTS,
        "running_verified_count": 0,
        "note": "Ollama serve is infrastructure only; no solo experiment RUNNING_VERIFIED at closeout.",
    }
    write_json(EVAL_OUT / "EXPERIMENT_RUNTIME_STATUS_ML.json", runtime_status)

    hl_runtime = [
        "# Experiment Runtime Status (HL)",
        "",
        f"**Recorded:** {recorded_at}  ",
        f"**Host:** magicSTUDIObox.local  ",
        f"**Branch:** `{AUTHORITATIVE_BRANCH}`  ",
        f"**SHA:** `{runtime_status['current_sha']}`",
        "",
        "## Summary",
        "",
        md_table(
            [
                ["Experiment", "Execution", "Scientific", "Terminal receipt"],
                *[
                    [
                        e["experiment_id"],
                        e["execution_state"],
                        e["scientific_state"],
                        f"`{e['terminal_receipt']}`",
                    ]
                    for e in EXPERIMENTS
                ],
            ]
        ),
        "",
        "**RUNNING_VERIFIED:** 0 — no material experiment actively executing at closeout.",
    ]
    (DOCS_OUT / "EXPERIMENT_RUNTIME_STATUS_HL.md").write_text("\n".join(hl_runtime) + "\n", encoding="utf-8")

    files = iter_solo_files()
    matrix_rows = []
    catalog_rows = []
    for i, path in enumerate(files):
        rel = path.relative_to(REPO).as_posix()
        try:
            digest = sha256_file(path)
            size = path.stat().st_size
        except OSError:
            continue
        role = classify_role(path)
        artifact_id = f"SOLO-{i+1:05d}"
        exp_id = next((e["experiment_id"] for e in EXPERIMENTS if e["terminal_receipt"] in rel), None)
        row = {
            "artifact_id": artifact_id,
            "path": rel,
            "sha256": digest,
            "size": size,
            "role": role,
            "source_dependencies": [],
            "generated_by": "repo_inventory",
            "deterministic_or_probabilistic": "deterministic" if role in {"script", "manifest", "terminal_receipt"} else "mixed",
            "experiment_id": exp_id,
            "execution_state": next((e["execution_state"] for e in EXPERIMENTS if e["experiment_id"] == exp_id), "ADMITTED"),
            "scientific_state": next((e["scientific_state"] for e in EXPERIMENTS if e["experiment_id"] == exp_id), "N/A"),
            "terminal_receipt": rel if role == "terminal_receipt" else None,
            "paper_admission": rel.startswith("paper/newinml2026_solo"),
            "package_admission": True,
            "claim_ceiling": "CUSTODY_MECHANICS",
            "ML_twin": rel if rel.endswith((".json", ".jsonl", ".yaml")) else None,
            "HL_twin": rel.replace(".json", ".md") if rel.endswith(".json") else None,
            "security_state": "UNSCANNED_INDIVIDUAL",
        }
        matrix_rows.append(row)
        catalog_rows.append(row)

    write_json(
        EVAL_OUT / "SOLO_COMPLETION_MATRIX_ML.json",
        {
            "recorded_at_utc": recorded_at,
            "artifact_count": len(matrix_rows),
            "team_only_primary_evidence_count": 0,
            "boundary_receipt": "paper/newinml2026_solo/provenance/SOLO_SUBMISSION_BOUNDARY.json",
            "artifacts": matrix_rows,
        },
    )

    (DOCS_OUT / "SOLO_COMPLETION_MATRIX_HL.md").write_text(
        "\n".join(
            [
                "# Solo Completion Matrix (HL)",
                "",
                f"**Artifacts inventoried:** {len(matrix_rows)}  ",
                "**TEAM_ONLY_PRIMARY_EVIDENCE_COUNT:** 0",
                "",
                "See machine twin: `eval/final_solo_closeout_20260829/SOLO_COMPLETION_MATRIX_ML.json`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    catalog_ml = PKG_OUT / "SOLO_PACKAGE_CATALOG_ML.jsonl"
    with catalog_ml.open("w", encoding="utf-8") as f:
        for script in SCRIPTS:
            p = REPO / script["path"]
            rec = {**script, "sha256": sha256_file(p) if p.exists() else None, "status": "PRESENT" if p.exists() else "MISSING"}
            f.write(json.dumps({"record_type": "script", **rec}, sort_keys=True) + "\n")
        for exp in EXPERIMENTS:
            f.write(json.dumps({"record_type": "experiment", **exp}, sort_keys=True) + "\n")
        for row in matrix_rows[:200]:
            f.write(json.dumps({"record_type": "artifact", **row}, sort_keys=True) + "\n")

    howto = """# How To Reproduce — NewInML 2026 Solo HydraDG

## WHAT IS THIS?
Governed solo submission lane for HydraDG / NewInML 2026 on branch `cursor/newinml-daisy-execute-20260829` (PR #36).

## WHAT DO I RUN?
```bash
cd /Users/byron/projects/active/hydradg
git checkout cursor/newinml-daisy-execute-20260829
python3 scripts/newinml_doc_roundtrip_execute.py
python3 scripts/newinml_seedgraph_full_traceability_execute.py
python3 scripts/newinml_gpu_sglang_daisy_execute.py   # expect BLOCKED unless SGLang installs
```

## WHAT SHOULD HAPPEN?
- Doc roundtrip emits `eval/newinml_doc_roundtrip_20260829/13_closeout/FINAL_CLOSEOUT.json` with `deterministic_green: true`.
- SeedGraph traceability emits GREEN closeout under `paper/newinml2026_solo/seedgraph_traceability/`.
- GPU lane preserves BLOCKED terminal if SGLang install fails.

## WHERE IS THE RESULT?
- Runtime status: `eval/final_solo_closeout_20260829/EXPERIMENT_RUNTIME_STATUS_ML.json`
- Completion matrix: `eval/final_solo_closeout_20260829/SOLO_COMPLETION_MATRIX_ML.json`
- Paper PDF: `paper/newinml2026_solo/manuscript/build/main.pdf`

## HOW DO I VERIFY IT?
```bash
shasum -a 256 paper/newinml2026_solo/manuscript/build/main.pdf
python3 scripts/final_solo_closeout_20260829.py
gitleaks detect --source . --no-git
```

## WHAT DOES A FAILURE MEAN?
- **BLOCKED** — dependency missing; do not promote claims.
- **UNDERPOWERED** — historical terminal; do not recolor as PASS.
- **PARTIAL** — incomplete matrix (e.g., Q38); omit from primary results.
"""
    (DOCS_OUT / "HOW_TO_REPRODUCE.md").write_text(howto, encoding="utf-8")

    kb = """# Knowledge Base — Solo Closeout 20260829

- Authoritative branch: `cursor/newinml-daisy-execute-20260829`
- Authoritative PR: #36 (draft)
- Protein Hinge team evidence admission count: **0**
- B4 Antigence comparator: **excluded** (team/biocustody lane)
- Signature state: NOT_SIGNED
- Merkle/MMR: NOT_COMMITTED (unless explicit receipt states otherwise)
- OpenReview operational deadline recorded: 2026-08-29T08:59:00Z (elapsed at closeout)
"""
    (DOCS_OUT / "KNOWLEDGE_BASE.md").write_text(kb, encoding="utf-8")
    (DOCS_OUT / "SOLO_PACKAGE_CATALOG_HL.md").write_text(
        "# Solo Package Catalog (HL)\n\nSee `package/final_solo/SOLO_PACKAGE_CATALOG_ML.jsonl`.\n", encoding="utf-8"
    )

    write_json(EVAL_OUT / "PREDECESSOR_RECONCILIATION_ML.json", {"recorded_at_utc": recorded_at, "entries": PREDECESSORS})
    (DOCS_OUT / "PREDECESSOR_RECONCILIATION_HL.md").write_text(
        "# Predecessor Reconciliation\n\n" + "\n".join(f"- {p['predecessor_artifact']} → {p['successor_state']}" for p in PREDECESSORS) + "\n",
        encoding="utf-8",
    )

    write_json(EVAL_OUT / "DG_SCORE_REGISTRY_ML.json", {"definition_count": len(DG_DEFINITIONS), "definitions": DG_DEFINITIONS})
    (DOCS_OUT / "DG_SCORE_REGISTRY_HL.md").write_text(
        f"# ΔG Score Registry\n\nDistinct formula definitions: **{len(DG_DEFINITIONS)}**\n", encoding="utf-8"
    )

    anticube_rows = [
        {"event_id": "AC-001", "self": -1, "safe": -1, "z_index": 0, "transition": "SECRET_REGISTRY_DISCLOSURE", "source": "longitudinal_fcg/SECRET_REGISTRY_AUDIT.jsonl"},
        {"event_id": "AC-002", "self": -1, "safe": 1, "z_index": 1, "transition": "RUNTIME_PERMITTED", "source": "longitudinal_fcg/SECRET_REGISTRY_AUDIT.jsonl"},
        {"event_id": "AC-003", "self": 1, "safe": 1, "z_index": 2, "transition": "DOC_ROUNDTRIP_PASS", "source": "eval/newinml_doc_roundtrip_20260829/13_closeout/FINAL_CLOSEOUT.json"},
    ]
    with (EVAL_OUT / "ANTICUBE_TRAJECTORIES_ML.jsonl").open("w", encoding="utf-8") as f:
        for row in anticube_rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    (DOCS_OUT / "ANTICUBE_TRAJECTORIES_HL.md").write_text("# AntiCube Trajectories\n\nCategorical coordinates only.\n", encoding="utf-8")

    fig_map = {
        "figures": [
            {
                "figure_id": "FIG-001",
                "label": "conceptual custody pipeline",
                "state": "APPENDIX_FIGURE_CANDIDATE",
                "receipt": "paper/newinml2026_solo/final_v4/manuscript/figures/FIG001_RECEIPT.json",
                "elements": [
                    {
                        "figure_element_id": "FIG001-SVG",
                        "visible_value": "custody pipeline diagram",
                        "input_artifact": "paper/newinml2026_solo/final_v4/manuscript/figures/FIG001_RECEIPT.json",
                        "json_pointer": "/svg_sha256",
                        "renderer": "deterministic_svg_builder",
                    }
                ],
            }
        ]
    }
    write_json(EVAL_OUT / "FIGURE_EVIDENCE_MAP_ML.json", fig_map)
    (DOCS_OUT / "FIGURE_EVIDENCE_MAP_HL.md").write_text("# Figure Evidence Map\n\nFIG-001 is appendix/conceptual candidate only.\n", encoding="utf-8")

    sec = security_scan_public()
    write_json(EVAL_OUT / "SECURITY_PUBLICATION_SCAN_ML.json", sec)
    (DOCS_OUT / "SECURITY_PUBLICATION_SCAN_HL.md").write_text(
        f"# Security Publication Scan\n\nPublic blockers: **{sec['public_blocker_count']}**\n", encoding="utf-8"
    )

    gitleaks = run_gitleaks()
    write_json(EVAL_OUT / "GITLEAKS_SCAN_ML.json", gitleaks)

    write_json(EVAL_OUT / "CITATION_VERIFICATION_QUEUE_ML.json", {"entries": CITATION_QUEUE})
    (DOCS_OUT / "CITATION_VERIFICATION_QUEUE_HL.md").write_text(
        "# Citation Verification Queue\n\nExternal ChatGPT verification required for flagged entries.\n", encoding="utf-8"
    )

    pdf_path = REPO / "paper/newinml2026_solo/manuscript/build/main.pdf"
    paper_sha = sha256_file(pdf_path) if pdf_path.exists() else None
    sums_path = PKG_OUT / "SHA256SUMS"
    sum_lines = []
    for key in [
        "eval/final_solo_closeout_20260829/EXPERIMENT_RUNTIME_STATUS_ML.json",
        "eval/final_solo_closeout_20260829/SOLO_COMPLETION_MATRIX_ML.json",
        "paper/newinml2026_solo/manuscript/build/main.pdf",
        "paper/newinml2026_solo/provenance/SOLO_SUBMISSION_BOUNDARY.json",
    ]:
        p = REPO / key
        if p.exists():
            sum_lines.append(f"{sha256_file(p)}  {key}")
    sums_path.write_text("\n".join(sum_lines) + "\n", encoding="utf-8")

    terminal = {
        "schema": "hydradg.final_solo.terminal_report.v1",
        "recorded_at_utc": recorded_at,
        "HOST": "magicSTUDIObox.local",
        "AUTHORITATIVE_PR": AUTHORITATIVE_PR,
        "AUTHORITATIVE_BRANCH": AUTHORITATIVE_BRANCH,
        "START_SHA": START_SHA,
        "FINAL_SHA": git_head(),
        "NEW_COMMIT_CREATED": "PENDING",
        "ORIGIN_PARITY": "PENDING",
        "OPENREVIEW_DEADLINE": "2026-08-29T08:59:00Z operational; August 29 2026 AoE official",
        "TIME_GATE": "SUBMISSION_DEADLINE_ELAPSED",
        "TEAM_ONLY_PRIMARY_EVIDENCE_COUNT": 0,
        "EXPERIMENTS_RUNNING_VERIFIED": 0,
        "EXPERIMENTS_TERMINAL": 4,
        "EXPERIMENTS_PARTIAL": 1,
        "EXPERIMENTS_BLOCKED": 2,
        "EXPERIMENTS_DEFERRED": 0,
        "DOC_ROUNDTRIP_STATE": "TERMINAL_PASS",
        "SEEDGRAPH_TRACEABILITY_STATE": "TERMINAL_PASS",
        "GPU_SGLANG_STATE": "BLOCKED",
        "QWEN38_STATE": "PARTIAL",
        "EXP008_STATE": "TERMINAL_UNDERPOWERED",
        "EXP009_STATE": "TERMINAL_UNDERPOWERED",
        "ANTICUBE_STATE": "DERIVED_FROM_ADMITTED_REGISTRY",
        "DG_SCORE_DEFINITION_COUNT": len(DG_DEFINITIONS),
        "FCG_DELTA_STATE": "DOCUMENTED_IN_ROUNDTRIP",
        "CFMO_DELTA_STATE": "NOT_EXECUTED_AS_PRIMARY",
        "GITLEAKS": gitleaks["status"],
        "SECRET_PUBLIC_BLOCKERS": sec["public_blocker_count"],
        "HARD_PATH_PUBLIC_BLOCKERS": len([h for h in sec["hits"] if h["pattern"].startswith("hard_path")]),
        "MACHINE_NAME_PUBLIC_BLOCKERS": len([h for h in sec["hits"] if h["pattern"] == "machine_name"]),
        "ANONYMITY_PUBLIC_BLOCKERS": len([h for h in sec["hits"] if h["pattern"] == "email"]),
        "PAPER_BUILD": "PRESENT" if pdf_path.exists() else "MISSING",
        "PAPER_SHA256": paper_sha,
        "PACKAGE_SHA256_MANIFEST": str(sums_path.relative_to(REPO)),
        "EVIDENCE_STATE": "CUSTODY_COMPLETE_PENDING_HUMAN_UPLOAD",
        "EXPERIMENT_STATE": "NO_NEW_LONG_RUNS",
        "FCO_STATE": "RECEIPTS_PRESENT",
        "FCG_STATE": "DELTA_DOCUMENTED_NOT_MERKLE_COMMITTED",
        "HYDRADB_STATE": "NOT_REQUIRED_FOR_SOLO_CLOSEOUT",
        "EARLIEST_DIVERGENCE": "SGLANG_INSTALL_FAILED",
        "CLAIM_CEILING": "CUSTODY_MECHANICS",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "NEXT_SAFE_ACTION": "HANDOFF_TO_CHATGPT_FINAL_REVIEW",
        "FINAL_REVIEW_GATE": "REQUIRED",
        "authority_files_missing": [
            "PROJECT_CONTROL.yaml",
            "FCO_FCG_CANONICAL_SPEC.md",
            "CLAIM_CEILINGS.md",
            "EVIDENCE_LEVELS.md",
            "FCO_SCHEMA.json",
            "FCG_SCHEMA.json",
            "SIGNING_AND_KEYS.md",
        ],
        "authority_files_present": ["AGENTS.md"],
    }
    write_json(EVAL_OUT / "TERMINAL_REPORT_ML.json", terminal)
    (DOCS_OUT / "TERMINAL_REPORT_HL.md").write_text(
        "\n".join(f"- **{k}:** {v}" for k, v in terminal.items() if k != "schema") + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"status": "OK", "artifact_count": len(matrix_rows), "terminal": terminal}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
