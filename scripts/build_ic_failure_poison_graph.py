#!/usr/bin/env python3
"""Build README poison FCO, antidote FCO, and failure propagation graph."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

FORENSIC_BASE_SHA = "7a737d868e3d444aa29a629219fba689425959da"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def readme_bytes(repo: Path) -> bytes:
    path = repo / "eval/ic_failure_learning_20260827/source_freeze/README_AT_SUBMISSION_SHA.md"
    if path.exists():
        return path.read_bytes()
    return subprocess.check_output(
        ["git", "show", f"{FORENSIC_BASE_SHA}:README.md"],
        cwd=repo,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out_dir = repo / "eval/ic_failure_learning_20260827"
    out_dir.mkdir(parents=True, exist_ok=True)

    readme_raw = readme_bytes(repo)
    readme_sha = sha256_bytes(readme_raw)
    submitted = json.loads(
        (repo / "eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json").read_text()
    )

    poison = {
        "schema": "hydradg.ic_failure_learning.readme_poison_fco.v1",
        "fco_id": "README_POISON_FCO",
        "source_path": "README.md",
        "source_commit": FORENSIC_BASE_SHA,
        "source_sha256": readme_sha,
        "submitted_repo_url": submitted["repo_url"],
        "presents_project_as": "HydraDG / Hack Hydra Track 03",
        "conflicts_with": "HydraLamp Immersive Commons Aug 26-27 delta",
        "anticube_classification": "SELF_NON_SAFE",
        "first_divergence_hypothesis": "H_README_POISON",
        "null_hypothesis": "H0_README",
        "propagation_candidates": [
            "OriginClassificationDecision",
            "LandsInProductRubricDimension",
            "ModelJudgeOriginAmbiguity",
        ],
        "downstream_dependent_count": 4,
        "POISON_RETAINED": True,
        "claim_ceiling": "INFERENCE_HYPOTHESIS",
    }
    poison_path = out_dir / "README_POISON_FCO.json"
    poison_path.write_text(json.dumps(poison, indent=2) + "\n", encoding="utf-8")

    antidote_readme = (
        "# HydraLamp — Immersive Commons Aug 26–27 Agent-Native Delta\n\n"
        "> **Judge start here:** This repository contains pre-existing HydraDG substrate "
        "(commits before 2026-08-26) plus the HydraLamp hackathon delta on branch "
        "`hack-hydra/hydralamp-20260826`.\n\n"
        "- **Substrate baseline:** `e4558026` (2026-08-18)\n"
        "- **HydraLamp delta:** `757f3fa7` (2026-08-26)\n"
        "- **Vault:** see `00_START_HERE.md` in IC folder\n"
        "- **Agent surface:** `/.well-known/ai-agent.json` + `/api/hydralamp/run`\n"
    )
    antidote = {
        "schema": "hydradg.ic_failure_learning.readme_antidote_fco.v1",
        "fco_id": "SUCCESSOR_README_ANTIDOTE",
        "supersedes": "README_POISON_FCO",
        "content_sha256": sha256_bytes(antidote_readme.encode("utf-8")),
        "content_preview": antidote_readme[:500],
        "repairs": [
            "project_identity",
            "origin_date",
            "substrate_vs_hackathon_delta",
            "branch_sha",
            "judge_start_path",
            "agent_discovery",
            "vault_evidence_path",
        ],
        "anticube_classification": "SELF_SAFE",
        "POISON_RETAINED": True,
        "basis": "Successor antidote supersedes poison for future judge entry without erasing historical README",
        "claim_ceiling": "PROTOCOL_CONTROL_ONLY_NOT_EMPIRICAL_EFFECT",
    }
    antidote_path = out_dir / "README_ANTIDOTE_FCO.json"
    antidote_path.write_text(json.dumps(antidote, indent=2) + "\n", encoding="utf-8")

    fixture_path = out_dir / "fixtures" / "README_ANTIDOTE.md"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(antidote_readme, encoding="utf-8")

    graph = {
        "schema": "hydradg.ic_failure_learning.failure_propagation_graph.v1",
        "nodes": [
            {"id": "SubmittedRepoURLFCO", "kind": "SubmissionFieldFCO", "value": submitted["repo_url"]},
            {"id": "RepositoryRootFCO", "kind": "ArtifactFCO"},
            {"id": "READMEFCO", "kind": "ArtifactFCO", "sha256": readme_sha},
            {"id": "HydraDGHackHydraIdentityFCO", "kind": "DecisionFCO"},
            {"id": "HydraLampICDeltaFCO", "kind": "ArtifactFCO"},
            {"id": "OriginClassificationDecision", "kind": "DecisionFCO"},
            {"id": "LandsInProductRubricDimension", "kind": "RuleFCO", "rule_id": "R_LANDS_IN_PRODUCT"},
            {"id": "MISSING_VAULT_FCO", "kind": "FailureFCO", "candidate": "C_media_not_in_vault"},
            {"id": "EVIDENCE_DELIVERY_RULE", "kind": "RuleFCO", "rule_id": "R_VAULT_FOLDER"},
            {"id": "DEMO_EVIDENCE_GAP", "kind": "FailureFCO"},
            {"id": "SUCCESSOR_README_ANTIDOTE", "kind": "RepairFCO"},
            {"id": "E07_EXPERIMENT", "kind": "ExperimentFCO"},
        ],
        "edges": [
            {"src": "SubmittedRepoURLFCO", "rel": "RESOLVES_TO", "dst": "RepositoryRootFCO"},
            {"src": "RepositoryRootFCO", "rel": "DEFAULT_ENTRY", "dst": "READMEFCO"},
            {"src": "READMEFCO", "rel": "PRESENTS_PROJECT_AS", "dst": "HydraDGHackHydraIdentityFCO"},
            {"src": "HydraDGHackHydraIdentityFCO", "rel": "CONFLICTS_WITH", "dst": "HydraLampICDeltaFCO"},
            {"src": "READMEFCO", "rel": "PROPAGATED_TO", "dst": "OriginClassificationDecision"},
            {"src": "OriginClassificationDecision", "rel": "AFFECTED", "dst": "LandsInProductRubricDimension"},
            {"src": "MISSING_VAULT_FCO", "rel": "VIOLATES", "dst": "EVIDENCE_DELIVERY_RULE"},
            {"src": "MISSING_VAULT_FCO", "rel": "PROPAGATED_TO", "dst": "DEMO_EVIDENCE_GAP"},
            {"src": "SUCCESSOR_README_ANTIDOTE", "rel": "REPAIRED_BY", "dst": "READMEFCO"},
            {"src": "E07_EXPERIMENT", "rel": "TESTED_BY", "dst": "SUCCESSOR_README_ANTIDOTE"},
        ],
        "eval_only_causal_ranking": {"primary": "C", "secondary": "D", "tertiary": "B"},
        "README_POISON_DOWNSTREAM_COUNT": 4,
        "claim_ceiling": "STRUCTURAL_CAUSAL_GRAPH_ONLY",
    }
    graph_path = out_dir / "FAILURE_PROPAGATION_GRAPH.json"
    graph_path.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")

    # Link to custody FCG if present
    custody_manifest = out_dir / "custody" / "FAILURE_LEARNING_FCG_MMR_MANIFEST.json"
    if custody_manifest.exists():
        graph["custody_fcg_root"] = json.loads(custody_manifest.read_text()).get("analysis_fcg_root")

    fcg_out = out_dir / "FAILURE_LEARNING_FCG.json"
    if custody_manifest.exists():
        fcg_out.write_bytes(custody_manifest.read_bytes())
    else:
        fcg_out.write_text(json.dumps({"status": "PENDING_FCG_BUILD"}, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "poison": str(poison_path),
        "antidote": str(antidote_path),
        "graph": str(graph_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
