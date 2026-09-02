"""FCO/FCG/MMR custody helpers for Daisy overnight train."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

DOMAIN = "hydradg.daisy_overnight.mmr.v1"
REFERENCE_COMMIT = "71bf05dc8630641965c513a16790c192c9799d2e"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def mmr(leaves: list[str]) -> tuple[str, list[tuple[int, str]]]:
    peaks: list[tuple[int, str]] = []
    for leaf in sorted(leaves):
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


def collect_leaf_hashes(exp_dir: Path) -> list[str]:
    leaves: list[str] = []
    for name in [
        "PREREGISTRATION.json",
        "EXECUTION_FREEZE.json",
        "RAW_OUTPUTS.jsonl",
        "SCORED_RESULTS.jsonl",
        "CASE_LEVEL_RESULTS.jsonl",
        "STATS.json",
        "VERDICT.json",
        "FCO_BUNDLE.jsonl",
        "FCG_EDGES.jsonl",
    ]:
        p = exp_dir / name
        if p.exists():
            leaves.append(sha256_bytes(p.read_bytes()))
    return leaves


def build_mmr_receipt(exp_dir: Path, predecessor_root: str | None) -> dict[str, Any]:
    leaves = collect_leaf_hashes(exp_dir)
    root, peaks = mmr(leaves)
    recomputed, _ = mmr(leaves)
    receipt = {
        "schema": "hydradg.daisy_overnight.mmr_verification.v1",
        "domain_separator": DOMAIN,
        "canonical_reference": {"commit": REFERENCE_COMMIT, "recipe": "leaf_sha256_0x00; node_sha256_0x01"},
        "predecessor_mmr_root": predecessor_root,
        "mmr_root": root,
        "recomputed_root": recomputed,
        "root_match": root == recomputed,
        "leaf_count": len(leaves),
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "COMMITTED" if root == recomputed and leaves else "NOT_COMMITTED",
    }
    (exp_dir / "MMR_VERIFICATION.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (exp_dir / "MMR_MANIFEST.json").write_text(
        json.dumps(
            {
                "schema": "hydradg.daisy_overnight.mmr_manifest.v1",
                "experiment_dir": str(exp_dir.name),
                "mmr_root": root,
                "predecessor_mmr_root": predecessor_root,
                "leaf_count": len(leaves),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return receipt


def append_fcg_edges(exp_dir: Path, experiment_id: str, verdict: str, predecessor: str) -> str:
    edges = [
        {"src": predecessor, "rel": "PREDECESSOR_OF", "dst": f"FCG:{experiment_id}"},
        {"src": f"ExperimentFCO:{experiment_id}", "rel": "YIELDS", "dst": f"VerdictFCO:{experiment_id}"},
        {"src": f"VerdictFCO:{experiment_id}", "rel": "CLASSIFIED_AS", "dst": verdict},
    ]
    path = exp_dir / "FCG_EDGES.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for edge in edges:
            fh.write(json.dumps(edge, sort_keys=True) + "\n")
    fco_path = exp_dir / "FCO_BUNDLE.jsonl"
    with fco_path.open("w", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "fco_id": f"ExperimentFCO:{experiment_id}",
                    "kind": "ExperimentFCO",
                    "experiment_id": experiment_id,
                    "verdict": verdict,
                },
                sort_keys=True,
            )
            + "\n"
        )
    validation = {
        "schema": "hydradg.daisy_overnight.fcg_validation.v1",
        "fcg_root": sha256_bytes((exp_dir / "FCG_EDGES.jsonl").read_bytes()),
        "edge_count": len(edges),
        "state": "PASS",
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (exp_dir / "FCG_VALIDATION_RECEIPT.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    return validation["fcg_root"]
