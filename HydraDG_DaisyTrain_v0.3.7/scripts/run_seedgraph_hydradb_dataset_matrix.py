#!/usr/bin/env python3
"""Run the raw-vs-governed dataset custody matrix for Hack Hydra.

This script compares two representations of the SAME downloaded dataset identities:

A. RAW_HYDRADB
   upstream repo/revision -> local SHA256 manifest -> minimal HydraDB baseline

B. SEEDGRAPH_FCO_FCG_HYDRADB
   upstream repo/revision -> local SHA256 manifest -> SeedGraph governed intake
   -> application-level FCO/FCG custody route -> HydraDB projection

The comparison is custody/provenance only. It does NOT claim better benchmark,
retrieval, QA, ontology, or scientific performance.

SeedGraph mutation boundary:
- invokes only the documented `seedgraph import` CLI surface;
- never reads SeedGraph Neo4j/SQLite/content-store internals directly;
- requires an explicit --operator value;
- records a publication-reingest not-applicable receipt because benchmark
  dataset descriptors are not publication-family reingests.

Large/raw dataset files are NOT copied into SeedGraph by this generic matrix.
Instead, one deterministic descriptor per dataset commits the exact downloaded
SHA256SUMS manifest. Dataset-specific semantic adapters remain separate work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

CLAIM_CEILING = "DATASET_CUSTODY_AND_PROVENANCE_COMPARISON_ONLY_NOT_BENCHMARK_PERFORMANCE"
DESCRIPTOR_CEILING = "DATASET_CUSTODY_DESCRIPTOR_ONLY_NOT_FULL_SEMANTIC_INGEST"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def make_fco(kind: str, payload: dict) -> dict:
    body = {"type": kind, "payload": payload}
    digest = sha256_bytes(canonical_json(body).encode("utf-8"))
    return {
        "id": f"fco:{digest}",
        "object_sha256": digest,
        "type": kind,
        "payload": payload,
    }


def hydra_numeric_id(stable_id: str) -> int:
    match = re.fullmatch(r"fco:([0-9a-f]{64})", stable_id)
    digest = match.group(1) if match else sha256_bytes(stable_id.encode())
    value = int(digest[:13], 16)  # 52 bits; exactly representable in JS too
    return value or 1


def raw_numeric_id(kind: str, *parts: object) -> int:
    digest = sha256_bytes((kind + "|" + "|".join(map(str, parts))).encode())
    return int(digest[:13], 16) or 1


class HydraHTTP:
    def __init__(self, endpoint: str, token: str, namespace: str = "default", cell_id: str = "cell-0"):
        self.endpoint = endpoint
        self.token = token
        self.namespace = namespace
        self.cell_id = cell_id

    def query(self, query: str, parameters: dict | None = None) -> dict:
        body = json.dumps({
            "cell_id": self.cell_id,
            "query": query,
            "parameters": parameters or {},
        }).encode()
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.token}",
                "X-Graph-Namespace": self.namespace,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"HydraDB HTTP {exc.code}: {detail[:1600]} query={query[:500]}") from exc

    @staticmethod
    def projected(resp: dict, col: str) -> list[object]:
        columns = resp.get("columns", [])
        if col not in columns:
            return []
        idx = columns.index(col)
        out = []
        for row in resp.get("rows", []):
            if idx >= len(row):
                continue
            value = row[idx]
            out.append(value.get("value") if isinstance(value, dict) and "value" in value else value)
        return out


def parse_sha_manifest(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.rstrip("\n")
        if not line:
            continue
        match = re.match(r"^([0-9a-f]{64})\s\s(.+)$", line)
        if not match:
            raise ValueError(f"invalid SHA256SUMS row in {path}: {line[:200]!r}")
        rows.append({"sha256": match.group(1), "relative_path": match.group(2)})
    return rows


def git_value(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
    except Exception:
        return "UNRESOLVED"


def extract_json_array(text: str) -> list[dict]:
    text = text.strip()
    try:
        value = json.loads(text)
        if isinstance(value, list):
            return value
    except json.JSONDecodeError:
        pass
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        value = json.loads(text[start : end + 1])
        if isinstance(value, list):
            return value
    raise ValueError(f"SeedGraph --json output was not a JSON array: {text[:1000]}")


def seedgraph_import_descriptor(seedgraph_root: Path, descriptor: Path, operator: str, receipt_path: Path) -> dict:
    cmd = [
        "uv", "run", "seedgraph", "import", str(descriptor),
        "--type", "evidence",
        "--json",
        "--no-require-publication-reingest-gate",
        "--publication-reingest-not-applicable",
        "Hack Hydra benchmark dataset custody descriptor; not a publication-family reingest",
        "--publication-reingest-operator", operator,
        "--publication-reingest-receipt", str(receipt_path),
    ]
    proc = subprocess.run(
        cmd,
        cwd=seedgraph_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "SeedGraph import failed. The script does not auto-run `seedgraph init` "
            "because that may create cryptographic key material. Review SeedGraph configuration first.\n"
            f"command={' '.join(cmd)}\nstdout={proc.stdout[-3000:]}\nstderr={proc.stderr[-3000:]}"
        )
    rows = extract_json_array(proc.stdout)
    if len(rows) != 1:
        raise RuntimeError(f"expected one SeedGraph import result for {descriptor}, got {len(rows)}")
    result = rows[0]
    if result.get("status") not in {"created", "duplicate"}:
        raise RuntimeError(f"SeedGraph import not admitted: {result}")
    return result


def merge_raw_baseline(hydra: HydraHTTP, dataset: dict, descriptor_sha: str) -> dict:
    repo = dataset["repo_id"]
    revision = dataset["revision"]
    manifest_sha = dataset["sha256_manifest_sha256"]
    dataset_id = raw_numeric_id("raw_dataset", repo, revision)
    manifest_id = raw_numeric_id("raw_manifest", repo, revision, manifest_sha)
    hydra.query(
        "MERGE (n {id: $id}) SET n:RawDataset, n.repo_id=$repo_id, n.revision=$revision, "
        "n.license_declared_upstream=$license, n.lane='RAW_HYDRADB', n.claim_ceiling=$claim_ceiling",
        {
            "id": dataset_id,
            "repo_id": repo,
            "revision": revision,
            "license": dataset["license_declared_upstream"],
            "claim_ceiling": CLAIM_CEILING,
        },
    )
    hydra.query(
        "MERGE (n {id: $id}) SET n:RawManifest, n.repo_id=$repo_id, n.revision=$revision, "
        "n.sha256_manifest_sha256=$manifest_sha, n.descriptor_sha256=$descriptor_sha, "
        "n.lane='RAW_HYDRADB', n.claim_ceiling=$claim_ceiling",
        {
            "id": manifest_id,
            "repo_id": repo,
            "revision": revision,
            "manifest_sha": manifest_sha,
            "descriptor_sha": descriptor_sha,
            "claim_ceiling": CLAIM_CEILING,
        },
    )
    hydra.query(
        "MATCH (a {id:$src}), (b {id:$dst}) MERGE (a)-[:HAS_MANIFEST]->(b)",
        {"src": dataset_id, "dst": manifest_id},
    )
    return {"dataset_vertex": dataset_id, "manifest_vertex": manifest_id, "route_edges": 1}


def merge_fco_node(hydra: HydraHTTP, node: dict, dataset_id: str) -> int:
    vertex = hydra_numeric_id(node["id"])
    hydra.query(
        "MERGE (n {id:$id}) SET n:DatasetCustodyFCO, n.fco_id=$fco_id, n.object_sha256=$object_sha256, "
        "n.fco_type=$fco_type, n.dataset_id=$dataset_id, n.lane='SEEDGRAPH_FCO_FCG_HYDRADB', "
        "n.claim_ceiling=$claim_ceiling",
        {
            "id": vertex,
            "fco_id": node["id"],
            "object_sha256": node["object_sha256"],
            "fco_type": node["type"],
            "dataset_id": dataset_id,
            "claim_ceiling": CLAIM_CEILING,
        },
    )
    return vertex


def link(hydra: HydraHTTP, src: int, rel: str, dst: int) -> None:
    if not re.fullmatch(r"[A-Z_]+", rel):
        raise ValueError(rel)
    hydra.query(
        f"MATCH (a {{id:$src}}), (b {{id:$dst}}) MERGE (a)-[:{rel}]->(b)",
        {"src": src, "dst": dst},
    )


def build_governed_route(hydra: HydraHTTP, dataset: dict, descriptor: dict, descriptor_sha: str, sg: dict, seedgraph_commit: str) -> dict:
    repo = dataset["repo_id"]
    dataset_key = repo.replace("/", "__")
    source = make_fco("UpstreamDataset", {
        "repo_id": repo,
        "revision": dataset["revision"],
        "license_declared_upstream": dataset["license_declared_upstream"],
        "source_manifest_sha256": dataset["sha256_manifest_sha256"],
        "claim_ceiling": CLAIM_CEILING,
    })
    snapshot = make_fco("LocalDatasetSnapshot", {
        "repo_id": repo,
        "local_path": dataset["local_path"],
        "source_manifest_sha256": dataset["sha256_manifest_sha256"],
        "descriptor_sha256": descriptor_sha,
        "declared_file_count": len(descriptor["files"]),
        "claim_ceiling": CLAIM_CEILING,
    })
    intake = make_fco("SeedGraphIntake", {
        "repo_id": repo,
        "seedgraph_commit": seedgraph_commit,
        "seed_id": sg.get("seed_id"),
        "seedgraph_entry_hash": sg.get("entry_hash"),
        "seedgraph_source_sha256": sg.get("source_sha256"),
        "seedgraph_proof_state": sg.get("proof_state"),
        "descriptor_sha256": descriptor_sha,
        "source_semantics": "DATASET_CUSTODY_DESCRIPTOR_NOT_FULL_RAW_SEMANTIC_INGEST",
        "claim_ceiling": DESCRIPTOR_CEILING,
    })
    projection = make_fco("HydraDBDatasetProjection", {
        "repo_id": repo,
        "namespace": hydra.namespace,
        "cell_id": hydra.cell_id,
        "source_fco": source["id"],
        "snapshot_fco": snapshot["id"],
        "seedgraph_intake_fco": intake["id"],
        "claim_ceiling": CLAIM_CEILING,
    })
    nodes = [source, snapshot, intake, projection]
    vertices = {node["id"]: merge_fco_node(hydra, node, dataset_key) for node in nodes}
    edges = [
        (snapshot["id"], "DERIVED_FROM", source["id"]),
        (intake["id"], "DERIVED_FROM", snapshot["id"]),
        (projection["id"], "DERIVED_FROM", intake["id"]),
    ]
    for src, rel, dst in edges:
        link(hydra, vertices[src], rel, vertices[dst])

    response = hydra.query(
        "MATCH (p {id:$p})-[:DERIVED_FROM]->(i)-[:DERIVED_FROM]->(s)-[:DERIVED_FROM]->(u) "
        "RETURN count(u) AS route_count",
        {"p": vertices[projection["id"]]},
    )
    vals = HydraHTTP.projected(response, "route_count")
    route_count = int(vals[0]) if vals else 0
    return {
        "nodes": nodes,
        "edges": [{"src": src, "rel": rel, "dst": dst} for src, rel, dst in edges],
        "projection_vertex": vertices[projection["id"]],
        "complete_route": route_count > 0,
        "route_edges": 3,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-receipt", required=True, type=Path)
    parser.add_argument("--seedgraph-root", type=Path, default=Path("/Users/byron/projects/active/seedgraph"))
    parser.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    parser.add_argument("--token-file", type=Path, default=Path("~/.local/share/hydradg-best-use/hydradb-auth-token").expanduser())
    parser.add_argument("--namespace", default="default")
    parser.add_argument("--operator", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    receipt_path = args.dataset_receipt.expanduser().resolve()
    seedgraph_root = args.seedgraph_root.expanduser().resolve()
    token_file = args.token_file.expanduser().resolve()
    out = args.out.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    descriptor_dir = out.parent / "seedgraph_dataset_descriptors"
    descriptor_dir.mkdir(parents=True, exist_ok=True)
    bypass_dir = out.parent / "seedgraph_reingest_not_applicable_receipts"
    bypass_dir.mkdir(parents=True, exist_ok=True)

    if not receipt_path.is_file():
        raise SystemExit(f"dataset receipt not found: {receipt_path}")
    if not (seedgraph_root / "pyproject.toml").is_file():
        raise SystemExit(f"SeedGraph repo not found: {seedgraph_root}")
    if not token_file.is_file():
        raise SystemExit(f"HydraDB token file not found: {token_file}")
    if not shutil_which("uv"):
        raise SystemExit("uv is required to invoke the governed SeedGraph CLI")

    pull = json.loads(receipt_path.read_text())
    datasets = pull.get("datasets", [])
    if not datasets:
        raise SystemExit("dataset pull receipt has no datasets")

    seedgraph_commit = git_value(seedgraph_root, "rev-parse", "HEAD")
    seedgraph_status = git_value(seedgraph_root, "status", "--porcelain")
    hydra = HydraHTTP(args.endpoint, token_file.read_text().strip(), namespace=args.namespace)

    results: list[dict] = []
    for dataset in datasets:
        local_path = Path(dataset["local_path"]).expanduser().resolve()
        manifest_path = Path(dataset["sha256_manifest"]).expanduser().resolve()
        manifest_sha = sha256_file(manifest_path)
        expected_manifest_sha = dataset["sha256_manifest_sha256"]
        if manifest_sha != expected_manifest_sha:
            raise RuntimeError(
                f"manifest SHA mismatch for {dataset['repo_id']}: got={manifest_sha} expected={expected_manifest_sha}"
            )
        files = parse_sha_manifest(manifest_path)
        dataset_slug = dataset["repo_id"].replace("/", "__")
        descriptor = {
            "schema": "hydradg.seedgraph_dataset_descriptor.v1",
            "dataset_id": dataset_slug,
            "track": dataset["track"],
            "repo_id": dataset["repo_id"],
            "revision": dataset["revision"],
            "license_declared_upstream": dataset["license_declared_upstream"],
            "local_path": str(local_path),
            "source_manifest_sha256": expected_manifest_sha,
            "source_manifest_path": str(manifest_path),
            "files": files,
            "evidence_class": "DETERMINISTIC_DATASET_CUSTODY_DESCRIPTOR",
            "claim_ceiling": DESCRIPTOR_CEILING,
            "signature_state": "NOT_A_HYDRADG_AUTHOR_SIGNATURE",
            "merkle_state": "NOT_A_HYDRADB_MERKLE_COMMITMENT",
        }
        descriptor_path = descriptor_dir / f"{dataset_slug}.json"
        descriptor_path.write_text(json.dumps(descriptor, indent=2, sort_keys=True) + "\n")
        descriptor_sha = sha256_file(descriptor_path)
        bypass_receipt = bypass_dir / f"{dataset_slug}.json"
        sg = seedgraph_import_descriptor(seedgraph_root, descriptor_path, args.operator, bypass_receipt)
        descriptor_hash_match = sg.get("source_sha256") == descriptor_sha
        if not descriptor_hash_match:
            raise RuntimeError(
                f"SeedGraph descriptor hash mismatch for {dataset['repo_id']}: "
                f"seedgraph={sg.get('source_sha256')} local={descriptor_sha}"
            )
        raw = merge_raw_baseline(hydra, dataset, descriptor_sha)
        governed = build_governed_route(hydra, dataset, descriptor, descriptor_sha, sg, seedgraph_commit)
        results.append({
            "dataset_id": dataset_slug,
            "track": dataset["track"],
            "repo_id": dataset["repo_id"],
            "revision": dataset["revision"],
            "license_declared_upstream": dataset["license_declared_upstream"],
            "manifest_verified": True,
            "manifest_sha256": expected_manifest_sha,
            "file_count": len(files),
            "descriptor_path": str(descriptor_path),
            "descriptor_sha256": descriptor_sha,
            "seedgraph_import": sg,
            "seedgraph_descriptor_hash_match": descriptor_hash_match,
            "raw_hydradb": raw,
            "governed_hydradb": governed,
            "semantic_ingest_state": "CUSTODY_DESCRIPTOR_ONLY",
        })

    total = len(results)
    manifest_verified = sum(1 for r in results if r["manifest_verified"])
    seedgraph_matches = sum(1 for r in results if r["seedgraph_descriptor_hash_match"])
    governed_routes = sum(1 for r in results if r["governed_hydradb"]["complete_route"])
    raw_route_edges = sum(r["raw_hydradb"]["route_edges"] for r in results)
    governed_route_edges = sum(r["governed_hydradb"]["route_edges"] for r in results)
    orphan_count = total - governed_routes

    payload = {
        "schema": "hydradg.seedgraph_hydradb_dataset_matrix.v1",
        "timestamp_unix": int(time.time()),
        "dataset_pull_receipt": str(receipt_path),
        "dataset_pull_receipt_file_sha256": sha256_file(receipt_path),
        "seedgraph_commit": seedgraph_commit,
        "seedgraph_worktree_clean": seedgraph_status == "",
        "seedgraph_worktree_status_sha256": sha256_bytes(seedgraph_status.encode()),
        "hydradb_endpoint": args.endpoint,
        "hydradb_namespace": args.namespace,
        "operator": args.operator,
        "datasets": results,
        "comparison": {
            "dataset_count": total,
            "manifest_verification_coverage": manifest_verified / total if total else 0,
            "seedgraph_descriptor_hash_agreement": seedgraph_matches / total if total else 0,
            "governed_complete_route_coverage": governed_routes / total if total else 0,
            "governed_orphan_count": orphan_count,
            "raw_declared_route_edges_total": raw_route_edges,
            "governed_declared_route_edges_total": governed_route_edges,
            "raw_lane": "RAW_HYDRADB_MANIFEST_BASELINE",
            "treatment_lane": "SEEDGRAPH_FCO_FCG_HYDRADB",
            "interpretation": (
                "A larger governed route is a measured provenance/custody property only. "
                "It is not evidence of improved task performance."
            ),
        },
        "status": "PASS" if total and manifest_verified == total and seedgraph_matches == total and governed_routes == total else "FAIL",
        "evidence_class": "RECOMPUTED_LOCAL_CROSS_SYSTEM_CUSTODY_COMPARISON",
        "claim_ceiling": CLAIM_CEILING,
        "signature_state": "HYDRADG_NOT_SIGNED_SEEDGRAPH_ENTRY_STATE_RECORDED_SEPARATELY",
        "merkle_state": "HYDRADB_NOT_MERKLE_COMMITTED",
        "cfmo_state": "NOT_IMPLEMENTED_BY_THIS_RUN",
        "independent_verification_state": "NOT_ESTABLISHED_BY_THIS_RUN",
    }
    science = dict(payload)
    science.pop("timestamp_unix", None)
    payload["result_sha256"] = sha256_bytes(canonical_json(science).encode())
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] != "PASS":
        raise SystemExit(1)


def shutil_which(name: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


if __name__ == "__main__":
    main()
