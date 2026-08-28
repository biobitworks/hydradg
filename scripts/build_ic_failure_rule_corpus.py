#!/usr/bin/env python3
"""Build normalized IC rule/criterion objects from frozen rubric and protocol sources."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

RUBRIC_DIM_MAP = {
    "cold_start_success": "R_TRACK01_COLD_START",
    "it_runs": "R_IT_RUNS",
    "surface_quality": "R_SURFACE_QUALITY",
    "lands_in_product": "R_LANDS_IN_PRODUCT",
    "demo": "R_DEMO",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(repo: Path, rel: str) -> tuple[Any, str, bytes]:
    raw = (repo / rel).read_bytes()
    return json.loads(raw.decode("utf-8")), sha256_bytes(raw), raw


def rule_atom(
    rule_id: str,
    source: str,
    source_sha256: str,
    locator: str,
    fragment: str,
    meaning: str,
    requirement_type: str,
    rubric_dimension: str | None,
    hard_gate: bool | None,
    max_points: int | None,
    required_evidence: list[str],
    judge_visible_location: str,
    claim_ceiling: str,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "source": source,
        "source_sha256": source_sha256,
        "exact_locator": locator,
        "verbatim_fragment": fragment,
        "normalized_meaning": meaning,
        "requirement_type": requirement_type,
        "rubric_dimension": rubric_dimension,
        "hard_gate": hard_gate,
        "max_points": max_points,
        "required_evidence": required_evidence,
        "judge_visible_location": judge_visible_location,
        "claim_ceiling": claim_ceiling,
    }


def build_rules(repo: Path) -> dict[str, Any]:
    rubric_path = "eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json"
    schema_path = "eval/ic_postmortem_20260827/IC_TOOL_SCHEMA_SNAPSHOT.json"
    protocol_path = "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md"

    rubric, rubric_sha, _ = load_json(repo, rubric_path)
    schema, schema_sha, _ = load_json(repo, schema_path)
    protocol_raw = (repo / protocol_path).read_bytes()
    protocol_sha = sha256_bytes(protocol_raw)
    protocol_text = protocol_raw.decode("utf-8")

    atoms: list[dict[str, Any]] = []

    atoms.append(rule_atom(
        "R_EVENT_IMMERSIVE_COMMONS",
        rubric_path, rubric_sha,
        "event.eid",
        rubric["event"]["event"]["eid"],
        "Submission targets Immersive Commons Agent Natives hackathon event",
        "EVENT", None, None, None,
        ["ic_hack_get response"],
        "event context",
        "SOURCE_IDENTITY_ONLY",
    ))

    track = rubric["official_rubric"]["tracks"]["track01_external"]
    for key, spec in track["criteria"].items():
        rule_id = RUBRIC_DIM_MAP.get(key, f"R_{key.upper()}")
        atoms.append(rule_atom(
            rule_id,
            rubric_path, rubric_sha,
            f"official_rubric.tracks.track01_external.criteria.{key}",
            json.dumps(spec, ensure_ascii=False),
            track["question"] if key == "cold_start_success" else f"Track01 criterion {key}",
            "RUBRIC_DIMENSION", key,
            spec.get("gate"), spec.get("max"),
            ["agent_surface", "live demo", "repo", "vault"] if key == "cold_start_success" else ["repo", "vault", "demo"],
            "rubric dimension + judge-visible artifacts",
            "SOURCE_IDENTITY_ONLY",
        ))

    submit_fields = schema.get("submit_schema", schema.get("tools", {}))
    field_defs = submit_fields if isinstance(submit_fields, dict) else {}
    for field in ["title", "blurb", "repo_url", "demo_url", "agent_surface", "folder_id"]:
        atoms.append(rule_atom(
            f"R_SUBMIT_FIELD_{field.upper()}",
            schema_path, schema_sha,
            f"submit.{field}",
            field,
            f"IC submission requires field {field}",
            "REQUIRED_FIELD", None, field == "folder_id", None,
            ["ic_hack_submit"],
            "submission payload",
            "SOURCE_IDENTITY_ONLY",
        ))

    atoms.append(rule_atom(
        "R_VAULT_FOLDER",
        schema_path, schema_sha,
        "submit.folder_id",
        "folder_id",
        "folder_id represents populated IC vault with judge-visible evidence",
        "ARTIFACT_REQUIREMENT", "demo", True, None,
        ["ic_folder_create", "ic_files_put"],
        "vault / folder_id",
        "SOURCE_IDENTITY_ONLY",
    ))

    atoms.append(rule_atom(
        "R_AGENT_SURFACE_30PT",
        rubric_path, rubric_sha,
        "official_rubric.tracks.track01_external.criteria.cold_start_success",
        "scores_via: agent_surface + live demo",
        "agent_surface is the scored cold-start discovery surface (30pt dimension)",
        "CRITERION", "cold_start_success", False, 30,
        ["agent_surface field", "live API"],
        "agent_surface + demo",
        "SOURCE_IDENTITY_ONLY",
    ))

    if "VAULT_BUNDLE" in protocol_text:
        vault_section = protocol_text[protocol_text.index("VAULT_BUNDLE"):protocol_text.index("VAULT_BUNDLE") + 400]
        atoms.append(rule_atom(
            "R_NO_SUBMIT_BEFORE_VAULT",
            protocol_path, protocol_sha,
            "VAULT_BUNDLE",
            _WS.sub(" ", vault_section.split("\n")[0]),
            "Vault must be populated before submission; folder_id must not be null at submit",
            "HARD_GATE", "it_runs", True, None,
            ["ic_folder_create", "ic_files_put", "folder_id"],
            "vault before ic_hack_submit",
            "PROTOCOL_CONTROL_ONLY",
        ))

    atoms.append(rule_atom(
        "R_NO_UNSURFACED_JUDGE_EVIDENCE",
        protocol_path, protocol_sha,
        "successor protocol",
        "Do not submit while required judge evidence remains unsurfaced",
        "Judge-relevant evidence must be in vault or submission fields before submit",
        "EVIDENCE_REQUIREMENT", "demo", True, None,
        ["vault manifest", "media", "origin doc"],
        "vault + submission fields",
        "PROTOCOL_CONTROL_ONLY",
    ))

    atoms.append(rule_atom(
        "R_ORIGIN_LEGIBILITY",
        protocol_path, protocol_sha,
        "ORIGIN_PROVENANCE",
        "Origin doc: substrate vs new work with commit SHAs",
        "Judge must be able to distinguish hackathon delta from pre-existing substrate",
        "CRITERION", "lands_in_product", False, 15,
        ["origin comparison", "branch-qualified repo", "what is new doc"],
        "blurb + vault + repo entry",
        "SOURCE_IDENTITY_ONLY",
    ))

  # README identity conflict rule (derived, not pre-seeded as ground truth)
    atoms.append(rule_atom(
        "R_README_PROJECT_IDENTITY",
        "eval/ic_failure_learning_20260827/source_freeze/README_AT_SUBMISSION_SHA.md",
        sha256_bytes((repo / "eval/ic_failure_learning_20260827/source_freeze/README_AT_SUBMISSION_SHA.md").read_bytes())
        if (repo / "eval/ic_failure_learning_20260827/source_freeze/README_AT_SUBMISSION_SHA.md").exists()
        else "PENDING_SOURCE_FREEZE",
        "README.md:1",
        "HydraDG — Graph-Native Governed Context Engine / Hack Hydra 2026 — Track 03",
        "Repository root README presents HydraDG/Hack Hydra identity, not HydraLamp IC delta",
        "ARTIFACT_REQUIREMENT", "lands_in_product", False, 15,
        ["README", "repo_url root"],
        "repo_url default entry",
        "INFERENCE_HYPOTHESIS",
    ))

    return {
        "schema": "hydradg.ic_failure_learning.rule_corpus.v1",
        "rule_atoms": atoms,
        "rule_atom_count": len(atoms),
        "rule_source_bytes": {
            rubric_path: rubric_sha,
            schema_path: schema_sha,
            protocol_path: protocol_sha,
        },
        "contradiction_edges": [],
        "orphan_atoms": [],
        "failed_atoms": [],
        "abstentions": [],
        "CLAIM_CEILING": "RULE_CORPUS_FIXTURE_ONLY",
    }


_WS = re.compile(r"\s+")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/RULE_CORPUS_MANIFEST.json")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    corpus = build_rules(repo)
    out = (repo / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"rule_atoms": corpus["rule_atom_count"], "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
