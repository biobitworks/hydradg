#!/usr/bin/env python3
"""Build successor HydraLamp IC failure-learning FCO candidates, FCG edges and MMR receipt.

This script does NOT mutate historical submission/audit artifacts and does NOT sign anything.
MMR recipe is pinned to the canonical reference implementation:
biobitworks/fractal-custody-objects@71bf05dc8630641965c513a16790c192c9799d2e
scripts/seal_app_fcg.py

Recipe:
  leaf = sha256(0x00 || atom_bytes)
  node = sha256(0x01 || (left_hex || right_hex).encode())
  peaks bagged right-to-left with node tag 0x01

The predecessor ORIGIN_MMR_COMMITMENT.json is intentionally NOT consumed as a canonical MMR;
it declares itself a simplified linear chain for audit only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_SUBMISSION_SHA = "230bd00a6d95e57d423dd26d2be18512c2041030f1b7007bdb0374a85722611d"
REFERENCE_COMMIT = "71bf05dc8630641965c513a16790c192c9799d2e"
DOMAIN = "hydradg.ic_failure_learning.mmr.v1"
_WS = re.compile(r"\s+")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def mmr(leaves: list[str]) -> tuple[str, list[tuple[int, str]]]:
    peaks: list[tuple[int, str]] = []
    for leaf in leaves:
        node = (0, leaf)
        while peaks and peaks[-1][0] == node[0]:
            left = peaks.pop()
            node = (node[0] + 1, sha256_bytes(b"\x01" + (left[1] + node[1]).encode("ascii")))
        peaks.append(node)
    if not peaks:
        return sha256_bytes(b""), []
    acc = peaks[-1][1]
    for _, peak in reversed(peaks[:-1]):
        acc = sha256_bytes(b"\x01" + (peak + acc).encode("ascii"))
    return acc, peaks


def flatten(value: Any, prefix: str = "") -> list[str]:
    atoms: list[str] = []
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            atoms.extend(flatten(value[key], child))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            atoms.extend(flatten(item, f"{prefix}[{idx}]"))
    else:
        atoms.append(f"{prefix}\t{json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)}")
    return atoms


def text_atoms(text: str) -> list[str]:
    return [_WS.sub(" ", line).strip() for line in text.splitlines() if _WS.sub(" ", line).strip()]


def seal_atoms(atoms: list[str]) -> dict[str, Any]:
    leaves = [sha256_bytes(b"\x00" + atom.encode("utf-8")) for atom in atoms]
    root, peaks = mmr(leaves)
    return {
        "n_atoms": len(atoms),
        "fco_root": root,
        "backbones": [
            {"height": height, "atoms": 2 ** height, "peak_root": peak}
            for height, peak in peaks
        ],
    }


def read_source(repo: Path, rel: str) -> tuple[bytes, Any, str]:
    path = repo / rel
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    if path.suffix == ".json":
        return raw, json.loads(raw.decode("utf-8")), digest
    return raw, raw.decode("utf-8"), digest


def build(repo: Path) -> dict[str, Any]:
    submission_path = "eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json"
    _, submission, submission_sha = read_source(repo, submission_path)
    if submission_sha != EXPECTED_SUBMISSION_SHA:
        raise SystemExit(
            f"STOP source hash mismatch: {submission_path} {submission_sha} != {EXPECTED_SUBMISSION_SHA}"
        )

    source_paths = [
        submission_path,
        "eval/immersive_commons_submission_20260827/IC_SUBMIT_RECEIPT.json",
        "eval/ic_postmortem_20260827/ACTUAL_SUBMISSION_FREEZE.json",
        "eval/ic_postmortem_20260827/POSTMORTEM.md",
        "eval/ic_postmortem_20260827/EARLIEST_DIVERGENCE.json",
        "eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json",
        "eval/ic_postmortem_20260827/IC_TOOL_SCHEMA_SNAPSHOT.json",
        "eval/ic_postmortem_20260827/MULTIMODAL_EVIDENCE_COVERAGE.json",
        "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md",
    ]

    nodes: list[dict[str, Any]] = []
    for rel in source_paths:
        raw, value, digest = read_source(repo, rel)
        atoms = flatten(value) if rel.endswith(".json") else text_atoms(value)
        sealed = seal_atoms(atoms)
        nodes.append({
            "node_id": f"source:{rel}",
            "kind": "SOURCE_EVIDENCE_FCO_CANDIDATE",
            "source_path": rel,
            "source_sha256": digest,
            "source_bytes": len(raw),
            "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
            "claim_ceiling": "SOURCE_IDENTITY_ONLY",
            **sealed,
        })

    divergence_path = repo / "eval/ic_postmortem_20260827/EARLIEST_DIVERGENCE.json"
    divergence = json.loads(divergence_path.read_text(encoding="utf-8"))
    candidates = divergence["candidates_tested"]

    for key in sorted(candidates):
        row = {
            "candidate": key,
            "status": candidates[key]["status"],
            "evidence": candidates[key]["evidence"],
            "audit_ground_truth_role": (
                "PRIMARY" if key.startswith("C_") else
                "SECONDARY" if key.startswith("D_") else
                "TERTIARY" if key.startswith("B_") else
                "CONTRIBUTING_OR_PARTIAL"
            ),
        }
        sealed = seal_atoms(flatten(row))
        nodes.append({
            "node_id": f"failure:{key}",
            "kind": "FORENSIC_FAILURE_FCO_CANDIDATE",
            "derived_from": "eval/ic_postmortem_20260827/EARLIEST_DIVERGENCE.json",
            "evidence_class": "RECOMPUTED_RESULT",
            "claim_ceiling": "IDENTITY_AND_SUBMISSION_FORENSICS_ONLY",
            **row,
            **sealed,
        })

    protocol_gate = {
        "gate_id": "NO_SUBMISSION_WHILE_JUDGE_RELEVANT_EVIDENCE_IS_AVAILABLE_BUT_UNSURFACED",
        "prevents": "C_media_not_in_vault",
        "source": "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md",
    }
    nodes.append({
        "node_id": "control:submission_evidence_surface_gate",
        "kind": "PREVENTIVE_CONTROL_FCO_CANDIDATE",
        "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
        "claim_ceiling": "PROTOCOL_CONTROL_ONLY_NOT_EMPIRICAL_EFFECT",
        **protocol_gate,
        **seal_atoms(flatten(protocol_gate)),
    })

    edges = [
        {"edge_id": "e:submission-exhibits-vault-omission", "src": f"source:{submission_path}", "rel": "EXHIBITS", "dst": "failure:C_media_not_in_vault"},
        {"edge_id": "e:submission-exhibits-origin-ambiguity", "src": f"source:{submission_path}", "rel": "EXHIBITS", "dst": "failure:D_provenance_not_exposed"},
        {"edge_id": "e:submission-exhibits-text-form", "src": f"source:{submission_path}", "rel": "EXHIBITS", "dst": "failure:B_text_form_not_agent_native"},
        {"edge_id": "e:postmortem-derives-primary", "src": "source:eval/ic_postmortem_20260827/POSTMORTEM.md", "rel": "DERIVES", "dst": "failure:C_media_not_in_vault"},
        {"edge_id": "e:protocol-prevents-primary", "src": "control:submission_evidence_surface_gate", "rel": "PREVENTS", "dst": "failure:C_media_not_in_vault"},
        {"edge_id": "e:failure-precedes-ack", "src": "failure:C_media_not_in_vault", "rel": "PRECEDES", "dst": "source:eval/immersive_commons_submission_20260827/IC_SUBMIT_RECEIPT.json"},
    ]
    edges = sorted(edges, key=lambda e: e["edge_id"])
    edge_seal = seal_atoms([canonical_json(edge).decode("utf-8") for edge in edges])
    nodes.append({
        "node_id": "fcg:failure_learning_edges",
        "kind": "FCG_EDGE_SET_FCO_CANDIDATE",
        "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
        "claim_ceiling": "STRUCTURAL_CAUSAL_GRAPH_ONLY",
        "edge_count": len(edges),
        **edge_seal,
    })

    nodes = sorted(nodes, key=lambda n: n["node_id"])
    graph_leaves = [
        sha256_bytes(b"\x00" + f"{node['node_id']}|{node['fco_root']}".encode("utf-8"))
        for node in nodes
    ]
    graph_root, graph_peaks = mmr(graph_leaves)

    return {
        "schema": "hydradg.ic_failure_learning.fcg_manifest.v1",
        "domain_separator": DOMAIN,
        "canonical_reference": {
            "repo": "biobitworks/fractal-custody-objects",
            "commit": REFERENCE_COMMIT,
            "path": "scripts/seal_app_fcg.py",
            "recipe": "leaf_sha256_0x00; node_sha256_0x01; MMR peaks bagged right-to-left",
        },
        "base_forensic_sha": "7a737d868e3d444aa29a629219fba689425959da",
        "historical_submission_payload_sha256": submission_sha,
        "predecessor_origin_commitment_policy": "PRESERVED_UNCHANGED_LINEAR_CHAIN_AUDIT_ONLY_NOT_FULL_MMR",
        "nodes": nodes,
        "edges": edges,
        "analysis_fcg_root": graph_root,
        "analysis_backbones": [
            {"height": h, "objects": 2 ** h, "peak_root": peak} for h, peak in graph_peaks
        ],
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "COMMITTED_FAILURE_LEARNING_DOMAIN",
        "CLAIM_CEILING": "IDENTITY_AND_SUBMISSION_FORENSICS_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out-dir", default="eval/ic_failure_learning_20260827/custody")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    out = (repo / args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    manifest = build(repo)
    manifest_path = out / "FAILURE_LEARNING_FCG_MMR_MANIFEST.json"
    manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    manifest_path.write_bytes(manifest_bytes)

    recomputed = build(repo)
    verified = recomputed["analysis_fcg_root"] == manifest["analysis_fcg_root"]
    receipt = {
        "schema": "hydradg.ic_failure_learning.mmr_verification.v1",
        "manifest_path": str(manifest_path.relative_to(repo)),
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "analysis_fcg_root": manifest["analysis_fcg_root"],
        "recomputed_root": recomputed["analysis_fcg_root"],
        "root_match": verified,
        "leaf_order": [n["node_id"] for n in manifest["nodes"]],
        "algorithm": manifest["canonical_reference"]["recipe"],
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "COMMITTED_FAILURE_LEARNING_DOMAIN" if verified else "NOT_COMMITTED_VERIFICATION_FAILED",
    }
    receipt_path = out / "FAILURE_LEARNING_MMR_VERIFICATION_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "manifest": str(manifest_path),
        "root": manifest["analysis_fcg_root"],
        "nodes": manifest["n_nodes"],
        "edges": manifest["n_edges"],
        "verified": verified,
    }, indent=2))
    return 0 if verified else 2


if __name__ == "__main__":
    raise SystemExit(main())
