#!/usr/bin/env python3
"""Project the public HydraDG FCG snapshot into an isolated HydraDB namespace.

Canonical custody remains in the JSONL FCG snapshot. HydraDB is a query projection.
This script is intentionally fail-closed and requires --allow-write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCHEMA = "hydradg.fcg_snapshot_hydradb_projection.v1"
CLAIM = "PUBLIC_FCG_SNAPSHOT_PROJECTION_REPRODUCTION_ONLY_NOT_SCIENTIFIC_RECOMPUTATION"
EXPECTED_ROOT = "experiment:fa170ab51cdfba46f9a24979c9be9b90fdc4ccedcdb292f313aa4439a92b08d8"


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def stable_numeric_id(fco_id: str) -> int:
    digest = hashlib.sha256(fco_id.encode("utf-8")).hexdigest()
    value = int(digest[:13], 16)
    return value or 1


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid JSONL at {path}:{lineno}: {exc}") from exc
        if not isinstance(value, dict):
            raise RuntimeError(f"expected JSON object at {path}:{lineno}")
        out.append(value)
    if not out:
        raise RuntimeError(f"empty JSONL: {path}")
    return out


class Hydra:
    def __init__(self, endpoint: str, token: str, namespace: str):
        self.endpoint = endpoint
        self.token = token
        self.namespace = namespace

    def query(self, query: str, parameters: dict[str, Any] | None = None) -> dict[str, Any]:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps({"cell_id": "cell-0", "query": query, "parameters": parameters or {}}).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.token}",
                "X-Graph-Namespace": self.namespace,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            body = error.read().decode(errors="replace")
            raise RuntimeError(f"HydraDB HTTP {error.code}: {body[:1600]}") from error

    @staticmethod
    def scalar(response: dict[str, Any], column: str) -> int:
        columns = response.get("columns", [])
        rows = response.get("rows", [])
        if column not in columns or not rows:
            return 0
        value = rows[0][columns.index(column)]
        if isinstance(value, dict) and "value" in value:
            value = value["value"]
        return int(value or 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=Path, default=Path("custody/graph/live/nodes.jsonl"))
    parser.add_argument("--edges", type=Path, default=Path("custody/graph/live/edges.jsonl"))
    parser.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--allow-write", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("repro/receipts/HYDRADB_FCG_IMPORT_RECEIPT.json"))
    args = parser.parse_args()

    if not args.allow_write:
        raise SystemExit("STOP: --allow-write is required")
    namespace = args.namespace.strip()
    if not namespace or namespace.lower() in {"default", "shared", "prod", "production"}:
        raise SystemExit("STOP: use an isolated non-default HydraDB namespace")
    if not namespace.startswith("hydradg-"):
        raise SystemExit("STOP: namespace must start with hydradg-")

    nodes_path = args.nodes.expanduser().resolve()
    edges_path = args.edges.expanduser().resolve()
    token_path = args.token_file.expanduser().resolve()
    nodes = load_jsonl(nodes_path)
    edges = load_jsonl(edges_path)
    token = token_path.read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit("STOP: empty HydraDB token")

    node_ids: set[str] = set()
    numeric_ids: dict[int, str] = {}
    for node in nodes:
        fco_id = str(node.get("id", ""))
        if not fco_id:
            raise RuntimeError("node missing id")
        if fco_id in node_ids:
            raise RuntimeError(f"duplicate node id: {fco_id}")
        node_ids.add(fco_id)
        numeric = stable_numeric_id(fco_id)
        if numeric in numeric_ids and numeric_ids[numeric] != fco_id:
            raise RuntimeError(f"numeric id collision: {fco_id} vs {numeric_ids[numeric]}")
        numeric_ids[numeric] = fco_id

    for edge in edges:
        src = str(edge.get("source", ""))
        dst = str(edge.get("target", ""))
        pred = str(edge.get("predicate", ""))
        if src not in node_ids or dst not in node_ids:
            raise RuntimeError(f"edge references missing node: {src} -> {dst}")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", pred):
            raise RuntimeError(f"unsafe/noncanonical predicate token: {pred!r}")

    hydra = Hydra(args.endpoint, token, namespace)

    for node in nodes:
        fco_id = str(node["id"])
        hydra.query(
            "MERGE (n {id:$id}) SET n:HydraDGFCO, n.fco_id=$fco_id, n.fco_type=$fco_type, n.schema=$schema, n.claim_ceiling=$claim_ceiling, n.payload_json=$payload_json",
            {
                "id": stable_numeric_id(fco_id),
                "fco_id": fco_id,
                "fco_type": str(node.get("type", "")),
                "schema": str(node.get("schema", "")),
                "claim_ceiling": str(node.get("claim_ceiling", "")),
                "payload_json": canonical(node).decode("utf-8"),
            },
        )

    for edge in edges:
        pred = str(edge["predicate"])
        hydra.query(
            f"MATCH (a:HydraDGFCO {{id:$src}}),(b:HydraDGFCO {{id:$dst}}) MERGE (a)-[r:{pred}]->(b) SET r.evidence_class=$evidence_class",
            {
                "src": stable_numeric_id(str(edge["source"])),
                "dst": stable_numeric_id(str(edge["target"])),
                "evidence_class": str(edge.get("evidence_class", "")),
            },
        )

    observed_nodes = Hydra.scalar(hydra.query("MATCH (n:HydraDGFCO) RETURN count(n) AS c"), "c")
    observed_edges = Hydra.scalar(hydra.query("MATCH (:HydraDGFCO)-[r]->(:HydraDGFCO) RETURN count(r) AS c"), "c")
    root_observed = Hydra.scalar(
        hydra.query("MATCH (n:HydraDGFCO {fco_id:$id}) RETURN count(n) AS c", {"id": EXPECTED_ROOT}),
        "c",
    )

    expected_nodes = len(nodes)
    expected_edges = len(edges)
    passed = observed_nodes == expected_nodes and observed_edges == expected_edges and root_observed == 1
    result = {
        "schema": SCHEMA,
        "namespace": namespace,
        "nodes_jsonl_sha256": sha_file(nodes_path),
        "edges_jsonl_sha256": sha_file(edges_path),
        "nodes_expected": expected_nodes,
        "nodes_observed": observed_nodes,
        "edges_expected": expected_edges,
        "edges_observed": observed_edges,
        "expected_fcg_root": EXPECTED_ROOT,
        "fcg_root_readback_count": root_observed,
        "hydradb_traceability_canary": "PASS" if root_observed == 1 else "FAIL",
        "status": "PASS" if passed else "FAIL",
        "evidence_class": "RECOMPUTED_ISOLATED_HYDRADB_PUBLIC_FCG_PROJECTION",
        "claim_ceiling": CLAIM,
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
        "timestamp_unix": int(time.time()),
    }
    result["result_sha256"] = hashlib.sha256(canonical({k: v for k, v in result.items() if k not in {"timestamp_unix", "result_sha256"}})).hexdigest()

    out = args.out.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"HYDRADB_FCG_IMPORT={result['status']}")
    print(f"RECEIPT={out}")
    print(f"RECEIPT_FILE_SHA256={sha_file(out)}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
