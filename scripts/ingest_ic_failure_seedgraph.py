#!/usr/bin/env python3
"""Attempt governed SeedGraph import for IC failure-learning rule sources."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SEEDGRAPH_ROOT_DEFAULT = Path("/Users/byron/projects/active/seedgraph")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def try_seedgraph_import(seedgraph_root: Path, descriptor: Path, operator: str, receipt_path: Path) -> dict[str, Any]:
    cmd = [
        "uv", "run", "seedgraph", "import", str(descriptor),
        "--type", "requirement",
        "--json",
        "--no-require-publication-reingest-gate",
        "--publication-reingest-not-applicable",
        "IC failure-learning rule corpus; not a publication-family reingest",
        "--publication-reingest-operator", operator,
        "--publication-reingest-receipt", str(receipt_path),
    ]
    proc = subprocess.run(cmd, cwd=seedgraph_root, capture_output=True, text=True)
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def atomize_rules(repo: Path) -> list[dict[str, Any]]:
    corpus_path = repo / "eval/ic_failure_learning_20260827/RULE_CORPUS_MANIFEST.json"
    if not corpus_path.exists():
        raise SystemExit("STOP: RULE_CORPUS_MANIFEST.json missing; run build_ic_failure_rule_corpus.py first")
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    atoms: list[dict[str, Any]] = []
    for rule in corpus["rule_atoms"]:
        body = canonical_json(rule)
        atoms.append({
            "atom_id": f"rule:{rule['rule_id']}",
            "kind": "RULE",
            "parent": "ImmersiveCommonsEventFCO",
            "source_locator": rule["exact_locator"],
            "source_sha256": rule["source_sha256"],
            "atom_sha256": sha256_bytes(body.encode("utf-8")),
            "payload": rule,
        })
    return atoms


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--seedgraph-root", default=str(SEEDGRAPH_ROOT_DEFAULT))
    ap.add_argument("--operator", default="ic-failure-learning-daisy")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    seedgraph_root = Path(args.seedgraph_root).resolve()
    out_dir = repo / "eval/ic_failure_learning_20260827"
    out_dir.mkdir(parents=True, exist_ok=True)

    atoms = atomize_rules(repo)
    atom_receipt = {
        "schema": "hydradg.ic_failure_learning.seedgraph_atomization.v1",
        "rule_atoms": len(atoms),
        "atoms": atoms,
        "orphan_atoms": [],
        "failed_atoms": [],
        "abstentions": [],
        "RULE_ATOMIZATION_COVERAGE": "COMPLETE" if atoms else "EMPTY",
        "CLAIM_CEILING": "RULE_ATOMIZATION_RECEIPT_ONLY",
    }
    atom_path = out_dir / "SEEDGRAPH_ATOMIZATION_RECEIPT.json"
    atom_path.write_text(json.dumps(atom_receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    descriptor = {
        "schema": "hydradg.ic_failure_learning.seedgraph_descriptor.v1",
        "family": "ic_failure_learning_rules",
        "source_repo": "biobitworks/hydradg",
        "atomization_receipt_sha256": sha256_bytes(atom_path.read_bytes()),
        "rule_atom_count": len(atoms),
        "claim_ceiling": "RULE_CUSTODY_DESCRIPTOR_ONLY",
    }
    desc_path = out_dir / "seedgraph" / "ic_failure_rules_descriptor.json"
    desc_path.parent.mkdir(parents=True, exist_ok=True)
    desc_path.write_text(json.dumps(descriptor, indent=2) + "\n", encoding="utf-8")

    import_receipt_path = out_dir / "seedgraph" / "PUBLICATION_REINGEST_BYPASS_RECEIPT.json"
    import_receipt_path.write_text(
        json.dumps({"status": "not_applicable", "reason": "ic_failure_learning_rules"}, indent=2) + "\n",
        encoding="utf-8",
    )

    import_state = "BLOCKED_SEEDGRAPH_NOT_INITIALIZED"
    import_result: dict[str, Any] = {}
    if seedgraph_root.exists():
        result = try_seedgraph_import(seedgraph_root, desc_path, args.operator, import_receipt_path)
        import_result = result
        if result["returncode"] == 0:
            import_state = "PASS"
        else:
            import_state = "BLOCKED_SEEDGRAPH_IMPORT_FAILED"

    receipt = {
        "schema": "hydradg.ic_failure_learning.seedgraph_import.v1",
        "seedgraph_root": str(seedgraph_root),
        "descriptor_path": str(desc_path.relative_to(repo)),
        "descriptor_sha256": sha256_bytes(desc_path.read_bytes()),
        "atomization_receipt_path": str(atom_path.relative_to(repo)),
        "import_state": import_state,
        "import_attempt": import_result,
        "RULE_SOURCE_BYTES": atom_receipt.get("RULE_SOURCE_BYTES", {}),
        "RULE_ATOMS": len(atoms),
        "RULE_ATOMIZATION_COVERAGE": atom_receipt["RULE_ATOMIZATION_COVERAGE"],
        "ORPHAN_ATOMS": [],
        "FAILED_ATOMS": [] if import_state == "PASS" else [{"reason": import_state}],
        "ABSTENTIONS": [],
        "CLAIM_CEILING": "SEEDGRAPH_IMPORT_RECEIPT_ONLY",
    }
    receipt_path = out_dir / "SEEDGRAPH_IMPORT_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"import_state": import_state, "rule_atoms": len(atoms)}, indent=2))
    return 0 if import_state == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
